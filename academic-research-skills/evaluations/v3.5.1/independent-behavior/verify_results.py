import csv,json,re,hashlib
from fractions import Fraction as F
from pathlib import Path
rows=list(csv.DictReader(open('measurements.csv'))); result=json.load(open('results.json')); fits=list(csv.DictReader(open('errors-and-fits.csv')))
x=[F(r['scale']) for r in rows];n=len(rows)
checks=[]
for m in ['a','b']:
    y=[abs(F(r['method_'+m])-F(r['truth'])) for r in rows]
    xb=sum(x)/n;yb=sum(y)/n
    slope=sum((a-xb)*(b-yb) for a,b in zip(x,y))/sum((a-xb)**2 for a in x);intercept=yb-slope*xb
    assert slope==F(result['linear_models'][m]['slope']) and intercept==F(result['linear_models'][m]['intercept'])
    assert yb==F(result['descriptives'][m]['mean'])
    assert all(F(r['abs_error_'+m])==v for r,v in zip(fits,y))
    assert all(v==intercept+slope*z for z,v in zip(x,y))
    checks.append({'method':m,'MAE':str(yb),'intercept':str(intercept),'slope':str(slope),'all_rows_exact':True})
assert F(result['paired_comparison']['difference_A_minus_B']['mean'])==F(19,40)
assert abs(float(result['paired_comparison']['relative_MAE_reduction_B_vs_A'])-float(F(19,37)))<1e-15
registry={r['claim_id']:r for r in csv.DictReader(open('claims.csv'))}
for line in Path('manuscript.md').read_text().splitlines():
    m=re.search(r'\[claim:(C\d+)\]',line)
    if m:
        clean=' '.join(re.sub(r'\[(?:claim|evidence):[^]]+\]','',line).split())
        assert hashlib.sha256(clean.encode()).hexdigest()==registry[m.group(1)]['claim_text_sha256']
initial=json.load(open('initial-phase.json'));phase=json.load(open('phase.json'))
for key in ['id','started_at','project_deadline','deadline','reserve_seconds','authorization','objective','latest_instruction','budget_kind']:
    assert initial[key]==phase[key],key
assert len(phase['repairs']['retired_stats_helper unavailable'])==4
out={'status':'pass','independent_method':'stdlib Fraction rational arithmetic, separately executed; no numpy/Decimal reuse','record_count':n,'checks':checks,'claim_hashes_checked':len(registry),'original_budget_and_objective_preserved':True,'original_failed_attempts_preserved':True,'scope':'computation reproducibility within same supplied data; no independent empirical replication'}
Path('verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
