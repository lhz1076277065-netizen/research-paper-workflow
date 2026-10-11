# 阶段出口与预算控制

## 先按请求范围进入

维护安装完成即结束；局部写作/单篇精读直达能力，不增加原创研究门槛。完整、长计算或显式预算任务用phase_control.py收据。既有假设保持假设，不扩大为历史重建；固定目标改变要有真实授权。

缺省最多45分钟可行性，用户更短预算/上级剩余预算优先。记录问题、近邻、决定性证据、依赖、最小验证和成本（资料先做[200 GB规划](data-acquisition.md)），随后一次取得研究总预算与阶段安排。已给总预算就init --minutes --authority沿用原指令，不追加45分钟或重复确认。授权字段不创造授权；读取Skill和收束也计时。

| 阶段 | 出口证据 |
|---|---|
| feasibility | 问题主线、适用近邻、已最小验证的路径、依赖与成本 |
| design | 假设、竞争预测、反驳条件与最小验证；前提失效则解阻 |
| research | 核心判断所需正式证据、正负结果及最终范围 |
| manuscript | 证据驱动的图稿、引用和科学/事实/视觉复核 |
| delivery | 编辑源、复算输出、真实完成层级、限制与下一动作；不自动投稿 |

阶段截止是计划；advance --minutes分配，用完后reassess --minutes在原总预算内重排。用户硬性阶段上限不可重排。总时间/token/交付预留触顶才closed_limit，不重置基点。默认预留时间10%且至多5分钟，长研究可增大计划预留；容量累计也不按阶段重置。前阶段短截止不会默认带入后阶段。

## 执行与复评

昂贵动作先写所支持的主张、结果如何改变判断、预计资源及失败后动作；命令用run，其他工具前guard。取得资料先用research_storage.py，绑定phase storage；guard --estimated-bytes/--transfer-bytes预检容量，run周期检查绑定项目并只管理自己创建的进程组。它不是OS沙箱，严格逐块约束由有界获取工具实施。源码准备也检查实际时间，保留核验过的缓存，触顶不取下一文件。

### 自主解阻与继续研究

读实际报错/样本→定位工程、证据、假设或真实边界→比较适配原问题的方案及科学有效性/信息/成本→选最有希望的方案→保存诊断并reassess→立即做最小验证→有效才扩大。可修复环境/接口、复用运行时、改分块算法、调用同14库另一匹配入口或采用有效替代材料。登录、免费条款、token配置沿用实际用户的自主处理授权，按[访问流程](data-acquisition.md)解决，不当作默认人类待办。

同一定位原因每次复评前最多两次实质不同修复；相同方法不重复。两次失败/两轮无信息增量触发自主复评，保留尝试，针对原blocker选新验证，不改名称绕过。不等文件自行出现或人类接手。完整覆盖/因果识别等不足不得宣称对应结论，但可做有效局部诊断、方法写作和其他独立工作；模拟不冒充实测。pilot不优胜先核实现、设计、功效和竞争解释，可靠零结果与边界可成证据。

单路线失败保持active并验证替代，不close整个目标。只有可行路径实际验证耗尽且无获授权高价值工作，或真实总预算/用户暂停/不可替代权限边界，才交付准确障碍。额外费用、伦理、固定目标改变按真实授权；只索取不可替代输入，同时继续独立工作。评审建议阶段报告不等于用户撤销完整目标。

证据足够进入成稿；design→manuscript可用advance --skip-reason绑定已有证据，不空做研究阶段。缺核心证据不能借此跳过。写作发现必要缺口时完成/有据取消当前步骤，reassess --stage research或design回传；完成收据重新check并消费，未完成的先完成/取消，改变产物不能借旧记录过门。

## 命令与计量

```bash
python3 scripts/phase_control.py --state project/phase.json init --scope full --objective '已授权问题' --minutes 120 --authority '实际总预算指令'
python3 scripts/phase_control.py --state project/phase.json meter --rollout /absolute/host-rollout.jsonl
python3 scripts/phase_control.py --state project/phase.json guard --estimated-seconds 120 --estimated-tokens 5000 --estimated-bytes 3000000
python3 scripts/phase_control.py --state project/phase.json reassess --blocker '原障碍' --evidence diagnosis.md --root project --next-action '已选方案的最小验证' --minutes 15
python3 scripts/phase_control.py --state project/phase.json run --log project/run.log --claim '核心前提' --decision '如何更新路线' --estimated-seconds 30 --professional-started project/start.json -- python3 project/test.py
python3 scripts/phase_control.py --state project/phase.json resume
```

未给总预算的init省略minutes/authority；可行性完成后advance到design会awaiting_budget，再authorize --minutes --authority。已有总预算不重复authorize。实际meter来自同一宿主rollout，分别报input、cached_input、output增量；额度默认input+output，另报非缓存量。有token上限而计量失效先修计量；无可靠计量不宣称严格达标。重试、恢复、换阶段不重置；后续新预算须真实授权及新记录，不掩盖旧超限。首次采样不是零耗费证明；guard不能撤销已发生的超限。

## 续接与专业步骤出口

resume默认只给最新3项产物/已交步骤、当前待做收据、失败次数/最近方案、最新指令及下一动作；完整历史在state文件，必要时--full定位。begin默认只给真实入口路径，不把大篇指导塞进stdout；必须读当前适用模式和必要支持文件再专业执行，不加载19技能/14整库/全部日志。完成安装不会因旧聊天重现而重做。

每个阶段advance及完成型close提交该阶段所有--professional-started/--professional-finished对；逐项check且与登记集合相符，遗漏/旧阶段/变更文件拒绝。辅助图稿/精读按真实能力调用。delivery只整理已核验输出且没有待交步骤时可复用刚完成manuscript收据；核验真实身份/指令，不能用旧历史替代新专业修改。暂停/触顶/路线关闭不需伪造完成。

completed不重启；closed_limit仅收束；paused等真实恢复，continue --authority沿用未过期原预算；awaiting_budget只取得缺失预算；active复评由Agent执行。旧route_closed只有实际续做指令可reassess --authority恢复，原预算仍有效才继续。cancel-step保留理由与证据，不算专业完成。run只终止自己创建的子进程组；不按任意PID杀外部作业，不把本地状态当作宿主goal已暂停/恢复。遇到工具needs_attention先诊断，不自动交人类。暂停和实际总限额不可用解阻绕过。
