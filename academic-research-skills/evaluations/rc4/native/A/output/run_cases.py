"""Reproduce the local checks; no external dependencies, no manuscript fabrication."""
from pathlib import Path
import csv
import itertools
import json
from collections import Counter

OUT = Path(__file__).resolve().parent


def save(case, name, value):
    p = OUT / case / name
    p.parent.mkdir(exist_ok=True, parents=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    return value


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def main():
    rows = list(csv.DictReader((OUT / 'direction-no-data/raw/hour.csv').open()))
    weather = {}
    for code in ['1', '2', '3', '4']:
        group = [r for r in rows if r['weathersit'] == code]
        weather[code] = {'hours': len(group), 'dates': len({r['dteday'] for r in group}),
                         'years': dict(Counter(r['yr'] for r in group))}
    timestamps = {(r['dteday'], r['hr']) for r in rows}
    total_days = len({r['dteday'] for r in rows})
    bike = save('direction-no-data', 'suitability.json', {
        'rows': len(rows), 'days': total_days, 'unique_timestamps': len(timestamps),
        'missing_hours_on_731_day_grid': 731 * 24 - len(rows), 'weather': weather,
        'cnt_equals_casual_plus_registered': all(int(r['cnt']) == int(r['casual']) + int(r['registered']) for r in rows),
        'date_range': [min(r['dteday'] for r in rows), max(r['dteday'] for r in rows)]})
    assert bike['rows'] == len(timestamps) == 17379 and weather['4']['hours'] == 3

    occupation = '51-4041.00'
    snapshots = {}
    for version in ['20_0', '30_0']:
        base = OUT / 'human-collection' / ('v' + version)
        tasks = [r for r in csv.DictReader((base / 'Task Statements.txt').open(), delimiter='\t') if r['O*NET-SOC Code'] == occupation]
        ratings = [r for r in csv.DictReader((base / 'Task Ratings.txt').open(), delimiter='\t') if r['O*NET-SOC Code'] == occupation and r['Scale ID'] == 'IM']
        save('human-collection', 'v' + version + '/machinist_tasks.json', tasks)
        save('human-collection', 'v' + version + '/machinist_importance.json', ratings)
        snapshots[version] = ({r['Task ID']: r for r in tasks}, {r['Task ID']: r for r in ratings})
    before, after = snapshots['20_0'], snapshots['30_0']
    shared = before[0].keys() & after[0].keys()
    comparison = []
    for task_id in sorted(shared, key=int):
        a, b = before[0][task_id], after[0][task_id]
        ar, br = before[1][task_id], after[1][task_id]
        comparison.append({'task_id': task_id, 'task': b['Task'], 'task_before': a['Task'], 'same_text': a['Task'] == b['Task'],
                           'type_before': a['Task Type'], 'type_after': b['Task Type'],
                           'date_before': ar['Date'], 'date_after': br['Date'],
                           'importance_before': float(ar['Data Value']), 'importance_after': float(br['Data Value']),
                           'difference': float(br['Data Value']) - float(ar['Data Value']),
                           'N_before': ar['N'], 'N_after': br['N'],
                           'SE_before': ar['Standard Error'], 'SE_after': br['Standard Error']})
    human = save('human-collection', 'comparison.json', {
        'occupation': occupation, 'release_before': '20.0 (August 2015)', 'release_after': '30.0 (August 2025)',
        'actual_measurement_dates_before': sorted({r['Date'] for r in before[0].values()}),
        'actual_measurement_dates_after': sorted({r['Date'] for r in after[0].values()}),
        'tasks_before': len(before[0]), 'tasks_after': len(after[0]), 'shared_ids': len(shared),
        'same_text_shared': sum(r['same_text'] for r in comparison),
        'paired_task_definitions': comparison,
        'inference': 'Descriptive repeated occupation surveys, not worker panel; no automation causal effect identified.'})
    assert len(comparison) == 29 and sum(r['same_text'] for r in comparison) == 26

    flip = [[0, 1], [1, 0]]
    powers = []
    power = [[1, 0], [0, 1]]
    for n in range(7):
        powers.append({'n': n, 'P_power': power})
        power = matmul(power, flip)
    save('theory-known-principle', 'input.json', {'P': flip, 'definition': 'finite row-stochastic; entries nonnegative, each row sums to one'})
    save('theory-known-principle', 'powers.json', powers)
    assert powers[2]['P_power'] == [[1, 0], [0, 1]] and powers[3]['P_power'] == flip

    n = 6
    edges = {tuple(sorted((i, (i + 1) % n))) for i in range(n)}
    overlaps = Counter()
    for perm in itertools.permutations(range(n)):
        new = {tuple(sorted((perm[i], perm[j]))) for i, j in edges}
        assert all(sum(i in e for e in new) == 2 for i in range(n))
        overlaps[len(edges & new)] += 1
    trials = sum(overlaps.values())
    mean_overlap = sum(k * v for k, v in overlaps.items()) / trials
    save('equal-predictions', 'input.json', {
        'nodes': list(range(n)), 'initial_edges': sorted(edges),
        'A': 'Keep labeled edges unchanged at each time step.',
        'B': 'At each time step draw an independent uniform permutation of node labels of the six-cycle.',
        'digital_operation': 'Observe a second labeled snapshot; measure surviving edges / initial edges.',
        'evaluation': 'Exact enumeration of all 6! permutations, no Monte Carlo error.'})
    network = save('equal-predictions', 'result.json', {
        'static_degree_distribution_both': {'2': 6}, 'A_edge_survival': 1.0,
        'B_expected_surviving_edges': mean_overlap, 'B_expected_survival': mean_overlap / len(edges),
        'B_overlap_histogram': dict(sorted(overlaps.items())), 'permutations': trials,
        'probability_B_second_snapshot_equals_initial': overlaps[6] / trials})
    assert trials == 720 and abs(mean_overlap / 6 - 2 / 5) < 1e-12

    baseline = [1.0] * 10
    candidate_uniform = [1.12] * 10
    candidate_heterogeneous = [.2] * 2 + [1.35] * 8
    failure = save('initial-failure', 'aggregate_check.json', {
        'input_kind': 'Synthetic development record supplied in cases.json; allocations below are constructed examples, not actual algorithm errors.',
        'reported_candidate_error': 1.12, 'reported_baseline_error': 1.00,
        'reported_resource_ratio': 2.0, 'relative_error_increase': 1.12 / 1.0 - 1,
        'baseline_errors': baseline, 'compatible_allocation_A': candidate_uniform,
        'compatible_allocation_B': candidate_heterogeneous,
        'mean_A': sum(candidate_uniform) / 10, 'mean_B': sum(candidate_heterogeneous) / 10,
        'candidate_wins_A': 0, 'candidate_wins_B': 2,
        'next_action': 'Obtain and audit paired per-unit development predictions, losses, strata, seeds, and resource logs before opening the formal test set.'})
    assert abs(failure['mean_A'] - 1.12) < 1e-12 and abs(failure['mean_B'] - 1.12) < 1e-12

    assets = [{'name': p.name, 'is_file': p.is_file()} for p in sorted(OUT.parent.iterdir()) if p.name not in ['library', 'output']]
    handoff = save('author-pending', 'delivery_check.json', {
        'input_inventory': assets,
        'analysis_and_proof': 'User reports complete; underlying records absent, not independently verified.',
        'source_manuscript': 'not supplied', 'pdf': 'not supplied', 'figures': 'not supplied',
        'caption_audit': 'not executable without captions/figures',
        'abstract_value_audit': 'not executable without abstract/frozen results',
        'source_pdf_sync_audit': 'not executable without source/PDF',
        'author_identity_and_declarations': 'awaiting human confirmation',
        'delivery_state': 'internal handoff only; not submission-ready',
        'external_actions': []})
    print(json.dumps({'bike': bike, 'human': human, 'network': network, 'failure': failure, 'handoff': handoff}, ensure_ascii=False, indent=2))
    print('SELF-CHECK PASS')


if __name__ == '__main__':
    main()
