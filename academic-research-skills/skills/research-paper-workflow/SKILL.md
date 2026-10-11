---
name: research-paper-workflow
description: "自动科研总控：选题、实验、论文、必调来源与自主解阻；局部直达能力，维护不启动研究。"
metadata:
  version: "3.5.1"
---

# 有界研究到真实成果

识别维护、局部或完整研究；沿用最新指令，不重复安装。维护交付后结束。完整研究读[阶段控制](references/phase-control.md)：无预算最多45分钟做可行性判断，再一次确定后续预算；已有预算沿用。

每个专业步骤执行[必调流程](references/mandatory-professional-flow.md)：professional_flow.py begin调用14库匹配入口，阅读实施后finish/check才移交；子skill同样必调。缺来源/依赖先自主修复或换同14库匹配入口；严禁跳过专业调用或host_fallback。下载或无关函数不算专业完成。

依[四段主线](references/research-quality.md)连接“缺口→既有局限/竞争解释→贡献与反驳检验→新增认识/范围”；贯穿选题到实验与图稿。反证就修订，证据足够即成稿；恢复沿用证据。

默认computational-autonomous；executor是当前Agent，research_model是科研对象/算法；在来源流程内自主选择方法，改造或新写代码，保存实际证据。昂贵动作先guard。两次修复/两轮无增量须自主诊断、比较方案、验证并继续；单路线失败不关闭目标，阶段时间可在原总预算内重排。

局部不扩任务。恢复读当前阶段/步骤、指令、产物与下一动作；总预算触顶不启动工作，不伪称goal暂停。显式预算/长任务必登记阶段；局部无预算的阶段脚本是可选工具，不作为日常前置；专业调用必执行。
