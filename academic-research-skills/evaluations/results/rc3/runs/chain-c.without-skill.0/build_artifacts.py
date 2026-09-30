"""Local stdlib Word export and preserved-source copy; no external services."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import zipfile
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
REQUEST = HERE.parent.parent / "transfer-suite/requests/chain-c.without-skill.0.json"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W)


def word_element(parent, tag, text=None, attributes=None):
    item = ET.SubElement(parent, f"{{{W}}}{tag}", attributes or {})
    if text is not None:
        item.text = text
    return item


def paragraph(parent, text, style=None):
    p = word_element(parent, "p")
    if style:
        prop = word_element(p, "pPr")
        word_element(prop, "pStyle", attributes={f"{{{W}}}val": style})
    r = word_element(p, "r")
    t = word_element(r, "t", text)
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def docx_from_md(path):
    doc = ET.Element(f"{{{W}}}document")
    body = word_element(doc, "body")
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("|"):
            table = word_element(body, "tbl")
            pr = word_element(table, "tblPr")
            word_element(pr, "tblStyle", attributes={f"{{{W}}}val": "TableGrid"})
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [v.strip() for v in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", v) for v in cells):
                    row = word_element(table, "tr")
                    for text in cells:
                        cell = word_element(row, "tc")
                        paragraph(cell, text)
                i += 1
            continue
        heading = re.match(r"^(#{1,3}) (.*)$", line)
        if heading:
            style = "Title" if len(heading[1]) == 1 else f"Heading{len(heading[1]) - 1}"
            paragraph(body, heading[2], style)
        else:
            paragraph(body, line)
        i += 1
    section = word_element(body, "sectPr")
    word_element(section, "pgSz", attributes={f"{{{W}}}w": "11906", f"{{{W}}}h": "16838"})
    word_element(section, "pgMar", attributes={f"{{{W}}}top": "1440", f"{{{W}}}bottom": "1440", f"{{{W}}}left": "1440", f"{{{W}}}right": "1440"})
    styles = '''<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/></w:pPr><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/></w:pPr><w:rPr><w:b/></w:rPr></w:style><w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4"/><w:left w:val="single" w:sz="4"/><w:bottom w:val="single" w:sz="4"/><w:right w:val="single" w:sz="4"/><w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/></w:tblBorders></w:tblPr></w:style></w:styles>'''
    members = {
        "[Content_Types].xml": '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>''',
        "_rels/.rels": '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>''',
        "word/document.xml": ET.tostring(doc, encoding="utf-8", xml_declaration=True),
        "word/styles.xml": styles,
        "word/_rels/document.xml.rels": '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>''',
        "docProps/core.xml": '''<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>Synthetic developmental draft</dc:title><dc:creator></dc:creator><cp:lastModifiedBy></cp:lastModifiedBy></cp:coreProperties>'''
    }
    destination = path.with_suffix(".docx")
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in members.items():
            archive.writestr(name, content)
    return destination


def main():
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    material = Path(request["material_root"])
    snapshot = material / "published-snapshot-v1.md"
    copied = HERE / "preserved/published-snapshot-v1.md"
    copied.parent.mkdir(exist_ok=True)
    copied.write_bytes(snapshot.read_bytes())
    expected = next(f["sha256"] for f in request["material_files"] if f["path"] == str(snapshot))
    assert hashlib.sha256(copied.read_bytes()).hexdigest() == expected
    paths = sorted((HERE / "submission").rglob("*.md"))
    paths.append(HERE / "correction/version-correction-v1-to-v3-draft.md")
    for path in paths:
        docx_from_md(path)
    before = (material / "draft-v2.md").read_text(encoding="utf-8").splitlines(keepends=True)
    after = (HERE / "submission/review/manuscript-v3-anonymous.md").read_text(encoding="utf-8").splitlines(keepends=True)
    diff = difflib.unified_diff(before, after, fromfile="draft-v2.md", tofile="manuscript-v3-anonymous.md")
    (HERE / "reasoning/manuscript-v2-to-v3.diff").write_text("".join(diff), encoding="utf-8")
    (HERE / "build-receipt.json").write_text(json.dumps({
        "editable_docx_created": [str(p.with_suffix(".docx").relative_to(HERE)) for p in paths],
        "snapshot_sha256": expected,
        "docx_export": "stdlib OOXML; text and table export, no Word rendering performed",
        "submitted": False,
        "submission_ready": False
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"docx_created": len(paths), "snapshot_copy_hash_matches": True}))


if __name__ == "__main__":
    main()
