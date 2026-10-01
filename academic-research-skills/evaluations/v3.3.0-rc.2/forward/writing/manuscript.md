# Cost-sensitive decisions on a fixed synthetic packet: comparator choice and an exact uncertainty margin

**Methods and results research manuscript. Original-study contribution has not been locked; this is not a submission-ready full original paper.**

## Provisional synopsis

On the supplied twelve-case synthetic packet, the established cost–loss rule reduces total modeled realized cost from 440 to 222 relative to the supplied probability-above-0.5 comparator, a reduction of 218 cost units (49.55%). An exhaustive search over common probability thresholds gives a stronger, outcome-selected benchmark of 292. Classical expected-cost minimization reproduces the cost–loss rule exactly. The packet also permits an exact comparison of two fixed policies under a per-case probability-error box: their worst-case expected-cost advantage reaches zero at an error radius of 149/1080 (approximately 0.137963). This conditional margin and explicit counterexamples distinguish the observed packet-level advantage from a general performance guarantee. The probability-error radius is a sensitivity parameter, not a measured calibration statistic.

## 1. Study design and authoritative inputs

The material is a fixed, synthetic decision-cost packet supplied by the user. The twelve cases are equally weighted and include seven event outcomes. Each row supplies an event forecast pᵢ, action cost cᵢ, missed-event loss Lᵢ, and binary outcome yᵢ. The probability values are inputs rather than validated field forecasts. The costs share unspecified modeled units. All twelve rows were included; no values were imputed, rescaled, or excluded. Input hashes were checked against the supplied manifest, and an unchanged copy is retained in `input-snapshot/`.

The original draft specified the cost rule and comparator but contained no analysis implementation or completed results. The primary outcome is the sum of modeled realized costs on this packet. Additional comparator, uncertainty, and outcome-enumeration analyses were introduced after inspecting the materials. They are exploratory diagnostics, not preregistered or independent validation. There is no sampling frame, recruitment process, temporal follow-up, or causal intervention in these materials; sampling confidence intervals and significance tests are therefore not assigned.

## 2. Cost model, decisions, and prior-method equivalence

Let aᵢ ∈ {0,1} denote action. The modeled realized cost is

ℓᵢ(aᵢ,yᵢ) = aᵢcᵢ + (1−aᵢ)yᵢLᵢ, and C(a,y) = Σᵢℓᵢ(aᵢ,yᵢ).  (1)

Action incurs cᵢ for both event and non-event cases. Within this model, acting removes the missed-event loss completely. The two expected costs, when pᵢ is used as the event probability, are cᵢ for action and pᵢLᵢ for no action. Thus Aᵢ = 1[pᵢLᵢ > cᵢ], equivalently Aᵢ = 1[pᵢ > cᵢ/Lᵢ]. Equality selects no action, following the supplied specification. There are no ties for this rule in the observed packet.

This is the standard cost–loss decision rule. Murphy's original cost–loss treatment uses the same protective-action expense matrix and threshold C/L; the publisher's indexed excerpt supplies that formulation [1]. Elkan derives minimum-expected-cost decisions from general cost matrices and explicitly discusses example-dependent costs [2, Sections 1.2–1.3]. Setting C(0,0)=0, C(0,1)=Lᵢ and C(1,0)=C(1,1)=cᵢ in that framework yields the supplied rule. A separate cost-matrix implementation was compared case by case and matched all twelve decisions.

The supplied comparator is Bᵢ = 1[pᵢ > 0.5]. Its decision threshold is not the cost-optimal rule for this packet's heterogeneous ratios cᵢ/Lᵢ, which range from 0.05 to 6/7. The cost rule acts on u7 at p=0.10 yet withholds action on u3 at p=0.60; no increasing common probability threshold can reproduce both choices.

## 3. Comparators and reproducible analysis

Comparators include the specified 0.5 threshold, the equivalent classical Bayes rule, acting on every case, and acting on no case. A stronger constrained benchmark exhaustively evaluates all distinct policies 1[pᵢ > t] for t ∈ [0,1]. Because the predictions are fixed, evaluating their unique values plus the interval endpoints represents every distinct policy. Selecting the cheapest threshold after viewing outcomes is an optimistic in-packet diagnostic; it is not a trained and independently tested comparator.

An outcome-informed oracle minimizes each realized cost after y is known. It provides a descriptive lower bound, not an available decision policy. The exact comparison uses Python 3.12.14 and standard-library rational arithmetic (`fractions.Fraction`). All original decimal inputs are read exactly. No stochastic fitting, random seed, new dependency, or external dataset is involved. Running `analyze.py` regenerates the result files and runs an embedded assertion check covering the input hashes, cost totals, threshold coverage, five independent uncertainty-box corner enumerations, all 4096 binary outcome vectors, and strict tie conventions.

## 4. Fixed-packet results

Table 1. Decisions and costs for the original twelve outcomes. Expected costs use the supplied p values as a model assumption, not as validated probabilities. Costs are sums over all twelve equally weighted cases, in modeled cost units. The outcome-informed oracle is included as a descriptive bound; no forecast-expected performance interpretation is assigned to its hindsight decisions.

| Policy | Actions | Missed events | Realized cost | Expected cost under supplied p |
|---|---:|---:|---:|---:|
| Cost–loss rule | 9 | 1 | 222 | 272 |
| Supplied p > 0.5 | 5 | 3 | 440 | 356.5 |
| Classical Bayes rule | 9 | 1 | 222 | 272 |
| Act on all cases | 12 | 0 | 297 | 297 |
| Act on no cases | 0 | 7 | 560 | 434.5 |
| Outcome-informed oracle | 7 | 0 | 172 | — |

The cost rule incurs 162 action-cost units and 60 missed-event-loss units. The supplied comparator incurs 190 action-cost units and 250 missed-event-loss units. Their realized-cost difference is therefore 218, or 49.55% of the comparator's cost. The equivalent Bayes rule has the same total of 222 and no algorithmic performance difference. The outcome-selected best common threshold has cost 292, achieved for t ∈ [0.10,0.15), acting on every case except u7. Relative to that benchmark, the cost rule saves 70 units (23.97%). These comparisons preserve the original total-cost outcome rather than selecting a new favorable metric.

Table 2. Contributions to G(y) = C(B,y)−C(A,y) from the eight cases with discordant decisions. The other four cases contribute zero.

| Case | A | B | Observed contribution to G |
|---|---:|---:|---:|
| u1 | 1 | 0 | 88 |
| u2 | 1 | 0 | −10 |
| u3 | 0 | 1 | −15 |
| u5 | 1 | 0 | 60 |
| u6 | 0 | 1 | 60 |
| u7 | 1 | 0 | −5 |
| u11 | 1 | 0 | −20 |
| u12 | 1 | 0 | 60 |
| Total | | | 218 |

The negative contributions show the trade-offs within the favorable total. In particular, the event at u3 is missed by the cost rule, and extra actions on u2, u7, and u11 incur costs without event losses to avoid.

## 5. Exact expected-cost sensitivity

This diagnostic holds both action vectors and all costs fixed. Let qᵢ be a hypothetical true marginal event probability at case i. Linearity of expectation yields

G(q) = E_q[C(B,Y)−C(A,Y)] = Σᵢ(Bᵢ−Aᵢ)(cᵢ−qᵢLᵢ).  (2)

No independence between outcomes is needed for this expectation. The uncertainty set is qᵢ ∈ [max(0,pᵢ−ε), min(1,pᵢ+ε)] for every i, with ε ∈ [0,1]. This is a per-case marginal probability-error bound. Aggregate or subgroup calibration error does not establish such a bound, and ε has not been estimated from the packet.

For Aᵢ=1 and Bᵢ=0, the coefficient of qᵢ in (2) is positive, so the adverse endpoint is max(0,pᵢ−ε). For Aᵢ=0 and Bᵢ=1, the coefficient is negative, so the adverse endpoint is min(1,pᵢ+ε). Cases with equal decisions contribute zero. Because the set is a Cartesian box and the objective is additive, these endpoints attain the minimum exactly. Denote the resulting sharp lower margin by M(ε).

For this packet, G(p)=84.5. The slopes change first at ε=0.10, when u7 reaches its lower endpoint zero:

M(ε) = 84.5−640ε for 0 ≤ ε ≤ 0.10;

M(ε) = 74.5−540ε for 0.10 ≤ ε ≤ 0.15.  (3)

The unique zero is ε* = 149/1080 ≈ 0.137963. Below ε*, the fixed cost rule has strictly lower expected cost than B throughout this declared box. At ε*, an admissible endpoint vector ties their expected costs; above ε*, an admissible vector reverses the expected ranking. The witness probabilities are saved exactly in `case_results.csv`. This is a sensitivity certificate for the two fixed policies, not a claim that either is optimal for every q. Research on decisions under miscalibration already treats uncertainty in cost-induced thresholds and worst-case regret [3]; the present box calculation concerns per-case marginals and a fixed-policy pair, rather than the subgroup-calibration setting described in that source's abstract.

Table 3. Selected values of the exact lower expected-cost margin. A positive margin favors the cost rule.

| ε | M(ε), modeled cost units |
|---:|---:|
| 0 | 84.5 |
| 0.05 | 52.5 |
| 0.10 | 20.5 |
| 149/1080 | 0 |
| 0.15 | −6.5 |
| 0.20 | −28.5 |
| 1 | −102 |

## 6. Outcome counterexamples and interpretation

Keeping probabilities, costs, and both policies unchanged, all 2¹²=4096 binary outcome vectors were enumerated. The cost rule has lower realized cost for 3952 assignments and higher realized cost for 144, with no ties. G(y) ranges from −102 to 538. These are combinatorial counts, not event probabilities, estimated failure rates, or an empirical measure of deployment reliability.

A reversal can be obtained by changing three of the supplied outcomes: set u1, u5, and u12 to non-events while preserving the other nine outcomes. The cost rule then costs 222 and the supplied comparator costs 190. Exhaustive enumeration establishes that fewer than three outcome changes cannot reverse this packet's observed comparison. This constructed counterexample is separate from the authoritative input dataset.

The packet demonstrates the benefit of using heterogeneous costs in this specific modeled comparison, and the expected-cost derivation identifies the rule as an established method. The stronger common-threshold comparison, exact uncertainty margin, and explicit counterexamples make the scope of the result inspectable. Their mathematical basis is additive binary decision loss, and the calculations alone do not establish an original method or an important new empirical finding. A field-response interpretation would additionally require validated conditional forecasts, defensible costs, action effectiveness, and a real evaluation design. None is supplied by this synthetic packet.

## 7. Evidence, data, and remaining manuscript requirements

The fixed-packet results correspond to evidence IDs R1 (policy accounting), R2 (all common thresholds), R3 (sharp probability-box margin), and R4 (outcome counterexamples). `results.json`, the four CSV tables, and `analyze.py` are the reproducible source artifacts. The original provisional draft is preserved in `input-snapshot/draft.md`; expression edits are preserved separately. There is no claim of external peer review, publication, or journal compliance.

Author identities, affiliations, funding, conflicts of interest, target journal, material licence, and any formal ethics determination remain unknown. The supplied data are synthetic and contain no identified participants. This statement does not invent an ethics approval or waive a future field study's requirements. An AI assistant performed source retrieval, code creation, numerical verification, derivation, and drafting. Submission requires author review of that substantive assistance and the applicable journal policy.

## References

[1] Murphy AH. The Value of Climatological, Categorical and Probabilistic Forecasts in the Cost-Loss Ratio Situation. *Monthly Weather Review*. 1977;105:803–816. [Publisher record and indexed excerpt](https://journals.ametsoc.org/abstract/journals/mwre/105/7/1520-0493_1977_105_0803_tvocca_2_0_co_2.xml). DOI: 10.1175/1520-0493(1977)105<0803:TVOCCA>2.0.CO;2. The publisher page's full retrieval returned HTTP 403; the expense matrix and threshold were read in its indexed primary-source excerpt, not a verified complete article.

[2] Elkan C. The Foundations of Cost-Sensitive Learning. *Proceedings of IJCAI 2001*:973–978. [Author-hosted paper](https://cseweb.ucsd.edu/~elkan/rescale.pdf). Sections 1.2–1.3 supply the example-dependent cost discussion and decision threshold. The original PDF is archived in `sources/elkan2001.pdf`; the relevant text was read through the web tool.

[3] Rothblum GN, Yona G. Decision-Making Under Miscalibration. *ITCS 2023*, LIPIcs 251:92:1–92:20. [Publisher record and abstract](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITCS.2023.92). DOI: 10.4230/LIPIcs.ITCS.2023.92. This source was inspected at abstract and metadata level; its full method was not reproduced or independently evaluated here.
