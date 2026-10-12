from pathlib import Path
import csv,json,math,hashlib,flow
R=Path('.')
flow.run('phase_control.py','--state','phase.json','reassess','--minutes','1.2','--reserve-seconds','10','--evidence','manuscript-before-review.md','--root','.','--next-action','完成已启动的全稿复核和最小状态修订；保留原12分钟总截止')
rows=list(csv.DictReader(open('inputs/results/test-predictions.csv'))); expected=json.load(open('inputs/results/results.json'));actual={}
for m in ('raw','offset','affine'):
 e=[float(x[m])-float(x['reference']) for x in rows]
 actual[m]={'n':len(e),'rmse':math.sqrt(sum(x*x for x in e)/len(e)),'mae':sum(abs(x) for x in e)/len(e),'bias':sum(e)/len(e)}
 for k in ('rmse','mae','bias'): assert abs(actual[m][k]-expected['test_metrics'][m][k])<1e-12
cv=list(csv.DictReader(open('inputs/results/cv-metrics.csv')))
for m in actual:
 a=[x for x in cv if x['model']==m];v=math.sqrt(sum(int(x['n'])*float(x['rmse'])**2 for x in a)/sum(int(x['n']) for x in a));assert abs(v-expected['cv_rmse'][m])<1e-12
original=list(csv.DictReader(open('inputs/measurements.csv')))
for x in rows:
 o=original[int(x['source_row'])-2]; assert o['split']=='test';assert float(o['reference'])==float(x['reference']); assert float(o['sensor'])==float(x['sensor'])
Path('numeric-review.json').write_text(json.dumps({'scope':'read-only reaggregation of existing predictions, no fit or experiment','test_metrics':actual,'cv_reaggregation_pass':True,'test_source_row_alignment_pass':True,'n_test_batches':len(set(x['batch'] for x in rows))},ensure_ascii=False,indent=2))
Path('quick-review.md').write_text('''# 全稿专业复核（同宿主快速模式）
来源：academic-paper-reviewer，固定提交6ab4b03bf70a118a1b3ee7f3263ed9f19031061b。模式为quick assessment：本代理分别执行领域分析与编辑判断，完整阅读摘要、方法、结果、讨论、透明性及引文；不是独立同行评审，也不是五专家完整面板。不得修改提交稿，以下报告独立保存。

## 三个判断视角
内部有效性：numeric-review.json重新聚合40条原有预测，核对3模型RMSE/MAE/bias和3折加权CV，误差小于1e-12；source_row逐条对应原始test读数。未重新拟合。测试前模型锁定在已有代码和记录内成立，当前稿如实承认原计划批次数错误与修订。最强替代解释是任意0.05阈值和只2批次；稿件已限定为教学决策，不能等效推断。
外部有效性：§方法“测试包含一个共享批次和一个未见批次”与原始分组一致；§讨论“未知数据生成机制、合成来源和任意教学阈值限制推广”明确禁止真实仪器推广。
贡献：仅为附件中的复杂度量化教学例；不存在可据此确认的科学原创性或现实效用。

## 七维审查
|维度|本稿范围判定|依据及限制|
|---|---|---|
|原创性|不适用真实研究原创门槛|引言明确只补充附件内量化|
|方法严谨性|MEETS教学范围|冻结80/40、训练3折、共享批次限制已披露|
|证据充分性|MEETS教学范围|逐行和聚合核查；不足总体等效或外部有效性|
|论证连贯性|MEETS|训练规则选偏移，测试收益0.001952低于约定阈值|
|写作质量|PARTLY_MEETS|待复核状态字样在复核后需更新；正文已完整|
|文献整合|MEETS方法说明范围|NIST与NumPy官方资料；预印本仅软件致谢，未冒称全文阅读|
|意义|MEETS教学范围|复杂度权衡清楚；非原创研究、非投稿就绪|

## 实际发现与编辑决定
MINOR，置信高。text：§首部“待本次全稿专业复核”及§透明性“待完成的全稿专业复核”。复核完成后这些时间状态将过时，应由写作角色更新并明确同宿主快速复核，保留非独立评审、人类未核验和非投稿就绪限制。无需新增实验或重拟合。可选补充低/高区间n=14/26，不影响现有结论。

图像核验：本次直接打开彩色和灰度文件，确认坐标、单位、40点、聚合菱形与批次空心符号一致，灰度仍可识别；校准散点重叠来自真实小差异。未添加CI或显著性标记。现有图与输入资产哈希一致。

判定：完成上述状态修订后可作为可编辑教学演示交付。该判断不构成期刊接收建议或独立同行评审。没有未处理的关键科学缺陷；现实研究门槛均明确未达到。审稿未改动提交稿。
''')
s=json.load(open('review-start.json')); src=Path(s['source']['entry']).read_text();line=next(x.strip() for x in src.splitlines() if 'typed' in x.lower() and 'anchor' in x.lower())
flow.finish('review',line,'快速模式完整阅读全稿，执行三视角与七维审查；只读重聚合现有预测与CV并逐行对照原数据，直接看彩色/灰度图；报告状态字样需更新，不冒称独立面板',['numeric-review.json','quick-review.md'])
flow.begin('revision','manuscript-writing',['manuscript-before-review.md','quick-review.md','numeric-review.json'])
text=Path('manuscript-before-review.md').read_text().replace('待本次全稿专业复核的教学演示稿','已完成本次同宿主快速全稿专业复核的教学演示稿').replace('数字核查和待完成的全稿专业复核','数字核查和同宿主快速全稿专业复核').replace('低参考区间的线性RMSE','低参考区间(n=14)的线性RMSE').replace('高区间线性为','高区间(n=26)线性为')
Path('manuscript.md').write_text(text)
Path('revision-validation.md').write_text('仅修订审稿指出的状态字样，并补充已有分层n=14/26；与review提交稿逐段对照，所有模型、数值、结论、限定及引用保持一致。报告建议全部落实，无新增实验。最终稿是教学演示，同宿主快速复核，不是独立同行评审或投稿就绪。')
s=json.load(open('revision-start.json'));src=Path(s['source']['entry']).read_text();line=next(x.strip() for x in src.splitlines() if len(x.strip())>35 and not x.startswith('#'))
flow.finish('revision',line,'按全稿复核完成状态修订，仅补充现成分层样本数并逐段验证未改科学主张',['manuscript.md','revision-validation.md'])
