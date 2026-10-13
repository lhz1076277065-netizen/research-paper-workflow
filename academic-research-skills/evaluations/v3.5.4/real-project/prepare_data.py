"""Whole-table preparation; no model fitting and no fitted preprocessing."""
import csv,json,pathlib,platform
import numpy as np
R=pathlib.Path(__file__).resolve().parent
D=R/'derived';D.mkdir(exist_ok=True)
spec=json.loads((R/'dataset-spec-v2.json').read_text())
qa={};splits=[];stats=[]
for item in spec['datasets']:
    name=item['id'];f=item['files'][0]
    rows=[row for row in csv.reader((R/f['path']).open()) if row]
    assert len(rows)==f['expected_rows'] and all(len(row)==len(f['columns']) for row in rows)
    assert not any(not v.strip() for row in rows for v in row)
    names=f['columns'];target=names.index('class');features=[i for i in range(len(names)) if i!=target]
    x=np.array([[float(row[i]) for i in features] for row in rows]);labels=np.array([row[target] for row in rows])
    assert np.isfinite(x).all()
    categories=sorted(set(labels));y=np.array([categories.index(v) for v in labels])
    with (D/f'{name}.csv').open('w',newline='') as h:
        w=csv.writer(h);w.writerow(names);w.writerows(rows)
    duplicate_excess=len(x)-len(np.unique(x,axis=0))
    qa[name]={'rows':len(x),'features':len(features),'class_counts':{c:int(sum(labels==c)) for c in categories},'feature_duplicate_excess':int(duplicate_excess),'missing_cells':0,'nonfinite_features':0,'raw_changed':False,'rows_removed':0,'row_order_preserved':True,'target_column':target,'feature_units':('cm for all 4 columns' if name=='iris' else 'Dictionary names verified; not all constituent units supplied, so treated in source numeric units'),'independent_unit_count':'unknown: no source subject/site identifiers available'}
    for j,i in enumerate(features):
        a=x[:,j];q1,median,q3=np.quantile(a,[.25,.5,.75]);mad=np.median(abs(a-median))
        stats.append({'dataset':name,'feature':names[i],'min':float(a.min()),'max':float(a.max()),'mean':float(a.mean()),'sd':float(a.std(ddof=1)),'median':float(median),'iqr':float(q3-q1),'mad':float(mad),'iqr_flag_count':int(((a<q1-1.5*(q3-q1))|(a>q3+1.5*(q3-q1))).sum())})
    for fraction in (.2,.3):
        for seed in range(30):
            rng=np.random.default_rng(seed);tr=[];te=[]
            for c in range(3):
                idx=np.flatnonzero(y==c);idx=rng.permutation(idx);n=max(1,round(fraction*len(idx)))
                te.extend(idx[:n].tolist());tr.extend(idx[n:].tolist())
            assert not(set(tr)&set(te)) and sorted(tr+te)==list(range(len(x)))
            dup_overlap=len(set(map(tuple,x[tr]))&set(map(tuple,x[te])))
            splits.append({'dataset':name,'test_fraction':fraction,'seed':seed,'train':tr,'test':te,'duplicate_feature_vectors_across_split':dup_overlap})
(D/'splits.json').write_text(json.dumps(splits,indent=2))
with (D/'feature-summary.csv').open('w',newline='') as h:
    w=csv.DictWriter(h,fieldnames=list(stats[0]));w.writeheader();w.writerows(stats)
(D/'quality.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'datasets':qa,'split_count':len(splits),'train_test_index_overlap':False,'split_before_learned_preprocessing':True,'all_raw_rows_preserved':True,'max_duplicate_vector_overlap':max(s['duplicate_feature_vectors_across_split'] for s in splits),'no_model_fitted':True},indent=2))
print(json.dumps(qa,indent=2))
