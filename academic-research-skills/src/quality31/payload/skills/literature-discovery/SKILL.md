---
name: literature-discovery
description: "当需要定向或系统检索学术文献、核对来源和综合相关证据时使用；建立可追溯覆盖，不将一次搜索命中当作完成综述。"
metadata:
  version: "3.5.0"
---

# 检索、筛选与证据地图

先执行 [必调流程](references/mandatory-professional-flow.md)：调用 professional_flow.py begin，以本skill名称选14库内匹配真实入口；阅读入口及必要资源，按其专业流程处理当前输入。finish/check通过才交付或进入下一步。严禁跳过来源自行思考代替专业执行；缺入口或必要条件就报障，禁止host_fallback。下载、读名称或无关函数不算完成。

按[四段科学论证主线](references/research-quality.md#四段科学论证主线)实际阅读摘要与关键原文，检索真实缺口、前作已解决部分、限制依据、最强替代解释和反证；追踪数据声明、附件与作者仓储。把会改变贡献、判别检验或材料选择的证据交下游，不堆支持预设故事的文献。

默认computational-autonomous；executor为当前Agent，research_model为科研对象/算法；自主选择方法，改造或新写代码，保存实际证据。详见[原参考](references/protocol.md)。

交付成果、实际证据、来源版本与完成范围。显式预算或长任务先用[阶段控制](references/phase-control.md)保存预算、步骤与截止；同版任务复用已核验调用。无预算局部的预算脚本是可选工具，不作为日常前置；专业调用必须执行。
