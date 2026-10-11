# 比较图方案

图1回答：在这些测试记录中B的绝对误差是否始终更小，其优势随scale如何变化？绘图专业调用在正式绘制之前开始；以已通过analysis检查的results.json、errors-and-fits.csv和analysis-report.md为输入。

已实际运行SciPilot profile_data.py，记录figure-data-profile.log。24行、无缺失；case_id为标识符，原脚本把数字ID报为连续变量，本任务不据此把ID作为预测量。scale为有序数值变量，绝对误差为连续变量；每个scale只有一个case，没有重复测量误差条的依据。

推荐：两面板，左侧展示全部A/B原始点及带截距OLS线，右侧展示全部配对差A−B和零基线。它保留全部记录，既呈现绝对水平又避免读者心算两线差值。备选为只用误差散点+回归线（更紧凑但差值需心算）；箱线+原始点可展示分布，但会压平scale关系，故不选。

期刊未指定；采用通用稿件7.2×4英寸，矢量SVG和300dpi PNG，英文轴标签配中文图注。输入物理单位未给，标CSV units；不虚构单位、置信区间或显著性星号。Okabe-Ito橙/蓝并用圆点/三角、实线/虚线冗余编码；差值用黑色；零起点、范围覆盖全部数据。误差线只画1—24，不做外推。

已验证bundled运行时缺matplotlib，故在SciPilot完整工作流内使用SVG绘制及同一图元的Pillow渲染作宿主适配，保留专业数据剖析、选图、形式检查、数值检查、灰度与实际看图闭环；不声称原生matplotlib或原生visual_qa函数已运行。
