---
name: robustness-reproducibility
description: "当需要复算、独立验证、敏感性、失败诊断或整理可复现材料时使用；检查与主张有关的脆弱处，保存关键反例。"
metadata:
  version: "3.5.0"
---

# 关键结论的验证与复现

先执行 [必调流程](references/mandatory-professional-flow.md)：调用 professional_flow.py begin，以本skill名称选14库内匹配真实入口；阅读入口及必要资源，按其专业流程处理当前输入。finish/check通过才交付或进入下一步。严禁跳过来源自行思考代替专业执行；缺入口或必要条件就报障，禁止host_fallback。下载、读名称或无关函数不算完成。

按[四段科学论证主线](references/research-quality.md#四段科学论证主线)优先检查会让贡献失效的竞争解释、假设及测量风险，选择独立复算、敏感性、消融、跨条件验证或证明边界。分开实现正确性、数值收敛与模型适用性；反证更新主张、知识范围和图稿，不靠有利检查保护原故事。

默认computational-autonomous；executor为当前Agent，research_model为科研对象/算法；自主选择方法，改造或新写代码，保存实际证据。详见[原参考](references/protocol.md)。

交付成果、实际证据、来源版本与完成范围。显式预算或长任务先用[阶段控制](references/phase-control.md)保存预算、步骤与截止；同版任务复用已核验调用。无预算局部的预算脚本是可选工具，不作为日常前置；专业调用必须执行。
