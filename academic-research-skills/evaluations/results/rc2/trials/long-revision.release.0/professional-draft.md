# Target averages and group-level comparisons under changing evaluation composition: a synthetic demonstration

Synthetic Skill-development manuscript. This editable document reports a frozen development fixture, not human research or a research publication.

## Abstract

A favorable target-weighted average can coexist with unfavorable group-level comparisons. This synthetic demonstration examines that distinction across two evaluation conditions using six frozen group summaries for procedures A and B. Loss is measured in loss points, with smaller values preferred and positive A−B favoring B. Each condition includes 30 independent clusters, with paired evaluations within groups. Under the C1 target weights, mean losses are 7.40 for A and 6.72 for B, giving a difference of +0.68, while B has higher loss in G2 and G3. Under the C2 target weights, mean losses are 6.74 and 7.58, giving −0.84. Applying the C1 weights to the C2 outcomes gives 7.34 and 7.46, or −0.12: the unfavorable C2 point ordering for B persists when the target composition is held fixed. The contribution is an explicit interpretation of target-average ordering alongside its group-level counterexamples, rather than a claim of uniform advantage. The comparisons are exploratory, and supplied uncertainty intervals apply to groups; aggregate significance, causal attribution, and transfer to other settings are not established.

## Introduction

An average comparison answers a question about the population represented by its weights. It does not by itself establish the same ordering within every constituent group. A change in the average between evaluation conditions can also combine two descriptive changes: the target composition and the relative losses within groups. Reporting these quantities together clarifies what an average supports and where its interpretation changes.

This fixture addresses two questions. First, does the favorable C1 target average for B imply favorable comparisons in every group? Second, does the unfavorable C2 ordering persist when C2 outcomes are summarized using the C1 target composition? The six supplied rows permit direct answers to these questions without changing the loss metric, selecting favorable subgroups, or replacing the specified target populations.

The local evidence notes distinguish what is available from what remains unknown. N1 is a supplied summary of an earlier evaluation reporting average advantages under balanced composition. Its full methods, unit-level data, interval procedure, and version history are unavailable, so comparability with the present fixture is unresolved. N2 distinguishes target weights from observed cluster proportions, N3 records tuning before this demonstration, and N4 specifies the scope of the supplied difference intervals. These fixture labels do not represent published citations or independent external validation.

The contribution is a transparent account of conditional ordering: a target average can favor B while identified groups favor A, and the C2 point ordering can remain unfavorable to B under the C1 composition. The analysis keeps the original groups, losses, and target weights together so that a favorable average is interpreted with the counterexamples that constrain it.

## Materials and comparison

### Frozen materials and evaluation units

The materials comprise the current frozen `figure-results.csv`, six synthetic group summaries, and the supplied evidence notes N1–N4. The current table supersedes the earlier draft's C2/G3 loss for B. No human research was conducted. N1 is available as a summary; N2–N4 are supplied complete local notes.

C1 contains 30 independent clusters: 16 in G1, 4 in G2, and 10 in G3. C2 also contains 30: 6 in G1, 15 in G2, and 9 in G3. Procedures A and B are evaluated on the same clusters within each condition and group, while clusters are independent between conditions. Each row is a group summary. The six rows are therefore not six individual observations for a generic six-point significance test.

### Target-weighted comparisons

Loss is expressed in loss points, with smaller values preferred. For procedure p and condition c, the target-weighted mean is

\[
\bar L_{p,c}=\sum_{g=1}^{3} w_{c,g}L_{p,c,g},\qquad
D_c=\bar L_{A,c}-\bar L_{B,c}.
\]

The target weights sum to one within each condition. C1 weights for G1, G2, and G3 are 0.5, 0.2, and 0.3; C2 weights are 0.2, 0.5, and 0.3. Positive D favors B and negative D favors A. As N2 specifies, these weights define the decision population rather than the observed fraction of clusters. Cluster counts describe evaluated independent units and are not substituted for the target weights.

The fixed-composition comparison applies the C1 target weights to C2 group losses:

\[
D_{C2\mid w_{C1}}=\sum_{g=1}^{3} w_{C1,g}(L_{A,C2,g}-L_{B,C2,g}).
\]

It retains C2 outcomes while holding the weighting composition fixed for description. It is not a causal intervention or a test of a cross-condition interaction.

## Uncertainty and research status

The table supplies 95% percentile cluster-bootstrap intervals for each procedure's group loss and for the paired difference A−B. The difference intervals concern paired comparisons within a condition and group (N4). Overlap of the marginal intervals for A and B does not determine whether the paired-difference interval contains zero. The intervals are supplied summaries, not newly reconstructed bootstrap estimates.

No cluster-level observations, aggregate bootstrap draws, or cross-group covariances are available. The material supplies neither aggregate confidence intervals nor a cross-condition interaction test. Aggregate values and the fixed-composition comparison are consequently reported as descriptive point summaries. N3 records that tuning preceded this frozen demonstration, making the comparisons exploratory. The record contains no preregistration, causal assignment, equivalence margin, or out-of-domain validation.

## Results

### Group-level comparisons

Table 1 retains all supplied group estimates, cluster counts, target weights, and intervals. In C1, G1 losses are 10 for A and 8 for B, with A−B = +2 and an interval from 1 to 3. In G2, losses are 6 and 7, giving −1 with an interval from −1.8 to −0.2. In G3, losses are 4 and 4.4, giving −0.4 with an interval from −0.7 to −0.1. B therefore has lower loss in G1 and higher loss in G2 and G3, with each supplied paired interval excluding zero in the corresponding direction.

In C2, G1 losses are 9 and 8.4, giving +0.6 with an interval from 0.1 to 1.1. G2 losses are 7 and 8.8, giving −1.8 with an interval from −2.5 to −1.1. The current G3 losses are 4.8 and 5.0, giving −0.2 with an interval from −0.6 to 0.2. The G3 point estimate favors A, but its interval contains zero and both signs; it does not establish equivalence or the absence of a difference.

**Table 1. Frozen synthetic group comparisons.** Values in brackets are the supplied 95% percentile cluster-bootstrap intervals. Loss and A−B are in loss points. Positive A−B favors B. Marginal loss intervals and paired-difference intervals summarize different quantities.

| Condition | Group | Independent clusters | Target weight | A loss [interval] | B loss [interval] | A−B [paired interval] |
|---|---|---:|---:|---|---|---|
| C1 | G1 | 16 | 0.5 | 10 [8, 12] | 8 [6, 10] | +2 [1, 3] |
| C1 | G2 | 4 | 0.2 | 6 [4, 8] | 7 [5, 9] | −1 [−1.8, −0.2] |
| C1 | G3 | 10 | 0.3 | 4 [3, 5] | 4.4 [3.4, 5.4] | −0.4 [−0.7, −0.1] |
| C2 | G1 | 6 | 0.2 | 9 [7, 11] | 8.4 [6.4, 10.4] | +0.6 [0.1, 1.1] |
| C2 | G2 | 15 | 0.5 | 7 [5, 9] | 8.8 [6.8, 10.8] | −1.8 [−2.5, −1.1] |
| C2 | G3 | 9 | 0.3 | 4.8 [3.8, 5.8] | 5.0 [4, 6] | −0.2 [−0.6, 0.2] |

### C1 target average

Using the C1 target weights gives mean losses of 7.40 for A and 6.72 for B, with A−B = +0.68. The favorable target average for B coexists with higher B loss in G2 and G3. These groups directly constrain a claim that every group benefits, while the weighted mean remains a valid arithmetic summary of the specified target composition.

### C2 target average and fixed composition

Using the current C2 group losses and C2 target weights gives 6.74 for A and 7.58 for B, with A−B = −0.84. Applying the C1 weights to these same C2 outcomes gives 7.34 and 7.46, with A−B = −0.12. The C2 point ordering thus favors A under both weighting compositions. This fixed-composition result shows that the unfavorable C2 ordering for B does not require the change to C2 target weights. It does not assign a causal share of the between-condition change to composition or within-group performance.

## Figure 1 caption

Synthetic paired loss comparisons across conditions C1 and C2 and groups G1–G3. Loss is in loss points; smaller loss is better and positive A−B favors B. Group intervals are the supplied paired 95% percentile cluster-bootstrap intervals, with 16, 4, and 10 evaluated independent clusters in C1 and 6, 15, and 9 in C2. Target weights are 0.5, 0.2, and 0.3 in C1 and 0.2, 0.5, and 0.3 in C2; they are not cluster proportions. Target-weighted differences are +0.68 in C1 and −0.84 in C2. Applying C1 target weights to C2 outcomes gives −0.12. These aggregate values are descriptive points without supplied aggregate confidence intervals. C1 G2 and G3 and C2 G2 constrain a uniform advantage claim for B. The current C2/G3 difference is −0.2 with an interval from −0.6 to 0.2, which includes zero. This revision updates the supplied textual caption; no new figure is supplied.

## Discussion

The frozen comparisons distinguish target-average ordering from group-wide advantage. C1 gives B a favorable average difference of +0.68, alongside G2 and G3 comparisons favoring A. C2 gives B an unfavorable average difference of −0.84, and its point ordering remains unfavorable at −0.12 with the C1 target weights. The established result is conditional ordering across the supplied comparisons, with the population represented by each average stated explicitly.

Both target composition and within-group losses change between conditions. Holding the C1 composition fixed for C2 makes the descriptive comparison easier to interpret: the C2 point ordering persists with the earlier weights. It does not identify why within-group losses changed, establish a causal explanation, or determine the statistical significance of the aggregate reversal. Bootstrap intervals cannot be treated as raw cluster observations to recover the missing joint uncertainty.

The supplied N1 summary motivates attention to comparison conditions but cannot resolve these questions. Without its full methods, unit-level data, interval procedure, and version history, differences in procedures, losses, evaluation units, or target populations remain unknown. Agreement would not establish replication, and disagreement would not establish a scientific contradiction. Its reported balanced-composition advantage is kept at the level of the available summary.

The demonstration supports reporting target weights, group results, and aggregate summaries together. This preserves the useful target-level comparison while making visible the groups that limit a uniform claim. A subsequent external evaluation would need a defined target population, appropriate independent units, retained group-level counterexamples, and data sufficient to evaluate aggregate uncertainty and transfer.

## Limitations

The evidence is a synthetic summary-data fixture. No independent external research was conducted, and cluster-level records are unavailable. Supplied group intervals support group-specific uncertainty statements; the missing aggregate draws and covariances prevent an aggregate confidence interval from being reconstructed here. The absence of a cross-condition interaction test prevents an inferential claim about a change in the differences.

Tuning preceded the frozen demonstration, so these comparisons are exploratory rather than prospectively registered evidence. No causal assignment, equivalence margin, or out-of-domain validation exists in the supplied record. These constraints bound causal interpretation, equivalence claims, and general deployment benefit. They leave intact the reproducible arithmetic and the distinction between a target average and uniform group-level ordering.

## Conclusion

In this exploratory synthetic fixture, the C1 target-average difference of +0.68 favors B while G2 and G3 favor A. The current C2 average difference is −0.84 and the fixed-C1-weight C2 difference is −0.12, both favoring A as descriptive point comparisons. Reporting the target population and group-level counterexamples together gives the average its appropriate meaning. The supported conclusion is conditional ordering within the frozen materials; causal attribution, aggregate significance, equivalence, and general deployment benefit remain unestablished.

## Evidence notes and availability

N1 is a supplied summary with its full source unavailable; N2–N4 are supplied complete local notes. They are development-fixture labels, not a formal bibliography or independently verified outside research. Data consist of the frozen six-row summary table; unit-level observations and aggregate uncertainty are unavailable. The retained Table 1 reproduces the current supplied values, and Figure 1 is a textual caption update.

No authors, affiliations, funding, approvals, participant consent, or published data identifier were supplied. No journal was selected. This synthetic development manuscript is not submission-ready.
