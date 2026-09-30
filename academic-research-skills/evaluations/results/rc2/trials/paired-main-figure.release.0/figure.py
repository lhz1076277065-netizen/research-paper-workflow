#!/usr/bin/env python3
"""Frozen synthetic fixture: paired contrasts and target-weight sensitivity.

Run: python -B figure.py [--preview-only]
Requires matplotlib and Pillow. Bundled SciPilot helpers are MIT licensed.
Chart design adapts SciPilot chart_selection and plot_recipes sections 6/9.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import os
import sys
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(BASE / ".mplconfig"))
sys.dont_write_bytecode = True
sys.path.insert(0, str(BASE / "scipilot"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from setup_style import setup_style
from layout_tools import add_panel_labels
from visual_qa import render_preview, audit_layout
from export_figure import export_figure
from check_figure import check_figure

WIDTH_MM, HEIGHT_MM = 180, 104
SIZE = WIDTH_MM / 25.4, HEIGHT_MM / 25.4
COLORS = {"C1": "#0072B2", "C2": "#D55E00"}  # Okabe–Ito + redundant shape
MARKERS = {"C1": "o", "C2": "s"}
INPUT_SHA256 = "e2d5923ff6b2d1a95321ece8956a892ad4416d051c8c763c9ea31881a306374c"


def signed(x, digits=1):
    return f"{x:+.{digits}f}".replace("-", "−")


def load_data():
    path = BASE / "figure-results.csv"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == INPUT_SHA256, "Fixture changed"
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    assert len(rows) == 6
    data = {}
    for row in rows:
        key = row["condition"], row["group"]
        assert key not in data
        numeric = {k: float(v) for k, v in row.items() if k not in ("condition", "group")}
        assert all(math.isfinite(x) for x in numeric.values())
        assert numeric["n_clusters"] > 0 and numeric["n_clusters"].is_integer()
        assert 0 <= numeric["target_weight"] <= 1
        assert math.isclose(numeric["loss_A"] - numeric["loss_B"],
                            numeric["difference_A_minus_B"], abs_tol=1e-12)
        for point, lower, upper in [("loss_A", "A_low", "A_high"),
                                    ("loss_B", "B_low", "B_high"),
                                    ("difference_A_minus_B", "diff_low", "diff_high")]:
            assert numeric[lower] <= numeric[point] <= numeric[upper]
        data[key] = numeric
    assert set(data) == {(c, g) for c in ("C1", "C2") for g in ("G1", "G2", "G3")}
    for condition in ("C1", "C2"):
        assert math.isclose(sum(data[condition, g]["target_weight"]
                                for g in ("G1", "G2", "G3")), 1)
    return data


def weighted(data, condition, weight_condition):
    return sum(data[weight_condition, g]["target_weight"] *
               data[condition, g]["difference_A_minus_B"]
               for g in ("G1", "G2", "G3"))


def make_figure(data, summary):
    setup_style(journal="general", lang="en", use_sciplots=False, constrained_layout=False)
    plt.rcParams.update({"font.sans-serif": ["DejaVu Sans"], "font.size": 7.8,
                         "axes.labelsize": 8, "xtick.labelsize": 7.5,
                         "savefig.bbox": None})
    fig = plt.figure(figsize=SIZE, dpi=150)
    grid_a = fig.add_gridspec(1, 1, left=.36, right=.735, bottom=.405, top=.77)
    grid_b = fig.add_gridspec(1, 1, left=.36, right=.735, bottom=.12, top=.26)
    ax_a, ax_b = fig.add_subplot(grid_a[0]), fig.add_subplot(grid_b[0])
    for ax in (ax_a, ax_b):
        ax.set_xlim(-3.1, 3.3)
        ax.set_yticks([])
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.axvline(0, color=".45", linewidth=.7, linestyle=(0, (3, 3)), zorder=0)
    ax_a.set_ylim(0, 5.8)
    ax_a.set_xticks([])
    ax_a.spines["bottom"].set_visible(False)
    ax_b.set_ylim(0, 3)
    ax_b.set_xticks(range(-3, 4))
    ax_b.tick_params(axis="x", length=2.5, pad=3)

    fig.text(.025, .959, "Target-weighted loss difference reverses between conditions",
             fontsize=9.6, weight="bold", va="top")
    fig.text(.025, .913, "Synthetic fixtures · Lower loss is better · Negative A−B favors A; positive favors B",
             fontsize=7.7, va="top")

    def row_text(ax, x, y, text, **kw):
        pos = ax.get_position()
        y0, y1 = ax.get_ylim()
        fy = pos.y0 + (y - y0) / (y1 - y0) * pos.height
        return fig.text(x, fy, text, va="center", **kw)

    # The same physical offsets align a/b; the plotting region is fixed-size.
    xoffset = (.025 - .36) * SIZE[0] * 72
    add_panel_labels(fig, axes=[ax_a, ax_b], style="nature", fontsize=9,
                     x_offset_pt=xoffset, y_offset_pt=20, ha="left")
    for ax, title in [(ax_a, "Group contrasts with paired uncertainty"),
                      (ax_b, "Target-weighted means: point estimates only")]:
        pos = ax.get_position()
        fig.text(.058, pos.y1 + 20 / (SIZE[1] * 72), title,
                 fontsize=8.5, weight="bold", va="bottom")

    hy = ax_a.get_position().y1 + .02
    for x, label, align in [(.025, "Group", "left"), (.127, "Cond.", "left"),
                             (.225, "Clusters", "center"), (.307, "Target %", "center"),
                             (.36, "A−B (loss points)", "left"),
                             (.765, "Difference [95% interval]", "left")]:
        fig.text(x, hy, label, fontsize=7.2, weight="bold", ha=align, va="bottom")

    for group, ys in zip(("G1", "G2", "G3"), [(5.3, 4.5), (3.3, 2.5), (1.3, .5)]):
        row_text(ax_a, .025, sum(ys) / 2, group, fontsize=8, weight="bold")
        for condition, y in zip(("C1", "C2"), ys):
            row = data[condition, group]
            point, lo, hi = (row[k] for k in ("difference_A_minus_B", "diff_low", "diff_high"))
            ax_a.errorbar(point, y, xerr=[[point - lo], [hi - point]],
                          fmt=MARKERS[condition], color=COLORS[condition],
                          ecolor=COLORS[condition], elinewidth=1, capsize=2.2,
                          capthick=.8, markersize=4.3, markeredgewidth=.7)
            row_text(ax_a, .127, y, condition, color=COLORS[condition])
            row_text(ax_a, .225, y, str(int(row["n_clusters"])), ha="center")
            row_text(ax_a, .307, y, f'{row["target_weight"]:.0%}', ha="center")
            row_text(ax_a, .765, y, f"{signed(point)} [{signed(lo)}, {signed(hi)}]", fontsize=7.5)
    fig.text(.025, .383, "Intervals concern paired A−B within each group: 95% percentile cluster bootstrap.",
             fontsize=7.2, va="bottom")

    fig.text(.765, ax_b.get_position().y1 + .02, "Difference", fontsize=7.2,
             weight="bold", va="bottom")
    means = [("C1", 2.5, "C1 · C1 weights (50/20/30%)", summary["C1_target"], False),
             ("C2", 1.5, "C2 · fixed C1 weights (50/20/30%)", summary["C2_at_C1_weights"], True),
             ("C2", .5, "C2 · C2 weights (20/50/30%)", summary["C2_target"], False)]
    for condition, y, label, point, hollow in means:
        ax_b.plot(point, y, marker=MARKERS[condition], markersize=5,
                  linestyle="none", color=COLORS[condition],
                  markerfacecolor="white" if hollow else COLORS[condition], markeredgewidth=1)
        row_text(ax_b, .025, y, label, fontsize=7.7)
        row_text(ax_b, .765, y, signed(point, 2), fontsize=8, weight="bold")

    fig.text(.025, .020,
             "Fixed C1 weights retain 53% of the C1→C2 change (−0.80 of −1.52); descriptive sensitivity, no interval.",
             fontsize=7.1, va="bottom")
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview-only", action="store_true")
    args = parser.parse_args()
    data = load_data()
    summary = {"C1_target": weighted(data, "C1", "C1"),
               "C2_target": weighted(data, "C2", "C2"),
               "C2_at_C1_weights": weighted(data, "C2", "C1")}
    summary["total_change"] = summary["C2_target"] - summary["C1_target"]
    summary["fixed_weight_change"] = summary["C2_at_C1_weights"] - summary["C1_target"]
    summary["retained_fraction"] = summary["fixed_weight_change"] / summary["total_change"]
    # One fixture self-check: catches direction, wrong weights, and arithmetic regressions.
    for key, expected in {"C1_target": .68, "C2_target": -.84,
                           "C2_at_C1_weights": -.12, "total_change": -1.52,
                           "fixed_weight_change": -.80, "retained_fraction": 10 / 19}.items():
        assert math.isclose(summary[key], expected, abs_tol=1e-12), (key, summary[key])
    fig = make_figure(data, summary)
    qa_dir = BASE / "qa"
    qa_dir.mkdir(exist_ok=True)
    render_preview(fig, str(qa_dir / "upstream-preview.png"), dpi=150)
    fig.savefig(BASE / "preview.png", dpi=96, bbox_inches=None)
    issues = audit_layout(fig)
    assert not issues, issues
    # The upstream audit does not compare figure footnotes against tick labels.
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    footer_top = fig.texts[-1].get_window_extent(renderer).y1
    footer_gap = min(t.get_window_extent(renderer).y0 - footer_top
                     for t in fig.axes[1].get_xticklabels() if t.get_visible())
    assert footer_gap >= 0, "Footer overlaps bottom tick labels"
    report = {"synthetic_fixture": True, "summary": summary, "layout_issues": issues,
              "size_mm": [WIDTH_MM, HEIGHT_MM], "minimum_font_pt": 7.1,
              "target_preview_dpi": 96, "profile_note": "Six summary rows, not six observed clusters.",
              "footer_to_ticks_separation_pt": footer_gap * 72 / fig.dpi,
              "aggregate_intervals": "unavailable; no reconstruction from marginal endpoints"}
    if not args.preview_only:
        # tight=False preserves the requested 180 × 104 mm canvas.
        export_figure(fig, str(BASE / "figure"), formats=["svg", "png"], dpi=300,
                      size_inches=SIZE, tight=False, grayscale_preview=False)
        image = Image.open(BASE / "figure.png")
        image.convert("L").save(BASE / "figure_grayscale.png", dpi=(300, 300))
        image_preview = Image.open(BASE / "preview.png")
        image_preview.convert("L").save(BASE / "preview_grayscale.png", dpi=(96, 96))
        svg = ET.parse(BASE / "figure.svg").getroot()
        svg_mm = [float(svg.attrib[key].removesuffix("pt")) / 72 * 25.4 for key in ("width", "height")]
        assert all(math.isclose(a, b, abs_tol=1e-5) for a, b in zip(svg_mm, [WIDTH_MM, HEIGHT_MM]))
        assert not svg.findall(".//{http://www.w3.org/2000/svg}image"), "Unexpected raster content"
        assert svg.findall(".//{http://www.w3.org/2000/svg}text"), "SVG text must remain editable"
        checks = {}
        for filename in ("figure.svg", "figure.png"):
            file_issues, info = check_figure(str(BASE / filename), min_dpi=300, target_inches=SIZE)
            assert not file_issues, file_issues
            checks[filename] = {"issues": file_issues, "info": info}
        report.update({"output_checks": checks, "svg_size_mm": svg_mm,
                       "png_pixels": image.size, "preview_pixels": image_preview.size})
    (qa_dir / "checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"self_check": "passed", "layout_issues": issues,
                      "summary": summary, "stage": "preview" if args.preview_only else "final"}))
    plt.close(fig)


if __name__ == "__main__":
    main()
