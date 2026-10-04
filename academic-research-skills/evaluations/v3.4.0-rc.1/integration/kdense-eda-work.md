## KDense：数据剖析与决策

运行 tabular_profile.py 处理 launch-results.csv 的24条真实记录，产生 kdense-profile.json。trial 是配对调用标识，不是连续生物学变量；started 是二元软件事件；wall_seconds 是启动开销，受机器/启动顺序影响，不作性能优越性推断。CSV没有缺失值；6个过期状态与6个活动状态各有direct/control两行。该入口只完成CSV核心剖析，不宣称所有科学格式兼容。

