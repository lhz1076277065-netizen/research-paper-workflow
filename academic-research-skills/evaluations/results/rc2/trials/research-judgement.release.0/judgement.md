# Research judgement: when is an apparent estimation gain reliable?

R1–R4 are fabricated study profiles supplied for this reasoning task, not real publications or empirical evidence. Statements below about what they establish refer only to those profiles. The proposed research and the constructed example are not findings from a new study.

## Revised scientific commitment

Study **when an observed improvement in estimation error survives a change in reference acquisition and measurement precision, and what information permits a justified decision to use that improvement**. The intended knowledge gain is a defensible reliability boundary, possibly with a conditional diagnostic or an abstention rule. A bigger model, a new benchmark, and a lower selected average error do not by themselves supply that gain.

Declare the target quantity, estimation decision time, admissible inputs, deployment population, acquisition mechanisms and precision range before evaluating methods. For a concrete initial analysis, use squared error and define the gain of candidate $f_1$ over baseline $f_0$ in regime $(a,p)$ as

\[
\Delta(a,p)=E_{Q_{a,p}}[(f_0(O)-T)^2-(f_1(O)-T)^2].
\]

Here $T$ is target truth and $O$ is information available at the declared decision time. Positive gain in one regime is a local statement. A reliability claim needs positive gain, with uncertainty and a practically relevant margin specified in advance, across the declared regimes or a validated rule that limits use to suitable regimes. Average error may remain the primary estimand, but inspect error tails and selection strata so an aggregate gain does not conceal consequential deterioration. The deployment regimes, margin and consequential errors are currently unspecified; they are research design choices, not known facts.

## What the supplied profiles establish and leave open

| Profile | Evidence within the supplied profile | Remaining uncertainty and implication |
|---|---|---|
| R1 | An established correction improves average error when reference acquisition is independent of the target outcome. | References obtained through target selection were not evaluated. Reusing this correction in that setting is an extrapolation; independently collected-reference improvement is already covered. |
| R2 | A larger estimator improves average error on a random split of the same records. | A post-target proxy raises an input-availability or leakage concern. Timing alone does not prove leakage: its origin and availability at the intended decision must be checked. There is no proxy-removal result or acquisition-shift evaluation, so capacity, proxy access and shared acquisition conditions remain competing explanations. |
| R3 | Simple calibration is stable under one independent acquisition change within a narrow precision range. | Stability outside that range is unknown. It is neither evidence of general robustness nor evidence of inevitable failure elsewhere. |
| R4 | A careful replication loses the advertised average gain when reference acquisition depends on target selection. | This identifies a failure setting and distinguishes the two tested mechanisms. It does not show that every dependent mechanism fails, locate the boundary, or provide a target-truth-free diagnostic. Merely repeating its disappearance result adds little new knowledge. |

Together these profiles motivate separate questions about mechanism, precision and information availability. They do not establish a universal ordering of methods or publication novelty. A real novelty claim would require real nearest-neighbour literature verification; that is outside this fixed-material task.

## Comparison of plausible research routes

| Route | Potential knowledge increment relative to R1–R4 | Evidence that would distinguish it from alternatives | Priority and limitation |
|---|---|---|---|
| **A. Explain the correction's reliability boundary.** Derive when acquisition dependence changes the sign or size of gain. | Extend R1/R4 from two tested settings to explicit sufficient conditions, failure mechanisms or useful bounds. | An explicit measurement-and-selection model; proofs or counterexamples; a planned manufactured pilot that varies dependence while holding information, precision and evaluation protocol fixed. Compare against a precision-only explanation. | High value and feasible with symbolic reasoning. An arbitrary simulator threshold would describe that simulator, not establish a general law. |
| **B. Diagnose whether to use the improvement without observing target truth.** | Address R4's unresolved practical obstacle: whether lawful observables support a reliable use/abstain decision. | First test identifiability: can admissible worlds have identical available observations but opposite gains? If additional constraints resolve this, derive a conditional diagnostic or gain bound, then challenge it on held-out mechanisms. | **First discriminating route.** Its feasibility changes the whole plan. Dependence detection and certification of beneficial correction are different tasks; detecting one does not automatically solve the other. |
| **C. Determine the precision envelope of simple calibration.** | Extend R3's narrow domain and distinguish precision failure from acquisition failure. | Keep acquisition fixed and change measurement precision; separately change acquisition at matched precision. Require error uncertainty and a mechanism explanation, not just a fitted threshold. | Strong, relatively economical fallback or companion to A/B. A broader numerical range alone is a limited increment; a transferable condition would be more useful. |
| **D. Test a larger estimator fairly.** | Determine whether capacity yields additional reliable gain after controlling proxy access and regime coverage. | Audit decision-time inputs; compare proxy-present and proxy-removed variants, simple correction/calibration and the larger estimator with the same permissible inputs and tuning budget; evaluate changed acquisition and precision regimes. | Lower initial priority. R2's current comparison cannot isolate capacity. Keep this route if simpler methods have a substantive limitation and its gain survives the controls; do not rank it by model size. |

Choose **B, supported by A's mechanism analysis**, before expanding the model search. A diagnostic could make reliability actionable, while an information barrier would prevent wasted work on an impossible general promise and identify what extra assumptions or acquisition information is needed. C resolves a distinct uncertainty rather than serving as an automatic replacement for the scientific objective. D is a method candidate, not the research question.

## Analytical check completed now

For an illustrative correction, let the baseline be $f_0=X$, the corrected estimator be $f_1=X-C$, and $C$ be a reference-derived correction available at the decision time. Under squared error and finite second moments,

\[
\Delta=2E[C(X-T)]-E[C^2]
       =2E[CX]-2E[CT]-E[C^2].
\]

The cross term with raw estimation error can change with acquisition, while the correction's second moment can change with precision. This is an algebraic explanation of why those factors deserve separate investigation; it does not assert which term caused the outcomes in the fabricated profiles.

There is a concrete barrier under an **unrestricted latent-target model**. Let $C$ take $-1,+1$ with equal probability and let the observable raw measurement satisfy $X=C$. Use the same observable acquisition/precision labels and recorded metadata in both worlds:

| Constructed world | Unobserved target $T$ | Baseline risk | Corrected risk | Gain |
|---|---:|---:|---:|---:|
| A | $0$ | $1$ | $0$ | $+1$ |
| B | $C$ | $0$ | $1$ | $-1$ |

The complete stipulated observable distribution is identical, yet the beneficial action reverses. Hence no rule using only those observables can uniformly certify the sign of gain over this unrestricted class. Even infinitely many observations of that same law would not resolve the missing relationship between $C$ and $T$. `check_reasoning.py` recomputes both risks and the identity using exact rational arithmetic; it is an arithmetic self-check of an invented example, not simulator or empirical evidence.

**Scope of this result:** these worlds are deliberately constructed, not recovered from R1–R4. They do not encode the full independent/dependent acquisition mechanisms described there, prove that dependence itself is always unobservable, or establish impossibility under a justified shared-error model, known randomization, a target constraint or informative auxiliary measurements. Known acquisition design can distinguish mechanisms that this unrestricted example does not. The useful conclusion is that a universal target-truth-free gain certificate needs substantive restrictions; an observable correlation or many additional same-source records is insufficient by itself.

## Next discriminating work and decision branches

The immediate next work is **a model-specific symbolic identifiability check**, not a benchmark search. Write an explicit target measurement, reference measurement and target-selection model; specify which errors are shared, what acquisition randomization or timing is known, what precision information is observable, and which target constraints are justified. R1–R4's summaries do not provide those equations or constraints, so they must remain proposed assumptions until supported. Then seek two worlds that satisfy *all* those constraints and preserve *all* available observations while changing the sign of \(\Delta\). Alternatively derive an identification formula or sharp, informative bounds. Keep proof failures distinct from actual counterexamples.

This produces three useful branches:

1. **Opposite-sign observationally equivalent worlds remain admissible.** Restrict the scientific claim to partial identification or conditional use, and identify the smallest extra information or acquisition intervention that separates the worlds. Examples to assess include known randomized reference collection or a justified shared-error constraint; neither is automatically sufficient. Do not train a universal diagnostic on an unidentifiable target.
2. **A justified restriction identifies gain or bounds it away from zero.** State the condition as a candidate reliability certificate. Next plan a small manufactured pilot to test implementation and failure behaviour inside and outside that condition. Success would support the specified model only; it would not validate real deployment.
3. **Information is sufficient, but precision makes the gain sign unstable.** Prioritize C: derive a precision-dependent boundary and a conditional use rule, then test whether acquisition shift moves that boundary. This retains the same reliability objective.

If the symbolic result warrants the pilot, its proposed design is:

- Cross independent versus selection-dependent reference acquisition with precision settings spanning a declared narrow calibration regime and its exterior; R3 motivates this contrast but supplies no numerical range. Specify at least two distinct dependence mechanisms so a diagnostic cannot merely recognize one simulator recipe. This is a design proposal, not a reconstruction of any profile's data.
- Start with the simple correction/calibration baselines. Introduce the larger estimator only for a stated capacity hypothesis; audit the post-target proxy and evaluate its removal. Extra truth access must not be called an algorithmic advantage under the same information budget.
- Keep simulator truth available to the evaluator for computing gain but unavailable to any proposed runtime diagnostic. Diagnostics may use only the declared lawful observations and metadata. Hold out entire mechanism/precision combinations and independent runs, rather than randomly splitting records from one acquisition process.
- Separate exploration from a locked comparison. Fix candidate selection, primary gain, uncertainty procedure and held-out evaluation before inspecting evaluation truth. Retain all tested configurations and negative outcomes; account for tuning effort. Reporting only the best run would confound reliable improvement with selection of favourable noise.
- Interpret the controlled outcomes: disappearance after proxy removal implicates the proxy explanation; disappearance only under mechanism change implicates transport assumptions; changes under precision manipulation implicate the precision envelope; surviving all declared controls supports only that declared envelope. More than one explanation may operate, and each result can motivate a follow-up rather than force a single winner.

No pilot or new empirical study was conducted here. The deliverable is the revised scientific problem, comparison, bounded analytical result and discriminating next action. The proposed diagnostic, generalized correction and robust larger estimator remain ideas; none is established by this task.
