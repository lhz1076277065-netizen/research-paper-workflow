import importlib.util,json,sys,pickle,csv
from pathlib import Path
import matplotlib.pyplot as plt
out=Path(__file__).parent
r=json.loads((out/'prepared/scipilot-figure.json').read_text());sys.path.insert(0,str(Path(r['root'])/'scripts'))
from setup_style import setup_style
from visual_qa import audit_layout,render_preview
setup_style(journal='general',lang='en',use_sciplots=False)
rows=list(csv.DictReader((out/'launch-results.csv').open()))
fig,axs=plt.subplots(1,2,figsize=(9,3.5),layout='constrained')
for ax,status in zip(axs,['expired','active']):
 vals=[sum(int(r['started']) for r in rows if r['state']==status and r['method']==m) for m in ['direct','phase_control']]
 ax.barh([1,0],vals,color=['#666666','#0072B2'],height=.42)
 ax.set_yticks([1,0],['Direct launch','Phase control']);ax.set_xlim(0,7);ax.set_xticks(range(7));ax.set_xlabel('Commands started (of 6)');ax.set_title(status.title()+' state')
 for y,v in zip([1,0],vals):ax.text(v+.10,y,str(v),va='center')
 ax.spines[['top','right']].set_visible(False)
fig.suptitle('Software fixture: deadlines change launch decisions')
issues=audit_layout(fig)
(out/'layout-qa.json').write_text(json.dumps(issues))
render_preview(fig,str(out/'launch-preview.png'),dpi=150)
with (out/'figure.pkl').open('wb') as f:pickle.dump(fig,f)
(out/'figure-values.json').write_text(json.dumps({'expired':{'direct':6,'phase_control':0},'active':{'direct':6,'phase_control':6},'n_per_cell':6,'uncertainty':'no inferential interval; deterministic local fixture'},indent=2))
print(json.dumps({'qa':issues,'preview':'launch-preview.png'}))
