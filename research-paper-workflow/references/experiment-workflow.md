# Experiment Workflow

Use this workflow to design, run, reproduce, repair, and document the evidence-generating work needed to write an academic article. "Experiment" includes empirical studies, simulations, computational analyses, models, laboratory or field work, observational analysis, qualitative coding, theoretical derivation with verification, and structured literature synthesis.

When the user requests a paper and the necessary analysis is feasible in the available environment, execute it. Do not stop at an experiment plan or list of recommended analyses.

## Contents

- Research contract
- Evidence inventory
- Data and material protocol
- Data currency and coverage
- Experimental matrix
- Analysis and figure production
- Execution discipline
- Result derivation
- Analysis and interpretation
- Failure reporting
- Reproducibility package

## Research Contract

- Define the research question before choosing methods.
- Convert objectives into hypotheses, estimands, performance targets, validation targets, or qualitative propositions.
- State the primary outcome or evaluation criterion.
- State secondary outcomes separately.
- Define the decision boundary for success, failure, inconclusive evidence, and exploratory evidence.
- Predefine what evidence would weaken or falsify the main claim.

## Evidence Inventory

Create a project inventory before running or judging experiments:

`Artifact | Location | Purpose | Input dependency | Output produced | Version/date | Owner/source | Reproducibility status | License/permission`

Required categories when applicable:

- raw or source data
- processed data
- data dictionary or schema
- protocols or methods
- scripts, notebooks, or analysis code
- environment files and dependency versions
- random seeds and run configurations
- logs and run manifests
- intermediate outputs
- final result tables
- generated figures
- supplementary materials
- permissions, ethics, and licenses

## Data and Material Protocol

- Define inclusion and exclusion criteria before analysis.
- Document collection, acquisition, extraction, measurement, annotation, simulation, or synthesis procedures.
- Record units, scales, transformations, missing values, quality flags, duplicates, outliers, censoring, and exclusions.
- Separate raw inputs from processed inputs.
- Preserve an immutable or restorable copy of source material.
- Document known bias sources and mitigation attempts.
- Check that training, tuning, validation, and final testing materials are separated when required.
- Verify that licensing and consent allow the intended analysis and sharing.

## Data Currency and Coverage

- Apply `data-currency-and-coverage.md` before finalizing the experiment matrix.
- Record source versions, release dates, access dates, update frequency, observation window and cutoff date.
- Check for new releases or corrections before execution and before manuscript acceptance.
- Build a coverage matrix over all claim-relevant dimensions and identify absent or sparse conditions.
- Use independent sources for triangulation or external validation where required.
- Freeze one versioned data release and bind every experiment to its identifier.

## Experimental Matrix

Build a table before execution:

`Experiment ID | Research question | Input data | Method | Baseline/control | Variables changed | Metrics | Seeds/repeats | Expected output | Acceptance criterion | Status`

Include these classes when relevant:

- main experiment answering the primary research question
- baseline or control experiment
- ablation or component-removal experiment
- sensitivity analysis over important assumptions or parameters
- robustness analysis under noise, missingness, perturbation, distribution shift, or alternate preprocessing
- external or independent validation
- benchmark or known-case reproduction
- subgroup, stratified, temporal, spatial, or condition-specific analysis
- calibration, uncertainty, reliability, or coverage analysis
- error analysis and failure-case inspection
- negative control or sanity check

Do not expand the matrix mechanically. Include experiments that materially test the claims.

## Analysis and Figure Production

- Apply `advanced-analysis-and-figures.md` and document why the method family fits the estimand, constructs and data.
- If using SmartPLS or AMOS, include measurement-model, structural-model, uncertainty, fit or prediction, invariance and robustness tasks as applicable.
- Preserve native project files and machine-readable exports in addition to publication figures.
- Generate figures from frozen outputs, not by redrawing values manually.
- Treat every figure as an evidence artifact with a linked research question, source result and verification status.

## Execution Discipline

- Run experiments from versioned scripts, notebooks with cleared execution order, workflow files, or documented commands.
- Record command, timestamp, code version, data version, environment, seed, parameters, hardware or platform if relevant, and output path.
- Prefer deterministic pipelines for final results.
- Freeze final result inputs and outputs before manuscript drafting.
- Keep exploratory outputs separate from final outputs.
- Do not overwrite final outputs without preserving the old version or documenting why it was superseded.
- If installation or environment setup fails, record the failure, fix, and final environment.
- Continue from setup through execution, diagnostics, reruns, result freezing, and manuscript-ready outputs.
- Rerun affected analyses when newer data, corrected data or revised domain definitions materially change the input.
- Treat an experiment matrix as a work queue. Mark an item complete only after its output and provenance exist.
- If a planned method fails, diagnose and repair it where feasible; otherwise run the strongest valid alternative and document the changed claim boundary.

## Result Derivation

- Generate tables and figures from frozen outputs, not from manually typed values.
- Keep a trace from each manuscript number to a source file, computation, or log.
- Store metric definitions with formulas, units, denominators, aggregation level, and excluded cases.
- Report all planned primary outcomes, including unfavorable or inconclusive ones.
- Report missing runs, failed runs, and excluded runs with reasons.
- Use consistent rounding rules and units.
- Verify that confidence intervals, error bars, statistical tests, and labels match the data.
- Produce a manuscript-ready result bundle containing machine-readable results, publication-quality tables or figures, metric definitions, and a short evidence interpretation for each research question.
- Export SEM diagrams and other analytical figures as clean vector or high-resolution artifacts; do not use raw GUI screenshots.

## Analysis and Interpretation

- Answer the research questions in the order defined by the research contract.
- Distinguish primary, secondary, exploratory, and post hoc analyses.
- Compare against baselines before interpreting absolute performance.
- Interpret practical magnitude, not only direction or significance.
- Identify where the method works, where it fails, and where evidence is insufficient.
- Avoid causal language unless the design supports causal inference.
- Avoid broad generalization unless external validity evidence exists.
- Tie each figure and table to a specific claim.

## Failure Reporting

For every important failed attempt, record:

`Attempt | Goal | Command/procedure | Failure mode | Diagnostic evidence | Fix attempted | Final status | Effect on claims`

Failure categories:

- inaccessible or invalid data
- irreproducible output
- dependency or environment failure
- method not applicable
- baseline cannot be implemented fairly
- benchmark lacks necessary details
- convergence, instability, or calibration failure
- unacceptable error or uncertainty
- licensing, ethics, or permission block
- result contradicts the proposed claim

Failed experiments are valid scholarly evidence when reported honestly. Do not hide failures that change the scope or conclusion.

## Reproducibility Package

Prepare enough material for an independent reader to reproduce or audit the claims:

- exact data availability statement
- code availability statement
- environment and dependency record
- run instructions for final results
- frozen outputs used in the manuscript
- figure and table generation path
- seeds and configuration files
- provenance and license notes
- known limitations and non-reproducible elements

If full sharing is impossible, provide a truthful restricted-access, synthetic, redacted, or procedural alternative and state what cannot be reproduced externally.
