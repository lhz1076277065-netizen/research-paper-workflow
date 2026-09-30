"""Lean routing/source lifecycle tests. API replies here are synthetic fixtures.

No LLM competence, live GitHub execution or publication validity is inferred.
"""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
def mod(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m
u=mod('lean_upstream','scripts/upstream.py')
b=mod('lean_bridge','scripts/provider_runtime.py')
e=mod('lean_environment','scripts/environment.py')
p=mod('lean_portable','scripts/portable_skill.py')
def h(text):
    data=text.encode();return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def row(path,text='test'):
    return {'path':path,'mode':'100644','type':'blob','sha':h(text),'size':len(text.encode())}
class Sources(unittest.TestCase):
    def setUp(self):
        self.repo='outside-library/new-skills';self.commit='a'*40;self.tree='b'*40
        self.text='---\nname: new-method\ndescription: New method\n---\nUse actual input.'
        self.path='new-layout/new-method/SKILL.md'
        self.rows=[row(self.path,self.text),row('shared/guide.md'),row('tools/current.py')]
        self.calls=[]
    def api(self,url):
        self.calls.append(url)
        if url==f'/repos/{self.repo}':return {'full_name':self.repo,'default_branch':'renamed-default'}
        if '/commits/' in url:return {'sha':self.commit,'commit':{'tree':{'sha':self.tree}}}
        if '?recursive=1' in url:return {'tree':self.rows,'truncated':False}
        if '/contents/' in url:return {'type':'file','encoding':'base64','sha':h(self.text),'content':base64.b64encode(self.text.encode()).decode()}
        raise AssertionError(url)
    def index(self):return u.discover(self.repo,api=self.api)
    def test_arbitrary_repo_not_in_13_sources(self):self.assertEqual(self.index()['repository'],self.repo)
    def test_default_branch_is_detected(self):self.index();self.assertIn(f'/repos/{self.repo}/commits/renamed-default',self.calls)
    def test_new_entry_path_is_discovered(self):self.assertEqual(self.index()['skills'],[self.path])
    def test_fresh_discovery_sees_new_commit_and_path(self):
        first=self.index();self.commit='c'*40;self.rows=[row('moved/SKILL.md')]
        latest=self.index();self.assertNotEqual(first['commit'],latest['commit']);self.assertEqual(latest['skills'],['moved/SKILL.md'])
    def test_read_pins_original_run_commit(self):
        i=self.index();self.commit='c'*40;self.assertEqual(u.read_source(i,self.path,api=self.api),self.text)
        self.assertTrue(self.calls[-1].endswith('?ref='+'a'*40))
    def test_ref_is_quoted(self):u.discover(self.repo,ref='release/next',api=self.api);self.assertIn('/commits/release%2Fnext',self.calls[1])
    def test_reference_repository_no_native_skills(self):self.rows=[row('README.md')];self.assertEqual(self.index()['skills'],[])
    def test_symlink_not_skill(self):self.rows[0]['mode']='120000';self.assertEqual(self.index()['skills'],[])
    def test_submodule_not_skill(self):self.rows[0]['type']='commit';self.assertEqual(self.index()['skills'],[])
    def test_traversal_rejected(self):
        self.rows=[row('../SKILL.md')]
        with self.assertRaises(u.UpstreamError):self.index()
    def test_bad_url_rejected(self):
        with self.assertRaises(u.UpstreamError):u.repository('https://github.com/owner/repo/tree/main')
    def test_repository_url_normalized(self):self.assertEqual(u.repository('https://github.com/owner/repo.git'),'owner/repo')
    def test_credentials_in_url_rejected(self):
        with self.assertRaises(u.UpstreamError):u.repository('https://secret@github.com/owner/repo')
    def test_network_not_implicitly_used(self):
        with self.assertRaises(u.UpstreamError):u.GitHubAPI()('/repos/x/y')
    def test_blob_mismatch_rejected(self):
        index=self.index();self.text+='changed'
        with self.assertRaises(u.UpstreamError):u.read_source(index,self.path,api=self.api)
    def test_missing_entry_rejected(self):
        with self.assertRaises(u.UpstreamError):u.read_source(self.index(),'old/SKILL.md',api=self.api)
    def test_verified_read_cache_reuses_bytes_without_network(self):
        index=self.index()
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'entry.md'
            self.assertEqual(u.read_source(index,self.path,api=self.api,cache=path),self.text)
            self.assertEqual(u.read_source(index,self.path,api=lambda _:self.fail('cache reuse called the network'),cache=path),self.text)
    def test_edited_cache_is_preserved_and_rejected(self):
        index=self.index()
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'entry.md';path.write_text('User edits')
            with self.assertRaises(u.UpstreamError):u.read_source(index,self.path,api=self.api,cache=path)
            self.assertEqual(path.read_text(),'User edits')
    def test_cache_cannot_hide_a_changed_index_blob(self):
        index=self.index()
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'entry.md';path.write_text(self.text)
            index['files'][self.path]['blob_sha']='c'*40
            with self.assertRaises(u.UpstreamError):u.read_source(index,self.path,cache=path)
    def test_unsupported_binary_response(self):
        with self.assertRaises(u.UpstreamError):u.read_source(self.index(),self.path,api=lambda _: {'type':'file','encoding':'none'})
    def test_unknown_semantic_quality_not_faked(self):
        d=u.bind(self.index(),self.path,'research-design','invent-new-method')
        self.assertEqual(d['providers'][0]['source_review_status'],'discovered_needs_task_reading')
        self.assertIsNone(d['providers'][0]['entry_git_blob_sha'])
    def test_native_bind_keeps_support_paths(self):
        d=u.bind(self.index(),self.path,'paper-deep-reading','read',support=['shared/guide.md'])
        self.assertIn('shared/guide.md',d['providers'][0]['required_paths'])
    def test_support_path_missing_is_specific(self):
        with self.assertRaises(u.UpstreamError):u.bind(self.index(),self.path,'paper-deep-reading','read',support=['missing.md'])
    def dependency_fixture(self,root):
        reg=u.bind(self.index(),self.path,'paper-deep-reading','read',support=['shared/guide.md'])
        entry=root/self.path;entry.parent.mkdir(parents=True);entry.write_text(self.text)
        guide=root/'shared/guide.md';guide.parent.mkdir();guide.write_text('test')
        provider=reg['providers'][0];cfg={'providers':{provider['id']:{'root':str(root)}}}
        return provider,cfg,guide
    def test_entry_unchanged_does_not_hide_declared_dependency_drift(self):
        with tempfile.TemporaryDirectory() as t:
            provider,cfg,guide=self.dependency_fixture(Path(t))
            self.assertEqual(b.inspect_provider(provider,cfg)['status'],'files_available')
            guide.write_text('Changed operation, same entry')
            result=b.inspect_provider(provider,cfg)
            self.assertEqual(result['status'],'source_review_required')
            self.assertEqual(result['indexed_files_changed'],['shared/guide.md'])
            self.assertEqual(guide.read_text(),'Changed operation, same entry')
    def test_local_dependency_adaptation_needs_matching_digest_review(self):
        with tempfile.TemporaryDirectory() as t:
            provider,cfg,guide=self.dependency_fixture(Path(t));guide.write_text('Reviewed local adaptation')
            cfg['providers'][provider['id']]['source_reviewed']=True
            self.assertEqual(b.inspect_provider(provider,cfg)['status'],'source_review_required')
            cfg['providers'][provider['id']]['reviewed_file_sha256']={'shared/guide.md':b.sha(guide)}
            result=b.inspect_provider(provider,cfg)
            self.assertEqual(result['status'],'files_available');self.assertEqual(result['indexed_files_changed'],['shared/guide.md'])
            guide.write_text('Unreviewed next adaptation')
            self.assertEqual(b.inspect_provider(provider,cfg)['status'],'source_review_required')
    def test_declared_dependency_identity_input_is_validated(self):
        with tempfile.TemporaryDirectory() as t:
            provider,cfg,guide=self.dependency_fixture(Path(t))
            for identities in ([],{'unbound.md':'a'*40},{'shared/guide.md':'not-a-blob-sha'}):
                with self.subTest(identities=identities):
                    provider['discovered_file_blob_sha']=identities
                    with self.assertRaises(b.ContractError):b.inspect_provider(provider,cfg)
    def test_reference_not_mislabeled_native(self):
        with self.assertRaises(u.UpstreamError):u.bind(self.index(),'shared/guide.md','research-design','read')
    def test_only_chosen_entry_bound(self):
        self.rows.append(row('other/SKILL.md'));r=u.bind(self.index(),self.path,'paper-deep-reading','read')
        self.assertEqual(len(r['providers']),1)
    def test_dynamic_native_handoff_without_review_form(self):
        i=self.index();reg=u.bind(i,self.path,'research-design','invent-new-method')
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);entry=root/self.path;entry.parent.mkdir(parents=True);entry.write_text(self.text)
            pid=reg['providers'][0]['id'];cfg={'host_capabilities':[],'providers':{pid:{'root':str(root)}}}
            d=b.plan({'capability':'research-design','service':'invent-new-method','request':'Develop an original method','operation':'plan'},cfg,reg)
            self.assertEqual(d['selected_provider'],pid);self.assertFalse(d['executed'])
    def test_discovered_entry_changed_requires_new_source(self):
        reg=u.bind(self.index(),self.path,'research-design','invent')
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);f=root/self.path;f.parent.mkdir(parents=True);f.write_text('changed')
            pid=reg['providers'][0]['id'];cfg={'providers':{pid:{'root':str(root)}}}
            self.assertNotEqual(b.inspect_provider(reg['providers'][0],cfg)['status'],'files_available')
    def test_function_interface_uses_discovered_path(self):
        d=u.bind(self.index(),self.path,'data-preparation','profile',adapter='scipilot-profile',script='tools/current.py')
        self.assertEqual(d['providers'][0]['script']['path'],'tools/current.py');self.assertEqual(d['providers'][0]['mode'],'script-adapter')
    def test_unknown_function_interface_not_invented(self):
        with self.assertRaises(u.UpstreamError):u.bind(self.index(),self.path,'data-preparation','profile',adapter='made-up',script='tools/current.py')
    def test_compact_display_preserves_full_index(self):
        self.rows=[row(f's{i}/SKILL.md') for i in range(40)];i=self.index();d=u.candidates(i,limit=5)
        self.assertEqual(len(d['shown']),5);self.assertEqual(d['remaining'],35);self.assertEqual(len(i['skills']),40)
    def test_truncated_tree_falls_back_to_subtrees(self):
        def api(url):
            if '?recursive=1' in url:return {'tree':[],'truncated':True}
            if '/git/trees/' in url:
                if url.endswith('b'*40):return {'tree':[{'path':'new-layout','type':'tree','sha':'d'*40}],'truncated':False}
                return {'tree':[row('new-method/SKILL.md',self.text)],'truncated':False}
            return self.api(url)
        d=u.discover(self.repo,api=api);self.assertTrue(d['complete']);self.assertEqual(d['skills'],[self.path])
    def test_truncated_budget_does_not_claim_complete(self):
        def api(url):return {'tree':[],'truncated':True} if '?recursive=1' in url else self.api(url)
        d=u.discover(self.repo,api=api,max_tree_calls=1);self.assertFalse(d['complete']);self.assertTrue(d['unresolved_trees'])
    def test_duplicate_conflicting_paths_rejected(self):
        self.rows.append(row(self.path,'other'))
        with self.assertRaises(u.UpstreamError):self.index()

class LeanDefaults(unittest.TestCase):
    def test_no_runtime_static_provider_whitelist(self):
        self.assertEqual(json.loads((ROOT/'docs/provider-catalog.json').read_text())['providers'],[])
        for s in (ROOT/'skills').iterdir():
            if s.is_dir():self.assertEqual(json.loads((s/'assets/providers.json').read_text())['providers'],[])
    def test_sources_are_unpinned_repository_pointers(self):
        d=json.loads((ROOT/'assets/repository-sources.json').read_text())
        self.assertEqual(len(d['repositories']),13)
        for r in d['repositories']:
            self.assertEqual(set(r),{'url','hints'});u.repository(r['url'])
    def test_no_static_provider_cards_in_active_skills(self):self.assertFalse(list((ROOT/'skills').glob('*/references/provider-details/*')))
    def test_entries_short_and_do_not_load_universe(self):
        for f in (ROOT/'skills').glob('*/SKILL.md'):
            t=f.read_text();self.assertLess(len(t),850);self.assertNotIn('github.com/',t);self.assertNotIn('assets/providers.json',t)
    def test_autonomy_explicit_without_data_fabrication(self):
        for f in (ROOT/'skills').glob('*/SKILL.md'):
            t=f.read_text();self.assertIn('自主选择',t);self.assertIn('改造或新写代码',t);self.assertIn('实际证据',t)
    def test_focused_entry_does_not_require_admin_ledger(self):
        for f in (ROOT/'skills').glob('*/SKILL.md'):self.assertIn('可选工具，不作为日常前置',f.read_text())
    def test_default_export_is_short(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'core.md';result=p.export_prompt(ROOT/'skills/manuscript-writing',out)
            self.assertEqual(result['included_resources'],['SKILL.md']);self.assertLess(len(out.read_text()),1000)
    def test_full_export_preserves_30_steps(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'detail.md';p.export_prompt(ROOT/'skills/manuscript-writing',out,detail=True)
            self.assertIn('30. 最终交付',out.read_text())
    def test_plain_journal_task_needs_no_statistics(self):
        d=e.requirements_for({'request':'Match journals to this abstract','capability':'journal-intelligence','service':'matching'})
        self.assertEqual(d['packages'],[])
    def test_theory_needs_no_gpu_or_data_stack(self):
        d=e.requirements_for({'request':'Derive a formula','capability':'analysis-execution','service':'derive'})
        self.assertEqual(d['packages'],[])
    def test_forward_compatible_custom_operation(self):
        reg={'capabilities':['research-design'],'providers':[]}
        d=b.plan({'request':'Explore a new approach','capability':'research-design','service':'custom-approach','operation':'plan'},{},reg)
        self.assertEqual(d['status'],'fallback_needed');self.assertEqual(d['evidence_blocks'],[])
    def test_compatible_minimum_versions_merge(self):
        d=e.validate_packages([{'spec':'numpy>=1.24','import':'numpy'},{'spec':'numpy>=2.0','import':'numpy'}])
        self.assertEqual(len(d),1);self.assertEqual(d[0]['spec'],'numpy>=2.0')
    def test_pin_meeting_minimum_merges(self):
        d=e.validate_packages([{'spec':'numpy>=1.24','import':'numpy'},{'spec':'numpy==2.0','import':'numpy'}]);self.assertEqual(d[0]['spec'],'numpy==2.0')
    def test_pin_below_minimum_rejected(self):
        with self.assertRaises(e.EnvironmentError):e.validate_packages([{'spec':'numpy==1.24','import':'numpy'},{'spec':'numpy>=2','import':'numpy'}])
    def test_reverse_order_pin_meeting_minimum_merges(self):
        d=e.validate_packages([{'spec':'numpy==2.0','import':'numpy'},{'spec':'numpy>=1.24','import':'numpy'}]);self.assertEqual(d[0]['spec'],'numpy==2.0')
    def test_two_exact_conflicting_versions_rejected(self):
        with self.assertRaises(e.EnvironmentError):e.validate_packages([{'spec':'numpy==1.24','import':'numpy'},{'spec':'numpy==2','import':'numpy'}])
    def test_named_dependency_count_is_not_artificial_cap(self):
        self.assertEqual(len(e.validate_packages([{'spec':f'lib{x}>=1','import':f'lib{x}'} for x in range(41)])),41)
    def test_important_negative_results_preserved_in_reference(self):
        t=(ROOT/'skills/analysis-execution/references/protocol.md').read_text();self.assertIn('不能只保存最好的随机种子',t)
    def test_writing_no_per_paragraph_paperwork(self):
        t=(ROOT/'skills/manuscript-writing/references/protocol.md').read_text();self.assertIn('无需逐段填写台账',t)
    def test_reading_still_requires_actual_figure_observation(self):
        t=(ROOT/'skills/paper-deep-reading/references/protocol.md').read_text();self.assertIn('实际打开每张',t);self.assertIn('逐图与逐面板',t)

    def test_active_markdown_links_resolve_locally(self):
        files=[*ROOT.glob('*.md'),*(ROOT/'docs').rglob('*.md'),*(ROOT/'skills').rglob('*.md')]
        broken=[]
        for file in files:
            text=re.sub(r'```.*?```','',file.read_text(encoding='utf-8'),flags=re.S)
            for match in re.finditer(r'(?<!!)\[[^\]\n]+\]\(([^)\s]+)\)',text):
                target=match[1].split('#',1)[0]
                if not target or '://' in target or target.startswith(('mailto:','sandbox:')):
                    continue
                if not (file.parent/target).exists():
                    broken.append((str(file.relative_to(ROOT)),target))
        self.assertEqual(broken,[])

if __name__=='__main__':unittest.main()
