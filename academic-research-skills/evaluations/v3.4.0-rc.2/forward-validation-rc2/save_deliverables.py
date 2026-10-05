from pathlib import Path
import json, hashlib, csv, datetime
root=Path(__file__).resolve().parent

a=root/'task-a'
a_text='''以下为基于所给合成观察的候选选题；价值和可行性都是待检验判断，未核实原创性。检验方案仅供后续选择，本次未检索文献、收集数据或开展实验。

| 可验证选题与预测 | 研究价值与受影响者 | 最低成本检验方案 | 失败条件与边界 |
|---|---|---|---|
| 1. 固定释放宽限期能否同时减少空置占位和迟到误释放？预测：若未到场者与短暂迟到者的到场时间分布存在可分离区间，就可能找到兼顾两类损失的宽限期。 | 直接量化等待找座者与短暂迟到者之间的代价，给规则选择提供依据。 | 若以后获得现成的匿名预约起止时间、实际签到时间和候补需求记录，可离线比较若干宽限期。以当前规则和不提前释放为比较基线，报告可释放的空座分钟、实际迟到却被释放的预约比例，并分开列示，不先赋任意权重。当前未提供日志，不能计算。 | 若任何空座改善都伴随超过管理方事先允许范围的误释放，或到场记录误差大于宽限期差异，则不能支持“兼顾”的假设。没有候补需求时，释放分钟也不能等同于新增实际使用。 |
| 2. “临时迟到确认”能否保留必要宽限，同时识别最终未到场者？预测：若迟到者通常能及时确认而未到场者较少确认，确认状态可能帮助区分两类预约。 | 针对迟到者的权益和管理员识别成本，检验是否有比统一缩短宽限期更低误伤的判别信息。 | 首先检查既有系统是否已有确认状态与最终签到记录；若有，仅以现成匿名记录做交叉表，比较有无确认者的最终到场情况。没有该功能或记录时，最低成本只能核查信息是否可获得；以后是否试用功能需要另行研究执行授权。 | 若未到场者也普遍确认，迟到者因无法及时操作而不确认，或确认记录不能和最终到场对应，则判别价值不足。即使确认与到场相关，也不能据此认定上线后能减少占位。 |
| 3. 释放规则的价值是否取决于时段的候补需求？预测：同样的未到场占位，在供不应求时段造成更多可避免的找座损失，而低需求时段提前释放的收益有限。 | 让规则收益与实际受影响人数相联系，判断是否值得采用分时规则及承担维护成本。 | 若以后获得现成的匿名时段容量、占用和候补记录，按预先规定的需求分层，比较未到场占位分钟与未满足需求同时发生的程度；以全时段统一规则为简单基线。先检验损失是否集中于特定时段，暂不预测学生在新规则下的行为。 | 若需求层之间差异很小，候补记录严重漏记，或损失集中模式不稳定，则分时规则的理由不足。若统一宽限期已达到相同目标，应优先简单规则。 |

建议先选题1：它最直接对应已有矛盾，也便于将两类损失放在同一张表中比较；前提是能取得可靠的签到与候补记录。若只有容量和时段记录，选题3更可行。选题2依赖额外的确认状态，当前成本与可行性最不确定。

三个题目都从具体困扰出发：谁在等待、谁会被误释放、规则增加了多少操作负担。现有两条观察不能确定问题规模，也不能证明某种规则有效；后续应先确认数据可用性和可接受误伤范围，再决定是否投入研究。
'''
(a/'deliverable.md').write_text(a_text)
(a/'professional-work.md').write_text('''本次从 Orchestra brainstorming-research-ideas 入口应用 F1、F3、F8 三个适合当前材料的视角。
F1：问题优先。受影响者为找座者、短暂迟到者和规则管理者；问题规模未知，不能把占位观察写成已证明的重大损失。
F3：列出空座可用性、迟到容忍、低操作负担、可解释规则、时段适配五项目标；效率与误伤、识别信息与操作负担、适配与简单规则三组张力产生候选。
F8：换位考察找座者能否真正得到释放座位，迟到者是否被误释放，管理者是否有可用日志、维护与解释成本。
实际候选清单：固定宽限期；迟到确认；分时规则；预约提醒；候补队列；重复未到场惩罚；押金；超售；预测模型；自助取消。后三类可能增加复杂度或误伤，提醒/候补/自助取消缺少当前材料中的行为机制证据，暂不优先。最终选择前三个，与用户要求的三个选题对应。
收敛筛选：每题有具体受益者、可反驳预测、最简单比较方案；没有日志则不能实施最低成本检验。未把现成数据关联写成新规则的因果效果。候选选题范围不运行两周试验、不搜最强近邻、不核实原创性。
实际所得：deliverable.md 的三行比较与推荐。所有检验均为未来方案，无数字或研究结果新增。
''')

b=root/'task-b'
paragraph='在这份合成示例中，20个预约中有4个未到场：提醒组为10个预约中1个，对照组为10个中3个。由于没有随机分组记录，也未进行显著性检验，这些数据仅作描述，不能据此确认提醒的因果效果、统计显著性或对所有学校的适用性。'
(b/'deliverable.md').write_text(paragraph+'\n')
claims=[('C001','numeric','在这份合成示例中，20个预约中有4个未到场：提醒组为10个预约中1个，对照组为10个中3个。'),('C002','method','没有随机分组记录，也未进行显著性检验。'),('C003','interpretive','这些数据仅作描述，不能据此确认提醒的因果效果、统计显著性或对所有学校的适用性。')]
(b/'draft-with-evidence.md').write_text('# 合成示例改写草稿：人工核验未完成\n\n'+'\n'.join(f'{t} [claim:{cid}] [evidence:E001]' for cid,k,t in claims)+'\n')
source={'schema_version':'1.0','sources':[{'authors':[],'confidentiality':'public','evidence_id':'E001','identifiers':{'doi':'','isbn':'','pmcid':'','pmid':'','url':''},'locator':'本任务 materials.md 第1行（合成测试材料）','source_type':'other','title':'用户提供的合成自习室预约示例','verification':{'source_opened':False,'status':'unverified','verified_by':'','verified_on':''},'year':None}]}
(b/'source_manifest.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
with (b/'claims.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['claim_id','section','claim_kind','claim_text_sha256','evidence_ids','verification_status','uncertainty','analysis_intent'])
 for cid,k,t in claims:w.writerow([cid,'results',k,hashlib.sha256(t.encode()).hexdigest(),'E001','unverified','not_estimated','descriptive'])
facts=[]
for i,(label,n,d) in enumerate([('all',4,20),('reminder',1,10),('control',3,10)],1):
 facts.append({'fact_id':f'N{i:03}','concept':'未到场预约数','section':'results','value':n,'unit':'预约','numerator':n,'denominator':d,'sample_size':d,'analysis_set':label,'evidence_ids':['E001']})
cons={'schema_version':'1.0','numeric_facts':facts,'methods':[{'analysis_intent':'descriptive','method_id':'M001','name':'仅转述用户提供的合成计数，不新增分析','outcome_ids':['O001'],'protocol_status':'not_applicable'}],'results':[{'analysis_intent':'descriptive','evidence_ids':['E001'],'method_id':'M001','outcome_id':'O001','reported_sections':['results'],'result_id':'R001','sample_size':20}]}
(b/'consistency_manifest.json').write_text(json.dumps(cons,ensure_ascii=False,indent=2)+'\n')
(b/'professional-work.md').write_text('''证据提纲：E001=用户提供的合成材料。C001/N001-N003是总体和两组未到场计数；C002是缺少随机分组记录与未做显著性检验；C003是基于这些缺口的结论边界。目的仅为清晰简洁改写结果段。
实际改写：删除“证明”“显著减少占位”“适合所有学校”，保留六个给定计数与分母，不计算百分比、效应量、P值或置信区间。未到场数不等于占位时长，原文的占位效果表述不能由材料支撑。
结果与方法核对：10+10=20；1+3=4；总样本与组别分母一致。没有随机分组记录不等于已证实没有随机分组，因此保留原限定。没有显著性检验不表示检验后“不显著”，不新增这种结论。
人工核验状态：未完成；没有登记人类核验者，未设 submission_ready。evidence_workflow.md 允许草稿保持不完整和不确定，因而提供基于给定记录的改写草稿。此次不是投稿、全文撰写、伦理或作者声明审查；未启动这些流程。
范围处理：没有引入上游指南的自引文献，因为用户要求不扩展结果段且未授权外部研究；上游软件版本记录在来源回执，不构成文献核实。
实际审查输出见一致性检查记录；一致性工具不验证源是否真实、不验证因果，也不替代人工核验。
''')
for key,actions,func in [('a',[
 ('21-research-ideation/brainstorming-research-ideas/SKILL.md','Identify pairs that are commonly treated as trade-offs','将空座可用性和迟到误伤作为成对目标，形成宽限期题目而不承诺存在双赢阈值。','deliverable.md','固定释放宽限期能否同时减少空置占位和迟到误释放？'),
 ('21-research-ideation/brainstorming-research-ideas/SKILL.md','Maintain a written list of all candidates, even rejected ones','记录十个实际考虑的候选及按复杂度、材料支持程度收敛的理由。','professional-work.md','实际候选清单：固定宽限期；迟到确认；分时规则；预约提醒；候补队列；重复未到场惩罚；押金；超售；预测模型；自助取消。')],False),('b',[
 ('skills/scientific-writing/references/writing_principles.md','Match the strength of each verb to the design and evidence.','将证明和普适性结论改为描述性报告，保留所有提供的数值与原限定。','deliverable.md','这些数据仅作描述，不能据此确认提醒的因果效果、统计显著性或对所有学校的适用性。'),
 ('skills/scientific-writing/references/evidence_workflow.md','A draft may remain\n  incomplete and uncertain.','保存来源和声明对应关系，不虚填人类核验者；交付是局部改写草稿而非已验证稿。','professional-work.md','人工核验状态：未完成；没有登记人类核验者，未设 submission_ready。')],True)]:
 d=root/f'task-{key}';start=json.loads((d/'start.json').read_text())
 report={'step_id':start['id'],'scope':'requested_step','omitted_required_work':[],'functions_run':func,'actions':[{'source_file':src,'source_excerpt':excerpt,'applied':applied,'output':str(d/out),'output_excerpt':out_ex} for src,excerpt,applied,out,out_ex in actions]}
 (d/'work-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Saved actual candidate comparison, revision, intermediate work and evidence records.')
