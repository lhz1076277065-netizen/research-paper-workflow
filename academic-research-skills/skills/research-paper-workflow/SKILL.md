---
name: research-paper-workflow
description: "协调完整研究的可行性、预算、必调来源、证据和图稿交付；局部直达对应能力，Skill维护不启动研究。"
metadata:
  version: "3.5.0"
---

# 有界研究到真实成果

先识别维护、局部或完整研究；沿用最新指令，不重复安装/播报。维护交付后结束。完整研究读[阶段控制](references/phase-control.md)：无预算最多45分钟做可行性判断，再一次确定后续预算；已有预算沿用。

每个专业步骤执行[必调流程](references/mandatory-professional-flow.md)：professional_flow.py begin调用14库匹配真实入口，阅读并实施；finish/check通过才接入产物或推进。子skill同样必调；缺来源或必要条件就报障，严禁跳过自行思考或host_fallback。下载、读名称或无关函数不算完成。

依[四段主线](references/research-quality.md#四段科学论证主线)连接“缺口→既有局限/竞争解释→贡献与反驳检验→新增认识/范围”；选题、设计、实验、主图及写作据此取舍。反证就修订，证据足够即成稿；阶段与恢复沿用证据版本。

默认computational-autonomous；executor是当前Agent，research_model是科研对象/算法；在来源流程内自主选择方法，改造或新写代码，保存实际证据。昂贵动作先guard，两次修复/两轮无增量复评。

局部直达入口，不扩任务。恢复只读当前阶段/步骤、指令、产物与下一动作；预算触顶不启动工作，不伪称goal暂停。显式预算/长任务必登记阶段；无预算局部预算脚本是可选工具，不作为日常前置；专业调用必执行。
