---
name: manuscript-review
description: "当需要科学内容审查、论证诊断或稿件一致性检查时使用；指出影响结论的缺口和可执行修订，不自动重建研究。"
metadata:
  version: "3.5.0"
---

# 科学贡献、证据与表达审查

先执行 [必调流程](references/mandatory-professional-flow.md)：调用 professional_flow.py begin，小型清单用--profile focused调用K-Dense，完整评审用Academic入口；阅读入口及必要资源，按其专业流程处理当前输入。finish/check通过才交付或进入下一步。严禁跳过来源自行思考代替专业执行；缺入口或必要条件就报障，禁止host_fallback。下载、读名称或无关函数不算完成。

按[四段科学论证主线](references/research-quality.md#四段科学论证主线)审查缺口真实性、最强近邻评价、判别证据和新增认识/范围；定位断链，区分表达缺陷与科学缺口。贡献不足回传具体研究动作并撤回受影响就绪判断；证据足够即成稿，改表达后核事实，局部审查只处理指定范围。

默认computational-autonomous；executor为当前Agent，research_model为科研对象/算法；自主选择方法，改造或新写代码，保存实际证据。详见[原参考](references/protocol.md)。

交付成果、实际证据、来源版本与完成范围。显式预算或长任务先用[阶段控制](references/phase-control.md)保存预算、步骤与截止；同版任务复用已核验调用。无预算局部的预算脚本是可选工具，不作为日常前置；专业调用必须执行。
