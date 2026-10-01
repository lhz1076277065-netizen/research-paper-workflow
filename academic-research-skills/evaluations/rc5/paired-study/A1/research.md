# A short-burst deletion rule for causal first alarms: exploratory study and limits

## Question and competing explanations

Can discounting the evidence from one contiguous short interval improve first alarms for sustained scalar shifts when short bursts are nuisances, rather than merely raising the CUSUM threshold? The competing explanation is that any gain is an ordinary delay/false-alarm tradeoff, or a dev-selection effect. This is an exploratory, task-specific implementation study. It does not establish publication novelty or an out-of-sample advantage. Here causal means nonanticipating; no intervention effect is estimated.

The supplied train/dev files contain 40/120 streams, each 360 slots long, with four conditions (clean, bursts, gaps, heavy), equally represented. Half of each condition has a sustained-shift target. The first 64 slots are declared stable calibration material. The gaps condition has mean missing fractions 0.0839/0.0951 in train/dev. There is no imputation. The train set was used for implementation checks; all tuning used dev. No generator or holdout was read. Labels enter scoring and retrospective diagnostics only.

The supplied loss gives 90 to any first false alarm, or a shift without a detection within 60 slots; a timely detection costs its delay; a null stream without alarm costs zero. Thus a detector can improve mean loss by recovering missed shifts while raising more false alarms. Timely-hit counts have denominator 60; false-alarm counts have denominator 120. Counts are not average run lengths or population false-alarm probabilities.

## Known methods and nearest primary work

| Primary work and inspected scope | Mechanism and difference from this implementation |
|---|---|
| [Page (1954), Continuous Inspection Schemes](https://doi.org/10.1093/biomet/41.1-2.100), bibliographic publisher record; baseline implementation supplied locally | CUSUM is known machinery. The supplied two-sided clipped recurrence, robust calibration and skipping missing observations are the baseline, never an originality claim. Its recurrence has no explicit allowance for one contiguous nuisance interval. |
| [Fearnhead and Rigaill (2019), Changepoint Detection in the Presence of Outliers](https://doi.org/10.1080/01621459.2017.1385466), publisher-emitted bounded-loss/segment-length passages and arXiv HTML entry | Their penalized segmentation uses bounded loss to resist arbitrarily extreme outliers and implies a minimum segment length; clustered outliers can still exceed it. This study uses fixed-window first alarms, subtracting an interval's directional evidence rather than optimizing a penalized segmentation. Its clip is inherited robustness, not a new robust loss. The shared duration tradeoff makes this a close conceptual neighbor. |
| [Lau and Tay (2019), Quickest Change Detection in the Presence of a Nuisance Change](https://arxiv.org/html/1902.03460), sections II–III | Their nuisance-aware windowed GLR compares known distributional regimes and maximizes nuisance change-point likelihoods in numerator and denominator. Their nuisance can change the distribution after the critical event. Here the nuisance is a finite short burst; the rule pessimistically deletes one bounded interval without specifying densities. No GLR, optimality, or ARL theorem is claimed. |
| [Xie, Moustakides and Xie (2023), Window-Limited CUSUM for Sequential Change Detection](https://arxiv.org/html/2206.06777), introduction and mechanism | Their sliding window estimates post-change parameters, which enter a recursively updated CUSUM. Our sliding window supplies a finite moving evidence sum and a worst-case deleted interval; it does not estimate a post-change parameter. Windowing alone is already known. |

These are mechanism comparisons, not an exhaustive nearest-neighbor search. Duration constraints, robust scans, run rules, nuisance GLRs, and two-stage confirmation are crowded prior-art areas. Source access and search queries are recorded in `sources.json`.

## Implemented initial idea and diagnostic

`detect_initial` creates a two-sided CUSUM candidate with k=0.4, h=12, clip=3. It then discards the candidate-building data from confirmation and requires the next n observed samples to have directional clipped mean above c. Failed confirmation resets both CUSUM sides. Missing samples do not count; the candidate expires after 60 wall-clock slots. This is a practical known-style two-stage confirmation rule, not a claimed invention.

The 12 initial configurations cross n={6,10,16} and c={0.3,0.5,0.7,0.9}. The first setting, n=6/c=0.3, failed relative to the tuned baseline: loss 37.075 with 35 false alarms and 48 timely hits (`initial_00.json`). Tightening confirmation to n=10/c=0.9 selected `initial_07.json`: loss 20.883, 3 false alarms, 49 timely hits. Increasing n to 16/c=0.9 cut false alarms to one but reduced timely hits to 43 and raised loss to 24.817. All failed and successful configurations remain saved.

The diagnostic is both retrospective and mechanistic. Among initial timely/untimely targets, the absolute clipped mean over the first 60 post-shift slots averaged 1.278/0.691 (n=49/11). These are observed descriptive magnitudes, not true shift parameters or causal estimates. The runnable known-case check shows that a constant standardized shift of 0.8 never passes the selected 0.9 fresh-mean gate; the baseline alarms 89 slots after that shift, whereas the refined rule alarms after 31 slots. A stronger 16-slot burst can contaminate both candidate and confirmation and causes an initial alarm. This evidence favors testing support that remains after one potential burst is removed, while exposing a sensitivity cost.

Both mechanism alternatives were implemented before the initial grid finished; this was not a preregistered sequence in which the diagnostics uniquely determined the code. The initial-grid results and subsequent explicit checks support the refinement's rationale. They do not retroactively turn it into a pre-specified hypothesis.

## Refined mechanism and an established boundary

For a trailing wall-clock window of W slots, standardize with the frozen prefix median and MAD (scale floor 0.25) and clip to ±3. For direction s in {−1,+1}, let e_i=s*z_i−k on observed slots and zero on missing slots. Define

`R_s = sum_window(e_i) - max(0, max over contiguous intervals I of length <= B of sum_I(e_i))`.

Equivalently, R_s is the minimum remaining directional evidence after deleting any one interval of at most B slots, including an empty interval. `detect_refined` alarms at the earliest observed slot when max(R_+,R_−)>h, a full window is available, and at least ceil(coverage*W) slots are observed. The strongest interval is found by a prefix-sum/minimum deque, checked against exhaustive enumeration. Its implementation costs O(W) per time slot and O(W) memory. It handles both signs and has no label, generator-time, or future-data access. Missing entries age out in wall time; they provide neither evidence nor a new alarm.

The selected parameters are W=36, B=8, k=0.3, h=10, coverage=0.6, clip=3. Eleven refined proposals were evaluated: W={36,48,60}, B={8,12}, h={6,10}, excluding W=60/B=12/h=10. The twelfth refined-stage call is the matched B=0 ablation at the selected other parameters. Parameter selection minimizes dev loss within each allocated grid; it is not a claim that the baseline or proposal is globally tuned.

A deterministic limit is established, not a stochastic robustness guarantee. If all positive directional evidence is inside one interval of at most B slots, with nonpositive evidence outside, deleting that interval leaves R_s<=0; h>=0 cannot be crossed. Therefore the selected rule rejects the checked 8-slot burst in an otherwise zero post-calibration background even when its amplitude saturates the clip. Background noise, two bursts, a burst longer than B, or a bad calibration can break this protection.

For a dense constant standardized shift a>k and no noise, the plateau is `(W-B)*(min(a,clip)-k)`. When this is <=h, the refined rule cannot detect it. With the frozen parameters, the positive no-noise sensitivity boundary is a<=0.6571. For a=0.8, the strict threshold is crossed after 32 shifted observations (delay 31); for a=1.2 it is crossed after 24 (delay 23), exactly as the checks record. A clipped amplitude-3 burst of length 16 alarms after 15 observations, demonstrating the budget's ceiling. Before the burst ends, a same-amplitude permanent shift has the identical observed prefix: a causal detector that alarms on one must alarm on the other. Discrimination before that point is impossible without further assumptions.

## Validation results from actual scorer records

The following tables are inserted verbatim from `tables.md`, generated by `summarize.py` from the four frozen selected score records. Every individual comparison is in `paired-cases.csv`; unrounded summaries and retrospective diagnostic rows are in `comparison.json` and `diagnostics.json`.

| Method | Mean loss | False alarms / 120 | Hits / 60 | Mean delay among hits | Runtime, s |
|---|---:|---:|---:|---:|---:|
| baseline | 22.692 | 4 | 44 | 25.07 | 0.0069 |
| initial | 20.883 | 3 | 49 | 25.43 | 0.0067 |
| refined | 20.825 | 5 | 52 | 27.29 | 0.2482 |
| ablation | 47.675 | 53 | 37 | 18.41 | 0.0369 |

| Condition, n=30 | Baseline loss | Initial loss | Refined loss | Ablation loss |
|---|---:|---:|---:|---:|
| bursts | 27.000 | 29.800 | 21.967 | 47.300 |
| clean | 25.067 | 21.400 | 20.000 | 33.333 |
| gaps | 19.967 | 17.867 | 21.367 | 50.833 |
| heavy | 18.733 | 14.467 | 19.967 | 59.233 |

| Refined minus comparator | Mean paired loss delta | Descriptive SE | Better / tie / worse | Common-hit delay delta |
|---|---:|---:|---:|---:|
| baseline | -1.867 | 2.074 | 24 / 69 / 27 | 0.68, n=44 |
| initial | -0.058 | 1.874 | 24 / 65 / 31 | 1.67, n=46 |
| ablation | -26.850 | 3.966 | 46 / 37 / 37 | 9.51, n=35 |

The refined rule improves baseline mean loss by 1.867 units (8.2%) and recovers eight additional timely targets, but has one extra false alarm. It is better on 24 paired cases, worse on 27, and tied on 69. All 44 baseline timely hits remain timely under refinement; their mean delay increases by 0.68 slots. Relative to the selected initial rule, the refined loss improvement is only 0.058 units; it wins 24 cases and loses 31. It recovers six initial untimely targets and loses three initial timely targets. The IDs are recorded, including `65109-bursts-1` among recoveries and `65109-heavy-13` among losses. The initial rule remains a credible competitor, particularly for heavy tails and gaps.

Condition results support a specific tradeoff: refinement improves bursts and clean targets over the baseline, but worsens gaps and heavy-tail loss. The deletion-off ablation has much lower loss control, 53 false alarms versus five. This establishes that interval deletion matters at these fixed settings; it does not establish that the deletion rule beats an independently retuned moving-sum detector. Such retuning was not performed. The chosen B=12/W=36/h=10 alternative has loss 21.342, only two false alarms and 50 hits, illustrating a budget/sensitivity tradeoff.

Paired standard errors are descriptive and exceed the refined-minus-baseline and refined-minus-initial differences. No independent confidence interval, significance claim, selection correction, or holdout result is available. The conditional delay column cannot by itself rank methods: it conditions on different hit sets. Runtime is measured by the supplied scorer on each single call, not a benchmark repeated under controlled CPU load. The refined selected call is about 36 times slower than the selected baseline call, though still 0.248 seconds for 120 short streams. Broadening the tuning grid or measuring long-stream throughput would require additional work.

## Manuscript result paragraph

On 120 supplied development streams, a causal trailing-window detector that discounted the strongest contiguous interval of up to eight slots achieved mean first-alarm loss 20.825, compared with 22.692 for a tuned clipped two-sided CUSUM and 20.883 for fresh-block confirmation. Timely sustained-shift detections increased from 44/60 under CUSUM to 52/60, while false alarms increased from 4/120 to 5/120. The matched deletion-off ablation had loss 47.675 and 53 false alarms. Improvement was concentrated in the burst and clean conditions; gap and heavy-tail losses worsened relative to CUSUM. Paired dev loss differences were small relative to their descriptive standard errors, and all methods were selected using this development set. Deterministic checks established rejection of a single burst within the deletion budget and exposed failure on longer bursts and sufficiently weak shifts. These results justify independent evaluation of the task-specific rule but do not establish general superiority or publication novelty.

## Reproduction, causality and scope

Use the supplied Python executable; no installation is needed:

```sh
cd A1
/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 checks.py
/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 summarize.py
/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 run_dev.py --out rerun
```

`run_dev.py` defaults to scoring the four frozen configurations into a fresh directory; `--stage baseline|initial|refined` reproduces each allocated grid, including the refinement ablation. It refuses a directory with existing score events to avoid silently combining runs. The original study made exactly 40 scored dev calls: 16 baseline, 12 initial, 11 refined proposals and one matched ablation. There were no scored train calls. Running the reproduction command adds new calls in its separate output directory.

`checks.py` passed 324 bounded-interval brute-force comparisons and 6,404 causal prefix/suffix assertions. It exhausts all prefixes of constructed known cases and checks selected cuts, alarm boundaries and perturbed suffixes on all 40 train streams. These verify the checked scope, not every possible input. Algorithmically, decisions start after calibration and depend only on the prefix up to the current time. Short inputs and inadequate/nonfinite calibration safely return −1. The known-case output preserves the longer-burst failure.

Known machinery is prefix median/MAD, clipping, CUSUM, finite moving sums, two-stage confirmation, and nuisance-duration constraints. The task-level incremental change is pessimistic removal of one bounded contiguous evidence interval from each directional moving sum, combined with wall-clock missingness and observed-coverage gating. Publication novelty is unestablished. The next decisive work is the coordinator's independently generated common holdout, followed by a wider prior-art comparison and a retuned moving-sum comparator. No post-holdout change is authorized or performed here.

Skill use was restricted to the assigned analysis-execution library through the task recorder: the entry and protocol, provider-policy and handoff references informed actual computation, failure preservation, limits, paired outputs and freeze. Guidance reading is logged separately from the implemented research work. No attached skill function, external executor, subagent, or independent review was used. `usage.json` records measured scope and resources.

## Final research-quality self-check

The coordinator requested the assigned `references/research-quality.md`, read through the recorder after drafting. Its relevant guidance emphasizes competing explanations, fair nearest-neighbor comparisons, independent decisive evidence, and separating implemented checks from research value. The reading changed the interpretation emphasis, not the method or frozen parameters. This is an executor self-review, not independent review.

At the frozen parameters, deletion penalty D lies in [0, B*(clip-k)]=[0,21.6]. Hence the refined score satisfies E−21.6<=R<=E. A refined alarm implies the identical moving-sum score exceeds 10; a moving-sum score exceeding 31.6 implies a refined alarm (with the same coverage and full-window requirements). The rule is therefore a data-adaptive threshold between these two fixed thresholds. Three hundred assertions on synthetic bounded evidence arrays check these implications, recorded in `quality-selfcheck.json`; they add no dev score calls. This makes the strongest alternative explanation explicit: ordinary threshold adjustment may account for some benefit. The existing matched ablation establishes a component effect at fixed settings, not a unique structured-burst advantage.

The clearest established result is the explicit single-burst and weak-shift boundary; the overall dev advantage over the initial competitor is essentially a tie. A common unseen test can assess the frozen methods' transfer. Resolving whether contiguous deletion itself adds value also requires an independently tuned moving-sum comparator, which the exhausted 16/12/12 budgets do not permit in this study. These limitations reduce the strength of the scientific claim without undoing the completed task-level implementation and evidence. No additional skill fragment is needed to articulate this gap, and no post-holdout modification was made.
