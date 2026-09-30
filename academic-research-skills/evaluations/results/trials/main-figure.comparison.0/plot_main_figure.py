"""Frozen synthetic main figure. Run once for preview; --export after visual review.

Uses the vendored, pinned SciPilot implementation (MIT; see sources/scipilot).
No raw observations, tests, causal model, or aggregate intervals are inferred.
"""
from pathlib import Path
import argparse
import csv
from decimal import Decimal
import hashlib
import json
import os
import sys

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "sources/scipilot/scripts"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image
import pandas as pd
from profile_data import profile_data
from setup_style import setup_style
from layout_tools import finalize_figure, add_panel_labels
from visual_qa import audit_layout
from export_figure import export_figure

SIZE = (7.2, 4.5)
STYLE = {"A": ("#0072B2", "o", 0.14), "B": ("#D55E00", "s", -0.14)}
CONDITIONS = ("reference", "changed")
STRATA = ("S1", "S2")
INPUT_HASH = "a3b1fcc3f32705955e861c529c915845b5ceac0b84f50037fd9f5dcaf1764884"


def main(export=False):
    data_path = ROOT / "inputs/fixed-results.csv"
    assert hashlib.sha256(data_path.read_bytes()).hexdigest() == INPUT_HASH
    with data_path.open() as stream:
        raw = list(csv.DictReader(line for line in stream if not line.startswith("#")))
    assert len(raw) == 8
    rows = {}
    for row in raw:
        key = (row["condition"], row["stratum"], row["method"])
        assert key not in rows
        row = dict(row, n=int(row["n"]))
        row.update({field: Decimal(row[field]) for field in ("loss", "lo", "hi")})
        assert row["n"] > 0 and all(row[field].is_finite() for field in ("loss", "lo", "hi"))
        assert row["lo"] <= row["loss"] <= row["hi"]
        rows[key] = row
    assert set(rows) == {(c, s, m) for c in CONDITIONS for s in STRATA for m in STYLE}

    totals = {}
    differences = {}
    for condition in CONDITIONS:
        for stratum in STRATA:
            a, b = (rows[(condition, stratum, method)] for method in STYLE)
            assert a["n"] == b["n"]
            differences[(condition, stratum)] = b["loss"] - a["loss"]
        for method in STYLE:
            group = [rows[(condition, stratum, method)] for stratum in STRATA]
            totals[(condition, method)] = sum(row["n"] * row["loss"] for row in group) / sum(row["n"] for row in group)
    # One runnable check covers the substantive reversal and all four mixtures.
    assert totals == {("reference", "A"): Decimal("4.8"), ("reference", "B"): Decimal("4.36"), ("changed", "A"): Decimal("6.6"), ("changed", "B"): Decimal("7.52")}
    assert [differences[key] for key in [("reference", "S1"), ("reference", "S2"), ("changed", "S1"), ("changed", "S2")]] == [Decimal("-0.8"), Decimal("1.0"), Decimal("-0.2"), Decimal("1.2")]

    frame = pd.read_csv(data_path, comment="#")
    profile = profile_data(frame, group_cols=["condition", "stratum", "method"])
    profile["interpretation"] = "Eight supplied summary rows, not eight independent samples. Profiler group counts/correlations are not inferential evidence; supplied n defines weights."
    (ROOT / "data-profile.json").write_text(json.dumps(profile, indent=2, ensure_ascii=False, default=lambda value: value.item()) + "\n")

    style_info = setup_style(journal="general", lang="en", use_sciplots=False)
    plt.rcParams.update({"font.sans-serif": ["DejaVu Sans"], "font.size": 9, "axes.labelsize": 9, "axes.titlesize": 10, "xtick.labelsize": 8, "ytick.labelsize": 8, "legend.fontsize": 9})
    fig, axes = plt.subplots(1, 2, figsize=SIZE, gridspec_kw={"width_ratios": [1.08, 1]})
    fig.suptitle("Synthetic comparison: aggregate ranking reverses", fontsize=12, fontweight="bold", y=0.97)
    handles = [Line2D([], [], color=color, marker=marker, linestyle="none", markersize=5, label=f"Method {method}") for method, (color, marker, _) in STYLE.items()]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.915), ncol=2, frameon=False)
    fig.text(0.5, 0.10, "a: Supplied 95% intervals.  b: Weighted points; aggregate intervals not supplied.", ha="center", fontsize=8)
    fig.text(0.5, 0.055, "Lower loss is better. Synthetic results; no significance test or causal identification.", ha="center", fontsize=8)

    drawn_rows = []
    y_positions = [3, 2, 1, 0]
    labels = []
    for y, (condition, stratum) in zip(y_positions, [(c, s) for c in CONDITIONS for s in STRATA]):
        labels.append(f"{condition.title()} / {stratum}\nn = {rows[(condition, stratum, 'A')]['n']} per method")
        for method, (color, marker, offset) in STYLE.items():
            row = rows[(condition, stratum, method)]
            loss, lo, hi = (float(row[field]) for field in ("loss", "lo", "hi"))
            error = axes[0].errorbar(loss, y + offset, xerr=[[loss - lo], [hi - loss]], fmt=marker, color=color, elinewidth=1.1, capsize=2.5, markersize=5)
            segment = error.lines[2][0].get_segments()[0]
            actual = [float(error.lines[0].get_xdata()[0]), float(segment[0, 0]), float(segment[1, 0])]
            assert all(abs(a - b) < 1e-10 for a, b in zip(actual, [loss, lo, hi]))
            drawn_rows.append({"condition": condition, "stratum": stratum, "method": method, "plotted_loss_lo_hi": actual, "n": row["n"]})
            axes[0].annotate(f"{loss:.1f}", (loss, y + offset), xytext=(0, 7 if offset > 0 else -12), textcoords="offset points", ha="center", color=color, fontsize=8)
    axes[0].set_yticks(y_positions, labels)
    axes[0].set_ylim(-0.58, 3.58)
    axes[0].axhline(1.5, color="0.82", linewidth=0.6)
    axes[0].set_title("Stratum-level loss", loc="left", pad=12)

    aggregate_rows = []
    weight_labels = []
    for condition, y in zip(CONDITIONS, [1, 0]):
        counts = [rows[(condition, stratum, "A")]["n"] for stratum in STRATA]
        total_n = sum(counts)
        weight_labels.append(f"{condition.title()}\nS1 {counts[0] / total_n:.0%}, S2 {counts[1] / total_n:.0%}")
        for method, (color, marker, offset) in STYLE.items():
            loss = totals[(condition, method)]
            point, = axes[1].plot(float(loss), y + offset, marker=marker, color=color, linestyle="none", markersize=5)
            assert abs(float(point.get_xdata()[0]) - float(loss)) < 1e-10
            axes[1].annotate(f"{loss:.2f}", (float(loss), y + offset), xytext=(0, 7 if offset > 0 else -12), textcoords="offset points", ha="center", color=color, fontsize=8)
            aggregate_rows.append({"condition": condition, "method": method, "weighted_loss": str(loss), "total_n_per_method": total_n, "S1_weight": str(Decimal(counts[0]) / total_n), "S2_weight": str(Decimal(counts[1]) / total_n), "interval": "not supplied; not estimated"})
    axes[1].set_yticks([1, 0], weight_labels)
    axes[1].set_ylim(-0.58, 1.58)
    axes[1].set_title("Condition-weighted loss", loc="left", pad=12)
    for ax in axes:
        ax.set_xlim(0, 10)
        ax.set_xticks([0, 2, 4, 6, 8, 10])
        ax.set_xlabel("Loss (units unspecified)")
        ax.tick_params(axis="y", length=0, pad=5)
        ax.grid(axis="x", color="0.9", linewidth=0.5)
        ax.set_axisbelow(True)

    finalize_figure(fig)
    fig.get_layout_engine().set(rect=(0.015, 0.18, 0.97, 0.64), wspace=0.09)
    fig.canvas.draw()
    add_panel_labels(fig, axes=axes, x_offset_pt=-9, y_offset_pt=10, fontsize=10)
    issues = audit_layout(fig)
    assert not any(severity == "FAIL" for severity, _ in issues), issues
    report = {"input_sha256": INPUT_HASH, "weighted_formula": "sum(n_stratum * loss_stratum) / sum(n_stratum), within each condition and method", "drawn_source_rows": drawn_rows, "aggregates": aggregate_rows, "stratum_difference_B_minus_A": [{"condition": c, "stratum": s, "difference": str(differences[(c, s)])} for c in CONDITIONS for s in STRATA], "aggregate_difference_B_minus_A": [{"condition": c, "difference": str(totals[(c, "B")] - totals[(c, "A")])} for c in CONDITIONS], "assertions": "PASS: supplied endpoints, all eight point values, all four aggregates, weights and reversal", "layout_issues": issues, "style": style_info, "figure_size_inches": SIZE, "smallest_font_pt": min(t.get_fontsize() for t in fig.findobj(matplotlib.text.Text) if t.get_text().strip())}
    (ROOT / "numeric-review.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    # tight=False preserves the intended canvas size; grayscale is derived from that exact PNG.
    fig.savefig(ROOT / "preview.png", dpi=150, bbox_inches=None)
    with Image.open(ROOT / "preview.png") as img:
        img.convert("L").save(ROOT / "preview_grayscale.png")
    if export:
        export_figure(fig, str(ROOT / "main-figure"), formats=["pdf", "svg", "png"], dpi=300, size_inches=SIZE, tight=False)
        with Image.open(ROOT / "main-figure.png") as img:
            img.convert("L").save(ROOT / "main-figure_grayscale.png", dpi=(300, 300))
    plt.close(fig)
    print(json.dumps({"aggregates": aggregate_rows, "layout_issues": issues, "smallest_font_pt": report["smallest_font_pt"], "exported": export}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", action="store_true")
    main(export=parser.parse_args().export)
