"""Exact audit of the supplied fixed synthetic packet; standard library only."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import csv, hashlib, json, shutil, sys

OUT = Path(__file__).resolve().parent
INPUT = OUT.parent / 'writing-input'

def cost(rows, acts, outcomes=None, expected=False):
    ys = outcomes if outcomes is not None else [r['p'] if expected else r['y'] for r in rows]
    return sum((a*r['c'] + (1-a)*y*r['L'] for r,a,y in zip(rows,acts,ys)), F(0))

def gain(rows, a, b, q):
    return cost(rows,b,q) - cost(rows,a,q)

def adverse_q(rows,a,b,eps):
    return [max(F(0),r['p']-eps) if x>z else min(F(1),r['p']+eps) if x<z else r['p'] for r,x,z in zip(rows,a,b)]

def lower_gain(rows,a,b,eps):
    return gain(rows,a,b,adverse_q(rows,a,b,eps))

def exact_zero(rows,a,b):
    points = sorted({F(0),F(1)} | {r['p'] if x>z else 1-r['p'] for r,x,z in zip(rows,a,b) if x!=z})
    for lo,hi in zip(points,points[1:]):
        gl,gh = lower_gain(rows,a,b,lo),lower_gain(rows,a,b,hi)
        if gl==0:return lo
        if gl>0 and gh<=0:return lo+gl*(hi-lo)/(gl-gh)
    return None

def rational(x):return {'exact':str(x),'value':float(x)}

def main():
    manifest=json.loads((INPUT/'manifest.json').read_text())
    assert all(hashlib.sha256((INPUT/k).read_bytes()).hexdigest()==v for k,v in manifest.items()), 'Input hash mismatch'
    rows=[]
    with (INPUT/'cases.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            p,c,L=F(r['probability']),F(r['action_cost']),F(r['miss_loss'])
            assert 0<=p<=1 and c>=0 and L>0 and r['outcome'] in ('0','1')
            rows.append({'id':r['case'],'p':p,'c':c,'L':L,'y':int(r['outcome'])})
    assert len({r['id'] for r in rows})==len(rows)==12
    a=[int(r['p']*r['L']>r['c']) for r in rows]
    b=[int(r['p']>F(1,2)) for r in rows]
    bayes=[int((1-r['p'])*r['c']+r['p']*r['c']<(1-r['p'])*0+r['p']*r['L']) for r in rows]
    oracle=[int(r['c']<r['y']*r['L']) for r in rows]
    policies={'cost_rule':a,'probability_0.5':b,'classical_bayes':bayes,'act_all':[1]*len(rows),'act_none':[0]*len(rows),'outcome_oracle':oracle}
    summaries=[]
    for name,acts in policies.items():
        summaries.append({'policy':name,'actions':sum(acts),'misses':sum(r['y']*(1-x) for r,x in zip(rows,acts)), 'realized_cost':float(cost(rows,acts)), 'input_forecast_expected_cost':float(cost(rows,acts,expected=True)),'deployable_comparator':name!='outcome_oracle'})
    # Every distinct rule p>t on t in [0,1] is represented by these breakpoints.
    thresholds=sorted({F(0),F(1)}|{r['p'] for r in rows})
    threshold_results=[{'threshold':float(t),'exact':str(t),'realized_cost':float(cost(rows,[int(r['p']>t) for r in rows]))} for t in thresholds]
    best=min(x['realized_cost'] for x in threshold_results)
    eps=exact_zero(rows,a,b)
    outcomes=[]
    for ys in product([0,1],repeat=len(rows)):
        g=gain(rows,a,b,ys)
        outcomes.append((g,ys,sum(y!=r['y'] for y,r in zip(ys,rows))))
    losing=min((x for x in outcomes if x[0]<0),key=lambda x:(x[2],x[0],x[1]))
    exhaustive={'assignments':len(outcomes),'gain_min':float(min(x[0] for x in outcomes)),'gain_max':float(max(x[0] for x in outcomes)),'cost_rule_lower':sum(x[0]>0 for x in outcomes),'equal':sum(x[0]==0 for x in outcomes),'cost_rule_higher':sum(x[0]<0 for x in outcomes),'min_outcome_flips_to_reverse':losing[2],'nearest_counterexample':{'outcomes':list(losing[1]),'flipped_cases':[r['id'] for r,y in zip(rows,losing[1]) if y!=r['y']],'cost_rule':float(cost(rows,a,losing[1])),'probability_0.5':float(cost(rows,b,losing[1])),'gain':float(losing[0])},'interpretation':'Combinatorial counts, not empirical or forecast probabilities.'}
    sensitivities=[{'epsilon':float(e),'exact':str(e),'lower_expected_gain':float(lower_gain(rows,a,b,e))} for e in [F(0),F(1,20),F(1,10),eps,F(3,20),F(1,5),F(3,10),F(1)]]
    witness=adverse_q(rows,a,b,eps)
    # One runnable check: independent corner enumeration, exact identities, ties.
    assert a==bayes and cost(rows,a)==222 and cost(rows,b)==440 and best==292
    assert cost(rows,oracle)==172 and cost(rows,a,expected=True)==272
    assert gain(rows,a,b,[r['p'] for r in rows])==F(169,2)
    assert eps==F(149,1080) and lower_gain(rows,a,b,eps)==0
    for e in [F(0),F(1,10),eps,F(1,5),F(1)]:
        corners=product(*[(max(F(0),r['p']-e),min(F(1),r['p']+e)) for r in rows])
        assert min(gain(rows,a,b,q) for q in corners)==lower_gain(rows,a,b,e)
    assert int(F('0.5')>F('0.5'))==0 and int(F('0.2')*100>20)==0
    assert sum(exhaustive[k] for k in ['cost_rule_lower','equal','cost_rule_higher'])==4096
    assert exhaustive['gain_min']==-102 and exhaustive['gain_max']==538 and losing[2]==3
    (OUT/'input-snapshot').mkdir(exist_ok=True)
    for p in INPUT.iterdir():
        if p.is_file():shutil.copyfile(p,OUT/'input-snapshot'/p.name)
    detailed=[]
    for r,x,z,q in zip(rows,a,b,witness):
        detailed.append({'case':r['id'],'probability':float(r['p']),'action_cost':float(r['c']),'miss_loss':float(r['L']),'outcome':r['y'],'score':float(r['p']*r['L']-r['c']),'cost_loss_threshold':float(r['c']/r['L']),'cost_rule_action':x,'probability_0.5_action':z,'cost_rule_realized_cost':float(x*r['c']+(1-x)*r['y']*r['L']),'probability_0.5_realized_cost':float(z*r['c']+(1-z)*r['y']*r['L']),'gain':float((z-x)*(r['c']-r['y']*r['L'])),'adversarial_q_at_epsilon_star':float(q),'adversarial_q_exact':str(q)})
    for name,data in [('case_results.csv',detailed),('policy_results.csv',summaries),('threshold_results.csv',threshold_results),('sensitivity_results.csv',sensitivities)]:
        with (OUT/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    result={'design':'Fixed synthetic packet; all cases equally weighted; no sampling inference','n':len(rows),'event_count':sum(r['y'] for r in rows),'policies':summaries,'best_global_threshold_cost':best,'best_thresholds':[x for x in threshold_results if x['realized_cost']==best],'fixed_baseline_gain':218,'fixed_baseline_reduction_percent':100*218/440,'best_threshold_gain':70,'best_threshold_reduction_percent':100*70/292,'input_forecast_expected_gain':rational(F(169,2)),'sharp_uniform_probability_error_radius':rational(eps),'exhaustive_outcomes':exhaustive,'uncertainty_model':'Per-case marginal q within [max(0,p-eps),min(1,p+eps)], fixed policies and costs; not aggregate calibration','self_check':'passed: exact accounting, input hashes, all threshold rules, five box-corner searches, 4096 outcome vectors, strict ties','python_version':sys.version,'input_sha256':manifest,'analysis_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    table='| Policy | Actions | Misses | Realized cost | Expected cost under input p |\n|---|---:|---:|---:|---:|\n'+'\n'.join('| {policy} | {actions} | {misses} | {realized_cost:g} | {input_forecast_expected_cost:g} |'.format(**r) for r in summaries)
    (OUT/'results-tables.md').write_text(table+'\n\nBest outcome-selected common threshold: cost 292, t in [0.10,0.15). Outcome selection is an optimistic diagnostic, not held-out validation.\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
