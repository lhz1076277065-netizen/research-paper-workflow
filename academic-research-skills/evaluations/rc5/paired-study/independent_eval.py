"""Independent, post-freeze evaluation with common holdout and a known comparator."""
import hashlib, importlib.util, json, statistics, time
from pathlib import Path
import numpy as np
from generate import generate
from harness import baseline, evaluate, score

HERE=Path(__file__).resolve().parent
PARTICIPANTS=('A1','B1','B2','A2')

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


def main():
    out=HERE/'independent';out.mkdir(exist_ok=True)
    # Missing submissions stop before any holdout is generated.
    frozen={}
    for name in PARTICIPANTS:
        folder=HERE/name
        for filename in ['methods.py','frozen.json','research.md','usage.json']:
            if not (folder/filename).is_file():raise ValueError('Incomplete submission: '+name+'/'+filename)
        frozen[name]={str(p.relative_to(folder)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
    (out/'frozen-submissions.json').write_text(json.dumps(frozen,indent=2)+'\n')
    if (out/'holdout.json').exists():raise ValueError('Use preserved reports; do not silently repeat or retune a holdout')
    data=generate(104927,60)+generate(838651,60)
    (out/'holdout.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    # 16 same-data development configurations for one common known comparator.
    choices=[]
    for w in (16,24,36,48):
        for threshold in (2.5,3.,3.5,4.):
            p={'window':w,'threshold':threshold};r=score(median_window,p,HERE/'data/dev.json',out/'median-development',f'w{w}-t{threshold}')
            choices.append(r)
    chosen=min(choices,key=lambda r:r['mean_loss']);common=evaluate(median_window,chosen['params'],data)
    (out/'common-median.json').write_text(json.dumps(common,indent=2)+'\n')
    summary={'holdout_cases':len(data),'holdout_sha256':hashlib.sha256((out/'holdout.json').read_bytes()).hexdigest(),
             'common_median_params':chosen['params'],'common_median_mean_loss':common['mean_loss'],
             'participants':{},'post_holdout_tuning':False,'scientific_or_publication_novelty_certified':False}
    for name in PARTICIPANTS:
        folder=HERE/name;spec=importlib.util.spec_from_file_location('study_'+name,folder/'methods.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        config=json.loads((folder/'frozen.json').read_text())
        functions={'baseline':baseline,'initial':module.detect_initial,'refined':module.detect_refined,
                   'ablation':getattr(module,config.get('ablation_function','detect_refined'))}
        functions.update({extra:module.detect_refined for extra in ('ablation_comparator','secondary_ablation') if extra in config})
        reports={};causal=0
        for method,fn in functions.items():
            if method not in config:continue
            r=evaluate(fn,config[method],data);reports[method]=r
            for case,row in zip(data,r['rows']):
                # Fixed checkpoints plus every alarm boundary; code review checks the causal loop.
                lengths={64,65,96,128,192,256,320,len(case['x'])}
                if row['alarm']>=64:lengths.update({row['alarm'],row['alarm']+1,min(len(case['x']),row['alarm']+2)})
                for length in sorted(lengths):
                    actual=fn(case['x'][:length],dict(config[method]))
                    expected=row['alarm'] if 0<=row['alarm']<length else -1
                    if actual!=expected:raise AssertionError((name,method,case['id'],length,actual,expected))
                    causal+=1
            (out/(name+'-'+method+'.json')).write_text(json.dumps(r,indent=2)+'\n')
        entry={k:{a:b for a,b in r.items() if a!='rows'} for k,r in reports.items()}
        entry['baseline_to_refined']=paired(reports['baseline'],reports['refined'])
        entry['initial_to_refined']=paired(reports['initial'],reports['refined'])
        entry['median_to_refined']=paired(common,reports['refined'])
        if 'ablation' in reports:
            entry['ablation_to_refined']=paired(reports['ablation'],reports['refined'])
            entry['ablation_parameter_differences']={k:[config['ablation'].get(k),config['refined'].get(k)] for k in set(config['ablation'])|set(config['refined']) if config['ablation'].get(k)!=config['refined'].get(k)}
        if 'ablation_comparator' in reports:entry['matched_ablation_to_refined_variant']=paired(reports['ablation'],reports['ablation_comparator'])
        entry['causal_prefix_checks']=causal
        summary['participants'][name]=entry
        print(json.dumps({'participant':name,'loss':{k:r['mean_loss'] for k,r in reports.items()},'causal_prefix_checks':causal}),flush=True)
    for name,digests in frozen.items():
        for rel,digest in digests.items():
            if hashlib.sha256((HERE/name/rel).read_bytes()).hexdigest()!=digest:raise AssertionError('Submission changed after freeze: '+name+'/'+rel)
    (out/'evaluation.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'holdout_cases':len(data),'common_median_mean_loss':common['mean_loss'],'post_freeze_digests_unchanged':True}))

if __name__=='__main__':main()
