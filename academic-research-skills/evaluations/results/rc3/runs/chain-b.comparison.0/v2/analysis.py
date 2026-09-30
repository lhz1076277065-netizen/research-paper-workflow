"""SYNTHETIC paired-unit preparation, target standardization, exact bootstrap and figure."""
import argparse
import csv
import io
import itertools
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
os.environ["MPLCONFIGDIR"] = str(HERE / ".mplconfig")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.patches import Patch

from prepare import prepare

BASE = HERE.parents[2]
PRO = BASE / "professional/Haojae/scipilot-figure-skill/scripts"
sys.path.insert(0, str(PRO))
from profile_data import profile_data, render_report
from setup_style import setup_style
from layout_tools import add_panel_labels
from visual_qa import audit_layout, render_preview
from check_figure import check_figure


def write_json(name, value):
    def scalar(value):
        if isinstance(value, np.generic):
            return value.item()
        raise TypeError(f"Unsupported JSON type: {type(value).__name__}")
    (HERE / name).write_text(json.dumps(value, indent=2, allow_nan=False, default=scalar) + "\n")


def write_csv(name, rows):
    rows = list(rows)
    with (HERE / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def paired_units(texts):
    raw = list(csv.DictReader(io.StringIO(texts["measurements.csv"])))
    metadata = list(csv.DictReader(io.StringIO(texts["units.csv"])))
    by_event, duplicates = {}, []
    for row in raw:
        assert all(row.values()), "Missing event field"
        event = row["event_id"]
        if event in by_event:
            assert row == by_event[event], f"Conflicting duplicate event: {event}"
            duplicates.append(event)
        else:
            by_event[event] = row
    scales = {"score": Decimal(1), "subscore": Decimal("0.001")}
    grouped, joined = defaultdict(list), []
    for row in by_event.values():
        when = date.fromisoformat(row["observed_at"])
        active = [m for m in metadata if m["unit_id"] == row["unit_id"]
                  and date.fromisoformat(m["valid_from"]) <= when <= date.fromisoformat(m["valid_to"])]
        assert len(active) == 1, f"Metadata match must be unique: {row['event_id']}"
        assert row["method"] in {"A", "B"} and row["measurement_unit"] in scales
        value = Decimal(row["raw_value"]) * scales[row["measurement_unit"]]
        assert value.is_finite()
        stratum = active[0]["stratum"]
        grouped[(row["unit_id"], stratum, row["observed_at"], row["method"])].append(value)
        joined.append({**row, "stratum": stratum, "score": str(value),
                       "metadata_record": active[0]["record"]})
    units = sorted({(u, s, t) for u, s, t, _ in grouped})
    assert len({u for u, _, _ in units}) == len(units), "Unit has multiple strata/dates"
    pairs = []
    for unit, stratum, when in units:
        values = {}
        for method in ["A", "B"]:
            reps = grouped[(unit, stratum, when, method)]
            assert reps, f"Incomplete method pair: {unit}"
            values[method] = sum(reps) / len(reps)
        pairs.append({"unit_id": unit, "stratum": stratum, "observed_at": when,
                      "A": float(values["A"]), "B": float(values["B"]),
                      "difference_A_minus_B": float(values["A"] - values["B"]),
                      "n_A_technical": len(grouped[(unit, stratum, when, "A")]),
                      "n_B_technical": len(grouped[(unit, stratum, when, "B")])})
    counts = Counter(x["stratum"] for x in pairs)
    assert counts == {"g1": 4, "g2": 4}
    write_csv("events_prepared.csv", joined)
    write_csv("pairs.csv", pairs)
    audit = {"raw_rows": len(raw), "unique_events": len(by_event),
             "exact_duplicates_removed": duplicates, "metadata_rows": len(metadata),
             "joined_rows": len(joined), "metadata_matches_per_event": 1,
             "unit_pairs": len(pairs), "units_per_stratum": dict(counts),
             "measurement_unit_counts_unique_events": dict(Counter(r["measurement_unit"] for r in by_event.values())),
             "missing_values": 0, "unpaired_units": 0,
             "rule": "deduplicate event_id; convert; validity-date join; mean technical repetitions; pair independent units"}
    write_json("preparation_audit.json", audit)
    return pairs


def interval(values):
    # Exact empirical CDF quantiles, with no Monte Carlo interpolation or seed.
    return np.quantile(np.round(values, 12), [0.025, 0.975], method="inverted_cdf").tolist()


def compute(pairs):
    grouped = {s: np.array([p["difference_A_minus_B"] for p in pairs if p["stratum"] == s])
               for s in ["g1", "g2"]}
    draws = {}
    strata = []
    for stratum, values in grouped.items():
        # ponytail: exact enumeration is for this four-unit fixture; use seeded resampling for larger n.
        draws[stratum] = np.array([np.mean(x) for x in itertools.product(values, repeat=len(values))])
        rows = [p for p in pairs if p["stratum"] == stratum]
        strata.append({"stratum": stratum, "n": len(values), "mean_A": float(np.mean([p["A"] for p in rows])),
                       "mean_B": float(np.mean([p["B"] for p in rows])),
                       "mean_difference": float(values.mean()), "sd_difference": float(values.std(ddof=1)),
                       "ci95_percentile": interval(draws[stratum]), "ordered_resamples": len(draws[stratum])})
    aggregates = []
    for label, w, other in [("target", 0.8, 0.2), ("sample", 0.5, 0.5)]:
        boot = (w * draws["g1"][:, None] + other * draws["g2"][None, :]).ravel()
        delta = w * grouped["g1"].mean() + other * grouped["g2"].mean()
        aggregates.append({"composition": label, "weights": [w, other], "difference": round(float(delta), 12),
                           "mean_A": round(float(w * strata[0]["mean_A"] + other * strata[1]["mean_A"]), 12),
                           "mean_B": round(float(w * strata[0]["mean_B"] + other * strata[1]["mean_B"]), 12),
                           "ci95_percentile": interval(boot), "ordered_resamples": len(boot)})
        values, counts = np.unique(np.round(boot, 12), return_counts=True)
        write_csv(f"bootstrap_{label}_pmf.csv", ({"difference": v, "multiplicity": int(c),
                                                 "probability": c / len(boot)} for v, c in zip(values, counts)))
    loo = []
    for omitted in pairs:
        remaining = [p for p in pairs if p["unit_id"] != omitted["unit_id"]]
        means = {s: np.mean([p["difference_A_minus_B"] for p in remaining if p["stratum"] == s])
                 for s in grouped}
        loo.append({"omitted_unit": omitted["unit_id"], "stratum": omitted["stratum"],
                    "target_difference": float(0.8 * means["g1"] + 0.2 * means["g2"])})
    write_csv("leave_one_unit_out.csv", loo)
    sensitivity = [{"stratum_1_weight": float(w), "difference": float(w * grouped["g1"].mean() + (1-w) * grouped["g2"].mean())}
                   for w in np.linspace(0, 1, 101)]
    write_csv("weight_sensitivity.csv", sensitivity)
    zero = grouped["g2"].mean() / (grouped["g2"].mean() - grouped["g1"].mean())
    summary = {"synthetic": True, "score_direction": "lower is better", "contrast": "A minus B",
               "strata": strata, "aggregates": aggregates,
               "bootstrap": {"unit": "paired independent unit", "within_stratum": True,
                             "target_weights_fixed": True, "quantiles": [0.025, 0.975],
                             "quantile_definition": "inverse empirical CDF", "monte_carlo": False,
                             "conditional_model": "independent draws from each stratum's empirical paired-unit distribution",
                             "population_coverage_validated": False},
               "robustness": {"leave_one_unit_out_range": [min(x["target_difference"] for x in loo), max(x["target_difference"] for x in loo)],
                              "leave_one_unit_out_all_negative": all(x["target_difference"] < 0 for x in loo),
                              "zero_crossing_stratum_1_weight": float(zero),
                              "weight_sensitivity_is_alternative_estimand_not_weight_uncertainty": True}}
    write_json("results.json", summary)
    # Hand-calculated reference cases catch unit conversion, event duplication and weighting mistakes.
    expected = [-1.5, -1, -0.5, -1, 1, 2, 3, 5]
    assert np.allclose([p["difference_A_minus_B"] for p in pairs], expected, atol=1e-12)
    assert np.allclose([a["difference"] for a in aggregates], [-0.25, 0.875], atol=1e-12)
    assert np.isclose(zero, 11/15)
    assert np.isclose(np.mean(0.8 * draws["g1"][:, None] + 0.2 * draws["g2"][None, :]), -0.25)
    return summary


def figure(pairs, summary, preview_only):
    profile = profile_data(str(HERE / "pairs.csv"), group_cols=["stratum"])
    (HERE / "scipilot_profile.md").write_text(render_report(profile))
    write_json("scipilot_profile.json", profile)
    style = setup_style(journal="general", lang="en", use_sciplots=False, constrained_layout=False)
    plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "axes.titlesize": 8.5,
                         "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "font.sans-serif": ["DejaVu Sans"],
                         "legend.fontsize": 7.5, "svg.hashsalt": "synthetic-paired-standardization"})
    blue, orange = "#0072B2", "#E69F00"
    size = (180/25.4, 103/25.4)
    fig = plt.figure(figsize=size, dpi=150)
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.6], height_ratios=[0.9, 1.3],
                          left=0.13, right=0.975, bottom=0.2, top=0.82, wspace=0.62, hspace=0.82)
    a, b, c = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[:, 1]), fig.add_subplot(gs[1, 0])
    fig.suptitle("SYNTHETIC | Composition changes the aggregate comparison", x=0.055, ha="left", y=0.98,
                 fontsize=10, fontweight="bold")
    fig.legend(handles=[Patch(facecolor=blue, label="Stratum 1"),
                        Patch(facecolor=orange, hatch="///", label="Stratum 2")],
               loc="upper left", bbox_to_anchor=(0.12, 0.934), ncol=2, frameon=False)
    for y, w in [(1, 0.8), (0, 0.5)]:
        a.barh(y, 100*w, color=blue, height=0.5, edgecolor="white", linewidth=0.5)
        a.barh(y, 100*(1-w), left=100*w, color=orange, height=0.5,
               hatch="///", edgecolor="black", linewidth=0.3)
        a.text(50*w, y, f"{100*w:.0f}%", ha="center", va="center", color="white", fontsize=7.5)
        a.text(100*w + 50*(1-w), y, f"{100*(1-w):.0f}%", ha="center", va="center", fontsize=7.5,
               bbox={"facecolor": orange, "edgecolor": "none", "pad": 0.3})
    a.set(xlim=(0, 100), ylim=(-0.65, 1.65), xlabel="Composition (%)")
    a.set_yticks([1, 0], ["Target", "Sample"])
    a.set_xticks([0, 50, 100])
    a.set_title("Target vs sampled mix", loc="left", pad=13)
    a.tick_params(axis="y", length=0)
    rows = [("g1", 3.2, blue), ("g2", 2.2, orange)]
    for index, (stratum, y, color) in enumerate(rows):
        values = [p["difference_A_minus_B"] for p in pairs if p["stratum"] == stratum]
        b.scatter(values, y + 0.22 + np.linspace(-0.09, 0.09, len(values)),
                  s=20, facecolors="none", edgecolors=color, linewidths=0.9,
                  marker="o" if stratum == "g1" else "s", zorder=4)
        item = summary["strata"][index]
        mean, ci = item["mean_difference"], item["ci95_percentile"]
        b.errorbar(mean, y, xerr=[[mean-ci[0]], [ci[1]-mean]], fmt="D", color=color,
                   markersize=4.5, capsize=2.5, linewidth=1.05, zorder=3)
    for index, y in [(0, 1), (1, 0)]:
        item = summary["aggregates"][index]
        mean, ci = item["difference"], item["ci95_percentile"]
        b.errorbar(mean, y, xerr=[[mean-ci[0]], [ci[1]-mean]], fmt="D", color="black" if index == 0 else "#666666",
                   markerfacecolor="black" if index == 0 else "white", markersize=5,
                   capsize=2.5, linewidth=1.2, zorder=3)
    b.axvline(0, color="#999999", linestyle="--", linewidth=0.8)
    b.axhline(1.65, color="#dddddd", linewidth=0.65)
    b.set(xlim=(-1.9, 6.5), ylim=(-0.65, 3.9), xlabel="Paired difference A - B (score)")
    b.set_yticks([3.2, 2.2, 1, 0], ["Stratum 1 (n=4)", "Stratum 2 (n=4)", "Target 80/20", "Sample 50/50"])
    b.set_xticks([-1, 0, 2, 4, 6])
    b.tick_params(axis="y", length=0)
    b.set_title("Opposite stratum directions", loc="left", pad=13)
    b.text(-1.9, 3.82, "A lower", color="#555555", fontsize=7.5, va="bottom")
    b.text(6.5, 3.82, "B lower", color="#555555", fontsize=7.5, va="bottom", ha="right")
    w = np.linspace(0, 1, 101)
    m1, m2 = [row["mean_difference"] for row in summary["strata"]]
    crossing = summary["robustness"]["zero_crossing_stratum_1_weight"]
    c.plot(100*w, m2 + (m1-m2)*w, color="#444444", linewidth=1.1)
    c.axhline(0, color="#999999", linestyle="--", linewidth=0.8)
    c.scatter(50, summary["aggregates"][1]["difference"], marker="o", facecolors="white", edgecolors="#666666", s=26, zorder=4)
    c.scatter(80, summary["aggregates"][0]["difference"], marker="D", color="black", s=24, zorder=4)
    c.text(20, 0.8, "Sample", fontsize=7.5, ha="center")
    c.text(81, 0.3, "Target", fontsize=7.5, ha="left")
    c.text(18, -0.74, f"{100*crossing:.1f}%: tie", fontsize=7.5)
    c.plot([100*crossing, 100*crossing], [0, -0.63], color="#777777", linestyle=":", linewidth=0.7)
    c.set(xlim=(0, 100), ylim=(-1.1, 3.25), xlabel="Stratum 1 share (%)", ylabel="A - B (score)")
    c.set_xticks([0, 50, 100*crossing, 100], ["0", "50", f"{100*crossing:.1f}", "100"])
    c.set_yticks([-1, 0, 1, 2, 3])
    c.set_title("Alternative target weights", loc="left", pad=13)
    add_panel_labels(fig, axes=[a, b, c], labels=["a", "b", "c"],
                     x_offset_pt=-36, y_offset_pt=11, fontsize=9)
    fig.text(0.055, 0.063, "Open circles/squares: unit pairs. Diamonds: means. Bars: conditional 95% percentile bootstrap intervals.", fontsize=7)
    fig.text(0.055, 0.025, "Four independent units per stratum; target weights fixed. The curve varies the target, not its uncertainty.", fontsize=7)
    issues = audit_layout(fig)
    write_json("figure_layout_audit.json", {"issues": issues, "style": style,
               "width_mm": 180, "height_mm": 103, "minimum_font_pt": 7})
    assert not any(level == "FAIL" for level, _ in issues), issues
    render_preview(fig, str(HERE / "main_figure_preview.png"), dpi=180)
    if not preview_only:
        fig.savefig(HERE / "main_figure.png", dpi=600, bbox_inches=None)
        fig.savefig(HERE / "main_figure.svg", bbox_inches=None, metadata={"Date": None})
        with Image.open(HERE / "main_figure.png") as img:
            img.convert("L").save(HERE / "main_figure_grayscale.png", dpi=(600, 600))
        audits = []
        for filename in ["main_figure.png", "main_figure.svg"]:
            found, info = check_figure(str(HERE / filename), min_dpi=600, target_inches=size)
            assert not any(level == "FAIL" for level, _ in found), found
            audits.append({"file": filename, "issues": found, "info": info})
        write_json("figure_file_audit.json", audits)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview-only", action="store_true")
    args = parser.parse_args()
    pairs = paired_units(prepare())
    results = compute(pairs)
    figure(pairs, results, args.preview_only)
    print(json.dumps(results, indent=2))
    print("SYNTHETIC preparation, weighting, exact-bootstrap and hand-reference checks passed.")
