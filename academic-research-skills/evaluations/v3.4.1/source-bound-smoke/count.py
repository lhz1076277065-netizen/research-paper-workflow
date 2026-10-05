import csv,json,sys
from collections import Counter
rows=list(csv.DictReader(open(sys.argv[1])))
assert len(rows)==20 and len({r['appointment_id'] for r in rows})==20
assert all(r['no_show'] in {'0','1'} and r['group'] in {'reminder','control'} for r in rows)
counts={g:{'n':sum(r['group']==g for r in rows),'no_show':sum(int(r['no_show']) for r in rows if r['group']==g)} for g in ['reminder','control']}
assert all(v['n']==10 for v in counts.values())
for v in counts.values():v['fraction']=v['no_show']/v['n']
open(sys.argv[2],'w').write(json.dumps(counts,indent=2)+'\n')
