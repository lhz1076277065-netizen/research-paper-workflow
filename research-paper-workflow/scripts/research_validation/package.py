from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from .citations import validate_literature
from .common import (
    Issue,
    ValidationReport,
    load_csv,
    load_json,
    parse_iso_date,
    resolve_project_path,
    sha256,
    split_values,
)
from .docx import validate_docx
from .figures import validate_figures
from .profiles import load_profile
from .results import validate_results


KNOWN_GATES = (
    "artifacts", "profile", "claims", "literature", "data", "experiments", "analysis",
    "results", "figures", "docx", "language", "reproducibility",
)

CLAIM_COLUMNS = {
    "claim_id", "priority", "claim", "status", "evidence_type", "evidence_sources",
    "result_ids", "manuscript_location", "limitations", "required_action",
}
DATA_COLUMNS = {
    "dataset_id", "source", "version", "release_date", "coverage_start", "coverage_end",
    "access_date", "cutoff_date", "latest_available_date", "update_checked_at",
    "update_frequency", "license", "population", "variables", "units", "raw_location",
    "processed_location", "checksum", "coverage_status", "bias_status",
    "freshness_justification", "status",
}
EXPERIMENT_COLUMNS = {
    "experiment_id", "experiment_class", "research_question", "input_data", "method",
    "baseline_control", "metrics", "seeds_repeats", "command", "environment",
    "output_artifact", "acceptance_criterion", "status", "failure_reason",
}
DOMAIN_COLUMNS = {
    "knowledge_id", "element_type", "knowledge_element", "current_understanding",
    "authoritative_source", "competing_view", "relevance", "uncertainty",
    "manuscript_location", "status",
}
DIAGNOSTIC_COLUMNS = {
    "diagnostic_id", "category", "metric", "value", "unit", "threshold_or_comparator",
    "method", "source_artifact", "status", "interpretation",
}


def _guard_validation(report: ValidationReport, gate: str, function, *args, default=None):
    """Fail closed on malformed project artifacts without terminating the full audit."""
    try:
        return function(*args)
    except Exception as error:
        report.add(Issue(
            gate,
            "error",
            "validator_exception",
            f"{type(error).__name__}: {error}",
            action="Repair the malformed or out-of-package artifact and rerun validation.",
        ))
        return default


def _load_required_csv(root: Path, name: str, columns: set[str], gate: str, report: ValidationReport) -> list[dict[str, str]]:
    path = root / name
    if not path.exists():
        report.add(Issue(gate, "error", "missing_artifact", f"Required artifact is missing: {name}", str(path), action=f"Create {name} from the current template."))
        return []
    report.checked(path)
    try:
        rows = load_csv(path)
    except (OSError, ValueError) as error:
        report.add(Issue(gate, "error", "invalid_csv", str(error), str(path), action=f"Repair {name}."))
        return []
    if not rows:
        report.add(Issue(gate, "error", "empty_artifact", f"Required artifact has no records: {name}", str(path), action=f"Complete {name}."))
        return []
    missing = columns - set(rows[0])
    if missing:
        report.add(Issue(gate, "error", "missing_columns", f"{name} lacks columns: {', '.join(sorted(missing))}", str(path), action=f"Regenerate {name} from the current template."))
        return []
    return rows


def validate_claims(root: Path, report: ValidationReport) -> list[dict[str, str]]:
    rows = _load_required_csv(root, "claim_evidence_ledger.csv", CLAIM_COLUMNS, "claims", report)
    ids: set[str] = set()
    for index, row in enumerate(rows, start=2):
        claim_id = row["claim_id"]
        if not claim_id or claim_id in ids:
            report.add(Issue("claims", "error", "claim_id", "Claim ID is missing or duplicated.", str(root / "claim_evidence_ledger.csv"), f"row {index}", "Assign a unique claim_id."))
        ids.add(claim_id)
        if row["priority"].lower() not in {"core", "secondary", "exploratory"}:
            report.add(Issue("claims", "error", "claim_priority", f"Claim {claim_id} has an invalid priority.", str(root / "claim_evidence_ledger.csv"), f"row {index}", "Use core, secondary or exploratory."))
        if row["status"].lower() not in {"supported", "partial", "unsupported", "contradicted", "unverifiable"}:
            report.add(Issue("claims", "error", "claim_status", f"Claim {claim_id} has an invalid status.", str(root / "claim_evidence_ledger.csv"), f"row {index}", "Use a defined claim status."))
        if row["priority"].lower() == "core" and row["status"].lower() != "supported":
            report.add(Issue("claims", "error", "unsupported_core_claim", f"Core claim {claim_id} is not supported.", str(root / "claim_evidence_ledger.csv"), f"row {index}", "Generate evidence or narrow/remove the claim."))
        if not row["manuscript_location"]:
            report.add(Issue("claims", "error", "claim_location", f"Claim {claim_id} has no manuscript location.", str(root / "claim_evidence_ledger.csv"), f"row {index}", "Map the claim to manuscript text."))
    return rows


def validate_data(root: Path, profile: dict, report: ValidationReport) -> None:
    if not profile.get("require_data"):
        return
    rows = _load_required_csv(root, "data_manifest.csv", DATA_COLUMNS, "data", report)
    ids: set[str] = set()
    for index, row in enumerate(rows, start=2):
        location = f"row {index}"
        dataset_id = row["dataset_id"]
        if not dataset_id or dataset_id in ids:
            report.add(Issue("data", "error", "dataset_id", "Dataset ID is missing or duplicated.", str(root / "data_manifest.csv"), location, "Assign a unique dataset_id."))
        ids.add(dataset_id)
        for field in ("release_date", "access_date", "cutoff_date", "latest_available_date", "update_checked_at"):
            try:
                parsed = parse_iso_date(row[field])
                if parsed is None:
                    raise ValueError
            except ValueError:
                report.add(Issue("data", "error", "invalid_date", f"{dataset_id} has invalid or missing {field}.", str(root / "data_manifest.csv"), location, "Use YYYY-MM-DD and document the update check."))
        try:
            cutoff = parse_iso_date(row["cutoff_date"])
            latest = parse_iso_date(row["latest_available_date"])
            if cutoff and latest and cutoff < latest and not row["freshness_justification"]:
                report.add(Issue("data", "error", "stale_data", f"{dataset_id} excludes newer available data without justification.", str(root / "data_manifest.csv"), location, "Update the dataset or document a defensible exclusion."))
        except ValueError:
            pass
        for field in ("raw_location", "processed_location"):
            target = resolve_project_path(root, row[field]) if row[field] else None
            if not target or not target.exists():
                report.add(Issue("data", "error", "missing_data_file", f"{dataset_id} lacks {field}.", str(root / "data_manifest.csv"), location, "Restore the declared data artifact."))
            else:
                report.checked(target)
        processed = resolve_project_path(root, row["processed_location"]) if row["processed_location"] else None
        if not row["checksum"]:
            report.add(Issue("data", "error", "missing_checksum", f"Dataset {dataset_id} has no processed-data checksum.", str(root / "data_manifest.csv"), location, "Record the SHA-256 checksum of the frozen processed data."))
        elif processed and processed.exists() and sha256(processed).lower() != row["checksum"].lower():
            report.add(Issue("data", "error", "checksum_mismatch", f"Checksum mismatch for {dataset_id}.", str(processed), action="Freeze and re-register the processed data release."))
        if row["coverage_status"].lower() != "complete":
            report.add(Issue("data", "error", "coverage_incomplete", f"Coverage audit for {dataset_id} is not complete.", str(root / "data_manifest.csv"), location, "Complete the coverage matrix or narrow claims."))
        if row["bias_status"].lower() not in {"assessed", "mitigated"}:
            report.add(Issue("data", "error", "bias_unassessed", f"Bias audit for {dataset_id} is incomplete.", str(root / "data_manifest.csv"), location, "Assess selection, measurement and source bias."))
        if row["status"].lower() != "frozen":
            report.add(Issue("data", "error", "data_not_frozen", f"Dataset {dataset_id} is not frozen.", str(root / "data_manifest.csv"), location, "Freeze one versioned analysis release."))


def validate_experiments(root: Path, profile: dict, report: ValidationReport) -> None:
    rows = _load_required_csv(root, "experiment_manifest.csv", EXPERIMENT_COLUMNS, "experiments", report)
    present_classes: set[str] = set()
    ids: set[str] = set()
    for index, row in enumerate(rows, start=2):
        location = f"row {index}"
        experiment_id = row["experiment_id"]
        if not experiment_id or experiment_id in ids:
            report.add(Issue("experiments", "error", "experiment_id", "Experiment ID is missing or duplicated.", str(root / "experiment_manifest.csv"), location, "Assign a unique experiment_id."))
        ids.add(experiment_id)
        present_classes.add(row["experiment_class"])
        if row["status"].lower() != "complete":
            report.add(Issue("experiments", "error", "experiment_incomplete", f"Experiment {experiment_id} is not complete.", str(root / "experiment_manifest.csv"), location, "Run, repair or explicitly remove the affected claim."))
        if not row["command"] or not row["environment"]:
            report.add(Issue("reproducibility", "error", "experiment_provenance", f"Experiment {experiment_id} lacks command or environment.", str(root / "experiment_manifest.csv"), location, "Record the exact command and environment."))
        output = resolve_project_path(root, row["output_artifact"]) if row["output_artifact"] else None
        if not output or not output.exists():
            report.add(Issue("experiments", "error", "missing_experiment_output", f"Experiment {experiment_id} lacks its output artifact.", str(root / "experiment_manifest.csv"), location, "Restore or rerun the experiment."))
        else:
            report.checked(output)
    required = set(profile.get("required_experiment_classes", []))
    missing = required - present_classes
    if missing:
        report.add(Issue("experiments", "error", "missing_experiment_classes", f"Missing experiment classes: {', '.join(sorted(missing))}", str(root / "experiment_manifest.csv"), action="Complete the profile-required experiment matrix."))
    if profile.get("require_external_validation") and "external_validation" not in present_classes:
        report.add(Issue("experiments", "error", "external_validation", "Profile requires external validation.", str(root / "experiment_manifest.csv"), action="Add an independent external-validation experiment."))


def validate_domain(root: Path, profile: dict, report: ValidationReport) -> None:
    rows = _load_required_csv(root, "domain_knowledge_map.csv", DOMAIN_COLUMNS, "profile", report)
    present = {row["element_type"] for row in rows if row["status"].lower() == "verified"}
    for index, row in enumerate(rows, start=2):
        if not row["authoritative_source"]:
            report.add(Issue("profile", "error", "domain_source", f"Domain element {row['knowledge_id']} lacks an authoritative source.", str(root / "domain_knowledge_map.csv"), f"row {index}", "Add a standard, authoritative review or primary source."))
        if row["status"].lower() != "verified":
            report.add(Issue("profile", "error", "domain_unverified", f"Domain element {row['knowledge_id']} is not verified.", str(root / "domain_knowledge_map.csv"), f"row {index}", "Verify the knowledge element and its source."))
    missing = set(profile.get("required_domain_elements", [])) - present
    if missing:
        report.add(Issue("profile", "error", "domain_elements", f"Missing verified domain elements: {', '.join(sorted(missing))}", str(root / "domain_knowledge_map.csv"), action="Complete the profile-specific domain knowledge map."))


def validate_analysis(root: Path, manifest: dict, profile: dict, report: ValidationReport) -> None:
    rows = _load_required_csv(root, "analysis_diagnostics.csv", DIAGNOSTIC_COLUMNS, "analysis", report)
    present = {row["category"] for row in rows if row["status"].lower() in {"pass", "complete"}}
    for index, row in enumerate(rows, start=2):
        source = resolve_project_path(root, row["source_artifact"]) if row["source_artifact"] else None
        if not source or not source.exists():
            report.add(Issue("analysis", "error", "diagnostic_source", f"Diagnostic {row['diagnostic_id']} lacks a source artifact.", str(root / "analysis_diagnostics.csv"), f"row {index}", "Preserve the machine-readable diagnostic output."))
        else:
            report.checked(source)
        if row["status"].lower() not in {"pass", "complete"}:
            report.add(Issue("analysis", "error", "diagnostic_failed", f"Diagnostic {row['diagnostic_id']} did not pass.", str(root / "analysis_diagnostics.csv"), f"row {index}", "Repair the analysis or narrow the claim."))
    missing = set(profile.get("required_analysis_diagnostics", [])) - present
    if missing:
        report.add(Issue("analysis", "error", "missing_diagnostics", f"Missing analysis diagnostics: {', '.join(sorted(missing))}", str(root / "analysis_diagnostics.csv"), action="Complete profile-required diagnostics."))
    if profile.get("require_sem"):
        files = [resolve_project_path(root, value) for value in manifest.get("sem_model_files", [])]
        if not files:
            report.add(Issue("analysis", "error", "missing_sem_model", "SEM profile has no native SmartPLS, AMOS or equivalent model artifact.", str(root / "research_manifest.json"), action="Preserve the genuine native model file and exported results."))
        for path in files:
            if not path.exists():
                report.add(Issue("analysis", "error", "missing_sem_model", "Declared SEM model artifact is missing.", str(path), action="Restore the native model artifact."))
            else:
                report.checked(path)


def validate_language(root: Path, manuscript_paths: list[Path], report: ValidationReport) -> None:
    if not manuscript_paths:
        return
    script = Path(__file__).resolve().parents[1] / "audit_manuscript_language.py"
    command = [sys.executable, str(script), *[str(path) for path in manuscript_paths], "--json", "--fail-on", "none", "--language", "auto"]
    environment = dict(os.environ)
    environment["PYTHONIOENCODING"] = "utf-8"
    process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", env=environment)
    if process.returncode != 0:
        report.add(Issue("language", "error", "language_scan_error", process.stderr or process.stdout, str(script), action="Repair and rerun the language scanner."))
        return
    try:
        payload = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        report.add(Issue("language", "error", "language_scan_json", str(error), str(script), action="Repair the language scanner output."))
        return
    for finding in payload.get("findings", []):
        severity = "error" if finding.get("severity") in {"high", "medium"} else "warning"
        report.add(Issue(
            "language", severity, finding.get("rule_id", "language_finding"),
            f"{finding.get('match')}: {finding.get('excerpt')}", finding.get("file", ""),
            finding.get("location", ""), finding.get("guidance", "Rewrite in academic language."),
        ))


def validate_project(root: Path, profile_override: str = "auto") -> ValidationReport:
    root = root.expanduser().resolve()
    manifest_path = root / "research_manifest.json"
    provisional = ValidationReport(str(root), profile_override)
    if not manifest_path.exists():
        provisional.add(Issue("artifacts", "error", "missing_manifest", "research_manifest.json is missing.", str(manifest_path), action="Run init_research_project.py and map existing artifacts."))
        provisional.finalize(KNOWN_GATES)
        return provisional
    provisional.checked(manifest_path)
    try:
        manifest = load_json(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        provisional.add(Issue("artifacts", "error", "invalid_manifest", str(error), str(manifest_path), action="Repair research_manifest.json."))
        provisional.finalize(KNOWN_GATES)
        return provisional
    if manifest.get("schema_version") != "2.0":
        provisional.add(Issue("artifacts", "error", "schema_version", "Manifest schema_version must be 2.0.", str(manifest_path), action="Migrate using the current templates."))
    profile_id = manifest.get("article_type", "") if profile_override == "auto" else profile_override
    try:
        profile = load_profile(profile_id)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        provisional.profile = profile_id
        provisional.add(Issue("profile", "error", "invalid_profile", str(error), str(manifest_path), action="Select one supported article_type."))
        provisional.finalize(KNOWN_GATES)
        return provisional
    report = provisional
    report.profile = profile_id

    for name in profile.get("required_ledgers", []):
        if not (root / name).exists():
            report.add(Issue("artifacts", "error", "missing_required_ledger", f"Profile requires {name}.", str(root / name), action="Create and complete the required ledger."))

    manuscript_values = manifest.get("manuscript_files", [])
    if not isinstance(manuscript_values, list):
        report.add(Issue("artifacts", "error", "invalid_manuscript_list", "manuscript_files must be a JSON array.", str(manifest_path), action="List every manuscript path in a JSON array."))
        manuscript_values = []
    manuscript_paths: list[Path] = []
    for value in manuscript_values:
        try:
            manuscript_paths.append(resolve_project_path(root, str(value)))
        except ValueError as error:
            report.add(Issue("artifacts", "error", "external_artifact", str(error), str(manifest_path), action="Copy the manuscript into the project package and use a relative path."))
    if not manuscript_paths:
        report.add(Issue("artifacts", "error", "missing_manuscript", "Manifest lists no manuscript files.", str(manifest_path), action="Create the manuscript and add its path."))
    for path in manuscript_paths:
        if not path.exists():
            report.add(Issue("artifacts", "error", "missing_manuscript", "Declared manuscript file is missing.", str(path), action="Restore or correct the manuscript path."))
        else:
            report.checked(path)
            if path.suffix.lower() == ".docx":
                _guard_validation(report, "docx", validate_docx, path, report)

    claim_rows = _guard_validation(report, "claims", validate_claims, root, report, default=[]) or []
    _guard_validation(report, "literature", validate_literature, root, manifest, profile, report, claim_rows)
    _guard_validation(report, "data", validate_data, root, profile, report)
    _guard_validation(report, "experiments", validate_experiments, root, profile, report)
    _guard_validation(report, "profile", validate_domain, root, profile, report)
    _guard_validation(report, "analysis", validate_analysis, root, manifest, profile, report)
    _guard_validation(report, "results", validate_results, root, manifest, profile, report)
    result_ids = set()
    results_path = root / "results_ledger.csv"
    if results_path.exists():
        try:
            result_ids = {row.get("result_id", "") for row in load_csv(results_path)}
        except (OSError, ValueError):
            pass
    _guard_validation(report, "figures", validate_figures, root, manifest, profile, report, result_ids)
    _guard_validation(report, "language", validate_language, root, [path for path in manuscript_paths if path.exists()], report)
    report.finalize(KNOWN_GATES)
    return report
