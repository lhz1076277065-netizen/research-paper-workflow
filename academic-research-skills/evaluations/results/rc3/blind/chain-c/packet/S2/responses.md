# Point-by-point developmental response

SYNTHETIC / AUTHOR-REVIEW DRAFT. The comments and journal are fictional. No editor decision, assigned review, acceptance, submission or reviewer contact is implied. Baseline: supplied author working draft v2; revised file: `submission/anonymous/manuscript-v3.md`. Locations below refer to the final Markdown's one-based lines, not the older draft. The supplied comments are retained in `baseline/review-comments.md`; actual text changes are in `draft-v2-to-v3.diff`.

## R1 — accepted: units, target and interval explanation

Comment: “Explain independent units, technical repetitions, target weights, the interval object, and why observed mixture and target mixture give different directions.”

Response: We have added the sampling object and weighting formulas to the Methods and made the directional change explicit in the Results. The supplied record specifies eight independent paired units, four per stratum. Technical repetitions were averaged within unit and method after conversion, so they do not create additional independent sampling units. We have also made clear that independence is a supplied premise, not independently verified from unavailable raw records.

The target weights were fixed before measurement at 0.8:0.2, while the equal sampled mixture uses 0.5:0.5. With the supplied stratum means, 0.8 × (−1.00) + 0.2 × (+3.00) = −0.20 and 0.5 × (−1.00) + 0.5 × (+3.00) = +1.00. The quantities answer different mixture-specific questions and reverse point-estimate direction using the same stratum contrasts. The reported 95% percentile interval [−0.60, 0.20] belongs to the fixed-weight target contrast, using within-stratum resampling of paired units. Pairing and the unit-level resampling object remain intact.

Actual changes and locations: manuscript §2.1 (line 17), §2.2 (line 21), §2.3 (line 25), and §3 (lines 29–33); Supplement S1.1–S1.3 (lines 5–19); Figure 1 and caption (caption line 5). Supporting record: `baseline/evidence.md`, `baseline/draft-v2.md` Methods and `baseline/supplement-v2.md`. We checked the aggregate arithmetic; no raw-data or bootstrap replication was performed.

## R2 — reasoned disagreement: retain g2

Comment: “Drop g2 from the main text and figure to make the contribution stronger. The g2 result is negative for A, so it cannot help the paper.”

Response: We retain g2 because the opposite stratum directions are the evidence explaining why changing mixture weights changes the aggregate direction. Under the stated lower-is-better score convention, g2's A−B of +3.00 favors B. Removing g2 would conceal an essential boundary and prevent the reader from checking the diagnostic. It would also leave a misleading impression of universal advantage for A.

We have corrected the original Results sentence that said g2 supported A, and reorganized the contribution around the mixture diagnostic. Both strata and both aggregates remain visible in Figure 1; no unfavorable result is hidden or relocated out of the main argument.

Actual changes and locations: title (line 1), Abstract (line 7), §3 (lines 29 and 31), §4 (line 37), and §5 (line 45); Figure 1 contains a g2 row at +3.00; caption line 5; Supplement S1.2 (line 11). Supporting record: `baseline/evidence.md` and the supplied caption's lower-score convention. This is disagreement with omission, not a request for new experiments.

## R3 — reasoned disagreement: preserve independent-unit count

Comment: “Count all technical repeats as independent observations for a narrower interval. Cite Efron to establish the independence assumption.”

Response: Technical repeats on the same unit are measurement repetitions, not new independent units in the supplied design. We retain eight independent paired units, four per stratum. Inflating the independent-unit count would change the resampling object and could misrepresent precision. No new or narrower interval was computed, and the supplied [−0.60, 0.20] interval is retained unchanged.

Efron's DOI identity is present in the supplied metadata, but its full text was not obtained. Those metadata cannot establish independence of this task's units or validate this task's interval for every population. We therefore removed the unsupported Efron statements and unused final reference; the original bibliographic identity remains in the baseline and citation audit.

Actual changes and locations: §2.1 (line 17), §2.3 (line 25), and §3 (line 33); Supplement S1.1/S1.3; caption line 5. Final References (line 57) contains only the bounded Rosenbaum/Rubin item. Supporting records: unit-level averaging and resampling descriptions in `baseline/draft-v2.md` Methods, `baseline/supplement-v2.md`, and Efron's metadata-only availability in `baseline/source-availability.md`. Original analysis code, technical-repeat counts and resampling outputs remain unavailable.

## R4 — reasoned disagreement: no causal or equivalence claim

Comment: “The propensity-score citation establishes causal interpretation; keep the causal title and abstract. Also describe the interval crossing zero as equivalence.”

Response: The supplied abstract-level description of Rosenbaum and Rubin concerns assignment probabilities conditional on observed covariates and adjustment for imbalance in those observed variables. It supplies no evidence about this comparison's assignment, unmeasured confounding or weighted interval. There is no causal assignment, confounding measurement or causal adjustment in the record. We therefore changed the title and Abstract to a descriptive mixture diagnostic and removed the claim of causal advantage. The original [2] is renumbered [1] and used only for that observed-covariate background, with its availability limit stated.

The interval contains zero and both signs. Without an equivalence margin and registered equivalence test, crossing zero cannot establish practical equivalence or an exact absence of a difference. We retain the estimate and interval, state the uncertainty in direction, and remove the equivalence interpretation throughout the Abstract, Results, caption and supplement.

Actual changes and locations: title (line 1), Abstract (line 7), §3 (line 33), §4 (line 39), and References (line 57); caption line 5 and Supplement S1.3 (lines 17–19). Supporting records: `baseline/evidence.md` for absent causal/equivalence evidence and `baseline/source-availability.md` for the limited abstract-level content. Neither source full text nor an implementation was read or run.

## R5 — accepted: shorter introduction and explicit contribution

Comment: “I prefer a shorter introduction and a clearer contribution sentence. This is an expression request, not a demand for additional experimental evidence.”

Response: We shortened the Introduction and replaced the indirect usefulness claim with an explicit diagnostic contribution: “This note diagnoses that dependence by comparing stratum-specific paired contrasts under sampled and prespecified target weights.” The Introduction now has two sentences and fewer whitespace-delimited words than the supplied v2 Introduction. This is a change in expression; it adds no experimental evidence and does not claim a new predictive or causal method.

Actual change and location: §1 Introduction (line 11). The full manuscript also underwent evidence-preserving expression review; `expression-diff.diff` links the scientifically corrected draft to the final text. g2, the zero-crossing interval, the target mixture and the descriptive inference scope remain unchanged.

## Additional consistency and declaration repairs

We removed the unsupported all-author/ethics/open-raw-data approvals in v2. Author approval, funding, conflicts, human-participant status and ethics determination remain UNKNOWN in manuscript Declarations (line 53) and the separate title page. Raw-unit redistribution is prohibited under the supplied license; the specific controlled-access statement and unsent request draft do not promise approval. These edits are part of the actual revised files, not claims that declarations have been approved.

Status: local response and revisions completed for author review. No resubmission, reviewer contact, author signature or acceptance has occurred.
