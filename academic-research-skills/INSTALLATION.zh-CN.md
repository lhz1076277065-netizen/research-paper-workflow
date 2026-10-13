# v3.5.4 安装与回退

从[v3.5.4正式发行页](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.5.4)下载[一键安装包](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.5.4/academic-research-skills-v3.5.4-one-click.zip)及[SHA256SUMS](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.5.4/academic-research-skills-v3.5.4-SHA256SUMS.txt)。先核验文件摘要，再解压一键包，保留install.py与运行版ZIP，运行“一键安装.command”或执行：

```bash
python3 install.py
python3 install.py --check
```

默认将全部19项安装到~/.agents/skills。安装器核验固定ZIP SHA256、清单文件摘要和CRC；替换前把同名旧目录备份到~/.codex/academic-research-skills-backups/并保存精确收据。其他Skill、全局配置和已核验14库来源缓存保留。相同完整版本重复安装不产生新备份。当前会话已加载的提示不会追溯替换，新会话读取SKILL.md核实metadata.version为3.5.4。

安装后检查全部19项matching、missing_or_changed为空、other_user_copies为空。用户要求删除旧版时，核验后只清理本次收据指向的同名旧目录和事务备份，保存安装记录；不删除其他Skill、研究材料或来源缓存。清理后不能再用该事务备份restore，需重新安装历史发行包回退。

保留事务备份时，可按安装输出的精确目录回退：

```bash
python3 install.py --restore /absolute/path/to/backup-directory
```

恢复检查当前文件身份，安装后编辑会阻止覆盖；selfcheck.py在隔离临时目录检查安装、幂等、异常回滚及恢复，不改真实用户目录。安装器需Python3.9+；研究工程CLI需Python3.10+，部分上游入口需3.11+。本机安装验收macOS ARM64；Linux工程检查由GitHub Actions执行，Windows安装未认证。

每个专业步骤调用14库内匹配的固定入口，读取并实施后finish/check才交付。缺缓存时在已授权网络内professional_flow.py begin --allow-network逐文件核commit/blob，缓存~/.codex/academic-research-source-cache可离线复用。源码准备不算专业完成；依赖/渠道问题先自主诊断并验证适配替代。

研究资料首次获取前做[200 GB容量与自主访问规划](docs/data-acquisition.md)。旧阶段、输入与成果不随安装重启，历史未计量传输保持未知。当前[发行说明](docs/RELEASE-v3.5.4.zh-CN.md)及[迁移](MIGRATION.zh-CN.md)给出实际范围与兼容变化。

运行包含使用资源，源码包含维护源、测试及历史验收，一键包含安装器和运行包。三包来自同一源码提交，manifest记录身份；SHA256不是数字签名。手动安装同样替换运行包skills/下全部19项，先备份并避免~/.codex/skills或其他自动发现位置的同名重复目录，不另装仓库根兼容副本。

可复制给Agent：

> 请从 https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.5.4 下载最新版v3.5.4一键包，核验摘要，将全部19项安装到本机Codex；安装后逐文件核验并删除收据指向的同名旧版与备份，保留其他Skill、配置和来源缓存，报告实际版本与检查结果。

历史[v3.5.0](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.5.0)及[v3.4.1](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.4.1)标签与文件保持不变。
