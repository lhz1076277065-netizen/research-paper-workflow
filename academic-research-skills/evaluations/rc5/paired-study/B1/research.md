# Causal first alarms under transient bursts: an excision experiment and its detection boundary

## Research question and competing explanations

Can explicit evidence outside an unknown short nuisance interval improve a causal first-alarm detector for sustained scalar shifts, given heavy tails and missing runs? The scientific target is the distinction between persistent change and localized nuisance, rather than new clipping or a relabeled CUSUM. We compare (i) the supplied robust two-sided clipped CUSUM, (ii) a trigger-plus-fresh-confirmation initial idea, and (iii) a finite-window test that must survive every possible contiguous nuisance deletion. An alternative explanation is that apparent robustness comes only from imposing a more conservative effective threshold. A same-parameter excision ablation diagnoses the component, while the tuned CUSUM is the substantive competitive control.

The main completed finding is a limit: the refinement repairs much of the initial method's development loss, but does not improve the best tuned baseline overall. Its explicit short-burst guarantee has a sharp, implemented weak-shift blind region. This is a development method study and a boundary result, not evidence of a publication-ready new detector.

## Data, target, and evaluation design

Only supplied train/dev were used. Train has 40 streams and dev has 120; each split has equal counts in clean, bursts, gaps, heavy and exactly half have sustained targets. Every stream has 360 steps and a stated stable 64-step calibration prefix. The dev set contains 1,027 missing entries, all in its gaps condition. No generator source, other participant submission, or holdout was read. Stream IDs, condition labels, and target times are used only by evaluation/diagnostics; neither detector receives labels.

The harness penalizes a false first alarm, or a target not hit within 60 steps, with loss 90; a timely hit incurs its delay and a correctly silent null incurs zero. Early alarms prevent later recovery because this is a first-alarm task. Mean hit delays therefore describe different selected hit subsets, and cannot on their own establish faster detection. All validation calls use `harness.score`, retain every per-case row, and store the input data SHA-256. `paired-cases.csv` joins all 120 dev IDs across methods without dropping failures.

We searched the prewritten grids in `run_dev.py`: 16 baseline maps; 12 initial maps; 10 refined maps plus two component ablations, within the 12 refined-map budget. The choice rule is minimum dev mean loss, then fewer false alarms, more hits, and record name. The three selected methods were additionally scored on train as a secondary check. Train was inspected for condition/sample quality but was not a separate tuning split. Consequently the dev results are selection-biased, and train is not an independent test. Chosen maps are frozen in `frozen.json`; independent holdout evaluation remains the decisive next action.

## Nearest primary works and mechanism differences

The following are verified primary sources. Metadata/abstract inspection is distinguished from relevant full-text inspection; no claim of exhaustive nearest-neighbor coverage is made.

| Primary work | Relevant existing ability | Actual difference in this study | Reading scope |
|---|---|---|---|
| [Page (1954), Continuous Inspection Schemes](https://doi.org/10.1093/biomet/41.1-2.100) | Cumulative evidence with restarts is the known CUSUM foundation. | The baseline is the task's clipped two-sided implementation; neither its recursion nor robust calibration is claimed as new. | Publisher metadata; implemented formula supplied by harness. |
| [Lau and Tay (2019), Quickest Change Detection in the Presence of a Nuisance Change](https://arxiv.org/html/1902.03460) | W-SGLR contrasts critical distributions against a likelihood-maximized nuisance model; its null and post-change models use four distributions. | We assume an unknown finite contiguous nuisance interval within the current window and conservatively delete it. This is not their parametric likelihood construction and inherits none of their asymptotic optimality results. | Full-text problem model and equations (10)–(17), including the two-stage failure discussion. |
| [Zhang, Mei and Shi (2022), Robust Change Detection for Large-Scale Data Streams](https://www.tandfonline.com/doi/full/10.1080/07474946.2022.2043045) | L-alpha CUSUM uses a likelihood transformation to reduce outlier effects, then combines sparse multi-stream evidence. | Our scalar test changes temporal support, requiring evidence after a worst contiguous deletion. Clipping alone remains an ordinary bounded-influence device. | Publisher abstract and author-hosted PDF introduction. |
| [Xie, Moustakides and Xie (2023 revision), Window-Limited CUSUM](https://arxiv.org/html/2206.06777) | A moving estimate of unknown post-change parameters is inserted into a recursive CUSUM update. | Our rolling window is the entire statistic; it does not estimate a post-change likelihood parameter or carry recursive evidence beyond that window. | Full-text equations (6)–(9), assumptions and computational comparison. |
| [Tang, Chen, Li and Yu (2026 preprint), Online change point detection under heavy-tailedness and contamination](https://arxiv.org/html/2606.09737v1) | An online multiscale detector compares prefix and recent robust means or medians, with contamination and tail inputs and theoretical delay regimes. | We use a fixed trusted calibration prefix, one clock-window size, and a contiguous deletion budget. Their distributional contamination guarantees are stronger and different; no theorem transfers to this heuristic. | Abstract and full-text Algorithm 1, Section 2.2 and thresholds. |

These works already establish nuisance-aware and robust sequential detection as existing research areas. Contiguous excision is a task-level mechanism experiment, and may overlap other trimmed-scan or nuisance-model methods. Publication novelty is unestablished: we did not implement all these competitors or complete a search for prior contiguous-deletion statistics.

## Initial implementation, diagnosis, and refinement

Both methods share the supplied median/MAD center-scale calibration and bounded standardized residuals. This common machinery is known. The initial method arms a direction after CUSUM crosses `h`, then collects a fresh batch of `confirm` observed residuals, requiring their signed average to exceed `mean`. Missing entries age the candidate but add no observations; an over-age candidate resets. It asks for repeated future support, but a sufficiently long burst can fill both trigger and confirmation phases, and repeated noise-driven proposals create multiple opportunities to pass.

Its selected map is `clip=2.5, k=.35, h=10, confirm=12, mean=.65, timeout=24`. It produced 11 false first alarms versus one for the tuned baseline, with a higher loss despite five more timely hits. Initial false alarms included two bursts cases and five heavy cases. The implemented `alarm-diagnostics.json` reconstructs, at each initial alarm, the amount of signed support concentrated in the most supportive six-step interval and the worst residual standardized sum. Nine of the 11 initial false alarms have this excision statistic below the selected refined threshold at the initial alarm time. This is a retrospective diagnostic, not evidence that all nine streams are rescued: the refined method can alarm at another time.

The refinement requires distributed evidence across a fixed wall-clock window. If `z_i` is a clipped observed residual, let `O` be observed positions in the last `w` steps. For direction `s` and every length-`b` contiguous clock interval `I`, define

`R_s(I) = s * sum(z_i for i in O outside I) / sqrt(number of observed positions outside I)`.

All windows must satisfy full-window coverage and every deletion must leave at least `ceil(coverage*(w-b))` observations. The statistic is `max_s min_I R_s(I)`. The earliest observed time with this value strictly greater than the threshold is the alarm. Missing values advance and expire the clock window; they are never imputed, and an alarm is not issued on a missing observation. With no missing entries this subtracts, for each direction, the most supportive contiguous interval; with gaps it also respects the varying retained denominator.

The selected map is `clip=2, window=24, burst=6, threshold=3, coverage=.6`. This is a substantive change of evidence support and nuisance set relative to the initial latching CUSUM. The initial and refinement concepts were drafted before the single bounded search; the detailed alarm diagnostic was executed after seeing the recorded results. Thus this is open development with a retrospective mechanism diagnosis, not a preregistered sequential redesign. The failed initial implementation and all configurations are retained. The actual evidence changed the interpretation from a hoped-for detector advantage to the boundary result below; we did not retune after inspecting that result.

## Actual paired development results

Result ID `dev-frozen-001`; all values below are generated from the saved harness reports by `analyze.py`, with full precision in `comparison-summary.json`.

| Method | Mean loss | False alarms /120 | Hits /60 | Mean hit delay | Runtime (s/120 streams) |
|---|---:|---:|---:|---:|---:|
| baseline | 19.658 | 1 | 49 | 26.102 | 0.0069 |
| initial | 22.667 | 11 | 54 | 27.037 | 0.0061 |
| refined | 19.842 | 9 | 51 | 21.980 | 0.1250 |
| ablation | 46.175 | 52 | 38 | 15.553 | 0.1131 |
| no_coverage | 19.842 | 9 | 51 | 21.980 | 0.1286 |

The refinement's paired mean loss difference from baseline is +0.183 loss units (descriptive paired bootstrap percentile interval −3.558 to +4.275); it improves 36 cases, ties 67, and worsens 17. Against the initial method, the paired difference is −2.825 (−5.950 to −0.100), with 43 improved, 66 tied, and 11 worsened. The nominal bootstrap intervals resample the 120 paired cases 10,000 times with seed 774091 after method selection; they omit selection uncertainty and are not confirmatory confidence intervals. The apparent 12.46% loss reduction versus initial is a development comparison only. The baseline has materially fewer false alarms, while refinement has two more timely hits.

| Condition (n=30 each) | Baseline loss | Initial loss | Refined loss | Refined − baseline | Refined improved / worsened cases |
|---|---:|---:|---:|---:|---:|
| clean | 23.767 | 21.967 | 20.633 | -3.133 | 9 / 3 |
| bursts | 19.600 | 22.933 | 19.300 | -0.300 | 10 / 3 |
| gaps | 19.033 | 19.733 | 18.700 | -0.333 | 9 / 3 |
| heavy | 16.233 | 26.033 | 20.733 | +4.500 | 8 / 8 |

The heavy condition reverses the modest improvements elsewhere. Fixed-prefix calibration error, scattered heavy-tailed excursions, and bursts longer or more complex than one excised interval remain plausible failure mechanisms. The available labels do not identify every nuisance time, so the actual six-step concentration diagnostic does not certify which specific excursions are true bursts. We do not infer a universal cause from condition names.

| Case ID | Target time | Baseline alarm / loss | Initial alarm / loss | Refined alarm / loss |
|---|---:|---:|---:|---:|
| 65109-bursts-24 | none | -1 / 0 | 153 / 90 | -1 / 0 |
| 65109-bursts-22 | none | -1 / 0 | 177 / 90 | 176 / 90 |
| 65109-clean-15 | 209 | -1 / 90 | 108 / 90 | 201 / 90 |
| 65109-clean-3 | 165 | 237 / 90 | 191 / 26 | 187 / 22 |
| 65109-heavy-13 | 170 | 197 / 27 | 195 / 25 | 150 / 90 |
| 65109-gaps-7 | 177 | 286 / 90 | 233 / 56 | 282 / 90 |

These examples include rescue, retained false alarm, faster timely detection, and deterioration. They were selected to illustrate both signs of the paired differences; the full CSV is the quantitative basis. For example, bursts-24 is rescued relative to initial but the baseline was already silent, while heavy-13 is an early refined alarm that changes a valid baseline hit into loss 90. A gap stream can still be delayed beyond the 60-step horizon.

The no-excision ablation (`burst=0`, all other selected parameters held fixed) has loss 46.175, 52 false alarms, and 38 timely hits. It shows the component suppresses concentrated support at the same numeric threshold, but is not a separately calibrated moving-average competitor: deleting six samples changes the statistic's null distribution and signal strength. It cannot by itself prove a superior operating tradeoff. Removing coverage (`coverage=.01`) changes none of the 120 dev first alarms; the coverage guard is mechanistically defensible but its effect is not established on this sample. The two ablations consumed the last two refined configuration slots.

Selected train losses were 14.575 (baseline), 20.850 (initial), and 12.725 (refined), with 0/4/1 false alarms and 18/18/19 timely hits. This disagreement with the dev ranking reinforces the need for unseen evaluation. Runtime for refined was approximately 18 times baseline in this one recorded dev call; all methods remain small on these 360-step streams. The implementation is O(T*w) time and O(w) working storage, versus O(T) and constant detector state for the baseline. Timing is descriptive and not a controlled benchmark.

## Deterministic mechanism guarantees and an explicit limit

**Bounded single-burst property.** Assume the calibrated inlier residual is exactly zero, there is one contiguous nuisance burst of duration at most `b`, and threshold is positive. Every current full window has some length-`b` interval containing all burst positions in that window. If coverage gates permit testing, deleting that interval leaves zero signed sum in both directions; consequently each direction's minimum statistic is at most zero. If coverage fails, testing is suppressed. Therefore the refinement cannot alarm at any time for this idealized nuisance, irrespective of burst amplitude or sign. This deterministic argument is conditional on exact inlier centering and one bounded interval; it is not an average-run-length bound under noisy nulls.

**Weak-shift blind region.** With no missing entries, zero inlier residuals before a sustained constant clipped shift of magnitude `delta`, and a fixed window, the maximum possible worst-retained statistic is `delta*sqrt(w-b)`. During onset, if `m` changed samples are in the window, it is `delta*max(0,m-b)/sqrt(w-b)`. Thus whenever `delta <= threshold/sqrt(w-b)`, the strict-threshold refinement never alarms, regardless of how long the shift persists. For the selected map, this boundary is `3/sqrt(18) = 0.7071067812` calibrated units. This is an exact limitation of the implemented finite window, not a limitation of all robust detectors.

`check.py` verifies both signs and multiple burst positions, exact unit-shift alarm time 114 for onset 96, missing-run expiration, and the excision component on a small-bias plus six-step burst (refined silent; no-excision alarm 154). It also constructs a shift of calibrated magnitude .7: baseline alarm 156 (delay 60), initial alarm 136 (delay 40), and refined no alarm. This deterministic case substantiates the blind-region prediction and identifies a concrete cost of the refinement.

A separate causal indistinguishability argument applies to any detector: a sustained shift and a transient burst with the same first `b` changed observations have identical histories until the burst ends. A rule that rejects every such transient burst cannot guarantee a sustained alarm within those shared observations. This familiar information constraint explains the need to pay some delay, but does not make our extra threshold delay optimal.

All 28,880 prefix comparisons on every prefix of the 40 train streams passed for both submitted methods, including prefixes shorter than calibration. An independently implemented direct-deletion oracle agrees with refined on all 120 dev streams. These establish the checked implementation and prefix behavior; they are not holdout evidence. Checks are reproducible with the supplied Python and `python check.py`.

## Manuscript result paragraph

A contiguous-excision first-alarm detector was evaluated against a robust clipped CUSUM and an initial trigger-confirmation detector on 120 development streams containing sustained shifts, transient bursts, missing runs, and heavy tails. The refined detector reduced mean task loss from 22.667 to 19.842 relative to the initial implementation, but did not outperform the tuned CUSUM (19.658). It produced nine false first alarms and 51 timely hits, compared with one and 49 for CUSUM. Same-parameter removal of interval excision increased loss to 46.175, although this ablation was not independently threshold-calibrated. A deterministic analysis established rejection of a single noiseless burst of at most six steps, together with a weak-shift blind region below 0.707 calibrated units; executable examples confirmed both properties. These development findings support a specific robustness-versus-sensitivity limit, while generalization and publication novelty remain unresolved.

## Quality self-check, guidance contribution, and next decision

The assigned analysis-execution skill and its protocol/provider-policy/execution-handoff/research-quality references were read through the task recorder. No other skill library was used. The skill's actual contribution was to preserve every failed configuration, distinguish implementation checks from scientific evidence, keep original and improved methods, join comparisons by case, and articulate a decisive next test. Reading `research-quality.md` after the bounded search did not alter either detector or frozen parameter maps. It changed the interpretation and checks: an algebraic sensitivity ceiling and executable .7-shift counterexample were added, and the result is framed as a negative/boundary study rather than detector superiority. External skill installation and anti-defensive-writing guidance were not invoked because this isolated task explicitly restricts skill guidance to the assigned library.

Known method: robust prefix calibration, clipping, CUSUM, finite-window aggregation, confirmation, and nuisance-aware detection are established. Task-level increment: a concrete causal first-alarm implementation of worst contiguous interval deletion with missing-aware residual support, its complete paired development records, and a proved noiseless suppression/sensitivity tradeoff. Unestablished claim: publication novelty, broad minimax robustness, average-run-length control, superiority to modern robust sequential methods, or superiority on independent data.

The most decision-changing next action is the root's common blind holdout evaluation of these frozen functions and maps, with the same first-alarm loss and per-condition pairing. No change to methods or maps will follow holdout inspection. A future separate study could independently calibrate an ordinary moving-window control at comparable false-alarm levels and map performance over burst duration, shift magnitude and missing coverage; that work is outside this submission and its tuning budget. The complete study is delivered as frozen development evidence with its negative result intact.
