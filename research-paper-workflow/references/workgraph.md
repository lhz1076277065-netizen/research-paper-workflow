# 研究工作图：可选，不是必填的研究操作系统

只在多阶段、可恢复的项目中使用。focused 单项任务不需要它；外部 Skill 也无需知道它。一个可选总控负责共同图状态，工作者只交付局部结果。

可用 `scripts/workgraph.py assess --state workgraph.json --root /project` 查看 ready、reusable、waiting、stale、needs_rebind、budget_exhausted 和写路径冲突。该脚本不理解自然语言、不执行研究、不调度子代理，也不以 ready 代替科学批准。

图只含此次明确需要的任务，不自动补上所有 19 个模块。各节点可有 capability、service、status、depends_on、inputs/outputs（path+SHA256）、acceptance_report（实际接收检查报告 path+SHA256）、write_paths、attempts、max_attempts。checked 节点只有在输入、实际输出、接收报告和前置节点仍有效时才返回 reusable。

依赖是证据依赖，不是“某个 Skill 必须先调用”。已有材料可以直接作为输入，不要求伪造上游执行历史。被跳过的前置不会自动满足依赖；无需依赖时由宿主重设图并记录原因。

## 变更

`invalidate` 根据宿主给出的 task_id+kind（data/method/results/citations/presentation/journal_policy/unknown）生成新 revision，保留旧输出。沿显式依赖保守使后继失效，不影响祖先或无关任务；需要更细粒度时把任务拆到实际证据角色，不在本版引入字段级自动语义推断。kind 用来解释变更，不用它跳过已声明依赖。类型由真实变化决定，脚本不会自动证明是“仅风格修改”。

```bash
python scripts/workgraph.py invalidate --state workgraph.json --changes changes.json --reason "主要结果已更正" --expected-revision 2 --out workgraph-r3.json
```

单一整合者写图，expected_revision 用来发现过期交接；并不是多进程数据库锁。旧状态不覆盖，所有尝试保留。changed 的结果重新生成后需新的接收报告，不可通过把状态改回 checked 复用旧批准。

## 回退、并行与预算

只返回可开始的任务集合；存在共同 write_paths 时返回冲突，由宿主串行或隔离。图中的 max_attempts 是准备/续跑检查，只有实际宿主遵守才能限制外部工作；网络、费用、物理设备和 OS 安全边界仍由宿主实施。

实验失败和科学零结果不同。checked_for_handoff 只代表契约检查通过；真正可进入写作的论断仍必须有来源、方法和科学审核。有效零结果可以进入稿件，不为了获得显著性无限重试。
