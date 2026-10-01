# 工具按需

当前Agent已有工具足够时直接使用。环境准备沿用environment-setup.md所述真实项目工具，专业方法沿用protocol.md。动态来源遵守provider-policy.md，完整研究先用research-quality.md和research-lifecycle.md。

可选scripts/research31.py提供指定来源封装与记录检查；它不启动模型、不认证科学质量、不要求每段写JSON。旧结构工具仍可用于明确的工程复现，但不把兼容性、多宿主benchmark当正式研究前置。

`environment.py`提供动态资源检查、实际后端小计算校准，以及任意语言/专业工具的项目argv执行；步骤与输出验收见`environment-setup.md`和按需`research-tools.md`。API/CLI优先，GUI使用宿主已有自动化并以真实项目/求解输出核验。科研模型和当前executor分别配置，免费依赖可在项目环境准备。读取指导、实施研究与运行函数分别记录，角色比较见provider-policy.md。
