# 实际操作记录

- 输入：只从指定请求取得 `user_prompt`、`material`、`initial_skill_text` 与相关路径；材料为合成 A1–A5/B1–B6。未读取其他测试组、旧成果或评审答案，也未重复读取材料文件与 Skill 入口。
- 主 Skill：`paper-deep-reading` 3.2.0-rc.1；经共同 Python 的 `run_host.py read` 读取当前快照 `protocol.md`、`provider-policy.md`、`execution-handoff.md`。
- 专业支持：按需读取共同配置及专业索引片段，选用 K-Dense `scientific-writing` 2.1 入口和 `evidence_workflow.md`（commit `65d6e786832e2c52832713117bbbf5096b56f77f`），实际用于主张分类、定位和缺失约束。`adapted_in_host`，未执行其完整稿件流程或专业脚本；未实时核验远程版本及库论文引用。
- 实际成果：逐段精读、文字图说明解读、同名术语/前提差异判断、四项迁移条件与研究设计分支，写入 `answer.md`。读取内容与身份由 `resource_reads.jsonl` 记录；索引定位辅助仅输出行范围。
- 限制：未获得全文、原始图像、完整转录/附录或 B 第三份记录身份核验；未独立重证 A、复现 B、获取研究数据、生成论文或估算成本；没有调用其他助手、模型或子代理。
- 检查：交付后以本地断言检查两份文件存在、非空及关键范围/定位标记。该检查只验证文件完整性，不替代科学判断或人工原文核验。
