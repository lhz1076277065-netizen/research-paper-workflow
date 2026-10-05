---
name: research-paper-workflow
description: "协调跨阶段学术研究与完整成果：可行性、阶段预算、专业来源、决定性证据与图稿交付；单项请求直达对应能力，Skill维护不启动研究。"
metadata:
  version: "3.4.1"
---

# 有界研究到真实成果

先识别维护、局部工作或完整研究；沿用最新指令，已完成安装不重复执行或播报。维护交付后结束，不启动科研。完整研究先读 [阶段控制](references/phase-control.md)：无预算最多45分钟做可行性判断，再一次确定后续预算；已有预算沿用。

每个专业步骤必读并执行 [必调流程](references/mandatory-professional-flow.md)：professional_flow.py begin 自动调用14库内匹配真实入口，阅读并实施专业流程，finish/check通过才接入产物或推进。所有子skill同样必调；禁止跳过来源自行构思或写作。缺来源或必要条件就报障，不允许host_fallback；下载、读名称或无关函数不算专业完成。

默认 computational-autonomous；executor是当前Agent，research_model是科研对象/算法。在已调用流程内自主选择方法，改造或新写代码，保存实际证据。路线板连接主张、近邻与决定性检验；昂贵动作先guard，两次修复/两轮无增量复评。证据足够成稿，否则按出口交付报告。

局部工作直接调用对应入口，不扩展任务。恢复只读当前阶段/步骤、指令、产物与下一动作；预算触顶不启动新工作，不伪称goal暂停。显式预算/长任务必须登记阶段；无预算局部的预算脚本是可选工具，不作为日常前置；专业调用必须执行。
