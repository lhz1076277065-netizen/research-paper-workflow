# rc.5 定向独立工程审查

结论：修复前有 **4 个可复现的自动假通过**，作者已修复共享根因。修复后独立重跑 **20 项实际文件样例、四个调用入口，unexpected=[]**；本轮无未修复的可操作发现。这里评估文件／字段／关系绑定，不判断科学句子真值、原创性或出版资格。比较阈值等超出简单主体—精确主值范围的句子现在留在实际定位的 pending。

审查基线：rc.4 `ed4c86ec00593de48d2cb88109afe4191d1bfe04`。审查对象包括 `src/common/scripts/result_links.py`、源 schema、runtime/integrity 文档、结果关联和真实 PDF 测试、PDF 报告脚本、父仓库 CI 工作流及 provider_runtime/research31 实际调用链。未改运行时文件。

执行解释器：`/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`，实际版本 **3.12.14**。系统 3.9 未用于审查。

## 修复前发现（均已独立验证修复）

| 优先级 | 位置（修复前快照行号） | 可复现问题及必要行为 |
|---|---|---|
| P1 | `result_links.py:399–406` | 主值实际变为 `410.0 g`，但 unit mapping 指到另一行 `Documentation unit: ms.`，仍按秒→毫秒换算并通过。独立 locator 跳过数字旁单位及关系检查，错误量纲的实际数字被接受。只允许经过实际坐标验证的单位表头；普通独立说明无法绑定时留 located pending，明确冲突单位应报错。该跳过逻辑 rc.4 已存在，rc.5 仍未封住。 |
| P1 | `result_links.py:512–518`，`_located` 与 schema locator | Markdown 主句为未知方法，另一行 `Solver A is background.`；给两个 locator 添加伪 `table,row,cell` 坐标就获得 `table_subject_coordinates=checked`。Markdown 提取仅使用 line，而关系检查信任额外坐标。必须验证实际文件格式和 locator 类型；混合 locator 不得建立表格关系。该自动表格关系分支为 rc.5 新增。 |
| P2 | `result_links.py:543–557` | `Solver A latency was lower than 410.0 ms ...` 是比较阈值，仍得到 `primary_subject=checked` 且全审计通过。删除语义 token，再清除 `lower/than` 等白名单词，抹掉了关键连接意义。比较主值应定位 pending；保持已支持的简单精确值句式。该自动关系分支为 rc.5 新增。 |
| P2 | `result_links.py:294` | 原值 `0.41 s`，复算值 `0.41000000000000000000000000001 s`，`abs=0,rel=0` 仍通过。乘除在默认 Decimal 28 位精度中先舍入，记录的 converted_value 变为 `0.4100000000000000000000000000`，容差检查看不到真实差值。换算／差值计算须保留输入精度；这是 rc.5 新增换算路径的回归。 |

修复前四个样例不仅 `audit_links` 返回 `passed=true, errors=[], pending=[]`，还在 **provider_runtime.audit_payload、research31.audit、provider_runtime.accept_result** 返回通过。修复后四入口均正确返回未通过。

## 独立复现材料与命令

小型复现脚本：`independent-review/probe.py`（修后 20 项），`independent-review/probe-before.py`（原始 17 项）。原审计器／调用器快照在 `independent-review/source-at-review/`；实际测量输入、可执行计算代码、执行输出、冻结 JSON、稿件 MD、payload、handoff、返回 envelope 和完整报告按样例保留于 `independent-review/before/`。修后材料在 `independent-review/after/`，对应源快照在 `independent-review/source-at-after/`。

在仓库根运行（输出目录须尚不存在）：

```sh
/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 evaluations/rc5/engineering/independent-review/probe-before.py --scripts evaluations/rc5/engineering/independent-review/source-at-review --out evaluations/rc5/engineering/independent-review/reproduced-before
```

初次输出、退出码 1（明确表示发现与期望不符）：

```json
{"cases":17,"unexpected":["comparative_threshold","unrelated_unit_locator","mixed_markdown_table_locator","exact_tolerance_precision_loss"]}
```

`before/summary.json` 记录全部入口结果及快照哈希。审计器快照 SHA256：`efc12d7e5474005e96b70cb0abff1a446df4458dd82cdc7ee5da1bfe4d05003e`。

其余 13 个独立对照符合期望：基准实际值、正确秒／毫秒换算、同裸数字错误量级、不同 split、显示标签不能当科学等价、冻结模型／实现等价授权、独立定位直接否定、未知连接词 pending、端点交换、明确 upper/lower 标签、另一句背景主体、图注加正文覆盖、仅图注的全稿字段缺口。不是仅按测试总数接受。

## 修复后独立复跑

运行当前真实共享入口，未改源码：

```sh
/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 evaluations/rc5/engineering/independent-review/probe.py --out evaluations/rc5/engineering/independent-review/after
```

实际退出 0，输出 `{"cases":20,"unexpected":[]}`。保留目录不可覆盖；重复执行请指定另一个新目录。审计器 SHA256 为 `471b32401fa0b2f35ac5cafd1b2eea67f20cc8b9eb728212dbfd58f274fb92a2`，重跑完成后再次核对源文件哈希未变。

| 原发现 | 修后实际结果（四入口一致） |
|---|---|
| 比较阈值误认精确主值 | 无 errors；located pending `primary_value_is_comparison_threshold`，全审计未通过。 |
| 另一行 ms 掩盖实际主值 g | errors `Actual numeric unit differs from mapped unit: g`。 |
| MD 伪 table,row,cell | builder 先正确拒绝非法行；再用合法行构建 payload、向最终 payload 注入伪坐标，四入口均 errors `Mixed or inapplicable locator coordinates for .md`。不是把预期拒绝当脚本异常。 |
| 零容差高精度差值丢失 | 字符串与 JSON 数字 literal 两条路径均 errors `Recomputed numeric value exceeds tolerance: value`。 |

新增三个独立样例：

1. 复算源使用未加引号的 JSON literal `0.41000000000000000000000000001`，读取值保留全部十进制数字；对原值 `0.41` 的零容差拒绝有效。
2. 原源与复算源均使用上述相同高精度 JSON literal，显示仍按毫秒舍入；四入口正确通过。
3. 冻结源 `time:6.25, uncertainty:0.95` 使用 JSON 数字 scalar；builder payload 和四入口报告均直接 `json.dumps` 成功，无 default 编码器。`coverage.declared_semantic` 保存 `source_value:"6.25"` 与 `source_value:"0.95"`，规范化后仍匹配源意义与真实文本。

对这三个新增样例另调用真实 provider_runtime CLI，保存 `after/cli-checks.json` 的 argv／退出码及各样例 `cli-audit.stdout.json`／stderr。差值样例退出 2，输出可解析的正常拒绝报告；相等高精度与数字型语义样例退出 0，stdout JSON 可解析且 passed=true。没有把正确的输入拒绝误算成运行异常。

原 13 个有效对照继续符合预期；所有 20 项 `audit_links / provider_runtime.audit_payload / research31.audit / provider_runtime.accept_result` 结果逐样例一致。完整 `after/summary.json` 的 unexpected 为空。

## 现有测试与其余核对

```sh
/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -p 'test_result_links.py' -v
/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m unittest discover -s tests -p 'test_pdf_extract.py' -v
```

修复前结果：54 个结果／渲染关联测试通过。修复后独立重跑：**59 个结果／渲染关联测试通过，2 个真实 PDF 测试通过，均无 skip**。PDF 覆盖真实 pdftotext 和在新进程 `PATH=''` 中真实调用 pypdf 的有效文件、损坏 PDF、越界页；pypdf 的错误类型转换和实际回退测试有效，未用 mock 替代后端。

身份／单位／容差的基本改动有效：先核冻结科学身份、量纲一致后换算、abs 使用源单位、容差不放宽稿件显示、value/estimate 不能用上下界冒充、缺身份进入 located pending、科学等价仅接受冻结 equivalent_values。修复后的换算及容差计算保留高精度边界。

局部出现与同稿件字段覆盖分别报告；端点不会获得主值覆盖，简单图注可由正文补全。build_links 使用已有构建行、按源标签选实际文字，已有 source/target/version sha256 均经共享 artifact 校验，setdefault 不覆盖已有 sha256。复杂句关系和独立定位的未确定关联现在进入 located pending，明确单位冲突和非法坐标报错。

CI 文件检查：两个 matrix 分支分别安装 pdftotext 和固定 pypdf，并断言 pypdf 分支找不到 pdftotext；先清除旧回归／验证报告；run_all 保存逐用例状态；report_pdf_links 必须看到指定 PDF 用例状态为 passed，skipped 无法满足；同时重新执行真实 PDF 探测并上传实际 JSON／哈希材料。未运行 GitHub Actions，结论限代码检查和本机两个真实后端结果。

科学真值、完整论断关系、因果解释、原创性和视觉验收继续需要实际人工／代理阅读；工程通过不得用来代替这些判断。
