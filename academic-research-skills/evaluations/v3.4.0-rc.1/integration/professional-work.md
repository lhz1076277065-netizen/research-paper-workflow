# 专业流程实施记录

任务范围：Skill 软件维护与集成验收。输入是真实本机软件调用记录，不是学科数据，不形成原创科研论文。

## ResearchStudio：检索与筛选

固定入口读取后调用真实 search_papers 函数：Crossref、2010–2026、最多3条、关键词 reproducible computational research。CLI 文档的 --json 不被解析器支持，第一次退出2；适配器只序列化函数返回值，未修改上游。

实际返回3条。Computational workflows for research students 是工具使用教育材料，保留为背景候选；Reproducible Science In Intelligent Transportation Research 是特定领域危机讨论，排除作为控制工具有效性证据；CDE: Automatically Package and Reproduce Computational Experiments 是复现封装相关候选，保留为概念对照。只依据返回元数据筛选，没有读全文、没有证明最近邻或创新。前两条年份和发布日期是null，保持未知，不冒称时间过滤已核实。全部3条及DOI见 search-results.json。

## Nature：源文问题与术语一致

source_format=pasted-text/Markdown。问题：autoresearch 的固定5分钟是否代表整个研究会在5分钟结束？

结论：不是。program.md 的 Experimentation 节限定每次训练5分钟，排除启动与编译；The experiment loop 节指示继续循环直至人类中断。因此它不能直接继承为总研究预算。这里将有限试验记账思想适配到软件试验，整体循环受阶段预算约束。原文没有说明如何保障 Codex 宿主预算，不能据此推断保障。

原文依据：已校验的 autoresearch program.md 的 Experimentation、Logging results、The experiment loop 三节。没有纸本文本或页码，不造 page/block IDs。

术语：fixed time budget=固定时长预算；wall clock training time=训练墙钟时间；baseline=基线；val_bpb=上游训练验证指标，本测试不测；keep/discard=保留/弃用方案，不是科学接受/拒稿。

## KDense：数据剖析与决策

运行 tabular_profile.py 处理 launch-results.csv 的24条真实记录，产生 kdense-profile.json。trial 是配对调用标识，不是连续生物学变量；started 是二元软件事件；wall_seconds 是启动开销，受机器/启动顺序影响，不作性能优越性推断。CSV没有缺失值；6个过期状态与6个活动状态各有direct/control两行。该入口只完成CSV核心剖析，不宣称所有科学格式兼容。

## Scholar：只读统计审计

逐行检查24条记录，以trial和state+method定位观测单位。核心对比：过期状态direct启动6/6、control启动0/6；活动状态两者均启动6/6。标记文件和受控拒绝记录吻合。

有效：描述事件计数与对照；同一台Mac的确定性软件回归测试。无效：将24行当作独立样本计算科研p值/置信区间；用启动时长推断研究提速；推断任意宿主API可被拦截。缺证：长期自主行为、多个宿主、多领域科研质量。选择 results-analysis 的 read-only audit 分支，由命令层保存本审计摘要，未生成伪统计分析包。

## SciPilot：选图、核验与导出

论证目标是过期拒绝与活动接受。先运行 profile_data.py，再选择两个横条计数面板，零基线、direct labels；不画均值误差棒或显著性。备选为2×2数值表或12试验标记矩阵；计数条图用于快速对照且配表保留每次真实事件。

按 general 规范调用 setup_style、audit_layout、render_preview，目视检查实际PNG后调用 export_figure 得到PDF/SVG/300DPI PNG与灰度图。程序报告x轴标签可能裁切；短化标签后警告仍存在。实际导出使用tight边界，目视检查两张预览与最终PNG：标题、数值、零刻度与轴标签完整，未遮数据；警告保留，不伪称机器无警告。灰度依靠分组标签/数值而非只靠颜色。figure-values.json与原CSV一致。

图注：同一台Mac的12个配对软件场景，每格6次。横轴为实际启动数；没有推断统计误差棒。过期control为0/6，活动control为6/6。输出只支持此测试范围。

## Sleep：主张驱动实验计划

experiment-plan.md在执行前写出2条主张、反主张、最小证据、观测单位、必做块、排除块、顺序和5分钟测试预算。执行记录见launch-results.csv、command-receipts.json与tracker.md。软件适配，不生成论文实验路线；不调用另一个独立实验审计模型。

## Autoresearch：有限试验记账适配

固定测试命令和评价函数，先direct基线，再control变体；不改评价标准，不挑选有利场景。results.tsv逐项保留24次结果，并用明确软件列名替代val_bpb/memory_gb。保留控制变体的判断来自过期拒绝且活动接受，不来自模型训练。上游H100/CUDA专用训练未执行；无限循环被阶段预算替换，非原生训练通过。

## Rougier：参考代码与图设计

原样运行 legend-alternatives.py，保持相对输出目录，得到原示例PDF与预览。它是代码/书籍参考，不是Agent skill。采用其直接标签方式减少主图图例与数据对应负担；没有将原正弦曲线当成本测试结果。缺Roboto字体使用Matplotlib回退，保留stderr。原BSD声明保留在源码中。

## Orchestra：问题优先与简化选择

应用Problem-First、Simplicity与Explain-It三项框架：候选A继续扩大专业仓库/写提示词，候选B阶段出口+真实能力适配，候选C先开发新独立研究应用。受影响者是运行长研究的用户；A不能证明阻止重复启动，C成本高且偏离维护范围，选择B。两句话：当前研究会在预算/恢复边界上重复工作；将可执行阶段出口与真实输入输出连接，使范围及剩余工作可检查。受限验证是有限软件场景，不宣称学术方法创新；停止扩展选题。

## Imbad：quick review本机适配

输入final-report.md、原CSV和图。按field analyst→Journal-Fit quick assessment顺序，在同一当前Agent中进行两项判断，不冒充独立审查面板。类型为软件验证报告；没有目标学术期刊，journal fit为不适用，审查关键是内部有效性、外推范围与主张一致。

证据锚：final-report.md §结果与范围。优点：真实标记对照避免只验状态字段。关键修订：明确control只能约束经guard/run的动作；保留6/6活动接受，防止“全部禁用”也被视为成功；将全14来源声称收窄为逐源指定能力验收。最强反方：同一维护Agent与短fixture不能证明长期研究不再失控，必须保留此限制。建议接受为本机软件交付报告，不能标论文完成。已把这些限制落实到final-report.md，未编辑原科研稿件。

## Anti-defensive：证据保持表达

采用真实优势先行、删除执行流水账、主张不超过证据。保留全部关键数字和限制；不按上游措辞规则删除不利结果或扩大主张。before-after.md记录原稿与成稿；final-report.md从功能与支持证据展开，未声称显著提速、原创科研贡献或消除平台故障。

## OpenDesign：HTML技术分享适配

按tech-sharing入口复制实际模板样式及共享runtime，重写../../../assets为本地assets。保留tpl-tech-sharing与结构类，把演示Rust内容替换成真实软件结果与边界；notes放aside而非可见正文。输出deck/index.html、style.css、assets和LICENSE。没有启动OpenDesign服务/模型，也不冒充完整应用已部署。输出进入交付摘要展示。

## Codex PPT：已有图像组装函数

使用真实launch-figure.png，运行assemble_ppt.py，生成1页16:9 PPTX并核实1个图片shape及speaker notes。没有付费/外部图像生成流程，也没有可编辑图文布局，图像填充可能改变画面比例。验收只覆盖已有图像组装与备注，function_only；正常完整PPT生成采用OpenDesign HTML替代，不伪称原生全图工作流接通。

## PaperSpine：结果绑定子流程

本地results_validation.md把C1/C2连到CSV、profile与图，并明确允许/禁止推断。运行原checker：有效表通过；空claim的metric-only负对照失败。只有这项本地专业子流程完成，完整PaperSpine工作台、自动更新、远端任务或完整paper rewriting未启动。
