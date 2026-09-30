# Research judgement: when is an apparent estimation gain reliable?

This is a plan and a reasoned comparison using **fabricated development profiles R1–R4**. They are stipulated evidence within this exercise, not real publications or evidence of publication priority. No observations were collected, simulator was run, or empirical finding produced.

## Scientific objective and revised question

Keep the objective: determine when an apparent improvement in an estimation system deserves reliance. A smaller average error on one benchmark is an observation about that evaluation; it does not by itself establish deployment reliability, a causal explanation, or novelty.

A defensible primary question is:

> Under what reference-acquisition mechanisms and measurement-precision ranges does an apparent estimation gain persist on independently assessed targets, and what evidence is needed before relying on that gain in a new acquisition regime?

The practical user of the answer is someone choosing whether to adopt a correction, calibration, or larger estimator. A useful answer would delimit where adoption is justified, where an independent audit is needed, and where evidence remains insufficient. A boundary finding or a well-supported null result can answer this question without introducing a new algorithm.

For a later study, freeze a baseline, loss, deployment population, acquisition regimes, and input-availability rule. Define the gain in a regime c as

**Δ(c) = E_c[loss(baseline, Y) − loss(candidate, Y)].**

Positive Δ means lower expected loss for the candidate. “Reliable” should mean that the positive gain is estimated honestly and persists within the **declared** operating domain, with uncertainty and any precision or subgroup failures visible. It should not mean success under every conceivable distribution. Average gain is the primary quantity here; predeclared tail or precision-stratum checks guard against a favorable average hiding relevant failures.

## What the profiles establish—and leave open

| Profile | Supported within the supplied profile | Not established | Consequence for the plan |
|---|---|---|---|
| R1 | An established correction substantially improves average error when references are acquired independently of the target outcome. | Its behavior when references and targets share a selection process. | Keep this correction as an essential comparator; do not relabel its established gain as a new method. |
| R2 | A larger estimator reports lower average error on a random split of the same records, with a post-target proxy among its inputs. | Gain after removing that proxy; input availability at the intended decision time; transport to changed acquisition conditions. | Capacity is still a plausible explanation, but so are proxy dependence and split-specific advantage. The current result cannot distinguish them. |
| R3 | Simple calibration remains stable under an independent acquisition change in one narrow precision range. | Stability or failure outside that range; stability under selection-dependent reference acquisition. | Precision is a plausible effect modifier to test, not a proven universal limitation. |
| R4 | In a careful replication, an advertised average gain disappears when the reference process becomes dependent on target selection. | That all dependence destroys gains, that dependence is the only failure mechanism, or that it can be diagnosed without target truth. | The mechanism contrast is a strong starting point. Repeating it unchanged would add little; a justified boundary or diagnosis question could add knowledge. |

“Post-target” is a warning about provenance and timing, not proof that R2's estimator is unusable: the intended prediction time is unspecified. The future input audit must decide which measurements exist at that time. Likewise, independence concerns the **acquisition process**, not an assumption that reference values contain no information about Y. Do not silently treat R1's outcome-independence and R4's selection-dependence as exact opposites; explicitly model their relationship first.

## Comparison of plausible routes

### Route A — Acquisition mechanism and the boundary of reliable gains: prioritize

**Question.** Does the gain of the established correction or simple calibration depend on how reference observations and target records are selected, and where does it remain defensible?

**Closest profiles and proposed increment.** R1 and R4 already motivate an acquisition boundary; R3 adds a possible precision interaction. The proposed increment is an explicit set of assumptions and a falsifiable operating-domain boundary, including whether observable acquisition information can support a deployment decision. It is a proposed mechanism/boundary contribution, not demonstrated novelty.

**Plausible explanation.** The correction estimates quantities valid under one acquisition process; selection dependence can change those quantities or their relation to the target population. Precision may alter sensitivity to that change. This is an idea to examine, not an established explanation of R4.

**Evidence needed.** An explicit selection/measurement model; matched acquisition contrasts that hold other factors fixed; independently assessed target truth in any later performance evaluation; precision strata; comparison against the uncorrected baseline and R3-style calibration. A later simulator can manufacture these contrasts, but would support conclusions only about its modeled mechanisms.

**What would weaken it.** Under controlled contrasts, dependence has no meaningful effect on gain, while a different factor explains the change; or the predicted boundary fails despite satisfied assumptions. Such a result would narrow this route and favor capacity or precision explanations.

**Feasibility and value of a null.** Symbolic work and a small manufactured pilot are available. An explicit demonstration that a particular dependence is harmless would prevent an overbroad “dependence always invalidates improvement” rule. This route most directly preserves the scientific objective and resolves the tension among R1, R3, and R4.

### Route B — Genuine capacity gain versus proxy/split advantage: retain as a comparator

**Question.** Does the larger estimator improve independently evaluated error using only inputs available at the intended decision time, including under a changed acquisition process?

**Closest profile and increment.** R2. An input-timing audit, proxy removal, and acquisition-aware validation would distinguish explanations that its random split cannot. A reproducible capacity gain could be useful, but “larger model on a new benchmark” alone is not a justified originality claim.

**Evidence needed.** Later compare the same larger estimator with and without the proxy, against a smaller estimator using the same legitimate inputs. Freeze tuning, evaluate on untouched records from changed acquisition conditions, and keep any reference-estimation step inside the training boundary. Evaluate the proxy-inclusive version separately only if its availability is justified. Removal losing the gain shows reliance on that feature; it does not alone prove leakage or isolate model capacity.

**What would weaken it.** The gain vanishes without the proxy or on an honest acquisition shift. A remaining gain would support capacity within the tested domain, still not general robustness. A null result would explain why the original apparent advantage was insufficient for adoption.

**Priority.** Feasible and important as a control, but weaker as the central route because it currently conflates capacity, input provenance, and evaluation design. Resolve those distinctions before expanding configurations.

### Route C — Precision limits of simple calibration: focused fallback or part of A

**Question.** Within which precision ranges does the simple calibration retain its gain or stability, and does that range change with acquisition mechanism?

**Closest profile and increment.** R3, with R4 motivating a crossed mechanism contrast. The increment would be a measured or derived applicability boundary, not the unsupported assertion that calibration fails outside R3's range.

**Evidence needed.** A later controlled precision sweep with independent target assessment, including points inside and outside the reported range, crossed with acquisition regimes. Separate changed precision from changed selection. Compare calibration, correction, and an uncalibrated baseline using a fixed rule and loss.

**What would weaken it.** No meaningful precision interaction across the declared domain; or apparent precision effects disappear once selection is controlled. This null would broaden the supported range or shift attention toward acquisition.

**Priority.** A tractable, interpretable fallback. Incorporate a small precision contrast in A to avoid misattributing a precision effect to acquisition. Do not turn the entire study into a precision benchmark before resolving the mechanism question.

### Route D — A truth-free deployment diagnostic: high value, conditional feasibility

**Question.** Can information available without target truth distinguish a regime in which the gain is trustworthy from one in which it is not?

**Closest profile and increment.** R4 explicitly leaves this open. A valid diagnostic, or a proof of non-identifiability under stated observables, could change practice. Lack of a diagnostic in R4 is not evidence that none exists or that this proposal is first.

**Evidence needed.** First specify the accessible variables: reference values, target covariates, acquisition records, inclusion probabilities, timing, and any design intervention. Then test whether different admissible mechanisms can produce the same accessible evidence while implying different dependence or gain. If so, an assumption-free diagnostic on those variables cannot work; identify the additional provenance, independent truth audit, or intervention needed. If not, derive an observable implication under explicit assumptions and test it later.

**What would weaken it.** Observational equivalence defeats the proposed diagnostic; or later cases with the same diagnostic output have opposite performance conclusions. A valid impossibility result remains informative, but a weak heuristic with no identification argument would not justify deployment.

**Priority.** Investigate its identifiability immediately as part of A; do not commit to building a diagnostic before this check. Acquisition metadata may help, but metadata's existence alone does not establish its accuracy or sufficiency.

## The next discriminating work

**Choose an acquisition-model and identifiability audit first, followed conditionally by a manufactured mechanism-by-precision pilot.** The audit is cheap, can expose a fatal information gap, and determines what the later simulator must represent. A capacity search before this audit could lower an evaluation score while leaving the reliability question unanswered.

The audit should produce a short assumptions-and-counterexamples sheet:

1. Define target selection S, reference acquisition A, target truth Y, legitimate pre-decision inputs X, reference measurements Z, precision q, and the post-target proxy P. Draw candidate selection/measurement graphs. Explain whether independence means unconditional or conditional independence and whether it concerns Y, S, or both. Do not assert that the brief already specifies such a graph.
2. State the deployment observables and desired Δ(c). Seek two admissible worlds with the same observable evidence but different gain signs, and separately seek worlds with different acquisition dependence. A performance ambiguity is not automatically a proof that acquisition dependence is undiagnosable.
3. If equivalence is possible, determine the least additional information capable of breaking it—such as a documented independent reference-acquisition intervention or an independently sampled truth audit—and state the remaining assumptions. If a sufficient observable implication can instead be derived, spell out its failure cases.
4. Use this result to freeze the candidate operating domain and a minimal simulator specification. Advance to a pilot only once its outputs can distinguish the competing explanations. If neither observable information nor a feasible audit can answer the full question, explicitly restrict the claim to a modeled boundary; do not replace the objective with “our code runs.”

A small **symbolic illustration**, not an empirical result, shows why the information check matters. Suppose the only performance-relevant observable in a new regime is Z, taking −1 and +1 equally often, and observable metadata are identical between worlds. Let the baseline predict 0 and the candidate predict Z; use squared loss. In world W+, Y = Z, so baseline risk is 1, candidate risk is 0, and Δ = +1. In world W−, Y = −Z, so baseline risk is 1, candidate risk is 4, and Δ = −3. The observable Z distribution is identical. No rule using only these stipulated observables can certify the sign in both worlds. This establishes a limited non-identifiability example for gain; it does **not** identify R4's mechanism, prove all truth-free diagnostics impossible, or describe actual data. Additional validated assumptions or information can exclude one world.

If the audit justifies a pilot, specify it now but **do not run it in this task**:

| Design element | Planned contrast | What it distinguishes |
|---|---|---|
| Reference acquisition | Independent design versus explicit selection-dependent design, keeping the target population fixed | Acquisition sensitivity; avoid confounding a changed mechanism with a different target population |
| Precision | One setting inside R3's narrow range and settings below and above it, defined numerically before running | Precision boundaries and mechanism-by-precision interaction |
| Estimator | Uncorrected baseline, established correction, simple calibration, larger estimator with legitimate inputs | Mechanism robustness versus complexity benefit |
| Proxy | Separate justified proxy-inclusive and proxy-removed variants | Feature reliance; assess availability before interpreting it as leakage |
| Evaluation | Sealed manufactured target truth; separate fitting, tuning, and final evaluation; independent repetitions fixed before viewing results | Honest estimation of Δ, uncertainty, and protection against selecting a lucky configuration |

Specify the manufactured generative mechanisms and selection strength before running; their numerical choices are design decisions, not supplied facts. Keep the final evaluation untouched after selection. Report the full predeclared set of relevant contrasts and uncertainty; if configurations are explored, treat them as exploration and require a fresh confirmation set. No precise sample size, effect size, or success probability can be justified from these summaries alone. Set the smallest practically meaningful gain and desired uncertainty first, then choose pilot scale accordingly.

The pilot's decision rule should be qualitative until those quantities are fixed: a gain confined to one acquisition regime supports a conditional boundary; a precision interaction motivates C; a legal-input capacity gain that persists across declared regimes motivates B; opposite gain conclusions under equivalent diagnostic evidence rule out that proposed diagnostic. A null, an inferior correction, or an informative counterexample should still be reported. Simulator success would justify a mechanism hypothesis and a better real-study design, not an empirical claim about the world.

## Replacement for the weak draft

> Compare an established correction, simple calibration, and a larger estimator to a fixed baseline to determine the acquisition and precision conditions under which apparent gains can be relied on. First specify the selection/measurement assumptions and available information, audit input timing, and test identifiability with counterexamples. Use that result to design a small manufactured pilot crossing acquisition mechanism and precision with independently evaluated target truth. Freeze the loss, tuning and evaluation boundaries, and reporting rules; report relevant gains, uncertainty, failures, and nulls rather than only the best configuration. Treat a robust method, a boundary, and a diagnostic as competing proposed contributions. Make a novelty claim only after appropriate real-literature checking and make a deployment claim only with evidence for the intended domain.

## Decision and evidence limits

Continue with **A**, starting with the audit above; retain **C** as its precision check, **B** as a necessary competing explanation/comparator, and **D** as a conditional goal. This choice maximizes discriminating value using the supplied resources while preserving the reliability question.

All profile-based claims trace to the frozen research brief. The synthetic profiles are the only nearest-neighbor comparison here; no real-literature search was performed, and no priority, general robustness, empirical effect, or validated diagnostic is claimed. The remaining uncertainty is substantive: the profiles do not fully specify acquisition graphs, precision ranges, legal deployment inputs, or what additional information is observable. Those are the first design questions, not grounds for claiming that the problem is solved.
