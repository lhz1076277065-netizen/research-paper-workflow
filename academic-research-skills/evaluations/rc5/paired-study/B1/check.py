"""Correctness checks only; no tuning or validation configuration search."""
import json
import math
import sys
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import harness
from methods import _calibrate, detect_initial, detect_refined


def brute_refined(x,p):
    calibration=_calibrate(x)
    if calibration is None: return -1
    mu,scale=calibration
    w,b=p['window'],p['burst']
    for t in range(63+w,len(x)):
        if x[t] is None: continue
        a=[None if v is None else max(-p['clip'],min(p['clip'],(v-mu)/scale)) for v in x[t-w+1:t+1]]
        if sum(v is not None for v in a)<math.ceil(p['coverage']*w): continue
        for sign in (1,-1):
            values=[]
            for j in range(w-b+1):
                retained=[v for v in a[:j]+a[j+b:] if v is not None]
                values.append(sign*sum(retained)/math.sqrt(len(retained)) if len(retained)>=math.ceil(p['coverage']*(w-b)) else -math.inf)
            if min(values)>p['threshold']: return t
    return -1


def main():
    start=time.perf_counter(); p=json.loads((HERE/'frozen.json').read_text()); checks=[]
    for fn in (detect_initial,detect_refined):
        q=p['initial' if fn is detect_initial else 'refined']
        assert fn([],q)==-1 and fn([0.]*63,q)==-1
        assert fn([None]*360,q)==-1 and fn([0.]*360,q)==-1
    checks.append('short-prefix, empty-calibration, zero-signal')
    known=[]
    for sign in (1,-1):
        for onset in (64,91,150):
            x=[0.]*360; x[onset:onset+p['refined']['burst']]=[sign*1e9]*p['refined']['burst']
            assert detect_refined(x,p['refined'])==-1
            known.append({'kind':'bounded isolated burst','sign':sign,'onset':onset,'alarm':-1})
        x=[0.]*96+[sign*.25]*264
        alarms={name:fn(x,p[name]) for name,fn in [('baseline',harness.baseline),('initial',detect_initial),('refined',detect_refined)]}
        assert alarms['refined']==114, alarms
        known.append({'kind':'sustained unit-z shift','sign':sign,'onset':96,'alarms':alarms})
    for sign in (1,-1):
        x=[0.]*96+[sign*.175]*264  # calibrated delta=.7, below 3/sqrt(18)
        alarms={name:fn(x,p[name]) for name,fn in [('baseline',harness.baseline),('initial',detect_initial),('refined',detect_refined)]}
        assert alarms['refined']==-1 and alarms['baseline']==156 and alarms['initial']==136, alarms
        known.append({'kind':'weak sustained shift below excision boundary','sign':sign,'onset':96,'calibrated_delta':.7,'alarms':alarms})
    x=[0.]*64+[.0625]*296; x[150:156]=[1000.]*6
    assert detect_refined(x,p['refined'])==-1
    assert detect_refined(x,p['ablation'])>=150
    known.append({'kind':'small baseline bias plus six-step burst','refined':-1,'ablation':detect_refined(x,p['ablation'])})
    x=[0.]*96+[.25]*6+[None]*30+[.25]*6+[0.]*222
    assert detect_refined(x,p['refined'])==-1
    known.append({'kind':'separated sub-bursts with missing run','refined':-1})
    checks.append('two signs; bounded bursts; exact sustained-shift alarm; burst ablation; missing-run expiration')
    train=json.loads((HERE.parent/'data'/'train.json').read_text())
    prefix_calls=0
    for case in train:
        for name,fn in [('initial',detect_initial),('refined',detect_refined)]:
            full=fn(case['x'],p[name])
            for length in range(len(case['x'])+1):
                result=fn(case['x'][:length],p[name]); expected=full if 0<=full<length else -1
                assert result==expected,(case['id'],name,length,result,expected)
                prefix_calls+=1
    checks.append('every prefix of all 40 training streams for both submitted detectors')
    dev=json.loads((HERE.parent/'data'/'dev.json').read_text())
    for case in dev:
        assert brute_refined(case['x'],p['refined'])==detect_refined(case['x'],p['refined']),(case['id'],'oracle mismatch')
    checks.append('independent direct-excision oracle matches all 120 development alarms')
    result={'status':'passed','checks':checks,'prefix_calls':prefix_calls,'oracle_cases':len(dev),'known_cases':known,'elapsed_seconds':time.perf_counter()-start,'scope':'Implementation/causality checks, not holdout validation or an average-run-length theorem.'}
    (HERE/'check-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
