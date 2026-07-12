# Advanced Analysis and Publication-Grade Figures

Use this protocol before selecting analysis software and before generating final figures. Methodological fit controls tool choice; visual complexity never substitutes for valid analysis.

## Contents

- Method-to-tool routing
- Structural equation modeling decision
- SmartPLS protocol
- AMOS and covariance-based SEM protocol
- Non-SEM analysis standard
- Figure production standard
- Analysis and figure acceptance

## Method-to-Tool Routing

Start from the estimand, theory, data-generating process, measurement level, dependence structure, sample design, and intended inference.

| Research structure | Preferred method family | Typical tools | Required justification |
|---|---|---|---|
| Latent common factors; theory confirmation; global model fit | Covariance-based SEM (CB-SEM) | AMOS, SmartPLS CB-SEM, lavaan, Mplus, equivalent validated software | Construct theory, identification, estimator, distributional assumptions, fit and residual diagnostics |
| Composite/formative constructs; prediction or driver analysis; complex PLS path model | PLS-SEM | SmartPLS or equivalent validated PLS-SEM software | Why PLS-SEM fits the objective better than CB-SEM or observed-score regression |
| Observed-variable association or causal estimand | Regression, generalized models, causal inference, multilevel or panel methods | Validated statistical software | Identification assumptions, confounding strategy, dependence and uncertainty |
| Time-to-event, longitudinal, spatial, network, time-series, functional, image, text or high-dimensional data | Domain-matched specialist method | Validated domain software or libraries | Sampling structure, assumptions, diagnostics, validation and uncertainty |
| Exploratory description only | Descriptive and exploratory analysis | Reproducible statistical or visualization tools | No confirmatory or causal overclaim |

Do not choose SmartPLS or AMOS solely to make the analysis or figures appear advanced. Do not use SEM when constructs, sample design, theory, identification, or measurement quality do not support it.

Use only legitimately licensed and accessible software. If SmartPLS or AMOS cannot be run, do not invent native output; use a methodologically equivalent validated implementation only when equivalence is defensible, and disclose the software substitution and any feature differences.

## Structural Equation Modeling Decision

Before SEM, document:

- theoretical constructs, directional hypotheses and alternative models;
- reflective, formative, composite or common-factor measurement specification;
- indicator provenance, scale validity, coding and missing-data treatment;
- sample-size or power justification based on model complexity and target effects;
- distribution, outlier, dependence and nonresponse diagnostics;
- model identification and degrees of freedom;
- why PLS-SEM, CB-SEM or a simpler model is the appropriate method;
- prespecified model modifications and protection against data-driven overfitting.

If these items are absent, do not present an SEM path diagram as confirmatory evidence.

## SmartPLS Protocol

For an appropriate PLS-SEM study, preserve the project file, software version, algorithm settings, seed, bootstrap settings and exported result tables.

Assess the measurement model as applicable:

- indicator loadings or formative weights and their uncertainty;
- internal consistency using justified coefficients rather than a single reliability statistic;
- convergent validity, discriminant validity and collinearity;
- AVE, HTMT, VIF and cross-loading evidence where methodologically applicable;
- content validity and construct specification before statistical deletion of indicators;
- measurement invariance before multigroup comparisons.

Assess the structural and predictive model as applicable:

- path estimates with standard errors, confidence intervals and multiplicity handling;
- direct, indirect, total, mediation and moderation effects;
- collinearity, explained variance, effect sizes and out-of-sample prediction;
- predictive diagnostics such as PLSpredict or equivalent, with a defensible benchmark;
- model fit or discrepancy measures only with interpretation appropriate to PLS-SEM;
- heterogeneity, endogeneity, nonlinearity, robustness and alternative specifications;
- a large, justified final bootstrap with a fixed recorded seed; use current methodological guidance rather than an arbitrary default.

Do not report only path significance. A PLS-SEM claim requires measurement quality, structural evidence, uncertainty, prediction where claimed, and limitations.

## AMOS and Covariance-Based SEM Protocol

For an appropriate AMOS or other CB-SEM study, preserve the model file, data version, software version, estimator, starting values, convergence status and exported output.

Report as applicable:

- confirmatory factor analysis before interpretation of structural paths;
- model identification, estimator and treatment of nonnormal, ordinal or missing data;
- standardized and unstandardized estimates with standard errors and confidence intervals;
- global fit using a justified set of complementary indices, including exact fit, comparative fit, residual fit and interval estimates;
- standardized residuals, local strain and influence diagnostics;
- reliability, convergent validity, discriminant validity and factor correlations;
- indirect effects using an appropriate bootstrap or other justified uncertainty procedure;
- nested or information-criterion model comparisons when alternatives are theory-supported;
- configural, metric, scalar and other relevant invariance levels before group comparisons;
- modification indices only when theoretically justified and independently validated.

Do not claim causality from a cross-sectional path model alone. Do not tune a model solely to fit-index thresholds.

## Non-SEM Analysis Standard

When SEM is not appropriate, use the strongest method matched to the research question. Require:

- explicit estimand or prediction target;
- baseline, comparator or null model;
- assumption and diagnostic checks;
- effect magnitude and uncertainty;
- sensitivity, robustness and subgroup analysis where relevant;
- independent, external, temporal or distribution-shift validation when generalization is claimed;
- reproducible code, parameters, versions and frozen outputs.

Advanced analysis means valid design, diagnostics and uncertainty, not a larger number of algorithms.

## Figure Production Standard

Generate each figure from frozen result files. Never manually alter numerical geometry, labels or plotted values.

- Use vector output (`PDF`, `SVG`, `EPS` or suitable editable vector format) for diagrams and line art; use high-resolution raster only when required by the image type or venue.
- Do not submit screenshots from SmartPLS, AMOS, spreadsheets, notebooks or statistical GUIs as final figures.
- Recreate or carefully export path diagrams with readable construct names, standardized notation, nonoverlapping arrows and coefficients tied to frozen outputs.
- Use consistent fonts, units, scales, decimal precision, panel labels, legends and color semantics across the manuscript.
- Use colorblind-safe palettes and ensure interpretation does not depend on color alone.
- Show raw distributions, uncertainty, sample size and missingness where they affect interpretation; avoid bars that hide variation.
- Avoid 3D effects, shadows, decorative gradients, chartjunk, excessive gridlines and unnecessary interpolation.
- Match the visual form to the scientific task: comparison, distribution, relationship, composition, time, uncertainty, spatial structure or model architecture.
- Use captions that define population or material, conditions, statistic, uncertainty, abbreviations and direction of better performance.
- Verify every displayed number against the result artifact and manuscript text.

For SEM figures, distinguish measurement and structural components when density harms readability. Put full diagnostics in tables or supplements instead of crowding a path diagram.

## Analysis and Figure Acceptance

Pass only when:

- the analysis family is justified against credible alternatives;
- all applicable diagnostics and uncertainty analyses are complete;
- software files and exported outputs are preserved and reproducible;
- every figure answers a research question or supports a defined claim;
- no final figure is a raw GUI screenshot;
- figures remain legible at final publication size and in grayscale or accessible color;
- figure values, captions, results text and supplements agree exactly.
