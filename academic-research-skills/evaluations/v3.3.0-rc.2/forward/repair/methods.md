# Methods and model boundaries (research notes, not a submission manuscript)

All calculations concern one crew, release times zero, no interruption, omitted repairs consuming no time, and reward earned only at C_j <= d_j. Durations/deadlines/rewards in supplied files are synthetic and have no physical units specified.

## Nominal exact comparator

The standard EDD exchange argument sorts a feasible selected set by ascending deadline without lowering its reward. Processing the ordered jobs, DP[t] stores the largest reward of a feasible subset ending at time t. Descending updates for t<=d_j compare skip with DP[t-p_j]+w_j. The state invariant proves optimality by induction. Scalar objective complexity is O(nD), D=min(sum p,max d); the supplied bitmask reconstructs a selected set. This is a Lawler-Moore implementation, not an algorithm contribution. See Hermelin et al. (2022), Lemma 9 and Theorem 1; the 1969 publisher abstract was read but its full original text was not available in this run.

Density admission ignores deadline interactions. The two-job family (p,d,w)=(1,B,2),(B,B,B), integer B>2, has density-greedy reward 2, optimum B and approximation ratio 2/B. EDD insertion retains the same failure; a singleton fallback fixes this family but still has 22.60% maximum observed loss in the 480-instance new synthetic battery. The brute permutation/subset oracle checks correctness on 40 six-job instances; it is independent of EDD ordering.

## Uniform box uncertainty

If each duration lies in [p_j,1.2p_j], a fixed plan's earned reward is nonincreasing in every duration. All upper durations therefore attain its worst-case total reward. Omitting jobs that fail at that vertex cannot reduce reward. Solve the known DP with d'_j=floor(5d_j/6); execute the returned plan with original durations. This is a monotonic robust reduction, not a new robust-optimization principle. Sensitivity evaluates a fixed selected sequence without discarding late jobs during execution. Clairvoyant reoptimization is an unattainable upper comparator, not an operational policy.

## Budgeted uncertainty and advance guarantees

At most one duration gains p_j/5. A selected prefix has maximum completion sum(p)+max(p)/5. EDD again preserves feasibility: moving an earlier-deadline job before a later one gives it a subset prefix, while the later job inherits the original pair's prefix. The robust completion bound is monotone in a prefix's set. For EDD jobs define DP[t,m] as the greatest weight of a robust-feasible subset with nominal total t and largest selected duration m. Skip, or include job j if 5(t+p_j)+max(m,p_j)<=5d_j. Taking the best state is exact for maximum reward of jobs individually promised on time in every allowed scenario. Induction: every feasible subset is reachable; equal t,m states have identical future feasibility, so retain only maximum weight. Complexity O(nD pmax), with max-duration states restricted to durations occurring in the input; no claim of strong polynomiality. Independent exhaustive subset/permutation/scenario checks used 30 five-job instances; each of the 240 new generated plans was checked in all single-deviation extreme scenarios. Intermediate deviations cannot exceed these extremes.

The 2026 nearest neighbor already proves EDD structure and develops a DP carrying the top-Gamma deviations for unweighted advance promises. Our weighted proportional Gamma=1 state compression is a working adaptation. Literature coverage does not establish originality. Its Remark 1 distinguishes sum_j max_s U_j from max_s sum_j U_j; these objectives must not be exchanged.

## Constructive boundary after a negative search

A bounded search of 1500 five-job instances with p in [1,10] located no strict optimal-value difference between advance guarantees and scenario-wise worst-case total reward. This does not prove equivalence. Widening duration imbalance yields a rigorous two-job construction:

A=(a,a,w), B=(b,d_B,w), with a(1+epsilon)+b <= d_B < b(1+epsilon), epsilon>0, w>0, Gamma=1.

Neither job can be promised individually even when processed alone: A's own deviation exceeds its deadline, and B's own deviation exceeds d_B. Thus advance-guaranteed optimum=0. In order A,B, an A-deviation loses A but B still finishes by d_B; a B-deviation preserves A but loses B; no deviation earns 2w. Consequently minimum scenario total reward=w. No policy earns more in every scenario because either selected job can fail under its own deviation. The admissible d_B interval exists exactly when b/a>(1+epsilon)/epsilon. This is a sufficient family construction, not a general classification of all instances.

For epsilon=1/5,a=5,b=100,d_B=112,w=1: nominal completion=(5,105); A-deviation completion=(6,106); B-deviation completion=(5,125). Advance optimum=0; minimax total optimum=1. Five subset/orders exhaust all policies. Six boundary instances b=10,20,29,30,31,100 with d_B=b+6 confirm the transition at b>30; the large-size contrast is why the earlier bounded generator missed it. This instantiated distinction and its threshold are useful model diagnostics; novelty beyond the checked 2026 source remains unknown.

## Reproduction and applicability

Run research.py final; uncertainty.py; objective_search.py; objective_search.py constructed using the supplied Python environment. Runtime measurements describe single local invocations, exclude data generation/checks, and are not statistically established speed comparisons. Generated batteries are synthetic algorithm evidence. Transport, multiple crews, electrical dependencies, reward calibration, duration distributions, and the appropriate advance-versus-ex-post objective are unknown. Tan et al. (2019) uses network restoration/energization time, so the present additive deadline model does not reproduce observed electricity restoration.

The Gamma=1 objective comparison uses a cardinality/discrete scenario set: delta_j in {0,1}, sum(delta)<=1. A single deviating duration may vary up to its endpoint with the same guarantees. It does not permit several durations to share a continuous fractional deviation budget; worst-case joint reward under that alternative requires additional interior-scenario analysis.
