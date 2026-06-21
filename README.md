# Research Paper Workflow Skill

A discipline-neutral Codex skill for high-standard academic research article workflows. It helps audit and guide research questions, evidence standards, data sufficiency, experiment design, result traceability, manuscript writing, submission readiness, and not-ready decisions.

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
Use $research-paper-workflow to audit this academic manuscript from evidence to submission readiness.
```

## What It Enforces

- Inspect real project materials before judging readiness.
- Build a claim-evidence ledger for all major claims.
- Require traceable evidence, data sufficiency rationale, experimental validity, uncertainty, limitations, and reproducibility.
- Prevent unsupported "ready", "submission-ready", or "publishable" conclusions.
- Keep paper claims aligned with completed and verified work.

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
