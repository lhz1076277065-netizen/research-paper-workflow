---
name: research-paper-workflow
description: Use when Codex must create, write, complete, substantially revise, or finalize a full evidence-based scholarly article from research materials, data, code, analyses, experiments, literature, or an incomplete draft, including work requiring current comprehensive data, recent high-impact literature, advanced method-matched analysis, publication-grade figures, deep domain knowledge, removal of non-academic language, and complete submission artifacts.
---

# Research Paper Workflow

## Core Mandate

Produce the paper. The primary deliverable is a complete, editable, evidence-bound manuscript, not an audit report, outline, checklist, or readiness opinion.

Inspect first, then execute the work required to build the evidence and write the article. Do not stop after planning, gap analysis, literature mapping, experiment design, or manuscript review when the requested work can be completed with available tools and materials.

Keep the workflow discipline-neutral. Apply verified field or venue requirements only when supplied by the user or obtained from authoritative sources.

## Non-Negotiable Rules

- Write every manuscript section requested by the user and create the actual manuscript file in the requested or most practical editable format.
- Use real, traceable sources, data, methods, analyses, experiments, results, figures, tables, and citations.
- Never fabricate evidence, data, experiments, statistical outputs, citations, authorship, approvals, permissions, or availability.
- Execute feasible literature retrieval, data processing, analysis, computation, experiment, figure generation, and reference verification instead of merely recommending them.
- Use current, sufficiently comprehensive data and document its release, cutoff date, coverage, gaps and update check.
- Prioritize recent, directly relevant Web of Science evidence from verified JCR Q1/Q2 journals while preserving necessary foundational, standards and contradictory sources.
- Choose analysis software from the research design. Use SmartPLS or AMOS only when PLS-SEM or covariance-based SEM is methodologically appropriate and fully report the measurement and structural evidence.
- Generate publication-grade figures from frozen outputs; never use raw statistical-software screenshots as final scientific figures.
- Build a domain knowledge map from authoritative specialist sources before finalizing hypotheses, methods or interpretation.
- If an essential activity requires unavailable physical work, private data, credentials, ethics approval, author judgment, or other irreducible external action, complete everything else and mark only the affected claim or passage as unresolved.
- Keep claims proportional to completed evidence. Narrow the title, abstract, contribution statements, and conclusions when needed.
- Preserve negative findings and failures when they affect validity, scope, reproducibility, or interpretation.
- Remove conversational, promotional, formulaic, process-narrating, placeholder, reader-directed, and other non-academic language from the manuscript before delivery.
- Treat final acceptance as quality control after manuscript production, not as the main product.

## Required Workflow

1. **Define the paper contract**
   - Establish the research problem, questions or objectives, contribution type, audience, article structure, target length, output format, and supplied venue constraints.
   - Convert proposed contributions into testable claims and define the evidence each claim requires.
   - Choose a defensible narrower scope when the requested scope cannot be supported.
   - Read `references/domain-knowledge-integration.md`; create the domain knowledge map, terminology ledger, applicable standards list and mechanism alternatives.

2. **Inventory and organize the project**
   - Inspect manuscripts, notes, data, code, logs, protocols, results, figures, tables, supplements, references, licenses, and prior editorial material.
   - Create a claim-evidence ledger and an artifact inventory.
   - Identify missing evidence, broken pipelines, unsupported claims, and missing manuscript components.

3. **Build the literature and data evidence**
   - Read `references/research-quality-gates.md`.
   - Read `references/literature-evidence-workflow.md`; run a reproducible search, verify WoS/JCR metadata, and build the literature evidence matrix.
   - Read `references/data-currency-and-coverage.md`; update, integrate, audit and freeze a data release with an explicit cutoff date and coverage matrix.
   - Read `references/experiment-workflow.md` whenever evidence must be designed, generated, reproduced, repaired, compared, or analyzed.
   - Retrieve and verify literature, prepare data, implement or run methods, execute analyses or experiments, evaluate baselines and controls, quantify uncertainty, inspect failures, and freeze final outputs where feasible.
   - Record commands, versions, parameters, seeds, provenance, exclusions, and output paths.

4. **Run advanced analysis and generate figures**
   - Read `references/advanced-analysis-and-figures.md` before selecting analysis software or generating final figures.
   - Route the problem to SEM, regression, causal, multilevel, temporal, spatial, predictive, qualitative or another justified method family.
   - If SEM is justified, select SmartPLS for an appropriate PLS-SEM objective or AMOS/equivalent for an appropriate CB-SEM objective; complete all applicable measurement, structural, fit, prediction, invariance, uncertainty and robustness checks.
   - Generate publication-grade vector or high-resolution figures from frozen outputs and verify every plotted value.

5. **Produce the manuscript**
   - Read `references/manuscript-workflow.md` before drafting or substantially revising the paper.
   - Build a results-led detailed outline, then write the full title, abstract, keywords, main text, declarations, captions, references, and supplementary cross-references.
   - Write concrete scholarly prose from verified evidence. Do not leave section-level placeholders when source material is sufficient.
   - Generate tables and figures from frozen results and insert or call them out in sequence.
   - Create or update the editable manuscript file and any separate figure, table, supplement, data, code, or response files required by the task.

6. **Revise as an author**
   - Check argument continuity, methods reproducibility, result completeness, discussion depth, claim boundaries, citation support, terminology, notation, units, and cross-file consistency.
   - Repair weaknesses directly in the manuscript and supporting artifacts.
   - Repeat analysis or regenerate outputs when a writing inconsistency reveals an evidence problem.

7. **Run the manuscript language audit**
   - Read `references/manuscript-language-audit.md` and apply its complete rewrite protocol.
   - Run `scripts/audit_manuscript_language.py` against every final manuscript source file supported by the scanner.
   - Inspect every finding in context, rewrite the underlying sentence or paragraph, and rerun the scanner until no unresolved high- or medium-severity findings remain.
   - Perform the required manual semantic pass because pattern matching cannot determine authorship or detect every form of non-academic prose.
   - Preserve truthful, venue-required AI-use disclosure; remove AI-assistant conversation and drafting residue from the scholarly text.

8. **Validate the finished package**
   - Read `references/final-acceptance-checklist.md`.
   - Open and inspect every final file. Recompute or trace core results, verify citations and callouts, and visually inspect the rendered manuscript.
   - Fix all feasible defects before reporting status.
   - State `ready`, `ready only after minor fixes`, or `not ready` only after the completed manuscript has undergone final acceptance.

## Claim-Evidence Ledger

Maintain:

`Claim | Evidence source | Data/material basis | Method or experiment | Result artifact | Uncertainty or limitation | Manuscript location | Status | Required action`

Use `supported`, `partial`, `unsupported`, `contradicted`, or `unverifiable`. The ledger controls claim wording but does not replace manuscript writing.

## Deliverables

Unless the user explicitly narrows the task, deliver:

- a complete editable manuscript file, such as `.docx`, `.tex`, or a project-native source file;
- final title, abstract, keywords, main sections, declarations, captions, and references;
- generated figures, tables, and supplements required to support the paper;
- a literature search log and evidence matrix with recent-window, WoS and JCR verification;
- a data manifest, currency check, coverage matrix and frozen release identifier;
- a domain knowledge map, terminology ledger and standards record;
- complete analysis diagnostics and publication-grade figure source files;
- reproducibility or provenance artifacts needed to trace the reported results;
- a clean language-audit result or a documented, narrowly scoped rationale for any retained scanner false positive;
- a concise completion note listing files, validation performed, unresolved external dependencies, and final acceptance state.

Do not return only a plan, review, claim ledger, checklist, or list of suggested edits when manuscript production was requested.

## Completion Rule

Continue through domain learning, literature retrieval, data updating, evidence generation, advanced analysis, figure production, writing, revision, language purification, and validation within the available environment. Stop only when the requested manuscript and supporting artifacts have been produced and checked, all applicable quality gates pass, and the manual semantic pass finds no non-academic drafting residue, or when a genuinely external dependency prevents the remaining work. In the latter case, deliver the most complete defensible manuscript possible and identify the exact blocked passages, claims, and required external actions.
