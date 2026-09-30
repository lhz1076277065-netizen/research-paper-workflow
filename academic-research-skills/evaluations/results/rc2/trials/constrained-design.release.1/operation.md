# 实际操作

完整读取本次请求及 `common-options.json`，直接采用请求已提供的 `initial_skill_text` 和合成材料，未重新读取入口或材料文件。采用 `research-design` 完成此局部数学设计任务。按入口要求，经 `run_host.py read` 读取 `references/research-quality.md` 与 `references/provider-policy.md`；额外读取记录在 `resource_reads.jsonl`。本题的封闭二元模型可用直接推导处理，未调用外部专业 Skill、其他助手或子代理，未读取其他试验答案、评分、版本映射或 suite 清单。

交付 `answer.md`：推导完整观测分布、A 的锐区间与满足全部约束的端点世界、B 的唯一解；比较三条数据路线，并给出 24 个真值的分组校准、有限样本置信集合、结果分支及复制报告的独立性边界。交付标准库复核 `verify.py`，使用有理数枚举三个参数世界的二元潜变量状态，检验全部约束和完整观测分布，复核目标公式与导数公式，并核查依赖复制反例和独立复制等式。

实际执行以下命令，退出码 0，标准输出保存为 `verification.txt`；两个 PASS 均通过。全区间单调性由答案中的解析证明给出，代码的导数检查取三个可行点。

```sh
'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' -B 'LOCAL_EVIDENCE_ROOT/trials/constrained-design.release.1/verify.py'
```

未采集真值、真实研究数据、复制报告或撰写论文；没有未来样本结果。实际决策阈值、容忍误差和 24 个样本能达到的精度仍未知。操作与产物均位于本试验目录；未修改冻结源码、材料或其他目录，未作版本优劣判断。
