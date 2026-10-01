"""Seeded digital objects; post-freeze holdout uses disjoint random seeds."""
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

def generate(seed,n_each):
    rng=np.random.default_rng(seed); cases=[]
    for condition in ['clean','bursts','gaps','heavy']:
        for i in range(n_each):
            tau=int(rng.integers(140,211)) if i%2 else None
            x=rng.normal(0,1,360) if condition!='heavy' else rng.standard_t(4,360)/np.sqrt(2)
            if tau is not None: x[tau:]+=rng.choice([-1.,1.])*rng.choice([.65,1.,1.4])
            if condition in ['bursts','gaps','heavy']:
                for _ in range(3):
                    at=int(rng.integers(70,330)); length=int(rng.integers(1,7))
                    x[at:at+length]+=rng.choice([-1.,1.])*rng.uniform(5,10)
            if condition=='gaps':
                for _ in range(3):
                    at=int(rng.integers(70,330)); x[at:at+int(rng.integers(4,21))]=np.nan
            cases.append({'id':f'{seed}-{condition}-{i}','condition':condition,'tau':tau,
                          'x':[float(v) if np.isfinite(v) else None for v in x]})
    return cases

if __name__=='__main__':
    (HERE/'data').mkdir(exist_ok=True)
    for split,seed,n in [('train',51321,10),('dev',65109,30)]:
        (HERE/'data'/(split+'.json')).write_text(json.dumps(generate(seed,n),separators=(',',':'))+'\n')
