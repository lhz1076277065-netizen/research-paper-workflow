# Target-weighted comparisons reverse across conditions while group-level exceptions persist

Synthetic Skill-development manuscript. This editable demonstration uses frozen summary fixtures, not research observations.

## Abstract

A target-weighted average can favor a procedure even when that procedure has higher loss in some groups. This exploratory synthetic demonstration distinguishes target-average ordering from group-level ordering and uses fixed weights to examine the descriptive role of composition. Six frozen group summaries compare procedures A and B in two conditions, with lower loss preferred. In C1, target-weighted losses are 7.40 for A and 6.72 for B, yielding an A−B difference of +0.68 loss points; B nevertheless has higher loss in G2 and G3. In C2, the losses are 6.74 and 7.58, yielding −0.84. Applying C1 weights to C2 results gives losses of 7.34 and 7.46 and a difference of −0.12: the point-estimate reversal persists under fixed composition. C2 G3 has a difference of −0.2 with a supplied paired interval of −0.6 to +0.2, leaving both directions compatible with that interval. These comparisons establish a conditional average ordering and identify the group exceptions that constrain its interpretation. Aggregate uncertainty and a cross-condition interaction test are unavailable; the fixed-weight calculation is descriptive rather than causal.

## Introduction

Average performance answers a question about the population represented by its weights. It does not establish that the same ordering holds for every constituent group. When evaluation conditions change, the target composition and the relative performance within groups can both change. A change in an average's magnitude and a reversal in its direction therefore require distinct comparisons.

This fixture asks what the supplied paired group comparisons establish and whether the target-average reversal persists when composition is held fixed. Its contribution is an explicit account of conditional ordering: a favorable average can coexist with group-level counterexamples, and a fixed-weight comparison can distinguish a reversal that persists from the additional change associated descriptively with reweighting. The original loss metric, groups and prescribed target populations are retained.

The available N1 summary describes average advantages under balanced composition, but its full methods, unit-level data, interval procedure and version history were not supplied. Its procedures, loss definitions and evaluation units have not been established as comparable with this fixture. N2 distinguishes target weights, which define the decision population, from cluster counts, which describe evaluated independent units. N3 records tuning before the demonstration. N4 bounds the available uncertainty to paired within-group differences. These fixture notes support interpretation at different levels; N1 does not supply independent validation of the current comparisons.

## Materials and comparison

The materials are the six synthetic rows in `figure-results.csv` and the supplied N1–N4 notes. The current table is authoritative. C1 contains 30 independent clusters: 16 in G1, 4 in G2 and 10 in G3. C2 also contains 30: 6, 15 and 9. A and B were evaluated on the same clusters within each condition and group; clusters are independent between conditions. Each table row is a group summary. The six rows are not six independent individual observations for a generic significance test.

Loss is measured in loss points, with smaller values preferred. Define the group difference as d = loss_A − loss_B: a positive value favors B and a negative value favors A. The prescribed target weights for G1, G2 and G3 are 0.5, 0.2 and 0.3 in C1, and 0.2, 0.5 and 0.3 in C2. They define the target comparison and are not replaced by observed cluster proportions.

For each procedure, the target-weighted loss is the sum of target weight multiplied by group loss. The corresponding difference is the sum of target weight multiplied by d. The sensitivity comparison applies C1 target weights to C2 group outcomes. It holds composition fixed while retaining C2 performance; it does not represent a causal intervention. All reported weighted values are arithmetic summaries of the frozen table.

## Uncertainty and research status

The supplied marginal loss intervals and paired-difference intervals are 95% percentile cluster-bootstrap intervals within each condition and group. Paired-difference intervals reflect the paired evaluation at that level. Overlap between the marginal A and B intervals does not determine whether the interval for A−B includes zero.

Underlying cluster observations, aggregate bootstrap draws and cross-group covariances are unavailable. No aggregate confidence interval or cross-condition interaction test is supplied, and none is reconstructed from marginal or group intervals. The demonstration follows tuning and is exploratory (N3). There is no preregistration, randomized causal assignment, equivalence margin or out-of-domain validation.

## Results: C1

In G1, losses are 10 for A and 8 for B. The paired difference is +2, with a supplied interval from +1 to +3. In G2, losses are 6 and 7, with difference −1 and interval −1.8 to −0.2. In G3, losses are 4 and 4.4, with difference −0.4 and interval −0.7 to −0.1. B has lower loss in G1 and higher loss in G2 and G3; all three supplied paired intervals exclude zero in their respective directions.

Using C1 target weights gives average losses of 7.40 for A and 6.72 for B, with difference +0.68. The target-average comparison favors B while two group comparisons favor A. These counterexamples rule out a uniform group-level advantage for B across the supplied C1 groups. They do not invalidate the weighted arithmetic; they identify the scope of the question it answers.

## Results: C2 and fixed composition

In C2, G1 losses are 9 for A and 8.4 for B, with paired difference +0.6 and interval +0.1 to +1.1. G2 losses are 7 and 8.8, with difference −1.8 and interval −2.5 to −1.1. G3 losses are 4.8 and 5.0, with difference −0.2 and interval −0.6 to +0.2. The G3 point estimate favors A, but its interval spans zero and remains compatible with both directions. It does not establish equivalence or an absence of difference.

Using C2 target weights gives losses of 6.74 for A and 7.58 for B and a difference of −0.84. The target-average point estimate favors A, whereas G1 favors B. Thus neither condition's average direction describes every group uniformly.

Applying C1 weights to C2 results gives losses of 7.34 and 7.46, with difference −0.12. The C1-to-C2 point-estimate reversal therefore persists in this fixed-composition comparison. Changing to the C2 weights is not necessary for the reversal along this comparison, although it makes the C2 difference more negative, from −0.12 to −0.84.

The fixed-weight difference changes by −0.80 relative to C1, compared with a −1.52 change between the two conditions under their respective target weights. The ratio is 52.6%, rounded to 53% in Figure 1. This describes the retained magnitude along the specified fixed-weight comparison; it is not a causal fraction. No interval for these changes or their ratio can be calculated from the supplied summaries.

## Figure 1 caption

**Figure 1. Target-average ordering and group-level exceptions in frozen synthetic comparisons.** Loss is measured in loss points; negative A−B favors A and positive A−B favors B. **a**, Group-level paired differences and their supplied 95% percentile cluster-bootstrap intervals. Circles denote C1 and squares denote C2. Cluster counts and prescribed target weights are shown by group; target weights are not observed cluster proportions. A and B share evaluation clusters within each condition and group, while clusters are independent between conditions. The marginal A and B intervals are not plotted or used to reconstruct paired uncertainty. **b**, Target-weighted differences are descriptive point estimates without supplied aggregate intervals: +0.68 in C1, −0.84 in C2 and −0.12 when C1 weights are applied to C2 outcomes (hollow square). C1 weights for G1/G2/G3 are 50/20/30%; C2 weights are 20/50/30%. C1 G2 and G3 run against the C1 average direction, and C2 G1 runs against the C2 average direction. C2 G3 has a negative point estimate but an interval spanning zero, which does not establish equivalence. Relative to C1, the fixed-weight change is −0.80, retaining 52.6% of the −1.52 change under the conditions' respective weights (53% after rounding). This is a descriptive sensitivity comparison, not a causal decomposition or interaction test. Cluster observations, aggregate bootstrap draws and cross-group covariances are unavailable; no aggregate, change or ratio interval is supplied.

## Discussion

The frozen comparisons demonstrate why a target average and a uniform group-level claim must be reported separately. C1 favors B on average while G2 and G3 favor A. C2 favors A on average while G1 favors B; G3 remains directionally uncertain under its supplied interval. Reporting these exceptions preserves the decision-relevant distinction between the target population's summary and the groups composing it.

The fixed-weight result sharpens the interpretation of the between-condition reversal. With C1 composition held fixed, the difference changes from +0.68 to −0.12, so the new C2 composition is not required for the observed point-estimate reversal. Reweighting the C2 outcomes then moves the difference to −0.84. Within-group performance and target composition therefore matter to the descriptive comparison, but the supplied sensitivity calculation answers an arithmetic question rather than identifying a mechanism. Its retained-magnitude ratio cannot replace the direction evidence or quantify causal attribution.

The N1 summary can motivate questions about the conditions behind average advantages. Its unavailable methods and unit-level data prevent establishing comparability or evidence independence. Agreement would not automatically demonstrate replication, and disagreement would not establish a scientific contradiction. The contribution supported here is the transparent interpretation of these frozen comparisons, without a claim to a new general method. A subsequent external evaluation would need to specify its decision population, retain group-level counterexamples and evaluate uncertainty using appropriate independent units.

## Limitations

This is a synthetic fixture with group summaries; no independent external research or human study was conducted. Cluster observations and aggregate uncertainty are unavailable. The sign reversal is established for the supplied point estimates, not as a statistically demonstrated aggregate reversal or cross-condition interaction. Group intervals cannot be treated as raw observations to recover the missing joint uncertainty.

Tuning preceded the demonstration, and no preregistration, causal assignment, equivalence margin or out-of-domain evaluation is available. These conditions constrain inference and transfer. They leave the arithmetic and the distinction between an average ordering and a uniform group ordering directly checkable within the fixture.

## Conclusion

C1's target-average difference of +0.68 coexists with group comparisons unfavorable to B. C2's difference is −0.84, and its fixed-C1-weight difference is −0.12. The point-estimate ordering reverses across the supplied conditions even under fixed composition, while group-level exceptions constrain both target averages. Reporting target weights, paired group comparisons and descriptive sensitivity together makes this conditional ordering explicit. The fixture does not establish aggregate significance, equivalence, causal attribution or general deployment benefit.

## Evidence notes and availability

N1 is a supplied summary; its full methods, unit-level data, interval procedure and version history are unavailable. N2–N4 are supplied complete local notes. These labels identify synthetic development evidence, not published citations or a bibliography. Data consist of the current frozen summary table, and Figure 1 refers to the supplied prior figure. No new figure or empirical observations were generated for this manuscript. No journal, authors, affiliations, funding, approvals, participant consent or published data identifier was supplied. The document remains a synthetic development manuscript and is not submission-ready.
