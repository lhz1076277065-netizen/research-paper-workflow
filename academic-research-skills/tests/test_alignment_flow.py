"""Source-bound integration and real subprocess gates; fixtures are not science."""
import contextlib, io, json, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/common/scripts'))
import capabilities as C
import professional_flow as F
import phase_control as P
import local_data as D
import research_commitment as R
import research_storage as S
import work_units as W


class AlignmentFlow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve(); self.n = 0
        self.task = self.root / 'request.md'
        self.task.write_text('Fixture user request: study the relationship between A and B.')
        self.material = self.root / 'materials.md'; self.material.write_text('Fixture constraints.')
        self.guide = 'Read the actual inputs and report a reproducible comparison with limitations.'
        caps = ['topic-novelty', 'research-design', 'data-discovery', 'data-preparation',
                'analysis-execution', 'robustness-reproducibility', 'scientific-visualization',
                'manuscript-writing', 'citation-audit', 'manuscript-review', 'final-expression']
        cap = dict(id='fixture', repository='owner/repo', commit='a' * 40, tree='b' * 40,
                   entry='SKILL.md', kind='skill_protocol', roles=['research'], dependencies=[],
                   host_adaptation='Software fixture',
                   required_files=[dict(path='SKILL.md', blob=C.blob(self.guide.encode()))])
        self.idx = {'capabilities': [cap], 'professional_routes': {
            k: dict(primary='fixture', alternatives=[], work='Use actual inputs', boundary='Fixture only')
            for k in caps}}
        self.index = self.root / 'index.json'; P.save(self.index, self.idx)
        self.cache = self.root / 'cache'
        guide = self.cache / 'fixture' / ('a' * 40) / 'SKILL.md'
        guide.parent.mkdir(parents=True); guide.write_text(self.guide)
        self.mock_index = patch.object(C, 'index_path', return_value=self.index); self.mock_index.start()
        self.phase = self.root / 'phase.json'
        state = P.init('full', 'Fixture fixed A–B relationship', autonomous_plan=True,
                       workflow='local-data', alignment=True)
        self.commit_spec = self.root / 'commitment-spec.json'
        P.save(self.commit_spec, dict(title='Fixture relationship of A and B', objects=['A', 'B'],
            relationship='A–B relationship', scope='Two specified fixture tables',
            completion_criteria=['Answer Q1 by a valid completed test; no positive direction required.'],
            questions=[dict(id='Q1', text='How are A and B related?', required=True),
                       dict(id='Q2', text='Optional subgroup explanation of A–B.', required=False)],
            primary_experiments=[dict(id='E1', question_ids=['Q1'],
                purpose='Estimate the fixed A–B relationship', method='Fixture comparison')]))
        R.bind(state, self.root, self.commit_spec, self.task, self.material, self.task.read_text())
        P.save(self.phase, state)
        self.step('topic-novelty'); self.advance('design')
        self.planfile = self.root / 'research-plan.md'
        self.step('research-design', {self.planfile: 'Fixture plan: estimate A–B using both planned tables.'})
        self.advance('data')
        self.discovery = self.begin('data-discovery', [self.planfile])
        self.spec = self.root / 'data-spec.json'
        P.save(self.spec, {'datasets': [dict(id=k, purpose='Fixture ' + k, files=[dict(
            path=k + '.csv', format='csv', required_columns=['x', 'target'],
            numeric_columns=['x', 'target'], expected_rows=2)]) for k in ('a', 'b')]})
        state = P.load(self.phase); D.plan(state, self.root, self.spec, self.planfile)
        S.plan(self.root, {'needs': [dict(purpose='Both planned tables', subset='Two small tables',
            access='Fixture files')], 'expected_download_bytes': 10000,
            'expected_peak_project_bytes': 10_000_000})
        state['storage'] = dict(root=str(self.root), id=S.read(self.root)['id'])
        P.save(self.phase, state)

    def tearDown(self):
        self.mock_index.stop(); self.tmp.cleanup()

    def begin(self, capability, inputs=None, **kwargs):
        if inputs is None and capability in D.INPUT_GROUPS:
            inputs = []; state = P.load(self.phase)
            rows = state.get('professional_steps', []) + state.get('professional_pending', [])
            for group in D.INPUT_GROUPS[capability]:
                row = next((x for x in reversed(rows) if x['capability'] in group and x.get('finished')), None)
                if row: inputs.extend(Path(x['path']) for x in P.load(row['finished'])['outputs'])
        self.n += 1; name = str(self.n) + '-' + capability
        start = F.begin(self.idx, capability, self.task, inputs or [self.material], self.cache,
                        phase=self.phase, **kwargs)
        path = self.root / (name + '-start.json'); F.persist(start, path)
        return start, path, name

    def finish(self, begun, outputs=None):
        start, path, name = begun
        outputs = outputs or {self.root / (name + '.md'): 'Fixture computed result and limitations.'}
        for file, content in outputs.items(): file.write_text(content)
        report = self.root / (name + '-work.json')
        P.save(report, dict(step_id=start['id'], scope='requested_step', omitted_required_work=[],
            functions_run=False, actions=[dict(source_file='SKILL.md', source_excerpt=self.guide,
                applied='Read fixture inputs and computed this comparison.', output=str(file),
                output_excerpt=content) for file, content in outputs.items()]))
        done = F.finish(self.idx, start, list(outputs), report, 'adapted_in_host')
        end = self.root / (name + '-finish.json'); F.persist(done, end, start)
        return path, end

    def step(self, capability, outputs=None, inputs=None, **kwargs):
        return self.finish(self.begin(capability, inputs, **kwargs), outputs)

    def advance(self, following):
        state = P.load(self.phase)
        rows = [x for x in state['professional_pending'] if x['status'] != 'cancelled']
        evidence = self.root / ('exit-' + state['stage'] + '.md')
        evidence.write_text('Fixture stage work is complete for the specified next action.')
        checked = P.professional_exit(state, [x['started'] for x in rows], [x['finished'] for x in rows])
        P.advance(state, following, evidence, self.root, 'Continue the fixed A–B test')
        P.consume_professional(state, checked); P.save(self.phase, state)

    def acquire(self):
        metadata = self.root / 'metadata.md'; selection = self.root / 'selection.md'
        start, end = self.finish(self.discovery, {
            metadata: 'Fixture publisher documents both complete two-row tables.',
            selection: 'Both tables support the specified A–B test.'})
        state = P.load(self.phase)
        for key in ('a', 'b'):
            (self.root / (key + '.csv')).write_text('x,target\n1,0\n2,1\n')
            D.source(state, key, metadata, selection, start, end,
                     'Fixture publisher', 'v1', 'https://example.org/fixture')
        return state

    def research(self):
        self.acquire()
        self.step('data-preparation', inputs=[self.root / 'a.csv', self.root / 'b.csv'])
        self.advance('research')

    def run_marker(self, begun, marker):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return P.main(['--state', str(self.phase), 'run', '--log', str(self.root / (marker + '.log')),
                '--claim', 'Fixed A–B fixture test', '--decision', 'Compute the planned test',
                '--professional-started', str(begun[1]), '--', sys.executable, '-c',
                'from pathlib import Path; Path(' + repr(str(self.root / marker)) + ').write_text("executed")'])

    def answers(self, answer='answered', execution='completed', outcome='refuted'):
        result = self.root / 'primary-result.json'
        self.step('analysis-execution', {result: '{"effect": 0, "precision": "fixture only"}'},
                  question_ids=['Q1'])
        state = P.load(self.phase)
        W.checkpoint(state, 'primary', 'Fixed A–B test', 'Resolve Q1 and write its evidence-supported answer', [result], self.root,
            outcome=outcome, question_ids=['Q1'], execution=execution, answer=answer,
            validity='valid' if execution == 'completed' else 'unknown', results=[result], experiment_id='E1')
        P.save(self.phase, state)
        index = self.root / 'result-index.json'
        P.save(index, dict(questions=[dict(id='Q1', answer='Fixture zero effect within tested scope.',
            work_units=['primary'])], experiments=[dict(id='E1', work_unit='primary', results=[result.name])]))
        return result, index

    def manuscript(self):
        self.research(); result, index = self.answers()
        state = P.load(self.phase); R.bind_results(state, self.root, self.planfile, index); P.save(self.phase, state)
        self.step('robustness-reproducibility'); self.step('scientific-visualization'); self.advance('manuscript')
        state = P.load(self.phase)
        contract = self.root / state['research_commitment']['record']['path']
        figure = D.completed(state, 'scientific-visualization')
        inputs = [contract, self.planfile, index, result] + [Path(x['path']) for x in P.load(figure['finished'])['outputs']]
        writing = self.step('manuscript-writing', inputs=inputs)
        review = self.step('manuscript-review')
        return writing, review

    def test_partial_data_diagnostic_really_runs_without_resetting_budget_or_quota(self):
        self.acquire(); (self.root / 'b.csv').unlink()
        before = P.load(self.phase); quota = S.read(self.root)
        begun = self.begin('analysis-execution', [self.root / 'a.csv'], purpose='diagnostic', question_ids=['Q1'])
        self.assertEqual(self.run_marker(begun, 'diagnostic-ran'), 0)
        self.assertEqual((self.root / 'diagnostic-ran').read_text(), 'executed')
        self.finish(begun)
        state = P.load(self.phase)
        with self.assertRaises(D.DataError): D.completed(state, 'analysis-execution')
        self.assertEqual(state['budget_anchor'], before['budget_anchor'])
        self.assertEqual(S.read(self.root), quota)
        self.assertEqual(state['status'], 'active')

    def test_diagnostic_follows_actual_preparation_output_to_available_planned_data(self):
        self.acquire(); (self.root / 'b.csv').unlink()
        prepared = self.root / 'prepared-a.csv'
        self.step('data-preparation', {prepared: 'x,target\n1,0\n2,1\n'},
                  inputs=[self.root / 'a.csv'], purpose='diagnostic')
        begun = self.begin('analysis-execution', [prepared], purpose='diagnostic', question_ids=['Q1'])
        selected = D.diagnostic_ready(P.load(self.phase), 'analysis-execution', begun[0]['inputs'])
        self.assertEqual([row['path'] for row in selected['local_files_checked']], ['a.csv'])
        self.assertFalse(selected['all_required_data_checked'])
        self.assertEqual(self.run_marker(begun, 'derived-diagnostic-ran'), 0)
        self.assertTrue((self.root / 'derived-diagnostic-ran').exists())
        with self.assertRaises(D.DataError): D.completed(P.load(self.phase), 'data-preparation')

    def test_external_reader_establishes_inspection_before_diagnostic_analysis(self):
        # A versioned software-fixture contract selects an external reader; its
        # actual subprocess parses the table instead of asserting readability.
        revised = self.root / 'external-data-spec.json'; spec = P.load(self.spec)
        spec['datasets'][0]['files'][0]['format'] = 'external'; P.save(revised, spec)
        state = P.load(self.phase)
        D.plan(state, self.root, revised, self.planfile, 'Fixture uses an external table reader')
        P.save(self.phase, state); self.acquire(); (self.root / 'b.csv').unlink()
        raw = self.root / 'a.csv'
        with self.assertRaises(D.DataError):
            self.begin('analysis-execution', [raw], purpose='diagnostic')
        reader = self.begin('data-preparation', [raw], purpose='diagnostic')
        result = self.root / 'reader-result.json'
        code = ('import csv,json; from pathlib import Path; '
                'rows=list(csv.reader(Path(' + repr(str(raw)) + ').open())); '
                'Path(' + repr(str(result)) + ').write_text(json.dumps({"columns":rows[0],'
                '"rows":len(rows)-1,"sum_x":sum(float(row[0]) for row in rows[1:])}))')
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = P.main(['--state', str(self.phase), 'run', '--log', str(self.root / 'reader.log'),
                '--claim', 'Decode the selected local table', '--decision', 'Establish actual readability',
                '--professional-started', str(reader[1]), '--', sys.executable, '-c', code])
        self.assertEqual(rc, 0)
        self.assertEqual(P.load(result), {'columns': ['x', 'target'], 'rows': 2, 'sum_x': 3.0})
        start, end = self.finish(reader, {result: result.read_text()})
        attached = D.external_inspection(P.load(self.phase), start, end)
        self.assertEqual(attached['inspected_files'], ['a.csv'])
        analysis = self.begin('analysis-execution', [raw], purpose='diagnostic')
        self.assertEqual(self.run_marker(analysis, 'external-diagnostic-ran'), 0)
        self.assertTrue((self.root / 'external-diagnostic-ran').exists())

    def test_formal_run_rechecks_all_required_data_before_launch(self):
        self.research(); begun = self.begin('analysis-execution')
        (self.root / 'b.csv').unlink()
        self.assertEqual(self.run_marker(begun, 'formal-must-not-run'), 2)
        self.assertFalse((self.root / 'formal-must-not-run').exists())
        self.assertEqual(P.load(self.phase)['status'], 'active')

    def test_complete_data_allows_actual_formal_process(self):
        self.research(); begun = self.begin('analysis-execution')
        self.assertEqual(self.run_marker(begun, 'formal-ran'), 0)
        self.assertTrue((self.root / 'formal-ran').is_file())

    def test_diagnostic_preparation_cannot_replace_formal_data_stage_exit(self):
        self.acquire()
        self.step('data-preparation', inputs=[self.root / 'a.csv'], purpose='diagnostic')
        with self.assertRaises(D.DataError): self.advance('research')
        self.assertEqual(P.load(self.phase)['stage'], 'data')

    def test_diagnostic_analysis_cannot_be_a_formal_predecessor(self):
        self.research()
        self.step('analysis-execution', inputs=[self.root / 'a.csv'], purpose='diagnostic')
        with self.assertRaises(D.DataError): self.begin('robustness-reproducibility')
        with self.assertRaises(D.DataError):
            D.input_lineage(P.load(self.phase), 'robustness-reproducibility',
                            [F.ref(self.root / (str(self.n - 1) + '-analysis-execution.md'))])

    def test_diagnostic_requires_valid_planned_local_content_and_correct_stage(self):
        self.acquire(); (self.root / 'a.csv').write_text('wrong,target\n1,0\n2,1\n')
        for cap, inputs in [('analysis-execution', [self.material]),
                            ('analysis-execution', [self.root / 'a.csv']),
                            ('manuscript-writing', [self.root / 'b.csv'])]:
            with self.subTest(cap=cap, inputs=inputs):
                with self.assertRaises((D.DataError, R.CommitmentError)):
                    self.begin(cap, inputs, purpose='diagnostic')

    def test_operational_steering_keeps_data_results_and_review_bound(self):
        writing, review = self.manuscript()
        state = P.load(self.phase); before = state['budget_anchor']; quota = S.read(self.root)
        old_id = state['research_commitment']['id']
        P.update_instruction(state, 'Please report progress.', 'operational'); P.save(self.phase, state)
        self.assertEqual(D.load(state)[1]['instruction'], old_id)
        for cap in ('analysis-execution', 'manuscript-writing', 'manuscript-review'):
            self.assertEqual(D.completed(state, cap)['capability'], cap)
        F.validate_start(self.idx, P.load(review[0]))
        self.assertEqual(R._results(state)['commitment_id'], old_id)
        self.assertEqual(state['budget_anchor'], before); self.assertEqual(S.read(self.root), quota)

    def test_citation_and_review_revisions_feed_next_stage_without_original_draft(self):
        writing, _ = self.manuscript()
        original = Path(P.load(writing[1])['outputs'][0]['path'])
        cited = self.root / 'manuscript-v2-cited.md'
        self.step('citation-audit', {cited: 'Fixture A–B manuscript with corrected source attribution.'},
                  inputs=[original])
        reviewed = self.root / 'manuscript-v2-reviewed.md'
        review = self.begin('manuscript-review', [cited])
        self.assertNotIn(str(original), [x['path'] for x in review[0]['inputs']])
        self.finish(review, {reviewed: 'Fixture A–B manuscript with the scientific review revision.'})
        polished = self.root / 'manuscript-v2-polished.md'
        polish = self.begin('final-expression', [reviewed])
        self.assertEqual([x['path'] for x in polish[0]['inputs']], [str(reviewed)])
        self.finish(polish, {polished: 'Fixture polished A–B manuscript preserving the reviewed answer.'})
        self.assertEqual(D.completed(P.load(self.phase), 'final-expression')['capability'], 'final-expression')

    def test_new_writing_invalidates_citation_revision_from_older_draft(self):
        writing, _ = self.manuscript()
        original = Path(P.load(writing[1])['outputs'][0]['path'])
        cited = self.root / 'manuscript-v2-cited.md'
        self.step('citation-audit', {cited: 'Fixture citation correction of the earlier A–B draft.'},
                  inputs=[original])
        self.assertEqual(D.completed(P.load(self.phase), 'citation-audit')['capability'], 'citation-audit')
        change = self.root / 'writing-revision.md'; change.write_text('Fixture substantive explanation revision.')
        inputs = [Path(x['path']) for x in P.load(writing[0])['inputs']] + [change]
        self.step('manuscript-writing', {self.root / 'manuscript-v3.md': 'Fixture revised A–B argument.'},
                  inputs=inputs)
        with self.assertRaises(D.DataError): D.completed(P.load(self.phase), 'citation-audit')
        with self.assertRaises(D.DataError): self.begin('manuscript-review', [cited])

    def test_presentation_steering_invalidates_only_text_work(self):
        writing, review = self.manuscript(); state = P.load(self.phase)
        starts = [writing[0], review[0]]; finishes = [writing[1], review[1]]
        self.assertEqual(len(P.professional_exit(state, starts, finishes)), 2)
        P.update_instruction(state, 'Write the paper in Chinese.', 'presentation'); P.save(self.phase, state)
        for cap in ('data-preparation', 'analysis-execution', 'scientific-visualization'):
            self.assertEqual(D.completed(state, cap)['capability'], cap)
        self.assertTrue(R._results(state)['result_refs'])
        with self.assertRaises(F.FlowError): F.validate_start(self.idx, P.load(review[0]))
        with self.assertRaises((D.DataError, F.FlowError)): D.completed(state, 'manuscript-review')
        with self.assertRaises(P.PhaseError): P.professional_exit(state, starts, finishes)

    def test_unknown_or_retargeted_work_cannot_replace_the_fixed_question(self):
        state = P.load(self.phase)
        with self.assertRaises(R.CommitmentError):
            W.route(state, 'main', 'C–D', 'Test C–D', [self.material], self.root, question_ids=['Q999'])
        W.route(state, 'main', 'A–B', 'Test A–B', [self.material], self.root, question_ids=['Q1'])
        with self.assertRaises(P.PhaseError):
            W.route(state, 'main', 'Different test', 'Test subgroup', [self.material], self.root, question_ids=['Q2'])
        with self.assertRaises(R.CommitmentError):
            self.begin('data-preparation', [self.material], question_ids=['Q999'])

    def test_cli_full_requires_a_commitment_before_leaving_feasibility(self):
        fresh = self.root / 'fresh-phase.json'
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(P.main(['--state', str(fresh), 'init', '--scope', 'full',
                                     '--objective', 'A–B question']), 0)
        state = P.load(fresh); self.assertTrue(state['alignment_required'])
        with self.assertRaises(P.PhaseError):
            P.advance(state, 'design', self.material, self.root, 'Do research')
        self.assertEqual(state['stage'], 'feasibility')

    def test_failed_or_inconclusive_execution_cannot_complete_original_question(self):
        self.research(); _, index = self.answers(answer='inconclusive', execution='failed', outcome='inconclusive')
        state = P.load(self.phase)
        with self.assertRaises(R.CommitmentError): R.bind_results(state, self.root, self.planfile, index)
        before = state['budget_anchor']
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = P.main(['--state', str(self.phase), 'close', '--status', 'completed',
                '--reason', 'All files delivered', '--evidence', self.material.name,
                '--root', str(self.root), '--task-id', 'paper'])
        self.assertEqual(rc, 2); state = P.load(self.phase)
        self.assertEqual(state['status'], 'active'); self.assertEqual(state['budget_anchor'], before)

    def test_zero_or_refuting_formal_results_can_be_indexed_without_optional_work(self):
        self.research(); result, index = self.answers()
        state = P.load(self.phase); bound = R.bind_results(state, self.root, self.planfile, index)
        self.assertEqual(bound['result_refs'], [R._ref(self.root, result)])
        self.assertEqual(R.snapshot(state)['questions'][0]['answer_state'], 'answered')
        self.assertEqual(R.snapshot(state)['questions'][1]['answer_state'], 'unanswered')

    def test_compact_resume_keeps_every_question_despite_newer_explorations(self):
        self.research(); self.answers(answer='inconclusive', outcome='inconclusive')
        state = P.load(self.phase)
        for number in range(8):
            W.checkpoint(state, 'side-' + str(number), 'Optional exploration ' + str(number),
                'Return to Q1 decisive test', [self.material], self.root,
                question_ids=['Q2'], kind='exploration', purpose='diagnostic')
            state['artifacts'].append(P.artifact(self.material, self.root))
        focus = P.resume(state, compact=True)['research_focus']
        self.assertEqual([q['id'] for q in focus['questions']], ['Q1', 'Q2'])
        self.assertEqual(focus['relationship'], 'A–B relationship')
        self.assertEqual(focus['questions'][0]['answer_state'], 'inconclusive')
        self.assertIn('Q1', focus['questions'][0]['next_action'])


if __name__ == '__main__': unittest.main()
