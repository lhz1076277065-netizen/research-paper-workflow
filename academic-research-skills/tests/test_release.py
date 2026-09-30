"""Release regressions: local software fixtures, not empirical research or host A/B."""
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import portable_skill as p
import upstream as u
import environment as e
import provider_runtime as b

class Work(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def mirror(self):
        d=self.root/'mirror';d.mkdir();(d/'SKILL.md').write_text('---\nname: example\ndescription: Synthetic local fixture\n---\n')
        (d/'references').mkdir();(d/'references/guide.md').write_text('Synthetic support')
        for c in [['git','init',str(d)],['git','-C',str(d),'add','.'],['git','-C',str(d),'-c','user.name=Fixture','-c','user.email=fixture@invalid','commit','-m','synthetic']]:
            subprocess.run(c,check=True,capture_output=True)
        commit=subprocess.check_output(['git','-C',str(d),'rev-parse','HEAD'],text=True).strip()
        rows=[]
        for path in ['SKILL.md','references/guide.md']:
            data=(d/path).read_bytes();h=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            rows.append({'path':path,'type':'blob','mode':'100644','sha':h,'size':len(data)})
        return d,u.index_tree('synthetic/source',commit,'b'*40,rows)
    def checkout(self):
        mirror,index=self.mirror();dest=self.root/'checkout'
        r=u.fetch_snapshot(index,'SKILL.md',dest,apply=True,mirror=mirror,support=['references/guide.md'])
        self.assertEqual(r['status'],'source_checked_out_needs_review')
        return mirror,index,dest,r
    def handoff(self,required=(),scopes=None):
        task={'capability':'journal-intelligence','service':'matching','request':'Synthetic handoff, not actual journal advice',
              'operation':'review','requested_outputs':['figure','text'],'required_reviews':list(required)}
        if scopes is not None:task['required_review_outputs']=scopes
        directory=self.root/'handoff';reg=b.load(ROOT/'docs/provider-catalog.json')
        b.prepare_handoff(task,{},reg,directory)
        for file in ['figure.txt','text.txt']:(self.root/file).write_text('Synthetic artifact '+file)
        result={'capability':task['capability'],'task_sha256':b.sha(directory/'task.json'),'provider_id':'host_fallback',
                'execution_mode':'host_fallback','execution_status':'executed','outputs':[
                 {'role':'figure','path':'figure.txt','sha256':b.sha(self.root/'figure.txt')},
                 {'role':'text','path':'text.txt','sha256':b.sha(self.root/'text.txt')}], 'reviews':[]}
        return directory,result
    def review(self,kind,roles):
        (self.root/(kind+'.md')).write_text('Synthetic review record; not scientific verification')
        return {'kind':kind,'status':'passed','performed_by':'host_agent','checked_at':'2026-09-30T00:00:00Z',
                'coverage':'Synthetic selected role check','report_path':kind+'.md','report_sha256':b.sha(self.root/(kind+'.md')),
                'reviewed_outputs':{role:b.sha(self.root/({'figure':'figure.txt','text':'text.txt'}[role])) for role in roles}}

class DynamicCheckout(Work):
    def test_fetch_bind_identity_matches(self):
        _,index,_,r=self.checkout();reg=u.bind(index,'SKILL.md','research-design','plan')
        pid=reg['providers'][0]['id'];self.assertIn(pid,r['configuration_fragment']['providers'])
    def test_fetch_config_to_plan_end_to_end(self):
        _,index,_,r=self.checkout();reg=u.bind(index,'SKILL.md','research-design','plan',support=['references/guide.md'])
        decision=b.plan({'capability':'research-design','service':'plan','operation':'plan','request':'Synthetic task'},r['configuration_fragment'],reg)
        self.assertEqual(decision['status'],'prepared_not_executed')
    def test_existing_clean_snapshot_reused_offline(self):
        mirror,index,dest,r=self.checkout()
        again=u.fetch_snapshot(index,'SKILL.md',dest,apply=True,mirror=mirror)
        self.assertEqual(again['status'],'source_reused_needs_review');self.assertFalse(again['network_used'])
    def test_modified_tracked_source_preserved(self):
        mirror,index,dest,_=self.checkout();(dest/'SKILL.md').write_text('USER CHANGES')
        again=u.fetch_snapshot(index,'SKILL.md',dest,apply=True,mirror=mirror)
        self.assertEqual(again['status'],'source_local_changes');self.assertEqual((dest/'SKILL.md').read_text(),'USER CHANGES')
    def test_added_file_preserved(self):
        mirror,index,dest,_=self.checkout();(dest/'new.txt').write_text('user notes')
        again=u.fetch_snapshot(index,'SKILL.md',dest,apply=True,mirror=mirror)
        self.assertEqual(again['status'],'source_local_changes');self.assertEqual((dest/'new.txt').read_text(),'user notes')
    def test_mismatched_index_not_marked_configured(self):
        mirror,index=self.mirror();index['files']['SKILL.md']['blob_sha']='c'*40
        r=u.fetch_snapshot(index,'SKILL.md',self.root/'checkout',apply=True,mirror=mirror)
        self.assertEqual(r['status'],'source_index_mismatch');self.assertIsNone(r['configuration_fragment'])
    def test_support_must_exist_in_index(self):
        _,index=self.mirror()
        with self.assertRaises(u.UpstreamError):u.fetch_snapshot(index,'SKILL.md',self.root/'out',support=['unknown.md'])
    def test_timeout_is_passed_to_git(self):
        mirror,index=self.mirror();real=subprocess.run;seen=[]
        def run(*a,**kw):seen.append(kw.get('timeout'));return real(*a,**kw)
        with patch.object(p.subprocess,'run',side_effect=run):u.fetch_snapshot(index,'SKILL.md',self.root/'d',apply=True,mirror=mirror,timeout=9)
        self.assertTrue(seen);self.assertTrue(all(x==9 for x in seen))
    def test_nan_timeout_rejected(self):
        with self.assertRaises(u.UpstreamError):u.GitHubAPI(timeout=float('nan'))
    def test_infinite_fetch_timeout_rejected(self):
        _,index=self.mirror()
        with self.assertRaises(p.PortableError):u.fetch_snapshot(index,'SKILL.md',self.root/'d',timeout=float('inf'))
    def test_relative_dot_not_file(self):
        with self.assertRaises(u.UpstreamError):u.relpath('.')
    def test_snapshot_dry_run_does_not_create_directory(self):
        _,index=self.mirror();r=u.fetch_snapshot(index,'SKILL.md',self.root/'d')
        self.assertEqual(r['status'],'source_fetch_planned');self.assertFalse((self.root/'d').exists())

class PortabilityFixes(Work):
    def minimal(self,quoted=False):
        src=self.root/'small-skill';src.mkdir();name='"small-skill"' if quoted else 'small-skill'
        (src/'SKILL.md').write_text('---\nname: '+name+'\ndescription: Local fixture\n---\nDo the task.\n')
        return src
    def test_minimal_external_skill_exports_without_our_assets(self):
        src=self.minimal();r=p.export_prompt(src,self.root/'prompt.md')
        self.assertEqual(r['included_resources'],['SKILL.md'])
    def test_quoted_valid_name_supported(self):
        src=self.minimal(True);self.assertEqual(p.inventory(src)[1],'small-skill')
    def test_unclosed_frontmatter_rejected(self):
        src=self.minimal();(src/'SKILL.md').write_text('---\nname: small-skill\ndescription: missing close')
        with self.assertRaises(p.PortableError):p.inventory(src)
    def test_installer_preserves_executable_bit(self):
        src=self.minimal();script=src/'run.sh';script.write_text('#!/bin/sh\nexit 0\n');script.chmod(0o755)
        dest=self.root/'install';p.install(src,dest,True)
        self.assertEqual((dest/src.name/'run.sh').stat().st_mode & 0o111,script.stat().st_mode & 0o111)
    def test_desktop_metadata_excluded(self):
        src=self.minimal();(src/'.DS_Store').write_bytes(b'local desktop state');p.install(src,self.root/'out',True)
        self.assertFalse((self.root/'out/small-skill/.DS_Store').exists())
    def test_local_build_version_satisfies_numeric_minimum(self):self.assertTrue(e.version_ok('2.3.1+cpu','torch>=2.0'))
    def test_local_build_public_pin(self):self.assertTrue(e.version_ok('2.3.1+cu128','torch==2.3.1'))
    def test_prerelease_not_silently_final(self):self.assertFalse(e.version_ok('2.3.1rc1','torch>=2.3.1'))
    def test_scoped_review_schema_present(self):
        schema=json.loads((ROOT/'assets/task.schema.json').read_text());self.assertIn('required_review_outputs',schema['properties'])

class ScopedReviews(Work):
    def test_figure_only_required_review(self):
        d,r=self.handoff(['visual'],{'visual':['figure']});r['reviews']=[self.review('visual',['figure'])]
        self.assertTrue(b.accept_result(d,r,self.root)['passed'])
    def test_separate_review_responsibilities(self):
        d,r=self.handoff(['visual','semantic'],{'visual':['figure'],'semantic':['text']})
        r['reviews']=[self.review('visual',['figure']),self.review('semantic',['text'])]
        self.assertTrue(b.accept_result(d,r,self.root)['passed'])
    def test_unscoped_required_review_retains_old_coverage(self):
        d,r=self.handoff(['visual']);r['reviews']=[self.review('visual',['figure'])]
        self.assertFalse(b.accept_result(d,r,self.root)['passed'])
    def test_optional_review_can_be_partial(self):
        d,r=self.handoff();r['reviews']=[self.review('semantic',['text'])]
        self.assertTrue(b.accept_result(d,r,self.root)['passed'])
    def test_scoped_review_wrong_version_rejected(self):
        d,r=self.handoff(['visual'],{'visual':['figure']});review=self.review('visual',['figure']);review['reviewed_outputs']['figure']='0'*64;r['reviews']=[review]
        self.assertFalse(b.accept_result(d,r,self.root)['passed'])
    def test_empty_scope_rejected(self):
        d,r=self.handoff(['visual'],{'visual':[]})
        with self.assertRaises(b.ContractError):b.accept_result(d,r,self.root)
    def test_unknown_output_scope_rejected(self):
        d,r=self.handoff(['visual'],{'visual':['missing']})
        with self.assertRaises(b.ContractError):b.accept_result(d,r,self.root)
    def test_deterministic_image_check_not_visual_observation(self):
        d,r=self.handoff(['visual'],{'visual':['figure']});review=self.review('visual',['figure']);review['performed_by']='deterministic_tool';r['reviews']=[review]
        self.assertFalse(b.accept_result(d,r,self.root)['passed'])

class ScopeAndCoverage(Work):
    def test_dynamic_schematic_route_not_unconditionally_blocked(self):
        src=self.root/'provider';src.mkdir();text='---\nname: schematic\ndescription: Fixture\n---\n'
        (src/'SKILL.md').write_text(text);h=hashlib.sha1(b'blob '+str(len(text.encode())).encode()+b'\0'+text.encode()).hexdigest()
        index=u.index_tree('test/diagram','a'*40,'b'*40,[{'path':'SKILL.md','type':'blob','mode':'100644','sha':h}])
        reg=u.bind(index,'SKILL.md','scientific-visualization','schematic');pid=reg['providers'][0]['id']
        t={'capability':'scientific-visualization','service':'schematic','request':'Diagram of the supplied mechanism','facts':{'schematic_only':True}}
        r=b.plan(t,{'providers':{pid:{'root':str(src)}}},reg)
        self.assertEqual(r['selected_provider'],pid)
    def test_all_protocol_headings_preserved(self):
        book=json.loads((ROOT/'release/coverage-baseline.json').read_text())
        for name,headings in book['protocol_headings'].items():
            text=(ROOT/'skills'/name/'references/protocol.md').read_text()
            for h in headings:self.assertIn(h,text,name)
    def test_all_entries_stay_short(self):
        for f in (ROOT/'skills').glob('*/SKILL.md'):self.assertLess(len(f.read_text()),850)
    def test_no_hardware_or_host_pin_in_entries(self):
        for f in (ROOT/'skills').glob('*/SKILL.md'):
            text=f.read_text().lower()
            for s in ['m5max','128gb','4t 硬盘','spawn_agent','gpt-6','claude-project-dir']:self.assertNotIn(s,text)
    def test_release_version_all_entries(self):
        for f in (ROOT/'skills').glob('*/SKILL.md'):self.assertIn('version: "'+(ROOT/'VERSION').read_text().strip()+'"',f.read_text())


class EnvironmentRecovery(Work):
    def test_managed_package_can_resume_without_network_or_wheelhouse(self):
        from test_portability import wheel
        wheels=self.root/'wheels';wheel(wheels)
        task={'request':'Synthetic offline environment reuse','runtime':{'backend':'python','packages':[{'spec':'academic_bootstrap_fixture==0.0.1','import':'academic_bootstrap_fixture'}]}}
        first=e.ensure(task,self.root,apply=True,wheelhouse=wheels,force_isolated=True)
        self.assertTrue(first['ready'])
        again=e.ensure(task,self.root,apply=True,force_isolated=True)
        self.assertTrue(again['ready']);self.assertEqual(first['python'],again['python']);self.assertFalse(again['installation_executed'])
    def test_interrupted_owned_venv_creation_is_repairable(self):
        task={'request':'Synthetic interrupted venv','runtime':{'backend':'python','python_groups':['core']}}
        planned=e.plan(task);obs=planned['observed'];identity={'requirements':planned['requirements'],'python':obs['python'],'base_python':obs['executable'],'platform':obs['platform'],'machine':obs['machine']}
        dest=self.root/'.academic/envs'/e.digest(identity)[:16];dest.mkdir(parents=True)
        e.write(dest/'.academic-managed.json',{'identity':identity,'status':'creating'})
        result=e.ensure(task,self.root,apply=True,force_isolated=True)
        self.assertTrue(result['ready']);self.assertTrue(any('repair-venv' in x['stdout'] for x in result['steps']))

class PublicAPICompatibility(Work):
    def test_invalid_quoted_name_rejected(self):
        src=self.root/'name';src.mkdir();(src/'SKILL.md').write_text('---\nname: "name\'\ndescription: x\n---\n')
        with self.assertRaises(p.PortableError):p.inventory(src)
    def test_missing_description_rejected(self):
        src=self.root/'name';src.mkdir();(src/'SKILL.md').write_text('---\nname: name\n---\n')
        with self.assertRaises(p.PortableError):p.inventory(src)
    def test_large_text_contents_none_uses_indexed_blob(self):
        import base64
        text='Current source';raw=text.encode();h=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        index=u.index_tree('team/repo','a'*40,'b'*40,[{'path':'SKILL.md','type':'blob','mode':'100644','sha':h}])
        calls=[]
        def api(path):
            calls.append(path)
            if '/contents/' in path:return {'type':'file','encoding':'none','sha':h}
            return {'encoding':'base64','sha':h,'content':base64.b64encode(raw).decode()}
        self.assertEqual(u.read_source(index,'SKILL.md',api=api),text);self.assertTrue(calls[-1].endswith('/git/blobs/'+h))
    def test_transient_http_retried_but_no_model_claim(self):
        import io
        from urllib.error import HTTPError
        errors=[HTTPError('https://api.github.com/repos/a/b',503,'temporary',{},None),io.BytesIO(b'{"ok":true}')]
        with patch.object(u,'urlopen',side_effect=errors),patch.object(u.time,'sleep'):
            self.assertTrue(u.GitHubAPI(allow_network=True)('/repos/a/b')['ok'])
    def test_permission_error_not_retried(self):
        from urllib.error import HTTPError
        with patch.object(u,'urlopen',side_effect=HTTPError('https://api.github.com/repos/a/b',403,'permission',{},None)) as call:
            with self.assertRaises(u.UpstreamError):u.GitHubAPI(allow_network=True)('/repos/a/b')
            self.assertEqual(call.call_count,1)
    def test_long_rate_limit_does_not_hang(self):
        from urllib.error import HTTPError
        exc=HTTPError('https://api.github.com/repos/a/b',429,'limited',{'Retry-After':'600'},None)
        with patch.object(u,'urlopen',side_effect=exc),patch.object(u.time,'sleep') as sleep:
            with self.assertRaises(u.UpstreamError):u.GitHubAPI(allow_network=True)('/repos/a/b')
            sleep.assert_not_called()

class WorkgraphAutonomy(Work):
    def graph(self,tasks):return {'schema_version':'workgraph-1','revision':0,'tasks':tasks}
    def load_graph_tool(self):
        spec=importlib.util.spec_from_file_location('release_workgraph',ROOT/'scripts/workgraph.py')
        g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g);return g
    def test_no_implicit_single_attempt_limit(self):
        g=self.load_graph_tool();r=g.assess(self.graph([{'id':'new-method','status':'failed','attempts':4}]),self.root)
        self.assertEqual(r['ready'],['new-method'])
    def test_explicit_attempt_budget_still_respected(self):
        g=self.load_graph_tool();r=g.assess(self.graph([{'id':'new-method','status':'failed','attempts':4,'max_attempts':4}]),self.root)
        self.assertEqual(r['tasks']['new-method']['status'],'budget_exhausted')
    def test_ready_writer_conflict_with_running_writer(self):
        g=self.load_graph_tool();r=g.assess(self.graph([{'id':'writing','status':'running','write_paths':['paper']},{'id':'figure','write_paths':['paper/fig.svg']}]),self.root)
        self.assertEqual(len(r['write_conflicts']),1)
    def test_disjoint_running_work_does_not_stop_ready_work(self):
        g=self.load_graph_tool();r=g.assess(self.graph([{'id':'writing','status':'running','write_paths':['text']},{'id':'figure','write_paths':['figures']}]),self.root)
        self.assertFalse(r['write_conflicts']);self.assertEqual(r['ready'],['figure'])

class EvaluationHarness(Work):
    def tool(self):
        spec=importlib.util.spec_from_file_location('host_eval',ROOT/'evaluations/run_host.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
    def cases(self):
        (self.root/'material.md').write_text('Fixed synthetic material, not empirical evidence.\n')
        path=self.root/'cases.json';path.write_text(json.dumps({'cases':[
            {'id':name,'skill':skill,'prompt':'Complete this synthetic case.','material_files':['material.md'],'private_expected':'Do not expose the scoring answer'}
            for name,skill in [('judgement','topic-novelty'),('figure','scientific-visualization'),('manuscript','manuscript-writing')]]}))
        return path
    def test_custom_cases_keep_raw_material_equal_without_scoring_leak(self):
        m=self.tool();suite=m.prepare(ROOT/'skills',self.root/'suite',ROOT/'skills',cases_file=self.cases())
        self.assertEqual(len(suite['jobs']),9);grouped={}
        for job in suite['jobs']:
            request=m.load(job['request']);grouped.setdefault(request['case_id'],[]).append(request)
            self.assertNotIn('private_expected',request);self.assertNotIn('Do not expose',json.dumps(request))
            self.assertEqual(request['material_files'][0]['sha256'],m.hashfile(self.root/'material.md'))
        for rows in grouped.values():
            self.assertEqual(len(rows),3)
            self.assertEqual({row['material'] for row in rows},{rows[0]['material']})
    def test_custom_material_path_and_duplicate_case_rejected(self):
        m=self.tool();path=self.cases();cases=m.load(path)
        cases['cases'][0]['material_files']=['../outside.md'];m.save(path,cases)
        with self.assertRaisesRegex(ValueError,'outside'):m.prepare(ROOT/'skills',self.root/'bad-path',cases_file=path)
        cases['cases'][0]['material_files']=['material.md'];cases['cases'][1]['id']=cases['cases'][0]['id'];m.save(path,cases)
        with self.assertRaisesRegex(ValueError,'Unique'):m.prepare(ROOT/'skills',self.root/'bad-id',cases_file=path)
    def test_changed_material_stops_adapter_before_execution(self):
        m=self.tool();suite=m.prepare(ROOT/'skills',self.root/'suite',cases_file=self.cases())
        (self.root/'material.md').write_text('Changed after requests were frozen')
        with self.assertRaisesRegex(ValueError,'Evaluation material changed'):
            m.run(suite,['unused-adapter','{request}','{output}'],self.root/'runs','fixture','no-model')
    def test_paired_material_identical_and_no_quality_claim(self):
        m=self.tool();suite=m.prepare(ROOT/'skills',self.root/'suite')
        self.assertEqual(len(suite['jobs']),10);self.assertEqual(suite['status'],'prepared_not_run')
        grouped={}
        for job in suite['jobs']:
            r=m.load(job['request']);grouped.setdefault(r['case_id'],[]).append(r)
        for rows in grouped.values():self.assertEqual(rows[0]['material'],rows[1]['material']);self.assertEqual(rows[0]['user_prompt'],rows[1]['user_prompt'])
    def test_fixture_command_not_reported_as_model_performance(self):
        m=self.tool();suite=m.prepare(ROOT/'skills',self.root/'suite');suite['jobs']=suite['jobs'][:1]
        adapter=self.root/'adapter.py';adapter.write_text('from pathlib import Path\nimport sys\nPath(sys.argv[2]).write_text("SOFTWARE FIXTURE, NOT A MODEL RESPONSE")\n')
        result=m.run(suite,[sys.executable,str(adapter),'{request}','{output}'],self.root/'runs','fixture','no-model')
        self.assertEqual(result['runs'][0]['status'],'answer_received');self.assertFalse(result['ability_improvement_established'])
        self.assertFalse(result['quality_evaluated'])
    def test_unconfigured_command_not_used(self):
        m=self.tool()
        with self.assertRaises(ValueError):m.run({'jobs':[]},[],self.root/'out','none','none')

if __name__=='__main__':unittest.main()
