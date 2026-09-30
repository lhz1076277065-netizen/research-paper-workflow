# Supplement S1 — units, aggregation and evidence availability

SYNTHETIC DEVELOPMENTAL DRAFT — anonymous author-review copy.

## S1.1. Sampling and pairing

The supplied record specifies eight independent paired units, with four in g1 and four in g2. Each unit was measured under A and B. Technical repetitions were averaged within unit and method after conversion. They do not increase the independent-unit sample size. Their counts, raw values, conversion factors and unit identifiers were not supplied. The design's independence premise has not been independently checked against source records.

## S1.2. Quantities and arithmetic

Lower score is better. A unit's contrast is its converted, repetition-averaged A score minus its corresponding B score. The supplied stratum mean contrasts are d_g1 = −1.00 score and d_g2 = +3.00 score. g1 favors A and g2 favors B in their point estimates.

The target weights were fixed before measurement at g1:g2 = 0.8:0.2. The target estimate is 0.8 × (−1.00) + 0.2 × (+3.00) = −0.20 score. The equal sampled mixture is 0.5 × (−1.00) + 0.5 × (+3.00) = +1.00 score. Their difference is −1.20 score. These two aggregates reuse the same eight units and the same stratum contrasts; they are not independent additional samples or new experiments.

## S1.3. Interval object

The authoritative memo gives a 95% within-stratum paired-unit bootstrap percentile interval [−0.60, 0.20] for the fixed-weight target aggregate. The recorded procedure resampled paired units within stratum and reapplied the target weights. The resampling objects are paired units, not individual A and B measurements and not technical repeats. Numerical source data, original script, bootstrap realizations, number of resamples and random seed were not supplied. The endpoints are reported, not recomputed. No stratum intervals, equal-mixture interval, p-values or equivalence test are supplied.

The interval includes zero and both signs. It cannot alone establish equivalence, a precise zero effect, a causal effect, or a ranking for all mixtures. There is no equivalence margin, registered equivalence test, causal assignment, confounding measurement or external validation in the record.

## S1.4. Reproduction boundary

The accompanying aggregate-results JSON and figure-generation script can reproduce the displayed summary values and arithmetic. They cannot reproduce the original unit aggregation or bootstrap interval. Raw records and identifiers are absent and their redistribution is prohibited by the fixture license. The original inferential analysis code is absent. A controlled-materials request is a draft only; the lawful access mechanism, recipient and approval have not been confirmed.

## S1.5. Sources and versions

Numerical authority: supplied `evidence.md`, “Synthetic authoritative result memo, version 2.” Design details are corroborated by the supplied `draft-v2.md` Methods and `supplement-v2.md`. Figure 1 uses only those supplied aggregate values. The older public snapshot v1 reported −0.30; it is retained unchanged in the separate version archive. A correction draft links that older number to the v2 reporting authority and current manuscript v3; no new dataset or reanalysis is implied.
