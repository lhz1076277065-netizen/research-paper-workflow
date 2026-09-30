# Changelog

## 3.1.1

Fix five reproduced record semantics: strict factual-review booleans; manuscript-bound review subjects; assistant scope separate from research action names; task/prior-art bindings for literature, reading and novelty; prospective protocol delivery applicability. Preserve 19 capabilities and focused-task autonomy.

# 3.1.0

完整通用学术Skill迭代：保留19个独立能力与详细专业协议，补充重要问题/知识增量/决定性证据的研究路线，明确局部任务与Skill开发更新的边界；不绑定任何具体学科。

外部专业实现从用户指定13来源动态选择，使用当前Agent及现有模型；正式主图和完整全文要求真实专业步骤与最终文件关联。指定反防御性写作采用事实保持适配。可选检查器只验证记录与产物一致性，不认证科学质量。

修复帮助命令副作用、macOS路径别名断言、合法等号CLI参数、错误记录类型、focused单图误触发完整流程、全文版本关联、旧版本元数据与重复维护源覆盖。完整日常版/源码版各自打包，开发历史不进入日常版。

# 3.0.0

定稿：动态快照交接与缓存、环境恢复、安装可移植性、产物范围审查、工作图自主性及发布验证。详见release/FINAL-REVIEW.zh-CN.md。

# 3.0.0-alpha.5

Lean entrypoints and optional references; dynamic GitHub repository discovery and per-run source snapshots; short default text export; retained full research references and 30 writing items; compatible dependency constraints merge; optional portable selftest. Legacy provider snapshots moved to test fixtures, not the runtime registry.
