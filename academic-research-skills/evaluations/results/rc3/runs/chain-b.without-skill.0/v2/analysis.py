"""SYNTHETIC: paired, stratified descriptive analysis; fixed target weights."""
from pathlib import Path
from datetime import date, datetime, timezone
from collections import defaultdict
from itertools import product
import csv
import hashlib
import json
import math
import os
import sys

ROOT = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
sys.path.insert(0, str(ROOT / "vendor/scipilot"))

import numpy as np
import pandas as pd
import scipy
from scipy.stats import t
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import PIL
from profile_data import profile_data, render_report
from setup_style import setup_style
from visual_qa import audit_layout, render_preview
from check_figure import check_figure

WEIGHTS = {"g1": 0.8, "g2": 0.2}
SIZE_IN = (180 / 25.4, 100 / 25.4)
COLORS = {"g1": "#0072B2", "g2": "#E69F00"}


def dump_json(name, value):
    def native_scalar(item):
        if isinstance(item, np.generic):
            return item.item()
        raise TypeError(f"Unsupported JSON type: {type(item)}")
    (ROOT / name).write_text(json.dumps(value, indent=2, allow_nan=False, default=native_scalar) + "\n")


def read_member(name):
    identity = json.loads((ROOT / "archive_identity.json").read_text())
    expected = next(m["sha256"] for m in identity["members"] if m["path"] == name)
    path = ROOT / "inputs/original" / name
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != expected:
        raise ValueError(f"Original member changed: {name}")
    text = raw.decode("utf-8")
    with (ROOT / "derived_resource_reads.jsonl").open("a") as trace:
        trace.write(json.dumps({
            "read_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_archive_sha256": identity["archive_sha256"],
            "member": name, "member_sha256": digest,
            "line_start": 1, "line_end": len(text.splitlines()),
            "byte_count": len(raw), "purpose": "Rebuild analysis from original member",
        }) + "\n")
    return text


def prepare_events(raw, metadata):
    """Reject conflicting events and non-unique active metadata; convert before means."""
    events = {}
    removed = 0
    for row in raw:
        event_id = row["event_id"]
        if not event_id:
            raise ValueError("Empty event_id")
        if event_id in events:
            if events[event_id] != row:
                raise ValueError(f"Conflicting duplicate event: {event_id}")
            removed += 1
        else:
            events[event_id] = row.copy()
    prepared = []
    for row in events.values():
        observed = date.fromisoformat(row["observed_at"])
        # ponytail: scan 16 metadata rows per event; index by unit if archives grow.
        active = [m for m in metadata if m["unit_id"] == row["unit_id"]
                  and date.fromisoformat(m["valid_from"]) <= observed
                  <= date.fromisoformat(m["valid_to"])]
        if len(active) != 1:
            raise ValueError(f"Expected one active metadata record for {row['event_id']}, got {len(active)}")
        if row["method"] not in {"A", "B"}:
            raise ValueError("Unknown method")
        scale = {"score": 1.0, "subscore": 0.001}.get(row["measurement_unit"])
        if scale is None:
            raise ValueError("Unknown measurement unit")
        score = float(row["raw_value"]) * scale
        if not math.isfinite(score):
            raise ValueError("Non-finite score")
        if active[0]["stratum"] not in WEIGHTS:
            raise ValueError("Unknown stratum")
        prepared.append({**row, "score": score, "stratum": active[0]["stratum"],
                         "metadata_record": active[0]["record"]})
    return pd.DataFrame(prepared), removed


def pair_units(events):
    unit_strata = events.groupby("unit_id")["stratum"].nunique()
    if not (unit_strata == 1).all():
        raise ValueError("A unit has observations in more than one stratum")
    means = events.groupby(["unit_id", "stratum", "method"]).agg(
        score=("score", "mean"), n_technical=("score", "size"))
    scores = means["score"].unstack("method")
    counts = means["n_technical"].unstack("method")
    if set(scores.columns) != {"A", "B"} or scores.isna().any().any():
        raise ValueError("Incomplete paired unit")
    paired = scores.rename(columns={"A": "A_score", "B": "B_score"}).reset_index()
    paired["n_A_technical"] = counts["A"].to_numpy()
    paired["n_B_technical"] = counts["B"].to_numpy()
    paired["difference_A_minus_B"] = paired["A_score"] - paired["B_score"]
    return paired.sort_values("unit_id").reset_index(drop=True)


def bootstrap_means(values):
    """All equally likely ordered bootstrap samples of independent units in one stratum."""
    values = np.asarray(values, dtype=float)
    indices = np.array(list(product(range(len(values)), repeat=len(values))))
    return values[indices].mean(axis=1)


def percentile_interval(values):
    return np.quantile(values, [0.025, 0.975], method="linear").tolist()


def calculate(paired):
    summaries = {}
    boots = {}
    for group, frame in paired.groupby("stratum"):
        differences = frame["difference_A_minus_B"].to_numpy()
        assert len(frame) == 4, "Fixture requires four independent units per stratum"
        boots[group] = bootstrap_means(differences)
        summaries[group] = {
            "n_independent_units": len(frame), "target_weight": WEIGHTS[group],
            "sample_weight": len(frame) / len(paired),
            "A_mean_score": float(frame["A_score"].mean()),
            "B_mean_score": float(frame["B_score"].mean()),
            "difference_A_minus_B": float(differences.mean()),
            "sd_difference": float(differences.std(ddof=1)),
            "bootstrap_percentile_95": percentile_interval(boots[group]),
            "n_bootstrap_ordered_samples": len(boots[group]),
        }
    assert set(summaries) == set(WEIGHTS) and len(paired) == 8
    target_boot = (WEIGHTS["g1"] * boots["g1"][:, None]
                   + WEIGHTS["g2"] * boots["g2"][None, :]).ravel()
    sample_boot = (0.5 * boots["g1"][:, None] + 0.5 * boots["g2"][None, :]).ravel()
    aggregates = {}
    for name, weights, boot in [("target", WEIGHTS, target_boot),
                               ("sample_mix", {"g1": 0.5, "g2": 0.5}, sample_boot)]:
        A = sum(weights[g] * summaries[g]["A_mean_score"] for g in weights)
        B = sum(weights[g] * summaries[g]["B_mean_score"] for g in weights)
        aggregates[name] = {
            "weights": weights, "A_mean_score": A, "B_mean_score": B,
            "difference_A_minus_B": A - B,
            "bootstrap_percentile_95": percentile_interval(boot),
            "n_joint_ordered_bootstrap_samples": len(boot),
        }
    loo = []
    for unit in paired["unit_id"]:
        reduced = paired[paired["unit_id"] != unit]
        stratum_means = reduced.groupby("stratum")["difference_A_minus_B"].mean()
        estimate = sum(WEIGHTS[g] * stratum_means[g] for g in WEIGHTS)
        loo.append({"omitted_unit": unit,
                    "omitted_stratum": paired.loc[paired["unit_id"] == unit, "stratum"].iloc[0],
                    "target_difference_A_minus_B": float(estimate),
                    "g1_n": int((reduced["stratum"] == "g1").sum()),
                    "g2_n": int((reduced["stratum"] == "g2").sum())})
    pd.DataFrame(loo).to_csv(ROOT / "robustness_leave_one_out.csv", index=False)
    d1, d2 = [summaries[g]["difference_A_minus_B"] for g in ["g1", "g2"]]
    grid = np.linspace(0, 1, 101)
    pd.DataFrame({"g1_weight": grid, "g2_weight": 1 - grid,
                  "difference_A_minus_B": grid * d1 + (1 - grid) * d2}).to_csv(
                      ROOT / "robustness_weight_sensitivity.csv", index=False)
    components = [WEIGHTS[g] ** 2 * summaries[g]["sd_difference"] ** 2 / 4 for g in WEIGHTS]
    variance = sum(components)
    degrees_freedom = variance ** 2 / sum(v ** 2 / 3 for v in components)
    half_width = float(t.ppf(0.975, degrees_freedom) * math.sqrt(variance))
    target = aggregates["target"]["difference_A_minus_B"]
    sensitivity = {
        "leave_one_unit_out_fixed_target_weights": {
            "n_checks": len(loo),
            "range": [min(r["target_difference_A_minus_B"] for r in loo),
                      max(r["target_difference_A_minus_B"] for r in loo)],
            "all_negative": all(r["target_difference_A_minus_B"] < 0 for r in loo),
        },
        "composition": {"zero_crossing_g1_weight": d2 / (d2 - d1),
                        "difference_at_g1_0_7": 0.7 * d1 + 0.3 * d2,
                        "difference_at_g1_0_9": 0.9 * d1 + 0.1 * d2},
        "alternative_welch_satterthwaite_approximation": {
            "standard_error": math.sqrt(variance), "degrees_freedom": degrees_freedom,
            "approximate_95_interval": [target - half_width, target + half_width],
            "assumption": "Independent units within strata; within-stratum normal paired differences for small-sample t approximation",
        },
    }
    result = {"synthetic": True, "score_direction": "lower is better",
              "contrast": "A minus B; negative favors A", "strata": summaries,
              "aggregates": aggregates, "robustness": sensitivity,
              "interval": {"method": "Approximate 95% percentile stratified paired unit bootstrap",
                           "weights": "Fixed; no uncertainty in target composition included",
                           "sampling": "All 256 ordered resamples per stratum and 65536 joint combinations; no Monte Carlo",
                           "quantile": "numpy.quantile(method='linear')",
                           "scope": "Conditional on fixture independence and empirical within-stratum units; population coverage not validated"}}
    dump_json("results.json", result)
    np.savez_compressed(ROOT / "bootstrap_distribution.npz", g1=boots["g1"], g2=boots["g2"],
                        target=target_boot, sample_mix=sample_boot)
    pd.DataFrame.from_dict(summaries, orient="index").to_csv(ROOT / "stratum_summary.csv", index_label="stratum")
    return result


def make_figure(result):
    style = setup_style(journal="nature", lang="en", use_sciplots=False,
                        constrained_layout=False)
    plt.rcParams.update({"font.sans-serif": ["DejaVu Sans"], "font.size": 8,
                         "axes.labelsize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8,
                         "savefig.bbox": None, "svg.fonttype": "none"})
    fig = plt.figure(figsize=SIZE_IN)
    fig.suptitle("SYNTHETIC | A–B contrasts depend on the target composition", fontsize=10, y=0.97)
    ax_a = fig.add_axes([0.10, 0.33, 0.26, 0.48])
    ax_b = fig.add_axes([0.56, 0.26, 0.41, 0.55])
    ax_a.set_title("a  Target and sampled mix", loc="left", fontweight="bold", fontsize=8, pad=12)
    ax_b.set_title("b  Paired A−B differences", loc="left", fontweight="bold", fontsize=8, pad=12)
    for y, weights in [(1, [0.8, 0.2]), (0, [0.5, 0.5])]:
        start = 0
        for g, weight, hatch in zip(["g1", "g2"], weights, ["///", "..."]):
            ax_a.barh(y, weight, left=start, height=0.48, color=COLORS[g],
                      edgecolor="white", linewidth=0.6, hatch=hatch)
            ax_a.text(start + weight / 2, y, f"{int(round(weight * 100))}%", ha="center", va="center",
                      color="white" if g == "g1" else "black", fontsize=8)
            start += weight
    ax_a.set_yticks([0, 1], ["Sample\n4 + 4 units", "Target\nstipulated"])
    ax_a.tick_params(axis="y", length=0)
    ax_a.set_xlim(0, 1)
    ax_a.set_ylim(-0.65, 1.7)
    ax_a.set_xticks([0, 0.5, 1], ["0", "50", "100"])
    ax_a.set_xlabel("Composition (%)")
    ax_a.spines["left"].set_visible(False)
    from matplotlib.patches import Patch
    ax_a.legend(handles=[Patch(facecolor=COLORS[g], edgecolor="white", hatch=h, label=g)
                        for g, h in [("g1", "///"), ("g2", "...")]],
                frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.24), fontsize=8)
    paired = pd.read_csv(ROOT / "paired_units.csv")
    labels = []
    rows = [(3, "g1", "g1 (n = 4)"), (2, "g2", "g2 (n = 4)"),
            (1, "target", "Target 80/20"), (0, "sample_mix", "Sample 50/50")]
    for y, key, label in rows:
        stats = result["strata"][key] if key in WEIGHTS else result["aggregates"][key]
        estimate = stats["difference_A_minus_B"]
        lo, hi = stats["bootstrap_percentile_95"]
        color = COLORS.get(key, "black" if key == "target" else "#6B6B6B")
        marker = "o" if key == "g1" else "s"
        if key in WEIGHTS:
            values = paired.loc[paired["stratum"] == key, "difference_A_minus_B"].to_numpy()
            offsets = [0.18, 0.10, 0.18, 0.26]
            ax_b.scatter(values, y + np.array(offsets), s=15, marker=marker,
                         facecolors="none", edgecolors=color, linewidths=0.8, zorder=3)
        ax_b.errorbar(estimate, y - 0.10 if key in WEIGHTS else y,
                      xerr=[[estimate - lo], [hi - estimate]], fmt="D", color=color,
                      markerfacecolor="white" if key == "sample_mix" else color,
                      markersize=4, capsize=2, linewidth=1.2, zorder=4)
        labels.append(f"{label}\nΔ = {estimate:+.2f}")
    ax_b.axvline(0, color="#A0A0A0", linestyle="--", linewidth=0.8, zorder=0)
    ax_b.axhline(1.5, color="#DDDDDD", linewidth=0.6)
    ax_b.set_yticks([3, 2, 1, 0], labels)
    ax_b.tick_params(axis="y", length=0)
    ax_b.set_xlim(-2, 6.5)
    ax_b.set_ylim(-0.6, 3.6)
    ax_b.set_xticks([-2, 0, 2, 4, 6])
    ax_b.set_xlabel("A − B (score)")
    ax_b.spines["left"].set_visible(False)
    fig.text(0.76, 0.125, "← lower for A     lower for B →", ha="center", fontsize=8)
    fig.text(0.10, 0.055, "Diamonds: means. Small open points: paired units. Whiskers: approximate 95% percentile bootstrap.", fontsize=7)
    preview = render_preview(fig, str(ROOT / "main_figure_preview.png"), dpi=150)
    layout_issues = audit_layout(fig)
    assert not any(severity == "FAIL" for severity, _ in layout_issues), layout_issues
    # Final physical dimensions are preserved: no tight bounding-box resizing.
    fig.savefig(ROOT / "main_figure.png", dpi=600, bbox_inches=None)
    fig.savefig(ROOT / "main_figure.svg", bbox_inches=None)
    Image.open(ROOT / "main_figure.png").convert("L").save(ROOT / "main_figure_grayscale.png", dpi=(600, 600))
    files = {}
    for name in ["main_figure.png", "main_figure.svg"]:
        issues, info = check_figure(str(ROOT / name), min_dpi=300, target_inches=SIZE_IN)
        assert not any(s == "FAIL" for s, _ in issues), issues
        files[name] = {"issues": issues, "info": info}
    dump_json("figure_machine_qa.json", {"layout_issues": layout_issues, "files": files,
                                       "width_mm": 180, "height_mm": 100,
                                       "style": style, "preview": preview,
                                       "visual_review": "See checks.md for separate Agent PNG inspection"})
    plt.close(fig)


def main():
    started = datetime.now(timezone.utc).isoformat()
    raw = list(csv.DictReader(read_member("measurements.csv").splitlines()))
    metadata = list(csv.DictReader(read_member("units.csv").splitlines()))
    events, removed = prepare_events(raw, metadata)
    paired = pair_units(events)
    events.to_csv(ROOT / "prepared_events.csv", index=False)
    paired.to_csv(ROOT / "paired_units.csv", index=False)
    flow = {"raw_event_rows": len(raw), "exact_duplicate_archive_rows_removed": removed,
            "unique_measurement_events": len(events), "unit_metadata_history_rows": len(metadata),
            "independent_paired_units": len(paired), "stratum_unit_counts": paired["stratum"].value_counts().to_dict(),
            "technical_events_by_method": events["method"].value_counts().to_dict(),
            "unmatched_metadata": 0, "multiply_matched_metadata": 0,
            "incomplete_pairs": 0, "missing_score_values": 0,
            "independence": "Stipulated by dictionary for fixture within-stratum resampling; real population independence unknown"}
    dump_json("flow.json", flow)
    profile = profile_data(paired, group_cols=["stratum"])
    dump_json("profile.json", profile)
    (ROOT / "profile.md").write_text(render_report(profile) + "\n")
    result = calculate(paired)
    make_figure(result)
    receipt = {
        "analysis_started_at_utc": started,
        "analysis_finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "libraries": {"numpy": np.__version__, "pandas": pd.__version__,
                  "scipy": scipy.__version__, "matplotlib": matplotlib.__version__, "Pillow": PIL.__version__},
        "professional_calls": ["profile_data(paired, group_cols=['stratum'])", "render_report(profile)",
             "setup_style(journal='nature', lang='en', use_sciplots=False, constrained_layout=False)",
             "render_preview(fig, main_figure_preview.png, dpi=150)", "audit_layout(fig)",
             "check_figure(main_figure.png/svg, min_dpi=300, target_inches=(180/25.4,100/25.4))"],
        "external_model_calls": 0, "subagents_created": 0,
        "token_usage": "unknown", "cost": "unknown",
    }
    dump_json("analysis_receipt.json", receipt)
    print(json.dumps({"flow": flow, "result": result}, indent=2))


if __name__ == "__main__":
    main()
