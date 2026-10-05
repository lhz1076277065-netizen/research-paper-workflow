"""Actual command/artifact binding scenarios; fixtures do not prove science."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import professional_flow as F
import capabilities as C
import provider_runtime as B
import phase_control as P

class Step(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.task=self.root/'request.md';self.task.write_text('Software fixture: compare actual options within supplied scope.')
        self.input=self.root/'input.md';self.input.write_text('Software fixture observations, no scientific claim.')
        self.guide=b'Compare plausible options against the actual constraints and decisive test.'
        c=dict(id='fixture',repository='owner/repo',commit='a'*40,tree='b'*40,
            entry='SKILL.md',kind='skill_protocol',roles=['ideation'],dependencies=[],
            host_adaptation='Fixture host protocol',required_files=[dict(path='SKILL.md',blob=C.blob(self.guide))])
        self.idx={'capabilities':[c],'professional_routes':{'topic-novelty':dict(primary='fixture',alternatives=[],work='Compare options',boundary='Fixture only')}}
        self.cache=self.root/'cache';p=self.cache/'fixture'/('a'*40)/'SKILL.md';p.parent.mkdir(parents=True);p.write_bytes(self.guide)
    def tearDown(self):self.tmp.cleanup()
    def begin(self):return F.begin(self.idx,'topic-novelty',self.task,[self.input],self.cache)
    def complete(self,start=None):
        start=start or self.begin();out=self.root/'result.md';out.write_text('Software fixture: option A requires fewer independent units than option B.')
        report=self.root/'work.json';report.write_text(json.dumps(dict(step_id=start['id'],scope='requested_step',omitted_required_work=[],functions_run=False,
            actions=[dict(source_file='SKILL.md',source_excerpt=self.guide.decode(),applied='Compared supplied constraints; no inferred measurements.',output=str(out),output_excerpt=out.read_text())])))
        return start,F.finish(self.idx,start,[out],report,'adapted_in_host'),out,report
    def test_default_begin_reads_real_source_before_work(self):
        r=self.begin();self.assertEqual(r['source']['id'],'fixture');self.assertEqual(r['guide'],self.guide.decode());self.assertFalse(r['professional_work_done'])
    def test_unmatched_source_cannot_be_selected(self):
        with self.assertRaises(F.FlowError):F.begin(self.idx,'topic-novelty',self.task,[self.input],self.cache,'unrelated')
    def test_missing_offline_source_blocks_without_fallback(self):
        with self.assertRaises(C.CapabilityError):F.begin(self.idx,'topic-novelty',self.task,[self.input],self.root/'missing')
    def test_preparation_only_cannot_pass(self):
        s=self.begin()
        with self.assertRaises(F.FlowError):F.check(self.idx,s,s['source'])
    def test_bound_output_passes_and_remains_semantically_unverified(self):
        s,r,_,_=self.complete();self.assertEqual(F.check(self.idx,s,r)['status'],'eligible_for_handoff');self.assertFalse(r['semantic_work_verified_by_tool'])
    def test_new_input_invalidates_completion(self):
        s,r,_,_=self.complete();self.input.write_text('New materials')
        with self.assertRaises(F.FlowError):F.check(self.idx,s,r)
    def test_task_scope_change_invalidates_completion(self):
        s,r,_,_=self.complete();self.task.write_text('A different requested scope')
        with self.assertRaises(F.FlowError):F.check(self.idx,s,r)
    def test_output_edit_invalidates_completion(self):
        s,r,out,_=self.complete();out.write_text('Unreviewed changed result')
        with self.assertRaises(F.FlowError):F.check(self.idx,s,r)
    def test_different_step_receipt_is_rejected(self):
        s,r,_,_=self.complete();r['step_id']='another'
        with self.assertRaises(F.FlowError):F.check(self.idx,s,r)
    def test_output_predating_invocation_is_rejected(self):
        out=self.root/'old.md';out.write_text('Old unrelated work');s=self.begin();_,r,_,report=self.complete(s)
        with self.assertRaises(F.FlowError):F.finish(self.idx,s,[out],report,'adapted_in_host')
    def test_unrelated_function_does_not_complete_professional_work(self):
        s,r,out,report=self.complete()
        with self.assertRaises(F.FlowError):F.finish(self.idx,s,[out],report,'function_only')
    def test_fake_source_action_does_not_complete_work(self):
        s,r,out,report=self.complete();d=json.loads(report.read_text());d['actions'][0]['source_excerpt']='Not in the selected guide';report.write_text(json.dumps(d))
        with self.assertRaises(F.FlowError):F.finish(self.idx,s,[out],report,'adapted_in_host')
    def test_action_not_in_current_output_is_rejected(self):
        s,r,out,report=self.complete();d=json.loads(report.read_text());d['actions'][0]['output_excerpt']='An unrelated result from another test';report.write_text(json.dumps(d))
        with self.assertRaises(F.FlowError):F.finish(self.idx,s,[out],report,'adapted_in_host')
    def test_partial_work_is_not_claimed_complete(self):
        s,r,out,report=self.complete();d=json.loads(report.read_text());d['omitted_required_work']=['comparison'];report.write_text(json.dumps(d))
        with self.assertRaises(F.FlowError):F.finish(self.idx,s,[out],report,'adapted_in_host')
    def test_binary_artifact_binding(self):
        s=self.begin();out=self.root/'chart.bin';out.write_bytes(b'\xff\x00fixture');report=self.root/'work.json'
        report.write_text(json.dumps(dict(step_id=s['id'],scope='requested_step',omitted_required_work=[],actions=[dict(source_file='SKILL.md',source_excerpt=self.guide.decode(),applied='Rendered fixture and checked labels.',output=str(out),output_sha256=F.ref(out)['sha256'],observation='Fixture labels were examined at final size.')])))
        r=F.finish(self.idx,s,[out],report,'adapted_in_host');self.assertEqual(F.check(self.idx,s,r)['status'],'eligible_for_handoff')
    def test_source_drift_is_not_silently_repaired(self):
        s=self.begin();Path(s['source']['entry']).write_text('changed source')
        with self.assertRaises(C.CapabilityError):F.validate_start(self.idx,s)
    def test_restored_begin_can_be_checked_without_restart(self):
        s,r,_,_=self.complete();serialized=json.loads(json.dumps(s));self.assertEqual(F.check(self.idx,serialized,r)['step_id'],s['id'])
    def test_phase_cli_refuses_unsupported_exit(self):
        state=self.root/'phase.json';P.save(state,P.init('full','Fixture phase'))
        command=[sys.executable,str(ROOT/'scripts/phase_control.py'),'--state',str(state),'advance','--stage','design','--evidence','input.md','--root',str(self.root),'--next-action','next']
        result=subprocess.run(command,capture_output=True,text=True);self.assertEqual(result.returncode,2);self.assertEqual(P.load(state)['stage'],'feasibility')
    def bound_phase(self):
        state=P.init('full','Fixture source-bound feasibility');path=self.root/'phase.json';P.save(path,state)
        s=F.begin(self.idx,'topic-novelty',self.task,[self.input],self.cache,phase=path)
        return state,path,s
    def test_phase_accepts_actual_bound_step_and_rejects_cross_phase_reuse(self):
        state,path,s=self.bound_phase();s,r,_,_=self.complete(s)
        start=self.root/'started.json';start.write_text(json.dumps(s));finish=self.root/'finished.json';finish.write_text(json.dumps(r));index=self.root/'index.json';index.write_text(json.dumps(self.idx))
        with patch.object(C,'index_path',return_value=index):steps=P.professional_exit(state,[start],[finish])
        self.assertEqual(steps[0]['step_id'],s['id']);state['professional_steps']=steps;P.advance(state,'design','input.md',self.root,'budget');P.authorize(state,10,'Fixture authorization');P.save(path,state)
        self.assertEqual(F.check(self.idx,s,r)['status'],'eligible_for_handoff')
        with patch.object(C,'index_path',return_value=index):
            with self.assertRaises(P.PhaseError):P.professional_exit(state,[start],[finish])
    def test_pause_prevents_new_completion_without_destroying_previous_records(self):
        state,path,s=self.bound_phase();s,r,out,report=self.complete(s);state['status']='paused';P.save(path,state)
        self.assertEqual(F.check(self.idx,s,r)['status'],'eligible_for_handoff')
        with self.assertRaises(F.FlowError):F.finish(self.idx,s,[out],report,'adapted_in_host')
    def test_instruction_change_blocks_unfinished_step(self):
        state,path,s=self.bound_phase();state['latest_instruction']='Different fixed question';P.save(path,state)
        with self.assertRaises(F.FlowError):F.validate_start(self.idx,s)
    def test_cli_research_process_needs_source_begin_before_launch(self):
        state,path,_=self.bound_phase();stamp=self.root/'launched'
        command=[sys.executable,str(ROOT/'scripts/phase_control.py'),'--state',str(path),'run','--log',str(self.root/'log'),'--claim','fixture','--decision','fixture','--',sys.executable,'-c',f'open({str(stamp)!r},"w").write("bad")']
        r=subprocess.run(command,capture_output=True);self.assertEqual(r.returncode,2);self.assertFalse(stamp.exists())
    def handoff(self):
        c=self.idx['capabilities'][0]
        provider=dict(id='fixture',repository=c['repository'],entrypoint='SKILL.md',required_paths=['SKILL.md'],
            entry_git_blob_sha=c['required_files'][0]['blob'],discovered_file_blob_sha={'SKILL.md':c['required_files'][0]['blob']},
            capabilities=['topic-novelty'],default_candidate=True,phase=1,mode='adapted-protocol',requires_host=[],requires_facts=[],purpose='Fixture source workflow',notes='Software fixture only',adaptations=['Local fixture'])
        registry=dict(providers=[provider],capabilities=['topic-novelty'],professional_source_policy='required_before_every_professional_step_no_host_fallback',professional_routes=self.idx['professional_routes'])
        directory=self.root/'handoff';task=dict(capability='topic-novelty',request='Fixture comparison',operation='review',requested_outputs=['report'])
        B.prepare_handoff(task,{'providers':{'fixture':{'root':str(self.cache/'fixture'/('a'*40))}}},registry,directory)
        s=F.begin(self.idx,'topic-novelty',directory/'task.json',[self.input],self.cache);s,r,out,report=self.complete(s)
        start=self.root/'start.json';finish=self.root/'finish.json';start.write_text(json.dumps(s));finish.write_text(json.dumps(r))
        result=dict(capability='topic-novelty',task_sha256=B.sha(directory/'task.json'),provider_id='fixture',execution_mode='adapted-protocol',execution_status='executed',
            professional_started=str(start),professional_finished=str(finish),outputs=[dict(role='report',path=out.name,sha256=B.sha(out))],reviews=[])
        return directory,result
    def accept_fixture(self,directory,result):
        # Inject fixture bytes at the index IO boundary; execute the actual receipt checks.
        loader=B.load
        def load(path):return self.idx if Path(path).name=='capability-index.json' else loader(path)
        with patch.object(B,'load',side_effect=load):return B.accept_result(directory,result,self.root)
    def test_handoff_accepts_actual_source_guided_current_output(self):
        d,r=self.handoff();result=self.accept_fixture(d,r);self.assertTrue(result['passed'],result['errors'])
    def test_handoff_rejects_a_substituted_generic_output(self):
        d,r=self.handoff();out=self.root/'other.md';out.write_text('Different output that did not follow the professional step')
        r['outputs']=[dict(role='report',path=out.name,sha256=B.sha(out))]
        result=self.accept_fixture(d,r);self.assertFalse(result['passed']);self.assertIn('Returned output was not produced by this professional step',result['errors'])

class Defaults(unittest.TestCase):
    def test_all_independent_specialists_have_real_routes_in_fourteen_repositories(self):
        idx=C.load(ROOT/'assets/capability-index.json');approved={x['repository'] for x in idx['capabilities']}
        self.assertEqual(len(approved),14)
        for skill in (ROOT/'skills').iterdir():
            if not skill.is_dir() or skill.name=='research-paper-workflow':continue
            route=idx['professional_routes'][skill.name]
            for uid in [route['primary']]+route.get('alternatives',[]):
                c=C.entry(idx,uid);self.assertIn(c['repository'],approved);self.assertIn(c['entry'],[f['path'] for f in c['required_files']])
    def test_legacy_planner_missing_source_is_blocked(self):
        reg=C.load(ROOT/'docs/provider-catalog.json')
        task={'capability':'topic-novelty','request':'Propose candidate topics','operation':'plan'}
        with tempfile.TemporaryDirectory() as td:
            config={'providers':{p['id']:{'root':td} for p in reg['providers']}}
            r=B.plan(task,config,reg);self.assertEqual(r['status'],'blocked_source_step');self.assertIsNone(r['fallback']);self.assertFalse(r['executed']);self.assertFalse(r['host_fallback_allowed'])
    def test_default_topic_planner_selects_actual_orchestra_without_manual_enable(self):
        reg=C.load(ROOT/'docs/provider-catalog.json');p=next(p for p in reg['providers'] if p['id']=='orchestra-ideation')
        with tempfile.TemporaryDirectory() as td:
            # Materialize a verified fixture cache; exercise real default resolution and inspection.
            home=Path(td);root=home/'.codex/academic-research-source-cache'/p['id']/p['commit']
            for rel in p['required_paths']:
                target=root/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('Synthetic source fixture '+rel)
                p['discovered_file_blob_sha'][rel]=B.blob(target)
            p['entry_git_blob_sha']=p['discovered_file_blob_sha'][p['entrypoint']]
            with patch.object(B.Path,'home',return_value=home):r=B.plan({'capability':'topic-novelty','request':'Propose topics','operation':'plan'},{},reg)
            self.assertEqual(r['selected_provider'],p['id']);self.assertFalse(r['executed'])

if __name__=='__main__':unittest.main()
