# 可选研究记录检查器

`research31.py`是标准库工具，不运行模型、不判断论文是否达到顶刊，也不是操作系统沙箱。日常用一份Markdown路线板即可；准备最终交接、需要发现遗漏时可把现有记录映射到示例JSON，再检查实际文件与专业步骤覆盖。

```bash
python3 scripts/research31.py sources --role figure
python3 scripts/research31.py upstream discover --repo OWNER/REPO --out run/source.json --allow-network
python3 scripts/research31.py assess --state research-route.json --root /path/to/research --out readiness.json
```

第2条检查来源属于用户库，再调用同目录原有upstream.py；不会安装或启动其他Agent。原有宿主GitHub工具也可按相同来源范围直接使用。source清单约束的是外部Skill，不约束文献、数据、普通库或原创代码。

结果`ready_for_content_review`只说明当前文件及声明记录齐全，仍需当前Agent进行科学内容判断；`research_in_progress`给出具体下一步，不妨碍探索或起草；已解析记录的结构/文件问题报告`record_error`；无法解析的字段类型或CLI输入返回`needs_attention`和具体原因。不能由填写“通过”制造语义验证。

每个正式图关联其真实provider_use记录：同一图的输入/输出、已执行的设计/绘制/数值与视觉步骤。函数导出不足以满足完整figure角色。写作末次反防御性改稿关联原稿与最终稿，实质改动之后要复核事实。示例只是结构，不是可直接当作研究已完成的证据。

完整稿件写作的provider_use标scope=full_manuscript；摘要适配只能记录abstract，不满足整稿角色。所有字段描述实际已做的工作，不通过编造字段使记录“完整”。

完整全文角色还关联本稿文件：专业writing输出须是最终稿或反防御性修订的输入；末次final_expression标scope=full_manuscript。focused单图/图注任务核对其文件版本，不追加整份论文的主图设计前置。

最终表达必须完成实际论证整理、证据保持与事实复核；`assets/research31-policy.json`中的`final_expression_repository`是优先来源，不是默认必需来源。使用其他库内匹配实现时沿用`provider_use`；当前Agent直接按本库协议完成时，可在`final_expression.operation`中记录`actor_scope: current_host`、`scope: full_manuscript`、含`argument_review`与`evidence_preservation`的`steps`，以及实际`inputs`、`outputs`、`evidence`文件的path/SHA-256，无需伪造外部仓库或commit。两种方式均须保留原稿，关联真正最终稿，并按上述`facts_rechecked`和`review.subjects`规则复核。

仅用户明确要求某来源时，在`final_expression.required_repository`记录其库内仓库；未完成该来源的实际步骤列为外部必需事项，同时继续其他工作。检查器不验证这项用户要求的真实性，不得根据优先来源自行填写；记录与文件齐全仍不等于语义或科学质量已获认证。


## 从3.1.0迁移记录

只有需要机器核对交接时才补这些关联；单段修改、读单篇、找期刊不需要完整研究记录。

- `facts_rechecked`使用JSON布尔值`true`或`false`；字符串不是已完成复核。
- `final_expression.review`继续使用原报告的`path`与`sha256`，另加`subjects`数组，定位它真正审查的稿件版本（也可列必要的表格/证据版本）。最终稿改变后，复核受影响内容再更新审查对象；只更新稿件输出哈希不能使旧审查自动有效。
- literature、reading、novelty操作的`document_bindings`关联当前`research_brief`与`prior_art`的path/SHA-256。它说明操作服务哪个任务与知识背景，不声称语义审查已通过。相关旧产物可以复用；换了研究问题或关键背景后核对关联和必要重新检索，不拿另一个测试的角色标签补齐。原inputs、outputs、evidence字段继续保留。
- 普通`host_actions`字符串仍可用，新的研究动词不因没列入词表就被禁止。需要描述执行者范围时用对象，例如`{"action":"verify_citations","actor_scope":"current_host"}`；`assistant_target`只描述拟切换的执行助手，不是研究中训练的模型。检查器不决定动作的所有语义，也不授予其他权限。
- 方案稿可声明`research_context.article_type`为`study-protocol`、`protocol-design`或`registered-report-stage1`；可明确`requested_deliverable: protocol`，已有study_types继续用于方法选择。交付仍须有问题、背景、设计、完整稿件与适用审查，但不编造未来results/validation。结果标明delivery_scope=protocol，不能据此声称整个实证项目完成。明确的empirical_paper请求不能靠修改文章标签跳过研究；applicability理由本身不豁免普通实证证据。

3.1.0记录缺少新关联时返回具体下一步，保留原文件；不假造subjects、bindings或已复核标记以凑齐记录。

## 可选字段与检查

`select --role ROLE --input candidates.json --out selection.json`接收`candidates`数组及可选`requirements`。候选包含唯一id、repository、实际entry/commit、roles、available布尔值、installed布尔值、missing_dependencies，以及已检查的domains/tasks/materials/outputs字符串数组。requirements使用后四个数组要求完全覆盖；这些是实际检查记录，不是工具自动认定。主实现优先匹配的已安装者；互补者注明`complement_role: complementary_coverage | independent_evaluation | fallback`与具体`selection_reason`。

provider_use可加`progress: {guidance_read: true, research_work_done: true, functions_run: false}`，三个布尔值各描述真实工作，互不推导；旧记录兼容，未知状态仍未知。附带函数单独运行不覆盖完整专业角色。`host_actions`对象可明确`role: research_model`、purpose与local/free_to_use/license_allows_research=true；模型用于科研，assistant_target仍只可为current_host。

`audit --input evidence.json --root /path/to/project --out audit.json`调用同目录结果/渲染检查；`assess`可按需接收同格式`evidence_checks`，错配进入record_errors，未关联出现位置进入next_actions。分别报告字节、数值与语义覆盖，记录齐全不认证原创性或视觉正确性。

三个可选字符串队列为`research_work`、`artifact_work`、`external_items`。前两队列未完成项进入next_actions，外部作者确认/访问/正式提交单独返回，不把外部等待当内部研究停工条件。
