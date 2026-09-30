# Factual and semantic comparison

## Compared subjects and evidence

The baseline is the complete supplied `fixtures/rc2/long-manuscript.md`, embedded in `long-revision.comparison.0.json`, with file SHA-256 `bbaafe34c9cce3dec51214f8b1dd9af386fe19c445dce3dfcb3b75ede3557ce3`.

The reviewed final subject is `manuscript.md`, SHA-256 **`ce4f35c9e57b0a359c78fe1c61efce06fa2b170607cd5f2e1b0a137400a9eb66`**. This comparison concerns the complete delivered file after the English anti-defensive-writing pass.

| Evidence ID | Authoritative support | Identity and scope |
|---|---|---|
| E-T | Current `fixtures/rc2/figure-results.csv` | SHA-256 `e2d5923ff6b2d1a95321ece8956a892ad4416d051c8c763c9ea31881a306374c`; all six rows, counts, target weights, group means, marginal intervals, and paired-difference intervals |
| E-U | `fixtures/rc2/evidence-notes.md`, frozen update | SHA-256 `b49f1fca8a10230480d33f0cc8ce32e988daea811269adafe296785f7f01f044`; older-to-current correction and N1–N4 provenance/inference boundaries |
| E-D | Supplied complete long draft | Baseline identity above; pairing within condition/group, independence between conditions, loss definition, interval description, and existing claims to preserve or correct |

All supplied material-file hashes matched the files at the request's specified paths. Evidence IDs here are local fixture mappings, not citations to published research or a record of human verification.

## Numerical changes and preserved facts

| Fact | Baseline | Delivered manuscript | Locations and reason |
|---|---|---|---|
| C2/G3 B loss | 5.1 | 5.0 | Materials, Table 1, and C2 Results; required E-U correction, confirmed by E-T |
| C2/G3 A loss | 4.8 | 4.8 | Table 1 and C2 Results; unchanged |
| C2/G3 paired A−B | −0.3 | −0.2 | Table 1, C2 Results, and Figure 1 caption; 4.8 − 5.0 |
| C2 target-weighted A loss | 6.74 | 6.74 | Abstract and C2 Results; unchanged |
| C2 target-weighted B loss | 7.61 | 7.58 | Abstract and C2 Results; 0.2×8.4 + 0.5×8.8 + 0.3×5.0 |
| C2 target-weighted A−B | −0.87 | −0.84 | Abstract, C2 Results, caption, Discussion, and Conclusion; 6.74 − 7.58 |
| C2 A loss with C1 weights | 7.34 | 7.34 | Abstract and C2 Results; unchanged |
| C2 B loss with C1 weights | 7.49 | 7.46 | Abstract and C2 Results; 0.5×8.4 + 0.2×8.8 + 0.3×5.0 |
| C2 A−B with C1 weights | −0.15 | −0.12 | Abstract, C2 Results, caption, Discussion, and Conclusion; 7.34 − 7.46 |
| C1 target losses and difference | A 7.40; B 6.72; A−B +0.68 | Same | Abstract, C1 Results, caption, Discussion, and Conclusion; unchanged |
| All other group means/differences | C1: (10, 8, +2), (6, 7, −1), (4, 4.4, −0.4); C2/G1: (9, 8.4, +0.6); C2/G2: (7, 8.8, −1.8) | Same, with consistent display precision | Table 1 and group Results; no new observations |
| Independent cluster counts | C1 (16, 4, 10); C2 (6, 15, 9); 30 per condition | Same | Materials, Table 1, caption; not treated as six individual observations |
| Target weights | C1 (0.5, 0.2, 0.3); C2 (0.2, 0.5, 0.3) | Same | Methods, Table 1, caption; never replaced with cluster proportions |
| Group interval values | Current source supplies all marginal and paired intervals; baseline narrates only some | All current source intervals transcribed in Table 1 | E-T unchanged; added reporting is not new interval estimation |
| C2/G3 paired interval | Not explicitly interpreted in baseline Results; current source provides [−0.6, 0.2] | Reported and interpreted as spanning zero | Table 1, C2 Results, caption; no equivalence or resolved direction claim |
| Contrast between the two C2 weighted differences | Not numerically stated | −0.84 − (−0.12) = −0.72 loss points | Discussion; transparent arithmetic from E-T, not a causal effect or interaction estimate |

The corrected C2/G3 value lowers each reported C2 B aggregate by 0.03 because G3 retains weight 0.3 in both compositions. Each A−B aggregate consequently increases by 0.03. No current-manuscript occurrence of the obsolete 5.1, 7.61, 7.49, −0.87, or −0.15 remains; historical values appear only in this comparison.

## Scientific meaning before and after

| Scientific subject | Baseline meaning | Final meaning and review |
|---|---|---|
| Core contribution | Tentatively describes a conditional average comparison | States the established distinction directly: population-specific ranking can coexist with opposite group-level orderings. No new method, novelty priority, or universal performance advantage is claimed. |
| Uniform benefit | C1 average favors B while G2 and G3 do not | Preserved and made central. C1/G2 and C1/G3 remain explicit counterexamples with negative paired intervals. The writing pass did not hide unfavorable groups. |
| C2 ordering | Old target and fixed-weight point differences favor A | Corrected current differences still favor A. This remains a descriptive point ordering; it is not expanded to a uniform C2 benefit for A. |
| C2/G3 uncertainty | Old point difference reported without its uncertainty interpretation | Current point difference −0.2 favors A, while its supplied interval spans zero. The manuscript explicitly distinguishes that point ordering from an unresolved direction and from equivalence. |
| Composition and condition | Changing conditions and target composition are distinct questions; fixed weights are descriptive | Preserved and sharpened. Both C2 compositions have negative differences, so changing weights within C2 changes magnitude without reversing the ranking. The between-condition sign change persists at common C1 weights. No claim that composition alone causes the sign change is made. |
| Causal strength | No causal intervention or mechanism attribution | Preserved in Methods, Discussion, and Limitations. The new −0.72 arithmetic contrast is not interpreted causally. |
| Group versus aggregate inference | Group intervals cannot determine aggregate reversal significance | Preserved. No aggregate confidence interval, p value, significance claim, or cross-condition interaction test is fabricated. |
| Pairing and units | A/B paired within groups/conditions; clusters independent between conditions | Preserved. The paired group intervals are used directly; a paired cross-condition design is not invented. Six summary rows are not treated as independent individual observations. |
| Marginal interval overlap | Does not determine the paired-difference interval's zero inclusion | Preserved explicitly in Methods. No overlap-based significance argument is introduced. |
| Research history | Tuning preceded the demonstration; exploratory | Preserved throughout. No prespecification, preregistration, causal assignment, equivalence margin, or out-of-domain validation is implied. |
| N1 provenance | Summary available, full methods/data missing; not independent validation | Preserved with the additional E-U details that the interval procedure and version history are unavailable. Neither replication nor contradiction is claimed. |
| N2–N4 | Local notes with distinct roles | Preserved and mapped explicitly. Complete local availability does not turn these fixture labels into published or independently verified external research. |
| Generalization | No general deployment guarantee | Preserved through the synthetic banner, exploratory Methods, concrete Limitations, and bounded conclusion. No deployment recommendation is added. |
| Missing declarations | Authors, affiliations, funding, approvals, consent, published data identifier not supplied | Preserved as unavailable. No missing declaration is filled with a plausible value or “none”; the file remains explicitly not submission-ready. |

## Editorial restructuring

The title and first abstract sentences now identify the actual supported contribution. The Introduction states the question and contribution before discussing incomplete prior-note provenance. Methods consolidate material, evaluation units, target-weighted formulas, and interval status. Results retain both favorable and unfavorable groups, include the authoritative table, and separate C1 from C2 and the fixed-composition comparison. The supplied textual Figure 1 caption is updated; no figure image or new evaluation was produced.

The preparatory-operation paragraph and repeated statements that the work “perhaps” needs more caution were removed. Their removal changes presentation, not research history: the performed weighted calculations are reproducible, and exploratory status and concrete inferential limits remain explicit. Discussion distinguishes arithmetic contrasts from inference and comparison from replication. Limitations are concentrated in one substantive section. Conclusion reinforces the conditional result without adding a new claim.

## Actual review and checks

The current Agent reviewed the full draft against E-T/E-U/E-D, applied K-Dense `scientific-writing`, then applied the designated English `anti-defensive-writing-en` to the complete manuscript under the project's evidence-preserving adaptation. The anti-defensive source's suggestions to suppress unfavorable evidence, change the evaluation frame to obtain a win, or omit necessary limits were not followed. The original metric, groups, weights, counterexamples, and causal/inferential strength were retained.

`check_revision.py` ran successfully after the final expression pass. It checks frozen input hashes, all six exact table rows including intervals, within-row subtraction, cluster counts and weight sums, the three weighted summaries, obsolete-number absence, and corrected aggregate differences in the Abstract, caption, and Conclusion. It also checks that key boundary statements remain present and that this comparison binds the delivered manuscript hash. These machine checks support numerical and structural consistency; the semantic table records the current Agent's full-text review. Human scientific verification, external peer review, journal compliance, and submission approval were not performed.
