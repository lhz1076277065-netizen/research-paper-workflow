# v3.2.0 正式发布收尾

以v3.2.0-rc.5（9813b193a2cd6504205ede70393c22c7683e22c6）为稳定基线。本次只完成迁移说明、版本/导航一致、PR正式评审合并及新归档验收发布。19能力、16画像、14路线、按需参考、专业协议和审计接口保留。

| 文件 | 实际改变 |
|---|---|
| MIGRATION.zh-CN.md | 增加population主体显式指定和跨文件字段不自动合并两个短例；说明冻结已有封装/schema/API。 |
| VERSION、src/common版本字段、src/quality31/payload入口元数据 | 更新3.2.0，经原构建器同步937副本；运行时算法不改。 |
| 根README、library双语README、INSTALLATION、installation导航/checklist | 指向正式v3.2.0与正确能力路径；修旧固定提交；安装正文只维护一份，旧文档存history/rc5-reports。 |
| COMPATIBILITY.zh-CN.md | 明确macOS ARM64安装、Linux CLI双后端、未验证宿主/平台及有限结果/导出语义；记录实际s/was保守pending边界。 |
| release/make_package.py、test_package_identity.py | 复用既有归档机制，运行包带当前短验收/评审报告；真实Git/ZIP回归固定正式版本。 |
| test-results、evaluations/v3.2.0 | 当前608回归、双PDF、隔离模块、迁移例与独立PR评审；rc.5研究保留原范围，未重新调参。 |
| source-diffs、history/rc5-reports | 权威源差异和旧导航/汇总保留；rc.5标签与1104份既有评估文件字节保持。 |

正式包从PR合并后的最终提交重新生成运行/源码/一键ZIP，不能复用候选包摘要。所有文件摘要、最终tag/commit、解压后回归、双后端CI、安装/备份恢复和异常回退由同次发行外部receipt核验。当前源内报告不写包自身SHA，避免自引用。

稳定版表示已有软件接口在列明范围内的稳定基线；研究新颖性、普遍方法创造力及论文录用仍按实际研究判断。3.2.x只处理真实缺陷/小型兼容改进；后续能力升级使用新的研究任务和新的开发/独立评价安排，已查看480条流保持已评估证据。
