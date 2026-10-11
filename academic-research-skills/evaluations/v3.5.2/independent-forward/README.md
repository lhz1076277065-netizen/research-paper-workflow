# 验收交付
本次是本地合成软件夹具的资料访问、容量限制和预测比较，没有完成科研论文。
- 主结果：analysis-report.md；数值results.json；逐条预测predictions.csv。
- 复算：python3 analyze.py；资料输入derived/observations.csv；无需网络或额外库。
- 专业来源：data-start/data-finish/data-work与analysis-start/analysis-finish/analysis-work；均完成真实begin、读取、实施、finish/check。
- 访问：自主接受常规免费本地条款并登录取得token；token仅在子进程环境，未写入源码、参数、日志或交付。acquire.py是可审计取得过程，重跑会拒绝覆盖已有材料，复算不用重复下载。
- 服务只提供整包，受管资料下载2307bytes；只解压202bytes observations.csv，无关other-region.bin（展开2,000,000bytes）未解压。
- 元数据681bytes和会话响应59bytes是有界探测/鉴权，自写请求单列access-log；全部响应实际3047bytes。storage收据2307bytes仅代表受管资料传输，初始历史preplan_download_bytes保持null。不会声称脚本自动拦截所有HTTP响应。
- 空间计划400000bytes，限制512000bytes，阶段预算由总8分钟扣除最初约1分钟指导读取后登记7分钟，未重置阶段与配额。未验证宿主token计量。
- linear validation MAE/RMSE=0/0，constant=24/24.241837，估计仅开发1–18，19–24保留最终评价。
- 数据为精确合成序列，验证区间为外推；未检验真实抽样独立性，不作总体推断、p值、CI或因果结论。
- 实際障碍：第一次数据收据CSV对应摘录小于8字符导致check拒绝，补成真实跨行摘录后通过；PNG转换缺cairosvg，用已有Pillow绘制实际查看，无新增下载；中文临时stdin发生编码错误，使用已有明确Python3.12重试解决。
