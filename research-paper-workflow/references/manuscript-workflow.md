# Manuscript Workflow

Use this workflow to produce, complete, repair, compress, expand, or revise a scholarly manuscript. The manuscript must follow the evidence, not the desired claim. The required outcome is finished manuscript text and an editable manuscript file, not comments about what an author should write.

## Contents

- Claim alignment
- Title and abstract
- Introduction
- Literature review
- Methods
- Results
- Discussion
- Conclusion
- Figures and tables
- Citations and references
- Declarations and transparency statements
- Revision and response writing
- Language purification
- Style rules

## Production Sequence

1. Freeze the research questions, primary claims, final result artifacts, and claim boundaries.
2. Freeze the domain knowledge map, literature evidence matrix, data release, analysis diagnostics and final figure sources.
3. Build a detailed section outline that assigns evidence, citations, figures, and tables to each subsection.
4. Draft Methods and Results from traceable artifacts before finalizing the Introduction, Discussion, Abstract, and Title.
5. Write every required section in full. Replace advice such as "discuss this limitation" with the actual limitation text.
6. Insert sequential figure and table callouts, captions, equations, references, and supplementary links.
7. Create or update the editable manuscript file and render it for visual inspection.
8. Run a consistency pass across title, abstract, methods, results, discussion, conclusion, figures, tables, supplements, and declarations.
9. Run the language-audit protocol, rewrite every substantive finding, and repeat until the automated and manual gates pass.

Do not stop after producing an outline, sample section, revision memo, or list of edits unless the user explicitly requested only that output.

## Claim Alignment

- Start from the claim-evidence ledger.
- Remove, weaken, or relabel claims that are unsupported, exploratory, failed, or not externally validated.
- Keep contribution statements specific: what was done, with what evidence, under what conditions, and what changed relative to prior work.
- Do not use novelty, superiority, reliability, generality, or readiness language unless the quality gates support it.
- Make limitations visible in the abstract, methods, discussion, or conclusion when they affect interpretation.

## Title and Abstract

- Title must describe the verified contribution, not the intended or aspirational contribution.
- Avoid universal claims, exaggerated adjectives, and unsupported novelty.
- Abstract structure:
  - problem and context
  - evidence gap
  - method or approach
  - data/materials and validation design
  - primary results with quantitative or concrete evidence where appropriate
  - implication and limitation
- Do not introduce results in the abstract that are absent from the results section.
- Do not hide major limitations that would change reader interpretation.

## Introduction

Use this sequence:

1. State the important problem.
2. Explain why current knowledge or practice is insufficient.
3. Summarize the closest existing approaches or evidence.
4. Define the unresolved gap.
5. State the objective or research questions.
6. State contributions only at the level supported by evidence.
7. Preview the validation logic.

Avoid a broad textbook opening unless it is necessary for the audience.

## Literature Review

- Organize by concepts, methods, evidence types, and unresolved limitations, not by one-paper summaries.
- Separate what is known, what is debated, and what remains untested.
- Include competing approaches and negative or contradictory evidence.
- Cite primary sources for factual or methodological claims.
- Use recent literature where the area moves quickly, while retaining necessary foundational sources.
- Do not imply comprehensive coverage unless the search strategy supports it.
- Base the review on the literature evidence matrix rather than memory or opportunistic searching.
- Emphasize directly relevant work from the rolling five-year window and verified WoS/JCR Q1/Q2 sources, while retaining necessary foundational and standards references.
- Synthesize mechanisms, methods, evidence strength, contradictions and gaps; do not create a sequence of paper summaries.
- State the final search date and describe database coverage when the review supports a novelty claim.

## Methods

Write enough detail for reproduction or independent audit:

- study design or research design
- data/material source and eligibility
- sample, case, corpus, simulation, or specimen selection logic
- preprocessing, measurement, annotation, extraction, or transformation
- method, model, algorithm, instrument, protocol, intervention, simulation, derivation, or analysis procedure
- baseline, control, comparator, or reference method
- parameter settings, stopping rules, thresholds, and software versions
- metrics, statistical tests, uncertainty quantification, and correction procedures
- validation splits, repeats, seeds, independent tests, and robustness checks
- ethics, permission, license, and privacy handling where applicable
- data source version, release, access date, coverage period, cutoff date and frozen release identifier
- analysis software, version, method-selection rationale, native project file and complete diagnostic protocol

Distinguish prespecified analyses from exploratory analyses.

## Results

- Present results in the order of research questions.
- Start with data/material description and quality checks when needed.
- Report primary outcomes before secondary outcomes.
- Pair every table or figure with the claim it supports.
- Include uncertainty, variability, failed runs, exclusions, and negative results when relevant.
- Compare against baselines or controls before claiming improvement.
- Avoid explaining implications before the reader sees the evidence.
- Do not duplicate every table value in prose; state the result pattern and important numbers.
- Draft each result subsection from its frozen result artifact, naming the comparison, sample or case basis, metric, uncertainty, and relevant figure or table.
- If a required result is missing, generate it where feasible before continuing; otherwise narrow the corresponding question and state the limitation.

## Discussion

Cover:

- principal findings
- interpretation relative to the research question
- comparison with prior evidence
- why the result may occur
- practical or theoretical implications
- limitations and threats to validity
- failure modes and non-use cases
- generalizability boundary
- future work only where it follows from observed gaps

Do not use the discussion to add unsupported claims that were not tested.

## Conclusion

- Restate what the evidence demonstrates.
- State the narrowest accurate contribution.
- Include the most important limitation if omission would mislead.
- Avoid recommendations, deployment claims, or broad policy statements unless directly supported.

## Figures and Tables

- Every figure and table must be cited in order in the main text.
- Captions should state what is shown, the population/materials or conditions, key metric or unit, and any uncertainty indicator.
- Tables should include units, denominators, sample sizes or case counts where relevant, and clear abbreviations.
- Figures should expose variability when it matters.
- Do not use decorative figures that do not support a claim.
- Ensure values in figures, tables, abstract, results, and supplements match the same frozen outputs.
- Do not use raw SmartPLS, AMOS, spreadsheet or statistics-software screenshots.
- Use publication-grade vector graphics for model diagrams and line art; use suitable high-resolution raster only when scientifically appropriate.
- For SEM, report complete measurement and structural diagnostics in tables or supplements rather than crowding the path diagram.
- Preserve editable figure sources and verify readability at final publication size.

## Citations and References

- Every reference must be cited in the text.
- Every in-text citation must have a reference entry.
- Check author names, year, title, source, volume, pages, article number, DOI or URL where applicable.
- Do not cite inaccessible or irrelevant work to inflate counts.
- Do not cite generated or hallucinated references.

## Declarations and Transparency Statements

Prepare truthful statements for:

- data availability
- code or materials availability
- ethics approval or exemption
- consent where applicable
- funding
- competing interests
- author contributions
- acknowledgments
- AI or language-model assistance where required
- license and third-party restrictions

AI-use statements should be minimal and accurate. Do not state that AI designed, performed, verified, or authored scientific work unless that is exactly true and allowed.

## Revision and Response Writing

- Address each editor or reviewer point separately.
- State what changed, where it changed, and why.
- If a request cannot be met, explain the evidence-based reason and offer a narrower correction.
- Do not claim new experiments were added unless they were actually performed and documented.
- Keep the response factual, respectful, and traceable to manuscript locations.

## Style Rules

- Prefer precise verbs over promotional adjectives.
- Use active structure when it improves clarity.
- Define abbreviations on first use.
- Keep terminology consistent.
- Avoid unsupported claims of novelty, universality, robustness, safety, reliability, or superiority.
- Keep methods and results concrete; keep speculation in the discussion.
- Write direct publication-ready prose. Do not address the author, narrate the writing process, or leave editorial instructions inside the manuscript.
- Maintain coherent transitions and paragraph-level argument structure rather than assembling disconnected evidence summaries.

## Language Purification

- Read `manuscript-language-audit.md` before the final prose revision.
- Remove AI-assistant residue, generic filler, stock transitions, inflated promotional wording, conversational explanation, reader instructions, drafting notes, and unsupported evaluative adjectives.
- Contextually rewrite every AI-style or formulaic match according to the paragraph's scholarly function and evidence.
- Replace flagged wording by rewriting the complete sentence or paragraph around its scholarly function; do not perform synonym substitution that preserves the same vague logic.
- Preserve technical terms and justified claims when they are precise and evidenced. Do not weaken valid disciplinary language merely because a word is common in generated text.
- Retain a truthful AI-use disclosure when required, but keep it in the designated declaration rather than the scientific argument.
- Run the bundled language scanner after revision and manually inspect paragraph purpose, claim precision, evidence linkage, tone, redundancy, and transitions.
- Do not finalize the manuscript while any high- or medium-severity finding remains unresolved.
