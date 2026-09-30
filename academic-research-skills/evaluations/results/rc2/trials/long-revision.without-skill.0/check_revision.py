"""Run with the common Python; checks only this trial and the fixed packed request."""
import csv
import io
import json
import re
from decimal import Decimal as D
from pathlib import Path

request = Path('LOCAL_EVIDENCE_ROOT/suite/requests/long-revision.without-skill.0.json')
out = Path(__file__).resolve().parent
packed = json.loads(request.read_text())['material']
rows = list(csv.DictReader(io.StringIO(packed.split('## fixtures/rc2/figure-results.csv\n', 1)[1].strip())))
text = (out / 'manuscript.md').read_text()
assert len(rows) == 6
table = [line for line in text.splitlines() if re.match(r'\| C[12] \| G[123] \|', line)]
assert len(table) == 6

for row, line in zip(rows, table):
    cells = [c.strip() for c in line.strip('|').split('|')]
    assert cells[:2] == [row['condition'], row['group']]
    assert int(cells[2]) == int(row['n_clusters'])
    assert D(cells[3]) == D(row['target_weight'])
    for cell, keys in zip(cells[4:], (
        ('loss_A', 'A_low', 'A_high'),
        ('loss_B', 'B_low', 'B_high'),
        ('difference_A_minus_B', 'diff_low', 'diff_high'),
    )):
        numbers = re.findall(r'-?\d+(?:\.\d+)?', cell.replace('−', '-'))
        assert [D(n) for n in numbers] == [D(row[k]) for k in keys]
    assert D(row['loss_A']) - D(row['loss_B']) == D(row['difference_A_minus_B'])

weighted = {}
for condition in ('C1', 'C2'):
    group_rows = [r for r in rows if r['condition'] == condition]
    assert sum(int(r['n_clusters']) for r in group_rows) == 30
    assert sum(D(r['target_weight']) for r in group_rows) == 1
    a = sum(D(r['target_weight']) * D(r['loss_A']) for r in group_rows)
    b = sum(D(r['target_weight']) * D(r['loss_B']) for r in group_rows)
    weighted[condition] = (a, b, a-b)
assert weighted == {'C1': (D('7.40'), D('6.72'), D('0.68')), 'C2': (D('6.74'), D('7.58'), D('-0.84'))}
weights = {r['group']: D(r['target_weight']) for r in rows if r['condition'] == 'C1'}
a = sum(weights[r['group']] * D(r['loss_A']) for r in rows if r['condition'] == 'C2')
b = sum(weights[r['group']] * D(r['loss_B']) for r in rows if r['condition'] == 'C2')
assert (a, b, a-b) == (D('7.34'), D('7.46'), D('-0.12'))

for stale in ('5.1', '−0.3', '7.61', '−0.87', '7.49', '−0.15'):
    assert not re.search(r'(?<![\d.])' + re.escape(stale) + r'(?![\d.])', text), stale
for current in ('7.40', '6.72', '+0.68', '6.74', '7.58', '−0.84', '7.34', '7.46', '−0.12'):
    assert current in text, current
for boundary in (
    'interval spans zero', 'nor equivalence', '95% percentile cluster-bootstrap',
    'no supplied aggregate confidence interval', 'no cross-condition interaction test',
    'not a causal intervention', 'tuning preceded', 'comparisons are exploratory',
    'not replaced by the observed cluster fractions', 'not published citations',
    'not a research publication or a submission-ready document',
):
    assert boundary in text, boundary
for deliverable in ('manuscript.md', 'factual-semantic-diff.md', 'operation.md'):
    assert (out / deliverable).stat().st_size > 0
print('PASS: all six table rows and intervals, cluster counts, target weights, three weighted comparisons, stale-value scan, and evidence boundaries.')
