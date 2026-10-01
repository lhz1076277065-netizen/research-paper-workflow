# 动态使用指定来源

从assets/research31-policy.json选择本次所需的用户指定仓库。先用当前宿主已有技能目录定位本地安装；查看选中仓库当前版本/入口并保持本次版本一致。只查当前需要的来源，缓存与必要片段可复用，不扫描或切换其他执行助手；科研模型的发现/准备仅按具体研究需要和授权推进。

使用原有GitHub工具或：

```bash
python3 scripts/research31.py sources --role figure
python3 scripts/research31.py upstream discover --repo OWNER/REPO --out run/source.json --allow-network
python3 scripts/research31.py upstream read --index run/source.json --entry ACTUAL_PATH/SKILL.md --out run/skill.md --allow-network
```

read/fetch/bind保留原有实际接口；新包装器先检查仓库范围。路径来自当前目录而非写死的子Skill清单。同一任务用已记录版本，离线可复用已有源码，注明未查询到当前远程状态。库内不适合时继续必要原创研究或提出库外Skill替代建议，不把未经同意的外部Agent当工具补位。

正式产物的实际使用见provider-policy.md；函数、入口读取与完整专业步骤分开。旧原生upstream.py仍是通用底层工具，新研究通过本范围包装器或按相同范围使用宿主工具。此规则不限制公开文献/数据查询。

一个已保存index冻结本任务的repository、commit、tree和逐文件blob。`read`按commit取文件并核对blob，缓存不一致保留原文件；`fetch`核对checkout的commit tree及入口/支持blob，错配不提供可用配置。`bind`携带同一tree与已发现blob，不把发现标记当已审阅。更新任务另存新index，保留旧快照、本地适配、输入输出版本和原来的两个函数适配器。
