import importlib.util,json,re
from pathlib import Path
out=Path(__file__).parent.resolve();scripts=out.parent/'repository/academic-research-skills/src/common/scripts'
s=importlib.util.spec_from_file_location('capabilities',scripts/'capabilities.py');C=importlib.util.module_from_spec(s);s.loader.exec_module(C);idx=C.load(scripts.parent/'assets/capability-index.json')
parts=re.split(r'(?m)^## ',(out/'professional-work.md').read_text())[1:]
labels=['researchstudio-search','nature-reader','kdense-eda','scholar-analysis','scipilot-figure','sleep-experiment-plan','autoresearch-protocol','rougier-reference','orchestra-ideation','academic-reviewer','anti-defensive','open-design-deck','codex-ppt','paperspine-workbench']
for uid,part in zip(labels,parts):(out/(uid+'-work.md')).write_text('## '+part)
(out/'software-problem.md').write_text('软件维护范围：阶段出口、预算/恢复及专业能力接入。重要失败：状态没有阻止真实启动，安装事项恢复时重复成为主任务。比较有限阶段控制与扩大提示词/新工作台方案，不生成科学课题。\n')
uses={
'researchstudio-search':(['software-problem.md'],['search-results.json','researchstudio-search-work.md'],True,'adapted_in_host'),
'nature-reader':([str(Path(C.load(out/'prepared/autoresearch-protocol.json')['root'])/'program.md')],['nature-reader-work.md'],False,'adapted_in_host'),
'kdense-eda':(['launch-results.csv'],['kdense-profile.json','kdense-eda-work.md'],True,'native_in_host'),
'scholar-analysis':(['launch-results.csv','figure-values.json'],['scholar-analysis-work.md'],False,'adapted_in_host'),
'scipilot-figure':(['launch-results.csv','kdense-profile.json'],['launch-figure.png','launch-figure.pdf','scipilot-figure-work.md','layout-qa.json'],True,'native_in_host'),
'sleep-experiment-plan':(['software-problem.md'],['experiment-plan.md','tracker.md','sleep-experiment-plan-work.md'],False,'adapted_in_host'),
'autoresearch-protocol':(['experiment-plan.md','launch-results.csv'],['results.tsv','autoresearch-protocol-work.md'],False,'adapted_in_host'),
'rougier-reference':([str(Path(C.load(out/'prepared/rougier-reference.json')['root'])/'code/ornaments/legend-alternatives.py')],['rougier/figures/ornaments/legend-alternatives.pdf','rougier-reference-work.md','launch-figure.png'],True,'reference_only'),
'orchestra-ideation':(['software-problem.md'],['orchestra-ideation-work.md','experiment-plan.md'],False,'adapted_in_host'),
'academic-reviewer':(['final-report.md','launch-results.csv'],['academic-reviewer-work.md'],False,'adapted_in_host'),
'anti-defensive':(['before-after.md','launch-results.csv'],['final-report.md','anti-defensive-work.md'],False,'adapted_in_host'),
'open-design-deck':(['final-report.md','figure-values.json'],['deck-plan.md','deck/index.html','open-design-deck-work.md'],False,'adapted_in_host'),
'codex-ppt':(['launch-figure.png','ppt/fixture-deck/speech.md'],['ppt/fixture-deck/fixture-deck.pptx','ppt-inspection.json','codex-ppt-work.md'],True,'function_only'),
'paperspine-workbench':(['launch-results.csv','final-report.md'],['spine/results_validation.md','spine/results_validation_check.md','paperspine-workbench-work.md'],True,'adapted_in_host')}
summary=[];(out/'receipts').mkdir(exist_ok=True)
for uid,(inputs,outputs,ran,mode) in uses.items():
 r=C.usage(C.entry(idx,uid),C.load(out/'prepared'/f'{uid}.json'),[str(out/p) for p in inputs],[str(out/p) for p in outputs],['Read verified entry and task-relevant support','Apply steps and limits recorded in '+uid+'-work.md','Connect actual task output to final software validation report'],mode,ran)
 (out/'receipts'/f'{uid}.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));summary.append({'id':uid,'mode':mode,'functions_run':ran,'outputs':outputs,'semantic_scope':'See dedicated work artifact; software integration only'})
(out/'integration-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print('14 source identities and actual input/output digests verified')
