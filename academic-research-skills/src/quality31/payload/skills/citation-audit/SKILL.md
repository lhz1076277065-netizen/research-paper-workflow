---
name: citation-audit
description: "当需要核查引文、参考文献、来源身份或论断与出处的对应关系时使用；区分实际取得的正文证据与尚未核实的信息。"
metadata:
  version: "3.5.0"
---

# 引用真实性与论断支持核验

先执行 [必调流程](references/mandatory-professional-flow.md)：调用 professional_flow.py begin，以本skill名称选14库内匹配真实入口；阅读入口及必要资源，按其专业流程处理当前输入。finish/check通过才交付或进入下一步。严禁跳过来源自行思考代替专业执行；缺入口或必要条件就报障，禁止host_fallback。下载、读名称或无关函数不算完成。

按[四段科学论证主线](references/research-quality.md#四段科学论证主线)追核缺口、前作局限和领域意义的原方法与结果；核对象、结局、比较、时间、样本、方向、效应与范围。“为何未解决”无依据则保留假设，单时点不扩为持续性；本文突破对应实际证据，修复受影响的稿件位置。

默认computational-autonomous；executor为当前Agent，research_model为科研对象/算法；自主选择方法，改造或新写代码，保存实际证据。详见[原参考](references/protocol.md)。

交付成果、实际证据、来源版本与完成范围。显式预算或长任务先用[阶段控制](references/phase-control.md)保存预算、步骤与截止；同版任务复用已核验调用。无预算局部的预算脚本是可选工具，不作为日常前置；专业调用必须执行。
