from pathlib import Path
import numpy as np,pandas as pd,json,math
from statistics import NormalDist
P=Path(__file__).resolve().parent
Z=NormalDist().inv_cdf(.975)
def ols(X,y):
 X=np.asarray(X,float);y=np.asarray(y,float);n,k=X.shape
 b=np.linalg.lstsq(X,y,rcond=None)[0];inv=np.linalg.inv(X.T@X);res=y-X@b
 h=np.einsum('ij,jk,ik->i',X,inv,X);ss=float(res@res)
 v3=inv@((X.T*(res/(1-h))**2)@X)@inv
 vc=inv*(ss/(n-k));se3=np.sqrt(np.diag(v3));sec=np.sqrt(np.diag(vc))
 return {'n':n,'k':k,'beta':b,'resid':res,'fitted':X@b,'h':h,'hc3_cov':v3,'hc3_se':se3,'classical_se':sec,'hc3_ci':np.column_stack([b-Z*se3,b+Z*se3]),'classical_normal_ci':np.column_stack([b-Z*sec,b+Z*sec]),'sse':ss,'r_squared':float(1-ss/((y-y.mean())@(y-y.mean())))}
def serial(v):
 if isinstance(v,dict):return {k:serial(x) for k,x in v.items()}
 if isinstance(v,np.ndarray):return v.tolist()
 if isinstance(v,np.generic):return v.item()
 if isinstance(v,list):return [serial(x) for x in v]
 return v
def corr(x,y):
 r=float(np.corrcoef(x,y)[0,1]);z=np.arctanh(r);h=Z/math.sqrt(len(x)-3)
 return {'pearson_r':r,'pearson_fisher95':np.tanh([z-h,z+h]).tolist(),'spearman_rho':float(pd.Series(x).rank().corr(pd.Series(y).rank()))}
def design(d,kind='pooled'):
 x=d.alcohol.to_numpy();g=d['class'].to_numpy();one=np.ones(len(d));c2=(g==2).astype(float);c3=(g==3).astype(float)
 if kind=='pooled':return np.column_stack([one,x])
 if kind=='adjusted':return np.column_stack([one,x,c2,c3])
 if kind=='interaction':return np.column_stack([one,x,c2,c3,x*c2,x*c3])
 raise ValueError(kind)
