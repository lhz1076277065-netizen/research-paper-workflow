# 合成测量校准科研写作演示：交付
本项目是人为合成教学演示，不是真实研究或原创发现。主体产物为可编辑中文短稿 [manuscript-draft.md](manuscript-draft.md)，包含摘要、引言、方法、结果、讨论、表1、图注、声明与引用。

主要结论：按冻结训练验证规则选择偏移。测试RMSE raw=1.5275819、offset=0.3462390、affine=0.3442872，线性额外收益0.0019518，未达到预定0.05教学阈值；不能将此解释为总体等效。真实train为batch0/1/2共80条，test为batch2(10)+batch3(30)共40条。

## 可编辑代码与结果
- calibration.py：训练3折按批次留出，先锁模型再测；原始分区SHA256冻结。
- robustness.py：10000次二批次描述重采样、精确4种重采样/符号诊断、量级/中位数/影响点敏感性、闭式OLS及完整复算。
- make_figures.py：图形源与原生布局审计；figures/figure1.png、PDF、SVG及灰度版。
- results/results.json、primary-metrics.csv、cv-metrics.csv、test-predictions.csv、model-lock.json为首次主要结果；rerun/为实际完整复算（5个主文件SHA256相同）。
- source_manifest.json、claims.csv、citations.md为主张/来源索引；人类verified状态保持unverified。

复算在项目内新目录执行：`PYTHONDONTWRITEBYTECODE=1 python3 calibration.py --output-dir new-rerun`。默认Python3.9.6+NumPy2.0.2可执行计算；原生EDA要求Python3.11，实际用了本机已有python3.11。重新运行robustness.py前需要为其完整复算目标提供新目录，现有rerun不应覆盖。绘图设置MPLCONFIGDIR/XDG_CACHE_HOME到本项目。

## 真实完成层级
已完成输入审计、冻结实验、必要稳健性、完整复算、图表数字/视觉检查、中文短稿、科学证据单元复核和引用身份/语义核查。最后manuscript-review的begin因阶段截止/交付预留而拒绝；该专业稿件复核未完成，没有伪造完成回执。故交付层级是“可复现的教学短稿”，不是通过全稿专业复核的终稿，不是投稿就绪。没有人类作者确认、独立同行评审或外部研究消息。

## 恢复与问题
原20分钟预算起点14:17:07Z，总截止14:37:07Z；reserve=120秒。phase.json、*-start/finish/work.json、actions.jsonl、delivery-status.json和delivery-manifest.json保留真实动作/成本/专业收据。八个已完成专业步骤check均通过，语义不由check认证。

原生EDA默认Python3.9报zip(strict=True)错误，复用现有Python3.11重跑成功。reassess首次因blocker未先repair登记拒绝，保留错误后按真实修复登记继续。SciPilot profile_data在缺SciPy环境仍实际成功，未假定失败。元数据文字曾误读4批次，analysis-amendment.md纠正为3训练/2测试，保留原文与数值，不修改冻结阈值或为了成绩重分测试。网页版快照保存时遇到stdout编码问题，转ASCII Unicode转义成功；网络传输总字节没有独立计量，不冒充0。

来源必调选择同14库匹配入口，不是每篇论文调用全部14库。当前使用Galaxy-Dawn/claude-scholar、K-Dense-AI/scientific-agent-skills、Haojae/scipilot-figure-skill。使用K-Dense的流程软件致谢已写入短稿，arXiv当前v2身份实际核查。
