# Factual and claim comparison

The revision changes the manuscript's argument and expression, not its benchmark evidence. The manuscript and results CSV matched the frozen request's SHA-256 values before revision. Evidence locators below refer to the supplied manuscript sections and CSV row keys; E1–E4 remain internal memo labels, not newly retrieved sources. This is an agent review of a development fixture, not accountable human scientific verification or publication approval.

## Substantive changes and their support

| Original claim or presentation | Revised claim or presentation | Treatment and factual basis |
| --- | --- | --- |
| Title: “An apparently general improvement in an estimation system.” | “Conditional average gains in estimation: a fixed synthetic benchmark of methods A and B.” | Narrows the scope and names the synthetic setting. The two weighted comparisons have opposite signs; general improvement is unsupported. |
| Abstract: “We perhaps very tentatively examine whether method B is better than A…” | Opens with the decision question about an average reduction when acquisition conditions and stratum weights differ. | Removes rhetorical uncertainty, not inferential uncertainty. The supplied design has two conditions and different weights. |
| Abstract suggests B “could be an improved method” while mentioning limitations. | States the reference gain, reference S2 counterexample, changed-condition disadvantage and descriptive boundary. | Replaces an ambiguous method-level endorsement with the actual conditional result. Both directions remain prominent. |
| Reference weighted losses: A = 4.8, B = 4.36; difference = −0.44. | A = 4.80, B = 4.36; difference = −0.44, with the calculation shown in Results. | Preserved exactly; 4.80 is formatting, not a changed estimate. Verified from reference rows with weights 80 and 20. |
| Reference S2: A = 8.0, B = 9.0; intervals [7.5, 8.5] and [8.4, 9.6]. | Retained in Abstract, Results, Table 1 and Figure 1A. | No unfavorable result is removed or reframed as a favorable trade-off. These rows delimit the favorable average. |
| Reference S1: A = 4.0, B = 3.2; its intervals are in the CSV but not reported in the original Results prose. | Reports both supplied intervals and includes both rows in the full table and figure. | Adds existing evidence, not a new analysis: intervals [3.7, 4.3] and [2.9, 3.5]. |
| Changed weighted losses: A = 6.6, B = 7.52; difference = +0.92. | A = 6.60, B = 7.52; difference = +0.92, with calculation shown. | Preserved exactly; 6.60 changes display precision only. Verified from changed rows with weights 20 and 80. |
| Changed S1 losses 5.0 and 4.8; S2 losses 7.0 and 8.2, with four supplied intervals. | All retained in Results, Table 1 and Figure 1B. | No values, counts or interval endpoints altered. |
| Favorable average and unfavorable S2 presented as separate observations. | Explicitly states that B has lower S1 loss and higher S2 loss in both conditions. | A descriptive synthesis derived directly from the four within-stratum comparisons. It is not a hypothesis test or an all-settings claim. |
| Counts reverse from S1/S2 = 80/20 to 20/80. | Retained; clarifies that each method's condition-specific total weight is 100. | The total is the arithmetic sum of supplied n. It is not a claim of 100 actual participants or independent raw observations. |
| Intervals supplied with unknown dependence; no aggregate confidence interval or significance calculation. | Calls them supplied row 95% intervals; does not assign aggregate intervals, difference intervals, p-values or significance. | The “95%” label comes from the CSV preamble. Interval construction remains unspecified. No interpretation from overlap or separation is added. |
| Figure 1 is “intended” to show relevant comparisons. | Supplies the actual figure, separating row intervals from averages without bars. | A visualization of existing rows plus the declared weighted means; no new observations or estimated uncertainty. Shape cues and alt text support readability. |
| “We do not know whether our very limited work is sufficiently interesting…” | States the contribution as a precise boundary between a supported average gain and an unsupported robustness claim. | Removes unsupported self-assessment. Adds no priority, novelty, superiority or publication claim. |
| Acquisition conditions are not assigned interventions; mechanism is unknown. | Retains the noncausal interpretation and explains that condition and weights change together. | No claim that mixture, acquisition or method sensitivity caused the reversal; no numerical causal decomposition is introduced. |
| Future validation would hold mixture fixed while changing acquisition, and separately vary mixture under fixed acquisition. | Retains this design as prospective and explicitly unperformed [E4]. | No proposed validation is represented as completed evidence. |
| Repeated generic caveats and editorial comments about how to strengthen presentation. | Consolidates concrete inferential boundaries in Methods and Discussion; removes editorial advice from manuscript prose. | Synthetic status remains at the opening, in Methods, the displays and end matter. The limitations that change interpretation are preserved. |
| No empirical data, participants, ethics approvals or publication claims; E1–E4 internal memos. | Retains these declarations and identifies the separate memos as unsupplied. | No authors, grants, conflict declarations, ethics identifiers, external scientific references or journal compliance assertions are invented. |

## Quantitative reconciliation

| Comparison | A weighted loss | B weighted loss | B − A | Weights S1/S2 | Supported description |
| --- | ---: | ---: | ---: | --- | --- |
| Reference | 4.80 | 4.36 | −0.44 | 80/20 | B has the lower weighted average. |
| Changed | 6.60 | 7.52 | +0.92 | 20/80 | A has the lower weighted average. |

The check script verifies all eight table rows against the frozen CSV, recomputes both weighted averages and their signed differences using decimal arithmetic, checks the condition-specific denominators, and compares the editable Word text and table with the Markdown. It also checks the plotted data record against the source. No resampling, model fitting, raw-data reconstruction or inferential test was performed.

## Claim boundary retained

Supported: a reference-average gain of 0.44; a changed-condition average disadvantage of 0.92; lower B loss in S1 and higher B loss in S2 in each setting; the need to report these comparisons together when describing the scope of the gain.

Unsupported and absent from the revision: general robustness; universal superiority or inferiority; causal acquisition or mixture effects; statistical significance, equivalence or aggregate confidence intervals; empirical validation; a newly established mechanism; literature-gap or publication-readiness claims. The revised conclusion requests separate validation of acquisition and mixture changes without claiming that validation has occurred.
