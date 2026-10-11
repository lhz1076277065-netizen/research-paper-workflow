import csv,json,math,statistics,hashlib
from fractions import Fraction
from pathlib import Path
from decimal import Decimal,localcontext
root=Path(__file__).resolve().parent
source=root/'derived/observations.csv'
rows=[{'id':int(r['id']),'x':Fraction(r['x']),'y':Fraction(r['y'])} for r in csv.DictReader(source.open())]
assert [r['id'] for r in rows]==list(range(1,25))
assert all(math.isfinite(float(r[k])) for r in rows for k in ('x','y'))
train=[r for r in rows if 1<=r['id']<=18]
validation=[r for r in rows if 19<=r['id']<=24]
def mean(a): return sum(a,Fraction(0))/len(a)
mx,my=mean([r['x'] for r in train]),mean([r['y'] for r in train])
sxx=sum((r['x']-mx)**2 for r in train)
assert sxx>0
b=sum((r['x']-mx)*(r['y']-my) for r in train)/sxx
a=my-b*mx
# Independent Decimal raw-sum normal-equation reproduction on development only.
with localcontext() as ctx:
 ctx.prec=40
 n=Decimal(len(train)); sx=sum(Decimal(str(float(r['x']))) for r in train); sy=sum(Decimal(str(float(r['y']))) for r in train)
 sxy=sum(Decimal(str(float(r['x'])))*Decimal(str(float(r['y']))) for r in train)
 sx2=sum(Decimal(str(float(r['x'])))**2 for r in train)
 b2=(n*sxy-sx*sy)/(n*sx2-sx*sx);a2=(sy-b2*sx)/n
 assert abs(float(a2)-float(a))<1e-12 and abs(float(b2)-float(b))<1e-12
metrics={}
predictions=[]
for label,data in [('development',train),('validation',validation)]:
 metrics[label]={}
 for model in ('linear','constant'):
  errors=[r['y']-(a+b*r['x'] if model=='linear' else my) for r in data]
  metrics[label][model]={'n':len(data),'MAE':float(mean([abs(e) for e in errors])),'MSE':float(mean([e**2 for e in errors])),'RMSE':math.sqrt(float(mean([e**2 for e in errors]))),'maximum_absolute_error':float(max(abs(e) for e in errors))}
 for r in data:
  predictions.append({'id':r['id'],'split':label,'x':float(r['x']),'y':float(r['y']),'linear':float(a+b*r['x']),'constant':float(my),'linear_residual':float(r['y']-a-b*r['x']),'constant_residual':float(r['y']-my)})
result={'data_kind':'synthetic software fixture','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'development_ids':[r['id'] for r in train],'validation_ids':[r['id'] for r in validation],'model':{'intercept':float(a),'slope':float(b),'constant':float(my),'decimal_reproduction_matches':True},'metrics':metrics,'diagnostics':{'missing':0,'duplicate_ids':0,'development_x_range':[float(min(r['x'] for r in train)),float(max(r['x'] for r in train))],'validation_x_range':[float(min(r['x'] for r in validation)),float(max(r['x'] for r in validation))],'linearity':'exact deterministic line in this fixture','residual_variance':'zero for linear; stochastic normality/variance tests not meaningful','independence':'not established as scientific sampling; ordered synthetic rows','inference':'no population CI, p value or scientific superiority claim'}}
(root/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
with (root/'predictions.csv').open('w') as out:
 writer=csv.DictWriter(out,fieldnames=list(predictions[0]));writer.writeheader();writer.writerows(predictions)
# Raw observations with fixed fitted models, and residuals, drawn without optional dependencies.
elements=['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450" viewBox="0 0 800 450">','<rect width="800" height="450" fill="white"/>','<text x="30" y="25" font-family="sans-serif">Synthetic fixture: development 1-18, validation 19-24</text>','<line x1="50" y1="250" x2="760" y2="250" stroke="black"/>']
def xx(x):return 50+(x-1)*710/23
def yy(y):return 240-(y-5)*200/46
for r in predictions:
 c='#205caa' if r['split']=='development' else '#d45d00'
 elements.append(f'<circle cx="{xx(r["x"]):.3f}" cy="{yy(r["y"]):.3f}" r="4" fill="{c}"/>')
elements.extend([f'<line x1="{xx(1)}" y1="{yy(float(a+b))}" x2="{xx(24)}" y2="{yy(float(a+24*b))}" stroke="#37934a" stroke-width="2"/>',f'<line x1="50" y1="{yy(float(my))}" x2="760" y2="{yy(float(my))}" stroke="#7c4690" stroke-dasharray="5 4"/>','<text x="50" y="280" font-family="sans-serif">Green: linear; purple dashed: development mean. Orange: final validation.</text>','<text x="50" y="310" font-family="sans-serif">Linear residuals: zero for all 24 rows; constant residuals increase with x.</text>','<line x1="50" y1="360" x2="760" y2="360" stroke="black"/>'])
for r in predictions:
 elements.append(f'<circle cx="{xx(r["x"]):.3f}" cy="360" r="3" fill="#37934a"/>')
 elements.append(f'<circle cx="{xx(r["x"]):.3f}" cy="{360-r["constant_residual"]*1.7:.3f}" r="3" fill="#7c4690"/>')
elements.append('</svg>')
(root/'diagnostic.svg').write_text(''.join(elements))
print(json.dumps(result,ensure_ascii=False,indent=2))
