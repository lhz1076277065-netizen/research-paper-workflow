# 3.4.0-rc.2 本地安装与回退

本版是本地候选版，未发布GitHub。适用于当前macOS ARM64与已有Codex系统skill-installer。安装器Python3.9+；工程CLI Python3.10+，部分上游入口要求3.11+。验证环境Python3.12.14。其他宿主原生安装未认证。

解压academic-research-skills-v3.4.0-rc.2-one-click.zip，保留目录中install.py与日常版ZIP；运行“一键安装.command”，或在该目录执行：

```bash
python3 install.py
python3 install.py --check
```

默认安装全部19个skill到~/.agents/skills；替换前把所有同名用户安装目录转移到~/.codex/academic-research-skills-backups/下的新备份，保留收据及原始字节。 unrelated skills不变。相同完整版本重复安装不产生新备份。安装成功说明文件匹配；当前会话已加载的旧提示不会因此被追溯替换，下一轮或重启后读取实际SKILL.md核实metadata.version。

回退使用安装输出的精确备份目录：

```bash
python3 install.py --restore /absolute/path/to/backup-directory
```

恢复前核对新版本文件身份；若用户后来编辑了文件，停止恢复并保留所有内容，不能强制覆盖。恢复会保留新版本副本。独立selfcheck.py在临时用户目录检验安装、重复安装、文件保护、失败回退及旧目录恢复，不更改真实用户目录。

专业来源缓存不混进Agent全局skill目录。capabilities.py prepare按固定commit校验源码，需要显式allow-network；可以复用交付的本地integration-cache并离线准备。缓存只存源码，不安装依赖、不运行模型、不启动工作台。每个项目按任务声明缓存根和原生依赖，详见docs/capability-routing.md。

日常版ZIP只包含使用资源；源码ZIP包含src、tests与验收档案；one-click ZIP包含安装器和日常版ZIP。SHA256SUMS校验文件身份，不是数字签名或科学质量证明。安装包不得从不存在的rc GitHub发行链接下载。本轮没有远端发布。
