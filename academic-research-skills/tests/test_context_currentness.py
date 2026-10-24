"""Actual receipt/recovery regressions; isolated fixtures do not certify science."""
import collections
import contextlib
import copy
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import test_research_commitment as fixtures

R, P, F, A = fixtures.R, fixtures.P, fixtures.F, fixtures.A
import work_units as W
import research_storage as S


class Currentness(unittest.TestCase):
    def setUp(self):
        self.t = fixtures.ResearchCommitment()
        self.t.setUp()
        self.addCleanup(self.t.tearDown)

    def cli(self, module, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = module.main([str(x) for x in args])
        return code, stdout.getvalue(), stderr.getvalue()

    def two_experiments(self):
        t = self.t
        t.spec = copy.deepcopy(t.spec)
        t.spec['primary_experiments'].append(dict(id='E2', question_ids=['Q1'], purpose='Sensitivity estimate'))
        t.state = P.init('full', 'Study A and B', autonomous_plan=True)
        R.bind(t.state, t.root, t.json('two-tests.json', t.spec), t.request, t.brief, t.request.read_text())
        P.save(t.phase, t.state)

    def method_revision(self, eid='E1'):
        t = self.t
        spec = copy.deepcopy(t.spec)
        next(e for e in spec['primary_experiments'] if e['id'] == eid)['method'] = 'Repaired estimator'
        R.bind(t.state, t.root, t.json('method-revision.json', spec), t.request, t.brief,
               t.request.read_text(), implementation_reason='Repair the affected estimator after a pilot')
        P.save(t.phase, t.state)

    def science_revision(self):
        t = self.t
        spec = copy.deepcopy(t.spec); spec['relationship'] = 'causal effect'
        request = t.write('new-user-request.md', 'Change the target to the causal effect of A on B.')
        R.bind(t.state, t.root, t.json('science-revision.json', spec), request, t.brief,
               request.read_text(), science_revision=True, revision_reason='Actual new user instruction')
        P.save(t.phase, t.state)

    def start(self, **kwargs):
        t = self.t; P.save(t.phase, t.state)
        begun = F.begin(t.idx, 'analysis-execution', t.request, [t.brief], t.cache,
                        phase=t.phase, question_ids=['Q1'], **kwargs)
        path = t.root / ('analysis-' + str(len(t.state['professional_pending'])) + '-start.json')
        F.persist(begun, path); t.state = P.load(t.phase)
        return begun, path

    def output(self, begun):
        t = self.t
        output = t.write('old-estimator-result.json', '{"estimate": 0.0, "method": "original"}')
        report = t.json('old-estimator-work.json', dict(step_id=begun['id'], scope='requested_step',
            omitted_required_work=[], functions_run=False, actions=[dict(source_file='SKILL.md',
            source_excerpt=t.guide, applied='Computed the estimator selected at begin.',
            output=str(output), output_excerpt=output.read_text())]))
        return output, report

    def steer_presentation(self):
        t = self.t
        P.update_instruction(t.state, 'Write the paper in Chinese.', 'presentation')
        P.save(t.phase, t.state)

    def test_new_language_invalidates_direct_closure_and_delivery(self):
        t = self.t; parts = t.delivery(); t.attach(parts)
        self.steer_presentation()
        with self.assertRaises(ValueError): R.closure(t.state)
        with self.assertRaises(ValueError): t.attach(parts)
        self.assertTrue(R._results(t.state)['result_refs'])
        # Old receipts retain their historical file identity.
        self.assertEqual(F.check(t.idx, P.load(parts[2]), P.load(parts[3]))['status'], 'eligible_for_handoff')

    def test_cli_rejects_old_delivery_without_writing_state(self):
        t = self.t; parts = t.delivery(); t.attach(parts); self.steer_presentation()
        before = t.phase.read_bytes()
        code, _, error = self.cli(R, ['--state', t.phase, 'check'])
        self.assertEqual(code, 2, error); self.assertEqual(t.phase.read_bytes(), before)

    def test_new_language_invalidates_cached_review(self):
        t = self.t; parts = t.delivery()
        W.review_record(t.state, 'paper', [parts[0]], t.root, parts[2], parts[3])
        self.steer_presentation()
        self.assertFalse(W.review_status(t.state, 'paper', [parts[0]], t.root)['reusable'])
        code, output, error = self.cli(W, ['--state', t.phase, 'review-status', '--key', 'paper',
                                          '--root', t.root, '--evidence', parts[0]])
        self.assertEqual(code, 0, error); self.assertFalse(json.loads(output)['reusable'])

    def test_progress_request_preserves_review_and_delivery(self):
        t = self.t; parts = t.delivery(); t.attach(parts)
        W.review_record(t.state, 'paper', [parts[0]], t.root, parts[2], parts[3])
        P.update_instruction(t.state, 'Please report progress.', 'operational'); P.save(t.phase, t.state)
        self.assertTrue(W.review_status(t.state, 'paper', [parts[0]], t.root)['reusable'])
        self.assertEqual(R.closure(t.state)['required_questions'], 1)

    def test_method_change_rejects_finish_and_persist(self):
        t = self.t; begun, _ = self.start(); output, report = self.output(begun)
        done = F.finish(t.idx, begun, [output], report, 'adapted_in_host')
        self.method_revision()
        with self.assertRaises(ValueError): F.finish(t.idx, begun, [output], report, 'adapted_in_host')
        path = t.root / 'stale-finish.json'
        with self.assertRaises(ValueError): F.persist(done, path, begun)
        self.assertFalse(path.exists())

    def test_method_change_prevents_cli_process_launch(self):
        t = self.t; _, start = self.start(); self.method_revision()
        marker = t.root / 'must-not-run'
        code, _, error = self.cli(P, ['--state', t.phase, 'run', '--log', t.root / 'run.log',
            '--claim', 'Test A–B', '--decision', 'Estimate the relationship', '--professional-started', start,
            '--', sys.executable, '-c', 'from pathlib import Path; Path(' + repr(str(marker)) + ').touch()'])
        self.assertEqual(code, 2, error); self.assertFalse(marker.exists())

    def test_method_change_blocks_stage_exit_with_old_step(self):
        t = self.t; t.result(); self.method_revision()
        rows = [x for x in t.state['professional_pending'] if x['status'] == 'completed']
        with self.assertRaises(ValueError):
            P.professional_exit(t.state, [x['started'] for x in rows], [x['finished'] for x in rows])

    def test_explicit_experiment_scope_preserves_unaffected_running_step(self):
        self.two_experiments(); t = self.t
        begun, _ = self.start(experiment_ids=['E1']); self.method_revision('E2')
        output, report = self.output(begun)
        done = F.finish(t.idx, begun, [output], report, 'adapted_in_host')
        F.persist(done, t.root / 'unchanged-e1-finish.json', begun)
        self.assertEqual(done['status'], 'completed_for_handoff')

    def test_legacy_step_uses_question_scope_conservatively(self):
        self.two_experiments(); t = self.t; begun, _ = self.start()
        # v3.5.5 receipts have the full fingerprint map but no explicit scope.
        begun['phase'].pop('experiment_ids', None)
        self.method_revision('E2'); output, report = self.output(begun)
        with self.assertRaises(ValueError): F.finish(t.idx, begun, [output], report, 'adapted_in_host')

    def test_cli_accepts_repeated_experiment_ids(self):
        self.two_experiments(); t = self.t; path = t.root / 'cli-start.json'
        code, _, error = self.cli(F, ['--index', t.index, 'begin', '--capability', 'analysis-execution',
            '--task', t.request, '--input', t.brief, '--cache', t.cache, '--phase', t.phase,
            '--question-id', 'Q1', '--experiment-id', 'E1', '--experiment-id', 'E2', '--out', path])
        self.assertEqual(code, 0, error)
        self.assertEqual(P.load(path)['phase']['experiment_ids'], ['E1', 'E2'])

    def test_unknown_or_unrelated_experiment_ids_are_rejected(self):
        t = self.t
        for ids in (['unknown'], []):
            with self.subTest(ids=ids), self.assertRaises(ValueError): self.start(experiment_ids=ids)
        spec=copy.deepcopy(t.spec)
        spec['questions'].append(dict(id='Q2',text='A distinct question',required=True))
        spec['primary_experiments'].append(dict(id='E2',question_ids=['Q2'],purpose='Test Q2'))
        t.state=P.init('full','Two questions',autonomous_plan=True)
        R.bind(t.state,t.root,t.json('separate-questions.json',spec),t.request,t.brief,t.request.read_text())
        with self.assertRaises(ValueError):self.start(experiment_ids=['E2'])

    def test_scoped_step_cannot_supply_another_experiments_results(self):
        self.two_experiments(); t=self.t
        begun,_=self.start(experiment_ids=['E1'])
        with self.assertRaises(ValueError):F.require_current(t.state,begun,experiment_ids=['E2'])

    def test_full_plan_step_invalidated_by_an_added_experiment(self):
        t=self.t
        begun=F.begin(t.idx,'research-design',t.request,[t.brief],t.cache,phase=t.phase,question_ids=['Q1'])
        spec=copy.deepcopy(t.spec)
        spec['primary_experiments'].append(dict(id='E2',question_ids=['Q1'],purpose='New required sensitivity'))
        R.bind(t.state,t.root,t.json('added-test.json',spec),t.request,t.brief,t.request.read_text(),implementation_reason='Add a required sensitivity test')
        P.save(t.phase,t.state)
        with self.assertRaises(ValueError):F.require_current(t.state,begun)

    def test_legacy_unscoped_step_invalidated_by_a_removed_experiment(self):
        self.two_experiments();t=self.t;begun,_=self.start()
        begun['phase'].pop('experiment_ids',None);begun['phase'].pop('whole_plan',None)
        spec=copy.deepcopy(t.spec);spec['primary_experiments'].pop()
        R.bind(t.state,t.root,t.json('removed-test.json',spec),t.request,t.brief,t.request.read_text(),implementation_reason='Remove the redundant method while preserving Q1')
        P.save(t.phase,t.state)
        with self.assertRaises(ValueError):F.require_current(t.state,begun)

    def test_source_preparation_and_begin_persistence_recheck_revision(self):
        t=self.t
        begun=F.begin(t.idx,'analysis-execution',t.request,[t.brief],t.cache,phase=t.phase,question_ids=['Q1'])
        self.method_revision()
        with self.assertRaises(ValueError):F.persist(begun,t.root/'stale-begin.json')
        prepare=fixtures.C.prepare
        def revise_during_preparation(*args,**kwargs):
            spec=copy.deepcopy(t.spec);spec['primary_experiments'][0]['method']='Third estimator'
            R.bind(t.state,t.root,t.json('third-method.json',spec),t.request,t.brief,t.request.read_text(),implementation_reason='A new pilot exposed the remaining defect')
            P.save(t.phase,t.state)
            return prepare(*args,**kwargs)
        with patch.object(fixtures.C,'prepare',side_effect=revise_during_preparation):
            with self.assertRaises(ValueError):
                F.begin(t.idx,'analysis-execution',t.request,[t.brief],t.cache,phase=t.phase,question_ids=['Q1'])

    def test_new_review_can_complete_delivery_after_language_change(self):
        t=self.t;t.state['stage']='manuscript';parts=t.delivery();t.attach(parts)
        pending=t.state['professional_pending']
        checked=P.professional_exit(t.state,[x['started'] for x in pending],[x['finished'] for x in pending])
        P.advance(t.state,'delivery',t.brief,t.root,'Deliver the reviewed manuscript')
        P.consume_professional(t.state,checked);self.steer_presentation()
        P.reassess(t.state,t.brief,t.root,'Revise the requested language',stage='manuscript')
        manuscript,coverage=t.paper('revised-language.md')
        row=t.state['research_commitment'];inputs=[t.root/row['record']['path'],t.plan,t.resultindex,t.resultfile,manuscript,coverage]
        start,finish=t.source_step('manuscript-review',inputs,{t.root/'new-review.json':json.dumps(t.report())})
        R.bind_delivery(t.state,t.root,t.plan,t.resultindex,manuscript,coverage,start,finish)
        checked=P.professional_exit(t.state,[start],[finish])
        P.advance(t.state,'delivery',t.brief,t.root,'Deliver the revised manuscript')
        P.consume_professional(t.state,checked);P.save(t.phase,t.state)
        self.assertEqual(P.professional_exit(t.state,[],[]),[])
        self.assertEqual(R.closure(t.state)['required_questions'],1)

    def test_delivery_exit_cannot_fall_back_to_unchanged_scientific_support(self):
        t=self.t;t.state['stage']='manuscript';parts=t.delivery();t.attach(parts)
        pending=t.state['professional_pending']
        checked=P.professional_exit(t.state,[x['started'] for x in pending],[x['finished'] for x in pending])
        P.advance(t.state,'delivery',t.brief,t.root,'Deliver the reviewed manuscript')
        P.consume_professional(t.state,checked);self.steer_presentation()
        with self.assertRaises(P.PhaseError):P.professional_exit(t.state,[],[])

    def test_unscoped_exploration_remains_visible_in_current_science(self):
        t=self.t
        W.checkpoint(t.state,'side','Optional exploration','Inspect optional evidence',[t.brief],t.root,
                     question_ids=[],kind='exploration',purpose='diagnostic')
        self.assertEqual(P.resume(t.state,compact=True)['current_work']['key'],'side')

    def test_method_change_preserves_unchanged_data_preparation(self):
        t=self.t
        t.idx['professional_routes']['data-preparation']=copy.deepcopy(t.idx['professional_routes']['research-design'])
        P.save(t.index,t.idx)
        start,finish=t.source_step('data-preparation',[t.brief],{t.root/'prepared.csv':'a,b\n1,2\n3,4\n'})
        self.method_revision()
        begun=P.load(start);F.require_current(t.state,begun)
        # Old v3.5.5 preparation receipts also remain reusable with unchanged inputs.
        begun['phase'].pop('experiment_ids',None)
        F.require_current(t.state,begun)
        self.assertEqual(F.check(t.idx,P.load(start),P.load(finish))['status'],'eligible_for_handoff')

    def test_science_revision_removes_old_work_from_recovery_and_preserves_limits(self):
        t = self.t
        quota=S.plan(t.root,dict(needs=[dict(purpose='Fixed study',subset='Small local tables',access='Fixture files')],
                                expected_download_bytes=1000,expected_peak_project_bytes=1_000_000))
        ledger=S.read(t.root);ledger['downloaded_bytes']=123;S.save(t.root,ledger)
        t.state['storage']=dict(root=str(t.root),id=ledger['id'])
        quota_before=(t.root/S.NAME).read_bytes()
        W.checkpoint(t.state, 'old-test', 'Estimate observational association', 'Run old fit',
                     [t.brief], t.root, question_ids=['Q1'], experiment_id='E1')
        W.route(t.state, 'old-route', 'Estimate observational association', 'Run old fit',
                [t.brief], t.root, question_ids=['Q1'])
        self.start(); old = copy.deepcopy(t.state)
        self.science_revision()
        snapshot = P.resume(t.state, compact=True)
        self.assertIsNone(snapshot['current_work']); self.assertEqual(snapshot['ready_routes'], [])
        self.assertNotEqual(snapshot['next_action'], 'Run old fit')
        self.assertEqual(snapshot['professional_pending_count'], 0)
        self.assertEqual(t.state['professional_pending'][0]['status'], 'cancelled')
        self.assertIn('old-test', t.state['work_units']); self.assertIn('old-route', t.state['routes'])
        for key in ('started_at', 'project_deadline', 'deadline', 'budget_anchor', 'meter', 'storage'):
            self.assertEqual(old.get(key), t.state.get(key), key)
        self.assertEqual(t.state['status'], 'active')
        self.assertEqual((t.root/S.NAME).read_bytes(),quota_before)
        with self.assertRaises(P.PhaseError): W.validate_route_exit(t.state)
        P.reassess(t.state, t.brief, t.root, 'Update the new scientific design', stage='feasibility')
        self.assertEqual(t.state['status'], 'active')

    def test_failed_old_routes_cannot_close_new_science(self):
        t = self.t
        W.route(t.state, 'old-failed', 'Old association route', 'Run old fit', [t.brief], t.root,
                status='failed', question_ids=['Q1'])
        self.science_revision()
        with self.assertRaises(P.PhaseError): W.validate_route_exit(t.state)
        W.route(t.state, 'new-failed', 'New causal route', 'Test identification', [t.brief], t.root,
                status='failed', question_ids=['Q1'])
        self.assertEqual(W.validate_route_exit(t.state)['candidate_count'], 1)

    def test_read_only_recovery_filters_preexisting_stale_pointers(self):
        t = self.t
        W.checkpoint(t.state, 'old-test', 'Old relationship', 'Old action', [t.brief], t.root,
                     question_ids=['Q1'], experiment_id='E1')
        W.route(t.state, 'old-route', 'Old relationship', 'Old action', [t.brief], t.root, question_ids=['Q1'])
        self.science_revision()
        # Also handle old serialized states written before the fix.
        t.state.update(current_unit='old-test', next_action='Old action')
        before = copy.deepcopy(t.state); snap = P.resume(t.state, compact=True)
        self.assertIsNone(snap['current_work']); self.assertEqual(snap['ready_routes'], [])
        self.assertNotEqual(snap['next_action'], 'Old action'); self.assertEqual(t.state, before)

    def test_snapshot_hashes_each_commitment_file_once_independent_of_experiment_count(self):
        t = self.t; counts = []
        for n in (1, 8):
            spec = copy.deepcopy(t.spec)
            for i in range(2, n + 1):
                spec['questions'].append(dict(id='Q' + str(i), text='Question ' + str(i), required=True))
                spec['primary_experiments'].append(dict(id='E' + str(i), question_ids=['Q' + str(i)], purpose='Required test'))
            state = P.init('full', 'Recovery scaling', autonomous_plan=True)
            R.bind(state, t.root, t.json('scaling-' + str(n) + '.json', spec), t.request, t.brief, t.request.read_text())
            for i in range(n):
                W.checkpoint(state,'unit-'+str(i),'Current test '+str(i),'Continue test '+str(i),[t.brief],t.root,
                             question_ids=['Q1'],experiment_id='E1')
                W.route(state,'route-'+str(i),'Current route '+str(i),'Run route '+str(i),[t.brief],t.root,question_ids=['Q1'])
            with patch.object(A, 'digest', wraps=A.digest) as digest:
                with patch.object(R,'_experiment_fingerprints',wraps=R._experiment_fingerprints) as fingerprints:
                    P.resume(state, compact=True)
            self.assertEqual(fingerprints.call_count,1)
            per_file = collections.Counter(str(x.args[0]) for x in digest.call_args_list)
            self.assertTrue(all(count == 1 for count in per_file.values()), per_file)
            counts.append(digest.call_count)
        self.assertEqual(counts[0], counts[1])


if __name__ == '__main__': unittest.main()
