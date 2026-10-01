# 关键 primary 来源核对与审阅探针

以下均直接打开论文/作者全文或出版者原始记录；只核对决定方法差异的部分，不声称通读全部证明或穷尽先例。

| 来源与实际核对范围 | 核对结果及对匿名产物的含义 |
|---|---|
| [Tang, Chen, Li, Yu，2026，Online change point detection under heavy-tailedness and contamination](https://arxiv.org/html/2606.09737v1)：Definition 1、Assumption 1、§2.2 Algorithm 1、§S6.2 Algorithm S5。 | 逐时污染比例有上界、观察独立，污染分布可随时间变化；扫描多个前缀/近期尾部尺度。小样本用median，大样本用RUME，并设样本量及风险相关阈值。RUME将样本分半，在一半的数值轴找短覆盖区间，用另一半区间内值取均值。没有Q/R/S的时间连续块减法，也没有任务的None处理/固定64步MAD前缀。简单rolling median不是其完整方法。 |
| [Li与Yu，2021，Adversarially Robust Change Point Detection](https://papers.nips.cc/paper/2021/file/c1e39d912d21c91dce811d6da9929ae8-Paper.pdf)：§1.2 Assumption 1、§3.1、Algorithm 1。 | 离线多变点定位；动态Huber混合允许逐时任意污染分布且比例<1/2。ARC比较候选点左右块的RUME差，筛局部极大值。不是first stopping time；不能把其定位率或污染保证移植到删时间区间启发式。 |
| [Fearnhead与Rigaill，2019出版，Changepoint Detection in the Presence of Outliers](https://arxiv.org/html/1609.07363)：摘要、§2.1 Theorems 2.1–2.2及动态规划描述；另核对[出版者全文记录](https://doi.org/10.1080/01621459.2017.1385466)。 | 有界biweight损失和惩罚产生最小段长；连续同值异常长于该长度仍可能成段。不可把不封顶Huber损失等同其任意极端异常保护。它是支持短异常/短真段权衡已知的近邻，不是Q/R/S的完全相同统计量。 |
| [Zhang, Mei, Shi，2022，Robust change detection for large-scale data streams](https://bpb-us-e1.wpmucdn.com/sites.gatech.edu/dist/4/216/files/2022/05/p141.pdf)：引言、§2、§3.1–3.2。 | 目标已明确包括较小持续变化与较大短时异常。局部L-alpha CUSUM以密度幂差作增量，多流用shrinkage聚合，并分析误报breakdown。匿名产物未实现该密度变换/多流机制，也未证明其风险性质。 |
| [Lau与Tay，2019，Quickest Change Detection in the Presence of a Nuisance Change](https://arxiv.org/html/1902.03460)：§II–III。 | 四种已知分布描述关键/干扰变化顺序，window-limited SGLR在分子分母处理干扰；干扰可持续影响关键变化后的分布。一般干扰抑制和两阶段方案已有研究。单个短区间最坏删除没有实现该似然构造或继承其ARL/WADD结论。 |
| [Chen, Zuo, Veeravalli, Towsley，2024，Quickest Change Detection with Confusing Change](https://arxiv.org/html/2405.00842v1)：§IV Algorithms 1–2、式15–22。 | Successive CUSUM在第一统计量跨阈值后才启动区分bad/confusing分布的第二统计量；Joint CUSUM耦合和重置两者。T有明确的架构先例，区别为固定观察块确认、失败丢弃与缺失重置。不能以两阶段架构本身声称原创。 |
| [Xie, Moustakides, Xie，Window-Limited CUSUM](https://arxiv.org/html/2206.06777)：§IV式6–9、Remark 3。 | 滚动窗口估计未知post-change参数并用于递归CUSUM；论文也区分了已有窗口截断扫描。Q/R/S的窗口就是完整证据统计量，不能借窗口名称继承此论文理论。 |
| [Sokolov, Spivak, Tartakovsky，Detecting an Intermittent Change of Unknown Duration](https://arxiv.org/html/2210.17342)：§3、§4.3 FMA式23。 | 已有有限移动似然和与时长相关的风险/检测权衡。论文将短时变化当检测目标；匿名任务把短突发当干扰。修改其证据符号/删块用途可能有任务价值，仍须公平比较有效阈值。 |
| [Bhatt, Fang, Li，2022，Offline change detection under contamination](https://proceedings.mlr.press/v180/bhatt22a/bhatt22a.pdf)：§2 C1–C2、§2.1；核对[PMLR原始记录](https://proceedings.mlr.press/v180/bhatt22a.html)。 | 条件均值/二阶矩条件允许相关观察；污染对足够长子序列的比例有界，并限制利用完整数据蓄意藏变点的攻击。用影响函数稳健均值进行离线扫描。不是单个时间区间删除，不能省掉污染密度与弱对抗条件。 |
| [Zou, Fellouris, Veeravalli，2018修订，Quickest Change Detection under Transient Dynamics](https://arxiv.org/html/1711.02186)：摘要、§1–2。 | 暂态阶段是进入持续目标前的有用检测证据，返回原状态的突发不属于相同目标定义；D/WD-CUSUM的ARL/WADD结果不转用于本任务。 |
| [Lucas与Crosier，1982，Robust CUSUM](https://doi.org/10.1080/03610928208828414)：出版者摘要；未读全文。 | 原始摘要已有忽略首个疑似异常、连续异常才报警的修改CUSUM及污染正态ARL评价。仅支持“异常确认/连续证据思路已存在”，不据摘要判定与固定块确认完全等价。Page原文未另行通读；CUSUM递归以共用harness和上述顺序检测全文核对。 |

**结构区别的最小反例。** 给定8步证据`[1,0,1,0,0,0,0,0]`，至多2步连续删除最多删去1，剩余1；任意两个逐点删除可删去2，剩余0。同一数值集合重排成`[1,1,0,0,0,0,0,0]`后，连续删除也剩0。时间结构确实改变统计量，但这个例子只说明区别，不证明新颖或对实际污染的总体优势。动态Huber模型是分布级混合约束，也不能直接等同这个确定性逐点删除集合。

**独立机制探针（首次审阅）。** 在本目录以`PYTHONDONTWRITEBYTECODE=1 python3`直接加载四个`methods.py`，仅使用已有冻结参数和构造序列：

- 校准前缀为`[-1.,1.]*32`，因此center=0、scale=1.4826；对Q/R/S，在64个后续零之后加入其各自删除预算长度的`3*scale`突发，再接64个零，三者均返回−1。该探针只检查理想单突发性质。
- 同一前缀与64个零之后接200个`0.7*scale`：Q报警162，R返回−1，S报警157。与Q约0.6571、R约0.7071的已声明敏感度边界一致；不代表随机噪声中的检测概率。
- 对每项修订，用`prefix + [0.]*32 + [2*scale]*80 + [None]*20 + [0.]*40`的全部237个前缀，逐项核对完整序列报警应在足够长前缀保持、短前缀无报警；共948次断言通过。这不是复跑包内声称的数万次检查。
- 汇总JSON内部每组n、FA和加权mean_loss与总数一致。上述探针不等于参与者原检查脚本的全面复现。

**补齐原始包后的实际复现。** 最小脚本 [reproduce-review.py](reproduce-review.py) 读取本匿名目录，输出 [reproduction-results.json](reproduction-results.json)。运行：`PYTHONDONTWRITEBYTECODE=1 python3 reproduce-review.py`；使用环境已有NumPy 2.0.2，没有安装依赖。脚本使用harness的`evaluate`，不写参与者score日志；执行前后受审`methods.py`/`frozen.json`的SHA-256相同。

| 复现对象 | 实际结果 |
|---|---|
| 数据 | holdout 480例、240目标、每组120例；dev120例、60目标。ID各自唯一且无交集。holdout SHA-256=`b9a22153f1b505fff8920c140ae6615d9324d7a8ee477f8ee0a24c51287654fa`；dev=`bb3822e32f65cdfb5a3dfa08a517c5605d74d92e101a52bd2ebfbe2295c8907f`。 |
| 冻结方法原始留出行 | Q4、R5、S5、T4个变体，共8640行，与所供报告逐字段一致，包括报警、false_alarm、hit、delay、loss。R涵盖secondary_ablation，S涵盖ablation_comparator。所有总计、分组和均值也一致；不要求计时相同。 |
| 简单median对照 | `evaluation-functions.py`实际函数、所选window48/threshold4和480条原始行全部复现；mean_loss33.885416666666664、FA112、命中199。函数依赖固定prefix中位数/MAD及最近窗观察覆盖，没有实现2026 Algorithm 1的RUME与多尺度阈值。原16配置搜索日志未提供，未复核它的选择过程。 |
| 配对统计 | Q/R/T各4组、S5组，共17组：baseline/initial/ablation/median到refined，以及S同窗匹配消融。从按ID对齐的重跑行计算的均差、改善/恶化/并列数与摘要相同。 |
| bootstrap | 按`bootstrap-definition.json`独立计算差数组，NumPy default_rng seed50973，2000次各n=480有放回，quantile默认linear。17组的两个端点均与原摘要完全相同，并与提取的原`paired()`交叉核对一致。单位为流，未分层、未校正四项比较；复现并不验证生成分布或独立性假设。 |
| S同窗消融 | window48保持不变，只变erase0→8；loss47.025→24.866666666666667，下降22.158333333333335，区间[18.3,26.175]；160改善、181恶化、139并列。跨window48→32的下降24.65未作为单组件效果。 |
| 开发事件与选择 | 四项各40个dev事件，16/12/12分阶段，所有160事件的原始参数在同一dev数据上重跑，全部汇总指标相同。Q/T最后阶段11提案+1消融，R/S为10+2。冻结参数均可追到事件，并按照原文平局规则复现所选提案。R的3个训练事件数据未供，未复跑；所有日志未见holdout指纹。 |

此前“480条原始行和bootstrap定义缺失”的限制已解除。仍保留：训练数据、原诊断文件、历史方法快照、原检查脚本未供；score事件没有足以验证所有开发行为的可信时间链，不能排除未记录操作；生成器未核查，不能仅凭ID无交集确认概率独立。没有修改冻结提交，没有新选配置。主要结论与最近邻比较不因数值复现改变：机制实现和任务证据成立，发表原创性仍未建立。
