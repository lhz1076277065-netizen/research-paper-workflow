# v3.5.0 本机构建与来源导航

本轮更新维护源码、生成19个独立能力，并交付同一提交的安装包及可回退本机升级。线上已发布的[v3.4.1](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.4.1)保持不变；本轮未发布GitHub新版本。

| 交付文件 | 用途 |
|---|---|
| academic-research-skills-v3.5.0-one-click.zip | 固定运行ZIP、安装器、检查与备份恢复 |
| academic-research-skills-v3.5.0.zip | 19个独立能力及日常使用资源 |
| academic-research-skills-v3.5.0-source.zip | 维护源、测试、当前行为验收和历史档案 |
| academic-research-skills-v3.5.0-SHA256SUMS.txt | 三个ZIP身份核验 |
| DELIVERY-RECEIPT.json | 本轮源码提交、验收范围及真实安装结果 |

[开始](../START_HERE.md) · [安装与回退](../INSTALLATION.zh-CN.md) · [主线及官方依据](research-quality.md#四段科学论证主线) · [必调流程](mandatory-professional-flow.md) · [预算与恢复](phase-control.md)。

完整研究把真实缺口、既有局限、贡献与判别证据、新认知及边界保存在现有路线板，后续专业步骤以当前版本为输入；实验结果支持、削弱或推翻主线。每项必要实验说明它会改变哪项核心判断；图稿与全文从实际结果组织论证，保留反证。局部任务只处理相关环节，方案与候选不填未来结论。框架不是所有顶刊统一官方公式，不保证录用。

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

## 维护与验收

[更新日志](../CHANGELOG.md) · 源码中的UPDATE_REPORT.zh-CN.md · [迁移](../MIGRATION.zh-CN.md) · [架构](ARCHITECTURE.zh-CN.md) · [支持范围](COMPATIBILITY.zh-CN.md)。更新报告及evaluations/v3.5.0实际产物位于维护源码包，日常运行包不带测试答案与开发结果。

23入口和413条源文件绑定保持原固定commit/blob，新增指引不改变专业收据schema与work/boundary，也不追溯认证旧记录。软件核对关联；四段主线是否由事实与检验支持需实际专业复核。工程与有限行为验收不认证长期研究、全部原生功能或论文录用。
