"""Local fixture checks; run with the shared Python. No external actions."""
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from decimal import Decimal as D
from pathlib import Path

OUT = Path(__file__).resolve().parent
REQUEST = OUT.parent.parent / 'targeted-regression' / 'request.json'
request = json.loads(REQUEST.read_text())
for entry in request['material_files']:
    assert hashlib.sha256(Path(entry['path']).read_bytes()).hexdigest() == entry['sha256'], entry['path']
root = Path(request['material_root'])
rows = list(csv.DictReader((root / 'figure-results.csv').open()))
assert len(rows) == 6
for row in rows:
    d = D(row['difference_A_minus_B'])
    assert D(row['loss_A']) - D(row['loss_B']) == d
    assert D(row['diff_low']) <= d <= D(row['diff_high'])
for condition in ('C1', 'C2'):
    subset = [r for r in rows if r['condition'] == condition]
    assert sum(D(r['target_weight']) for r in subset) == 1
    assert sum(int(r['n_clusters']) for r in subset) == 30

def weighted(subset, weights):
    return [sum(weights[r['group']] * D(r[key]) for r in subset)
            for key in ('loss_A', 'loss_B', 'difference_A_minus_B')]

c1 = [r for r in rows if r['condition'] == 'C1']
c2 = [r for r in rows if r['condition'] == 'C2']
w1 = {r['group']: D(r['target_weight']) for r in c1}
w2 = {r['group']: D(r['target_weight']) for r in c2}
values = [weighted(c1, w1), weighted(c2, w2), weighted(c2, w1)]
assert values == [[D('7.40'), D('6.72'), D('0.68')],
                  [D('6.74'), D('7.58'), D('-0.84')],
                  [D('7.34'), D('7.46'), D('-0.12')]]
fixed_change = values[2][2] - values[0][2]
total_change = values[1][2] - values[0][2]
assert fixed_change == D('-0.80') and total_change == D('-1.52')
assert round(100 * fixed_change / total_change) == 53
svg = ET.parse(root / 'prior-figure.svg')
texts = [''.join(e.itertext()).replace('−', '-')
         for e in svg.iter() if e.tag.endswith('}text')]
for row in rows:
    label = f"{D(row['difference_A_minus_B']):+.1f} [{D(row['diff_low']):+.1f}, {D(row['diff_high']):+.1f}]"
    assert label in texts, label

manuscript = (OUT / 'manuscript.md').read_text().replace('−', '-')
for heading in ('Abstract', 'Introduction', 'Materials and comparison',
                'Uncertainty and research status', 'Results: C1',
                'Results: C2 and fixed composition', 'Figure 1 caption',
                'Discussion', 'Limitations', 'Conclusion',
                'Evidence notes and availability'):
    assert f'## {heading}\n' in manuscript, heading
for stale in ('5.1', '-0.87', '-0.15', '7.61', '7.49'):
    assert stale not in manuscript, stale
for heading in ('Abstract', 'Results: C2 and fixed composition', 'Figure 1 caption', 'Conclusion'):
    section = manuscript.split(f'## {heading}\n', 1)[1].split('\n## ', 1)[0]
    assert '-0.84' in section and '-0.12' in section, heading
sentence = (OUT / 'sentence.md').read_text().strip()
assert re.findall(r'\d+\.\d+', sentence) == ['0.24', '0.10', '0.38']
assert 'illustrative' in sentence and 'association' in sentence
assert '95%' not in sentence and 'caus' not in sentence.lower()
for name in ('reading-answer.md', 'manuscript.md', 'factual-semantic-diff.md',
             'figure-review.md', 'sentence.md', 'operation.md'):
    assert (OUT / name).is_file(), name
result = {'status': 'pass', 'scope': 'fixture hashes, weighted arithmetic, SVG textual intervals, complete section coverage, stale-value checks and sentence numbers',
          'scientific_validity_or_human_approval': 'not_certified',
          'weighted_values': [[str(v) for v in item] for item in values]}
(OUT / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(result, ensure_ascii=False))
