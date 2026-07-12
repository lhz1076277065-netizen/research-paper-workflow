from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from .common import Issue, ValidationReport, extract_text, load_csv, load_json, normalize_doi, parse_bool, resolve_project_path, split_values


DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
LITERATURE_COLUMNS = {
    "reference_id", "in_text_key", "title", "authors", "year", "journal", "document_type", "doi",
    "wos_index", "jcr_year", "jcr_category", "jcr_quartile", "foundational",
    "core_claim_ids", "source_file", "retracted_or_corrected", "verification_status",
}
JCR_COLUMNS = {"journal", "issn", "jcr_year", "jcr_category", "jcr_quartile", "source_export", "verified_at"}


def _tagged_records(text: str, separator: re.Pattern[str], end_tag: str) -> list[dict[str, list[str]]]:
    records: list[dict[str, list[str]]] = []
    current: dict[str, list[str]] = {}
    for raw in text.splitlines():
        match = separator.match(raw)
        if not match:
            continue
        tag, value = match.group(1), match.group(2).strip()
        if tag == end_tag:
            if current:
                records.append(current)
            current = {}
        else:
            current.setdefault(tag, []).append(value)
    if current:
        records.append(current)
    return records


def parse_ciw(path: Path) -> list[dict[str, str]]:
    tagged = _tagged_records(path.read_text(encoding="utf-8-sig"), re.compile(r"^([A-Z0-9]{2})\s+(.*)$"), "ER")
    return [{
        "reference_id": values.get("UT", [""])[0],
        "title": " ".join(values.get("TI", [])),
        "authors": "; ".join(values.get("AU", [])),
        "year": values.get("PY", [""])[0],
        "journal": values.get("SO", [""])[0],
        "doi": values.get("DI", [""])[0],
        "document_type": values.get("DT", [""])[0],
    } for values in tagged]


def parse_ris(path: Path) -> list[dict[str, str]]:
    tagged = _tagged_records(path.read_text(encoding="utf-8-sig"), re.compile(r"^([A-Z0-9]{2})\s*-\s*(.*)$"), "ER")
    records = []
    for values in tagged:
        year = values.get("PY", values.get("Y1", [""]))[0][:4]
        records.append({
            "reference_id": values.get("ID", [""])[0],
            "title": values.get("TI", values.get("T1", [""]))[0],
            "authors": "; ".join(values.get("AU", values.get("A1", []))),
            "year": year,
            "journal": values.get("JO", values.get("T2", [""]))[0],
            "doi": values.get("DO", [""])[0],
            "document_type": values.get("TY", [""])[0],
        })
    return records


def parse_bibtex(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8-sig")
    records: list[dict[str, str]] = []
    for match in re.finditer(r"@(\w+)\s*\{\s*([^,]+),(.*?)(?=\n@|\Z)", text, re.IGNORECASE | re.DOTALL):
        entry_type, key, body = match.groups()
        fields: dict[str, str] = {}
        for field in re.finditer(r"(\w+)\s*=\s*(?:\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|\"([^\"]*)\")\s*,?", body, re.DOTALL):
            fields[field.group(1).lower()] = re.sub(r"\s+", " ", field.group(2) or field.group(3) or "").strip()
        records.append({
            "reference_id": key.strip(),
            "title": fields.get("title", ""),
            "authors": fields.get("author", "").replace(" and ", "; "),
            "year": fields.get("year", ""),
            "journal": fields.get("journal", fields.get("booktitle", "")),
            "doi": fields.get("doi", ""),
            "document_type": entry_type.lower(),
        })
    return records


def parse_reference_export(path: Path) -> list[dict[str, str]]:
    suffix = path.suffix.lower()
    if suffix == ".ciw":
        return parse_ciw(path)
    if suffix == ".ris":
        return parse_ris(path)
    if suffix in {".bib", ".bibtex"}:
        return parse_bibtex(path)
    if suffix == ".csv":
        return load_csv(path)
    raise ValueError(f"unsupported reference export: {path}")


def validate_literature(
    root: Path,
    manifest: dict,
    profile: dict,
    report: ValidationReport,
    claim_rows: list[dict[str, str]],
) -> None:
    gate = "literature"
    path = root / "literature_matrix.csv"
    if not path.exists():
        report.add(Issue(gate, "error", "missing_literature_matrix", "Literature matrix is missing.", str(path), action="Create literature_matrix.csv from the template."))
        return
    report.checked(path)
    try:
        rows = load_csv(path)
    except (OSError, ValueError) as error:
        report.add(Issue(gate, "error", "invalid_literature_matrix", str(error), str(path), action="Repair the literature matrix."))
        return
    if not rows:
        report.add(Issue(gate, "error", "empty_literature_matrix", "Literature matrix has no references.", str(path), action="Run and document the literature search."))
        return
    missing = LITERATURE_COLUMNS - set(rows[0])
    if missing:
        report.add(Issue(gate, "error", "literature_columns", f"Missing columns: {', '.join(sorted(missing))}", str(path), action="Regenerate the literature matrix from the current template."))
        return

    exception = manifest.get("recent_q1q2_exception", {})
    exception_approved = bool(exception.get("approved")) and bool(str(exception.get("reason", "")).strip())
    exception_evidence = resolve_project_path(root, str(exception.get("evidence_file", ""))) if exception.get("evidence_file") else None
    if exception_approved:
        if not exception_evidence or not exception_evidence.exists():
            report.add(Issue(gate, "error", "invalid_q1q2_exception", "Q1/Q2 exception lacks its evidence file.", str(root / "research_manifest.json"), action="Preserve search evidence supporting the field-scarcity exception."))
            exception_approved = False
        else:
            report.checked(exception_evidence)

    metrics_path = root / "journal_metrics.csv"
    metric_keys: set[tuple[str, str, str, str]] = set()
    if not metrics_path.exists():
        report.add(Issue(gate, "error", "missing_jcr_export", "journal_metrics.csv is missing.", str(metrics_path), action="Import and document a legitimate JCR export."))
    else:
        report.checked(metrics_path)
        try:
            metric_rows = load_csv(metrics_path)
        except (OSError, ValueError) as error:
            report.add(Issue(gate, "error", "invalid_jcr_export", str(error), str(metrics_path), action="Repair journal_metrics.csv."))
            metric_rows = []
        if not metric_rows or JCR_COLUMNS - set(metric_rows[0]):
            report.add(Issue(gate, "error", "invalid_jcr_export", "journal_metrics.csv is empty or has invalid columns.", str(metrics_path), action="Regenerate journal_metrics.csv from the current template."))
        else:
            for metric_index, metric in enumerate(metric_rows, start=2):
                key = (metric["journal"].casefold(), metric["jcr_year"], metric["jcr_category"].casefold(), metric["jcr_quartile"].upper())
                metric_keys.add(key)
                export_path = resolve_project_path(root, metric["source_export"]) if metric["source_export"] else None
                if not export_path or not export_path.exists():
                    report.add(Issue(gate, "error", "missing_jcr_source", "JCR metric lacks its legitimate source export.", str(metrics_path), f"row {metric_index}", "Preserve the JCR export used for quartile verification."))
                else:
                    report.checked(export_path)
                if not metric["verified_at"]:
                    report.add(Issue(gate, "error", "jcr_verification_date", "JCR metric lacks a verification date.", str(metrics_path), f"row {metric_index}", "Record the JCR verification date."))

    manuscript_text = "\n".join(
        extract_text(resolve_project_path(root, value))
        for value in manifest.get("manuscript_files", [])
        if resolve_project_path(root, value).exists()
    )
    ids: set[str] = set()
    dois: set[str] = set()
    recent_high_tier = 0
    nonfoundational_journal = 0
    minimum_year = date.today().year - 4
    for index, row in enumerate(rows, start=2):
        location = f"row {index}"
        reference_id = row["reference_id"]
        if not reference_id or reference_id in ids:
            report.add(Issue(gate, "error", "reference_id", "Reference ID is missing or duplicated.", str(path), location, "Assign a unique reference_id."))
        ids.add(reference_id)
        if not row["in_text_key"]:
            report.add(Issue(gate, "error", "missing_in_text_key", "Reference has no exact in-text citation key.", str(path), location, "Record the exact citation string used in the manuscript."))
        elif row["in_text_key"] not in manuscript_text:
            report.add(Issue(gate, "error", "uncited_reference", f"Reference {reference_id} was not found in manuscript text.", str(path), location, "Cite the reference where its supported claim occurs or remove it."))
        doi = normalize_doi(row["doi"])
        if doi:
            if not DOI_RE.match(doi):
                report.add(Issue(gate, "error", "invalid_doi", f"Invalid DOI: {row['doi']}", str(path), location, "Verify the DOI against the source."))
            if doi in dois:
                report.add(Issue(gate, "error", "duplicate_doi", f"Duplicate DOI: {doi}", str(path), location, "Deduplicate the bibliography."))
            dois.add(doi)
        if row["retracted_or_corrected"].lower() == "retracted":
            report.add(Issue(gate, "error", "retracted_reference", "Retracted reference supports the manuscript.", str(path), location, "Remove or explicitly handle the retracted evidence."))
        if row["verification_status"].lower() != "verified":
            report.add(Issue(gate, "error", "unverified_reference", "Reference metadata or source inspection is unverified.", str(path), location, "Open the source and verify metadata and claim support."))
        source_file = row["source_file"]
        if source_file:
            source_path = resolve_project_path(root, source_file)
            if not source_path.exists():
                report.add(Issue(gate, "error", "missing_source_file", "Inspected source file is missing.", str(path), location, "Restore the inspected source or update source_file."))
            else:
                report.checked(source_path)

        if row["jcr_quartile"]:
            metric_key = (row["journal"].casefold(), row["jcr_year"], row["jcr_category"].casefold(), row["jcr_quartile"].upper())
            if metric_key not in metric_keys:
                report.add(Issue(gate, "error", "unmatched_jcr_metric", "Reference quartile is not supported by journal_metrics.csv.", str(path), location, "Match the reference to a preserved JCR export record."))

        is_foundational = parse_bool(row["foundational"])
        is_journal = row["document_type"].lower() in {"article", "journal article", "review", "article; early access"}
        if not is_foundational and is_journal:
            nonfoundational_journal += 1
            try:
                year = int(row["year"])
            except ValueError:
                year = 0
                report.add(Issue(gate, "error", "invalid_year", "Reference year is invalid.", str(path), location, "Set a four-digit publication year."))
            if year >= minimum_year and row["jcr_quartile"].upper() in {"Q1", "Q2"} and row["wos_index"]:
                recent_high_tier += 1

    target = float(profile.get("recent_q1q2_target", 0.7))
    ratio = recent_high_tier / nonfoundational_journal if nonfoundational_journal else 0.0
    if nonfoundational_journal == 0 or ratio < target:
        severity = "warning" if exception_approved else "error"
        report.add(Issue(
            gate, severity, "recent_q1q2_ratio",
            f"Recent verified WoS/JCR Q1-Q2 ratio is {ratio:.1%}; required target is {target:.1%}.",
            str(path), action="Add eligible recent high-tier sources or document an approved field-scarcity exception.",
        ))

    core_claims = [row for row in claim_rows if row.get("priority", "").lower() == "core"]
    for claim in core_claims:
        evidence_ids = set(split_values(claim.get("evidence_sources", "")))
        if not evidence_ids:
            report.add(Issue(gate, "error", "uncited_core_claim", f"Core claim {claim.get('claim_id')} has no direct source.", str(root / "claim_evidence_ledger.csv"), action="Map the claim to directly inspected references."))
        unknown = evidence_ids - ids
        if unknown:
            report.add(Issue(gate, "error", "unknown_reference", f"Core claim cites unknown references: {', '.join(sorted(unknown))}", str(root / "claim_evidence_ledger.csv"), action="Correct the claim-reference mapping."))

    cache_value = manifest.get("citation_metadata_cache", "")
    if cache_value:
        cache_path = resolve_project_path(root, cache_value)
        if cache_path.exists():
            report.checked(cache_path)
            try:
                cache = load_json(cache_path)
                for doi, metadata in cache.get("records", {}).items():
                    if metadata.get("retracted") is True:
                        report.add(Issue(gate, "error", "cached_retraction", f"Metadata cache flags DOI {doi} as retracted.", str(cache_path), action="Verify and remove or explicitly handle the retracted work."))
            except (OSError, ValueError, json.JSONDecodeError) as error:
                report.add(Issue(gate, "error", "invalid_citation_cache", str(error), str(cache_path), action="Refresh the citation metadata cache."))
        else:
            report.add(Issue(gate, "warning", "missing_citation_cache", "Citation metadata cache is missing.", str(cache_path), action="Run refresh_literature_metadata.py --online or provide a frozen cache."))

    references_value = manifest.get("references_file", "")
    if references_value:
        references_path = resolve_project_path(root, references_value)
        if not references_path.exists():
            report.add(Issue(gate, "error", "missing_reference_export", "Declared reference export is missing.", str(references_path), action="Restore the CIW, RIS, BibTeX or CSV export."))
        else:
            report.checked(references_path)
            try:
                exported = parse_reference_export(references_path)
                if not exported:
                    raise ValueError("reference export contains no records")
                matrix_dois = {normalize_doi(row["doi"]) for row in rows if row["doi"]}
                export_dois = {normalize_doi(row.get("doi", "")) for row in exported if row.get("doi")}
                missing_from_export = matrix_dois - export_dois
                missing_from_matrix = export_dois - matrix_dois
                if missing_from_export:
                    report.add(Issue(gate, "error", "bibliography_missing_references", f"Reference export lacks matrix DOI(s): {', '.join(sorted(missing_from_export))}", str(references_path), action="Synchronize the bibliography export with the literature matrix."))
                if missing_from_matrix:
                    report.add(Issue(gate, "error", "unregistered_bibliography_entries", f"Reference export contains unregistered DOI(s): {', '.join(sorted(missing_from_matrix))}", str(references_path), action="Add inspected sources to the literature matrix or remove uncited entries."))
            except (OSError, ValueError) as error:
                report.add(Issue(gate, "error", "invalid_reference_export", str(error), str(references_path), action="Regenerate the reference export."))
