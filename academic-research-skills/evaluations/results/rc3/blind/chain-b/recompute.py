"""Independent raw-byte review. Run with the pre-existing acceptance Python."""
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
import io
from itertools import product
import json
from math import ceil, floor, isclose, sqrt
from pathlib import Path
from zipfile import ZipFile

PACKET = Path('LOCAL_EVIDENCE_ROOT/blind-packets/chain-b')
OUT = Path(__file__).parent


def bootstrap(values):
    n = len(values)
    return Counter(sum(draw, F(0)) / n for draw in product(values, repeat=n))


def combine(a, b, weight):
    counts = Counter()
    for x, nx in a.items():
        for y, ny in b.items():
            counts[weight * x + (1-weight) * y] += nx * ny
    return counts


def order_value(counts, index):
    seen = 0
    for value, count in sorted(counts.items()):
        seen += count
        if index < seen:
            return value
    raise AssertionError('Quantile index out of range')


def interval(counts, definition):
    n = sum(counts.values())
    endpoints = []
    for q in [F(1, 40), F(39, 40)]:
        if definition == 'inverse_empirical_cdf':
            value = order_value(counts, ceil(q*n)-1)
        else:
            position = (n-1)*q
            lo, hi = floor(position), ceil(position)
            value = order_value(counts, lo) + (position-lo)*(order_value(counts, hi)-order_value(counts, lo))
        endpoints.append(float(value))
    return endpoints


def stats(counts):
    return {'ordered_resamples':sum(counts.values()),
            'inverse_empirical_cdf_95':interval(counts, 'inverse_empirical_cdf'),
            'linear_95':interval(counts, 'linear')}


def near(a, b):
    assert isclose(float(a), float(b), rel_tol=0, abs_tol=1e-12), (a, b)


report = {'computed_at_utc':datetime.now(timezone.utc).isoformat(), 'archive_identity':{}, 'member_sha256':{}}
candidates = json.loads((PACKET/'raw/candidates.json').read_text())
for candidate in candidates:
    p = PACKET/'raw'/candidate['path']
    digest = sha256(p.read_bytes()).hexdigest()
    assert digest == candidate['sha256']
    report['archive_identity'][candidate['id']] = {'sha256':digest, 'matches_catalogue':True}
assert report['archive_identity']['paired']['sha256'] == report['archive_identity']['mirror']['sha256']
assert report['archive_identity']['paired']['sha256'] != report['archive_identity']['proxy']['sha256']
with ZipFile(PACKET/'raw/archives/paired-measurements-v1.zip') as z:
    data = {name:z.read(name) for name in z.namelist()}
    report['member_sha256'] = {name:sha256(blob).hexdigest() for name, blob in data.items()}
raw = list(csv.DictReader(io.StringIO(data['measurements.csv'].decode())))
metadata = list(csv.DictReader(io.StringIO(data['units.csv'].decode())))
unique, copied = {}, []
for line, row in enumerate(raw, 2):
    assert all(row.values()), (line, row)
    event = row['event_id']
    if event in unique:
        assert unique[event] == row, ('conflicting_event', event)
        copied.append({'event_id':event, 'duplicate_csv_line':line})
    else:
        unique[event] = row
means = defaultdict(list)
strata, joins = {}, []
for event, row in unique.items():
    matches = [m for m in metadata if m['unit_id'] == row['unit_id'] and m['valid_from'] <= row['observed_at'] <= m['valid_to']]
    assert len(matches) == 1, (event, matches)
    m = matches[0]
    unit = row['unit_id']
    assert unit not in strata or strata[unit] == m['stratum']
    strata[unit] = m['stratum']
    assert row['method'] in {'A','B'}
    factor = {'score':F(1), 'subscore':F(1,1000)}[row['measurement_unit']]
    means[(unit,row['method'])].append(F(row['raw_value'])*factor)
    joins.append({'event_id':event,'unit_id':unit,'observed_at':row['observed_at'],'metadata_record':m['record'],'active_match_count':len(matches)})
pairs = []
for unit in sorted(strata):
    a, b = means[(unit,'A')], means[(unit,'B')]
    assert a and b
    am, bm = sum(a,F(0))/len(a), sum(b,F(0))/len(b)
    pairs.append({'unit_id':unit,'stratum':strata[unit],'A_score':float(am),'B_score':float(bm),
                  'n_A_technical':len(a),'n_B_technical':len(b),'difference_A_minus_B':float(am-bm)})
groups = {h:[F(str(p['difference_A_minus_B'])) for p in pairs if p['stratum']==h] for h in ['g1','g2']}
assert [len(groups[h]) for h in ['g1','g2']] == [4,4]
report['preparation'] = {'raw_measurement_rows':len(raw),'metadata_history_rows':len(metadata),'copies_removed':copied,
                         'unique_events':len(unique),'methods':dict(Counter(r['method'] for r in unique.values())),
                         'measurement_units':dict(Counter(r['measurement_unit'] for r in unique.values())),
                         'independent_pairs':len(pairs),'all_metadata_matches_unique':True,'joins':joins}
report['pairs'] = pairs
distributions = {h:bootstrap(groups[h]) for h in groups}
report['strata'] = {}
for h, values in groups.items():
    selected = [p for p in pairs if p['stratum']==h]
    avg = sum(values)/len(values)
    variance = sum((x-avg)**2 for x in values)/(len(values)-1)
    report['strata'][h] = {'A_mean':sum(p['A_score'] for p in selected)/len(selected),
                           'B_mean':sum(p['B_score'] for p in selected)/len(selected),
                           'mean_difference':float(avg),'sample_variance':float(variance),**stats(distributions[h])}
report['aggregates'] = {}
for name, weight in [('target',F(4,5)),('sample',F(1,2))]:
    c = combine(distributions['g1'],distributions['g2'],weight)
    report['aggregates'][name] = {'g1_weight':float(weight),
                                 'mean_difference':float(weight*sum(groups['g1'])/4+(1-weight)*sum(groups['g2'])/4),**stats(c)}
report['leave_one_unit_out'] = []
for pair in pairs:
    kept = {h:[F(str(p['difference_A_minus_B'])) for p in pairs if p['stratum']==h and p['unit_id']!=pair['unit_id']] for h in groups}
    point = F(4,5)*sum(kept['g1'])/len(kept['g1']) + F(1,5)*sum(kept['g2'])/len(kept['g2'])
    c = combine(bootstrap(kept['g1']),bootstrap(kept['g2']),F(4,5))
    report['leave_one_unit_out'].append({'omitted_unit':pair['unit_id'],'mean_difference':float(point),**stats(c)})
report['weight_sensitivity'] = {'formula':'3 - 4*w_g1','zero_crossing':0.75,'at_0_7':0.2,'at_0_8':-0.2,'at_0_9':-0.6}
terms = [F(4,5)**2*F(1,6)/4,F(1,5)**2*F(14,3)/4]
variance = sum(terms)
df = variance**2/sum(v*v/3 for v in terms)
try:
    from scipy.stats import t
    half = float(t.ppf(.975,float(df)))*sqrt(float(variance))
    report['welch_satterthwaite'] = {'standard_error':sqrt(float(variance)),'degrees_freedom':float(df),'ci95':[-.2-half,-.2+half]}
except ImportError:
    report['welch_satterthwaite'] = {'standard_error':sqrt(float(variance)),'degrees_freedom':float(df),'ci95':None,'reason':'scipy unavailable; not installed'}
checks = []
for s in ['S1','S2','S3']:
    result = json.loads((PACKET/s/'results.json').read_text())
    if s == 'S1':
        given = [('g1',result['strata']['g1']['difference_A_minus_B'],result['strata']['g1']['bootstrap_percentile_95']),
                 ('g2',result['strata']['g2']['difference_A_minus_B'],result['strata']['g2']['bootstrap_percentile_95']),
                 ('target',result['aggregates']['target']['difference_A_minus_B'],result['aggregates']['target']['bootstrap_percentile_95']),
                 ('sample',result['aggregates']['sample_mix']['difference_A_minus_B'],result['aggregates']['sample_mix']['bootstrap_percentile_95'])]
    elif s == 'S2':
        given = [(h,result['strata'][h]['mean_difference_A_minus_B'],result['strata'][h]['bootstrap_percentile_interval_95']) for h in groups]
        given += [(n,result[k]['difference_A_minus_B'],result[k]['bootstrap_percentile_interval_95']) for n,k in [('target','primary_target'),('sample','sample_composition_comparator')]]
    else:
        given = [(x['stratum'],x['mean_difference'],x['ci95_percentile']) for x in result['strata']]
        given += [(x['composition'],x['difference'],x['ci95_percentile']) for x in result['aggregates']]
    for name, point, bounds in given:
        computed = (report['strata'] if name in groups else report['aggregates'])[name]
        near(point,computed['mean_difference'])
        for a,b in zip(bounds,computed['linear_95']): near(a,b)
        for a,b in zip(bounds,computed['inverse_empirical_cdf_95']): near(a,b)
    support = list(csv.DictReader(io.StringIO((PACKET/s/'support-table.csv').read_text())))
    if s in {'S1','S3'}:
        for row, independent in zip(support,pairs):
            assert row['unit_id']==independent['unit_id'] and row['stratum']==independent['stratum']
            for field in ['n_A_technical','n_B_technical','difference_A_minus_B']:
                near(row[field],independent[field])
            for method in ['A','B']:
                near(row[method+'_score' if s=='S1' else method],independent[method+'_score'])
    else:
        for row, name in zip(support,['g1','g2','target','sample']):
            computed = (report['strata'] if name in groups else report['aggregates'])[name]
            near(row['difference_A_minus_B'],computed['mean_difference'])
            for a,b in zip([row['interval_lo'],row['interval_hi']],computed['inverse_empirical_cdf_95']): near(a,b)
    if s=='S1' and report['welch_satterthwaite']['ci95'] is not None:
        alternative = result['robustness']['alternative_welch_satterthwaite_approximation']
        near(alternative['standard_error'],report['welch_satterthwaite']['standard_error'])
        near(alternative['degrees_freedom'],report['welch_satterthwaite']['degrees_freedom'])
        for a,b in zip(alternative['approximate_95_interval'],report['welch_satterthwaite']['ci95']): near(a,b)
    rows = list(csv.DictReader(io.StringIO((PACKET/s/'leave-one-unit-out.csv').read_text())))
    key = {'S1':'target_difference_A_minus_B','S2':'fixed_target_difference','S3':'target_difference'}[s]
    for row, independent in zip(rows,report['leave_one_unit_out']):
        assert row['omitted_unit']==independent['omitted_unit']
        near(row[key],independent['mean_difference'])
        if s=='S2':
            near(row['interval_lo'],independent['inverse_empirical_cdf_95'][0])
            near(row['interval_hi'],independent['inverse_empirical_cdf_95'][1])
    sensitivity = list(csv.DictReader(io.StringIO((PACKET/s/'weight-sensitivity.csv').read_text())))
    wk,dk = {'S1':('g1_weight','difference_A_minus_B'),'S2':('weight_g1','difference_A_minus_B'),'S3':('stratum_1_weight','difference')}[s]
    for row in sensitivity: near(row[dk],3-4*float(row[wk]))
    checks.append({'artifact':s,'point_estimates':'match','main_intervals_both_quantile_conventions':'match',
                   'support_table':'match','LOO_points':'match','LOO_intervals':('match' if s=='S2' else 'not supplied'),
                   'weight_sensitivity':'match','alternative_interval':('match' if s=='S1' else 'not supplied')})
assert report['preparation']['unique_events']==41
assert report['aggregates']['target']['inverse_empirical_cdf_95']==[-.65,.25]
assert all(x['mean_difference']<0 for x in report['leave_one_unit_out'])
assert report['leave_one_unit_out'][-1]['inverse_empirical_cdf_95'][1]<0
report['anonymous_artifact_checks'] = checks
report['input_sha256'] = {str(p.relative_to(PACKET)):sha256(p.read_bytes()).hexdigest() for p in PACKET.rglob('*') if p.is_file()}
(OUT/'recomputation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
with (OUT/'independent-pairs.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(pairs[0]))
    writer.writeheader()
    writer.writerows(pairs)
print(json.dumps({k:v for k,v in report.items() if k in ['aggregates','leave_one_unit_out','welch_satterthwaite','anonymous_artifact_checks']},ensure_ascii=False,indent=2))
