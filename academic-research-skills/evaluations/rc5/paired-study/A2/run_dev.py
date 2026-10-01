"""Reproduce bounded tuning; every train/dev evaluation uses harness.score.
Run with the supplied Python. --stage summarize reuses rows without scoring.
"""
import argparse
import csv
import json
from pathlib import Path
import statistics
import sys

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
sys.path.insert(0, str(TASK))
import harness
from methods import detect_initial, detect_refined, trace_refined

BASELINES = [{'clip': clip, 'k': k, 'h': h}
             for clip, k in [(2., .4), (2., .6), (3., .4), (3., .6)]
             for h in [12., 20., 30., 40.]]
INITIALS = [{'clip': 2., 'k': .4, 'h': h, 'min_age': age}
            for h in [12., 20., 30.] for age in [12, 20, 28, 36]]
# Refined grid is set after the recorded initial diagnostic, not beforehand.
REFINED = [{'clip': 2., 'k': .4, 'h': h, 'block': block,
            'confirm_mean': .35, 'max_gap': 12, 'two_blocks': True}
           for h in [6., 10., 14.] for block in [6, 8, 10]]
REFINED += [{'clip': 2., 'k': .4, 'h': 10., 'block': block,
             'confirm_mean': .55, 'max_gap': 12, 'two_blocks': True}
            for block in [6, 8]]


def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')


def tune(detector, configurations, family):
    reports = []
    for i, params in enumerate(configurations):
        report = harness.score(detector, params, TASK / 'data/dev.json', HERE,
                               f'dev-{family}-{i:02d}')
        reports.append(report)
        print(family, i, 'loss', round(report['mean_loss'], 3),
              'FA', report['false_alarms'], 'hits', report['hits'], params)
    # Fixed selection rule: task mean loss, then fewer false alarms, then grid order.
    return min(enumerate(reports), key=lambda p: (p[1]['mean_loss'],
                                                 p[1]['false_alarms'], p[0]))[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['initial', 'refined', 'summarize'], default='summarize')
    args = parser.parse_args()
    if args.stage == 'initial':
        if (HERE / 'score-events.jsonl').exists():
            raise RuntimeError('Existing validation log: preserve it; do not silently retune.')
        baseline = tune(harness.baseline, BASELINES, 'baseline')
        initial = tune(detect_initial, INITIALS, 'initial')
        save('selection-initial.json', {'baseline': baseline, 'initial': initial})
    elif args.stage == 'refined':
        if any(HERE.glob('dev-refined-*.json')):
            raise RuntimeError('Refined stage has already run.')
        assert REFINED, 'Set refined grid after inspecting the initial diagnostic.'
        selected = json.loads((HERE / 'selection-initial.json').read_text())
        refined = tune(detect_refined, REFINED, 'refined')
        ablation_params = {**refined['params'], 'two_blocks': False}
        ablation = harness.score(detect_refined, ablation_params, TASK / 'data/dev.json',
                                 HERE, 'dev-refined-ablation')
        print('ablation', ablation['mean_loss'], ablation['false_alarms'], ablation['hits'])
        save('selection-final.json', {**selected, 'refined': refined, 'ablation': ablation})
    else:
        summarize()


def summarize():
    frozen = json.loads((HERE / 'frozen.json').read_text())
    reports = {key: json.loads((HERE / frozen['selected_reports'][key]).read_text())
               for key in ['baseline', 'initial', 'refined', 'ablation']}
    by_id = {key: {r['id']: r for r in rep['rows']} for key, rep in reports.items()}
    rows = []
    for case_id, baseline in by_id['baseline'].items():
        row = {'id': case_id, 'condition': baseline['condition'], 'tau': baseline['tau']}
        for key in reports:
            r = by_id[key][case_id]
            for metric in ['alarm', 'false_alarm', 'hit', 'delay', 'loss']:
                row[f'{key}_{metric}'] = r[metric]
        row['refined_minus_baseline_loss'] = row['refined_loss'] - row['baseline_loss']
        rows.append(row)
    with (HERE / 'paired-dev.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    summary = {}
    for group in ['all', 'clean', 'bursts', 'heavy', 'gaps']:
        block = [r for r in rows if group == 'all' or r['condition'] == group]
        entry = {}
        for key in reports:
            delays = [r[f'{key}_delay'] for r in block if r[f'{key}_hit']]
            entry[key] = {'n': len(block),
                          'mean_loss': statistics.mean(r[f'{key}_loss'] for r in block),
                          'false_alarms': sum(r[f'{key}_false_alarm'] for r in block),
                          'hits': sum(r[f'{key}_hit'] for r in block),
                          'mean_hit_delay': statistics.mean(delays) if delays else None}
        differences = [r['refined_minus_baseline_loss'] for r in block]
        entry['paired_refined_minus_baseline'] = {
            'mean': statistics.mean(differences),
            'better': sum(d < 0 for d in differences),
            'worse': sum(d > 0 for d in differences),
            'tied': sum(d == 0 for d in differences)}
        summary[group] = entry
    save('paired-summary.json', summary)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
