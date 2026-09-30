"""Integrity and exact symbolic-example check; no empirical sampling."""
import hashlib
import json
from fractions import Fraction
from pathlib import Path


def check():
    root = Path(__file__).resolve().parent
    record = json.loads((root / "execution.json").read_text())
    request_bytes = Path(record["request"]["path"]).read_bytes()
    assert hashlib.sha256(request_bytes).hexdigest() == record["request"]["sha256"]
    request = json.loads(request_bytes)
    for item in request["material_files"]:
        material = Path(item["path"]).read_bytes()
        assert hashlib.sha256(material).hexdigest() == item["sha256"], item["path"]
        assert material.decode() in request["material"]
    entry = Path(request["skill_entry"]).read_bytes()
    assert hashlib.sha256(entry).hexdigest() == request["skill_entry_sha256"]
    assert entry.decode() == request["initial_skill_text"]
    for item in record["file_reads"] + record["artifacts"]:
        assert hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() == item["sha256"], item["path"]
    assert record["model"]["exact_identifier"] == "unknown"
    assert record["empirical_study_conducted"] is False
    x = (-1, 1)
    observable_a = tuple((value, value, "same metadata") for value in x)
    observable_b = tuple((value, value, "same metadata") for value in x)
    assert observable_a == observable_b
    gains = []
    for direction in (1, -1):
        baseline = Fraction(sum((direction * value) ** 2 for value in x), 2)
        candidate = Fraction(sum((value - direction * value) ** 2 for value in x), 2)
        gains.append(baseline - candidate)
    assert gains == [Fraction(1), Fraction(-3)]
    print("PASS: provenance, artifact integrity, JSON, and exact two-world arithmetic; no empirical validation.")


if __name__ == "__main__":
    check()
