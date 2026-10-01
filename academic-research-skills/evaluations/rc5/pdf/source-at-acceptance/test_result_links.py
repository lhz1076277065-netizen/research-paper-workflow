"""Actual-file consistency checks with synthetic values, not research evidence.

Run: python3 -m unittest discover -s tests -p test_result_links.py
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'src/common/scripts' / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


audit = module('result_links_test', 'result_links.py')
bridge = module('result_bridge_test', 'provider_runtime.py')


def pdf_bytes(text):
    """One-page actual PDF; avoids an optional PDF creation library in tests."""
    escaped = text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
    stream = ('BT /F1 7 Tf 25 750 Td (' + escaped + ') Tj ET').encode('ascii')
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>',
               b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
               b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 1400 800] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
               b'<< /Length ' + str(len(stream)).encode() + b' >>\nstream\n' + stream + b'\nendstream']
    result, offsets = b'%PDF-1.4\n', [0]
    for index, body in enumerate(objects, 1):
        offsets.append(len(result))
        result += str(index).encode() + b' 0 obj\n' + body + b'\nendobj\n'
    xref = len(result)
    result += b'xref\n0 6\n0000000000 65535 f \n'
    result += b''.join(('%010d 00000 n \n' % offset).encode() for offset in offsets[1:])
    result += ('trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n' % xref).encode()
    return result


class Links(unittest.TestCase):
    TEXT = ('Accuracy increased to 12.35% (95% CI 10.00%-15.00%; n=120) in held-out cohort '
            'at 6 months versus baseline using M1 test; absolute.')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ('data.csv', 'analysis.py', 'execution.json'):
            (self.root / name).write_text('Synthetic ' + name + '\n')
        self.record = {'value': .123456, 'unit': 'ratio', 'direction': 'increase',
                       'denominator': 120, 'outcome': 'accuracy', 'population': 'held-out cohort',
                       'time': '6 months', 'comparison': 'baseline', 'model': 'M1', 'split': 'test',
                       'uncertainty': '95% CI', 'lower': .1, 'upper': .15, 'effect_type': 'absolute'}
        self.write_source()
        (self.root / 'draft.md').write_text(self.TEXT + '\n')
        semantics = {field: {'value': self.record[field], 'text': str(self.record[field])}
                     for field in audit.SEMANTICS if field in self.record}
        semantics.update(unit={'value': 'percent', 'text': '%'},
                         direction={'value': 'increase', 'text': 'increased'},
                         denominator={'value': 120, 'text': 'n=120'})
        self.payload = {'kind': 'result-links', 'sources': [self.source()], 'links': [{
            'result_id': 'R1', 'role': 'body', 'artifact': self.artifact('draft.md'), 'locator': {'line': 1},
            'numeric': [{'field': 'value', 'text': '12.35', 'decimals': 2},
                        {'field': 'lower', 'text': '10.00', 'decimals': 2},
                        {'field': 'upper', 'text': '15.00', 'decimals': 2}], 'semantics': semantics}]}

    def tearDown(self):
        self.temp.cleanup()

    def artifact(self, path):
        return {'path': path, 'sha256': hashlib.sha256((self.root / path).read_bytes()).hexdigest()}

    def source(self):
        return dict(self.artifact('results.json'), id='frozen', versions={
            name: self.artifact(path) for name, path in [('data', 'data.csv'), ('code', 'analysis.py'), ('execution', 'execution.json')]})

    def write_source(self):
        (self.root / 'results.json').write_text(json.dumps({'R1': self.record}))

    def result(self):
        return audit.audit_links(self.payload, self.root)

    def edit(self, before, after):
        (self.root / 'draft.md').write_text(self.TEXT.replace(before, after) + '\n')
        self.payload['links'][0]['artifact'] = self.artifact('draft.md')

    def test_real_markdown_occurrence_and_separate_coverage(self):
        result = self.result()
        self.assertTrue(result['passed'], result)
        self.assertEqual(len(result['coverage']['numeric']), 3)

    def test_interval_endpoints_cannot_hide_unchecked_estimate(self):
        self.edit('12.35%', '99.00%')
        self.payload['links'][0]['numeric'] = self.payload['links'][0]['numeric'][1:]
        result = self.result()
        self.assertFalse(result['passed'])
        self.assertTrue(any('value' in gap['fields'] for gap in result['coverage_gaps']))
        self.assertTrue(result['coverage']['bytes'])
        self.assertTrue(result['coverage']['declared_semantic'])
        self.assertFalse(result['semantic_truth_certified'])
        self.assertFalse(result['actual_visual_inspection_performed'])

    def test_latex_actual_occurrence(self):
        (self.root / 'draft.tex').write_text(self.TEXT.replace('%', r'\%'))
        self.payload['links'][0]['artifact'] = self.artifact('draft.tex')
        self.assertTrue(self.result()['passed'])

    def test_actual_docx_paragraph(self):
        path = self.root / 'draft.docx'
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>' + self.TEXT + '</w:t></w:r></w:p></w:body></w:document>')
        self.payload['links'][0].update(artifact=self.artifact('draft.docx'), locator={'paragraph': 1})
        self.assertTrue(self.result()['passed'])

    def test_actual_docx_table_cell(self):
        with zipfile.ZipFile(self.root / 'draft.docx', 'w') as archive:
            archive.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:tbl><w:tr><w:tc><w:p><w:r><w:t>' + self.TEXT + '</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>')
        self.payload['links'][0].update(artifact=self.artifact('draft.docx'), locator={'table': 1, 'row': 1, 'cell': 1})
        self.assertTrue(self.result()['passed'])

    @unittest.skipUnless(shutil.which('pdftotext') or importlib.util.find_spec('pypdf'), 'actual PDF extraction requires pdftotext or pypdf')
    def test_actual_pdf_page_line(self):
        (self.root / 'draft.pdf').write_bytes(pdf_bytes(self.TEXT))
        self.payload['links'][0].update(artifact=self.artifact('draft.pdf'), locator={'page': 1, 'line': 1})
        self.assertTrue(self.result()['passed'], self.result())

    def test_edited_value_even_with_current_target_hash_fails(self):
        self.edit('12.35', '12.99')
        self.assertFalse(self.result()['passed'])

    def test_edit_cannot_redefine_source_value_with_display_token(self):
        self.edit('12.35', '12.99')
        self.payload['links'][0]['numeric'][0]['text'] = '12.99'
        self.assertIn('rounding mismatch', str(self.result()['errors']))

    def test_wrong_unit_fails(self):
        self.edit('12.35%', '12.35 mg')
        self.payload['links'][0]['semantics']['unit'] = {'value': 'mg', 'text': 'mg'}
        self.assertIn('Unit mismatch', str(self.result()['errors']))

    def test_wrong_direction_with_correct_declared_value_fails(self):
        self.edit('increased', 'decreased')
        self.payload['links'][0]['semantics']['direction']['text'] = 'decreased'
        self.assertIn('Direction mismatch', str(self.result()['errors']))

    def test_wrong_denominator_text_fails(self):
        self.edit('n=120', 'n=121')
        self.payload['links'][0]['semantics']['denominator']['text'] = 'n=121'
        self.assertIn('Denominator text mismatch', str(self.result()['errors']))

    def test_wrong_followup_even_with_correct_declared_time_fails(self):
        self.edit('6 months', '12 months')
        self.payload['links'][0]['semantics']['time']['text'] = '12 months'
        self.assertIn('time canonical', str(self.result()['errors']))

    def test_outcome_population_comparison_model_split_uncertainty(self):
        for field, wrong in [('outcome', 'precision'), ('population', 'training cohort'),
                             ('comparison', 'placebo'), ('model', 'M2'), ('split', 'train'),
                             ('uncertainty', '90% CI'), ('effect_type', 'relative')]:
            with self.subTest(field=field):
                before = copy.deepcopy(self.payload)
                self.payload['links'][0]['semantics'][field]['value'] = wrong
                self.assertFalse(self.result()['passed'])
                self.payload = before

    def test_percent_ratio_conversion_is_not_a_hundredfold_display_error(self):
        self.edit('12.35%', '0.123456 ratio')
        self.payload['links'][0]['numeric'][0] = {'field': 'value', 'text': '0.123456'}
        # All interval occurrences must use the same unit conversion.
        (self.root / 'draft.md').write_text((self.root / 'draft.md').read_text().replace('10.00%', '0.10 ratio').replace('15.00%', '0.15 ratio').replace('ratio-', 'ratio to '))
        link = self.payload['links'][0]
        link['numeric'][1:] = [{'field': 'lower', 'text': '0.10', 'decimals': 2}, {'field': 'upper', 'text': '0.15', 'decimals': 2}]
        link['semantics']['unit'] = {'value': 'ratio', 'text': 'ratio'}
        link['artifact'] = self.artifact('draft.md')
        self.assertTrue(self.result()['passed'], self.result())

    def test_recomputation_tolerance_does_not_relax_display_rounding(self):
        (self.root / 'recomputed.json').write_text(json.dumps({'R1': dict(self.record,value=.12345600001)}))
        self.payload['sources'].append(dict(self.artifact('recomputed.json'), id='recomputed'))
        link = self.payload['links'][0]
        link['source_id'] = 'frozen'
        link['numeric'][0].update(recomputed={'source_id': 'recomputed'}, tolerance={'abs': 1e-9, 'rel': 1e-8})
        self.assertTrue(self.result()['passed'], self.result())
        self.edit('12.35', '12.99')
        link['numeric'][0]['text'] = '12.99'
        self.assertFalse(self.result()['passed'])

    def test_recomputation_outside_tolerance_fails(self):
        (self.root / 'recomputed.json').write_text(json.dumps({'R1': dict(self.record,value=.124)}))
        self.payload['sources'].append(dict(self.artifact('recomputed.json'), id='recomputed'))
        self.payload['links'][0]['source_id'] = 'frozen'
        self.payload['links'][0]['numeric'][0].update(recomputed={'source_id': 'recomputed'}, tolerance={'abs': 1e-9})
        self.assertIn('exceeds tolerance', str(self.result()['errors']))

    def test_rounding_tie_is_explicit_decimal_half_even_or_half_up(self):
        self.record['value'] = .12345
        self.write_source()
        self.payload['sources'][0] = self.source()
        self.payload['links'][0]['numeric'][0]['rounding'] = 'half-up'
        self.assertTrue(self.result()['passed'], self.result())
        self.edit('12.35', '12.34')
        self.payload['links'][0]['numeric'][0].update(text='12.34', rounding='half-even')
        self.assertTrue(self.result()['passed'])

    def test_display_tolerance_without_recomputed_source_is_rejected(self):
        self.payload['links'][0]['numeric'][0]['tolerance'] = {'abs': 99}
        self.assertFalse(self.result()['passed'])

    def test_frozen_output_and_execution_data_code_version_identity(self):
        for filename in ['results.json', 'data.csv', 'analysis.py', 'execution.json']:
            with self.subTest(filename=filename):
                path = self.root / filename
                content = path.read_bytes()
                path.write_bytes(content + b'changed')
                self.assertFalse(self.result()['passed'])
                path.write_bytes(content)

    def test_missing_source_versions_stay_pending(self):
        self.payload['sources'][0].pop('versions')
        result = self.result()
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['pending']), 3)

    def test_unlinked_critical_claim_has_actionable_location(self):
        self.payload['claims'] = [{'id': 'abstract-1', 'artifact': self.artifact('draft.md'),
                                  'locator': {'line': 1}, 'text': self.TEXT, 'result_ids': ['R1']}]
        result = self.result()
        self.assertFalse(result['passed'])
        self.assertEqual(result['pending'][0]['claim_id'], 'abstract-1')
        self.payload['links'][0]['claim_id'] = 'abstract-1'
        self.assertTrue(self.result()['passed'])

    def test_path_escape_symlink_and_malformed_mapping_are_clean_diagnostics(self):
        for mutation in [lambda link: link['artifact'].update(path='../outside.md'),
                         lambda link: link.update(locator={'line': 0}),
                         lambda link: link.update(semantics=[]),
                         lambda link: link.update(numeric=[None]),
                         lambda link: link['numeric'][0].update(tolerance={'abs': True})]:
            with self.subTest(mutation=mutation):
                before = copy.deepcopy(self.payload)
                mutation(self.payload['links'][0])
                result = self.result()
                self.assertFalse(result['passed'])
                self.assertTrue(result['errors'])
                self.payload = before
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / 'outside.md'
            outside.write_text(self.TEXT)
            (self.root / 'symlink.md').symlink_to(outside)
            self.payload['links'][0]['artifact'] = {'path': 'symlink.md', 'sha256': self.artifact('draft.md')['sha256']}
            self.assertIn('escapes', str(self.result()['errors']))

    def test_csv_frozen_output_uses_existing_result_id(self):
        self.record = {'value': .123456, 'unit': 'ratio'}
        (self.root / 'results.csv').write_text('result_id,value,unit\nR1,0.123456,ratio\n')
        self.payload['sources'][0].update(self.artifact('results.csv'))
        self.payload['links'][0]['numeric'] = self.payload['links'][0]['numeric'][:1]
        self.payload['links'][0]['semantics'] = {'unit': {'value': 'percent', 'text': '%'}}
        result=self.result()
        self.assertTrue(result['coverage']['numeric'])
        self.assertTrue(any(item.get('reason')=='primary_subject_unbound' for item in result['pending'] if isinstance(item,dict)))

    def test_theory_proposition_conditions_and_actual_proof(self):
        (self.root / 'proof.md').write_text('Proof: summing nonnegative terms gives the bound.\n')
        self.record = {'type': 'theory', 'proposition': 'The bound holds', 'conditions': ['x > 0'],
                       'proof': dict(self.artifact('proof.md'), locator={'line': 1}, text='summing nonnegative terms gives the bound')}
        self.write_source()
        (self.root / 'draft.md').write_text('The bound holds when x > 0.\n')
        self.payload = {'sources': [self.source()], 'links': [{'result_id': 'R1', 'role': 'theorem',
            'artifact': self.artifact('draft.md'), 'locator': {'line': 1},
            'bindings': {'proposition': {'text': 'The bound holds'}, 'conditions': {'texts': ['x > 0']}}}]}
        self.assertTrue(self.result()['passed'], self.result())
        (self.root / 'proof.md').write_text('Different proof')
        self.assertFalse(self.result()['passed'])

    def test_interpretation_binds_actual_source_snippet(self):
        (self.root / 'source.md').write_text('The author explicitly rejects the earlier rule.\n')
        self.record = {'type': 'interpretive', 'interpretation': 'The text rejects the rule',
                       'snippets': [dict(self.artifact('source.md'), locator={'line': 1}, text='explicitly rejects the earlier rule')]}
        self.write_source()
        (self.root / 'draft.md').write_text('The text rejects the rule.\n')
        self.payload = {'sources': [self.source()], 'links': [{'result_id': 'R1', 'role': 'interpretation',
            'artifact': self.artifact('draft.md'), 'locator': {'line': 1},
            'bindings': {'interpretation': {'text': 'The text rejects the rule'}}}]}
        self.assertTrue(self.result()['passed'])
        self.record['snippets'][0]['text'] = 'endorses the rule'
        self.write_source()
        self.payload['sources'][0] = self.source()
        self.assertFalse(self.result()['passed'])

    def test_provider_dispatch_uses_same_actual_file_audit(self):
        self.assertTrue(bridge.audit_payload(self.payload, self.root)['passed'])

    def envelope(self):
        task = {'capability': 'manuscript-writing', 'request': 'Synthetic return contract check',
                'requested_outputs': ['draft'], 'facts': {'has_verified_results': True}}
        handoff = self.root / 'handoff'
        bridge.prepare_handoff(task, {}, {'capabilities': ['manuscript-writing'], 'providers': []}, handoff)
        envelope = {'capability': task['capability'], 'task_sha256': bridge.sha(handoff / 'task.json'),
                    'provider_id': 'host_fallback', 'execution_mode': 'host_fallback',
                    'execution_status': 'executed', 'outputs': [dict(self.artifact('draft.md'), role='draft')]}
        return handoff, envelope

    def test_legacy_envelope_needs_no_new_linkage_fields(self):
        handoff, envelope = self.envelope()
        self.assertTrue(bridge.accept_result(handoff, envelope, self.root)['passed'])

    def test_accept_result_optional_inline_links(self):
        handoff, envelope = self.envelope()
        envelope['result_links'] = self.payload
        result = bridge.accept_result(handoff, envelope, self.root)
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['linkage_audits'][0]['kind'], 'result-links')
        self.edit('12.35', '12.99')
        envelope['outputs'][0].update(self.artifact('draft.md'))
        self.assertFalse(bridge.accept_result(handoff, envelope, self.root)['passed'])

    def test_accept_result_hash_bound_manifest_and_pending_claim(self):
        handoff, envelope = self.envelope()
        self.payload['claims'] = [{'id': 'c1', 'artifact': self.artifact('draft.md'), 'locator': {'line': 1}, 'text': self.TEXT}]
        (self.root / 'links.json').write_text(json.dumps(self.payload))
        envelope['result_links'] = self.artifact('links.json')
        result = bridge.accept_result(handoff, envelope, self.root)
        self.assertFalse(result['passed'])
        self.assertEqual(result['status'], 'received_needs_review')
        self.assertTrue(result['pending'])
        (self.root / 'links.json').write_text('{}')
        self.assertEqual(bridge.accept_result(handoff, envelope, self.root)['status'], 'rejected')

    def test_accept_result_unrelated_occurrence_cannot_validate_returned_draft(self):
        handoff, envelope = self.envelope()
        (self.root / 'other.md').write_text(self.TEXT)
        self.payload['links'][0]['artifact'] = self.artifact('other.md')
        envelope['result_links'] = self.payload
        self.assertIn('not a returned output', str(bridge.accept_result(handoff, envelope, self.root)['errors']))

    def test_adapter_optional_project_interpreter_and_workspace(self):
        upstream = self.root / 'upstream'
        upstream.mkdir()
        (upstream / 'SKILL.md').write_text('Synthetic provider entry')
        (upstream / 'profile.py').write_text('import os, sys\ndef profile_data(path, group_cols):\n    return {"cwd":os.getcwd(), "python":sys.executable}\n')
        provider = {'id': 'synthetic.profile', 'entrypoint': 'SKILL.md',
                    'required_paths': ['SKILL.md', 'profile.py'],
                    'script': {'path': 'profile.py', 'adapter': 'scipilot-profile', 'network': False}}
        config = {'providers': {'synthetic.profile': {'root': str(upstream), 'source_reviewed': True, 'script_reviewed': True}}}
        receipt = bridge.run_adapter(provider, config, {'input': str(self.root / 'data.csv')},
                                     self.root / 'adapter-run', interpreter=sys.executable, workspace=self.root)
        self.assertEqual(receipt['status'], 'executed_needs_review')
        raw = json.loads((self.root / 'adapter-run/raw.json').read_text())
        self.assertEqual(raw['cwd'], str(self.root.resolve()))
        self.assertEqual(receipt['python'], str(Path(sys.executable).absolute()))
        self.assertGreaterEqual(receipt['wall_seconds'], 0)

    def test_independent_copy_needs_only_sibling_scripts(self):
        standalone = self.root / 'standalone/scripts'
        standalone.mkdir(parents=True)
        for name in ('provider_runtime.py', 'result_links.py'):
            shutil.copyfile(ROOT / 'src/common/scripts' / name, standalone / name)
        (self.root / 'payload.json').write_text(json.dumps(self.payload))
        (self.root / 'registry.json').write_text('{"providers": []}')
        result = subprocess.run([sys.executable, '-S', '-B', str(standalone / 'provider_runtime.py'),
            '--registry', str(self.root / 'registry.json'), 'audit', '--input', str(self.root / 'payload.json'),
            '--root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class Renders(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.payload = {'kind': 'render-dependencies', 'artifacts': [], 'renders': []}
        for identity, filename in [('tex', 'draft.tex'), ('figure', 'figure.svg'), ('word', 'draft.docx'), ('pdf', 'draft.pdf')]:
            (self.root / filename).write_text('Synthetic frozen ' + filename)
            self.payload['artifacts'].append({'id': identity, 'path': filename,
                'sha256': hashlib.sha256((self.root / filename).read_bytes()).hexdigest()})
        digests = {item['id']: item['sha256'] for item in self.payload['artifacts']}
        self.payload['renders'] = [
            {'output': 'word', 'inputs': {key: digests[key] for key in ['tex', 'figure']}, 'renderer': {'name': 'pandoc', 'version': 'recorded-test-version'}},
            {'output': 'pdf', 'inputs': {'word': digests['word']}, 'renderer': {'name': 'libreoffice', 'version': 'recorded-test-version'}}]

    def tearDown(self):
        self.temp.cleanup()

    def result(self):
        return audit.audit_render(self.payload, self.root)

    def test_actual_frozen_inputs_and_outputs_pass(self):
        result = self.result()
        self.assertTrue(result['passed'], result)
        self.assertEqual(result['rebuild_order'], [])
        self.assertFalse(result['commands_executed'])

    def test_latex_change_identifies_word_and_old_pdf_transitively(self):
        (self.root / 'draft.tex').write_text('Changed editing source')
        result = self.result()
        self.assertFalse(result['passed'])
        self.assertEqual(result['rebuild_order'], ['word', 'pdf'])
        self.assertEqual(result['impacted_rebuild_targets'][1]['changed_inputs'], ['word'])

    def test_word_change_identifies_old_pdf(self):
        (self.root / 'draft.docx').write_text('Changed editing source')
        self.assertEqual(self.result()['rebuild_order'], ['word', 'pdf'])

    def test_refreshed_source_inventory_does_not_refresh_prior_render(self):
        for filename, index in [('draft.tex', 0), ('draft.docx', 2)]:
            with self.subTest(filename=filename):
                before = copy.deepcopy(self.payload)
                path = self.root / filename
                content = path.read_bytes()
                path.write_text('Current edited source')
                self.payload['artifacts'][index]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                result = self.result()
                self.assertFalse(result['passed'])
                expected = ['word', 'pdf'] if filename.endswith('.tex') else ['pdf']
                self.assertEqual(result['rebuild_order'], expected)
                path.write_bytes(content)
                self.payload = before

    def test_changed_figure_propagates_and_pdf_tamper_is_detected(self):
        (self.root / 'figure.svg').write_text('Different figure')
        self.assertEqual(self.result()['rebuild_order'], ['word', 'pdf'])
        (self.root / 'draft.pdf').unlink()
        self.assertFalse(self.result()['passed'])

    def test_malformed_digest_cycle_and_path_escape_fail_cleanly(self):
        before = copy.deepcopy(self.payload)
        for mutation in [lambda: self.payload['artifacts'][0].update(path='../escape'),
                         lambda: self.payload['renders'][0]['inputs'].update(tex='0' * 64),
                         lambda: self.payload['renders'][0]['inputs'].update(pdf=self.payload['artifacts'][3]['sha256']),
                         lambda: self.payload.update(renders=[None])]:
            mutation()
            result = self.result()
            self.assertFalse(result['passed'])
            self.assertTrue(result['errors'])
            self.payload = copy.deepcopy(before)

    def test_manifest_commands_are_not_executed(self):
        self.payload['renders'][0]['command'] = ['touch', str(self.root / 'SHOULD-NOT-EXIST')]
        self.assertTrue(self.result()['passed'])
        self.assertFalse((self.root / 'SHOULD-NOT-EXIST').exists())

    def test_provider_dispatch_render(self):
        self.assertTrue(bridge.audit_payload(self.payload, self.root)['passed'])


if __name__ == '__main__':
    unittest.main()
