"""SYNTHETIC summary display; uses supplied aggregates, never fabricates units.

Run once to preview and audit; rerun with --export after viewing the preview.
Requires installed matplotlib/Pillow and the pinned SciPilot script directory.
"""
import argparse
import hashlib
import json
import os
import sys
from decimal import Decimal
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-scripts', type=Path, required=True)
    parser.add_argument('--receipts', type=Path, required=True)
    parser.add_argument('--export', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    args.receipts.mkdir(parents=True, exist_ok=True)
    os.environ['MPLCONFIGDIR'] = str(args.receipts / 'mpl-cache')
    sys.dont_write_bytecode = True
    expected = {
        'setup_style.py': 'd58ef81684577bb605a92733dd2ca48ade03b4f819b3d255fd62f319be7fea82',
        'visual_qa.py': '67675709e523c76e2748d50749de7bc6332f07df865379b26d024321fb40120f',
        'check_figure.py': '861191858ff47c5af5247f08d0759b14956a2a7e7d8eafcc6b414d37b9d70f06',
    }
    for filename, digest in expected.items():
        assert hashlib.sha256((args.skill_scripts / filename).read_bytes()).hexdigest() == digest, filename
    sys.path.insert(0, str(args.skill_scripts))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from setup_style import setup_style
    from visual_qa import audit_layout, render_preview
    from check_figure import check_figure
    from PIL import Image

    data = json.loads((root / 'aggregate-results.json').read_text())
    means = {key: Decimal(value) for key, value in data['stratum_mean_A_minus_B'].items()}
    target = sum(Decimal(data['target_weights'][key]) * means[key] for key in means)
    sampled = sum(Decimal(data['sampled_weights'][key]) * means[key] for key in means)
    assert target == Decimal(data['target_estimate']) == Decimal('-0.20')
    assert sampled == Decimal(data['sampled_estimate']) == Decimal('1.00')
    assert sum(data['n_by_stratum_reported'].values()) == data['independent_paired_units_reported'] == 8
    assert means['g1'] < 0 < means['g2']
    assert tuple(map(Decimal, data['target_interval'])) == (Decimal('-0.60'), Decimal('0.20'))
    assert data['other_intervals'] is None and not data['bootstrap_replicated']

    style = setup_style(journal='general', lang='en', use_sciplots=False)
    plt.rcParams.update({'font.sans-serif': ['DejaVu Sans'], 'font.size': 9, 'axes.titlesize': 11})
    fig, ax = plt.subplots(figsize=(7.2, 3.5), constrained_layout=True)
    labels = ['g1 (n = 4)', 'g2 (n = 4)', 'Target (0.8 / 0.2)', 'Sampled (0.5 / 0.5)']
    values = [float(means['g1']), float(means['g2']), float(target), float(sampled)]
    ys = [3, 2, 1, 0]
    colors = ['#4d4d4d', '#4d4d4d', '#0072B2', '#D55E00']
    markers = ['o', 'o', 'D', 's']
    for y, value, color, marker in zip(ys, values, colors, markers):
        ax.plot(value, y, marker=marker, color=color, markersize=6, linestyle='none')
        ax.text(3.45, y, f'{value:+.2f}', va='center', ha='left', fontsize=9)
    ax.errorbar(float(target), 1, xerr=[[0.40], [0.40]], fmt='none', color='#0072B2', capsize=4, elinewidth=1.3)
    ax.axvline(0, color='#777777', linestyle='--', linewidth=0.8)
    ax.set_yticks(ys, labels)
    ax.set_ylim(-0.65, 3.65)
    ax.set_xlim(-1.4, 3.95)
    ax.set_xticks([-1, 0, 1, 2, 3])
    ax.set_xlabel('Mean A-B (score): negative favors A, positive favors B', fontsize=9)
    ax.set_title('SYNTHETIC: mixture-dependent paired comparison')
    ax.text(0.02, 0.02, 'Only the target row has the supplied 95% percentile interval.', transform=ax.transAxes, fontsize=8)
    preview = args.receipts / 'figure1-preview.png'
    render_preview(fig, str(preview), dpi=150)
    layout_issues = audit_layout(fig)
    assert not any(severity == 'FAIL' for severity, _ in layout_issues), layout_issues
    report = {'summary_arithmetic': 'PASS', 'bootstrap_replicated': False, 'style': style, 'layout_issues': layout_issues, 'exported': args.export}
    if args.export:
        vector = root / 'figure1-v3.svg'
        fig.savefig(vector, format='svg', metadata={'Title': 'Synthetic mixture-dependent comparison', 'Description': 'Summary estimates from supplied memo v2; no raw unit points.'})
        final_preview = args.receipts / 'figure1-final.png'
        fig.savefig(final_preview, dpi=300)
        with Image.open(final_preview) as image:
            image.convert('L').save(args.receipts / 'figure1-grayscale.png')
        report['file_checks'] = {}
        for path in [vector, final_preview]:
            issues, info = check_figure(str(path), target_inches=(7.2, 3.5))
            assert not any(severity == 'FAIL' for severity, _ in issues), issues
            report['file_checks'][path.name] = {'issues': issues, 'info': info}
    (args.receipts / 'figure-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    plt.close(fig)
    print(json.dumps({'arithmetic': 'PASS', 'layout_issues': layout_issues, 'exported': args.export}))


if __name__ == '__main__':
    main()
