# PR #1 合并前独立评审

结论：在本次冻结源码与用户导航范围内，**未发现阻止合并的实际问题**。正式版保留已审查rc.5接口，更新版本、迁移说明、支持范围与发行导航；未增加研究循环、默认框架或能力。

评审基准：本地origin/main为`c47c98a094fafac65b3beb283d35cf478ae6e2af`；正式发布以rc.5提交`9813b193a2cd6504205ede70393c22c7683e22c6`为业务基线。本报告检查该PR相对主分支的权威维护源、既有独立审查及最终3.2.0工作树；没有改运行时源码或向GitHub提交评审／合并操作。

## 本轮实际检查

- 读取唯一维护源、生成器、task/result/result-links schema及provider_runtime/research31调用链。正式树所有公共脚本与rc.5的差异仅为版本字符串；三个接口schema逐字不变，19份入口正文除版本外不变，19份详细protocol不变。实际计数仍为19能力、16画像、14路线、13指定来源，三个按需推演分片保留。
- 独立运行6项真实JSON／Markdown迁移检查：population不指定主体时保留pending，明确`subject_field=population`后通过；同source/result/artifact内正文补图注覆盖，跨文件caption的lower/upper缺口仍定位pending。直接解析MIGRATION内实际JSON与句子，补canonical value后的等号例通过。
- 保留`Cohort A mean was 0.41 s.`的实测保守pending：现有单位文本处理使连接词不能自动确认，报告保留实际定位，没有假通过。COMPATIBILITY已如实说明；本次冻结不扩写解析器。
- 读取归档和安装代码，核对版本固定、包摘要绑定、旧目录备份、用户修改保护及异常回退。根README、双语库README、安装教程、installation导航／checklist统一`v3.2.0`和正确能力目录；已修复旧rc.3固定提交。安装教程的支持链接使用固定版本URL，直接复制到一键包README后不会指向缺失的docs目录。
- 按真实make_package选择逻辑投影运行包：当前短验收／评审报告在包内，必要用户文档的相对文件链接均可到达；历史研究原始材料保留在源码包与固定旧tag链接，不以丢失的运行包相对链接代替。构建检查为937文件、无漂移。
- 对rc.5提交中1103份已跟踪评估文件与原Git blob逐字节比较，未发现变化；作者的独立文件清单另统计1104份材料。480条已查看留出、冻结方法、失败记录与原比较没有重调参或重标为本轮新研究。

预审指出的安装旧引用、文档语义映射缺value和包内导航问题已修正；没有留下未修复的合并阻塞项。

## 证据与复现

本轮独立代码／投影与迁移材料在[正式源包评审目录](https://github.com/lhz1076277065-netizen/research-paper-workflow/tree/v3.2.0/academic-research-skills/evaluations/v3.2.0/review)。在库根使用Python3.12.14运行：

```sh
/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 evaluations/v3.2.0/review/migration_probe.py /tmp/academic-v320-migration-review
/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 evaluations/v3.2.0/review/release_tree_check.py /tmp/academic-v320-tree-review.json
```

迁移输出目录须尚不存在。保留结果为`review/migration-final/summary.json`（6项符合预期）与`review/release-tree.json`（全部检查通过）。result_links.py SHA256仍为`471b32401fa0b2f35ac5cafd1b2eea67f20cc8b9eb728212dbfd58f274fb92a2`。

复用[rc.5独立工程审查](https://github.com/lhz1076277065-netizen/research-paper-workflow/blob/v3.2.0-rc.5/academic-research-skills/evaluations/rc5/engineering/INDEPENDENT_REVIEW.zh-CN.md)：此前本人实际执行20个文件探针／四个入口，修复后的unexpected为空，59个关联测试与两个真实PDF后端测试通过。共享审计器字节未变。本轮读取作者重新生成的608项完整回归、30项根回归、双PDF后端及19目录／76项隔离基本检查记录；没有将这些作者执行结果写成本评审重新执行，也没有新增研究评价。

## 范围与发布后核验

检查覆盖当前接口、上述迁移行为、源到生成副本、归档筛选、安装代码和导航；不认证完整句子真值、源结果真实性、原创性、一般研究质量或发表概率。复杂关系仍需实际定位阅读。macOS ARM64与Linux工程CLI证据、未验证平台和原生宿主范围在[支持说明](../../docs/COMPATIBILITY.zh-CN.md)中分别表述。

本地origin/HEAD指向main。GitHub实时默认分支、PR正式评审／ready／合并提交、最终tag、三个ZIP及其摘要、远程CI和最终归档安装，尚不属于本次源码投影的完成证据；由同次发行后的外部release-receipt.json记录实际状态。报告不将拟发布链接或预期包身份当成已验证结果。
