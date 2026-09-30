# When are apparent estimation gains reliable?

This is a judgement of fixed, fabricated profiles R1–R4. They are not real literature, and this document reports no new empirical results. Statements about what those profiles establish apply only within this supplied scenario; the proposed mechanisms, diagnostics and tests below remain research ideas.

## Revised scientific objective

Determine the conditions under which an apparent reduction in estimation error persists when the reference acquisition process or measurement precision changes, using only inputs available at the intended estimation time. Where those conditions cannot be verified, determine what additional information is needed to justify using the improvement.

The objective remains the reliability of apparent improvements. A larger model, a new benchmark and a particular diagnostic are possible means of answering it, not the objective itself. The draft confuses lower error on one evaluation with general robustness and confuses an engineering change with an established scientific contribution. Reporting the best of many configurations would also leave the selection procedure entangled with the claimed gain.

For a predeclared loss, define the improvement in acquisition/precision condition m as

    Δ(m) = E_m[loss(baseline estimate, target truth)]
           − E_m[loss(candidate estimate, target truth)].

Positive Δ denotes improvement. Use one primary loss, such as squared error, chosen before comparing configurations. “Reliable” should mean a gain supported across a specified set of relevant conditions, with uncertainty and harmful reversals visible. It does not mean a smaller pooled average or a guarantee over every possible environment. A meaningful minimum gain and an allowable degradation must be specified before future tests; the profiles contain no numbers from which to choose them now.

## What the profiles support, and what they leave open

| Profile | Supported within the supplied scenario | Unresolved implication |
| --- | --- | --- |
| R1 | An established correction substantially lowers average error with independently collected references. | The same conclusion cannot be extended to references sharing the target selection process. Independence is part of its demonstrated scope. |
| R2 | A larger estimator lowers average error on a random split of the same records. | Model capacity, the post-measurement proxy and the evaluation setting have not been separated. The result does not establish a usable gain under changed acquisition. |
| R3 | Simple calibration is stable under an independent acquisition change in one narrow precision range. | The supported precision domain is restricted. Stability outside it, and stability under target-dependent acquisition, remain unknown. |
| R4 | A careful replication finds that the advertised average gain vanishes when reference acquisition depends on target selection. | It demonstrates a mechanism-sensitive failure, but supplies no way to certify or diagnose dependence without target truth. |

R1 and R4 can be compatible because they describe different acquisition mechanisms; an unconditional claim would hide that boundary. R3 supplies a reason to test precision as another boundary, rather than assume every acquisition change is equivalent. R2 gives weaker support for the intended reliability claim because two obvious alternative explanations remain uncontrolled. This assessment is about the fit of the reported evidence to the claim, not a ranking of real papers.

The profiles omit estimators, losses, effect sizes, uncertainty and detailed acquisition equations. They cannot be pooled numerically or treated as a proof that all four studied the same system. A post-measurement proxy is a risk to investigate, not automatically proven leakage: a retrospective estimation task might legitimately have it available. Its timing and relationship to the target must match the proposed use case; otherwise its removal is required.

## Comparison of plausible research routes

| Route | Research question and rationale | Evidence that would distinguish its answer | Judgement |
| --- | --- | --- | --- |
| A. Capacity and input availability | Does added capacity yield a usable gain after controlling the proxy and acquisition setting? R2 leaves this possibility open. | Compare simple and larger estimators with the same admissible inputs, separately ablate the proxy, and evaluate on held-out acquisition conditions. A gain confined to the proxy-enabled random split would undermine the capacity explanation. A gain without it under the specified shifts would support a bounded capacity contribution. | Feasible as a control, but a bigger model on a fresh benchmark alone has little discriminating value. Keep secondary until the confounds are separated. |
| B. Acquisition-dependent reliability boundary | Which properties of reference acquisition preserve or reverse an existing correction's gain? R1 and R4 directly motivate this question. | Hold the target-generating process, estimator and precision fixed while varying reference selection from independent to dependent. Separately change precision. Persistence or loss of Δ then bears on the mechanism explanation, rather than simultaneous changes in model and data. | Best initial route: close to the scientific objective, supported by contrasting profiles, and tractable with symbolic reasoning and a small manufactured pilot. Its contribution would be a conditional reliability boundary, not another independent-versus-dependent demonstration already described by R4. |
| C. Diagnosis or certification without target truth | Can observable acquisition information identify when a gain is trustworthy, or trigger abstention? R4 leaves this practical gap. | First test whether opposite-gain mechanisms can generate indistinguishable observable information. If so, no diagnostic using only that information can universally separate them. Under additional stated assumptions, test any proposed indicator against sealed simulated truth and entirely held-out acquisition mechanisms. | Potentially valuable, but identifiability comes before fitting a diagnostic. Neither the existence of a universal certificate nor the sufficiency of an observable discrepancy score is established. |
| D. Precision limits of simple calibration | Does R3's stability extend beyond its narrow precision range, and how does precision interact with acquisition dependence? | Vary precision with acquisition fixed, then test the interaction with acquisition. Stable gains would broaden a conditional domain; collapse confined to precision or to its interaction would distinguish those failure modes. | A useful companion to B. A precision sweep alone risks losing the wider reliability question; use it to test an explicit boundary hypothesis. |

The routes share a common comparison: an apparent gain may reflect a real but conditional correction, access to a target-related proxy, a restricted precision domain, or an evaluation procedure that concealed a failure. More than one explanation can hold. The next work should separate them rather than force one winner from a pooled average.

## Chosen next discriminating work

Start with **B, preceded by C's identifiability check**, and include one controlled precision contrast from D. Do not start a broad model search. This sequence tests whether a useful reliability claim is identifiable and what drives its boundary, before spending effort optimizing an estimator whose evaluation may be misleading.

**First, specify the information and mechanism.** Write a minimal symbolic model with latent target truth T, operational inputs X, reference measurement R, target inclusion S, and measurement precision p. Fix the estimation time and list which quantities are observable then. Describe independent reference acquisition and acquisition influenced by target selection explicitly; do not silently equate correlation, shared selection and dependence on truth. Keep scoring truth unavailable to the estimator, diagnostic and tuning procedure. These are proposed model assumptions, not facts supplied by R1–R4.

The immediate discriminating deliverable is an identifiability memo: attempt to construct two allowed acquisition mechanisms with the same distribution of operationally observable information but opposite signs of Δ for a fixed correction. If such a pair can be constructed, a universally valid truth-free certificate from those observables is impossible within that model class: it would see the same information in both worlds and have to make the same decision. Record the construction and the assumptions on which it depends. If no pair is found, that alone is not a proof of identifiability; seek a derivation under explicit restrictions before making the claim.

This check determines whether route C can proceed with existing observables, needs observable selection metadata or an independently acquired reference sample, or must narrow its guarantee. Failure of a universal certificate is not failure of the scientific objective: it identifies what information reliable inference requires. Conversely, a sufficient condition proved under restrictions would justify a conditional certificate, not general robustness.

**Second, prepare a small discriminating simulator pilot, to be run only as subsequent work.** The simulator would operationalize the symbolic assumptions and keep truth sealed for scoring. Use the same generated target process and matched random seeds across conditions to reduce irrelevant variation. Begin with the four cells formed by independent versus target-dependent reference acquisition and precision inside versus outside the nominated narrow range. Keep training and final evaluation draws separate; reserve an acquisition mechanism or strength not used during tuning. The actual precision range is absent from R3, so pilot values would be manufactured choices, not reproduced literature thresholds.

Compare a fixed simple baseline, an explicitly specified existing-style correction, and a simple calibration. The profiles do not provide their formulas, so these would illustrate the proposed mechanisms rather than reproduce R1–R4. Fix configurations before the held-out comparison. Use a larger estimator only in a separately controlled capacity/proxy ablation if it adds a necessary distinction. The unavailable-at-estimation-time proxy must not enter the primary pipeline; a proxy-enabled arm may illustrate the alternative explanation, clearly labelled with its timing assumptions.

Report Δ and its uncertainty separately for each mechanism/precision cell, alongside baseline and candidate errors. Retain repeated draws and all predeclared comparisons instead of selecting the best configuration. The cellwise results expose a gain that disappears or reverses despite a favourable pooled average. If a truth-free indicator survives the symbolic check, evaluate both its false assurances and its abstentions against sealed truth; do not tune its threshold on the same mechanisms used to claim transfer. No simulator has been executed for this judgement.

## How the next evidence changes the plan

- **Opposite-gain worlds are observationally indistinguishable:** restrict route C to explicit assumptions or added acquisition information. Continue B to characterize which assumptions matter; do not market an observable heuristic as a universal reliability test.
- **Gain disappears when dependence changes at fixed precision:** prioritize the acquisition boundary. Extend beyond R4 by deriving a sufficient condition, a graded boundary or an information requirement; repeating its contrast alone is insufficient contribution evidence.
- **Gain disappears when precision changes with acquisition fixed:** prioritize the calibration domain in D. If only their combination causes failure, investigate the interaction rather than attribute it entirely to dependence.
- **R2-style gain disappears after proxy removal or acquisition holdout:** reject the current evidence for a capacity-driven robust improvement. A surviving gain with matched admissible inputs permits route A to advance, with its tested domain stated.
- **All tested cells improve:** broaden the challenge conditions and inspect whether the simulator assumptions excluded the relevant failure. Finite manufactured successes support only that model class and test set; they do not establish general robustness.

The intended contribution is therefore an evidenced statement about when an improvement can be trusted, and what prevents trust when it fails. A conditional result or a demonstrated information limit can answer that question. At this stage those are candidate contributions. Real scientific novelty, practical applicability and any field-level generalization remain unassessed; fabricated profiles and an unrun pilot cannot establish them.
