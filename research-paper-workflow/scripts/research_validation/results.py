from __future__ import annotations

import math
import json
import re
from pathlib import Path

from .common import Issue, ValidationReport, extract_text, load_csv, resolve_project_path, split_values


RESULT_COLUMNS = {
    "result_id", "label", "value", "unit", "uncertainty_type", "lower", "upper",
    "sample_n", "display_decimals", "tolerance", "source_artifact", "manuscript_targets", "status",
}


def _format_number(value: float, decimals: int) -> str:
    return f"{value:.{decimals}f}"


def _number_pattern(display: str) -> re.Pattern[str]:
    escaped = re.escape(display)
    return re.compile(rf"(?<![\w.+-]){escaped}(?![\w.])")


def _result_contexts(text: str, label: str, display: str) -> list[str]:
    pattern = _number_pattern(display)
    blocks = [block for block in re.split(r"\n\s*\n|\n", text) if block.strip()]
    return [block for block in blocks if pattern.search(block) and label.casefold() in block.casefold()]


def _source_record(path: Path, result_id: str) -> dict[str, str] | None:
    if path.suffix.lower() == ".csv":
        rows = load_csv(path)
        return next((row for row in rows if row.get("result_id") == result_id), None)
    if path.suffix.lower() == ".json":
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(value, dict) and isinstance(value.get("results"), list):
            value = value["results"]
        if isinstance(value, list):
            return next((item for item in value if isinstance(item, dict) and str(item.get("result_id", "")) == result_id), None)
        if isinstance(value, dict):
            record = value.get(result_id, value if str(value.get("result_id", "")) == result_id else None)
            return {str(key): str(item) for key, item in record.items()} if isinstance(record, dict) else None
    raise ValueError("result source must be machine-readable CSV or JSON")


def validate_results(root: Path, manifest: dict, profile: dict, report: ValidationReport) -> None:
    gate = "results"
    if "results_ledger.csv" not in profile.get("required_ledgers", []):
        return
    path = root / "results_ledger.csv"
    if not path.exists():
        report.add(Issue(gate, "error", "missing_results_ledger", "Results ledger is missing.", str(path), action="Create results_ledger.csv from frozen outputs."))
        return
    report.checked(path)
    try:
        rows = load_csv(path)
    except (OSError, ValueError) as error:
        report.add(Issue(gate, "error", "invalid_results_ledger", str(error), str(path), action="Repair the results ledger."))
        return
    if not rows:
        report.add(Issue(gate, "error", "empty_results_ledger", "Results ledger has no records.", str(path), action="Record every manuscript result."))
        return
    missing = RESULT_COLUMNS - set(rows[0])
    if missing:
        report.add(Issue(gate, "error", "results_columns", f"Missing columns: {', '.join(sorted(missing))}", str(path), action="Regenerate the ledger from the current template."))
        return

    ids: set[str] = set()
    manuscript_defaults = [str(value) for value in manifest.get("manuscript_files", [])]
    text_cache: dict[Path, str] = {}
    for index, row in enumerate(rows, start=2):
        location = f"row {index}"
        result_id = row["result_id"]
        if not result_id or result_id in ids:
            report.add(Issue(gate, "error", "result_id", "Result ID is missing or duplicated.", str(path), location, "Assign a unique result_id."))
        ids.add(result_id)
        if row["status"].lower() != "final":
            report.add(Issue(gate, "error", "nonfinal_result", f"Result {result_id} is not final.", str(path), location, "Freeze the result or remove its manuscript claim."))
        source = resolve_project_path(root, row["source_artifact"])
        if not row["source_artifact"] or not source.exists():
            report.add(Issue(gate, "error", "missing_result_source", f"Source artifact for {result_id} is missing.", str(path), location, "Restore the machine-readable result source."))
        else:
            report.checked(source)
        try:
            value = float(row["value"])
            decimals = int(row["display_decimals"] or "3")
            tolerance = float(row["tolerance"] or "0")
            sample_n = int(row["sample_n"]) if row["sample_n"] else None
            if not math.isfinite(value) or decimals < 0 or decimals > 12 or tolerance < 0:
                raise ValueError
            if sample_n is not None and (sample_n <= 0 or str(sample_n) != row["sample_n"].strip()):
                raise ValueError
        except (TypeError, ValueError):
            report.add(Issue(gate, "error", "invalid_result_value", f"Result {result_id} has invalid numeric or display settings.", str(path), location, "Correct value, display_decimals and tolerance."))
            continue
        if row["lower"] and row["upper"]:
            try:
                lower, upper = float(row["lower"]), float(row["upper"])
                if not all(math.isfinite(item) for item in (lower, upper)) or lower > value + tolerance or upper < value - tolerance or lower > upper:
                    raise ValueError
            except ValueError:
                report.add(Issue(gate, "error", "invalid_interval", f"Result {result_id} has an inconsistent interval.", str(path), location, "Correct the estimate or interval."))

        if source.exists():
            try:
                source_record = _source_record(source, result_id)
                if source_record is None:
                    raise ValueError(f"result_id {result_id} not found in source")
                comparisons = {"value": row["value"], "lower": row["lower"], "upper": row["upper"], "sample_n": row["sample_n"]}
                for field, expected in comparisons.items():
                    if not expected:
                        continue
                    actual = str(source_record.get(field, source_record.get("n", "") if field == "sample_n" else ""))
                    if not actual:
                        raise ValueError(f"source lacks {field} for {result_id}")
                    if field == "sample_n":
                        actual_number = float(actual)
                        expected_number = float(expected)
                        if not actual_number.is_integer() or not expected_number.is_integer() or int(actual_number) != int(expected_number):
                            raise ValueError(f"source {field}={actual}, ledger={expected}")
                    else:
                        actual_number = float(actual)
                        expected_number = float(expected)
                        if not math.isfinite(actual_number) or not math.isfinite(expected_number) or abs(actual_number - expected_number) > tolerance:
                            raise ValueError(f"source {field}={actual}, ledger={expected}")
            except (OSError, ValueError, json.JSONDecodeError) as error:
                report.add(Issue(gate, "error", "result_source_mismatch", str(error), str(source), action="Regenerate the ledger directly from the frozen source output."))

        targets = split_values(row["manuscript_targets"]) or manuscript_defaults
        display = _format_number(value, decimals)
        for target_value in targets:
            target = resolve_project_path(root, target_value)
            if not target.exists():
                report.add(Issue(gate, "error", "missing_manuscript_target", f"Target manuscript is missing for {result_id}.", str(target), action="Restore the manuscript or update manuscript_targets."))
                continue
            report.checked(target)
            try:
                text = text_cache.setdefault(target, extract_text(target))
            except (OSError, ValueError) as error:
                report.add(Issue(gate, "error", "unreadable_manuscript", str(error), str(target), action="Repair the manuscript file."))
                continue
            contexts = _result_contexts(text, row["label"], display)
            if not contexts:
                report.add(Issue(gate, "error", "result_not_found", f"Label '{row['label']}' and displayed value {display} for {result_id} were not found in the same manuscript block.", str(target), action="Report each labeled result and value together in the manuscript."))
            if row["sample_n"]:
                n = re.escape(row["sample_n"])
                if contexts and not any(re.search(rf"\b[nN]\s*=\s*{n}\b|\bsample(?: size)?\s+(?:of\s+)?{n}\b", context) for context in contexts):
                    report.add(Issue(gate, "error", "sample_n_not_found", f"Sample size {row['sample_n']} was not found in the same manuscript block as {result_id}.", str(target), action="Report the result and its denominator or sample size together."))
