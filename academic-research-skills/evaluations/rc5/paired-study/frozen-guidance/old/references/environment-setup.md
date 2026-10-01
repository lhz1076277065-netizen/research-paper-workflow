# 当前研究的环境与工具

先按科学问题选择实现，动态探测操作系统、CPU架构和线程、内存、项目磁盘、Python及其他运行时/编译器。`environment.py plan/doctor`记录当前资源与选中解释器的框架可用性；发现包或设备不等于该算子已运行。个人设备值只留在项目记录。已有环境满足就复用，缺少免费依赖时在项目环境内安装、验证并继续；常规安装已经授权时直接推进。

优先沿用上游锁、venv/uv、conda、renv、Julia Project/Manifest、Cargo等真实项目环境。Python简单配方可用：

```bash
python3 scripts/environment.py ensure --task task.json --workspace /path/to/project --apply --allow-network --report environment.json
python3 scripts/environment.py calibrate --task task.json --workspace /path/to/project --backend numpy --size 128 --report calibration.json
python3 scripts/environment.py exec --task task.json --workspace /path/to/project --output results.json -- '{python}' analysis.py
```

`environment.json.python`是后续解释器；`{python}`、`python`、`python3`参数映射到它，PATH优先该环境。`--isolated`创建/复用项目专用环境；`--wheelhouse`支持离线。`runtime.python_groups`选择最小配方，`runtime.packages`补实际依赖。默认不下载全部工具或框架。外部语言包与复杂/源码依赖由其原生包管理器准备，不由pip代替。

`exec`接收argv数组，不解释shell字符串；Rscript、Julia、编译器、Rust、GIS/CAD/求解器CLI均可按实际项目执行。默认cwd是workspace，`runtime.cwd`可选已有项目子目录。`--output`列相对项目路径，记录实际文件哈希、大小和本轮是否产生/改变；缺少产物返回失败。已有文件未变只证明复用文件的身份，不能单靠成功退出码认定本轮重建。`run --script`保留Python兼容接口，也在项目目录执行。

后端候选为CPU、适用CUDA/MPS或MLX。`calibrate`真实执行小矩阵乘法并核对解析校验和，记录框架版本、精度、运行时间、进程峰值及可取得的设备内存。CPU不需要科学包；其余须已准备实际框架。该校准只覆盖指定稠密算子，不保证全部精度/算子或正式规模：继续用实际研究中的代表性求解、训练、误差或收敛任务测成本，再采用分块、流式、稀疏、降阶或更有效算法安排规模。

argv执行日志保留命令、cwd、解释器、退出码、stdout/stderr、耗时和约0.1秒采样的进程树RSS；采样内存是观测下界，精确峰值用工具自身分析器，无法取得保持null。安装和导入检查不认证研究结论。失败时修复具体依赖/接口或切换匹配实现，其余研究继续。

任务可分别描述`executor: {role: executor, actor_scope: current_host}`与`research_model: {role: research_model, purpose, source, revision, license, local: true, free_to_use: true, license_allows_research: true}`。科研模型可加载、训练、微调和评价；当前宿主继续协调。权重许可、数据许可与框架许可分别查证，新增费用或授权列外部事项。

选用时核对[PyTorch MPS官方说明](https://docs.pytorch.org/docs/stable/notes/mps.html)、[MLX安装与平台说明](https://ml-explore.github.io/mlx/build/html/install.html)和专业工具官方文档。具体接口与支持范围以本次文档和实际运行为准，软件接入步骤见`research-tools.md`。
