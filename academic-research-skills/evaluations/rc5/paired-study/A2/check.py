"""Small runnable known-case and causal-prefix check; no validation scoring."""
import json
from pathlib import Path
from methods import detect_initial, detect_refined, trace_refined

HERE = Path(__file__).resolve().parent


def main():
    frozen = json.loads((HERE / 'frozen.json').read_text())
    initial, refined = frozen['initial'], frozen['refined']
    prefix = [0.] * 64
    cases = {'null': prefix + [0.] * 100,
             'positive_shift': prefix + [2.] * 100,
             'negative_shift': prefix + [-2.] * 100,
             'short_burst': prefix + [2.] * 12 + [0.] * 88,
             'all_missing': [None] * 164,
             'gap': prefix + [2.] * 8 + [None] * 13 + [2.] * 79}
    results = {}
    for name, x in cases.items():
        results[name] = {}
        for label, detector, params in [('initial', detect_initial, initial),
                                        ('refined', detect_refined, refined)]:
            alarm = detector(x, params)
            for length in range(len(x) + 1):
                expected = alarm if 0 <= alarm < length else -1
                assert detector(x[:length], params) == expected, (name, label, length)
            if alarm >= 0:
                # A wildly different future must not change a past alarm.
                assert detector(x[:alarm + 1] + [-1000., None, 1000.] * 20, params) == alarm
            results[name][label] = alarm
    assert results['null'] == {'initial': -1, 'refined': -1}
    assert results['all_missing'] == {'initial': -1, 'refined': -1}
    assert results['positive_shift']['refined'] == results['negative_shift']['refined'] == 82
    assert results['short_burst']['refined'] == -1
    assert results['gap']['refined'] == 103

    # Excursion age can grow while old burst energy remains above threshold.
    low_initial = {'clip': 2., 'k': .4, 'h': 12., 'min_age': 20}
    residual_alarm = detect_initial(cases['short_burst'], low_initial)
    assert residual_alarm == 83  # The burst ended at 75; eight null samples followed.
    _, events = trace_refined(cases['short_burst'], refined)
    assert any(e['event'] == 'reject' and e['right_mean'] == 0 for e in events)

    # Boundary: a sustained shift and a 24-observation nuisance burst share
    # exactly the same prefix until the nuisance ends. A causal alarm within
    # that prefix cannot distinguish their intended labels.
    sustained = prefix + [2.] * 100
    long_burst = prefix + [2.] * 24 + [0.] * 76
    assert sustained[:88] == long_burst[:88]
    boundary_alarm = detect_refined(long_burst, refined)
    assert boundary_alarm == detect_refined(sustained, refined) == 82
    try:
        detect_refined(prefix + [float('nan')], refined)
    except ValueError:
        pass
    else:
        raise AssertionError('nonfinite values were silently accepted')
    report = {'passed': True, 'causal_prefixes_checked': sum((len(x) + 1) * 2 for x in cases.values()),
              'known_cases': results, 'residual_energy_counterexample_alarm': residual_alarm,
              'short_burst_trace': events, 'shared_prefix_length': 88,
              'indistinguishable_long_burst_alarm': boundary_alarm,
              'scope': 'Synthetic cases and all their prefixes; does not establish statistical calibration.'}
    (HERE / 'checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
