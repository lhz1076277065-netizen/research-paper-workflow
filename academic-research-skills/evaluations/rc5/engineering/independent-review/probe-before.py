#!/usr/bin/env python3
"""Independent actual-file rc.5 probes; synthetic latency is not research evidence."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
TEXT = ('Solver A latency was 410.0 ms (95% CI 390.0 ms-430.0 ms), lower than Solver baseline '
        'on digital instances (n=4), holdout at one run; absolute mean; loop.')


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scripts', type=Path, default=REPO / 'src/common/scripts')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    audit = load('independent_result_links', args.scripts / 'result_links.py')
    bridge = load('independent_provider_runtime', args.scripts / 'provider_runtime.py')
    research = load('independent_research31', args.scripts / 'research31.py')
    names = [
        ('baseline', True),
        ('comparative_threshold', False),
        ('unrelated_unit_locator', False),
        ('mixed_markdown_table_locator', False),
        ('exact_tolerance_precision_loss', False),
        ('correct_unit_conversion', True),
        ('equal_bare_number_wrong_unit_scale', False),
        ('different_scientific_split', False),
        ('display_label_is_not_equivalence', False),
        ('frozen_model_implementation_equivalence', True),
        ('independent_locator_direct_negation', False),
        ('unknown_subject_connector', False),
        ('reversed_interval', False),
        ('explicit_upper_lower_labels', True),
        ('subject_in_background_sentence', False),
        ('caption_and_body_coverage', True),
        ('caption_only_coverage_gap', False),
    ]
    results = []
    for name, desired in names:
        root = args.out / name
        root.mkdir()
        (root / 'measurements.json').write_text('["0.40", "0.42", "0.41", "0.41"]\n')
        (root / 'compute.py').write_text('import json,sys\nfrom decimal import Decimal\nfrom pathlib import Path\nx=json.loads(Path(sys.argv[1]).read_text())\nprint(json.dumps({"value":str(sum(map(Decimal,x))/len(x))}))\n')
        execution = subprocess.run([sys.executable, str(root / 'compute.py'), str(root / 'measurements.json')],
                                   text=True, capture_output=True, check=True)
        (root / 'execution.json').write_text(execution.stdout)
        record = {'value': json.loads(execution.stdout)['value'], 'unit': 's', 'lower': '0.39', 'upper': '0.43',
                  'model': {'value': 'solver-a', 'labels': ['Solver A'], 'equivalent_values': ['solver-a-fast']},
                  'implementation': {'value': 'loop', 'labels': ['loop'], 'equivalent_values': ['vectorized']},
                  'outcome': 'latency', 'direction': 'decrease', 'population': 'digital instances', 'denominator': 4,
                  'comparison': 'Solver baseline', 'split': 'holdout', 'time': 'one run',
                  'effect_type': 'absolute mean', 'uncertainty': '95% CI'}
        text = TEXT
        rows = [{'path': 'draft.md', 'result_id': 'R-latency', 'role': 'body', 'locator': {'line': 1}, 'unit': 'ms',
                 'numeric': [{'field': field, 'decimals': 1} for field in ('value', 'lower', 'upper')]}]
        if name == 'comparative_threshold':
            text = text.replace('latency was 410.0', 'latency was lower than 410.0')
        elif name == 'unrelated_unit_locator':
            text = text.replace('was 410.0 ms', 'was 410.0 g') + '\nDocumentation unit: ms.'
            rows[0]['semantics'] = {'unit': {'value': 'ms', 'text': 'ms', 'locator': {'line': 2}}}
        elif name == 'mixed_markdown_table_locator':
            text = text.replace('Solver A latency was', 'An unknown method latency was') + '\nSolver A is background.'
            rows[0]['locator'].update(table=1, row=2, cell=2)
            rows[0]['semantics'] = {'model': {'value': 'solver-a', 'text': 'Solver A',
                                             'locator': {'line': 2, 'table': 1, 'row': 2, 'cell': 1}}}
        elif name == 'independent_locator_direct_negation':
            text += '\nThis is not lower.'
            rows[0]['semantics'] = {'direction': {'value': 'decrease', 'text': 'lower', 'locator': {'line': 2}}}
        elif name == 'unknown_subject_connector':
            text = text.replace('latency was', 'latency was reported incorrectly as')
        elif name == 'reversed_interval':
            text = text.replace('390.0 ms-430.0 ms', '430.0 ms-390.0 ms')
        elif name == 'explicit_upper_lower_labels':
            text = text.replace('390.0 ms-430.0 ms', 'upper: 430.0 ms, lower: 390.0 ms')
        elif name == 'subject_in_background_sentence':
            text = text.replace('Solver A latency was', 'Solver A is background. An unknown method latency was')
        elif name in {'caption_and_body_coverage', 'caption_only_coverage_gap'}:
            text += '\nSolver A latency was 410.0 ms.'
            caption = {'path': 'draft.md', 'result_id': 'R-latency', 'role': 'caption', 'locator': {'line': 2},
                       'unit': 'ms', 'numeric': [{'field': 'value', 'decimals': 1}]}
            rows = rows + [caption] if name == 'caption_and_body_coverage' else [caption]
        save(root / 'results.json', {'R-latency': record})
        (root / 'draft.md').write_text(text + '\n')
        sources = [{'id': 'frozen', 'path': 'results.json', 'versions': {
            key: {'path': path} for key, path in [('data', 'measurements.json'), ('code', 'compute.py'), ('execution', 'execution.json')]}}]
        payload = audit.build_links(root, sources, rows)
        if name in {'exact_tolerance_precision_loss', 'correct_unit_conversion', 'equal_bare_number_wrong_unit_scale',
                    'different_scientific_split', 'display_label_is_not_equivalence', 'frozen_model_implementation_equivalence'}:
            other = copy.deepcopy(record)
            if name == 'exact_tolerance_precision_loss':
                other['value'] = '0.41000000000000000000000000001'
            elif name in {'correct_unit_conversion', 'equal_bare_number_wrong_unit_scale'}:
                other.update(unit='ms', value='410' if name == 'correct_unit_conversion' else '0.41', lower='390', upper='430')
            elif name == 'different_scientific_split':
                other['split'] = 'training'
            elif name == 'display_label_is_not_equivalence':
                other['model']['value'] = 'Solver A'
            elif name == 'frozen_model_implementation_equivalence':
                other['model']['value'] = 'solver-a-fast'
                other['implementation']['value'] = 'vectorized'
            save(root / 'repeated.json', {'R-latency': other})
            payload['sources'].append({'id': 'repeated', 'path': 'repeated.json', 'sha256': sha(root / 'repeated.json')})
            payload['links'][0]['numeric'][0].update(recomputed={'source_id': 'repeated'}, tolerance={'abs': 0, 'rel': 0})
        save(root / 'payload.json', payload)
        reports = {'audit_links': audit.audit_links(payload, root), 'provider_runtime.audit_payload': bridge.audit_payload(payload, root),
                   'research31.audit': research.audit(payload, root)}
        task = {'capability': 'manuscript-writing', 'request': 'Independent synthetic actual-file binding probe',
                'requested_outputs': ['draft'], 'facts': {'has_verified_results': True}}
        handoff = root / 'handoff'
        bridge.prepare_handoff(task, {}, {'capabilities': ['manuscript-writing'], 'providers': []}, handoff)
        envelope = {'capability': 'manuscript-writing', 'task_sha256': bridge.sha(handoff / 'task.json'),
                    'provider_id': 'host_fallback', 'execution_mode': 'host_fallback', 'execution_status': 'executed',
                    'outputs': [{'path': 'draft.md', 'sha256': sha(root / 'draft.md'), 'role': 'draft'}], 'result_links': payload}
        save(root / 'envelope.json', envelope)
        reports['provider_runtime.accept_result'] = bridge.accept_result(handoff, envelope, root)
        save(root / 'reports.json', reports)
        summary = {'case': name, 'desired_passed': desired, 'actual_passed': reports['audit_links']['passed'],
                   'caller_results': {key: value['passed'] for key, value in reports.items()},
                   'errors': reports['audit_links']['errors'], 'pending': reports['audit_links']['pending']}
        assert len(set(summary['caller_results'].values())) == 1, summary
        results.append(summary)
    summary = {'python': sys.version, 'scripts': str(args.scripts.resolve()),
               'script_sha256': {name: sha(args.scripts / name) for name in ['result_links.py', 'provider_runtime.py', 'research31.py']},
               'cases': results, 'unexpected': [r['case'] for r in results if r['desired_passed'] != r['actual_passed']]}
    save(args.out / 'summary.json', summary)
    print(json.dumps({'cases': len(results), 'unexpected': summary['unexpected']}, ensure_ascii=False))
    return bool(summary['unexpected'])


if __name__ == '__main__':
    raise SystemExit(main())
