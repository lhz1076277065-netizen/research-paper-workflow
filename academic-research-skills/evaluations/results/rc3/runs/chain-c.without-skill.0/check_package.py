"""One offline runnable check: frozen bytes, aggregates, anonymity and editability."""
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import zipfile
from xml.etree import ElementTree as ET

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = HERE.parent.parent
REQUEST = BASE / "transfer-suite/requests/chain-c.without-skill.0.json"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def markdown_text(path):
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.fullmatch(r"\|\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?", line):
            continue
        line = re.sub(r"^#{1,3} ", "", line)
        lines.append(line.replace("|", " "))
    return " ".join(lines).split()


def main():
    req = json.loads(REQUEST.read_text(encoding="utf-8"))
    assert req["condition"] == "without-skill"
    assert req["case_id"] == "chain-c" and req["replicate"] == 0
    assert req["skill_snapshot"] is None and req["initial_skill_text"] == ""
    for source in req["material_files"]:
        assert sha(Path(source["path"])) == source["sha256"], source["path"]
    snap = Path(req["material_root"]) / "published-snapshot-v1.md"
    copy = HERE / "preserved/published-snapshot-v1.md"
    assert snap.read_bytes() == copy.read_bytes()

    trace = [json.loads(line) for line in (HERE / "resource_reads.jsonl").read_text().splitlines()]
    assert not any(r["kind"] == "project" for r in trace)
    assert {r["path"] for r in trace if r["kind"] == "material"} == {s["path"] for s in req["material_files"]}
    assert all(r["line_start"] == 1 and r["line_end"] is None and r["display_sha256"] == r["sha256"] for r in trace)
    professionals = json.loads((BASE / "professional/sources.json").read_text())
    allowed = {p["local_path"]: p for p in professionals}
    for r in trace:
        if r["kind"] == "professional":
            assert r["path"] in allowed and r["sha256"] == allowed[r["path"]]["sha256"]

    review = HERE / "submission/review"
    with (review / "aggregate-results-v3.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 4
    values = {r["comparison"]: float(r["mean_A_minus_B_score"]) for r in rows}
    assert values == {"g1": -1.0, "g2": 3.0, "equal_sampled_mixture": 1.0, "target_mixture": -0.2}
    for r in rows:
        calculated = float(r["w_g1"]) * values["g1"] + float(r["w_g2"]) * values["g2"]
        assert abs(calculated - float(r["mean_A_minus_B_score"])) < 1e-12
    assert [int(r["n_independent_units"]) for r in rows] == [4, 4, 8, 8]
    assert [(r["ci_lower"], r["ci_upper"]) for r in rows[:3]] == [("", "")] * 3
    assert (float(rows[-1]["ci_lower"]), float(rows[-1]["ci_upper"])) == (-0.6, 0.2)
    assert "raw" not in rows[0] and "identifier" not in rows[0]

    manuscript = review / "manuscript-v3-anonymous.md"
    text = manuscript.read_text(encoding="utf-8")
    count = len(re.findall(r"\S+", text))
    assert count <= 2500  # Conservative: entire manuscript, including notes/declarations.
    assert text != (Path(req["material_root"]) / "draft-v2.md").read_text(encoding="utf-8")
    assert "−0.30" not in text and "A universally outperformed B" not in text
    for name in ["manuscript-v3-anonymous.md", "figure-1-caption-v3.md", "supplement-s1-v3.md"]:
        content = (review / name).read_text(encoding="utf-8")
        for value in ["−1.00", "+3.00", "+1.00", "−0.20", "−0.60", "0.20"]:
            assert value in content, (name, value)
        assert "g2" in content and "paired" in content and "percentile" in content
    response = (review / "responses-v3-draft.md").read_text(encoding="utf-8")
    assert all(f"## R{i}" in response for i in range(1, 6))
    correction = (HERE / "correction/version-correction-v1-to-v3-draft.md").read_text(encoding="utf-8")
    assert "−0.30" in correction and "−0.20" in correction and sha(copy) in correction

    svg = ET.parse(review / "figure-1-v3.svg")
    labels = " ".join(svg.getroot().itertext())
    assert "g2 (n=4)" in labels and "Target mix (0.8/0.2; n=8)" in labels
    assert any(e.tag.endswith("text") for e in svg.getroot().iter())  # Editable text.

    docs = sorted((HERE / "submission").rglob("*.docx"))
    docs.append(HERE / "correction/version-correction-v1-to-v3-draft.docx")
    for path in docs:
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            for name in archive.namelist():
                if name.endswith(".xml") or name.endswith(".rels"):
                    ET.fromstring(archive.read(name))
            document = ET.fromstring(archive.read("word/document.xml"))
            words = " ".join(e.text or "" for e in document.iter(f"{{{W}}}t")).split()
            assert words == markdown_text(path.with_suffix(".md")), path
            props = archive.read("docProps/core.xml").decode()
            assert "Mira Example" not in props and "Synthetic Unit Laboratory" not in props
    for path in review.iterdir():
        if path.suffix in {".md", ".py", ".csv", ".svg"}:
            content = path.read_text(encoding="utf-8")
            assert "Mira Example" not in content and "Synthetic Unit Laboratory" not in content, path
        elif path.suffix == ".docx":
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    content = archive.read(name).decode("utf-8")
                    assert "Mira Example" not in content and "Synthetic Unit Laboratory" not in content
    assert "Mira Example" in (HERE / "submission/editor-only/title-page-v3.md").read_text()

    with zipfile.ZipFile(HERE / "submission-package-v3.zip") as archive:
        assert archive.testzip() is None
        expected = {str(p.relative_to(HERE / "submission")): p for p in (HERE / "submission").rglob("*") if p.is_file()}
        assert set(archive.namelist()) == set(expected)
        assert all(archive.read(name) == path.read_bytes() for name, path in expected.items())

    host = BASE / "work/academic-research-skills/evaluations/run_host.py"
    spec = importlib.util.spec_from_file_location("run_host_for_integrity", host)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    integrity_return = module.verify_request(req)
    receipt = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "passed_local_checks",
        "frozen_request_sha256": sha(REQUEST),
        "verify_request": {"completed_without_exception": True, "return": integrity_return},
        "material_hashes_checked": len(req["material_files"]),
        "material_reads_full": sum(r["kind"] == "material" for r in trace),
        "professional_reads_full": sum(r["kind"] == "professional" for r in trace),
        "project_reads": 0,
        "snapshot_preserved_sha256": sha(copy),
        "aggregate_arithmetic_checked": True,
        "reporting_values_consistent": True,
        "g2_retained": True,
        "main_text_word_count_upper_bound": count,
        "word_count_method": "All whitespace-delimited tokens in manuscript, including title/notes/declarations",
        "docx_xml_zip_and_text_parity_checked": len(docs),
        "anonymous_review_text_and_docx_properties_checked": True,
        "editable_svg_text_checked": True,
        "zip_content_matches_submission_folder": True,
        "submission_ready": False,
        "submitted": False,
        "unverified": ["Raw-data numerical replication", "independence audit", "bootstrap implementation and coverage", "original full texts", "human authorship and ethics approval", "controlled-access mechanism", "DOCX rendering in Word", "journal acceptance"]
    }
    (HERE / "verification.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
