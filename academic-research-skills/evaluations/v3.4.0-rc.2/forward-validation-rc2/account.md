独立前向测试执行记录

我作为独立评估 Agent，从两个指定的 rc.2 SKILL.md 开始，实际运行各自 professional_flow.py begin，阅读返回的固定版本入口及必要写作资源，然后生成当前任务的结果。没有先生成答案再补记来源调用。记录均保存在本隔离目录，没有打开或联系其他聊天，没有检索外部文献、开展实验或安装依赖。输入数字与观察全部作为合成测试材料处理。

任务 A 实际完成：提出固定宽限期、迟到确认、分时规则三个可验证选题，逐项写出价值、可获得数据条件下的最低成本检验、基线、失败条件与推断边界，并给出条件式优先顺序。上游 F1/F3/F8 改变了结果：把空座损失和迟到误释放分开，识别等待者、迟到者、管理者不同成本，避免只优化释放速度。未声称原创性核实或方法有效。

任务 B 实际完成：给出两句结果段，保持全部给定计数和分母，删除因果证明、统计显著与学校普适性主张；没有计算新的研究结果或扩展研究。上游 evidence workflow 允许不完整草稿，故登记证据与声明而不虚填人工核验者。未把“没有随机分组记录”改成“没有随机分组”。

实际工具结果：A、B 的 begin/finish/check 均返回0，check=eligible_for_handoff，并明示 semantic_work_verified_by_tool=false。B 的上游 check_consistency 返回0/pass。B 的 audit_claims 返回1/fail：三个 CLAIM_NOT_VERIFIED、三个 UNVERIFIED_CITATION_MARKER、三个 UNVERIFIED_CLAIM_EVIDENCE，共9个错误，均来自如实保留的未核验状态；详见 task-b/claim-audit.stdout.json。没有把失败修成虚构核验，也没有声称稿件已获人类批准。

观察到的限制：这次局部改写可以完成，但上游科学声明审计需要人工核验，不能由来源流程check替代；流程check通过与下游科学声明审计失败同时存在，应分别报告。若把上游全稿“final audit”当作本次局部草稿完成前提，B会受阻；当前按照入口边界“Partial writing stays within requested section; no forced full study or human approval claim”和证据资源中“A draft may remain incomplete and uncertain”交付有记录的改写草稿。不是对生产研究或全文投稿工作的验证。

入口版本：topic-novelty/manuscript-writing 均3.4.0-rc.2；A使用 Orchestra-Research/AI-Research-SKILLs commit 773a52944ba4747a18bd4ae9ade53fff041adcbc；B使用 K-Dense scientific-writing 2.3，commit 154988403bb5a18e9d3c0ce4e6d5e2e4b184a298。具体源文件blob/sha256、task/input/output哈希见 start.json 与 finish.json。

产出位置：task-a/deliverable.md，task-b/deliverable.md；真实输入：各自 request.md/materials.md；过程：各自 professional-work.md/work-report.json；工具轨迹：*.command.json、*.stdout.json、*.stderr.txt；完整执行索引：execution-trace.json。另有保存实际生成文件的 save_deliverables.py。

从输入保存到本记录完成耗时 234.2 秒，低于10分钟；首次阅读技能发生在保存输入前，整个前向测试亦未超过10分钟。
