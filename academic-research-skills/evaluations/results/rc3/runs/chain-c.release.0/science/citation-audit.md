# 引文身份与语义支持核查

本轮只读取冻结 `references.json` 和 `source-availability.md`；没有再次访问 Crossref、出版社全文或数据库。材料记录的身份核验时间分别为 2026-09-30T13:54:17.025683+00:00 和 13:54:18.601266+00:00，不是本 Agent 新做的在线核验。当前纠正/撤稿/关注声明状态未查询，保持 UNKNOWN。

| 原引用 | 冻结身份记录 | 实际取得层级 | 原主张的语义判定 | 真正处理 |
|---|---|---|---|---|
| v2 [1] Efron (1979), 10.1214/aos/1176344552 | B. Efron；Bootstrap Methods: Another Look at the Jackknife；The Annals of Statistics；1979 | 身份元数据。原文全文、具体段落与实现未取得 | “文献证明本样本独立”“验证所有目标总体的此区间”不可核验且缺本设计证据；metadata 不能提供此支持 | 移除这两项担保和最终稿 Efron 书目。原记录保存在 baseline；§2.1 从给定单位记录说明采样对象，不改说读过原文 |
| v2 [2] Rosenbaum/Rubin (1983), 10.1093/biomet/70.1.41 | Paul R. Rosenbaum、Donald B. Rubin；The central role of the propensity score in observational studies for causal effects；Biometrika；1983 | 身份元数据及 `source-availability.md` 对官方 abstract 的原始转述。没有取得原 abstract 全文副本或论文全文/实现 | 对“以 observed covariates 定义 assignment probabilities/调整 observed imbalance”的背景，给定摘要级转述有有限支持；对本任务无未测混杂、因果优势、目标混合/区间，未提供支持 | v3 改为 [1]，只用于 §4 的观察协变量背景与适用范围；取消经验性因果担保。参考条目注明摘要级边界 |

身份映射可靠性来自本任务提供的核验记录，当前 Agent 未自行查验真实 DOI 现状。K-Dense citation-management 只适配其身份/编号/缺字段处理原则；未执行多库检索、metadata enrichment 或在线 DOI 校验。没有将“DOI 可解析”换成“已支持本论文结论”。

最终稿只使用一项文内引用 [1]，并有一个对应书目条目；原 [2]→新 [1] 的映射已记录。Efron 从最终书目移除，避免未用条目。图注及补充未引入额外外部引文。参考年份、作者、题名、期刊和 DOI 保持与给定元数据一致。卷、期、页范围未由给定记录提供，未从 DOI 字符串或记忆补齐，需作者核对；Lens 闭合政策未规定更细引文格式。

原稿经验数字、n、独立性前提、权重、区间和许可事实均归因于 fixture 对应文件，而非这两个真实论文。可定位的语义来源为 `source-availability.md` 的 R/R abstract paraphrase 段；其限定内容不能升级为原始全文证据。源码/Skill 的帮助也不能升级为科学发现。

K-Dense 上游要求的自身论文引文未加入科学书目：其身份/当前版本未在许可范围内取得或核验，且不是本诊断的科学证据。专业仓库、入口版本和 commit 以操作记录的软件来源列出；未编造第三篇科学文献。作者核验及完整书目/出版状态检查仍待确认。
