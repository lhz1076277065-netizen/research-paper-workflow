"""Frozen synthetic fixture; no new observations or inferred aggregate intervals.

Run: python figure.py [--export]
Without --export, make a preview and run numerical/layout checks. After visually
reviewing that preview, --export writes the exact-size SVG and PNG.
Professional helper location can be overridden with SCIPILOT_SCRIPTS.
"""
from pathlib import Path
import argparse
import csv
import io
import json
import math
import os
import sys

OUT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(OUT / ".mplconfig"))
sys.dont_write_bytecode = True
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image

PROFESSIONAL = Path(os.environ.get("SCIPILOT_SCRIPTS", str(
    OUT.parents[1] / "professional/Haojae/scipilot-figure-skill/scripts")))
sys.path.insert(0, str(PROFESSIONAL))
from setup_style import setup_style
from export_figure import export_figure
from visual_qa import audit_layout
from profile_data import profile_data
from check_figure import check_figure

CSV = """condition,group,n_clusters,target_weight,loss_A,loss_B,A_low,A_high,B_low,B_high,difference_A_minus_B,diff_low,diff_high
C1,G1,16,0.5,10,8,8,12,6,10,2,1,3
C1,G2,4,0.2,6,7,4,8,5,9,-1,-1.8,-0.2
C1,G3,10,0.3,4,4.4,3,5,3.4,5.4,-0.4,-0.7,-0.1
C2,G1,6,0.2,9,8.4,7,11,6.4,10.4,0.6,0.1,1.1
C2,G2,15,0.5,7,8.8,5,9,6.8,10.8,-1.8,-2.5,-1.1
C2,G3,9,0.3,4.8,5,3.8,5.8,4,6,-0.2,-0.6,0.2
"""
BLUE, ORANGE, GRAY = "#0072B2", "#D55E00", "#555555"
SIZE = (180 / 25.4, 100 / 25.4)


def main(export=False):
    (OUT / "figure-results.csv").write_text(CSV)
    rows = list(csv.DictReader(io.StringIO(CSV)))
    for row in rows:
        for key in list(row)[2:]:
            row[key] = float(row[key])
        assert row["n_clusters"] > 0 and row["n_clusters"].is_integer()
        assert 0 <= row["target_weight"] <= 1
        assert all(math.isfinite(v) for v in list(row.values())[2:])
        assert math.isclose(row["loss_A"] - row["loss_B"], row["difference_A_minus_B"], abs_tol=1e-12)
        for prefix, middle in [("A", "loss_A"), ("B", "loss_B"), ("diff", "difference_A_minus_B")]:
            assert row[prefix + "_low"] <= row[middle] <= row[prefix + "_high"]
    by = {(r["condition"], r["group"]): r for r in rows}
    assert len(by) == 6 and set(by) == {(c, g) for c in ("C1", "C2") for g in ("G1", "G2", "G3")}
    weights = {c: [by[c, g]["target_weight"] for g in ("G1", "G2", "G3")] for c in ("C1", "C2")}
    assert all(math.isclose(sum(w), 1) for w in weights.values())

    def weighted(condition, weight_condition, column):
        return sum(w * by[condition, g][column] for w, g in zip(weights[weight_condition], ("G1", "G2", "G3")))

    averages = [(c, wc, weighted(c, wc, "loss_A"), weighted(c, wc, "loss_B"), weighted(c, wc, "difference_A_minus_B"))
                for c, wc in [("C1", "C1"), ("C2", "C2"), ("C2", "C1")]]
    c1, c2, fixed = [v[-1] for v in averages]
    total, retained, reweight = c2 - c1, fixed - c1, c2 - fixed
    assert all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip((c1, c2, fixed, total, retained, reweight), (.68, -.84, -.12, -1.52, -.80, -.72)))
    assert math.isclose(total, retained + reweight)
    assert c1 > 0 > c2 and fixed < 0
    assert by["C2", "G3"]["diff_low"] < 0 < by["C2", "G3"]["diff_high"]

    # Profile the six supplied summaries only; its row counts are not cluster n.
    profile = profile_data(str(OUT / "figure-results.csv"), group_cols=["condition", "group"])
    (OUT / "aggregate-profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2, default=lambda v: v.item()))
    style = setup_style(journal="nature", lang="en", use_sciplots=False, constrained_layout=False)
    plt.rcParams.update({"font.sans-serif": ["DejaVu Sans"], "font.size": 7.5,
                         "axes.labelsize": 7.5, "xtick.labelsize": 7, "ytick.labelsize": 7.5})
    fig = plt.figure(figsize=SIZE, dpi=150)
    fig.text(.045, .954, "Target-weighted advantage reverses between conditions", fontsize=10, weight="bold", va="top")
    fig.text(.045, .905, "Synthetic development fixture  |  Lower loss is better", fontsize=7.5, color=GRAY)
    fig.text(.045, .837, "a", fontsize=9, weight="bold")
    fig.text(.071, .837, "Paired group differences", fontsize=8.5, weight="bold")
    fig.text(.55, .837, "b", fontsize=9, weight="bold")
    fig.text(.576, .837, "Target-weighted means", fontsize=8.5, weight="bold")

    fig.legend(handles=[Line2D([], [], marker="o", color=BLUE, linestyle="none", label="C1"),
                        Line2D([], [], marker="s", color=ORANGE, linestyle="none", label="C2")],
               loc="center left", bbox_to_anchor=(.071, .785), frameon=False, ncol=2,
               fontsize=7, handletextpad=.4, columnspacing=1.5)
    ax = fig.add_axes([.085, .295, .31, .455])
    ax.axvline(0, color="#888888", lw=.8, ls="--", zorder=0)
    ax.set(xlim=(-2.8, 3.25), ylim=(-.6, 5.6), xticks=[-2, -1, 0, 1, 2, 3], yticks=[4.5, 2.5, .5], yticklabels=["G1", "G2", "G3"])
    ax.tick_params(axis="y", length=0, pad=8)
    ax.spines["left"].set_visible(False)
    for i, group in enumerate(("G1", "G2", "G3")):
        for condition, y, color, marker in [("C1", 5 - 2*i, BLUE, "o"), ("C2", 4 - 2*i, ORANGE, "s")]:
            r = by[condition, group]
            d = r["difference_A_minus_B"]
            ax.errorbar(d, y, xerr=[[d-r["diff_low"]], [r["diff_high"]-d]],
                        color=color, fmt=marker, ms=4.7, capsize=2.3, elinewidth=1.2, markeredgewidth=.7)
            ax.text(1.10, y, f'{r["n_clusters"]:.0f}', transform=ax.get_yaxis_transform(), ha="center", va="center", fontsize=7)
            ax.text(1.27, y, f'{r["target_weight"]:.0%}', transform=ax.get_yaxis_transform(), ha="center", va="center", fontsize=7)
    ax.text(1.10, 5.85, "n", transform=ax.get_yaxis_transform(), ha="center", fontsize=7, style="italic")
    ax.text(1.27, 5.85, "weight", transform=ax.get_yaxis_transform(), ha="center", fontsize=7)
    ax.text(.04, -.15, "A lower loss", transform=ax.transAxes, fontsize=7, ha="left")
    ax.text(.97, -.15, "B lower loss", transform=ax.transAxes, fontsize=7, ha="right")
    ax.set_xlabel("A − B (loss points)", labelpad=6)
    fig.text(.071, .156, "Whiskers: supplied paired 95% cluster-bootstrap CIs", fontsize=6.8)
    fig.text(.071, .087, "C1: G2/G3 oppose the B-favoring mean.\nC2: G1 opposes the A-favoring mean.", fontsize=7, linespacing=1.4)

    fig.text(.576, .787, "Point estimates only; no recoverable mean CIs", fontsize=7, color=GRAY)
    axb = fig.add_axes([.765, .425, .20, .315])
    axb.axvline(0, color="#888888", lw=.8, ls="--")
    axb.set(xlim=(-1.08, 1.08), ylim=(-.55, 2.65), xticks=[-1, 0, 1], yticks=[])
    axb.spines["left"].set_visible(False)
    for y, (condition, wc, a, b, d), color, marker, face in zip([2, 1, 0], averages,
            [BLUE, ORANGE, ORANGE], ["o", "s", "s"], [BLUE, ORANGE, "white"]):
        axb.plot(d, y, marker=marker, color=color, markerfacecolor=face, ms=5.4, markeredgewidth=1.2, linestyle="none")
        axb.annotate(f"{d:+.2f}".replace("-", "−"), (d, y), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=7.5, color=color)
        axb.text(-1.02, y+.03, f"{condition} · {wc} weights", transform=axb.get_yaxis_transform(), va="center", fontsize=7.4)
        axb.text(-1.02, y-.24, f"A {a:.2f} · B {b:.2f}", transform=axb.get_yaxis_transform(), va="center", fontsize=6.6, color=GRAY)
    axb.set_xlabel("A − B (loss points)", labelpad=3)

    fig.text(.55, .310, "c", fontsize=9, weight="bold")
    fig.text(.576, .310, "C1 → C2 change: −1.52 loss points", fontsize=8, weight="bold")
    fig.text(.576, .267, "Fixed C1 weights retain −0.80 (52.6%)", fontsize=7.5)
    axc = fig.add_axes([.576, .209, .389, .036])
    axc.barh([0], [.80], height=.7, color="#777777")
    axc.barh([0], [.72], left=[.80], height=.7, color="#D6D6D6", edgecolor="#777777", hatch="///", linewidth=.6)
    axc.set(xlim=(0, 1.52), ylim=(-.5, .5))
    axc.axis("off")
    fig.text(.576, .170, "Additional target-weight change: −0.72 (47.4%)", fontsize=7)
    fig.text(.576, .103, "Descriptive, C1-reference decomposition.\nNo causal or equivalence conclusion.", fontsize=7, color=GRAY, linespacing=1.4)
    fig.text(.045, .034, "n = independent clusters; weights are prescribed targets. C2/G3 CI includes zero.", fontsize=6.8, color=GRAY)

    issues = audit_layout(fig)
    fig.canvas.draw()
    assert not issues, f"Professional layout audit found: {issues}"
    assert min(t.get_fontsize() for t in fig.findobj(matplotlib.text.Text) if t.get_visible() and t.get_text()) >= 6.6
    # Native savefig preserves the requested canvas; upstream preview crops it.
    fig.savefig(OUT / "preview.png", dpi=150, bbox_inches=None)
    Image.open(OUT / "preview.png").convert("L").save(OUT / "preview-grayscale.png", dpi=(150, 150))
    report = {"synthetic": True, "size_mm": [180, 100], "professional_style": style,
              "numerical_checks": "PASS", "layout_audit": issues,
              "means": [{"condition": c, "weight_condition": w, "loss_A": a, "loss_B": b, "A_minus_B": d} for c,w,a,b,d in averages],
              "total_change": total, "fixed_weight_change": retained, "additional_reweighting": reweight,
              "retained_fraction": retained/total, "aggregate_CI": "not identifiable from supplied summaries"}
    if export:
        # tight=False fixes canvas size. Disable upstream grayscale option because
        # its helper overwrites the main PNG using bbox_inches='tight'.
        export_figure(fig, str(OUT / "figure"), formats=["svg", "png"], size_inches=SIZE,
                      dpi=300, tight=False, grayscale_preview=False)
        for filename in ("figure.svg", "figure.png"):
            failures, info = check_figure(str(OUT / filename), target_inches=SIZE)
            assert not failures, failures
            report[filename] = info
        import xml.etree.ElementTree as ET
        svg = ET.parse(OUT / "figure.svg").getroot()
        assert abs(float(svg.attrib["width"][:-2])*25.4/72 - 180) < 1e-6
        assert abs(float(svg.attrib["height"][:-2])*25.4/72 - 100) < 1e-6
        assert not svg.findall(".//{http://www.w3.org/2000/svg}image")
        with Image.open(OUT / "figure.png") as im:
            assert im.size == (2125, 1181), im.size
        Image.open(OUT / "figure.png").convert("L").save(OUT / "figure-grayscale.png", dpi=(300, 300))
    (OUT / "checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({"numerical_checks": report["numerical_checks"], "layout_audit": issues, "exported": export}))
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true")
    main(parser.parse_args().export)
