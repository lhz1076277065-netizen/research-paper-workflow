SYNTHETIC DEVELOPMENT DRAFT — authorized local response to fictional comments; not sent, approved or accepted.

# Response to the supplied developmental comments
Baseline: supplied draft-v2.md and review-comments.md. Revised file: manuscript-v3-anonymous.md. The line locations below refer to that final editable Markdown source, not converted DOCX/PDF pagination. Real changes are recorded in manuscript-v2-to-v3.diff; Figure 1, caption-v3.md and supplement-v3.md are revised supporting outputs. No raw-data reanalysis or new experiment was performed.

## R1 — accepted: clarify design, mixtures and uncertainty
> R1. Explain independent units, technical repetitions, target weights, the interval object, and why observed mixture and target mixture give different directions.

Response: We clarified that the inference and resampling object is a paired independent unit: eight units, four per stratum, with A and B measured on the same unit. Technical repetitions were averaged within unit/method after unit conversion and were not additional independent units. Their counts and conversion details remain unavailable. We identify the target weights 0.8/0.2 as fixed before measurement and the observed weights 0.5/0.5 as implied by four units in each stratum. We added the weighted-contrast formula and both numerical calculations. The target interval is named as the supplied 95% within-stratum paired-unit bootstrap percentile interval, with paired units resampled and target weights reapplied. Its implementation is not claimed to have been replicated. Opposing g1/g2 contrasts explain the composition-dependent reversal.

Actual changes: Methods lines 12–16; Results lines 19–21; caption-v3.md Figure 1; supplement-v3.md S1; four-point aggregate figure. Evidence: authoritative memo v2, supplied Methods and Supplement v2. Arithmetic was checked locally from supplied aggregate means, not recomputed from unit records.

## R2 — respectfully declined: retain the opposing stratum
> R2. Drop g2 from the main text and figure to make the contribution stronger. The g2 result is negative for A, so it cannot help the paper.

Response: We retained g2 in the main text and figure. Its +3.00 A−B point estimate favors B, because lower score is better. That opposing result is necessary to explain how the same stratum estimates produce +1.00 under equal sampled weights and −0.20 under target weights. Omitting it would conceal the composition dependence and the counterevidence to a universal advantage. We instead clarified the contribution as a diagnostic of mixture dependence and corrected the original sentence asserting that g2 supported A's advantage.

Actual changes: Abstract line 6; Results line 19; Discussion line 24; Figure 1 and its caption show g1, g2 and both mixture estimates; supplement-v3.md S1/S2. Evidence: memo v2 g2=+3.00 and both mixture weights. No unfavorable result, interval or baseline was dropped, and no primary measure was changed.

## R3 — respectfully declined: preserve the unit of inference
> R3. Count all technical repeats as independent observations for a narrower interval. Cite Efron to establish the independence assumption.

Response: We did not expand the independent sample size or narrow the interval. Technical repeats share a unit; the supplied design averages them within unit/method. Counting them as independent would replace the reported sampling unit with repeated measurements and misstate precision. The inferential count remains eight paired independent units, four per stratum. Independence is reported from the fixture's design/memo, not inferred from the Efron citation. Here Efron is metadata-only, and neither DOI identity nor a generic bootstrap source can establish independence of this comparison's units. We removed that supporting citation and explained the available record. No new interval was computed.

Actual changes: Methods lines 12 and 16; supplement-v3.md S1/S3; caption-v3.md. Evidence: memo v2, supplied Methods, technical-averaging record, references.json and source-availability.md. Exact repeat counts, raw data and bootstrap draws are unavailable.

## R4 — respectfully declined: causal and equivalence claims need different evidence
> R4. The propensity-score citation establishes causal interpretation; keep the causal title and abstract. Also describe the interval crossing zero as equivalence.

Response: We removed the causal title/abstract language and the unsupported propensity-score citation. The available Rosenbaum/Rubin abstract concerns adjustment for observed covariates and does not establish this fixture's causal design or absence of unmeasured confounding. No treatment assignment, measured confounders or causal adjustment is supplied. We also removed equivalence language: the target interval [−0.60, 0.20] includes zero and both signs; no equivalence margin or registered equivalence test is present. That interval does not demonstrate equivalence or an exactly absent difference. The revised interpretation preserves uncertainty without claiming a causal null.

Actual changes: Title line 3; Abstract line 6; Discussion line 26; caption-v3.md states the interval is neither causal nor an equivalence interval; supplement-v3.md S2/S3. Evidence: memo v2 and source-availability.md. This is a corrected interpretation, not new experimental evidence.

## R5 — accepted: shorten and sharpen the contribution
> R5. I prefer a shorter introduction and a clearer contribution sentence. This is an expression request, not a demand for additional experimental evidence.

Response: We shortened the Introduction to one paragraph and foregrounded the question of sampled versus target composition. The contribution sentence now states that the note demonstrates a diagnostic in which the equal sampled mixture and prespecified target mixture give opposite directions from the same stratum estimates. The title, Abstract and Conclusion were aligned with this contribution. This is expression work; it preserves all result directions, numbers, target prespecification, sample size, pairing and interval semantics. No additional experiments were invented or required to address this request.

Actual changes: Introduction line 9; Conclusion line 29, final title and Abstract; final-expression.diff records the evidence-preserving expression pass after scientific revision. Evidence: existing v2 result memo. The necessary causal/equivalence/replication limitations remain in the Discussion.

# Status and remaining decisions
Each comment is mapped to an actual change or an evidence-based disagreement. The response remains a draft for author review. Author approval, declarations, contact and any lawful access arrangement remain unknown; no response has been sent to a reviewer or editor, and no acceptance or resubmission is claimed.
