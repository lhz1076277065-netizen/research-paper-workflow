import os,json,csv,sys,argparse,warnings
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ['MPLCONFIGDIR']=str(ROOT/'.mpl');os.environ['XDG_CACHE_HOME']=str(ROOT/'.cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image
SOURCE=Path(json.loads((ROOT/'figure-start.json').read_text())['source']['root'])
sys.path.insert(0,str(SOURCE/'scripts'))
from visual_qa import render_preview,audit_layout
ap=argparse.ArgumentParser();ap.add_argument('--export',action='store_true');args=ap.parse_args()
figdir=ROOT/'figures';figdir.mkdir(exist_ok=True)
r=json.loads((ROOT/'results/results.json').read_text());rob=json.loads((ROOT/'robustness-results.json').read_text());rows=list(csv.DictReader((ROOT/'results/test-predictions.csv').open()))
y=np.array([float(v['reference']) for v in rows]);cols={'raw':'#555555','offset':'#0072B2','affine':'#D55E00'};marks={'raw':'o','offset':'s','affine':'^'};labels={'raw':'Raw','offset':'Offset','affine':'Affine'}
plt.rcParams.update({'font.size':8,'axes.labelsize':9,'axes.titlesize':9,'legend.fontsize':7,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(7.2,3.6),layout='constrained')
profile={}
for k in cols:
 e=np.array([float(v[k]) for v in rows])-y;profile[k]={'n':len(e),'mean':float(np.mean(e)),'sd':float(np.std(e,ddof=1)),'median':float(np.median(e)),'min':float(min(e)),'max':float(max(e))}
 axes[0].scatter(y,e,s=20,marker=marks[k],edgecolor=cols[k],facecolor='none' if k=='affine' else cols[k],alpha=.75,label=labels[k])
axes[0].axhline(0,color='.6',linewidth=.7,linestyle='--');axes[0].set(xlabel='Reference (attachment units)',ylabel='Prediction - reference (units)',title='a  Held-out residuals, n = 40');axes[0].legend(loc='upper left',bbox_to_anchor=(0,1),frameon=False,ncol=3);axes[0].set_ylim(-1.05,2.6)
for i,k in enumerate(cols):
 total=r['test_metrics'][k]['rmse'];axes[1].scatter(i,total,color=cols[k],marker='D',s=42,zorder=3)
 for j,b in enumerate(rob['by_batch']):axes[1].scatter(i+(-.13 if j==0 else .13),b[k]['rmse'],color=cols[k],marker=('o' if j==0 else '^'),s=20,facecolors='none',zorder=2)
 axes[1].annotate(f'{total:.4f}',(i,total),xytext=(0,9),textcoords='offset points',ha='center',fontsize=8)
axes[1].set(xticks=range(3),xticklabels=['Raw','Offset','Affine'],ylabel='RMSE (attachment units)',ylim=(0,1.8),title='b  Same frozen predictions');axes[1].set_xlim(-.4,2.4)
from matplotlib.lines import Line2D
handles=[Line2D([],[],marker='D',color='none',markerfacecolor='.3',markeredgecolor='.3',label='All 40 readings'),Line2D([],[],marker='o',color='none',markerfacecolor='none',markeredgecolor='.3',label='Shared batch 2, n=10'),Line2D([],[],marker='^',color='none',markerfacecolor='none',markeredgecolor='.3',label='New batch 3, n=30')]
axes[1].legend(handles=handles,loc='upper right',frameon=False)
render_preview(fig,str(figdir/'preview.png'),dpi=150);issues=audit_layout(fig)
(ROOT/'figure-layout.json').write_text(json.dumps({'native_audit_layout':issues,'dimensions_inches':[7.2,3.6],'font_minimum_pt':7,'no_error_bars':True,'profile':profile},ensure_ascii=False,indent=2)+'\n')
assert not any(i[0]=='FAIL' for i in issues)
if args.export:
 for ext in ['png','pdf','svg']:fig.savefig(figdir/('figure1.'+ext),dpi=300)
 with Image.open(figdir/'figure1.png') as im:im.convert('L').save(figdir/'figure1-grayscale.png',dpi=(300,300))
print(json.dumps({'layout':issues,'export':args.export,'size':[7.2,3.6]}));plt.close(fig)
