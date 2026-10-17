from pathlib import Path
import json,sys,subprocess,numpy as np,pandas as pd
P=Path(__file__).resolve().parent
s=json.loads((P/'pilot-start.json').read_text());src=Path(s['source']['entry']).parent/'scripts/assumption_checks.py'
proc=subprocess.run([sys.executable,str(src)],capture_output=True,text=True)
(P/'upstream-assumption-import-failure.json').write_text(json.dumps({'command':[sys.executable,str(src)],'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'functions_executed':False,'repair':'Use source protocol with explicit NumPy computations; no unavailable numerical/plot helper is claimed executed.'},indent=2))
d=pd.read_csv(P/'derived/wine.csv');x=d.alcohol.to_numpy();y=d.color_intensity.to_numpy()
b=np.linalg.lstsq(np.column_stack([np.ones(len(x)),x]),y,rcond=None)[0]
r=float(np.corrcoef(x,y)[0,1]);direct=float(((x-x.mean())@(y-y.mean()))/((x-x.mean())@(x-x.mean())))
assert abs(b[1]-direct)<1e-11
# Raw-data plot before formal interpretation. Retained SVG is editable.
def xy(xi,yi):return 55+(xi-11)/4*600,310-(yi-1)/12*260
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="720" height="380" viewBox="0 0 720 380">','<rect width="720" height="380" fill="white"/>','<text x="55" y="25" font-size="17">Diagnostic pilot: raw complete data (not formal evidence)</text>','<path d="M55 50 V310 H655" stroke="black" fill="none"/>']
for xi,yi in zip(x,y):
 px,py=xy(xi,yi);parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="2.4" fill="#305E8C" opacity=".65"/>')
parts+=['<text x="260" y="350" font-size="14">Alcohol (recorded units)</text>','<text x="10" y="45" font-size="12">Color intensity</text>','</svg>']
(P/'pilot-raw.svg').write_text(''.join(parts))
(P/'pilot-results.json').write_text(json.dumps({'purpose':'diagnostic only, not formal results','n':len(d),'pooled_r':r,'slope_lstsq':float(b[1]),'slope_centered_formula':direct,'agreement_abs':abs(float(b[1])-direct),'fit_count':1,'source_helper_import_returncode':proc.returncode,'next':'Run formal models under formal source receipt, then independent robustness; runtime alternative verified.'},indent=2))
print((P/'pilot-results.json').read_text())
