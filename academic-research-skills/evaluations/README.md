# 宿主行为评估：驱动器可用，真实模型对照待运行

本目录不进入日常Skill上下文。run_host.py准备配对材料，再调用操作者提供的实际Agent适配命令；不绑定模型、品牌、API或子代理。

```bash
python evaluations/run_host.py prepare --skills skills --comparison-skills /path/to/alpha5/skills --out evaluation-suite --repetitions 3
python evaluations/run_host.py run --suite evaluation-suite/suite.json --command-json actual-adapter.json --host-label ACTUAL_HOST --model-label ACTUAL_MODEL --out evaluation-runs
```

actual-adapter.json为argv数组，包含`{request}`和`{output}`占位符。该适配器应在真实的新上下文中加载请求及对应入口，提供相同工具/权限/预算，写出答案，并可额外记录资源读取与工具轨迹。没有适配器时只prepare，不制造运行结果。不要把命令行标签当自动识别出的真实模型身份。

比较无Skill、当前版本和可选旧版。盲评实际任务完成、专业正确性、无依据事实、创造性价值、额外问题、上下文与工具成本。包含局部改写、形式证明、仅摘要阅读、仅选刊和新路线构思。软件夹具只验证请求交接和日志，不计入模型能力评估。

上游export_figure函数的实跑脚本另见upstream_export_smoke.py；需要提供已读的真实源码文件。它测试指定导出参数，不代表完整上游Skill或论文质量。
