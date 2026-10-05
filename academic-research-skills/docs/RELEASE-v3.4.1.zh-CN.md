# v3.4.1 发行与文件导航

[正式发行页](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.4.1)提供下面的文件。首次使用选择一键安装包，维护与查证选择源码包；安装步骤与恢复命令见[教程](../INSTALLATION.zh-CN.md)。

| 文件 | 用途 |
|---|---|
| [一键安装包](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1-one-click.zip) | 安装器、日常运行ZIP、安装与回退说明 |
| [日常运行包](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1.zip) | 19个完整能力及运行资源 |
| [维护源码包](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1-source.zip) | 维护源、测试、历史和真实验收档案 |
| [程序包校验](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1-SHA256SUMS.txt) | 三个ZIP及原验收附件的SHA256 |
| [交付收据](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/DELIVERY-RECEIPT.json) | 原始源码提交、安装和验收范围 |
| [安装验收](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/INSTALLER-SELFCHECK.json) | 9项实际安装与回退检查 |
| [完整验收报告](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/VALIDATION.zh-CN.md) | 通过、初次失败和未覆盖能力 |
| [文档补充包](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1-documentation.zip) | 本次更正的说明、来源索引及参考文本；不包含执行脚本 |
| [文档校验](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1-documentation-SHA256SUMS.txt) | 文档ZIP的独立SHA256 |

程序包、源码包、一键包和原始验收附件固定到提交 `de8bf4a63bf7081ef9760bf7e3f9fffe469f587c`，与正式标签一致。后续文档补充单独记录自己的提交与逐文件摘要，不覆盖这些原包或沿用它们的校验值。GitHub `main` 展示最新说明；补充ZIP提供当前说明和19个能力的参考文本，可解压阅读，安装程序仍使用一键包。

## 开始使用

在新会话调用 `$research-paper-workflow` 处理完整研究，或直接调用 `$topic-novelty`、`$manuscript-writing` 等对应能力处理局部工作。当前安装/维护任务结束后不自动启动科研。

每个专业步骤都先执行[必调流程](mandatory-professional-flow.md)：begin调用匹配来源，读取并实施真实工作，再finish/check核对本步输入输出。开放选题默认Orchestra，固定问题使用Scholar问题卡；有限清单审查用focused入口，完整评审用Academic入口。Agent在来源流程内判断，不得先自行完成再补记调用。每一步调用适用入口，不调用与本步无关的所有仓库。

完整研究和显式预算任务登记[阶段控制](phase-control.md)。无预算先最多45分钟可行性；已有预算直接沿用。阶段出口核对实际产物及所有已开始步骤，恢复不重置预算。足够证据及时写作，无可行决定性检验交付报告；局部任务只完成本次范围。

## 14个固定来源与真实入口

下面按当前 `assets/capability-index.json` 列出14个仓库、23个入口的固定身份。链接指向已核实的上游commit；完整文件blob、依赖、输入输出、宿主适配及原生限制见[能力索引](../assets/capability-index.json)。

| 仓库 | 固定入口与实际类型 |
|---|---|
| [microsoft/ResearchStudio](https://github.com/microsoft/ResearchStudio) | [researchstudio-search](https://github.com/microsoft/ResearchStudio/blob/063f10088af49909e1a4a7ea8d29efe19633f34e/ResearchStudio-Idea/skills/paper_search/SKILL.md)（Skill协议） |
| [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | [nature-reader](https://github.com/Yuan1z0825/nature-skills/blob/84880815fb37317b3766bff2c2abba395b8993c3/skills/nature-reader/SKILL.md)（Skill协议） |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills) | [kdense-eda](https://github.com/K-Dense-AI/scientific-agent-skills/blob/154988403bb5a18e9d3c0ce4e6d5e2e4b184a298/skills/exploratory-data-analysis/SKILL.md)（Skill协议）；[kdense-writing](https://github.com/K-Dense-AI/scientific-agent-skills/blob/154988403bb5a18e9d3c0ce4e6d5e2e4b184a298/skills/scientific-writing/SKILL.md)（Skill协议）；[kdense-design](https://github.com/K-Dense-AI/scientific-agent-skills/blob/154988403bb5a18e9d3c0ce4e6d5e2e4b184a298/skills/experimental-design/SKILL.md)（Skill协议）；[kdense-critical](https://github.com/K-Dense-AI/scientific-agent-skills/blob/154988403bb5a18e9d3c0ce4e6d5e2e4b184a298/skills/scientific-critical-thinking/SKILL.md)（Skill协议）；[kdense-venue](https://github.com/K-Dense-AI/scientific-agent-skills/blob/154988403bb5a18e9d3c0ce4e6d5e2e4b184a298/skills/venue-templates/SKILL.md)（Skill协议）；[kdense-citation](https://github.com/K-Dense-AI/scientific-agent-skills/blob/154988403bb5a18e9d3c0ce4e6d5e2e4b184a298/skills/citation-management/SKILL.md)（Skill协议）；[kdense-database](https://github.com/K-Dense-AI/scientific-agent-skills/blob/154988403bb5a18e9d3c0ce4e6d5e2e4b184a298/skills/database-lookup/SKILL.md)（Skill协议）；[kdense-statistics](https://github.com/K-Dense-AI/scientific-agent-skills/blob/154988403bb5a18e9d3c0ce4e6d5e2e4b184a298/skills/statistical-analysis/SKILL.md)（Skill协议） |
| [Haojae/scipilot-figure-skill](https://github.com/Haojae/scipilot-figure-skill) | [scipilot-figure](https://github.com/Haojae/scipilot-figure-skill/blob/43098ddb9e6a6d142218540c114f9ed38922fc42/SKILL.md)（Skill协议） |
| [Galaxy-Dawn/claude-scholar](https://github.com/Galaxy-Dawn/claude-scholar) | [scholar-analysis](https://github.com/Galaxy-Dawn/claude-scholar/blob/903787345d6aec134086afa2b97715a78fbde519/skills/results-analysis/SKILL.md)（Skill协议）；[scholar-intake](https://github.com/Galaxy-Dawn/claude-scholar/blob/903787345d6aec134086afa2b97715a78fbde519/skills/research-ideation/SKILL.md)（Skill协议）；[scholar-response](https://github.com/Galaxy-Dawn/claude-scholar/blob/903787345d6aec134086afa2b97715a78fbde519/skills/review-response/SKILL.md)（Skill协议） |
| [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) | [academic-reviewer](https://github.com/Imbad0202/academic-research-skills/blob/6ab4b03bf70a118a1b3ee7f3263ed9f19031061b/academic-paper-reviewer/SKILL.md)（Skill协议） |
| [wanshuiyin/Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | [sleep-experiment-plan](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/blob/2132036060e03e8d0df69a4b21e5971819c0c2d6/skills/experiment-plan/SKILL.md)（Skill协议） |
| [karpathy/autoresearch](https://github.com/karpathy/autoresearch) | [autoresearch-protocol](https://github.com/karpathy/autoresearch/blob/228791fb499afffb54b46200aca536f79142f117/program.md)（代码工具） |
| [Adkid-Zephyr/anti-defensive-writing-Skill](https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill) | [anti-defensive](https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill/blob/102c8b21acf5eda3a0aef3d9779a65db646c8980/skills/anti-defensive-writing/SKILL.md)（Skill协议） |
| [rougier/scientific-visualization-book](https://github.com/rougier/scientific-visualization-book) | [rougier-reference](https://github.com/rougier/scientific-visualization-book/blob/62fa569f30333c817c13e4dc757877c1192fd15a/code/ornaments/legend-alternatives.py)（参考代码） |
| [nexu-io/open-design](https://github.com/nexu-io/open-design) | [open-design-deck](https://github.com/nexu-io/open-design/blob/53231d40b778d88eba23f35547bf99485d3ae9fc/design-templates/html-ppt-tech-sharing/SKILL.md)（工作台协议） |
| [ningzimu/codex-ppt-skill](https://github.com/ningzimu/codex-ppt-skill) | [codex-ppt](https://github.com/ningzimu/codex-ppt-skill/blob/6d76c0eded7f8a8b0c4e304697e6f2bda7c408b2/skills/codex-ppt/SKILL.md)（Skill协议） |
| [WUBING2023/PaperSpine](https://github.com/WUBING2023/PaperSpine) | [paperspine-workbench](https://github.com/WUBING2023/PaperSpine/blob/f7e3dabaf499b2aef1eabdd1cd5d64f173d7dcc3/dist/codex/skills/paper-spine/SKILL.md)（工作台协议） |
| [Orchestra-Research/AI-Research-SKILLs](https://github.com/Orchestra-Research/AI-Research-SKILLs) | [orchestra-ideation](https://github.com/Orchestra-Research/AI-Research-SKILLs/blob/773a52944ba4747a18bd4ae9ade53fff041adcbc/21-research-ideation/brainstorming-research-ideas/SKILL.md)（Skill协议） |

固定源码及缓存核验不等于完整原生执行；原生训练、工作台启动、完整PPT生成或独立多角色审查必须有对应实际执行证据。14库适配记录保留在候选版验收档案；本版413条源文件绑定（去重404份文件）的核验与专业行为证据分开披露。

## 维护、迁移与验收

- [正式更新日志](../CHANGELOG.md)、[本版更新报告](../UPDATE_REPORT.zh-CN.md)、[迁移说明](../MIGRATION.zh-CN.md)。
- [维护架构](ARCHITECTURE.zh-CN.md)、[兼容性与覆盖范围](COMPATIBILITY.zh-CN.md)、[专业路由](capability-routing.md)。
- [实际验收档案](https://github.com/lhz1076277065-netizen/research-paper-workflow/blob/v3.4.1/academic-research-skills/evaluations/v3.4.1/VALIDATION.zh-CN.md)、[原始双版本CI](https://github.com/lhz1076277065-netizen/research-paper-workflow/actions/runs/37281003277)。

软件和小型行为检查不能证明科研原创性、全部来源原生可用或论文录用；专业移交仅针对本次步骤，投稿就绪单独核对。
