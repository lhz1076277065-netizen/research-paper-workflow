from pathlib import Path
from fractions import Fraction as F
import csv,json,platform
root=Path(__file__).resolve().parent
rows=list(csv.DictReader((root/'raw.csv').open()))
assert len(rows)==4
cells={}
for r in rows:
 key=r['method'],r['condition'];assert key not in cells
 s,n=int(r['success']),int(r['n']);assert n>0 and 0<=s<=n
 cells[key]=(s,n)
assert set(cells)=={('A','easy'),('A','hard'),('B','easy'),('B','hard')}
rates={f'{m}_{c}':F(*cells[m,c]) for m,c in cells}
agg={m:F(sum(cells[m,c][0] for c in ['easy','hard']),sum(cells[m,c][1] for c in ['easy','hard'])) for m in ['A','B']}
std={m:(rates[m+'_easy']+rates[m+'_hard'])/2 for m in ['A','B']}
diffs={c:rates['A_'+c]-rates['B_'+c] for c in ['easy','hard']}
assert agg['A']>agg['B'] and all(v<0 for v in diffs.values())
assert std['A']<std['B']
out={'synthetic':True,'python':platform.python_version(),'rates':{k:str(v) for k,v in rates.items()},'aggregate':{k:str(v) for k,v in agg.items()},'equal_weights':{k:str(v) for k,v in std.items()},'A_minus_B':{k:str(v) for k,v in diffs.items()},'aggregate_difference':str(agg['A']-agg['B']),'standardized_difference':str(std['A']-std['B']),'common_weight_difference':'-3/20+w/10','data_checks':'4 unique cells, integer counts, valid denominators, all rows retained'}
(root/'results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
