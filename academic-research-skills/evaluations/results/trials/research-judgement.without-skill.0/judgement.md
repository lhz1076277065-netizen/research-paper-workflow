# Research judgement: when is an apparent estimation gain reliable?

**Decision:** Replace the larger-model benchmark proposal with a study of the conditions under which an estimated gain survives valid prediction timing, acquisition changes, and changes in measurement precision. First determine what can be identified from the observables available before target truth is revealed. A simulator pilot is a subsequent, conditional step; none has been run here.

## Evidence status and revised question

R1–R4 are fabricated profiles supplied for this development evaluation. They are premises for this comparison, not real publications or empirical findings. Their summaries contain no estimator formulas, original observations, or precision units. They cannot support a faithful implementation or reproduction of the described methods, publication priority, or an actual novelty claim.

The scientific question remains: **Under which acquisition mechanisms and precision conditions does an apparent reduction in average estimation error represent a reproducible improvement, and what evidence lets an investigator recognize those conditions?**

Use a fixed baseline and candidate to define a paired gain

\[
G(m,q)=\mathbb E_{P_{m,q}}[L(\hat Y_0,Y)-L(\hat Y_1,Y)],
\]

where `m` is the acquisition mechanism, `q` is measurement precision, and both estimates are scored against the same target truth in a declared target population. Positive `G` means the candidate helps under that condition. Squared error is a provisional loss for the analytical illustration below; the eventual loss and a scientifically meaningful minimum gain must be fixed before a pilot. Population changes must be stated separately from changes to the reference process: mixing them would make a mechanism explanation ambiguous.

“Reliable” should mean that a gain survives evaluation in a prespecified, bounded deployment envelope with inputs available at the intended prediction time. It does not mean that the method improves everywhere. Report the gain and its uncertainty by mechanism and precision, with bias and a prespecified tail or subgroup loss to check whether a favorable average conceals consequential deterioration. A single lower benchmark mean cannot establish that claim.

Working timing assumption: estimation is intended before the target truth is available. If the actual task is retrospective and a downstream variable is legitimately available, its interpretation changes; that timing must be resolved before comparing estimators.

## What the supplied profiles establish, and what they leave open

| Profile | Established within the supplied fictional profile | Consequence for this plan | Unresolved question |
|---|---|---|---|
| R1 | An established correction improves average error with references collected independently of the target outcome. | Use a simple correction as a serious candidate; model size is not the only plausible explanation of a gain. | Does its gain survive a reference process connected to target selection? Independence alone is not a universal guarantee for every correction rule. |
| R2 | A larger estimator has lower average error on a random split of the same records, while using a proxy recorded after the target measurement. | Audit predictor availability and use identical clean inputs for a capacity comparison. | The proxy may be legitimate in a retrospective task or may transmit unavailable target information. The profile does not distinguish these possibilities or demonstrate acquisition robustness. |
| R3 | Simple calibration is stable under an independent acquisition change within one narrow precision range. | Precision is a separate candidate boundary condition and must be varied independently of acquisition. | Stability outside that range, under dependent acquisition, or for other procedures is unestablished. |
| R4 | A carefully executed replication loses the advertised average gain when the reference process depends on target selection. | Take the mechanism failure seriously; merely repeating this contrast would add little to the supplied knowledge. | Can investigators detect the relevant dependence, or predict gain failure, without target truth? The summary supplies no such diagnostic. |

Do not assume the procedures, populations, precision scales, or losses in R1, R3, and R4 are identical. Their profiles motivate controlled comparisons; they cannot be pooled quantitatively.

## Plausible research routes

| Route | Scientific proposition and discriminating evidence | Why it is plausible | Limits and decision value |
|---|---|---|---|
| **A. Acquisition dependence and identifiability** | A correction's useful domain depends on how reference acquisition relates to target selection or outcome. Ask whether declared observables distinguish acquisition mechanisms and, separately, whether they predict the sign of `G`. Begin with competing symbolic worlds; later hold precision fixed while changing only the acquisition mechanism in manufactured worlds. | R1 and R4 indicate that an acquisition contrast matters in their reported settings. The missing practical issue is recognition of a failure regime before truth is known. | Identifiability may fail without process provenance, assumptions, or some truth measurements. Recognizing a process label is not the same as proving a positive gain. This route can eliminate an impossible diagnostic claim before implementation. |
| **B. Precision boundary of simple methods** | Calibration may work only when measurement precision lies in a bounded range. Hold acquisition fixed and vary precision; then cross the two factors to test whether the boundary depends on acquisition. | R3 directly supports stability in a narrow range and leaves the surrounding range open. | A precision sweep alone cannot explain selection dependence or cure unavailable predictors. It can yield a useful conditional operating range, but “outside the reported range” is a gap, not proof of a new mechanism. |
| **C. Genuine capacity gain after timing controls** | A larger estimator may improve error even after removal of unavailable downstream information. Compare small and large estimators with the same predecision inputs and evaluation conditions; compare any legitimate proxy version separately. | R2 provides an apparent capacity gain that has not been separated from the proxy or acquisition conditions. | Its clean gain could persist, disappear, or reverse. A loss after proxy removal would not alone prove causally that leakage caused the original gain. This is an important control, but it is less direct evidence about recognizing acquisition failure. |

These explanations can coexist. For example, larger capacity might help within one precision range and still fail after a dependent acquisition change. Compare them through isolated interventions, not a contest in which each route changes several things at once.

**Choose A first, with B as the immediate boundary test and C as a controlled comparator when estimator development becomes necessary.** The supplied profiles already make unrestricted robustness implausible, and A addresses the missing link between a favorable result and a trustworthy decision. The cheap first task is analytical: establish whether the proposed information could distinguish the answers at all. No hardware or computational limitation forces this ordering; its benefit is scientific discrimination.

## Next discriminating work: specify observables, then test identifiability

1. **Declare the information set.** Inventory predecision predictors, reference values, precision metadata, and any selection or acquisition provenance. State which facts are observed, recorded by design, assumed, or hidden. Independence from the target outcome, an association with an observed selection variable, and a shared acquisition protocol are different assertions. Process records or randomized acquisition may establish aspects of the mechanism without observing every target truth; outcome independence is not generally readable from an unlabeled reference distribution.
2. **Construct observationally indistinguishable worlds.** Require identical distributions of the permitted observables but different mechanism or reliability answers. If such worlds exist, a universally correct diagnostic based only on those observables cannot exist. If provenance excludes one world, repeat the test with that expanded information set and state the extra assumption.
3. **Identify the minimum rescue.** Candidates include a documented randomized reference acquisition that enforces the relevant independence, or an independently sampled truth audit that measures gain directly. The latter gives up a strictly truth-free assessment, which should be acknowledged. Randomized acquisition by itself still does not establish the gain of an arbitrary estimator. Other identifying assumptions would need an explicit argument, not a correlation threshold invented for convenience.

A minimal analytical example checks why this task matters. It is an invented illustration, **not** R1's correction, R4's replication, or a simulator result. Suppose only \(R\in\{-1,+1\}\), an otherwise constant input, and fixed precision are observed. Let `R` have equal probabilities. Compare baseline \(\hat Y_0=R\) with correction \(\hat Y_1=0\), using squared error.

| Hypothetical world | Hidden truth mechanism | Baseline risk | Correction risk | Gain |
|---|---|---:|---:|---:|
| I | `Y` is an independent, equally probable sign. | 2 | 1 | +1 |
| D | The equally probable truth `Y` determines the acquired reference, `R=Y`. | 0 | 1 | −1 |

Both worlds give exactly the same observable distribution of `R`; their error gains have opposite signs. In I, \(\mathbb E[RY]=0\); in D, \(\mathbb E[RY]=1\). Since both squared values equal one, the baseline risk is \(2-2\mathbb E[RY]\), while the correction risk is one. These are exact expectations over hypothetical finite worlds, with no generated observations. The accompanying runnable check verifies those calculations and the equal observable distributions.

**What this establishes:** without additional assumptions or information, that minimal observable distribution cannot identify the sign of the correction's gain. **What it does not establish:** that all acquisition diagnostics are impossible, that every real method behaves this way, that the exact R1–R4 mechanisms have been reproduced, or that the problem remains unidentified once trustworthy acquisition provenance is available. If selection metadata reveal a defining mechanism directly, diagnosing that mechanism may be easy, while diagnosing its effect on loss can remain unresolved.

The next substantive deliverable should therefore be an assumption-and-observable specification plus either an identifiability argument or an explicit impossibility result for that specification. A diagnostic algorithm is warranted only after its required information is justified.

## Conditional pilot plan, not an experiment conducted here

If the specification identifies a feasible conditional diagnostic or reliability boundary, use the inexpensive manufactured simulator to test that precise proposition. Specify a minimal mathematical estimator and data-generating mechanism first: the profiles do not provide enough detail to implement their actual procedures. Label any chosen toy rule accordingly.

- Independently vary reference-acquisition dependence and measurement precision, including conditions within and outside the proposed stable range. Include an independent acquisition change to address R3's reported setting. Keep the target population fixed for the first mechanism contrast; evaluate population transfer separately.
- Compare the candidate with a fixed simple baseline on paired target truths. Fix the loss, meaningful gain threshold, diagnostic output, and unacceptable tail or subgroup deterioration before examining pilot outcomes.
- Expose only the declared observables to a diagnostic. Use manufactured target truth solely to evaluate it. A diagnostic that silently uses truth at deployment fails the proposed truth-free claim.
- Separate estimator or diagnostic tuning worlds from final evaluation worlds. Hold out complete acquisition conditions or data-generating families, rather than relying on a random record split. Use independent replications and evaluate uncertainty appropriate to those independent units. A random split remains useful for a limited within-condition question.
- Record all planned configurations and failed cases. Choose configurations using the development partition; freeze the choice before final evaluation. Reporting the best configuration from the final test would confound improvement with selection among trials.

**Discriminating predictions:** an acquisition explanation requires a gain change under the acquisition intervention with precision and estimator fixed. A precision explanation requires a gain change under the precision intervention with acquisition fixed. A capacity explanation requires a surviving advantage for the larger model on identical clean inputs; survival under changed acquisition is an additional test. Interactions would justify a joint conditional boundary rather than selecting one explanation by average rank.

**Decision rules:** if the symbolic information set cannot identify reliability, stop universal diagnostic development and state what additional information is required. If a manufactured diagnostic succeeds only within assumed mechanisms, report that bounded domain and challenge it with a held-out family. If gains disappear under dependence or outside a precision range, map the failure boundary rather than renaming the method “generally robust.” If clean capacity gains survive, retain them as a conditional result, not as proof of mechanism independence.

The defensible contribution currently proposed is an explicit connection among acquisition assumptions, observable information, precision, and trustworthy gain claims. Its feasibility has been sharpened by the analytical counterexample. Empirical validation, superiority of any estimator, and publication novelty remain unestablished.
