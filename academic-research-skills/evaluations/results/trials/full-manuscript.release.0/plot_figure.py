"""Reproduce Figure 1 from frozen summary values; no new statistical inference."""
from pathlib import Path
from decimal import Decimal
import argparse
import csv
import json
import os
import sys

OUT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(OUT / "process/mpl-config"))
sys.path.insert(0, str(OUT / "source-snapshots/Haojae/scripts"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
from PIL import Image
from profile_data import profile_data
from setup_style import setup_style
from visual_qa import audit_layout, render_preview
from export_figure import export_figure
from check_figure import check_figure

parser = argparse.ArgumentParser()
parser.add_argument("--export", action="store_true")
args = parser.parse_args()
values = json.loads((OUT / "verified-values.json").read_text())
rows = values["rows"]
assert len(rows) == 8
frame = pd.read_csv(OUT / "inputs/fixed-results.csv", comment="#")
profile = profile_data(frame, group_cols=["condition", "stratum"])
profile["interpretation"] = "Summary-row structure only. Profiler correlations, skewness, distribution suggestions and small-group counts are not inferential evidence or supplied sample n."
(OUT / "process/data-profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2, default=lambda value: value.item()) + "\n")

style = setup_style(journal="general", lang="en", use_sciplots=False, constrained_layout=False)
plt.rcParams.update({"font.sans-serif": ["DejaVu Sans"], "font.size": 8.5,
                     "axes.labelsize": 9, "axes.titlesize": 10,
                     "xtick.labelsize": 8, "ytick.labelsize": 8.5,
                     "legend.fontsize": 8.5})
fig, ax = plt.subplots(figsize=(6.3, 4.7))
fig.subplots_adjust(left=0.30, right=0.85, bottom=0.22, top=0.84)
locations = [6.0, 5.0, 3.8, 2.8, 0.6, -0.4]
groups = [("reference", "S1"), ("reference", "S2"),
          ("changed", "S1"), ("changed", "S2"),
          ("reference", "average"), ("changed", "average")]
method_style = {"A": {"color": "#474747", "marker": "o", "face": "white", "offset": 0.11},
                "B": {"color": "#0072B2", "marker": "s", "face": "#0072B2", "offset": -0.11}}
labels, source_rows = [], []
for y, (condition, stratum) in zip(locations, groups):
    cell = {}
    for method, spec in method_style.items():
        if stratum == "average":
            record = values["aggregates"][condition][method]
            loss, n = float(record["loss"]), record["n"]
            lo = hi = None
            ax.plot(loss, y + spec["offset"], marker=spec["marker"],
                    markersize=5, markerfacecolor=spec["face"],
                    markeredgecolor=spec["color"], linestyle="none")
        else:
            record = next(r for r in rows if (r["condition"], r["stratum"], r["method"]) == (condition, stratum, method))
            loss, n = float(record["loss"]), int(record["n"])
            lo, hi = float(record["lo"]), float(record["hi"])
            assert 0 <= lo <= loss <= hi <= 10.5
            ax.errorbar(loss, y + spec["offset"], xerr=[[loss - lo], [hi - loss]],
                        fmt=spec["marker"], color=spec["color"],
                        markerfacecolor=spec["face"], markeredgecolor=spec["color"],
                        markersize=5, capsize=2.5, capthick=0.8, elinewidth=1)
        cell[method] = Decimal(str(record["loss"]))
        source_rows.append({"row_type": "weighted_average" if stratum == "average" else "supplied_summary",
                            "condition": condition, "stratum": stratum, "method": method,
                            "n": n, "loss": record["loss"], "lo": record.get("lo", ""), "hi": record.get("hi", "")})
    delta = cell["B"] - cell["A"]
    ax.text(1.17, y, f"{delta:+.2f}", transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=8.5)
    labels.append(f"{condition.capitalize()} {stratum if stratum != 'average' else 'average'}\nn = {n} per method")

ax.set_yticks(locations, labels)
ax.tick_params(axis="y", length=0, pad=9)
ax.set_ylim(-1.15, 6.55)
ax.set_xlim(0, 10.5)
ax.set_xticks([0, 2, 4, 6, 8, 10])
ax.set_xlabel("Benchmark loss (supplied scale)", labelpad=8)
ax.grid(axis="x", color="#E4E4E4", linewidth=0.6)
ax.set_axisbelow(True)
ax.spines["left"].set_visible(False)
ax.axhline(1.65, color="#BEBEBE", linewidth=0.7)
ax.text(1.17, 6.65, "B − A", transform=ax.get_yaxis_transform(), ha="right", va="bottom", fontsize=8.5)
fig.text(0.025, 0.967, "A conditional reference-average gain", fontsize=10, weight="bold", va="top")
handles = [Line2D([], [], marker=s["marker"], markerfacecolor=s["face"], markeredgecolor=s["color"],
                  color=s["color"], linestyle="none", markersize=5, label=f"Method {m}") for m, s in method_style.items()]
fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.29, 0.933), ncol=2, frameon=False)
fig.text(0.025, 0.078, "Manufactured summaries. Whiskers: supplied 95% row intervals.", fontsize=8)
fig.text(0.025, 0.038, "Weighted averages: no uncertainty estimate. Lower loss is better.", fontsize=8)
issues = audit_layout(fig)
render_preview(fig, str(OUT / "process/figure1.preview.png"), dpi=180)
with (OUT / "figure1_source_data.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(source_rows[0]))
    writer.writeheader()
    writer.writerows(source_rows)
audit = {"style": style, "dimensions_inches": [6.3, 4.7], "layout_issues": issues,
         "source_summary_rows": 8, "aggregate_points": 4, "aggregate_intervals": 0,
         "minimum_font_pt": 8, "scope": "Single data axis; final scientific display made with SciPilot, not Nature Figure."}
(OUT / "process/figure-layout-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n")
assert not issues, issues
if args.export:
    paths = export_figure(fig, str(OUT / "figure1"), formats=["pdf", "svg", "png"],
                          dpi=300, size_inches=(6.3, 4.7), tight=False, grayscale_preview=False)
    # Preserve the exact-size PNG; the upstream grayscale helper would overwrite it with a tight crop.
    Image.open(OUT / "figure1.png").convert("L").save(OUT / "process/figure1.grayscale.png", dpi=(300, 300))
    compliance = {}
    for path in paths:
        findings, info = check_figure(path, min_dpi=300, target_inches=(6.3, 4.7))
        compliance[Path(path).name] = {"findings": findings, "info": info}
        assert not any(severity == "FAIL" for severity, _ in findings), findings
    (OUT / "process/figure-file-audit.json").write_text(json.dumps(compliance, ensure_ascii=False, indent=2) + "\n")
plt.close(fig)
print(json.dumps({"layout_issues": issues, "exported": bool(args.export), "source_summary_rows": 8}))
