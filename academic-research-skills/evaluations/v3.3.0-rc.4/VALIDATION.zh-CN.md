# rc.4 文本与工程验证范围

逐字审读范围与修正见[路线验收](ROUTE-AUDIT.zh-CN.md)，119份维护指令/参考、83份不同文本及14条计算路线。按最新要求取消科研个案试验，本轮不声称新模型行为验证或跨领域原创科研成功。

本机macOS ARM64/Python3.12.14完整回归610项，无失败/错误；1项因缺少对侧PDF后端跳过。root30项通过；19个独立Skill通过官方quick_validate；977项生成副本一致；git diff --check通过。现有回归包含实际Git/ZIP身份与内容排除、文件位置/数值/语义范围和渲染依赖等工程检查，不用断言新文字的出现证明科研能力。

运行/源码/一键安装包在发布提交后重新构建。实际归档CRC、逐文件SHA256、19个Skill集合、内容排除、一键内置运行包及安装器固定摘要、macOS隔离安装/恢复/异常回退检查以发行页archive-audit.json、selfcheck-results.json及release-receipt.json为准。CI在本次实际合并提交运行Linux两种PDF后端工程回归，具体链接附于发行页。

软件只证明对应检查范围；Linux工程CLI不等同其原生安装，Windows/macOS Intel及其他宿主安装加载仍未覆盖。本轮不修改用户全局Skill目录。
