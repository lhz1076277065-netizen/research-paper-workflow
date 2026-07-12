# Final Acceptance Checklist

Use this checklist after producing the manuscript and before declaring it ready, preparing a submission package, responding to an editorial technical check, or making a final not-ready decision. Apply fixes directly wherever feasible; do not substitute the checklist for a finished paper.

## Contents

- Decision rule
- Manuscript integrity
- Evidence and reproducibility
- Domain knowledge
- Literature evidence quality
- Data, code, and materials
- Advanced analysis
- Figures, tables, and supplements
- References
- Language integrity
- Declarations
- Submission package
- Final output format

## Decision Rule

Choose exactly one final state:

- `ready`: all applicable hard gates pass and only ordinary submission risk remains.
- `not ready`: any automated or manual gate fails, any fix remains, or any core scientific claim is unsupported, unverifiable, contradicted, unreproducible, based on stale or materially incomplete data, under-researched, methodologically mismatched, domain-invalid, ethically unresolved, or overstated.

Never choose `ready` because the user wants to submit quickly. Readiness follows evidence.

Before choosing a state, confirm that the requested editable manuscript exists, contains all required sections, opens correctly, and has been rendered and inspected. If no manuscript was produced, the workflow is incomplete rather than merely `not ready`.

Run the unified package validator before choosing a state:

```bash
python scripts/validate_research_package.py PROJECT_ROOT --profile auto --report validation/report.json
```

An exit code other than `0` requires `not ready`; no wording such as "ready after fixes" is permitted. Manual visual and semantic review must also pass before `ready`.

## Manuscript Integrity

- Title matches verified contribution.
- Abstract matches methods, results, limitations, and conclusion.
- Introduction gap matches the literature review.
- Contribution list matches completed work.
- Methods contain enough detail for reproduction or audit.
- Results answer the declared research questions.
- Discussion does not add untested claims.
- Conclusion does not exceed evidence.
- Limitations are specific and visible.
- Terminology, abbreviations, units, and notation are consistent.
- Word count, structure, and formatting meet the target instructions if supplied.

## Evidence and Reproducibility

- Claim-evidence ledger is complete for all major claims.
- Final numbers trace to result files, logs, scripts, or documented calculations.
- Primary experiments or analyses have executable records.
- Baselines, controls, ablations, robustness checks, external validation, or uncertainty analyses are present when required by the claim.
- Failed attempts that affect scope are disclosed or used to narrow claims.
- Random seeds, versions, parameters, and environment are recorded when relevant.
- Independent reproduction is possible, or unreproducible parts are clearly justified.

## Domain Knowledge

- Domain knowledge map and terminology ledger cover all core claims and methods.
- Current standards, guidelines, units, thresholds and reporting conventions have been verified.
- Mechanisms, competing explanations, boundary conditions and known failure modes are represented.
- Interpretations have an authoritative specialist basis and do not rely only on generic reasoning.

## Literature Evidence Quality

- Reproducible search queries, databases, filters, dates, screening and deduplication records are present.
- Each core claim maps to an inspected source in the literature evidence matrix.
- Core claims, closest comparators, original methods, datasets, standards and contradictory evidence all have direct references; no required evidence class is empty.
- Recent evidence uses the rolling five-year window and records verified WoS index plus JCR year, category and quartile.
- At least 70% of nonfoundational journal references are recent verified Q1/Q2 sources when the field provides sufficient eligible work, or a documented exception is present.
- Foundational works, standards, decisive methods and contradictory evidence are retained where necessary.
- DOI, bibliographic metadata, corrections and retractions have been checked.

## Data, Code, and Materials

- Data source, collection, extraction, or generation process is documented.
- Inclusion and exclusion rules are documented.
- Missingness, exclusions, outliers, and quality control are explained.
- Data licenses, consent, privacy, and access restrictions are respected.
- Code or analysis files needed for the manuscript are present and open.
- Dependencies and run instructions are sufficient for review or audit.
- Availability statements match the actual shareable artifacts.
- Data freshness and currency checks record source version, release date, access date, cutoff date and lag to the latest available observation.
- Coverage matrix demonstrates the periods, populations, regions, subgroups, ranges and boundary conditions required by the claims.
- Multi-source joins preserve provenance and address overlap, incompatibility, leakage and source-specific bias.
- All results trace to one frozen data release identifier.

## Advanced Analysis

- Method and software choice follow the research design rather than visual sophistication.
- SmartPLS or AMOS is used only when the study has a justified SEM structure and complete applicable diagnostics are reported.
- Measurement validity precedes interpretation of structural paths.
- Fit, prediction, effect magnitude, uncertainty, robustness, invariance, heterogeneity and alternative models are addressed as applicable.
- Native model files, versions, settings, seeds and machine-readable exports are preserved.

## Figures, Tables, and Supplements

- Every figure and table is called out in main-text order.
- Every figure, table, and supplement file opens correctly.
- Captions are complete and accurate.
- Units, denominators, sample sizes, uncertainty indicators, and abbreviations are clear.
- Values match the frozen outputs and manuscript text.
- Supplementary material is cited where needed and does not hide essential methods or results.
- File names are simple, stable, and submission-safe.
- No final figure is a raw software or GUI screenshot.
- Diagrams and line art use clean vector output; raster figures meet resolution and scientific-image requirements.
- Figures show uncertainty and distributions when relevant and remain legible at final publication size.

## References

- Every in-text citation has a reference entry.
- Every reference entry is cited.
- References are real, relevant, and sufficiently complete.
- Citation style follows the target instructions if supplied.
- Literature claims are supported by appropriate sources.
- Novelty claims are backed by a documented search or are softened.

## Language Integrity

- The bundled language scanner has been run against every supported final manuscript source file.
- Zero unresolved high- or medium-severity findings remain.
- Any retained scanner match is a documented false positive reviewed in its full sentence and paragraph context.
- No AI-assistant conversation, response preamble, drafting instruction, placeholder, revision note, or reader-directed coaching remains.
- No generic AI-style filler, ornamental transition, exaggerated promotion, vague praise, casual explanation, or unsupported certainty remains.
- Every paragraph performs a scholarly function and connects claims to evidence, methods, interpretation, limitation, or prior work.
- A manual semantic review has checked issues beyond pattern matching, including repetition, empty abstraction, unnatural parallelism, abrupt transitions, and verbose restatement.
- Required AI-use disclosure remains truthful, minimal, and confined to the appropriate declaration.

## Declarations

Verify presence and accuracy of:

- data availability statement
- code or materials availability statement
- ethics approval, exemption, or not-applicable statement
- consent statement where applicable
- funding statement
- competing interests statement
- author contribution statement
- acknowledgments
- AI-use disclosure where required
- license and third-party permission notes

## Submission Package

- Main manuscript is the correct final version.
- Supplementary files are current.
- Figures and tables are embedded or uploaded separately according to supplied instructions.
- Cover letter or response letter is consistent with the manuscript.
- Metadata title, abstract, authors, affiliations, keywords, highlights, and declarations match the manuscript.
- Generated PDF is visually checked for line breaks, missing symbols, broken equations, unreadable figures, and incorrect order.
- No placeholder text remains.
- No unresolved language-audit finding or non-academic drafting residue remains.
- No private paths, credentials, personal notes, hidden comments, or tracked changes remain unless intentionally included.
- `validation/report.json` corresponds to the final artifact versions and reports no failed gate.

## Final Output Format

Report final acceptance as:

`Decision: ready | not ready`

Then provide:

- passed gates
- failed gates
- affected claims
- required fixes
- artifacts checked
- artifacts missing or inaccessible
- residual risks
- exact next action

Keep this report secondary to the delivered manuscript and supporting files. If `not ready`, do not imply submission readiness; repair all feasible defects first, then identify only the unresolved evidence or external-action blockers.
