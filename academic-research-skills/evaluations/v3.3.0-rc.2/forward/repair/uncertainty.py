"""Post-hoc robust extension: maximize reward guaranteed job by job.
At most one selected job takes 20% extra time; no estimated probability claim.
Run: python uncertainty.py. Uses existing nominal solver from research.py.
"""
import csv, itertools, json, math, random, statistics, time
from fractions import Fraction
from pathlib import Path
from research import read_jobs, exact, reward
OUT = Path(__file__).resolve().parent

def gamma1(jobs):
    ordered = sorted(jobs,key=lambda j:(j[2],j[0]))
    states = {(0,0):(0,0)}
    peak = 1
    # ponytail: O(n*D*pmax) states/work ceiling; generic Gamma needs top-Gamma deviations.
    for index, (_,p,d,w) in enumerate(ordered):
        updated = dict(states)
        for (elapsed,largest),(value,mask) in states.items():
            key = (elapsed+p,max(largest,p))
            if 5*key[0]+key[1] <= 5*d:
                if key not in updated or value+w > updated[key][0]:
                    updated[key] = (value+w, mask|(1<<index))
        states = updated
        peak = max(peak,len(states))
    best = max(states.values(),key=lambda x:x[0])
    return [j for i,j in enumerate(ordered) if best[1]&(1<<i)],peak

def scenarios(plan):
    values, guaranteed = [], set(j[0] for j in plan)
    for deviating in range(-1,len(plan)):
        elapsed, value, early = Fraction(0),0,set()
        for i,(name,p,d,w) in enumerate(plan):
            elapsed += p + (Fraction(p,5) if i==deviating else 0)
            if elapsed <= d:
                early.add(name); value += w
        values.append(value)
        guaranteed &= early
    return {"minimum_total_reward":min(values),"jobwise_guaranteed_reward":sum(j[3] for j in plan if j[0] in guaranteed),"guaranteed_jobs":sorted(guaranteed),"scenario_count":len(values)}

def brute_gamma(jobs):
    best = 0
    for n in range(len(jobs)+1):
        for plan in itertools.permutations(jobs,n):
            value = sum(j[3] for j in plan)
            if value > best and scenarios(plan)["jobwise_guaranteed_reward"] == value:
                best = value
    return best

def run():
    rng = random.Random(831)
    for _ in range(30):
        jobs = [(str(i),rng.randint(1,4),rng.randint(1,15),rng.randint(1,20)) for i in range(5)]
        plan,_ = gamma1(jobs)
        assert sum(j[3] for j in plan) == brute_gamma(jobs)
        assert scenarios(plan)["jobwise_guaranteed_reward"] == sum(j[3] for j in plan)
    distinction = [("A",10,11,1),("B",20,33,1)]
    distinction_result = scenarios(distinction)
    assert distinction_result["minimum_total_reward"] == 1
    assert distinction_result["jobwise_guaranteed_reward"] == 0
    real_inputs = {}
    for name in ["development.csv","validation.csv"]:
        jobs = read_jobs(name)
        nominal = exact(jobs)
        box = exact(jobs,Fraction(6,5))
        budgeted,peak = gamma1(jobs)
        real_inputs[name] = {"nominal_plan":reward(nominal)|scenarios(nominal),"box20_plan":reward(box)|scenarios(box),"gamma1_plan":reward(budgeted)|scenarios(budgeted),"gamma1_peak_states":peak,"gamma1_under_all_jobs_20percent":reward(budgeted,Fraction(6,5))["value"]}
    rng = random.Random(20261003)
    records,generated = [],[]
    for n in [12,30,100]:
        for q in [0.25,0.5,0.75,1.0]:
            for r in range(20):
                p = [rng.randint(1,10) for _ in range(n)]
                jobs = [(str(i),p[i],max(p[i],math.ceil(sum(p)*q*rng.uniform(0.25,1))),rng.randint(1,100)) for i in range(n)]
                begin = time.perf_counter(); budgeted,peak = gamma1(jobs); seconds=time.perf_counter()-begin
                box = exact(jobs,Fraction(6,5)); nominal=exact(jobs)
                nv,bv,gv = [reward(plan)["value"] for plan in [nominal,box,budgeted]]
                assert bv <= gv <= nv
                assert scenarios(budgeted)["jobwise_guaranteed_reward"] == gv
                instance=f"n{n}_q{q}_r{r}"
                records.append({"instance":instance,"n":n,"tightness":q,"nominal_optimum":nv,"box20_guarantee":bv,"gamma1_guarantee":gv,"gamma1_seconds":seconds,"peak_states":peak})
                generated.append({"instance":instance,"jobs":jobs})
    with (OUT/"uncertainty_benchmark.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    with (OUT/"uncertainty_generated.jsonl").open("w") as f:
        for g in generated:f.write(json.dumps(g)+"\n")
    result={"scope":"weighted jobwise advance guarantees, Gamma=1, proportional 20% deviations; NOT minmax total reward or measured outage benefit","origin":"post-hoc after nominal/stress results and 2026 nearest-neighbor read","parameters":{"gamma":1,"deviation_fraction":"1/5","seed":20261003,"replicates":20,"n":[12,30,100],"tightness":[0.25,0.5,0.75,1]},"checks":{"independent_permutation_scenario_checks":30,"objective_distinction":distinction_result,"all_240_generated_gamma1_plans_feasible_in_all_single_deviation_scenarios":True},"inputs_exploratory":real_inputs,"fresh_synthetic_summary":{"instances":len(records),"mean_gain_over_box":statistics.mean(r["gamma1_guarantee"]-r["box20_guarantee"] for r in records),"mean_gain_fraction_of_nominal":statistics.mean((r["gamma1_guarantee"]-r["box20_guarantee"])/r["nominal_optimum"] for r in records),"strict_gain_instances":sum(r["gamma1_guarantee"]>r["box20_guarantee"] for r in records),"median_seconds":statistics.median(r["gamma1_seconds"] for r in records),"max_seconds":max(r["gamma1_seconds"] for r in records),"peak_states":max(r["peak_states"] for r in records)},"novelty":"not established; 2026 primary paper already has EDD structure and top-Gamma-deviation DP; this special weighted/proportional implementation is not evidence of a new general scheduling method"}
    (OUT/"uncertainty_results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__ == "__main__":run()
