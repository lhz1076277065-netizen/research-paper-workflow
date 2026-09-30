"""SYNTHETIC: paired-unit estimation and exact stratified resampling."""
from pathlib import Path
from itertools import product
from collections import Counter
from datetime import datetime, timezone
import csv
import hashlib
import json
import math
import sys

sys.dont_write_bytecode = True
import numpy as np

ROOT = Path(__file__).resolve().parent
WEIGHTS = {"g1": 0.8, "g2": 0.2}


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def resampled_means(values):
    # ponytail: exhaustive n^n enumeration for n<=4; use seeded paired resampling for larger n.
    if not 2 <= len(values) <= 4:
        raise ValueError("Exact enumerator is bounded to this small fixture")
    return np.array([sum(draw) / len(draw) for draw in product(values, repeat=len(values))])


def interval(distribution):
    # Inverse empirical CDF: endpoint k is sorted value at ceil(q*M), with 1-based k.
    ordered = np.sort(distribution)
    return [float(ordered[math.ceil(q * len(ordered)) - 1]) for q in (0.025, 0.975)]


def weighted_distribution(groups, w=0.8):
    m1, m2 = resampled_means(groups["g1"]), resampled_means(groups["g2"])
    return (w * m1[:, None] + (1 - w) * m2[None, :]).ravel()


def main():
    paired_path = ROOT / "derived/paired_units.csv"
    rows = list(csv.DictReader(paired_path.open(encoding="utf-8")))
    if len({r["unit_id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate independent unit")
    groups = {g: [float(r["difference_A_minus_B"]) for r in rows if r["stratum"] == g]
              for g in WEIGHTS}
    if {g: len(d) for g, d in groups.items()} != {"g1": 4, "g2": 4}:
        raise ValueError("Unexpected strata")
    for row in rows:
        assert math.isclose(float(row["A_score"]) - float(row["B_score"]),
                            float(row["difference_A_minus_B"]), abs_tol=1e-12)
    summaries = {}
    for g, values in groups.items():
        group_rows = [r for r in rows if r["stratum"] == g]
        summaries[g] = {
            "n_independent_units": len(values),
            "A_mean_score": float(np.mean([float(r["A_score"]) for r in group_rows])),
            "B_mean_score": float(np.mean([float(r["B_score"]) for r in group_rows])),
            "mean_difference_A_minus_B": float(np.mean(values)),
            "sample_variance_difference": float(np.var(values, ddof=1)),
            "paired_unit_differences": values,
            "bootstrap_percentile_interval_95": interval(resampled_means(values)),
        }
    target_dist = weighted_distribution(groups)
    sample_dist = weighted_distribution(groups, w=0.5)
    target = {
        "weights": WEIGHTS,
        "A_mean_score": sum(WEIGHTS[g] * summaries[g]["A_mean_score"] for g in WEIGHTS),
        "B_mean_score": sum(WEIGHTS[g] * summaries[g]["B_mean_score"] for g in WEIGHTS),
        "difference_A_minus_B": sum(WEIGHTS[g] * np.mean(groups[g]) for g in WEIGHTS),
        "bootstrap_percentile_interval_95": interval(target_dist),
    }
    sampled = {
        "weights": {"g1": 0.5, "g2": 0.5},
        "A_mean_score": float(np.mean([float(r["A_score"]) for r in rows])),
        "B_mean_score": float(np.mean([float(r["B_score"]) for r in rows])),
        "difference_A_minus_B": float(np.mean([float(r["difference_A_minus_B"]) for r in rows])),
        "bootstrap_percentile_interval_95": interval(sample_dist),
        "interpretation": "Comparator at sampled stratum composition, not the prespecified target estimator",
    }
    loo = []
    for row in rows:
        remaining = [r for r in rows if r["unit_id"] != row["unit_id"]]
        left = {g: [float(r["difference_A_minus_B"]) for r in remaining if r["stratum"] == g]
                for g in WEIGHTS}
        dist = weighted_distribution(left)
        lo, hi = interval(dist)
        loo.append({"omitted_unit": row["unit_id"], "omitted_stratum": row["stratum"],
                    "n_g1_remaining": len(left["g1"]), "n_g2_remaining": len(left["g2"]),
                    "fixed_target_difference": float(sum(WEIGHTS[g] * np.mean(left[g]) for g in WEIGHTS)),
                    "interval_lo": lo, "interval_hi": hi,
                    "resample_configurations": len(dist)})
    d1, d2 = summaries["g1"]["mean_difference_A_minus_B"], summaries["g2"]["mean_difference_A_minus_B"]
    crossing = d2 / (d2 - d1)
    sensitivity = [{"weight_g1": i / 100, "weight_g2": 1 - i / 100,
                    "difference_A_minus_B": i / 100 * d1 + (1 - i / 100) * d2}
                   for i in range(101)]
    output = {
        "synthetic": True, "analysis_intent": "descriptive",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "analysis_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "paired_data_sha256": hashlib.sha256(paired_path.read_bytes()).hexdigest(),
        "score_direction": "lower is better; negative A-minus-B favors A",
        "n_independent_units": 8, "strata": summaries,
        "primary_target": target, "sample_composition_comparator": sampled,
        "bootstrap": {
            "method": "exhaustive stratified paired-unit percentile bootstrap",
            "draws_per_stratum": {g: len(groups[g]) ** len(groups[g]) for g in groups},
            "joint_configurations": len(target_dist),
            "sampling": "sample n_h paired units with replacement independently within each stratum; fixed stratum weights",
            "quantile_definition": "inverse empirical CDF; sorted order statistic ceil(q*M), q=0.025 and 0.975",
            "random_seed": None, "Monte_Carlo_error": "none; exact enumeration of the empirical resampling distribution",
            "conditional_scope": "empirical paired-unit distributions, fixed target weights, and fixture-stipulated unit independence",
            "coverage_limit": "not a guaranteed 95% population coverage interval with n=4 per stratum; no real-world probability sampling information supplied",
        },
        "robustness": {
            "intent": "exploratory; chosen after data inspection",
            "leave_one_unit_out": loo,
            "loo_target_estimate_range": [min(r["fixed_target_difference"] for r in loo),
                                           max(r["fixed_target_difference"] for r in loo)],
            "all_loo_point_estimates_favor_A": all(r["fixed_target_difference"] < 0 for r in loo),
            "all_loo_intervals_include_zero": all(r["interval_lo"] <= 0 <= r["interval_hi"] for r in loo),
            "weight_sensitivity_formula": "difference(w_g1) = 3 - 4*w_g1",
            "sign_crossing_weight_g1": crossing,
            "scope": "composition sensitivity changes the described population; it does not revise the fixed 0.8/0.2 target or identify a causal mechanism",
        },
        "unknown_real_world_inputs": ["sampling frame and inclusion probabilities", "target transportability",
                                      "measurement validity", "independence outside the stipulated fixture",
                                      "assignment or causal identification"],
    }
    for data, name in [(loo, "leave_one_unit_out.csv"), (sensitivity, "composition_sensitivity.csv")]:
        write_csv(ROOT / name, data)
    source = [{"row": g, "n_independent_units": 4,
               "target_weight": WEIGHTS[g], "sampled_weight": 0.5,
               "A_mean_score": summaries[g]["A_mean_score"],
               "B_mean_score": summaries[g]["B_mean_score"],
               "difference_A_minus_B": summaries[g]["mean_difference_A_minus_B"],
               "interval_lo": summaries[g]["bootstrap_percentile_interval_95"][0],
               "interval_hi": summaries[g]["bootstrap_percentile_interval_95"][1]}
              for g in WEIGHTS]
    source += [{"row": name, "n_independent_units": 8,
                "target_weight": "", "sampled_weight": "",
                "A_mean_score": item["A_mean_score"], "B_mean_score": item["B_mean_score"],
                "difference_A_minus_B": item["difference_A_minus_B"],
                "interval_lo": item["bootstrap_percentile_interval_95"][0],
                "interval_hi": item["bootstrap_percentile_interval_95"][1]}
               for name, item in [("Target 80/20", target), ("Sampled 50/50", sampled)]]
    write_csv(ROOT / "figure_source.csv", source)
    masses = [{"target_difference": d, "count": c, "probability": c / len(target_dist)}
              for d, c in sorted(Counter(np.round(target_dist, 12)).items())]
    write_csv(ROOT / "target_bootstrap_mass.csv", masses)
    np.savez(ROOT / "bootstrap_arrays.npz", g1=resampled_means(groups["g1"]),
             g2=resampled_means(groups["g2"]), target=target_dist, sampled=sample_dist)
    (ROOT / "results.json").write_text(json.dumps(output, indent=2) + "\n")
    # One executable end-to-end check against the fixture's algebra, not individual helpers.
    assert math.isclose(target["difference_A_minus_B"], -0.2, abs_tol=1e-12)
    assert math.isclose(sampled["difference_A_minus_B"], 1.0, abs_tol=1e-12)
    assert len(target_dist) == 65536 and math.isclose(crossing, 0.75)
    assert math.isclose(sum(m["probability"] for m in masses), 1.0, abs_tol=1e-12)
    print(json.dumps({"strata": summaries, "target": target, "sampled": sampled,
                      "robustness": output["robustness"]}, indent=2))


if __name__ == "__main__":
    main()
