> 仅在主动选择结构化交接或兼容旧脚本时阅读。普通科研任务直接按当前目标执行；动态来源见 references/upstream.md。

# 独立使用与可选脚本

最小使用方式是让宿主读取本目录的 `SKILL.md`，提供自然语言目标和材料。无须安装总控或其他模块，也无须先生成全项目状态。需要的参考、模板和脚本都在本目录内部。

下面命令从本 Skill 文件夹执行，使用 Python 3.10 或更新版本；三个运行脚本仅依赖标准库。宿主没有 Python 时，仍可按本地协议完成研究并提供实际产物，明确没有执行脚本检查。

```bash
python scripts/init_run.py /path/to/new-run --request "此次实际任务"
python scripts/validate_run.py /path/to/new-run
```

第二条只能检查已初始化结构。它不表示研究完成。所有输出起初是 planned、所有门槛是 unknown。

完成真实工作后，登记本次目录内的真实文件。例如，`--role` 必须替换为 `assets/contract.json` 中对应的逻辑交付角色；文件名可以与角色不同。

```bash
python scripts/register_artifact.py /path/to/new-run \
  --path outputs/actual-output.md --id ART-001 --role ROLE_FROM_CONTRACT
```

脚本计算真实 SHA-256，登记文件和匹配输出；不会替你判定质量门槛或把运行状态改成 completed。先登记被依赖的对象，再登记引用它们的产物。原始数据不要为满足脚本而复制到不获准的目录。

使用 `assets/record.template.json` 建立实际任务记录，一行一个 JSON 写入 `assets/contract.json` 的 records_file。模板中的 null 必须根据实际工作填写或解释，不得把空模板标成 observed。来源、门槛理由与范围由实际证据填充。完成所有约定交付后再执行：

```bash
python scripts/validate_run.py /path/to/new-run --completion \
  --report /path/to/new-run/structural-check.json
```

## 状态与完成范围

`run.json` 的 schema_version 是数据契约版本；Skill 包 metadata.version 是发行版本，二者有意分开。`completed` 仅表示本次 scope 的约定产物和记录完成。允许用户仅要求某一章节、仅基于摘要初筛或仅寻找数据候选；应把不适用的交付设为 required=false，并写明用户范围与原因，不能删去交付声明或偷改科学标准。关联门槛可记录 not_applicable，但必须有理由和范围证据。

## 校验器能做与不能做

能做：本包使用的 JSON Schema 子集、必需字段、枚举、唯一对象 ID、文件存在与 SHA-256、相对路径边界、产物依赖引用和循环、声明的输出与门槛、完成状态的记录一致性。

不能做：实际访问 DOI/API、判断引用是否支持论断、认证数据真实性、决定统计识别是否成立、看懂图表、核验人类签名和伦理证明、判断抄袭、检测 AI 作者、保证论文录用。即便全部脚本通过，也需要执行协议规定的视觉、语义与科学检查。

本校验器不是通用 JSON Schema 引擎；它对使用到的未支持关键词报错。要扩展 schema，应同步测试，不得把完整 JSON Schema 的支持能力归给本脚本。

## 文件与并行安全

初始化拒绝覆盖已存在的目录。登记脚本采用本机独占锁和原子替换；它不是跨服务事务系统。所有写入者必须遵守同一约定。最稳妥的默认是每个任务独立目录，冻结输入只读，整合时核对 base_revision；不要让多个执行过程任意直接修改同一个 run.json。

只声明本次真正运行过的检查；未运行的测试和外部依赖分别记录。不得为了绿色状态修改科学事实。
