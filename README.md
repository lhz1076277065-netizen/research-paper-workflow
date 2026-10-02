# Academic Research Skills

Candidate **3.3.0-rc.4** audits the complete Skill route, preserves contribution search and fixes scope, stopping and manuscript-entry conflicts. One optional orchestrator and eighteen independent specialists remain available. This release uses text and engineering acceptance; research case validation is not a release prerequisite.

The complete source lives in [academic-research-skills/](academic-research-skills/). Runtime and source ZIPs are published in [GitHub Releases](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases). Start with its [中文说明](academic-research-skills/README.zh-CN.md), [English guide](academic-research-skills/README.md), or the chosen `skills/<capability>/SKILL.md`.

The [route acceptance report](academic-research-skills/evaluations/v3.3.0-rc.4/ROUTE-AUDIT.zh-CN.md) records the reviewed instructions, corrections and five required mechanisms. Earlier evaluation archives remain development material and do not certify general originality or publication.

## Install

### 一句话让 AI Agent 安装

> 请按照 https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.3.0-rc.4 中的部署教程，将全部19项通用学术Skill安装到本机Codex，核验安装包SHA256、备份同名旧版，并在安装后报告实际路径、版本和检查结果。

[完整中文教程](academic-research-skills/INSTALLATION.zh-CN.md) · [macOS 一键安装包](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/download/v3.3.0-rc.4/academic-research-skills-v3.3.0-rc.4-one-click.zip) · [后续发行要求](installation/RELEASE_CHECKLIST.zh-CN.md)

本次 SHA256 以发行页的校验文件为准；安装器绑定实际日常包摘要。文件安装检查与宿主实际加载分别确认。

Use the existing Codex installer to install one capability from this repository:

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" --repo lhz1076277065-netizen/research-paper-workflow --ref v3.3.0-rc.4 --path academic-research-skills/skills/research-paper-workflow --dest "$HOME/.agents/skills"
```

Replace the path's final name with the capability you need, for example `journal-intelligence` or `scientific-visualization`. Installing all nineteen is optional. Codex detects local Skill changes; restart it if new Skills do not appear. Other Agents may load a selected folder or use the library's documented export tools; file loading is distinct from native automatic routing.

The previous installation path `research-paper-workflow/` retains its compatibility copy and old v2 helpers, nine legacy validator profiles and project experiments for existing consumers. For this update use `academic-research-skills/skills/research-paper-workflow`; [LEGACY_HELPERS.md](research-paper-workflow/LEGACY_HELPERS.md) explains the preserved helpers. Avoid installing both copies of the same orchestrator name.

## Use and verification

Ask `$journal-intelligence` to match journals, `$manuscript-writing` to edit the supplied text, or `$research-paper-workflow` to pursue a complete authorized research project. The current Agent uses its existing model, chooses necessary professional implementations and preserves the actual scientific objective. Native internal delegation is optional. Optional record checkers verify artifact identity and applicable completion; they do not certify scientific quality.

The stable interface includes six separate research dimensions, fourteen on-demand computational routes, discriminating experiments, project-environment tool execution and local research-model evaluation. Result auditing checks declared numeric/semantic occurrences and render dependencies, while three lightweight queues keep research and artifact progress moving during external waiting. See [migration](academic-research-skills/MIGRATION.zh-CN.md), [file changes](academic-research-skills/UPDATE_REPORT.zh-CN.md) and [candidate validation](academic-research-skills/evaluations/v3.3.0-rc.4/VALIDATION.zh-CN.md). Earlier reports and source diffs remain in the source package only.

```bash
python academic-research-skills/scripts/build_release.py --check
python -m unittest discover -s academic-research-skills/tests -v
python academic-research-skills/scripts/selftest.py --out /tmp/academic-skill-smoke
```

Read the [actual test summary](academic-research-skills/test-results/regression.json) and [candidate validation report](academic-research-skills/evaluations/v3.3.0-rc.4/VALIDATION.zh-CN.md) for engineering, actual digital operations and native output-review scope. Tests and development examples do not certify originality or publication quality. Existing root tests, legacy helpers and unrelated experiments are preserved; release manifests bind exact source commit and file hashes.

See [supported platforms and semantic scope](academic-research-skills/docs/COMPATIBILITY.zh-CN.md). macOS ARM64 installation and Linux engineering CLI have evidence; other native hosts/platform installations are unverified. Historical releases remain available for rollback.

## License

MIT. External professional sources retain their own licenses and are discovered on demand; their complete code is not bundled here.
