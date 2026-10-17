from analysis_core import *
d=pd.read_csv(P/'derived/wine.csv');x=d.alcohol.to_numpy();y=d.color_intensity.to_numpy();g=d['class'].to_numpy()
assert len(d)==178 and d.isna().sum().sum()==0
(P/'results').mkdir(exist_ok=True)
models={kind:ols(design(d,kind),y) for kind in ['pooled','adjusted','interaction']}
pooled=models['pooled'];adj=models['adjusted'];inter=models['interaction']
groups={}
for c,z in d.groupby('class'):
 f=ols(design(z),z.color_intensity.to_numpy());models['class_'+str(c)]=f
 groups[str(c)]={'n':len(z),**corr(z.alcohol.to_numpy(),z.color_intensity.to_numpy()),'slope':float(f['beta'][1]),'slope_hc3_95':f['hc3_ci'][1].tolist(),'alcohol_mean':float(z.alcohol.mean()),'alcohol_sd':float(z.alcohol.std()),'color_mean':float(z.color_intensity.mean()),'color_sd':float(z.color_intensity.std()),'alcohol_range':[float(z.alcohol.min()),float(z.alcohol.max())],'color_range':[float(z.color_intensity.min()),float(z.color_intensity.max())]}
xd=x-d.groupby('class').alcohol.transform('mean').to_numpy();yd=y-d.groupby('class').color_intensity.transform('mean').to_numpy()
R=np.zeros((2,6));R[0,4]=1;R[1,5]=1;delta=R@inter['beta'];w=float(delta@np.linalg.solve(R@inter['hc3_cov']@R.T,delta))
e1={'experiment_id':'E1','question_ids':['Q1'],'execution':'completed','n':178,**corr(x,y),'slope':float(pooled['beta'][1]),'slope_hc3_95':pooled['hc3_ci'][1].tolist(),'slope_classical_normal95':pooled['classical_normal_ci'][1].tolist(),'r_squared':pooled['r_squared'],'definition':'Color-intensity units per one recorded alcohol unit; HC3 normal-approximation intervals are descriptive model sensitivity, not population inference.'}
e2={'experiment_id':'E2','question_ids':['Q2'],'execution':'completed','groups':groups,'adjusted_common_slope':float(adj['beta'][1]),'adjusted_slope_hc3_95':adj['hc3_ci'][1].tolist(),'adjusted_slope_classical_normal95':adj['classical_normal_ci'][1].tolist(),'partial_r_class_demeaned':float(np.corrcoef(xd,yd)[0,1]),'class_adjusted_r_squared':adj['r_squared'],'interaction_hc3_wald_chi2':w,'interaction_df':2,'interaction_reference_p':math.exp(-w/2),'interaction_interpretation':'A model diagnostic for slope heterogeneity, not proof of identical effects or a population test.','common_slope_weighting':'Class-specific slopes averaged with within-class alcohol sums-of-squares weights.'}
for name,obj in [('E1',e1),('E2',e2),('models',models)]: (P/'results'/f'{name}-v1.json').write_text(json.dumps(serial(obj),indent=2,allow_nan=False))
(P/'results/formal-run-summary.json').write_text(json.dumps({'formal_ols_fits':6,'primary_experiments':2,'model_matrix_orders':{'pooled':['intercept','alcohol'],'adjusted':['intercept','alcohol','class2','class3'],'interaction':['intercept','alcohol','class2','class3','alcohol_class2','alcohol_class3']},'software':{'numpy':np.__version__,'pandas':pd.__version__},'method':'Explicit NumPy lstsq OLS, HC3 sandwich leverage adjustment, normal reference; pandas average-tied ranks; Fisher z correlation intervals; deterministic no random seeds used','source_helper_functions_run':False,'input_sha256':__import__('hashlib').sha256((P/'raw/wine.data').read_bytes()).hexdigest()},indent=2))
print(json.dumps({'E1':e1,'E2':e2},indent=2))
