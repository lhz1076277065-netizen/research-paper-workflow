# Research Paper Workflow Skill

A discipline-neutral Codex skill that directs an agent to create a complete, evidence-based scholarly paper. It moves from available research materials through evidence generation, experiments or analyses, full manuscript writing, artifact production, revision, and final validation.

## Install

Install from this GitHub repository with the Codex skill installer:

```bash
python "$CODEX_HOME/skills/.system/skill-installer/scripts/install-skill-from-github.py" --repo lhz1076277065-netizen/research-paper-workflow --path research-paper-workflow
```

On Windows PowerShell:

```powershell
python "$env:CODEX_HOME\skills\.system\skill-installer\scripts\install-skill-from-github.py" --repo lhz1076277065-netizen/research-paper-workflow --path research-paper-workflow
```

Restart Codex after installation.

## Use

Invoke the skill with:

```text
Use $research-paper-workflow to use these project materials to write and validate a complete scholarly manuscript.
```

The primary output is the actual editable manuscript and its supporting artifacts, not only a review, plan, or readiness report.

## What It Does

- Inspect and organize real project materials.
- Retrieve literature and execute feasible analyses or experiments needed by the claims.
- Write the complete title, abstract, main text, declarations, captions, and references.
- Generate and connect figures, tables, supplements, and reproducibility artifacts.
- Revise the manuscript directly until the evidence, argument, and files are consistent.
- Build a claim-evidence ledger for all major claims.
- Require traceable evidence, data sufficiency rationale, experimental validity, uncertainty, limitations, and reproducibility.
- Prevent fabricated evidence and unsupported claims.
- Run final acceptance only after the manuscript has been produced.

## Repository Layout

```text
research-paper-workflow/
  SKILL.md
  agents/
    openai.yaml
  references/
    research-quality-gates.md
    experiment-workflow.md
    manuscript-workflow.md
    final-acceptance-checklist.md
```

## License

MIT License.
