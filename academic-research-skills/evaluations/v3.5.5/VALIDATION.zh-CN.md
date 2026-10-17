# v3.5.5 研究主线、真实实验与正文验收

日期：2026-10-18。维护基线：v3.5.4，提交 `c87ac62e4ab4a19475e7089d1ed698df981e4a48`。本轮只修改 Skill 及隔离验收项目，没有修改、续跑或向原研究会话发送消息。

本版把交付依据从“流程有收据、文件有衔接”推进到“原问题有真实检验和有效回答，主要实验在正文说清，全文论证连贯”。文件检查和科学含义判断分别留证，没有把程序通过冒充科学认证。

## 实现与行为

| 需求 | 实际实现及验收 |
|---|---|
| 固定 A–B，不能用 C–D 结题 | 不可变研究约定绑定真实请求、对象、关系、范围、完成标准及问题 ID；旁支单独标记。修改标题或单元名不能替换原问题。新核心模块及流程测试拒绝未知问题、重新定向单元和以旁支替代必答问题。 |
| 恢复时记住全部主线 | compact resume 保留全部必答问题、当前回答状态、关键结果和下一动作；不只保留最近三项工作。测试加入更多更新的旁支后仍恢复原问题；损坏约定时恢复保存的问题并标为未知，不伪造答案。恢复摘要用已有文件观察定位，不重复全链重哈希。 |
| 区分运行和回答 | checkpoint 分离 execution、answer、validity、purpose，保留旧 outcome。正式结果必须来自实际当前设计/实验输出；失败、未运行、无充分信息、诊断或旧 inconclusive 不能自动变成可靠零结果。可靠零值及反向结果的正式记录可进入结果索引；可选扩展不增加完成门槛。 |
| 方法可调整，科学目标稳定 | 方法/主要实验修改保留 implementation 版本及理由，未改实验可复用。科学目标变更需要真实新用户指令，工具拒绝 assistant 伪引句。语言/格式只影响相关稿件；普通进度指令不使科学数据与实验全部失效。 |
| 诊断可以提前 | 新专业步骤默认 formal；diagnostic 可以使用已核验的必要部分数据及真实准备输出进行试跑。独立流程测试实际启动进程并留下结果；正式启动在数据未齐时拒绝，数据齐备后实际运行。诊断收据不能充当正式前序产物或主要实验答案。 |
| 实验进入正文 | 写作消费研究约定、执行版计划、全部主要结果及索引。交付定位问题结论和每项主要实验的 Methods/Results 实际段落；日志、错误章节、伪定位、替换稿件和未消费完整结果的审稿不能通过。支持嵌套小节与明确自定义章节，不强迫按固定关键词写论文。 |
| 合并科学与叙事审查 | 在既有 manuscript-review 中实际检查目标、结果、正文覆盖、衔接及内部流程污染。独立 Agent 阅读缺陷稿和科学材料后落实改稿；没有再设一套审批链。润色消费实际审稿稿件，审查真实变更跨度及含义；未变数字不能替代语义判断。 |
| 增量修订可衔接 | 真实流程暴露 citation 生成 v2 后的错误旧稿依赖，已修复为当前 writing→citation revision→review→expression；新增正反向测试，既不强加装饰性 v1 输入，也不接受旧 citation 掩盖新稿。 |

对应可执行测试见 [test_research_commitment.py](../../tests/test_research_commitment.py)（44 项）和 [test_alignment_flow.py](../../tests/test_alignment_flow.py)（17 项）。这些程序测试核对行为、实际文件/进程、身份、覆盖和版本；不依靠词频或人工填写 passed 判定科学含义。

## 真实官方数据完整流程

隔离项目见 [real-project/README.md](real-project/README.md)、[实际完成快照](real-project/closure-snapshot.json)及[验收摘要](real-project/acceptance-summary.json)。研究固定为：官方 UCI Wine 全部 178 条记录中 alcohol 与 color intensity 的总体关系，以及类别内/类别调整后的关系。没有转成分类、酒质预测或其他较容易的目标。

执行顺序为真实研究接入与计划、数据需求与来源选择、官方下载和本地核验、准备与诊断、本机正式实验及复算、科研图表、整稿写作、引用核查与科学审查、表达润色、真实 Word/PDF 导出和交付。官方必要数据及字典全部落地后开展正式实验。phase 最终为 completed / delivery，两个必答问题 Q1/Q2 已回答、E1/E2 为有效正式完成，没有待处理专业步骤或运行进程。

- 官方原始 `wine.zip` 6,038 字节；178 行、13 个化学变量及类别，类别数 59/71/48。没有为这项小研究下载整个数据池。
- 主要实验运行 6 个 OLS 拟合；稳健性另有 356 个逐条剔除拟合、1 个二次项拟合、1 个独立 QR 计算，共 364 个正式 OLS 解。另有 2 个诊断拟合，含首次失败试跑；未从实际执行计数中隐藏失败。
- 总体 Pearson r = 0.546364，斜率 1.560220；三个类别斜率为 1.094289、0.463852、1.527045。调整后斜率 0.940491，partial r = 0.318503。正文如实写出方向一致、大小不同；交互参考 p = 0.106 没有被解释成斜率相等。
- 从原始文件用中心化求和、类别去均值及独立 QR/HC3 复算关键结果。最大斜率差约 1.33×10⁻¹⁵，HC3 标准误差约 3.36×10⁻¹⁴；这属于同一数据的复算，不是独立样本复现。
- 两张主图及残差补充图保留 SVG、矢量 PDF、300 DPI PNG、实际绘图数据和代码。真实 LibreOffice/Poppler 导出五页 Word/PDF，最终五页逐页查看并核数值、表格和图。可读稿：[Markdown](real-project/manuscript-delivery.md)、[Word](real-project/wine-association-paper.docx)、[PDF](real-project/wine-association-paper.pdf)。
- 13 项专业步骤覆盖 11 种能力，按匹配入口实际使用 14 库池中的 6 个仓库。全部步骤实际读源并实施；仅数据准备、图检、写作一致性、引用格式四个步骤运行了相应来源函数。统计拟合、向量绘图、科学判断及润色是来源指导下的宿主适配，未虚报原生函数、外部模型或人类同行评审。逐项见 [source-use-summary.json](real-project/source-use-summary.json)。

本项目采用 NumPy/pandas 和现有本机工具，不为依赖缺失下载大型环境。来源 helper 的缺依赖失败、一次试跑变量遮蔽、初图重叠、Word 继承边框及实际修正均保留。最后一次差异覆盖对删除参考文献的边界句号定位不足，扩大实际引用跨度后完成窄幅 amendment，保留原收据；没有重跑科学实验或重复全稿审查。

资源快照：受管理下载 21,884 字节，交付前项目占用 11,158,227 字节，累计下载与项目占用各自低于 200,000,000,000 字节，并保留 10 GB 磁盘余量。浏览器/宿主响应传输量无法由本地工具独立计量，历史 preplan 字段保持 null；没有把未知计为零或声称严格测得所有网络字节。宿主精确 token 计量不可用，未声称 token 严格达标。用户未给总时间/token 硬预算，自定阶段时长仍可自主重排。

## 独立缺陷稿审查与实际修复

父任务制作 [review-input/manuscript.md](review-input/manuscript.md) 缺陷稿及真实原始数据、结果、代码材料；输入来源/哈希在 [challenge-input-manifest.json](challenge-input-manifest.json)。独立 Agent 以无父会话历史的 fork 接收普通审稿修订任务，未收到预设缺陷列表或标准答案。不是只检查评语字段，而是阅读其 [实际审查报告](independent-review/review-report.md)、[最终修订稿](independent-review/manuscript-revised.md)及 [原稿→修订稿差异](independent-review/original-to-revised.diff)。

实际修复了：换为分类/酒质目标；把未报告说成未开展，再写成“无关系”；E2 方法与结果仅留附件；p = 0.106 被写成相同斜率；章节按工作日志拼接；预算、安装、校验与接受状态进入正文。终稿完整表达总体、类别内和类别调整后结果，恢复科学论证顺序，保留方法、范围与真实未知。语义错误的修复有真实正文变化，即便原稿使用的数字来自真实结果，也没有被数字检查放过。

独立修订的 manuscript-review / manuscript-writing / final-expression 三项来源流程 finish/check 全部通过。写作来源原生一致性检查覆盖 82 项数值、4 组方法、4 组结果；最终表达除核对 117 个数字标记外，另行核对比较对象、方向、等效性、因果强度、结论范围和遗漏。14 个输入文件哈希未变。详见 [acceptance-report.md](independent-review/acceptance-report.md)及 [professional-check-summary.json](independent-review/professional-check-summary.json)。

该修订包有意仅提供既有材料，缺少原执行包的 dataset-spec 与派生 CSV，独立 Agent 如实指出不能声称新鲜端到端复算；没有为了审稿重跑模型。完整真实执行依赖位于上面的 real-project。独立 Agent 指独立任务上下文，不代表不同基础模型、外部专家或人类复核。

## 工程、来源与生成验证

| 检查 | 实际结果 | 证据 |
|---|---:|---|
| 全库回归 | 864/864；0 failure、0 error、0 skip | [regression.json](regression.json)、[运行记录](regression-run.log) |
| 根目录旧接口/结构兼容 | 30/30 | [compatibility.log](compatibility.log)；当前总控生成文件同步，旧 helper 按原接口保留 |
| 19 个独立 Skill 官方结构校验 | 19/19 | [entry-validation.json](entry-validation.json) |
| 维护源码生成一致性 | 1,324 个生成文件，无漂移 | [engineering-summary.json](engineering-summary.json) |
| 14 库全部索引与锁定文件 | 14 仓库、23 入口、416 文件绑定/407 唯一文件 | [source-validation.json](source-validation.json)；全部版本/内容核验，不冒充全部应用原生运行 |
| 入口与恢复上下文 | 各入口最多 799 字符；按需加载 | [context-scope.json](context-scope.json)，不是模型能力或精确 token 测试 |
| 可移植基础 smoke | 通过 | [portable-smoke.json](portable-smoke.json)；真实科研另由上述项目验收 |

本机回归使用 Python 3.12.14。发布提交的 GitHub Python 3.11/pdftotext 与 3.13/pypdf 矩阵、发布资产下载校验、一键安装隔离检查及 19 项本机替换的证明由发布事务保存；安装读取已发布包，不以工作目录冒充下载包。旧安装删除前核对新文件和原安装身份，保留无关 Skill、profile 配置与来源缓存。历史发行不改写。

初次失败没有删去或当作最终通过：简短入口缺少继承显式说明、入口长度、来源统计漏掉附加入口、诊断与引用修订衔接、证据收集对保留旧 helper 的误判均已修正。汇总见 [development-failures.json](development-failures.json)。

## 证据边界

[evidence-snapshots.json](evidence-snapshots.json)逐文件核对副本与隔离项目。收据保留实际测试时的绝对路径、哈希和失败记录，不能作为解压后当前运行状态直接续跑；另存副本、显式调整输入后再复现。快照排除 bytecode、锁文件和系统临时文件，未改写历史收据来制造可移植通过。

这次小型流程证明受测路径能固定问题、运行实际实验、将主要结果写入正文并修正具体语义缺陷，不证明所有领域、长周期无人科研或第三方应用都可用。Wine 数据未提供单位、概率抽样、批次和重复层级；小稿不声称因果、总体覆盖、等效性、原创性高度或可投稿完成。人类核验、作者批准、外部审稿与录用未进行；相应状态保持未知。
