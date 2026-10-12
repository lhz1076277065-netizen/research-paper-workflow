"""Executed sensitivity and independent closed-form checks; two test clusters only."""
from pathlib import Path
import numpy as np
import json,csv,itertools,hashlib,time,subprocess,sys,os
import calibration as cal
ROOT=Path(__file__).resolve().parent
start=time.perf_counter()
rows,x,y,batch,tr=cal.load();te=~tr
main=json.loads((ROOT/'results/results.json').read_text());beta={k:np.array(v) for k,v in main['parameters'].items()}
yp={k:cal.predict(v,x[te]) for k,v in beta.items()};yb=y[te];tb=batch[te];groups=np.unique(tb)
assert len(groups)==2
bybatch=[]
for b in groups:
 idx=tb==b;bybatch.append({'batch':b,'setting':'shared batch' if b in set(batch[tr]) else 'unseen batch','n':int(idx.sum()),**{k:cal.metrics(p[idx],yb[idx]) for k,p in yp.items()},'delta_rmse':cal.metrics(yp['offset'][idx],yb[idx])['rmse']-cal.metrics(yp['affine'][idx],yb[idx])['rmse']})
def delta_for(gsample):
 ids=np.concatenate([np.flatnonzero(tb==g) for g in gsample])
 return cal.metrics(yp['offset'][ids],yb[ids])['rmse']-cal.metrics(yp['affine'][ids],yb[ids])['rmse']
exact_boot=[delta_for(g) for g in itertools.product(groups,repeat=len(groups))]
rng=np.random.default_rng(20261012);bootstrap=np.array([delta_for(rng.choice(groups,len(groups),replace=True)) for _ in range(10000)])
lossdiff=np.array([np.mean((yp['offset'][tb==g]-yb[tb==g])**2-(yp['affine'][tb==g]-yb[tb==g])**2) for g in groups]);stat=np.mean(lossdiff)
signed=np.array([np.mean(np.array(s)*lossdiff) for s in itertools.product([-1,1],repeat=len(groups))]);p=float(np.mean(np.abs(signed)>=abs(stat)-1e-14))
median=cal.fit(x[tr],y[tr],'median');medmetrics=cal.metrics(cal.predict(median,x[te]),yb)
cut=np.median(y[tr]);strata=[]
for name,mask in [('low',yb<=cut),('high',yb>cut)]:
 strata.append({'stratum':name,'train_reference_cut':float(cut),**{k:cal.metrics(v[mask],yb[mask]) for k,v in yp.items()}})
# Only training observations are eligible for influence refits.
trainids=np.flatnonzero(tr);maxid=trainids[np.argmax(abs(cal.predict(beta['offset'],x[tr])-y[tr]))];keep=tr.copy();keep[maxid]=False
influence={k:cal.metrics(cal.predict(cal.fit(x[keep],y[keep],k),x[te]),yb) for k in ['offset','affine']}
# Independent OLS formula uses no linalg.lstsq and verifies all predictions.
xt=x[tr];yt=y[tr];slope=sum((xt-np.mean(xt))*(yt-np.mean(yt)))/sum((xt-np.mean(xt))**2);intercept=np.mean(yt)-slope*np.mean(xt)
closed=np.array([intercept,slope]);diff=float(np.max(np.abs(closed-beta['affine'])));assert diff<1e-12
probe=np.arange(5,dtype=float)
assert np.allclose(cal.fit(probe,3+2*probe,'affine'),[3,2]);assert np.allclose(cal.fit(probe,probe+1.5,'offset'),[1.5,1])
try:cal.fit(np.ones(4),np.arange(4.),'affine');raise AssertionError('constant input not rejected')
except ValueError:pass
# Actual complete deterministic rerun to a new project-local folder.
proc=subprocess.run([sys.executable,str(ROOT/'calibration.py'),'--output-dir','rerun'],cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
(ROOT/'rerun.log').write_text(proc.stdout+proc.stderr);assert proc.returncode==0
names=['results.json','model-lock.json','primary-metrics.csv','cv-metrics.csv','test-predictions.csv'];hashes={}
for n in names:
 a=hashlib.sha256((ROOT/'results'/n).read_bytes()).hexdigest();b=hashlib.sha256((ROOT/'rerun'/n).read_bytes()).hexdigest();assert a==b;hashes[n]={'initial':a,'rerun':b,'identical':True}
result={'evidence_id':'ER-20261012-robustness-01','actual_train_clusters':int(len(np.unique(batch[tr]))),'actual_test_clusters':len(groups),'by_batch':bybatch,'two_cluster_bootstrap_10000_descriptive_percentiles':np.quantile(bootstrap,[.025,.975]).tolist(),'two_cluster_exact_resample_deltas':exact_boot,'bootstrap_scope':'conditional on frozen parameters; only two clusters; not reliable population CI or equivalence evidence','sign_flip_descriptive_p':p,'sign_flip_arrangements':len(signed),'permutation_scope':'nonrandomized paired loss-sign diagnostic only; exchangeability not established','median_offset_parameter':median.tolist(),'median_offset_test':medmetrics,'strata':strata,'influence_deleted_train_source_row':int(maxid+2),'influence':influence,'closed_form_affine':closed.tolist(),'closed_form_max_coefficient_difference':diff,'toy_and_degeneracy_checks':'passed','rerun_hashes':hashes,'extra_sensitivity_fits':3,'primary_model_selection_unchanged':main['selection'],'elapsed_seconds':time.perf_counter()-start}
cal.dump(ROOT/'robustness-results.json',result);print(json.dumps(result,ensure_ascii=False))
