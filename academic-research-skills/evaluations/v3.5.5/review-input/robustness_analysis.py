from analysis_core import *
import csv,hashlib
# Critical-thinking source directs explicit unit/assumption appraisal and remedies.
d=pd.read_csv(P/'derived/wine.csv');y=d.color_intensity.to_numpy();x=d.alcohol.to_numpy()
models=json.loads((P/'results/models-v1.json').read_text());e1=json.loads((P/'results/E1-v1.json').read_text());e2=json.loads((P/'results/E2-v1.json').read_text())
loo={}
for kind in ['pooled','adjusted']:
 vals=[]
 for j in range(len(d)):
  z=d.drop(index=j);fit=ols(design(z,kind),z.color_intensity.to_numpy());vals.append(float(fit['beta'][1]))
 loo[kind]={'min':min(vals),'max':max(vals),'all_positive':all(v>0 for v in vals),'most_changed_row_1based':int(np.argmax(np.abs(np.array(vals)-models[kind]['beta'][1]))+1),'fits':len(vals)}
 pd.DataFrame({'omitted_record_1based':np.arange(1,len(d)+1),'slope':vals}).to_csv(P/'results'/f'loo-{kind}.csv',index=False)
xc=x-d.groupby('class').alcohol.transform('mean').to_numpy();X=design(d,'adjusted');q=ols(np.column_stack([X,xc**2]),y)
# Separate input parser and algebra: no derived table or shared OLS call for these checks.
with (P/'raw/wine.data').open(newline='') as f:a=np.array([[float(v) for v in row] for row in csv.reader(f)])
g=a[:,0].astype(int);xx=a[:,1];yy=a[:,10];dx=xx.copy();dy=yy.copy()
for c in [1,2,3]:
 m=g==c;dx[m]-=xx[m].mean();dy[m]-=yy[m].mean()
ind_p=float(np.dot(xx-xx.mean(),yy-yy.mean())/np.dot(xx-xx.mean(),xx-xx.mean()));ind_a=float(np.dot(dx,dy)/np.dot(dx,dx))
# Independent HC3 slope variance from residualized weights in the adjusted design.
mat=np.column_stack([np.ones(len(g)),xx,(g==2).astype(float),(g==3).astype(float)])
qr,rr=np.linalg.qr(mat);coef=np.linalg.solve(rr,qr.T@yy);ee=yy-mat@coef;hh=(qr**2).sum(axis=1)
weights=np.linalg.solve(rr,np.eye(4))@qr.T
se=float(np.sqrt(np.sum((weights[1,:]*ee/(1-hh))**2)))
assert abs(ind_p-e1['slope'])<1e-11 and abs(ind_a-e2['adjusted_common_slope'])<1e-11
assert abs(se-models['adjusted']['hc3_se'][1])<1e-10
checks={}
for kind in ['pooled','adjusted']:
 mo=models[kind];res=np.array(mo['resid']);h=np.array(mo['h']);mse=mo['sse']/(178-mo['k']);cook=res**2/(mo['k']*mse)*h/(1-h)**2
 checks[kind]={'max_leverage':float(h.max()),'max_cooks_distance':float(cook.max()),'max_abs_residual':float(abs(res).max()),'residual_sd':float(res.std(ddof=mo['k'])),'corr_abs_residual_fitted':float(np.corrcoef(abs(res),mo['fitted'])[0,1])}
out={'purpose':'formal robustness and independent recomputation of E1/E2','leave_one_out':loo,'quadratic_within_class_centered':{'coefficient':float(q['beta'][-1]),'hc3_95':q['hc3_ci'][-1].tolist(),'interpretation':'Sensitivity diagnostic, common curvature added to class-intercept/common-slope model; interval does not prove linearity.'},'independent_raw_file_checks':{'pooled_slope':ind_p,'adjusted_slope_fwl':ind_a,'adjusted_slope_qr':float(coef[1]),'adjusted_hc3_se_independent':se,'max_slope_abs_difference':max(abs(ind_p-e1['slope']),abs(ind_a-e2['adjusted_common_slope'])),'hc3_se_abs_difference':abs(se-models['adjusted']['hc3_se'][1])},'residual_influence':checks,'fit_counts':{'loo_ols':356,'quadratic_ols':1,'independent_qr_ols':1,'total_new_ols_solutions':358},'limitations':['No documented probability sampling frame, collection times, batch or independence structure; no population/causal claims.','HC3 handles independent-error heteroscedastic variance, not clustering, measurement error or mean-model misspecification.','Class-specific slopes differ numerically; nonsignificant interaction diagnostic is not an equivalence test.','Shapiro/Breusch-Pagan source helpers were unavailable; visual/raw/rank/influence/curvature checks and explicit HC3 sensitivity were used; no helper assumption certification.']}
(P/'results/robustness-v1.json').write_text(json.dumps(out,indent=2,allow_nan=False))
(P/'robustness-appraisal-v1.md').write_text('# Result-level appraisal\nQ1/E1 and Q2/E2 are descriptive results on the same 178 records, not independent replications. Exact full-data effects are fixed summaries; intervals are hypothetical-model sensitivity and cannot justify population coverage. Source numerical outputs and denominators were checked before judging. Composition: pooled slope exceeds the class-conditioned slope; all three class estimates remain positive, but common slope is a weighted summary and not equality. No causal confounding framework or intervention risk-of-bias score is applicable.\n\nIndependent raw-file algebra and separate QR/HC3 computation reproduce the main slopes/uncertainty. LOO checks all 178 omissions per model without selecting or deleting outliers. Rank comparisons and curvature diagnostic qualify functional form. Unknown sampling hierarchy and units remain unknown, not evidence of absence. Report actual ranges/diagnostics and retain all data. Independent external/human verification remains unperformed. See results/robustness-v1.json for exact evidence and limitations.\n')
print(json.dumps(out,indent=2))
