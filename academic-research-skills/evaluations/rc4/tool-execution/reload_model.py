import csv,json
from pathlib import Path
import numpy as np
root=Path.cwd();weights=json.loads((root/'research-model.json').read_text())
assert weights['role']=='research_model' and weights['license']=='BSD-3-Clause'
rows=list(csv.DictReader((root/'heldout-predictions.csv').open()))
x=np.array([float(r['x']) for r in rows]).reshape(-1,1)
prediction=x@np.array(weights['coefficient'])+weights['intercept']
original=np.array([float(r['prediction']) for r in rows]);assert np.allclose(prediction,original,rtol=1e-12,atol=1e-12)
result={'model_role':'research_model','executor':'current_host','saved_parameter_reload_passed':True,'prediction_count':len(rows),'max_replay_difference':float(np.max(np.abs(prediction-original))),'scope':'Manufactured algorithm parameter reload, not empirical validation'}
(root/'research-model-replay.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
