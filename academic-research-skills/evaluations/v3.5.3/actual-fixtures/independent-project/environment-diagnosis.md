# 实际执行障碍与恢复
- 原生 K-Dense manifest 和 missingness/leakage audit 在默认Python3.9.6运行成功，记录在 actions.jsonl。
- eda_analyzer.py 原样运行失败：TypeError: zip() takes no keyword arguments，实际源码要求Python3.11+；未修改缓存、未安装包。
- 候选A：复用现有Python3.11；候选B：同入口按CSV规范编写最小标准库审计。A保持原生流程，成本较低，已发现 /Users/luca/.local/bin/python3.11 并实际重跑成功。
- manifest/EDA覆盖全部120行，未达到1000行上限。原生泄漏审计只报1个entity-token跨划分；人工标准库核验 batch=0,1,2,3 均跨train/test（4个）；以实际逐组计数为准，原始回执保留，不把审计工具输出当完整科学验证。
