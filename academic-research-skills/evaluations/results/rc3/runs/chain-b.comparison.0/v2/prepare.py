"""Acquire only the selected frozen SYNTHETIC paired archive; verify and trace reads."""
import csv
import hashlib
import io
import json
import shutil
import stat
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
REQUEST = HERE.parents[2] / "continuations/chain-b.comparison.0/correction/request.json"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def prepare(show=False):
    request = json.loads(REQUEST.read_text())
    frozen = {x["path"]: x["sha256"] for x in request["material_files"]}
    root = Path(request["material_root"])
    correction_path = next(Path(x) for x in frozen if Path(x).name == "approved-correction.json")
    correction_bytes = correction_path.read_bytes()
    assert sha256(correction_bytes) == frozen[str(correction_path)]
    correction = json.loads(correction_bytes)
    source = next(Path(x) for x in frozen if Path(x).name == "paired-measurements-v2.zip")
    archive_bytes = source.read_bytes()
    archive_sha = sha256(archive_bytes)
    assert archive_sha == correction["corrected_zip_sha256"] == frozen[str(source)], "ZIP identity mismatch"
    prior_path = HERE.parent / "inputs/source.zip"
    assert sha256(prior_path.read_bytes()) == correction["original_zip_sha256"]
    prior_members, current_members = {}, {}
    with ZipFile(prior_path) as prior, ZipFile(source) as current:
        assert prior.namelist() == current.namelist(), "Archive member set changed"
        for name in prior.namelist():
            if not name.endswith("/"):
                prior_members[name], current_members[name] = prior.read(name), current.read(name)
                if name == "dictionary.md":
                    assert current_members[name].startswith(prior_members[name]), "Original definitions changed"
                    annotation = current_members[name][len(prior_members[name]):].decode("utf-8").strip()
                    assert annotation == ("Version 2 approved synthetic correction: u08 method B raw values each increased by 1000 subscore. "
                                          "Exact event copies receive the same correction; definitions and target weights are unchanged.")
                elif name != "measurements.csv":
                    assert prior_members[name] == current_members[name], f"Unapproved member change: {name}"
    old_rows = list(csv.DictReader(io.StringIO(prior_members["measurements.csv"].decode("utf-8"))))
    new_rows = list(csv.DictReader(io.StringIO(current_members["measurements.csv"].decode("utf-8"))))
    assert len(old_rows) == len(new_rows)
    changed_rows, changed_lines = [], []
    for line_number, (old, new) in enumerate(zip(old_rows, new_rows), 2):
        assert old.keys() == new.keys()
        if old != new:
            assert [k for k in old if old[k] != new[k]] == ["raw_value"]
            assert old["unit_id"] == "u08" and old["method"] == "B" and old["measurement_unit"] == "subscore"
            assert Decimal(new["raw_value"]) - Decimal(old["raw_value"]) == 1000
            changed_rows.append({"event_id": old["event_id"], "before": old["raw_value"],
                                 "after": new["raw_value"], "unit": old["measurement_unit"]})
            changed_lines.append(line_number)
    assert changed_rows == correction["changed_rows"], "Raw changes do not match approved correction"
    destination = HERE / "inputs"
    destination.mkdir(exist_ok=True)
    copied = destination / "source.zip"
    shutil.copyfile(source, copied)
    assert sha256(copied.read_bytes()) == archive_sha
    extracted = destination / "extracted"
    extracted.mkdir(exist_ok=True)
    members, reads, texts = [], [], {}
    now = datetime.now(timezone.utc).isoformat()
    for name, data in prior_members.items():
        reads.append({"original_archive": str(prior_path),
                      "original_archive_sha256": correction["original_zip_sha256"],
                      "member_name": name, "member_sha256": sha256(data), "bytes": len(data),
                      "read_at_utc": now, "byte_range": [0, len(data)],
                      "range_convention": "bytes half-open", "purpose": "verify authorised correction against retained original"})
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
    identity = {"synthetic": True, "selected_id": "authorised_corrected_paired",
                "selection_reason": "same paired measurements with exactly the authorised u08 B correction",
                "request_sha256": sha256(REQUEST.read_bytes()), "source_path": str(source),
                "source_sha256": archive_sha, "copied_path": str(copied), "zip_crc_ok": True,
                "prior_source_sha256": correction["original_zip_sha256"],
                "correction_authorisation_path": str(correction_path),
                "correction_authorisation_sha256": sha256(correction_bytes), "members": members}
    (HERE / "archive_identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    audit = {"synthetic": True, "checked_at_utc": now, "prior_source_sha256": correction["original_zip_sha256"],
             "corrected_source_sha256": archive_sha, "changed_raw_rows": changed_rows,
             "changed_measurement_csv_lines": changed_lines,
             "changed_unique_events": sorted({x["event_id"] for x in changed_rows}),
             "other_raw_fields_identical": True, "unit_metadata_and_license_byte_identical": True,
             "dictionary_original_definition_bytes_retained": True, "dictionary_appended_annotation": annotation,
             "member_digests": [{"member": name, "prior_sha256": sha256(prior_members[name]),
                                 "corrected_sha256": sha256(current_members[name])} for name in prior_members]}
    (HERE / "correction_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    with (HERE / "derived_member_reads.jsonl").open("a") as handle:
        for read in reads:
            handle.write(json.dumps(read) + "\n")
    return texts


if __name__ == "__main__":
    prepare(show=True)
