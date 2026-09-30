# 实际操作记录

- 完整读取 `suite/requests/constrained-design.comparison.0.json`（包括 initial_skill_text、user_prompt 与嵌入材料）及 `common-options.json`；没有再次读取 Skill 入口。
- 运行冻结工作副本 `evaluations/run_host.py read --help`。所有额外来源读取均通过其 read CLI，记录于 `resource_reads.jsonl`：project 类为当前快照的 `references/research-quality.md`、`protocol.md`、`provider-policy.md`、`execution-handoff.md`；material 类为冻结工作副本的 `evaluations/fixtures/rc2/design.md`。没有读取其他 trial、评分标准或版本答案，没有调用外部专业 Skill、其他助手或网络来源。
- 推导完整联合分布及校准公式；参数化情形 A、证明 f 严格递增、构造锐界端点；解出情形 B；分析真值采样和相关/独立复制报告的识别条件。
- 新建并实际运行 `verify.py`，使用指定 Python `LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python`。返回 exit code 0 和 PASS；精确分数验证全部端点与约束，并复算二项尾概率和 K=0 的单侧上限。有限网格检查仅作代码核对，单调性与锐界依据 answer.md 中的解析证明。
- 文件仅写入本 trial：`answer.md`、`operation.md`、`verify.py`、`resource_reads.jsonl`。冻结候选源码未改动。
- 未实施：购买 24 个真值、抽样、实际复制测量、联合似然推断真实样本或任何真实研究实验；无真实 K,S。24 样本精度、真值正确性、实际抽样有效性与复制独立性尚无实测验证。
