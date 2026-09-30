#!/usr/bin/env python3
"""Rebuild the fixed figure: python plot_main_figure.py.

Layout and direct annotation adapted from Nicolas P. Rougier (2021),
scientific-visualization-book, master @ 62fa569f30333c817c13e4dc757877c1192fd15a:
code/layout/layout-gridspec.py and code/ornaments/annotation-direct.py.
Copyright 2021 Nicolas P. Rougier; BSD terms: source-reference/LICENSE.txt.
The reference examples' simulated data and stylistic defaults are not used.
"""
import csv
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.text import Text

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "fixed-results.csv"
EXPECTED_SHA = "a3b1fcc3f32705955e861c529c915845b5ceac0b84f50037fd9f5dcaf1764884"
METHODS = ("A", "B")
CONDITIONS = ("reference", "changed")
STRATA = ("S1", "S2")
COLORS = {"A": "#0072B2", "B": "#D55E00"}
MARKERS = {"A": "o", "B": "s"}


def main():
    raw = DATA.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA, "Fixed input changed"
    rows = list(csv.DictReader(line for line in raw.decode().splitlines() if not line.startswith("#")))
    assert len(rows) == 8
    values = {}
    for row in rows:
        key = (row["condition"], row["stratum"], row["method"])
        assert key not in values
        r = {name: float(row[name]) for name in ("n", "loss", "lo", "hi")}
        assert r["n"] > 0 and r["n"].is_integer() and r["lo"] <= r["loss"] <= r["hi"]
        values[key] = r
    assert set(values) == {(c, s, m) for c in CONDITIONS for s in STRATA for m in METHODS}
    weights, means = {}, {}
    for c in CONDITIONS:
        totals = {m: sum(values[c, s, m]["n"] for s in STRATA) for m in METHODS}
        assert totals["A"] == totals["B"] == 100
        for s in STRATA:
            assert values[c, s, "A"]["n"] == values[c, s, "B"]["n"]
            weights[c, s] = values[c, s, "A"]["n"] / totals["A"]
        for m in METHODS:
            means[c, m] = sum(weights[c, s] * values[c, s, m]["loss"] for s in STRATA)
    expected = {("reference", "A"): 4.80, ("reference", "B"): 4.36,
                ("changed", "A"): 6.60, ("changed", "B"): 7.52}
    assert all(abs(means[k] - v) < 1e-12 for k, v in expected.items())
    assert means["reference", "B"] < means["reference", "A"]
    assert means["changed", "A"] < means["changed", "B"]

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                         "axes.titlesize": 10, "axes.labelsize": 9,
                         "axes.linewidth": 0.7, "svg.fonttype": "none", "pdf.fonttype": 42})
    fig = plt.figure(figsize=(8.6, 5.1), facecolor="white")
    # A spans both rows; B shows the weighting context immediately above C.
    gs = fig.add_gridspec(2, 2, width_ratios=(1.36, 1), height_ratios=(1, 1),
                          left=0.20, right=0.97, bottom=0.15, top=0.80,
                          wspace=0.35, hspace=0.72)
    axa = fig.add_subplot(gs[:, 0])
    axb = fig.add_subplot(gs[0, 1])
    axc = fig.add_subplot(gs[1, 1])
    fig.text(0.035, 0.94, "Method ranking varies by stratum and acquisition condition",
             fontsize=13, fontweight="bold", va="top")
    fig.text(0.035, 0.882, "Fixed synthetic results  |  Lower loss is better",
             fontsize=9.5, color="#4B5563", va="top")

    for ax in (axa, axb, axc):
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", length=3, width=0.7)
        ax.set_axisbelow(True)
        ax.grid(axis="x", color="#E4E7EB", linewidth=0.6)

    axa.set_title("a  Stratum-specific loss", loc="left", fontweight="bold", pad=12)
    positions = [("reference", "S1", 3.1), ("reference", "S2", 2.1),
                 ("changed", "S1", 0.95), ("changed", "S2", -0.05)]
    axa.axhline(1.55, color="#CDD3D9", linewidth=0.8)
    plotted_intervals = []
    for c, s, y in positions:
        for m, offset in (("A", 0.15), ("B", -0.15)):
            r = values[c, s, m]
            axa.errorbar(r["loss"], y + offset,
                         xerr=[[r["loss"] - r["lo"]], [r["hi"] - r["loss"]]],
                         fmt=MARKERS[m], color=COLORS[m], markersize=5.2,
                         elinewidth=1.2, capsize=2.5, capthick=1.1, zorder=3)
            axa.annotate(f'{r["loss"]:.1f}', xy=(r["hi"], y + offset),
                         xytext=(5, 0), textcoords="offset points", va="center",
                         color=COLORS[m], fontsize=8.5)
            plotted_intervals.append({"condition": c, "stratum": s, "method": m,
                                      "loss": r["loss"], "lo": r["lo"], "hi": r["hi"]})
    axa.set_yticks([p[2] for p in positions],
                  [f'{c.title()} · {s}\nn = {int(values[c, s, "A"]["n"])}; w = {weights[c, s]:.2f}'
                   for c, s, _ in positions])
    axa.set(xlim=(2.5, 10.3), ylim=(-0.6, 3.7), xlabel="Loss (supplied 95% intervals)")
    axa.set_xticks([3, 5, 7, 9])
    handles = [Line2D([], [], marker=MARKERS[m], color=COLORS[m], linestyle="none",
                      markersize=5, label=f"Method {m}") for m in METHODS]
    legend = fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.97, 0.902),
                        ncol=2, frameon=False, handletextpad=0.3, columnspacing=1.4, fontsize=8.5)

    axb.set_title("b  Stratum weights", loc="left", fontweight="bold", pad=12)
    for c, y in (("reference", 1), ("changed", 0)):
        left = 0
        for s, color, textcolor in (("S1", "#5D6A78", "white"), ("S2", "#DCE2E8", "#26313D")):
            w = weights[c, s]
            axb.barh(y, 100 * w, left=100 * left, height=0.48,
                     color=color, edgecolor="white", linewidth=0.5)
            axb.text(100 * (left + w / 2), y, f"{s}\n{100*w:.0f}%", ha="center",
                     va="center", color=textcolor, fontsize=8.5)
            left += w
    axb.set(xlim=(0, 100), ylim=(-0.5, 1.5), xlabel="Share of observations (%)")
    axb.set_xticks([0, 50, 100])
    axb.set_yticks([1, 0], ["Reference", "Changed"])

    axc.set_title("c  Weighted loss", loc="left", fontweight="bold", pad=12)
    for c, y in (("reference", 1), ("changed", 0)):
        for m, offset in (("A", 0.16), ("B", -0.16)):
            v = means[c, m]
            axc.plot(v, y + offset, MARKERS[m], color=COLORS[m], markersize=5.2)
            axc.annotate(f"{m} {v:.2f}", xy=(v, y + offset), xytext=(5, 0),
                         textcoords="offset points", va="center", color=COLORS[m], fontsize=8.5)
    axc.set(xlim=(3.85, 8.7), ylim=(-0.5, 1.5), xlabel="Loss (point means only)")
    axc.set_xticks([4, 6, 8])
    axc.set_yticks([1, 0], ["Reference", "Changed"])
    footer = fig.text(0.035, 0.030, "Weights = n / Σn within each condition. Aggregate intervals and significance tests are unavailable.",
                      fontsize=8.2, color="#4B5563", va="bottom")

    # One runnable numeric/geometry check; preserves fixed intervals and omits aggregate error bars.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    clipped = []
    for t in fig.findobj(Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        box = t.get_window_extent(renderer)
        if box.x0 < bounds.x0 - 0.5 or box.y0 < bounds.y0 - 0.5 or box.x1 > bounds.x1 + 0.5 or box.y1 > bounds.y1 + 0.5:
            clipped.append(t.get_text())
    assert not clipped, f"Text falls outside canvas: {clipped}"
    assert not legend.get_window_extent(renderer).overlaps(footer.get_window_extent(renderer))
    for ext in ("svg", "pdf", "png"):
        fig.savefig(ROOT / f"main-figure.{ext}", dpi=300, facecolor="white")
    summary = {"input_sha256": hashlib.sha256(raw).hexdigest(), "row_count": len(rows),
               "intervals_reestimated": False, "aggregate_intervals_drawn": False,
               "weighted_means": {c: {m: round(means[c, m], 2) for m in METHODS} for c in CONDITIONS},
               "stratum_weights": {c: {s: weights[c, s] for s in STRATA} for c in CONDITIONS},
               "difference_B_minus_A": {c: round(means[c, "B"] - means[c, "A"], 2) for c in CONDITIONS},
               "within_stratum_difference_B_minus_A": [
                   {"condition": c, "stratum": s,
                    "difference": round(values[c, s, "B"]["loss"] - values[c, s, "A"]["loss"], 2)}
                   for c in CONDITIONS for s in STRATA],
               "drawn_row_estimates_and_intervals": plotted_intervals,
               "checks": {"fixed_hash": "pass", "complete_unique_rows": "pass",
                          "n_and_interval_bounds": "pass", "expected_weighted_means": "pass",
                          "ranking_reversal": "pass", "text_within_canvas": "pass",
                          "legend_footer_separated": "pass"},
               "runtime": {"python": sys.version, "matplotlib": matplotlib.__version__}}
    (ROOT / "numeric-review.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"weighted_means": summary["weighted_means"], "checks": summary["checks"]}, indent=2))
    plt.close(fig)


if __name__ == "__main__":
    main()
