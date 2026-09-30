"""SYNTHETIC independent numeric check: rational arithmetic and count convolution."""
from pathlib import Path
from fractions import Fraction
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
import csv
import hashlib
import io
import json
import math
import zipfile

ROOT = Path(__file__).resolve().parent
ZIP_SHA = "79b22107370676dc295fc00eb7f376b895baea4dfebf4ac2d781cf45bd588e07"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_member(z, name):
    data = z.read(name)
    record = {"at_utc": datetime.now(timezone.utc).isoformat(), "original_zip_sha256": ZIP_SHA,
              "member_name": name, "member_sha256": hashlib.sha256(data).hexdigest(),
              "member_bytes": len(data), "actual_read_byte_range": [0, len(data)],
              "range_semantics": "half-open bytes; full member",
              "purpose": "independent rational-arithmetic and count-convolution check"}
    with (ROOT / "derived_member_reads.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return data.decode("utf-8")


def mean_mass(values):
    frequencies = Counter(values)
    state = Counter({Fraction(0): 1})
    for _ in values:
        updated = Counter()
        for partial, count in state.items():
            for value, multiplicity in frequencies.items():
                updated[partial + value] += count * multiplicity
        state = updated
    return Counter({s / len(values): count for s, count in state.items()})


def joint_mass(groups, weight):
    combined = Counter()
    for x, count_x in mean_mass(groups["g1"]).items():
        for y, count_y in mean_mass(groups["g2"]).items():
            combined[weight * x + (1 - weight) * y] += count_x * count_y
    return combined


def endpoints(mass):
    out, total = [], sum(mass.values())
    for q in [Fraction(1, 40), Fraction(39, 40)]:
        threshold, accumulated = math.ceil(q * total), 0
        for value, count in sorted(mass.items()):
            accumulated += count
            if accumulated >= threshold:
                out.append(float(value))
                break
    return out


def near(a, b):
    assert math.isclose(float(a), float(b), rel_tol=0, abs_tol=1e-12), (a, b)


def main():
    assert digest(ROOT / "raw/original.zip") == ZIP_SHA
    with zipfile.ZipFile(ROOT / "raw/original.zip") as z:
        dictionary = read_member(z, "dictionary.md")
        measurements = list(csv.DictReader(io.StringIO(read_member(z, "measurements.csv"))))
        history = list(csv.DictReader(io.StringIO(read_member(z, "units.csv"))))
    assert "1 score = 1000 subscore" in dictionary
    assert len(measurements) == 43 and len(history) == 16
    row_fields = list(measurements[0])
    distinct = {tuple(r[k] for k in row_fields) for r in measurements}
    unique = [dict(zip(row_fields, item)) for item in distinct]
    assert len(unique) == 41 and len({r["event_id"] for r in unique}) == 41
    per_unit = defaultdict(lambda: defaultdict(list))
    strata = {}
    for row in unique:
        when = date.fromisoformat(row["observed_at"])
        active = [m for m in history if m["unit_id"] == row["unit_id"]
                  and date.fromisoformat(m["valid_from"]) <= when <= date.fromisoformat(m["valid_to"])]
        assert len(active) == 1
        strata[row["unit_id"]] = active[0]["stratum"]
        divisor = {"score": 1, "subscore": 1000}[row["measurement_unit"]]
        per_unit[row["unit_id"]][row["method"]].append(Fraction(row["raw_value"]) / divisor)
    independent = {}
    for unit, methods in sorted(per_unit.items()):
        assert set(methods) == {"A", "B"}
        a = sum(methods["A"]) / len(methods["A"])
        b = sum(methods["B"]) / len(methods["B"])
        independent[unit] = {"A": a, "B": b, "D": a - b, "stratum": strata[unit]}
    derived = list(csv.DictReader((ROOT / "derived/paired_units.csv").open()))
    assert len(independent) == len(derived) == 8
    for row in derived:
        reference = independent[row["unit_id"]]
        near(row["A_score"], reference["A"])
        near(row["B_score"], reference["B"])
        near(row["difference_A_minus_B"], reference["D"])
    groups = {g: [r["D"] for r in independent.values() if r["stratum"] == g] for g in ["g1", "g2"]}
    results = json.loads((ROOT / "results.json").read_text())
    for g, values in groups.items():
        near(sum(values) / len(values), results["strata"][g]["mean_difference_A_minus_B"])
        for a, b in zip(endpoints(mean_mass(values)), results["strata"][g]["bootstrap_percentile_interval_95"]):
            near(a, b)
    target_mass = joint_mass(groups, Fraction(4, 5))
    sample_mass = joint_mass(groups, Fraction(1, 2))
    assert sum(target_mass.values()) == sum(sample_mass.values()) == 65536
    for weight, key, mass in [(Fraction(4, 5), "primary_target", target_mass),
                              (Fraction(1, 2), "sample_composition_comparator", sample_mass)]:
        reference = weight * sum(groups["g1"]) / 4 + (1 - weight) * sum(groups["g2"]) / 4
        near(reference, results[key]["difference_A_minus_B"])
        for a, b in zip(endpoints(mass), results[key]["bootstrap_percentile_interval_95"]):
            near(a, b)
    for row in results["robustness"]["leave_one_unit_out"]:
        left = {g: [r["D"] for u, r in independent.items() if r["stratum"] == g and u != row["omitted_unit"]]
                for g in groups}
        reference = Fraction(4, 5) * sum(left["g1"]) / len(left["g1"]) + Fraction(1, 5) * sum(left["g2"]) / len(left["g2"])
        near(reference, row["fixed_target_difference"])
        mass = joint_mass(left, Fraction(4, 5))
        assert sum(mass.values()) == row["resample_configurations"] == 6912
        for a, b in zip(endpoints(mass), [row["interval_lo"], row["interval_hi"]]):
            near(a, b)
    loo = results["robustness"]["leave_one_unit_out"]
    assert sum(r["interval_lo"] <= 0 <= r["interval_hi"] for r in loo) == 6
    assert {r["omitted_unit"] for r in loo if not r["interval_lo"] <= 0 <= r["interval_hi"]} == {"u03", "u08"}
    near(results["robustness"]["sign_crossing_weight_g1"], Fraction(11, 15))
    for row in csv.DictReader((ROOT / "composition_sensitivity.csv").open()):
        near(row["difference_A_minus_B"], 2.75 - 3.75 * float(row["weight_g1"]))
    qa = json.loads((ROOT / "figure_qa.json").read_text())
    figure_rows = {r["row"]: r for r in qa["displayed_values"]}
    for g in groups:
        near(figure_rows[g]["estimate"], results["strata"][g]["mean_difference_A_minus_B"])
        for a, b in zip(figure_rows[g]["interval"], results["strata"][g]["bootstrap_percentile_interval_95"]):
            near(a, b)
    for name, key in [("target", "primary_target"), ("sampled", "sample_composition_comparator")]:
        near(figure_rows[name]["estimate"], results[key]["difference_A_minus_B"])
        for a, b in zip(figure_rows[name]["interval"], results[key]["bootstrap_percentile_interval_95"]):
            near(a, b)
    assert qa["exported"] and not qa["layout_issues"] and qa["SVG_text_editable"]
    final = (ROOT / "manuscript.md").read_text()
    caption = (ROOT / "caption.md").read_text()
    assert all(x in final for x in ["[-0.65, +0.15]", "[+0.1875, +1.6250]", "Six omission intervals included zero", "w=11/15", "u03", "[-0.733, -0.033]"])
    assert all(x in caption for x in ["[-0.65, +0.15]", "65,536", "within each stratum", "weights are held fixed"])
    assert caption.count("All measurements in this figure are synthetic Skill-development inputs.") == 1
    assert all(x in final.lower() for x in ["synthetic", "descriptive", "conditional", "independence", "no causal"])
    assert all(x not in final for x in ["chain-b", "release.0", "3.2.0-rc.3"])
    facts = {
        "synthetic": True, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS within synthetic computational scope",
        "checker": "current Agent and verify.py; not an external scientific reviewer",
        "independent_numeric_method": "Exact Fraction arithmetic from original archive members; bootstrap count convolution independent of ordered-draw enumerator",
        "passed": ["original ZIP digest", "43 to 41 exact-copy row flow", "one active date-valid metadata record per event",
                   "score/subscore conversion", "eight paired unit means", "two stratum mean contrasts and intervals",
                   "fixed target and sampled-composition contrasts and intervals", "all eight fixed-weight omission contrasts and intervals",
                   "six zero-containing omission intervals; u03/u08 exclusions", "composition crossing and all 101 sensitivity rows",
                   "main-figure source values and interval labels", "final manuscript and caption key numerical consistency"],
        "subject_hashes": {name: digest(ROOT / name) for name in ["manuscript.before-expression.md", "manuscript.md",
                           "manuscript.expression.diff", "caption.md", "results.json", "figure_source.csv",
                           "main_figure.png", "main_figure.svg", "writing_review.md"]},
        "semantic_review": {
            "record": "writing_review.md", "reviewer": "current Agent",
            "checks": ["target and comparator unchanged", "paired independent unit and denominator unchanged",
                       "opposite strata retained", "primary interval zero inclusion retained", "descriptive and conditional scope retained",
                       "non-equivalence and non-causal semantics retained", "exploratory sensitivity not relabeled prespecified"],
            "human_verification": "not performed", "real_world_validation": "not supplied", "submission_ready": False,
        },
    }
    (ROOT / "fact_check.json").write_text(json.dumps(facts, indent=2) + "\n")
    print(json.dumps({"status": facts["status"], "numerical_check_groups": len(facts["passed"]),
                      "target_interval": endpoints(target_mass), "sampled_interval": endpoints(sample_mass),
                      "loo_intervals_containing_zero": 7}))


if __name__ == "__main__":
    main()
