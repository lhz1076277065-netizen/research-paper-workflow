# v3.3.0-rc.1 独立源码审查

范围：只读审查 `iteration-20260930061350/repository` 当前未提交增量，相对 `v3.2.0`；按 skill-creator 的范围保持、渐进披露与行为验证原则。未联网、创建 PR、发布或修改库文件。待完成的验收报告和未发布 URL 不计为缺陷。

## 结论与已修复发现

当前未发现尚未解决的可复现缺陷。以下P2在本次审查中发现，主任务修复后已独立复核通过。

**[P2，已修复] 日常包升级报告的四个本地证据链接失效。**

原 `academic-research-skills/release/make_package.py:14–17` 的 runtime allowlist 仅纳入本轮 VALIDATION 与 BEHAVIOR。实际被包含的 `UPDATE_REPORT.zh-CN.md:18–22` 还链接了本轮 `context-metrics.json`、`SOURCE-OBSERVATIONS.json`、`CHANGES.json`、`ORCHESTRATOR.md`，但四个已存在的目标被 evaluations 目录排除规则删除，造成日常包/一键包中的报告断链。

主任务将四项加入现有allowlist，并增加 `test_package_identity.PackageIdentity.test_runtime_keeps_update_report_local_targets`。ORCHESTRATOR原文进入代码块，导航链接指向真实能力入口，避免复制原文内的相对路径按报告目录错误解析。重新检查全部runtime Markdown本地链接闭包，断链从4项降为0；本轮6份记录全部包含。

在仓库根目录运行以下只读复现：修复前四项均为 `False`，修复后四项均为 `True`：

```python
import importlib.util
from pathlib import Path
p = Path('academic-research-skills/release/make_package.py')
s = importlib.util.spec_from_file_location('package_review', p)
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
included = {f.relative_to(m.ROOT).as_posix() for f in m.chosen('runtime')}
for name in ['context-metrics.json', 'SOURCE-OBSERVATIONS.json', 'CHANGES.json', 'ORCHESTRATOR.md']:
    target = 'evaluations/v3.3.0-rc.1/' + name
    print(target, target in included)
```

未发现其余新增可复现缺陷。

## 已核对

- 完整阅读19个维护短入口、新增两份指导、3个修改专业协议、完整30项写作协议、来源/宿主约束、动态发现与选择代码、构建/打包/安装器及相关修改测试。`src/common` 与 `src/quality31/payload` 仍生成公共资源/短入口；各能力 `protocol.md` 仍为直接维护源。
- `build_release.py --check` 为 clean，977项生成身份全部匹配。19入口最长795字符；16份未修改专业协议逐字保留，3份协议只改相应问题综合段；完整写作协议与基线字节相同，30项齐全。
- 原13仓库及旧角色全部保留，当前14来源。Orchestra 仅可选 ideation/novelty，来源入口仍在使用时动态发现；STORM未纳入自动来源。当前宿主、科研模型与执行助手边界保留。
- 开放选题指导按需读取；允许算法/模型创新、成熟方法与基础理论，以问题/解释能力判断价值。局部写作、图注、选刊、既定方法请求仍保持局部范围，没有新增全链调用要求。
- VERSION、19入口、公共配置及工具版本为3.3.0-rc.1；安装教程/标签/目录引用一致，稳定3.2.0保留为基线。工作树与修复后的runtime本地导航全部可解析。

## 实际检查与边界

- Python3.11：`test_quality31`、`test_lean.Sources`、`test_release.ScopeAndCoverage` 共110项通过；测试仅使用临时目录或读本库。
- 修复后重新检查生成977项为clean，`test_package_identity`新增目标保留检查及原有归档身份/输出保护检查共3项通过；合计113项针对性测试。
- 使用已有Python3.12/PyYAML环境运行 skill-creator `quick_validate.py`，19/19通过，未安装依赖。所有检查关闭bytecode写入。
- 本轮只读检查打包文件选择与链接闭包；未构建最终归档、安装到用户目录、验证原生加载或判断普遍科研能力。
