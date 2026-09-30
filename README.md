# Academic Research Skills

Version **3.2.0-rc.3** is the complete release candidate of this discipline-neutral library: one optional research orchestrator and eighteen independently usable specialist Skills. Stable **3.1.1** remains available in [Releases](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases/tag/v3.1.1). The library preserves sixteen extensible research profiles, a `general` default and the user's thirteen external professional source repositories. Use a focused Skill for a focused request; developing this library produces Skill files and validation, without starting a research project.

The complete source lives in [academic-research-skills/](academic-research-skills/). Runtime and source ZIPs are published in [GitHub Releases](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases). Start with its [中文说明](academic-research-skills/README.zh-CN.md), [English guide](academic-research-skills/README.md), or the chosen `skills/<capability>/SKILL.md`.

## Install

Use the existing Codex installer to install one capability from this repository:

```bash
python "$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py" --repo lhz1076277065-netizen/research-paper-workflow --ref v3.2.0-rc.3 --path academic-research-skills/skills/research-paper-workflow
```

Replace the path's final name with the capability you need, for example `journal-intelligence` or `scientific-visualization`. Installing all nineteen is optional. Restart Codex to refresh its native Skill catalog. Other Agents may load a selected folder or use the library's documented export tools; file loading is distinct from native automatic routing.

The previous installation path `research-paper-workflow/` retains its rc.1 compatibility copy and old v2 helpers, nine legacy validator profiles and project experiments for existing consumers. For this update use `academic-research-skills/skills/research-paper-workflow`; [LEGACY_HELPERS.md](research-paper-workflow/LEGACY_HELPERS.md) explains the preserved helpers. Avoid installing both copies of the same orchestrator name.

## Use and verification

Ask `$journal-intelligence` to match journals, `$manuscript-writing` to edit the supplied text, or `$research-paper-workflow` to pursue a complete authorized research project. The current Agent uses its existing model, chooses necessary professional implementations and preserves the actual scientific objective. Native internal delegation is optional. Optional record checkers verify artifact identity and applicable completion; they do not certify scientific quality.

v3.1.1 fixes five reproduced record issues: factual-review types, reviewed manuscript version, assistant scope versus ordinary action names, literature/reading/novelty input association and prospective protocol delivery. v3.2.0-rc.1 established navigation and professional handoffs; rc.2 added resource freezing, transferable reasoning examples and reader-directed evidence revision. v3.2.0-rc.3 binds selected upstream dependencies and an exact reviewed local adaptation, aligns source dates and definitions, strengthens reader comparisons, and distinguishes numerical magnitude, direction and conditions in final expression. The nineteen short entry bodies remain unchanged. See [MIGRATION.zh-CN.md](academic-research-skills/MIGRATION.zh-CN.md), [UPDATE_REPORT.zh-CN.md](academic-research-skills/UPDATE_REPORT.zh-CN.md) and [source changes](academic-research-skills/source-diffs/README.zh-CN.md).

```bash
python academic-research-skills/scripts/build_release.py --check
python -m unittest discover -s academic-research-skills/tests -v
python academic-research-skills/scripts/selftest.py --out /tmp/academic-skill-smoke
```

Local candidate regression: **517 passed**, nineteen structural checks, seven manufactured scientific smoke checks and a consistent 797-file build. Read the [actual test summary](academic-research-skills/test-results/SUMMARY.json) for scope. Nine fresh comparison tasks, one old-material context with four focused operations, six continuations within existing task contexts and three anonymous content reviews are reported in the [quality evaluation](academic-research-skills/evaluations/results/QUALITY_REPORT.zh-CN.md). The candidate has bounded gains in proof conditions, explicit figure comparisons, and actual introduction shortening; core evidence and computations are comparable across the three arms. Loading burden is mixed. The intake capability was not exercised, and native automatic Skill discovery, universal scientific improvement and measured token/cost benefits are not established. Prior rc.2 evaluation records are retained separately. Existing root tests, legacy helpers and unrelated experiment files remain intact. Current release identity and remote CI are verified in the release publication receipt.

## License

MIT. External professional sources retain their own licenses and are discovered on demand; their complete code is not bundled here.
