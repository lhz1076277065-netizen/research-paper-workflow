from pathlib import Path
import json, csv, re, hashlib, sys
root=Path(__file__).resolve().parent.parent
report='''# 校园预约提醒与未到场记录：合成汇总数据描述性演示

**草稿状态：合成数据演示，供写作与审查；尚未完成人工科学核验及投稿审批。**

## 摘要

本报告以用户提供的合成校内预约汇总材料，演示如何报告分组未到场记录，不评价真实校园提醒政策。 [claim:C001] [evidence:E001]
材料共涉及20条预约记录，提醒组10条中未到场1次，对照组10条中未到场3次。两组未到场比例分别为10.0%和30.0%，提醒组减对照组的描述性差值为−20.0个百分点。 [claim:C002] [evidence:E001,E002]
随机分组、显著性检验和因果识别均未开展，因此上述差异不能用于判定提醒的因果效果或统计显著性。 [claim:C003] [evidence:E001,E002]

## 目的与材料

目的在于展示同一二元结局在两组汇总记录中的分布，以及现有证据允许的解释范围。 [claim:C004] [evidence:E001,E002]
实际收到的是分组汇总计数，未收到逐条预约记录；“20条记录”不能解释为“20名独立参与者”。提醒内容、发送时间、分组机制、重复预约、观察期间及未到场判定口径均未提供。 [claim:C005] [evidence:E001,E002]
“提醒组”和“对照组”仅沿用材料标签，不代表已经实施随机对照试验。 [claim:C006] [evidence:E001]

## 方法

以预约记录为描述单位，按“未到场次数÷该组预约记录数×100%”计算未到场比例，再以提醒组比例减去对照组比例计算百分点差。 [claim:C007] [evidence:E002]
分析只进行汇总计数一致性与比例核算，没有个体数据清洗、缺失值填补、显著性检验、置信区间估计、混杂调整或因果识别；也未开展追加实验。 [claim:C008] [evidence:E002]

## 结果

| 组别 | 预约记录数 | 未到场次数 | 未到场比例 |
|---|---:|---:|---:|
| 提醒组 | 10 | 1 | 10.0% | [claim:C009] [evidence:E001,E002]
| 对照组 | 10 | 3 | 30.0% | [claim:C010] [evidence:E001,E002]
| 合计 | 20 | 4 | 20.0% | [claim:C011] [evidence:E001,E002]

表中分母为预约记录数；合计比例由合计未到场次数除以合计记录数得到。 [claim:C012] [evidence:E002]
提醒组的未到场比例比对照组低20.0个百分点；这是对本组合成汇总值的描述，不能写成“提醒使未到场减少20%”。 [claim:C013] [evidence:E002]

## 解释与限制

现有材料支持“两个组标签下的未到场比例不同”这一描述，不支持干预效果、统计显著性、总体差异或政策成效结论。 [claim:C014] [evidence:E001,E002]
未随机分组且缺少组间背景资料，无法排除选择差异和混杂；无逐条记录，不能检查独立性、重复预约与记录错误。合成数据本身也不提供真实校园总体的经验性证据。 [claim:C015] [evidence:E001,E002]
没有进行显著性检验，因而不能报告“显著降低”，也不能报告“无显著差异”。 [claim:C016] [evidence:E001,E002]

## 结论

在本组合成演示材料中，提醒组和对照组未到场比例分别为10.0%和30.0%，描述性差值为−20.0个百分点。报告到此收束；现有证据不支持因果或显著性判断。 [claim:C017] [evidence:E001,E002]

## 可复核材料与声明

本次核算使用Python标准库脚本；原始用户汇总、核算脚本、JSON结果与命令轨迹保存在同一交付目录的inputs、evidence及logs中，可在本地复算。 [claim:C018] [evidence:E002]
没有使用真实个人资料，也没有开展真实参与者招募或新实验；本报告不填写伦理批准编号、知情同意、资助、利益冲突或作者贡献的假定内容，这些正式声明的适用性与内容仍待负责作者确认。 [claim:C019] [evidence:E001,E002]
报告由当前Codex Agent按本地专业来源流程辅助起草；使用了K-Dense scientific-agent-skills缓存中的statistical-analysis和scientific-writing入口，固定commit为154988403bb5a18e9d3c0ce4e6d5e2e4b184a298。人工核验和目标期刊AI政策审查尚未完成。 [claim:C020] [evidence:E003]
上游缓存给出的软件引用为：Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065；此书目信息未联网核验，正式引用前需核验。 [claim:C021] [evidence:E003]
'''
(root/'outputs/short-report.zh.md').write_text(report)
source={'schema_version':'1.0','sources':[]}
for eid,title,loc,stype in [('E001','用户提供的合成预约汇总与任务边界','inputs/provided-materials.json；inputs/request.md','other'),('E002','本次实际描述性核算','evidence/descriptive-results.json；evidence/analysis-note.md；evidence/descriptive_analysis.py','other'),('E003','K-Dense本地专业来源与调用收据','evidence/analysis-start.json；evidence/writing-start.json','other')]:
    source['sources'].append({'evidence_id':eid,'title':title,'authors':[],'year':None,'source_type':stype,'identifiers':{'doi':'','isbn':'','pmcid':'','pmid':'','url':''},'confidentiality':'public','locator':loc,'verification':{'source_opened':True,'status':'unverified','verified_by':'','verified_on':''},'agent_check':'当前Agent已打开材料并核对；不冒充具名人工核验'})
(root/'evidence/source_manifest.json').write_text(json.dumps(source,ensure_ascii=False,indent=2))
headers=['claim_id','section','claim_kind','claim_text_sha256','evidence_ids','verification_status','uncertainty','analysis_intent']
with (root/'evidence/claims.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=headers);writer.writeheader()
    section=''
    for line in report.splitlines():
        if line.startswith('##'):section=line.lstrip('# ')
        m=re.search(r'\[claim:(C\d+)\].*\[evidence:([^]]+)\]',line)
        if not m:continue
        clean=re.sub(r'\[claim:[^]]+\]|\[evidence:[^]]+\]|\[@E[^]]+\]','',line)
        writer.writerow({'claim_id':m[1],'section':section,'claim_kind':'numeric' if re.search(r'\d',clean) else 'factual','claim_text_sha256':hashlib.sha256(' '.join(clean.split()).encode()).hexdigest(),'evidence_ids':m[2].replace(',',';'),'verification_status':'unverified','uncertainty':'仅合成描述；人工核验待完成','analysis_intent':'descriptive'})
outline='''# 证据提纲及范围判断

E001为用户汇总和任务边界；E002为实际核算；E003为本地专业入口及归属。当前Agent已核对，具名人工核验状态保持unverified。
目的/材料：C001、C004—C006→E001/E002。方法：C007—C008→E002。结果：C002、C009—C013→E001/E002。解释/结论：C003、C014—C017→E001/E002。声明/工具：C018—C021→E001/E002/E003。
不是随机试验，不使用CONSORT符合性声明；未指定期刊且不联网，当前官方指南和作者须知未核验。未开展文献综述、原创性查新或追加实验；它们不属于本次局部任务。
只以本地分组计数拟稿。待解决的是人工核验、作者和适用声明、正式投稿目标；不把这些未完成事项伪写成已批准。
已复核摘要、方法、表格和结论的分母/比例/差值一致，并保留未知信息。
'''
(root/'evidence/evidence-outline.md').write_text(outline)
manifest={'schema_version':'1.0','methods':[{'method_id':'M001','name':'分组计数与未到场比例核算','analysis_intent':'descriptive','outcome_ids':['O001'],'protocol_status':'descriptive_scope_user_supplied'}],'numeric_facts':[],'results':[{'result_id':'R001','method_id':'M001','outcome_id':'O001','analysis_intent':'descriptive','sample_size':20,'evidence_ids':['E001','E002'],'reported_sections':['摘要','结果','结论']}]}
for section in ['摘要','结果','结论']:
    for j,(concept,numerator,denominator,value) in enumerate([('提醒组未到场比例',1,10,10.0),('对照组未到场比例',3,10,30.0)]):
        manifest['numeric_facts'].append({'fact_id':'N'+str(len(manifest['numeric_facts'])+1).zfill(3),'concept':concept,'section':section,'analysis_set':concept[:3],'value':value,'unit':'percent','numerator':numerator,'denominator':denominator,'sample_size':denominator,'evidence_ids':['E001','E002']})
(root/'evidence/consistency_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Created Chinese draft, evidence outline, source manifest, claim hashes, consistency manifest.')
