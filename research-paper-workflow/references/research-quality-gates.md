# Research Quality Gates

Use these gates to decide whether a research article has enough evidence to support its claims. Apply only the gates relevant to the project, but do not waive a relevant gate without an explicit reason.

## Contents

- Evidence integrity
- Data sufficiency and academic quantity requirements
- Literature review standard
- Method validity
- Experimental validity
- Statistical and uncertainty standard
- Generalization and external validity
- Reliability, calibration, and risk
- Ethics, permissions, licensing, and availability
- Readiness decisions

## Evidence Integrity

- Every core claim must map to verifiable evidence: raw or source material, processing steps, method description, execution record, output artifact, and manuscript text.
- Evidence must be traceable from final tables and figures back to original inputs or justified derived inputs.
- Manual edits to numbers, selective deletion of unfavorable results, and undocumented preprocessing fail the gate.
- If a file cannot be opened, a script cannot be run, a result cannot be traced, or provenance is unclear, classify the affected claim as `unverifiable`.
- If evidence contradicts a claim, revise the claim downward or report the contradiction.

## Data Sufficiency and Academic Quantity Requirements

Do not use fixed sample-size numbers as universal academic standards. Establish data quantity and quality from the research design.

- For inferential studies, justify sample size or case count with statistical power, detectable effect size, variance, error tolerance, confidence level, expected attrition, multiplicity, and planned subgroup analysis.
- For predictive or modeling studies, justify effective sample size with feature dimensionality, outcome rarity, leakage risk, train/validation/test separation, learning curves, calibration, external validation, and performance uncertainty.
- For simulation or computational studies, justify coverage through the design space, boundary conditions, convergence checks, sensitivity analysis, independent replication, and comparison against known solutions or benchmarks.
- For experimental or measurement studies, justify the number of specimens, trials, instruments, operators, batches, sites, time points, repeats, and controls with variability and reproducibility needs.
- For observational studies, justify inclusion/exclusion criteria, representativeness, missingness, confounding control, measurement validity, and bias assessment.
- For qualitative or interpretive studies, justify corpus size or participant/case count with saturation, sampling logic, coding stability, triangulation, and audit trail.
- For review articles, justify literature coverage with transparent search strategy, databases or sources, date range, screening rules, inclusion/exclusion criteria, deduplication, and quality appraisal.
- If a project lacks a defensible quantity or coverage rationale, mark related claims as `partial` or `unsupported`.

## Literature Review Standard

- Cover the problem background, current state of knowledge, competing methods, relevant benchmarks, methodological limitations, and unresolved gap.
- Use primary sources for core claims whenever possible.
- Separate foundational work, recent advances, methodological comparators, datasets or materials, standards, and contradictory evidence.
- Avoid citation padding. Each citation should support a specific claim or methodological choice.
- Claims of novelty, first use, superiority, or broad impact require a documented search trail and careful wording.
- If literature coverage is narrow, outdated, or biased toward favorable work, do not claim comprehensive novelty.

## Method Validity

- Define inputs, outputs, assumptions, controls, parameters, stopping rules, exclusion rules, and success criteria before interpreting results.
- Use established methods where available; justify new methods with ablation, comparison, validation, or theoretical argument.
- State what was fixed before analysis and what was exploratory.
- Document preprocessing, transformations, normalization, filtering, annotation, calibration, and quality control.
- Check for data leakage, circular reasoning, inappropriate comparators, unavailable ground truth, confounding, batch effects, and measurement artifacts.

## Experimental Validity

- Include credible baselines, controls, counterfactuals, reference cases, or null models where applicable.
- Include ablation, sensitivity, robustness, or subgroup analysis when a method has multiple important components or assumptions.
- Include negative controls or failure cases when false positives, overfitting, artifacts, or unsafe extrapolation are plausible.
- Ensure metrics align with the research question and practical interpretation.
- Do not treat a single favorable experiment as sufficient for broad claims.

## Statistical and Uncertainty Standard

- Report uncertainty using confidence intervals, credible intervals, prediction intervals, standard errors, bootstrap intervals, repeated-run variability, or other justified measures.
- Report effect sizes or practical magnitude, not only significance or ranking.
- Correct or discuss multiplicity when many hypotheses, models, endpoints, or comparisons are tested.
- Explain missing data handling, outliers, censoring, exclusions, and failed runs.
- Use visualizations that expose variability, not only summary means.
- If uncertainty is large or unreported, narrow the conclusion.

## Generalization and External Validity

- Claims of generalization require evidence beyond the development data or original setting.
- Use independent test sets, external datasets, cross-source validation, temporal validation, distribution-shift tests, benchmark reproduction, independent replication, or theoretically justified invariance as appropriate.
- Report where the method fails, degrades, or has not been tested.
- Do not describe a method as generally applicable when evidence covers only a narrow condition.

## Reliability, Calibration, and Risk

- Reliability claims require stability analysis, calibration checks, error bounds, conservative thresholds, stress cases, or independent verification.
- Risk-sensitive claims require false-positive and false-negative analysis, worst-case scenarios, uncertainty-aware decisions, and limitations.
- If the system or method may be used for decisions, state intended use, non-use cases, and failure modes.
- If calibration, coverage, robustness, or reliability fails, state the failure and revise claims.

## Ethics, Permissions, Licensing, and Availability

- Verify permissions, consent, privacy protections, ethics approvals or exemptions, material transfer terms, data licenses, code licenses, and third-party restrictions.
- Data and code availability statements must match what is actually shareable.
- Non-public, sensitive, proprietary, or restricted materials must be described truthfully without exposing protected content.
- AI assistance must be disclosed when required and must not be listed as an author, data source, or experimental actor.

## Readiness Decisions

- `ready`: all relevant gates pass; residual limitations are disclosed and do not invalidate core claims.
- `ready only after minor fixes`: evidence gates pass, but formatting, wording, callouts, references, declarations, or packaging need limited repair.
- `not ready`: any core claim is unsupported, contradicted, unverifiable, overgeneralized, ethically unresolved, or not reproducible enough for the intended claim.

When not ready, provide a repair plan that identifies the failed gate, affected claim, required evidence, exact task, expected artifact, and acceptance criterion.
