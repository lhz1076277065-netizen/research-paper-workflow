# SYNTHETIC — Target composition changes the descriptive ordering of two paired methods

This short manuscript analyzes manufactured development measurements. It reports no real academic field observations, population validation, or genuine research finding.
<!-- claim:C002 evidence:E001,E002,E003 -->

## Abstract

We compared lower-is-better scores from methods A and B on the same eight synthetic independent units, with four units in each of two strata. The specified target composition was 80% g1 and 20% g2, whereas the sample composition was 50%/50%. After converting units, removing exact duplicate measurement events, matching time-valid metadata, and averaging technical repetitions within each unit and method, mean A−B differences were −1.00 score in g1 and +2.75 in g2. The target-weighted difference was −0.25 score, with an approximate 95% stratified paired percentile-bootstrap interval of [−0.65, 0.15]. The sample-mix difference was +0.875 score. Fixed-target leave-one-unit-out estimates ranged from −0.40 to −0.1167 score. Thus, the descriptive target point estimate favors A while the strata disagree and the conditional interval includes both directions. Neither a causal advantage nor real-world superiority is established.
<!-- claim:C001 evidence:E001,E002,E005,E006 -->

## Introduction

The question is whether A or B has a lower mean score for the stipulated target mix. Both methods were measured on the same units, and the sample has equal numbers of units in the two strata. Equal sample counts therefore do not supply the target weights: weighting the strata by their observed counts would answer a different descriptive question. The primary comparison uses the target weights supplied before measurements; the sample-mix comparison is retained to show the consequence of substituting the observed composition. No assignment mechanism or causal-identification design is supplied.
<!-- claim:C003 evidence:E001,E002 -->

## Methods

### Original measurements and preparation

The analysis was rebuilt from the supplied corrected paired archive's measurement table, data dictionary, and unit metadata. The dictionary identifies `event_id` as a measurement event and `unit_id` as an independent paired unit. An exact repeated event was treated as an archive copy; conflicting copies would stop processing. Values were converted to score before averaging, using 1 score = 1,000 subscore. Each event was joined to the unique metadata record sharing its unit identifier and covering its observation date within inclusive validity bounds. Historical records outside that interval were not used. Technical repetitions within a unit and method were equally precise by fixture definition, so their arithmetic mean supplied that unit's method score. Each unit contributed one A/B pair regardless of its number of technical measurements.
<!-- claim:C004 evidence:E002,E003,E004,E005 -->

The supplied correction increases both unique u08 method B events by 1,000 subscore and applies the same change to the repeated event copy. The three corrected raw rows are 5,950, 6,050, and 6,050 subscore; after deduplication and conversion, this unit's mean B score is 6.00. A source comparison confirmed that the other 40 measurement rows and their fields were unchanged. Metadata and license bytes were unchanged, and the original dictionary definitions were retained with an appended correction note. The target weights and estimation procedures were retained.
<!-- claim:C018 evidence:E002,E003,E009,E010 -->

### Estimand and conditional uncertainty

For unit $i$ in stratum $h$, define $d_{hi}=A_{hi}-B_{hi}$, after within-unit/method averaging. Negative differences mean lower scores for A. The primary descriptive estimator was $\widehat\Delta=0.8\bar d_{g1}+0.2\bar d_{g2}$. Weighted means for A and B were computed on the same paired units. The comparison under the sample composition used $0.5\bar d_{g1}+0.5\bar d_{g2}$ and was not substituted for the target estimator. The dictionary stipulates independence conditional on stratum for this fixture's within-stratum resampling model; it does not establish population representativeness.
<!-- claim:C005 evidence:E001,E002,E005 -->

Approximate 95% percentile intervals were calculated by resampling whole paired units separately within each stratum and applying the fixed composition weights to each resampled pair of stratum means. With four units per stratum, all $4^4=256$ equally likely ordered resamples were enumerated in each stratum, yielding 65,536 joint resamples. The endpoints are the 2.5th and 97.5th percentiles using linear quantile interpolation. Enumeration removes Monte Carlo randomness; it does not make confidence coverage exact. The procedure holds observed unit scores, the aggregation rule, and target weights fixed. It does not separately propagate technical measurement uncertainty, uncertain target composition, or uncertainty about transport to a real population. Stratum intervals use the corresponding within-stratum resamples.
<!-- claim:C006 evidence:E002,E005 -->

### Sensitivity analyses

Three exploratory checks were performed after inspecting the measurements. First, each independent unit was omitted in turn; stratum means were recomputed while target weights remained 0.8 and 0.2. Second, the g1 weight was varied from zero to one, with the g2 weight defined as its complement. Third, an alternative approximate interval used variance $\sum_h w_h^2s_h^2/n_h$ and a Welch–Satterthwaite degrees-of-freedom approximation. This last check assumes within-stratum normal paired differences for its small-sample approximation; normality cannot be established from four units per stratum. These analysis and interval choices were analyst-selected, whereas the target weights were supplied before measurements. All analyses are descriptive; no confirmatory hypothesis test was conducted.
<!-- claim:C007 evidence:E001,E002,E005,E006 -->

## Results

### Data flow and within-stratum comparison

There were 43 measurement rows. Removing two exact event copies left 41 unique technical measurement events: 17 for A and 24 for B. The metadata contained 16 historical/current records, and every unique event had exactly one active record at its observation date. No incomplete A/B pair or missing score remained. Averaging yielded eight independent paired units, four in each stratum. The technical events were not treated as 41 independent comparison units.
<!-- claim:C008 evidence:E003,E004,E005 -->

| Comparison | Independent units | A mean (score) | B mean (score) | Mean A−B (score) | Approximate 95% percentile-bootstrap interval (score) |
|---|---:|---:|---:|---:|---|
| g1 | 4 | 5.50 | 6.50 | −1.00 | [−1.375, −0.625] |
| g2 | 4 | 9.50 | 6.75 | +2.75 | [1.50, 4.25] |
| Target mix, g1/g2 = 80%/20% | 8 | 6.30 | 6.55 | −0.25 | [−0.65, 0.15] |
| Sample mix, g1/g2 = 50%/50% | 8 | 7.50 | 6.625 | +0.875 | [0.1875, 1.625] |
<!-- claim:C009 evidence:E005 -->

The observed paired differences were [−1.5, −1.0, −0.5, −1.0] score in g1 and [1.0, 2.0, 3.0, 5.0] in g2. Every observed g1 unit had a lower A score; every observed g2 unit had a lower B score. Applying the specified target composition produced a small negative difference, whereas the observed sample composition produced a positive difference. Figure 1 displays the two compositions, all unit differences, and the conditional intervals. The primary interval [−0.65, 0.15] crosses zero.
<!-- claim:C010 evidence:E005,E007 -->

### Robustness and composition sensitivity

Across the eight fixed-target leave-one-unit-out analyses, estimates ranged from −0.40 to −0.1167 score and all retained the negative sign. This check shows that omission of any single observed unit does not reverse the target point estimate. The composition sensitivity was $\widehat\Delta(w)=2.75-3.75w$, where $w$ is the g1 weight. The point estimate is zero at $w=11/15$ (approximately 0.7333), positive below that threshold, and negative above it. For example, g1 weights of 0.70 and 0.90 give +0.125 and −0.625 score, respectively. The fixed target uses $w=0.80$; the sensitivity curve changes the estimand rather than estimating new target weights.
<!-- claim:C011 evidence:E005,E006 -->

The alternative Welch–Satterthwaite calculation had standard error 0.2363 score and approximately 5.988 degrees of freedom. Its approximate 95% interval was [−0.828, 0.328] score, also crossing zero. Both interval constructions therefore leave the target ordering uncertain under their respective conditional assumptions, although their widths differ.
<!-- claim:C012 evidence:E005,E006 -->

## Discussion

For the stipulated target mix, the descriptive point estimate favors A, but this is an average of opposite stratum patterns. The change in sign between the target and sampled mixes follows from their different weights applied to the same paired units. It should not be described as agreement that A is better across strata. The leave-one-unit-out sign stability addresses single-unit influence, while the intervals address conditional resampling uncertainty; passing the former does not eliminate the latter. An interval containing zero neither proves equal performance nor confirms an advantage for either method.
<!-- claim:C013 evidence:E001,E005,E006 -->

The inference is bounded by manufactured inputs and four units per stratum. An empirical bootstrap at this size cannot demonstrate nominal population coverage, and the alternative normal approximation adds an unverified distributional condition. Independence and equal technical precision are fixture stipulations, not empirical findings about real measurements. The provenance and practical meaning of a real target composition, a real sampling frame and selection mechanism, population representativeness, calibration, and possible inter-unit dependence remain unknown. No treatment assignment or causal identification is available. Extending this result to a real population would require evidence about those inputs and assumptions; the present synthetic analysis supplies none.
<!-- claim:C014 evidence:E001,E002,E003,E005 -->

## Conclusion

The target-weighted synthetic point estimate is negative, the strata favor different methods, and conditional uncertainty spans both directions. Using the sample composition changes the descriptive answer. This fixture supports an auditable demonstration of estimand-preserving preparation, pairing, weighting, and sensitivity analysis; it does not establish real-world or causal superiority.
<!-- claim:C015 evidence:E001,E005,E006 -->

## Materials, provenance, and declarations

The local reproduction bundle contains the copied corrected archive and extracted members, preparation and analysis code, prepared event and paired-unit tables, numeric results, bootstrap distributions, sensitivity tables, Figure 1 in PNG/SVG, and its caption. Evidence locators in the accompanying source manifest and claim ledger bind the assertions above to these files. All supplied observations are synthetic, with no real individuals or organizations, and the fixture license permits reuse. Human authorship, funding, conflicts, journal submission, and human scientific approval were not supplied or verified; no such status is asserted. The manuscript was prepared within the current Agent using local computation. It remains a synthetic development report, not a submission-ready research article.
<!-- claim:C016 evidence:E001,E002,E003,E005,E006,E007,E008,E009,E010 -->
