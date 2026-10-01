"""rc.4 deterministic tool/role contracts, not a scientific novelty evaluation."""
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
COMMON=ROOT/'src/common/scripts'
sys.path.insert(0,str(COMMON))
sys.path.insert(0,str(ROOT/'tests'))
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,COMMON/file)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
e=module('rc4_environment','environment.py');q=module('rc4_research31','research31.py');u=module('rc4_upstream','upstream.py')

def task(backend='python'):
    return {'request':'Manufactured engineering check only','service':'execute','runtime':{'backend':backend,'python_groups':['core']}}

class Tools(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_resources_are_dynamic_and_unknowns_are_not_claimed(self):
        r=e.resources(self.root)
        self.assertGreater(r['disk']['free_bytes'],0);self.assertTrue(r['architecture'])
        self.assertIn('memory_available_bytes',r);self.assertIn('runtimes_and_compilers',r)
        observed=e.plan(task())['observed'];self.assertTrue(observed['accelerators']['cpu']['available'])
        self.assertFalse(e.plan(task())['scientific_validity_certified'])
    def test_argv_uses_project_cwd_literal_arguments_and_actual_outputs(self):
        (self.root/'sub').mkdir();(self.root/'sub/input.txt').write_text('material')
        t=task();t['runtime']['cwd']='sub'
        code='import pathlib,sys; assert pathlib.Path("input.txt").read_text()=="material"; pathlib.Path("result.txt").write_text(sys.argv[1]); print(sys.executable)'
        literal='; $(touch SHOULD_NOT_EXIST)'
        r=e.run_command(t,self.root,['{python}','-c',code,literal],['sub/result.txt'],timeout=10)
        self.assertEqual(r['research_execution'],'passed');self.assertEqual((self.root/'sub/result.txt').read_text(),literal)
        self.assertFalse((self.root/'sub/SHOULD_NOT_EXIST').exists());self.assertFalse(r['execution']['shell'])
        self.assertEqual(r['execution']['cwd'],str((self.root/'sub').resolve()));self.assertGreater(r['execution']['wall_seconds'],0)
        self.assertTrue(r['outputs'][0]['created_or_changed']);self.assertEqual(len(r['outputs'][0]['sha256']),64)
        task_file=self.root/'task.json';task_file.write_text(json.dumps(t));receipt=self.root/'cli.json'
        process=subprocess.run([sys.executable,str(COMMON/'environment.py'),'exec','--task',str(task_file),'--workspace',str(self.root),'--cwd','sub','--report',str(receipt),'--output','sub/cli.txt','--','{python}','-c','from pathlib import Path; Path("cli.txt").write_text("actual CLI")'],capture_output=True,text=True)
        self.assertEqual(process.returncode,0,process.stdout+process.stderr)
        self.assertEqual(json.loads(receipt.read_text())['research_execution'],'passed')
    def test_missing_outputs_do_not_pass(self):
        r=e.run_command(task(),self.root,['{python}','-c','print("no result file")'],['absent.json'],timeout=10)
        self.assertEqual(r['research_execution'],'missing_outputs');self.assertEqual(r['missing_outputs'],['absent.json'])
    def test_output_and_cwd_escape_rejected(self):
        with self.assertRaises(e.EnvironmentError):e.run_command(task(),self.root,['{python}','-c','pass'],['../escape.json'])
        t=task();t['runtime']['cwd']='..'
        with self.assertRaises(e.EnvironmentError):e.run_command(t,self.root,['{python}','-c','pass'])
    def test_command_string_is_not_shell(self):
        with self.assertRaises(e.EnvironmentError):e.run_command(task(),self.root,'python -c pass')
    def test_cpu_calibration_checks_actual_numerical_output(self):
        r=e.calibrate(task(),self.root,'cpu',12,timeout=10)
        self.assertEqual(r['research_execution'],'passed');self.assertTrue(r['calibration']['numeric_check'])
        self.assertEqual(r['calibration']['value'],12**3);self.assertGreater(r['calibration']['compute_seconds'],0)
    @unittest.skipUnless(shutil.which('cc'),'C compiler unavailable')
    def test_compile_and_run_non_python_in_project(self):
        (self.root/'main.c').write_text('#include <stdio.h>\nint main(void){printf("%d\\n",7*8);return 0;}\n')
        r=e.run_command(task('c'),self.root,['cc','main.c','-o','solver'],['solver'],timeout=20)
        self.assertEqual(r['research_execution'],'passed')
        r=e.run_command(task('c'),self.root,['./solver'],timeout=10)
        self.assertEqual(Path(r['execution']['stdout']).read_text().strip(),'56')
    def test_prepared_managed_environment_runs_without_reinstall_permission(self):
        # Reuse the existing clearly synthetic offline-wheel fixture.
        sys.path.insert(0,str(ROOT/'tests'))
        from test_portability import wheel
        wheel(self.root/'wheels');t=task();t['runtime']['packages']=[{'spec':'academic_bootstrap_fixture==0.0.1','import':'academic_bootstrap_fixture'}]
        installed=e.ensure(t,self.root,apply=True,wheelhouse=self.root/'wheels',force_isolated=True,timeout=60)
        self.assertTrue(installed['ready'])
        r=e.run_command(t,self.root,['{python}','-c','import academic_bootstrap_fixture; print(academic_bootstrap_fixture.VALUE)'],timeout=20)
        self.assertEqual(r['research_execution'],'passed');self.assertFalse(r['installation_executed']);self.assertEqual(installed['python'],r['python'])
    def test_local_research_model_is_distinct_from_executor(self):
        t=task();t['research_model']={'role':'research_model','purpose':'prediction experiment','source':'upstream/model','revision':'v1','license':'BSD-3-Clause','local':True,'free_to_use':True,'license_allows_research':True}
        self.assertFalse(e.validate_roles(t)['assistant_switch_performed'])
        t['executor']={'role':'executor','assistant_target':'other'}
        with self.assertRaises(e.EnvironmentError):e.validate_roles(t)
    def test_worker_refuses_existing_output_before_import(self):
        script=self.root/'upstream.py';script.write_text('from pathlib import Path\nPath("SHOULD_NOT_EXIST").touch()\n')
        req=self.root/'request.json';req.write_text('{}');out=self.root/'raw.json';out.write_text('preserved')
        p=subprocess.run([sys.executable,str(COMMON/'provider_worker.py'),'--adapter','scipilot-profile','--script',str(script),'--request',str(req),'--out',str(out)],cwd=self.root,capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0);self.assertFalse((self.root/'SHOULD_NOT_EXIST').exists());self.assertEqual(out.read_text(),'preserved')

class Roles(unittest.TestCase):
    def candidate(self,id='primary',installed=False):
        return {'id':id,'repository':'Haojae/scipilot-figure-skill','entry':'SKILL.md','commit':'a'*40,'roles':['figure'],'available':True,'installed':installed,'domains':['statistics'],'tasks':['plot'],'materials':['table'],'outputs':['svg'],'missing_dependencies':[]}
    def test_installed_matching_primary_and_purposeful_complement(self):
        old=self.candidate('remote');local=self.candidate('local',True);second=self.candidate('independent',True)
        second.update(complement_role='independent_evaluation',selection_reason='Review axis/uncertainty choices independently')
        result=q.select_role('figure',[old,local,second],{'outputs':['svg']})
        self.assertEqual(result['primary']['id'],'local');self.assertEqual(result['complements'][0]['id'],'independent')
        self.assertFalse(result['guidance_read']);self.assertFalse(result['research_work_done']);self.assertFalse(result['functions_run'])
    def test_unavailable_or_wrong_material_never_selected(self):
        a=self.candidate();a['available']=False;b=self.candidate('wrong');b['materials']=['image']
        r=q.select_role('figure',[a,b],{'materials':['table']});self.assertIsNone(r['primary']);self.assertEqual(len(r['excluded']),2)
    def test_read_work_and_function_progress_are_separate(self):
        use={'mode':'native_in_host','status':'executed','progress':{'guidance_read':True,'research_work_done':False,'functions_run':True}}
        self.assertFalse(q.use_progress(use)['research_work_done'])
        legacy=q.use_progress({'mode':'adapted_in_host','status':'executed'})
        self.assertTrue(legacy['research_work_done']);self.assertIsNone(legacy['guidance_read']);self.assertIsNone(legacy['functions_run'])
        with self.assertRaises(q.ResearchError):q.use_progress({'progress':{'guidance_read':'true'}})
    def test_research_model_action_does_not_authorize_host_switch(self):
        a={'action':'train_local_model','role':'research_model','purpose':'held-out prediction','local':True,'free_to_use':True,'license_allows_research':True}
        self.assertTrue(q.host_action(a)['permitted_by_project_scope'])
        a['action']='discover_local_llm';self.assertTrue(q.host_action(a)['permitted_by_project_scope'])
        a['assistant_target']='other_assistant';self.assertFalse(q.host_action(a)['permitted_by_project_scope'])
    def test_external_wait_does_not_block_focused_internal_work(self):
        with tempfile.TemporaryDirectory() as root:
            r=q.assess({'mode':'focused','external_items':['Confirm author name']},root)
            self.assertEqual(r['status'],'ready_for_content_review');self.assertEqual(r['external_items'],['Confirm author name'])
            r=q.assess({'mode':'focused','research_work':['Validate a counterexample']},root)
            self.assertEqual(r['status'],'research_in_progress');self.assertIn('Validate a counterexample',r['next_actions'])
    def test_discovery_rejects_wrong_resolved_tree(self):
        def api(endpoint):
            if '/commits/' in endpoint:return {'sha':'a'*40,'commit':{'tree':{'sha':'b'*40}}}
            if '/git/trees/' in endpoint:return {'sha':'c'*40,'tree':[]}
            return {'full_name':'owner/repo','default_branch':'main'}
        with self.assertRaises(u.UpstreamError):u.discover('owner/repo',api=api)
    def test_bind_retains_commit_tree_blob(self):
        index=u.index_tree('owner/repo','a'*40,'b'*40,[{'path':'SKILL.md','type':'blob','mode':'100644','sha':'c'*40}])
        r=u.bind(index,'SKILL.md','research-design','plan')
        self.assertEqual(r['source_index']['tree_sha'],'b'*40);self.assertEqual(r['providers'][0]['discovered_file_blob_sha']['SKILL.md'],'c'*40)
    def test_assess_and_audit_cli_use_actual_result_link_checks(self):
        from test_result_links import Links
        fixture=Links();fixture.setUp()
        try:
            state={'mode':'focused','evidence_checks':[fixture.payload]}
            self.assertEqual(q.assess(state,fixture.root)['status'],'ready_for_content_review')
            source=fixture.root/'audit.json';source.write_text(json.dumps(fixture.payload));out=fixture.root/'audit-result.json'
            process=subprocess.run([sys.executable,str(COMMON/'research31.py'),'audit','--input',str(source),'--root',str(fixture.root),'--out',str(out)],capture_output=True,text=True)
            self.assertEqual(process.returncode,0,process.stderr);self.assertTrue(json.loads(out.read_text())['passed'])
            fixture.payload['links'][0]['numeric'][0]['text']='12.36'
            self.assertEqual(q.assess(state,fixture.root)['status'],'record_error')
            fixture.payload['links'][0]['numeric'][0]['text']='12.35';fixture.payload['sources'][0].pop('versions')
            pending=q.assess(state,fixture.root)
            self.assertEqual(pending['status'],'research_in_progress');self.assertTrue(pending['artifact_work'])
        finally:fixture.tearDown()

if __name__=='__main__':unittest.main(verbosity=2)
