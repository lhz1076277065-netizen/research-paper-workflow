# 完整本地数据到实验、图稿和润色

适用于用户要求完成数据驱动研究的总控任务。默认full采用local-data；局部写作/精读用focused，已有旧记录不追溯伪造数据就绪。确属理论等非数据任务可显式general，不能用它绕过完整实证研究的数据缺口。

## 工作顺序与实际出口

| 次序 | 实施与产物 | 对应阶段/必调能力 |
|---|---|---|
| 1 | 结合材料与近邻确定并绑定[稳定研究约定](research-alignment.md)，完成执行版计划：假设、竞争解释、方法、基线、划分、指标、必要实验与成本 | feasibility；design / research-design |
| 2 | 每项实验映射变量、标签、样本、时空/分辨率、独立验证材料；列齐所需数据及文件，估计下载/解压/衍生/临时峰值 | data / data-discovery |
| 3 | 联网查官方发布、采集方法、版本、覆盖、质量及许可，保存候选比较和选择依据 | data / data-discovery |
| 4 | 全部所需内容完整落到本机；可用官方子集，整包不可拆时有界下载整包。复用已核验本地文件 | data / data-discovery |
| 5 | 实际读取所有必要文件，核对完整性、变量/覆盖、缺失、单位、连接与泄漏，准备固定划分；已核验部分数据可先做显式诊断试跑 | data / data-preparation；诊断 / analysis-execution |
| 6 | 按执行版计划本机正式模型、基线、对照/必要消融和稳健性；保存代码、参数、真实结果/失败并复算关键结论 | research / analysis-execution、robustness-reproducibility |
| 7 | 真实结果→科研图、图表数据、绘图代码与可编辑源；核数值、单位、图注、实际渲染 | research / scientific-visualization |
| 8 | 研究约定、执行版计划、全部主要实验索引、真实结果与图→连贯全文；合并原问题回答、实验覆盖、科学、引用和语义审查，实质缺口回传 | manuscript / manuscript-writing、citation-audit、manuscript-review |
| 9 | 必调final-expression（现有anti-defensive-writing），另存润色稿，核事实/数值/引用/结论边界差异，再交Word/PDF、图源及数据代码复现包 | manuscript / final-expression；delivery |

专业调用均遵守[begin→读源→实施→finish/check](mandatory-professional-flow.md)，仍从指定14库选择匹配真实入口。各阶段不需要加载整库。方法草稿可早写，正式结果不预写；不规定实验必须胜出。数据不足、失败或复核缺口触发[自主解阻](phase-control.md#自主解阻与继续研究)，先修复或验证适配原问题的替代。自定配额可调整；200 GB累计下载/项目占用、实际用户预算和固定目标不自行变更。

## 一次规划全部必要数据

研究计划是已完成research-design的真实输出。进入data后先begin data-discovery，以当前计划为输入，读源实施数据需求评估，再创建不可变版本的dataset-spec-v1.json并用local_data plan绑定；清单属于这次专业步骤，随后来源选择和获取继续该步骤，全部完成后finish。若清单已经是design的真实输出可直接绑定。只列研究实际需要的全部内容，覆盖所有必要主分析/基线/外部验证，不能把可选大库添加为必需，也不能删掉缺失项装作齐备。例子仅示范结构：

```json
{"datasets":[{"id":"observations","purpose":"计划中检验H1及预先确定的验证","files":[{"path":"raw/observations.csv","format":"csv","required_columns":["subject","x","target"],"numeric_columns":["x","target"],"expected_rows":150}]}]}
```

CSV/TSV默认有表头；无表头显式header:false和columns（来自官方字典）。expected_rows、expected_bytes、expected_sha256只在有真实依据时提供，未知不填猜值。JSONL逐行读取；小JSON全解析。NetCDF/影像/Parquet等设format:external，用专业准备步骤实际执行适配读取器检查所需变量、维度和覆盖；大JSON用流式外部读取器。missing_values与allow_missing按实际数据约定设置；原数据缺失不等于自动放弃研究。

```bash
python3 scripts/phase_control.py --state project/phase.json init --scope full --objective '实际完整研究请求'
# 按阶段/必调流程先完成feasibility、design，并advance到data。
python3 scripts/professional_flow.py begin --capability data-discovery --phase project/phase.json --task project/request.md --input project/research-plan-v1.md --out project/discovery-start.json
# 读真实入口，评估数据需求，再写dataset-spec-v1.json。
python3 scripts/local_data.py --state project/phase.json plan --root project --spec dataset-spec-v1.json --research-plan research-plan-v1.md
python3 scripts/research_storage.py --root project plan --spec project/acquisition-plan.json
python3 scripts/phase_control.py --state project/phase.json storage --root project
```

沿[有界获取](data-acquisition.md)执行必要下载、重试与选择性解压。下载只用同一研究容量收据；传输累计不因清理或修改清单重置。来源选择/下载在实际data-discovery步骤内进行；保存官方元数据与候选选择报告作为该步骤输出，再逐数据集绑定：

```bash
python3 scripts/local_data.py --state project/phase.json source --dataset observations --metadata sources/official-metadata.md --selection sources/selection.md --started project/discovery-start.json --finished project/discovery-finish.json --publisher '真实发布机构' --version '真实版本/获取日期' --url 'https://official.example/dataset'
python3 scripts/local_data.py --state project/phase.json check --local-only
# 全部必要文件真实存在且来源已绑定后，begin data-preparation并实际清洗/检查。
# 外部格式的准备收据需把实际原文件作为输入，读取器产物作为输出：
python3 scripts/local_data.py --state project/phase.json inspect-external --started project/prep-start.json --finished project/prep-finish.json
python3 scripts/local_data.py --state project/phase.json check --refresh
# 数据全部通过且data-preparation已真实完成，才advance --stage research。
```

metadata/selection及spec/plan为project相对路径，started/finished为实际收据路径。source要求真实data-discovery输入包含当前计划或清单；来源真实性/科学覆盖需Agent核对，工具不作权威性证书。官方网页URL用于溯源，不能当本地数据。所有必需文件一项缺失就先修复；已有文件可复用，不重复下载。check失败保持研究active并给修复动作，不关闭整个目标。

## 实验、恢复与变更

begin的实际输入须包含上一步成果：模型接准备输出，复算接实验输出，图接实验/复算结果，写稿接稳定研究约定、执行版计划、全部主要实验结果索引、真实结果和图，审查接稿件及上述科学依据，润色接稿件与已有审查意见。重新实验后旧图/旧评审不能只凭完成状态继续移交；依据变化重做受影响部分。工具核对文件版本衔接，科学含义由专业工作核对。

data→research检查全部数据和准备收据；analysis-execution的run在启动进程前重核。全部必要数据齐备前，允许以purpose=diagnostic对已经核验的部分数据进行解析、假设、代码和成本试跑；同样先读来源并实际实施，结果仅作诊断，不能抵扣正式数据准入、正式实验或论文核心证据。正式purpose=formal仍在research使用全部必要本地数据。实验后依次完成robustness、visualization，才能进入manuscript；writing→citation/review→final-expression，完成后才delivery。不能用下载、导出、收据数量代替实际专业工作。

文件摘要分块计算，CSV/TSV/JSONL逐行核验。普通check可复用未变inode/大小/修改时间对应的已完整摘要与解析，结果明确标注此依据；--refresh重新全读，阶段出口和正式实验run强制使用。缓存统计不是防恶意篡改认证。恢复先看phase resume中的原问题及全部回答状态，再看当前清单，发现文件变化回到对应步骤，保持预算/容量历史，不重复所有前序研究。

专业输入/输出用不可变版本文件。不要把会持续更新的phase.json、.research-data.json或容量收据作为专业成果；需要引用时保存一次只读快照。原始数据变更时另存版本，保存原因，必要时reassess回design并重做受影响的计划，回data后local_data plan --revision-reason；保留原始证据与容量累计。未变材料的专业复核可复用，变化只重做受影响步骤；润色后做差异事实核对，不无限全稿复核。
