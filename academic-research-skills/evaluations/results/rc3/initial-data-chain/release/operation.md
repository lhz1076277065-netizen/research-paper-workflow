# 独立合成任务操作记录

本记录含评估身份与实施版本；科学稿件、图注与图内没有这些身份或 Skill 版本。全部测量与稿件属于 SYNTHETIC 开发夹具，不是真实研究、真实论文成果或投稿完成。

## 输入与隔离范围

唯一请求为 `transfer-suite/requests/chain-b.release.0.json`，专属输出为本目录。使用该请求冻结的 `research-paper-workflow` 及按需能力，入口版本 3.2.0-rc.3，入口 SHA-256 为 `795e1046ad1ae9a52b302fda9029b8c0ca45d554354afbdc92c2e6bba9acda01`。冻结能力目录为手工评估组合，没有声称原生自动发现。未读取其他请求、其他组答案、维护源或先前结论；未启动子代理、其他模型/宿主、全局安装或外发消息。原始输入保持只读，全部新增文件均在本专属输出目录内。

请求 JSON 和共同选项是控制输入，直接读取一次；冻结项目、原始 README/candidates 和所选专业资源的必要文字读取通过指定 `run_host.py read` 完成，记录在 `resource_reads.jsonl`。39 次成功资源读取涉及 35 个不同路径：project 16、material 2、professional 21。部分首次批量结果在显示端被截断，必要片段随后按行范围回读；记录保留真实重复读取。没有把文件字节或显示字符折算为 token。

## 原始来源获取与准备

选择 `paired-measurements-v1.zip`，符合原始配对测量对象；候选清单声明镜像与其同摘要，因此不作为独立重复；不同代理测量未替代目标。将原始 ZIP 复制到 `raw/original.zip`，校验 SHA-256 `078a354c60fa96ee7ceedca955517176765f7406bd409dec7512337f59018ef4` 后安全解压。`archive_receipt.json` 与 `derived_member_reads.jsonl` 保存原 ZIP 摘要、成员名称、成员字节摘要及实际完整读取范围 [0,n)。解出成员直接读取，未强行以 reader 的 material 模式读取请求清单之外的衍生成员。

`prepare.py` 实际执行事件复制去重、显式 score/subscore 换算、按观测日期选择有效元数据、单位/方法内技术重复均值和完整配对检查。43 原始行变为 41 独特事件、16 单位方法均值和 8 个独立配对单位。原始数据与历史元数据均保留。

## 专业实施与实际作用范围

| 所选来源与固定版本 | 实际执行及最终产物 |
|---|---|
| Haojae/scipilot-figure-skill；commit `43098ddb9e6a6d142218540c114f9ed38922fc42` | 读入口、选图框架、误差棒配方、避坑与视觉/形式核查；实际调用 `profile_data`、`setup_style`、`render_preview`、`audit_layout`、`export_figure`、`check_figure`；参与本稿主图选图、制作、标签修订、最终 PNG/灰度读图和导出 |
| K-Dense-AI/scientific-agent-skills；scientific-writing 2.1；commit `65d6e786832e2c52832713117bbbf5096b56f77f` | 当前 Agent 应用完整写作入口与证据/IMRAD/表达参考；形成全文初稿、终稿、来源与主张记录、方法结果核对和缺失状态；未声称运行其可选 CLI 或取得人类验证 |
| Adkid-Zephyr/anti-defensive-writing-Skill；英文入口；commit `102c8b21acf5eda3a0aef3d9779a65db646c8980` | 当前 Agent 对全文的标题、摘要、引言、讨论、结论及冗余过程表达进行证据保持整理；保留修订前稿、差异与全文语义核对 |

专业版本来自提供的共享固定缓存；本 Agent 核对所选入口字节摘要，没有另外查询这些仓库的 GitHub HEAD。`professional_selection.json`、`professional_calls.jsonl` 保存选中入口、实际代码调用、输入输出、版本摘要、耗时或未知状态。绘图流程不止于 export 函数。

适配标记均为 `adapted_in_host`。pandas 3 字符串类型在上游 profiler 中可能被判断为 unknown，故显式声明 stratum 为分类、unit_id 为标识对象。图尺寸由用户的 180 × 100 mm 要求控制，不据通用期刊预设宣称投稿合规。SVG/PNG 导出使用 `tight=False` 保留画布；灰度预览从最终 PNG 生成。写作采用冻结项目的证据保持约定，没有采纳上游隐藏不利结果、换主指标或重新定义有利比较的规则。原来的第二层反例、样本构成参照、目标零包含区间和影响点结果均保留。

为了满足所选写作来源的归属要求，公开打开 `https://arxiv.org/abs/2609.00065` 核对软件论文标题、五名作者、年份、DOI 与当前书目记录 v2；未发送材料或稿件，未读取其全文，也未把该论文当作合成 score 结果证据。稿件的软件归属引用与 `bibliographic_receipt.json` 对应。

## 分析、验证与交付

`analyze.py` 保留原配对单位，按固定 0.8/0.2 目标权重执行全部 65,536 个分层经验重抽样组合；同时计算同一对象的 0.5/0.5 参照、8 个固定权重删一单位检验与构成敏感性。`verify.py` 从原 ZIP 独立使用 Fraction 分数运算与计数卷积复核准备、所有区间、敏感性和图稿数值。此独立计算方法不代表外部科学重复。

2026-09-30 15:11:32.354673 至 15:11:34.959729 UTC 实际执行 `reproduce.py`，prepare/analyze/figure/verify 四阶段均退出 0；各阶段耗时之和为 2.603722 秒，原始日志见 `execution_log.jsonl` 及各 `*.execution.log`。最终数值：目标 A−B = -0.20，条件性区间 [-0.65,+0.25]；样本构成参照 +1.00；两层均值 -1.00、+3.00。12 类数值检查通过，语义核对保留比较对象、因果强度、条件、分母和反例。该状态仅适用于合成计算交付。

主图为 180 × 100 mm 画布；实际 SVG 序列化尺寸为 179.999999833 × 100.000000025 mm，PNG 为 2125 × 1181 像素、名义 300 dpi。SVG 文字可编辑且没有嵌入位图。实际预览修订及最终颜色/灰度读图见 `visual_review.md`。完整稿件为 `manuscript.md`，前稿和差异同时保存；`caption.md`、`results.json`、`figure_source.csv`、`fact_check.md/json`、`source_manifest.json` 和 `claims.csv` 连接最终成果与证据。

初次把控制请求交给 project reader 被拒绝为 outside frozen Skill，随后只直接读取已获指令的唯一请求；一次编排 JavaScript 括号错误发生在发出读取调用之前；一次 SVG 检查容差 1e-8 mm 过严，因点单位六位小数序列化产生约 1.7e-7 mm 差异，改为 1e-6 mm 后通过。没有为这些技术修复改变原始数据、科学目标或统计结果。

## 时间与费用

2026-09-30 15:20:13.945896 UTC 保存的实际记录：首个成功资源读取 14:35:14.657475 UTC，至记录时间的可观察窗口为 2699.288421 秒。该窗口不是精确 Agent 派发时刻或完整 turn 墙钟。前者不可获得，标记未知。输入、缓存输入、输出、总 token 与费用均不可从本任务 API 获取，保持 null/未知；没有估算或用工具输出字数冒充用量。详见 `operation_metrics.json`。

真实世界的抽样/纳入概率、测量有效性、独立性验证、可迁移性与因果设计未提供；人类科学验证、署名/投稿批准和真实研究成果均未声称。当前合成任务的初版实际产物已完成，可按后续局部要求续接，不必从头重做。
