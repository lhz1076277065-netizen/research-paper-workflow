---
name: research-paper-workflow
description: Discipline-neutral workflow for high-standard SCI-style academic research articles. Use when Codex needs to plan, audit, execute, repair, or validate scholarly paper work involving research questions, evidence standards, data sufficiency, experimental design, result traceability, manuscript writing, submission readiness, revision responses, or a not-ready decision.
---

# Research Paper Workflow

Use this skill to move an academic article from research intent to an evidence-bound manuscript. Keep the workflow discipline-neutral. Do not introduce field-specific thresholds, journal rules, datasets, tools, or claims unless the user supplies them or they are verified from project materials.

## Operating Rules

- Inspect available materials first: manuscript files, data, code, logs, notebooks, protocols, results, figures, tables, supplements, references, submission files, licenses, and prior reviewer or editor messages.
- Build a claim-evidence ledger before judging readiness. Each major claim needs a source, method, data basis, analysis or experiment, result artifact, uncertainty or limitation, and manuscript location.
- Treat unrun experiments, missing data, inaccessible files, broken scripts, undocumented preprocessing, and unverifiable outputs as gaps, not as completed work.
- Never fabricate experiments, data, citations, benchmark results, statistics, authorship information, permissions, ethics approvals, availability statements, or submission readiness.
- Use "ready", "submission-ready", "publishable", or equivalent conclusions only when all applicable hard gates pass. Otherwise state "not ready" and provide concrete repair steps.
- Keep writing proportional to evidence. Downgrade the title, abstract, contribution list, and conclusions when the evidence supports a narrower claim.
- Preserve negative results and failed attempts when they affect validity, scope, reproducibility, or claims.

## Workflow

1. **Define the research contract**
   - State the problem, research questions, hypotheses or objectives, target contribution type, intended audience, and non-goals.
   - Convert each proposed contribution into a testable claim.

2. **Audit evidence and gaps**
   - Create the claim-evidence ledger.
   - Read `references/research-quality-gates.md` for data, evidence, validity, reliability, ethics, and reproducibility gates.
   - Classify each claim as supported, partially supported, unsupported, contradicted, or unverifiable.

3. **Plan or verify experiments**
   - Read `references/experiment-workflow.md` when designing, running, rerunning, or auditing empirical, computational, theoretical, simulation, laboratory, field, clinical, observational, qualitative, or review-based evidence.
   - Require baselines, controls, uncertainty, robustness, error analysis, and traceable result generation where applicable.

4. **Write or repair the manuscript**
   - Read `references/manuscript-workflow.md` before drafting, revising, shortening, expanding, or aligning the manuscript.
   - Ensure the title, abstract, introduction, methods, results, discussion, conclusion, declarations, figures, tables, and supplements all match the verified evidence.

5. **Perform final acceptance**
   - Read `references/final-acceptance-checklist.md` before declaring readiness or preparing submission files.
   - Produce a final decision with passed gates, failed gates, remaining risks, and exact next actions.

## Claim-Evidence Ledger

Use a compact table with these columns when auditing or planning:

`Claim | Evidence source | Data/material basis | Method or experiment | Result artifact | Uncertainty or limitation | Manuscript location | Status | Required fix`

Statuses:

- `supported`: evidence is real, traceable, sufficient, and accurately represented.
- `partial`: evidence exists but scope, uncertainty, controls, or reporting are incomplete.
- `unsupported`: no adequate evidence exists.
- `contradicted`: available evidence conflicts with the claim.
- `unverifiable`: files, logs, data, scripts, or provenance are missing or inaccessible.

## Output Standard

- Start with the decision state: `ready`, `not ready`, or `ready only after minor fixes`.
- Report the highest-risk blockers first.
- Separate evidence-backed findings from assumptions.
- Give executable next steps, including what to run, inspect, rewrite, collect, or disclose.
- When writing manuscript text, avoid hype, unsupported novelty language, and claims that exceed the verified result boundary.
