"""Display supplied synthetic aggregates; never generate unit data or bootstrap draws."""
import argparse
import csv
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(OUT / ".mplconfig"))
sys.dont_write_bytecode = True
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

sys.path.insert(0, "LOCAL_EVIDENCE_ROOT/professional/Haojae/scipilot-figure-skill/scripts")
from visual_qa import audit_layout, render_preview

parser = argparse.ArgumentParser()
parser.add_argument("--export", action="store_true", help="Export vectors after visual inspection of the preview")
args = parser.parse_args()
rows = list(csv.DictReader((OUT / "aggregate-results-v2.csv").open()))
values = [float(r["mean_A_minus_B_score"]) for r in rows]
assert values == [-1.0, 3.0, 1.0, -0.2]
assert abs(0.8 * values[0] + 0.2 * values[1] - values[3]) < 1e-12
assert 0.5 * values[0] + 0.5 * values[1] == values[2]
assert [r["quantity"] for r in rows if r["ci_lower"]] == ["target mixture"]
lower, upper = float(rows[3]["ci_lower"]), float(rows[3]["ci_upper"])
assert lower == -0.6 and upper == 0.2 and lower < 0 < upper

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "svg.fonttype": "none", "pdf.fonttype": 42})
fig, ax = plt.subplots(figsize=(7.2, 3.7), layout="constrained")
labels = ["g1 (n = 4)", "g2 (n = 4)", "Equal sampled mix (0.5/0.5; n = 8)", "Target mix (0.8/0.2; n = 8)"]
for i, (value, marker) in enumerate(zip(values, ["o", "s", "^", "D"])):
    y = 3 - i
    color = "#0072B2" if i == 3 else "#333333"
    ax.plot(value, y, marker=marker, color=color, markersize=6, linestyle="none")
    ax.annotate(f"{value:+.2f}".replace("-", "−"), (value, y), xytext=(0, 12), textcoords="offset points", ha="center", fontsize=9)
ax.errorbar(values[3], 0, xerr=[[values[3] - lower], [upper - values[3]]], fmt="none", color="#0072B2", linewidth=1.2, capsize=4)
ax.text(0.47, -0.03, "Supplied 95% interval [−0.60, 0.20]", va="center", fontsize=9)
ax.axvline(0, color="#777777", linewidth=0.9, linestyle="--", zorder=0)
ax.set_yticks([3, 2, 1, 0], labels)
ax.set_xlim(-1.7, 3.9)
ax.set_ylim(-0.48, 3.75)
ax.set_xticks([-1, 0, 1, 2, 3])
ax.set_xlabel("Mean A−B score (lower score is better)", fontsize=10)
ax.set_title("SYNTHETIC — aggregate estimates from memo v2", fontsize=10, pad=12)
ax.tick_params(axis="y", length=0, pad=8)
ax.spines[["top", "right", "left"]].set_visible(False)
issues = audit_layout(fig)
assert not any(severity == "FAIL" for severity, _ in issues), issues
render_preview(fig, str(OUT / "figure-1-preview.png"), dpi=150)
Image.open(OUT / "figure-1-preview.png").convert("L").save(OUT / "figure-1-grayscale.png")
qa = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "matplotlib": matplotlib.__version__, "size_inches": [7.2, 3.7], "min_font_pt": 9, "layout_issues": issues, "interval_source": "supplied memo v2; not recomputed", "raw_data_available": False, "visual_check": "see operation.md"}
(OUT / "figure-qa.json").write_text(json.dumps(qa, indent=2) + "\n")
if args.export:
    fig.savefig(OUT / "figure-1.svg", metadata={"Date": None, "Creator": "Synthetic aggregate display"})
    fig.savefig(OUT / "figure-1.pdf", metadata={"Author": "", "Creator": "Synthetic aggregate display", "CreationDate": None, "ModDate": None})
    fig.savefig(OUT / "figure-1.png", dpi=300)
plt.close(fig)
print(json.dumps({"preview": "figure-1-preview.png", "layout_issues": issues, "vectors_exported": args.export}))
