# Academic Research Skills v3.3.0-rc.1 一键安装与部署教程

适用：macOS 上已经可以使用的 Codex。固定安装通用学术 Skill v3.3.0-rc.1，共 19 项独立能力。核对日期：2026-10-01，Asia/Shanghai。

## 最快安装：解压后双击

1. 解压 `academic-research-skills-v3.3.0-rc.1-one-click.zip`，把整个文件夹放在电脑任意位置。保留文件夹内的脚本和日常版 ZIP。
2. 双击 **一键安装.command**。终端窗口会显示校验、安装结果、安装位置和旧版本备份位置。
3. 看到 **“安装完成：19 个 Skill，版本 3.3.0-rc.1”** 即表示本机文件安装完成。如果已是该完整版本，会显示无需重复安装。
4. 回到 Codex，在下一轮消息中按名字使用 Skill。如果没有出现，重启 Codex 后再试。

安装到当前用户的 `~/.agents/skills/`。该目录是官方当前文档列出的用户级 Skill 位置；Codex 会检测新文件。如果同名 Skill 有两份，选择器可能同时显示，因此本脚本会把所选能力在用户 `.agents/skills`、`.codex/skills` 及自定义 CODEX_HOME 中的旧副本移到备份位置，然后保留一份新目录。[官方本地 Skill 说明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

安装器要求Python 3.9+，复用已有Codex系统skill-installer；研究工程脚本要求Python 3.10+。本机macOS ARM64安装验收使用Python 3.9.6，工程回归使用3.12.14。其他系统/宿主范围见[支持说明](https://github.com/lhz1076277065-netizen/research-paper-workflow/blob/v3.3.0-rc.1/academic-research-skills/docs/COMPATIBILITY.zh-CN.md)。

这里的“部署”是把专业工作流放入本机 Codex 能读取的位置，之后由当前 Agent 和现有模型执行。日常安装包已经内置，安装阶段无需联网；首次任务需要在线文献或专业来源时再使用网络。

## 安装包内有什么

| 文件 | 用途 |
|---|---|
| 一键安装.command | 双击安装全部 19 项能力 |
| 检查安装.command | 双击检查已安装文件与原版的身份 |
| install.py | 实际安装、备份、检查及恢复脚本 |
| academic-research-skills-v3.3.0-rc.1.zip | 已核验的完整日常版，全部必要 Skill 文件在其中 |
| README.zh-CN.md | 本教程 |
| selfcheck.py | 运行隔离安装、备份恢复与异常回退检查；实际结果另附在发行页 |

| SHA256SUMS.txt | 安装器、教程与内置日常包的文件摘要 |

本安装包是日常使用安装包；完整维护源码和开发证据另见 [v3.3.0-rc.1 GitHub 发行页](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.3.0-rc.1)。

## 怎么确认真的装好了

先双击 **检查安装.command**。完整安装应显示：

```json
{
  "version": "3.3.0-rc.1",
  "selected": 19,
  "matching": 19,
  "missing_or_changed": [],
  "other_user_copies": []
}
```

这一步核对全部所选目录的必需文件集合及 SHA-256，忽略 Python 的 __pycache__/pyc 和 Finder 的 .DS_Store 缓存。其他新增文件或原文件修改会列为变化。然后在 Codex 下一轮发送下面这段，用实际入口确认本机加载：

```text
请检查通用学术 Skill v3.3.0-rc.1 的本机安装。
先确认 research-paper-workflow 和 journal-intelligence 是否出现在当前可用 Skill 中；
读取它们的真实 SKILL.md，报告路径、名称和版本。
这里只做安装自查，不开展论文研究。
```

应取得两个真实入口路径及 `metadata.version: 3.3.0-rc.1`。在默认安装中路径为：

```text
~/.agents/skills/research-paper-workflow/SKILL.md
~/.agents/skills/journal-intelligence/SKILL.md
```

文件检查与 Agent 实际读取是两项不同验证。如果文件检查通过但当前聊天未出现新 Skill，先换下一轮，再重启 Codex。不要以旧聊天的入口或旧版本缓存证明新版本已启用。[官方检测与启用说明](https://learn.chatgpt.com/docs/build-skills#create-a-skill)

## 安装后怎样使用

局部任务直接点名相应能力。安装全部 19 项使它们可供选择，任务仍按需要读取对应资源。[官方 Skill 调用方式](https://learn.chatgpt.com/docs/build-skills#how-chatgpt-and-codex-use-skills)

| 你想做的工作 | 能力名称 |
|---|---|
| 梳理已有材料与目标 | research-intake |
| 判断适合哪些期刊 | journal-intelligence |
| 查找和整理文献 | literature-discovery |
| 精读单篇论文 | paper-deep-reading |
| 判断创新和选题价值 | topic-novelty |
| 设计研究与决定性验证 | research-design |
| 伦理、研究协议与许可 | ethics-protocol |
| 寻找数据 | data-discovery |
| 清理、连接和准备数据 | data-preparation |
| 执行分析、计算或证明 | analysis-execution |
| 稳健性与复现 | robustness-reproducibility |
| 专业论文图表 | scientific-visualization |
| 正式稿件撰写与修改 | manuscript-writing |
| 核查引用身份和支持范围 | citation-audit |
| 审稿与科学内容核查 | manuscript-review |
| 整理投稿文件 | submission-packaging |
| 回复审稿意见 | peer-review-response |
| 版本、更正和发表后维护 | publication-stewardship |
| 已授权研究的全生命周期协调 | research-paper-workflow |

可以直接复制这些请求，把附件或资料放进同一聊天或工作目录：

```text
请使用 paper-deep-reading 精读我提供的论文，区分已经证明的结论、假设和待核对问题。
```

```text
请使用 manuscript-writing 修改我提供的全文，保留数据、比较对象和证据支持的结论，并说明关键修改。
```

```text
请使用 journal-intelligence，依据我的稿件类型、研究内容和投稿约束比较合适的期刊。
```

明确要开展一个研究项目时，再使用总控：

```text
请使用 research-paper-workflow。
这是一个已授权的研究任务。先读取我提供的资料，梳理当前问题、已完成产物和最重要的证据缺口，
建立简短路线板，然后推进下一项有信息价值的工作。
```

Codex CLI/IDE 可用 `$技能名称` 明确调用；桌面端也可以用上述自然语言点名，或从实际界面的 Skill 选择器选取。

## 计算与绘图环境

安装器本身支持 Python 3.9+。附带的研究工程工具要求 Python 3.10+；需要的数值、绘图或其他运行依赖由具体任务决定。先让 Codex 查找并复用已有可用环境：

```text
请为本次任务检查本机现有工具和 Python 环境。
如果需要运行 Skill 附带的 Python 工具，选择 Python 3.10 或以上；
优先复用已有环境，必要依赖安装到本项目的独立环境，并实际运行相关检查。
```

Skill 的模型使用、网络、文件读写和研究操作仍采用当前 Codex 的实际配置。安装完成不等于科学计算环境全部准备完成，也不代表已运行第三方专业工作流。

## 双击没有启动时

打开 macOS“终端”，输入 `bash` 和一个空格，把 **一键安装.command** 拖到终端窗口，再按回车。这样不需要手工拼路径。

若解压在默认下载目录，也可以直接运行：

```bash
bash "$HOME/Downloads/academic-research-skills-v3.3.0-rc.1-one-click/一键安装.command"
```

如果提示找不到 `python3`，先准备 Python 3.9+，或让 Codex 查找应用已有 Python 来运行 `install.py`。如果提示未找到系统安装器，在 Codex 中使用 `skill-installer`，或采用下面的官方命令/手动目录方式。安装器验证失败时会显示非零退出码和具体原因。

## 只安装一个能力

在安装包文件夹中打开终端，例如只装选刊能力：

```bash
python3 install.py --skill journal-intelligence
python3 install.py --check --skill journal-intelligence
```

此操作只备份和更新该能力的用户目录；其他能力不受影响。检查部分安装时，应带上同样的 `--skill` 参数。

已有官方系统安装器，也可以从 GitHub 的固定发行标签安装单个能力：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo lhz1076277065-netizen/research-paper-workflow \
  --ref v3.3.0-rc.1 \
  --path academic-research-skills/skills/journal-intelligence \
  --dest "$HOME/.agents/skills"
```

官方命令需要联网，并在目标目录已存在时停止；处理旧版升级优先用本教程的一键脚本。其内部复用本机系统安装器的 Skill 验证和复制实现；若这些接口改变，会在更换旧目录前停止。

手动安装时，完整复制日常版 `skills/` 下所需能力文件夹到 `~/.agents/skills/`；确保直接路径是 `~/.agents/skills/能力名称/SKILL.md`，并保留该目录内的 scripts、references、assets、agents。对已有同名目录先移到 Skill 扫描范围以外的备份目录。不要把整个发行包作为一个 Skill，也不要只复制 SKILL.md。

## 备份与恢复

备份位于 `${CODEX_HOME:-~/.codex}/academic-research-skills-backups/`；每次实际更新有独立子目录及 `receipt.json`，终端会输出其完整位置。备份不会混入 Skill 扫描目录。

恢复时，在安装包目录运行以下命令，把路径替换为安装时输出的真实备份目录：

```bash
python3 install.py --restore "/完整路径/academic-research-skills-backups/本次备份目录"
```

脚本先确认本次新 Skill 原字节未改变，再恢复旧目录；新版本副本保留在备份的 `new-after-restore/`。如果你已经编辑新 Skill，会停止恢复并保留当前文件，避免丢失你的修改。安装写入过程中发生普通错误会尝试回退并保存失败收据；断电等进程无法继续的情况，可依据备份内的路径记录进行恢复。

## 正式归档验证与支持范围

正式版重新构建三个包，并针对最终归档运行构建一致性、完整回归、双PDF后端、隔离安装/备份恢复与异常回退；实际结果和最终提交摘要以同次发行的release-receipt.json为准。可运行python3 selfcheck.py重现隔离安装检查。正式包摘要与rc.5不同，安装器绑定本次实际日常包SHA256。

一键包面向macOS及已有Codex系统安装器，原生文件加载应在用户的下一轮任务中另行确认。Linux工程CLI由双后端CI验证，未认证Linux宿主安装；Windows、macOS Intel及其他Agent的原生加载尚未覆盖。本次不替换全局用户Skill。[完整支持范围](https://github.com/lhz1076277065-netizen/research-paper-workflow/blob/v3.3.0-rc.1/academic-research-skills/docs/COMPATIBILITY.zh-CN.md)。稳定v3.2.0、历史研究和旧发行附件保留。
