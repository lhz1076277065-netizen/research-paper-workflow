"""Observed state/artifact regressions, not keyword acceptance of guidance."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import phase_control as P
import work_units as W

class WorkUnits(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'evidence.json').write_text('{"actual_result":0}')
        self.state=P.init('focused','Compare measurement methods',60,authority='User gave 60 minutes')
    def tearDown(self):self.tmp.cleanup()
    def test_actual_request_anchor_not_initialization(self):
        s=P.init('full','question',1440,clock=100000,authority='24 hours',started_at=98000,anchor_basis='real request')
        self.assertEqual(s['project_deadline'],98000+86400)
        self.assertEqual(s['budget_anchor']['started_at'],P.iso(98000))
        self.assertTrue(s['budget_anchor']['verified'])
    def test_future_anchor_rejected(self):
        with self.assertRaises(P.PhaseError):P.init('full','x',10,clock=50,started_at=51)
    def test_rollout_anchor_reads_user_not_folder(self):
        p=self.root/'rollout.jsonl'
        p.write_text(json.dumps({'type':'session_meta','timestamp':'2026-10-12T00:00:00Z','payload':{}})+'\n'+json.dumps({'type':'event_msg','timestamp':'2026-10-12T00:05:00Z','payload':{'type':'user_message','message':'24 hours'}})+'\n')
        self.assertEqual(P.request_anchor(p),1791763500)
    def test_long_chat_does_not_use_old_installation_request_for_new_budget(self):
        p=self.root/'rollout.jsonl'
        p.write_text(''.join(json.dumps({'type':'event_msg','timestamp':t,
            'payload':{'type':'user_message','message':m}})+'\n' for t,m in
            [('2026-10-11T00:00:00Z','Install the Skill'),('2026-10-12T00:05:00Z','Research for 24 hours')]))
        with self.assertRaises(P.PhaseError):P.request_anchor(p)
        self.assertEqual(P.request_anchor(p,'Research for 24 hours'),1791763500)
    def test_duplicate_budget_message_requires_actual_timestamp_selection(self):
        p=self.root/'rollout.jsonl'
        p.write_text(''.join(json.dumps({'type':'event_msg','timestamp':t,
            'payload':{'type':'user_message','message':'24 hours'}})+'\n' for t in
            ['2026-10-11T00:00:00Z','2026-10-12T00:05:00Z']))
        with self.assertRaises(P.PhaseError):P.request_anchor(p,'24 hours')
    def test_request_log_without_timezone_not_guessed(self):
        p=self.root/'rollout.jsonl'
        p.write_text(json.dumps({'type':'event_msg','timestamp':'2026-10-12T00:05:00',
            'payload':{'type':'user_message','message':'24 hours'}})+'\n')
        with self.assertRaises(P.PhaseError):P.request_anchor(p)
    def test_unknown_anchor_is_not_claimed_verified(self):
        self.assertFalse(self.state['budget_anchor']['verified'])
        P.set_meter(self.state,{'input_tokens':500,'cached_input_tokens':100,'output_tokens':50},'actual sample')
        self.assertTrue(P.guard(self.state)['token_meter_verified'])
        self.assertFalse(P.guard(self.state)['strict_token_budget_verified'])
        self.assertEqual(P.guard(self.state)['token_budget_coverage'],'unknown')
    def test_late_meter_initialization_backfills_actual_budget_usage(self):
        s=P.init('full','x',60,clock=200,authority='60 minutes',started_at=100)
        p=self.root/'usage.jsonl'
        def row(t,a,b,c):return json.dumps({'type':'token_usage_record','timestamp':P.iso(t),
            'payload':{'thread_token_usage':{'input_tokens':a,'cached_input_tokens':b,'output_tokens':c}}})+'\n'
        p.write_text(row(90,100,20,10)+row(150,500,200,50))
        d=P.meter_rollout(s,p)
        self.assertEqual(d['input_tokens'],400);self.assertEqual(d['cached_input_tokens'],180);self.assertEqual(d['output_tokens'],40)
        self.assertEqual(s['meter']['coverage'],'budget_anchor')
        self.assertTrue(P.guard(s,clock=200)['strict_token_budget_verified'])
    def test_missing_initial_token_coverage_does_not_claim_strict_limit(self):
        s=P.init('full','x',60,clock=time.time(),authority='60 minutes',started_at=time.time()-100)
        P.set_meter(s,{'input_tokens':500,'cached_input_tokens':0,'output_tokens':50},'actual host')
        s['token_limit']=1000
        self.assertIn('initial_token_coverage_unknown',P.guard(s)['reasons'])
    def test_budget_metric_matches_actual_authority_not_assumed_cache_cost(self):
        s=self.state
        P.set_meter(s,{'input_tokens':0,'cached_input_tokens':0,'output_tokens':0},'fixture meter')
        P.set_meter(s,{'input_tokens':100,'cached_input_tokens':90,'output_tokens':10},'fixture meter')
        s['token_limit']=100
        self.assertFalse(P.guard(s)['allowed'])
        s['token_metric']='noncached_input_plus_output'
        self.assertTrue(P.guard(s)['allowed']);self.assertEqual(P.token_spent(s,P.usage_delta(s)),20)
    def test_plan_ceiling_autonomously_revised(self):
        W.plan(self.state,'fits',450,448,'agent','Original estimate',['evidence.json'],self.root)
        W.plan(self.state,'fits',600,448,'agent','Necessary sensitivity fits within real time',['evidence.json'],self.root)
        self.assertEqual(self.state['resource_plans']['fits']['limit'],600)
        self.assertTrue(P.guard(self.state)['allowed'])
    def test_real_user_limit_not_relabelled(self):
        W.plan(self.state,'fits',450,0,'user','Explicit user limit',['evidence.json'],self.root)
        with self.assertRaises(P.PhaseError):W.plan(self.state,'fits',600,448,'agent','Try override',['evidence.json'],self.root)
    def test_default_plan_expiry_is_reassessment_not_terminal(self):
        s=P.init('full','x',clock=0,autonomous_plan=True)
        g=P.enforce(s,clock=3000)
        self.assertIn('stage_reassessment_required',g['reasons']);self.assertEqual(s['status'],'active')
        P.reassess(s,'evidence.json',self.root,'Test next candidate',minutes=15,clock=3000)
        self.assertTrue(P.guard(s,clock=3001)['allowed']);self.assertEqual(s['started_at'],P.iso(0))
    def test_unbudgeted_feasibility_advances_without_approval(self):
        s=P.init('full','x',clock=time.time(),autonomous_plan=True)
        P.advance(s,'design','evidence.json',self.root,'Design minimal test')
        self.assertEqual(s['status'],'active');self.assertEqual(s['stage'],'design')
    def test_user_budget_cannot_be_extended(self):
        deadline=self.state['project_deadline']
        P.reassess(self.state,'evidence.json',self.root,'Next test',minutes=1000)
        self.assertEqual(self.state['project_deadline'],deadline)
    def test_agent_reserve_reallocation_runs_real_remaining_work(self):
        s=P.init('full','Review existing manuscript',10,clock=0,authority='Ten actual minutes')
        g=P.enforce(s,clock=550)
        self.assertFalse(g['allowed']);self.assertEqual(s['status'],'active');self.assertTrue(s['delivery_required'])
        before=s['project_deadline']
        P.reassess(s,'evidence.json',self.root,'Review the existing manuscript',clock=550,minutes=.5,reserve_seconds=10)
        self.assertTrue(P.guard(s,estimated_seconds=20,clock=551)['allowed']);self.assertEqual(s['project_deadline'],before)
        P.enforce(s,clock=600);self.assertEqual(s['status'],'closed_limit')
    def test_user_or_unknown_reserve_is_not_silently_reallocated(self):
        for origin in ('user',None):
            s=self.state.copy();s['reserve_authority']=origin
            with self.assertRaises(P.PhaseError):P.reassess(s,'evidence.json',self.root,'Next',reserve_seconds=0)
    def test_reserve_reallocation_executes_child_without_renewing_budget(self):
        s=P.init('maintenance','Finish actual local export',1,authority='Fixture one minute',started_at=time.time()-55)
        self.assertFalse(P.enforce(s)['allowed']);self.assertEqual(s['status'],'active')
        original=s['project_deadline']
        P.reassess(s,'evidence.json',self.root,'Finish export',minutes=.03,reserve_seconds=.1)
        state=self.root/'phase.json';P.save(state,s);out=self.root/'actual-export.json'
        r=P.run(state,[sys.executable,'-c',f'import json;open({str(out)!r},"w").write(json.dumps({{"sum":sum([2,3,5])}}))'],self.root/'run.log','Export computed sum','Deliver existing evidence')
        self.assertEqual(r['returncode'],0);self.assertEqual(json.loads(out.read_text()),{'sum':10})
        self.assertEqual(P.load(state)['project_deadline'],original)
    def test_default_token_reserve_is_revisable_but_actual_ceiling_is_not(self):
        s=self.state
        P.set_meter(s,{'input_tokens':0,'cached_input_tokens':0,'output_tokens':0},'fixture meter')
        P.set_meter(s,{'input_tokens':96,'cached_input_tokens':0,'output_tokens':0},'fixture meter')
        s.update(token_limit=100,token_reserve=5)
        self.assertFalse(P.enforce(s)['allowed']);self.assertEqual(s['status'],'active')
        P.reassess(s,'evidence.json',self.root,'Complete small deliverable',token_reserve=0)
        self.assertTrue(P.guard(s,estimated_tokens=1)['allowed']);self.assertEqual(s['token_limit'],100)
    def test_failed_route_does_not_stop_task(self):
        W.route(self.state,'broken','claim','dependency probe',['evidence.json'],self.root,'failed')
        W.route(self.state,'alternative','claim','native estimator',['evidence.json'],self.root,'ready')
        self.assertEqual(self.state['status'],'active');self.assertEqual(self.state['next_action'],'native estimator')
        with self.assertRaises(P.PhaseError):W.validate_route_exit(self.state)
    def test_route_closure_requires_tests_and_current_evidence(self):
        with self.assertRaises(P.PhaseError):W.validate_route_exit(self.state)
        W.route(self.state,'broken','claim','actual test',['evidence.json'],self.root,'failed')
        self.assertEqual(W.validate_route_exit(self.state)['candidate_count'],1)
        (self.root/'evidence.json').write_text('changed test results')
        with self.assertRaises(P.PhaseError):W.validate_route_exit(self.state)
    def test_actual_result_updates_next_action(self):
        self.state['next_action']='Run already completed experiment'
        W.checkpoint(self.state,'model','offset matters','Write negative result',['evidence.json'],self.root,'refuted')
        self.assertEqual(P.resume(self.state,True)['current_work']['outcome'],'refuted')
        self.assertEqual(self.state['next_action'],'Write negative result')
    def test_checkpoint_cannot_rewrite_claim(self):
        W.checkpoint(self.state,'x','Original claim','Next',['evidence.json'],self.root)
        with self.assertRaises(P.PhaseError):W.checkpoint(self.state,'x','Stronger new claim','Next',['evidence.json'],self.root)
    def test_181_completed_receipts_do_not_become_pending(self):
        self.state['professional_pending']=[{'step_id':str(i),'status':'completed'} for i in range(181)]+[{'step_id':'live','status':'started'}]
        s=P.resume(self.state,True)
        self.assertEqual(s['professional_pending_count'],1);self.assertEqual(s['professional_completed_unconsumed_count'],181)
        self.assertEqual(len(s['professional_completed_unconsumed']),3)
        self.assertLess(len(json.dumps(s)),7000)
        self.assertEqual(len(P.resume(self.state)['professional_pending']),182)
    def test_adopt_preserves_budget_and_pause_unknowns(self):
        s=self.state;s.pop('workflow_version');s.pop('budget_anchor');s['status']='paused';deadline=s['project_deadline']
        W.adopt(s,'Use newest workflow autonomously')
        self.assertEqual(s['status'],'paused');self.assertEqual(s['project_deadline'],deadline)
        self.assertEqual(s['budget_anchor']['basis'],'legacy_unknown')
    def test_review_content_change_invalidates_reuse(self):
        rows=W.refs(['evidence.json'],self.root)
        self.state['reviews']={'x':{'fingerprint':W.identity(rows),'instruction':self.state['latest_instruction'],
            'started':'start','finished':'finish','receipt':{'verified':'source receipt'}}}
        with patch.object(W,'check_review',return_value={'verified':'source receipt'}) as call:
            self.assertTrue(W.review_status(self.state,'x',['evidence.json'],self.root)['reusable']);self.assertEqual(call.call_count,1)
        (self.root/'evidence.json').write_text('{"actual_result":1}')
        with patch.object(W,'check_review') as call:
            self.assertFalse(W.review_status(self.state,'x',['evidence.json'],self.root)['reusable']);call.assert_not_called()
    def test_review_changed_receipt_rejected(self):
        self.state['reviews']={'x':{'fingerprint':W.identity(W.refs(['evidence.json'],self.root)),
            'instruction':self.state['latest_instruction'],'started':'start','finished':'finish','receipt':{'original':1}}}
        with patch.object(W,'check_review',return_value={'edited':1}):
            self.assertFalse(W.review_status(self.state,'x',['evidence.json'],self.root)['reusable'])
    def test_process_reconciliation_never_kills_live_pid(self):
        self.state['owned_processes']=[{'pid':123,'runner_token':'old'}]
        with patch.object(P,'process_observation',return_value={'pid':123,'state':'exists_ownership_unverified'}),patch.object(P.os,'kill') as kill:
            self.assertEqual(P.reconcile_processes(self.state)['removed'],0);kill.assert_not_called()
    def test_absent_process_is_not_success(self):
        self.state['owned_processes']=[{'pid':123,'runner_token':'old'}]
        with patch.object(P,'process_observation',return_value={'pid':123,'state':'absent'}):
            result=P.reconcile_processes(self.state)
        self.assertEqual(result['removed'],1);self.assertFalse(result['success_verified'])

if __name__=='__main__':unittest.main()
