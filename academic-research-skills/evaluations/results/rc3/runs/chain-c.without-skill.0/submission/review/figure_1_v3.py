"""Draw only supplied aggregates; do not simulate units or rerun the bootstrap."""
import csv
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(HERE.parent.parent / ".matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    with (HERE / "aggregate-results-v3.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert [r["comparison"] for r in rows] == [
        "g1", "g2", "equal_sampled_mixture", "target_mixture"
    ]
    means = [float(r["mean_A_minus_B_score"]) for r in rows]
    assert means == [-1.0, 3.0, 1.0, -0.2]
    assert [(r["ci_lower"], r["ci_upper"]) for r in rows[:-1]] == [("", "")] * 3
    lo, hi = float(rows[-1]["ci_lower"]), float(rows[-1]["ci_upper"])
    assert (lo, hi) == (-0.6, 0.2)
    plt.rcParams.update({"font.size": 11, "svg.fonttype": "none", "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(9.4, 4.6))
    ys = [3, 2, 1, 0]
    for x, y, marker in zip(means, ys, ["o", "s", "^", "D"]):
        ax.plot(x, y, marker=marker, color="#222222", markersize=7, linestyle="none")
        ax.annotate(f"{x:+.2f}", (x, y), xytext=(0, 12), textcoords="offset points",
                    ha="center", fontsize=10)
    ax.errorbar(means[-1], 0, xerr=[[means[-1] - lo], [hi - means[-1]]],
                fmt="none", ecolor="#222222", capsize=5, linewidth=1.5)
    ax.axvline(0, color="#666666", linestyle="--", linewidth=1)
    ax.set_yticks(ys, ["g1 (n=4)", "g2 (n=4)",
                      "Equal sampled mix (0.5/0.5; n=8)",
                      "Target mix (0.8/0.2; n=8)"])
    ax.set_xlim(-1.6, 3.6)
    ax.set_ylim(-0.6, 3.65)
    ax.set_xlabel("Mean A−B (score; lower score is better)")
    ax.set_title("Composition changes the aggregate direction", pad=15)
    ax.tick_params(axis="y", length=0)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.text(0.03, 0.04,
             "SYNTHETIC memo v2 aggregates. Interval only for target: 95% within-stratum\n"
             "paired-unit percentile bootstrap [−0.60, 0.20]; not independently recomputed.",
             fontsize=9)
    fig.subplots_adjust(left=0.36, right=0.98, top=0.83, bottom=0.25)
    for extension in ("svg", "png", "pdf"):
        fig.savefig(HERE / f"figure-1-v3.{extension}", dpi=200,
                    metadata={"Creator": "Synthetic developmental local package"})
    plt.close(fig)


if __name__ == "__main__":
    main()
