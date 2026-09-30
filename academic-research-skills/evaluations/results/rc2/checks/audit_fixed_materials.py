"""Root-side exact arithmetic for synthetic evaluation materials; not a scoring oracle."""
from pathlib import Path
from fractions import Fraction as F
import csv, json, sys

ROOT = Path(__file__).resolve().parent
FIXTURES = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT / 'work/academic-research-skills/evaluations/fixtures/rc2'

def joint(q, theta):
    result = {(x, y): F(0) for x in (0, 1) for y in (0, 1)}
    for t in (0, 1):
        for e in (0, 1):
            for d in (0, 1):
                p = F(1, 2) * (q if e else 1-q) * (1-theta if d else theta)
                result[t ^ e, t ^ d] += p
    return result

def theta(a, q):
    return (a-q)/(1-2*q)

endpoints = []
for q1, q2, expected in [(F(0), F(1,6), F(69,100)), (F(1,5), F(1,30), F(307,420))]:
    t1, t2 = theta(F(3,4),q1), theta(F(3,5),q2)
    assert F(2,5)*q1+F(3,5)*q2 == F(1,10)
    assert all(F(0)<=q<=F(1,5) for q in (q1,q2))
    assert all(F(1,2)<=t<=F(1) for t in (t1,t2))
    for a,q,t in [(F(3,4),q1,t1), (F(3,5),q2,t2)]:
        assert joint(q,t) == {(0,0):a/2,(1,1):a/2,(0,1):(1-a)/2,(1,0):(1-a)/2}
    target = F(2,5)*t1+F(3,5)*t2
    assert target == expected
    endpoints.append({'q1':str(q1),'q2':str(q2),'theta1':str(t1),'theta2':str(t2),'target':str(target)})
tb = [theta(F(3,4),F(1,10)), theta(F(3,5),F(1,10))]
assert F(2,5)*tb[0]+F(3,5)*tb[1] == F(7,10)

with (FIXTURES/'figure-results.csv').open() as f:
    rows = list(csv.DictReader(f))
assert len(rows)==6
for row in rows:
    assert F(row['loss_A'])-F(row['loss_B']) == F(row['difference_A_minus_B'])
    assert F(row['diff_low']) <= F(row['difference_A_minus_B']) <= F(row['diff_high'])
means = {}
for name, condition, weights in [('C1','C1',[F(1,2),F(1,5),F(3,10)]),('C2','C2',[F(1,5),F(1,2),F(3,10)]),('C2_C1_weights','C2',[F(1,2),F(1,5),F(3,10)])]:
    selected = [r for r in rows if r['condition']==condition]
    assert sum(weights)==1
    a=sum(w*F(r['loss_A']) for w,r in zip(weights,selected))
    b=sum(w*F(r['loss_B']) for w,r in zip(weights,selected))
    means[name]={'A':str(a),'B':str(b),'difference':str(a-b)}
assert [means[k]['difference'] for k in means] == ['17/25','-21/25','-3/25']
change=F(means['C2']['difference'])-F(means['C1']['difference'])
fixed=F(means['C2_C1_weights']['difference'])-F(means['C1']['difference'])
assert change==F(-38,25) and fixed==F(-4,5) and fixed/change==F(10,19)
result={'status':'passed','material_kind':'synthetic_only','design':{'sharp_endpoints':endpoints,'B_theta':[str(t) for t in tb],'B_target':'7/10','bound_reason':'q2=1/6-(2/3)q1; target is strictly increasing on q1 in [0,1/5]; endpoint complete joint laws verified'},'figure_and_manuscript':{'weighted_means':means,'total_change':str(change),'fixed_weight_change':str(fixed),'retained_fraction':str(fixed/change),'aggregate_interval':None,'causal_attribution':False},'scope':'Exact arithmetic and feasible constructions. Human-readable claims, figures and full manuscripts require separate content review.'}
(ROOT/'fixed-material-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
