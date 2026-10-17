# 自主研究单元、解阻与增量复核

按[稳定研究约定](research-alignment.md)组织工作：一个单元关联原问题ID，写明主张、竞争解释、实际检验、输入及可交付结果；旁支明确标为exploration，不能替代原问题。下载、转换、拟合、图表、导出等内部动作服务这个单元，不各自启动一轮完整外部评审。不同专业能力仍各自走14库 begin→读源→实施→finish/check；合并复核不合并或跳过专业调用。用户明确要求的逐步外部复核，按约定的专业单元执行；不得静默取消或用本地check冒充外部审查。

论文正文交代全部主要实验的目的、关键方法、实际结果和真实材料/方法边界；必要科学复现信息与适用AI披露保留；“待复核/已复核”、Skill收据、预算、阶段状态放在独立README或交付记录。签收后不要为了标记签收再改已审正文，否则会人为制造新版本和无限复核。管理记录、导出清单和文件名更新不算新科学单元，也无需再次begin专业审查。

正文有改动时先读已有全稿审查和实际diff，将修改映射到受影响的主张/数字/图注/引文；以适用14库入口执行一次该范围的增量审查，保留旧全稿审查覆盖的未变部分。不因“最终版”标签重复全部专家流程。增量报告写入独立文件，不再回写论文的审查状态；有新的科学问题才回传研究或修订。真实外部评审如被明确要求仍按该约定执行。

## 计划可改，科学约束有依据

拟合/调参次数、搜索批次、代理排定的阶段分钟、默认review/maxIterations均是计划。代理达到自定配额时，依据实际收益、成本和剩余用户预算自主调整并实施，不要求用户“解锁”。记录origin=agent；用户硬预算、供应商真实配额、200 GB容量、用户暂停及不可替代权限边界仍有效。工具的authority字段是收据，不能创造授权。

代理默认交付预留也可重排：有已成稿件但必要复核被guard拒绝时，先核对真实剩余时间和打包实测成本，用reassess --minutes/--reserve-seconds安排适配的审查与交付并立即执行；不要把预留当整个目标已blocked。只有实际总预算触顶才停止新工作。审查尽量随研究单元推进，避免将全部关键复核拖到最后；成本不足时选14库内适配当前范围的实现，不省略必要工作或冒称完整评审。

选择方法先比较识别能力、适用前提、误差/泄漏风险、可复现性和实测成本，再用同等条件的最小验证选适配方案；不能只选最复杂或结果最好的模型。扩展搜索不能改动已冻结的测试集、端点或显著性规则；确需改变时保留原分析并标注新的探索分析，固定用户目标的改变另按实际授权。

障碍出现后读取真实错误和最小样本，按证据/工程/访问/前提分类，比较候选并执行能改变判断的最小检验。用route记录ready/testing/failed/useful/external_dependency及真实证据。单路线失败只关闭该路线；选择剩余高价值路线或独立任务立即推进。两次不同修复或两轮无增量要求自主reassess，不是向人类移交。不得反复仅检查文件是否出现；没有可检验的候选时，交付准确限制，不虚造科学证据、无限换名称或无价值扩展。

接入外部助手先读其真实Skill与项目配置。在用户已授权自主处理和原任务范围内，用该工具支持的配置调整代理默认迭代配额，保留固定对话地址、凭证及回执；不修改其他项目的全局配置。硬服务额度/安全限制按真实边界处理。评审指出缺证据后转成一次具体实验或修订，不反复提交相同材料求另一答复。多个评审问题可并入一个有证据增量的修订单元。

## 轻量记录与恢复

`work_units.py`与phase共用锁和记录，不启动模型或改变宿主goal。只写当前单元必要证据，默认恢复读compact快照；需要旧收据时精确定位，不反复cat完整phase/日志。每次单元有结果都checkpoint，分别保存execution、answer、validity和实际结果，不能把运行成功或旧inconclusive当有效答案。恢复先给研究约定、全部必答问题回答状态、关键结果和下一必要动作。语言/格式/进度指令仅影响相关工作，未变科学证据继续复用；真正科学目标变更须保存真实用户指令，受影响next_action重新制定。adopt记录新版操作规则和实际授权，保留旧预算、状态、收据及未知计量；不自动恢复暂停/已完成/真实预算触顶任务。

```bash
python3 scripts/work_units.py --state project/phase.json plan --key fits --limit 600 --used 448 --rationale '追加独立敏感性验证，实测成本仍在原预算内' --evidence decision.md --root project
python3 scripts/work_units.py --state project/phase.json route --key alternative --claim '当前核心判断' --action '候选方案的决定性最小检验' --status ready --estimated-seconds 30 --evidence diagnosis.md --root project
python3 scripts/work_units.py --state project/phase.json checkpoint --key contrast --claim '对应原问题的实际主张' --question-id Q1 --experiment-id E1 --execution completed --answer answered --validity valid --outcome refuted --next-action '将实际反向结果写入正文' --result result.json --evidence result.json --root project
python3 scripts/work_units.py --state project/phase.json review-status --key contrast --evidence result.json --evidence draft.md --root project
python3 scripts/work_units.py --state project/phase.json review-record --key contrast --evidence result.json --evidence draft.md --root project --started project/review-start.json --finished project/review-finish.json
```

review-record要求对应真实14库审查能力收据，begin输入必须包含复核单元所有文件。review-status只有输入内容、指令、审查收据、报告和输出仍一致才复用；变化就重新执行适用复核。缓存是已有审查的索引，不是自动科学认证。外部助手回复如为任务要求，应成为本次审查的输入/输出证据；没有真实外部回执不得声称其已接受。

恢复时已完成但尚未阶段消费的收据单列计数，不能当待做任务。未完成步骤续做；已交付阶段不重启；当前进程仅显示存在/缺失观察，PID存在不等于归属。reconcile-processes只移除进程及进程组均已不存在的旧登记，保留失败日志与未完状态，不杀任意PID也不声称计算成功。
