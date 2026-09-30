"""Acquire only the selected frozen SYNTHETIC paired archive; verify and trace reads."""
import hashlib
import json
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
REQUEST = HERE.parents[1] / "transfer-suite/requests/chain-b.comparison.0.json"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def prepare(show=False):
    request = json.loads(REQUEST.read_text())
    frozen = {x["path"]: x["sha256"] for x in request["material_files"]}
    root = Path(request["material_root"])
    catalogue_path = root / "candidates.json"
    catalogue_bytes = catalogue_path.read_bytes()
    assert sha256(catalogue_bytes) == frozen[str(catalogue_path)]
    candidates = json.loads(catalogue_bytes)
    selected = next(x for x in candidates if x["id"] == "paired")
    source = root / selected["path"]
    archive_bytes = source.read_bytes()
    archive_sha = sha256(archive_bytes)
    assert archive_sha == selected["sha256"] == frozen[str(source)], "ZIP identity mismatch"
    destination = HERE / "inputs"
    destination.mkdir(exist_ok=True)
    copied = destination / "source.zip"
    shutil.copyfile(source, copied)
    assert sha256(copied.read_bytes()) == archive_sha
    extracted = destination / "extracted"
    extracted.mkdir(exist_ok=True)
    members, reads, texts = [], [], {}
    now = datetime.now(timezone.utc).isoformat()
    with ZipFile(copied) as archive:
        assert archive.testzip() is None, "ZIP CRC error"
        assert sum(x.file_size for x in archive.infolist()) < 20_000_000
        seen = set()
        for info in archive.infolist():
            name = PurePosixPath(info.filename)
            assert not name.is_absolute() and ".." not in name.parts
            assert not stat.S_ISLNK(info.external_attr >> 16)
            assert info.filename not in seen, "Duplicate member name"
            seen.add(info.filename)
            if info.is_dir():
                continue
            data = archive.read(info)
            target = extracted.joinpath(*name.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            record = {"original_archive": str(source), "original_archive_sha256": archive_sha,
                      "member_name": info.filename, "member_sha256": sha256(data),
                      "bytes": len(data), "extracted_path": str(target)}
            members.append(record)
            if target.suffix.lower() in {".csv", ".json", ".md", ".txt"}:
                decoded = data.decode("utf-8")
                texts[info.filename] = decoded
                reads.append({**record, "read_at_utc": now, "byte_range": [0, len(data)],
                              "line_range": [1, len(decoded.splitlines())],
                              "range_convention": "bytes half-open; lines inclusive",
                              "purpose": "inspect original synthetic measurements and dictionary"})
                if show:
                    print(json.dumps({"member": info.filename, "text": decoded}, ensure_ascii=False))
    identity = {"synthetic": True, "selected_id": selected["id"],
                "selection_reason": "original paired scores and unit metadata match the target; proxy does not",
                "request_sha256": sha256(REQUEST.read_bytes()), "source_path": str(source),
                "source_sha256": archive_sha, "copied_path": str(copied), "zip_crc_ok": True,
                "mirror_is_duplicate_by_catalogue_digest": True, "members": members}
    (HERE / "archive_identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    with (HERE / "derived_member_reads.jsonl").open("a") as handle:
        for read in reads:
            handle.write(json.dumps(read) + "\n")
    return texts


if __name__ == "__main__":
    prepare(show=True)
