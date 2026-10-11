---
name: data-preparation
description: "当已有研究数据或材料需要清理、整合、转换和质量检查时使用；保留来源与处理记录，避免改变目标量或泄漏验证信息。"
metadata:
  version: "3.5.1"
---

# 真实材料整理与可复现处理

先执行 [必调流程](references/mandatory-professional-flow.md)：用 professional_flow.py begin选14库匹配入口；阅读必要资源，按其专业流程处理当前输入。finish/check通过才移交。严禁绕过来源代替专业执行；缺入口/依赖按[阶段控制](references/phase-control.md)自主修复或换库内匹配入口；禁host_fallback。下载或无关函数不算专业完成。

按[四段科学论证主线](references/research-quality.md)优先核关键比较所需定义、测量、单位、时间、连接键及样本流。识别同队列/镜像重复，分区内预处理，保留原始材料、处理代码及质量检查；不按期望故事挑结果，缺陷回传为证据与主张范围变化。

默认computational-autonomous；executor为当前Agent，research_model为科研对象/算法；自主选择方法，改造或新写代码，保存实际证据。详见[原参考](references/protocol.md)。

交付成果、实际证据、来源版本与完成范围。显式预算/长任务用[阶段控制](references/phase-control.md)记录预算与步骤；复用同版核验任务。局部无预算的阶段脚本是可选工具，不作为日常前置；专业调用必执行。
