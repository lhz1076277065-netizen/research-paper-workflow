# 阶段出口与预算控制

## 先按请求范围进入

维护安装完成即结束；局部写作/单篇精读直达能力，不增加原创研究门槛。完整、长计算或显式预算任务用phase_control.py收据。既有假设保持假设，不扩大为历史重建；固定目标改变要有真实授权。

未给预算时，45分钟是首次可行性复评计划，代理据判断自主安排后续工作；不能把默认分钟当用户硬上限或等待批准。记录问题、近邻、决定性证据、依赖、最小验证和成本（资料先做[200 GB规划](data-acquisition.md)）。已给总预算用init --minutes --authority并以实际授权请求的--started-at（含时区）或--request-rollout为基点；多条用户消息时用--request-message精确选择实际授权原文，重复原文则从日志核实时间戳，不能默认取早先安装消息。代理自行定位真实记录，不因此要求人类接手。不从目录创建时间推断、减去任意分钟或在初始化时续24小时。无可靠起点明确未知并保留旧截止，不能承诺严格计时。读取Skill和收束也计入真实预算。

| 阶段 | 出口证据 |
|---|---|
| feasibility | 问题主线、适用近邻、已最小验证的路径、依赖与成本 |
| design | 假设、竞争预测、反驳条件与最小验证；前提失效则解阻 |
| research | 核心判断所需正式证据、正负结果及最终范围 |
| manuscript | 证据驱动的图稿、引用和科学/事实/视觉复核 |
| delivery | 编辑源、复算输出、真实完成层级、限制与下一动作；不自动投稿 |

阶段截止和默认交付预留是代理计划；advance --minutes分配，用完后reassess --minutes在原总预算内重排。默认预留时间10%且至多5分钟，可依据已完成产物、必要复核和实际打包成本用reassess --reserve-seconds调整；代理token预留用--token-reserve。预留触发delivery_required而非关闭任务：选择收束或有据重排后继续必要工作，不等用户解锁。真实总时间/token耗尽才closed_limit，不重置基点；用户硬性阶段/预留上限不可调整，旧来源未知不猜。容量累计不按阶段重置。

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

未给总预算的init省略minutes/authority，budget_authority=agent；默认可行性advance后继续design，计划过期用reassess --minutes自主重排，保留起点、累计使用和历史。仅用户明确要求先批准预算时用--require-budget，沿用旧awaiting_budget/authorize接口。实际用户总预算budget_authority=user，不能被reassess、换回合或恢复延长。旧记录的权限来源未知按原截止保守保持；迁移不虚造授权。实际meter来自同一宿主rollout，分别报input、cached_input、output增量；额度默认input+output，另报非缓存量。首次采样之前的用量保持未知，不当零；基点不因重试/恢复重置。

## 续接与专业步骤出口

token预算口径必须匹配用户/宿主真实定义：init/authorize --token-metric可选input_plus_output或noncached_input_plus_output，旧记录默认前者。分别显示输入、缓存输入、输出，不把缓存量推断为同等费用；口径不明时保持未知，不自行缩减真实额度或宣布严格达标。真实预算不能通过换口径放宽。累计计量在初始化晚于请求时回填起点前最近实际计数；没有可回填计数标明覆盖缺口，先修计量而非报零。guard分别输出token_meter_verified（样本来源）与strict_token_budget_verified（实际预算起点及覆盖）；样本真实不代表整个预算已完整计量，未知旧记录不能据前者宣称严格达标。

resume默认给最新3项产物/已交步骤、最多3个真正未完收据及总数、已完成未消费收据的单独计数、当前科学单元、候选路线和下一动作；完整历史在state文件，必要时精确定位。用[自主研究单元](autonomous-work.md)更新结果、复用不变材料的审查并区分自定配额。begin默认给真实入口路径；必须读当前适用模式和必要支持文件，不加载19技能/14整库/全部日志。完成安装不会因旧聊天重现而重做。

每个阶段advance及完成型close提交该阶段所有--professional-started/--professional-finished对；逐项check且与登记集合相符，遗漏/旧阶段/变更文件拒绝。辅助图稿/精读按真实能力调用。delivery只整理已核验输出且没有待交步骤时可复用刚完成manuscript收据；核验真实身份/指令，不能用旧历史替代新专业修改。暂停/触顶/路线关闭不需伪造完成。

completed不重启；closed_limit仅收束；paused等真实恢复，continue --authority沿用未过期原预算；awaiting_budget只取得缺失预算；active复评由Agent执行。旧route_closed只有实际续做指令可reassess --authority恢复，原预算仍有效才继续。cancel-step保留理由与证据，不算专业完成。run只终止自己创建的子进程组；不按任意PID杀外部作业，不把本地状态当作宿主goal已暂停/恢复。遇到工具needs_attention先诊断，不自动交人类。暂停和实际总限额不可用解阻绕过。
