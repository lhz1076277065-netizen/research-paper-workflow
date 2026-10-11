# v3.5.2 本地维护版安装

本地交付包包含academic-research-skills-v3.5.2-one-click.zip及对应SHA256SUMS；解压后执行一键安装，再运行install.py --check。全部19个能力须一起更新，共享工具与指引同步；替换前自动备份，验证后按用户清理偏好移除旧副本。保留固定来源缓存和无关Skill配置。当前会话已加载的提示不会追溯替换，新会话核实实际版本。v3.5.2尚未发布GitHub，以下v3.5.0链接仅供历史正式版下载。

阶段状态和研究材料不随安装重启；新解阻逻辑及真实恢复边界见[维护导航](docs/RELEASE-v3.5.2.zh-CN.md)。下列安装器命令、验证与回退机制也适用于本地v3.5.2包。

## 历史v3.5.0发行安装

# v3.5.0 安装与回退

当前正式版、14库入口与验收范围见[发行与文件导航](docs/RELEASE-v3.5.0.zh-CN.md)。三个安装/源码ZIP固定到同一发布源码提交，带逐文件摘要和独立SHA256。

从[v3.5.0正式发行页](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.5.0)下载[academic-research-skills-v3.5.0-one-click.zip](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.5.0/academic-research-skills-v3.5.0-one-click.zip)及[SHA256SUMS](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.5.0/academic-research-skills-v3.5.0-SHA256SUMS.txt)。已验收macOS ARM64与已有Codex系统skill-installer；安装器Python3.9+，工程CLI Python3.10+，部分上游入口要求3.11+。Windows安装未认证，Linux工程CLI由CI检查。

解压一键包，保留目录中install.py与日常版ZIP，运行“一键安装.command”或在该目录执行：

```bash
python3 install.py
python3 install.py --check
```

默认安装全部19项到~/.agents/skills。安装器验证固定ZIP SHA256、全部清单文件摘要和CRC；替换前把同名旧目录备份到~/.codex/academic-research-skills-backups/并保存精确收据；其他Skill保持原样。相同完整版本重复安装不产生新备份。当前会话已加载的提示不会被追溯替换，新会话读取实际SKILL.md核实metadata.version。

按安装输出的精确备份目录回退：

```bash
python3 install.py --restore /absolute/path/to/backup-directory
```

恢复核对当前文件身份，安装后用户编辑过的内容会阻止覆盖；原始字节保留，新版副本也保留。selfcheck.py在临时用户目录检查安装、重复安装、异常回滚及恢复，不改真实目录。

每个专业步骤的14库来源保持固定commit/blob。首次使用未缓存入口时，在已授权的联网任务中调用professional_flow.py begin --allow-network；缓存命中后离线复用。源码存于~/.codex/academic-research-source-cache，不能只读本地总控替代专业入口。无需额外安装全部应用或训练依赖；源不可用或必要条件缺失如实报障。缓存不进入全局Skill目录，不把准备源码计作执行。

日常版ZIP只含使用资源；源码ZIP含维护源、测试和历史验证；一键包含安装器与日常版ZIP。SHA256用于核对文件身份，不是数字签名。手动安装可将日常版skills/下19个目录复制到~/.agents/skills/，先备份同名旧目录并排除~/.codex/skills/内重复副本；不能同时安装根目录兼容副本。

可复制给AI Agent：

> 请从 https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.5.0 下载v3.5.0一键安装包，按其中部署教程将全部19项通用学术Skill安装到本机Codex，核验安装包SHA256、备份同名旧版，并在安装后报告实际路径、版本和检查结果。
