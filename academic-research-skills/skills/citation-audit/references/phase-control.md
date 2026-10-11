# 阶段出口与预算控制

## 先按请求范围进入

Skill维护在安装/版本核验交付后结束；局部写作、翻译、读单篇或单图只做对应范围，不要求原创贡献或全研究状态。完整研究、长计算及用户显式预算任务必须使用阶段收据；无预算的小型局部请求无需阶段管理。用户给定的假设保持为假设；真实历史重建、因果归因或新总体不是默认附加任务，固定问题的实质范围改变要先取得确认。

45分钟是缺省上限而不是追加额度；用户已给的更短预算、上级任务预算和剩余总预算优先，init时将其传入--minutes。无预算时可行性阶段最多45分钟（包括检索、环境检查和交付），不开展整年下载或模型矩阵。产物说明：问题与主张、直接最近邻、决定性证据、材料/硬件依赖、最小验证、成本及停止条件。完成后一次取得后续总预算和阶段安排；用户已经给过总预算时init加--minutes和--authority记录原指令，直接沿用；可行性出口不再次报价或等待预算，不额外增加45分钟。预算记录不是授权证明，必须来自实际用户指令。

| 阶段 | 必要产物与出口 |
|---|---|
| feasibility | 可行性决策稿：真实缺口、已知局限、待验突破、条件性价值与成本；先找出并最小验证可行路径，预算内仍无路径才交付障碍报告 |
| design | 主线对应的核心假设、竞争解释、可判别预测、反驳条件及最小验证；关键前提失败则诊断原因，比较替代设计并实际验证 |
| research | 只补核心判断不可缺少的证据；根据支持/反证修订主线，范围成立就冻结，不按期望故事挑结果 |
| manuscript | 从实际证据组织四段论证、图稿、引用及科学/事实/视觉复核；只有影响核心结论的缺口才回传 |
| delivery | 编辑源、可复算输出、最终支持的主线、真实完成范围、限制与下一动作；不自动投稿 |

各阶段记录预计成本与出口，用advance --minutes配置计划截止；所有阶段仍受同一个总预算约束。阶段计划用完触发stage_reassessment_required，Agent用reassess --minutes自主重排剩余阶段时间；只有总预算或交付预留触顶才closed_limit。用户明确给定的硬性阶段上限仍必须遵守，不能把它当可调整计划。下一阶段未指定分钟数时恢复总截止，不继承上一阶段的短截止；不会重置总预算。读取Skill、规划及最终交付说明也计入用户总时限；init时传剩余额度，不能在准备后才起算完整预算。预留总时间至少10%（上限5分钟为工具默认，长项目可在计划中提高）用于保存、清理与交付；close前先保存主体产物和必要交付说明，关闭记录不能让后续收束免计时。稿件所需工作在计划中提前分配，不把剩余全部时间交给探索。

主线具体判断见[四段科学论证主线](research-quality.md#四段科学论证主线)，复用路线板作为阶段证据和专业调用输入。旧阶段记录不足保持未知，续接只补当前决策所需信息，不追溯重跑或增加预算。维护、局部请求按原范围执行。

## 执行与复评

开始下载、移植、大规模计算前写明所支持的核心主张、会改变决策的结果、预估成本以及停止条件；高成本命令通过phase_control.py run执行。非命令工具前调用guard。工具只约束经它检查/启动的动作，不是OS沙箱，不能拦截所有API调用或保证宿主停止采样。

绑定phase的源码准备也检查当前指令、状态和剩余时间，每个请求的timeout受工作截止限制；触顶不继续取下一文件，保留已核验的部分缓存，不能用一次准备覆盖后续各阶段预算。

同一已定位工程原因每次复评前最多两次有实质差异的修复；相同方法不重复。两次失败或连续两轮没有减少核心不确定性时，由Agent自主复评并执行新的判别动作，不等人类接手。reassess --blocker针对原障碍记录诊断和下一验证后允许新的不同修复；保留全部尝试，不能改障碍名称绕过复评。计算失败不能包装成科学发现。

### 自主解阻与继续研究

1. 读取相关报错、数据样本、来源要求和当前状态，定位根因。区分获取/接口/环境/计算/导出障碍、证据不足、假设未获支持和真正的权限或资源边界；缺一个文件、一次pilot未优胜、模型尚未拟合都不等于任务无解。
2. 在现有研究笔记中比较可行方案，说明各方案对原问题的适配、科学有效性、预期信息增量、资源和时间成本。选择最有希望解决核心阻塞的方案；若验证失败，依据新信息选择下一方案。可检查公开替代数据、同14库匹配入口、独立环境、已有运行时、分块/降阶/等价实现或新的判别设计。固定目标不能因容易完成而偷换。
3. 保存实际诊断、替代比较、所选理由和下一项最小验证；执行reassess后立即做该验证，而不是仅写“待人类执行”。验证成立就推进必要正式规模；失败则保存原因并更新路线。等待外部输入时继续不受影响的设计、可运行分析、方法写作和图稿工作。
4. 准入条件按所支持的主张与操作判断。完整时空覆盖、来源独立性或因果识别缺失时，不得宣称相应结果；仍应修复输入，并在有效材料上开展有信息价值的诊断、校准或局部检验，明确其范围。不得让未来完整结论的前提阻断所有可执行工作，也不得用模拟数据冒充缺失实测证据。
5. 试点反证先检验实现、功效、设计及竞争解释；可靠零结果和适用边界也可成为论文证据，不以“必须优胜”驱动筛样本或改弱基线。评审意见是科研输入，不能把“建议阶段报告”当作用户撤销完整论文目标。必要主张仍未验证时继续补证；足够证据则成稿。

路线失败默认只结束该实现或假设，保留active阶段并在原授权内探索适配原问题的替代路线；不要调用close route_closed关闭整个项目。仅当已诊断并实际验证的可行路径均不能解决必要缺口，且无其他获授权、有信息价值的工作可推进，才交付障碍报告；须列真实尝试、失败证据和不可替代的外部条件。真实总预算触顶、用户暂停、必需伦理/访问权限、额外付费或实质改变固定目标仍按真实授权处理。只向用户索取不可替代的信息或权限，同时推进独立工作。不存在“任意两次失败即交人类”的规则。

正式证据足够支持原范围就转图稿。设计阶段已确认现有材料足够时，用advance --stage manuscript --skip-reason记录证据覆盖与判断，绑定设计产物和真实专业记录后直接成稿；无需空做研究阶段或追加实验。准入失败或只够写阶段报告不构成完整论文的“证据足够”，不能用skip-reason跳过未做的核心研究。写作中发现核心缺口时，完成或有据取消当前专业步骤，用reassess --stage research（或design）回传研究，再对新工作执行真实专业调用；回传时工具重新核验并消费当前已完成的专业步骤；仍在进行的步骤须先完成或有据取消，产物变更仍拒绝。不复用旧阶段收据冒充新成果。可选扩展不阻挡完成；贡献不足不授权持续抬高目标。报告、探索稿、正式论文、投稿分别标记，路线失败不等于原研究已经完成。

## 命令与计量

```bash
# 尚无总预算：只开展可行性；已有总预算则使用下一行的--authority路径。
python3 scripts/phase_control.py --state project/phase.json init --scope full --objective '用户已授权问题'
# 有实际总预算时替代上一行，不能重复init。
python3 scripts/phase_control.py --state project/phase.json init --scope full --objective '用户已授权问题' --minutes 120 --authority '实际用户给定的总预算指令'
python3 scripts/phase_control.py --state project/phase.json meter --rollout /absolute/current-host-rollout.jsonl
python3 scripts/phase_control.py --state project/phase.json guard --estimated-seconds 120 --estimated-tokens 5000
python3 scripts/phase_control.py --state project/phase.json advance --stage design --evidence feasibility.md --root project --next-action '待确认一次后续预算' --professional-started project/intake-start.json --professional-finished project/intake-finish.json
python3 scripts/phase_control.py --state project/phase.json authorize --minutes 120 --authority '实际用户确认定位'
python3 scripts/phase_control.py --state project/phase.json run --log project/run.log --claim '检验核心前提' --decision '按结果修订设计与下一检验' --estimated-seconds 30 --professional-started project/analysis-start.json -- python3 project/test.py
# 两次工程修复后自主诊断，recover.md含实际报错、替代比较和所选验证。
python3 scripts/phase_control.py --state project/phase.json reassess --blocker '原障碍名称' --evidence recover.md --root project --next-action '执行已选替代方案的最小验证'
# 计划阶段时间用完时重排；原总截止、token基点及交付预留不变。
python3 scripts/phase_control.py --state project/phase.json reassess --minutes 15 --evidence recover.md --root project --next-action '运行判别检验'
python3 scripts/phase_control.py --state project/phase.json resume
```

meter读取当前宿主实际累计input/cached_input/output的阶段增量；首次采样是基点，不是零耗费证明。初始总token额度用init --token-limit --rollout --authority同时建立实际基点；若已经先采样可行性，新的后续授权会把原阶段用量归档，绝不清除已有总预算内的用量。批准的token额度默认input+output（含缓存输入），另报非缓存量。若用户指定另一计量口径，先给相应真实增量，不混用goal累计量和新阶段额度。下一调用包含长历史时用预计上下文token做guard；检查不能撤销已发生的超限。

无可靠meter时不得声明token达标；有token上限且计量不可用则先修复计量，不启动无法核算的高成本工作。换回合、恢复、失败重试或换阶段都不重置时间/token基点。追加预算需新的明确授权及新收据，不能覆盖旧超限；init拒绝覆盖已有状态。自动续跑遇到completed不重启，closed_limit保存交付，paused等待真实恢复，awaiting_budget只取得缺失预算；active中的reassessment_required由Agent自主处理，不反复查旧文件等待“自然出现新证据”。工具的needs_attention是诊断提示，不等于必须请求人类操作。

run只监控自己创建的进程组，时间截止、暂停或token触顶后终止自己的作业并记录实际退出。close不根据任意PID杀进程。外部终止runner可能留下子进程，恢复须检查真实句柄，不能盲目重启。外部进程、宿主goal由真实权限与授权管理，不改全局认证或伪称平台暂停。

begin/finish自动登记当前专业步骤的路径、任务/输入身份和完成记录，resume只读这些简明信息，完整指导留在步骤文件中。同一阶段同一任务/输入的重复begin拒绝重启，指向已有记录；检查或续接该记录即可。

resume返回只读快照；禁止启动时退出2并包含guard原因，仍不自动改变宿主目标。恢复保留latest_instruction、completed_tasks、当前阶段/截止、关键产物、失败和下一动作；详细日志只定位相关片段。完成的维护task不能因旧聊天开头再次成为当前任务。

## 专业步骤出口

delivery仅整理已核验产物且没有任何未取消、未消费的专业登记时，可不另造begin/finish对。工具须重新核验刚完成manuscript阶段的真实收据、文件身份及当前指令；缺历史信息、产物变化或仍有待交步骤均拒绝。其他研究阶段仍要求当前步骤记录；新专业修订仍先调用，不用旧阶段收据冒充。

每个研究阶段CLI advance和完成型close必须提交该阶段所有专业步骤的 `--professional-started step-start.json --professional-finished step-finish.json` 对；工具逐项check并记录关联。没有专业实施记录、准备源码代替执行、旧阶段重复记录或不匹配角色会拒绝出口。工具将出口所提交的步骤与当前登记集合逐一比较；遗漏尚在进行的步骤就拒绝推进。阶段内的辅助工作仍调用其真实能力入口，例如研究阶段绘图、写作阶段精读；不以阶段名排除适用能力。暂停、路线关闭、触顶报告与维护完成不要求虚构专业完成记录。局部任务同样先执行[必调流程](mandatory-professional-flow.md)，不因任务小而绕过来源。

明确的后续恢复授权可用continue --authority恢复paused阶段。旧route_closed在实际用户要求继续原目标时，可用reassess --authority '实际续做指令' --stage research --evidence recover.md --root project --next-action '具体验证'恢复；阶段计划已过则同时给--minutes。工具保留原截止、计量、失败记录和目标；原预算耗尽就拒绝继续。写入authority字段本身不构成授权。用户替换任务或某步骤失去必要性时，可cancel-step --started --reason --evidence --root保留取消理由与材料，不能把取消写成专业完成或跳过当前请求仍需的工作。宿主goal按其真实规则管理，不能因本地单路线失败就判整个目标blocked，也不能把本地active冒充已恢复宿主goal。
