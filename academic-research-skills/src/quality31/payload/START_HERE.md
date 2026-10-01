# 使用通用学术Skill

本套Skill不指定具体学科。开发、优化或打包本套Skill时交付完整通用目录与软件验证记录；用户明确要求开展学术研究时才进入下述研究路线。

单项任务直接读取skills下对应能力的SKILL.md；完整研究读取 [研究总控](skills/research-paper-workflow/SKILL.md)，按其 [科研主线](skills/research-paper-workflow/references/research-lifecycle.md) 推进问题、最近邻、设计、研究、正式图表与全文，在最后调用指定反防御性写作并复核。外部Skill从来源清单内仓库中动态选择，当前Agent负责实际执行，executor保留当前宿主，research_model可本地训练和评价。

工程smoke与软件回归是运行基础，不是论文完成标准。无需补其它宿主认证、旧版对照或重做整个工程验收才开始研究。首次本机依赖检查后，把主要资源用于解决科学问题。

新阶段的任务与成果写在一份简短路线板，用户可查看并纠正目标。重要性/验证不足时主动补研究，不按小型试跑的篇数、图数或90分钟时限降低目标。研究时间和计算预算采用用户真实约束，没有约束时先估计高价值下一阶段而非无限执行。

本次为合并后的完整版本；原细节协议和工具仍保留。更新和验证范围见 [更新报告](UPDATE_REPORT.zh-CN.md)。源码版另外提供tests/run_all.py和scripts/build_release.py；维护后用python3 scripts/build_release.py --check检查生成文件。日常版无需这些开发文件，脚本的--help只显示帮助。
