# v3.3.1 研究规则迁移

沿用现有路线板和研究笔记：贡献锁定补实质意义与反方审查，构思补观察到不同预测的理由，已成立贡献按原范围完成论文，不把可选扩展列为必需。最终表达的优先Skill不再是默认硬性依赖；可选记录检查器接受其他库内实现或`final_expression.operation`实际工作，用户明确要求的来源用`required_repository`记录。原provider_use、原稿/终稿身份和事实复核关联继续有效。字段详情见[记录检查说明](docs/research31-usage.md)。

## 保留的v3.3.0选题增强

维护源和生成规则保持不变。安装时用完整能力目录替换所选旧目录；按现有安装器备份并核验。选题新增两份按需参考，跨篇学习、现实需要与科学未知进入候选比较；已固定的局部改稿、选刊继续直接执行。算法、成熟方法和基础理论均按所解决的问题判断。

来源表新增 Orchestra，保留原13来源，补充 K-Dense 构思角色。旧记录继续有效；新入口在使用时动态发现，不必全量安装或执行来源库。运行接口与六维画像保持不变；稳定 v3.2.0 作为比较/回退基线。

日常运行包不包含开发验收档案。以下保留 v3.2.0 通用接口说明。

# v3.2.0 迁移与接口冻结

本版以已验收rc.5为基础，仍为1个可选总控与18个独立能力、16画像及14条按需研究路线。用完整能力目录替换所选旧目录；专业协议、三个详细推演分片和实际项目材料保留。维护源仍为src/common、src/quality31/payload及各能力protocol.md，由现有build_release.py生成。

冻结rc.5的任务/返回封装、result-links schema和调用形状：build_links(root, sources, occurrences, claims=())、audit_links(data, root)继续使用。正式版只更新版本元数据、迁移解释、导航和发行证据，不新增检查流程。后续3.2.x仅按真实缺陷或小型兼容需求改动；新能力以新的真实研究任务验证。

复算先核双方科学身份与量纲，再换到原源单位比较容差；模型/实现的equivalent_values由冻结源授权，labels只定义显示文字。正文舍入不被容差放宽。原始JSON、换算和容差保留Decimal精度，公开数值语义scalar可序列化为精确字符串。复杂关系保留带实际定位的pending。

## 总体作为主体时显式指定

冻结源的population为Cohort A、unit为s，实际句子为“Cohort A mean = 0.41 s”。已有link的数字映射和文件定位照旧，关系字段可写为：

```json
{"subject_field":"population",
 "semantics":{"population":{"value":"Cohort A","text":"Cohort A"},
              "unit":{"value":"s","text":"s"}}}
```

这是已有link的字段片段。若只映射population而省略subject_field，自动主体只从本地model、implementation、outcome选取，可能报告primary_subject_unbound；显式指定population后才按总体核主值关系。多个主体、跨句归属或未知连接仍需要定位阅读，不通过补一个字段认证句子的完整科学含义。

## 跨文件覆盖不自动合并

同一source_id/result_id在draft.md正文映射了value、unit、model，而caption.md只映射value和unit：draft.md的model不会补齐caption.md。coverage.occurrences列出各次角色与当地字段；coverage_gaps按(source_id, result_id, artifact.path)汇总。即使两个文件属于同一稿件、或是DOCX/PDF两种导出，路径不同就各自报告。

需要检查caption.md的该字段时，补它自身真实文字和定位。若主文与图注都在同一artifact.path，不同角色的实际出现可以在该文件内补全覆盖。这个范围解释延续现有接口，不增加跨文件合并或新的人工流程。

## 其他使用边界

比较阈值不当作精确主值。独立单位定位仍核数字旁单位；仅真正DOCX同列首行表头等已定义关系支持自动绑定。定位须与实际格式相符，Markdown不能附伪表格坐标绕过检查。旧的词共现映射可能需要补关系定位。程序只检查声明位置和源语义，不自动发现全文论断，不判断科学真相或发表新颖性。

三个examples参考文件仍经质量主线与路线锚点按需到达；19个模块不依赖相邻能力或src。正式包绑定源码提交与逐文件摘要；开发历史留在源码档案。[当前支持范围](docs/COMPATIBILITY.zh-CN.md)。
