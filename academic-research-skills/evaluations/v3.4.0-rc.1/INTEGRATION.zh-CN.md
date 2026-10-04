# 14个来源的真实集成验收

固定14个来源的commit/tree，192个入口/支持文件逐一核对Git blob。能力索引保存类型、依赖、输入输出与宿主适配；旧sources/select/upstream/assess接口保留，增加capabilities与phase。19个独立skills拥有统一索引与阶段工具；provider种子按相关能力分配，默认不自动执行。旧记录缺字段保持未知。

每源实际输入、工作说明、输出哈希见integration/receipts；语义是否实施仍由工作证据核查，收据脚本只验证来源与文件身份。以下是指定能力的验收，不是仓库全能力认证，也不要求每篇研究调用14库。

| 来源 / 真入口 | 实际输入→工作→输出 | 模式与限制 |
|---|---|---|
| Microsoft ResearchStudio / paper_search | 有限查询→真实Crossref函数检索3条、筛选→search-results.json与筛选说明 | 当前宿主适配；CLI --json不存在，保留失败并按真签名调用；2条年份未知 |
| Yuan1z0825/nature-skills / nature-reader | 原program.md问题→准确节定位与术语→源文回答 | 适配源文问答，无全文论文reader/虚构页码 |
| K-Dense scientific-agent-skills / exploratory-data-analysis | 24行真实CSV→tabular_profile→JSON剖析与字段解读 | 原生CSV子流程；其他科学格式未认证 |
| SciPilot figure skill | CSV→剖析/选图/样式/程序与目视检查→PDF/SVG/PNG/灰度 | 原生数据图流程；保留裁切警告，最终tight图目视完整 |
| Galaxy-Dawn/claude-scholar results-analysis | 原CSV/观测单位→只读统计有效性审计→计数/限制 | read-only audit适配；不算p值或独立样本，不冒称完整统计包 |
| Imbad academic-paper-reviewer | 软件报告/CSV→quick两视角核查→具体证据锚与修订 | 当前Agent适配；没有独立面板/跨模型或期刊推荐 |
| wanshuiyin/Auto-claude-code-research-in-sleep experiment-plan | 软件问题→预先2主张/反主张/实验顺序→plan与tracker | 计划协议适配；不用原生独立审计模型 |
| karpathy autoresearch / program.md | 固定baseline/control记录→有限试验记账→真实24行TSV | 协议适配；H100/CUDA训练阻碍，未测val_bpb；拒绝无限循环 |
| anti-defensive-writing | 原稿/实际计数→突出有证据优势、保留限制→before-after与final-report | 证据保持适配；不删重要不利结果，不事后换指标 |
| Rougier scientific-visualization / legend-alternatives.py | 真参考代码→原样运行→示例PDF，并实际采用直接标签 | 参考代码执行，不是Agent skill；缺字体回退保留日志 |
| OpenDesign / html-ppt-tech-sharing | 最终软件报告→真实模板/本地assets/runtime/notes→4页HTML | 模板/协议适配；页面渲染和Right翻页核验，无完整应用部署 |
| codex-ppt / assemble_ppt.py | 已有真实图像/备注→组装→1页PPTX并检验图片/notes | 仅function_only；第一次单#备注不被识别，改成真实##格式；未跑原生图像生成或可编辑文字流程 |
| PaperSpine / results_validation_check.py | C1/C2证据表→原检查器与空claim负对照→PASS/FAIL实录 | 本地结果绑定子流程；完整工作台/重写管线未启动 |
| Orchestra / brainstorming-research-ideas | 软件失败→problem-first/simplicity筛选→选择有限阶段方案 | 当前宿主适配；未增加科研课题或追求学术创新 |

实际检索、剖析、图、审计、表达、展示和检查输出进入同一software final-report；规划说明或单次函数不会冒充完整专业角色完成。平台/硬件不足的原生工作保持受限，替代路径分别为有限软件协议、当前宿主审查和OpenDesign静态HTML。当前本机依赖锁在requirements-verified.txt，源码没有携带虚拟环境或全局改动。

本地缓存与独立安装目录分开，缓存2.2MB，准备不启动代码。源码包保留集成产物，额外交付固定来源缓存ZIP可离线复用。哈希是身份记录，不是许可/安全/科学质量认证。
