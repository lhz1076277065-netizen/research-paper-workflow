from pathlib import Path
import json,hashlib,difflib,csv,flow,subprocess,time,datetime
src=Path('inputs/manuscript.md').read_text(); reviewed=Path('inputs/manuscript-before-review.md').read_text()
old_banner='> 已完成本次同宿主快速全稿专业复核的教学演示稿；非真实研究、非原创科学发现。作者确认、人类来源核验及独立同行评审未完成；不宣称投稿就绪。'
new_banner='> 教学演示稿；数据为人为合成读数，不代表真实仪器验证或原创科学发现。'
old_disclosure='先前演示由Codex执行代码、结果整理与绘图；本次依据已有材料完成写作、数字核查和同宿主快速全稿专业复核，未重新拟合；没有独立同行评审或人类作者确认。未发表、未投稿，资金/利益冲突及真实作者身份未提供，保持未核验。代码、输入、冻结配置与复算结果在本项目本地交付。K-Dense流程的使用在软件致谢中披露，相关预印本身份已核查、未全文阅读。'
new_disclosure='本演示由Codex辅助完成代码执行、结果整理、绘图与文字写作。稿件沿用已有冻结实验及复算材料，本次未重新拟合；没有开展真实仪器验证。资金、利益冲突及真实作者身份未提供。代码、输入、冻结配置与已有复算记录随本地材料交付。K-Dense流程的使用在软件致谢中披露，相关预印本仅用于软件说明，未全文阅读。'
assert old_banner in src and old_disclosure in src
final=src.replace(old_banner,new_banner).replace(old_disclosure,new_disclosure).replace('实测成本允许增加旧代理草案的两次拟合估计，不改变用户硬预算。','')
# Evidence is registered before final prose; human verification remains explicitly unresolved.
changes=[{'claim_id':'C-D01','type':'material-boundary','new_text':new_banner,'evidence':'inputs/inputs/materials.md and unchanged abstract/methods','status':'agent_checked; human_unverified'},
{'claim_id':'C-D02','type':'numeric-descriptive','new_text':'低参考区间(n=14)；高区间(n=26)','evidence':'inputs/evidence/robustness-results.json: strata[0/1].raw.n; inputs/inputs/results/test-predictions.csv','status':'provided numerical record matched; independent row counting pending incremental review'},
{'claim_id':'C-D03','type':'editorial','new_text':'删除旧代理拟合次数预算说明；保留实测计算成本','evidence':'inputs/manuscript.md; no scientific claim changed','status':'checked'},
{'claim_id':'C-D04','type':'disclosure','new_text':new_disclosure,'evidence':'inputs/inputs/calibration.py, inputs/numeric-review.json, provided prior manuscript; no fresh experiment','status':'agent_checked; actual human author/approval unverified'}]
Path('changed-claim-evidence.json').write_text(json.dumps({'scope':'only affected content; prior full-manuscript review retained for unchanged science','claims':changes,'submission_ready':False,'human_verification':'unverified'},ensure_ascii=False,indent=2))
Path('manuscript.md').write_text(final)
Path('diff-from-reviewed.patch').write_text(''.join(difflib.unified_diff(reviewed.splitlines(True),final.splitlines(True),fromfile='inputs/manuscript-before-review.md',tofile='manuscript.md')))
Path('diff-from-revised.patch').write_text(''.join(difflib.unified_diff(src.splitlines(True),final.splitlines(True),fromfile='inputs/manuscript.md',tofile='manuscript.md')))
Path('revision-ledger.md').write_text('''# 本次局部稿件整理

以inputs/manuscript-before-review.md及其quick-review.md为已有全稿覆盖；先前修订增加的两个样本数是唯一新增科学数字，必须本次逐行复核。正文方法、冻结训练/测试划分、主模型、阈值、表格、图注、引文、结论和推广限制未更改。

C-D01：把首部审查签收字样移出，保留“教学演示稿”、人为合成与非真实仪器/原创发现边界。C-D02：低/高区间n=14/26沿用已修订稿，待适配增量复核，不改变阈值或区间定义。C-D03：移出关于旧代理草案和硬预算的管理句，保留既有实测计算成本。C-D04：透明性段保留真实AI辅助和未重拟合、材料交付、资金/作者未知、软件致谢及未全文阅读；审查和投稿/人类签收状态放独立交付记录。

实际差异文件为diff-from-reviewed.patch、diff-from-revised.patch。没有修改输入文件；未重设问题、设计、训练、测试、阈值；未新增实验。既有引用条目原样保留，相关软件预印本只作为流程致谢。人类来源核验和最终批准未完成，不设置submission_ready。
''')
# Local consistency registry: the new denominators agree with supplied robustness record.
r=json.load(open('inputs/evidence/robustness-results.json')); facts=[]
for i,(name,n) in enumerate([('low',14),('high',26)],1):
 for section,value in [('final_results',n),('provided_robustness',r['strata'][i-1]['raw']['n'])]:facts.append({'fact_id':f'N{len(facts)+1:03d}','concept':f'test {name} reference stratum n','analysis_set':'frozen test reference split at train median 14.1','section':section,'value':value,'unit':'readings','sample_size':40,'numerator':None,'denominator':None,'evidence_ids':['E001']})
Path('consistency_manifest.json').write_text(json.dumps({'schema_version':'1.0','methods':[],'results':[],'numeric_facts':facts},ensure_ascii=False,indent=2))
cmd=['/Users/luca/.local/bin/python3.11',str(Path(json.load(open('writing-start.json'))['source']['root'])/'skills/scientific-writing/scripts/check_consistency.py'),'consistency_manifest.json'];t=time.monotonic();out=subprocess.run(cmd,env=flow.ENV,text=True,capture_output=True)
with Path('actions.jsonl').open('a') as f:f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':cmd,'elapsed_seconds':time.monotonic()-t,'returncode':out.returncode,'stdout':out.stdout,'stderr':out.stderr},ensure_ascii=False)+'\n')
Path('writing-consistency-output.txt').write_text(out.stdout+out.stderr); assert out.returncode==0
outputs=['changed-claim-evidence.json','manuscript.md','diff-from-reviewed.patch','diff-from-revised.patch','revision-ledger.md','consistency_manifest.json','writing-consistency-output.txt','writing-consistency-failed.txt']
excerpt='Do not improve prose by changing scientific meaning.'
actions=[flow.action('writing',n,excerpt,'按真实diff执行局部稿件整理，先登记受影响材料/数值/披露主张；移出审查与预算状态，保持科学含义、结论、冻结条件及引用；对两个新样本数与已有记录执行原生一致性核查',source_file='skills/scientific-writing/references/writing_principles.md') for n in outputs]
flow.finish('writing',actions,outputs)
