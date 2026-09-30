# 宿主行为评估：固定场景已实际运行

本目录不进入日常Skill上下文。run_host.py准备配对材料，再调用操作者提供的实际Agent适配命令；不绑定模型、品牌、API或子代理。

```bash
python evaluations/run_host.py prepare --skills skills --comparison-skills /path/to/v3.1.0/skills --cases evaluations/quality-cases.json --out evaluation-suite --repetitions 1
python evaluations/run_host.py run --suite evaluation-suite/suite.json --command-json actual-adapter.json --host-label ACTUAL_HOST --model-label ACTUAL_MODEL --out evaluation-runs
```

actual-adapter.json为argv数组，包含`{request}`和`{output}`占位符。该适配器应在真实的新上下文中加载请求及对应入口，提供相同工具/权限/预算，写出答案，并可额外记录资源读取与工具轨迹。没有适配器时只prepare，不制造运行结果。不要把命令行标签当自动识别出的真实模型身份。

比较无Skill、当前版本和可选旧版。盲评实际任务完成、专业正确性、无依据事实、创造性价值、额外问题、上下文与工具成本。包含局部改写、形式证明、仅摘要阅读、仅选刊和新路线构思。软件夹具只验证请求交接和日志，不计入模型能力评估。

上游export_figure函数的实跑脚本另见upstream_export_smoke.py；需要提供已读的真实源码文件。它测试指定导出参数，不代表完整上游Skill或论文质量。


## 三个完整成果场景

`quality-cases.json`提供研究判断、正式主图和完整全文场景；fixtures/heldout是明确标注的固定合成材料，未写入专业参考里的判断示例。使用prepare --cases evaluations/quality-cases.json指定这些场景，与默认五个边界任务分开。准备请求时不把评审标准或其他组答案传给执行者。

比较未提供本项目Skill、3.1.0与候选版；在同一当前Agent内用新的独立上下文、同模型/工具/输入和权限执行，不寻找其他宿主或本地LLM。分开保存工程检查、执行轨迹和盲评内容。首次少量试验是开发观察，不证明跨学科普遍提高。盲评研究问题/知识增量、设计区分解释、证据强度、主图关键比较、全文论证与事实保持；运行成本另报，不计算统一顶刊分数。实际对照、路由和续接结果及未取得的指标进入本版报告。

## 本轮实跑及复核

九次三组场景执行、三次研究判断复测，均通过原生协作工具在新上下文中实际完成。另有三份匿名内容审查、两个描述语义路由观察和一个局部续接。prepare 用于冻结请求；没有把未运行的 CLI 适配器当作执行结果。详细产物、映射和分项发现见 [QUALITY_REPORT.zh-CN.md](results/QUALITY_REPORT.zh-CN.md)。

研究判断的首次观察用于修复两处入口导航，其复测不能称未接触留出测试或同版本稳定性验证。图与全文资源没有在看到其结果后调整。reserved-cases.json 是未运行、未用于本轮调试的保留材料；发布后成为公开样例，不计作通过。

公开证据只替换文本中的本机路径，原件与副本的 SHA-256 见 results/published-evidence-ledger.json。旧 request/subjects 哈希在脱敏时仍指原件，重新运行应 prepare 新请求并取得所记录的专业源。未将上游 checkout、依赖、字体和私有认证装入包；涉及这些路径的原始产物代码需按锁定来源及自己的环境适配，不宣称脱敏副本原样可执行。日常发行省去整个 evaluations 目录，实际证据随源码版及 GitHub 报告提供。
