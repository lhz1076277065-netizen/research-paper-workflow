# 工具按需

每个专业步骤先执行[必调流程](mandatory-professional-flow.md)，调用、读取并实施14库内匹配入口，再使用当前Agent已有工具完成实际工作。环境准备沿用environment-setup.md，专业方法按所调用来源及protocol.md实施；完整研究先用research-quality.md和research-lifecycle.md。

`professional_flow.py begin/finish/check` 是当前专业步骤的必调工具；`phase_control.py` 用于完整研究、显式预算与长任务。可选 `research31.py` 保留sources/select/upstream/assess及旧记录检查，不代替必调流程，也不要求每段写JSON。旧结构工具用于有明确需要的工程复现，不把多宿主benchmark当正式研究前置。

`environment.py`提供动态资源检查、实际后端小计算校准，以及任意语言/专业工具的项目argv执行；步骤与输出验收见`environment-setup.md`和按需`research-tools.md`。API/CLI优先，GUI使用宿主已有自动化并以真实项目/求解输出核验。科研模型和当前executor分别配置，免费依赖可在项目环境准备。读取指导、实施研究与运行函数分别记录，角色比较见provider-policy.md。
