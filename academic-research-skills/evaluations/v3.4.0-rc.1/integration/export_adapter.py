import json,sys,pickle
from pathlib import Path
out=Path(__file__).parent;r=json.loads((out/'prepared/scipilot-figure.json').read_text());sys.path.insert(0,str(Path(r['root'])/'scripts'))
from export_figure import export_figure
with (out/'figure.pkl').open('rb') as f:fig=pickle.load(f)
paths=export_figure(fig,str(out/'launch-figure'),formats=['pdf','svg','png'],size_inches=(9,3.5),dpi=300,grayscale_preview=True)
(out/'figure-export.json').write_text(json.dumps(paths,indent=2));print(len(paths))
