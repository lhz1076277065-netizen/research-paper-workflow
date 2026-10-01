# v3.2.0-rc.5 定向修补验收

基线v3.2.0-rc.4（ed4c86ec00593de48d2cb88109afe4191d1bfe04）。本次形成通用Skill候选更新，研究例用于实际验收，没有交付原创新论文。

| 目标 | 实际结果 | 可运行证据 |
|---|---|---|
| P0 复算身份与单位 | 先核科学身份和量纲，换算后比较容差；实现等价只接受源授权；保留任意输入Decimal精度 | tests/test_result_links.py；engineering/INDEPENDENT_REVIEW.zh-CN.md、independent-review/after/ |
| P1 位置关系 | 端点顺序、主值主体、限定否定；比较阈值进入定位pending，错误单位及伪格式定位不通过 | 同一共享helper、schema、59项针对测试与20个独立实际文件探针，四入口一致 |
| P1 覆盖与构建行 | 当地角色、全稿字段、自动关系与定位审阅分开；复用真正稿件行生成哈希关联 | paired-study/manuscript-build/build-rows.json、links.json、result-links-report.json；24处三格式通过，无pending；PDF实际视觉审查另记 |
| P1 实际方法循环 | 四个新上下文、两对同任务比较；每个40次dev，B1另3次train；方法冻结后480条共同留出 | paired-study/TASK.md、conditions.json、各提交research.md/methods.py/frozen.json/日志、independent/、independent-review.md |
| P2 PDF完整路径 | 真实pdftotext和仅pypdf执行；旧PDF定位、有效/坏PDF、越界页检查 | tests/test_pdf_extract.py、report_pdf_links.py；pdf/和engineering/final-*-after-review/；根CI两真实backend lane上传新库完整回归及结果链接报告 |
| P2 按需读取与独立性 | 三片推演内容保留；实际同路径读量12666→10020字符，减少20.9%；19个独立复制执行 | paired-study/usage-audit.json、read日志；engineering/distribution/distribution.json：76项基本检查；16画像、14路线、13来源和协议保留 |
| P2 收敛发行 | 唯一维护源生成937文件，无漂移；完整608项回归0失败/错误/跳过 | engineering/final-regression.json/txt、build-check.json、root-regression.log；source-diffs权威差异；最终ZIP/CI/安装在外部发行receipt |

首轮603项中两项失败（导航缺报告、旧包fixture仍指rc.4）与独立审阅发现四个假通过均保存，修后完成608项全回归。未删除失败材料，也未用脚本成功替代科学判断。软件回归的合成HTTP夹具与实际PDF/研究操作分开报告。

研究结果：A1相对自身基线损失降低4.021，探索区间[1.940,6.052]；B1、B2降低0.500、1.087，其区间包含0；A2增加1.410。初始方法、修订、消融和失败均保留。B2组件消融使用同48步窗口的匹配版本。共同rolling-median只是已知比较方法，不是最新robust RUME论文的完整实现。83211项固定前缀和报警邻界检查通过，非全时点形式证明。

匿名内容审阅基于实际近邻文献、冻结源码及原始留出/开发评分材料；独立复现8640条方法留出行、480条median行、160次开发调用、17组配对统计及bootstrap端点，全部吻合。匿名包未含训练/历史诊断与median搜索过程，未据复现认证所有开发行为；完整原始记录另随源包保存。连续区间删除有实际任务增量，确认、截断和窗口成分已有近邻；这些构造问题实验未建立发表新颖性。两对上下文、一个问题、计时边界与运行中追加共同自检的限制见[比较报告](paired-study/COMPARISON.zh-CN.md)。读量为实际输出字符，非token、完整隐藏上下文或费用。

正式发布评估：工程修补已具候选发布证据，保留rc.5 prerelease；有限研究比较不足以宣称普遍质量提升。稳定版宜待更多问题的使用反馈与迁移确认再评估。

同次发行后的外部receipt包含实际commit/tag、每个ZIP CRC/文件SHA256、隔离提取安装、远程CI及附件检查。远程两条单后端lane允许缺失对侧后端的专属用例跳过，旧PDF定位及所选后端必须执行；本机两后端完整回归为0跳过。旧rc.4证据保持其原范围。
