---
name: peer-review-response
description: "当给定真实审稿或编辑意见需要逐点回应和修订稿件时使用；定位改动与证据，保留不接受意见的有据说明。"
metadata:
  version: "3.5.0"
---

# 审稿意见驱动的修订与回应

先执行 [必调流程](references/mandatory-professional-flow.md)：调用 professional_flow.py begin，以本skill名称选14库内匹配真实入口；阅读入口及必要资源，按其专业流程处理当前输入。finish/check通过才交付或进入下一步。严禁跳过来源自行思考代替专业执行；缺入口或必要条件就报障，禁止host_fallback。下载、读名称或无关函数不算完成。

按[四段科学论证主线](references/research-quality.md#四段科学论证主线)定位真实意见影响的缺口、前作比较、突破证据或意义范围；补有据数字研究、解释或不同意，回复连到真实改动与新版位置。超出证据给可检验替代；反证出现就修订主张及整条论证，不把未发生的检验写成已完成。

默认computational-autonomous；executor为当前Agent，research_model为科研对象/算法；自主选择方法，改造或新写代码，保存实际证据。详见[原参考](references/protocol.md)。

交付成果、实际证据、来源版本与完成范围。显式预算或长任务先用[阶段控制](references/phase-control.md)保存预算、步骤与截止；同版任务复用已核验调用。无预算局部的预算脚本是可选工具，不作为日常前置；专业调用必须执行。
