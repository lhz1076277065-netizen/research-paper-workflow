# v3.2.0-rc.5 变更与实际效果

基线为v3.2.0-rc.4 / ed4c86ec00593de48d2cb88109afe4191d1bfe04。本版定向修补结果审计、实际研究验收与读取负担；保留19个独立模块、原有专业协议和已有工具路径。

| 权威文件 | 改变及原因 | 实际验收与边界 |
|---|---|---|
| src/common/scripts/result_links.py | 复算先核科学身份与量纲，再换成原源单位使用容差；等价实现须源授权 | 真换算相等、量纲/值不等、分区差异、显示别名与科学等价正反例；完整Decimal精度及JSON往返 |
| 同一helper | 端点顺序、主值主体、否定范围；比较阈值不认作精确值；按格式拒绝混合定位，实际单位不能被远端映射掩盖 | 59项结果测试；独立20个实际文件探针在audit_links、provider audit、research31 audit及accept_result四入口一致 |
| 同一helper的build_links | 复用稿件构建行和result_id生成链接、实际哈希；校验既有哈希而非自动刷新 | 真实研究汇总24处Markdown/DOCX/PDF出现位置；复杂关系仍需定位语义复核 |
| src/common/assets/result-links.schema.json | 同步定位格式、出现角色、构建行与身份语义约束 | 实际Draft202012验证器检查合法输入及跨格式/混合坐标反例 |
| src/common/references/runtime.md、integrity.md | 分开当地出现角色、全稿字段覆盖、自动关系与定位审阅 | 图注可局部覆盖，同稿正文补全；缺失不能靠重复端点获得通过 |
| research-quality.md、computational-routes.md及三个examples文件 | 保留原推演内容，按问题加载；质量主线3152→1829字符 | 两对同路径实际读取合计12666→10020字符，减少20.9%；非token/账单测量 |
| tests/test_result_links.py、test_pdf_extract.py、report_pdf_links.py | 增加19项结果回归及2项真实PDF后端测试；旧PDF装饰器认识两后端 | 本机608项完整回归零跳过；pypdf-only真正无pdftotext，坏PDF有诊断 |
| 根.github/workflows/validate-skill.yml | pdftotext与pypdf-only两条真实CI路径，上传新库回归和PDF结果链接报告 | 所选后端及旧定位用例必须通过；对侧专属用例可跳过；远程结果在发行receipt |
| evaluations/rc5/paired-study | 四个新原生上下文做完整基线→改动→实施→检验→修订；同开发材料与预算，冻结后480条共用留出 | 三种改善各自基线、一种变差；内容/最近邻与原始结果独立匿名审阅；不认证发表新颖性 |
| evaluations/rc5/engineering | 保留首轮失败、四项假通过、修后探针、全回归、隔离模块验证及实际导出审计 | 工程事实与研究价值分别记录；原始失败未删除 |
| release/make_package.py及tests/test_package_identity.py | 复用干净Git、tracked-only、文件摘要与固定版本安装器；运行包带当前三份验收报告 | ZIP绑定真实commit/tag，最终CRC/摘要/隔离安装外部验收 |
| VERSION、README、CHANGELOG、MIGRATION、COMPATIBILITY、SUMMARY及source-diffs | 更新当前候选导航、逐项范围和权威源码差异 | rc.4报告移入history保留；不在补丁重复937个生成文件 |

公共修复由现有build_release.py统一生成，937个文件无漂移。19个模块分别复制到隔离目录后实际运行，共76项基本检查通过；16画像、13来源内容与原根UI字节保留，14路线与旧知识仍可到达。

正式发布评估：工程边界和发行检查适合rc.5候选发布；两对、一个构造问题不足以宣称普遍创新提升。保持候选版，待更多问题的实际使用反馈再评估稳定版。

[验收映射](evaluations/rc5/VALIDATION.zh-CN.md)、[研究比较](evaluations/rc5/paired-study/COMPARISON.zh-CN.md)和[独立工程审阅](evaluations/rc5/engineering/INDEPENDENT_REVIEW.zh-CN.md)可追溯。发行commit/tag、ZIP SHA256、远程CI及实际安装结果写入发行后的外部receipt，避免将包摘要写回包。
