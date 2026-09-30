"""Offline reporting/package checks; not experiment replication or acceptance."""
import hashlib
import json
import re
from datetime import datetime, timezone
from difflib import unified_diff
from pathlib import Path
from xml.etree import ElementTree as ET


def main():
    root = Path(__file__).resolve().parent
    def read(name):
        return (root / name).read_text()
    def section(text, start, end):
        return text.split(start, 1)[1].split(end, 1)[0].strip()
    original = read('baseline/draft-v2.md')
    manuscript = read('submission/anonymous/manuscript-v3.md')
    for item in json.loads(read('baseline-manifest.json'))['items']:
        assert hashlib.sha256((root / item['file']).read_bytes()).hexdigest() == item['sha256'], item['file']
        assert hashlib.sha256(Path(item['source']).read_bytes()).hexdigest() == item['sha256'], item['source']
    old_intro = section(original, '## Introduction', '## Methods')
    new_intro = section(manuscript, '## 1. Introduction', '## 2. Methods')
    old_words, new_words = len(old_intro.split()), len(new_intro.split())
    assert new_words < old_words, (old_words, new_words)
    main_words = len(section(manuscript, '## 1. Introduction', '## Data and code access').split())
    total_words = len(manuscript.split())
    assert main_words <= 2500 and total_words <= 2500
    assert manuscript.splitlines()[0] == '# Mixture-dependent direction in a paired method comparison'
    assert 'g2 also\nsupports A' not in manuscript
    assert '10.1214/aos/1176344552' not in manuscript
    assert set(re.findall(r'\[(\d+)\]', manuscript)) == {'1'}
    assert manuscript.count('10.1093/biomet/70.1.41') == 1
    assert 'Author list, contributions and approval: UNKNOWN.' in manuscript
    for text in [manuscript, read('submission/anonymous/caption-v3.md'), read('submission/anonymous/supplement-v3.md')]:
        for value in ['−1.00', '+3.00', '−0.20', '+1.00', '−0.60', '0.20']:
            assert value in text, value
    locations = {'2.1': 17, '2.2': 21, '2.3': 25, 'g2': 29, 'weighted': 31, 'interval': 33, 'R/R': 39, 'R5': 11}
    expected = {'2.1': 'eight independent units', '2.2': '0.8:0.2', '2.3': 'resampled paired units', 'g2': "favoring B's lower score", 'weighted': '−1.20', 'interval': 'neither practical equivalence', 'R/R': 'abstract-level', 'R5': 'This note diagnoses'}
    for key, number in locations.items():
        assert expected[key] in manuscript.splitlines()[number-1], (key, number)
    response = read('review/response-draft.md')
    assert re.findall(r'^## R([1-5]) ', response, re.M) == ['1', '2', '3', '4', '5']
    assert 'fewer whitespace-delimited words' in response
    correction = read('correction/correction-note-draft.md')
    assert '−0.30' in correction and '−0.20' in correction
    assert 'fe70fc7ea3069c4507b59737a781ded7bda8d96f45eda8ed8de1e52d98ac6caf' in correction
    assert 'cause of the earlier numerical discrepancy has not been documented' in correction
    for name in ['submission/anonymous/manuscript-v3.md', 'submission/anonymous/caption-v3.md', 'submission/anonymous/supplement-v3.md', 'submission/anonymous/data-code-access.md', 'submission/anonymous/build_figure.py', 'submission/anonymous/figure1-v3.svg']:
        for identifier in ['Mira Example', 'Synthetic Unit Laboratory', '/Users/luca', 'contact and ORCID']:
            assert identifier not in read(name), (name, identifier)
    svg = ET.fromstring(read('submission/anonymous/figure1-v3.svg'))
    svg_text = ' '.join(''.join(node.itertext()) for node in svg.iter() if node.tag.endswith('}text'))
    for value in ['g2 (n = 4)', '+3.00', '-1.00', '-0.20', '+1.00', 'Target (0.8 / 0.2)', 'Sampled (0.5 / 0.5)']:
        assert value in svg_text, value
    assert not any(node.tag.endswith('}image') for node in svg.iter())
    qa = json.loads(read('receipts/figure-qa.json'))
    assert qa['exported'] and not qa['layout_issues'] and not qa['bootstrap_replicated']
    for source, target in [('baseline/draft-v2.md', 'review/draft-v2-to-v3.diff'), ('review/manuscript-v3-before-expression.md', 'review/expression-diff.diff')]:
        diff = ''.join(unified_diff(read(source).splitlines(keepends=True), manuscript.splitlines(keepends=True), fromfile=source, tofile='submission/anonymous/manuscript-v3.md'))
        assert diff
        (root / target).write_text(diff)
    result = {'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'PASS', 'old_intro_words': old_words, 'new_intro_words': new_words, 'main_text_words': main_words, 'whole_manuscript_words': total_words, 'word_count_rule': 'whitespace-delimited; main text sections 1-5 including headings; whole count includes draft banner and references', 'baseline_and_source_hashes': 'PASS', 'anonymous_text_and_svg': 'PASS', 'numeric_display_and_locations': 'PASS', 'R1_R5_response_coverage': 'PASS', 'actual_diffs_refreshed': True, 'computational_replication_performed': False, 'author_or_ethics_approval_inferred': False}
    (root / 'receipts/package-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
