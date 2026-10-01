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


class Rc5Relations(unittest.TestCase):
    """Fresh computed latency material, independent of the rc4 wine/export packet."""
    TEXT=('Solver A latency was 410.0 ms (95% CI 390.0 ms-430.0 ms), lower than Solver baseline '
          'on digital instances (n=4), holdout at one run; absolute mean; loop.')

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        (self.root/'measurements.json').write_text('["0.40", "0.42", "0.41", "0.41"]')
        code=self.root/'compute.py'
        code.write_text('import json,sys\nfrom pathlib import Path\nfrom decimal import Decimal\nx=json.loads(Path(sys.argv[1]).read_text())\nprint(json.dumps({"value":str(sum(map(Decimal,x))/len(x))}))\n')
        run=subprocess.run([sys.executable,str(code),str(self.root/'measurements.json')],capture_output=True,text=True,check=True)
        (self.root/'execution.json').write_text(run.stdout)
        self.record={'value':json.loads(run.stdout)['value'],'unit':'s','lower':'0.39','upper':'0.43',
            'model':{'value':'solver-a','labels':['Solver A'],'equivalent_values':['solver-a-fast']},
            'implementation':{'value':'loop','labels':['loop'],'equivalent_values':['vectorized']},
            'outcome':'latency','direction':'decrease','population':'digital instances','denominator':4,
            'comparison':'Solver baseline','split':'holdout','time':'one run','effect_type':'absolute mean','uncertainty':'95% CI'}
        self.records={'R-latency':self.record}
        self.sources=[{'id':'frozen','path':'results.json','versions':{name:{'path':path} for name,path in [
            ('data','measurements.json'),('code','compute.py'),('execution','execution.json')]}}]
        self.rows=[{'path':'draft.md','result_id':'R-latency','role':'body','locator':{'line':1},'unit':'ms',
                    'numeric':[{'field':field,'decimals':1} for field in ('value','lower','upper')]}]
        self.text=self.TEXT;self.save()

    def tearDown(self):self.temp.cleanup()

    def save(self):
        (self.root/'results.json').write_text(json.dumps(self.records))
        (self.root/'draft.md').write_text(self.text+'\n')

    def payload(self):return audit.build_links(self.root,self.sources,self.rows)

    def result(self):return audit.audit_links(self.payload(),self.root)

    def recomputation(self,other):
        (self.root/'repeated.json').write_text(json.dumps({'R-latency':other}))
        data=self.payload();data['sources'].append({'id':'repeated','path':'repeated.json','sha256':audit._sha(self.root/'repeated.json')})
        data['links'][0]['numeric'][0].update(recomputed={'source_id':'repeated'},tolerance={'abs':0,'rel':0})
        return audit.audit_links(data,self.root)

    def test_actual_build_rows_reuse_frozen_semantics_and_display(self):
        data=self.payload();report=audit.audit_links(data,self.root)
        self.assertEqual(data['links'][0]['numeric'][0]['text'],'410.0')
        self.assertTrue(report['passed'],report)
        self.assertTrue(report['coverage']['relationships'])
        self.assertFalse(report['semantic_truth_certified'])

    def test_recomputed_true_unit_equivalence_not_equal_bare_numbers(self):
        other=copy.deepcopy(self.record);other.update(unit='ms',value='410',lower='390',upper='430')
        result=self.recomputation(other)
        self.assertTrue(result['passed'],result)
        self.assertEqual(result['coverage']['numeric'][0]['recomputation']['converted_value'],'0.410')
        other['value']='0.41'
        self.assertIn('exceeds tolerance',str(self.recomputation(other)['errors']))
        other['unit']='g'
        self.assertIn('dimensions differ',str(self.recomputation(other)['errors']))

    def test_recomputed_context_and_field_roles_must_agree(self):
        for field in ('split','time','outcome','population','comparison','effect_type'):
            with self.subTest(field=field):
                other=copy.deepcopy(self.record);other[field]='another '+field
                self.assertIn('identity mismatch: '+field,str(self.recomputation(other)['errors']))
        data=self.payload();data['sources'].append({'id':'repeated','path':'results.json','sha256':audit._sha(self.root/'results.json')})
        data['links'][0]['numeric'][0]['recomputed']={'source_id':'repeated','field':'lower'}
        self.assertIn('field role differs',str(audit.audit_links(data,self.root)['errors']))

    def test_only_frozen_scientific_equivalence_aliases_authorize_models(self):
        other=copy.deepcopy(self.record);other['model']['value']='solver-a-fast';other['implementation']['value']='vectorized'
        self.assertTrue(self.recomputation(other)['passed'])
        other['model']['value']='Solver A'  # A display label is not scientific equivalence.
        self.assertIn('identity mismatch: model',str(self.recomputation(other)['errors']))
        other['model']['value']='solver-a-fast';self.record['model'].pop('equivalent_values');self.save()
        self.assertIn('identity mismatch: model',str(self.recomputation(other)['errors']))

    def test_missing_recomputation_identity_remains_located_pending(self):
        self.record.pop('split');self.save();other=copy.deepcopy(self.record)
        report=self.recomputation(other)
        self.assertFalse(report['passed']);self.assertFalse(report['errors'])
        self.assertTrue(any(item.get('reason')=='recomputation_identity_unbound' and item['locator']=={'line':1} for item in report['pending']))

    def test_swapped_intervals_fail_but_explicit_upper_lower_labels_are_valid(self):
        self.text=self.TEXT.replace('390.0 ms-430.0 ms','430.0 ms-390.0 ms');self.save()
        self.assertIn('endpoints are reversed',str(self.result()['errors']))
        self.text=self.TEXT.replace('390.0 ms-430.0 ms','upper: 430.0 ms, lower: 390.0 ms');self.save()
        self.assertTrue(self.result()['passed'],self.result())

    def test_range_separator_does_not_hide_a_negative_primary_value(self):
        self.text=self.TEXT.replace('was 410.0 ms','was -410.0 ms');self.save()
        self.assertIn('Numeric token absent',str(self.result()['errors']))
        self.text=self.TEXT.replace('was 410.0 ms','was −410.0 ms');self.save()
        self.assertIn('Numeric token absent',str(self.result()['errors']))

    def test_known_wrong_subject_and_paragraph_cooccurrence_cannot_pass(self):
        other=copy.deepcopy(self.record);other['model']={'value':'solver-b','labels':['Solver B']}
        self.records['R-other']=other
        self.text=self.TEXT.replace('Solver A latency was 410.0 ms','Solver A latency was 500.0 ms; Solver B latency was 410.0 ms');self.save()
        self.assertIn('different model',str(self.result()['errors']))
        self.text=self.TEXT.replace('Solver A latency was','Solver A is background. An unknown method latency was');self.save()
        result=self.result()
        self.assertFalse(result['passed'])
        self.assertTrue(any(item.get('reason')=='primary_subject_relationship_unresolved' for item in result['pending']))

    def test_unknown_connectors_are_review_pending_not_certified(self):
        for connector in ('was reported incorrectly as','contrasted with unknown B at'):
            with self.subTest(connector=connector):
                self.text=self.TEXT.replace('latency was','latency '+connector);self.save()
                result=self.result()
                self.assertFalse(result['passed']);self.assertFalse(result['errors'])
                self.assertTrue(any(item.get('reason')=='primary_subject_connector_unresolved' for item in result['pending']))

    def test_comparison_threshold_cannot_be_an_exact_primary_value(self):
        for comparison in ('lower than','higher than','at least','below','<'):
            with self.subTest(comparison=comparison):
                self.text=self.TEXT.replace('was 410.0','was '+comparison+' 410.0');self.save()
                result=self.result();self.assertFalse(result['passed']);self.assertFalse(result['errors'],result)
                self.assertTrue(any(item.get('reason')=='primary_value_is_comparison_threshold' for item in result['pending']))
                self.assertFalse(any(item['relationship']=='primary_subject' for item in result['coverage']['relationships']))

    def test_independent_unit_locator_still_checks_the_actual_number(self):
        self.text=self.TEXT.replace('was 410.0 ms','was 410.0 g')+'\nms';self.save()
        data=self.payload();data['links'][0]['semantics']['unit']={'value':'ms','text':'ms','locator':{'line':2}}
        self.assertIn('Actual numeric unit differs',str(audit.audit_links(data,self.root)['errors']))
        self.text=self.TEXT.replace('was 410.0 ms','was 410.0')+'\nms';self.save()
        data=self.payload();data['links'][0]['semantics']['unit']={'value':'ms','text':'ms','locator':{'line':2}}
        result=audit.audit_links(data,self.root);self.assertFalse(result['passed']);self.assertFalse(result['errors'],result)
        self.assertTrue(any(item.get('reason')=='numeric_unit_relationship_unresolved' for item in result['pending']))
        self.text=self.TEXT+'\nms';self.save()
        data=self.payload();data['links'][0]['semantics']['unit']={'value':'ms','text':'ms','locator':{'line':2}}
        self.assertTrue(audit.audit_links(data,self.root)['passed'])

    def test_fake_table_coordinates_and_mixed_locators_are_rejected(self):
        original=self.payload();data=copy.deepcopy(original);link=data['links'][0]
        link['locator'].update(table=1,row=2,cell=2)
        link['semantics']['model']['locator']={'line':1,'table':1,'row':2,'cell':1}
        self.assertIn('inapplicable locator',str(audit.audit_links(data,self.root)['errors']))
        for locator in ({'line':1,'paragraph':1},{'line':1,'page':1},{'line':1,'line_start':1},{'table':1,'row':1,'cell':1}):
            with self.subTest(locator=locator):
                data=copy.deepcopy(original);data['links'][0]['locator']=locator
                self.assertIn('inapplicable locator',str(audit.audit_links(data,self.root)['errors']))
        data=copy.deepcopy(original);data['links'][0]['semantics']['model']['locator']={'line':1,'table':1,'row':2,'cell':1}
        self.assertIn('inapplicable locator',str(audit.audit_links(data,self.root)['errors']))
        for extension,locator in [('tex',{'line':1,'paragraph':1}),('pdf',{'page':1,'line':1,'table':1,'row':2,'cell':2}),
                                  ('docx',{'paragraph':1,'table':1,'row':2,'cell':2})]:
            with self.subTest(extension=extension):
                path=self.root/('draft.'+extension)
                if extension=='pdf':path.write_bytes(pdf_bytes(self.TEXT))
                elif extension=='docx':
                    with zipfile.ZipFile(path,'w') as archive:
                        archive.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>'+self.TEXT+'</w:t></w:r></w:p></w:body></w:document>')
                else:path.write_text(self.TEXT)
                data=copy.deepcopy(original);data['links'][0].update(artifact={'path':path.name,'sha256':audit._sha(path)},locator=locator)
                self.assertIn('inapplicable locator',str(audit.audit_links(data,self.root)['errors']))

    def test_zero_tolerance_preserves_all_decimal_digits_during_conversion(self):
        for unit,value in [('s','0.41000000000000000000000000001'),
                           ('ms','410.00000000000000000000000001')]:
            with self.subTest(unit=unit):
                other=copy.deepcopy(self.record);other.update(unit=unit,value=value)
                self.assertIn('exceeds tolerance',str(self.recomputation(other)['errors']))
        other=copy.deepcopy(self.record);other['value']='0.41000000000000000000000000001'
        data=self.payload();(self.root/'repeated.json').write_text(json.dumps({'R-latency':other}))
        data['sources'].append({'id':'repeated','path':'repeated.json','sha256':audit._sha(self.root/'repeated.json')})
        data['links'][0]['numeric'][0].update(recomputed={'source_id':'repeated'},tolerance={'abs':1e-29,'rel':0})
        self.assertTrue(audit.audit_links(data,self.root)['passed'])
        data['links'][0]['numeric'][0]['tolerance']['abs']=1e-30
        self.assertIn('exceeds tolerance',str(audit.audit_links(data,self.root)['errors']))
        # JSON numeric literals must preserve precision just as string-valued raw outputs do.
        numeric_json=json.dumps({'R-latency':other}).replace('"'+other['value']+'"',other['value'])
        (self.root/'repeated.json').write_text(numeric_json)
        data['sources'][-1]['sha256']=audit._sha(self.root/'repeated.json')
        data['links'][0]['numeric'][0]['tolerance']['abs']=0
        self.assertIn('exceeds tolerance',str(audit.audit_links(data,self.root)['errors']))

    def test_numeric_semantic_json_remains_serializable_through_actual_cli(self):
        self.record['time']=0.5;self.text=self.TEXT.replace('one run','0.5');self.save()
        payload=self.payload()
        encoded=json.dumps(payload,allow_nan=False)
        self.assertEqual(payload['links'][0]['semantics']['time']['value'],'0.5')
        report=audit.audit_links(payload,self.root);self.assertTrue(report['passed'],report)
        json.dumps(report,allow_nan=False)
        manifest=self.root/'links.json';manifest.write_text(encoded)
        registry=self.root/'registry.json';registry.write_text('{"providers":[]}')
        execution=subprocess.run([sys.executable,str(ROOT/'src/common/scripts/provider_runtime.py'),
            '--registry',str(registry),'audit','--input',str(manifest),'--root',str(self.root)],capture_output=True,text=True)
        self.assertEqual(execution.returncode,0,execution.stderr+execution.stdout)
        returned=json.loads(execution.stdout)
        self.assertTrue(returned['passed'],returned)
        self.assertEqual(next(item['source_value'] for item in returned['coverage']['declared_semantic'] if item['field']=='time'),'0.5')

    def test_negation_scope_direct_nonlocal_and_unrelated(self):
        self.text=self.TEXT.replace('was 410.0','was not 410.0');self.save()
        self.assertIn('Negated actual occurrence',str(self.result()['errors']))
        self.text='It is not true that '+self.TEXT;self.save()
        result=self.result();self.assertFalse(result['passed'])
        self.assertTrue(any(item.get('reason')=='negation_scope_unresolved' for item in result['pending']))
        self.text='No values were excluded. '+self.TEXT;self.save()
        self.assertTrue(self.result()['passed'],self.result())

    def test_separate_semantic_locator_cannot_hide_negated_direction(self):
        self.record['direction']='increase';self.text=self.TEXT.replace('lower','increased')+'\nThis is not an increase.';self.save()
        data=self.payload();data['links'][0]['semantics']['direction']={'value':'increase','text':'increase','locator':{'line':2}}
        self.assertIn('Negated actual occurrence',str(audit.audit_links(data,self.root)['errors']))
        self.text=self.TEXT.replace('lower','increased')+'\nIt is not known whether this is an increase.';self.save()
        data=self.payload();data['links'][0]['semantics']['direction']={'value':'increase','text':'increase','locator':{'line':2}}
        report=audit.audit_links(data,self.root)
        self.assertTrue(any(item.get('reason')=='semantic_negation_scope_unresolved' for item in report['pending']))

    def test_local_caption_and_whole_manuscript_coverage_are_separate(self):
        self.text=self.TEXT+'\nSolver A latency was 410.0 ms.';self.save()
        caption={'path':'draft.md','result_id':'R-latency','role':'caption','locator':{'line':2},'unit':'ms',
                 'numeric':[{'field':'value','decimals':1}]}
        self.rows.append(caption);report=self.result()
        self.assertTrue(report['passed'],report)
        self.assertTrue(report['coverage']['occurrences'][1]['fields_not_in_this_occurrence'])
        self.assertFalse(report['coverage_gaps'])
        self.rows=[caption];report=self.result()
        self.assertFalse(report['passed']);self.assertFalse(report['errors']);self.assertTrue(report['coverage_gaps'])
        self.assertIn('lower',report['coverage_gaps'][0]['fields'])

    def test_actual_table_subject_cell_and_header_have_limited_coverage(self):
        ns='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        rows=[['Model (ms)','latency (ms)'],['Solver A','410.0'],['Solver A','410.0']]
        xml='<w:document xmlns:w="'+ns+'"><w:body><w:tbl>'
        for row in rows:
            xml+='<w:tr>'+''.join('<w:tc><w:p><w:r><w:t>'+cell+'</w:t></w:r></w:p></w:tc>' for cell in row)+'</w:tr>'
        xml+='</w:tbl></w:body></w:document>'
        with zipfile.ZipFile(self.root/'table.docx','w') as archive:archive.writestr('word/document.xml',xml)
        self.rows=[{'path':'table.docx','result_id':'R-latency','role':'table','locator':{'table':1,'row':2,'cell':2},'unit':'ms',
            'numeric':[{'field':'value','decimals':1}], 'subject_field':'model',
            'semantics':{'model':{'value':'solver-a','text':'Solver A','locator':{'table':1,'row':2,'cell':1}},
                         'outcome':{'value':'latency','text':'latency','locator':{'table':1,'row':1,'cell':2}},
                         'unit':{'value':'ms','text':'ms','locator':{'table':1,'row':1,'cell':2}}}}]
        report=self.result()
        self.assertFalse(report['errors'],report)
        self.assertEqual(report['coverage']['numeric'][0]['unit_binding'],'same-column-header')
        self.assertTrue(any(item['relationship']=='table_subject_coordinates' for item in report['coverage']['relationships']))
        self.assertTrue(report['coverage_gaps'])  # This table does not bind the full study design.
        self.rows[0]['subject_field']='outcome';report=self.result()
        self.assertTrue(any(item.get('field')=='outcome' for item in report['coverage']['relationships']))
        self.rows[0]['subject_field']='model'
        self.rows[0]['semantics']['model']['locator']['row']=3
        report=self.result();self.assertFalse(report['errors'],report)
        self.assertTrue(any(item.get('reason')=='primary_subject_relationship_unresolved' for item in report['pending']))
        self.rows[0]['semantics']['model']['locator']['row']=2
        self.rows[0]['semantics']['unit']['locator']['cell']=1
        report=self.result();self.assertFalse(report['errors'],report)
        self.assertTrue(any(item.get('reason')=='numeric_unit_relationship_unresolved' for item in report['pending']))
        self.rows[0]['semantics']['unit']['locator']['cell']=2
        with zipfile.ZipFile(self.root/'table.docx','w') as archive:
            archive.writestr('word/document.xml',xml.replace('410.0','410.0 g'))
        self.assertIn('Actual numeric unit differs',str(self.result()['errors']))

    def test_build_preserves_pinned_source_identity(self):
        self.sources[0]['sha256']=audit._sha(self.root/'results.json')
        self.record['value']='0.42';self.save()
        with self.assertRaisesRegex(ValueError,'version mismatch'):self.payload()


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
