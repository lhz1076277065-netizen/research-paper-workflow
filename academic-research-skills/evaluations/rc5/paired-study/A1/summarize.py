"""Build paired tables and diagnostics only from already-recorded validation rows."""
import csv
import json
import math
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    frozen = json.loads((HERE / 'frozen.json').read_text())
    reports = {k: json.loads((HERE / v).read_text()) for k, v in frozen['selected_records'].items()}
    indexed = {m: {r['id']: r for r in report['rows']} for m, report in reports.items()}
    base_rows = reports['baseline']['rows']
    paired = []
    for b in base_rows:
        row = {k: b[k] for k in ['id', 'condition', 'tau']}
        for m in reports:
            for k in ['alarm', 'false_alarm', 'hit', 'delay', 'loss']:
                row[f'{m}_{k}'] = indexed[m][b['id']][k]
        for m in ['baseline', 'initial', 'ablation']:
            row[f'refined_minus_{m}_loss'] = row['refined_loss'] - row[f'{m}_loss']
        paired.append(row)
    with (HERE / 'paired-cases.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)
    summary = {}
    for m, report in reports.items():
        hits = [r['delay'] for r in report['rows'] if r['hit']]
        summary[m] = {'mean_loss': report['mean_loss'], 'false_alarms': report['false_alarms'],
                      'timely_hits': report['hits'], 'critical_cases': sum(r['tau'] is not None for r in report['rows']),
                      'mean_delay_among_hits': statistics.mean(hits), 'runtime_seconds': report['runtime_seconds'],
                      'groups': report['groups']}
    differences = {}
    for m in ['baseline', 'initial', 'ablation']:
        ds = [r[f'refined_minus_{m}_loss'] for r in paired]
        common = [r['refined_delay'] - r[f'{m}_delay'] for r in paired if r['refined_hit'] and r[f'{m}_hit']]
        differences[m] = {'mean_paired_loss_difference': statistics.mean(ds),
                          'paired_standard_error': statistics.stdev(ds) / math.sqrt(len(ds)),
                          'better': sum(d < 0 for d in ds), 'tie': sum(d == 0 for d in ds), 'worse': sum(d > 0 for d in ds),
                          'common_timely_hit_n': len(common), 'mean_delay_difference_on_common_hits': statistics.mean(common)}
    data = json.loads((HERE.parent / 'data/dev.json').read_text())
    magnitude = {'initial_timely': [], 'initial_untimely': []}
    raw_rows = []
    for c in data:
        if c['tau'] is None:
            continue
        prefix = [v for v in c['x'][:64] if v is not None]
        mu = statistics.median(prefix)
        scale = max(.25, 1.4826 * statistics.median(abs(v - mu) for v in prefix))
        vals = [max(-3., min(3., (v - mu) / scale)) for v in c['x'][c['tau']:c['tau'] + 60] if v is not None]
        mag = abs(statistics.mean(vals))
        hit = indexed['initial'][c['id']]['hit']
        magnitude['initial_timely' if hit else 'initial_untimely'].append(mag)
        raw_rows.append({'id': c['id'], 'absolute_postshift_clipped_mean': mag, 'initial_hit': hit,
                         'refined_hit': indexed['refined'][c['id']]['hit']})
    diagnostic = {'postshift_descriptive_magnitude': {k: {'n': len(v), 'mean': statistics.mean(v), 'median': statistics.median(v)} for k, v in magnitude.items()},
                  'initial_untimely_refined_timely_ids': [r['id'] for r in paired if r['tau'] is not None and not r['initial_hit'] and r['refined_hit']],
                  'initial_timely_refined_untimely_ids': [r['id'] for r in paired if r['initial_hit'] and not r['refined_hit']],
                  'scope': 'Post-label descriptive magnitude; never used as detector input. No new validation calls.', 'rows': raw_rows}
    (HERE / 'diagnostics.json').write_text(json.dumps(diagnostic, indent=2) + '\n')
    result = {'summary': summary, 'paired_differences': differences,
              'uncertainty_scope': 'Paired standard errors describe this tuned dev sample only; no selection adjustment or independent confidence interval.'}
    (HERE / 'comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    overall = ['| Method | Mean loss | False alarms / 120 | Hits / 60 | Mean delay among hits | Runtime, s |', '|---|---:|---:|---:|---:|---:|']
    for m, s in summary.items():
        overall.append(f"| {m} | {s['mean_loss']:.3f} | {s['false_alarms']} | {s['timely_hits']} | {s['mean_delay_among_hits']:.2f} | {s['runtime_seconds']:.4f} |")
    groups = ['| Condition, n=30 | Baseline loss | Initial loss | Refined loss | Ablation loss |', '|---|---:|---:|---:|---:|']
    for g in reports['baseline']['groups']:
        groups.append('| ' + g + ' | ' + ' | '.join(f"{summary[m]['groups'][g]['mean_loss']:.3f}" for m in reports) + ' |')
    pairs = ['| Refined minus comparator | Mean paired loss delta | Descriptive SE | Better / tie / worse | Common-hit delay delta |', '|---|---:|---:|---:|---:|']
    for m, s in differences.items():
        pairs.append(f"| {m} | {s['mean_paired_loss_difference']:.3f} | {s['paired_standard_error']:.3f} | {s['better']} / {s['tie']} / {s['worse']} | {s['mean_delay_difference_on_common_hits']:.2f}, n={s['common_timely_hit_n']} |")
    (HERE / 'tables.md').write_text('\n'.join(overall) + '\n\n' + '\n'.join(groups) + '\n\n' + '\n'.join(pairs) + '\n')
    print((HERE / 'tables.md').read_text())
    print(json.dumps({k: v for k, v in diagnostic.items() if k != 'rows'}, indent=2))


if __name__ == '__main__':
    main()
