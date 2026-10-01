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
{"R1": {"value": 0.123456, "unit": "ratio", "outcome": "accuracy", "time": "6 months"}}
```

若正文实际为`Accuracy was 12.35% at 6 months.`，可直接复用稿件构建记录（Python需能导入同目录`result_links.py`）：

```python
from pathlib import Path
from result_links import build_links, audit_links

root = Path("PROJECT").resolve()
sources = [{"id": "frozen", "path": "results.json", "versions": {
    "data": {"path": "data.csv"}, "code": {"path": "analysis.py"},
    "execution": {"path": "execution.json"}}}]
# Existing build rows supply locations and display rules, not another copy of results.
rows = [{"path": "draft.md", "result_id": "R1", "role": "body",
         "locator": {"line": 1}, "unit": "percent",
         "numeric": [{"field": "value", "decimals": 2}]}]
data = build_links(root, sources, rows)
report = audit_links(data, root)
assert report["passed"], report
```

`build_links(root, sources, occurrences, claims=())`只读已有输出，返回可交给`audit_links`的payload；不写新结果台账、不搜索全稿论断。来源清单使用`id,path,sha256?,versions?`；构建行的`path`可换成`artifact: {path,sha256?}`。缺哈希时按当前真实文件冻结，已有哈希不匹配时抛出`ValueError`，不能静默更新。构建行支持`source_id`（多来源时必需）、`role`、`locator`、`result_id`、目标`unit`，以及数值`field,decimals,rounding,text,offset,recomputed,tolerance`；省略`numeric`时生成`value`映射。`text`缺省按来源原值、单位换算及显示精度生成；显式显示文字也须经审计核对。语义仅复用源端标签并核对当前定位实际文字，表头等可用`semantics`提供独立定位。

只在实际取得、运行或导出后冻结哈希；为修复失败而单独刷新哈希不会使错误文本通过。来源记录也可自带`versions`覆盖共享版本；数值来源缺少`data`、`code`或`execution`身份时报告pending，不宣称已完整绑定。直接使用审计payload的旧调用仍可继续。

`locator`均为1起算：Markdown／LaTeX／文本使用`line`或`line_start`（二选一）及可选`line_end`；DOCX使用XML顺序`paragraph`（含空段与表内段）或正文表格的`table,row,cell`；PDF使用`page`加提取文本的行／范围。按实际文件格式拒绝混合或不适用坐标，给MD附加table字段不能获得表格关系。PDF调用已安装`pdftotext`或`pypdf`，缺失、扫描页无可提取文本时清楚报告未检查。DOCX读原始XML；这些定位不证明格式或视觉质量。数字重复时用零起算字符`offset`指定当前定位文本内的那一个。

来源声明的`unit,direction,denominator,outcome,population,sample,time,comparison,model,implementation,split,uncertainty,effect_type`可放在原记录或`semantics`中。普通语义用`{value, labels:[...]}`定义源端允许的显示文字。模型／实现复算等价另用冻结源的`equivalent_values`声明；显示标签不构成科学等价授权。目标映射有自己的`locator`时仍检查该真实范围的否定。单位也须绑定实际数字：独立单位定位只有真实DOCX同列首行表头等已定义关系可自动绑定；明确错单位报错，普通另一行的说明或未确定关联进入pending。`coverage.numeric.unit_binding`报告紧邻数字、同列表头或待复核。只自动处理明确的比例／百分数、s／ms、g／mg和m／cm／mm转换；百分比与百分点保持不同含义。分母为正整数计数；区间类型用`uncertainty`或`uncertainty_type`记录。

显示以十进制`half-even`（默认）或`half-up`及`decimals: 0..12`核对。`tolerance: {abs, rel}`只能与`recomputed: {source_id, result_id?, field?}`共同使用；先核另一份真实、哈希绑定输出的科学身份与量纲，再转回原来源单位比较容差。冻结JSON数值和转换／差值／容差计算保留输入精度，零容差不会因默认28位Decimal上下文而抹平差异；数值语义scalar对外用精确字符串，payload和报告仍可JSON序列化。`abs`使用原来源单位；`rel`使用换算后两个绝对值的较大者。结局、总体、比较、分区、时间、效应身份缺失时进入定位pending；其余已声明字段也必须相符，模型／实现只接受源定义的明确等价。主值／estimate可互认，不能用上下界冒充主值。容差不放宽正文显示。

局部点值、摘要或图注可只映射其实际字段；不要求每次重复完整设计。`coverage.occurrences`列角色、定位、覆盖字段与该次未覆盖字段；`coverage_gaps`按同一来源、结果、稿件文件汇总缺失的主值、区间及源语义，并产生`manuscript_fields_uncovered`待补关联。遗漏主值不能靠核对端点得到全稿覆盖。源未声明的科学信息不能由脚本补成证据。

`coverage.relationships`限实际可定位的局部关系：同一句内简单主值与主体连接、区间端点顺序／明确上下限标签、DOCX相邻左侧主体单元格或同列首行结局表头。可用`subject_field`选模型、实现、结局或总体；默认为本地映射的模型、实现、结局。已知主体错绑、端点交换及直接否定报错；比较阈值（如`lower than 410 ms`）不能认作精确主值，进入定位pending。主体只在另一句出现、未知连接词、复杂否定范围或无法确认的表格关系也进入pending。全段词语共现不能代替关系核对，`not an increase`也不能借独立定位变成增加。对复杂语言、因果解释、完整科学真相仍需实际阅读审查。

`coverage.bytes`、`coverage.numeric`与`coverage.declared_semantic`分别列出实际角色、位置和版本；关系覆盖及语义待复核单列，任何通过都不代表科学真实性或视觉验收。

理论来源`type: theory`记录`proposition`、`conditions`列表和`proof: {path,sha256,locator,text}`；目标`bindings.proposition.text`及`bindings.conditions.texts`逐项绑定。解释来源`type: interpretive`记录`interpretation`及`snippets: [{path,sha256,locator,text}]`，目标绑定`bindings.interpretation.text`。审计读取证明／片段的真实定位和版本，但不宣称证明正确或解释充分。

`claims: [{id,artifact,locator,text,result_ids}]`可记录待关联的关键论断。对应链接使用同一`claim_id`、稿件版本与定位；缺关联时`pending`／`unlinked`给出论断文字、位置及下一步。覆盖只限已声明论断，不能据此声称自动发现了所有主张。

## 渲染依赖

真实导出后保存`artifacts: [{id,path,sha256}]`和`renders: [{output,inputs:{源id:本次使用的sha256},output_sha256,renderer:{name,version},command?}]`。`command`只作出处记录，审计不会执行。编辑源、图表、引用、构建代码等都是输入节点；Word→PDF、LaTeX→PDF或更长链分别记录实际转换，勿编造不存在的生成关系。

```python
from result_links import audit_render
import hashlib
def artifact(name):
    return {"path": name, "sha256": hashlib.sha256((root / name).read_bytes()).hexdigest()}
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
