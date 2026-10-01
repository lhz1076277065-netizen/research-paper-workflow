"""Run the bounded development search, or replay frozen configurations.

python run_dev.py --tune  # original development procedure (40 dev calls)
python run_dev.py         # four frozen methods; writes reproduction/ records
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK_ROOT = HERE.parent
sys.path.insert(0, str(TASK_ROOT))
import harness
from methods import detect_initial, detect_refined

BASELINE_GRID = [dict(clip=c, k=k, h=h) for c in (1.5, 2.5) for k in (.25, .5) for h in (8., 12., 16., 24.)]
INITIAL_GRID = [dict(clip=2.5, k=.35, h=h, confirm=n, mean=m, timeout=2*n) for h in (6., 10.) for n in (6, 12, 18) for m in (.35, .65)]
REFINED_GRID = [dict(clip=2., window=w, burst=b, threshold=h, coverage=.6) for w, b in ((24, 6), (32, 8), (40, 10), (32, 12), (40, 16)) for h in (2., 3.)]


def score(name, detector, params, split, out):
    report = harness.score(detector, params, TASK_ROOT/'data'/f'{split}.json', out, name)
    print(json.dumps({key:report[key] for key in ('name','mean_loss','false_alarms','hits','runtime_seconds')}))
    return report


def select(reports):
    return min(reports, key=lambda r:(r['mean_loss'], r['false_alarms'], -r['hits'], r['name']))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tune', action='store_true')
    p.add_argument('--output-dir', type=Path)
    args = p.parse_args()
    if args.tune:
        out = args.output_dir or HERE/'validation'
        if (out/'score-events.jsonl').exists():
            raise SystemExit('Use a fresh output directory to preserve the original call records.')
        base = select([score(f'baseline-{i:02d}', harness.baseline, q, 'dev', out) for i,q in enumerate(BASELINE_GRID)])
        initial = select([score(f'initial-{i:02d}', detect_initial, q, 'dev', out) for i,q in enumerate(INITIAL_GRID)])
        refined = select([score(f'refined-{i:02d}', detect_refined, q, 'dev', out) for i,q in enumerate(REFINED_GRID)])
        # Ablations are the final two refined configurations, inside the 12-config budget.
        ablation_no_excision = dict(refined['params'], burst=0)
        ablation_no_coverage = dict(refined['params'], coverage=.01)
        a1 = score('ablation-no-excision', detect_refined, ablation_no_excision, 'dev', out)
        a2 = score('ablation-no-coverage', detect_refined, ablation_no_coverage, 'dev', out)
        frozen = {'baseline':base['params'], 'initial':initial['params'], 'refined':refined['params'],
                  'ablation':ablation_no_excision, 'ablation_function':'detect_refined',
                  'secondary_ablation':ablation_no_coverage,
                  'selection':{k:r['name'] for k,r in [('baseline',base),('initial',initial),('refined',refined)]},
                  'selection_rule':'Minimum development mean loss; ties use fewer false alarms, more hits, lexicographic record name.',
                  'scope':'Development-selected, frozen before external holdout; no holdout inspected.'}
        (HERE/'frozen.json').write_text(json.dumps(frozen,indent=2)+'\n')
        for name, fn in [('baseline',harness.baseline),('initial',detect_initial),('refined',detect_refined)]:
            score(f'train-selected-{name}', fn, frozen[name], 'train', out)
    else:
        out = args.output_dir or HERE/'reproduction'
        q = json.loads((HERE/'frozen.json').read_text())
        for name, fn in [('baseline',harness.baseline),('initial',detect_initial),('refined',detect_refined),('ablation',detect_refined)]:
            score(name, fn, q[name], 'dev', out)


if __name__ == '__main__':
    main()
