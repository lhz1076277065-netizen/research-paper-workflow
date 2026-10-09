# v3.5.0 论证主线与兼容验收

本轮从v3.4.1维护源更新19项独立能力，将真实缺口→既有局限/竞争解释→贡献与判别证据→新认知及边界连接到选题、设计、研究、图表、写作与复核。沿用路线板与当前专业调用输入，结果可否定原主张；不新增固定图数、段数、评分器或全稿审批材料。仅维护本Skill，不读取、修改、恢复或消息触达原测试会话，不继续其科研课题。本轮没有新GitHub发布。

## 最终工程检查

- Python3.12.14/macOS ARM64主回归693项：0失败、0错误、0跳过，逐项结果在engineering/regression.json与.txt。原686项及7项空delivery出口回归均通过。
- 根目录兼容测试30项通过，见engineering/compatibility.txt；19入口官方quick_validate通过，见engineering/entry-validation.json。1120项生成资源一致，根目录兼容副本同步；19入口均小于800字符。
- 14个来源、23个固定入口、413条源文件绑定（404份不同仓库/commit/路径文件）离线逐Git blob核验通过，见source-integrity.json。代码、schema与来源身份的范围见engineering/interface-equivalence.json；除发行版本外，仅修复空delivery专业出口，不新增CLI或收据schema。
- 便携自检通过，见engineering/portable-selftest.json。系统skill-creator校验器缺PyYAML时，仅临时目录加载其依赖完成校验，未给科研Skill增加项目依赖。

本轮没有重新执行Linux CI、14仓库全部原生功能或真实论文生命周期。旧版本Linux与逐库有限集成仍是v3.4.1及rc.1/rc.2的历史证据，不能重标为新验证。

## 独立行为与实际产物

局部首测实际调用K-Dense scientific-writing与anti-defensive-writing，保持高湿稳定性、保护层效果和机制待验证，未承诺Nature录用；专业产物和close在182秒完成，但完整记录首次保存241秒，严格4分钟总限超约1秒。该失败保留在focused-edit，不能计为时间达标。随后明确准备与最终交付也计入预算、init传真实剩余额度、close前存必要交付说明。

第二次独立局部请求在166秒内保存全部文件、记录及close，连同交付在4分钟内；两项真实来源begin/read/apply/finish/check通过。147字方案段未编造唯一失效原因、20%提升或行业改写，没有追加检索或实验。见focused-repeat/final.md、evaluation-report.md及实际指导哈希。

完整小型合成流程完成六项必要专业步骤：接入、设计、真实算术分析、写作、最终表达与focused复核；均有源先调用和实际输出。A汇总75.83%高于B32.5%，但easy为90%<95%、hard为5%<20%，共同50/50权重为47.5%<57.5%。原始四行没有删选，反例实际否定“汇总优势代表所有工况更优”，结果改变主张并结束扩展。见full-flow/report.md、analysis.py、results.json、review.md及逐步收据。

该独立完整流程不能记为全绿：可选绘图因matplotlib缺失取消，未生成图片；完成型close遭遇空交付阶段无新专业pair而被拒，最终route_closed并保留障碍；记录助手的来源路径、引号、stdout解析错误均保留。登记计时402.9秒，但首次预读起点未准确保存，严格端到端8分钟达标保持未知，不以phase数字替代。没有token计量认证。

## 验收发现的代码修复

空delivery只有整理已核验产物，却被要求重复专业调用。修复后，仅full+delivery、无任何未取消未消费登记、存在刚完成的manuscript阶段及已消费记录时，才可先核原始begin/finish文件SHA256，再F.check真实来源、输入、输出、工作报告及当前phase/指令后完成。其它阶段、部分pairs、未知旧历史、编辑或删除产物、遗留步骤仍拒绝；原截止、暂停/终止、进程所有权检查保留。新增七项实际文件与状态测试，独立代码审查发现旧begin合法JSON改指令可绕过关联；新增原始文件摘要绑定，缺失旧身份保持未知，该攻击及旧身份缺失在修复前复现失败、修复后通过。静态及代码审查范围分别记录。

修复后另做真实固定来源CLI五阶段合成自检，见empty-delivery-final/receipt.json及run_empty_delivery_smoke.py：五项来源工作、实际CSV计数、空delivery完成，无重复专业步骤，已完成后启动进程被拒，约1秒。它是软件流程验证，不是第二次独立科学论证或完整绘图验收；原独立失败状态没有被改写或复活。

## 交付边界

维护源、生成能力及验收档案随源码包交付；运行包不带测试答案。最终源码提交后制作同一commit的运行/源码/一键ZIP并核摘要与CRC；安装器隔离检查、本机19项替换与备份身份另由交付目录的INSTALLER-SELFCHECK.json和DELIVERY-RECEIPT.json记录，本报告不提前认证这些后续动作。

这些证据证明有限工程与行为范围，不能保证长期自主研究质量、创新性、所有原生依赖或顶刊录用。四段论证的官方出处及适用范围见OFFICIAL-BASIS.zh-CN.md；前作能力、未知机制、零结果与研究边界仍需真实专业核验。
