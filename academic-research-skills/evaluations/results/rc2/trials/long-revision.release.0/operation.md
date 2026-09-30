# 本次操作说明

已交付完整可编辑英文 `manuscript.md`、事实与科学语义比较 `factual-semantic-diff.md`；保留原稿、冻结表/说明和完整终审前稿。只处理指定合成开发材料，没有启动新论文或获取研究数据。

实际专业流程：按请求中的 `manuscript-writing` 3.2.0-rc.2 及其 protocol、provider-policy、final-expression、execution-handoff 执行；选用 K-Dense `scientific-writing` 2.1 的证据索引、全文结构、方法结果核对与贡献边界流程，实际读 evidence_workflow、writing_principles、imrad_structure。以 E1/E2 锁定事实，以 C01–C12 绑定比较，重写全文并保留六组完整结果及区间，更新原 Figure 1 文本图注，没有生成新图。

实际终审：数值复核后的完整稿另存 `professional-draft.md`，再由当前 Agent/当前模型实际应用指定 `anti-defensive-writing-en`，突出条件排序这一已成立贡献，删除重复自我削弱和工作日志，强化标题与引言并逐段复查全稿。按项目证据保持规则适配上游：保留所有不利组别、探索性、N1 摘要层级和缺失推断边界，没有换指标或编造机制。

专业源码复用本次共享索引标记为已核验的缓存：K-Dense commit `65d6e786832e2c52832713117bbbf5096b56f77f`；英文 anti-defensive commit `102c8b21acf5eda3a0aef3d9779a65db646c8980`。本 Agent 没有另做在线 HEAD 核验。附加资源均经指定 `run_host.py read` 留下实际路径、身份和读取范围，见 `resource_reads.jsonl`。

`adapted_in_host`：专业工作由当前 Agent 完成；用本任务的证据比较表和一份标准库 `check_manuscript.py` 替代可选注册表/CLI 脚手架。最终脚本核对六行及全部端点、精确复算三组加权结果、查跨章节更新和旧值残留，通过结果见绑定终稿 SHA-256 的 `check-receipt.json`；再由当前 Agent 完成语义比较。未声称完整运行上游 CLI 或完成具名人类核验/审批。

实际限制：无原始簇数据、总体区间、交互检验、N1 全文、目标期刊、人工/外部专家认可或版面渲染检查；没有补入未经核验的外部出版物，也未宣称投稿就绪。token、缓存 token、费用和峰值资源未取得，保持未知。全部写入本 trial 目录，未调用其他助手、模型、宿主或子代理。

复跑实际检查：

```sh
'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' 'LOCAL_EVIDENCE_ROOT/trials/long-revision.release.0/check_manuscript.py'
```
