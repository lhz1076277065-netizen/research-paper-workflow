# Research Paper Workflow Skill

A discipline-neutral Codex skill that directs an agent to create a complete, evidence-based scholarly paper. It moves from specialist knowledge acquisition and recent high-impact literature through current data, method-matched advanced analysis, publication-grade figures, full manuscript writing, language purification, and final validation.

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
Use $research-paper-workflow to produce a complete paper with current data, top literature, advanced analysis, publication-grade figures, and final audit.
```

The primary output is the actual editable manuscript and its supporting artifacts, not only a review, plan, or readiness report.

## What It Does

- Inspect and organize real project materials.
- Retrieve literature and execute feasible analyses or experiments needed by the claims.
- Prioritize directly relevant literature from the rolling five-year window and verify WoS Core Collection and JCR Q1/Q2 status.
- Audit data freshness, source coverage, integration quality, bias and frozen-release provenance.
- Build a domain knowledge map from standards, authoritative reviews, primary studies and official technical sources.
- Use SmartPLS or AMOS when the study genuinely requires PLS-SEM or CB-SEM, with complete measurement and structural-model diagnostics.
- Produce publication-grade vector or high-resolution figures instead of raw software screenshots.
- Write the complete title, abstract, main text, declarations, captions, and references.
- Generate and connect figures, tables, supplements, and reproducibility artifacts.
- Revise the manuscript directly until the evidence, argument, and files are consistent.
- Detect and rewrite formulaic AI-style phrasing, conversational explanation, promotional language, drafting notes, and other non-academic residue.
- Scan Markdown, text, LaTeX, HTML, and DOCX manuscript sources before final acceptance.
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
    literature-evidence-workflow.md
    data-currency-and-coverage.md
    domain-knowledge-integration.md
    advanced-analysis-and-figures.md
    manuscript-workflow.md
    manuscript-language-audit.md
    final-acceptance-checklist.md
  scripts/
    audit_manuscript_language.py
```

## License

MIT License.
