"""Reproduce recorded scores. Default is frozen configurations in a fresh directory."""
import argparse
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
sys.path.insert(0, str(TASK))
import harness
from methods import detect_initial, detect_refined


def score_grid(stage, configs, out):
    detector = {'baseline': harness.baseline, 'initial': detect_initial, 'refined': detect_refined}[stage]
    reports = []
    for i, params in enumerate(configs):
        report = harness.score(detector, params, TASK / 'data/dev.json', out, f'{stage}_{i:02d}')
        reports.append(report)
    for r in sorted(reports, key=lambda r: r['mean_loss']):
        print(r['name'], r['params'], round(r['mean_loss'], 4), r['false_alarms'], r['hits'])
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['baseline', 'initial', 'refined', 'frozen'], default='frozen')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    out = args.out or (HERE / 'rerun')
    if (out / 'score-events.jsonl').exists():
        raise SystemExit('Use an empty output directory to keep call records unambiguous.')
    if args.stage == 'baseline':
        configs = [{'k': k, 'h': h, 'clip': 3.} for k, h in itertools.product([.2, .4, .6, .8], [8, 12, 18, 26])]
    elif args.stage == 'initial':
        configs = [{'k': .4, 'h': 12., 'clip': 3., 'confirm_n': n, 'confirm': c, 'expiry': 60} for n, c in itertools.product([6, 10, 16], [.3, .5, .7, .9])]
    elif args.stage == 'refined':
        configs = [{'k': .3, 'h': h, 'clip': 3., 'window': w, 'budget': b, 'coverage': .6} for w, b, h in itertools.product([36, 48, 60], [8, 12], [6., 10.])][:-1]
    else:
        frozen = json.loads((HERE / 'frozen.json').read_text())
        for stage in ['baseline', 'initial', 'refined', 'ablation']:
            detector = {'baseline': harness.baseline, 'initial': detect_initial, 'refined': detect_refined, 'ablation': detect_refined}[stage]
            r = harness.score(detector, frozen[stage], TASK / 'data/dev.json', out, stage)
            print(stage, round(r['mean_loss'], 4), r['false_alarms'], r['hits'])
        return
    reports = score_grid(args.stage, configs, out)
    if args.stage == 'refined':
        best = min(reports, key=lambda r: r['mean_loss'])
        ablation = dict(best['params'], budget=0)
        result = harness.score(detect_refined, ablation, TASK / 'data/dev.json', out, 'refined_ablation_11')
        print('refined_ablation_11', round(result['mean_loss'], 4), result['false_alarms'], result['hits'])


if __name__ == '__main__':
    main()
