"""Rebuild the fixed synthetic figure. Preview first; use --stage final after inspection.

Professional implementation: SciPilot, main@43098ddb9e6a6d142218540c114f9ed38922fc42.
The bundled provider/ scripts are unchanged MIT-licensed upstream files.
"""
from pathlib import Path
import argparse
import csv
from decimal import Decimal
import hashlib
import json
import math
import os
import sys

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".runtime" / "matplotlib"))
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "provider" / "scripts"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from PIL import Image
import pandas as pd
from profile_data import profile_data
from setup_style import setup_style
from layout_tools import finalize_figure, add_panel_labels
from visual_qa import audit_layout, render_preview
from export_figure import export_figure
from check_figure import check_figure

SIZE = (180 / 25.4, 132 / 25.4)
INPUT_SHA256 = "a3b1fcc3f32705955e861c529c915845b5ceac0b84f50037fd9f5dcaf1764884"
METHODS = {"A": ("#0072B2", "o", 0.13), "B": ("#D55E00", "s", -0.13)}


def write_json(name, content):
    (ROOT / name).write_text(json.dumps(content, indent=2, ensure_ascii=False,
                                      default=lambda value: value.item()) + "\n")


def read_and_check():
    path = ROOT / "fixed-results.csv"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == INPUT_SHA256
    with path.open(newline="") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    assert len(rows) == 8
    keys = {(r["condition"], r["stratum"], r["method"]) for r in rows}
    assert len(keys) == 8
    assert keys == {(c, s, m) for c in ("reference", "changed")
                    for s in ("S1", "S2") for m in METHODS}
    for r in rows:
        r["n"] = int(r["n"])
        for col in ("loss", "lo", "hi"):
            r[col] = Decimal(r[col])
        assert r["n"] > 0 and r["lo"] <= r["loss"] <= r["hi"]
    by_key = {(r["condition"], r["stratum"], r["method"]): r for r in rows}
    weights = {}
    for condition in ("reference", "changed"):
        counts = {s: by_key[condition, s, "A"]["n"] for s in ("S1", "S2")}
        assert all(counts[s] == by_key[condition, s, "B"]["n"] for s in counts)
        assert sum(counts.values()) == 100  # Per method; A/B counts are not added.
        weights[condition] = {s: Decimal(n) / 100 for s, n in counts.items()}
    assert weights["reference"] == {"S1": Decimal(".8"), "S2": Decimal(".2")}
    assert weights["changed"] == {"S1": Decimal(".2"), "S2": Decimal(".8")}
    summaries = []
    for condition, weight_condition, label in (
        ("reference", "reference", "Reference; observed 80:20"),
        ("changed", "changed", "Changed; observed 20:80"),
        ("changed", "reference", "Changed; fixed reference 80:20"),
    ):
        w = weights[weight_condition]
        loss = {m: sum(w[s] * by_key[condition, s, m]["loss"] for s in w)
                for m in METHODS}
        summaries.append({"label": label, "condition": condition,
                          "weight_source": weight_condition,
                          "S1_weight": str(w["S1"]), "S2_weight": str(w["S2"]),
                          "A_loss": str(loss["A"]), "B_loss": str(loss["B"]),
                          "B_minus_A": str(loss["B"] - loss["A"]),
                          "interval": None})
    assert [(s["A_loss"], s["B_loss"], s["B_minus_A"]) for s in summaries] == [
        ("4.80", "4.36", "-0.44"), ("6.60", "7.52", "0.92"),
        ("5.40", "5.48", "0.08")]
    contrasts = [{"condition": c, "stratum": s,
                  "B_minus_A": str(by_key[c, s, "B"]["loss"] -
                                   by_key[c, s, "A"]["loss"]),
                  "interval": None}
                 for c in ("reference", "changed") for s in ("S1", "S2")]
    assert [Decimal(d["B_minus_A"]) for d in contrasts] == [
        Decimal("-.8"), Decimal("1.0"), Decimal("-.2"), Decimal("1.2")]
    write_json("numeric-review.json", {
        "input_sha256": INPUT_SHA256, "rows": len(rows),
        "all_row_values_and_intervals_locked_by_hash": True,
        "intervals_reestimated": False, "aggregate_intervals_supplied": False,
        "weighted_summaries": summaries, "stratum_contrasts": contrasts,
        "tests": "Exact Decimal assertions for weights, all summaries and four stratum contrasts.",
        "inference": "Descriptive only; no significance, causality or mechanism inference."})
    with (ROOT / "weighted-summaries.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summaries[0]))
        writer.writeheader(); writer.writerows(summaries)
    # The profiler's n_rows/group counts refer to summary rows, not observations.
    df = pd.read_csv(path, comment="#")
    for col in ("condition", "stratum", "method"):
        df[col] = df[col].astype(object)
    profile = profile_data(df, group_cols=["condition", "stratum", "method"])
    profile["scope_note"] = ("8 fixed summary rows, not raw samples. Group-row counts, "
                             "correlations and distribution suggestions are not sample evidence; "
                             "the supplied n column gives per-method stratum counts.")
    write_json("provider-data-profile.json", profile)
    return rows, by_key, weights, summaries


def make_figure(by_key, weights, summaries):
    style = setup_style(journal="general", lang="en", use_sciplots=False)
    plt.rcParams.update({"font.sans-serif": ["DejaVu Sans"], "font.size": 8,
                         "axes.labelsize": 8.5, "axes.titlesize": 9.5,
                         "xtick.labelsize": 8, "ytick.labelsize": 8,
                         "legend.fontsize": 8, "hatch.linewidth": 0.4})
    fig, axes = plt.subplots(2, 2, figsize=SIZE, gridspec_kw={"height_ratios": [1, 1.06]})
    plotted_rows = []
    for ax, condition in zip(axes[0], ("reference", "changed")):
        for method, (color, marker, offset) in METHODS.items():
            for y, stratum in ((1, "S1"), (0, "S2")):
                r = by_key[condition, stratum, method]
                x, lo, hi = map(float, (r["loss"], r["lo"], r["hi"]))
                # SciPilot errorbar recipe, adapted to supplied asymmetric intervals.
                artist = ax.errorbar(x, y + offset, xerr=[[x - lo], [hi - x]],
                                     fmt=marker, color=color, ecolor=color, elinewidth=.9,
                                     capsize=2, capthick=.8, markersize=4.5,
                                     markeredgecolor="black", markeredgewidth=.4)
                displayed_x = float(artist.lines[0].get_xdata()[0])
                displayed_bounds = artist.lines[2][0].get_segments()[0][:, 0].tolist()
                assert math.isclose(displayed_x, x, abs_tol=1e-12)
                assert all(math.isclose(a, b, abs_tol=1e-12)
                           for a, b in zip(displayed_bounds, [lo, hi]))
                plotted_rows.append({"condition": condition, "stratum": stratum,
                                     "method": method, "point": displayed_x,
                                     "interval": displayed_bounds})
                ax.annotate(f"{x:.1f}", (hi, y + offset), xytext=(4, 0),
                            textcoords="offset points", va="center", color=color)
        ax.set(xlim=(0, 10.4), ylim=(-.5, 1.60), xticks=[0, 2, 4, 6, 8, 10],
               yticks=[1, 0], yticklabels=[
                   f"S1 (n={by_key[condition, 'S1', 'A']['n']})",
                   f"S2 (n={by_key[condition, 'S2', 'A']['n']})"],
               xlabel="Loss (lower is better)", title=condition.capitalize() + " condition")
        ax.grid(axis="x", color=".9", linewidth=.5)
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    handles = [Line2D([], [], color=color, marker=marker, linestyle="none",
                      markersize=4.5, label="Method " + method)
               for method, (color, marker, _) in METHODS.items()]
    axes[0, 0].legend(handles=handles, loc="upper left", ncol=2,
                      frameon=False, handletextpad=.4, columnspacing=1)

    ax = axes[1, 0]
    for y, condition in ((1, "reference"), (0, "changed")):
        s1 = float(weights[condition]["S1"] * 100)
        ax.barh(y, s1, height=.40, color=".82", edgecolor=".25", linewidth=.6)
        ax.barh(y, 100 - s1, left=s1, height=.40, color=".35",
                edgecolor=".25", linewidth=.6, hatch="///")
        ax.text(s1 / 2, y, f"{s1:.0f}%", ha="center", va="center")
        ax.text(s1 + (100 - s1) / 2, y, f"{100-s1:.0f}%", ha="center", va="center", color="white")
    ax.set(xlim=(0, 100), ylim=(-.55, 1.6), yticks=[1, 0],
           yticklabels=["Reference", "Changed"], xticks=[0, 20, 40, 60, 80, 100],
           xlabel="Stratum weight (%)", title="Acquisition mix (n=100 per method)")
    ax.legend(handles=[Patch(facecolor=".82", edgecolor=".25", label="S1"),
                       Patch(facecolor=".35", edgecolor=".25", hatch="///", label="S2")],
              ncol=2, loc="upper left", frameon=False, handlelength=1.3)
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)

    ax = axes[1, 1]
    ax.axvline(0, color=".5", linestyle="--", linewidth=.8, zorder=0)
    for i, s in enumerate(summaries):
        d = float(s["B_minus_A"])
        ax.plot(d, 2 - i, marker="D", markersize=5,
                markerfacecolor="white" if i == 2 else ".15",
                markeredgecolor=".15", linestyle="none")
        ax.annotate(f"{d:+.2f}", (d, 2-i), xytext=(7, 0),
                    textcoords="offset points", va="center", fontsize=8.5)
    ax.set(xlim=(-.95, 1.43), ylim=(-.6, 2.7), xticks=[-.5, 0, .5, 1.0],
           yticks=[2, 1, 0], yticklabels=["Reference\n80:20 observed", "Changed\n20:80 observed", "Changed\n80:20 fixed"],
           xlabel="Loss difference (B - A)", title="Weighted comparisons; no intervals")
    ax.text(-.63, 2.47, "B lower loss", ha="center", fontsize=7.5, color=".35")
    ax.text(.65, 2.47, "A lower loss", ha="center", fontsize=7.5, color=".35")
    ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
    layout = finalize_figure(fig)
    fig.get_layout_engine().set(rect=(.02, .065, .96, .90), hspace=.12, wspace=.10)
    add_panel_labels(fig, axes=axes.flat, fontsize=10, x_offset_pt=-13, y_offset_pt=5)
    fig.text(.02, .018, "Synthetic fixed results. Panels a-b: supplied row-level 95% intervals. Panel d: derived point differences only.",
             fontsize=7.5, va="bottom")
    fig.canvas.draw()
    issues = audit_layout(fig)
    assert len(plotted_rows) == 8
    write_json("plotted-row-review.json", {"rows": plotted_rows,
                                         "all_8_actual_artists_match_input": True})
    write_json("layout-review.json", {"provider_style": style, "layout": layout,
                                     "issues": issues, "size_inches": SIZE,
                                     "minimum_font_pt": 7.5})
    assert not issues, f"Resolve layout issues before delivery: {issues}"
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["preview", "final"], default="preview")
    args = parser.parse_args()
    _, by_key, weights, summaries = read_and_check()
    fig = make_figure(by_key, weights, summaries)
    if args.stage == "preview":
        render_preview(fig, str(ROOT / "review-preview.png"), dpi=150)
        Image.open(ROOT / "review-preview.png").convert("L").save(ROOT / "review-preview-grayscale.png")
    else:
        export_figure(fig, str(ROOT / "main-figure"), formats=["pdf", "svg", "png"],
                      size_inches=SIZE, dpi=300, tight=False, grayscale_preview=False)
        Image.open(ROOT / "main-figure.png").convert("L").save(ROOT / "main-figure-grayscale.png", dpi=(300, 300))
        audits = []
        for ext in ("pdf", "svg", "png"):
            path = ROOT / f"main-figure.{ext}"
            issues, info = check_figure(str(path), min_dpi=300, target_inches=SIZE)
            audits.append({"file": path.name, "issues": issues, "info": info})
            assert not any(s == "FAIL" for s, _ in issues)
        write_json("format-review.json", audits)
    plt.close(fig)
    print("Exact numeric checks and provider layout audit passed; stage:", args.stage)


if __name__ == "__main__":
    main()
