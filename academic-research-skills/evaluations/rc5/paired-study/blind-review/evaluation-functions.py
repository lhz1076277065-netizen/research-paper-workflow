import statistics
import numpy as np

def median_window(x,p):
    """Known robust rolling median; no originality claim or nominal error guarantee."""
    prefix=[v for v in x[:64] if v is not None]
    mu=statistics.median(prefix); scale=max(.25,1.4826*statistics.median(abs(v-mu) for v in prefix))
    for t in range(64,len(x)):
        if x[t] is None:continue
        block=[(v-mu)/scale for v in x[max(64,t-p['window']+1):t+1] if v is not None]
        if len(block)>=max(8,int(.6*p['window'])) and abs(statistics.median(block))*len(block)**.5>p['threshold']:
            return t
    return -1

def paired(a,b):
    assert [r['id'] for r in a['rows']]==[r['id'] for r in b['rows']]
    differences=np.array([x['loss']-y['loss'] for x,y in zip(a['rows'],b['rows'])],dtype=float)
    rng=np.random.default_rng(50973)
    samples=rng.choice(differences,size=(2000,len(differences)),replace=True).mean(axis=1)
    return {'mean_loss_reduction':float(differences.mean()),'bootstrap_95_percentile':np.quantile(samples,[.025,.975]).tolist(),
            'improved_cases':int((differences>0).sum()),'worsened_cases':int((differences<0).sum()),
            'tied_cases':int((differences==0).sum()),'n':len(differences),
            'scope':'Paired independent synthetic streams; exploratory percentile interval, fixed loss and selected development configs.'}
