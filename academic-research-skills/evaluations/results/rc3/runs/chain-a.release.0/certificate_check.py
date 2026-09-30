"""Synthetic ordered-DAG checks; uses only the Python standard library."""
from itertools import combinations
from pathlib import Path
import json


def target_relation(n, edges):
    # Floyd closure; all directed edges respect the integer time order.
    reach = [[False] * n for _ in range(n)]
    for a, b in edges:
        reach[a][b] = True
    for k in range(n):
        for a in range(n):
            for b in range(n):
                reach[a][b] |= reach[a][k] and reach[k][b]
    return {(a, b) for a in range(n) for b in range(n) if reach[a][b]}


def induced_relation(retained, edges):
    # Independent DFS over the induced graph, rather than reusing Floyd.
    adjacency = {a: [] for a in retained}
    for a, b in edges:
        if a in retained and b in retained:
            adjacency[a].append(b)
    relation = set()
    for start in retained:
        seen, pending = set(), list(adjacency[start])
        while pending:
            node = pending.pop()
            if node not in seen:
                seen.add(node)
                pending.extend(adjacency[node])
        relation.update((start, node) for node in seen)
    return relation


def assess(n, edges, retained):
    assert all(0 <= a < b < n for a, b in edges)
    assert retained <= set(range(n))
    full = target_relation(n, edges)
    restricted = {(a, b) for a, b in full if a in retained and b in retained}
    internal = induced_relation(retained, edges)
    covers = {(a, b) for a, b in restricted
              if not any((a, c) in restricted and (c, b) in restricted
                         for c in retained)}
    interval_closed = not any(
        (a, x) in full and (x, b) in full
        for a, b in combinations(sorted(retained), 2)
        for x in set(range(n)) - retained)
    return {
        'equivalence': internal == restricted,
        'cover_condition': covers <= edges,
        'interval_closed': interval_closed,
        'retained': sorted(retained),
        'edges': sorted(map(list, edges)),
        'internal_reachability': sorted(map(list, internal)),
        'target_reachability_on_retained': sorted(map(list, restricted)),
        'covers': sorted(map(list, covers)),
        'missing_covers': sorted(map(list, covers - edges)),
    }


def main():
    counterexample = assess(3, {(0, 1), (1, 2)}, {0, 2})
    nonnecessary = assess(3, {(0, 1), (1, 2), (0, 2)}, {0, 2})
    assert not counterexample['equivalence']
    assert not counterexample['cover_condition']
    assert nonnecessary['equivalence'] and not nonnecessary['interval_closed']

    graphs = cases = equivalence_cases = strict_examples = 0
    mismatches = []
    for n in range(6):
        possible = list(combinations(range(n), 2))
        for edge_mask in range(1 << len(possible)):
            edges = {edge for i, edge in enumerate(possible) if edge_mask >> i & 1}
            graphs += 1
            for retained_mask in range(1 << n):
                retained = {i for i in range(n) if retained_mask >> i & 1}
                result = assess(n, edges, retained)
                cases += 1
                if n < 3:
                    assert result['equivalence']  # A smaller target cannot fail.
                equivalence_cases += result['equivalence']
                strict_examples += result['equivalence'] and not result['interval_closed']
                if result['equivalence'] != result['cover_condition']:
                    mismatches.append({'n': n, **result})
                assert not result['interval_closed'] or result['equivalence']
                # Covers generate exactly the restricted partial order.
                generated = induced_relation(retained, set(map(tuple, result['covers'])))
                assert generated == set(map(tuple, result['target_reachability_on_retained']))
                # Every cover is indispensable within this generating certificate.
                for edge in map(tuple, result['covers']):
                    smaller = set(map(tuple, result['covers'])) - {edge}
                    assert edge not in induced_relation(retained, smaller)
    assert not mismatches, mismatches[:1]
    assert graphs == 1100 and cases == 33867
    chain = assess(8, {(i, i + 1) for i in range(7)}, set(range(8)))
    layers = assess(8, {(a, b) for a in range(4) for b in range(4, 8)}, set(range(8)))
    assert len(chain['covers']) == 7 and len(chain['target_reachability_on_retained']) == 28
    assert len(layers['covers']) == len(layers['target_reachability_on_retained']) == 16
    output = {
        'synthetic': True,
        'model': 'finite simple DAG; all labels z; vertex i timestamp i; induced inclusion of retained subset; distinct-vertex nonempty-path reachability',
        'enumeration_scope': 'all forward edge masks and retained subsets for n=0..5; not a proof for arbitrary n',
        'graphs': graphs, 'graph_subset_cases': cases,
        'equivalence_cases': equivalence_cases,
        'equivalence_without_interval_closure_cases': strict_examples,
        'cover_equivalence_mismatches': len(mismatches),
        'certificate_size_examples': {
            'chain_8': {'cover_pairs': 7, 'reachable_pairs': 28},
            'two_layers_4_plus_4': {'cover_pairs': 16, 'reachable_pairs': 16},
        },
        'minimal_converse_counterexample': counterexample,
        'interval_closure_not_necessary': nonnecessary,
        'certificate_scope': 'unique irredundant generating relation of the known restricted reachability order; no runtime or oracle-query minimality claim',
    }
    destination = Path(__file__).with_name('checks.json')
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in output.items() if not isinstance(v, dict)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
