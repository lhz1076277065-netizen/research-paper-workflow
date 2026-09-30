# SYNTHETIC — Target composition reverses the aggregate ranking of opposing paired score differences

Manufactured development fixture. Descriptive computational report; no observations from a real academic field.

## Abstract

A target composition can change the aggregate ranking even when the underlying paired measurements stay fixed. We compared lower-is-better scores for A and B using eight synthetic independent paired units, four in each of two strata. The stipulated target weights were 0.8 and 0.2; the observed unit composition was 0.5 and 0.5. Stratum-specific mean A-minus-B differences were -1.00 and +3.00 score, respectively. Standardization to the target gave -0.20 score with a conditional 95% paired-unit percentile bootstrap interval of [-0.65, +0.25], whereas the sampled composition gave +1.00 score. Exact within-stratum resampling retained pairing and fixed weights. Exploratory single-unit omissions preserved the negative target point direction, with estimates from -0.400 to -0.067 score; the composition-dependent point ranking crossed at a first-stratum weight of 0.75. The result establishes a descriptive ranking reversal within the manufactured records. The target interval includes zero, and opposing strata preclude a uniform method advantage.

## Introduction

An aggregate comparison answers a composition-specific question. In this fixture, lower scores are better, so a negative A-minus-B difference favors A. The requested target gives 80% weight to stratum 1 and 20% to stratum 2, while the observed sample contains four independent units in each stratum. An equal-weight pooled-unit summary therefore describes the sampled composition rather than the specified target.

We compare these two summaries of the same paired measurements. The objective is to quantify the target contrast, expose any disagreement between strata, and determine how conditional uncertainty and single-unit influence qualify the aggregate ranking. Composition is fixed for the primary analysis; sensitivity to other compositions is reported separately.

## Methods

### Material and preparation

The original paired archive supplies synthetic measurements, time-valid unit metadata, a data dictionary, and a reuse license. Its identity was checked against the supplied archive digest before local acquisition. The measurement table contains 43 rows, including exact copies of events e004 and e041. Removing these copies leaves 41 distinct events: 17 for A and 24 for B. Values labeled subscore were divided by 1,000, following the dictionary's definition of 1 score as 1,000 subscore.

Each measurement was joined by unit identifier and its observation date, 15 January 2026, to the metadata record whose inclusive validity period contained that date. Exactly one active record matched every event from the 16 metadata history rows. No event had a missing field, conflicting duplicate, unmatched metadata, or multiple active matches. Technical repetitions, stipulated to have equal precision, were averaged within each unit and method after conversion. The resulting 16 unit-method means formed eight complete paired units, four per stratum; repetition counts ranged from one to four. No independent unit was excluded and no value was imputed.

### Target contrast and conditional resampling

Let D_hi denote the mean A score minus the mean B score for paired unit i in stratum h. Units receive equal weight within each stratum. The primary descriptive standardized contrast is

Delta_T = 0.8 mean(D_1) + 0.2 mean(D_2).

The sampled-composition comparator Delta_S uses weights 0.5 and 0.5. The target weights were stipulated before the fixture measurements. Computational and exploratory sensitivity choices were made after inspection of the supplied material.

We enumerated all 4^4 ordered samples of four paired units drawn with replacement within each stratum. Resampling unit-level differences preserves A/B pairing and its covariance. Combining the independent within-stratum distributions yields 65,536 equally likely configurations. For each contrast, its stratum weights remain fixed. Interval endpoints are the 2.5th and 97.5th percentiles of the corresponding empirical resampling distribution, defined by the inverse empirical cumulative distribution: sorted order statistic ceil(qM), where M is the number of equally likely configurations. Enumeration removes Monte Carlo error.

These are conditional 95% paired-unit percentile bootstrap intervals. They condition on the empirical paired-unit distributions, the stipulated independence of the eight units conditional on stratum, and fixed weights. With four units per stratum, they do not guarantee nominal population coverage. No hypothesis test, p-value, equivalence test, or causal effect is estimated.

### Exploratory robustness

Each independent paired unit was omitted once, and the target contrast was recalculated with weights still fixed at 0.8/0.2. Each omission leaves three units in one stratum and four in the other, giving 3^3 × 4^4 = 6,912 resampling configurations. We also evaluated Delta(w) = w mean(D_1) + (1-w) mean(D_2) over first-stratum weights from zero to one and solved its zero crossing. Changing w describes another composition; it neither replaces the stipulated primary target nor identifies a causal composition effect.

## Results

The paired differences in stratum 1 were -1.5, -1.0, -0.5, and -1.0 score; those in stratum 2 were +1.0, +2.0, +3.0, and +6.0 score. Every observed unit favored A in the first stratum and B in the second. Figure 1 shows this disagreement alongside the target and sampled compositions.

| Summary | Mean A score | Mean B score | A-minus-B score | Conditional 95% percentile interval |
|---|---:|---:|---:|---:|
| Stratum 1, n=4 | 5.50 | 6.50 | -1.00 | [-1.375, -0.625] |
| Stratum 2, n=4 | 9.50 | 6.50 | +3.00 | [+1.500, +5.000] |
| Target 80/20, n=8 | 6.30 | 6.50 | -0.20 | [-0.650, +0.250] |
| Sampled 50/50, n=8 | 7.50 | 6.50 | +1.00 | [+0.1875, +2.0000] |

The target point estimate favors A by 0.20 score; the sampled-composition point estimate favors B by 1.00 score. The target interval includes zero. With stratum means held fixed, changing from sampled to target composition changes the aggregate contrast by -1.20 score.

The composition function is Delta(w) = 3 - 4w, with a zero crossing at w=0.75. The point estimate favors A above that weight and B below it. All eight single-unit omission estimates remained negative, ranging from -0.400 to -0.067 score. Seven omission intervals included zero. Omitting u08, whose second-stratum difference was +6.00, gave -0.400 score with interval [-0.733, -0.067]. The primary result retains u08 because the supplied records provide no basis for invalidating its measurement.

## Discussion

Composition determines which stratum-specific difference dominates the aggregate. The same paired records favor A at the stipulated 80/20 target and B at the sampled 50/50 composition. This reversal follows arithmetically from opposing stratum means; it does not require changing the measurement object or invoking a causal mechanism. Retaining the second-stratum counterexample prevents the target point estimate from being read as a universal advantage.

Single-unit omission supports the stability of the target point direction within these records, while its conditional interval remains sensitive to the observed units. Removing the largest second-stratum difference changes whether the interval includes zero. That sensitivity is a reason to display the raw paired differences and retain the full-data result, rather than select an omission that yields a preferred interval. The full target interval's inclusion of zero does not establish equivalence.

The fixture stipulates independence conditional on stratum and equal precision of technical repetitions. It supplies no real-world sampling frame, inclusion probabilities, assignment mechanism, score-validity evidence, or transportability assessment. Standardization addresses the stated composition mismatch but does not establish representativeness within strata. Dependence among real units or unequal measurement precision could require a different analysis. Accordingly, the present contrasts and intervals support a synthetic descriptive comparison, with no causal or real-population superiority claim.

## Conclusion

The original paired synthetic records yield a target A-minus-B contrast of -0.20 score and a sampled-composition contrast of +1.00 score. Explicit composition preserves the requested comparison; the opposing strata and zero-containing target interval define its scope. The fixture demonstrates why a ranking must be reported with its target weights, paired unit, and uncertainty.

## Data, code, and software attribution

The supplied license permits reuse of the synthetic material. Original archive members, preparation and analysis code, exact bootstrap outputs, figure sources, and the numerical audit are supplied in the local reproduction package. Evidence-bound writing guidance from Scientific Agent Skills informed the manuscript procedure [1]; implementation provenance is recorded separately. This is a synthetic draft without human scientific or submission approval.

## Reference

1. Kassis T, Agarwal V, He Y, Patel D, Brueckner AM. Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents. 2026. [doi:10.48550/arXiv.2609.00065](https://doi.org/10.48550/arXiv.2609.00065). Software-procedure attribution; not evidence for the synthetic score results.
