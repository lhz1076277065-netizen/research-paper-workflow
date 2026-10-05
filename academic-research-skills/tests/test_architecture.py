"""alpha.3 offline architecture tests. Fixtures are not scientific evidence.

Real filesystem/CLI/subprocess execution, but no native agent or public API run.
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
import test_integration as old

ROOT=Path(__file__).resolve().parents[1]
b=old.b
REG=b.load(ROOT/'tests/fixtures/legacy-provider-catalog.json')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
g=module('workgraph_test',ROOT/'scripts/workgraph.py')
build=module('build_test',ROOT/'scripts/build_release.py')

class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.config={'providers':{},'host_capabilities':['local-files','python','network','web','vision']}
    def tearDown(self):self.tmp.cleanup()
    def enable(self,pid,code=None):
        self.config['providers'][pid]=old.stub_provider(self.root,pid,code)
        return self.config['providers'][pid]
    def task(self,cap,service=None,**facts):
        t=old.task(cap,**facts)
        if service:t['service']=service
        return t
    def handoff(self,required_reviews=None):
        inp=self.root/'input.txt';inp.write_text('SYNTHETIC input, not real research')
        task=self.task('journal-intelligence');task.update(requested_outputs=['report.md'],operation='review',required_reviews=required_reviews or [],inputs=[{'path':str(inp),'role':'input'}])
        h=self.root/'handoff';b.prepare_handoff(task,self.config,REG,h)
        out=self.root/'output.md';out.write_text('SYNTHETIC report, not an actual journal match')
        result={'capability':task['capability'],'task_sha256':b.sha(h/'task.json'),'provider_id':'host_fallback','execution_mode':'host_fallback','execution_status':'executed',
                'outputs':[{'role':'report.md','path':'output.md','sha256':b.sha(out)}],'reviews':[],'evidence_checks':[]}
        return h,result
    def reviewed(self,h,result,kind='semantic'):
        p=self.root/'review.md';p.write_text('SYNTHETIC inspection report; not science')
        result['reviews'].append({'kind':kind,'status':'passed','performed_by':'host_agent','checked_at':'2026-09-29T00:00:00+00:00','coverage':'Synthetic test output only',
            'report_path':'review.md','report_sha256':b.sha(p),'reviewed_outputs':{x['role']:x['sha256'] for x in result['outputs']}})
        return result
    def graph(self):
        out=self.root/'source.md';out.write_text('SYNTHETIC completed source')
        receipt=self.root/'accepted.json';b.write(receipt,{'status':'checked_for_handoff','passed':True,'artifacts':[{'path':'source.md','sha256':b.sha(out)}]})
        return {'schema_version':'workgraph-1','revision':0,'tasks':[
            {'id':'A','capability':'analysis-execution','status':'checked','depends_on':[],
                'outputs':[{'path':'source.md','sha256':b.sha(out)}],'acceptance_report':{'path':'accepted.json','sha256':b.sha(receipt)}},
            {'id':'B','capability':'scientific-visualization','status':'pending','depends_on':['A'],'write_paths':['figures']},
            {'id':'C','capability':'manuscript-writing','status':'pending','depends_on':['B'],'write_paths':['manuscript']},
            {'id':'D','capability':'journal-intelligence','status':'pending','depends_on':[],'write_paths':['journal']}]}

class OperationTests(Fixture):
    def test_figure_review_does_not_require_data_or_python(self):
        self.enable('nature.figure');self.config['host_capabilities']=['vision']
        t=self.task('scientific-visualization','figure-review',has_figure=True);t['operation']='review'
        d=b.plan(t,self.config,REG);self.assertEqual(d['selected_provider'],'nature.figure');self.assertFalse(d['executed'])
    def test_figure_plan_does_not_require_a_plotting_backend(self):
        self.enable('nature.figure');self.config['host_capabilities']=[]
        d=b.plan(self.task('scientific-visualization','figure-plan'),self.config,REG)
        self.assertEqual(d['selected_provider'],'nature.figure')
    def test_profile_uses_function_not_full_plot_workflow(self):
        self.enable('scipilot.figure')
        d=b.plan(self.task('data-preparation','profile',has_data=True),self.config,REG)
        self.assertEqual(d['selected_provider'],'scipilot.figure');self.assertEqual(d['mode'],'script-adapter')
    def test_plot_is_not_completed_by_profile_function(self):
        self.enable('scipilot.figure')
        d=b.plan(self.task('scientific-visualization','plot',has_data=True),self.config,REG)
        self.assertEqual(d['mode'],'native');self.assertFalse(d['executed'])
    def test_table_not_sent_to_pure_plotter(self):
        self.enable('scipilot.figure');self.enable('scholar.publication-chart')
        d=b.plan(self.task('scientific-visualization','table',has_data=True),self.config,REG)
        self.assertEqual(d['selected_provider'],'scholar.publication-chart')
    def test_method_plan_without_python(self):
        self.enable('kdense.statistical-analysis');self.config['host_capabilities']=[]
        d=b.plan(self.task('analysis-execution','method-plan'),self.config,REG)
        self.assertEqual(d['selected_provider'],'kdense.statistical-analysis')
    def test_unknown_service_is_not_silently_promoted(self):
        self.enable('scipilot.figure')
        d=b.plan(self.task('scientific-visualization','make-a-movie',has_data=True),self.config,REG)
        self.assertIsNone(d['selected_provider']);self.assertIn('service_not_supported',d['considered'][0]['reasons'])
    def test_unknown_capability_rejected(self):
        with self.assertRaises(b.ContractError):b.plan(self.task('nonsense'),self.config,REG)
    def test_disabled_provider_never_chosen(self):
        self.enable('scipilot.figure');t=self.task('scientific-visualization','plot',has_data=True);t['disabled_providers']=['scipilot.figure']
        self.assertIsNone(b.plan(t,self.config,REG)['selected_provider'])
    def test_preference_explicitly_enables_nondefault_candidate(self):
        self.enable('kdense.statsmodels');t=self.task('analysis-execution','analyze',has_data=True);t['preferred_provider']='kdense.statsmodels'
        self.assertEqual(b.plan(t,self.config,REG)['selected_provider'],'kdense.statsmodels')
    def test_preference_cannot_override_missing_data(self):
        self.enable('kdense.statsmodels');t=self.task('analysis-execution','analyze');t['preferred_provider']='kdense.statsmodels'
        d=b.plan(t,self.config,REG);self.assertIsNone(d['selected_provider']);self.assertTrue(d['preferred_provider_unavailable'])
    def test_independent_module_rejects_other_capability(self):
        reg=b.load(ROOT/'skills/data-preparation/assets/providers.json')
        with self.assertRaises(b.ContractError):b.plan(self.task('manuscript-writing'),self.config,reg)
    def test_duplicate_output_roles_rejected(self):
        t=self.task('journal-intelligence');t['requested_outputs']=['r','r']
        with self.assertRaises(b.ContractError):b.plan(t,self.config,REG)
    def test_stage3_cannot_leak_through_explicit_preference(self):
        self.enable('paperspine.workbench');t=self.task('workbench');t['preferred_provider']='paperspine.workbench'
        self.assertIsNone(b.plan(t,self.config,REG)['selected_provider'])

class InspectionTests(Fixture):
    def test_installed_skill_with_shared_sibling(self):
        spec=self.enable('nature.reader');p=b.find_provider(REG,'nature.reader')
        upstream=Path(spec['root']);installed=self.root/'installed/skills/nature-reader'
        shutil.copytree(upstream/'skills/nature-reader',installed)
        shutil.copytree(upstream/'skills/nature-shared',installed.parent/'nature-shared')
        self.config['providers']['nature.reader']={'layout':'skill','skill_root':str(installed),'source_reviewed':True}
        d=b.inspect_provider(p,self.config);self.assertEqual(d['status'],'files_available');self.assertEqual(Path(d['entry']).resolve(),(installed/'SKILL.md').resolve())
    def test_installed_missing_shared_dependency_not_faked(self):
        spec=self.enable('nature.reader');p=b.find_provider(REG,'nature.reader');installed=self.root/'installed/reader'
        shutil.copytree(Path(spec['root'])/'skills/nature-reader',installed)
        self.config['providers']['nature.reader']={'layout':'skill','skill_root':str(installed),'source_reviewed':True}
        self.assertEqual(b.inspect_provider(p,self.config)['status'],'missing_files')
    def test_arbitrary_skill_folder_name_supported(self):
        spec=self.enable('scipilot.figure');installed=self.root/'arbitrary-plot-folder';shutil.copytree(spec['root'],installed)
        self.config['providers']['scipilot.figure']={'layout':'skill','skill_root':str(installed),'source_reviewed':True}
        self.assertEqual(b.inspect_provider(b.find_provider(REG,'scipilot.figure'),self.config)['status'],'files_available')
    def test_digest_bound_entry_review_supported(self):
        spec=self.enable('nature.reader');p=b.find_provider(REG,'nature.reader');entry=Path(spec['root'])/p['entrypoint']
        spec.pop('source_reviewed');spec['reviewed_file_sha256']={p['entrypoint']:b.sha(entry)}
        self.assertEqual(b.inspect_provider(p,self.config)['status'],'files_available')
    def test_digest_binding_cannot_be_overridden_by_legacy_boolean(self):
        spec=self.enable('nature.reader');p=b.find_provider(REG,'nature.reader');entry=Path(spec['root'])/p['entrypoint']
        spec['reviewed_file_sha256']={p['entrypoint']:b.sha(entry)};entry.write_text('CHANGED')
        self.assertEqual(b.inspect_provider(p,self.config)['status'],'source_review_required')
    def test_legacy_flag_is_explicitly_labelled(self):
        self.enable('nature.reader');self.assertEqual(b.inspect_provider(b.find_provider(REG,'nature.reader'),self.config)['review_record'],'legacy_boolean')
    def test_request_changes_invalidate_handoff(self):
        h,r=self.handoff();t=b.load(h/'task.json');t['request']='Changed after dispatch';b.write(h/'task.json',t)
        self.assertFalse(b.check_handoff(h)['passed'])

class AcceptanceTests(Fixture):
    def test_valid_files_are_contract_checked_not_science_certified(self):
        h,r=self.handoff();d=b.accept_result(h,r,self.root)
        self.assertEqual(d['status'],'checked_for_handoff');self.assertFalse(d['scientific_validity_certified']);self.assertFalse(d['semantic_review_performed_here'])
    def test_another_task_version_rejected(self):
        h,r=self.handoff();r['task_sha256']='0'*64;self.assertFalse(b.accept_result(h,r,self.root)['passed'])
    def test_failed_execution_is_not_complete(self):
        h,r=self.handoff();r['execution_status']='failed';self.assertEqual(b.accept_result(h,r,self.root)['status'],'received_needs_review')
    def test_planned_is_not_execution(self):
        h,r=self.handoff();r['execution_status']='prepared';self.assertEqual(b.accept_result(h,r,self.root)['status'],'rejected')
    def test_missing_output_role_not_complete(self):
        h,r=self.handoff();r['outputs']=[];self.assertFalse(b.accept_result(h,r,self.root)['passed'])
    def test_output_tamper_rejected(self):
        h,r=self.handoff();(self.root/'output.md').write_text('changed');self.assertFalse(b.accept_result(h,r,self.root)['passed'])
    def test_empty_output_rejected(self):
        h,r=self.handoff();(self.root/'output.md').write_text('');r['outputs'][0]['sha256']=b.sha(self.root/'output.md');self.assertFalse(b.accept_result(h,r,self.root)['passed'])
    def test_input_write_in_review_detected(self):
        h,r=self.handoff();(self.root/'input.txt').write_text('changed');self.assertFalse(b.accept_result(h,r,self.root)['passed'])
    def test_unrelated_capability_rejected(self):
        h,r=self.handoff();r['capability']='analysis-execution';self.assertFalse(b.accept_result(h,r,self.root)['passed'])
    def test_output_path_escape_rejected(self):
        h,r=self.handoff();r['outputs'][0]['path']='../elsewhere'
        with self.assertRaises(b.ContractError):b.accept_result(h,r,self.root)
    def test_missing_required_review_stays_pending(self):
        h,r=self.handoff(['semantic']);self.assertEqual(b.accept_result(h,r,self.root)['status'],'received_needs_review')
    def test_actual_report_reference_satisfies_record_contract_only(self):
        h,r=self.handoff(['semantic']);self.reviewed(h,r);d=b.accept_result(h,r,self.root)
        self.assertTrue(d['passed']);self.assertFalse(d['semantic_review_performed_here'])
    def test_old_review_version_rejected(self):
        h,r=self.handoff(['semantic']);self.reviewed(h,r);r['reviews'][0]['reviewed_outputs']={};self.assertFalse(b.accept_result(h,r,self.root)['passed'])
    def test_missing_review_report_rejected(self):
        h,r=self.handoff(['semantic']);self.reviewed(h,r);(self.root/'review.md').unlink();self.assertFalse(b.accept_result(h,r,self.root)['passed'])
    def test_deterministic_check_not_visual_observation(self):
        h,r=self.handoff(['visual']);self.reviewed(h,r,'visual');r['reviews'][0]['performed_by']='deterministic_tool';self.assertFalse(b.accept_result(h,r,self.root)['passed'])
    def test_required_review_cannot_be_waived_in_return(self):
        h,r=self.handoff(['visual']);r['reviews']=[{'kind':'visual','status':'not_applicable','reason':'SYNTHETIC attempted waiver'}]
        self.assertFalse(b.accept_result(h,r,self.root)['passed'])
    def test_evidence_mismatch_rejects_full_text_claim(self):
        h,r=self.handoff();r['evidence_checks']=[{'kind':'reading','records':[{'id':'test','source_access':'abstract-only','claimed_inspected':['full_text'],'coverage':{'full_text':{'inspected':True,'locator':'abstract'}}}]}]
        self.assertFalse(b.accept_result(h,r,self.root)['passed'])

class EvidenceTests(Fixture):
    def test_empty_reading_claim_no_vacuous_pass(self):
        self.assertFalse(b.audit_payload({'kind':'reading','records':[{'id':'x'}]},self.root)['passed'])
    def test_unknown_reading_level_rejected(self):
        self.assertFalse(b.audit_payload({'kind':'reading','records':[{'id':'x','claimed_inspected':['magic'],'coverage':{'magic':{'inspected':True,'locator':'x'}}}]},self.root)['passed'])
    def test_repeated_retained_attempt_ids_rejected(self):
        self.assertFalse(b.audit_payload({'kind':'experiments','all_attempts':[{'id':'a','status':'completed','metric':0}],'retained_attempt_ids':['a','a']},self.root)['passed'])
    def policies(self):return {'kind':'journal-policies','as_of':'2026-09-29T00:00:00Z','policies':[{'id':'apc','status':'checked','source':'synthetic:policy','checked_at':'2026-09-25T00:00:00Z','max_age_days':30}]}
    def test_current_policy_record_can_pass_without_claiming_web_read(self):
        d=b.audit_payload(self.policies(),self.root);self.assertTrue(d['passed']);self.assertIn('no official',d['checks'][0])
    def test_stale_policy_record_flagged(self):
        d=self.policies();d['policies'][0]['checked_at']='2025-01-01T00:00:00Z';self.assertFalse(b.audit_payload(d,self.root)['passed'])
    def test_unknown_policy_not_forced_to_fake_fact(self):
        d=self.policies();d['policies']=[{'id':'apc','status':'unknown'}];self.assertTrue(b.audit_payload(d,self.root)['passed'])
    def test_future_policy_check_rejected(self):
        d=self.policies();d['policies'][0]['checked_at']='2026-10-01T00:00:00Z';self.assertFalse(b.audit_payload(d,self.root)['passed'])

class GraphTests(Fixture):
    def test_only_requested_single_task_graph(self):
        state={'schema_version':'workgraph-1','revision':0,'tasks':[{'id':'match','capability':'journal-intelligence'}]}
        result=g.assess(state,self.root);self.assertEqual(result['ready'],['match']);self.assertEqual(len(result['tasks']),1);self.assertFalse(result['execution_started'])
    def test_valid_previous_output_reused(self):
        d=g.assess(self.graph(),self.root);self.assertEqual(d['reusable'],['A']);self.assertCountEqual(d['ready'],['B','D']);self.assertEqual(d['tasks']['C']['status'],'waiting')
    def test_changed_output_invalidates_consumers(self):
        state=self.graph();(self.root/'source.md').write_text('CHANGED');d=g.assess(state,self.root)
        self.assertEqual(d['tasks']['A']['status'],'stale');self.assertEqual(d['tasks']['B']['status'],'waiting')
    def test_result_change_invalidates_descendants_not_unrelated(self):
        state=self.graph();d=g.invalidate(state,[{'task_id':'A','kind':'results'}],'SYNTHETIC correction',0)
        status={t['id']:t.get('status') for t in d['tasks']};self.assertEqual(status,{'A':'stale','B':'stale','C':'stale','D':'pending'})
        self.assertEqual(state['tasks'][0]['status'],'checked');self.assertEqual(d['revision'],1)
    def test_figure_change_does_not_repeat_upstream_analysis(self):
        state=self.graph();d=g.invalidate(state,[{'task_id':'B','kind':'presentation'}],'SYNTHETIC layout fix',0)
        self.assertEqual(d['tasks'][0]['status'],'checked');self.assertEqual(d['tasks'][2]['status'],'stale')
    def test_revision_conflict_rejected(self):
        with self.assertRaises(g.GraphError):g.invalidate(self.graph(),[{'task_id':'A','kind':'results'}],'reason',3)
    def test_cycle_rejected(self):
        state=self.graph();state['tasks'][0]['depends_on']=['C']
        with self.assertRaises(g.GraphError):g.assess(state,self.root)
    def test_missing_dependency_rejected(self):
        state=self.graph();state['tasks'][1]['depends_on']=['absent']
        with self.assertRaises(g.GraphError):g.assess(state,self.root)
    def test_skipped_dependency_does_not_supply_evidence(self):
        state=self.graph();state['tasks'][0].update(applicable=False,skip_reason='not available')
        self.assertEqual(g.assess(state,self.root)['tasks']['B']['status'],'waiting')
    def test_budget_exhausted_not_restart(self):
        state=self.graph();state['tasks'][1].update(attempts=2,max_attempts=2)
        self.assertEqual(g.assess(state,self.root)['tasks']['B']['status'],'budget_exhausted')
    def test_write_overlap_reported_without_spawning(self):
        state=self.graph();state['tasks'][3]['write_paths']=['figures/panel.svg'];d=g.assess(state,self.root)
        self.assertCountEqual(d['write_conflicts'][0]['tasks'],['B','D']);self.assertFalse(d['execution_started'])
    def test_unchecked_files_not_reusable(self):
        state=self.graph();state['tasks'][0].pop('acceptance_report');self.assertEqual(g.assess(state,self.root)['tasks']['A']['status'],'stale')
    def test_forged_completed_state_without_outputs_rejected(self):
        state=self.graph();state['tasks'][0]['outputs']=[];self.assertEqual(g.assess(state,self.root)['tasks']['A']['status'],'stale')
    def test_receipt_for_other_output_cannot_reuse(self):
        state=self.graph();b.write(self.root/'accepted.json',{'status':'checked_for_handoff','passed':True,'artifacts':[]})
        state['tasks'][0]['acceptance_report']['sha256']=b.sha(self.root/'accepted.json');self.assertEqual(g.assess(state,self.root)['tasks']['A']['status'],'stale')

class WorkerAndBuildTests(Fixture):
    def test_old_search_signature_without_unused_dates(self):
        code='def search_papers(query,start_year,end_year,max_results,sources,parallel):\n    return {sources[0]:[{"title":"SYNTHETIC search fixture"}]}\n'
        self.enable('researchstudio.paper-search',code)
        d=b.run_adapter(b.find_provider(REG,'researchstudio.paper-search'),self.config,{'query':'synthetic','start_year':2025,'end_year':2026,'sources':['crossref']},self.root/'run',True,10)
        self.assertEqual(d['status'],'executed_needs_review')
    def test_requested_unsupported_date_does_not_silently_drop(self):
        code='def search_papers(query,start_year,end_year,max_results,sources,parallel):\n    return {sources[0]:[]}\n'
        self.enable('researchstudio.paper-search',code)
        d=b.run_adapter(b.find_provider(REG,'researchstudio.paper-search'),self.config,{'query':'synthetic','start_year':2025,'end_year':2026,'sources':['crossref'],'start_date':'2025-06-01'},self.root/'run',True,10)
        self.assertEqual(d['status'],'failed')
    def test_upstream_dataclass_module_import(self):
        code='from __future__ import annotations\nfrom dataclasses import dataclass\n@dataclass\nclass Item:\n    title: str\ndef search_papers(**kwargs):\n    return {"crossref":[{"title":Item("SYNTHETIC dataclass").title}]}\n'
        self.enable('researchstudio.paper-search',code)
        d=b.run_adapter(b.find_provider(REG,'researchstudio.paper-search'),self.config,{'query':'synthetic','start_year':2025,'end_year':2026,'sources':['crossref']},self.root/'run',True,10)
        self.assertEqual(d['status'],'executed_needs_review')
    def test_generation_is_clean(self):
        for rel,content in build.generated().items():self.assertEqual((ROOT/rel).read_bytes(),content,rel)
    def test_generation_drift_detectable(self):
        local=self.root/'copy';shutil.copytree(ROOT,local,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        rel='skills/journal-intelligence/scripts/provider_runtime.py';f=local/rel;before=f.read_bytes()+b'\n# SYNTHETIC drift\n';f.write_bytes(before)
        proc=subprocess.run([sys.executable,str(local/'scripts/build_release.py'),'--check'],capture_output=True,text=True,timeout=10)
        self.assertEqual(proc.returncode,1);self.assertIn(rel,json.loads(proc.stdout)['paths']);self.assertEqual(f.read_bytes(),before)
    def test_all_19_scientific_protocol_sections_retained(self):
        expected=b.load(ROOT/'tests/fixtures/protocol-sections.json');self.assertEqual(len(expected),19)
        import re
        for name, sections in expected.items():
            text=(ROOT/'skills'/name/'references/protocol.md').read_text()
            actual=re.findall(r'^#{2,3} (.+)$',text,re.M)
            for section in sections:self.assertIn(section,actual,(name,section))
    def test_30_writing_steps_preserved(self):
        import re
        text=(ROOT/'skills/manuscript-writing/references/protocol.md').read_text()
        self.assertEqual([int(x) for x in re.findall(r'^### (\d+)\.',text,re.M)],list(range(1,31)))
    def test_core_no_fixed_agents_runtime(self):
        d=b.plan(self.task('journal-intelligence'),{'providers':{},'host_capabilities':[]},REG)
        self.assertFalse(d['subagents_required_by_this_bridge'])

class StandaloneAcceptanceTests(unittest.TestCase):pass

def isolated(skill):
    def test(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);module_dir=root/'standalone';shutil.copytree(skill,module_dir,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            inp=root/'input.md';inp.write_text('SYNTHETIC standalone task material')
            task={'capability':skill.name,'request':'SYNTHETIC contract test only','operation':'review','facts':{},'inputs':[{'path':str(inp)}],'requested_outputs':['report']}
            b.write(root/'task.json',task);b.write(root/'config.json',{'providers':{},'host_capabilities':[]})
            cmd=[sys.executable,'-S','-B',str(module_dir/'scripts/provider_runtime.py')]
            p=subprocess.run(cmd+['handoff','--task',str(root/'task.json'),'--config',str(root/'config.json'),'--out',str(root/'handoff')],capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,0,p.stderr)
            out=root/'report.md';out.write_text('SYNTHETIC test output')
            result={'capability':skill.name,'task_sha256':b.sha(root/'handoff/task.json'),'provider_id':'host_fallback','execution_mode':'host_fallback','execution_status':'executed',
                    'outputs':[{'role':'report','path':'report.md','sha256':b.sha(out)}],'reviews':[]}
            b.write(root/'result.json',result)
            p=subprocess.run(cmd+['accept-result','--dir',str(root/'handoff'),'--result',str(root/'result.json'),'--root',str(root)],capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,2,p.stdout+p.stderr);report=json.loads(p.stdout);self.assertFalse(report['passed']);self.assertTrue(any('Mandatory professional' in x for x in report['errors']));self.assertFalse(report['scientific_validity_certified'])
            self.assertFalse((root/'src').exists());self.assertFalse((root/'docs').exists())
    return test
for skill in sorted((ROOT/'skills').iterdir()):
    if skill.is_dir():setattr(StandaloneAcceptanceTests,'test_'+skill.name.replace('-','_')+'_portable_receipt',isolated(skill))

if __name__=='__main__':unittest.main()
