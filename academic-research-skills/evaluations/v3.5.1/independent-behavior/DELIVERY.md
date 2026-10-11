# 已完成的交付

中文短论文草稿：manuscript.md。比较图：comparison.svg（可编辑）与comparison.png（300dpi）。完整数值：results.json、errors-and-fits.csv；说明：analysis-report.md。

在本目录使用已有bundled Python运行analysis.py复算（依赖numpy）；运行draw_comparison.py --final重绘（依赖Pillow与现有Arial字体）；使用系统Python运行verify_results.py作独立标准库Fraction核验。环境及输入/代码哈希见analysis-environment.json。

结果：A/B MAE=0.925/0.450；B低51.35%；分别e_A=0.30+0.05×scale、e_B=0.20+0.02×scale，R²均1。该材料为软件测试数据，结论仅限这24条记录。

阶段原总预算保留；原失败和新增matplotlib缺失记录均保留。动作、来源、耗时、范围与未完成事项见behavior-report.md；复算和反方审查见verification.json、critical-review.md。四个专业步骤均有来源前置、实施和finish/check收据。本交付是描述分析、比较图和中文短论文草稿，不是投稿就绪认证。
