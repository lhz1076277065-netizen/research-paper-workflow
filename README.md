# Academic Research Skills v3.4.1

通用学术Skill正式版：1个总控与18个独立专业能力。每个专业步骤必须调用指定14个GitHub仓库中匹配的真实入口，实施工作后绑定当前任务和产物；禁止跳过来源用通用推理替代。开放选题默认调用Orchestra，固定问题使用Scholar问题卡。能力索引包含23个固定版本入口。

[中文使用说明](academic-research-skills/README.zh-CN.md) · [English guide](academic-research-skills/README.md) · [开始使用](academic-research-skills/START_HERE.md) · [正式发行](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.4.1)

## 下载与安装

| 文件 | 使用场景 |
|---|---|
| [一键安装包](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1-one-click.zip) | 安装、检查、备份与回退全部19项 |
| [日常运行包](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1.zip) | 手动部署完整能力目录 |
| [维护源码包](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1-source.zip) | 修改维护源、查看测试与真实验收档案 |
| [SHA256校验](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1-SHA256SUMS.txt) | 核对原始程序与验收附件 |
| [文档补充包](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1-documentation.zip) | 阅读本次更新的说明与专业参考文本 |
| [文档补充校验](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.4.1/academic-research-skills-v3.4.1-documentation-SHA256SUMS.txt) | 核对独立文档包 |

按[安装与回退教程](academic-research-skills/INSTALLATION.zh-CN.md)核对SHA256后解压一键包，在目录中运行：

```bash
python3 install.py
python3 install.py --check
```

默认安装到 `~/.agents/skills`，旧版自动备份。安装器Python3.9+、工程CLI Python3.10+；macOS ARM64安装已验收，Linux工程CLI有CI，其他安装环境见[兼容性](academic-research-skills/docs/COMPATIBILITY.zh-CN.md)。在新会话读取实际 `SKILL.md` 确认3.4.1；同名能力不要重复安装。

## 流程与文件说明

完整研究先做有界可行性判断；无预算最多45分钟，已有总预算直接沿用。阶段记录真实专业步骤、证据、截止和下一动作，恢复不重置预算；有足够证据进入成稿，无可行决定性检验交付报告。局部任务直达对应能力，维护完成后结束。

[必调专业流程](academic-research-skills/docs/mandatory-professional-flow.md) · [阶段与预算](academic-research-skills/docs/phase-control.md) · [14来源与文件导航](academic-research-skills/docs/RELEASE-v3.4.1.zh-CN.md) · [更新日志](academic-research-skills/CHANGELOG.md) · [迁移](academic-research-skills/MIGRATION.zh-CN.md) · [架构](academic-research-skills/docs/ARCHITECTURE.zh-CN.md)

v3.4.1程序包固定到 `de8bf4a63bf7081ef9760bf7e3f9fffe469f587c`。后续文档补充使用独立提交、ZIP和校验，不替换原程序包或标签；GitHub main展示最新说明。

[正式版验收](academic-research-skills/evaluations/v3.4.1/VALIDATION.zh-CN.md)记录686项主回归、30项兼容、双版本Linux CI、9项安装回退及小型实际流程。来源准备、专业工作、原生函数运行分别记录；这些检查不认证科学质量或全部仓库原生可用，首次失败与限制如实保存。

维护对象在 `academic-research-skills`；根目录 `research-paper-workflow` 是保留旧工具的同步兼容副本。遵守 [LICENSE](LICENSE) 和各上游许可声明。历史科研测试不会因安装或文档维护而启动。
