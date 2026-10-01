# 当前操作的环境准备

先确定研究方法与执行器，再检查实际依赖。已有环境满足就复用；缺少时在项目环境内安装，使用同一解释器验证和运行。常规安装已经授权时直接推进，不逐包追问。平台、硬件、GPU和依赖在执行机器上探测。

优先使用上游的现有项目锁、uv/venv、conda、renv或对应包管理器；复杂依赖不必迁就本包最小安装器的语法。Python的简单任务可用：

```bash
python scripts/environment.py ensure --task task.json --workspace /path/to/project --apply --allow-network --report environment.json
```

`environment.json`中的`python`是后续解释器。`--isolated`新建项目环境；`--wheelhouse /path/to/wheels`支持离线。当前助手需要Python>=3.10；纯阅读写作不依赖Python。R、Julia、Node、LaTeX、设备及其他运行时由宿主按真实任务准备。

`runtime.python_groups`选择最小配方，`runtime.packages`可补充依赖。配方只是起点，以所选上游的实际接口为准；需要源码构建或复杂约束时直接使用其既有安装方式。系统提权、付费资源与私有材料外发按实际权限处理。

准备后先做一次针对性导入/小例验证，再执行研究。失败时修复具体问题或换合适实现；只暂停依赖失败环境的部分。保留实际版本、关键命令和失败信息，安装成功不替代结果检验。

可选 `environment.py plan/doctor/run` 提供只读检查及验证后运行本地Python脚本。无须每次都执行四个子命令；一般直接ensure即可。运行日志中的版本快照不是完整依赖锁。
