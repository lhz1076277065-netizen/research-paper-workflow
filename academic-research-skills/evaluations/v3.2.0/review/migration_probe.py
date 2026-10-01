#!/usr/bin/env python3
"""Exercise the two v3.2 migration caveats against actual JSON/Markdown files."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True, exist_ok=False)
    script = ROOT / 'src/common/scripts/result_links.py'
    spec = importlib.util.spec_from_file_location('migration_review_links', script)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    for name in ('data.csv', 'analysis.py', 'execution.json'):
        (out / name).write_text('Synthetic engineering fixture: ' + name + '\n')
    record = {'value': '0.25', 'lower': '0.20', 'upper': '0.30', 'unit': 'ratio',
              'population': {'value': 'cohort-a', 'labels': ['Cohort A']}}
    save(out / 'results.json', {'R1': record})
    (out / 'draft.md').write_text('Cohort A mean was 25.00% (20.00%-30.00%).\nCohort A mean was 25.00%.\n')
    (out / 'caption.md').write_text('Cohort A mean was 25.00%.\n')
    sources = [{'id': 'frozen', 'path': 'results.json', 'versions': {
        kind: {'path': name} for kind, name in [('data', 'data.csv'), ('code', 'analysis.py'), ('execution', 'execution.json')]}}]
    body = {'path': 'draft.md', 'result_id': 'R1', 'role': 'body', 'locator': {'line': 1}, 'unit': 'percent',
            'numeric': [{'field': field, 'decimals': 2} for field in ('value', 'lower', 'upper')]}
    checks = {}
    for name, rows, wanted in [
        ('population_without_explicit_subject', [body], False),
        ('population_with_explicit_subject', [{**body, 'subject_field': 'population'}], True),
        ('coverage_within_same_artifact', [{**body, 'subject_field': 'population'}, {
            **body, 'subject_field': 'population', 'role': 'caption', 'locator': {'line': 2},
            'numeric': [{'field': 'value', 'decimals': 2}]}], True),
        ('coverage_across_separate_artifacts', [{**body, 'subject_field': 'population'}, {
            **body, 'subject_field': 'population', 'path': 'caption.md', 'role': 'caption',
            'numeric': [{'field': 'value', 'decimals': 2}]}], False),
    ]:
        payload = audit.build_links(out, sources, copy.deepcopy(rows))
        report = audit.audit_links(payload, out)
        save(out / (name + '.payload.json'), payload)
        save(out / (name + '.report.json'), report)
        assert report['passed'] is wanted, (name, report)
        if name == 'population_without_explicit_subject':
            assert not report['errors'] and any(p.get('reason') == 'primary_subject_unbound' for p in report['pending'])
        elif name == 'coverage_across_separate_artifacts':
            assert not report['errors'] and len(report['coverage_gaps']) == 1
            gap = report['coverage_gaps'][0]
            assert (gap['source_id'], gap['result_id'], gap['path']) == ('frozen', 'R1', 'caption.md')
            assert gap['fields'] == ['lower', 'upper'], gap
        checks[name] = {'expected_passed': wanted, 'actual_passed': report['passed'],
                        'errors': report['errors'], 'pending': report['pending']}
    # Execute the literal published fragment, rather than a similar handwritten example.
    document = ROOT / 'MIGRATION.zh-CN.md'
    fragment = json.loads(re.search(r'```json\n(.*?)\n```', document.read_text(), re.S).group(1))
    example = out / 'document-example'
    example.mkdir()
    for name in ('data.csv', 'analysis.py', 'execution.json'):
        (example / name).write_bytes((out / name).read_bytes())
    save(example / 'results.json', {'R1': {'value': '0.41', 'unit': 's', 'population': 'Cohort A'}})
    actual_text = re.search(r'实际句子为“([^”]+)”', document.read_text()).group(1)
    (example / 'draft.md').write_text(actual_text.rstrip('.') + '.\n')
    row = {'path': 'draft.md', 'result_id': 'R1', 'role': 'body', 'locator': {'line': 1},
           'numeric': [{'field': 'value', 'decimals': 2}], **fragment}
    payload = audit.build_links(example, sources, [row])
    report = audit.audit_links(payload, example)
    save(example / 'payload.json', payload)
    save(example / 'report.json', report)
    assert report['passed'], report
    checks['literal_published_population_fragment'] = {
        'expected_passed': True, 'actual_passed': report['passed'],
        'document_sha256': hashlib.sha256(document.read_bytes()).hexdigest(), 'fragment': fragment}
    (example / 'was.md').write_text('Cohort A mean was 0.41 s.\n')
    payload = audit.build_links(example, sources, [{**row, 'path': 'was.md'}])
    report = audit.audit_links(payload, example)
    save(example / 'was.payload.json', payload)
    save(example / 'was.report.json', report)
    assert not report['passed'] and not report['errors']
    assert any(p.get('reason') == 'primary_subject_connector_unresolved' for p in report['pending'])
    checks['documented_s_was_conservative_pending'] = {
        'expected_passed': False, 'actual_passed': report['passed'], 'errors': report['errors'], 'pending': report['pending']}
    save(out / 'summary.json', {'script_sha256': hashlib.sha256(script.read_bytes()).hexdigest(),
                               'checks': checks, 'passed': True,
                               'scope': 'Synthetic actual-file migration behavior; no scientific certification.'})
    print(json.dumps({'checks': len(checks), 'passed': True}))


if __name__ == '__main__':
    main()
