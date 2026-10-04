# 使用已核实的专业入口

assets/capability-index.json保存14个来源的已核实commit/tree、入口、必需文件blob、能力类型、依赖、输入/输出及宿主适配。它是可用入口索引，不是所有子能力的穷尽目录。当前任务从对应角色选择一个主实现；需要其他子入口时用原upstream发现并另存版本，不全量扫描或下载。

```bash
python3 scripts/research31.py capabilities --role reading
python3 scripts/capabilities.py prepare --id nature-reader --root project/source-cache --allow-network --out project/nature-prepared.json
```

prepare保留原仓库相对目录并逐文件核对Git blob；离线可复用已核验缓存。读取返回entry和实际所需core/reference，随后按专业步骤执行。prepare不安装依赖、不调用模型、不启动应用；没有执行专业工作就不能登记research_work_done。

- skill_protocol：当前Agent按入口及所需资源实施；主体步骤与成果保留。
- code_tool：核实运行依赖、硬件与许可，实际执行代码才称native/functions_run。
- reference_code：使用相应参考或示例改变图表设计；不伪称调用Agent。
- workbench_protocol：可选工作台接口，任务无需工作台时采用明确的本地专业子流程，不强制启动产品。

上游的无限循环、自动更新、其他助手调度、收费/外发和额外审批不会扩大本任务授权。当前宿主适配写清替换部分，保留专业实质；没有独立审查就不能声称cross-model review。H100专用训练在Mac上不假装通过；图像整页PPT不能声称可编辑文本。缺必要条件时记录native阻碍、适配完成范围和替代实现。

每次使用关联当前任务的inputs、outputs、steps与source identity。capabilities.py use可保存真实文件哈希和独立progress三项；这只核对身份与文件存在，不验证语义。将输出实际接到路线板、结果、图或稿件，不拿别的测试补角色。局部流程可无需上游附带函数；运行函数不代表完整角色已完成。

sources/select/upstream/assess保持原接口。旧记录没有phase或能力信息时保持unknown，不要求重新执行已完成研究。查看索引里的known_requirements与adaptation；发现源码更新另建快照，不覆盖正在复现的版本。维护时逐库做集成验证；日常论文按需使用，不要求14库打卡。

源码缓存默认~/.codex/academic-research-source-cache，按id/commit复用，不进入全局skills目录；项目需隔离时显式--root。已缓存版本无需allow-network即可prepare，修改过的缓存拒绝覆盖。验收档案路径仅在源码包中可用，运行包不携带测试答案。
