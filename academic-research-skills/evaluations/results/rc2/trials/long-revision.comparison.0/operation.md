# 操作说明

**完成范围：** 当前 Agent、当前模型内执行指定 `manuscript-writing` 全稿修订；依据冻结表核对六行结果，重新计算三组加权结果，保存完整英文 `manuscript.md`、更新文本 Figure 1 图注，并在 `factual-semantic-diff.md` 逐项对照事实及语义。原始固定材料未改写。`check_revision.py` 已运行通过；对照报告绑定实际终稿 SHA-256。附加读取身份记录在 `resource_reads.jsonl`。

**采用来源：** 使用共同已核验缓存的 [K-Dense scientific-writing](https://github.com/K-Dense-AI/scientific-agent-skills)，提交 `65d6e786832e2c52832713117bbbf5096b56f77f`（证据、结构、写作和图表说明参考）；终审使用 [Adkid-Zephyr anti-defensive-writing-en](https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill)，提交 `102c8b21acf5eda3a0aef3d9779a65db646c8980`。实际应用于全稿论证、标题、摘要、引言、讨论、局限与结论，不将源码读取冒充操作完成。

**adapted_in_host：** 全部专业步骤在本 Agent 执行，未调用另一助手、模型或子代理。证据映射与一致性记录合并到对照报告，使用本地可运行检查而未生成投稿脚手架。按项目 `final-expression.md` 保留不利组别、原指标、区间及必要边界；未采用上游隐藏负面证据或改指标求优势的建议。专业来源作为操作出处记录，未添加未经核验的研究论文引用，未冒称人类核验或投稿审核通过。

**适用与未知：** 仅完成固定合成开发夹具修订，未获取研究数据或启动新论文；无目标期刊，未做特定期刊适配。没有新图像；未执行图像渲染检查。N1 全源、单元数据、聚合不确定性、交互检验及正式声明仍缺失，不能宣称可投稿。没有可用的 token、费用计量，未报告估算成本。
