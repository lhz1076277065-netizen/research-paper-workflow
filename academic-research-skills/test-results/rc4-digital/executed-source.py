#!/usr/bin/env python3
"""Real digital development examples, not evidence of research novelty.

Requires NumPy and a C compiler. Uses the official UCI archive, a deterministic
group split, an elementary proof and independently checked integer optimization.
Run in a new output directory; --archive permits replay of the frozen download.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import random
import shutil
import sys
import time
import urllib.request
import zipfile

URL = 'https://archive.ics.uci.edu/static/public/186/wine+quality.zip'
PAGE = 'https://archive.ics.uci.edu/dataset/186/wine+quality'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)+'\n')

def download(url, path):
    with urllib.request.urlopen(url, timeout=45) as response:
        body = response.read(5_000_001)
        if len(body) > 5_000_000:
            raise ValueError('Unexpected download size')
        path.write_bytes(body)
        return {'url':url, 'resolved_url':response.url, 'sha256':sha(path),
                'bytes':len(body), 'retrieved_at':datetime.now(timezone.utc).isoformat()}

def public_data(out, archive):
    import numpy as np
    raw=out/'wine-quality.zip'
    if archive:
        shutil.copyfile(archive, raw)
        receipt={'url':URL, 'sha256':sha(raw), 'access':'frozen replay'}
    else:
        receipt=download(URL, raw)
    page=out/'uci-source.html'
    source=download(PAGE, page)
    assert 'CC BY 4.0' in page.read_text() or 'Creative Commons Attribution 4.0' in page.read_text()
    with zipfile.ZipFile(raw) as z:
        rows=list(csv.DictReader(io.StringIO(z.read('winequality-white.csv').decode()), delimiter=';'))
        dictionary=z.read('winequality.names').decode()
    (out/'variable-dictionary.txt').write_text(dictionary)
    assert len(rows)==4898 and len(rows[0])==12
    fields=list(rows[0]);features=[x for x in fields if x!='quality']
    x=np.array([[float(r[k]) for k in features] for r in rows]);y=np.array([float(r['quality']) for r in rows])
    assert np.isfinite(x).all() and np.isfinite(y).all() and ((y>=0)&(y<=10)).all()
    # No bottle/cohort ID was supplied: identical predictor vectors form a
    # conservative dependency group. This does not establish source independence.
    keys=[hashlib.sha256(json.dumps([r[k] for k in features]).encode()).hexdigest() for r in rows]
    buckets=np.array([int(k[:8],16)%10 for k in keys]);train=buckets<6;validation=(buckets>=6)&(buckets<8);test=buckets>=8
    assert not (set(np.array(keys)[train])&set(np.array(keys)[test]))
    center=x[train].mean(axis=0);scale=x[train].std(axis=0);scale[scale==0]=1
    z=np.column_stack([np.ones(len(x)), (x-center)/scale])
    penalty=np.eye(z.shape[1]);penalty[0,0]=0
    coefficients=np.linalg.solve(z[train].T@z[train]+penalty,z[train].T@y[train])
    predict=z@coefficients;baseline=np.full(len(y),y[train].mean())
    rmse=lambda pred,mask:float(np.sqrt(np.mean((pred[mask]-y[mask])**2)))
    results={'material':'actual public observations; digital reanalysis', 'rows':len(rows),
       'variables':fields, 'missing':int((~np.isfinite(x)).sum()),
       'duplicate_predictor_rows':len(rows)-len(set(keys)),
       'split':{'train':int(train.sum()),'validation':int(validation.sum()),'test':int(test.sum()),'key':'SHA256 of predictor tuple modulo 10'},
       'preprocessing':'training mean/standard deviation only', 'ridge_alpha':1.0,
       'validation_rmse':rmse(predict,validation), 'test_rmse':rmse(predict,test),
       'baseline_test_rmse':rmse(baseline,test), 'unit':'quality score points',
       'limits':['No sampling date or bottle ID supplied','One white-wine source; no external-source validation','Prespecified baseline implementation; no novel method claim'],
       'attribution':'Cortez et al. (2009), Wine Quality, UCI, DOI 10.24432/C56S3T; CC BY 4.0',
       'source':receipt, 'license_source':source, 'numpy_version':np.__version__}
    save(out/'public-results.json',results)
    with (out/'split.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['row','predictor_group','partition'])
        w.writerows((i,k,'train' if train[i] else 'validation' if validation[i] else 'test') for i,k in enumerate(keys))
    return results

def formal(out):
    proof='''For a > 0, minimize f(x)=a(x-t)^2 over 0 <= x <= 1.
The unique minimizer is p=min(1,max(0,t)). For every feasible x,
f(x)-f(p)=a(x-p)^2+2a(p-t)(x-p). If 0<=t<=1, p=t and the second
term vanishes. If t<0, p=0 and both factors p-t and x-p are nonnegative.
If t>1, p=1 and both factors are nonpositive. Thus the difference is
nonnegative, and a>0 makes it strictly positive when x!=p.
At a=0 every feasible point minimizes, so uniqueness fails. For a<0
the proposed projection can fail (t=1/2: endpoints beat p=1/2).
This is an elementary established result used to verify the tool chain,
not a new mathematical theorem. The algebra and sign argument constitute
the proof; the following finite computations only check implementation.
'''
    (out/'proof.md').write_text(proof)
    checks=[]
    for t in map(Fraction,['-1/4','0','3/8','1','5/4']):
        p=min(Fraction(1),max(Fraction(0),t))
        for x in [Fraction(i,16) for i in range(17)]:
            left=(x-t)**2-(p-t)**2;right=(x-p)**2+2*(p-t)*(x-p)
            assert left==right and left>=0
        checks.append({'t':str(t),'p':str(p),'rational_checks':17})
    assert -(Fraction(0)-Fraction(1,2))**2 < 0
    result={'kind':'formal derivation with rational implementation checks', 'condition':'a>0, x in [0,1]',
            'proof':'proof.md','proof_sha256':sha(out/'proof.md'),'cases':checks,'formal_proof_assistant_used':False}
    save(out/'formal-results.json',result);return result

C_SOURCE=r'''
#include <stdio.h>
int main(int argc, char **argv) {
  if(argc!=3) return 2;
  FILE *in=fopen(argv[1],"r"), *out=fopen(argv[2],"w");
  if(!in || !out) return 3;
  int n,capacity,w[20],v[20];
  if(fscanf(in,"%d%d",&n,&capacity)!=2 || n<1 || n>20 || capacity<0) return 4;
  for(int i=0;i<n;i++) if(fscanf(in,"%d%d",&w[i],&v[i])!=2 || w[i]<=0 || v[i]<0) return 5;
  int best=0;unsigned mask_best=0;
  /* ponytail: exponential search limited to 20 items; use branch-and-bound for larger instances. */
  for(unsigned mask=0;mask<(1u<<n);mask++) {
    int weight=0,value=0;
    for(int i=0;i<n;i++) if(mask&(1u<<i)) {weight+=w[i];value+=v[i];}
    if(weight<=capacity && value>best) {best=value;mask_best=mask;}
  }
  fprintf(out,"%d %u\n",best,mask_best); fclose(in);fclose(out);return 0;
}
'''

def optimization(out):
    src=out/'knapsack.c';src.write_text(C_SOURCE)
    compiler=shutil.which('clang') or shutil.which('cc')
    if not compiler:raise RuntimeError('A free C compiler is required for this acceptance chain')
    executable=out/'knapsack';receipts=[]
    helper=Path(__file__).resolve().parents[2]/'src/common/scripts/environment.py'
    spec=importlib.util.spec_from_file_location('acceptance_environment',helper)
    environment=importlib.util.module_from_spec(spec);spec.loader.exec_module(environment)
    task={'request':'Compile and solve finite generated knapsack instances',
          'runtime':{'backend':'host'},'executor':{'role':'executor','host':'current_host'}}
    def run(argv, outputs):
        receipt=environment.run_command(task,out,argv,[q.name for q in outputs],interpreter=sys.executable,timeout=30)
        if receipt.get('research_execution')!='passed':raise RuntimeError(str(receipt))
        execution=receipt['execution'];i=len(receipts)
        for stream in ['stdout','stderr']:
            log=out/f'tool-{i}.{stream}.log';shutil.copyfile(execution[stream],log);execution[stream]=log.name
        receipts.append({'execution':execution,'outputs':receipt['outputs']})
    run([compiler,'-O2',str(src),'-o',str(executable)],[executable])
    rng=random.Random(10427);cases=[]
    for case in range(4):
        items=[(rng.randint(1,16),rng.randint(2,30)) for _ in range(14)];capacity=40+case
        inp=out/f'knapsack-{case}.txt';target=out/f'knapsack-{case}.result'
        inp.write_text(f'{len(items)} {capacity}\n'+''.join(f'{w} {v}\n' for w,v in items))
        run([str(executable),str(inp),str(target)],[target])
        best,mask=map(int,target.read_text().split());chosen=[i for i in range(len(items)) if mask&(1<<i)]
        # Independent dynamic programming, not a transcription of the C enumeration.
        dp=[0]*(capacity+1)
        for w,v in items:
            for c in range(capacity,w-1,-1):dp[c]=max(dp[c],dp[c-w]+v)
        assert best==dp[capacity] and sum(items[i][0] for i in chosen)<=capacity
        assert sum(items[i][1] for i in chosen)==best
        left=capacity;greedy=0
        for w,v in sorted(items,key=lambda pair:pair[1]/pair[0],reverse=True):
            if w<=left:left-=w;greedy+=v
        cases.append({'case':case,'capacity':capacity,'optimal_value':best,'greedy_value':greedy,'selected':chosen,'independent_dp_verified':True})
    result={'kind':'constructed finite optimization; no novel algorithm claim','compiler':compiler,
            'source_sha256':sha(src),'cases':cases,'executions':receipts}
    save(out/'optimization-results.json',result);return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True);parser.add_argument('--archive')
    args=parser.parse_args();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=False)
    result={'public_data':public_data(out,args.archive),'formal':formal(out),'optimization':optimization(out),
            'python':sys.version,'code_sha256':sha(__file__),'scientific_novelty_evaluated':False}
    save(out/'acceptance.json',result)
    print(json.dumps({'out':str(out),'data_rows':result['public_data']['rows'],'test_rmse':result['public_data']['test_rmse'],
                      'formal_cases':len(result['formal']['cases']),'optimization_cases':len(result['optimization']['cases'])}))

if __name__=='__main__':main()
