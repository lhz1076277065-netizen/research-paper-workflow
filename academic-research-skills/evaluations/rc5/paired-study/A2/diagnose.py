"""Diagnostics of saved validation outcomes; no new performance evaluations."""
from collections import Counter
import json
import statistics
from pathlib import Path
from methods import trace_refined

HERE = Path(__file__).resolve().parent


def initial_diagnostic(cases):
    report = json.loads((HERE / 'dev-initial-01.json').read_text())
    diagnostics = []
    for row in report['rows']:
        if not row['false_alarm']:
            continue
        case = cases[row['id']]
        alarm = row['alarm']
        calibration = case['x'][:64]
        mu = statistics.median(calibration)
        scale = max(.25, 1.4826 * statistics.median(abs(v - mu) for v in calibration))
        zs = [None if v is None else max(-2., min(2., (v - mu) / scale)) for v in case['x']]
        plus = minus = 0.
        ap = am = 0
        for z in zs[64:alarm + 1]:
            if z is None:
                continue
            plus = max(0., plus + z - .4)
            minus = max(0., minus - z - .4)
            ap = ap + 1 if plus > 0 else 0
            am = am + 1 if minus > 0 else 0
        direction = 1 if plus > minus else -1
        recent = [direction * z for z in zs[max(64, alarm - 7):alarm + 1] if z is not None]
        diagnostics.append({'id': case['id'], 'condition': case['condition'],
                            'alarm': alarm, 'tau': case['tau'], 'direction': direction,
                            'energy': max(plus, minus),
                            'excursion_observed_age': ap if direction == 1 else am,
                            'last_8_oriented_clipped_mean': statistics.mean(recent)})
    out = {'method': 'dev-initial-01',
           'question': 'Does excursion age guarantee recent evidence?',
           'false_alarm_rows': diagnostics,
           'false_alarms_with_last8_mean_below_0.4': sum(
               r['last_8_oriented_clipped_mean'] < .4 for r in diagnostics)}
    (HERE / 'diagnostic-initial.json').write_text(json.dumps(out, indent=2) + '\n')


def main():
    frozen = json.loads((HERE / 'frozen.json').read_text())
    cases = {r['id']: r for r in json.loads((HERE.parent / 'data/dev.json').read_text())}
    initial_diagnostic(cases)
    reports = {key: json.loads((HERE / path).read_text())
               for key, path in frozen['selected_reports'].items()}
    rows = {key: {r['id']: r for r in report['rows']} for key, report in reports.items()}
    totals = Counter()
    details = []
    for case_id, case in cases.items():
        alarm, events = trace_refined(case['x'], frozen['refined'])
        assert alarm == rows['refined'][case_id]['alarm']
        totals.update(e['event'] for e in events)
        a = rows['ablation'][case_id]
        r = rows['refined'][case_id]
        if a['hit'] and not r['hit']:
            details.append({'id': case_id, 'condition': case['condition'], 'tau': case['tau'],
                            'refined_row': r, 'pooled_row': a, 'refined_events': events})
    comparisons = []
    for case_id in cases:
        b, r = rows['baseline'][case_id], rows['refined'][case_id]
        if r['loss'] != b['loss']:
            comparisons.append({'id': case_id, 'condition': b['condition'],
                                'baseline_alarm': b['alarm'], 'refined_alarm': r['alarm'],
                                'baseline_loss': b['loss'], 'refined_loss': r['loss'],
                                'delta': r['loss'] - b['loss']})
    out = {'event_counts': dict(totals), 'pooled_hit_but_split_miss': details,
           'all_nonzero_paired_differences': comparisons,
           'scope': 'Replays and reconciles saved refined decisions; no configuration changes or scores.'}
    (HERE / 'diagnostic-refined.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({'event_counts': out['event_counts'],
                      'pooled_hit_but_split_miss': [
                          {k: v for k, v in r.items() if k != 'refined_events'} for r in details]}, indent=2))


if __name__ == '__main__':
    main()
