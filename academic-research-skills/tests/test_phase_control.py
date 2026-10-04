"""Executable phase scenarios: files/processes/usage, not keyword compliance."""
import importlib.util,json,subprocess,sys,tempfile,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'src/common/scripts'/ (name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
P=module('phase_control');C=module('capabilities')
class Phases(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'evidence.md').write_text('Actual scenario evidence; software fixture, not scientific evidence.')
 def tearDown(self):self.tmp.cleanup()
 def test_unbudgeted_feasibility_has_45_minute_exit(self):
  s=P.init('full','fixed user hypothesis',clock=0);self.assertEqual(s['project_deadline'],2700);self.assertFalse(P.guard(s,clock=2500)['allowed'])
 def test_maintenance_completion_survives_resume(self):
  state=self.root/'state.json';P.save(state,P.init('maintenance','install skill'))
  command=[sys.executable,str(ROOT/'src/common/scripts/phase_control.py'),'--state',str(state),'close','--status','completed','--reason','installation verified','--evidence','evidence.md','--root',str(self.root),'--task-id','installation-v340']
  self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
  s=P.load(state);r=P.resume(s);self.assertIn('installation-v340',r['completed_tasks']);self.assertFalse(P.guard(s)['allowed'])
  stamp=self.root/'installation-repeated'
  with self.assertRaises(P.PhaseError):P.run(state,[sys.executable,'-c',f'open({str(stamp)!r},"w").write("wrong")'],self.root/'run.log','maintenance','repeat')
  self.assertFalse(stamp.exists())
 def test_feasibility_does_not_automatically_authorize_research(self):
  s=P.init('full','hypothetical composition');P.advance(s,'design','evidence.md',self.root,'budget decision');self.assertEqual(s['status'],'awaiting_budget');self.assertFalse(P.guard(s)['allowed'])
 def test_authorization_requires_actual_meter_for_token_ceiling(self):
  s=P.init('full','goal');P.advance(s,'design','evidence.md',self.root,'next')
  with self.assertRaises(P.PhaseError):P.authorize(s,10,'user confirmed',40000)
 def test_stage_changes_and_repairs_preserve_budget(self):
  s=P.init('full','goal');P.advance(s,'design','evidence.md',self.root,'next');P.authorize(s,60,'user message')
  before=s['project_deadline'];P.repair(s,'missing library','configure path');P.advance(s,'research','evidence.md',self.root,'run',minutes=10)
  self.assertEqual(s['project_deadline'],before);self.assertLess(s['deadline'],before)
 def test_short_stage_uses_total_delivery_reserve_without_losing_its_own_runway(self):
  s=P.init('full','goal',clock=0);P.advance(s,'design','evidence.md',self.root,'next',clock=0);P.authorize(s,60,'user',clock=0);P.advance(s,'research','evidence.md',self.root,'small validation',clock=0,minutes=1)
  self.assertTrue(P.guard(s,estimated_seconds=30,clock=0)['allowed']);self.assertFalse(P.guard(s,estimated_seconds=61,clock=0)['allowed'])
 def test_same_failure_has_two_different_repairs_only(self):
  s=P.init('full','goal');P.repair(s,'missing library','path A')
  with self.assertRaises(P.PhaseError):P.repair(s,'missing library','path A')
  P.repair(s,'missing library','path B')
  with self.assertRaises(P.PhaseError):P.repair(s,'missing library','reinstall whole machine')
 def test_two_nonchanging_rounds_require_reassessment(self):
  s=P.init('full','goal');P.round_result(s,False,'evidence.md',self.root);P.round_result(s,False,'evidence.md',self.root)
  self.assertFalse(P.guard(s)['allowed']);self.assertTrue(s['reassessment_required'])
 def test_resume_preserves_exact_no_change_count_and_meter_baseline(self):
  s=P.init('full','goal');P.set_meter(s,dict(input_tokens=100,cached_input_tokens=10,output_tokens=2),'host');P.round_result(s,False,'evidence.md',self.root);P.round_result(s,False,'evidence.md',self.root);r=P.resume(s)
  self.assertEqual(r['unchanged_rounds'],2);self.assertEqual(r['meter']['baseline'],s['meter']['baseline']);self.assertEqual(r['reserve_seconds'],s['reserve_seconds'])
 def test_informative_round_resets_no_change_count(self):
  s=P.init('full','goal');P.round_result(s,False,'evidence.md',self.root);P.round_result(s,True,'evidence.md',self.root);self.assertEqual(s['unchanged_rounds'],0)
 def test_actual_delta_separates_cached_tokens(self):
  s=P.init('full','goal');P.set_meter(s,dict(input_tokens=1000,cached_input_tokens=800,output_tokens=100),'host')
  P.set_meter(s,dict(input_tokens=2000,cached_input_tokens=1700,output_tokens=130),'host')
  d=P.usage_delta(s);self.assertEqual(d['total_tokens'],1030);self.assertEqual(d['noncached_input_plus_output'],130)
 def test_usage_reset_cannot_erase_budget(self):
  s=P.init('full','goal');P.set_meter(s,dict(input_tokens=100,cached_input_tokens=10,output_tokens=2),'host')
  with self.assertRaises(P.PhaseError):P.set_meter(s,dict(input_tokens=50,cached_input_tokens=10,output_tokens=2),'host')
 def test_long_context_estimate_prevents_start_before_overshoot(self):
  s=P.init('full','goal');P.set_meter(s,dict(input_tokens=100,cached_input_tokens=10,output_tokens=2),'host');P.advance(s,'design','evidence.md',self.root,'next');P.authorize(s,60,'new budget',40000)
  self.assertFalse(P.guard(s,estimated_tokens=80583)['allowed']);self.assertEqual(s['status'],'active')
 def test_token_exhaustion_closes_phase(self):
  s=P.init('full','goal');P.set_meter(s,dict(input_tokens=100,cached_input_tokens=10,output_tokens=2),'host');P.advance(s,'design','evidence.md',self.root,'next');P.authorize(s,60,'user',100)
  P.set_meter(s,dict(input_tokens=210,cached_input_tokens=100,output_tokens=2),'host');P.enforce(s);self.assertEqual(s['status'],'closed_limit')
 def test_unreliable_token_meter_blocks_bounded_work(self):
  s=P.init('full','goal');s['token_limit']=40000;self.assertIn('token_meter_unavailable',P.guard(s)['reasons'])
 def test_incremental_rollout_meter_ignores_partial_write(self):
  s=P.init('full','goal');p=self.root/'rollout.jsonl';sample={'type':'token_usage_record','payload':{'thread_token_usage':dict(input_tokens=100,cached_input_tokens=10,output_tokens=2)}}
  text=json.dumps(sample);p.write_text(text+'\n'+text[:15]);P.meter_rollout(s,p);offset=s['meter']['offset'];self.assertEqual(offset,len(text.encode())+1)
  p.write_text(text+'\n'+json.dumps({'type':'token_usage_record','payload':{'thread_token_usage':dict(input_tokens=200,cached_input_tokens=110,output_tokens=5)}})+'\n');P.meter_rollout(s,p);self.assertEqual(P.usage_delta(s)['total_tokens'],103)
 def test_deadline_stops_real_child_and_no_duplicate_restart(self):
  p=self.root/'s.json';P.save(p,P.init('full','timed fixture',minutes=.004))
  r=P.run(p,[sys.executable,'-c','import time;time.sleep(30)'],self.root/'run.log','deadline stops child','cannot continue after budget')
  self.assertTrue(r['stop_reasons']);self.assertEqual(P.load(p)['owned_processes'],[]);self.assertEqual(P.load(p)['status'],'closed_limit')
  with self.assertRaises(P.PhaseError):P.run(p,[sys.executable,'-c','print(1)'],self.root/'again.log','x','y')
 def test_paused_state_does_not_launch_child_or_change_host_goal(self):
  s=P.init('full','goal');s['status']='paused';p=self.root/'s.json';P.save(p,s)
  with self.assertRaises(P.PhaseError):P.run(p,[sys.executable,'-c','print(1)'],self.root/'run.log','x','y')
  self.assertFalse((self.root/'run.log').exists());self.assertEqual(P.load(p)['host_goal_state'],'not_modified')
 def test_focused_edit_does_not_acquire_research_stages(self):
  s=P.init('focused','edit abstract')
  with self.assertRaises(P.PhaseError):P.advance(s,'design','evidence.md',self.root,'invent novelty')
 def test_counter_and_scope_survive_serialization(self):
  s=P.init('full','hypothesis, not historical reconstruction');s['latest_instruction']='do not rebuild history';P.repair(s,'compiler','path fix');p=self.root/'s.json';P.save(p,s);r=P.resume(P.load(p));self.assertEqual(r['latest_instruction'],'do not rebuild history');self.assertEqual(r['repairs']['compiler'],['path fix'])
 def test_existing_state_init_rejected(self):
  p=self.root/'s.json';P.save(p,P.init('full','goal'));r=subprocess.run([sys.executable,str(ROOT/'src/common/scripts/phase_control.py'),'--state',str(p),'init','--scope','full','--objective','reset'],capture_output=True)
  self.assertEqual(r.returncode,2);self.assertEqual(P.load(p)['objective'],'goal')
 def test_enough_evidence_moves_to_manuscript_without_extra_gate(self):
  s=P.init('full','goal');P.advance(s,'design','evidence.md',self.root,'budget');P.authorize(s,60,'user');P.advance(s,'research','evidence.md',self.root,'decisive test');P.advance(s,'manuscript','evidence.md',self.root,'write');self.assertEqual(s['stage'],'manuscript')
 def test_evidence_outside_root_is_not_accepted(self):
  s=P.init('full','goal')
  with self.assertRaises(P.PhaseError):P.advance(s,'design','../elsewhere.md',self.root,'next')
class Sources(unittest.TestCase):
 def test_14_pinned_sources_have_preparable_files(self):
  idx=json.loads((ROOT/'src/common/assets/capability-index.json').read_text());self.assertEqual(len(idx['capabilities']),14)
  for c in idx['capabilities']:self.assertIn(c['entry'],[f['path'] for f in c['required_files']]);self.assertEqual(len(c['commit']),40)
 def test_preparation_and_reuse_verify_source_bytes(self):
  with tempfile.TemporaryDirectory() as td:
   c={'id':'fixture','commit':'a'*40,'tree':'b'*40,'repository':'owner/repo','entry':'SKILL.md','kind':'skill_protocol','dependencies':[],'host_adaptation':'fixture','required_files':[{'path':'SKILL.md','blob':C.blob(b'actual fixture protocol')}]}
   p=Path(td)/'fixture'/c['commit']/'SKILL.md';p.parent.mkdir(parents=True);p.write_bytes(b'actual fixture protocol');r=C.prepare(c,td)
   self.assertFalse(r['research_work_done']);p.write_text('changed')
   with self.assertRaises(C.CapabilityError):C.prepare(c,td)
 def test_usage_receipt_cannot_skip_required_support(self):
  with tempfile.TemporaryDirectory() as td:
   c={'id':'fixture','commit':'a'*40,'tree':'b'*40,'repository':'owner/repo','entry':'SKILL.md','kind':'skill_protocol','roles':['reading'],'dependencies':[],'host_adaptation':'fixture','required_files':[{'path':'SKILL.md','blob':C.blob(b'protocol')}]};p=Path(td)/'fixture'/c['commit']/'SKILL.md';p.parent.mkdir(parents=True);p.write_bytes(b'protocol');r=C.prepare(c,td);r['files']=[]
   with self.assertRaises(C.CapabilityError):C.usage(c,r,[str(p)],[str(p)],['read'], 'adapted_in_host')
 def test_missing_offline_source_is_not_claimed_prepared(self):
  with tempfile.TemporaryDirectory() as td:
   c={'id':'fixture','commit':'a'*40,'repository':'owner/repo','required_files':[{'path':'SKILL.md','blob':'b'*40}]}
   with self.assertRaises(C.CapabilityError):C.prepare(c,td)
 def test_path_traversal_rejected(self):
  with self.assertRaises(C.CapabilityError):C.path_under('/tmp/cache','../elsewhere')
if __name__=='__main__':unittest.main()
