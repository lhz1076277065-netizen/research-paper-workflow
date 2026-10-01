"""Reproducible single-crew scheduling research; standard library only.
Run: python research.py dev|final. Jobs are (id, processing time, deadline, reward).
"""
import csv, hashlib, itertools, json, math, random, statistics, sys, time
from fractions import Fraction
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent

def read_jobs(name):
    rows = list(csv.DictReader((BASE / "repair-input" / name).open()))
    jobs = [(r["job"], int(r["duration"]), int(r["deadline"]), int(r["value"])) for r in rows]
    assert len({j[0] for j in jobs}) == len(jobs)
    assert all(min(j[1:]) > 0 for j in jobs)
    return jobs

def reward(plan, factor=Fraction(1)):
    elapsed = 0
    value = 0
    completions = []
    for name, p, d, w in plan:
        elapsed += p * factor
        on_time = elapsed <= d
        value += w if on_time else 0
        completions.append({"job": name, "completion": float(elapsed), "deadline": d, "reward": w if on_time else 0})
    return {"value": value, "jobs": [j[0] for j in plan], "completions": completions}

def feasible(plan):
    elapsed = 0
    for _, p, d, _ in plan:
        elapsed += p
        if elapsed > d:
            return False
    return True

def density(jobs):
    plan, elapsed = [], 0
    for j in sorted(jobs, key=lambda j: (-Fraction(j[3], j[1]), j[0])):
        if elapsed + j[1] <= j[2]:
            plan.append(j)
            elapsed += j[1]
    return plan

def insertion(jobs):
    plan = []
    for j in sorted(jobs, key=lambda j: (-Fraction(j[3], j[1]), j[0])):
        candidate = sorted(plan + [j], key=lambda j: (j[2], j[0]))
        if feasible(candidate):
            plan = candidate
    return plan

def hybrid(jobs):
    singleton = max(([j] for j in jobs if j[1] <= j[2]), key=lambda s: s[0][3], default=[])
    return max([density(jobs), insertion(jobs), singleton], key=lambda s: reward(s)["value"])

def exact(jobs, factor=Fraction(1)):
    # Known Lawler-Moore EDD dynamic program, NOT a proposed new algorithm.
    ordered = sorted(jobs, key=lambda j: (j[2], j[0]))
    if not ordered:
        return []
    horizon = min(sum(j[1] for j in ordered), max(j[2] * factor.denominator // factor.numerator for j in ordered))
    dp = [None] * (horizon + 1)
    dp[0] = (0, 0)
    # ponytail: bit masks store O(n) bits/state; use predecessor reconstruction if n is very large.
    for index, (_, p, d, w) in enumerate(ordered):
        deadline = min(horizon, d * factor.denominator // factor.numerator)
        for t in range(deadline, p - 1, -1):
            old = dp[t-p]
            if old is not None and (dp[t] is None or old[0] + w > dp[t][0]):
                dp[t] = (old[0] + w, old[1] | (1 << index))
    best = max((s for s in dp if s is not None), key=lambda s: s[0])
    return [j for i, j in enumerate(ordered) if best[1] & (1 << i)]

def brute(jobs):
    # Deliberately avoids the EDD theorem: independent permutation/subset check.
    best = 0
    for length in range(len(jobs)+1):
        for plan in itertools.permutations(jobs, length):
            if feasible(plan):
                best = max(best, sum(j[3] for j in plan))
    return best

def check():
    rng = random.Random(731)
    for _ in range(40):
        jobs = [(str(i), rng.randint(1,4), rng.randint(1,12), rng.randint(1,15)) for i in range(6)]
        assert reward(exact(jobs))["value"] == brute(jobs)
        assert feasible(density(jobs)) and feasible(insertion(jobs)) and feasible(hybrid(jobs))
        assert reward(hybrid(jobs))["value"] >= reward(density(jobs))["value"]
        upper = Fraction(6,5)
        scaled = [(j[0], j[1]*6, j[2]*5, j[3]) for j in jobs]
        assert reward(exact(jobs,upper),upper)["value"] == brute(scaled)
    sequencing = [("urgent",1,1,1),("later",2,3,3)]
    assert reward(density(sequencing))["value"] == 3
    assert reward(insertion(sequencing))["value"] == 4
    subset = [("small",1,20,2),("large",20,20,20)]
    assert reward(density(subset))["value"] == 2
    assert reward(insertion(subset))["value"] == 2
    assert reward(hybrid(subset))["value"] == 20
    return {"permutation_cross_checks":40,"robust_scaled_cross_checks":40,"sequencing_and_subset_checks":"passed"}

def compare(jobs):
    result = {}
    for name, method in [("density",density),("insertion",insertion),("hybrid",hybrid),("exact",exact)]:
        begin = time.perf_counter()
        plan = method(jobs)
        duration = time.perf_counter()-begin
        result[name] = reward(plan) | {"seconds":duration}
    optimum = result["exact"]["value"]
    for r in result.values():
        r["gap"] = (optimum-r["value"])/optimum if optimum else 0
    return result

def final():
    checks = check()
    development = compare(read_jobs("development.csv"))
    validation = compare(read_jobs("validation.csv"))
    rng = random.Random(20261002)
    records, generated = [], []
    for n in [12,30,100]:
        for tightness in [0.25,0.5,0.75,1.0]:
            for repetition in range(40):
                p = [rng.randint(1,10) for _ in range(n)]
                jobs = [(str(i),p[i],max(p[i], math.ceil(sum(p)*tightness*rng.uniform(0.25,1))),rng.randint(1,100)) for i in range(n)]
                instance = f"n{n}_q{tightness}_r{repetition}"
                generated.append({"instance":instance,"jobs":jobs})
                result = compare(jobs)
                for method, r in result.items():
                    records.append({"instance":instance,"n":n,"tightness":tightness,"replicate":repetition,"method":method,"value":r["value"],"gap":r["gap"],"seconds":r["seconds"]})
    with (OUT/"generated.jsonl").open("w") as f:
        for instance in generated:
            f.write(json.dumps(instance)+"\n")
    with (OUT/"benchmark.csv").open("w",newline="") as f:
        writer = csv.DictWriter(f,fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)
    summary = {}
    for method in ["density","insertion","hybrid","exact"]:
        rows = [r for r in records if r["method"] == method]
        gaps = [r["gap"] for r in rows]
        summary[method] = {"instances":len(rows),"mean_gap":statistics.mean(gaps),"worst_gap":max(gaps),"optimal_count":sum(g==0 for g in gaps),"median_seconds":statistics.median(r["seconds"] for r in rows),"max_seconds":max(r["seconds"] for r in rows)}
    worst = max((r for r in records if r["method"] == "hybrid"), key=lambda r:r["gap"])
    example = next(g for g in generated if g["instance"] == worst["instance"])
    stress = []
    for dataset in ["development.csv","validation.csv"]:
        jobs = read_jobs(dataset)
        nominal_plan = exact(jobs)
        robust_plan = exact(jobs,Fraction(6,5))
        for factor in [Fraction(1),Fraction(21,20),Fraction(11,10),Fraction(6,5),Fraction(3,2)]:
            stress.append({"dataset":dataset,"factor":str(factor),"nominal_fixed":reward(nominal_plan,factor)["value"],"robust_1.2_fixed":reward(robust_plan,factor)["value"],"clairvoyant_optimum":reward(exact(jobs,factor),factor)["value"]})
    results = {"development":development,"validation_exposed":validation,"fresh_synthetic":summary,"checks":checks,"stress":stress,"worst_hybrid":example|{"comparison":compare(example["jobs"])},"input_hashes":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (BASE/"repair-input").glob("*") if p.is_file()},"code_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"python":sys.version,"claims":"exact DP solves this specified model; all stress/benchmark evidence synthetic; novelty not established"}
    (OUT/"results.json").write_text(json.dumps(results,ensure_ascii=False,indent=2))
    print(json.dumps({"development":{k:r["value"] for k,r in development.items()},"validation_exposed":{k:r["value"] for k,r in validation.items()},"fresh_synthetic":summary,"checks":checks,"stress":stress,"worst_hybrid_instance":worst},ensure_ascii=False,indent=2))

if __name__ == "__main__":
    if sys.argv[1:] == ["final"]:
        final()
    else:
        result = compare(read_jobs("development.csv"))
        (OUT/"development-round1.json").write_text(json.dumps(result,indent=2))
        print(json.dumps({k:{"value":r["value"],"jobs":r["jobs"],"gap":r["gap"]} for k,r in result.items()},indent=2))
