"""Runnable checks for this SYNTHETIC artifact, using a second exact-bootstrap algorithm."""
import csv
import hashlib
import itertools
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction as F
from pathlib import Path

from PIL import Image

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
BASE = HERE.parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def count_bootstrap(values):
    """Multinomial count vectors instead of the analysis's ordered-sequence enumeration."""
    n, distribution = len(values), Counter()
    for counts in itertools.product(range(n+1), repeat=n):
        if sum(counts) != n:
            continue
        mean = sum(c*x for c, x in zip(counts, values)) / n
        multiplicity = math.factorial(n) // math.prod(math.factorial(c) for c in counts)
        distribution[mean] += multiplicity
    assert sum(distribution.values()) == n**n
    return distribution


def quantiles(distribution):
    result, total = [], sum(distribution.values())
    for q in [F(1, 40), F(39, 40)]:
        accumulated = 0
        for value, count in sorted(distribution.items()):
            accumulated += count
            if F(accumulated, total) >= q:
                result.append(float(value))
                break
    return result


def verify():
    request_path = BASE / "continuations/chain-b.comparison.0/correction/request.json"
    request = json.loads(request_path.read_text())
    identity = json.loads((HERE / "archive_identity.json").read_text())
    assert digest(request_path) == identity["request_sha256"], "Original request changed"
    checked_originals = []
    for entry in request["material_files"]:
        # Verify identities only; do not inspect other archives or use their contents.
        actual = digest(Path(entry["path"]))
        assert actual == entry["sha256"]
        checked_originals.append({"path": entry["path"], "sha256": actual})
    assert digest(HERE / "inputs/source.zip") == identity["source_sha256"]
    now = datetime.now(timezone.utc).isoformat()
    member_sources = {}
    with (HERE / "derived_member_reads.jsonl").open("a") as trace:
        for member in identity["members"]:
            path = Path(member["extracted_path"])
            data = path.read_bytes()
            assert hashlib.sha256(data).hexdigest() == member["member_sha256"]
            member_sources[member["member_name"]] = member
            trace.write(json.dumps({**member, "read_at_utc": now, "byte_range": [0, len(data)],
                                    "range_convention": "bytes half-open", "purpose": "final source identity and independent computational checks"}) + "\n")
    pairs = rows(HERE / "pairs.csv")
    assert len(pairs) == 8 and Counter(p["stratum"] for p in pairs) == {"g1": 4, "g2": 4}
    expected = [F(-3, 2), F(-1), F(-1, 2), F(-1), F(1), F(2), F(3), F(5)]
    assert [F(p["difference_A_minus_B"]) for p in pairs] == expected
    assert [float(p["B"]) for p in pairs] == [5.5, 6, 6.5, 8, 7, 7, 7, 6]
    assert sum(int(p["n_A_technical"]) + int(p["n_B_technical"]) for p in pairs) == 41
    prior_pairs = rows(HERE.parent / "pairs.csv")
    assert len(prior_pairs) == len(pairs)
    for prior, current in zip(prior_pairs, pairs):
        if current["unit_id"] == "u08":
            assert F(current["B"]) - F(prior["B"]) == 1
            assert F(current["difference_A_minus_B"]) - F(prior["difference_A_minus_B"]) == -1
            assert {k: v for k, v in current.items() if k not in {"B", "difference_A_minus_B"}} == {
                k: v for k, v in prior.items() if k not in {"B", "difference_A_minus_B"}}
        else:
            assert prior == current, "Unrelated paired-unit change"
    baseline = json.loads((HERE / "prior_run_snapshot.json").read_text())
    for name, prior_digest in baseline["files"].items():
        assert digest(HERE.parent / name) == prior_digest, f"Prior artifact changed: {name}"
    correction = json.loads((HERE / "correction_audit.json").read_text())
    assert len(correction["changed_raw_rows"]) == 3
    assert correction["changed_unique_events"] == ["e040", "e041"]
    assert correction["dictionary_original_definition_bytes_retained"]
    assert correction["unit_metadata_and_license_byte_identical"]
    result = json.loads((HERE / "results.json").read_text())
    boot1, boot2 = count_bootstrap(expected[:4]), count_bootstrap(expected[4:])
    for i, boot in enumerate([boot1, boot2]):
        assert quantiles(boot) == result["strata"][i]["ci95_percentile"]
    for i, (name, w1, w2) in enumerate([("target", F(4, 5), F(1, 5)), ("sample", F(1, 2), F(1, 2))]):
        independent = Counter()
        for m1, c1 in boot1.items():
            for m2, c2 in boot2.items():
                independent[w1*m1 + w2*m2] += c1*c2
        assert sum(independent.values()) == 65536
        actual = {F(row["difference"]): int(row["multiplicity"]) for row in rows(HERE / f"bootstrap_{name}_pmf.csv")}
        assert actual == dict(independent), "Exact probability distributions disagree"
        assert quantiles(independent) == result["aggregates"][i]["ci95_percentile"]
        assert sum(v*c for v, c in independent.items()) / 65536 == [F(-1, 4), F(7, 8)][i]
    loo = rows(HERE / "leave_one_unit_out.csv")
    assert len(loo) == 8 and all(float(r["target_difference"]) < 0 for r in loo)
    assert math.isclose(min(float(r["target_difference"]) for r in loo), -0.4)
    assert math.isclose(max(float(r["target_difference"]) for r in loo), -7/60)
    assert math.isclose(result["robustness"]["zero_crossing_stratum_1_weight"], 11/15)
    assert result["aggregates"][0]["weights"] == [0.8, 0.2]
    # Trust-boundary checks stop before output writes.
    from analysis import paired_units
    text = {name: Path(info["extracted_path"]).read_text() for name, info in member_sources.items()}
    bad_event = dict(text)
    bad_event["measurements.csv"] = text["measurements.csv"] + "e001,u01,A,2026-01-15,99,score\n"
    bad_metadata = dict(text)
    bad_metadata["units.csv"] = text["units.csv"] + "u01,g2,2026-01-01,2026-12-31,extra\n"
    for name, bad in [("conflicting event", bad_event), ("nonunique validity join", bad_metadata)]:
        try:
            paired_units(bad)
        except AssertionError:
            pass
        else:
            raise AssertionError(f"Did not reject {name}")
    svg = ET.parse(HERE / "main_figure.svg").getroot()
    dimensions = [float(svg.attrib[k].removesuffix("pt")) * 25.4/72 for k in ["width", "height"]]
    assert math.isclose(dimensions[0], 180, abs_tol=0.001) and dimensions[1] <= 105
    assert svg.findall(".//{http://www.w3.org/2000/svg}text"), "SVG text is not editable"
    assert not svg.findall(".//{http://www.w3.org/2000/svg}image"), "Unexpected raster in SVG"
    with Image.open(HERE / "main_figure.png") as image:
        dpi = image.info["dpi"]
        png_mm = [image.size[i] / dpi[i] * 25.4 for i in range(2)]
        assert all(round(x) == 600 for x in dpi)
        assert math.isclose(png_mm[0], 180, abs_tol=0.05) and png_mm[1] <= 105
        pixels = list(image.size)
    final = (HERE / "manuscript.md").read_text()
    before = (HERE / "manuscript_draft.md").read_text()
    caption = (HERE / "caption.md").read_text()
    remove_markers = lambda t: re.sub(r"\[(?:claim|evidence):[^]]+\]", "", t)
    numeric = lambda t: re.findall(r"(?<![A-Za-z])[-−+]?\d+(?:\.\d+)?", remove_markers(t))
    assert numeric(final) == numeric(before), "Expression pass changed numerical tokens"
    for phrase in ["80%", "20%", "−0.25", "−0.65", "0.15", "+0.875", "0.1875", "1.625", "−0.40", "−0.1167", "0.7333"]:
        assert phrase in final
    for phrase in ["SYNTHETIC", "conditional", "no assignment", "No causal", "unknown", "not a report of real", "interval includes zero"]:
        assert phrase in final
    for phrase in ["SYNTHETIC", "conditional", "65,536", "pointwise", "No hypothesis test"]:
        assert phrase in caption
    assert caption.endswith("All measurements in this figure are synthetic Skill-development inputs.\n")
    for stale in ["−0.20", "−0.0667", "+1.00", "+3.00", "w=0.75", "Δ(w)=3−4w", "9.50/6.50", "7.50/6.50"]:
        assert stale not in final and stale not in caption, f"Stale dependent value: {stale}"
    assert "chain-b" not in final and "comparison.0" not in final and "rc.1" not in final
    source_reads = [json.loads(line) for path in [HERE / "resource_reads_inherited.jsonl", HERE / "resource_reads.jsonl"]
                    for line in path.read_text().splitlines()]
    read_by_path = {r["path"]: r for r in source_reads}
    material_root = Path(request["material_root"])
    def source(eid, path, sha, locator):
        return {"evidence_id": eid, "path": str(path), "sha256": sha,
                "locator": locator, "verification": "Agent checked; human verification not performed"}
    sources = [source("E001", material_root / "README.md", read_by_path[str(material_root / "README.md")]["sha256"], "whole README")]
    for eid, name in [("E002", "dictionary.md"), ("E003", "measurements.csv"), ("E004", "units.csv"), ("E009", "LICENSE.txt")]:
        m = member_sources[name]
        sources.append({**source(eid, m["extracted_path"], m["member_sha256"], f"ZIP member {name}; full byte range"),
                        "original_archive_sha256": identity["source_sha256"]})
    for eid, name, locator in [("E005", "analysis.py", "paired_units, compute, figure"),
                               ("E006", "results.json", "strata, aggregates, bootstrap, robustness"),
                               ("E010", "archive_identity.json", "selected_id, source_sha256, zip_crc_ok, members"),
                               ("E008", "bibliographic_receipt.json", "arXiv metadata, author list, title, DOI")]:
        sources.append(source(eid, HERE / name, digest(HERE / name), locator))
    cat_path = str(material_root / "candidates.json")
    sources.append(source("E007", cat_path, read_by_path[cat_path]["sha256"], "paired, mirror and proxy candidates"))
    approval_path = identity["correction_authorisation_path"]
    sources.append(source("E011", approval_path, digest(Path(approval_path)), "changed_rows, unchanged_definitions and original/corrected ZIP digests"))
    (HERE / "source_manifest.json").write_text(json.dumps({"synthetic": True, "human_verified": False, "sources": sources}, indent=2) + "\n")
    known_ids = {x["evidence_id"] for x in sources}
    claims = []
    for line_number, line in enumerate(final.splitlines(), 1):
        match = re.search(r"\[claim:(C\d+)\] \[evidence:([^]]+)\]", line)
        if not match:
            continue
        evidence = match.group(2).split(",")
        assert set(evidence) <= known_ids
        claims.append({"claim_id": match.group(1), "final_line": line_number,
                       "claim_sha256": hashlib.sha256(remove_markers(line).strip().encode()).hexdigest(),
                       "evidence_ids": match.group(2), "verification": "Agent checked; no human certification"})
    assert len(claims) >= 20
    with (HERE / "claims.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(claims[0]))
        writer.writeheader()
        writer.writerows(claims)
    checks = {"status": "passed scoped computational and Agent semantic checks", "checked_at_utc": now,
              "synthetic": True, "original_identities_unchanged": checked_originals, "prior_run_files_unchanged": True,
              "authorised_correction_checked": True, "prior_caption_disclosure_retained": True,
              "independent_bootstrap_count_algorithm": "all multinomial count vectors; integer multiplicities; rational means",
              "bootstrap_distributions_match_exactly": True, "prespecified_target_weights_retained": True,
              "trust_boundary_checks": ["conflicting duplicate rejected", "nonunique date-valid metadata join rejected"],
              "figure": {"svg_mm": dimensions, "png_mm": png_mm, "png_pixels": pixels,
                         "editable_svg_text": True, "embedded_raster": False,
                         "Agent_viewed_final_png_and_grayscale": True},
              "subjects": [{"file": name, "sha256": digest(HERE / name)} for name in
                           ["manuscript_draft.md", "manuscript.md", "caption.md", "main_figure.svg", "main_figure.png", "results.json"]],
              "expression_numeric_tokens_unchanged": True,
              "semantic_review": {"target_and_comparator": "A-B paired units; 80/20 primary; 50/50 diagnostic retained",
                                  "direction": "opposing strata; target point estimate negative; interval crosses zero",
                                  "scope": "manufactured eight-unit fixture; conditional empirical resampling; real population unknown",
                                  "causality": "descriptive throughout; no causal attribution added",
                                  "significance": "no superiority, equivalence or hypothesis-test claim added",
                                  "important_counterevidence": "stratum-2 direction and positive sample aggregate retained"},
              "human_verification": "not performed", "real_external_validation": "not performed", "submission_ready": False}
    (HERE / "fact_semantic_check.json").write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "independent_bootstrap_match": True, "svg_mm": dimensions,
                      "png_mm": png_mm, "claim_occurrences_bound": len(claims)}))


if __name__ == "__main__":
    verify()
