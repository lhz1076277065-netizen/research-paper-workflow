# SYNTHETIC — A paired comparison at two stratum compositions

Manufactured development fixture. Descriptive computational report; no observations from a real academic field.

## Abstract

We performed an analysis of two methods, A and B, using the supplied synthetic paired measurements. The requested target gives weights 0.8 and 0.2 to two strata, whereas the sample contains four units per stratum. We removed duplicated events, converted measurement units, joined the valid metadata, and averaged technical repeats. The stratum-specific mean A-minus-B differences were -1.00 and +3.00 score. The target contrast was -0.20 score, with a conditional 95% paired bootstrap percentile interval of [-0.65, +0.25]. The sample-composition contrast was +1.00 score. Leave-one-unit-out target estimates ranged from -0.400 to -0.067 score. The ranking crossed at a first-stratum weight of 0.75. These calculations describe the synthetic empirical strata under the given independence model and do not establish a causal or real-world advantage. [claim:C001] [evidence:E001,E002,E006,E007]

## Introduction

The supplied fixture asks for a comparison of A and B on a target composition rather than the observed composition. Because lower scores are better, negative A-minus-B differences favor A. The target weights are 0.8 for stratum 1 and 0.2 for stratum 2; the observed sample instead assigns equal numbers of independent units to each stratum. We therefore need to preserve the stated target when calculating the overall difference. [claim:C002] [evidence:E001,E002]

We set out to calculate the within-stratum paired differences, their target-weighted mean, and a comparator at sampled composition. We also examined the empirical paired-unit resampling distribution and two exploratory sensitivities. The relevant comparison is between these summaries of the same measurement object. [claim:C003] [evidence:E005,E006,E007]

## Methods

### Synthetic material and preparation

The original paired archive contains a measurement table, a history-bearing unit table, a dictionary, and a reuse license. Its SHA-256 identity was checked against the supplied candidate record before local acquisition. The mirror has the same digest and does not provide an independent source; the proxy contains a different measurement object. [claim:C004] [evidence:E001,E003,E004,E005]

The measurement file has 43 rows, including exact copies of events e004 and e041. Removing these copies leaves 41 distinct events: 17 for A and 24 for B. Values labeled subscore were divided by 1,000 because the dictionary defines 1 score as 1,000 subscore. Each event was joined to unit metadata using unit identifier and its observation date, 15 January 2026, within inclusive validity dates. This selected one active record per event from 16 metadata rows. No event had a missing field, conflicting duplicate, unmatched metadata, or multiple active matches. [claim:C005] [evidence:E002,E003,E004,E005]

Technical repetitions were averaged within unit and method after conversion, as the dictionary stipulates equal precision. This produced 16 unit-method means and eight complete independent paired units, four per stratum. Repetition counts ranged from one to four. No unit was excluded and no value was imputed. Independence conditional on stratum is a fixture stipulation, not an external validation result. [claim:C006] [evidence:E002,E005]

### Estimand and conditional interval

For paired unit i in stratum h, let D_hi be its mean A score minus its mean B score. Each independent unit contributes equally to its stratum mean. The primary descriptive standardized contrast is Delta_T = 0.8 mean(D_1) + 0.2 mean(D_2). The comparator Delta_S uses weights 0.5 and 0.5. These weights summarize two different compositions. The target weights were stipulated before the fixture measurements; the computational and sensitivity choices here were made after inspecting the material. [claim:C007] [evidence:E001,E002,E006]

We enumerated all 4^4 ordered samples of four paired units drawn with replacement within each stratum. A and B remain paired because resampling acts on their joint unit-level difference. Combining the two independent stratum resampling distributions gives 65,536 equally likely configurations. We retained the relevant fixed weights for each statistic. The displayed interval is bounded by the 2.5th and 97.5th percentiles of this empirical resampling distribution, using the inverse empirical cumulative distribution: order statistic ceil(qM), where M is the number of equally likely configurations. Enumeration avoids Monte Carlo error. [claim:C008] [evidence:E006]

The interval is conditional on the empirical paired-unit distributions, the fixed weights, and the fixture's independence model. Four units per stratum do not establish reliable nominal population coverage. The material supplies no real-world sampling frame, inclusion probabilities, assignment mechanism, or validation of score meaning and transportability. No hypothesis test, p-value, equivalence test, or causal effect is estimated. [claim:C009] [evidence:E001,E002,E006]

### Exploratory robustness checks

We omitted each independent paired unit once and recalculated the target contrast, keeping 0.8/0.2 weights rather than reallocating them according to remaining row counts. With three units in one stratum and four in the other, each corresponding resampling distribution has 3^3 times 4^4 = 6,912 configurations. To expose composition dependence, we also evaluated Delta(w) = w mean(D_1) + (1-w) mean(D_2) for first-stratum weights from zero to one and solved its zero crossing. This does not change the prespecified primary target or estimate a causal composition effect. [claim:C010] [evidence:E007]

## Results

The stratum 1 paired differences were -1.5, -1.0, -0.5, and -1.0 score; the stratum 2 differences were +1.0, +2.0, +3.0, and +6.0 score. All observed units therefore favored A in stratum 1 and B in stratum 2. Figure 1 exposes this disagreement and the two compositions. [claim:C011] [evidence:E005,E006,E008]

| Summary | Mean A score | Mean B score | A-minus-B score | Conditional 95% percentile interval |
|---|---:|---:|---:|---:|
| Stratum 1, n=4 | 5.50 | 6.50 | -1.00 | [-1.375, -0.625] |
| Stratum 2, n=4 | 9.50 | 6.50 | +3.00 | [+1.500, +5.000] |
| Target 80/20, n=8 | 6.30 | 6.50 | -0.20 | [-0.650, +0.250] |
| Sampled 50/50, n=8 | 7.50 | 6.50 | +1.00 | [+0.1875, +2.0000] |

The target point estimate favors A by 0.20 score, whereas the sampled-composition point estimate favors B by 1.00 score. The target interval includes zero. Holding the stratum means fixed, moving from sampled to target composition changes the contrast by -1.20 score. [claim:C012] [evidence:E006,E008]

The composition function is Delta(w) = 3 - 4w. It crosses zero at w=0.75: point estimates favor A above that weight and B below it. All eight leave-one-unit-out target estimates remained negative, ranging from -0.400 to -0.067 score. Seven of the eight omission intervals included zero. Omitting u08, whose stratum 2 difference is +6.00, produced -0.400 score with interval [-0.733, -0.067]. We retained u08 in the primary analysis because no supplied information invalidates that measurement. [claim:C013] [evidence:E005,E006,E007]

## Discussion

The supplied records show that changing composition changes the aggregate descriptive ranking, while the underlying stratum-specific paired differences remain fixed. The target result and sampled result answer different questions. A universal method advantage would conceal the opposite second-stratum comparison. [claim:C014] [evidence:E006,E008]

The target point direction survives single-unit omission, but the width and zero inclusion of the conditional interval depend on the observed units. In particular, removing the largest second-stratum difference changes zero inclusion. This sensitivity does not justify excluding that unit or treating a favorable omission as the primary analysis. [claim:C015] [evidence:E007]

Inference beyond the manufactured fixture remains unresolved. Stratum weighting corrects the supplied composition mismatch but does not verify representativeness within strata, score validity, independence in a real population, or transportability. Dependence among real units could change the uncertainty calculation. The target interval's inclusion of zero does not establish equivalence, and the paired descriptive contrast does not identify a causal effect. [claim:C016] [evidence:E001,E002,E006]

## Conclusion

The original paired synthetic records give a target A-minus-B contrast of -0.20 score and a sampled-composition contrast of +1.00 score. Stratum-specific directions oppose each other, and the target conditional interval includes zero. A clearly stated composition and an intact paired unit are therefore essential to interpreting this fixture's comparison. [claim:C017] [evidence:E006,E008]

## Data, code, and software attribution

The supplied license permits reuse of the synthetic archive. Original members, preparation and analysis scripts, the bootstrap distribution, the figure sources, and the numerical audit are included in the local reproduction package. The writing procedure used evidence-bound guidance from Scientific Agent Skills [1]; implementation provenance is recorded separately. This manuscript is a synthetic draft without human scientific or submission approval. [claim:C018] [evidence:E002,E005,E006,E009]

## Reference

1. Kassis T, Agarwal V, He Y, Patel D, Brueckner AM. Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents. 2026. [doi:10.48550/arXiv.2609.00065](https://doi.org/10.48550/arXiv.2609.00065). Software-procedure attribution; not evidence for the synthetic score results.
