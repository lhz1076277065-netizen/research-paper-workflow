"""Recorded dev tuning, run from this directory with the task Python runtime.

An existing score-events file blocks accidental duplicate tuning. Use --check for causal/known cases and --report to rebuild summaries from
recorded rows without additional validation calls.
"""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
HERE = OUT.parent
sys.path.insert(0, str(HERE))
import harness
from methods import detect_initial, detect_refined

BASELINE_GRID = [dict(k=k, h=h, clip=2.) for k in (.15, .35, .55, .75) for h in (12., 20., 32., 48.)]
INITIAL_GRID = [dict(k=.35, h=10., clip=2., guard=guard, confirm=confirm,
                     min_count=max(6, int(.6*confirm)), mean=mean)
                for guard, confirm in ((4,12),(8,12),(8,18),(12,18)) for mean in (.35,.55,.75)]


def tune_initial():
    if (OUT/'score-events.jsonl').exists():
        raise SystemExit('Already recorded scores: do not rerun tuning in this frozen directory.')
    for family, detector, configs in [('baseline',harness.baseline,BASELINE_GRID),('initial',detect_initial,INITIAL_GRID)]:
        reports=[]
        for i, params in enumerate(configs):
            report=harness.score(detector,params,HERE/'data/dev.json',OUT,f'{family}-{i:02d}')
            reports.append(report)
            print(family,i,report['mean_loss'],report['false_alarms'],report['hits'])
        best=min(reports,key=lambda r:(r['mean_loss'],r['false_alarms'],-r['hits']))
        (OUT/f'{family}-selection.json').write_text(json.dumps(best,indent=2)+'\n')
        print('BEST',family,best['name'],best['params'])


REFINED_GRID = [dict(k=.2, h=h, clip=2., window=window, erase=8, min_count=16)
                for window in (32,48,64) for h in (6.,10.,14.)]
REFINED_GRID.append(dict(k=.2,h=10.,clip=2.,window=48,erase=12,min_count=16))
# Two ablations are included within the total 12 refined-config budget.
REFINED_GRID.extend([dict(k=.2,h=h,clip=2.,window=48,erase=0,min_count=16) for h in (10.,14.)])


def tune_refined():
    events=[json.loads(line) for line in (OUT/'score-events.jsonl').read_text().splitlines()]
    if any(e['name'].startswith('refined-') for e in events):
        raise SystemExit('Refinement already recorded.')
    reports=[]
    for i,params in enumerate(REFINED_GRID):
        report=harness.score(detect_refined,params,HERE/'data/dev.json',OUT,f'refined-{i:02d}')
        reports.append(report)
        print('refined',i,report['mean_loss'],report['false_alarms'],report['hits'])
    best=min(reports[:10],key=lambda r:(r['mean_loss'],r['false_alarms'],-r['hits']))
    (OUT/'refined-selection.json').write_text(json.dumps(best,indent=2)+'\n')
    print('BEST refined',best['name'],best['params'])


def check():
    """No scorer calls: analytic cases and exhaustive train-prefix causality."""
    import time
    start=time.perf_counter()
    frozen=json.loads((OUT/'frozen.json').read_text())
    prefix=[-1.,1.]*32
    p=frozen['refined']
    examples={}
    for sign in (-1.,1.):
        for duration in (1,4,8):
            x=prefix+[0.]*20+[sign*100.]*duration+[0.]*100
            alarm=detect_refined(x,p)
            assert alarm == -1,(sign,duration,alarm)
            examples[f'burst_sign{sign}_duration{duration}']=alarm
        x=prefix+[0.]*20+[sign*2.]*100
        alarm=detect_refined(x,p)
        assert 84 <= alarm <= 144,alarm
        examples[f'sustained_sign{sign}']=alarm
    assert detect_refined(prefix+[None]*100,p) == -1
    assert detect_initial(prefix+[None]*100,frozen['initial']) == -1
    assert detect_refined([],p) == -1
    # Same observed prefix cannot distinguish a sustained change from a burst.
    sustained=prefix+[0.]*20+[100.]*100
    sustained_alarm=detect_refined(sustained,p)
    burst=prefix+[0.]*20+[100.]*(sustained_alarm-84+1)+[0.]*100
    burst_alarm=detect_refined(burst,p)
    assert burst_alarm == sustained_alarm
    examples['long_burst_indistinguishability']={'sustained_alarm':sustained_alarm,'burst_alarm':burst_alarm,'burst_length':sustained_alarm-84+1}
    # A gap must not make stale pre-gap evidence alarm at an unobserved time.
    gap_case=prefix+[0.]*20+[2.]*10+[None]*40+[2.]*100
    gap_alarm=detect_refined(gap_case,p)
    assert gap_alarm >= 134 and gap_case[gap_alarm] is not None
    examples['long_gap_alarm']=gap_alarm
    try:
        detect_refined(prefix+[float('nan')],p)
    except ValueError:
        pass
    else:
        raise AssertionError('NaN accepted')
    data=json.loads((HERE/'data/train.json').read_text())
    checked=0
    for name,detector in [('initial',detect_initial),('refined',detect_refined)]:
        params=frozen[name]
        for case in data:
            alarm=detector(case['x'],params)
            for length in range(len(case['x'])+1):
                expected=alarm if alarm >= 0 and alarm < length else -1
                assert detector(case['x'][:length],params) == expected,(name,case['id'],length,alarm)
                checked+=1
    record={'known_cases':examples,'train_cases':len(data),'prefix_checks':checked,'all_passed':True,'runtime_seconds':time.perf_counter()-start,'note':'Checks establish these examples and prefix consistency, not statistical validity or holdout performance.'}
    (OUT/'checks.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record,indent=2))


def report():
    """Rebuild paired comparisons from recorded scores, without reevaluation."""
    import csv
    import statistics
    names={'baseline':'baseline-05','initial':'initial-01','refined':'refined-01',
           'ablation':'refined-10','matched_erasure':'refined-04',
           'conservative_erasure':'refined-05','conservative_ablation':'refined-11'}
    records={k:json.loads((OUT/(v+'.json')).read_text()) for k,v in names.items()}
    pairs=[]
    for i,b in enumerate(records['baseline']['rows']):
        a=records['initial']['rows'][i]; r=records['refined']['rows'][i]
        assert b['id']==a['id']==r['id']
        pairs.append(dict(id=b['id'],condition=b['condition'],tau=b['tau'],
                          baseline_alarm=b['alarm'],initial_alarm=a['alarm'],refined_alarm=r['alarm'],
                          baseline_loss=b['loss'],initial_loss=a['loss'],refined_loss=r['loss'],
                          initial_minus_baseline=a['loss']-b['loss'],
                          refined_minus_baseline=r['loss']-b['loss'],
                          refined_minus_initial=r['loss']-a['loss']))
    with (OUT/'paired-dev.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(pairs[0]));writer.writeheader();writer.writerows(pairs)
    summary={}
    for col in ['initial_minus_baseline','refined_minus_baseline','refined_minus_initial']:
        ds=[p[col] for p in pairs]
        summary[col]={'mean_difference':statistics.mean(ds),
                      'paired_standard_error':statistics.stdev(ds)/len(ds)**.5,
                      'better':sum(d<0 for d in ds),'worse':sum(d>0 for d in ds),
                      'equal':sum(d==0 for d in ds),'sum_difference':sum(ds),
                      'max_improvement':min(ds),'max_worsening':max(ds)}
    summary['selected']={k:{'record':names[k]+'.json','mean_loss':v['mean_loss'],
                           'false_alarms':v['false_alarms'],'hits':v['hits'],
                           'null_false_alarms':sum(r['false_alarm'] and r['tau'] is None for r in v['rows']),
                           'pre_shift_false_alarms':sum(r['false_alarm'] and r['tau'] is not None for r in v['rows']),
                           'mean_successful_delay':statistics.mean(r['delay'] for r in v['rows'] if r['hit']),
                           'runtime_seconds':v['runtime_seconds']}
                         for k,v in records.items()}
    (OUT/'paired-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    lines=['| Record / detector | Mean loss | False alarms | Hits ≤60 / 60 | Mean delay among hits |',
           '|---|---:|---:|---:|---:|']
    for k in names:
        r=summary['selected'][k]
        lines.append(f"| {names[k]} ({k}) | {r['mean_loss']:.3f} | {r['false_alarms']} | {r['hits']} | {r['mean_successful_delay']:.3f} |")
    lines+=['','| Condition (n=30 each) | Baseline loss | Initial loss | Refined loss | Refined − baseline |',
            '|---|---:|---:|---:|---:|']
    for c in records['baseline']['groups']:
        vs=[records[k]['groups'][c]['mean_loss'] for k in ('baseline','initial','refined')]
        lines.append(f'| {c} | {vs[0]:.3f} | {vs[1]:.3f} | {vs[2]:.3f} | {vs[2]-vs[0]:+.3f} |')
    (OUT/'results-table.md').write_text('\n'.join(lines)+'\n')
    print('Rebuilt paired-dev.csv, paired-summary.json, results-table.md.')


if __name__ == '__main__':
    if '--report' in sys.argv:
        report()
    elif '--check' in sys.argv:
        check()
    elif '--refine' in sys.argv:
        tune_refined()
    else:
        tune_initial()
