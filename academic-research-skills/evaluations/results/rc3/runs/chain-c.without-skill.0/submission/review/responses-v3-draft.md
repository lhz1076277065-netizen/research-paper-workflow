# Developmental response to the supplied comments

SYNTHETIC response draft v3. No reviewer or editor contact has occurred. Author approval is pending. Locations refer to manuscript-v3-anonymous.md, figure-1-caption-v3.md and supplement-s1-v3.md in this review folder.

## R1 — units, repetitions, weights, interval and direction

Comment: Explain independent units, technical repetitions, target weights, the interval object, and why observed mixture and target mixture give different directions.

Response: We revised Methods, “Units and paired differences” and “Composition and interval,” to identify eight independent paired units, four per stratum, with A and B measured on each same unit. Technical repetitions were averaged within unit and method after unit conversion and are not counted as extra independent units. We state that independence comes from the supplied design record and has not been independently audited. The target weights were fixed before measurement at 0.8/0.2; the sampled mixture is equal because there are four units per stratum. We name the interval object as the target-weighted mean paired difference and describe paired-unit resampling within strata with target weights reapplied. Results now shows both weighted calculations: +1.00 for 0.5/0.5 and −0.20 for 0.8/0.2. Thus composition changes the aggregate direction without changing the two stratum means. Figure 1 and S1.1–S1.3 carry the same definitions. Repetition counts and original resampling details are explicitly unavailable; no such details were fabricated.

Disposition: Accepted and implemented through manuscript, figure caption and supplement changes.

## R2 — request to remove g2

Comment: Drop g2 from the main text and figure to make the contribution stronger. The g2 result is negative for A, so it cannot help the paper.

Response: We retain g2 in Results, Discussion, Figure 1 and S1.2. Its +3.00 score difference favors B because lower scores are better. Omitting that result would conceal the stratum that explains why mixture weights change the aggregate direction, and would leave a misleading impression of consistent advantage for A. We instead revised the title, abstract and contribution sentence around the composition diagnostic. Both stratum directions remain visible and the main conclusion is bounded to the supplied comparison.

Disposition: Scientific disagreement with the deletion request; transparency and the stated question require retaining g2. The presentation has been revised to explain why it matters.

## R3 — technical repetitions and Efron

Comment: Count all technical repeats as independent observations for a narrower interval. Cite Efron to establish the independence assumption.

Response: We do not count repeated measurements within the same unit as independent observations and do not narrow the reported interval. Methods keeps the sample size at eight paired independent units, with four per stratum, after repetition averaging. Repetition counts are unknown. The supplied result memo reports unit-level paired resampling within strata; it does not provide data or outputs for an alternative analysis. The Efron DOI establishes a bibliographic identity, but only metadata was supplied and the original text was not obtained. A methods citation would not demonstrate the independence of these particular units. We removed the abstract's unsupported citation claim and explicitly state the source and audit limits of the independence assumption. The reported interval remains [−0.60, 0.20] score in every revised file.

Disposition: Statistical disagreement with the proposed inflation of n and unsupported citation; explanatory changes implemented without inventing a reanalysis.

## R4 — causal and equivalence claims

Comment: The propensity-score citation establishes causal interpretation; keep the causal title and abstract. Also describe the interval crossing zero as equivalence.

Response: We changed the title to “Target composition changes the direction of a paired method comparison” and rewrote the abstract around reported paired differences. The supplied record has no causal assignment, confounding measurements or causal adjustment. The available Rosenbaum/Rubin abstract concerns assignment probabilities conditional on observed covariates and adjustment for imbalance in those observed variables; it supplies no case-specific causal evidence and does not establish that unmeasured confounding is irrelevant. We removed that citation from the manuscript. Discussion now states that the interval spans zero and does not establish equivalence or exact absence of a difference. No equivalence margin or registered equivalence test is recorded. These limits also appear in the caption and S1.3/S1.6.

Disposition: Scientific/statistical disagreement with the requested overclaims; title, abstract and discussion corrected in the actual files.

## R5 — concise introduction and contribution

Comment: I prefer a shorter introduction and a clearer contribution sentence. This is an expression request, not a demand for additional experimental evidence.

Response: We replaced the working introduction with one short paragraph that identifies the intended-versus-sampled mixture question and states the contribution: “Its contribution is a transparent diagnostic of composition-dependent direction, without a claim to a new general causal or predictive method.” We did not add experiments, an algorithm, external validation or a new evidential claim to satisfy this expression request.

Disposition: Editorial request accepted and implemented.

## Additional consistency repairs

The unsupported approval, ethics and unrestricted open raw-data statements in the v2 Declarations were replaced by explicit unresolved drafts. The main manuscript contains no author name or affiliation; the supplied author line is on a separate editor-only title page under Lens policy v2. The old v1 target value −0.30 is preserved in its byte-identical snapshot and addressed in a separate correction draft, while all v3 results use −0.20. The present response and package remain developmental and require human approval before any external use.
