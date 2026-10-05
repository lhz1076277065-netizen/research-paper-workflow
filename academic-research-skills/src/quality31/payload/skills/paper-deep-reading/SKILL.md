---
name: paper-deep-reading
description: "当给定论文、摘要或图表需要精读、解释方法和证据时使用；按已取得原文定位，摘要任务不补造全文细节。"
metadata:
  version: "3.4.1"
---

# 顶刊问题、模型和图表精读

先执行 [必调流程](references/mandatory-professional-flow.md)：调用 professional_flow.py begin，以本skill名称选14库内匹配真实入口；阅读入口及必要资源，按其专业流程处理当前输入。finish/check通过才交付或进入下一步。严禁跳过来源自行思考代替专业执行；缺入口或必要条件就报障，禁止host_fallback。下载、读名称或无关函数不算完成。

拆解决定当前设计的原问题、公式假设、训练/估计、评价划分、失败边界与关键图表；真实页段、公式、表图定位及视觉观察进入方法、验证和主图选择。

executor为当前Agent，research_model为科研算法/对象；在已调用流程内自主选择方法，改造或新写代码。默认 computational-autonomous，免费数字工具按实际需要使用，保存真实输出。专业补充见 [原参考](references/protocol.md)，不得用它绕过上游入口。

交付成果、实际证据、来源版本与完成范围。显式预算或长任务先用[阶段控制](references/phase-control.md)保存预算、步骤与截止；同版任务复用已核验调用。无预算局部的预算脚本是可选工具，不作为日常前置；专业调用必须执行。
