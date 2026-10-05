# 阶段出口与预算控制

## 先按请求范围进入

Skill维护在安装/版本核验交付后结束；局部写作、翻译、读单篇或单图只做对应范围，不要求原创贡献或全研究状态。完整研究及长计算使用阶段收据。用户给定的假设保持为假设；真实历史重建、因果归因或新总体不是默认附加任务，固定问题的实质范围改变要先取得确认。

45分钟是缺省上限而不是追加额度；用户已给的更短预算、上级任务预算和剩余总预算优先，init时将其传入--minutes。无预算时可行性阶段最多45分钟（包括检索、环境检查和交付），不开展整年下载或模型矩阵。产物说明：问题与主张、直接最近邻、决定性证据、材料/硬件依赖、最小验证、成本及停止条件。完成后一次取得后续总预算和阶段安排；用户已经给过预算就直接沿用。预算记录不是授权证明，必须来自实际用户指令。

| 阶段 | 必要产物与出口 |
|---|---|
| feasibility | 可行性决策稿；可验证且有路径才报价后续，否则交付障碍报告 |
| design | 核心主张、竞争解释、可判别预测及最小验证；关键前提失败则改设计或收束 |
| research | 只补承诺主张不可缺少的证据；同条件验证通过且范围成立就冻结 |
| manuscript | 证据绑定图稿、引用与科学/事实/视觉复核；只有影响核心结论的缺口才回传 |
| delivery | 编辑源、可复算输出、真实完成范围、限制与下一动作；不自动投稿 |

各阶段记录预计成本与出口，用advance --minutes配置阶段截止；所有阶段仍受同一个后续总预算约束。预留总时间至少10%（上限5分钟为工具默认，长项目可在计划中提高）用于保存、清理与交付。稿件所需工作在计划中提前分配，不把剩余全部时间交给探索。

## 执行与复评

开始下载、移植、大规模计算前写明所支持的核心主张、会改变决策的结果、预估成本以及停止条件；高成本命令通过phase_control.py run执行。非命令工具前调用guard。工具只约束经它检查/启动的动作，不是OS沙箱，不能拦截所有API调用或保证宿主停止采样。

同一已定位工程原因最多两次有实质差异的修复；相同方法不重试。连续两轮没有减少核心不确定性时必须产出复评：不可替代的缺口、有限检验能否改变判断、修复后是否仍有贡献。能继续则在原预算内选择下一动作；不能则route_closed交付报告。修复计数不能换名字绕过；计算失败不能包装成科学发现。

正式证据足够支持原范围就转图稿。可选扩展不阻挡完成；贡献不足不授权持续抬高目标。报告、探索稿、正式论文、投稿分别标记，路线失败不等于原研究已经完成。

## 命令与计量

```bash
python3 scripts/phase_control.py --state project/phase.json init --scope full --objective '用户已授权问题'
python3 scripts/phase_control.py --state project/phase.json meter --rollout /absolute/current-host-rollout.jsonl
python3 scripts/phase_control.py --state project/phase.json guard --estimated-seconds 120 --estimated-tokens 5000
python3 scripts/phase_control.py --state project/phase.json advance --stage design --evidence feasibility.md --root project --next-action '待确认一次后续预算' --professional-started project/intake-start.json --professional-finished project/intake-finish.json
python3 scripts/phase_control.py --state project/phase.json authorize --minutes 120 --authority '实际用户确认定位'
python3 scripts/phase_control.py --state project/phase.json run --log project/run.log --claim '检验核心前提' --decision '失败则停止该路线' --estimated-seconds 30 --professional-started project/analysis-start.json -- python3 project/test.py
python3 scripts/phase_control.py --state project/phase.json resume
```

meter读取当前宿主实际累计input/cached_input/output的阶段增量；首次采样是基点，不是零耗费证明。批准的token额度默认input+output（含缓存输入），另报非缓存量。若用户指定另一计量口径，先给相应真实增量，不混用goal累计量和新阶段额度。下一调用包含长历史时用预计上下文token做guard；检查不能撤销已发生的超限。

无可靠meter时不得声明token达标；有token上限且计量不可用则不启动新高成本工作。换回合、恢复、失败重试或换阶段都不重置时间/token基点。追加预算需新的明确授权及新收据，不能覆盖旧超限；init拒绝覆盖已有状态。自动续跑遇到terminal/awaiting_budget就交付当前状态，不启动新研究。

run只监控自己创建的进程组，时间截止、暂停或token触顶后终止自己的作业并记录实际退出。close不根据任意PID杀进程。外部终止runner可能留下子进程，恢复须检查真实句柄，不能盲目重启。外部进程、宿主goal由真实权限与授权管理，不改全局认证或伪称平台暂停。

resume返回只读快照；禁止启动时退出2并包含guard原因，仍不自动改变宿主目标。恢复保留latest_instruction、completed_tasks、当前阶段/截止、关键产物、失败和下一动作；详细日志只定位相关片段。完成的维护task不能因旧聊天开头再次成为当前任务。

## 专业步骤出口

每个研究阶段CLI advance和完成型close必须提交该阶段所有专业步骤的 `--professional-started step-start.json --professional-finished step-finish.json` 对；工具逐项check并记录关联。没有专业实施记录、准备源码代替执行、旧阶段重复记录或不匹配角色会拒绝出口。暂停、路线关闭、触顶报告与维护完成不要求虚构专业完成记录。局部任务同样先执行[必调流程](mandatory-professional-flow.md)，不因任务小而绕过来源。
