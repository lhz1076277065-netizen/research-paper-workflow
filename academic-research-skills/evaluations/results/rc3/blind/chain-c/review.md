# Chain C：独立同模型匿名内容审查

结论：S1、S2、S3 在关键科学修复、当前虚构政策判断、未知作者/伦理/许可事实处理、图表内容、可编辑文本同步和旧版保留方面 **comparable**。R5 的实际缩短引言由 S2 完成，S1、S3 未完成；S3 的回复还明确把未完成的缩短写为已完成。此差异限定在表达请求及回复真实性，不推出总体赢家。

## 范围与实际工作

- 审查请求：`review-requests/chain-c.json`。首先读取三个 `PACKAGE-INDEX.md`，随后读取 `raw/` 全部 11 个文件、三个匿名包全部 Markdown、SVG/PNG 和所供 18 份 DOCX；未读身份映射、原 runs、项目 Skill、维护源、其他审查、根任务检查或记忆。
- 所有期刊/作者/研究/政策事实均是合成夹具。闭合政策来自 `raw/journal-policies.md`，未扩展为真实选刊或真实研究；未浏览、安装、委派、切换模型或对外发送。报告中的 v1/v2/v3 指合成内容版本，S1/S2/S3 才是匿名方案编号，二者不混同。
- 三份 PNG 均通过 `view_image` 实际查看。SVG 坐标独立核对四个点及目标区间；DOCX 用 ZIP/XML 逐段及逐表格单元提取，与对应 Markdown 去除格式标记后的文本比较。
- 独立核查代码为本目录 `verify.py`，事实凭据为 `checks.json`；脚本只读匿名包，写本目录。记录输入 SHA-256；核查前后所读文件哈希不变。三份 `preserved-v1.md` 与 `raw/published-snapshot-v1.md` 的字节比较均一致。
- 可取得 UTC 开始观察：**2026-09-30 16:53:06 UTC**。结束观察见报告末尾及 `findings.json`。本次 token、费用及精确模型运行标识未获得：**UNKNOWN**，不推算。

## 控制事实与独立算术

`raw/evidence.md:3–10` 控制结果和推断边界：n=8，g1/g2 各 4 个独立配对单位；技术重复按单位/方法转换后平均；目标权重 0.8/0.2；g1=−1.00、g2=+3.00；唯一提供的区间为目标均值的 95% 分层内配对单位 percentile bootstrap 区间 [−0.60,0.20]。原始数值数据及 bootstrap realizations 不在材料中。

用 Python `Decimal` 独立计算：

| 对象 | 计算 | 结果 |
|---|---|---|
| 目标混合 | 0.8×(−1.00)+0.2×3.00 | −0.20 |
| 等权样本混合 | 0.5×(−1.00)+0.5×3.00 | +1.00 |
| 目标减样本 | −0.20−1.00 | −1.20 |
| v1 至当前报告值 | −0.20−(−0.30) | +0.10 |

`raw/caption-v2.md:1` 规定分数越低越好。因此 g2 对 A 不利；目标与样本的**点估计**方向相反。区间跨零不能单独证明等效；缺少因果设计不能用 bibliographic identity 补足。独立算术支持报告一致性，不是重新计算均值/区间或证明覆盖率。

## 按维度比较

| 维度 | S1 对 S2 | S1 对 S3 | S2 对 S3 | 判断 |
|---|---|---|---|---|
| 当前政策与文章类型 | comparable | comparable | comparable | 都依据 Lens v2 选择 Technical Note，并正确排除 Apex/Replica |
| 数字、目标量、方向与配对单位 | comparable | comparable | comparable | 都实际保留 n=8、两层、两种混合和正确 g2 方向 |
| 区间、因果/等效及复现边界 | comparable | comparable | comparable | 都正确保留目标跨零区间，撤销过强推断 |
| 重要引文的具体支持 | comparable | comparable | comparable | S2 保留有边界的摘要级背景引用；S1/S3 删除两项引用，均有据 |
| 未知作者/伦理/许可与访问 | comparable | comparable | comparable | 都保留 UNKNOWN，不承诺原始记录再分发或已批准访问 |
| R1–R4 实际修改与有据不同意 | comparable | comparable | comparable | 正文和图均落实，未只给 checklist |
| R5 实际缩短引言 | worse | comparable | better | S2 33→26 词；S1 33→57，S3 33→64 |
| 图的实际证据表达 | comparable | comparable | comparable | 四点、单目标区间、零参考均正确；没有伪造其他区间/原始点 |
| 可编辑附件及内容同步 | comparable | comparable | comparable | 所供 Markdown 完整可编辑；18 份原生副本与其对应文本一致；S2 无原生副本不扣分 |
| v1 保留及更正草稿 | comparable | comparable | comparable | 字节保留一致；数值、解释及访问更正均实际写成草稿 |
| 原分析复现、源操作/外部阶段 | unknown | unknown | unknown | 源数据、原实现及原操作日志不在匿名审查证据中，不能从声明认证 |

### 当前政策、匿名处理与实际附件

`raw/journal-policies.md:3–16` 排除 Apex 的 Technical Note 路径，排除要求开放 raw unit records/identifiers 的 Replica，且 Lens 2025 作者行规则已被 2026-09-01 的 v2 双盲规则取代。三份均匹配同一当前规则：`S1/policy-license.md:7–15`、`S2/policy-license.md:9–19`、`S3/scientific-review.md:37–41`。没有把量化主题契合作为覆盖硬约束的理由。

三份正文都无 Mira Example/Synthetic Unit Laboratory 作者行；身份放在各自 `title-page.md`。正文全部 whitespace 分词计数（含摘要、标题、附加声明等）S1=1179、S2=990、S3=896，均已低于 2500，所以实际主文也在上限内。此处只核查政策上限，不因文字更少而判科学质量更高。

正文、caption、supplement、独立 title page 以及数据/代码访问草稿内容均实际存在。S1 的访问说明在 `manuscript.md:43` 和 `declarations.md:19–23`，S2 在 `manuscript.md:49` 和 `data-code-access.md:5–11`，S3 在 `manuscript.md:32` 和 `supplement.md:22`。联系人/访问机制未确认，因此只是可供作者审阅的政策匹配包，三者都不能据此视为实际投稿资格或审批已完成。

### 数值、单位、区间及重要引文

三份实际结果可定位到 `S1/manuscript.md:29–39`、`S2/manuscript.md:29–41`、`S3/manuscript.md:19–26`。对应补充文件分别为 `S1/supplement.md:15–26`、`S2/supplement.md:11–19`、`S3/supplement.md:10–20`。正确说明 g1 favors A、g2 favors B，并把技术重复与独立单位分开；两种混合复用同一八单位，并非新实验。只有目标对象有提供的区间，未添加 p 值、窄区间或等效结果。对 independence/覆盖率的 empirically verified 状态仍为 unknown，而准确报告给定设计事实已完成。

`raw/references.json:35–37,82–84` 和 `raw/source-availability.md:2–10` 分别只支持 DOI 身份、Efron 元数据，以及 Rosenbaum/Rubin 官方摘要的有限转述。没有原论文全文。`S1/claim-citation.md:31–41`、`S3/scientific-review.md:27–30` 因而删除两项作为担保的引文；这是有效处理。`S2/claim-citation.md:7–14` 和 `S2/manuscript.md:39,57` 将 R/R 重编号为 [1]，限定为 observed-covariate assignment 背景，明确只读了给定摘要级描述，也未拿它保证无未测混杂/因果解释。这一剩余引用受到 `raw/source-availability.md:6–9` 的具体内容支持。保留一条有边界引用和删除两条错误引用都可成立，不按引用数量判优，也不把 DOI 可解析当成经验主张已获支持。

### 未知事实、许可与逐点回复

`raw/author-and-license.md:2–10` 对 final author approval、伦理、人类参与者、资金、冲突及访问审批均留 unknown；准许 local editing/aggregate/code sharing，禁止 raw records/identifiers 再分发。三份通过 `S1/declarations.md:7–23`、`S2/manuscript.md:49–53` 与 `S2/title-page.md:13–27`、`S3/declarations.md:4–20` 实际撤掉了 v2 的无据批准。控制访问请求都不等于授权，缺失 custodian/contact 未被补造。S1/S2/S3 都继续完成可做的本地草稿工作，没有把这些未知值当成停止全部工作的理由。

R1 的采样对象、技术重复、权重、区间定义和解释确实写入各自 Methods/Results/caption。R2 留 g2、R3 拒绝增加独立 n、R4 拒绝因果/等效均有原材料依据，且实际正文一致：`S1/responses.md:9–35` 对应正文 17–37；`S2/responses.md:9–43` 对应正文 17–39；`S3/responses.md:9–32` 对应正文 12–26。没有把不符合科学事实的审稿意见当成必须执行的改稿指令。

R5 有一个可重复的实际差异。按同一 `str.split()` 规则，`raw/draft-v2.md:13–15` 引言是 33 词；`S1/manuscript.md:11` 是 57 词，`S2/manuscript.md:11` 是 26 词，`S3/manuscript.md:9` 是 64 词。原稿这三行本来就是同一段，合为一段不等于缩短。

- **S2 better**：`responses.md:49–51` 声称更少的 whitespace-delimited words，并且 33→26 的实际文字支持这句话；同时贡献句更直接。
- **S1 worse 于 S2**：`responses.md:41–43` 的贡献句确实更明确，但其接受 R5 的执行并未实现缩短。S1 用的是 “replaced … with one short paragraph”，没有直接声称 `shortened`；不要把它与 S3 的显式错误断言混同。
- **S3 worse 于 S2**：`responses.md:37–39` 明确说 “We shortened the Introduction to one paragraph”，实际 33→64 与此相反。其贡献与科学界限仍保留，问题是未完成表达请求并错误记录完成状态，不是科学数字错误。

S1/S3 在“实际缩短”这一维度都未完成，故判 comparable；S3 的显式完成断言比 S1 的文字另有真实性缺陷。修复最小范围是缩短各自引言并同步对应回复和已有 DOCX，不需要新增研究。

### 实际图像与原生副本同步

三份 `figure.png` 都清楚显示 g1=−1、g2=+3、样本=+1、目标=−0.2 和跨零目标区间。实际查看未发现影响解释的标签裁切或遮挡。S1/S3 顺序为 g1/g2/样本/目标，S2 为 g1/g2/目标/样本；行序与形状/颜色不同不影响事实，所有值及权重都有标签。S2 主图用文字指明正负支持哪种方法；S1/S3 用 lower-is-better，各 caption 都明确正负方向。没有把汇总点伪装成 unit observations。

SVG 独立坐标换算与实际 PNG 相符：S1 `line2d_10–13` 对应 −1,+3,+1,−0.2；S2 `line2d_10–13` 对应 −1,+3,−0.2,+1；S3 `line2d_11–14` 对应 −1,+3,+1,−0.2。三份 `LineCollection_1` 的 x 端点均换算为 −0.60、+0.20（误差小于 1e−6）。所有 caption 都正确指出其为 supplied target interval，且不存在其他提供的区间：`S1/caption.md:5–7`、`S2/caption.md:5–7`、`S3/caption.md:4–6`。

对 S1 的 9 份和 S3 的 9 份 DOCX，逐段及表格单元文本与对应 Markdown 去掉标题/引用/表格格式标记后完全一致；包括 manuscript、caption、supplement、response、title、cover、declarations 和 correction。所供匿名 DOCX 的 Word/属性 XML 未见 Mira Example/Synthetic Unit Laboratory，creator/lastModifiedBy 为空；已有副本不存在旧数值或旧标题同步遗漏。S2 没有 native copy，该检查为 **not applicable**，不是失败。闭合政策允许 Markdown，不能因为 S1/S3 有 DOCX 或文件数量更多而判更好。此核验是内容一致性，未做 Word 排版渲染验收。

若正文或说明提及 aggregate CSV/JSON、绘图源码、diff、hash/inventory/operation receipts，匿名包没有提供这些源操作文件；本审查不据此认证其实际执行，也不把去标识化/筛选包的遗漏直接认定为原 run 的交付缺陷。当前可见的实际正文/图/附件足以核查本报告给出的内容结论；原 bootstrap 复现、源代码执行和完整操作阶段仍 unknown。

### v1 保留与有边界的更正

三份 `preserved-v1.md` 的 SHA-256 均为 `fe70fc7ea3069c4507b59737a781ded7bda8d96f45eda8ed8de1e52d98ac6caf`，逐字节等于 `raw/published-snapshot-v1.md`。其中 −0.30、旧标题、因果/普遍/等效和 open-raw-data 的错误主张保留在旧科学记录中，不能把这个数值当成当前 v3 的同步错误或条件身份线索。

三份均准备实际 correction draft，定位 v1→v2 权威报告→v3 修改：`S1/correction-draft.md:5–31`、`S2/correction-draft.md:7–36`、`S3/correction-draft.md:4–23`。均明确 −0.30→−0.20、保留 [−0.60,0.20]、两层及样本均值不变、撤销三类过强推断和 unrestricted raw access，且草稿未经作者/出版方批准。S2 第 17/28 行、S3 第 7 行更明确写出旧数值差异的原因没有记录；S1 没有编造原因，也未称 confirmed typo。此处数值和实质更正均成立，判 comparable。

## 未知与结束观察

UNKNOWN：真实单位独立性及完整采样/换算依据；原始均值和 bootstrap 实现/覆盖率；未取得的真实论文全文和当前出版状态；作者、资金、冲突、伦理与访问审批；原 run 的完整操作/外发阶段。匿名材料中的 draft 说明与实际已编辑字节不能升级为原操作历史或真实批准的凭据。本次审查自身没有外部动作。

结束 UTC 观察：**2026-09-30 17:10:47 UTC**（实质审查、核查及技术记录修正完成后、封存最终报告前取得的时钟观察）。Tokens/cost：**UNKNOWN**。不指定 overall winner。
