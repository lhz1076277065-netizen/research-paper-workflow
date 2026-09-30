"""Plot every frozen synthetic summary; no new data or interval estimation."""
import csv
import json
import os
import sys
from decimal import Decimal
from pathlib import Path

OUT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(OUT / ".mplconfig"))
sys.dont_write_bytecode = True
sys.path.insert(0, str(OUT / "sources/nature-figure/skills/nature-figure/scripts"))

import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import ScaledTranslation
from audit_panel_alignment import require_matplotlib_panel_alignment

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.7,
    "legend.frameon": False,
})

with (OUT / "fixed-results.csv").open() as handle:
    rows = list(csv.DictReader(line for line in handle if not line.startswith("#")))
assert len(rows) == 8
for row in rows:
    assert Decimal(row["lo"]) <= Decimal(row["loss"]) <= Decimal(row["hi"])
    assert int(row["n"]) > 0

weighted = {}
for condition in ("reference", "changed"):
    losses = {}
    for method in ("A", "B"):
        part = [row for row in rows if row["condition"] == condition and row["method"] == method]
        losses[method] = sum(Decimal(r["n"]) * Decimal(r["loss"]) for r in part) / sum(Decimal(r["n"]) for r in part)
    weighted[condition] = {**{k: str(v) for k, v in losses.items()}, "B_minus_A": str(losses["B"] - losses["A"])}
assert Decimal(weighted["reference"]["B_minus_A"]) == Decimal("-0.44")
assert Decimal(weighted["changed"]["B_minus_A"]) == Decimal("0.92")

fig, axes = plt.subplots(2, 1, figsize=(7.08661417, 4.52755906), gridspec_kw={"height_ratios": [0.7, 1.3]})  # 180 × 115 mm
fig.subplots_adjust(left=0.29, right=0.97, top=0.88, bottom=0.14, hspace=0.73)
gray, blue = "#5C626B", "#176E9C"
ax = axes[0]
ax.axvline(0, color="#AEB4BA", linewidth=0.8, linestyle="--", zorder=0)
for condition, y in [("reference", 1), ("changed", 0)]:
    delta = float(weighted[condition]["B_minus_A"])
    ax.plot(delta, y, marker="s", color=blue, markersize=5)
    ax.annotate(f"{delta:+.2f}".replace("-", "−"), (delta, y), xytext=(8, 0), textcoords="offset points", va="center", fontsize=8)
ax.set(xlim=(-1.2, 1.5), ylim=(-0.6, 1.6), yticks=[1, 0], yticklabels=["Reference", "Changed"], xlabel="Weighted loss difference (B − A)")
ax.set_xticks([-1, 0, 1])
ax.set_title("Weighted comparison", loc="left", pad=10)

ax = axes[1]
groups = [("reference", "S1"), ("reference", "S2"), ("changed", "S1"), ("changed", "S2")]
labels = []
for index, (condition, stratum) in enumerate(groups):
    y = 3 - index
    for method, offset, color, marker in [("A", 0.13, gray, "o"), ("B", -0.13, blue, "s")]:
        row = next(r for r in rows if (r["condition"], r["stratum"], r["method"]) == (condition, stratum, method))
        center, lower, upper = (float(row[k]) for k in ["loss", "lo", "hi"])
        ax.errorbar(center, y + offset, xerr=[[center - lower], [upper - center]], fmt=marker, color=color, ecolor=color, markersize=4.5, capsize=2.5, linewidth=1.0, label=method if index == 0 else None)
    labels.append(f"{condition.capitalize()} {stratum} (n = {row['n']})")
ax.set(xlim=(0, 10.5), ylim=(-0.6, 3.6), yticks=[3, 2, 1, 0], yticklabels=labels, xlabel="Row loss (fixture scale)")
ax.set_xticks([0, 2, 4, 6, 8, 10])
ax.set_title("Stratum comparisons", loc="left", pad=10)
ax.legend(loc="lower right", bbox_to_anchor=(1, 1.01), ncol=2, handlelength=1.2)
for letter, ax in zip("ab", axes):
    ax.tick_params(axis="y", length=0, pad=6)
    ax.text(0, 1, letter, transform=ax.transAxes + ScaledTranslation(-118 / 72, 10 / 72, fig.dpi_scale_trans), fontsize=10, fontweight="bold", va="bottom")
fig.text(0.5, 0.968, "Fixed synthetic benchmark", ha="center", fontsize=10)
fig.text(0.025, 0.026, "Bars in b: supplied 95% row intervals; no aggregate intervals in a.", fontsize=7)

fig.canvas.draw()
require_matplotlib_panel_alignment(fig, json_out=str(OUT / "figure.alignment.json"), overlay_svg=str(OUT / "figure.alignment.svg"), require_panel_labels=True, strict=True, tolerance_pt=1.5)
fig.savefig(OUT / "figure-1.svg")
fig.savefig(OUT / "figure-1.pdf")
fig.savefig(OUT / "figure-1.png", dpi=600)
plt.close(fig)
(OUT / "figure-data.json").write_text(json.dumps({"rows": rows, "weighted": weighted, "row_interval_level": "supplied 95%", "aggregate_intervals": "not available; not drawn", "excluded_rows": 0}, indent=2) + "\n")
print(json.dumps({"weighted": weighted, "rows_plotted": len(rows), "dimensions_mm": [180, 115]}))
