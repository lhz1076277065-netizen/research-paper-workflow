from __future__ import annotations

import csv
import hashlib
import json
import re
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree


SEVERITY_RANK = {"info": 0, "warning": 1, "error": 2}


@dataclass(frozen=True)
class Issue:
    gate: str
    severity: str
    code: str
    message: str
    artifact: str = ""
    location: str = ""
    action: str = ""


@dataclass
class ValidationReport:
    project_root: str
    profile: str
    issues: list[Issue] = field(default_factory=list)
    artifacts_checked: list[str] = field(default_factory=list)
    gates: dict[str, str] = field(default_factory=dict)

    def add(self, issue: Issue) -> None:
        if issue.severity not in SEVERITY_RANK:
            raise ValueError(f"unknown severity: {issue.severity}")
        self.issues.append(issue)

    def checked(self, path: Path) -> None:
        value = str(path)
        if value not in self.artifacts_checked:
            self.artifacts_checked.append(value)

    def finalize(self, known_gates: Iterable[str]) -> None:
        for gate in known_gates:
            relevant = [item for item in self.issues if item.gate == gate]
            if any(item.severity == "error" for item in relevant):
                self.gates[gate] = "fail"
            elif any(item.severity == "warning" for item in relevant):
                self.gates[gate] = "warning"
            else:
                self.gates[gate] = "pass"

    @property
    def decision(self) -> str:
        return "not_ready" if any(item.severity == "error" for item in self.issues) else "ready"

    def to_dict(self) -> dict:
        ordered = sorted(
            self.issues,
            key=lambda item: (-SEVERITY_RANK[item.severity], item.gate, item.artifact, item.location, item.code),
        )
        return {
            "decision": self.decision,
            "profile": self.profile,
            "project_root": self.project_root,
            "gates": self.gates,
            "errors": [asdict(item) for item in ordered if item.severity == "error"],
            "warnings": [asdict(item) for item in ordered if item.severity == "warning"],
            "info": [asdict(item) for item in ordered if item.severity == "info"],
            "artifacts_checked": sorted(self.artifacts_checked),
            "required_actions": sorted({item.action for item in ordered if item.action}),
        }


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        headers = [header.strip() if header else "" for header in reader.fieldnames]
        if any(not header for header in headers):
            raise ValueError(f"CSV has an empty header: {path}")
        if len(headers) != len(set(headers)):
            raise ValueError(f"CSV has duplicate headers: {path}")
        rows: list[dict[str, str]] = []
        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"CSV row {line_number} has more fields than the header: {path}")
            normalized: dict[str, str] = {}
            for key, value in row.items():
                if not isinstance(value, str) and value is not None:
                    raise ValueError(f"CSV row {line_number} has an invalid field: {path}")
                normalized[str(key).strip()] = (value or "").strip()
            rows.append(normalized)
        return rows


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def split_values(value: str) -> list[str]:
    return [item.strip() for item in re.split(r"[;|]", value or "") if item.strip()]


def parse_bool(value: str | bool | None) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def normalize_doi(value: str) -> str:
    value = (value or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if value.startswith(prefix):
            return value[len(prefix):].strip()
    return value


def parse_iso_date(value: str) -> date | None:
    value = (value or "").strip()
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def resolve_project_path(root: Path, value: str) -> Path:
    root = root.resolve()
    candidate = Path(value)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if not ensure_within(root, resolved):
        raise ValueError(f"project artifact escapes the project root: {value}")
    return resolved


def ensure_within(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root.resolve())
        return True
    except ValueError:
        return False


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def required_columns(rows: list[dict[str, str]], columns: set[str], path: Path) -> list[Issue]:
    if not rows:
        return [Issue("artifacts", "error", "empty_csv", "CSV contains no records.", str(path), action="Add required records.")]
    missing = columns - set(rows[0])
    if not missing:
        return []
    return [Issue(
        "artifacts",
        "error",
        "missing_columns",
        f"CSV is missing columns: {', '.join(sorted(missing))}",
        str(path),
        action="Regenerate the artifact from the current template.",
    )]


def extract_text(path: Path) -> str:
    if path.suffix.lower() == ".docx":
        with zipfile.ZipFile(path) as archive:
            xml = archive.read("word/document.xml")
        root = ElementTree.fromstring(xml)
        namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
        paragraphs = []
        for paragraph in root.iter(f"{namespace}p"):
            value = "".join(node.text or "" for node in paragraph.iter(f"{namespace}t"))
            if value.strip():
                paragraphs.append(value)
        return "\n".join(paragraphs)
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"unsupported text encoding: {path}")
