"""Transparent fixed classifiers; learned scaling uses training records only."""
import argparse,csv,json,pathlib,platform,time,resource
import numpy as np
R=pathlib.Path(__file__).resolve().parent
ARMS=('majority','centroid_raw','centroid_scaled','knn5_raw','knn5_scaled')

def read_data(name):
    rows=list(csv.DictReader((R/'derived'/f'{name}.csv').open()))
    features=[k for k in rows[0] if k!='class'];classes=sorted({r['class'] for r in rows})
    x=np.array([[float(r[f]) for f in features] for r in rows])
    y=np.array([classes.index(r['class']) for r in rows])
    return x,y,classes

def classify(x,y,tr,te,arm):
    a=x[tr].copy();b=x[te].copy();yy=y[tr]
    mu=a.mean(0);scale=a.std(0,ddof=0);scale=np.where(scale==0,1.,scale)
    if arm.endswith('_scaled'):a=(a-mu)/scale;b=(b-mu)/scale
    if arm=='majority':pred=np.repeat(np.bincount(yy,minlength=3).argmax(),len(te))
    elif arm.startswith('centroid'):
        centers=np.vstack([a[yy==c].mean(0) for c in range(3)])
        pred=((b[:,None,:]-centers[None,:,:])**2).sum(2).argmin(1)
    else:
        distances=((b[:,None,:]-a[None,:,:])**2).sum(2)
        neighbors=np.array([np.lexsort((np.array(tr),row))[:5] for row in distances])
        pred=np.array([np.bincount(yy[ids],minlength=3).argmax() for ids in neighbors])
    return pred,mu,scale

def metric(y,p):
    confusion=np.zeros((3,3),dtype=int)
    np.add.at(confusion,(y,p),1)
    assert np.all(confusion.sum(1)>0)
    return float(np.mean(np.diag(confusion)/confusion.sum(1))),float(np.mean(y==p)),confusion

def selfcheck():
    x=np.repeat(np.array([[0.],[10.],[20.]]),5,axis=0);y=np.repeat(np.arange(3),5)
    for arm in ARMS[1:]:
        p,_,_=classify(x,y,list(range(15)),[0,5,10],arm);assert p.tolist()==[0,1,2]
    ba,acc,cm=metric(np.array([0,0,1,1,2,2]),np.array([0,1,1,1,0,2]))
    assert abs(ba-2/3)<1e-15 and abs(acc-2/3)<1e-15

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--fraction',type=float,default=.2);p.add_argument('--pilot',action='store_true');a=p.parse_args()
    out=R/a.out;out.mkdir(parents=True,exist_ok=False)
    selfcheck();start=time.perf_counter()
    parts=[s for s in json.loads((R/'derived'/'splits.json').read_text()) if s['test_fraction']==a.fraction and (not a.pilot or s['seed']==0)]
    predictions=[];results=[];params=[]
    for s in parts:
        x,y,classes=read_data(s['dataset']);tr=s['train'];te=s['test']
        assert not set(tr)&set(te)
        for arm in ARMS:
            pred,mu,scale=classify(x,y,tr,te,arm)
            assert np.array_equal(mu,x[tr].mean(0))
            ba,acc,cm=metric(y[te],pred)
            results.append({'dataset':s['dataset'],'test_fraction':a.fraction,'seed':s['seed'],'arm':arm,'n_train':len(tr),'n_test':len(te),'balanced_accuracy':ba,'accuracy':acc,**{f'cm_{i}{j}':int(cm[i,j]) for i in range(3) for j in range(3)}})
            for idx,guess in zip(te,pred):predictions.append({'dataset':s['dataset'],'test_fraction':a.fraction,'seed':s['seed'],'arm':arm,'row_id':idx,'truth':int(y[idx]),'prediction':int(guess)})
            if arm=='knn5_scaled':params.append({'dataset':s['dataset'],'test_fraction':a.fraction,'seed':s['seed'],'fit_row_ids':tr,'training_mean':mu.tolist(),'training_population_sd_zero_to_one':scale.tolist()})
    for n,rows in [('results',results),('predictions',predictions)]:
        with (out/(n+'.csv')).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'scaler-parameters.json').write_text(json.dumps(params,indent=2))
    summary=[];effects=[]
    for name in ('wine','iris'):
        for arm in ARMS:
            rows=[r for r in results if r['dataset']==name and r['arm']==arm];v=np.array([r['balanced_accuracy'] for r in rows]);acc=np.array([r['accuracy'] for r in rows])
            summary.append({'dataset':name,'test_fraction':a.fraction,'arm':arm,'partitions':len(v),'balanced_accuracy_mean':float(v.mean()),'balanced_accuracy_sd':float(v.std(ddof=1)) if len(v)>1 else None,'balanced_accuracy_min':float(v.min()),'balanced_accuracy_max':float(v.max()),'accuracy_mean':float(acc.mean())})
        for family in ('centroid','knn5'):
            raw=[r['balanced_accuracy'] for r in results if r['dataset']==name and r['arm']==family+'_raw'];scaled=[r['balanced_accuracy'] for r in results if r['dataset']==name and r['arm']==family+'_scaled'];v=np.array(scaled)-np.array(raw)
            effects.append({'dataset':name,'family':family,'test_fraction':a.fraction,'paired_difference_mean':float(v.mean()),'paired_difference_sd':float(v.std(ddof=1)) if len(v)>1 else None,'min':float(v.min()),'max':float(v.max()),'positive_splits':int(sum(v>0)),'zero_splits':int(sum(v==0)),'negative_splits':int(sum(v<0))})
    (out/'summary.json').write_text(json.dumps({'descriptive_only':True,'partitions_are_dependent':True,'summary':summary,'effects':effects},indent=2))
    timing={'python':platform.python_version(),'numpy':np.__version__,'fits':len(results),'prediction_rows':len(predictions),'elapsed_seconds':time.perf_counter()-start,'max_rss':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'max_rss_unit':'bytes on this macOS host','implementation_sanity_passed':True,'all_scaler_means_from_training':True,'pilot':a.pilot,'fraction':a.fraction}
    (out/'runtime.json').write_text(json.dumps(timing,indent=2));print(json.dumps(timing))
if __name__=='__main__':main()
