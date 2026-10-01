"""Pair saved score rows, diagnose initial alarms, and make the manuscript table."""
import csv
import hashlib
import json
import math
import random
import statistics
from pathlib import Path
from methods import _calibrate

HERE=Path(__file__).resolve().parent
f=json.loads((HERE/'frozen.json').read_text())
reports={name:json.loads((HERE/'validation'/(record+'.json')).read_text()) for name,record in f['selection'].items()}
reports['ablation']=json.loads((HERE/'validation'/'ablation-no-excision.json').read_text())
reports['no_coverage']=json.loads((HERE/'validation'/'ablation-no-coverage.json').read_text())
rows={name:{r['id']:r for r in report['rows']} for name,report in reports.items()}
ids=list(rows['baseline'])
assert all(set(r)==set(ids) for r in rows.values())
paired=[]
for case_id in ids:
    base=rows['baseline'][case_id]
    result={k:base[k] for k in ('id','condition','tau')}
    for name in reports:
        for key in ('alarm','loss','false_alarm','hit','delay'):
            result[f'{name}_{key}']=rows[name][case_id][key]
    result['refined_minus_baseline_loss']=result['refined_loss']-result['baseline_loss']
    result['refined_minus_initial_loss']=result['refined_loss']-result['initial_loss']
    paired.append(result)
with (HERE/'paired-cases.csv').open('w') as s:
    writer=csv.DictWriter(s,fieldnames=list(paired[0]));writer.writeheader();writer.writerows(paired)

comparisons={}
rng=random.Random(774091)
for competitor in ('baseline','initial','ablation'):
    diff=[rows['refined'][i]['loss']-rows[competitor][i]['loss'] for i in ids]
    # Descriptive post-selection interval, not an unbiased estimate of generalization.
    means=sorted(statistics.mean(rng.choices(diff,k=len(diff))) for _ in range(10000))
    comparisons[competitor]={'mean_paired_loss_difference':statistics.mean(diff),'bootstrap_percentile_95':[means[249],means[9749]],'improved_cases':sum(v<0 for v in diff),'tied_cases':sum(v==0 for v in diff),'worsened_cases':sum(v>0 for v in diff),'bootstrap_seed':774091,'resamples':10000,'status':'descriptive after development selection; selection uncertainty omitted'}

p=f['refined']; dev=json.loads((HERE.parent/'data'/'dev.json').read_text());diagnostics=[]
for case in dev:
    alarm=rows['initial'][case['id']]['alarm']
    if alarm<0: continue
    mu,scale=_calibrate(case['x']);q=case['x'][alarm-p['window']+1:alarm+1]
    z=[None if v is None else max(-p['clip'],min(p['clip'],(v-mu)/scale)) for v in q]
    sign=1 if sum(v for v in z if v is not None)>=0 else -1
    residual=[]
    removed=[]
    for j in range(p['window']-p['burst']+1):
        kept=[v for v in z[:j]+z[j+p['burst']:] if v is not None]
        residual.append(sign*sum(kept)/math.sqrt(len(kept)) if kept else None)
        removed.append(sign*sum(v for v in z[j:j+p['burst']] if v is not None))
    worst=min(v for v in residual if v is not None)
    diagnostics.append({'id':case['id'],'condition':case['condition'],'initial_alarm':alarm,'initial_false_alarm':rows['initial'][case['id']]['false_alarm'],'initial_delay':rows['initial'][case['id']]['delay'],'signed_full_window_sum':sign*sum(v for v in z if v is not None),'max_six_step_support':max(removed),'worst_retained_statistic_at_initial_alarm':worst,'excision_statistic_passes':worst>p['threshold'],'refined_alarm':rows['refined'][case['id']]['alarm']})
(HERE/'alarm-diagnostics.json').write_text(json.dumps(diagnostics,indent=2)+'\n')
summary={'result_id':'dev-frozen-001','n':len(ids),'target_n':sum(r['tau'] is not None for r in rows['baseline'].values()),'comparisons':comparisons,'methods':{name:{key:r[key] for key in ('name','params','mean_loss','false_alarms','hits','runtime_seconds','data_sha256','groups')} for name,r in reports.items()},'diagnostic_false_alarms':{'initial':sum(d['initial_false_alarm'] for d in diagnostics),'below_refined_excision_threshold_at_initial_alarm':sum(d['initial_false_alarm'] and not d['excision_statistic_passes'] for d in diagnostics)}}
(HERE/'comparison-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=['| Method | Mean loss | False alarms /120 | Hits /60 | Mean hit delay | Runtime (s/120 streams) |','|---|---:|---:|---:|---:|---:|']
for name,r in reports.items():
    delays=[v['delay'] for v in r['rows'] if v['hit']]
    lines.append(f"| {name} | {r['mean_loss']:.3f} | {r['false_alarms']} | {r['hits']} | {statistics.mean(delays):.3f} | {r['runtime_seconds']:.4f} |")
(HERE/'results-table.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines)); print(json.dumps(comparisons,indent=2));print(json.dumps(summary['diagnostic_false_alarms']))
