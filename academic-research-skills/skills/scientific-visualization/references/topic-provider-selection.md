# 选题必须调用真实专业入口

选题必经 [专业调用流程](mandatory-professional-flow.md)，不能先自行构思再补记调用。开放问题默认调用 `orchestra-ideation`；固定问题用 `--source scholar-intake`，实施问题卡、证据需求、缺口与可行性门，不重新发散。begin自动准备已核实源码并返回原文，必须阅读并应用后再交付。

**Orchestra-Research/AI-Research-SKILLs**：本轮纳入的选题候选。优先查找problem-first、stakeholder rotation、explain-it与abstraction ladder相关能力，用于现实问题、受益对象、跨尺度思考和简洁意义表达。当前观察的brainstorming-research-ideas入口是一个可复用指导实现。读取所选入口与需要的内容，由当前Agent完成构思与证据核对；构思数量、互动频率、pilot时长与工具安排按当前任务调整，记录为adapted_in_host。

**Galaxy-Dawn/claude-scholar**：已有来源。研究问题的What/Why/Who、应用缺口、文献组织和Zotero资源管理可作为主实现或互补。已有文献库直接复用；实际项目使用原有记录方式，无须复制另一套管理流程。

**K-Dense-AI/scientific-agent-skills**：已有来源。实际观察已经存在时，hypothesis-generation可帮助形成竞争预测；scientific-brainstorming可提供独立发散与证据复核思路。所读当前版本含团队讨论、人工决策和评价流程，实际使用时选择符合当前Agent与研究授权的专业部分，科研判断与外部授权各自处理。

不得以清单外的STORM或另一助手系统替代本步入口。选题需要补充近邻文献时，另调用 literature-discovery 的专业流程；没有证据不虚称新颖性已经得到验证。

第二实现只能承担明确补覆盖或复核，并留下本次实际结果。来源不可用就停止该步骤并报障，不能转为普通推理。执行记录表达实际读取了什么、怎样影响候选、进入成果的输出；仓库星数与下载成功不是专业完成证据。
