# v3.2.0-rc.5 迁移

用本版完整能力目录替换选定的rc.4目录；仍为1个可选总控与18个独立能力。维护源仍为src/common、src/quality31/payload与各能力protocol.md，运行build_release.py --write后用--check检查；项目材料与原始输出保留。

旧result-links封装继续接受。复算先核双方结果的单位量纲和科学身份，再把复算值换成原始结果单位使用容差。结局、总体、比较、分区、时间、效应类型等身份未绑定时进入有定位的pending；不适用字段可在冻结源明确声明。模型/实现的等价值只由冻结源semantics中的equivalent_values授权，labels仅作显示别名。正文舍入保持独立，容差不能放宽显示。

局部图注或表格不必重复全部设计字段：coverage.occurrences按角色列出当地覆盖与缺字段，coverage_gaps按同来源、结果与稿件汇总尚未覆盖的字段。主值归属、区间顺序、直接否定和有限表格坐标关系按已定义规则检查；复杂句式、未知否定范围或无法确定的关系进入pending。程序不发现全部论断，也不代替对关键句子科学含义的实际阅读。旧的词共现映射可能因此需要补关系定位。

比较阈值不能作为精确主值。独立单位定位仍核数字旁的实际单位；只有真正DOCX同列首行表头支持自动关联。定位须使用该文件格式的坐标，不能用Markdown上的伪表格坐标绕过主体检查。冻结JSON原值、换算与容差保留完整Decimal精度，零容差不会抹去高精度差异；数值语义scalar在公开payload中用精确字符串保持JSON可序列化。

复用真实稿件构建行调用result_links.build_links(root, sources, occurrences, claims=())，由已有result_id、角色、文件、定位与显示精度生成链接和当前哈希，减少重复填表。已提供的哈希会校验，不会为消除错误而刷新。实际API示例和边界见docs/runtime.md与docs/integrity.md。

详细推演保留在inference-examples.md、interpretive-examples.md和computation-examples.md，通过研究质量主线与原路线锚点按需到达。三个文件随每个独立模块生成，不要求新增总控、安装工具清单或更换执行模型。

CI分别运行实际pdftotext与仅pypdf的后端，旧PDF定位用例在两条路径都需通过；只缺对侧后端时，其专属用例可以明确跳过。CI上传新库完整回归与实际结果链接报告。rc.4报告保留在history/rc4-reports及evaluations/rc4；rc.5属于候选版本，研究比较的实测改进与文献原创性分别评价。
