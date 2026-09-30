# Scientific claim and citation decisions

SYNTHETIC internal reasoning, separate from manuscript prose. Materials were supplied as a closed-world record; observations below are Agent checks, not named-human verification or empirical replication.

## Evidence ladder used

The authoritative numerical source is evidence.md version 2. The methods described in draft-v2.md and supplement-v2.md agree on eight independent paired units, four per stratum, repetition averaging and target weights. caption-v2.md supplies score direction and agrees with the memo. Derived arithmetic was checked locally. No numerical source data, bootstrap realizations, protocol or original plotting/analysis code were obtained. Reported estimates and resampling description can be edited accurately; empirical reproducibility and coverage remain unverified.

## Important claims

| ID | v2 claim or issue | Support and limitation | Decision and implemented location |
| --- | --- | --- | --- |
| C01 | A universally outperformed B | evidence.md v2 gives g1 −1.00 and g2 +3.00; caption-v2 states lower score better. g2 favors B. | Reject universal advantage. New title/Abstract, Results and Discussion preserve opposing stratum directions. |
| C02 | Target mean A−B=−0.20 | Memo v2, caption-v2 and 0.8×(−1)+0.2×3 agree. | Retain −0.20 everywhere in v3. Arithmetic independently reconciled from supplied aggregates only. |
| C03 | Equal sampled mixture +1.00 | Memo v2 and 0.5×(−1)+0.5×3 agree; n=4 in each stratum supplies equal weights. | Retain +1.00; describe sampled and target summaries as differently weighted objects. |
| C04 | g2 supports A's advantage | +3.00 A−B, lower better, favors B. | Correct direction; retain g2 in main text, figure and S1. |
| C05 | Independent sample size includes technical repeats | Memo v2 and Methods specify eight paired units, technical repetitions averaged within unit/method. Repetition count unknown. | Keep n=8, n_g1=n_g2=4; no inflated denominator or narrowed interval. Methods/S1.1. |
| C06 | Independence is proven by Efron | Supplied design describes independence; Efron content access is metadata only, and metadata cannot establish case-specific independence. | Remove citation claim; explicitly state stipulated independence and absent audit in Methods. |
| C07 | Bootstrap interval valid for every target population | Supplied target interval is [−0.60, 0.20]; no raw data, implementation or external validation available. | Retain reported object and method only; no universal coverage claim. Methods/Discussion/S1.3. |
| C08 | Target result proves causal advantage | No causal assignment, measured confounding or adjustment in memo v2/Methods. | Remove causal title/abstract; label diagnostic comparison. Discussion and caption. |
| C09 | Propensity-score citation eliminates unmeasured confounding | Available official-abstract paraphrase addresses observed covariates; no case-specific causal design. | Reject support and remove reference use; R4 explains. |
| C10 | Interval crossing zero proves equivalence or zero effect | Memo says no equivalence margin/registered test; interval spans negative and positive values. | Reject equivalence and exact-zero conclusion; preserve uncertainty in Abstract/Discussion/caption. |
| C11 | All authors approved; ethics and unrestricted raw sharing confirmed | author-and-license.md states approval/ethics unknown and raw/identifier redistribution prohibited. | Replace with unresolved declarations and license-specific access draft; separate title page and author requests. |
| C12 | v1 target mean −0.30 | Conflicts with authoritative v2 and weighted arithmetic; original v1 interval and subgroup means agree with v2. | Preserve v1 bytes; propose explicit −0.30→−0.20 correction with same supplied interval and interpretive repair. |
| C13 | Contribution requires new algorithm or new experiments | README asks developmental revision; Introduction supplies mixture diagnostic; R5 is expression-only. | Retain diagnostic contribution, shorten introduction, invent no algorithm, experiment or validation. |

## Citation decisions: identity is not semantic support

### Reference 1 — Efron (1979)

Identity available: B. Efron, “Bootstrap Methods: Another Look at the Jackknife,” The Annals of Statistics (1979), DOI 10.1214/aos/1176344552. These fields are supplied in references.json, with a recorded Crossref check at 2026-09-30T13:54:17.025683+00:00. This agent did not perform that earlier Crossref query. Efron's original text was not obtained; evidence access is metadata only.

Semantic decision: no accessible full-text passage has been verified for any particular bootstrap claim. Bibliographic identity does not validate fixture-unit independence, implementation, interval coverage or every target population. Removed from the manuscript rather than retaining an unsupported empirical or methodological assertion. Identity remains in this audit. Generic historical use, if desired later, would require opening relevant original text and matching its scope; it is not necessary for the present memo-based diagnostic.

### Reference 2 — Rosenbaum and Rubin (1983)

Identity available: Paul R. Rosenbaum and Donald B. Rubin, “The central role of the propensity score in observational studies for causal effects,” Biometrika (1983), DOI 10.1093/biomet/70.1.41. Supplied references.json records a Crossref check at 2026-09-30T13:54:18.601266+00:00. Full text was not obtained.

Content available: source-availability.md supplies a bounded paraphrase of the official abstract at https://academic.oup.com/biomet/article-abstract/70/1/41/240879?login=false. It describes assignment probabilities conditional on observed covariates and adjustment for imbalance in observed variables. The original abstract page was not freshly opened by this agent; only the supplied availability record and paraphrase were read.

Semantic decision: the available abstract-level content does not establish that unmeasured confounding is irrelevant, that the fixture used propensity scores or that its paired comparison is causally identified. Removed from manuscript; response R4 gives the reason. No unsupported replacement citations added.

## Professional guidance actually used

The pinned K-Dense scientific-writing entry (metadata version 2.1; commit 65d6e786832e2c52832713117bbbf5096b56f77f), evidence_workflow.md, writing_principles.md and figures_tables.md guided evidence separation, retention of adverse results, bounded interpretation, provenance and declaration states. These are professional workflow resources, not scientific evidence about this fixture. Exact paths/hashes/read receipts are in resource_reads.jsonl and operation.md. Its CLI tools, linked policies and cited source papers were not obtained or executed. No new manuscript reference was invented from those workflow references.

The entry requests human verification and approval for external submission; the packet remains a local developmental draft with author requests rather than claiming those stages occurred.
