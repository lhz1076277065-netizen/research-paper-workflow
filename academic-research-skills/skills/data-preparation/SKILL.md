---
name: data-preparation
description: "当已有研究数据或材料需要清理、整合、转换和质量检查时使用；保留来源与处理记录，避免改变目标量或泄漏验证信息。"
metadata:
  version: "3.5.0"
---

# 真实材料整理与可复现处理

先执行 [必调流程](references/mandatory-professional-flow.md)：调用 professional_flow.py begin，以本skill名称选14库内匹配真实入口；阅读入口及必要资源，按其专业流程处理当前输入。finish/check通过才交付或进入下一步。严禁跳过来源自行思考代替专业执行；缺入口或必要条件就报障，禁止host_fallback。下载、读名称或无关函数不算完成。

按[四段科学论证主线](references/research-quality.md#四段科学论证主线)优先核关键比较所需定义、测量、单位、时间、连接键及样本流。识别同队列/镜像重复，分区内预处理，保留原始材料、处理代码及质量检查；不按期望故事挑结果，缺陷回传为证据与主张范围变化。

默认computational-autonomous；executor为当前Agent，research_model为科研对象/算法；自主选择方法，改造或新写代码，保存实际证据。详见[原参考](references/protocol.md)。

交付成果、实际证据、来源版本与完成范围。显式预算或长任务先用[阶段控制](references/phase-control.md)保存预算、步骤与截止；同版任务复用已核验调用。无预算局部的预算脚本是可选工具，不作为日常前置；专业调用必须执行。
