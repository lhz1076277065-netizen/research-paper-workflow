"""SYNTHETIC main figure, with an adapted-in-host SciPilot workflow."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
os.environ["MPLCONFIGDIR"] = str(ROOT / ".mplconfig")
sys.dont_write_bytecode = True
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

PROFESSIONAL = ROOT.parents[2] / "professional/Haojae/scipilot-figure-skill"
COMMIT = "43098ddb9e6a6d142218540c114f9ed38922fc42"
SIZE = (180 / 25.4, 100 / 25.4)


def module(name):
    path = PROFESSIONAL / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def log_call(implementation, function, started, inputs, outputs, scope):
    source = PROFESSIONAL / "scripts" / f"{implementation}.py"
    record = {"at_utc": datetime.now(timezone.utc).isoformat(),
              "repository": "Haojae/scipilot-figure-skill", "commit": COMMIT,
              "implementation": str(source), "implementation_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "function": function, "execution_mode": "adapted_in_host",
              "duration_seconds": time.perf_counter() - started,
              "inputs": inputs, "outputs": outputs, "scope": scope}
    with (ROOT / "professional_calls.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def main(export=False):
    results = json.loads((ROOT / "results.json").read_text())
    paired = pd.read_csv(ROOT / "derived/paired_units.csv")
    # pandas 3 uses StringDtype; explicit scientific roles avoid upstream unknown-type inference.
    paired["stratum"] = paired["stratum"].astype("category")
    paired["unit_id"] = paired["unit_id"].astype(object)
    profiler = module("profile_data")
    start = time.perf_counter()
    profile = profiler.profile_data(paired, group_cols=["stratum"])
    (ROOT / "profile.json").write_text(json.dumps(profile, indent=2, default=str) + "\n")
    (ROOT / "profile_report.md").write_text("# SYNTHETIC figure data profile\n\n" + profiler.render_report(profile))
    log_call("profile_data", "profile_data + render_report", start,
             ["derived/paired_units.csv"], ["profile.json", "profile_report.md"],
             "Actual eight-unit main-figure data; categorical stratum and identifier roles adapted explicitly")
    styler = module("setup_style")
    start = time.perf_counter()
    style = styler.setup_style(journal="general", lang="en", use_sciplots=False, constrained_layout=False)
    plt.rcParams.update({"font.sans-serif": ["DejaVu Sans"], "font.size": 8.5,
                         "axes.labelsize": 8.5, "axes.titlesize": 9,
                         "xtick.labelsize": 8, "ytick.labelsize": 8.5,
                         "svg.hashsalt": "synthetic-paired-composition"})
    log_call("setup_style", "setup_style", start, [style], ["main figure typography"],
             "Generic style adapted to user-specified 180 by 100 mm dimensions; no journal certification")
    fig = plt.figure(figsize=SIZE, dpi=150)
    fig.text(0.035, 0.965, "SYNTHETIC — Composition changes the descriptive ranking",
             ha="left", va="top", fontsize=11, weight="bold")
    fig.text(0.035, 0.85, "a", fontsize=10, weight="bold")
    fig.text(0.095, 0.85, "Target versus observed composition", fontsize=9, weight="bold")
    composition = fig.add_axes([0.28, 0.70, 0.57, 0.11])
    for y, proportions in [(1, [80, 20]), (0, [50, 50])]:
        composition.barh(y, proportions[0], height=0.62, color="#0072B2", linewidth=0.5, edgecolor="black")
        composition.barh(y, proportions[1], left=proportions[0], height=0.62,
                         color="#E69F00", linewidth=0.5, edgecolor="black", hatch="///")
        composition.text(proportions[0] / 2, y, f"Stratum 1: {proportions[0]}%",
                         ha="center", va="center", color="white", fontsize=8)
        composition.text(proportions[0] + proportions[1] / 2, y,
                         f"{proportions[1]}%" if proportions[1] == 20 else "Stratum 2: 50%",
                         ha="center", va="center", fontsize=8,
                         bbox={"facecolor": "#E69F00", "edgecolor": "none", "pad": 0.5})
    composition.set_xlim(0, 100)
    composition.set_ylim(-0.5, 1.5)
    composition.set_yticks([1, 0], ["Stipulated target", "Observed units (n=8)"])
    composition.set_xticks([])
    composition.tick_params(axis="y", length=0, pad=9)
    for spine in composition.spines.values():
        spine.set_visible(False)
    fig.text(0.86, 0.756, "Hatched:\nstratum 2", fontsize=7.5, va="center")
    fig.text(0.035, 0.61, "b", fontsize=10, weight="bold")
    fig.text(0.095, 0.61, "Paired differences and composition-weighted contrasts", fontsize=9, weight="bold")
    ax = fig.add_axes([0.28, 0.20, 0.42, 0.35])
    ypos = {"g1": 3, "g2": 2, "target": 1, "sampled": 0}
    colors = {"g1": "#0072B2", "g2": "#E69F00", "target": "black", "sampled": "#666666"}
    raw_offsets = np.array([0.12, 0.19, 0.26, 0.33])
    for g, marker in [("g1", "o"), ("g2", "s")]:
        values = results["strata"][g]["paired_unit_differences"]
        ax.scatter(values, ypos[g] + raw_offsets, s=19, marker=marker,
                   facecolors="white", edgecolors=colors[g], linewidths=0.8, zorder=4)
    displayed = []
    for name, marker in [("g1", "o"), ("g2", "s"), ("target", "D"), ("sampled", "D")]:
        item = results["strata"][name] if name in {"g1", "g2"} else results[
            "primary_target" if name == "target" else "sample_composition_comparator"]
        estimate = item["mean_difference_A_minus_B"] if name in {"g1", "g2"} else item["difference_A_minus_B"]
        lo, hi = item["bootstrap_percentile_interval_95"]
        y = ypos[name]
        ax.errorbar(estimate, y, xerr=[[estimate - lo], [hi - estimate]], fmt=marker,
                    color=colors[name], ecolor=colors[name], elinewidth=1.2,
                    markersize=4.5, capsize=3, capthick=0.8, zorder=5)
        displayed.append({"row": name, "estimate": estimate, "interval": [lo, hi]})
        # Same output values as the graphical marks; the table avoids endpoint guessing.
        ax.text(1.065, y, f"{estimate:+.2f} [{lo:+.2f}, {hi:+.2f}]",
                transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=8.3)
    ax.set_xlim(-2, 6.5)
    ax.set_ylim(-0.5, 3.65)
    ax.set_xticks([-2, 0, 2, 4, 6])
    ax.set_yticks([3, 2, 1, 0], ["Stratum 1 (n=4)", "Stratum 2 (n=4)",
                                "Target 80/20 (n=8)", "Sampled 50/50 (n=8)"])
    ax.tick_params(axis="y", length=0, pad=9)
    ax.axvline(0, color="#999999", linestyle="--", linewidth=0.85, zorder=1)
    ax.axhline(1.5, color="#CCCCCC", linewidth=0.6, zorder=1)
    ax.spines["left"].set_visible(False)
    ax.text(1.065, 3.66, "Mean [conditional 95% interval]",
            transform=ax.get_yaxis_transform(), fontsize=7.6, ha="left", va="bottom")
    fig.text(0.28, 0.565, "Open: individual units; filled: means",
             fontsize=7.5, va="bottom")
    ax.set_xlabel("A − B (score): negative favors A; positive favors B", labelpad=6)
    fig.text(0.035, 0.066, "Intervals: 2.5–97.5% percentile of paired units resampled within strata; weights held fixed.",
             fontsize=7.6, va="bottom")
    fig.text(0.035, 0.025, "Conditional on empirical strata and stipulated independence; target interval includes zero.",
             fontsize=7.6, va="bottom")
    qa = module("visual_qa")
    start = time.perf_counter()
    preview = qa.render_preview(fig, str(ROOT / "main_figure_preview.png"), dpi=150)
    issues = qa.audit_layout(fig)
    qa.print_report(issues)
    log_call("visual_qa", "render_preview + audit_layout", start, ["current main Figure object"],
             ["main_figure_preview.png"], "Actual main-figure glyph, clipping and tick-overlap audit before vector export")
    report = {"synthetic": True, "layout_issues": issues, "displayed_values": displayed,
              "size_mm_requested": [180, 100], "style": style,
              "preview": preview, "exported": export}
    if any(severity == "FAIL" for severity, _ in issues):
        raise RuntimeError("Repair figure glyph failure before export")
    if export:
        exporter = module("export_figure")
        start = time.perf_counter()
        outputs = exporter.export_figure(fig, str(ROOT / "main_figure"), formats=["svg", "png"],
                                         size_inches=SIZE, dpi=300, tight=False,
                                         grayscale_preview=False)
        Image.open(ROOT / "main_figure.png").convert("L").save(ROOT / "main_figure_grayscale.png")
        log_call("export_figure", "export_figure", start, ["visually reviewed main Figure object"],
                 outputs + ["main_figure_grayscale.png"],
                 "Editable SVG text and 300 dpi PNG; tight=False preserves exact canvas; grayscale derived from final PNG")
        checker = module("check_figure")
        checked = {}
        for filename in ("main_figure.png", "main_figure.svg"):
            start = time.perf_counter()
            found, info = checker.check_figure(str(ROOT / filename), min_dpi=300, target_inches=SIZE)
            checked[filename] = {"issues": found, "info": info}
            log_call("check_figure", "check_figure", start, [filename], ["figure_qa.json"],
                     "Final artifact format and PNG DPI/dimension audit; SVG bitmap embedding audit")
            if any(severity == "FAIL" for severity, _ in found):
                raise RuntimeError(f"Export failed compliance: {filename}")
        svg = ET.parse(ROOT / "main_figure.svg").getroot()
        svg_mm = [float(svg.attrib[k].removesuffix("pt")) * 25.4 / 72 for k in ("width", "height")]
        with Image.open(ROOT / "main_figure.png") as png:
            pixel = list(png.size)
            dpi = png.info["dpi"]
        # SVG serializes points to six decimals; tolerate that sub-micrometre rounding.
        assert all(abs(a - b) < 1e-6 for a, b in zip(svg_mm, [180, 100]))
        assert abs(pixel[0] / dpi[0] * 25.4 - 180) < 0.1
        assert abs(pixel[1] / dpi[1] * 25.4 - 100) < 0.1
        assert svg.findall(".//{http://www.w3.org/2000/svg}text")
        assert not svg.findall(".//{http://www.w3.org/2000/svg}image")
        report.update({"final_checks": checked, "svg_size_mm": svg_mm,
                       "PNG_pixels": pixel, "PNG_dpi": dpi, "SVG_text_editable": True,
                       "SVG_embedded_raster_images": 0})
    (ROOT / "figure_qa.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"preview": preview, "layout_issues": issues, "exported": export}))
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--export", action="store_true", help="Export after actual preview inspection")
    main(parser.parse_args().export)
