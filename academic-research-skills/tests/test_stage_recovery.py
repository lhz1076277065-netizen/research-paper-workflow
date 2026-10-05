"""Budget and interrupted workflow regressions using actual CLI outputs/files."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import phase_control as P
import capabilities as C

class Budget(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve()
  (self.root/'evidence.md').write_text('Existing evidence covers the requested descriptive claim; no extra study needed.')
 def tearDown(self):self.tmp.cleanup()
 def test_existing_total_authorization_preserves_time_and_token_baseline(self):
  s=P.init('full','bounded report',10,clock=0,authority='Actual user ten-minute total')
  P.set_meter(s,dict(input_tokens=100,cached_input_tokens=20,output_tokens=5),'host')
  P.set_meter(s,dict(input_tokens=300,cached_input_tokens=100,output_tokens=15),'host')
  before=copy.deepcopy(s['meter']);P.advance(s,'design','evidence.md',self.root,'minimal design',clock=20)
  self.assertEqual(s['status'],'active');self.assertEqual(s['stage'],'design');self.assertEqual(s['project_deadline'],600)
  self.assertEqual(s['meter'],before);self.assertEqual(P.usage_delta(s)['total_tokens'],210)
  with self.assertRaises(P.PhaseError):P.authorize(s,10,'same authorization again')
 def test_next_stage_does_not_inherit_previous_stage_deadline(self):
  s=P.init('full','goal',60,clock=0,authority='Actual total budget')
  P.advance(s,'design','evidence.md',self.root,'design',clock=0,minutes=1)
  self.assertEqual(s['deadline'],60)
  P.advance(s,'research','evidence.md',self.root,'test',clock=30)
  self.assertEqual(s['deadline'],3600);self.assertEqual(s['project_deadline'],3600)
  self.assertTrue(P.guard(s,estimated_seconds=120,clock=40)['allowed'])
 def test_existing_sufficient_evidence_goes_from_design_to_writing(self):
  s=P.init('full','goal',10,authority='Actual user total budget')
  P.advance(s,'design','evidence.md',self.root,'design')
  P.advance(s,'manuscript','evidence.md',self.root,'write',skip_reason='Supplied frozen data already support the limited descriptive claim')
  self.assertEqual(s['stage'],'manuscript');self.assertEqual(s['history'][-1]['skip_reason'],'Supplied frozen data already support the limited descriptive claim')
 def test_arbitrary_stage_skips_remain_rejected(self):
  s=P.init('full','goal',10,authority='Actual total budget')
  with self.assertRaises(P.PhaseError):P.advance(s,'delivery','evidence.md',self.root,'deliver',skip_reason='save time')
 def test_new_post_feasibility_token_budget_keeps_previous_usage_in_history(self):
  s=P.init('full','goal');P.set_meter(s,dict(input_tokens=100,cached_input_tokens=20,output_tokens=5),'host')
  P.set_meter(s,dict(input_tokens=300,cached_input_tokens=100,output_tokens=15),'host')
  P.advance(s,'design','evidence.md',self.root,'budget');P.authorize(s,10,'New actual authorization for subsequent work',1000)
  old=next(x for x in s['history'] if x['event']=='feasibility_usage')
  self.assertEqual(old['usage']['total_tokens'],210);self.assertEqual(old['meter_baseline']['input_tokens'],100)

class InterruptedFlow(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve()
  self.task=self.root/'request.md';self.task.write_text('Compare supplied options, software fixture only.')
  self.material=self.root/'material.md';self.material.write_text('Actual fixture option constraints.')
  self.guide='Compare plausible options against the supplied constraints and decisive test.'
  cap=dict(id='fixture',repository='owner/repo',commit='a'*40,tree='b'*40,entry='SKILL.md',kind='skill_protocol',roles=['ideation'],dependencies=[],host_adaptation='Fixture protocol',required_files=[dict(path='SKILL.md',blob=C.blob(self.guide.encode()))])
  self.index=self.root/'index.json';self.index.write_text(json.dumps(dict(capabilities=[cap],professional_routes={'topic-novelty':dict(primary='fixture',alternatives=[],work='Compare options',boundary='Fixture only')})))
  self.cache=self.root/'cache';entry=self.cache/'fixture'/('a'*40)/'SKILL.md';entry.parent.mkdir(parents=True);entry.write_text(self.guide)
  self.phase=self.root/'phase.json';P.save(self.phase,P.init('full','Fixture full flow',10,authority='Actual fixture total budget'))
  (self.root/'evidence.md').write_text('Fixture exit decision; requested material remains synthetic.')
 def tearDown(self):self.tmp.cleanup()
 def call(self,script,*args,code=0):
  p=subprocess.run([sys.executable,str(ROOT/'scripts'/script),*map(str,args)],capture_output=True,text=True,timeout=10)
  self.assertEqual(p.returncode,code,p.stdout+p.stderr)
  self.assertNotIn('Traceback',p.stderr)
  return json.loads(p.stdout if code==0 else p.stderr)
 def begin(self,name,material=None,code=0):
  return self.call('professional_flow.py','--index',self.index,'begin','--capability','topic-novelty','--task',self.task,'--input',material or self.material,'--cache',self.cache,'--phase',self.phase,'--out',self.root/(name+'-start.json'),code=code)
 def finish(self,name,code=0):
  start=C.load(self.root/(name+'-start.json'));out=self.root/(name+'.md');out.write_text('Fixture result: option A fits the supplied constraints better than option B.')
  work=self.root/(name+'-work.json');work.write_text(json.dumps(dict(step_id=start['id'],scope='requested_step',omitted_required_work=[],actions=[dict(source_file='SKILL.md',source_excerpt=self.guide,applied='Compared fixture options within supplied scope.',output=str(out),output_excerpt=out.read_text())])))
  return self.call('professional_flow.py','--index',self.index,'finish','--started',self.root/(name+'-start.json'),'--output',out,'--work-report',work,'--out',self.root/(name+'-finish.json'),code=code)
 def test_resume_records_active_step_and_completed_output_without_restart(self):
  r=self.begin('one');state=P.load(self.phase);pending=P.resume(state)['professional_pending']
  self.assertEqual(pending[0]['step_id'],r['id']);self.assertEqual(pending[0]['started'],str(self.root/'one-start.json'))
  self.finish('one');pending=P.resume(P.load(self.phase))['professional_pending'];self.assertEqual(pending[0]['finished'],str(self.root/'one-finish.json'))
  self.call('professional_flow.py','--index',self.index,'check','--started',self.root/'one-start.json','--finished',self.root/'one-finish.json')
 def test_duplicate_task_reuses_receipt_instead_of_silent_restart(self):
  self.begin('one');r=self.begin('duplicate',code=2)
  self.assertIn('resume/check',r['error']);self.assertFalse((self.root/'duplicate-start.json').exists());self.assertEqual(len(P.load(self.phase)['professional_pending']),1)
 def test_stage_exit_cannot_omit_a_started_step(self):
  self.begin('one');other=self.root/'other.md';other.write_text('A different current fixture constraint set.')
  self.begin('two',other);self.finish('one');state=P.load(self.phase)
  from unittest.mock import patch
  with patch.object(C,'index_path',return_value=self.index):
   with self.assertRaises(P.PhaseError):P.professional_exit(state,[self.root/'one-start.json'],[self.root/'one-finish.json'])
  self.finish('two');state=P.load(self.phase)
  with patch.object(C,'index_path',return_value=self.index):steps=P.professional_exit(state,[self.root/'one-start.json',self.root/'two-start.json'],[self.root/'one-finish.json',self.root/'two-finish.json'])
  P.advance(state,'design','evidence.md',self.root,'design');P.consume_professional(state,steps)
  self.assertEqual(len(state['professional_steps']),2);self.assertEqual(state['professional_pending'],[])
 def test_pause_and_actual_resume_preserve_original_budget_and_unfinished_step(self):
  self.begin('one');before=P.load(self.phase)
  self.call('phase_control.py','--state',self.phase,'close','--status','paused','--reason','Actual user pause','--evidence','evidence.md','--root',self.root,'--task-id','fixture')
  self.begin('blocked',code=2);self.assertFalse((self.root/'blocked-start.json').exists())
  self.call('phase_control.py','--state',self.phase,'continue','--authority','Actual later user resume instruction')
  after=P.load(self.phase);self.assertEqual(after['project_deadline'],before['project_deadline']);self.assertEqual(after['professional_pending'],before['professional_pending'])
  self.finish('one')
 def test_expired_pause_cannot_renew_itself(self):
  s=P.load(self.phase);s.update(status='paused',deadline=0,project_deadline=0);P.save(self.phase,s)
  self.call('phase_control.py','--state',self.phase,'continue','--authority','Actual user resume without new budget',code=2)
  self.assertEqual(P.load(self.phase)['status'],'paused')
 def test_explicit_cancellation_preserves_evidence_and_does_not_complete_work(self):
  self.begin('one');self.call('phase_control.py','--state',self.phase,'cancel-step','--started',self.root/'one-start.json','--reason','User replaced the request','--evidence','evidence.md','--root',self.root)
  self.finish('one',code=2);pending=P.load(self.phase)['professional_pending'][0]
  self.assertEqual(pending['status'],'cancelled');self.assertIsNone(pending['finished']);self.assertFalse((self.root/'one-finish.json').exists())
 def test_malformed_work_report_is_a_bounded_error(self):
  self.begin('one');out=self.root/'result.md';out.write_text('Current fixture result has actual content.')
  report=self.root/'bad.json';report.write_text('[]')
  self.call('professional_flow.py','--index',self.index,'finish','--started',self.root/'one-start.json','--output',out,'--work-report',report,'--out',self.root/'bad-finish.json',code=2)
  self.assertFalse((self.root/'bad-finish.json').exists())
 def test_completion_after_total_deadline_is_recorded_as_limit(self):
  self.begin('one');self.finish('one');state=P.load(self.phase);state.update(deadline=0,project_deadline=0);P.save(self.phase,state)
  self.call('phase_control.py','--state',self.phase,'close','--status','completed','--reason','Fixture was saved late','--evidence','evidence.md','--root',self.root,'--task-id','fixture','--professional-started',self.root/'one-start.json','--professional-finished',self.root/'one-finish.json',code=2)
  state=P.load(self.phase);self.assertEqual(state['status'],'closed_limit');self.assertEqual(state['completed_tasks'],[])


class Routing(unittest.TestCase):
 def test_current_service_alias_can_select_verified_source(self):
  import provider_runtime as B
  registry=C.load(ROOT/'docs/provider-catalog.json')
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);provider=next(p for p in registry['providers'] if p['id']=='kdense-critical');root=base/'source';root.mkdir()
   for rel in provider['required_paths']:
    f=root/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('Actual software fixture guide: '+rel)
    provider['discovered_file_blob_sha'][rel]=B.blob(f)
   provider['entry_git_blob_sha']=provider['discovered_file_blob_sha'][provider['entrypoint']]
   result=B.plan(dict(capability='manuscript-review',service='review',profile='focused',operation='review',request='A bounded evidence checklist'),dict(providers={'kdense-critical':{'root':str(root)}}),registry)
   self.assertEqual(result['selected_provider'],'kdense-critical');self.assertEqual(result['status'],'prepared_not_executed')
   denied=B.plan(dict(capability='manuscript-review',service='unverified-service',profile='focused',operation='review',request='Fixture'),dict(providers={'kdense-critical':{'root':str(root)}}),registry)
   self.assertEqual(denied['status'],'blocked_source_step')
 def test_focused_source_resolution_preserves_profile_before_work(self):
  import professional_flow as F
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);task=root/'task.md';task.write_text('A limited evidence review');material=root/'material.md';material.write_text('Current supplied fixture manuscript')
   caps=[]
   for uid in ['full','focused']:
    guide=('Verified fixture '+uid+' professional guide.').encode();p=root/'cache'/uid/('a'*40)/'SKILL.md';p.parent.mkdir(parents=True);p.write_bytes(guide)
    caps.append(dict(id=uid,repository='owner/repo',commit='a'*40,tree='b'*40,entry='SKILL.md',kind='skill_protocol',roles=['review'],dependencies=[],host_adaptation='Fixture protocol',required_files=[dict(path='SKILL.md',blob=C.blob(guide))]))
   idx=dict(capabilities=caps,professional_routes={'manuscript-review':dict(primary='full',alternatives=['focused'],profiles={'focused':'focused','full':'full'},work='Read and review',boundary='Fixture only')})
   phase=root/'phase.json';P.save(phase,P.init('focused','bounded evidence review',10,authority='Actual fixture budget'))
   result=F.begin(idx,'manuscript-review',task,[material],root/'cache',phase=phase)
   self.assertEqual(result['source']['id'],'focused');self.assertIn('focused professional guide',result['guide']);self.assertFalse(result['professional_work_done'])
 def test_review_template_and_roles_are_required_source_files(self):
  idx=C.load(ROOT/'assets/capability-index.json');review=C.entry(idx,'academic-reviewer');files={x['path'] for x in review['required_files']}
  self.assertIn('academic-paper-reviewer/templates/peer_review_report_template.md',files)
  self.assertIn('academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md',files)

if __name__=='__main__':unittest.main()
