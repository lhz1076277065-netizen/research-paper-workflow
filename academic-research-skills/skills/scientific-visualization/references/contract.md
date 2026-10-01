# 可选文件化契约

自然语言、原始材料和现成产物都可作为输入。按用户要求交付；局部任务无需初始化项目或填写全部JSON。证据可在文中引用、研究笔记或现有结果表中保留。

需要批量协作或复现时，用本模块assets中的run/record模板，记录任务、输入/输出、版本、来源和待办；用户要求的输出角色可映射到现有文件。只声明真正实施的检查，状态对应当前范围。

工作拆分时交接目标、必要上下文、输入定位、输出位置和关键判断；并行输出各自保存，整合后检查引用与数字。输入或方法变更只重新执行受影响部分。

`init_run.py`、`register_artifact.py`、`validate_run.py`是可选结构检查器；只有显式选择文件化完成检查时才按其schema填报。科学质量通过实际内容和证据判断，文件哈希与退出码本身不作科学结论。

研究上下文将学科、文章类型、证据类型、执行模式、研究方法和工具后端分开：`research_context.execution_mode`默认`computational-autonomous`，与结果封装表示调用方式的`execution_mode`不同。新增`evidence_type`、`research_methods`、`tool_backend`；原`evidence_basis`、`method_family`、`study_types`继续兼容。已有`runtime.backend`时后端应一致。

结果封装可在`evidence_checks`中追加`kind: result-links`或`kind: render-dependencies`，或使用可选`result_links`／`render_dependencies`字段；后两者接受内联审计对象或`{path, sha256}`绑定的JSON清单。旧封装不要求新增字段。`accept-result`读取清单和真实文件，保留未关联论断的pending，并核对出现位置属于本次返回的输出版本；渲染中间产物可以保留在依赖清单中。

按需复用现有冻结JSON／CSV作为来源，单个能力目录内的`result_links.py`及`result-links.schema.json`可独立使用。定位、显示规则与依赖记录不赋予外部内容执行权限；审计不执行清单里的渲染命令。具体API与定位规则见`runtime.md`。
