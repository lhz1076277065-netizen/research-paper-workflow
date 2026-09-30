"""One runnable integrity check for the fixed manuscript and real exports."""
from pathlib import Path
from decimal import Decimal
import csv
import hashlib
import json
import re
import zipfile
from xml.etree import ElementTree as ET
import fitz
from PIL import Image

OUT = Path(__file__).resolve().parent
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
checks = {}
for entry in json.loads((OUT / "input-checks.json").read_text()):
    assert hashlib.sha256(Path(entry["path"]).read_bytes()).hexdigest() == entry["expected_sha256"]
checks["frozen_input_and_entry_hashes"] = "matched"
rows = list(csv.DictReader(line for line in (OUT / "inputs/fixed-results.csv").read_text().splitlines() if not line.startswith("#")))
display_rows = list(csv.DictReader((OUT / "figure1_source_data.csv").open()))
assert len(rows) == 8 and len(display_rows) == 12
for row in rows:
    match = next(r for r in display_rows if r["row_type"] == "supplied_summary" and
                 (r["condition"], r["stratum"], r["method"]) == (row["condition"], row["stratum"], row["method"]))
    for key in ["n", "loss", "lo", "hi"]:
        assert Decimal(row[key]) == Decimal(match[key]), (row, match)
for condition, a, b, delta in [("reference", "4.80", "4.36", "-0.44"), ("changed", "6.60", "7.52", "0.92")]:
    actual = {}
    for method, target in [("A", a), ("B", b)]:
        selected = [r for r in rows if r["condition"] == condition and r["method"] == method]
        denominator = sum(Decimal(r["n"]) for r in selected)
        assert denominator == 100
        actual[method] = sum(Decimal(r["n"]) * Decimal(r["loss"]) for r in selected) / denominator
        assert actual[method] == Decimal(target)
        aggregate = next(r for r in display_rows if r["row_type"] == "weighted_average" and r["condition"] == condition and r["method"] == method)
        assert Decimal(aggregate["loss"]) == actual[method]
        assert aggregate["lo"] == aggregate["hi"] == ""
    assert actual["B"] - actual["A"] == Decimal(delta)
checks["eight_rows_intervals_weights_and_aggregates"] = "matched; no aggregate intervals"

manifest = json.loads((OUT / "process/document-export.json").read_text())
digest = hashlib.sha256((OUT / "manuscript.md").read_bytes()).hexdigest()
assert digest == manifest["source_sha256"]
assert digest in (OUT / "factual_claim_comparison.md").read_text()
with zipfile.ZipFile(OUT / "manuscript.docx") as archive:
    tree = ET.fromstring(archive.read("word/document.xml"))
    actual_units = []
    for block in tree.find("w:body", NS):
        if block.tag == f"{{{NS['w']}}}p":
            value = "".join(block.itertext())
            texts = "".join(element.text or "" for element in block.findall(".//w:t", NS))
            if texts.strip():
                actual_units.append(texts)
        elif block.tag == f"{{{NS['w']}}}tbl":
            for row in block.findall("w:tr", NS):
                for cell in row.findall("w:tc", NS):
                    actual_units.append("".join(element.text or "" for element in cell.findall(".//w:t", NS)))
    assert actual_units == manifest["expected_text_units"], "Editable text/table export differs from complete manuscript"
    assert len([name for name in archive.namelist() if name.startswith("word/media/")]) == 1
    core = archive.read("docProps/core.xml").decode()
    assert digest in core
checks["docx_complete_text_and_table_parity"] = {"matched_units": len(actual_units), "embedded_figures": 1}

png = Image.open(OUT / "figure1.png")
assert png.size == (1890, 1410)
assert round(png.info["dpi"][0]) == 300
figure = fitz.open(OUT / "figure1.pdf")
assert len(figure) == 1
assert abs(figure[0].rect.width - 6.3 * 72) < 0.01
assert abs(figure[0].rect.height - 4.7 * 72) < 0.01
fonts = figure[0].get_fonts(full=True)
assert fonts and all(font[2] != "Type3" for font in fonts)
font_info = []
for font in fonts:
    name, extension, font_type, content = figure.extract_font(font[0])
    assert content, "A figure font is not embedded"
    font_info.append({"name": name, "type": font[2], "embedded_bytes": len(content)})
assert not figure[0].get_images()
span_sizes = [span["size"] for block in figure[0].get_text("dict")["blocks"] if "lines" in block
              for line in block["lines"] for span in line["spans"]]
assert min(span_sizes) >= 8
checks["figure_export"] = {"inches": [6.3, 4.7], "pixels": [1890, 1410], "dpi": 300,
                           "fonts": font_info, "minimum_font_pt": min(span_sizes), "pdf_raster_images": 0}
figure.close()

pdf = fitz.open(OUT / "manuscript.pdf")
pdf_text = "\n".join(page.get_text() for page in pdf)
assert all(page.get_text().strip() for page in pdf)
for heading in ["Abstract", "Introduction", "Methods", "Results", "Discussion", "Conclusion", "Declarations and references"]:
    assert heading in pdf_text, heading
for token in ["4.80", "4.36", "6.60", "7.52", "0.44", "+0.92", "8.4, 9.6", "7.7, 8.7"]:
    assert token in pdf_text, token
assert len(pdf_text) > 9000
checks["manuscript_pdf"] = {"pages": len(pdf), "extracted_characters": len(pdf_text), "all_main_sections": "present"}
(OUT / "process/manuscript_pdf_text.txt").write_text(pdf_text)
preview_dir = OUT / "process/rendered-pages"
preview_dir.mkdir(exist_ok=True)
thumbs = []
for index, page in enumerate(pdf):
    pixmap = page.get_pixmap(dpi=110)
    destination = preview_dir / f"page-{index + 1:02d}.png"
    pixmap.save(destination)
    image = Image.open(destination).convert("RGB")
    image.thumbnail((340, 440))
    thumbs.append(image)
columns = 3
sheet = Image.new("RGB", (columns * 360, ((len(thumbs) + columns - 1) // columns) * 460), "#DDDDDD")
for index, image in enumerate(thumbs):
    sheet.paste(image, ((index % columns) * 360 + 10, (index // columns) * 460 + 10))
sheet.save(OUT / "process/manuscript_contact_sheet.png")
pdf.close()

for entry in json.loads((OUT / "source-manifest.json").read_text()):
    assert hashlib.sha256(Path(entry["snapshot"]).read_bytes()).hexdigest() == entry["sha256"]
checks["public_source_snapshot_hashes"] = "matched"
result = {"status": "pass", "subject": "manuscript.md", "subject_sha256": digest, "checks": checks,
          "scope": "File and arithmetic verification; agent semantic/visual review is separate; no empirical or human-peer-review claim."}
(OUT / "process/verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps(result, ensure_ascii=False, indent=2))
