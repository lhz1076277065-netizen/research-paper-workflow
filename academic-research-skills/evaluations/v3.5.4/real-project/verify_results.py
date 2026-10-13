"""Independent metrics from saved predictions, raw/derived checks and replay identity."""
import csv,json,hashlib,pathlib,collections,math
R=pathlib.Path(__file__).resolve().parent
def digest(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
checked=0;largest=0.;files=[]
for sub in ['results','sensitivity']:
    groups=collections.defaultdict(list)
    for row in csv.DictReader((R/sub/'predictions.csv').open()):
        groups[(row['dataset'],row['test_fraction'],row['seed'],row['arm'])].append((int(row['truth']),int(row['prediction'])))
    for row in csv.DictReader((R/sub/'results.csv').open()):
        values=groups[(row['dataset'],row['test_fraction'],row['seed'],row['arm'])]
        totals=collections.Counter(a for a,b in values);hits=collections.Counter(a for a,b in values if a==b);cm=collections.Counter(values)
        ba=sum(hits[c]/totals[c] for c in (0,1,2))/3;acc=sum(a==b for a,b in values)/len(values)
        err=max(abs(ba-float(row['balanced_accuracy'])),abs(acc-float(row['accuracy'])))
        assert err<1e-14 and int(row['n_test'])==len(values)
        for i in range(3):
            for j in range(3):assert cm[(i,j)]==int(row[f'cm_{i}{j}'])
        checked+=1;largest=max(largest,err)
for name in ('results.csv','predictions.csv','scaler-parameters.json','summary.json'):
    a=digest(R/'results'/name);b=digest(R/'replay'/name);assert a==b;files.append({'file':name,'sha256':a,'replay_identical':True})
for name in ('wine','iris'):
    raw=[v for v in csv.reader((R/'raw'/name/(name+'.data')).open()) if v]
    derived=list(csv.reader((R/'derived'/(name+'.csv')).open()))[1:]
    assert raw==derived
# Verify scaler records against the original raw numbers, using an independent
# Python arithmetic path instead of calling the classifier implementation.
scalers=json.loads((R/'results'/'scaler-parameters.json').read_text())
for item in scalers:
    name=item['dataset'];rows=[v for v in csv.reader((R/'raw'/name/(name+'.data')).open()) if v]
    x=[[float(v) for v in (row[1:] if name=='wine' else row[:-1])] for row in rows]
    ids=item['fit_row_ids']
    for j in range(len(x[0])):
        m=math.fsum(x[i][j] for i in ids)/len(ids)
        sd=math.sqrt(math.fsum((x[i][j]-m)**2 for i in ids)/len(ids)) or 1.
        assert math.isclose(m,item['training_mean'][j],rel_tol=1e-12,abs_tol=1e-12)
        assert math.isclose(sd,item['training_population_sd_zero_to_one'][j],rel_tol=1e-12,abs_tol=1e-12)
report={'metrics_checked':checked,'largest_metric_difference':largest,'replayed_files':files,'raw_derived_all_rows_exactly_equal':True,'scaler_records_independently_verified_from_raw':len(scalers),'independent_population_replication':False,'inference':'Repeated partitions share data; this verifies computational reproducibility and descriptive sensitivity only'}
(R/'robustness-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
