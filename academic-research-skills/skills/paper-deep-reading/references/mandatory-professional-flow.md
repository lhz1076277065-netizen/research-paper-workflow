# 每个专业步骤必须先调用指定来源

本规则适用于总控与所有独立专业 skill，优先于旧参考中“候选”“按需调用”“独立继续”或 host_fallback 的说法。维护、安装与预算记录不属于科研专业步骤，不启动科研。选题、检索、精读、设计、数据、分析、图稿、审查、投稿准备和局部写作都适用；不得先凭通用推理完成成果再补记调用。

每一步必须从用户指定的14个仓库中调用匹配的真实入口，读取入口及本步需要的资源，实施其专业流程，再将产物用于下一步或交付。Agent在该流程内分析判断；禁止绕开它另写通用答案。参考书、代码或工作台须如实记录其类型；参考或导出函数不能代替完整专业流程。

## 必经操作

1. 将当前请求和真实输入保存到任务目录；完整研究沿用阶段、预算和最新指令，begin须加 `--phase project/phase.json`，在预算检查后绑定当前阶段。执行 `professional_flow.py begin`，默认按能力路由选取已核实的源码缓存，无须用户另行点名仓库。工具输出真实入口全文、所需专业工作、边界与准备记录。必须阅读输出及本步需要的支持文件后再工作。
2. 按上游流程完成**本次请求范围**的专业工作，保存结果；记录来源条款怎样改变本步决策及结果位置。局部写作不扩展成全研究；固定问题不重新发散选题；不为完成调用强行启动应用、模型或无限循环。
3. 完成 work-report 后执行 `finish` 和 `check`，检查通过才移交产物或进入下一专业步骤。只有准备源码、读取指导、运行无关函数、历史测试或早于本步的产物不能完成本步。完整研究的阶段出口还要提交该阶段所有已调用步骤的开始/完成记录。

```bash
python3 scripts/professional_flow.py begin --capability topic-novelty \
  --task project/request.md --input project/materials.md --out project/topic-start.json
# 阅读返回的真实 SKILL.md 及有关支持资源，实施专业工作，生成 candidates.md。
python3 scripts/professional_flow.py finish --started project/topic-start.json \
  --output project/candidates.md --work-report project/topic-work.json --out project/topic-finish.json
python3 scripts/professional_flow.py check --started project/topic-start.json --finished project/topic-finish.json
```

work-report 是短操作记录，字段如下；actions覆盖实际返回的所有产物。source_excerpt引用已准备文件中的原文，output_excerpt引用本步文本结果，applied说明具体应用与结果；它们不是打卡口号。非文本产物用 output_sha256 和 observation 记录实际检查结果，保留图稿的数值与视觉复核。

```json
{
  "step_id": "begin返回的id",
  "scope": "requested_step",
  "omitted_required_work": [],
  "functions_run": false,
  "actions": [{
    "source_file": "真实入口或所读支持文件的仓库相对路径",
    "source_excerpt": "对应专业条款原文",
    "applied": "本次怎样实际实施该条款，产生什么判断",
    "output": "project/candidates.md的实际路径",
    "output_excerpt": "当前结果中的对应原文"
  }]
}
```

工具核对来源、先后次序、任务/输入/输出版本和关联，不自动证明专业语义正确。当前Agent仍须核对本步所需流程是否实质完成，不得填写虚假动作或把部分执行写成完成。材料不足可形成该流程支持的条件判断或明确障碍，不能虚报科研结果。

## 自动路由与不可用时的处理

`assets/capability-index.json` 的 professional_routes 覆盖所有专业子 skill，并含表达、演示与工作台子流程；默认选题为 Orchestra 的 brainstorming-research-ideas。已经固定的问题用同库清单内 Scholar 的 research-ideation 问题卡/证据门，不再次启动开放选题。指定另一匹配入口时用 --source；不能用不相关入口凑数。支持文件允许按本步需要读取，不要求全量载入。

缺缓存时可在已授权联网范围内加 --allow-network，仍逐文件核验固定 commit/blob。源不可用、能力不匹配或必要依赖失败时停止**受阻的专业步骤**并报告缺口；只允许调用这14库内另一已核实匹配入口，禁止 host_fallback 或自行推理冒充完成。确需新入口，先在同14库发现、读源码与依赖、固定版本、补充索引和实际路由，再开始该步骤。文献、数据库和普通科研软件不受 skill 仓库清单限制。

同一任务同一阶段的已完成步骤与同版源码可复用；check须确认请求范围及输入/输出仍对应，不用旧阶段记录完成新阶段。新问题、新材料或新版本不得借旧记录绕过调用。恢复读取当前步骤记录、最新指令、产物与下一动作；失败不重置预算，不反复安装。旧记录信息不足保持unknown，不虚称符合新规则，也不重跑已结束研究。
