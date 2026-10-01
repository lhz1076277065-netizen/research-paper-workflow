"""Reproduce the first NYC topic action; constructed worlds are not observations."""
from pathlib import Path
import csv
import hashlib
import json
import math
import platform
import sys

import numpy as np
import scipy
from scipy.stats import rankdata, spearmanr
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parent


def records(name):
    value = json.loads((ROOT / "raw" / (name + ".json")).read_text())
    assert isinstance(value, dict) and len({len(x) for x in value.values()}) == 1
    return [dict(zip(value, row)) for row in zip(*value.values())]


def select(name, measure, period):
    rows = [r for r in records(name) if (r["GeoType"], r["MeasureID"], r["TimePeriodID"])
            == ("UHF42", measure, period)]
    assert len(rows) == len({r["GeoID"] for r in rows}) == 42
    assert all(isinstance(r["Value"], (int, float)) and math.isfinite(r["Value"]) for r in rows)
    assert all(r["CI"] == "" for r in rows)
    assert all(r["Note"] in ("", "* Estimate is based on small numbers so should be interpreted with caution.") for r in rows)
    return {r["GeoID"]: r["Value"] for r in rows}


def joint(p, q, x):
    # Rows: no AC / AC. Columns: household cooling opportunity / none.
    cells = np.array([[x, p - x], [q - x, 1 - p - q + x]])
    assert cells.min() >= -1e-12
    assert np.allclose(cells.sum(axis=1), [p, 1-p])
    assert np.allclose(cells.sum(axis=0), [q, 1-q])
    return cells


def bounds(p, q):
    assert 0 < p <= 1 and 0 <= q <= 1
    return max(0, p + q - 1) / p, min(p, q) / p


def check():
    # Verify analytic common-household bounds against an independent LP.
    for p in (.05, .2, .7, 1.):
        for q in (0., .1, .5, .95, 1.):
            equality = [[1, 1, 0, 0], [1, 0, 1, 0], [1, 1, 1, 1]]
            answers = []
            for sign in (1, -1):
                r = linprog([sign, 0, 0, 0], A_eq=equality,
                            b_eq=[p, q, 1], bounds=(0, None), method="highs")
                assert r.success
                answers.append(r.x[0] / p)
            assert np.allclose(answers, bounds(p, q))
    assert np.array_equal(rankdata([.1, .3, .9]), rankdata(np.exp([.1, .3, .9])))


def main():
    check()
    ac = select("2185", 781, 46)
    vegetation = select("2143", 690, 46)
    temperature = select("2141", 688, 47)
    assert ac.keys() == vegetation.keys() == temperature.keys()
    names = {r["GeoID"]: r["Name"] for r in records("GeoLookup") if r["GeoType"] == "UHF42"}
    cautions = {r["GeoID"]: r["Note"] for r in records("2185")
                if (r["GeoType"], r["MeasureID"], r["TimePeriodID"]) == ("UHF42", 781, 46)}
    ids = sorted(ac)
    p = np.array([(100-ac[i])/100 for i in ids])
    g = np.array([vegetation[i]/100 for i in ids])
    t = np.array([temperature[i] for i in ids])
    assert np.all((p > 0) & (p < .5)) and np.all((g > 0) & (g < 1))
    # Two admissible probability tables with SAME household marginals. q=.5 is
    # a hypothetical extra measurement, NOT inferred from vegetation land area.
    worlds = []
    for i, a in zip(ids, p):
        lo, hi = bounds(a, .5)
        first, second = joint(a, .5, a*lo), joint(a, .5, a*hi)
        worlds.append({"GeoID": i, "Name": names[i], "observed_no_ac_fraction": a,
                       "observed_land_vegetation_fraction": vegetation[i]/100,
                       "hypothetical_household_opportunity_fraction": .5,
                       "world_zero": first.tolist(), "world_one": second.tolist(),
                       "no_ac_conditional_opportunity_bounds": [lo, hi]})
    def top(values):
        return [ids[k] for k in np.argsort(-values, kind="stable")[:10]]
    top_no_ac, top_land_deficit = top(p), top(1-g)
    # A conventional ecological product is only a descriptive shortcut.
    top_product = top(p*(1-g))
    def describe(values):
        return [{"GeoID": i, "Name": names[i]} for i in values]
    result = {
        "n_geographic_units": 42,
        "independence": "42 spatial districts, not independent households; no iid p-values or intervals",
        "time": {"AC_and_vegetation": 2017, "LST": "July 17, 2018 daytime Landsat spatial mean"},
        "no_ac_percent_range": [float(p.min()*100), float(p.max()*100)],
        "land_vegetation_percent_range": [float(g.min()*100), float(g.max()*100)],
        "AC_small_sample_flags": sum(bool(cautions[i]) for i in ids),
        "AC_intervals": "none supplied; plug-in summaries do not represent survey uncertainty",
        "sensitivity_unflagged_only": {"n": sum(not cautions[i] for i in ids),
              "no_ac_vs_vegetation": float(spearmanr([p[k] for k,i in enumerate(ids) if not cautions[i]],
                                                     [g[k] for k,i in enumerate(ids) if not cautions[i]]).statistic)},
        "spearman_descriptive": {"no_ac_vs_vegetation": float(spearmanr(p,g).statistic),
                                 "no_ac_vs_one_day_LST": float(spearmanr(p,t).statistic),
                                 "vegetation_vs_one_day_LST": float(spearmanr(g,t).statistic)},
        "top10_no_ac_fraction": describe(top_no_ac),
        "top10_land_vegetation_deficit": describe(top_land_deficit),
        "top10_ecological_product_p_times_one_minus_g": describe(top_product),
        "overlap_no_ac_vs_land_deficit": len(set(top_no_ac)&set(top_land_deficit)),
        "overlap_no_ac_vs_product": len(set(top_no_ac)&set(top_product)),
        "world_result": "42/42 districts permit both 0 and 1 subgroup opportunity in the constructed same-household marginal scenario q=.5; q is not observed",
        "identification": "Land-area vegetation g is not household opportunity q. Without a link between them, observed g imposes no household joint-marginal restriction. Constructed worlds prove ambiguity, not actual harm or actual exposure.",
        "inputs": {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
                   for f in sorted((ROOT/"raw").glob("*.json"))},
        "environment": {"python": sys.version, "platform": platform.platform(),
                        "numpy": np.__version__, "scipy": scipy.__version__},
        "checks": "20 common-household marginal cases agree with LP; joins unique, finite, complete; constructed marginals exact; monotone probability rank invariant"
    }
    out = ROOT/"derived"
    out.mkdir(exist_ok=True)
    with (out/"uhf42-aligned.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["GeoID", "Name", "no_AC_percent_2017_complement", "vegetation_land_percent_2017", "LST_F_2018_07_17", "AC_source_note"])
        writer.writerows((i, names[i], round(100-ac[i],10), vegetation[i], temperature[i], cautions[i]) for i in ids)
    (out/"constructed-worlds.json").write_text(json.dumps(worlds,ensure_ascii=False,indent=2))
    (out/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k: result[k] for k in ["n_geographic_units", "no_ac_percent_range", "land_vegetation_percent_range", "AC_small_sample_flags", "sensitivity_unflagged_only", "spearman_descriptive", "overlap_no_ac_vs_land_deficit", "overlap_no_ac_vs_product", "world_result", "checks"]},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
