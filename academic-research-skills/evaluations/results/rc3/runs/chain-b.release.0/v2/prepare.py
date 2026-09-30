"""SYNTHETIC fixture: verify an authorized correction, then prepare paired data."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from datetime import date
from collections import defaultdict
from statistics import mean
import csv
import hashlib
import io
import json
import math
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parents[2] / "continuation-materials/paired-measurements-v2.zip"
EXPECTED = "79b22107370676dc295fc00eb7f376b895baea4dfebf4ac2d781cf45bd588e07"
PRIOR_EXPECTED = "078a354c60fa96ee7ceedca955517176765f7406bd409dec7512337f59018ef4"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def verify_correction(archive):
    """Check every member and row against the preserved prior archive."""
    prior = (ROOT.parent / "raw/original.zip").read_bytes()
    if sha256(prior) != PRIOR_EXPECTED:
        raise ValueError("Preserved prior archive identity mismatch")
    contents, reads = {}, []
    for label, data, digest in [("prior", prior, PRIOR_EXPECTED),
                                ("corrected", archive, EXPECTED)]:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            names = z.namelist()
            if len(names) != len(set(names)):
                raise ValueError("Repeated member name")
            contents[label] = {name: z.read(name) for name in names}
        for name, member in contents[label].items():
            reads.append({
                "at_utc": datetime.now(timezone.utc).isoformat(),
                "original_zip_sha256": digest, "member_name": name,
                "member_sha256": sha256(member), "member_bytes": len(member),
                "actual_read_byte_range": [0, len(member)],
                "range_semantics": "half-open bytes; full member",
                "purpose": f"{label} member comparison for authorized input correction",
            })
    with (ROOT / "derived_member_reads.jsonl").open("a", encoding="utf-8") as log:
        log.write("".join(json.dumps(r) + "\n" for r in reads))
    expected_members = {"LICENSE.txt", "dictionary.md", "measurements.csv", "units.csv"}
    if any(set(c) != expected_members for c in contents.values()):
        raise ValueError("Correction changed archive member names")
    for name in expected_members - {"measurements.csv", "dictionary.md"}:
        if contents["prior"][name] != contents["corrected"][name]:
            raise ValueError(f"Unauthorized member change: {name}")
    dictionary_appendix = (
        b"\nVersion 2 approved synthetic correction: u08 method B raw values each increased by 1000 subscore. "
        b"Exact event copies receive the same correction; definitions and target weights are unchanged.\n"
    )
    if contents["corrected"]["dictionary.md"] != contents["prior"]["dictionary.md"] + dictionary_appendix:
        raise ValueError("Dictionary differs beyond the explicit correction-record appendix")
    before_reader = csv.DictReader(io.StringIO(contents["prior"]["measurements.csv"].decode()))
    after_reader = csv.DictReader(io.StringIO(contents["corrected"]["measurements.csv"].decode()))
    before, after = list(before_reader), list(after_reader)
    if (before_reader.fieldnames != after_reader.fieldnames
            or len(before) != 43 or len(after) != 43):
        raise ValueError("Correction changed measurement schema or row count")
    changes = []
    for index, (old, new) in enumerate(zip(before, after), start=1):
        changed_fields = [key for key in old if old[key] != new[key]]
        if not changed_fields:
            continue
        if (changed_fields != ["raw_value"] or old["unit_id"] != "u08"
                or old["method"] != "B" or old["measurement_unit"] != "subscore"
                or float(new["raw_value"]) - float(old["raw_value"]) != 1000):
            raise ValueError(f"Unauthorized row change: {index}")
        changes.append({"data_row_1_based": index, "event_id": old["event_id"],
                        "unit_id": old["unit_id"], "method": old["method"],
                        "before": old["raw_value"], "after": new["raw_value"],
                        "unit": old["measurement_unit"]})
    expected_changes = [("e040", "4950.000000", "5950.000000"),
                        ("e041", "5050.000000", "6050.000000"),
                        ("e041", "5050.000000", "6050.000000")]
    if [(c["event_id"], c["before"], c["after"]) for c in changes] != expected_changes:
        raise ValueError("Actual row changes differ from the approved correction")
    (ROOT / "correction_receipt.json").write_text(json.dumps({
        "synthetic": True, "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "prior_zip_sha256": PRIOR_EXPECTED, "corrected_zip_sha256": EXPECTED,
        "row_count_before": len(before), "row_count_after": len(after),
        "changed_rows": changes, "unchanged_members": ["LICENSE.txt", "units.csv"],
        "dictionary_definitions_byte_identical_prefix": True,
        "dictionary_appendix": dictionary_appendix.decode().strip(),
        "member_identity_and_full_read_ranges": reads,
        "scope": "three approved raw-value changes and the explicit dictionary correction-record appendix; all other fields, rows, and definitions equal",
    }, indent=2) + "\n")


def acquire():
    archive = SOURCE.read_bytes()
    if sha256(archive) != EXPECTED:
        raise ValueError("Original archive identity mismatch")
    verify_correction(archive)
    raw = ROOT / "raw"
    raw.mkdir(exist_ok=True)
    copied = raw / "original.zip"
    shutil.copyfile(SOURCE, copied)
    assert sha256(copied.read_bytes()) == EXPECTED
    records = []
    with zipfile.ZipFile(copied) as z:
        for member in z.infolist():
            name = PurePosixPath(member.filename)
            if name.is_absolute() or ".." in name.parts or member.is_dir():
                raise ValueError(f"Unsafe or unexpected archive member: {name}")
            if member.external_attr >> 16 & 0o170000 == 0o120000:
                raise ValueError("Symlinks are not accepted")
            data = z.read(member)
            dest = raw / "extracted" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            record = {
                "at_utc": datetime.now(timezone.utc).isoformat(),
                "original_zip_sha256": EXPECTED,
                "member_name": member.filename,
                "member_sha256": sha256(data),
                "member_bytes": len(data),
                "actual_read_byte_range": [0, len(data)],
                "range_semantics": "half-open bytes; full member",
                "purpose": "acquire, inspect, and preserve original member",
            }
            records.append(record)
    with (ROOT / "derived_member_reads.jsonl").open("a", encoding="utf-8") as log:
        log.write("".join(json.dumps(r) + "\n" for r in records))
    (ROOT / "archive_receipt.json").write_text(json.dumps({
        "synthetic": True,
        "selected_candidate": "authorized corrected paired archive",
        "source_path": str(SOURCE),
        "copied_archive": str(copied),
        "original_zip_sha256": EXPECTED,
        "approved_correction_sha256": "ea52cbde1af67ee7b218ad6be411549ee37547262bf4d3d0e116eaa8c2d2f379",
        "prior_archive_sha256": "078a354c60fa96ee7ceedca955517176765f7406bd409dec7512337f59018ef4",
        "members": records,
    }, indent=2) + "\n", encoding="utf-8")


def read_member(name):
    data = (ROOT / "raw/extracted" / name).read_bytes()
    receipt = json.loads((ROOT / "archive_receipt.json").read_text())
    expected = next(m["member_sha256"] for m in receipt["members"] if m["member_name"] == name)
    if sha256(data) != expected:
        raise ValueError(f"Extracted member identity mismatch: {name}")
    record = {"at_utc": datetime.now(timezone.utc).isoformat(),
              "original_zip_sha256": EXPECTED, "member_name": name,
              "member_sha256": sha256(data), "member_bytes": len(data),
              "actual_read_byte_range": [0, len(data)],
              "range_semantics": "half-open bytes; full member",
              "purpose": "reproducible preparation"}
    with (ROOT / "derived_member_reads.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps(record) + "\n")
    return data.decode("utf-8")


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def prepare():
    # The dictionary specifies equal precision for technical repetitions.
    dictionary = read_member("dictionary.md")
    if "1 score = 1000 subscore" not in dictionary:
        raise ValueError("Unrecognized score conversion")
    measurements = list(csv.DictReader(io.StringIO(read_member("measurements.csv"))))
    metadata = list(csv.DictReader(io.StringIO(read_member("units.csv"))))
    if list(measurements[0]) != ["event_id", "unit_id", "method", "observed_at", "raw_value", "measurement_unit"]:
        raise ValueError("Measurement schema changed")
    if list(metadata[0]) != ["unit_id", "stratum", "valid_from", "valid_to", "record"]:
        raise ValueError("Metadata schema changed")
    unique, duplicates = {}, []
    for row in measurements:
        if not all(row.values()):
            raise ValueError("Missing raw field")
        key = row["event_id"]
        if key in unique:
            if unique[key] != row:
                raise ValueError(f"Conflicting event copy: {key}")
            duplicates.append(key)
        else:
            unique[key] = row
    factors = {"score": 1.0, "subscore": 0.001}
    events = []
    active_metadata = set()
    for row in unique.values():
        when = date.fromisoformat(row["observed_at"])
        matches = [(i, m) for i, m in enumerate(metadata)
                   if m["unit_id"] == row["unit_id"]
                   and date.fromisoformat(m["valid_from"]) <= when <= date.fromisoformat(m["valid_to"])]
        if len(matches) != 1:
            raise ValueError(f"Expected one active metadata row: {row['event_id']}, got {len(matches)}")
        if row["measurement_unit"] not in factors or row["method"] not in {"A", "B"}:
            raise ValueError("Unknown method or measurement unit")
        value = float(row["raw_value"]) * factors[row["measurement_unit"]]
        if not math.isfinite(value):
            raise ValueError("Nonfinite score")
        i, matched = matches[0]
        active_metadata.add(i)
        events.append({**row, "stratum": matched["stratum"], "score": value,
                       "metadata_record": matched["record"]})
    grouped = defaultdict(list)
    unit_strata = defaultdict(set)
    for event in events:
        grouped[(event["unit_id"], event["method"])].append(event["score"])
        unit_strata[event["unit_id"]].add(event["stratum"])
    paired = []
    for unit_id, strata in sorted(unit_strata.items()):
        if len(strata) != 1 or (unit_id, "A") not in grouped or (unit_id, "B") not in grouped:
            raise ValueError(f"Invalid paired unit: {unit_id}")
        a, b = mean(grouped[(unit_id, "A")]), mean(grouped[(unit_id, "B")])
        paired.append({"unit_id": unit_id, "stratum": next(iter(strata)),
                       "A_score": a, "B_score": b, "difference_A_minus_B": a - b,
                       "n_A_events": len(grouped[(unit_id, "A")]),
                       "n_B_events": len(grouped[(unit_id, "B")])})
    counts = {g: sum(p["stratum"] == g for p in paired) for g in sorted({p["stratum"] for p in paired})}
    if counts != {"g1": 4, "g2": 4}:
        raise ValueError(f"Unexpected fixture unit structure: {counts}")
    assert len(events) == 41 and len(paired) == 8 and set(duplicates) == {"e004", "e041"}
    derived = ROOT / "derived"
    derived.mkdir(exist_ok=True)
    write_csv(derived / "converted_events.csv", events)
    write_csv(derived / "paired_units.csv", paired)
    flow = [{"stage": "raw_measurement_rows", "count": len(measurements)},
            {"stage": "unique_events_after_exact_copy_removal", "count": len(events)},
            {"stage": "events_after_active_metadata_join", "count": len(events)},
            {"stage": "unit_method_means", "count": len(grouped)},
            {"stage": "independent_paired_units", "count": len(paired)}]
    write_csv(derived / "sample_flow.csv", flow)
    report = {
        "synthetic": True, "archive_sha256": EXPECTED,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "preparation_code_sha256": sha256(Path(__file__).read_bytes()),
        "sample_flow": flow, "duplicates_removed": duplicates,
        "conflicting_events": 0, "missing_raw_fields": 0,
        "metadata_rows": len(metadata), "active_metadata_rows_used": len(active_metadata),
        "unmatched_events": 0, "ambiguous_metadata_matches": 0,
        "metadata_join": "unit_id and inclusive observation-date validity; one active match per event",
        "measurement_conversion": factors,
        "technical_repetition_rule": "equal-weight mean per independent unit and method after conversion",
        "independent_units_per_stratum": counts,
        "target_weights": {"g1": 0.8, "g2": 0.2},
        "sampled_unit_weights": {"g1": 0.5, "g2": 0.5},
        "unit_independence_status": "stipulated conditional on stratum by synthetic dictionary; not externally validated",
        "derived_hashes": {p.name: sha256(p.read_bytes()) for p in derived.glob("*.csv")},
    }
    (ROOT / "preparation_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"units": paired, "flow": flow}, indent=2))


if __name__ == "__main__":
    acquire()
    prepare()
