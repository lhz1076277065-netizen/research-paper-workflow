# 当前Agent的研究执行原则

由当前Agent及其现有模型完成研究；其原生子代理可按需分工，不另找宿主或推理服务。不要扫描本地大模型、端口和登录配置，不为并行调用其他Agent产品；其他宿主不可用与本研究无关。研究对象本身需要预测模型或训练算法时，按研究设计使用科学软件，这不等于更换执行你的助手。

默认推进用户的真实研究目标，不自行降成验收小题。先问“解决哪个重要问题、带来什么新理解或能力”，再选可行材料与方法；难度和数据缺口用于设计下一步，不是停止创新的借口。常规可逆工作自主推进，重大选题/核心主张/数据范围改变才向用户简短说明并确认目标。

外部专业Skill从用户指定13仓库的本地安装或当前GitHub版本选择。可调用普通检索、数据端点、科学库并写原创代码；外部Skill来源超出指定清单时先提出替换理由，不静默换源。不全量安装、不把仓库名称当已调用。

只有完整项目才维护一份简短研究路线板；局部任务直接完成。阶段展示核心问题、主要结论、对应实际产物、所用Skill和下一项关键判断，不重复建立大量台账。旧成果可复用但说明真正的生成路线，不能追认为新Skill已执行。

科研价值、事实证据与表达质量分别改进。审查不足时主动补证、比较、重设计；不要靠删必要反证、包装成顶刊措辞或换一个低目标结束。准确表述局限一次即可，正文以问题、贡献、证据和科学解释为主。

本次明确的当前宿主、指定来源与正式研究目标覆盖旧版宽泛执行默认值；原专业协议的科学方法和证据细节继续按适用部分使用。

## 结果出现位置与导出版本（按需）

`provider_runtime.py audit --input links.json --root PROJECT`分派到`result_links.audit_links(data, root)`；`kind: render-dependencies`分派到`audit_render`。两者只读真实文件，不运行研究或渲染命令。所有文件使用项目内相对路径和SHA-256；绝对路径、越界路径及越界符号链接返回诊断。

来源直接使用实际冻结JSON／CSV：JSON可由`result_id`作键、以`results`列表保存，或是含`result_id`的记录列表；CSV需要唯一表头和`result_id`列。下面的数值仅说明协议，不构成研究证据：

```json
{"R1": {"value": 0.123456, "unit": "ratio", "time": "6 months"}}
```

若正文实际为`At 6 months the value was 12.35%.`，可对已有文件构造最小审计（Python需能导入同目录`result_links.py`）：

```python
import hashlib
from pathlib import Path
from result_links import audit_links

root = Path("PROJECT").resolve()
def artifact(name):
    return {"path": name, "sha256": hashlib.sha256((root / name).read_bytes()).hexdigest()}

data = {"kind": "result-links", "sources": [{
    "id": "frozen", **artifact("results.json"),
    "versions": {"data": artifact("data.csv"), "code": artifact("analysis.py"),
                 "execution": artifact("execution.json")}}],
    "links": [{"result_id": "R1", "role": "body", "artifact": artifact("draft.md"),
        "locator": {"line": 1},
        "numeric": [{"field": "value", "text": "12.35", "decimals": 2}],
        "semantics": {"unit": {"value": "percent", "text": "%"},
                      "time": {"value": "6 months", "text": "6 months"}}}]}
report = audit_links(data, root)
assert report["passed"], report
```

只在实际取得、运行或导出后冻结这些哈希；为修复失败而单独刷新哈希不会使错误文本通过。来源记录也可自带`versions`覆盖共享版本；数值来源缺少`data`、`code`或`execution`身份时报告pending，不宣称已完整绑定。

`locator`均为1起算：Markdown／LaTeX／文本使用`line`或`line_start`和`line_end`；DOCX使用XML顺序`paragraph`（含空段与表内段）或正文表格的`table,row,cell`；PDF使用`page`加提取文本的行／范围。PDF调用已安装`pdftotext`或`pypdf`，缺失、扫描页无可提取文本时清楚报告未检查。DOCX读原始XML；这些定位不证明格式或视觉质量。数字重复时用零起算字符`offset`指定当前定位文本内的那一个。

来源声明的`unit,direction,denominator,outcome,population,sample,time,comparison,model,split,uncertainty,effect_type`都要对应实际文字；也可集中在来源`semantics`中。普通语义使用`{value, labels:[...]}`定义源端允许的文字，不允许目标自行发明同义关系。目标映射有自己的`locator`时可核对同一稿件的单位表头或模型说明；否则单位应紧邻数字。只自动处理明确的比例／百分数、s／ms、g／mg和m／cm／mm转换；百分比与百分点保持不同含义。分母为正整数计数，区间`lower,upper`应完整映射；区间类型用`uncertainty`或`uncertainty_type`记录。复核每个关键句子的整体语义仍由实际阅读完成。

显示以十进制`half-even`（默认）或`half-up`及`decimals: 0..12`核对。`tolerance: {abs, rel}`只能与`recomputed: {source_id, result_id?, field?}`共同使用，对另一份真实、哈希绑定的原始输出比较；容差不放宽正文显示。`coverage.bytes`、`coverage.numeric`与`coverage.declared_semantic`分别列出实际角色、位置和版本，任何通过都不代表科学真实性或视觉验收。

理论来源`type: theory`记录`proposition`、`conditions`列表和`proof: {path,sha256,locator,text}`；目标`bindings.proposition.text`及`bindings.conditions.texts`逐项绑定。解释来源`type: interpretive`记录`interpretation`及`snippets: [{path,sha256,locator,text}]`，目标绑定`bindings.interpretation.text`。审计读取证明／片段的真实定位和版本，但不宣称证明正确或解释充分。

`claims: [{id,artifact,locator,text,result_ids}]`可记录待关联的关键论断。对应链接使用同一`claim_id`、稿件版本与定位；缺关联时`pending`／`unlinked`给出论断文字、位置及下一步。覆盖只限已声明论断，不能据此声称自动发现了所有主张。

## 渲染依赖

真实导出后保存`artifacts: [{id,path,sha256}]`和`renders: [{output,inputs:{源id:本次使用的sha256},output_sha256,renderer:{name,version},command?}]`。`command`只作出处记录，审计不会执行。编辑源、图表、引用、构建代码等都是输入节点；Word→PDF、LaTeX→PDF或更长链分别记录实际转换，勿编造不存在的生成关系。

```python
from result_links import audit_render
render = {"kind": "render-dependencies",
    "artifacts": [{"id": "tex", **artifact("draft.tex")},
                  {"id": "pdf", **artifact("draft.pdf")}],
    "renders": [{"output": "pdf", "inputs": {"tex": artifact("draft.tex")["sha256"]},
                 "output_sha256": artifact("draft.pdf")["sha256"],
                 "renderer": {"name": "actual-renderer", "version": "observed-version"}}]}
report = audit_render(render, root)
```

导出时的输入／输出快照与当前文件清单分开保留。更新当前Word或LaTeX哈希不会更新旧渲染的输入快照。审计比较实际字节，检验依赖图无环，沿传递依赖输出`impacted_rebuild_targets`和`rebuild_order`；按该顺序真实重建后更新各步快照、复查数字与关键文字，并实际观察需要视觉检查的PDF页。已记录渲染器版本只是出处，审计不会凭它宣称渲染器已再次运行。

`run-script`可显式传`--python PROJECT_ENV/bin/python --workspace PROJECT`，将已选提供方放在同一项目解释器及工作目录内执行；省略时保留原来的解释器／新输出目录行为。回执记录实际解释器、工作目录、耗时、退出状态与日志，不以存在回执代替研究完成。
