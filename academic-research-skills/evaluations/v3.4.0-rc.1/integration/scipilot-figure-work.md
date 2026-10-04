## SciPilot：选图、核验与导出

论证目标是过期拒绝与活动接受。先运行 profile_data.py，再选择两个横条计数面板，零基线、direct labels；不画均值误差棒或显著性。备选为2×2数值表或12试验标记矩阵；计数条图用于快速对照且配表保留每次真实事件。

按 general 规范调用 setup_style、audit_layout、render_preview，目视检查实际PNG后调用 export_figure 得到PDF/SVG/300DPI PNG与灰度图。程序报告x轴标签可能裁切；短化标签后警告仍存在。实际导出使用tight边界，目视检查两张预览与最终PNG：标题、数值、零刻度与轴标签完整，未遮数据；警告保留，不伪称机器无警告。灰度依靠分组标签/数值而非只靠颜色。figure-values.json与原CSV一致。

图注：同一台Mac的12个配对软件场景，每格6次。横轴为实际启动数；没有推断统计误差棒。过期control为0/6，活动control为6/6。输出只支持此测试范围。

