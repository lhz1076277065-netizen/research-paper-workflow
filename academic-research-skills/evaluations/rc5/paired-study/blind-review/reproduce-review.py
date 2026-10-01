"""Read-only replay of anonymous frozen submissions; writes one review result file."""
import hashlib
import importlib.util
import json
import statistics
import sys
from pathlib import Path
import numpy as np

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent


def read(path):
    return json.loads((ROOT / path).read_text())


def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def metrics(result):
    return {key: result[key] for key in ('mean_loss', 'false_alarms', 'hits', 'groups')}


def paired(left, right):
    left = {row['id']: row for row in left['rows']}
    right = {row['id']: row for row in right['rows']}
    assert left.keys() == right.keys()
    difference = [left[key]['loss'] - right[key]['loss'] for key in left]
    return {
        'mean_loss_reduction': statistics.mean(difference),
        'improved_cases': sum(value > 0 for value in difference),
        'worsened_cases': sum(value < 0 for value in difference),
        'tied_cases': sum(value == 0 for value in difference),
        'n': len(difference),
    }, difference


def bootstrap(difference, seed, repetitions):
    values = np.asarray(difference, dtype=float)
    means = np.random.default_rng(seed).choice(values, size=(repetitions, len(values)), replace=True).mean(axis=1)
    return np.quantile(means, [.025, .975]).tolist()


def main():
    harness = module('review_harness', Path('harness.py'))
    data = {split: read(split + '.json') for split in ('holdout', 'dev')}
    hashes = {split: digest(split + '.json') for split in data}
    assert hashes['holdout'] == read('common-known-comparator.json')['holdout_sha256']
    ids = {split: [case['id'] for case in rows] for split, rows in data.items()}
    assert len(ids['holdout']) == len(set(ids['holdout'])) == 480
    assert len(ids['dev']) == len(set(ids['dev'])) == 120
    assert not set(ids['holdout']) & set(ids['dev'])
    definition = read('bootstrap-definition.json')
    seed, repetitions = definition['seed'], definition['replicates']
    functions = module('review_evaluation_functions', Path('evaluation-functions.py'))
    comparator = read('common-known-comparator.json')
    median = harness.evaluate(functions.median_window, comparator['common_median_params'], data['holdout'])
    saved_median = read('common-median-rows.json')
    assert median['rows'] == saved_median['rows']
    assert metrics(median) == metrics(saved_median)
    assert median['mean_loss'] == comparator['common_median_mean_loss']
    output = {
        'input_sha256': hashes,
        'harness_sha256': digest('harness.py'),
        'holdout_cases': 480,
        'dev_cases': 120,
        'holdout_targets': sum(case['tau'] is not None for case in data['holdout']),
        'bootstrap_reproduction': {**definition, 'numpy_version': np.__version__, 'implementation': 'independent loss-difference computation and NumPy resampling; cross-checked extracted original paired()'},
        'common_median': metrics(median),
        'submissions': {},
    }
    for name in 'QRST':
        print('Replaying ' + name, flush=True)
        folder = Path(name)
        before = {path.name: digest(path) for path in (folder / 'methods.py', folder / 'frozen.json')}
        detector = module('review_' + name, folder / 'methods.py')
        frozen = read(folder / 'frozen.json')
        supplied = read(folder / 'holdout-summary.json')
        variants = [key for key in ('baseline', 'initial', 'refined', 'ablation', 'secondary_ablation', 'ablation_comparator') if key in frozen]
        evaluated = {}
        evaluated['median'] = median
        result = {'submission_sha256': before, 'holdout': {}, 'paired': {}, 'dev': {}}
        for variant in variants:
            function = harness.baseline if variant == 'baseline' else getattr(detector, 'detect_initial' if variant == 'initial' else frozen.get('ablation_function', 'detect_refined') if variant == 'ablation' else 'detect_refined')
            current = harness.evaluate(function, frozen[variant], data['holdout'])
            saved = read(folder / (variant + '.json'))
            assert current['rows'] == saved['rows'], (name, variant, 'holdout rows')
            assert metrics(current) == metrics(saved) == metrics(supplied[variant]), (name, variant, 'holdout metrics')
            assert [row['id'] for row in saved['rows']] == ids['holdout']
            evaluated[variant] = current
            result['holdout'][variant] = metrics(current)
        pairs = [('baseline_to_refined', 'baseline', 'refined'), ('initial_to_refined', 'initial', 'refined'), ('ablation_to_refined', 'ablation', 'refined'), ('median_to_refined', 'median', 'refined')]
        if 'ablation_comparator' in frozen:
            pairs.append(('matched_ablation_to_refined_variant', 'ablation', 'ablation_comparator'))
        for label, left, right in pairs:
            summary, difference = paired(evaluated[left], evaluated[right])
            for key, value in summary.items():
                assert value == supplied[label][key], (name, label, key)
            interval = bootstrap(difference, seed, repetitions)
            reported = supplied[label]['bootstrap_95_percentile']
            assert interval == reported, (name, label, 'bootstrap endpoints')
            assert functions.paired(evaluated[left], evaluated[right]) == supplied[label], (name, label, 'original extracted paired definition')
            summary.update(reported_bootstrap_95_percentile=reported,
                           reproduced_bootstrap_95_percentile=interval,
                           reported_bootstrap_exact_match=True)
            result['paired'][label] = summary
        events = [json.loads(line) for line in (ROOT / folder / 'score-events.jsonl').read_text().splitlines()]
        dev_events = [event for event in events if event['data_sha256'] == hashes['dev']]
        other_events = [event for event in events if event['data_sha256'] != hashes['dev']]
        assert len(dev_events) == 40
        assert len({event['name'] for event in dev_events}) == 40
        assert not any(event['data_sha256'] == hashes['holdout'] for event in events)
        stages = {stage: [event for event in dev_events if stage in event['name']] for stage in ('baseline', 'initial')}
        stages['refined'] = [event for event in dev_events if 'baseline' not in event['name'] and 'initial' not in event['name']]
        assert {key: len(rows) for key, rows in stages.items()} == {'baseline': 16, 'initial': 12, 'refined': 12}
        for stage, stage_events in stages.items():
            function = harness.baseline if stage == 'baseline' else getattr(detector, 'detect_' + stage)
            for event in stage_events:
                replay = harness.evaluate(function, event['params'], data['dev'])
                assert metrics(replay) == metrics(event), (name, event['name'], 'dev replay')
        selections = frozen.get('selected_records', frozen.get('selection', frozen.get('selection_records', frozen.get('selected_reports'))))
        selected = {}
        for variant in variants:
            stage = variant if variant in ('baseline', 'initial') else 'refined'
            matches = [event for event in stages[stage] if event['params'] == frozen[variant]]
            if variant in selections:
                declared = selections[variant].removesuffix('.json')
                assert any(event['name'] == declared for event in matches), (name, variant, 'selected event')
            assert matches, (name, variant, 'frozen map absent from dev')
            selected[variant] = [{'name': event['name'], **metrics(event)} for event in matches]
        proposal_events = [event for event in stages['refined'] if event['params'].get('budget', event['params'].get('burst', event['params'].get('erase', 1))) != 0 and event['params'].get('coverage', .6) >= .6 and event['params'].get('two_blocks', True)]
        for stage, eligible in [('baseline', stages['baseline']), ('initial', stages['initial']), ('refined', proposal_events)]:
            assert min(event['mean_loss'] for event in eligible) == selected[stage][0]['mean_loss'], (name, stage, 'loss minimum')
            if name == 'Q':
                winner = min(eligible, key=lambda event: event['mean_loss'])
            elif name == 'R':
                winner = min(eligible, key=lambda event: (event['mean_loss'], event['false_alarms'], -event['hits'], event['name']))
            elif name == 'S':
                winner = min(eligible, key=lambda event: (event['mean_loss'], event['false_alarms'], -event['hits']))
            else:
                winner = min(eligible, key=lambda event: (event['mean_loss'], event['false_alarms']))
            assert winner['params'] == frozen[stage], (name, stage, 'declared selection rule')
        result['dev'] = {
            'event_count': len(dev_events),
            'stage_counts': {stage: len(rows) for stage, rows in stages.items()},
            'refined_proposal_count_excluding_component_ablations': len(proposal_events),
            'all_40_events_replayed': True,
            'selected_maps_present_and_minimum_stage_loss': True,
            'declared_stage_selection_rules_reproduced': True,
            'selected': selected,
            'other_events_not_replayed': [{'name': event['name'], 'data_sha256': event['data_sha256']} for event in other_events],
        }
        assert before == {path.name: digest(path) for path in (folder / 'methods.py', folder / 'frozen.json')}
        output['submissions'][name] = result
    (ROOT / 'reproduction-results.json').write_text(json.dumps(output, indent=2) + '\n')
    print('All holdout rows, summaries, paired counts, and 160 dev events matched.', flush=True)


if __name__ == '__main__':
    main()
