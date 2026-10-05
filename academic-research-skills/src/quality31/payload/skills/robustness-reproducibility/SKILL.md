---
name: robustness-reproducibility
description: "当需要复算、独立验证、敏感性、失败诊断或整理可复现材料时使用；检查与主张有关的脆弱处，保存关键反例。"
metadata:
  version: "3.4.0-rc.2"
---

# 关键结论的验证与复现

先执行 [必调流程](references/mandatory-professional-flow.md)：调用 professional_flow.py begin，以本skill名称选14库内匹配真实入口；阅读入口及必要资源，按其专业流程处理当前输入。finish/check通过才交付或进入下一步。严禁跳过来源自行思考代替专业执行；缺入口或必要条件就报障，禁止host_fallback。下载、读名称或无关函数不算完成。

按核心主张选择独立检查、敏感性、消融、跨条件验证或证明边界；分开实现正确性、数值收敛和模型适用性，检验后建设性改进并更新真实支持范围。

executor为当前Agent，research_model为科研算法/对象；在已调用流程内自主选择方法，改造或新写代码。默认 computational-autonomous，免费数字工具按实际需要使用，保存真实输出。专业补充见 [原参考](references/protocol.md)，不得用它绕过上游入口。

交付成果、实际证据、入口版本、专业步骤怎样影响结果及完成范围。局部请求仅做对应范围；完整研究沿用 [阶段控制](references/phase-control.md)，同版源码与本任务产物可复用，版本变化重新核对。预算记录脚本是可选工具，不作为日常前置；专业调用流程必须执行。
