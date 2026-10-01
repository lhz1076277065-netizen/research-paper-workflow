# v3.2.0-rc.4 逐文件变更与实际效果

基线为 `v3.2.0-rc.3`，commit `8985d90d7e3a599a8c06556b8d1c2cec6ccb8e21`；实施从现有 `c47c98a094fafac65b3beb283d35cf478ae6e2af` 开始，保留其后增加的安装说明。目标是升级通用 Skill，开发验收样例不作为原创论文交付。

## 入口、路由与研究协议

19 个短入口及交接规则维护于 `src/quality31/payload/skills/`，公共参考维护于 `src/common/references/`。下表的专业协议直接维护于各 `skills/<名称>/references/protocol.md`。共用表述统一替换为计算机闭环、当前 executor、本地 research_model、原创方法与代码、实际成果和按需读取。1 个可选总控与 18 个独立能力继续保留。

| 文件或能力 | 解决的问题与改变 | 预期效果及已验证范围 |
|---|---|---|
| research-paper-workflow/SKILL.md、START_HERE | 总控明确 computational-autonomous 数字完成路径；短入口分派必要能力 | 不预设新人工采集；入口长度、独立复制和原生任务记录可检查 |
| research-intake 协议/入口 | 分开学科、文章、证据、执行模式、方法、工具；未提供数据就实际发现材料 | 研究方向进入具体问题、证据与下一动作；路由与缺数据任务验收 |
| topic-novelty 协议/入口 | 最近邻能力→缺口→改变→新增知识→证据；已知原理作基线 | 建设性贡献选择；理论及初始失败原生输出审查，不自动给原创性分数 |
| research-design 协议/入口 | 竞争解释须给不同预测；同信息、分区、调参与计算预算比较 | 重合预测进入可区分数字操作；真实小模型与回归覆盖 |
| data-discovery 协议/入口 | 从论文数据声明到作者仓储、权威源、实际字典/样例/许可 | 材料取得改变研究选择；UCI 实际档案与样例检查 |
| literature-discovery 协议/入口 | 最近邻检索连接真实数据、代码和附件；访问事项单列 | 指向可取得材料；来源冻结和原生材料记录覆盖 |
| data-preparation 协议/入口 | 核定义、单位、连接键、时间、重复与独立单位；分区内预处理 | 防同来源泄漏；实际 4,898 条数据分组与训练内标准化 |
| ethics-protocol 协议/入口 | 分开公开元数据、免费访问、再使用许可；隐私归因与外部确认分流 | 免费合法资源选择；实际许可页面保留，未冒认所有公开资源许可 |
| analysis-execution 协议/入口 | 原创代码和多工具实施；先校准再正式规模；意外结果定位 | C 求解、NumPy、SymPy、RDKit、本地模型实际产物 |
| robustness-reproducibility 协议/入口 | 强基线、消融、替代、留出及适用边界；仿真正确性/收敛/适用性分开 | 开发集迭代与正式评价分离；真实留出、模型重载和独立 DP 检验 |
| paper-deep-reading 协议/入口 | 页段公式、假设、划分、关键图和失败进入设计选择 | 可定位的深读；协议保留原有专业知识；未将下载全文称完成精读 |
| citation-audit 协议/入口 | 对象、结局、比较、时间、样本、方向及支持范围 | 单随访点不称持续；新合成引用请求实际修订审查 |
| scientific-visualization 协议/入口 | 主图优先原创结论、最近邻、成本、消融和边界 | 主图选择服务贡献；旧科学制图 smoke、现有图值审计保持 |
| manuscript-writing 协议/入口 | 真实结果绑定关键文本与导出；指定表达 Skill 改善已成立贡献 | 四格式真实文本核验、局部段落请求；不扩大局部范围 |
| manuscript-review 协议/入口 | 具体科学缺口→最有信息价值的动作；三队列推进 | 外部等待继续稿件检查；审查结果与记录通过分开 |
| journal-intelligence 协议/入口 | 早期核计算/理论发表类型；最终按真实贡献选刊 | 保留聚焦选刊功能，软件回归覆盖；本轮未声称实际期刊录用评估 |
| submission-packaging 协议/入口 | 源版本、依赖、可编辑文件、声明与外部提交分开 | 字节/数值/声明语义/过期导出分别检查；不替用户正式提交 |
| peer-review-response 协议/入口 | 实际审稿输入进入回应、实做修改和版本定位 | 不凭空启动审稿；旧兼容回归保留 |
| publication-stewardship 协议/入口 | 实际校样/出版输入、来源与变更对应 | 不凭空启动出版；旧兼容回归保留 |
| research-lifecycle.md | 六环完成路径；科研、成果、外部三个轻量队列 | 外部确认不冻结独立工作；默认量级保持 |
| research-quality.md | 科学价值、最近邻增量、不同预测、公平比较与建设性迭代 | 原有三个深反例保留；新建设性推演按需，不给工程通过赋科学质量 |
| computational-routes.md（新增按需） | 14 条数字研究路线、具体证据与工具选择；两个深建设性推演 | 新知识/方法/设计/边界为目标，非固定软件清单；路由 10 项新回归 |
| research-types.md、figure-production.md、final-expression.md | 六维解释、贡献主图、结局与时间、实际数字复核 | 延续原有专业说明并连接新模式 |
| research-profiles.json、research_router.py | 原 16 画像逐字段保留；新执行模式与 14 路线独立匹配 | 未知扩展可保留；布尔事实标记不被认证为完成 |

## 执行、来源与结果检查

以下文件均在 `src/common/` 唯一维护，构建后进入根 `scripts/assets/docs` 及 19 个能力的同名独立资源。

| 公共文件 | 改变与原因 | 证据与边界 |
|---|---|---|
| scripts/environment.py | 探测系统/架构/内存/磁盘/运行时/编译器/线程/后端；argv 在项目 cwd 与同一环境运行；真实校准；输出哈希、日志和采样 RSS | 实际安装及复用、编译执行、CPU/NumPy/MLX CPU/GPU；RSS 是采样下界，不称精确峰值 |
| scripts/provider_worker.py | 先验证任务与输出位置，保留现有适配器；科研模型区别于 executor | 边界与兼容回归；本地训练对象不是替换宿主 |
| scripts/provider_runtime.py | 接入结果链接/渲染依赖审计；输出版本绑定；可选择已准备解释器 | 旧封装兼容，新实际格式及故意损坏检查 |
| scripts/result_links.py（新增） | 从冻结 JSON/CSV 结果表绑定 result_id、源版本和实际定位；核主值/上下界、舍入、复算容差、单位、方向、分母、时间等；理论/解释证据定位；递归渲染失效 | 40 项针对性测试、8 个实际出现位置、5 类故意错配、过期检测与重建；只检查声明的位置与来源语义，未自动发现全文全部论断 |
| scripts/research31.py | 按科研角色选主实现/互补实现；区分指导读取、研究实做、函数执行；三队列与 audit CLI | 18 项工具/角色回归与实际 CLI，读取指导不冒称研究完成 |
| scripts/upstream.py | 当前发现后冻结实际 commit/tree/blob，并核对应与本地适配 | 实际 SciPilot 版本和 blob 记录；来源可用性不冒称图表工作完成 |
| assets/environment-profiles.json | 当前 executor 与本地免费 research_model；实际资源与依赖准备 | 实际 Ridge 训练/40 点留出/可编辑参数与重载 |
| assets/research31-policy.json | 九类科研角色、选择理由和完成状态 | 一个主实现，互补者目的明确；不强制凑调用数 |
| assets/result-links.schema.json（新增）、task.schema.json、result.schema.json | 新关联与维度字段，旧任务/封装保持兼容 | 正反输入回归与独立目录执行 |
| references/environment-setup.md、provider-policy.md、upstream.md、research31-usage.md、tooling.md、research-tools.md（新增按需） | 免费按需安装、软件 API/CLI/必要 GUI 的输入项目/参数/运行/提取/专业核验；准确的来源角色与版本 | 本轮实际 API 与 CLI；桌面 GUI 通路有操作说明，未称通用 CAD/GIS GUI 验收完成 |
| references/runtime.md、contract.md、integrity.md | 字节/数值/声明语义覆盖分报；主值不能被端点替代；实际导出依赖 | 审查发现的两处问题有真实复现与根因修复 |

## 回归、验收与发行文件

| 文件 | 改变和实际范围 |
|---|---|
| tests/test_computational_routes.py | 10 项新路由/证据模式回归；新材料与可执行转化 |
| tests/test_research_tools.py | 18 项安装、环境、argv、模型角色、来源、三队列与 audit 路径检查 |
| tests/test_result_links.py | 40 项实际 Markdown/DOCX/PDF、来源、舍入/容差/语义、理论/解释定位与导出 DAG 检查 |
| tests/test_package_identity.py | 真 Git 提交/ZIP 回归：忽略文件不入包，未提交修改拒打包，manifest 绑定真实 commit |
| tests/test_quality31.py | 原有文本断言迁移至 current executor/research_model 与自主改写代码；不保留禁止本地研究模型的旧断言 |
| tests/test_release.py | 来源 checkout 夹具改为真实 Git tree，避免伪 SHA 掩盖错误 |
| evaluations/rc4/run_digital_acceptance.py | 实际合法公开数据、训练与重载、条件证明/边界、编译 C 优化和独立 DP 验证；不是原创新算法 |
| evaluations/rc4/run_export_acceptance.py | 冻结实算值→Markdown/TeX/DOCX/PDF、错配与过期、重建；ReportLab 使用 DOCX 段落，不宣称任意 Word 排版保真 |
| evaluations/rc4/native-cases.json、native/ | 八个新通用请求，各版本一个独立原生上下文；真实产物与独立输出审查；不把八子例称八重复 |
| evaluations/rc4/tool-execution/、engineering/、VALIDATION.zh-CN.md | 实做依赖/工具/来源、回归与失败历史、验证分类及限制 |
| release/make_package.py | 发行前要求干净提交，仅取已跟踪文件；两个 ZIP 的 manifest 记录 tag/commit/文件摘要；复用固定版本/SHA 一键安装器 |
| release/installer/ | 复用 rc.3 安装/备份/恢复/异常回滚，发行时将版本和实际 ZIP SHA 写入模板；不运行本机全局安装 |
| VERSION、README、START_HERE、CHANGELOG、docs/ARCHITECTURE.zh-CN.md、COMPATIBILITY.zh-CN.md | 当前 rc.4 导航，保持历史兼容路径；科学研究目标与开发验证范围分开 |
| MIGRATION.zh-CN.md、INSTALLATION.zh-CN.md、本文件 | 兼容字段、使用与安装、逐文件原因和证据；无需日常默认读取 |
| test-results/SUMMARY*、context-metrics.json、distribution-checks.json | 当前检查数字与范围；旧文件移至 history/rc3-reports 保存 |
| source-diffs/v3.2.0-rc.3-to-v3.2.0-rc.4.* | 权威源码差异与前后摘要；生成重复副本不在补丁中重列 |
| .gitattributes | 原始CRLF表、PDF、历史证据与补丁保留字节，不按维护源码空格规范重写 |
| GENERATED-FILES.json | 每个构建副本的摘要；来源变化通过现有构建器统一同步 |

默认示例的总控+生命周期+质量参考由 4,760 字变为 5,493 字（约 +15.4%）；19 个入口 639–798 字。14 路线及工具详情按需读取。字符数不是 token、缓存、实际账单或整个上下文的测量。实际原生读量、完成范围、完整回归与发行检查见 [验证报告](evaluations/rc4/VALIDATION.zh-CN.md) 和 [汇总](test-results/SUMMARY.json)。

发行 ZIP、实际 tag/commit、远程 CI 和安装隔离测试的最终摘要在同次发行的外部 receipt 与 SHA256SUMS 中记录，避免把 ZIP 自身摘要写回 ZIP 形成自引用。
