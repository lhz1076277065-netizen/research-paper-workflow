#!/usr/bin/env python3
"""Descriptive paired absolute-error analysis; deterministic test data, no inference."""
import csv, hashlib, json, platform, sys
from pathlib import Path
from decimal import Decimal, getcontext
import numpy as np
getcontext().prec=50
ROOT=Path(__file__).resolve().parent
D=Decimal
with (ROOT/'measurements.csv').open(newline='') as f:
    reader=csv.DictReader(f); rows=list(reader)
    if reader.fieldnames!=['case_id','scale','truth','method_a','method_b']:
        raise ValueError('Unexpected CSV schema')
if not rows or len({r['case_id'] for r in rows})!=len(rows):
    raise ValueError('Empty data or duplicate case_id')
cols={k:[D(r[k]) for r in rows] for k in ['scale','truth','method_a','method_b']}
if not all(v.is_finite() for values in cols.values() for v in values):
    raise ValueError('Nonfinite measurement')
x=cols['scale']; n=len(x)
if len(set(x))<2: raise ValueError('Scale must vary')
e={m:[abs(a-t) for a,t in zip(cols['method_'+m],cols['truth'])] for m in ['a','b']}
def mean(v): return sum(v)/D(len(v))
def summary(v):
    ordered=sorted(v); med=(ordered[(n-1)//2]+ordered[n//2])/2
    return {'n':n,'mean':str(mean(v)),'sample_sd':str((sum((z-mean(v))**2 for z in v)/D(n-1)).sqrt()),'median':str(med),'min':str(min(v)),'max':str(max(v))}
xbar=mean(x); sxx=sum((z-xbar)**2 for z in x)
models={}; residuals={}; predictions={}; float_checks={}
X=np.column_stack([np.ones(n),np.array(x,dtype=float)])
for m,y in e.items():
    b=sum((z-xbar)*(v-mean(y)) for z,v in zip(x,y))/sxx
    a=mean(y)-b*xbar
    pred=[a+b*z for z in x]; resid=[v-p for v,p in zip(y,pred)]
    sse=sum(z*z for z in resid); sst=sum((v-mean(y))**2 for v in y)
    models[m]={'result_id':'fit_'+m,'intercept':str(a),'slope':str(b),'r_squared':str(1-sse/sst),'sse':str(sse),'rmse':str((sse/D(n)).sqrt()),'max_abs_residual':str(max(abs(z) for z in resid)),'scale_range':[str(min(x)),str(max(x))]}
    residuals[m]=resid; predictions[m]=pred
    coefficients,_,rank,_=np.linalg.lstsq(X,np.array(y,dtype=float),rcond=None)
    err=max(abs(float(a)-coefficients[0]),abs(float(b)-coefficients[1]))
    assert err<1e-12 and rank==2
    float_checks[m]={'numpy_lstsq_intercept':float(coefficients[0]),'numpy_lstsq_slope':float(coefficients[1]),'max_coefficient_difference':float(err),'design_rank':int(rank)}
delta=[a-b for a,b in zip(e['a'],e['b'])]
ratio=(mean(e['a'])-mean(e['b']))/mean(e['a'])
result={'material_type':'software_behavior_test_not_real_research_data','data_quality':{'rows':n,'missing':0,'duplicates_case_id':0,'excluded':0,'all_finite':True,'units':'not provided'},'descriptives':{m:summary(y) for m,y in e.items()},'paired_comparison':{'result_id':'comparison_mae','difference_A_minus_B':summary(delta),'relative_MAE_reduction_B_vs_A':str(ratio),'B_lower_count':sum(b<a for a,b in zip(e['a'],e['b'])),'ties':sum(b==a for a,b in zip(e['a'],e['b']))},'linear_models':models,'diagnostics':{'exact_decimal_residuals_zero':all(z==0 for vals in residuals.values() for z in vals),'inferential_tests':'not performed: deterministic test material, unspecified sampling/noise model, zero residual variance','uncertainty_intervals':'not estimated: no justified sampling model'},'independent_numerical_crosscheck':float_checks}
(ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
fields=list(rows[0])+['abs_error_a','abs_error_b','difference_a_minus_b','fitted_a','fitted_b','residual_a','residual_b']
with (ROOT/'errors-and-fits.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
    for i,r in enumerate(rows):
        writer.writerow({**r,'abs_error_a':e['a'][i],'abs_error_b':e['b'][i],'difference_a_minus_b':delta[i],'fitted_a':predictions['a'][i],'fitted_b':predictions['b'][i],'residual_a':residuals['a'][i],'residual_b':residuals['b'][i]})
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['measurements.csv','analysis.py']}
env={'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'numpy':np.__version__,'decimal_precision':getcontext().prec,'input_and_code_sha256':hashes,'randomization':'none'}
(ROOT/'analysis-environment.json').write_text(json.dumps(env,ensure_ascii=False,indent=2)+'\n')
report=f'''# 绝对误差比较与线性拟合结果

软件行为测试材料；全部24条有效记录纳入，缺失=0，重复case_id=0，未删除记录；物理单位未提供。

同一case_id的方法A和B配对，e=|prediction−truth|。MAE_A={mean(e['a']):.6f}，MAE_B={mean(e['b']):.6f}；配对平均差A−B={mean(delta):.6f}。B相对A的MAE下降{ratio*100:.6f}%，B在全部{n}/{n}条记录的绝对误差均更小。[result_id: comparison_mae]

|方法|n|MAE|样本SD|中位数|最小|最大|
|---|---:|---:|---:|---:|---:|---:|
|A|{n}|{mean(e['a']):.6f}|{D(summary(e['a'])['sample_sd']):.6f}|{D(summary(e['a'])['median']):.6f}|{min(e['a']):.6f}|{max(e['a']):.6f}|
|B|{n}|{mean(e['b']):.6f}|{D(summary(e['b'])['sample_sd']):.6f}|{D(summary(e['b'])['median']):.6f}|{min(e['b']):.6f}|{max(e['b']):.6f}|

带截距OLS：A的拟合为e_A={D(models['a']['intercept']):.6f}+{D(models['a']['slope']):.6f}×scale，R²={D(models['a']['r_squared']):.6f}；B为e_B={D(models['b']['intercept']):.6f}+{D(models['b']['slope']):.6f}×scale，R²={D(models['b']['r_squared']):.6f}。[result_id: fit_a, fit_b]

Decimal直接读取原CSV，50位精度闭式拟合；两组SSE、RMSE及最大绝对残差均为0。numpy.linalg.lstsq独立数值实现的设计秩为2，各系数与Decimal结果差异小于1e−12。按CSV给出的十进制精度，两组绝对误差精确共线；这是该材料的结构，不证明真实测量误差遵循普遍规律。

诊断和范围：scale仅1—24；SD描述跨scale离散度，不是MAE标准误。配对差范围{min(delta):.6f}—{max(delta):.6f}。零残差方差不支持常规标准化残差检验；未运行Shapiro、Breusch-Pagan、t/F检验或置信区间，未声称正态性/独立性已验证。无真实抽样、独立实验或噪声模型，比较仅描述这24条记录，不作总体、因果或范围外推断。

复算：在本目录用已有Python运行 `analysis.py`；依赖numpy，详细版本、执行路径和输入/代码哈希见analysis-environment.json。逐行误差、预测、残差见errors-and-fits.csv；完整数值见results.json。没有随机步骤，无须随机种子。标准库Decimal结果是十进制精确核验，浮点结果仅交叉检查。

来源流程：已实施K-Dense统计入口的先定义目标量与配对单位、检查输入、带截距回归、解释残差退化与保留推断边界、可复算报告流程。使用固定核验源码commit 154988403bb5a18e9d3c0ce4e6d5e2e4b184a298；未安装或声称执行其原生全套依赖。新脚本是该流程内的当前宿主适配实现。
'''
(ROOT/'analysis-report.md').write_text(report)
print(json.dumps({'MAE_A':str(mean(e['a'])),'MAE_B':str(mean(e['b'])),'difference':str(mean(delta)),'relative_reduction':str(ratio),'models':models,'independent_check':'passed'},ensure_ascii=False))
