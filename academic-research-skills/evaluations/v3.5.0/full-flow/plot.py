from pathlib import Path
from fractions import Fraction
import json,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent
src=Path(json.loads((root/'table-start.json').read_text())['source']['root'])
sys.path.insert(0,str(src/'scripts'))
from visual_qa import audit_layout
r=json.loads((root/'results.json').read_text())
fig,ax=plt.subplots(figsize=(6.4,3.8),layout='constrained')
for method,marker,color,dy in [('A','o','#0072B2',-.08),('B','s','#D55E00',.08)]:
 vals=[float(Fraction(r['rates'][method+'_easy']))*100,float(Fraction(r['rates'][method+'_hard']))*100,float(Fraction(r['aggregate'][method]))*100]
 ys=[0+dy,1+dy,2+dy]
 ax.scatter(vals,ys,marker=marker,color=color,label=method,s=55)
 for x,y in zip(vals,ys):ax.annotate(f'{x:.2f}%',(x,y),xytext=(5,6),textcoords='offset points',fontsize=9)
ax.set_yticks([0,1,2],['Easy','Hard','Aggregate (different mixtures)']);ax.set_xlim(0,105);ax.set_ylim(-.5,2.5);ax.set_xlabel('Success rate (%)');ax.legend(loc='upper left');ax.set_title('Synthetic benchmark: aggregate ranking reverses');ax.grid(axis='x',alpha=.2)
fig.canvas.draw()
issues=audit_layout(fig)
(root/'plot-layout.json').write_text(json.dumps(issues,default=str,indent=2)+'\n')
fig.savefig(root/'comparison.png',dpi=160);fig.savefig(root/'comparison.svg')
print(json.dumps({'file':'comparison.png','layout':issues},default=str))
