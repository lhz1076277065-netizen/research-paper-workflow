"""Create editable DOCX and rendered PDF copies of this run's Markdown drafts."""
import html
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parent
OFFICE = "LOCAL_USER_ROOT/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/soffice"
names = ["manuscript-v3-anonymous", "caption-v3", "supplement-v3", "title-page-draft", "declarations-draft", "cover-letter-draft", "response-to-reviewers", "correction-note-v1-draft", "data-access-request-draft"]
for folder in ["editable", "render", "native-office-profile"]:
    (OUT / folder).mkdir(exist_ok=True)
profile = (OUT / "native-office-profile").as_uri()

for name in names:
    lines = (OUT / (name + ".md")).read_text().splitlines()
    body = []
    table = False
    for line in lines:
        if line.startswith("| "):
            if re.fullmatch(r"[| :\-]+", line):
                continue
            if not table:
                body.append("<table>"); table = True
            cells = line.strip("|").split("|")
            body.append("<tr>" + "".join("<td>" + html.escape(cell.strip()) + "</td>" for cell in cells) + "</tr>")
            continue
        if table:
            body.append("</table>"); table = False
        if not line.strip():
            continue
        match = re.match(r"^(#{1,3}) (.*)$", line)
        if match:
            level = len(match[1]); body.append(f"<h{level}>" + html.escape(match[2]) + f"</h{level}>")
        elif line.startswith("> "):
            body.append("<blockquote>" + html.escape(line[2:]) + "</blockquote>")
        else:
            body.append("<p>" + html.escape(line) + "</p>")
    if table:
        body.append("</table>")
    document = '<!doctype html><html><head><meta charset="utf-8"><title>Development draft</title><style>@page {size:A4; margin:20mm} body {font-family:DejaVu Sans,sans-serif;font-size:11pt;line-height:1.35} h1 {font-size:16pt} h2 {font-size:13pt} h3 {font-size:11pt} p {margin:7pt 0} blockquote {margin:7pt 10pt;color:#333} table {border-collapse:collapse;width:100%;font-size:10pt} td {border:1px solid #bbb;padding:5pt;vertical-align:top}</style></head><body>' + "\n".join(body) + "</body></html>"
    (OUT / "render" / (name + ".html")).write_text(document)

version = subprocess.run([OFFICE,"--version"], check=True, text=True, capture_output=True).stdout.strip()
cmd = [OFFICE, f"-env:UserInstallation={profile}", "--headless", "--convert-to", "docx:Office Open XML Text", "--outdir", str(OUT / "editable")]
result = subprocess.run(cmd + [str(OUT / "render" / (name + ".html")) for name in names], check=True, text=True, capture_output=True)
core_ns = {"dc": "http://purl.org/dc/elements/1.1/", "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"}
paragraphs = {}
for name in names:
    path = OUT / "editable" / (name + ".docx")
    assert path.exists(), result.stdout + result.stderr
    with zipfile.ZipFile(path) as z:
        members = {i.filename: z.read(i.filename) for i in z.infolist()}
    core = ET.fromstring(members["docProps/core.xml"])
    for key in ["dc:creator", "cp:lastModifiedBy"]:
        node = core.find(key, core_ns)
        if node is not None:
            node.text = ""
    members["docProps/core.xml"] = ET.tostring(core, encoding="utf-8", xml_declaration=True)
    w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    root = ET.fromstring(members["word/document.xml"])
    section = root.find(".//" + w + "sectPr")
    margins, size = section.find(w + "pgMar"), section.find(w + "pgSz")
    available = int(size.get(w + "w")) - int(margins.get(w + "left")) - int(margins.get(w + "right"))
    # The native HTML importer sizes 100%-width tables to its viewport; fit the page body instead.
    for table_node in root.iter(w + "tbl"):
        grid = list(table_node.find(w + "tblGrid"))
        original = [int(col.get(w + "w")) for col in grid]
        widths = [round(width * available / sum(original)) for width in original]
        widths[-1] = available - sum(widths[:-1])
        table_node.find(w + "tblPr").find(w + "tblW").set(w + "w", str(available))
        for col, width in zip(grid, widths):
            col.set(w + "w", str(width))
        for row in table_node.findall(w + "tr"):
            for cell, width in zip(row.findall(w + "tc"), widths):
                cell.find(w + "tcPr").find(w + "tcW").set(w + "w", str(width))
        assert sum(widths) <= available
    members["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for filename, content in members.items():
            z.writestr(filename, content)
    text = "\n".join("".join(node.text or "" for node in paragraph.iter(w + "t")) for paragraph in root.iter(w + "p"))
    # One round-trip check catches dropped headings/paragraphs/table-cell contents.
    expected = []
    for line in (OUT / (name + ".md")).read_text().splitlines():
        if not line.strip() or re.fullmatch(r"[| :\-]+", line):
            continue
        line = re.sub(r"^#{1,3} |^> ", "", line)
        if line.startswith("| "):
            expected.extend(cell.strip() for cell in line.strip("|").split("|"))
        else:
            expected.append(line)
    assert " ".join(expected).split() == text.split(), name
    paragraphs[name] = {"text_round_trip": True, "core_author_metadata_cleared": True}

pdf_cmd = [OFFICE, f"-env:UserInstallation={profile}", "--headless", "--convert-to", "pdf", "--outdir", str(OUT / "render")]
pdf_result = subprocess.run(pdf_cmd + [str(OUT / "editable" / (name + ".docx")) for name in names], check=True, text=True, capture_output=True)
import pymupdf as fitz
from PIL import Image, ImageDraw
images = []
for name in names:
    path = OUT / "render" / (name + ".pdf")
    assert path.exists(), pdf_result.stdout + pdf_result.stderr
    doc = fitz.open(path)
    paragraphs[name]["pdf_pages"] = len(doc)
    for page_num, page in enumerate(doc, 1):
        for block in page.get_text("blocks"):
            assert block[0] >= -1 and block[1] >= -1 and block[2] <= page.rect.width + 1 and block[3] <= page.rect.height + 1, (name, page_num, "outside-page text")
        pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        canvas = Image.new("RGB", (600, 870), "white")
        image.thumbnail((580, 835))
        canvas.paste(image, (10, 25))
        ImageDraw.Draw(canvas).text((10, 5), name + " / " + str(page_num), fill="black")
        images.append(canvas)
    doc.close()
for start in range(0, len(images), 6):
    sheet = Image.new("RGB", (1200, 2610), "#cccccc")
    for j, img in enumerate(images[start:start+6]):
        sheet.paste(img, ((j % 2) * 600, (j // 2) * 870))
    sheet.save(OUT / "render" / f"contact-sheet-{start//6 + 1}.png")
report = {"office_version": version, "documents": paragraphs, "contact_sheets": (len(images) + 5) // 6, "network_calls": 0}
(OUT / "native-document-check.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
