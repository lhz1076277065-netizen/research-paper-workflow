# v3.3.0-rc.1 问题导向选题升级报告

基线为正式 v3.2.0 / 1e2a56bc9db0bfd411ce8ce250703785e53bb43d。本次按用户提供的三份文本、候选ZIP及粘贴记录实施。附件里的方案和候选结论作为待核对材料；发布和验证状态以本次实际操作为准。

| 用户目标 | 本次维护源修改 | 交付与判断 |
|---|---|---|
| 学习顶刊怎样提出重要问题 | journal-intelligence、paper-deep-reading 的 protocol；research-quality、research-lifecycle | 跨篇归纳问题家族、成熟/未解部分、模型选择、数据来源与独立单位/时空尺度，作者论证与自身推断分开 |
| 选题解决现实困难 | 总控与 topic-novelty 短入口；新增 problem-led-topics | 连接受影响者、科学未知、现实瓶颈、最近邻差异与下一项决定性研究工作 |
| 不默认只换模型 | problem-led-topics、topic-novelty 原协议 | 同时允许有用算法、新事实、成熟方法及基础理论；按问题价值和证据判断 |
| 实际意义能被检验 | problem-led-topics | 分别报告技术指标、历史记录支持、模拟收益、潜在用途和部署效果；与实际约束对齐 |
| 题名简明但准确 | topic-novelty、problem-led-topics | 先写普通语言核心问题，保留决定问题身份的条件，实施细节放方法；无字数限制/限定词黑名单 |
| 接入成熟选题方法 | 两来源配置、新增 topic-provider-selection | 新增可选 Orchestra，保留原13来源，补 K-Dense ideation/novelty；主实现匹配任务，互补者有明确职责 |
| 低上下文与独立能力 | 唯一公共维护源及既有两层构建器 | 保留19完整模块、原专业协议、30项写作和运行接口；详细新增指导按需读取 |
| 完整验证与可安装发行 | 原测试、独立目录检查、真实任务、既有打包器和安装器 | 工程、实际行为及归档安装证据分列，不以软件通过证明科研质量 |

补丁应用器首先演练并生成实际diff，再在干净工作区应用并保留备份。修正两处陈旧来源数量断言：检查旧集合保留、两配置一致、无重复、动态路径及新增来源实际可选。发布版同步19入口与配置、工具报告的版本；科研算法和结果核查接口保持原样。打包器排除补丁备份并将本轮验收说明纳入日常包。

完整 manuscript-writing/protocol.md 字节与基线相同；19个原协议标题均保留。总控完整入口793→795字符，选题入口689→718字符，均包含发行版本元数据。详细比较范围见[上下文记录](evaluations/v3.3.0-rc.1/context-metrics.json)，长度不等于模型Token费用或研究能力。

Orchestra已通过项目自身来源包装器完成实时仓库发现与入口读取，核验commit/tree/blob与SHA256。记录见[SOURCE-OBSERVATIONS](evaluations/v3.3.0-rc.1/SOURCE-OBSERVATIONS.json)。上游专业思想由当前宿主按研究任务适配；不永久固定入口、不全量安装、不接入STORM后端。历史星数与本次观察分开，关注度不作科学质量评分。

工程验收见[本轮验证](evaluations/v3.3.0-rc.1/VALIDATION.zh-CN.md)，实际任务与版本对照见[行为观察](evaluations/v3.3.0-rc.1/BEHAVIOR.zh-CN.md)，逐文件身份见[变更清单](evaluations/v3.3.0-rc.1/CHANGES.json)。两问题首轮及洪水冻结重复共六份任务产物已保存，并完成两组匿名评阅：候选的需求与数据入口更具体、重复题名更清楚；跨篇/方法/效果边界多处相当，近邻与反证也有变弱、研究负担增加。首轮预算/冻结偏差、未完成数据联接和收益分析均记录，未用工程通过替代能力结论。完整总控原文见[ORCHESTRATOR](evaluations/v3.3.0-rc.1/ORCHESTRATOR.md)。日常/源码/一键安装包由最终提交构建，manifest绑定提交与逐文件摘要；发行页提供SHA256与核验收据。

按[迁移说明](MIGRATION.zh-CN.md)与[安装教程](INSTALLATION.zh-CN.md)替换所选完整能力目录。稳定[v3.2.0](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.2.0)保留为比较/回退基线；本次发布为候选版。尚未完成的更广领域重复、真实外部专家评阅和部署收益验证均保持待验证，不宣称普遍选题提升、绝对新颖性或论文录用。
