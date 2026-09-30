"""alpha.4 local portability and setup tests; fixture studies are not evidence.

Includes real venv + offline pip installation of a clearly synthetic wheel,
not a download from a scientific provider. No host/model capability is invented.
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
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
env=module('alpha4_env',ROOT/'scripts/environment.py')
port=module('alpha4_port',ROOT/'scripts/portable_skill.py')
rr=module('alpha4_router',ROOT/'scripts/research_router.py')
b=module('alpha4_bridge',ROOT/'scripts/provider_runtime.py')
REG=b.load(ROOT/'tests/fixtures/legacy-provider-catalog.json')

def task(service='profile',backend=None,**kwargs):
    t={'capability':'data-preparation','service':service,'request':'SYNTHETIC task for software testing, not scientific evidence','operation':'execute',**kwargs}
    if backend:t['runtime']={'backend':backend}
    return t

def wheel(directory,name='academic_bootstrap_fixture',version='0.0.1'):
    """A local software fixture, never presented as an upstream scientific package."""
    directory.mkdir(parents=True,exist_ok=True);info=f'{name}-{version}.dist-info'
    target=directory/f'{name}-{version}-py3-none-any.whl'
    content={f'{name}/__init__.py':'VALUE = "SYNTHETIC_INSTALL_FIXTURE"\n',
       f'{info}/METADATA':f'Metadata-Version: 2.1\nName: {name}\nVersion: {version}\nSummary: Synthetic offline installation test, not research\n',
       f'{info}/WHEEL':'Wheel-Version: 1.0\nGenerator: academic-local-test\nRoot-Is-Purelib: true\nTag: py3-none-any\n'}
    content[f'{info}/RECORD']='\n'.join(f'{p},,' for p in content)+f'\n{info}/RECORD,,\n'
    with zipfile.ZipFile(target,'w') as z:
        for p,c in content.items():z.writestr(p,c)
    return target

class Base(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()

class SelectionTests(Base):
    def test_journal_has_no_python_installs(self):
        t=task('matching',capability='journal-intelligence');r=env.requirements_for(t)
        self.assertEqual(r['backend'],'host');self.assertEqual(r['packages'],[])
    def test_method_plan_not_forced_to_statistical_stack(self):
        self.assertEqual(env.requirements_for(task('method-plan'))['packages'],[])
    def test_theory_no_forced_dependencies(self):
        t=task('derive',research_context={'study_types':['theory-proof']})
        self.assertEqual(env.requirements_for(t)['packages'],[])
    def test_humanities_no_ml_dependencies(self):
        self.assertEqual(env.requirements_for(task('interpret'))['packages'],[])
    def test_profile_minimal_packages(self):
        r=env.requirements_for(task());self.assertEqual({p['distribution'] for p in r['packages']},{'numpy','pandas'})
    def test_plot_scipilot_uses_verified_requirements(self):
        r=env.requirements_for(task('plot',preferred_provider='scipilot.figure'))
        self.assertEqual(len(r['packages']),7);self.assertNotIn('torch',[p['distribution'] for p in r['packages']])
    def test_unknown_method_requires_selection(self):
        r=env.plan(task('analyze'));self.assertEqual(r['status'],'needs_host_setup');self.assertEqual(r['requirements']['packages'],[])
    def test_regression_preset_selected_by_method(self):
        t=task('analyze',research_context={'method_family':'regression'})
        self.assertIn('statsmodels',[p['distribution'] for p in env.requirements_for(t)['packages']])
    def test_unknown_group_rejected(self):
        with self.assertRaises(env.EnvironmentError):env.requirements_for(task(runtime={'backend':'python','python_groups':['invented']}))
    def test_no_python_packages_installed_for_r(self):
        with self.assertRaises(env.EnvironmentError):env.requirements_for(task(runtime={'backend':'r','python_groups':['tabular']}))
    def test_required_binaries_not_commands(self):
        with self.assertRaises(env.EnvironmentError):env.requirements_for(task(runtime={'required_binaries':['Rscript; rm']}))
    def test_exact_package_spec_supported(self):
        self.assertTrue(env.version_ok('2.3.5','numpy==2.3.5'));self.assertFalse(env.version_ok('2.3.4','numpy==2.3.5'))
    def test_non_numeric_version_not_silently_accepted(self):
        self.assertFalse(env.version_ok('2.0rc1','numpy>=2.0'))
    def test_package_injection_rejected(self):
        for spec in ['--extra-index-url=https://bad.invalid','numpy; rm -rf x','x @ https://bad.invalid','-e .','git+https://bad.invalid']:
            with self.subTest(spec=spec),self.assertRaises(env.EnvironmentError):env.validate_packages([{'spec':spec,'import':'x'}])
    def test_module_injection_rejected(self):
        with self.assertRaises(env.EnvironmentError):env.validate_packages([{'spec':'numpy','import':'numpy;print(1)'}])
    def test_conflicting_explicit_specs_rejected(self):
        with self.assertRaises(env.EnvironmentError):env.validate_packages([{'spec':'numpy==1.0','import':'numpy'},{'spec':'numpy==2.0','import':'numpy'}])
    def test_text_only_never_probes_or_installs(self):
        with patch.object(env,'probe',side_effect=AssertionError('must not probe a claimed text-only model')):
            r=env.ensure(task(host={'mode':'text-only'}),self.root,apply=True,allow_network=True)
        self.assertEqual(r['status'],'needs_external_executor');self.assertFalse(r['installation_executed'])
    def test_doctor_does_not_create_workspace(self):
        p=self.root/'untouched';r=env.plan(task('matching'))
        self.assertFalse(p.exists());self.assertFalse(r['installation_executed']);self.assertEqual(r['observed']['host_features']['vision'],'not_probed')
    def test_missing_dependency_dry_run_no_install(self):
        t=task(runtime={'backend':'python','packages':[{'spec':'academic_missing_fixture==0.0.1','import':'academic_missing_fixture'}]})
        r=env.ensure(t,self.root/'new');self.assertEqual(r['status'],'install_needed');self.assertFalse((self.root/'new').exists())
    def test_missing_network_authorization_no_environment(self):
        t=task(runtime={'backend':'python','packages':[{'spec':'academic_missing_fixture==0.0.1','import':'academic_missing_fixture'}]})
        r=env.ensure(t,self.root/'new',apply=True);self.assertEqual(r['status'],'blocked_network_authorization');self.assertFalse((self.root/'new').exists())
    def test_windows_venv_path(self):
        self.assertEqual(env.venv_python(self.root,'nt'),self.root/'Scripts/python.exe')
    def test_posix_venv_path(self):
        self.assertEqual(env.venv_python(self.root,'posix'),self.root/'bin/python')
    def test_refuse_environment_path_escape(self):
        with self.assertRaises(env.EnvironmentError):env._managed_dir(self.root,'../escape')
    def test_interpreter_symlink_not_collapsed(self):
        p=self.root/'python';p.symlink_to(sys.executable)
        self.assertEqual(env.python_path(p),str(p.absolute()))

class InstallTests(Base):
    def fixture_task(self,name='academic_bootstrap_fixture'):
        return task(runtime={'backend':'python','packages':[{'spec':name+'==0.0.1','import':name}]})
    def test_real_offline_install_verify_reuse_and_execute(self):
        wheel(self.root/'wheels');t=self.fixture_task();before=importlib.util.find_spec('academic_bootstrap_fixture')
        r=env.ensure(t,self.root/'project',apply=True,wheelhouse=self.root/'wheels',force_isolated=True,timeout=60)
        self.assertEqual(r['status'],'environment_verified');self.assertTrue(r['created_venv']);self.assertTrue(r['installation_executed'])
        self.assertIsNone(before);self.assertIsNone(importlib.util.find_spec('academic_bootstrap_fixture'))
        python=r['python'];self.assertNotEqual(Path(python),Path(sys.executable))
        self.assertTrue((Path(r['logs'])/'pip-install-report.json').is_file())
        r2=env.ensure(t,self.root/'project',apply=True,wheelhouse=self.root/'wheels',force_isolated=True,timeout=60)
        self.assertEqual(r2['python'],python);self.assertTrue(r2['reused_managed_venv']);self.assertFalse(r2['installation_executed'])
        script=self.root/'run.py';script.write_text('import academic_bootstrap_fixture,sys\nprint(academic_bootstrap_fixture.VALUE)\nprint(sys.executable)\n')
        r3=env.run_script(t,self.root/'project',script,apply=True,wheelhouse=self.root/'wheels',force_isolated=True,timeout=60)
        self.assertEqual(r3['research_execution'],'passed')
        output=Path(r3['execution']['stdout']).read_text()
        self.assertIn('SYNTHETIC_INSTALL_FIXTURE',output);self.assertIn(python,output)
    def test_failed_install_prevents_research_script(self):
        (self.root/'empty-wheelhouse').mkdir();t=self.fixture_task('academic_absent_test_fixture');sentinel=self.root/'SHOULD_NOT_EXIST'
        script=self.root/'run.py';script.write_text(f'from pathlib import Path\nPath({str(sentinel)!r}).write_text("BAD")\n')
        r=env.run_script(t,self.root/'project',script,apply=True,wheelhouse=self.root/'empty-wheelhouse',timeout=60)
        self.assertEqual(r['research_execution'],'not_started');self.assertEqual(r['status'],'installation_failed');self.assertFalse(sentinel.exists())
        self.assertTrue(Path(r['logs']).is_dir());self.assertTrue(r['steps'])
    def test_missing_binary_blocks_install(self):
        t=task(runtime={'backend':'python','python_groups':['core'],'required_binaries':['academic_fixture_missing_executable']})
        r=env.ensure(t,self.root/'new',apply=True)
        self.assertEqual(r['status'],'needs_host_setup');self.assertFalse((self.root/'new').exists())
    def test_timeout_stops_explicit_script(self):
        script=self.root/'sleep.py';script.write_text('import time\ntime.sleep(10)\n')
        r=env._run([sys.executable,str(script)],self.root/'logs','timeout',0.1)
        self.assertEqual(r['status'],'timeout');self.assertIsNone(r['returncode'])
    def test_managed_marker_required(self):
        t=task(runtime={'backend':'python','python_groups':['core']});p=env.plan(t);req=p['requirements']
        identity={'requirements':req,'python':p['observed']['python'],'base_python':p['observed']['executable'],'platform':p['observed']['platform'],'machine':p['observed']['machine']}
        target=self.root/'.academic/envs'/env.digest(identity)[:16];target.mkdir(parents=True)
        with self.assertRaises(env.EnvironmentError):env.ensure(t,self.root,apply=True,force_isolated=True)
    def test_negative_timeout_rejected(self):
        with self.assertRaises(env.EnvironmentError):env.ensure(task(),self.root,timeout=-1)

class ResearchTypeTests(Base):
    def test_sixteen_profiles_have_evidence_and_boundaries(self):
        book=json.loads(rr.catalog_path().read_text());self.assertEqual(len(book['profiles']),16)
        for id,p in book['profiles'].items():
            with self.subTest(id=id):self.assertTrue(p['evidence_objects']);self.assertTrue(p['obligations']);self.assertTrue(p['do_not_force'])
    def test_unknown_type_not_promoted_to_ml(self):
        r=rr.route(task(research_context={'study_types':['custom-specialty']}))
        self.assertEqual(r['status'],'needs_specialist_mapping');self.assertEqual(r['profiles'],[]);self.assertFalse(r['forced_pipeline'])
    def test_unclassified_type_uses_general_guidance(self):
        self.assertEqual(rr.route(task())['status'],'general_guidance')
    def test_mixed_types_preserve_both(self):
        r=rr.route(task(research_context={'study_types':['qualitative','quantitative-observational']}))
        self.assertEqual(len(r['profiles']),2);self.assertEqual(r['mandatory_install_groups'],[])
    def test_planning_not_blocked_by_uncollected_data(self):
        t=task('method-plan',research_context={'study_types':['quantitative-observational']})
        self.assertEqual(rr.route(t)['evidence_to_confirm'],[])
    def test_theory_permitted_without_csv(self):
        t=task('derive',capability='analysis-execution',facts={'has_formal_statement':True})
        r=b.plan(t,{'providers':{},'host_capabilities':[]},REG)
        self.assertEqual(r['evidence_blocks'],[]);self.assertEqual(r['status'],'fallback_needed');self.assertIsNone(r['selected_provider'])
    def test_humanities_permitted_with_actual_source_condition(self):
        t=task('interpret',capability='analysis-execution',facts={'has_primary_sources':True})
        self.assertEqual(b.plan(t,{'providers':{},'host_capabilities':[]},REG)['evidence_blocks'],[])
    def test_profile_label_alone_not_evidence(self):
        t=task('derive',capability='analysis-execution',research_context={'study_types':['theory-proof']})
        self.assertEqual(b.plan(t,{'providers':{},'host_capabilities':[]},REG)['status'],'blocked_evidence')
    def test_numeric_analysis_still_needs_data(self):
        t=task('analyze',capability='analysis-execution',facts={'has_sources':True})
        self.assertEqual(b.plan(t,{'providers':{},'host_capabilities':[]},REG)['status'],'blocked_evidence')
    def test_humanities_profile_does_not_require_graphs_or_imrad(self):
        r=rr.route(task(research_context={'study_types':['humanities-interpretive']}))
        self.assertEqual(r['profiles'][0]['evidence_objects'],['primary-sources']);self.assertIn('IMRaD',' '.join(r['profiles'][0]['do_not_force']))

class PortableTests(Base):
    def test_copy_dry_run_idempotence_no_host_claim(self):
        src=ROOT/'skills/journal-intelligence';dest=self.root/'host-skills'
        r=port.install(src,dest);self.assertEqual(r['status'],'copy_planned');self.assertFalse(dest.exists())
        r=port.install(src,dest,True);self.assertEqual(r['status'],'files_installed');self.assertFalse(r['native_host_verified'])
        self.assertEqual(port.install(src,dest,True)['status'],'files_already_present')
    def test_copy_never_overwrites_changed_skill(self):
        src=ROOT/'skills/journal-intelligence';dest=self.root/'host';port.install(src,dest,True)
        (dest/src.name/'SKILL.md').write_text((dest/src.name/'SKILL.md').read_text()+'\nEdited\n')
        with self.assertRaises(port.PortableError):port.install(src,dest,True)
    def test_copy_refuses_recursive_overlap(self):
        src=ROOT/'skills/journal-intelligence'
        with self.assertRaises(port.PortableError):port.install(src,src/'nested')
    def test_text_export_self_contained_core_and_selected_type(self):
        out=self.root/'prompt.md';r=port.export_prompt(ROOT/'skills/manuscript-writing',out,['humanities-interpretive'],detail=True)
        text=out.read_text();self.assertIn('30. 最终交付',text);self.assertIn('humanities-interpretive',text);self.assertIn('真实材料',text)
        self.assertFalse(r['host_tools_created']);self.assertFalse(r['execution_performed'])
    def test_export_does_not_overwrite(self):
        out=self.root/'x.md';out.write_text('existing')
        with self.assertRaises(port.PortableError):port.export_prompt(ROOT/'skills/manuscript-writing',out)
    def test_source_fetch_requires_commit_not_blob_or_branch(self):
        with self.assertRaises(port.PortableError):port.fetch_provider('scipilot.figure','main',self.root/'source',registry=REG)
    def test_source_fetch_requires_authorized_network(self):
        r=port.fetch_provider('scipilot.figure','a'*40,self.root/'source',apply=True,registry=REG)
        self.assertEqual(r['status'],'blocked_network_authorization');self.assertFalse((self.root/'source').exists())
    def test_source_fetch_preserves_unknown_provider(self):
        with self.assertRaises(port.PortableError):port.fetch_provider('fictional','a'*40,self.root,registry=REG)
    def test_real_local_git_mirror_checkout_not_execution(self):
        mirror=self.root/'mirror';mirror.mkdir();(mirror/'SKILL.md').write_text('Synthetic source checkout fixture, not a scientific skill')
        commands=[['git','init',str(mirror)],['git','-C',str(mirror),'add','SKILL.md'],['git','-C',str(mirror),'-c','user.name=Local Fixture','-c','user.email=fixture@invalid','commit','-m','synthetic test']]
        for c in commands:subprocess.run(c,check=True,capture_output=True)
        commit=subprocess.check_output(['git','-C',str(mirror),'rev-parse','HEAD'],text=True).strip()
        registry={'providers':[{'id':'synthetic.provider','repo':'synthetic/provider','required_paths':['SKILL.md']}]}
        r=port.fetch_provider('synthetic.provider',commit,self.root/'checkout',apply=True,mirror=mirror,registry=registry)
        self.assertEqual(r['status'],'source_checked_out_needs_review');self.assertFalse(r['runtime_installed']);self.assertFalse(r['source_reviewed']);self.assertEqual((self.root/'checkout/SKILL.md').read_text(),(mirror/'SKILL.md').read_text())
    def test_all_19_standalone_setup_and_profile_resources(self):
        for src in sorted((ROOT/'skills').iterdir()):
            if not src.is_dir():continue
            with self.subTest(skill=src.name):
                dest=self.root/src.name;shutil.copytree(src,dest,ignore=shutil.ignore_patterns('__pycache__'))
                for f in ['scripts/environment.py','scripts/research_router.py','scripts/portable_skill.py','assets/environment-profiles.json','assets/research-profiles.json','references/environment-setup.md']:
                    self.assertTrue((dest/f).is_file(),f)
                inp=self.root/(src.name+'.json');inp.write_text(json.dumps(task('method-plan')))
                p=subprocess.run([sys.executable,'-S',str(dest/'scripts/environment.py'),'plan','--task',str(inp)],capture_output=True,text=True,timeout=20)
                self.assertEqual(p.returncode,0,p.stdout+p.stderr);self.assertEqual(json.loads(p.stdout)['requirements']['packages'],[])
                p=subprocess.run([sys.executable,'-S',str(dest/'scripts/research_router.py'),'--task',str(inp)],capture_output=True,text=True,timeout=20)
                self.assertEqual(p.returncode,0,p.stdout+p.stderr)

if __name__=='__main__':unittest.main(verbosity=2)
