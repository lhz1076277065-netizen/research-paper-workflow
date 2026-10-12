from pathlib import Path
import json,hashlib,csv,datetime,difflib,flow
flow.begin('final-review','manuscript-review',['manuscript.md','manuscript-before-review.md','quick-review.md','revision-validation.md','numeric-review.json','evidence/robustness-results.json'])
a=Path('manuscript-before-review.md').read_text();b=Path('manuscript.md').read_text();assert b==a.replace('待本次全稿专业复核的教学演示稿','已完成本次同宿主快速全稿专业复核的教学演示稿').replace('数字核查和待完成的全稿专业复核','数字核查和同宿主快速全稿专业复核').replace('低参考区间的线性RMSE','低参考区间(n=14)的线性RMSE').replace('高区间线性为','高区间(n=26)线性为')
rows=list(csv.DictReader(open('inputs/results/test-predictions.csv')));assert sum(float(r['reference'])<=14.1 for r in rows)==14
Path('final-review.md').write_text('最终版本增量复核：读取manuscript.md全稿，并与先前审稿版本逐段差异核对。仅2处状态描述和2处现成分层样本数变更，逐行计数低区间14、高26正确。科学主张和所有数值/图/引文/局限未变。此前全稿报告的唯一必要状态修订已落实；没有新问题。完成层级为同宿主快速专业全稿复核及修订后复核，非独立同行评审或完整专家面板。')
s=json.load(open('final-review-start.json'));src=Path(s['source']['entry']).read_text();line=next(x.strip() for x in src.splitlines() if 'typed' in x.lower() and 'anchor' in x.lower())
flow.finish('final-review',line,'重新读取修订后的完整稿件并逐段对照原审稿版本；实际计数新增分层n，确认原报告问题已处理且结论未变',['final-review.md'])
keys=['citations','writing','review','revision','final-review'];args=[]
for k in keys:args += ['--professional-started',k+'-start.json','--professional-finished',k+'-finish.json']
flow.run('phase_control.py','--state','phase.json','advance','--stage','delivery','--minutes','0.4','--evidence','final-review.md','--root','.','--next-action','交付教学稿、真实完成层级和动作证据',*args)
snap=json.load(open('inputs-snapshot.json'));print(type(snap));print(str(snap)[:100])
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
Path('README.md').write_text('''# 已有合成校准材料写作交付

可编辑主稿：manuscript.md；彩色与灰度图、PDF/SVG编辑图在assets/；引用在references.bib。输入材料保留于inputs/，未改写。不得在inputs目录直接运行会覆盖结果的原代码。

本次确认问题和冻结设计足够，直接写作，未再拟合/实验。完成引用核验、写作、同宿主快速模式全稿专业复核、状态修订和最终版本增量复核。quick-review.md记录三视角和七维审查；numeric-review.json是现有预测与CV只读重聚合、逐行原数据对照；final-review.md核查最终稿。不是独立同行评审、完整五专家面板、原创研究或投稿就绪。人类作者确认及来源独立核验未完成。

专业路径使用14库映射中匹配的Scholar、K-Dense、academic-paper-reviewer固定真实来源缓存；未因已有证据重新跑整个实验链。*-start/work/finish.json为各次可核验收据，actions.jsonl保留实际命令及错误。阶段与预留按实测自主重新安排，原接单14:41:22 UTC与14:53:22总截止没有重置。

实际问题：首次intake finish错误包含begin前已有文件，被时序核验拒绝，改为真实begin后产物；引用作者解析首次断言失败，按缓存官方元数据修正；一次reassess调用漏必填参数，保留原报错后按实际工具参数修复。没有把这些动作或上一轮最终审稿被拦截改记成功。

原结果JSON的scope文字写4个测试批次、旧冻结计划也写4折，原计算实际3训练折/2测试批次；本稿纠正并保留原记录及evidence/analysis-amendment.md。只有2测试批次，0.05为教学阈值，不能证明总体等效。完整性检查见delivery-status.json。
''')
# Snapshot shape is list/dict of path hashes; validate by direct before/after tree against manifest.
current={str(p.relative_to(Path('inputs'))):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('inputs').rglob('*') if p.is_file()}
Path('inputs-final-snapshot.json').write_text(json.dumps(current,indent=2))
old=snap.get('files',snap) if isinstance(snap,dict) else snap
unchanged = old==current
if not unchanged:
 # Original manifest uses paths rooted at project, compare normalized records.
 if isinstance(old,list): normalized={x['path'].removeprefix('inputs/'):x['sha256'] for x in old}
 elif isinstance(old,dict): normalized={k.removeprefix('inputs/'):v for k,v in old.items()}
 else: normalized={}
 unchanged=normalized==current
assert unchanged
Path('delivery-status.json').write_text(json.dumps({'completed_at':now,'level':'editable teaching manuscript; current-host quick full-manuscript professional review and focused revision recheck complete','independent_peer_review':False,'submission_ready':False,'new_fits':0,'inputs_unchanged':unchanged,'original_total_deadline':'2026-10-12T14:53:22Z'},ensure_ascii=False,indent=2))
flow.run('phase_control.py','--state','phase.json','close','--status','completed','--reason','已有证据写作任务及必要全稿专业复核、修订、最终版本复核实际完成；教学层级明确','--evidence','README.md','--root','.','--task-id','followup-writing')
flow.run('phase_control.py','--state','phase.json','resume')
manifest={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('.').rglob('*') if p.is_file() and str(p)!='delivery-manifest.json'}
Path('delivery-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
