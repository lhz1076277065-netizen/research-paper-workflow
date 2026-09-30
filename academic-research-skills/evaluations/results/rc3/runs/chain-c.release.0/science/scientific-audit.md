# 科学判断与实际修复

仅针对闭合合成材料作当前 Agent 的证据判断；不是实际同行评审、新研究或作者核验签字。所有数值以 `baseline/evidence.md` 的 authoritative result memo v2 为报告权威，不能将其当作原始数据复现凭证。

## 目标量和决定性证据

本任务已成立的贡献是一个可检查的诊断：同一组分层对比，因目标混合权重与观测混合权重不同而改变汇总点估计方向。它不提出已外部验证的新因果或预测方法，也不声称优先性。该贡献由给定 g1/g2 对比和两种权重的明确算式支撑；无须补造新实验。

独立采样对象是 8 个配对单位，每层 4 个。每个单位同时测 A/B，技术重复在换算后按单位和方法取平均。独立性是给定记录的前提；没有原始记录，不能独立审定其成立。技术重复数、转换因子、原始单位数值、采样时间和实际测量背景均未提供。

取 d_g1 = −1.00、d_g2 = +3.00，单位为 score，越低越好：

- 目标：0.8 × (−1.00) + 0.2 × (+3.00) = −0.20。
- 观测等权：0.5 × (−1.00) + 0.5 × (+3.00) = +1.00。
- 两者差：−0.20 − (+1.00) = −1.20。仅核对汇总算术，不是重跑原分析。

g1 点估计支持 A 的较低分数，g2 点估计支持 B 的较低分数。因此 g2 必须出现在主文和 Figure 1；它是解释混合权重效应的必要组成部分。

## 原稿关键论断 → 判断 → 真正修复

| 原稿位置与论断 | 判定和依据 | 实施位置与结果 |
|---|---|---|
| Title/Abstract：universal advantage | 与 g2 +3.00 及 lower-is-better 方向冲突；汇总优势也依赖权重 | v3 Title、Abstract、§3–5 改为 mixture-dependent descriptive diagnostic，保留 g2 |
| Abstract：causal advantage | 未提供分配、混杂测量、因果调整或识别条件；权重不是因果识别 | v3 Abstract、§4 删除肯定因果标题和推断，说明记录边界 |
| Abstract：practical equivalence to zero | 没有等效界值或注册等效检验；跨零不能证明等效或精确无效应 | v3 Abstract、§3、图注、S1.3 保持 [−0.60, 0.20]，明确含零与双方向 |
| Abstract：[1] Efron 证明单位独立及所有总体区间有效 | 只有身份元数据，没有全文语义证据；文献无法代替本样本设计证据 | 从经验论断及最终书目移除 Efron；独立性在 §2.1 标为给定前提，区间在 §2.3 限定目标对象 |
| Abstract：[2] R/R 证明本比较无未测混杂 | 给定摘要级描述涉及 observed covariates，未支持此推断；全文未知 | 最终 [1] 仅服务 §4 的 observed-covariate assignment 背景，取消因果担保 |
| Results：g2 也支持 A | +3.00 表示 A 分数更高，故方向错误 | v3 §3 第一段、Figure 1/图注及 S1.2 明确 g2 favors B |
| Declarations：all authors approved、ethics approved、open raw sharing confirmed | 作者事实未知；原始记录/标识符再分发被许可禁止 | v3 Declarations 与独立标题页保留 UNKNOWN；实际访问声明限定汇总/代码与待定控制访问 |

## 区间与复现边界

报告对象为固定 0.8:0.2 目标加权对比的 95% 分层内配对单位 percentile bootstrap 区间。已给操作是层内重采样配对单位并重新施加目标权重；不把 A/B 拆开、不把技术重复当独立样本。没有重采样次数、种子、分布、原始数据或原脚本，因此不能复算端点、评定实际覆盖或产生更窄区间。g1、g2 和观测等权对比的区间均未给出，不补画。

算术检查、跨文件检查及图稿核验属于软件/报告验证，不是对实验独立性、总体外推或 bootstrap 有效性的科学证明。给定 n=4/层的有限材料与无外部验证限制解释范围，但不阻碍完成这个已授权诊断说明。

## 来源与终稿表达的层级

当前 Agent 实际使用 K-Dense scientific-writing 的证据绑定和不捏造原则、peer-review 的设计/统计/复现/伦理/引文审查维度，及冻结模块的引文与治理规则。没有执行真实保密审稿 intake、官方报告指南合规认证或其原生全部 CLI，未将 UNKNOWN 人类核验、冲突或审批写成通过。

`review/manuscript-v3-before-expression.md` 先形成科学已收窄的全文；再对完整正文应用 anti-defensive-writing：引言改成问题→诊断贡献；摘要以方向变化及证据开篇；讨论集中推断限制；结论给可操作的解释规则。记录在 `review/expression-diff.diff`。采用冻结 `final-expression.md` 的证据保持适配，没有采纳隐去 g2、不利结果、区间跨零或改主要指标来制造优势的建议。

逐项复核摘要、Methods、Results、Discussion、Conclusion、Figure 1、图注和 Supplement，比较对象、权重、单位、方向、区间、推断强度与必要反例均保留。作者的最终科学核验和批准仍未知。
