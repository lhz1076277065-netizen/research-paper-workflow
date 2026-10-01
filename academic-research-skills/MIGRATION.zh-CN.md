# v3.2.0-rc.4 迁移

用本版完整能力目录替换选定的rc.3目录；1个可选总控与18个独立能力不变，任一能力无需src或邻居目录。保留项目数据、原始结果和已有专业适配。维护源仍为src/common、src/quality31/payload和各能力protocol.md；维护后运行build_release.py --write，再用--check核对。

默认执行模式是computational-autonomous，独立于学科、文章类型、证据类型、研究方法和工具后端。原study_types、method_family、evidence_basis与runtime.backend继续接受；新字段为research_context.execution_mode、evidence_type、research_methods、tool_backend、computational_routes。未提供数据先发现和实际取得适配材料；原人工采集路线转到公开数字资源、模型或理论，并明确改变的问题及证据范围。

executor保留当前宿主；research_model是本地研究对象或算法，可训练、加载和评价。按实际任务复用免费工具、项目环境和已有授权软件。environment.py的doctor/plan不安装；ensure按项目选定依赖准备；exec以argv、项目cwd、日志和文件回执运行任意已准备的专业工具；calibrate实际检查候选后端的小任务。

现有result envelope与figure-values检查兼容。需要跨稿件关联时追加result-links检查，绑定实际冻结结果、版本和具体出现位置；明确舍入和复算容差。render-dependencies独立记录源、图表、引用与输出依赖，源改动后按rebuild_order重建。旧记录缺少关联时显示待关联范围，不冒充全面语义核查。

科研、成果与external_items分别推进。provider_uses可追加guidance_read、research_work_done、functions_run三种进度；实际版本与所用入口继续记录。外部作者确认待办不阻止独立研究与成果工作，但仍不能宣称已正式提交。

rc.3迁移、更新和目录清单存入history/rc3-reports。本轮软件、真实数字执行、原生行为和视觉检查分列报告；接口通过不代表原创性、科学正确性或期刊录用。
