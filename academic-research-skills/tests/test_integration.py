"""Offline integration-policy tests. All stub papers/results are synthetic.

These exercise actual bridge code and subprocess boundaries, NOT real upstream
scientific performance, native agent behavior, networking, or venue acceptance.
"""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('provider_runtime',ROOT/'scripts/provider_runtime.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
REG=b.load(ROOT/'tests/fixtures/legacy-provider-catalog.json')
SKILLS=sorted(p for p in (ROOT/'skills').iterdir() if p.is_dir())

def task(cap,**facts):return {'capability':cap,'request':'SYNTHETIC test of '+cap,'facts':facts,'inputs':[]}

def stub_provider(base,pid,code=None):
    p=b.find_provider(REG,pid);repo=Path(base)/pid;repo.mkdir(parents=True,exist_ok=True)
    for rel in p['required_paths']:
        f=repo/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_text('SYNTHETIC dependency placeholder\n')
    if p.get('script'):
        s=repo/p['script']['path'];s.parent.mkdir(parents=True,exist_ok=True)
        s.write_text(code or 'def search_papers(**kwargs):\n    return {"crossref": [{"title": "SYNTHETIC PAPER; NOT REAL", "abstract": "Synthetic abstract", "source": "crossref"}]}\n')
    return {'root':str(repo),'source_reviewed':True,'script_reviewed':True}

class ProviderPolicyTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.path=Path(self.t.name)
        self.config={'providers':{},'host_capabilities':['python','web','network','local-files','vision']}
    def tearDown(self):self.t.cleanup()
    def enable(self,pid,code=None):self.config['providers'][pid]=stub_provider(self.path,pid,code)
    def test_14_sources_13_repos(self):
        s=b.load(ROOT/'docs/project-sources.json');self.assertEqual(s['source_files'],14);self.assertEqual(s['unique_repositories'],13)
    def test_namespaced_unique_ids(self):
        ids=[x['id'] for x in REG['providers']];self.assertEqual(len(ids),len(set(ids)));self.assertEqual(len(ids),29)
    def test_every_provider_is_from_project_sources(self):
        repos={x['repo'] for x in b.load(ROOT/'docs/project-sources.json')['sources']}
        self.assertTrue(all(p['repo'] in repos for p in REG['providers']))
    def test_journal_only_never_runs_other_capabilities(self):
        for pid in ['researchstudio.paper-search','aris.experiment-bridge','codex-ppt.image-deck']:self.enable(pid)
        d=b.plan(task('journal-intelligence',has_manuscript=True),self.config,REG)
        self.assertEqual(d['considered'],[]);self.assertIsNone(d['selected_provider']);self.assertFalse(d['executed'])
    def test_core_search_no_subagents(self):
        self.enable('researchstudio.paper-search')
        d=b.plan(task('literature-discovery'),self.config,REG)
        self.assertEqual(d['selected_provider'],'researchstudio.paper-search');self.assertFalse(d['subagents_required_by_this_bridge'])
    def test_installed_candidates_do_not_all_execute(self):
        for pid in ['scipilot.figure','nature.figure','scholar.publication-chart']:self.enable(pid)
        d=b.plan(task('scientific-visualization',has_data=True,plot_backend_chosen=True),self.config,REG)
        self.assertEqual(d['selected_provider'],'scipilot.figure');self.assertFalse(d['executed'])
    def test_user_preference_when_eligible(self):
        for pid in ['scipilot.figure','nature.figure']:self.enable(pid)
        t=task('scientific-visualization',has_data=True,plot_backend_chosen=True);t['preferred_provider']='nature.figure'
        self.assertEqual(b.plan(t,self.config,REG)['selected_provider'],'nature.figure')
    def test_missing_provider_falls_back(self):
        d=b.plan(task('literature-discovery'),self.config,REG)
        self.assertEqual(d['status'],'fallback_needed');self.assertIn('not_configured',d['considered'][0]['reasons'])
    def test_missing_declared_dependency_not_available(self):
        self.enable('nature.reader');root=Path(self.config['providers']['nature.reader']['root'])
        (root/'skills/nature-shared/core/terminology-ledger.md').unlink()
        self.assertEqual(b.inspect_provider(b.find_provider(REG,'nature.reader'),self.config)['status'],'missing_files')
    def test_source_drift_needs_review(self):
        self.enable('nature.reader');self.config['providers']['nature.reader']['source_reviewed']=False
        self.assertEqual(b.inspect_provider(b.find_provider(REG,'nature.reader'),self.config)['status'],'source_review_required')
    def test_phase2_not_default(self):
        self.enable('aris.experiment-bridge')
        d=b.plan(task('analysis-execution',has_data=True,has_experiment_plan=True,budget_defined=True,stop_conditions_defined=True),self.config,REG)
        self.assertNotEqual(d['selected_provider'],'aris.experiment-bridge')
    def test_phase2_explicit_bounded_without_subagents(self):
        self.enable('aris.experiment-bridge');t=task('analysis-execution',has_data=True,has_experiment_plan=True,budget_defined=True,stop_conditions_defined=True)
        t.update(allowed_phases=[2],enabled_providers=['aris.experiment-bridge'])
        self.assertEqual(b.plan(t,self.config,REG)['selected_provider'],'aris.experiment-bridge')
    def test_phase2_without_stop_condition_not_selected(self):
        self.enable('aris.experiment-bridge');t=task('analysis-execution',has_data=True,has_experiment_plan=True,budget_defined=True)
        t.update(allowed_phases=[2],enabled_providers=['aris.experiment-bridge'])
        self.assertIsNone(b.plan(t,self.config,REG)['selected_provider'])
    def test_no_data_no_generated_empirical_values(self):
        self.enable('scipilot.figure');d=b.plan(task('scientific-visualization'),self.config,REG)
        self.assertEqual(d['status'],'blocked_evidence')
    def test_read_only_chart_review_not_blocked_as_generation(self):
        t=task('scientific-visualization');t['operation']='review'
        self.assertNotEqual(b.plan(t,self.config,REG)['status'],'blocked_evidence')
    def test_method_planning_does_not_require_collected_data(self):
        t=task('analysis-execution');t['operation']='plan'
        self.assertNotEqual(b.plan(t,self.config,REG)['status'],'blocked_evidence')
    def test_analysis_no_data_no_fake_execution(self):
        d=b.plan(task('analysis-execution'),self.config,REG);self.assertEqual(d['status'],'blocked_evidence')
    def test_theoretical_executable_model_allowed(self):
        d=b.plan(task('analysis-execution',has_executable_model=True),self.config,REG);self.assertNotEqual(d['status'],'blocked_evidence')
    def test_unverified_results_flagged_not_fabricated(self):
        self.enable('nature.writing');d=b.plan(task('manuscript-writing'),self.config,REG)
        self.assertTrue(d['notices']);self.assertFalse(d['scientific_validity_certified'])
    def test_human_verification_not_assumed(self):
        self.enable('kdense.scientific-writing');t=task('manuscript-writing');t['enabled_providers']=['kdense.scientific-writing']
        self.assertIsNone(b.plan(t,self.config,REG)['selected_provider'])
    def test_generated_figures_not_forced_for_literature(self):
        self.enable('kdense.literature-review');t=task('literature-discovery');t['enabled_providers']=['kdense.literature-review']
        d=b.plan(t,self.config,REG);self.assertIsNone(d['selected_provider'])
    def test_reference_is_not_executor(self):
        self.enable('anti-defensive.expression');t=task('manuscript-writing');t['enabled_providers']=['anti-defensive.expression']
        self.assertIsNone(b.plan(t,self.config,REG)['selected_provider'])
    def test_third_phase_requires_actual_task(self):
        self.enable('open-design.academic-deck');self.config['host_capabilities'].append('browser')
        t=task('presentation');t.update(allowed_phases=[3],enabled_providers=['open-design.academic-deck'])
        self.assertIsNone(b.plan(t,self.config,REG)['selected_provider'])
    def test_native_fixed_subagent_condition_cannot_be_faked(self):
        self.enable('codex-ppt.image-deck');self.config['host_capabilities'].append('image-generation')
        t=task('presentation',presentation_requested=True,image_slides_accepted=True,guided_checkpoints_accepted=True)
        t.update(allowed_phases=[3],enabled_providers=['codex-ppt.image-deck'])
        self.assertIsNone(b.plan(t,self.config,REG)['selected_provider'])
    def test_handoff_no_execution(self):
        self.enable('nature.writing');out=self.path/'handoff';t=task('manuscript-writing',has_verified_results=True)
        d=b.prepare_handoff(t,self.config,REG,out)
        self.assertTrue((out/'handoff.md').is_file());self.assertFalse(d['executed']);self.assertFalse((out/'execution.json').exists())
    def test_handoff_keeps_original_request(self):
        t=task('journal-intelligence');t['request']='原始问题；不要重跑实验。';out=self.path/'handoff'
        b.prepare_handoff(t,self.config,REG,out);self.assertEqual(b.load(out/'task.json')['request'],t['request'])
    def test_handoff_existing_dir_rejected(self):
        with self.assertRaises(b.ContractError):b.prepare_handoff(task('journal-intelligence'),self.config,REG,self.path)
    def test_input_changes_invalidate_handoff(self):
        f=self.path/'evidence.txt';f.write_text('synthetic v1');t=task('journal-intelligence');t['inputs']=[{'path':str(f)}]
        out=self.path/'h';b.prepare_handoff(t,self.config,REG,out)
        self.assertTrue(b.check_handoff(out)['passed']);f.write_text('synthetic v2');self.assertFalse(b.check_handoff(out)['passed'])
    def test_provider_dependency_changes_invalidate_handoff(self):
        self.enable('nature.writing');out=self.path/'h';b.prepare_handoff(task('manuscript-writing'),self.config,REG,out)
        dep=Path(self.config['providers']['nature.writing']['root'])/'skills/nature-shared/core/ethics.md';dep.write_text('changed')
        self.assertFalse(b.check_handoff(out)['passed'])
    def test_nonexistent_input_not_prepared(self):
        t=task('journal-intelligence');t['inputs']=[{'path':str(self.path/'missing')}]
        with self.assertRaises(b.ContractError):b.prepare_handoff(t,self.config,REG,self.path/'h')
    def test_path_traversal_rejected(self):
        with self.assertRaises(b.ContractError):b.bounded(self.path,'../outside')

class AdapterAndEvidenceTests(unittest.TestCase):
    def setUp(self):self.t=tempfile.TemporaryDirectory();self.p=Path(self.t.name)
    def tearDown(self):self.t.cleanup()
    def config(self,pid,code=None):return {'providers':{pid:stub_provider(self.p,pid,code)}}
    def test_search_schema_keeps_abstract_not_read(self):
        f=self.p/'raw.json';b.write(f,{'crossref':[{'title':'SYNTHETIC','abstract':'test'}]});d=b.normalize_search(b.load(f),f)
        self.assertTrue(d['records'][0]['reading']['abstract_available']);self.assertFalse(d['records'][0]['reading']['abstract_inspected'])
        self.assertFalse(d['records'][0]['reading']['full_text_inspected']);self.assertEqual(d['records'][0]['citation_support'],'unverified')
    def test_recall_quarantined(self):
        f=self.p/'raw.json';b.write(f,{'crossref':[],'model_knowledge':[{'title':'SYNTHETIC memory lead'}]});d=b.normalize_search(b.load(f),f)
        self.assertEqual(len(d['records']),0);self.assertEqual(len(d['unverified_model_leads']),1)
    def test_unknown_search_envelope_rejected(self):
        f=self.p/'r.json';b.write(f,{'papers':'not a supported source list'})
        with self.assertRaises(b.ContractError):b.normalize_search(b.load(f),f)
    def test_empty_source_does_not_prove_no_literature(self):
        f=self.p/'r.json';b.write(f,{'crossref':[]});self.assertIn('unassessed',b.normalize_search(b.load(f),f)['completeness'])
    def test_malformed_paper_not_silently_dropped(self):
        f=self.p/'r.json';b.write(f,{'crossref':[{}]})
        with self.assertRaises(b.ContractError):b.normalize_search(b.load(f),f)
    def test_search_adapter_calls_function_in_real_subprocess_with_stub(self):
        pid='researchstudio.paper-search';cfg=self.config(pid);out=self.p/'run'
        req={'query':'synthetic','start_year':2024,'end_year':2026,'sources':['crossref']}
        result=b.run_adapter(b.find_provider(REG,pid),cfg,req,out,True,10)
        self.assertEqual(result['status'],'executed_needs_review');self.assertFalse(result['native_skill_workflow_completed'])
        self.assertTrue((out/'search-handoff.json').exists());self.assertEqual(b.load(out/'raw.json')['crossref'][0]['title'],'SYNTHETIC PAPER; NOT REAL')
    def test_network_denied_before_execution(self):
        pid='researchstudio.paper-search';cfg=self.config(pid)
        with self.assertRaises(b.ContractError):b.run_adapter(b.find_provider(REG,pid),cfg,{},self.p/'run',False)
        self.assertFalse((self.p/'run').exists())
    def test_script_drift_requires_actual_review(self):
        pid='researchstudio.paper-search';cfg=self.config(pid);cfg['providers'][pid]['script_reviewed']=False
        with self.assertRaises(b.ContractError):b.run_adapter(b.find_provider(REG,pid),cfg,{},self.p/'run',True)
    def test_native_provider_has_no_fake_call_api(self):
        with self.assertRaises(b.ContractError):b.run_adapter(b.find_provider(REG,'nature.reader'),{}, {},self.p/'r')
    def test_subprocess_failure_retained(self):
        pid='researchstudio.paper-search';cfg=self.config(pid,'def search_papers(**kwargs):\n    raise RuntimeError("SYNTHETIC failure")\n');out=self.p/'r'
        req={'query':'synthetic','start_year':2024,'end_year':2026,'sources':['crossref']}
        result=b.run_adapter(b.find_provider(REG,pid),cfg,req,out,True,10)
        self.assertEqual(result['status'],'failed');self.assertIn('SYNTHETIC failure',(out/'stderr.log').read_text())
    def test_timeout_receipt_is_not_success(self):
        pid='researchstudio.paper-search';cfg=self.config(pid,'import time\ndef search_papers(**kwargs):\n    time.sleep(30)\n');out=self.p/'r'
        req={'query':'synthetic','start_year':2024,'end_year':2026,'sources':['crossref']}
        result=b.run_adapter(b.find_provider(REG,pid),cfg,req,out,True,.25)
        self.assertEqual(result['status'],'timeout');self.assertIsNone(result['raw_output_sha256'])
    def test_empty_request_invalid_function_args(self):
        pid='researchstudio.paper-search';cfg=self.config(pid);result=b.run_adapter(b.find_provider(REG,pid),cfg,{},self.p/'r',True,10)
        self.assertEqual(result['status'],'failed')
    def test_scipilot_adapter_stub_and_null_semantics(self):
        pid='scipilot.figure';cfg=self.config(pid,'def profile_data(source, group_cols=None):\n    return {"n_rows":2,"undefined":float("nan"),"groups":group_cols}\n')
        inp=self.p/'data.csv';inp.write_text('x\n1\n2\n');out=self.p/'r'
        result=b.run_adapter(b.find_provider(REG,pid),cfg,{'input':str(inp),'groups':[]},out,False,10)
        self.assertEqual(result['status'],'executed_needs_review');self.assertTrue(result['input_unchanged']);self.assertIsNone(b.load(out/'raw.json')['undefined'])
    def test_modified_input_is_reported(self):
        pid='scipilot.figure';cfg=self.config(pid,'from pathlib import Path\ndef profile_data(source, group_cols=None):\n    Path(source).write_text("SYNTHETIC mutation")\n    return {}\n')
        inp=self.p/'data.csv';inp.write_text('x\n1\n');out=self.p/'r'
        result=b.run_adapter(b.find_provider(REG,pid),cfg,{'input':str(inp)},out,False,10)
        self.assertEqual(result['status'],'failed_input_modified')
    def test_reading_abstract_cannot_be_full_text(self):
        d={'kind':'reading','records':[{'id':'SYNTHETIC','source_access':'abstract-only','claimed_inspected':['full_text'],'coverage':{'full_text':{'inspected':True,'locator':'abstract'}}}]}
        self.assertFalse(b.audit_payload(d,self.p)['passed'])
    def test_reading_legitimate_abstract_only(self):
        d={'kind':'reading','records':[{'id':'SYNTHETIC','source_access':'abstract-only','claimed_inspected':['abstract'],'coverage':{'abstract':{'inspected':True,'locator':'abstract'}}}]}
        result=b.audit_payload(d,self.p);self.assertTrue(result['passed']);self.assertFalse(result['scientific_validity_certified'])
    def test_reading_needs_locator(self):
        d={'kind':'reading','records':[{'id':'SYNTHETIC','claimed_inspected':['figures'],'coverage':{'figures':{'inspected':True}}}]}
        self.assertFalse(b.audit_payload(d,self.p)['passed'])
    def test_failed_attempt_not_discarded_from_log(self):
        d={'kind':'experiments','all_attempts':[{'id':'a','status':'keep','metric':0.5},{'id':'b','status':'crash','metric':None}],'retained_attempt_ids':['a']}
        self.assertFalse(b.audit_payload(d,self.p)['passed'])
    def test_crash_zero_is_not_best_metric(self):
        d={'kind':'experiments','all_attempts':[{'id':'b','status':'crash','metric':0}],'retained_attempt_ids':['b'],'selected_attempt_id':'b'}
        self.assertFalse(b.audit_payload(d,self.p)['passed'])
    def test_missing_attempt_status_not_passed(self):
        d={'kind':'experiments','all_attempts':[{'id':'a','metric':0.5}], 'retained_attempt_ids':['a'],'selected_attempt_id':'a'}
        self.assertFalse(b.audit_payload(d,self.p)['passed'])
    def test_discarded_attempt_not_selected_as_final(self):
        d={'kind':'experiments','all_attempts':[{'id':'a','status':'discard','metric':0.5}],'retained_attempt_ids':['a'],'selected_attempt_id':'a'}
        self.assertFalse(b.audit_payload(d,self.p)['passed'])
    def test_failed_metric_null_log_can_pass_structure(self):
        d={'kind':'experiments','all_attempts':[{'id':'a','status':'keep','metric':0},{'id':'b','status':'crash','metric':None}],'retained_attempt_ids':['a','b'],'selected_attempt_id':'a'}
        self.assertTrue(b.audit_payload(d,self.p)['passed'])
    def fig(self):
        f=self.p/'frozen.json';b.write(f,{'RESULT-SYNTHETIC':{'estimate':2.347,'unit':'synthetic-unit'}})
        return {'kind':'figure-values','results_path':'frozen.json','results_sha256':b.sha(f),'values':[{'result_id':'RESULT-SYNTHETIC','field':'estimate','value':2.347,'unit':'synthetic-unit'}]}
    def test_figure_actual_result_mapping(self):
        d=self.fig();result=b.audit_payload(d,self.p);self.assertTrue(result['passed']);self.assertFalse(result['actual_visual_inspection_performed'])
    def test_figure_wrong_value_fails(self):
        d=self.fig();d['values'][0]['value']=2.5;self.assertFalse(b.audit_payload(d,self.p)['passed'])
    def test_figure_rounding_explicit(self):
        d=self.fig();d['values'][0].update(value=2.35,decimals=2);self.assertTrue(b.audit_payload(d,self.p)['passed'])
    def test_figure_wrong_unit_fails(self):
        d=self.fig();d['values'][0]['unit']='other';self.assertFalse(b.audit_payload(d,self.p)['passed'])
    def test_figure_tampered_source_fails(self):
        d=self.fig();(self.p/'frozen.json').write_text('{}');self.assertFalse(b.audit_payload(d,self.p)['passed'])
    def test_figure_boolean_not_numeric(self):
        d=self.fig();d['values'][0]['value']=True;self.assertFalse(b.audit_payload(d,self.p)['passed'])

class IsolatedProviderTests(unittest.TestCase):pass

def make_isolation(original):
    def test(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/original.name;shutil.copytree(original,root,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            result=subprocess.run([sys.executable,'-S','-B',str(root/'scripts/provider_runtime.py'),'list'],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads(result.stdout);self.assertEqual(report['capability'],original.name)
            reg=json.loads((root/'assets/providers.json').read_text())
            if original.name!='research-paper-workflow':self.assertTrue(all(original.name in p['capabilities'] for p in reg['providers']))
            # Explicitly no central registry or sibling modules available.
            self.assertFalse((Path(temp)/'docs').exists())
            b.write(Path(temp)/'task.json',task(original.name));b.write(Path(temp)/'config.json',{'providers':{},'host_capabilities':[]})
            result=subprocess.run([sys.executable,'-S','-B',str(root/'scripts/provider_runtime.py'),'plan','--task',str(Path(temp)/'task.json'),'--config',str(Path(temp)/'config.json')],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr);self.assertFalse(json.loads(result.stdout)['executed'])
    return test
for skill in SKILLS:setattr(IsolatedProviderTests,'test_'+skill.name.replace('-','_')+'_provider_independence',make_isolation(skill))

if __name__=='__main__':unittest.main()
