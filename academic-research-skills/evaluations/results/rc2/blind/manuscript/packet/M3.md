# Target averages and group-level comparisons diverge: a synthetic paired-loss demonstration

Synthetic Skill-development manuscript. This editable development fixture is not a research publication. No human research was conducted.

## Abstract

A favorable target average can coexist with opposite group-level orderings. This exploratory synthetic demonstration separates population-specific ranking, group-level heterogeneity, and changes in target composition using the frozen paired comparisons of procedures A and B. The materials contain six group summaries from two evaluation conditions, with 30 independent clusters per condition. Smaller loss is preferred, and positive A−B favors B. In C1, target-weighted losses of 7.40 for A and 6.72 for B give +0.68 loss points, although B has higher loss in G2 and G3. In C2, losses of 6.74 and 7.58 give −0.84 points. Applying the C1 target weights to the C2 outcomes gives 7.34 and 7.46, or −0.12 points. The average ordering thus changes between conditions even under a common composition. The supplied C2/G3 paired-difference interval includes zero, and aggregate intervals are unavailable. Reporting target weights and group-level differences together makes the scope of the average advantage explicit; these descriptive comparisons do not establish causal attribution.

## Introduction

An average comparison answers a question about the population represented by its weights. It need not answer whether each constituent group has the same ordering. When evaluation conditions change, two features can change together: the procedures' losses within groups and the target composition used to combine those losses. Distinguishing these features is necessary to interpret a change in an average without attributing it to an untested mechanism.

The supplied fixture permits a direct examination of that distinction. Procedures A and B are compared in three groups under each of two conditions, C1 and C2. We ask whether a favorable target average for B extends to every group, whether the average ordering changes between conditions, and whether the C2 ordering persists when the earlier target composition is retained. These questions use the original loss metric, groups, and target weights.

The contribution is a reproducible account of a conditional average comparison. The supplied results show that a favorable C1 average coexists with group-level counterexamples, that the C2 average has the opposite ordering, and that this ordering persists under the C1 weights. Presenting those results together separates a population-specific average from a claim of uniform benefit and separates a descriptive composition comparison from causal explanation.

The evidence notes distinguish the provenance of the comparison. N1 supplies a summary of an earlier average advantage under balanced composition, but its full methods, unit-level data, interval procedure, and version history are unavailable. Direct comparability with this fixture remains unresolved. N2 defines target weights separately from observed cluster proportions, N3 records that tuning preceded this exploratory demonstration, and N4 defines the scope of the supplied intervals. These are local fixture notes, not published evidence of replication.

## Materials and comparison

### Frozen materials and evaluation units

The materials are the current `figure-results.csv` and four local evidence notes, N1–N4. The table contains six synthetic group summaries. C1 includes 30 independent clusters: 16 in G1, 4 in G2, and 10 in G3. C2 includes 30: 6 in G1, 15 in G2, and 9 in G3. Procedures A and B were evaluated on the same clusters within each condition and group; clusters are independent between conditions. Each table row summarizes a group and is not an individual observation. Treating the six rows as six independent observations would discard the actual evaluation units and pairing.

The current frozen table is authoritative, including a C2/G3 B loss of 5.0. No cluster-level records are available. C1 and C2 are condition labels; operational definitions of the procedures and conditions were not supplied. The means and intervals are retained as supplied, rather than reconstructed from unavailable observations.

### Loss and target-weighted comparisons

Loss is measured in loss points, with smaller values preferred. For condition c and group g, let L_A,cg and L_B,cg denote the supplied group means and d_cg = L_A,cg − L_B,cg. A positive difference favors B; a negative difference favors A. For target weights w_g summing to one, the comparison is

Δ_c(w) = Σ_g w_g d_cg = Σ_g w_g L_A,cg − Σ_g w_g L_B,cg.

The C1 target weights for G1–G3 are (0.5, 0.2, 0.3); the C2 weights are (0.2, 0.5, 0.3). As specified in N2, these weights define the decision population and are not replaced by observed cluster proportions. We report each condition using its own target weights. A descriptive sensitivity calculation applies the C1 weights to the C2 group means, retaining the C2 outcomes. It holds target composition fixed without imposing a causal intervention.

### Uncertainty and analysis status

The supplied marginal intervals for A and B and the paired-difference intervals are 95% percentile cluster-bootstrap intervals within a condition and group. The difference intervals reflect paired evaluation. Overlap of the two marginal loss intervals does not determine whether the interval for A−B includes zero.

N3 records that tuning preceded the demonstration, so the comparisons are exploratory. N4 supplies neither aggregate confidence intervals nor a cross-condition interaction test. Cluster observations, aggregate bootstrap draws, and cross-group covariances are unavailable. We therefore retain the supplied group intervals and report aggregate differences as descriptive point values. No aggregate significance test, equivalence analysis, or causal estimate is inferred from them.

## Results

### Group-level comparisons

Table 1 retains all six frozen rows, including the updated C2/G3 value. Counts refer to independent evaluated clusters; weights refer to the target population. All losses and differences are in loss points. Brackets contain the supplied 95% percentile cluster-bootstrap intervals; the A−B intervals are paired.

**Table 1. Frozen synthetic group-level loss comparisons.**

| Condition | Group | Clusters | Target weight | A loss [95% interval] | B loss [95% interval] | A−B [paired 95% interval] |
|---|---|---:|---:|---|---|---|
| C1 | G1 | 16 | 0.5 | 10.0 [8.0, 12.0] | 8.0 [6.0, 10.0] | +2.0 [1.0, 3.0] |
| C1 | G2 | 4 | 0.2 | 6.0 [4.0, 8.0] | 7.0 [5.0, 9.0] | −1.0 [−1.8, −0.2] |
| C1 | G3 | 10 | 0.3 | 4.0 [3.0, 5.0] | 4.4 [3.4, 5.4] | −0.4 [−0.7, −0.1] |
| C2 | G1 | 6 | 0.2 | 9.0 [7.0, 11.0] | 8.4 [6.4, 10.4] | +0.6 [0.1, 1.1] |
| C2 | G2 | 15 | 0.5 | 7.0 [5.0, 9.0] | 8.8 [6.8, 10.8] | −1.8 [−2.5, −1.1] |
| C2 | G3 | 9 | 0.3 | 4.8 [3.8, 5.8] | 5.0 [4.0, 6.0] | −0.2 [−0.6, 0.2] |

### C1: a favorable average with group-level counterexamples

In C1, the G1 paired difference is +2.0, whereas G2 and G3 have differences of −1.0 and −0.4. Their supplied paired intervals lie on the corresponding sides of zero (Table 1). Thus B has lower loss in G1 and higher loss in G2 and G3.

With the C1 target weights, the mean losses are 7.40 for A and 6.72 for B. The difference of +0.68 favors B for this target population. That average coexists with two groups in which B has higher loss. The group comparisons limit a uniform-benefit claim without invalidating the arithmetic of the target average.

### C2: the opposite average ordering persists under fixed composition

In C2, G1 has a paired difference of +0.6 and G2 a difference of −1.8, with the supplied intervals respectively above and below zero. The updated G3 losses are 4.8 for A and 5.0 for B, giving −0.2. Its interval, [−0.6, 0.2], includes zero and differences in either direction. The G3 point ordering favors A, but the interval does not resolve the direction or establish equivalence.

Using the C2 target weights gives mean losses of 6.74 for A and 7.58 for B, with a difference of −0.84. Applying the C1 weights to the same C2 outcomes gives 7.34 for A and 7.46 for B, with a difference of −0.12. Both C2 weighted comparisons favor A at the point-estimate level. The sign change from C1 therefore persists when the target composition is held fixed.

## Figure 1 caption

**Figure 1. Synthetic paired loss comparisons in C1 and C2.** Smaller loss is preferred, and positive A−B favors B. The group intervals are the supplied paired 95% percentile cluster-bootstrap intervals. Cluster counts for G1–G3 are (16, 4, 10) in C1 and (6, 15, 9) in C2. Target weights are (0.5, 0.2, 0.3) for C1 and (0.2, 0.5, 0.3) for C2. Target-weighted differences are +0.68 in C1 and −0.84 in C2; applying C1 weights to C2 outcomes gives −0.12 loss points. Aggregate values are descriptive points without supplied aggregate intervals. C1/G2 and C1/G3 provide counterexamples to a uniform advantage for B; C2/G3 has a paired difference of −0.2 with an interval of [−0.6, 0.2], which includes zero.

## Discussion

The comparison establishes a distinction between an average ordering and a uniform group-level ordering. In C1, the target average favors B even though G2 and G3 favor A. In C2, the target average favors A. Retaining the C1 target weights for C2 leaves the C2 point ordering unchanged. Together, these comparisons show why an average advantage must be attached to its condition and target population.

The fixed-composition calculation also sharpens the interpretation of the between-condition change. Using the C2 group means, the C1 weights give −0.12 and the C2 weights give −0.84; the difference between those two descriptive summaries is −0.72 loss points. Changing the target weights therefore changes the magnitude of the C2 comparison without changing its sign. Comparing the two conditions under the common C1 weights still yields opposite signs, +0.68 and −0.12. These arithmetic contrasts separate the questions of target composition and within-group outcomes. They do not identify why those outcomes differ or quantify a causal contribution of composition.

The group intervals and aggregate values answer different inferential questions. Group-level evidence includes a C2/G3 interval spanning zero, alongside directional intervals in the other groups. Aggregate points have no supplied joint uncertainty. Consequently, the observed change in average ordering cannot be promoted to a statistically established aggregate reversal or cross-condition interaction. The intervals also cannot be treated as raw observations to recover missing cluster-level structure.

N1 motivates attention to comparison conditions but does not validate this fixture. Without its full source and version history, neither comparability nor a separate evaluation cohort can be established. Agreement would not demonstrate replication, and disagreement would not establish a scientific contradiction. A subsequent external evaluation would need to define the target population, document procedures and conditions, retain group-level counterexamples, and supply uncertainty based on the appropriate independent units.

## Limitations

This is a synthetic demonstration based on summary data. The absence of cluster-level records and joint uncertainty prevents aggregate uncertainty estimation from the supplied materials. The demonstration follows tuning and lacks preregistration, causal assignment, an equivalence margin, and out-of-domain validation. These limits constrain confirmatory inference, causal explanation, equivalence claims, and transfer beyond the fixture. They do not prevent reproducing the weighted arithmetic or distinguishing average and group-level orderings.

## Conclusion

In this frozen synthetic comparison, a C1 target-average advantage for B of +0.68 loss points coexists with unfavorable G2 and G3 comparisons. The updated C2 target difference is −0.84, and the fixed-C1-weight C2 difference is −0.12. The average ordering changes between conditions even at a common target composition. Reporting target weights and group-level differences together makes the supported comparison explicit and preserves the counterexamples that bound its interpretation.

## Evidence notes and availability

N1 is a supplied summary whose full source is unavailable. N2–N4 are supplied complete local notes: N2 defines target weights and independent evaluation units, N3 records exploratory status, and N4 defines the group-level intervals and unavailable aggregate or interaction inference. N1–N4 are development-fixture labels, not published citations or a formal bibliography.

The available data consist of the frozen summary table. The original draft and update remain in the supplied fixture materials. No authors, affiliations, funding information, approvals, participant consent, or published data identifier were supplied. This editable development-fixture manuscript is not submission-ready.
