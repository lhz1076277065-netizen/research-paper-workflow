"""Synthetic ordered-DAG boundary check; no input corpus or external libraries.

Run with the common Python interpreter. The general claim is proved in answer.md;
this independent finite enumeration checks examples and the implemented criterion.
"""
import json
from pathlib import Path
from time import perf_counter


def adjacency(n, edges):
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    adj = [set() for _ in range(n)]
    for u, v in edges:
        if not (isinstance(u, int) and isinstance(v, int) and 0 <= u < v < n):
            raise ValueError("edges must strictly increase integer timestamps")
        adj[u].add(v)
    return adj


def reachability(adj, retained):
    """Positive reachability in the induced graph on retained vertices, via DFS."""
    result = set()
    for start in retained:
        seen, todo = set(), list(adj[start] & retained)
        while todo:
            vertex = todo.pop()
            if vertex in seen:
                continue
            seen.add(vertex)
            todo.extend((adj[vertex] & retained) - seen)
        result.update((start, vertex) for vertex in seen)
    return result


def excursions(adj, retained):
    """Pairs linked by a path of length >= 2 whose internal vertices are outside."""
    if not retained <= set(range(len(adj))):
        raise ValueError("retained vertices must belong to the target graph")
    result = set()
    for start in retained:
        seen, todo = set(), list(adj[start] - retained)
        while todo:
            vertex = todo.pop()
            if vertex in seen:
                continue
            seen.add(vertex)
            for nxt in adj[vertex]:
                if nxt in retained:
                    result.add((start, nxt))
                elif nxt not in seen:
                    todo.append(nxt)
    return result


def interval_closed(n, retained, target_reach):
    """Independent test: no omitted vertex lies between two retained endpoints."""
    return not any(
        (start, omitted) in target_reach and (omitted, end) in target_reach
        for omitted in set(range(n)) - retained
        for start in retained for end in retained
    )


def describe(n, edges, retained):
    adj = adjacency(n, edges)
    retained = set(retained)
    boundary = excursions(adj, retained)
    source_reach = reachability(adj, retained)
    target_reach = reachability(adj, set(range(n)))
    missing = {(u, v) for u, v in target_reach if u in retained and v in retained} - source_reach
    return {
        "timestamps": list(range(n)), "labels": ["z"] * n,
        "target_edges": sorted(map(list, edges)), "retained": sorted(retained),
        "source_edges": sorted([u, v] for u, v in edges if u in retained and v in retained),
        "source_reachability": sorted(map(list, source_reach)),
        "excursion_pairs": sorted(map(list, boundary)),
        "missing_source_pairs": sorted(map(list, missing)),
        "bidirectional": not missing,
        "interval_closed": interval_closed(n, retained, target_reach),
    }


def main():
    started = perf_counter()
    examples = {
        "inducedness_insufficient": describe(3, {(0, 1), (1, 2)}, {0, 2}),
        "interval_closure_unnecessary": describe(3, {(0, 1), (1, 2), (0, 2)}, {0, 2}),
        "replacement_need_not_be_an_edge": describe(4, {(0, 1), (1, 3), (0, 2), (2, 3)}, {0, 1, 3}),
        "sparse_boundary": describe(4, {(0, 1), (1, 2), (2, 3), (1, 3)}, {0, 1, 3}),
    }
    assert examples["inducedness_insufficient"]["missing_source_pairs"] == [[0, 2]]
    assert not examples["inducedness_insufficient"]["bidirectional"]
    assert examples["interval_closure_unnecessary"]["bidirectional"]
    assert not examples["interval_closure_unnecessary"]["interval_closed"]
    assert examples["replacement_need_not_be_an_edge"]["bidirectional"]
    assert [0, 3] not in examples["replacement_need_not_be_an_edge"]["source_edges"]
    assert examples["sparse_boundary"]["excursion_pairs"] == [[1, 3]]
    try:
        adjacency(2, {(1, 0)})
    except ValueError:
        pass
    else:
        raise AssertionError("invalid time order was accepted")

    counts = {key: 0 for key in ("graphs", "images", "preserved", "interval_closed", "preserved_not_interval_closed", "failed_bidirectional")}
    for n in range(6):
        possible = [(u, v) for u in range(n) for v in range(u + 1, n)]
        vertices = set(range(n))
        for graph_mask in range(1 << len(possible)):
            edges = {edge for i, edge in enumerate(possible) if graph_mask & (1 << i)}
            adj = adjacency(n, edges)
            target = reachability(adj, vertices)
            counts["graphs"] += 1
            for image_mask in range(1 << n):
                retained = {v for v in range(n) if image_mask & (1 << v)}
                source = reachability(adj, retained)
                target_pairs = {(u, v) for u, v in target if u in retained and v in retained}
                assert source <= target_pairs
                preserved = source == target_pairs
                boundary = excursions(adj, retained)
                assert preserved == (boundary <= source), (n, edges, retained)
                closed = interval_closed(n, retained, target)
                assert closed == (not boundary)
                assert not closed or preserved
                counts["images"] += 1
                counts["preserved"] += preserved
                counts["interval_closed"] += closed
                counts["preserved_not_interval_closed"] += preserved and not closed
                counts["failed_bidirectional"] += not preserved

    # ponytail: materializes O(|S|^2) boundary pairs; use compressed relations if scale matters.
    k, middle = 8, 8
    quadratic_edges = {(u, middle) for u in range(k)} | {(middle, v) for v in range(middle + 1, 2 * k + 1)}
    quadratic_retained = set(range(2 * k + 1)) - {middle}
    quadratic_pairs = excursions(adjacency(2 * k + 1, quadratic_edges), quadratic_retained)
    assert len(quadratic_pairs) == k * k
    result = {
        "scope": "all identity inclusions in all timestamp-ordered DAGs with 0..5 vertices; constant label z",
        "examples": examples, "enumeration": counts,
        "criterion_mismatches": 0,
        "quadratic_boundary_example": {"retained_vertices": 2 * k, "omitted_vertices": 1, "target_edges": len(quadratic_edges), "boundary_pairs": len(quadratic_pairs)},
        "check_elapsed_seconds": round(perf_counter() - started, 6),
        "status": "assertions_passed",
    }
    Path(__file__).with_name("results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "enumeration": counts, "criterion_mismatches": 0, "check_elapsed_seconds": result["check_elapsed_seconds"]}))


if __name__ == "__main__":
    main()
