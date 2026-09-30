"""Frozen synthetic fixture, 180 × 103 mm. Run --export after preview review.

Uses SciPilot's actual style, panel-label, layout-audit and export implementation.
The CSV contains summary estimates, not cluster observations.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import os
import sys

OUT = Path(__file__).resolve().parent
ROOT = Path('LOCAL_EVIDENCE_ROOT')
SOURCE = ROOT / 'work/academic-research-skills/evaluations/fixtures/rc2/figure-results.csv'
PROFESSIONAL = ROOT / 'professional/Haojae/scipilot-figure-skill/scripts'
SIZE = (180 / 25.4, 103 / 25.4)
EXPECTED_SHA256 = 'e2d5923ff6b2d1a95321ece8956a892ad4416d051c8c763c9ea31881a306374c'
BLUE, ORANGE = '#0072B2', '#D55E00'

# Keep font caches and Python bytecode inside the authorized output boundary.
sys.dont_write_bytecode = True
os.environ['MPLCONFIGDIR'] = str(OUT / '.mplconfig')
sys.path.insert(0, str(PROFESSIONAL))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
from setup_style import setup_style
from layout_tools import add_panel_labels
from visual_qa import audit_layout
from export_figure import export_figure


def load_and_check():
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED_SHA256
    with SOURCE.open(newline='') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 6
    for row in rows:
        for key in row.keys() - {'condition', 'group'}:
            row[key] = float(row[key])
            assert math.isfinite(row[key]), key
        d = row['difference_A_minus_B']
        assert math.isclose(d, row['loss_A'] - row['loss_B'], abs_tol=1e-12)
        assert row['diff_low'] <= d <= row['diff_high']
        assert row['n_clusters'] > 0 and row['n_clusters'].is_integer()
        assert 0 <= row['target_weight'] <= 1
    by = {(r['condition'], r['group']): r for r in rows}
    assert set(by) == {(c, g) for c in ('C1', 'C2') for g in ('G1', 'G2', 'G3')}
    for c in ('C1', 'C2'):
        assert math.isclose(sum(by[c, g]['target_weight'] for g in ('G1', 'G2', 'G3')), 1)

    def weighted(result_condition, weight_condition, column):
        return sum(by[weight_condition, g]['target_weight'] * by[result_condition, g][column]
                   for g in ('G1', 'G2', 'G3'))

    estimates = [
        dict(results=c, weights=w, A=weighted(c, w, 'loss_A'),
             B=weighted(c, w, 'loss_B'), difference=weighted(c, w, 'difference_A_minus_B'))
        for c, w in [('C1', 'C1'), ('C2', 'C2'), ('C2', 'C1')]
    ]
    c1, c2, standardized = [e['difference'] for e in estimates]
    total = c2 - c1
    retained = standardized - c1
    weight_switch = c2 - standardized
    # One runnable scientific check: signed contrasts, fixed-weight comparison,
    # and the path-specific descriptive decomposition must agree with the fixture.
    assert all(math.isclose(a, b, abs_tol=1e-12)
               for a, b in zip((c1, c2, standardized, total, retained, weight_switch),
                               (.68, -.84, -.12, -1.52, -.80, -.72)))
    assert math.isclose(total, retained + weight_switch, abs_tol=1e-12)
    calc = dict(estimates=estimates, total_change=total, fixed_C1_weight_change=retained,
                weight_switch_at_C2=weight_switch, retained_fraction=retained / total,
                weight_switch_fraction=weight_switch / total,
                aggregate_intervals=None,
                interval_scope='supplied 95% paired percentile cluster-bootstrap intervals, within group and condition')
    (OUT / 'calculations.json').write_text(json.dumps(calc, indent=2) + '\n')
    return by, calc


def draw(by, calc):
    style = setup_style(journal='general', lang='en', use_sciplots=False, constrained_layout=False)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                         'axes.labelsize': 8, 'xtick.labelsize': 7.5,
                         'axes.linewidth': .6, 'savefig.facecolor': 'white'})
    fig = plt.figure(figsize=SIZE, dpi=150)
    ax = fig.add_axes([.04, .29, .555, .48])
    table = fig.add_axes([.64, .48, .335, .29])
    ax.set_xlim(-5.25, 3.35)
    ax.set_ylim(-.9, 6.05)
    ax.set_yticks([])
    ax.set_xticks([-2, -1, 0, 1, 2, 3])
    ax.set_xlabel('Paired difference A − B (loss points)', labelpad=5)
    ax.spines[['left', 'right', 'top']].set_visible(False)
    ax.spines['bottom'].set_bounds(-2.65, 3.25)
    ax.tick_params(axis='x', length=3)
    ax.plot([0, 0], [-.55, 5.35], color='#777777', lw=.65, ls='--', zorder=1)
    for y in [3.6, 1.3]:
        ax.axhline(y, color='#DDDDDD', lw=.45)
    ax.text(-5.08, 5.82, 'Group', fontsize=7.2, color='#555555')
    ax.text(-4.20, 5.82, 'C', fontsize=7.2, color='#555555')
    ax.text(-3.66, 5.82, 'n', fontsize=7.2, ha='center', color='#555555')
    ax.text(-3.05, 5.82, 'w (%)', fontsize=7.2, ha='center', color='#555555')
    ax.text(-1.35, 5.82, 'A lower', fontsize=7.6, ha='center')
    ax.text(1.55, 5.82, 'B lower', fontsize=7.6, ha='center')
    for group, base in [('G1', 5.10), ('G2', 2.80), ('G3', .50)]:
        ax.text(-5.08, base - .35, group, fontsize=8.5, va='center', fontweight='bold')
        for c, y, color, marker in [('C1', base, BLUE, 'o'), ('C2', base - .70, ORANGE, 's')]:
            row = by[c, group]
            ax.text(-4.20, y, c, color=color, va='center', fontsize=7.8)
            ax.text(-3.66, y, str(int(row['n_clusters'])), ha='center', va='center', fontsize=7.6)
            ax.text(-3.05, y, str(round(row['target_weight'] * 100)), ha='center', va='center', fontsize=7.6)
            d = row['difference_A_minus_B']
            ax.errorbar(d, y, xerr=[[d - row['diff_low']], [row['diff_high'] - d]],
                        fmt=marker, color=color, ecolor=color, capsize=2.2,
                        elinewidth=1, capthick=.8, markersize=4.8,
                        markeredgecolor='white', markeredgewidth=.45, zorder=3)

    table.set_axis_off()
    for x, label in [(0, 'Results / weights'), (.50, 'A'), (.71, 'B'), (.97, 'A−B')]:
        table.text(x, .91, label, ha='left' if x == 0 else 'right', fontsize=7.2, color='#555555')
    for y, e in zip([.69, .41, .13], calc['estimates']):
        table.text(0, y, f"{e['results']}\n{e['weights']} weights", fontsize=7.7, va='center')
        table.text(.50, y, f"{e['A']:.2f}", fontsize=8, ha='right', va='center')
        table.text(.71, y, f"{e['B']:.2f}", fontsize=8, ha='right', va='center')
        lower = 'A lower' if e['difference'] < 0 else 'B lower'
        table.text(.97, y, f"{e['difference']:+.2f}\n{lower}", fontsize=7.8,
                   ha='right', va='center', fontweight='bold')

    add_panel_labels(fig, axes=[ax, table], labels=['a', 'b'], x_offset_pt=0,
                     y_offset_pt=10, ha='left', fontsize=9)
    title_y = .77 + 10 / (SIZE[1] * 72)
    fig.text(.075, title_y, 'Paired group contrasts', fontsize=9, va='bottom', fontweight='bold')
    fig.text(.675, title_y, 'Target-weighted losses', fontsize=9, va='bottom', fontweight='bold')
    fig.text(.04, .966, 'Target-weighted averages reverse between conditions', fontsize=10.5,
             va='top', fontweight='bold')
    fig.text(.04, .908, 'Synthetic development fixture • lower loss is better', fontsize=8, va='top')
    fig.text(.04, .871, 'Whiskers: supplied 95% paired cluster-bootstrap intervals', fontsize=7.6, va='top', color='#555555')
    fig.text(.64, .445, 'Averages are point estimates; no aggregate CI.', fontsize=7.1, color='#555555')
    fig.text(.64, .394, 'C1 → C2 change in A−B: −1.52 points', fontsize=8.1, fontweight='bold')
    fig.text(.64, .351, 'C1 weights retained: −0.80 (53% of change)', fontsize=7.5)
    fig.text(.64, .312, 'Weight switch at C2: −0.72 (47%)', fontsize=7.5)
    fig.text(.04, .170, 'Counterexamples: C1 G2 and G3 favor A; C2 G1 favors B.', fontsize=8, fontweight='bold')
    fig.text(.04, .126, 'C2 G3: its interval includes zero; direction remains unresolved.', fontsize=7.6)
    fig.text(.04, .071, 'n = independent clusters; w = prescribed target %. Intervals concern each paired group A−B.', fontsize=7.1)
    fig.text(.04, .033, 'Frozen synthetic fixtures • no causal or equivalence inference • aggregate uncertainty unavailable', fontsize=7)
    return fig, style


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export', action='store_true')
    args = parser.parse_args()
    by, calc = load_and_check()
    fig, style = draw(by, calc)
    issues = audit_layout(fig)
    report = dict(stage='export' if args.export else 'preview', style=style, issues=issues,
                  exact_size_mm=[180, 103], minimum_font_pt=7)
    (OUT / 'layout_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    assert not issues, issues
    # SciPilot's preview/grayscale helpers crop with bbox='tight'; use an exact
    # canvas here so the specified physical width and height survive export.
    fig.savefig(OUT / 'preview-target-size.png', dpi=150, bbox_inches=None)
    with Image.open(OUT / 'preview-target-size.png') as image:
        image.convert('L').save(OUT / 'preview-grayscale.png', dpi=(150, 150))
    if args.export:
        export_figure(fig, str(OUT / 'figure'), formats=['svg', 'png'], dpi=300,
                      size_inches=SIZE, tight=False, grayscale_preview=False)
    print(json.dumps(dict(size_mm=[180, 103], calculations=calc, layout_issues=issues), indent=2))
    plt.close(fig)


if __name__ == '__main__':
    main()
