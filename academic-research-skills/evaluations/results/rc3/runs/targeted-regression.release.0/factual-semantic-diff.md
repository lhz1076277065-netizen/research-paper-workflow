# Factual and semantic comparison of the complete revision

Baseline: the complete supplied `long-manuscript.md`. Authority for updates: `evidence-notes.md` and the current `figure-results.csv`. Subject of this audit: the final `manuscript.md` in this run directory. N1–N4 are fixture labels, not publications. No external source or new experiment was added.

## Authorized numeric changes

| Quantity and comparison | Before | Final | Source / calculation |
|---|---:|---:|---|
| C2/G3 loss_B | 5.1 | 5.0 | Current CSV row C2/G3 |
| C2/G3 A−B | −0.3 | −0.2 | 4.8 − 5.0 |
| C2 target-weighted loss_A | 6.74 | 6.74 | 0.2×9 + 0.5×7 + 0.3×4.8 |
| C2 target-weighted loss_B | 7.61 | 7.58 | 0.2×8.4 + 0.5×8.8 + 0.3×5.0 |
| C2 target-weighted A−B | −0.87 | −0.84 | 6.74 − 7.58 |
| C2 loss_A with C1 weights | 7.34 | 7.34 | 0.5×9 + 0.2×7 + 0.3×4.8 |
| C2 loss_B with C1 weights | 7.49 | 7.46 | 0.5×8.4 + 0.2×8.8 + 0.3×5.0 |
| C2 A−B with C1 weights | −0.15 | −0.12 | 7.34 − 7.46 |

Affected numeric assertions were synchronized in the Abstract, C2 and fixed-composition Results, Figure 1 caption and Conclusion. Discussion and Introduction were checked for the corresponding direction and scope. The final manuscript does not retain the obsolete C2 values as current findings.

The revision states arithmetic already supported by the current table and supplied prior figure/caption: the fixed-weight change from C1 is −0.80, the change under each condition's respective weights is −1.52, and their ratio is 52.6% (53% rounded). These are derived descriptive comparisons, not additional observations or a causal decomposition. Under the old values the analogous changes would have been −0.83 and −1.55; those are not used in the final manuscript.

## Preserved facts and supplied additions

| Fact or relation | Before / evidence | Final treatment |
|---|---|---|
| Metric and direction | Lower loss preferred; positive A−B favors B | Preserved throughout; “paired improvement” becomes the more neutral “paired difference” |
| C1 outcomes and weighted values | Loss_A 7.40, loss_B 6.72, difference +0.68 | Unchanged |
| Group and independent-unit scope | C1 counts 16/4/10; C2 counts 6/15/9; 30 clusters in each condition | Unchanged; six summaries are not treated as six independent individual observations |
| Pairing and between-condition independence | Same clusters for A/B within groups; conditions independent | Preserved in Methods and caption |
| Target weights | C1 0.5/0.2/0.3; C2 0.2/0.5/0.3 | Preserved; no substitution of cluster proportions |
| C1 paired intervals | G1 [1,3]; G2 [−1.8,−0.2]; G3 [−0.7,−0.1] | All retained unchanged |
| C2 paired intervals | CSV: G1 [0.1,1.1]; G2 [−2.5,−1.1]; G3 [−0.6,0.2] | All reported; the old draft omitted G3's interval, which is now made explicit |
| Uncertainty type | Supplied 95% percentile cluster-bootstrap intervals within groups | Preserved; marginal overlap does not replace paired-difference uncertainty |
| Missing joint uncertainty | No cluster observations, aggregate draws or cross-group covariances | Preserved; no aggregate or change/ratio interval is invented |
| Research history | Tuning preceded the fixture; exploratory | Preserved; no prospective or confirmatory relabeling |
| Unperformed inference | No causal assignment, equivalence margin, aggregate CI or interaction test | Preserved; no causal, equivalence, aggregate significance or interaction claim |
| N1 access level | Summary; full methods and data unavailable | Kept at summary level; missing interval procedure and version history explicitly retained from the frozen notes |
| N2–N4 status | Complete local notes | Preserved as fixture evidence, not independently verified publications |
| Authorship and readiness | No supplied authors, approvals, funding or journal | Retained as unavailable; no submission-readiness claim |

## Semantic and argument changes

**Title, Abstract and Introduction.** The old title and opening hedged the usefulness of the comparison and described an attempt to explore it. The final title and opening state the established contribution: target-average ordering is conditional and coexists with group exceptions. The claim remains restricted to the synthetic comparisons. No unverified novelty, universal performance or new method claim is introduced.

**Materials and uncertainty.** The procedural paragraph about inspecting notes, calculating averages and considering a figure was removed from the scientific narrative. Its actual operations are recorded in `operation.md`. The final Methods instead defines the estimand, weights, units and fixed-weight calculation. Missing aggregate uncertainty and exploratory status remain explicit.

**Results.** The six group comparisons and adverse findings are retained. C1 G2/G3 constrain a uniform advantage claim for B; C2 G1 constrains a uniform advantage claim for A. The final text adds the supplied C2/G3 interval and explains that its negative point estimate is compatible with either direction. “No equivalence” is preserved, not converted into proof of no difference.

**Direction versus magnitude.** The old text said the C2 ordering remained unfavorable to B under C1 weights. The final text makes its implication explicit: changing to C2 weights is not required for this point-estimate reversal. It separately states the larger negative magnitude obtained with C2 weights. This is an interpretation of the specified fixed-weight comparison, not an assertion that target composition never causes reversals in other settings. The 52.6% retained magnitude does not prove why the ordering changes.

**Discussion, Limitations and Conclusion.** Repeated apologies and generic warnings were consolidated. Limitations that affect the inference remain in the uncertainty section, focused Limitations, and brief Abstract/Conclusion bounds. The final text retains the absence of aggregate significance, causal attribution, equivalence and deployment evidence. It neither hides unfavorable results nor changes the primary metric or groups to make one procedure win.

**Evidence access and scope.** N1 remains a summary; no unobserved methods or replication are assigned to it. N1 agreement/disagreement is not treated as replication/contradiction without comparability and independence. Reading operation A/B and the sentence task were not merged into this manuscript.

## Actual writing and audit

The current Agent applied K-Dense `scientific-writing` to material intake, evidence-bound argument structure, all manuscript sections, numerical reconciliation and scientific fidelity. It then applied the designated English `anti-defensive-writing` pass to the complete draft, followed by a fact/meaning audit of the resulting manuscript. The frozen project's evidence-preserving adaptation takes precedence over upstream advice that would omit adverse findings or suppress necessary limitations. No external model/service or human scientific approval was claimed.

The local `check_outputs.py` recomputes the current weighted values with Decimal arithmetic, checks the input hashes and manuscript coverage/stale values, matches the SVG's six textual intervals, and verifies the sentence's unchanged numbers and association wording. This supplements the manual relation, scope and inference checks above; it does not certify scientific validity or simulate peer review.
