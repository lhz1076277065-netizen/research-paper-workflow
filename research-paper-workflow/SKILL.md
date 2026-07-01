---
name: research-paper-workflow
description: Use when Codex must create, write, complete, substantially revise, or finalize a full evidence-based scholarly article from research materials, data, code, analyses, experiments, literature, or an incomplete draft, including tasks that require producing the manuscript, removing formulaic AI-style or non-academic language, and preparing supporting submission artifacts rather than only reviewing them.
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

2. **Inventory and organize the project**
   - Inspect manuscripts, notes, data, code, logs, protocols, results, figures, tables, supplements, references, licenses, and prior editorial material.
   - Create a claim-evidence ledger and an artifact inventory.
   - Identify missing evidence, broken pipelines, unsupported claims, and missing manuscript components.

3. **Build the evidence**
   - Read `references/research-quality-gates.md`.
   - Read `references/experiment-workflow.md` whenever evidence must be designed, generated, reproduced, repaired, compared, or analyzed.
   - Retrieve and verify literature, prepare data, implement or run methods, execute analyses or experiments, evaluate baselines and controls, quantify uncertainty, inspect failures, and freeze final outputs where feasible.
   - Record commands, versions, parameters, seeds, provenance, exclusions, and output paths.

4. **Produce the manuscript**
   - Read `references/manuscript-workflow.md` before drafting or substantially revising the paper.
   - Build a results-led detailed outline, then write the full title, abstract, keywords, main text, declarations, captions, references, and supplementary cross-references.
   - Write concrete scholarly prose from verified evidence. Do not leave section-level placeholders when source material is sufficient.
   - Generate tables and figures from frozen results and insert or call them out in sequence.
   - Create or update the editable manuscript file and any separate figure, table, supplement, data, code, or response files required by the task.

5. **Revise as an author**
   - Check argument continuity, methods reproducibility, result completeness, discussion depth, claim boundaries, citation support, terminology, notation, units, and cross-file consistency.
   - Repair weaknesses directly in the manuscript and supporting artifacts.
   - Repeat analysis or regenerate outputs when a writing inconsistency reveals an evidence problem.

6. **Run the manuscript language audit**
   - Read `references/manuscript-language-audit.md` and apply its complete rewrite protocol.
   - Run `scripts/audit_manuscript_language.py` against every final manuscript source file supported by the scanner.
   - Inspect every finding in context, rewrite the underlying sentence or paragraph, and rerun the scanner until no unresolved high- or medium-severity findings remain.
   - Perform the required manual semantic pass because pattern matching cannot determine authorship or detect every form of non-academic prose.
   - Preserve truthful, venue-required AI-use disclosure; remove AI-assistant conversation and drafting residue from the scholarly text.

7. **Validate the finished package**
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
- reproducibility or provenance artifacts needed to trace the reported results;
- a clean language-audit result or a documented, narrowly scoped rationale for any retained scanner false positive;
- a concise completion note listing files, validation performed, unresolved external dependencies, and final acceptance state.

Do not return only a plan, review, claim ledger, checklist, or list of suggested edits when manuscript production was requested.

## Completion Rule

Continue through evidence generation, writing, artifact creation, revision, language purification, and validation within the available environment. Stop only when the requested manuscript and supporting artifacts have been produced and checked, the language audit passes, and the manual semantic pass finds no non-academic drafting residue, or when a genuinely external dependency prevents the remaining work. In the latter case, deliver the most complete defensible manuscript possible and identify the exact blocked passages, claims, and required external actions.
