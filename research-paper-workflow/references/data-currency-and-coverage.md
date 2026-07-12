# Data Currency and Coverage

Use this protocol before final analysis and repeat it immediately before manuscript acceptance.

## Contents

- Data contract
- Freshness and update checks
- Coverage matrix
- Multi-source integration
- Quality and bias audit
- Frozen analysis release
- Acceptance gate

## Data Contract

For every dataset or material source, record:

`Source | Version | Release date | Coverage period | Access date | License | Population/domain | Variables | Units | Update frequency | Owner | Raw location | Processing status`

Define the required observation window, spatial or institutional scope, subgroups, variables, outcomes, boundary conditions and minimum resolution from the research questions.

## Freshness and Update Checks

- Establish a data cutoff date before analysis.
- Check the authoritative source for newer releases, revisions, corrections and schema changes before freezing results.
- Repeat the update check before final acceptance when data are dynamic or the project duration is long.
- Quantify the lag between the latest available observation and the manuscript cutoff date.
- Explain why older data remain valid when newer data exist but are excluded.
- Rerun affected preprocessing, analysis, tables and figures when an update materially changes coverage or conclusions.
- State the exact data version and cutoff date in Methods and availability statements.

Do not describe data as current, complete or comprehensive without this record.

## Coverage Matrix

Maintain:

`Required dimension | Target coverage | Observed coverage | Missing regions/periods/groups/conditions | Bias risk | Mitigation | Effect on claims`

Evaluate dimensions applicable to the study:

- time, geography, site, institution, batch, operator or instrument;
- demographic, clinical, environmental, material, operational or other domain-relevant strata;
- outcome prevalence, rare events, extremes and boundary conditions;
- predictor and response ranges;
- missingness patterns and data availability by subgroup;
- training, tuning, validation and external-test independence;
- benchmark and real-world coverage.

More records do not make data comprehensive when important dimensions remain absent.

## Multi-Source Integration

Use multiple independent sources when needed for scope, triangulation or external validation.

- Preserve source identifiers and provenance through all joins.
- Harmonize definitions, units, coding, timestamps, coordinate systems and ontologies explicitly.
- Detect duplicates, overlapping populations, repeated entities and leakage across sources.
- Quantify source-specific bias and distribution differences before pooling.
- Compare source-stratified results and pooled results.
- Keep an untouched external source for validation when the claim requires generalization.

Do not pool incompatible sources merely to increase sample size.

## Quality and Bias Audit

- Validate schema, type, range, units, impossible values, duplicates and referential integrity.
- Quantify missingness and justify imputation, deletion or censoring methods.
- Audit measurement error, label quality, inter-rater agreement, batch effects and temporal drift.
- Test representativeness against the intended population or design space.
- Identify selection, survivorship, nonresponse, reporting and availability biases.
- Use power analysis, precision analysis, learning curves, convergence studies or saturation evidence to justify quantity.
- Separate exploratory correction from prespecified quality-control rules.

## Frozen Analysis Release

Create an immutable or content-addressed analysis release containing:

- raw-source manifest and checksums where permitted;
- processed data and schema;
- inclusion and exclusion log;
- data dictionary and units;
- update and correction log;
- preprocessing code and environment;
- final split or sampling assignments;
- coverage and quality reports;
- release identifier used by every result artifact.

## Acceptance Gate

Pass only when the latest authoritative releases have been checked, the cutoff date and lag are explicit, required coverage is demonstrated or limitations narrow the claims, integration is traceable, quantity is justified, quality and bias audits pass, and all manuscript outputs trace to one frozen data release.

