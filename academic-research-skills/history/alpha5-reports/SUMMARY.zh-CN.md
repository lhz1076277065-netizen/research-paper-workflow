# alpha.5 验证与瘦身摘要

最终独立回归：**386项**，失败0、错误0、跳过0。335项基线另行复跑，不重复计入最终数量。完整逐项结果在regression.json和regression.txt。

19个入口字符由34846减到10920，减少68.66%；默认稿件文本导出由13786减到691，减少94.99%。这是字符统计，不是模型能力或速度测量。

147个原专业章节、19个能力和30项写作内容保留。默认上游注册表为空；来源库13个URL只作起点，支持其他仓库与运行时新路径。动态API测试使用合成响应；本轮另通过真实GitHub连接器读取了一个来源的commit、树与代码片段。

真实本地功能链：验证已有NumPy/Pandas/SciPy/Matplotlib环境→已知解析关系计算→SVG/PNG→Markdown报告→结果交接。测试数据明确为人工构造的解析校验材料，不是论文实验或外部数据集。当前助手实际查看了生成图像，记录在scientific-smoke/visual-review.json。

运行平台：Linux x86_64，Python 3.13.5。macOS、Windows原生、品牌Agent的原生发现/执行、模型A/B能力、真实上游科研后端与真实论文全周期未测试。本机可运行scripts/selftest.py；源码包可运行tests/run_all.py。

容器直接HTTP解析api.github.com和pypi.org失败；不将连接器读取或mock API测试说成该CLI已经联网运行。没有访问用户电脑或修改GitHub。

发行检查：不含src/tests的日常包、单独复制的选刊能力均运行本地自检通过；独立能力的真实科学库解析测试链通过。发行冒烟不重复计入386项回归，也不表示原生Agent已加载。
