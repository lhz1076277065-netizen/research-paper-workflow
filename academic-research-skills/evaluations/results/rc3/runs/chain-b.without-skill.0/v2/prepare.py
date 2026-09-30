"""SYNTHETIC: obtain and verify the authorized corrected paired fixture archive."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[2] / "continuation-materials/paired-measurements-v2.zip"
EXPECTED_SHA256 = "79b22107370676dc295fc00eb7f376b895baea4dfebf4ac2d781cf45bd588e07"
CORRECTION = ROOT.parents[2] / "continuation-materials/approved-correction.json"
CORRECTION_SHA256 = "ea52cbde1af67ee7b218ad6be411549ee37547262bf4d3d0e116eaa8c2d2f379"
PROFESSIONAL = ROOT.parents[2] / "professional/Haojae/scipilot-figure-skill"
VENDOR_HASHES = {
    "LICENSE": "9138113e804093683aea49033b274c7ab35babce90c3acb86eae115d44585671",
    "scripts/profile_data.py": "d8a2a72c2607c390f2d3ed1508209d515ad4fbf833fa1602ab9da519b3596ec4",
    "scripts/setup_style.py": "d58ef81684577bb605a92733dd2ca48ade03b4f819b3d255fd62f319be7fea82",
    "scripts/visual_qa.py": "67675709e523c76e2748d50749de7bc6332f07df865379b26d024321fb40120f",
    "scripts/check_figure.py": "861191858ff47c5af5247f08d0759b14956a2a7e7d8eafcc6b414d37b9d70f06",
}


def audit_correction(destination, archive_sha256):
    approval = json.loads((ROOT / "inputs/approved-correction.json").read_text())
    previous = ROOT.parent / "inputs/original"
    old_identity = json.loads((ROOT.parent / "archive_identity.json").read_text())
    if old_identity["archive_sha256"] != approval["original_zip_sha256"]:
        raise ValueError("Correction predecessor archive mismatch")
    if archive_sha256 != approval["corrected_zip_sha256"]:
        raise ValueError("Correction successor archive mismatch")
    before = list(csv.DictReader((previous / "measurements.csv").read_text().splitlines()))
    after = list(csv.DictReader((destination / "measurements.csv").read_text().splitlines()))
    if len(before) != len(after):
        raise ValueError("Unauthorized row-count change")
    changes = []
    for old, new in zip(before, after, strict=True):
        if old != new:
            if (old["unit_id"], old["method"], old["measurement_unit"]) != ("u08", "B", "subscore"):
                raise ValueError("Unexpected corrected unit, method or measurement scale")
            if {k: v for k, v in old.items() if k != "raw_value"} != {k: v for k, v in new.items() if k != "raw_value"}:
                raise ValueError("Unauthorized non-value change")
            if float(new["raw_value"]) - float(old["raw_value"]) != 1000:
                raise ValueError("Unexpected correction magnitude")
            changes.append({"event_id": old["event_id"], "before": old["raw_value"],
                            "after": new["raw_value"], "unit": old["measurement_unit"]})
    if changes != approval["changed_rows"] or not approval["unchanged_definitions"]:
        raise ValueError("Observed changes differ from authorized correction")
    unchanged = {}
    for name in ["LICENSE.txt", "units.csv"]:
        unchanged[name] = (previous / name).read_bytes() == (destination / name).read_bytes()
        if not unchanged[name]:
            raise ValueError(f"Unauthorized member change: {name}")
    old_dictionary = (previous / "dictionary.md").read_bytes()
    new_dictionary = (destination / "dictionary.md").read_bytes()
    if not new_dictionary.startswith(old_dictionary):
        raise ValueError("Original dictionary definitions changed")
    record = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "synthetic": True,
              "approved_changes": changes, "changed_raw_rows_including_copy": len(changes),
              "changed_unique_events": len({r["event_id"] for r in changes}),
              "unchanged_raw_rows": len(before) - len(changes),
              "byte_identical_members": unchanged,
              "dictionary_original_definitions_retained": True,
              "dictionary_appended_note": new_dictionary[len(old_dictionary):].decode("utf-8"),
              "target_weights": [0.8, 0.2], "preparation_and_analysis_methods_changed": False}
    (ROOT / "correction_dependency_audit.json").write_text(json.dumps(record, indent=2) + "\n")
    with (ROOT / "derived_resource_reads.jsonl").open("a") as trace:
        for folder, identity in [(previous, old_identity), (destination, {"archive_sha256": archive_sha256})]:
            for name in ["measurements.csv", "dictionary.md", "LICENSE.txt", "units.csv"]:
                raw = (folder / name).read_bytes()
                trace.write(json.dumps({"read_at_utc": datetime.now(timezone.utc).isoformat(),
                    "source_archive_sha256": identity["archive_sha256"], "member": name,
                    "member_sha256": hashlib.sha256(raw).hexdigest(),
                    "path": str(folder / name), "line_start": 1,
                    "line_end": len(raw.decode("utf-8").splitlines()),
                    "byte_count": len(raw), "purpose": "Verify only authorized source correction"}) + "\n")


def prepare():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("Original archive identity mismatch")
    correction_digest = hashlib.sha256(CORRECTION.read_bytes()).hexdigest()
    if correction_digest != CORRECTION_SHA256:
        raise ValueError("Correction authorization identity mismatch")
    archive = ROOT / "inputs/paired-measurements-v2.zip"
    archive.parent.mkdir(exist_ok=True)
    shutil.copyfile(SOURCE, archive)
    shutil.copyfile(CORRECTION, ROOT / "inputs/approved-correction.json")
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
    audit_correction(destination, digest)
    record = {
        "synthetic": True,
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate": "authorized corrected paired",
        "selection_reason": "Explicit correction continuation; original estimator and definitions retained",
        "source": str(SOURCE), "archive_sha256": digest,
        "supersedes_archive_sha256": "078a354c60fa96ee7ceedca955517176765f7406bd409dec7512337f59018ef4",
        "correction_authorization_source": str(CORRECTION),
        "correction_authorization_sha256": correction_digest,
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
