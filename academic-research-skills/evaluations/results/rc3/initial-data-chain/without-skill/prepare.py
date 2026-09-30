"""SYNTHETIC: obtain and verify the original paired fixture archive."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[1] / "materials/chain-b/archives/paired-measurements-v1.zip"
EXPECTED_SHA256 = "078a354c60fa96ee7ceedca955517176765f7406bd409dec7512337f59018ef4"
PROFESSIONAL = ROOT.parents[1] / "professional/Haojae/scipilot-figure-skill"
VENDOR_HASHES = {
    "LICENSE": "9138113e804093683aea49033b274c7ab35babce90c3acb86eae115d44585671",
    "scripts/profile_data.py": "d8a2a72c2607c390f2d3ed1508209d515ad4fbf833fa1602ab9da519b3596ec4",
    "scripts/setup_style.py": "d58ef81684577bb605a92733dd2ca48ade03b4f819b3d255fd62f319be7fea82",
    "scripts/visual_qa.py": "67675709e523c76e2748d50749de7bc6332f07df865379b26d024321fb40120f",
    "scripts/check_figure.py": "861191858ff47c5af5247f08d0759b14956a2a7e7d8eafcc6b414d37b9d70f06",
}


def prepare():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("Original archive identity mismatch")
    mirror_digest = hashlib.sha256(SOURCE.with_name("mirror-v1.zip").read_bytes()).hexdigest()
    if mirror_digest != digest:
        raise ValueError("Mirror identity differs from declared shared source")
    archive = ROOT / "inputs/paired-measurements-v1.zip"
    archive.parent.mkdir(exist_ok=True)
    shutil.copyfile(SOURCE, archive)
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest
    destination = ROOT / "inputs/original"
    destination.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        assert zf.testzip() is None, "Corrupt ZIP member"
        for member in zf.infolist():
            path = (destination / member.filename).resolve()
            assert path.is_relative_to(destination.resolve()), "Unsafe ZIP path"
            assert member.file_size < 10_000_000, "Unexpected fixture member size"
            assert (member.external_attr >> 16) & 0o170000 != 0o120000, "ZIP symlink refused"
        zf.extractall(destination)
        members = [m.filename for m in zf.infolist() if not m.is_dir()]
    record = {
        "synthetic": True,
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate": "paired",
        "selection_reason": "Original paired scores with dictionary and unit metadata",
        "source": str(SOURCE), "archive_sha256": digest,
        "mirror_sha256": mirror_digest,
        "mirror_is_same_source": True,
        "proxy_used": False,
        "members": [{"path": m, "sha256": hashlib.sha256((destination / m).read_bytes()).hexdigest()} for m in members],
    }
    (ROOT / "archive_identity.json").write_text(json.dumps(record, indent=2) + "\n")
    vendor = ROOT / "vendor/scipilot"
    vendor.mkdir(parents=True, exist_ok=True)
    for relative, expected in VENDOR_HASHES.items():
        source = PROFESSIONAL / relative
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
        shutil.copyfile(source, vendor / Path(relative).name)
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    prepare()
