# Mixture-dependent direction in a paired method comparison

SYNTHETIC DEVELOPMENTAL DRAFT — anonymous author-review copy. Technical Note for fictional Journal Lens, policy v2. Not approved for submission.

## Abstract

An aggregate method comparison can change direction when the intended mixture differs from the sampled mixture. This diagnostic note makes that dependence explicit using supplied results for eight independent paired units, four in each of two strata. Mean A−B was −1.00 score in g1 and +3.00 in g2; lower score is better. The equal sampled mixture gives +1.00, whereas the prespecified g1:g2 target mixture of 0.8:0.2 gives −0.20. The target's supplied 95% within-stratum paired-unit bootstrap percentile interval is [−0.60, 0.20] and includes zero. Reporting both stratum contrasts and mixture weights explains the directional change while retaining the g2 result favoring B. The finding is a descriptive diagnostic for the specified comparison; it establishes neither universal dominance, a causal effect, nor equivalence.

## 1. Introduction

An aggregate comparison may change direction when its mixture changes. This note diagnoses that dependence by comparing stratum-specific paired contrasts under sampled and prespecified target weights.

## 2. Methods

### 2.1. Units and measurement

The supplied record specifies eight independent units, four in g1 and four in g2. Methods A and B were measured on every same unit. Technical repetitions were averaged within each unit and method after unit conversion. The unit contrast is the converted, repetition-averaged score under A minus that under B. Units are the independent sampling objects; repetitions within a unit are not additional independent units. Independence is a premise of the supplied record, not a conclusion established by a citation or independently verified from raw records in this task. Lower score denotes better performance.

### 2.2. Target quantity and sampled quantity

The g1:g2 target weights of 0.8:0.2 were fixed before measurement. If the supplied stratum means are d_g1 and d_g2, the target contrast is Δ_target = 0.8 × d_g1 + 0.2 × d_g2. The observed equal unit mixture has weights 0.5:0.5, giving Δ_sampled = 0.5 × d_g1 + 0.5 × d_g2. These are two descriptive aggregate quantities formed from the same stratum contrasts.

### 2.3. Reported interval

The reported analysis script resampled paired units within stratum and reapplied the fixed target weights. The supplied interval is a 95% within-stratum paired-unit bootstrap percentile interval for Δ_target. This resampling object preserves the A/B pairing and the unit as the sampling object; counting technical repetitions as independent observations would change that object. No interval is supplied for either stratum or the equal sampled mixture. The numerical source records, original script, bootstrap realizations, resample count and seed were not supplied; the interval has not been independently replicated here.

## 3. Results

The g1 mean A−B was −1.00 score, favoring A's lower score. The g2 mean was +3.00 score, favoring B's lower score. The opposite stratum directions are essential to the aggregate comparison and are retained in Figure 1.

For the equal sampled mixture, Δ_sampled = 0.5 × (−1.00) + 0.5 × (+3.00) = +1.00 score. For the prespecified target mixture, Δ_target = 0.8 × (−1.00) + 0.2 × (+3.00) = −0.20 score. Reweighting changes the aggregate point estimate by −1.20 score and reverses its direction without changing either stratum contrast. The sampled point estimate favors B; the target point estimate favors A. These calculations check arithmetic from the supplied results and do not constitute a new analysis of raw units.

The target interval [−0.60, 0.20] includes negative values, zero and positive values. It therefore leaves uncertainty about the direction of the target comparison. No equivalence margin or registered equivalence test is present in the record; crossing zero establishes neither practical equivalence nor an exact absence of a difference.

## 4. Interpretation and evidence limits

The directional change is explained by mixture weighting: g1's negative contrast receives more weight in the target mixture, while g2's positive contrast remains visible. A sample aggregate and a target aggregate answer different mixture-specific questions. Neither one alone establishes a universal ranking.

The supplied abstract-level description of Rosenbaum and Rubin concerns assignment probabilities conditional on observed covariates [1]. It supplies no evidence that unmeasured confounding is irrelevant to this comparison. There is no causal assignment, confounding measurement or causal adjustment in the available record, so reweighting cannot supply a causal interpretation.

The numerical estimates and interval are reported from the authoritative synthetic result memo v2. Missing numerical source data, original analysis code and resampling outputs prevent independent replication and assessment of empirical interval coverage. Four units per stratum provide a small evidence base, and no external validation is supplied. The note identifies a mixture-dependent point-estimate direction within this record.

## 5. Conclusion

Report stratum-specific paired contrasts with explicit target weights before interpreting an aggregate comparison. In this fixture, the equal sampled mixture gives +1.00 score and the prespecified target mixture gives −0.20, while g2 favors B. Together, these values make mixture dependence directly inspectable for the stated comparison.

## Data and code access

Aggregate results and display-generation code accompany this local package. Raw unit-level records and identifiers may not be redistributed under the fixture license and are not included. Original numerical data and analysis code were not supplied. A draft controlled-materials request must specify verification purpose, required materials, intended users, and storage and redistribution safeguards; access requires an authorized custodian to confirm a lawful mechanism and approve it. The custodian, contact and approval remain unknown. No access entitlement, repository deposit or transfer is asserted. See the accompanying data/code access statement.

## Declarations

Author list, contributions and approval: UNKNOWN. Funding and sponsor role: UNKNOWN. Conflicts: UNKNOWN. Human-participant status, ethics determination, consent and approval: UNKNOWN. No approval or exemption is asserted. AI-assisted developmental editing and aggregate-display preparation were used; accountable author verification remains pending.

## References

[1] Rosenbaum, P. R., and Rubin, D. B. (1983). The central role of the propensity score in observational studies for causal effects. Biometrika. https://doi.org/10.1093/biomet/70.1.41. Use is limited to the supplied abstract-level description; full text and implementation were not obtained.
