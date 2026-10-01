"""Manufactured software acceptance cases; no empirical or originality claim."""
import csv,json,math,sys
from pathlib import Path
import numpy as np
import sympy as sp
from rdkit import Chem,rdBase
from rdkit.Chem import Descriptors,rdMolDescriptors
import sklearn
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
root=Path.cwd()
def write(name,value): (root/name).write_text(json.dumps(value,indent=2)+'\n')
x=sp.symbols('x',real=True);f=sp.exp(-x)*sp.sin(x)
derivative=sp.diff(f,x)
assert sp.simplify(derivative-sp.exp(-x)*(sp.cos(x)-sp.sin(x)))==0
integral=sp.integrate(sp.sin(x),(x,0,sp.pi));assert integral==2
write('symbolic-result.json',{'kind':'exact symbolic identities','function':str(f),'derivative':str(derivative),'integral':str(integral),'sympy':sp.__version__})
smiles=['CCO','c1ccccc1','CC(=O)O','CCN','CC(C)O','CO','CCC','c1ccncc1']
rows=[]
with Chem.SDWriter(str(root/'molecule-project.sdf')) as writer:
    for s in smiles:
        m=Chem.MolFromSmiles(s);assert m is not None
        formula=rdMolDescriptors.CalcMolFormula(m)
        rows.append({'smiles':s,'formula':formula,'molecular_weight':Descriptors.MolWt(m),'heavy_atoms':m.GetNumHeavyAtoms(),'rings':rdMolDescriptors.CalcNumRings(m)})
        m.SetProp('input_smiles',s);writer.write(m)
assert rows[0]['formula']=='C2H6O' and abs(rows[0]['molecular_weight']-46.069)<0.01
assert rows[1]['rings']==1 and rows[1]['heavy_atoms']==6
with (root/'molecule-descriptors.csv').open('w',newline='') as out:
    writer=csv.DictWriter(out,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
reloaded=list(Chem.SDMolSupplier(str(root/'molecule-project.sdf')));assert len(reloaded)==len(smiles) and all(m is not None for m in reloaded)
# Fixed even/odd split; held-out response is never used by fit.
X=np.linspace(-3,3,80).reshape(-1,1);y=2*X[:,0]+1
train=np.arange(0,80,2);test=np.arange(1,80,2)
model=Ridge(alpha=0.01).fit(X[train],y[train]);prediction=model.predict(X[test]);mse=mean_squared_error(y[test],prediction)
assert mse<1e-6 and math.isclose(float(model.coef_[0]),2,rel_tol=0.001)
write('research-model.json',{'role':'research_model','type':'sklearn.linear_model.Ridge','license':'BSD-3-Clause','version':sklearn.__version__,'alpha':0.01,'coefficient':model.coef_.tolist(),'intercept':float(model.intercept_),'train_indices':train.tolist(),'heldout_indices':test.tolist(),'material':'manufactured y=2x+1, algorithm execution only'})
with (root/'heldout-predictions.csv').open('w',newline='') as out:
    writer=csv.writer(out);writer.writerow(['index','x','observed','prediction'])
    writer.writerows((int(i),float(X[i,0]),float(y[i]),float(p)) for i,p in zip(test,prediction))
summary={'scope':'manufactured software correctness and professional API execution, not scientific novelty or a biological claim','symbolic_passed':True,'molecule_count':len(rows),'sdf_reload_passed':True,'ethanol_formula':rows[0]['formula'],'ethanol_molecular_weight':rows[0]['molecular_weight'],'rdkit':rdBase.rdkitVersion,'model_heldout_n':len(test),'model_heldout_mse':float(mse),'model_research_role':'research_model','executor':'current_host','python':sys.executable}
write('software-result.json',summary);print(json.dumps(summary))
