"""Exact bounded counterexample search for the two robust objectives.
Every subset/order and every Gamma=1 extreme scenario is enumerated.
"""
import itertools,json,random,time
from pathlib import Path
from uncertainty import gamma1,scenarios
OUT=Path(__file__).resolve().parent

def minimax(plan):
    worst=sum(j[3] for j in plan)
    for deviating in range(-1,len(plan)):
        elapsed,value=0,0
        for i,(_,p,d,w) in enumerate(plan):
            elapsed += 5*p+(p if i==deviating else 0)
            if elapsed<=5*d:value+=w
        worst=min(worst,value)
    return worst

def solve(jobs):
    value,best=0,[]
    examined=0
    for n in range(len(jobs)+1):
        for plan in itertools.permutations(jobs,n):
            examined+=1
            v=minimax(plan)
            if v>value:value,best=v,list(plan)
    return value,best,examined

def run():
    seed=947;rng=random.Random(seed);begin=time.perf_counter();found=None
    for repetition in range(1500):
        jobs=[(str(i),rng.randint(1,10),rng.randint(1,30),rng.randint(1,10)) for i in range(5)]
        advance,_=gamma1(jobs);av=sum(j[3] for j in advance)
        mv,plan,examined=solve(jobs)
        assert mv>=av
        if mv>av:
            found={"jobs":jobs,"advance_optimal_value":av,"advance_plan":advance,"minimax_optimal_value":mv,"minimax_plan":plan,"minimax_plan_scenarios":scenarios(plan),"plans_examined_for_counterexample":examined,"result":"strict_difference"}
            break
    result={"seed":seed,"instances_searched":repetition+1,"maximum_planned_instances":1500,"seconds":time.perf_counter()-begin,"generation":{"n":5,"p":[1,10],"d":[1,30],"w":[1,10]},"gamma":1,"deviation":"1/5","result":found if found else "no strict difference located within bounded search; not a proof of equivalence","analysis_status":"post-hoc adversarial formal model search, synthetic","novelty":"2026 nearest neighbor explicitly distinguishes these objectives; counterexample instantiates that distinction, not an original literature claim"}
    (OUT/"objective_comparison.json").write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))


def constructed():
    rows=[]
    for b in [10,20,29,30,31,100]:
        jobs=[("A",5,5,1),("B",b,b+6,1)]
        advance,_=gamma1(jobs);av=sum(j[3] for j in advance)
        mv,plan,examined=solve(jobs)
        rows.append({"b":b,"duration_ratio":b/5,"jobs":jobs,"advance_optimum":av,"minimax_optimum":mv,"minimax_plan":plan,"scenario_evaluation":scenarios(plan),"all_subset_orders_examined":examined})
        assert mv==1 and av==(1 if b<=30 else 0)
    example=[("A",5,5,1),("B",100,112,1)]
    plan,_=gamma1(example);mv,best,examined=solve(example)
    assert sum(j[3] for j in plan)==0 and mv==1
    result={"origin":"post-hoc constructive follow-up to 1500 null random instances with p<=10","epsilon":"1/5","proposition":"For A=(a,a,w), B=(b,d_B,w), if a(1+epsilon)+b<=d_B<b(1+epsilon), advance-guaranteed optimum is 0 while Gamma=1 minimax reward is w. The interval exists when b/a>(1+epsilon)/epsilon.","boundary_checks":rows,"example":{"jobs":example,"advance_optimum":0,"minimax_optimum":mv,"minimax_plan":best,"scenarios":scenarios(best),"all_subset_orders_examined":examined},"novelty":"self-contained constructive result; broad objective distinction already present in 2026 nearest-neighbor Remark 1; originality of this particular boundary is unknown"}
    (OUT/"objective_constructed.json").write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":
    import sys
    constructed() if sys.argv[1:]==["constructed"] else run()
