# 每个专业步骤必须先调用指定来源

适用于总控与19专业能力，包括局部写作、选题、数据、实验、图稿和审查。维护/安装不启动研究。本规则优先于旧参考的候选、host_fallback或自行继续说法。

每步从指定14库调用匹配真实入口，阅读当前适用模式/必要资源，实施其流程后才能输出成果；不得先自行完成再补调用。参考资源、代码工具、Skill和工作台如实区分；准备、读指导和无关函数不等于专业执行。Agent在专业流程内判断，不要求每篇调用全部仓库。

## 必经操作

1. 保存当前请求与真实输入；完整/显式预算任务先登记phase并沿用最新指令/原预算。begin --phase绑定当前阶段；默认自动选已核验入口，stdout精简，完整收据仍存盘，--full可显示全文。必须打开guide_path读取本步相关段和支持文件，不能把返回路径当已读，不能为瘦身跳过专业流程。无需读取全部源码、能力索引或19个Skill。
2. 按上游流程完成本次范围，把具体条款、实施和输出位置关联。完整研究把现有[四段路线板](research-quality.md#四段科学论证主线)作为输入并回填本步支持/反证/边界；局部任务只记录有关主张。科研资料获取另遵守[容量与访问](data-acquisition.md)。
3. 写短work-report，finish/check通过才移交下一专业步骤或交付；完整研究出口核对当前全部专业收据。失败先[自主解阻](phase-control.md#自主解阻与继续研究)，不把状态填齐当完成。

```bash
python3 scripts/professional_flow.py begin --capability topic-novelty --task project/request.md --input project/materials.md --out project/start.json
# 实际阅读guide_path及相关资源并实施，生成本步输出。
python3 scripts/professional_flow.py finish --started project/start.json --output project/result.md --work-report project/work.json --out project/finish.json
python3 scripts/professional_flow.py check --started project/start.json --finished project/finish.json
```

```json
{
  "step_id": "begin返回的id",
  "scope": "requested_step",
  "omitted_required_work": [],
  "functions_run": false,
  "actions": [{
    "source_file": "真实入口或所读支持文件的仓库相对路径",
    "source_excerpt": "对应条款原文",
    "applied": "实际实施及如何改变判断",
    "output": "本步真实输出路径",
    "output_excerpt": "结果中的对应原文"
  }]
}
```

actions覆盖所有输出；二进制或超过8 MiB的文本产物用output_sha256、observation记实际观察，摘要分块计算。大文件是内存处理分支，不是研究停止条件。完整实证研究还按[本地数据全流程](local-data-workflow.md)检查实际前序产物。工具检查来源、先后、文件版本及关联，不能自动认证语义/原创性。省略必要工作、虚填动作、引用早于本步的成果不能通过实质验收。

## 自动路由与不可用时的处理

professional_routes默认选题Orchestra brainstorming-research-ideas；已固定问题用Scholar research-ideation问题卡。focused小审查选K-Dense critical-thinking，完整评审选Academic。--source可选其他匹配入口，不能凑不相关调用。--compact保留兼容，默认已经精简；原API/完整存盘guide保持。

缺缓存时在已授权网络内--allow-network逐文件核commit/blob；环境/依赖失效先修复、用已有运行时或同14库匹配替代，实际验证后继续。切换前有据cancel-step；新入口仍begin/read/apply/finish/check。新入口须同14库发现、读源/依赖、固定版本并补项目索引/真实路由，不覆写核验缓存，不host_fallback。明确限定的来源不可静默替换；普通科研软件、论文、数据和上游内原创代码不限于Skill仓库。

同阶段同版输入/输出的已完成步骤check后可复用；同一未完步骤resume，不重复begin。新问题/材料/版本或新阶段不能借旧收据过门。phase绑定自动登记开始/完成；出口拒绝遗漏；旧记录未知不追溯虚造。预算触顶保存交付预留，不启动下一步；单阶段计划不足先重排或选有效小检验。

复核围绕[实际研究单元](autonomous-work.md)，合并同一主张的转换、拟合、制图、导出和文件检查；各能力的14库调用仍分别保留。已有审查须核对材料与回执身份才复用，修改后执行受影响的审查。不能将反复导出或整包核验当新增科学证据。

## 完成范围与交付预留

completed_for_handoff只说明requested_step_only，submission_readiness=not_assessed。图稿检查、导出和文件数不表示论文可投稿；草稿/研究报告/正式稿分别标记。上游具名人工核验未做保留unverified，同时继续Agent可做的补证/复算/审查/全文写作，不能冒充人类verified或用此默认阻断研究。作者、伦理和实际投稿授权遵循真实要求。局部写作直接用上游schema字段/枚举维护有关主张，不增加全稿审批材料。
