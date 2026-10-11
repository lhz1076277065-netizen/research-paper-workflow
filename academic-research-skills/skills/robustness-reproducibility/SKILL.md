---
name: robustness-reproducibility
description: "当需要复算、独立验证、敏感性、失败诊断或整理可复现材料时使用；检查与主张有关的脆弱处，保存关键反例。"
metadata:
  version: "3.5.1"
---

# 关键结论的验证与复现

先执行 [必调流程](references/mandatory-professional-flow.md)：用 professional_flow.py begin选14库匹配入口；阅读必要资源，按其专业流程处理当前输入。finish/check通过才移交。严禁绕过来源代替专业执行；缺入口/依赖按[阶段控制](references/phase-control.md)自主修复或换库内匹配入口；禁host_fallback。下载或无关函数不算专业完成。

按[四段科学论证主线](references/research-quality.md)优先检查会让贡献失效的竞争解释、假设及测量风险，选择独立复算、敏感性、消融、跨条件验证或证明边界。分开实现正确性、数值收敛与模型适用性；反证更新主张、知识范围和图稿，不靠有利检查保护原故事。

默认computational-autonomous；executor为当前Agent，research_model为科研对象/算法；自主选择方法，改造或新写代码，保存实际证据。详见[原参考](references/protocol.md)。

交付成果、实际证据、来源版本与完成范围。显式预算/长任务用[阶段控制](references/phase-control.md)记录预算与步骤；复用同版核验任务。局部无预算的阶段脚本是可选工具，不作为日常前置；专业调用必执行。
