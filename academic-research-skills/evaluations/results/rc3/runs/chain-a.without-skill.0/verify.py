"""Closed-corpus mathematical check; all graphs and examples are synthetic."""
from datetime import datetime, timezone
from itertools import combinations
import json
from pathlib import Path


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def reach(adj, keep):
    result = [0] * len(adj)
    for u in reversed(range(len(adj))):
        if keep & (1 << u):
            for v in bits(adj[u] & keep):
                result[u] |= (1 << v) | result[v]
    return result


def inspect(adj, keep):
    n = len(adj)
    full = reach(adj, (1 << n) - 1)
    retained = reach(adj, keep)
    outside = ((1 << n) - 1) ^ keep
    excursions, covers = [0] * n, [0] * n
    for u in bits(keep):
        pending, seen = adj[u] & outside, 0
        while pending:
            bit = pending & -pending
            pending ^= bit
            if seen & bit:
                continue
            seen |= bit
            v = bit.bit_length() - 1
            excursions[u] |= adj[v] & keep
            pending |= adj[v] & outside & ~seen
        via = 0
        for v in bits(full[u] & keep):
            via |= full[v] & keep
        covers[u] = (full[u] & keep) & ~via
    returns = sum(1 << v for v in bits(outside) if full[v] & keep)
    reflection = all(not ((full[u] & keep) & ~retained[u]) for u in bits(keep))
    boundary_ok = all(not (excursions[u] & ~retained[u]) for u in bits(keep))
    cover_ok = all(not (covers[u] & ~adj[u]) for u in bits(keep))
    interval_closed = all(not (full[u] & returns) for u in bits(keep))
    return reflection, boundary_ok, cover_ok, interval_closed, excursions, covers


def example(adj, keep):
    reflection, boundary_ok, cover_ok, closed, excursions, covers = inspect(adj, keep)
    pairs = lambda rows: [[u, v] for u in bits(keep) for v in bits(rows[u])]
    return {
        "timestamps": list(range(len(adj))), "labels": ["z"] * len(adj),
        "target_edges": [[u, v] for u, row in enumerate(adj) for v in bits(row)],
        "retained_vertices": list(bits(keep)), "reachability_reflected": reflection,
        "boundary_criterion": boundary_ok, "cover_criterion": cover_ok,
        "interval_closed": closed, "excursion_pairs": pairs(excursions),
        "target_retained_cover_pairs": pairs(covers),
    }


def main():
    examples = {
        "minimum_converse_failure": example([2, 4, 0], 5),
        "interval_closure_not_necessary": example([6, 4, 0], 5),
        "indirect_retained_path_discharges_excursion": example([6, 8, 8, 0], 13),
    }
    assert not examples["minimum_converse_failure"]["reachability_reflected"]
    for name in ("interval_closure_not_necessary", "indirect_retained_path_discharges_excursion"):
        assert examples[name]["reachability_reflected"] and not examples[name]["interval_closed"]
    assert [0, 3] in examples["indirect_retained_path_discharges_excursion"]["excursion_pairs"]
    assert [0, 3] not in examples["indirect_retained_path_discharges_excursion"]["target_edges"]

    results = []
    for n in range(2, 6):
        edges = list(combinations(range(n), 2))
        totals = dict(n=n, graphs=1 << len(edges), cases=0, reflection=0,
                      converse_failures=0, interval_closed=0,
                      reflection_without_interval_closure=0,
                      boundary_obligations=0, cover_obligations=0,
                      time_compatible_retained_pairs=0)
        for edge_mask in range(1 << len(edges)):
            adj = [0] * n
            for bit, (u, v) in enumerate(edges):
                if edge_mask & (1 << bit):
                    adj[u] |= 1 << v
            for keep in range(1 << n):
                k = keep.bit_count()
                if k < 2:
                    continue
                reflection, boundary_ok, cover_ok, closed, excursions, covers = inspect(adj, keep)
                assert reflection == boundary_ok == cover_ok, (adj, keep)
                assert not closed or reflection, (adj, keep)
                totals["cases"] += 1
                totals["reflection"] += reflection
                totals["converse_failures"] += not reflection
                totals["interval_closed"] += closed
                totals["reflection_without_interval_closure"] += reflection and not closed
                totals["boundary_obligations"] += sum(row.bit_count() for row in excursions)
                totals["cover_obligations"] += sum(row.bit_count() for row in covers)
                totals["time_compatible_retained_pairs"] += k * (k - 1) // 2
        results.append(totals)
    assert sum(row["cases"] for row in results) == 27362
    report = {
        "synthetic": True,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "enumeration": "Every i<j edge subset and retained subset of size >=2, n=2..5; labels z, timestamps i",
        "checks": "reflection == boundary criterion == cover criterion; interval closure implies reflection",
        "examples": examples, "by_n": results, "total_cases": 27362,
        "general_proof_required": True,
    }
    destination = Path(__file__).with_name("verification.json")
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
