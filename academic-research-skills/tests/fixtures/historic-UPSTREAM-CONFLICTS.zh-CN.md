> 历史观察（alpha.2/alpha.3）；并非alpha.4重新核验的全部上游。安装策略以本版environment-setup.md为准。

# 上游差异与本项目处理

这些是源代码/协议检查后的集成判断，不是在宣称上游已运行或整体有缺陷。

| 来源 | 已见差异/前提 | 本版行为 |
|---|---|---|
| ResearchStudio paper-search | SKILL 要求 --json；脚本 blob 1bb3d2ca452d743db2c266ba8de9fe03225e1270 的 CLI 无此参数，search_papers 函数返回 dict | 使用函数适配层保存 JSON 和日志；摘要语义筛选仍由宿主完成 |
| Nature reader/writing/figure | 读取相邻 nature-shared 和 manifest 片段 | 明确依赖，不称复制单个上游文件即完全独立；本地能力模块可回退 |
| IdeaSpark | fresh/isolated context 与指定状态接口 | 仅在宿主能满足时作为可选原生流程；不是全学科默认 |
| ARS | 固定代理配置、人工检查点、CC BY-NC 许可 | 默认不嵌套总控；引导模式才选择；未随包重新授权或分发源码 |
| K-Dense literature-review | 强制额外生成式图和其他技能 | 普通文献搜索不选；确有需求时复核适配条件 |
| K-Dense scientific-writing | 人类核验源文要求 | 未有人工证据不标该原版完成；不假造核验者 |
| anti-defensive-writing | 改变比较维度/弱化不利实验的规则可能改变报告事实 | 默认只作表达参考，禁止隐藏主要结果和实质局限 |
| ARIS / autoresearch | 专属模型/部署常量或无限循环等 | 第二批有界适配；保留原科学记录，预算/停止前提明确 |
| codex-ppt | 图像式页、确认步骤、固定子代理策略 | 第三批显式选择；不承诺可编辑图表，不成为主线依赖 |
| PaperSpine | 自有总控、Web配置、更新和运行时 | 第三批可选完整工作台，明确单一状态控制权 |
| Rougier book / OpenDesign examples | 参考书/模板，不等同研究证据或通用执行器 | 按需借鉴，真实数据另接；不分发字体/受限第三方全文 |

源标识见 providers.lock.json。只锁已读入口的 blob；引用目录和包版本并未全部锁定。将来在实际宿主执行前应记录该安装的文件版本与依赖，不能把这个观察清单当可完全重放的依赖锁。
