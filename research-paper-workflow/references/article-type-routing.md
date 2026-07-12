# Article-Type Routing

Select the profile from the research design before running experiments. Store it in `research_manifest.json`; `--profile auto` reads this value and never guesses from prose.

| Profile | Use for | Distinct hard gates |
|---|---|---|
| `empirical-general` | General inferential or comparative study | Main, baseline, robustness, assumptions and uncertainty |
| `sem-survey` | Justified latent-variable or survey SEM | Native model, measurement validity, structural evidence, fit or prediction, robustness |
| `ml-predictive` | Predictive modeling or machine learning | Leakage, calibration, ablation, error analysis and external validation |
| `simulation-computational` | Numerical simulation or solver study | Verification, convergence, benchmark, sensitivity and validation |
| `lab-field` | Laboratory, measurement or field experiment | Control, measurement error, repeatability and robustness |
| `observational-causal` | Observational causal or policy estimand | Identification, confounding, negative control, sensitivity and external validation |
| `systematic-review-meta-analysis` | Systematic review or quantitative synthesis | Search coverage, screening, risk of bias, heterogeneity and publication bias |
| `qualitative` | Qualitative or interpretive research | Sampling, saturation, coding stability, reflexivity and negative cases |
| `theoretical-methods` | Theoretical, conceptual or methods paper | Assumptions, derivation, known cases, counterexamples and limitations |

Do not use `sem-survey` merely because SmartPLS or AMOS is available. Do not use a lighter profile to avoid evidence required by the actual design. Changing profile after seeing results requires a documented rationale and a complete rerun of applicable validation.

