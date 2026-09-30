"""SYNTHETIC: runnable data, numeric, text and figure checks; not human approval."""
from pathlib import Path
from datetime import datetime, timezone
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from analysis import ROOT, WEIGHTS, prepare_events, pair_units, read_member
from prepare import EXPECTED_SHA256, CORRECTION_SHA256, VENDOR_HASHES


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rejects(function, *arguments):
    try:
        function(*arguments)
    except ValueError:
        return
    raise AssertionError("Malformed input was silently accepted")


def run():
    checked_at = datetime.now(timezone.utc).isoformat()
    identity = json.loads((ROOT / "archive_identity.json").read_text())
    assert sha(Path(identity["source"])) == sha(ROOT / "inputs/paired-measurements-v2.zip") == EXPECTED_SHA256
    assert sha(ROOT / "inputs/approved-correction.json") == CORRECTION_SHA256
    correction = json.loads((ROOT / "correction_dependency_audit.json").read_text())
    assert correction["changed_raw_rows_including_copy"] == 3
    assert correction["changed_unique_events"] == 2 and correction["unchanged_raw_rows"] == 40
    assert all(correction["byte_identical_members"].values())
    assert correction["dictionary_original_definitions_retained"]
    old_files = json.loads((ROOT / "old_outputs_identity_before.json").read_text())["files"]
    assert all(sha(ROOT.parent / name) == digest for name, digest in old_files.items())
    assert sha(ROOT / "analysis.py") == sha(ROOT.parent / "analysis.py")
    for member in identity["members"]:
        assert sha(ROOT / "inputs/original" / member["path"]) == member["sha256"]
    for relative, expected in VENDOR_HASHES.items():
        assert sha(ROOT / "vendor/scipilot" / Path(relative).name) == expected
    raw = list(csv.DictReader(read_member("measurements.csv").splitlines()))
    metadata = list(csv.DictReader(read_member("units.csv").splitlines()))
    events, duplicates = prepare_events(raw, metadata)
    paired = pair_units(events)
    assert len(raw) == 43 and duplicates == 2 and len(events) == 41
    assert len(paired) == 8 and paired.groupby("stratum").size().to_dict() == {"g1": 4, "g2": 4}
    np.testing.assert_allclose(paired["A_score"], [4, 5, 6, 7, 8, 9, 10, 11])
    np.testing.assert_allclose(paired["B_score"], [5.5, 6, 6.5, 8, 7, 7, 7, 6])
    np.testing.assert_allclose(paired["difference_A_minus_B"], [-1.5, -1, -0.5, -1, 1, 2, 3, 5])
    assert paired["n_A_technical"].sum() == 17 and paired["n_B_technical"].sum() == 24
    assert set(events["metadata_record"]) == {"current"}
    # Edge checks exercise the shared preparation path, including inclusive validity.
    conflict = dict(raw[0], raw_value="99")
    rejects(prepare_events, raw + [conflict], metadata)
    rejects(prepare_events, [dict(raw[0], measurement_unit="unknown")], metadata)
    rejects(prepare_events, [dict(raw[0], raw_value="nan")], metadata)
    rejects(prepare_events, [dict(raw[0], observed_at="2030-01-01")], metadata)
    rejects(prepare_events, [raw[0]], metadata + [metadata[1]])
    for when, expected in [("2025-12-31", "historical"), ("2026-01-01", "current"), ("2026-12-31", "current")]:
        boundary, _ = prepare_events([dict(raw[0], observed_at=when)], metadata)
        assert boundary.iloc[0]["metadata_record"] == expected
    rejects(pair_units, events[(events["unit_id"] != "u01") | (events["method"] != "B")])
    result = json.loads((ROOT / "results.json").read_text())
    assert result["aggregates"]["target"]["weights"] == WEIGHTS
    np.testing.assert_allclose(result["aggregates"]["target"]["difference_A_minus_B"], -0.25, atol=1e-12)
    np.testing.assert_allclose(result["aggregates"]["sample_mix"]["difference_A_minus_B"], 0.875, atol=1e-12)
    np.testing.assert_allclose(result["aggregates"]["target"]["bootstrap_percentile_95"], [-0.65, 0.15], atol=1e-12)
    np.testing.assert_allclose(result["strata"]["g1"]["bootstrap_percentile_95"], [-1.375, -0.625], atol=1e-12)
    np.testing.assert_allclose(result["strata"]["g2"]["bootstrap_percentile_95"], [1.5, 4.25], atol=1e-12)
    np.testing.assert_allclose(result["aggregates"]["sample_mix"]["bootstrap_percentile_95"], [0.1875, 1.625], atol=1e-12)
    distribution = np.load(ROOT / "bootstrap_distribution.npz")
    assert len(distribution["target"]) == len(distribution["sample_mix"]) == 65536
    assert len(distribution["g1"]) == len(distribution["g2"]) == 256
    np.testing.assert_allclose(distribution["target"].mean(), -0.25, atol=1e-12)
    np.testing.assert_allclose(distribution["sample_mix"].mean(), 0.875, atol=1e-12)
    loo = list(csv.DictReader((ROOT / "robustness_leave_one_out.csv").read_text().splitlines()))
    values = [float(row["target_difference_A_minus_B"]) for row in loo]
    assert len(values) == 8 and max(values) < 0
    np.testing.assert_allclose([min(values), max(values)], [-0.4, -7 / 60], atol=1e-12)
    np.testing.assert_allclose(result["robustness"]["composition"]["zero_crossing_g1_weight"], 11 / 15)
    alt = result["robustness"]["alternative_welch_satterthwaite_approximation"]
    np.testing.assert_allclose(alt["standard_error"], np.sqrt(0.64 / 24 + 0.04 * 8.75 / 12), atol=1e-12)
    assert alt["approximate_95_interval"][0] < 0 < alt["approximate_95_interval"][1]
    xml = ET.parse(ROOT / "main_figure.svg").getroot()
    width_mm = float(xml.attrib["width"].removesuffix("pt")) / 72 * 25.4
    height_mm = float(xml.attrib["height"].removesuffix("pt")) / 72 * 25.4
    assert abs(width_mm - 180) < 0.001 and height_mm <= 105 and abs(height_mm - 100) < 0.001
    ns = {"svg": "http://www.w3.org/2000/svg"}
    assert len(xml.findall(".//svg:text", ns)) > 0
    assert not xml.findall(".//svg:image", ns)
    svg_text = "\n".join("".join(node.itertext()) for node in xml.findall(".//svg:text", ns))
    for label in ["SYNTHETIC", "Target 80/20", "Sample 50/50", "g1 (n = 4)", "g2 (n = 4)"]:
        assert label in svg_text, label
    for label in ["Δ = -0.25", "Δ = +0.88", "Δ = +2.75"]:
        assert label in svg_text, label
    png = Image.open(ROOT / "main_figure.png")
    actual_mm = [pixel / dpi * 25.4 for pixel, dpi in zip(png.size, png.info["dpi"])]
    assert abs(actual_mm[0] - 180) < 0.05 and abs(actual_mm[1] - 100) < 0.05
    assert min(png.info["dpi"]) >= 599
    machine_qa = json.loads((ROOT / "figure_machine_qa.json").read_text())
    assert not machine_qa["layout_issues"]
    assert all(not item["issues"] for item in machine_qa["files"].values())

    # K-Dense evidence workflow adapted to local fixture records and numeric checks.
    sources = [
        {"evidence_id": "E001", "path": str(ROOT.parents[2] / "materials/chain-b/README.md"),
         "locator": "Synthetic status, primary target, composition, design boundaries"},
        {"evidence_id": "E002", "path": str(ROOT / "inputs/original/dictionary.md"),
         "locator": "Event copies, independent units, precision, conversion, temporal join, independence"},
        {"evidence_id": "E003", "path": str(ROOT / "inputs/original/measurements.csv"),
         "locator": "Complete original event table"},
        {"evidence_id": "E004", "path": str(ROOT / "inputs/original/units.csv"),
         "locator": "Complete historical and current metadata table"},
        {"evidence_id": "E005", "path": str(ROOT / "results.json"),
         "locator": "strata; aggregates; interval; plus flow.json and paired_units.csv"},
        {"evidence_id": "E006", "path": str(ROOT / "robustness_leave_one_out.csv"),
         "locator": "All rows; results.json.robustness; robustness_weight_sensitivity.csv; analysis.py.calculate"},
        {"evidence_id": "E007", "path": str(ROOT / "main_figure.svg"),
         "locator": "Both panels; figure_machine_qa.json; PNG and grayscale Agent inspection"},
        {"evidence_id": "E008", "path": str(ROOT / "inputs/original/LICENSE.txt"),
         "locator": "Entire fixture reuse permission and synthetic material statement"},
        {"evidence_id": "E009", "path": str(ROOT / "inputs/approved-correction.json"),
         "locator": "Authorized raw-value correction; definitions and weights unchanged"},
        {"evidence_id": "E010", "path": str(ROOT / "correction_dependency_audit.json"),
         "locator": "Exactly three raw rows, two unique events; unchanged members and definitions"},
    ]
    for source in sources:
        source.update({"sha256": sha(Path(source["path"])), "agent_checked_at_utc": checked_at,
                       "verification": "Agent inspected and machine checked; human verification unknown",
                       "material_class": "synthetic development fixture or derived artifact"})
    (ROOT / "source_manifest.json").write_text(json.dumps({"sources": sources}, indent=2) + "\n")
    valid_evidence = {item["evidence_id"] for item in sources}
    claims = []
    for document in ["manuscript.md", "caption.md"]:
        text = (ROOT / document).read_text()
        assert "SYNTHETIC" in text
        assert not any(label in text for label in ["chain-b", "without-skill", "with-skill", "iteration-rc3"])
        assert not any(ord(character) < 32 and character not in "\n\t\r" for character in text)
        for match in re.finditer(r"(?P<claim>[^\n]*(?:\n(?!\n)[^\n]*)*)\n<!-- claim:(?P<id>C\d+) evidence:(?P<evidence>E\d+(?:,E\d+)*) -->", text):
            claim = match.group("claim").strip()
            assert claim and set(match.group("evidence").split(",")) <= valid_evidence
            claims.append({"claim_id": match.group("id"), "document": document,
                           "line_start": text.count("\n", 0, match.start()) + 1,
                           "line_end": text.count("\n", 0, match.end()) + 1,
                           "claim_sha256": hashlib.sha256(" ".join(claim.split()).encode()).hexdigest(),
                           "evidence_ids": match.group("evidence"),
                           "status": "Agent_checked_human_unverified"})
        for phrase in ["[−0.65, 0.15]", "−0.25", "+0.875"]:
            assert phrase in text, (document, phrase)
        for stale in ["[−0.65, 0.25]", "−0.20", "+3.00", "+1.00", "−0.0667"]:
            assert stale not in text, (document, stale)
    assert len(claims) == 18 and len({row["claim_id"] for row in claims}) == 18
    assert (ROOT / "caption.md").read_text().rstrip().endswith(
        "All measurements in this figure are synthetic Skill-development inputs.")
    with (ROOT / "claim_evidence.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=claims[0].keys())
        writer.writeheader()
        writer.writerows(claims)
    consistent = {
        "N001": {"concept": "Independent paired units", "value": 8, "unit": "units", "evidence": "E005"},
        "N002": {"concept": "Unique technical events", "value": 41, "unit": "events", "evidence": "E005"},
        "N003": {"concept": "Target A minus B", "value": -0.25, "unit": "score", "evidence": "E005"},
        "N004": {"concept": "Target percentile interval", "value": [-0.65, 0.15], "unit": "score", "evidence": "E005"},
        "N005": {"concept": "Sample-mix A minus B", "value": 0.875, "unit": "score", "evidence": "E005"},
        "N006": {"concept": "Fixed-target leave-one-unit-out range", "value": [-0.4, -7/60], "unit": "score", "evidence": "E006"},
        "M001": {"method": "Deduplicate, convert, date-valid join, unit/method mean, paired difference", "result": "N001,N002,N003"},
        "M002": {"method": "Fixed-weight stratified paired percentile bootstrap", "result": "N004"},
        "M003": {"method": "Leave one independent unit out; fixed target weights", "result": "N006"},
        "analysis_intent": "Descriptive; exploratory interval and sensitivity choices",
        "human_verification": "unknown; machine and Agent checks do not certify scientific approval",
    }
    (ROOT / "consistency_manifest.json").write_text(json.dumps(consistent, indent=2) + "\n")
    record = {"checked_at_utc": checked_at, "status": "PASS", "checks": {
        "archive_and_member_identity": True, "professional_byte_identity": True,
        "authorized_source_correction_matches": True, "old_output_bytes_preserved": True,
        "unchanged_analysis_method_code": True,
        "original_data_flow_and_pairing": True, "invalid_input_rejection": True,
        "inclusive_temporal_join": True, "unit_conversion_and_technical_aggregation": True,
        "target_estimand_and_stratum_disagreement": True, "bootstrap_reproducibility": True,
        "leave_one_unit_out_and_weight_sensitivity": True, "alternative_interval": True,
        "figure_dimension_dpi_editable_svg": True, "manuscript_caption_numeric_consistency": True,
        "all_18_claims_have_evidence_bindings": True,
    }, "svg_size_mm": [width_mm, height_mm], "png_size_mm": actual_mm,
        "human_scientific_approval": "unknown", "token_usage": "unknown", "cost": "unknown"}
    (ROOT / "check_results.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    run()
