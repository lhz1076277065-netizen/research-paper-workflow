from __future__ import annotations

import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from .common import Issue, ValidationReport


W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
PRIVATE_PATH = re.compile(r"(?:file:/+|[A-Za-z]:[\\/]|/Users/|/home/)", re.IGNORECASE)


def _xml(archive: zipfile.ZipFile, name: str) -> ElementTree.Element | None:
    try:
        return ElementTree.fromstring(archive.read(name))
    except KeyError:
        return None


def validate_docx(path: Path, report: ValidationReport) -> None:
    gate = "docx"
    report.checked(path)
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            document = _xml(archive, "word/document.xml")
            if document is None:
                raise ValueError("DOCX lacks word/document.xml")
            story_names = [name for name in names if re.fullmatch(r"word/(?:document|header\d+|footer\d+|footnotes|endnotes|comments)\.xml", name)]
            stories = [(name, _xml(archive, name)) for name in story_names]
            roots = [root for _, root in stories if root is not None]
            checks = {
                "tracked_insertions": sum(len(list(root.iter(f"{W}ins"))) for root in roots),
                "tracked_deletions": sum(len(list(root.iter(f"{W}del"))) for root in roots),
                "tracked_moves": sum(len(list(root.iter(f"{W}moveFrom"))) + len(list(root.iter(f"{W}moveTo"))) for root in roots),
                "comment_ranges": sum(len(list(root.iter(f"{W}commentRangeStart"))) for root in roots),
                "hidden_text": sum(len(list(root.iter(f"{W}vanish"))) for root in roots),
            }
            for code, count in checks.items():
                if count:
                    report.add(Issue(gate, "error", code, f"DOCX contains {count} {code.replace('_', ' ')} element(s).", str(path), action="Accept or remove all revisions, comments and hidden text."))

            comments = _xml(archive, "word/comments.xml")
            if comments is not None and list(comments.iter(f"{W}comment")):
                report.add(Issue(gate, "error", "comments_present", "DOCX contains comments.", str(path), action="Resolve and remove all comments."))

            bookmarks = {item.get(f"{W}name", "") for root in roots for item in root.iter(f"{W}bookmarkStart")}
            field_text = " ".join(item.text or "" for root in roots for item in root.iter(f"{W}instrText"))
            for target in re.findall(r"\bREF\s+([A-Za-z0-9_]+)", field_text, flags=re.IGNORECASE):
                if target not in bookmarks:
                    report.add(Issue(gate, "error", "broken_cross_reference", f"REF field targets missing bookmark '{target}'.", str(path), action="Repair and update all cross-references."))
            if any(item.get(f"{W}dirty", "").lower() in {"true", "1"} for root in roots for item in root.iter()):
                report.add(Issue(gate, "warning", "dirty_fields", "DOCX contains fields marked for update.", str(path), action="Update all fields and regenerate the final file."))

            relationship_names = [name for name in names if re.fullmatch(r"word/_rels/.+\.xml\.rels", name)]
            for relationship_name in relationship_names:
                relationships = _xml(archive, relationship_name)
                if relationships is None:
                    continue
                source_name = "word/" + posixpath.basename(relationship_name).removesuffix(".rels")
                source_directory = posixpath.dirname(source_name)
                for relation in relationships.iter(f"{PKG_REL}Relationship"):
                    target = relation.get("Target", "")
                    target_mode = relation.get("TargetMode", "")
                    if PRIVATE_PATH.search(target):
                        report.add(Issue(gate, "error", "private_relationship", f"DOCX relationship exposes a private path: {target}", str(path), action="Remove private and local filesystem relationships."))
                    if target_mode.lower() != "external":
                        resolved = posixpath.normpath(posixpath.join(source_directory, target))
                        if resolved not in names:
                            report.add(Issue(gate, "error", "broken_relationship", f"DOCX relationship target is missing: {target}", str(path), action="Repair missing media or embedded objects."))

            for name in ("docProps/core.xml", "docProps/custom.xml"):
                if name not in names:
                    continue
                content = archive.read(name).decode("utf-8", errors="ignore")
                if PRIVATE_PATH.search(content):
                    report.add(Issue(gate, "error", "private_metadata", f"DOCX metadata contains a private path in {name}.", str(path), action="Remove private paths from document properties."))
                if name == "docProps/core.xml":
                    properties = ElementTree.fromstring(content)
                    metadata = [item for item in properties.iter() if item.tag.rsplit("}", 1)[-1] in {"creator", "lastModifiedBy"} and (item.text or "").strip()]
                    if metadata:
                        report.add(Issue(gate, "warning", "author_metadata", "DOCX retains creator or last-modified author metadata.", str(path), action="Confirm author metadata is intentional for submission."))
    except (OSError, ValueError, zipfile.BadZipFile, ElementTree.ParseError) as error:
        report.add(Issue(gate, "error", "invalid_docx", str(error), str(path), action="Repair or regenerate the DOCX file."))
