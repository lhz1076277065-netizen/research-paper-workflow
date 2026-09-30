# SYNTHETIC — Target composition reverses the point estimate when paired stratum contrasts oppose

**Agent-produced synthetic development manuscript. All measurements are manufactured; this is not a report of real academic observations or a submission-ready paper.** [claim:C001] [evidence:E001,E002]

## Abstract

Opposing stratum contrasts make the intended composition decisive for an aggregate comparison. We compared methods A and B in a synthetic paired score archive at a prespecified target composition of 80% stratum 1 and 20% stratum 2. The observed sample had four independent paired units in each stratum. After deduplicating events, converting units, linking date-valid metadata and averaging technical repetitions, we calculated unit-level A−B differences; lower scores were preferable. The stratum means were −1.00 and +2.75 score. Target standardization gave −0.25 score with a conditional 95% percentile bootstrap interval of [−0.65, 0.15], whereas the sample's 50%/50% composition gave +0.875 [0.1875, 1.625]. Intervals enumerate within-stratum resampling of paired units with fixed weights. Removing any one unit retained a negative target mean, with estimates from −0.40 to −0.1167. Alternative compositions crossed zero at a 73.33% stratum-1 share. This synthetic analysis demonstrates that the descriptive aggregate depends on the intended composition; the target interval does not establish a definitive advantage for either method. [claim:C002] [evidence:E001,E005,E006]

## Introduction

A descriptive aggregate compares methods for a particular composition of units. When the target mix differs from the observed sample, its comparison must retain that intended mix. This synthetic paired dataset specifies a target composition distinct from the observed sample composition. The score is lower-is-better, and no assignment or causal-identification design is supplied. [claim:C011] [evidence:E001,E002]

Averaging equally over the observed units gives each stratum half the weight, while the target gives stratum 1 four times the weight of stratum 2. These aggregates answer different questions. The objective is to estimate the stipulated 80%/20% descriptive contrast, show whether strata agree, and assess its conditional uncertainty. The balanced sample aggregate serves as a composition diagnostic; it does not redefine the primary comparison. [claim:C002] [evidence:E001,E006]

## Methods

### Material and preparation

The authorised paired-score archive contains the relevant measurements, dictionary and unit metadata. Its SHA-256 digest was verified against the supplied frozen identity and correction authorisation before copying and extraction. For u08, the archive incorporates a +1,000 subscore adjustment to method B measurements, including exact event copies; other measurement fields and analytical definitions are unchanged. The dictionary retains its original definition text and appends a correction note. The original catalogue identifies the mirror as a duplicate of the original source, providing no independent validation; the proxy describes different measurements and was not analysed. [claim:C013] [evidence:E007,E010,E011]

Measurements carry event identifiers, unit identifiers, method, observation date, value and measurement unit. Exact repeated records with the same event identifier were removed; conflicting repeated identifiers would stop the analysis. Values reported in subscore were divided by 1,000 to obtain score. Each event was linked by unit identifier and observation date to exactly one metadata record whose inclusive validity interval contained that date. Historical metadata were therefore not joined as additional observations. Within each unit and method, converted technical repetitions were averaged using the dictionary's equal-precision rule. A and B were paired by independent unit; technical repetitions did not increase the independent-unit sample size. [claim:C004] [evidence:E002,E003,E004,E005]

### Estimand and conditional interval

For unit i in stratum h, define d_hi=mean(A_hi)−mean(B_hi), and let d̄_h be the equal-unit stratum mean. The primary descriptive estimand is Δ_target=0.8d̄_1+0.2d̄_2. The sample-composition diagnostic is Δ_sample=0.5d̄_1+0.5d̄_2. Negative contrasts indicate lower A scores; positive contrasts indicate lower B scores. The target weights were stipulated before measurement and were not estimated from row counts. [claim:C002] [evidence:E001,E002,E005]

The conditional bootstrap resampled four paired units with replacement inside each stratum, preserving the unit as the sampling unit and the A/B pairing. All 4⁴=256 ordered draws in each stratum and their 256²=65,536 joint combinations were enumerated. Aggregate weights remained fixed. Intervals use inverse empirical-CDF 2.5th and 97.5th percentiles, without Monte Carlo sampling. These are pointwise conditional percentile intervals rather than exact-coverage population confidence intervals. The dictionary stipulates independent units conditional on stratum for this fixture. Exchangeability under each empirical stratum distribution is the model used here; representative real sampling and population coverage are unestablished. The supplied material does not define a practical-importance threshold. No causal effect, hypothesis test, equivalence test or simultaneous confidence claim was estimated. [claim:C008] [evidence:E001,E002,E005,E006]

### Sensitivity analyses

Two analyst-chosen checks evaluated interpretation after source inspection. First, each independent unit was omitted in turn, its stratum mean recomputed with three remaining units, and the target weights retained at 0.8 and 0.2. Second, the stratum-1 weight w was varied over [0,1], holding the observed stratum means fixed. This sweep describes alternative target populations, not uncertainty in the stipulated target weights. [claim:C009] [evidence:E005,E006]

## Results

### Records and paired units

The archive contained 43 measurement rows and 16 metadata records. Removing duplicated events e004 and e041 left 41 distinct measurements: 30 in score and 11 in subscore. Each distinct event had one date-valid metadata match. All eight units had complete A/B pairs, with four units in each stratum and no missing values in the required fields. Method A had one to three technical repetitions per unit, and B had two to four; these repetitions were averaged rather than counted as independent units. [claim:C003] [evidence:E003,E004,E005,E006]

Stratum 1 unit contrasts were −1.5, −1.0, −0.5 and −1.0 score; stratum 2 contrasts were +1, +2, +3 and +5. Thus every observed stratum-1 unit had a lower A score, and every observed stratum-2 unit had a lower B score. Mean A/B scores were 5.50/6.50 in stratum 1 and 9.50/6.75 in stratum 2. [claim:C005] [evidence:E005,E006]

### Primary contrast and composition diagnostic

The target-standardized A/B means were 6.30/6.55 score, giving Δ_target=−0.25 and a conditional 95% interval [−0.65, 0.15]. The same observed units under the balanced sample composition gave means 7.50/6.625 and Δ_sample=+0.875 [0.1875, 1.625]. The two aggregates therefore have opposite point-estimate directions. Stratum-specific conditional intervals were [−1.375, −0.625] and [1.50, 4.25]. Figure 1 exposes both stratum directions, all unit contrasts, composition and interval definitions. [claim:C006] [evidence:E005,E006]

### Robustness

Deleting one independent unit at a time gave target contrasts between −0.40 and −0.1167 score; all eight estimates remained negative. Omitting the largest positive contrast, unit u08, gave −0.40; omitting u01 gave −0.1167; omitting u05 gave −0.1333. No single observed unit therefore caused the sign of the target point estimate, although this check does not establish population robustness or interval exclusion of zero. [claim:C009] [evidence:E005,E006]

For alternative weights, Δ(w)=w(−1)+(1−w)2.75=2.75−3.75w. The observed aggregate is zero at w=11/15≈0.7333, negative above that share and positive below it. The prespecified target share of 0.80 is 6.67 percentage points above this crossing. This sensitivity is a property of alternative estimands, not evidence that the given weights should be changed. [claim:C010] [evidence:E005,E006]

## Discussion

The observed results show why target composition must be stated with the aggregate comparison. The 80%/20% contrast slightly favours A in point estimate, while the equally weighted sample aggregate favours B. Both results follow from the same pairs and the opposing stratum means; neither requires changing measurements or ignoring a stratum. Reporting the pooled sample mean as the primary target answer would substitute a different estimand. [claim:C011] [evidence:E001,E005,E006]

The target's conditional interval includes zero, so the descriptive point estimate does not establish a definitive advantage for either method under the resampling model. Agreement of the unit-deletion signs assesses influence on that point estimate, not the uncertainty claim. Technical repetitions support each unit/method mean under the stipulated equal-precision rule; resampling those repetitions as independent units would answer a different uncertainty question. [claim:C011] [evidence:E002,E005,E006]

Scope is conditional on the manufactured archive, its dictionary, fixed target weights and the stated within-stratum resampling model. The fixture stipulates independence rather than empirically validating it. Inclusion probabilities, within-stratum representativeness, a real target population and dependence structures in any real application remain unknown. Small stratum sizes restrict the empirical distributions, and enumeration removes Monte Carlo error without validating nominal population coverage. External target-weight uncertainty, systematic measurement error and causal identification are not represented by the displayed intervals. Real use would require a defined sampling frame, transport justification and evidence about independent units and score validity. [claim:C011] [evidence:E001,E002,E006]

## Conclusion

Target-specific aggregation changes the descriptive answer in this synthetic comparison: the prespecified target mean is −0.25 score with a conditional interval crossing zero, while the balanced sample aggregate is +0.875. Preserving paired units, opposing stratum contrasts and the declared composition makes both the answer and its uncertainty explicit. [claim:C006] [evidence:E001,E006]

## Availability and declarations

The accompanying local package contains the checked authorised archive and correction provenance, extracted measurements and dictionary, `prepare.py`, `analysis.py`, `pairs.csv`, bootstrap probability tables, sensitivity outputs, editable figure and caption. The source license permits reuse of synthetic evaluation material and states that no real individuals or organizations are involved. Authorship, funding and competing-interest information were not supplied; no such declarations are invented. There is no real-participant study or asserted ethics approval, trial registration or submission. [claim:C012] [evidence:E002,E003,E004,E005,E009]

The current Agent prepared the code, figure and prose locally, using SciPilot figure guidance and K-Dense scientific-writing guidance. Factual checks are computational and Agent-performed; accountable human scientific verification and submission approval have not occurred. The scientific-writing resource is acknowledged in the software reference below. [claim:C015] [evidence:E005,E008]

## Software reference

Kassis, T., Agarwal, V., He, Y., Patel, D., and Brueckner, A. M. (2026). *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*. arXiv:2609.00065. [https://doi.org/10.48550/arXiv.2609.00065](https://doi.org/10.48550/arXiv.2609.00065). Bibliographic metadata were checked against the [arXiv record](https://arxiv.org/abs/2609.00065); this is a software-workflow acknowledgement, not empirical support for the synthetic score findings. [claim:C015] [evidence:E008]
