# Separating target-average ordering from group-level performance: an exploratory synthetic comparison

Synthetic Skill-development manuscript. This editable development fixture is not a research publication or a submission-ready document. No human research was conducted.

## Abstract

A target-weighted average and a uniform group-level advantage answer different questions. This synthetic demonstration makes that distinction explicit using six frozen group summaries of paired loss comparisons between procedures A and B across two evaluation conditions, C1 and C2. Each condition includes 30 independent clusters; the target weights describe the decision population rather than the observed cluster proportions. Smaller loss is preferred, and positive A−B favors B. In C1, target-weighted losses are 7.40 for A and 6.72 for B, giving a difference of +0.68 loss points, while B has higher loss in G2 and G3. In C2, target-weighted losses are 6.74 and 7.58, giving −0.84 points. Applying the C1 target weights to the C2 outcomes gives 7.34 and 7.46, with a difference of −0.12 points. Thus, the C2 point comparison remains favorable to A when target composition is held at C1 weights. Supplied paired group intervals also distinguish directional comparisons from the inconclusive C2/G3 comparison. The contribution is a reproducible account of conditional average ordering that retains group-level counterexamples and separates a fixed-composition description from causal explanation. The demonstration follows tuning and is exploratory; aggregate uncertainty is not supplied.

## Introduction

A favorable average loss does not imply a favorable comparison in every group. The average combines group-specific performance with weights representing a target population. When evaluation conditions change, group losses and target composition can both change. A reversal in the average ordering therefore requires interpretation at both levels.

This fixture asks two questions: what do the paired group summaries establish about the ordering of A and B, and how does the target-weighted comparison change when C2 outcomes are evaluated using C1 weights? Its contribution is a transparent worked comparison that reports the target average alongside the groups that qualify its interpretation. The analysis retains the supplied loss metric, groups, and target populations.

The local evidence notes establish the scope of the comparison. N2 distinguishes target-population weights from observed cluster proportions. N3 records that tuning preceded the frozen demonstration. N1 describes average advantages under a balanced composition in an earlier evaluation, but its full methods, unit-level data, interval procedure, and version history are unavailable. It supplies context for the question rather than independent validation of these results; comparability of procedures, losses, and evaluation units has not been established. N1–N4 are fixture labels, not published citations.

## Materials and comparison

The materials consist of six synthetic rows in the current frozen `figure-results.csv` and four local evidence notes. The table is authoritative for the reported values and intervals. Procedures A and B were evaluated on the same clusters within each condition and group. Clusters are independent between conditions. C1 contains 30 independent clusters distributed as 16 in G1, 4 in G2, and 10 in G3; C2 contains 30 distributed as 6, 15, and 9. Each row summarizes a group, so the six rows are not six independent individual observations for a generic six-point significance test.

Loss is expressed in loss points, with smaller values preferred. For each condition and group, the paired difference is A−B: a positive value favors B and a negative value favors A. For procedure P, the target-weighted mean in condition c is the sum of each group mean multiplied by its target weight:

\[
L_{P,c}=\sum_g w_{c,g}L_{P,c,g},\qquad D_c=L_{A,c}-L_{B,c}.
\]

The C1 target weights for G1, G2, and G3 are 0.5, 0.2, and 0.3; the C2 weights are 0.2, 0.5, and 0.3. These weights specify the decision population described by N2. They are not replaced by the observed cluster fractions. We report both procedures' target-weighted means and their difference.

For the fixed-composition sensitivity calculation, we apply C1 target weights to C2 group means while retaining all C2 outcomes. This gives a descriptive comparison under the same weights as C1. It is not a causal intervention or a test of a mechanism responsible for differences between conditions.

## Uncertainty and research status

The supplied marginal intervals for A and B and the paired-difference intervals are 95% percentile cluster-bootstrap intervals within each condition and group. The difference intervals incorporate the paired evaluations. Overlap between A and B marginal intervals does not determine whether the paired A−B interval contains zero.

The materials contain no unit-level cluster observations, aggregate bootstrap draws, or cross-group covariances. N4 specifies that there is no supplied aggregate confidence interval and no cross-condition interaction test. Aggregate means and differences are therefore reported as descriptive point estimates; their uncertainty is not inferred from the group intervals.

N3 records that tuning preceded the demonstration, so the comparisons are exploratory. No preregistration, causal assignment, equivalence margin, or out-of-domain validation is supplied. The table supports checking the arithmetic and interpreting the supplied comparisons within this fixture.

## Results: C1

Table 1 retains all six frozen summaries, including the marginal and paired intervals.

**Table 1. Supplied synthetic paired loss summaries.** Losses and differences are in loss points. Smaller loss is better; positive A−B favors B. All intervals are supplied 95% percentile cluster-bootstrap intervals within a condition and group.

| Condition | Group | Clusters (n) | Target weight | A loss [95% interval] | B loss [95% interval] | A−B [95% interval] |
|---|---|---:|---:|---|---|---|
| C1 | G1 | 16 | 0.5 | 10 [8, 12] | 8 [6, 10] | 2 [1, 3] |
| C1 | G2 | 4 | 0.2 | 6 [4, 8] | 7 [5, 9] | −1 [−1.8, −0.2] |
| C1 | G3 | 10 | 0.3 | 4 [3, 5] | 4.4 [3.4, 5.4] | −0.4 [−0.7, −0.1] |
| C2 | G1 | 6 | 0.2 | 9 [7, 11] | 8.4 [6.4, 10.4] | 0.6 [0.1, 1.1] |
| C2 | G2 | 15 | 0.5 | 7 [5, 9] | 8.8 [6.8, 10.8] | −1.8 [−2.5, −1.1] |
| C2 | G3 | 9 | 0.3 | 4.8 [3.8, 5.8] | 5.0 [4, 6] | −0.2 [−0.6, 0.2] |

In C1/G1, losses are 10 for A and 8 for B; the paired difference is 2 with an interval of [1, 3]. G2 has losses of 6 and 7, with a difference of −1 [−1.8, −0.2]. G3 has losses of 4 and 4.4, with a difference of −0.4 [−0.7, −0.1]. The supplied paired intervals lie above zero in G1 and below zero in G2 and G3. Thus, the group comparisons favor B in G1 and A in G2 and G3.

With C1 target weights, the average loss is 7.40 for A and 6.72 for B. The difference of +0.68 favors B at the target-average level while coexisting with higher B loss in two groups. These group-level counterexamples rule out interpreting the favorable C1 average as an advantage for every included group. They do not invalidate the weighted arithmetic or determine which target population a separate decision should use.

## Results: C2 and fixed composition

In C2/G1, losses are 9 for A and 8.4 for B; the paired difference is 0.6 [0.1, 1.1]. G2 has losses of 7 and 8.8, with a difference of −1.8 [−2.5, −1.1]. G3 has losses of 4.8 and 5.0, with a difference of −0.2 [−0.6, 0.2]. The G1 and G2 paired intervals favor B and A, respectively. In G3, the point estimate favors A, but the interval spans zero and supports neither a directional superiority conclusion nor equivalence.

With C2 target weights, the average loss is 6.74 for A and 7.58 for B, giving a difference of −0.84 points. Applying C1 weights to these same C2 group outcomes gives average losses of 7.34 and 7.46, with a difference of −0.12 points. The C2 point ordering therefore favors A under either supplied weighting, although its magnitude depends on the weights.

Holding the weights at the C1 composition does not restore the favorable C1 point ordering for B. This sensitivity calculation separates the target-composition question from the comparison of C2 outcomes. It does not quantify a causal contribution of composition, establish aggregate statistical significance, or supply a cross-condition interaction test.

## Figure 1 caption

Synthetic paired loss comparisons across C1 and C2. Losses and differences are in loss points; smaller loss is better and positive A−B favors B. Group intervals are the supplied paired 95% percentile cluster-bootstrap intervals. C1 target weights for G1, G2, and G3 are 0.5, 0.2, and 0.3; C2 weights are 0.2, 0.5, and 0.3. Target-weighted differences are +0.68 in C1 and −0.84 in C2. Applying C1 weights to C2 outcomes gives −0.12. Aggregate differences are descriptive point estimates without supplied aggregate confidence intervals. C1/G2 and C1/G3 counter a uniform B advantage interpretation; C2/G3 has a paired difference of −0.2 with an interval of [−0.6, 0.2] that spans zero.

## Discussion

The fixture establishes a conditional ordering of the supplied point comparisons. B has a favorable C1 target average alongside unfavorable G2 and G3 comparisons. A has a favorable C2 target average, and the C2 ordering remains favorable to A when the C1 target weights are used. Reporting these averages with their group-level comparisons makes their scope explicit: a target average summarizes the specified decision population, while a uniform advantage claim requires a different statement about the included groups.

The fixed-composition result adds an interpretable sensitivity comparison. Both target weights and within-group losses differ between C1 and C2. Applying C1 weights to C2 outcomes shows that the C2 point ordering is retained under that composition; the average reversal is not removed by this change of weights. The calculation identifies a descriptive contrast, not a causal mechanism. Without aggregate joint uncertainty or an interaction test, the reported point reversal does not establish aggregate significance or a statistically demonstrated between-condition difference in relative performance.

N1 does not resolve those inferential questions. Its available summary describes average advantages under balanced composition, but incomplete methods and source information prevent establishing direct comparability or an independent replication. Agreement with that summary would not establish replication, and disagreement would not establish a scientific contradiction. The contribution here rests on the frozen table and the explicit distinction between target averages, paired group comparisons, and fixed-weight descriptions.

For a later external evaluation, specifying the target population, retaining group-level counterexamples, and using the appropriate independent evaluation units would make the comparison interpretable. Such an evaluation would supply evidence beyond the current fixture; none is reported here.

## Limitations

This is a synthetic development fixture with group-summary data. No independent external research or human research was conducted. Group-wise intervals are supplied, but unit-level records and aggregate uncertainty are unavailable. The bootstrap intervals cannot reconstruct the missing cluster-level structure or provide an aggregate confidence interval.

The demonstration follows tuning and has no preregistration, causal assignment, equivalence margin, or out-of-domain validation. These conditions bound the results to exploratory description of the supplied comparisons. They preclude causal attribution, claims of equivalence, and evidence of general deployment benefit. N1's incomplete source limits its use to contextual comparison. These concrete limits leave the arithmetic and the distinction between average and group-level ordering directly checkable.

## Conclusion

A C1 target-weighted difference of +0.68 loss points coexists with paired G2 and G3 comparisons favoring A. The C2 target-weighted difference is −0.84, and the fixed-C1-weight difference is −0.12. Together, these frozen comparisons show how an average ordering can differ from group-level ordering and how its magnitude depends on the specified target composition. Reporting target-weighted means, paired group comparisons, and the fixed-composition sensitivity result together provides a reproducible interpretation of this exploratory fixture.

## Evidence notes and availability

N1 is a supplied summary whose full methods, unit-level data, interval procedure, and version history are unavailable. N2–N4 are supplied complete local notes: N2 defines the role of target weights and evaluated cluster counts; N3 records tuning and the exploratory status; N4 bounds the supplied difference intervals and identifies missing aggregate uncertainty and interaction testing. These labels are development-fixture evidence notes, not a formal bibliography or independently verified published research.

Data consist of the current frozen six-row summary table. No authors, affiliations, funding, approvals, participant consent, or published data identifier were supplied. No journal was selected. This document retains its synthetic development status and must not be described as submission-ready.
