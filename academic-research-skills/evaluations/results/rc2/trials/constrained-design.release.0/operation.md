# 操作说明

- 输入仅为指定 constrained-design.release.0.json 的提示、合成材料、初始 Skill 文本及其相关路径。共同配置用于确定共享 Python 路径；未读取其他组、旧成果、评审或 suite.json。
- 使用 research-design 3.2.0-rc.2。实际经 run_host.py read 读取并记录 research-quality、provider-policy、execution-handoff、protocol、method-routing 五个相关参考，身份记录在 resource_reads.jsonl。初始已打包材料未再读原夹具；曾尝试将请求 JSON 作为 material 读取，工具返回 Resource outside frozen materials，未声称该调用成功。
- 以当前宿主、当前模型独立推导并写入 answer.md；未调用其他助手、模型或子代理。无需外部专业来源、依赖安装、研究数据或实体实验。
- 使用共享 Python 的标准库运行 check.py，退出码为 0，结果保存在 check_output.json。复核包括两个端点及 101 个相容参数点的全部约束、完整联合分布、B 的解、无效复制反例、独立复制公式及有限真值样本的保守区间计算。参数网格不替代 answer.md 中的解析证明。
- 真值购买、抽样和复制均为设计，尚未实施；没有真实结果。token、费用和峰值使用记录不可取得，保持未知。
