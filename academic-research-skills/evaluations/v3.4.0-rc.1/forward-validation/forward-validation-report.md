> 后续更新验收见supplement/supplement-report.md；本报告保留第一轮当时结果。resume退出码问题已在新版复验修复。

# v3.4.0 独立前向试用记录

评估开始：2026-10-04 07:52:13 UTC。核心执行结束：07:54:18 UTC；总用时低于10分钟。评估只在forward-validation创建产物。未编辑库源码、安装、下载、外发、研究实际科学问题或启动科研计算。

## 已读取的入口与资源

- skill-creator/SKILL.md 的 Independent Forward-Testing。
- 新版 research-paper-workflow/SKILL.md、phase-control.md、research-lifecycle.md、capability-routing.md、execution-handoff.md。
- 新版 manuscript-writing/SKILL.md。
- phase_control.py 的实际帮助和实现，随后通过CLI执行，不以措辞匹配代替行为证据。

## 请求1：空科学材料、无后续预算，仅初步可行性

实际动作：生成8行software-fixture.csv；Python标准库读取并检验行数、字段与显式SOFTWARE_FIXTURE_NOT_SCIENTIFIC_DATA标记；执行phase_control init（full，默认45分钟入口上限）、guard（估计5秒）和close route_closed。

实际产物：software-fixture.csv、fixture-inspection.json、feasibility.md、feasibility-state.json。没有下载、科研检索、模型调用或科学计算，没有授权后续预算或进到design/research。

发现：输入请求没有提供具体科学假设。因此能给出的初步结论是缺少命题和可证伪预测，fixture只模拟软件材料；不能据此判断科学价值。可行性报告说明最近邻未定义、决定性证据未提供、下一步所需输入和停止条件。此项验证的是缺输入时能否守住范围，不能评估已有具体假设时的贡献判断质量。

预算局限：默认full状态实际写入45分钟，但本次另受上级最多10分钟测试要求约束并在两分钟左右收束。脚本的默认值不自动识别上级更短预算；此处没有启动高成本动作，不能说脚本强制执行了10分钟上限。meter未采样，usage为null，不声称token预算达标。

## 请求2：只精简已有摘要

实际动作：读取manuscript-writing局部任务入口，在本地保留原文并生成改稿、编辑记录；未创建完整研究状态，未新增实验、检索、引用或科学事实。

改稿：三项本地软件测试均拒绝过期启动；这只能验证截止检查，不能证明科研质量或所有宿主工具受控。

实际产物：abstract-original.txt、abstract-revised.txt、abstract-edit-record.json。

发现：入口明确允许局部工作直接完成，本次不要求原创贡献和全研究前置。改稿保留三项本地软件测试、过期启动拒绝，以及科研质量和宿主覆盖范围两项限制。这里是编辑输出和操作范围记录，未把关键词/措辞检测包装成行为测试，也没有独立科学事实复核。

## 请求3：已完成维护 + paused 测试恢复与启动

原始fixture：maintenance-state.json scope=maintenance，status=completed，completed_tasks=['installation-v340']；paused-test-state.json scope=focused，status=paused，同时保留已完成维护标记。两份文件均为软件模拟状态，不证明真实安装发生过。

实际CLI顺序及结果（逐条argv/stdout/stderr/退出码见actions.jsonl）：

1. maintenance resume：退出0，返回completed与installation-v340，内嵌guard.allowed=false/phase_completed。
2. paused test resume：退出0，返回paused与原始截止、最新指令、下一动作，内嵌guard.allowed=false/phase_paused。
3. paused guard：退出2，allowed=false/phase_paused。
4. paused run启动探针：退出2，stderr=Work blocked: phase_paused。探针若真正启动会写COMPUTATION_STARTED.marker；实际marker与startup-probe.log均不存在。
5. 独立positive-control状态为active；phase_control run实际启动软件探针，退出0，生成CONTROL_STARTED.marker和run.log，随后close completed。

状态检查：paused-test-state-before.json与实际最终状态JSON语义相等；status仍paused，completed_tasks仍['installation-v340']，owned_processes=[]，host_goal_state=not_modified。阳性对照执行后owned_processes亦为空。没有修改暂停意图，没有重复安装。检查结果见paused-launch-observations.json与behavior-checks.json。

发现：实际阻断了经run发起的暂停软件工作；阳性对照证明启动探针可正常运行，因此没有marker具有解释力。resume只是恢复读取，不解除暂停；退出0并不表示允许启动，调用方必须读嵌套guard或再执行guard/run。此接口约定可能让只看退出码的自动化误判，但本次run仍实际拒绝，因此未观察到暂停绕过。

## 验证局限

- 只验证本地CLI及它拥有的进程，不验证所有宿主工具、API、OS或宿主goal停止采样。
- 没有检验运行中暂停、token超限、截止触发杀进程、外部runner死亡与子进程恢复等路径。
- 没有实际上游专业库集成；简单局部摘要直接执行，不能声称跨模型独立复核或全科研工作完成。
- 科研问题未提供，无法判断科学贡献、真实材料可得性或论文质量。
- 不把摘要中原有“三项本地测试”追认为本评估已经复现；本次真实执行记录独立列在actions.jsonl。
- 所有fixture原始状态、probe、记录均在隔离目录，源码仅被读取。
