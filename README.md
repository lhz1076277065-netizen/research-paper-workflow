# Academic Research Skills

Version **3.1.1** is a complete, discipline-neutral library: one optional research orchestrator and eighteen independently usable specialist Skills. It preserves sixteen extensible research profiles, a `general` default and the user's thirteen external professional source repositories. Use a focused Skill for a focused request; developing this library produces Skill files and validation, without starting a research project.

The complete source lives in [academic-research-skills/](academic-research-skills/). Runtime and source ZIPs are published in [GitHub Releases](https://github.com/lhz1076277065-netizen/research-paper-workflow/releases). Start with its [中文说明](academic-research-skills/README.zh-CN.md), [English guide](academic-research-skills/README.md), or the chosen `skills/<capability>/SKILL.md`.

## Install

Use the existing Codex installer to install one capability from this repository:

```bash
python "$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py" --repo lhz1076277065-netizen/research-paper-workflow --path academic-research-skills/skills/research-paper-workflow
```

Replace the path's final name with the capability you need, for example `journal-intelligence` or `scientific-visualization`. Installing all nineteen is optional. Restart Codex to refresh its native Skill catalog. Other Agents may load a selected folder or use the library's documented export tools; file loading is distinct from native automatic routing.

The previous installation path `research-paper-workflow/` also contains the current complete orchestrator. Its old v2 helpers, nine legacy validator profiles and project experiments are preserved for existing consumers; [LEGACY_HELPERS.md](research-paper-workflow/LEGACY_HELPERS.md) explains their separate scope. Avoid installing both copies of the same orchestrator name.

## Use and verification

Ask `$journal-intelligence` to match journals, `$manuscript-writing` to edit the supplied text, or `$research-paper-workflow` to pursue a complete authorized research project. The current Agent uses its existing model, chooses necessary professional implementations and preserves the actual scientific objective. Native internal delegation is optional. Optional record checkers verify artifact identity and applicable completion; they do not certify scientific quality.

v3.1.1 fixes five reproduced record issues: factual-review types, reviewed manuscript version, assistant scope versus ordinary action names, literature/reading/novelty input association and prospective protocol delivery. See [MIGRATION.zh-CN.md](academic-research-skills/MIGRATION.zh-CN.md) and [UPDATE_REPORT.md](academic-research-skills/UPDATE_REPORT.md).

```bash
python academic-research-skills/scripts/build_release.py --check
python -m unittest discover -s academic-research-skills/tests -v
python academic-research-skills/scripts/selftest.py --out /tmp/academic-skill-smoke
```

Local v3.1.1 regression: **503 passed**, plus four basic and seven manufactured scientific smoke checks. Read the [actual test summary](academic-research-skills/test-results/SUMMARY.json) for scope and limitations. Native behavior and content quality require separate evidence. Existing root tests and CI retain the legacy helpers and additionally check the complete library; the unrelated experiment trigger is unchanged.

## License

MIT. External professional sources retain their own licenses and are discovered on demand; their complete code is not bundled here.
