from pathlib import Path
import csv, datetime, hashlib, json

ROOT=Path(__file__).resolve().parent; BASE=ROOT.parent; LIB=BASE/'library'
cases=json.loads((BASE/'cases.json').read_text())
(ROOT/'original_requests.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2))
def dump(path,obj):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2))

bike=json.loads((ROOT/'direction-no-data/result.json').read_text())
human=json.loads((ROOT/'human-collection/result.json').read_text())
changes=list(csv.DictReader((ROOT/'human-collection/changed_tasks.csv').open()))
control=next(x for x in changes if x['task_id']=='1882')
assert 'computer technology' in control['before'] and 'computer technology' in control['after']
assert control['old_date']==control['new_date']
dump('human-collection/negative_control.json',{'task_id':'1882','operation':'Compare action and tool in both real archive statements, then check update dates','input':control,'observation':'communication action and computer technology remain; population wording changed; update date unchanged','judgment':'Automation keyword plus wording change is insufficient evidence of a new technological task; negative control falsifies this naive indicator in the pilot','not_claimed':'No causal workplace change or validation of all 44 changes'})

citation='在第六个月评估时，两组参与者的表现存在组间差异。'
reason='记录只支持第六个月这个时点，不能写持续；未提供差异方向，不能写提高。随机分组不等于实际依从，不能据此描述依从干预者的效果。该记录为合成例子，不补造论文身份。'
paragraph='在白葡萄酒样本的留出分区上，模型误差为 0.757 分，低于训练均值基线的 0.898 分。这一比较支持模型在该留出分区上降低预测误差；尚未做跨来源验证，其跨来源泛化能力仍待检验。'
(ROOT/'citation-time').mkdir(exist_ok=True);(ROOT/'citation-time/revision.md').write_text(citation+'\n\n'+reason+'\n')
(ROOT/'focused-paragraph').mkdir(exist_ok=True);(ROOT/'focused-paragraph/revision.md').write_text(paragraph+'\n')

texts={
'direction-no-data':'''已实际取得 UCI Bike Sharing 原始压缩包、Readme 字典、hour.csv/day.csv 和 9 行展示样例。来源是 [UCI 数据页](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset)，持久标识 [10.24432/C5W894](https://doi.org/10.24432/C5W894)，当前页面标 CC BY 4.0；复用须署名，并保留 Readme 要求的原始论文引用。数据覆盖 Washington DC Capital Bikeshare 2011–2012。

实际解析为 17,379 个系统小时、731 个日期；cnt=casual+registered 的全部记录恒等检查通过。网页展示的 17,389 与原始文件不一致，本交付以文件实际解析数量为准。weathersit 1/2/3/4 的小时数分别为 11,413/4,544/1,419/3；类别4只有3个日期，2011年1小时、2012年2小时。时间键为 dteday+hr；原文件未明确时区/DST规则。结局是实际租借数量，不能视为完全未受供给限制的潜在需求。独立推断单位应按日期或连续天气事件阻断，小时行不是独立重复。天气为同小时观测而非提前发布预报；casual、registered 是结局分量，禁止用于预测 cnt。仅凭此数据无法可靠估计类别4的条件覆盖率，更不能宣称极端天气普适可靠。

Readme 与现网页在 season 映射、temp 归一化说明上存在不一致；本轮保留原值，未将它们误解为已核实物理单位。适配判断：支持系统层级、历史天气条件下的预测/校准先导；不支持站点需求、工况4的可靠验证或真实提前天气预报部署。

具体路线：研究“天气事件稀疏且连续相关时，带有效事件数诊断的分组校准能否避免全局区间在恶劣天气下过度自信”。以仅使用当时可得滞后需求和日历的季节基线为起点，比全局残差区间、天气分组区间、向全局收缩的分组区间；禁止把天气条件估计称真实提前预测。按整段天气事件进行滚动训练、校准、验证，比较覆盖率、区间宽度、最差天气组误差和拒绝发布比例，同时报告事件数与块自助不确定性。类别4仅作支持不足/拒绝发布示例；正式可靠性主张需取得更多独立恶劣事件。

最近邻 [Rochas 等全文 III–IV](https://arxiv.org/html/2412.03307v1) 用天气、时间和交通背景预测 Lyon OD 点需求并比较降雨子集；本候选改变的是相关稀疏事件下的区间校准与可验证边界，尚未证明新颖性，也未运行预测模型。下一项最有信息价值动作：先划分天气3的连续事件并计算各滚动分区的有效事件数，再执行全局区间的按事件覆盖审计；它决定分组校准是否有足够信息，而非先加深模型。''',
'human-collection':'''重要问题仍是自动化如何重组工作任务；本轮转为“公开职业任务记录中的技术相关变化，有多少是任务内容重组，有多少只是数据库编辑/更新”。它回答可测量的职业描述变化与测量有效性，不回答工人主观体验或自动化对真实工时的因果效应。

材料路径已执行：[O*NET® 版本档案](https://www.onetcenter.org/db_releases.html) 的 28.0（2023-08）与29.0（2024-08）免费 text 包，实际保存任务原表、职业表、版本字典、许可。依据 [许可页 Previous Versions](https://www.onetcenter.org/license_db.html)，旧版本可按 CC BY 4.0 使用，署名 USDOL/ETA 并注明28.0/29.0；本交付生成了差分，并非 USDOL/ETA 审定。字典将 Date 定义为更新日期；发行年月不能当每项任务的变更发生时间。

本轮按职业代码+Task ID精确连接：19,281 与18,796行，共有18,778个共同键，其中44条文本变化、18条新增键、503条移除键。全部44条差分已查看；没有把新增/移除键直接当真实任务生成/消失。自动化词根的文本变化命中仅1条，真实 task 1882 两版都保留 communication 与 computer technology，变化是服务对象描述，更新日期都为08/2022。实际负对照因此推翻“自动化词命中且文本改变就代表技术任务改变”这个测量规则。代码、全部差分和负对照输入/输出均已保留。

电脑内可完成的核心证据和决定性验证：在更长版本面板中把动作、对象、工具及任务类型变化分别编码，按职业更新批次建立比较；数据库统一措辞变更是负对照，真实新增技术工具/操作且可由公开职业描述或软件文档交叉核实的记录是阳性候选。检验技术任务指标是否在删除编辑性变化、匹配相同更新频率和职业分类后仍成立；若不成立，贡献为纠正自动化任务指标的测量偏差。已有 [Consoli 等](https://pmc.ncbi.nlm.nih.gov/articles/PMC9746329/) 研究职业内部任务变化，本候选增量是可追溯版本编辑与技术任务变化的区分，不把“使用 O*NET”称首创。本轮只读其摘要定位，全文获取遇到验证码，未声称完成最近邻全文审查。

下一动作：读官方任务更新流程，优先验证本轮503条删除键是否来自补充任务筛选而非任务消失，再扩大版本面板。所有关键材料和判别均可免费在当前电脑取得和复算；本轮完成实证先导与负对照，尚未完成全职业测量验证或因果研究。''',
'theory-known-principle':'''原命题为假。取行随机矩阵 P=[[0,1],[1,0]]，有 P²=I，故 P^(2k)=I、P^(2k+1)=P；两子序列不同，P^n 不收敛。本轮以 Fraction 精确计算 n=0,…,6，断言通过，数值仅核实现，反例证明来自恒等式。

精确修正：有限行随机矩阵 P 的幂收敛，当且仅当其所有闭合不可约类都非周期。不可约不是必要条件，I也收敛。证明：将状态按暂态与闭合类排列，P=[[Q,R],[0,S]]，S为不可约闭合块的直和，ρ(Q)<1。每个非周期有限不可约块按标准马尔可夫链收敛定理有 S^n→Π。右上块为 Σ(k=0到n−1) Q^k R S^(n−1−k)；由 ||S^m||∞=1、Σ||Q^k||<∞，有限头逐项收敛且尾一致可控，极限为 (I−Q)^−1 RΠ；Q^n→0，所以全矩阵收敛。反之若存在周期d>1闭合类，将其按循环子类分组，固定起点在特定 n mod d 时转移到某子类的概率为1、其他余数为0；概率和不收敛，因此至少一个元素不收敛。暂态不存在时相应块省略。

这是已有有限马尔可夫链理论，参见 [大学课程 Finite Markov Chains, §1.3](https://www.netlab.tkk.fi/opetus/s38215/k04/Lectures/ch1.pdf)。本轮检索取得该定理摘要，PDF展开工具失败；不冒称通读全文。以上证明为当前Agent独立展开，不是新贡献。

进一步值得检验的方向：从有噪声转移计数得到“有限时域收敛保证”时，如何区分真正周期与近周期并计算信息需求。Pε=[[ε,1−ε],[1−ε,ε]]，0<ε<1 时极限为每行(1/2,1/2)，非平稳误差为 |2ε−1|^n/2；ε=0不收敛，ε=1则为I（公式此时测的是到均匀向量误差，并非不存在矩阵极限）。若可信集合含ε=0，无法对该集合给统一趋于零的速率；若ε被独立信息限制在[a,b]⊂(0,1)，统一速率r=max(|2a−1|,|2b−1|)<1。已实际计算ε网格的n=100误差，展示近周期的慢收敛。这仍是基线推演。潜在增量应落在稀疏转移估计的可证明证书与最小额外观测需求；下一步核现有置信集合/混合时间证书文献，再检验保留概率下界的覆盖与证书效率。''',
'equal-predictions':'''原请求未指定甲乙公式，因此本轮构造明确、可反驳的小型替代模型，不替用户未给出的实际机制作结论。甲为三角闭合生成的两个互不连接三角形；乙为跨群体整合生成的六节点环。两者6节点、6边，每个节点度2，度分布完全相同。

数字操作是单点种子传播干预：同步SI、传染概率1、无恢复，记录t=0…3感染数。对全部6个种子位置精确枚举。甲在t=3为3个，乙为6个，所有断言通过；同一图的6个种子是穷举条件，不是6份独立网络。输入图边、规则、代码及48行输出已保存。

改变的判断：度分布无法区分本模型对，但传播可达范围能区分；若实际传播远达跨群体，则削弱这版纯闭合甲。并未据玩具模型确认真实甲乙身份。若当前已有完整邻接矩阵，这对模型本来就能由连通性区分；只有当前观测限于静态度分布时才存在所设等价。实际网络需保留度、种子、传播预算和观测范围，并按真实甲乙动力学重做。''',
'initial-failure':'''开发集结果为新算法误差1.12、基线1.00，即平均误差高12%；资源2倍，即多100%。按当前平均误差和资源两项指标，新算法被基线支配，不应打开正式测试集来寻找翻盘。

最有信息价值动作：取得同一开发单元的配对预测/残差及耗时，先核同信息、分区、预处理、调参预算与指标，排除实现或评价不公平；随后按问题已有的困难条件审查配对误差，做去掉昂贵组件的消融。它能区分“实现有错”“组件无价值”和“平均劣势掩盖有意义边界”，比重复算整体均值有价值。正式测试保持封存。

本轮可实际完成的检验是信息充分性构造：已保存合成原记录并运行两个与1.12/1.00完全相容的情景——全部单元误差1.12，或者20%困难单元误差0.60、其余80%误差1.25；基线均为1.00。两世界均值都1.12，但前者无该边界优势、后者存在。断言通过，说明仅凭均值不能判断边界。它们是人为构造，绝不是补回的开发数据。

若贵组件拖累大多数单元，可发展只在训练/开发信息可判定的困难状态启用的门控或便宜近似，检验完整/去组件/同预算替代及门控误差与成本；若优势依赖事后看真值才可识别的亚组，该边界没有部署意义。若公平校验后无可信优势且不能降成本，保留负结果并停止此版扩展。由于未提供算法代码、单元预测或开发集，本轮没有真实消融、方差、显著性或改进数值。''',
'citation-time':citation+'\n\n理由：'+reason,
'focused-paragraph':paragraph,
'author-pending':'''当前交付状态：not submission ready；本轮完成了文件清点、来源缺口审计、可运行的缺文件检查及三队列交接。B顶层实际只有cases.json和snapshot.json，未提供源稿、冻结结果表、图或PDF；本轮不查看其他工程寻找替代稿件。故没有可真实核对的图注、摘要数字或当前源稿-PDF组合。sync_check.py已运行，准确标记四类材料缺失，没有将文件存在检查冒称内容同步通过。

科研队列：分析和证明“已完成”只来自合成请求，尚未在本轮独立复核；下一可执行动作是取得冻结分析输出与证明源，再核主要主张/条件及结果定位。

成果队列：图注对象、样本/条件、单位、误差与编号；摘要每个数值追到冻结结果；源稿版本/哈希与PDF导出对应，文本/数值一致后检查实际页面布局。上述三项均尚未验证，原因是材料未提供。收到真实材料即可继续，不以作者确认作为这些独立工作的前置。本轮已生成包含真实缺口和执行顺序的handoff.md及sync_audit.json，未生成伪稿或伪PDF。

外部事项：作者身份、顺序、机构、贡献、资助/利益冲突/伦理及其他必要声明待人工确认；未知项保留pending，不能填“无”。正式外发/投稿未执行。本轮未替作者确认，也未外发。'''
}

(ROOT/'author-pending/handoff.md').write_text(texts['author-pending']+'\n')
for case in cases['cases']:
    folder=ROOT/case['id'];folder.mkdir(exist_ok=True)
    (folder/'request.txt').write_text(case['request']+'\n')
    (folder/'response.md').write_text(texts[case['id']]+'\n')

intro='''# B 原生研究验收输出

八项请求在同一个原生Agent上下文执行，冻结库为 `native/B/library`，未编辑库；这不是八次独立模型试验。原始请求另存 `original_requests.json`，各目录保留 request.txt/response.md。使用当前Agent、宿主网络工具及免费Python标准库，无其他Agent、付费工具、外发或代作者确认。实际范围是数据取得/适配先导、公开任务版本分析、数学反例与修正证明、小网络区分检验、失败诊断的信息充分性检验、两项局部改写、缺材料状态审计；不是整篇研究或投稿准备完成。

可复算命令（Python绝对路径见execution.json）：`python3 output/run_checks.py`；`python3 output/sync_check.py`。前者复用已下载文件；重新取得来源用 `python3 output/acquire.py`。下载响应、大小与SHA-256见download_log.json。研究检验通过的范围不等于科学新颖性通过。
'''
parts=[intro]
for c in cases['cases']:
    parts += [f"\n## {c['id']}\n\n原始请求：{c['request']}\n\n{texts[c['id']]}\n\n产物：`output/{c['id']}/`；共用代码为 `output/run_checks.py`（需要计算的前五项）或 `output/sync_check.py`（交付审计）。\n"]
(ROOT/'outputs.md').write_text('\n'.join(parts))

common=['research-paper-workflow/SKILL.md','research-paper-workflow/references/provider-policy.md','research-paper-workflow/references/execution-handoff.md','research-paper-workflow/references/research-quality.md','research-paper-workflow/references/research-lifecycle.md']
special={
'direction-no-data':['data-discovery/SKILL.md','data-discovery/references/protocol.md','topic-novelty/SKILL.md','topic-novelty/references/protocol.md','research-design/SKILL.md','research-design/references/protocol.md'],
'human-collection':['research-intake/SKILL.md','research-intake/references/protocol.md','data-discovery/SKILL.md','data-discovery/references/protocol.md','research-design/SKILL.md','research-design/references/protocol.md'],
'theory-known-principle':['analysis-execution/SKILL.md','analysis-execution/references/protocol.md','analysis-execution/references/method-routing.md','topic-novelty/SKILL.md','topic-novelty/references/protocol.md'],
'equal-predictions':['research-design/SKILL.md','research-design/references/protocol.md','research-design/references/method-routing.md','analysis-execution/SKILL.md','analysis-execution/references/protocol.md'],
'initial-failure':['analysis-execution/SKILL.md','analysis-execution/references/protocol.md','research-design/SKILL.md','research-design/references/protocol.md'],
'citation-time':['citation-audit/SKILL.md','citation-audit/references/protocol.md'],
'focused-paragraph':['manuscript-writing/SKILL.md','manuscript-writing/references/protocol.md'],
'author-pending':['research-intake/SKILL.md','research-intake/references/protocol.md','manuscript-writing/SKILL.md','manuscript-writing/references/protocol.md']}
paths=sorted(set(common+['research-paper-workflow/references/computational-routes.md']+sum(special.values(),[])))
reads=[]
for p in paths:
    raw=(LIB/p).read_bytes(); s=raw.decode()
    reads.append({'path':str(LIB/p),'characters':len(s),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'guidance_read':True,'functions_run':False,'note':'Read via host cat; shared references reused in the same native context. Combined tool outputs sometimes truncated; manuscript/intake/novelty protocols and computational/method routes were subsequently re-read.'})
operations={
'direction-no-data':['Downloaded raw zip and provider page','Parsed full hour.csv','Checked target component identity and unique timestamps','Counted weather support by year/date','Saved representative rows and suitability/design assessment'],
'human-collection':['Downloaded two O*NET archives, dictionaries and license','Joined task tables on occupation+task ID','Produced all changed/added/removed rows','Read all44 wording changes','Executed task1882 negative control and update-date check'],
'theory-known-principle':['Constructed analytic period2 counterexample','Exact Fraction powers and assertions','Proved corrected iff condition using canonical block form','Evaluated epsilon family finite-horizon errors'],
'equal-predictions':['Saved two graph inputs and SI rules','Enumerated six seed locations for each graph','Verified identical degree distributions and different intervention outputs'],
'initial-failure':['Preserved aggregate synthetic record','Calculated 12% error and 100% cost increases','Ran two aggregate-compatible synthetic worlds','Specified paired development audit and ablation; test unopened'],
'citation-time':['Compared time/direction/adherence support with sentence','Saved original and exact local revision'],
'focused-paragraph':['Saved scope-preserving local rewrite','Checked 0.757,0.898,white wine,holdout and no external-validation statements'],
'author-pending':['Inspected supplied file inventory','Ran fail-closed missing-artifact audit','Saved scientific/artifact/external queues and not-ready handoff']}
limitations={
'direction-no-data':'No forecasting model, calibrated interval or independent-source validation run; only3 severe-weather observations; nearest-neighbor review partial.',
'human-collection':'Only two-version pilot and one negative control; no causal automation effect or validated whole-panel coding; nearest-neighbor full text CAPTCHA blocked.',
'theory-known-principle':'Known result and independent mathematical proof; not formalized or claimed novel; source PDF expansion failed.',
'equal-predictions':'Toy model mechanisms chosen because actual A/B equations were absent; no real-world attribution.',
'initial-failure':'Actual algorithm, paired residuals and developer data absent; no real ablation or significance analysis possible.',
'citation-time':None,'focused-paragraph':None,
'author-pending':'Source manuscript, frozen results, figures and PDF absent; numeric/caption/PDF synchronization cannot be performed; authors/declarations pending human confirmation.'}
entries=[]
for c in cases['cases']:
    folder=ROOT/c['id']
    entries.append({'id':c['id'],'request':c['request'],'response_path':str(folder/'response.md'),'guidance_files_reused':common+special[c['id']],'guidance_character_counts':{p:len((LIB/p).read_text()) for p in common+special[c['id']]},'research_work_done':True,'functions_run':c['id'] not in ['citation-time','focused-paragraph'],'operations':operations[c['id']],'artifacts':[str(p) for p in sorted(folder.rglob('*')) if p.is_file()],'not_completed_reason':limitations[c['id']],'status':'requested_local_work_complete' if not limitations[c['id']] else 'completed_with_explicit_scope_limit'})
artifacts=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p.name!='execution.json':
        raw=p.read_bytes();artifacts.append({'path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
dump('execution.json',{'version':'B frozen rc4','native_contexts':1,'subcases_are_independent_trials':False,'executor':'current native Agent','research_model':None,'library':str(LIB),'library_modified':False,'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'python':'/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3','original_cases_characters':len((BASE/'cases.json').read_text()),'read_files':reads,'shared_reads_deduplicated_characters':sum(r['characters'] for r in reads),'cost':None,'tokens':None,'cost_and_tokens_note':'Host token billing and cost were not exposed; no estimates invented.','downloads':json.loads((ROOT/'download_log.json').read_text()),'run':json.loads((ROOT/'run_log.json').read_text()),'subcases':entries,'artifact_manifest':artifacts,'external_actions':[],'paid_actions':[],'subagents':[],'free_software':'Python3.12.14 standard library; urllib,csv,zipfile,fractions,json','workflow_adaptation':'guidance_read and research_work_done separated from bundled functions_run; custom scripts executed, no frozen-library attached functions run; no external specialized Skill library loaded because the experiment restricts Skills to B/library.'})
print(json.dumps({'cases':len(entries),'artifacts':len(artifacts),'guidance_files':len(reads),'guidance_chars':sum(r['characters'] for r in reads)},ensure_ascii=False))
