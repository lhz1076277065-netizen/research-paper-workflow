# Experiment Plan
Date: 2026-10-18. Problem: Q1 and Q2 in contract-v1. Method thesis: compare pooled and cultivar-conditioned descriptive associations on the same complete official dataset.

## Claim map and compact storyline
C1/Q1/E1: quantify overall association, without preset direction. Minimum convincing evidence: all 178 official records; Pearson r, Spearman rho, OLS slope and scatter. C2/Q2/E2: characterize within-class and adjusted consistency. Minimum evidence: class-specific correlations/slopes, fixed-class intercept model, interaction check and residual plot. Anti-claim: pooled composition alone establishes a within-class or causal effect. Cultivar is a recorded group label; adjustment cannot identify a causal effect.

## Must-run blocks
E1: pooled OLS color = intercept + alcohol, Pearson r, Spearman rho, range/mean/SD. All records; no train/test split or prediction task. Slope is change in recorded color units per one alcohol unit. Report HC3 normal-approximation 95% intervals as model-based sensitivity summaries. Correlation CI uses Fisher z. No significance threshold decides whether a question is answered. Figure 1a and Table 1.
E2: class-specific OLS/correlations; color = intercept + alcohol + two class indicators (common slope); color = alcohol * categorical class (separate slopes/intercepts). Compare slope directions, sizes and HC3 intervals. Test the two interaction coefficients jointly via HC3 Wald chi-square, described only as a model diagnostic. Partial r uses class-demeaned alcohol and color. Figure 1b and Table 1. Opposite directions, imprecision or heterogeneity are findings, not failures.
S1 (required robustness): Spearman rho pooled/within; HC3 versus classical intervals; leave-one-out slope ranges for pooled and adjusted models; within-class-centered quadratic term; residual/influence summaries; independent NumPy least-squares and Frisch–Waugh–Lovell reproduction of adjusted slope. These qualify, rather than replace, E1/E2. No novelty isolation, frontier model or human evaluation is applicable.

## Order and gates
M0: official source/dictionary and complete local acquisition; parse all fields, count classes, finite values, duplicates. Gate: document discrepancies before fitting. Explicit diagnostic pilot on full validated data checks metrics and shape but is not formal evidence.
M1: formal E1/E2 once data/preparation is accepted. Cost under 30 CPU seconds; zero GPU. Negative/zero results remain publishable descriptive answers.
M2: required robustness and independent recomputation, at most 400 OLS refits planned; revise agent quota if scientifically justified, never stop on an arbitrary count.
M3: evidence-based figures, coherent scientific paper, source/citation/full scientific review, expression meaning diff and actual docx/PDF rendering. Stop when both questions are validly answered and exports checked; do not expand into an unasked novelty project.

## Data and cost
Acquire all 178 records and all 13 attributes plus cultivar from official UCI source, official dictionary, metadata and citation. No substitutes for main data. Metadata/download estimate below 5 MB, peak project 100 MB, hard cumulative and project cap 200,000,000,000 bytes each. Existing Python runtime, no large installs. Source cache reuse is verified by mandatory tool. No actual user total budget; host token meter unknown. Risks: undocumented units/collection details, group composition and nonlinearity; mitigations: retain recorded units, descriptive scope, stratification and diagnostics. No causal identification or sampling-frame inference.
