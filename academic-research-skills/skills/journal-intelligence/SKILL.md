---
name: journal-intelligence
description: "当需要学习领域标杆期刊、比较投稿候选或核对期刊适配时使用；依据实际论文和当前官方要求判断，不启动实验或整稿重写。"
metadata:
  version: "3.4.1"
---

# 标杆学习与投稿期刊匹配

先执行 [必调流程](references/mandatory-professional-flow.md)：调用 professional_flow.py begin，以本skill名称选14库内匹配真实入口；阅读入口及必要资源，按其专业流程处理当前输入。finish/check通过才交付或进入下一步。严禁跳过来源自行思考代替专业执行；缺入口或必要条件就报障，禁止host_fallback。下载、读名称或无关函数不算完成。

早期核实接受相应计算、理论或数字证据的领域期刊与标杆；终稿依据实际贡献、证据范围和官网要求匹配。需要额外物理证据时说明缺口与投稿影响，不擅自改研究问题。

executor为当前Agent，research_model为科研算法/对象；在已调用流程内自主选择方法，改造或新写代码。默认 computational-autonomous，免费数字工具按实际需要使用，保存真实输出。专业补充见 [原参考](references/protocol.md)，不得用它绕过上游入口。

交付成果、实际证据、来源版本与完成范围。显式预算或长任务先用[阶段控制](references/phase-control.md)保存预算、步骤与截止；同版任务复用已核验调用。无预算局部的预算脚本是可选工具，不作为日常前置；专业调用必须执行。
