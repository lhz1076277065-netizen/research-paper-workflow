"""Run: the common Python interpreter verify_outputs.py. Checks actual deliverables."""
import csv
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

OUT = Path(__file__).resolve().parent
REQUEST = Path("LOCAL_EVIDENCE_ROOT/evaluation-suite/requests/full-manuscript.comparison.0.json")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    request = json.loads(REQUEST.read_text())
    inputs = []
    for item in request["material_files"]:
        actual = sha(Path(item["path"]))
        assert actual == item["sha256"], item["path"]
        inputs.append({"path": item["path"], "sha256": actual, "match": True})
    assert sha(Path(request["skill_entry"])) == request["skill_entry_sha256"]
    assert sha(OUT / "inputs/original-manuscript.md") == request["material_files"][0]["sha256"]
    assert sha(OUT / "fixed-results.csv") == request["material_files"][1]["sha256"]
    with (OUT / "fixed-results.csv").open() as handle:
        rows = list(csv.DictReader(line for line in handle if not line.startswith("#")))
    assert len(rows) == 8
    text = (OUT / "manuscript.md").read_text()
    table1 = []
    table2 = []
    current = None
    for line in text.splitlines():
        if line.startswith("**Table 1"): current = table1
        if line.startswith("**Table 2"): current = table2
        if current is not None and line.startswith(("| Reference |", "| Changed |")):
            current.append([cell.strip() for cell in line.strip("|").split("|")])
    assert len(table1) == 8 and len(table2) == 2
    for row, cells in zip(rows, table1):
        assert cells == [row["condition"].capitalize(), row["stratum"], row["method"], row["n"], row["loss"], f"[{row['lo']}, {row['hi']}]"]
    weighted = {}
    for condition, cells in zip(["reference", "changed"], table2):
        totals = {}
        for method in ["A", "B"]:
            group = [r for r in rows if r["condition"] == condition and r["method"] == method]
            assert sum(int(r["n"]) for r in group) == 100
            totals[method] = sum(Decimal(r["loss"]) * Decimal(r["n"]) for r in group) / Decimal(100)
        delta = totals["B"] - totals["A"]
        expected = Decimal("-0.44") if condition == "reference" else Decimal("0.92")
        assert delta == expected
        assert Decimal(cells[2]) == totals["A"] and Decimal(cells[3]) == totals["B"]
        assert Decimal(cells[4].replace("−", "-")) == delta
        weighted[condition] = {"A": str(totals["A"]), "B": str(totals["B"]), "B_minus_A": str(delta)}
    differences = {}
    for condition in ["reference", "changed"]:
        for stratum in ["S1", "S2"]:
            pair = {r["method"]: Decimal(r["loss"]) for r in rows if r["condition"] == condition and r["stratum"] == stratum}
            delta = pair["B"] - pair["A"]
            assert (delta < 0) if stratum == "S1" else (delta > 0)
            differences[condition + ":" + stratum] = str(delta)
    plotted = json.loads((OUT / "figure-data.json").read_text())
    assert plotted["rows"] == rows and plotted["weighted"] == weighted and plotted["excluded_rows"] == 0
    for name in ["Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion", "Declarations and references"]:
        assert "## " + name in text
    assert not re.search(r"\b(perhaps|tentatively|cautiously|unfortunately)\b", text, re.I)
    assert "not an empirical research article" in text
    assert "They are reproduced unchanged" in text
    assert "not an assigned intervention" in text
    assert "It remains a proposal" in text
    assert "full separate memo documents were not supplied" in text
    assert "independent human scientific review was not performed" in text
    assert "<text" in (OUT / "figure-1.svg").read_text()
    sources = json.loads((OUT / "source-read-manifest.json").read_text())
    for source in sources:
        assert sha(OUT / source["snapshot"]) == source["sha256"]
    assert json.loads((OUT / "figure.alignment.json").read_text())["verdict"] == "PASS"
    glyph = json.loads((OUT / "figure-pdf-text-audit.json").read_text())
    assert glyph["auditable"] and glyph["minimum_found_pt"] >= 5 and glyph["below_minimum_count"] == 0
    assert json.loads((OUT / "figure-collision-audit.json").read_text())["verdict"] == "PASS"
    rendered = json.loads((OUT / "render-review.json").read_text())
    assert rendered["tableRows"] == [8, 2] and rendered["imageLoaded"] and not rendered["horizontalOverflow"] and not rendered["pageErrors"]
    import fitz
    with fitz.open(OUT / "figure-1.pdf") as doc:
        width, height = doc[0].rect.width * 25.4 / 72, doc[0].rect.height * 25.4 / 72
        assert abs(width - 180) < 0.01 and abs(height - 115) < 0.01
    with fitz.open(OUT / "manuscript.pdf") as doc:
        extracted = " ".join("\n".join(p.get_text() for p in doc).split())
        assert all(name in extracted for name in ["Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion", "Declarations and references"])
        assert "10.48550/arXiv.2609.00065" in extracted
        assert "generate a figure from the supplied summaries" in extracted
        pages = len(doc)
    report = {"status": "PASS", "scope": "input/source hashes, eight table rows and intervals, arithmetic, direction, completeness, figure/render files", "input_checks": inputs, "skill_entry_sha256": request["skill_entry_sha256"], "source_snapshots_checked": len(sources), "source_row_count": len(rows), "weighted": weighted, "stratum_B_minus_A": differences, "manuscript_pdf_pages": pages, "figure_dimensions_mm": [width, height], "minimum_figure_font_pt": glyph["minimum_found_pt"], "human_review": "not performed", "causal_or_significance_analysis": "not performed"}
    (OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))

if __name__ == "__main__":
    main()
