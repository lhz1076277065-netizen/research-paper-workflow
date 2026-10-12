"""Frozen synthetic calibration demonstration; no test-driven model selection."""
import argparse,csv,json,hashlib,time,sys,resource
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
FITS=0
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def fit(x,y,kind):
 global FITS
 if kind=='raw':return np.array([0.,1.])
 FITS+=1
 if kind=='offset':return np.array([np.mean(y-x),1.])
 if kind=='median':return np.array([np.median(y-x),1.])
 if kind=='affine':
  if np.ptp(x)==0:raise ValueError('Affine slope not identifiable for constant sensor')
  return np.linalg.lstsq(np.column_stack([np.ones(len(x)),x]),y,rcond=None)[0]
 raise ValueError(kind)
def predict(beta,x):return beta[0]+beta[1]*x
def metrics(pred,y):
 e=pred-y
 return {'n':len(y),'rmse':float(np.sqrt(np.mean(e**2))),'mae':float(np.mean(np.abs(e))),'bias':float(np.mean(e))}
def writecsv(path,rows):
 with path.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def load():
 rows=list(csv.DictReader((ROOT/'measurements.csv').open()))
 return rows,np.array([float(r['sensor']) for r in rows]),np.array([float(r['reference']) for r in rows]),np.array([r['batch'] for r in rows]),np.array([r['split']=='train' for r in rows])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',default='results');args=ap.parse_args()
 out=(ROOT/args.output_dir).resolve();assert out==ROOT or ROOT in out.parents
 out.mkdir(parents=True,exist_ok=False)
 start=time.perf_counter();freeze=json.loads((ROOT/'analysis-freeze.json').read_text())
 assert hashlib.sha256((ROOT/'measurements.csv').read_bytes()).hexdigest()==freeze['csv_sha256']
 assert hashlib.sha256((ROOT/'analysis-plan.md').read_bytes()).hexdigest()==freeze['plan_sha256']
 rows,x,y,batch,tr=load();kinds=['raw','offset','affine'];groups=np.unique(batch[tr]);cv=[];cv_errors={k:[] for k in kinds}
 for g in groups:
  training=tr&(batch!=g);validation=tr&(batch==g)
  for kind in kinds:
   beta=fit(x[training],y[training],kind);p=predict(beta,x[validation]);m=metrics(p,y[validation]);cv.append({'held_batch':g,'model':kind,**m});cv_errors[kind].extend((p-y[validation]).tolist())
 cv_rmse={k:float(np.sqrt(np.mean(np.square(v)))) for k,v in cv_errors.items()};cv_gain=cv_rmse['offset']-cv_rmse['affine']
 selected='affine' if cv_gain>=freeze['threshold'] else 'offset'
 betas={k:fit(x[tr],y[tr],k) for k in kinds}
 dump(out/'model-lock.json',{'selection_from':'train-only leave-one-batch-out','threshold':freeze['threshold'],'cv_rmse':cv_rmse,'cv_gain':cv_gain,'selected':selected,'parameters':{k:v.tolist() for k,v in betas.items()},'test_used_in_selection':False})
 # Test assessment begins only after train-only model lock has been written.
 te=~tr;predictions={k:predict(v,x[te]) for k,v in betas.items()}
 primary=[{'model':k,**metrics(p,y[te])} for k,p in predictions.items()]
 test_rows=[]
 for i,idx in enumerate(np.flatnonzero(te)):
  test_rows.append({'source_row':int(idx+2),'batch':batch[idx],'reference':float(y[idx]),'sensor':float(x[idx]),**{k:float(v[i]) for k,v in predictions.items()}})
 train_summary={k:{'mean':float(np.mean(v)),'sd':float(np.std(v,ddof=1)),'median':float(np.median(v)),'iqr':float(np.quantile(v,.75)-np.quantile(v,.25)),'n':len(v)} for k,v in {'reference':y[tr],'sensor':x[tr],'raw_error':x[tr]-y[tr]}.items()}
 residual_diagnostics={k:{'train_residual_mean':float(np.mean(predict(v,x[tr])-y[tr])),'train_residual_sd':float(np.std(predict(v,x[tr])-y[tr],ddof=1)),'train_residual_reference_correlation':float(np.corrcoef(predict(v,x[tr])-y[tr],y[tr])[0,1]),'max_train_abs_residual':float(np.max(np.abs(predict(v,x[tr])-y[tr])))} for k,v in betas.items()}
 result={'evidence_id':'ER-20261012-frozen-calibration-01','data_sha256':freeze['csv_sha256'],'selection':selected,'cv_rmse':cv_rmse,'cv_gain':cv_gain,'parameters':{k:v.tolist() for k,v in betas.items()},'test_metrics':{r['model']:{k:v for k,v in r.items() if k!='model'} for r in primary},'test_delta_rmse':primary[1]['rmse']-primary[2]['rmse'],'train_descriptives':train_summary,'residual_diagnostics':residual_diagnostics,'fitted_model_count':FITS,'unit':'unspecified common attachment measurement unit','scope':'synthetic held-out readings in four existing batches','test_used_for_selection':False}
 dump(out/'results.json',result);writecsv(out/'primary-metrics.csv',primary);writecsv(out/'cv-metrics.csv',cv);writecsv(out/'test-predictions.csv',test_rows)
 dump(out/'cost.json',{'elapsed_seconds':time.perf_counter()-start,'maxrss_platform_units':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'platform':sys.platform,'python':sys.version,'numpy':np.__version__,'fits':FITS})
 print(json.dumps({'selected':selected,'cv_rmse':cv_rmse,'test_metrics':result['test_metrics'],'test_delta_rmse':result['test_delta_rmse'],'fits':FITS},ensure_ascii=False))
if __name__=='__main__':main()
