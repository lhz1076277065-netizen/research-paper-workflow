# 分组事实纠正与主计划保持
2026-10-12T14:25Z：实际读取data-context.json和CV明细，发现前面短文本误把“4个总batch”写成“4个train/test共同batch且每批20/10”。真实分组：batch0 train30；batch1 train30；batch2 train20/test10；batch3 test30。原生audit的1个重叠token正确，先前environment-diagnosis.md声称原生漏报是代理误读；该历史错误保留并由本说明纠正。data-context.json实际生成的逐组计数一直正确。

原analysis-plan.md的4折/4测试批次、16符号排列不能按原数字执行：真实train LOBO为3折；测试批次只有2个，精确符号排列为4种。calibration.py动态使用真实train groups，因此主要计算已经正确8次拟合（3折×2+2最终），不是analysis-work.json中误写的10。原始计划和错误记录不覆写，冻结主CSV/模型/阈值/终点/选择保持不变。该修订纠正元数据误解，不因测试优势改变路线。

两测试批次不足可靠总体置信推断；10000次条件批次bootstrap仅作离散描述范围并以4种精确重采样核对，排除“95%CI=等效证明”的措辞。分别报告partial/shared batch2与unseen batch3，以澄清组合测试含两种场景。批次显著性仅描述交换符号，不声称随机化试验或有效总体p值。
执行预设中位数偏移、低高区间、影响点删除和完整复算，修订四段路线板的边界，不新增事后调参。
