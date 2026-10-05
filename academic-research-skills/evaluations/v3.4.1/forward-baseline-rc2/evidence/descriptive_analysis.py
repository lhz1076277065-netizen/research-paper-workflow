import json
from pathlib import Path
from decimal import Decimal
root=Path(__file__).resolve().parent.parent
x=json.loads((root/'inputs/provided-materials.json').read_text())
groups=[]
for g in x['groups']:
    assert 0<=g['no_show']<=g['n'] and g['n']>0
    groups.append({**g,'attended':g['n']-g['no_show'],'no_show_percent':str(Decimal(g['no_show'])/g['n']*100)})
result={'unit':'预约记录；不得视为20名独立参与者','synthetic':True,'groups':groups,'total_n':sum(g['n'] for g in groups),'total_no_show':sum(g['no_show'] for g in groups),'difference_pp_reminder_minus_control':str(Decimal(groups[0]['no_show_percent'])-Decimal(groups[1]['no_show_percent'])),'inference_performed':False,'missingness':'汇总数可核算；个体记录、缺失与重复预约不可核验'}
(root/'evidence/descriptive-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2))
