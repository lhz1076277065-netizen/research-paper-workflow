"""Merged-release record checks. Synthetic records exercise software contracts;
these tests do not establish scientific novelty or real provider execution.
"""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
Q=module('quality31',ROOT/'scripts/research31.py')
POL=json.loads((ROOT/'assets/research31-policy.json').read_text())

class Temp(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def artifact(self,name,text='SYNTHETIC record, not research evidence'):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        return {'path':name,'sha256':Q.sha(path)}

class PolicyTests(unittest.TestCase):
    def test_preserves_baseline_sources_and_adds_ideation(self):
        baseline={
            'microsoft/ResearchStudio','Yuan1z0825/nature-skills',
            'K-Dense-AI/scientific-agent-skills','Haojae/scipilot-figure-skill',
            'Galaxy-Dawn/claude-scholar','Imbad0202/academic-research-skills',
            'wanshuiyin/Auto-claude-code-research-in-sleep','karpathy/autoresearch',
            'Adkid-Zephyr/anti-defensive-writing-Skill','rougier/scientific-visualization-book',
            'nexu-io/open-design','ningzimu/codex-ppt-skill','WUBING2023/PaperSpine'}
        sources={s['repository']:s for s in POL['sources']}
        self.assertEqual(set(sources),baseline|{'Orchestra-Research/AI-Research-SKILLs'})
        self.assertEqual(len(sources),len(POL['sources']))
        self.assertEqual(sources['Orchestra-Research/AI-Research-SKILLs']['roles'],['ideation','novelty'])
        self.assertTrue({'ideation','novelty'}<=set(sources['K-Dense-AI/scientific-agent-skills']['roles']))
    def test_new_ideation_source_is_selectable_with_dynamic_entry(self):
        candidate={'id':'orchestra','repository':'Orchestra-Research/AI-Research-SKILLs',
                   'entry':'new-location/SKILL.md','commit':'a'*40,'available':True,
                   'roles':['ideation'],'tasks':['problem-discovery']}
        result=Q.select_role('ideation',[candidate],{'tasks':['problem-discovery']},POL)
        self.assertEqual(result['primary'],candidate)
        self.assertFalse(result['research_work_done'])
    def test_known_alias(self):self.assertEqual(Q.allowed_repo('K-Dense-AI/claude-scientific-skills',POL),'K-Dense-AI/scientific-agent-skills')
    def test_case_normalization(self):self.assertEqual(Q.allowed_repo('HAOJAE/scipilot-figure-skill',POL),'Haojae/scipilot-figure-skill')
    def test_repo_url(self):self.assertEqual(Q.allowed_repo('https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill.git',POL),POL['final_expression_repository'])
    def test_off_library_not_silent(self):
        with self.assertRaises(Q.ResearchError):Q.allowed_repo('other/new-agent',POL)
    def test_local_llm_url_not_a_source(self):
        with self.assertRaises(Q.ResearchError):Q.allowed_repo('http://127.0.0.1:8002',POL)
    def test_native_subagent_stays_permitted(self):self.assertTrue(Q.host_action('native_subagent')['permitted_by_project_scope'])
    def test_other_host_action_not_in_research_scope(self):self.assertFalse(Q.host_action('launch_other_host')['permitted_by_project_scope'])
    def test_endpoint_discovery_not_in_research_scope(self):self.assertFalse(Q.host_action('discover_local_llm')['permitted_by_project_scope'])
    def test_research_model_code_permitted(self):self.assertTrue(Q.host_action('run_research_code')['permitted_by_project_scope'])
    def test_no_claim_os_sandbox(self):self.assertFalse(Q.host_action('run_research_code')['os_sandbox_enforced'])
    def test_literature_sources_not_restricted(self):self.assertTrue(POL['literature_data_and_scientific_software_unrestricted_by_skill_list'])
    def test_paths_not_pinned(self):self.assertEqual(POL['source_entry_paths'],'discover_at_use')
    def test_new_entry_for_approved_repo(self):
        self.assertEqual(Q.validate_upstream_command(['discover','--repo','Yuan1z0825/nature-skills','--out','new.json'],POL),'Yuan1z0825/nature-skills')
    def test_equal_form_repo_and_duplicate_flags(self):
        self.assertEqual(Q.validate_upstream_command(['discover','--repo=Yuan1z0825/nature-skills'],POL),'Yuan1z0825/nature-skills')
        with self.assertRaises(Q.ResearchError):Q.validate_upstream_command(['discover','--repo=Yuan1z0825/nature-skills','--repo','Haojae/scipilot-figure-skill'],POL)
    def test_empty_repo_argument_has_specific_error(self):
        for args in [['discover','--repo='],['discover','--repo','--out','index.json']]:
            with self.assertRaisesRegex(Q.ResearchError,'Missing --repo value'):Q.validate_upstream_command(args,POL)
    def test_duplicate_repo_rejected(self):
        with self.assertRaises(Q.ResearchError):Q.validate_upstream_command(['discover','--repo','a/b','--repo','Haojae/scipilot-figure-skill'],POL)

class RecordTests(Temp):
    def state(self):
        return {'mode':'publication_research','stage':'delivery','host_scope':'current_host',
                'research_goal':dict.fromkeys(['problem','importance','knowledge_delta','decisive_test'],'SYNTHETIC goal, not a scientific judgement'),
                'scope_achievement':'main_research','documents':{k:self.artifact(k+'.md') for k in ['research_brief','prior_art','design','research_results','validation','manuscript','scientific_review','journal_fit','figure_plan']},
                'provider_uses':[],'figures':[]}
    def use(self,s,uid,repo,roles,outputs=None):
        x={'id':uid,'repository':repo,'entry':'skills/ACTUAL-TEST/SKILL.md','commit':'a'*40,
           'actor_scope':'current_host','mode':'adapted_in_host','adaptation':'Synthetic fixture of a source-preserving adaptation',
           'status':'executed','roles':roles,'scope':'full_manuscript' if {'writing','final_expression'}&set(roles) else 'requested_role','inputs':[self.artifact(uid+'-input.md')],
           'outputs':outputs or [self.artifact(uid+'-output.md')],'evidence':[self.artifact(uid+'-operation.md')],
           'steps':[]}
        s['provider_uses'].append(x);return x
    def complete(self):
        s=self.state()
        literature=self.use(s,'literature','microsoft/ResearchStudio',['literature','novelty'])
        reading=self.use(s,'reading','Yuan1z0825/nature-skills',['reading'])
        for use in [literature,reading]:
            use['document_bindings']={k:dict(s['documents'][k]) for k in ['research_brief','prior_art']}
        writing=self.use(s,'writing','Yuan1z0825/nature-skills',['writing'])
        expression=self.use(s,'expression',POL['final_expression_repository'],['final_expression'],[s['documents']['manuscript']])
        expression['inputs']=writing['outputs']
        review=self.artifact('expression-review.md');review['subjects']=[dict(s['documents']['manuscript'])]
        s['final_expression']={'provider_use':'expression','facts_rechecked':True,'review':review}
        return s
    def assess(self,s):return Q.assess(s,self.root,POL)
    def test_pilot_not_main_completion(self):
        s=self.complete();s['scope_achievement']='pilot';r=self.assess(s)
        self.assertEqual(r['status'],'research_in_progress');self.assertTrue(any('Pilot' in x for x in r['next_actions']))
    def test_actual_record_readiness_not_top_journal_certification(self):
        r=self.assess(self.complete());self.assertEqual(r['status'],'ready_for_content_review');self.assertFalse(r['scientific_quality_certified']);self.assertIsNone(r['top_journal_ready'])
    def test_equal_form_index_and_bad_index_container(self):
        index=self.root/'index.json';index.write_text('{"repository":"Haojae/scipilot-figure-skill"}')
        self.assertEqual(Q.validate_upstream_command(['read','--index='+str(index)],POL),'Haojae/scipilot-figure-skill')
        index.write_text('[]')
        with self.assertRaisesRegex(Q.ResearchError,'Source index must be an object'):Q.validate_upstream_command(['read','--index='+str(index)],POL)
    def test_full_expression_cannot_be_only_an_abstract(self):
        s=self.complete();s['provider_uses'][-1]['scope']='abstract'
        self.assertTrue(any('full manuscript' in x for x in self.assess(s)['next_actions']))
    def test_unrelated_writing_output_cannot_cover_this_manuscript(self):
        s=self.complete();s['provider_uses'][2]['outputs']=[self.artifact('different-paper.md')]
        self.assertTrue(any('writing' in x for x in self.assess(s)['next_actions']))
    def test_focused_figure_keeps_only_local_record_checks(self):
        s={'mode':'focused','stage':'delivery','figures':[{'artifact':self.artifact('caption.svg','<svg/>')}]}
        self.assertEqual(self.assess(s)['status'],'ready_for_content_review')
        (self.root/'caption.svg').write_text('changed')
        self.assertEqual(self.assess(s)['status'],'record_error')
    def test_invalid_container_types_have_specific_errors(self):
        for field,bad in [('documents',[]),('provider_uses',['entry']),('figures','file'),('research_goal',None),('host_actions',[{}])]:
            with self.subTest(field=field),self.assertRaisesRegex(Q.ResearchError,field):self.assess({field:bad})
    def test_invalid_record_cli_has_json_diagnostic(self):
        state=self.root/'bad.json';state.write_text('{"documents": []}')
        p=subprocess.run([sys.executable,str(ROOT/'scripts/research31.py'),'assess','--state',str(state),'--root',str(self.root)],capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertEqual(json.loads(p.stderr)['status'],'needs_attention');self.assertNotIn('Traceback',p.stderr)
    def test_only_selected_sources_not_all13_required(self):self.assertEqual(self.assess(self.complete())['status'],'ready_for_content_review')
    def test_focused_no_full_project_admin(self):self.assertEqual(self.assess({'mode':'focused','stage':'delivery'})['status'],'ready_for_content_review')
    def test_missing_goal_produces_next_research_action(self):
        r=self.assess({'mode':'publication_research'});self.assertEqual(r['status'],'research_in_progress');self.assertTrue(any('knowledge_delta' in x for x in r['next_actions']))
    def test_smoke_does_not_certify_research(self):self.assertEqual(self.assess({'mode':'smoke','stage':'delivery'})['status'],'research_in_progress')
    def test_missing_novelty_operation_not_hidden(self):
        s=self.complete();s['provider_uses'][0]['roles']=['literature'];self.assertTrue(any('novelty' in x for x in self.assess(s)['next_actions']))
    def test_function_search_not_full_search_review(self):
        s=self.complete();s['provider_uses'][0]['mode']='function_only';self.assertEqual(self.assess(s)['status'],'research_in_progress')
    def test_empty_role_override_does_not_erase_project_obligations(self):
        s=self.complete();s['required_skill_roles']=[];s['provider_uses']=[]
        self.assertTrue(any('novelty' in x for x in self.assess(s)['next_actions']))
    def test_download_not_execution(self):
        s=self.complete();s['provider_uses'][0]['status']='downloaded';self.assertEqual(self.assess(s)['status'],'research_in_progress')
    def test_expression_missing_is_next_work(self):
        s=self.complete();s.pop('final_expression');self.assertTrue(any('evidence-preserving' in x for x in self.assess(s)['next_actions']))
    def test_expression_preferred_source_is_required_only_when_user_requests_it(self):
        s=self.complete();s['provider_uses'][-1]['repository']='Yuan1z0825/nature-skills'
        self.assertEqual(self.assess(s)['status'],'ready_for_content_review')
        s['final_expression']['required_repository']=POL['final_expression_repository']
        self.assertTrue(any('user-required' in x for x in self.assess(s)['external_items']))
        s['provider_uses'][-1]['repository']=POL['final_expression_repository']
        self.assertEqual(self.assess(s)['status'],'ready_for_content_review')
    def test_local_expression_preserves_actual_work_and_final_review_requirements(self):
        s=self.complete();use=s['provider_uses'].pop();end=s['final_expression'];end.pop('provider_use')
        end['operation']={k:use[k] for k in ['actor_scope','scope','inputs','outputs','evidence']}
        end['operation']['steps']=['argument_review','evidence_preservation']
        self.assertEqual(self.assess(s)['status'],'ready_for_content_review')
        for key,value in [('scope','abstract'),('outputs',[]),('evidence',[]),('steps',[])]:
            with self.subTest(key=key):
                bad=copy.deepcopy(s);bad['final_expression']['operation'][key]=value
                self.assertEqual(self.assess(bad)['status'],'research_in_progress')
        for value in [False,'true']:
            bad=copy.deepcopy(s);bad['final_expression']['facts_rechecked']=value
            self.assertNotEqual(self.assess(bad)['status'],'ready_for_content_review')
        bad=copy.deepcopy(s);bad['final_expression']['review'].pop('subjects')
        self.assertEqual(self.assess(bad)['status'],'research_in_progress')
        bad=copy.deepcopy(s);bad['final_expression']['operation']['inputs'][0]['sha256']='0'*64
        self.assertEqual(self.assess(bad)['status'],'record_error')
        end['required_repository']=POL['final_expression_repository']
        self.assertTrue(any('user-required' in x for x in self.assess(s)['external_items']))
    def test_abstract_writing_does_not_complete_full_paper_role(self):
        s=self.complete();s['provider_uses'][2]['scope']='abstract'
        self.assertTrue(any('writing' in x for x in self.assess(s)['next_actions']))
    def test_actual_final_version_not_earlier_abstract(self):
        s=self.complete();s['provider_uses'][-1]['outputs']=[self.artifact('abstract-only.md')];self.assertTrue(any('this final manuscript' in x for x in self.assess(s)['next_actions']))
    def test_post_rewrite_facts_checked(self):
        s=self.complete();s['final_expression']['facts_rechecked']=False;self.assertEqual(self.assess(s)['status'],'research_in_progress')
    def test_changed_output_is_error(self):
        s=self.complete();(self.root/'manuscript.md').write_text('edited after review');self.assertEqual(self.assess(s)['status'],'record_error')
    def test_outside_root_not_read(self):
        s=self.complete();s['documents']['design']['path']='../other.md';self.assertEqual(self.assess(s)['status'],'record_error')
    def test_other_host_evidence_cannot_complete(self):
        s=self.complete();s['provider_uses'][0]['actor_scope']='other_host';self.assertEqual(self.assess(s)['status'],'record_error')
    def test_unauthorized_endpoint_action_reported(self):
        s=self.complete();s['host_actions']=['discover_local_llm'];self.assertEqual(self.assess(s)['status'],'record_error')
    def test_boolean_string_does_not_pass_fact_review(self):
        for value in ['false','true',1,[],{}]:
            s=self.complete();s['final_expression']['facts_rechecked']=value
            self.assertEqual(self.assess(s)['status'],'record_error')
    def test_review_subject_changes_are_not_hidden_by_updated_outputs(self):
        s=self.complete();new=self.artifact('revised-manuscript.md','SYNTHETIC revised statement')
        s['documents']['manuscript']=new;s['provider_uses'][-1]['outputs']=[new]
        self.assertTrue(any('review' in a for a in self.assess(s)['next_actions']))
        s['final_expression']['review']['subjects']=[new]
        self.assertEqual(self.assess(s)['status'],'ready_for_content_review')
    def test_legacy_unbound_review_requests_migration_not_silent_readiness(self):
        s=self.complete();s['final_expression']['review'].pop('subjects')
        self.assertTrue(any('Bind the post-expression' in a for a in self.assess(s)['next_actions']))
    def test_new_current_host_research_verb_is_permitted(self):
        s={'mode':'focused','host_actions':['verify_citations','derive_counterexample','a_future_research_action']}
        self.assertEqual(self.assess(s)['status'],'ready_for_content_review')
    def test_explicit_external_assistant_target_is_rejected_for_any_verb(self):
        s={'mode':'focused','host_actions':[{'action':'verify_citations','assistant_target':'other_assistant'}]}
        self.assertEqual(self.assess(s)['status'],'record_error')
    def test_explicit_external_actor_is_rejected(self):
        s={'mode':'focused','host_actions':[{'action':'verify_citations','actor_scope':'another_host'}]}
        self.assertEqual(self.assess(s)['status'],'record_error')
    def test_changed_prior_art_invalidates_only_related_coverage(self):
        s=self.complete();s['documents']['prior_art']=self.artifact('new-prior-art.md','SYNTHETIC different sources')
        result=self.assess(s)
        self.assertTrue(any('literature' in a for a in result['next_actions']))
        self.assertTrue(any('novelty' in a for a in result['next_actions']))
        self.assertFalse(any('writing operation' in a for a in result['next_actions']))
    def test_related_version_bound_prior_work_can_be_reused(self):
        s=self.complete()
        self.assertEqual(self.assess(s)['status'],'ready_for_content_review')
    def test_unrelated_task_brief_cannot_cover_literature(self):
        s=self.complete();s['provider_uses'][0]['document_bindings']['research_brief']=self.artifact('other-task.md')
        self.assertTrue(any('literature' in a for a in self.assess(s)['next_actions']))
    def test_legacy_role_labels_need_associations(self):
        s=self.complete();s['provider_uses'][0].pop('document_bindings')
        self.assertTrue(any('novelty' in a for a in self.assess(s)['next_actions']))
    def test_protocol_delivery_does_not_require_future_results(self):
        s=self.complete();s['research_context']={'article_type':'registered-report-stage1','study_types':['protocol-design']}
        s['requested_deliverable']='protocol';s['scope_achievement']='protocol_deliverable'
        for role in ['research_results','validation']:s['documents'].pop(role)
        result=self.assess(s);self.assertEqual(result['status'],'ready_for_content_review')
        self.assertEqual(result['delivery_scope'],'protocol');self.assertFalse(result['empirical_research_completion_evaluated'])
    def test_empirical_request_cannot_be_relabelled_protocol(self):
        s=self.complete();s['research_context']={'article_type':'registered-report-stage1','study_types':['protocol-design']}
        s['requested_deliverable']='empirical_paper';s['documents'].pop('research_results')
        self.assertEqual(self.assess(s)['status'],'record_error')
    def test_not_applicable_flag_does_not_waive_empirical_results(self):
        s=self.complete();s['documents'].pop('research_results')
        s['applicability']={'research_results':{'applicable':False,'reason':'SYNTHETIC attempt to omit required evidence'}}
        self.assertTrue(any('research_results' in a for a in self.assess(s)['next_actions']))
    def test_protocol_review_and_design_still_required(self):
        s=self.complete();s['research_context']={'article_type':'study-protocol','study_types':['protocol-design']}
        s['documents'].pop('design');s['documents'].pop('scientific_review')
        result=self.assess(s);self.assertTrue(any('design' in a for a in result['next_actions']))
        self.assertTrue(any('scientific_review' in a for a in result['next_actions']))
    def add_figure(self,s):
        f=self.artifact('main-figure.svg','<svg><!-- synthetic test figure --></svg>')
        x=self.use(s,'figure','Haojae/scipilot-figure-skill',['figure'],[f]);x['steps']=['plan','select','produce','numeric_review','visual_review']
        s['figures']=[{'artifact':f,'claim':'Test comparison','provider_use':'figure',
           'numeric_review':{'output_sha256':f['sha256'],'report':self.artifact('numbers.md')},
           'visual_review':{'output_sha256':f['sha256'],'report':self.artifact('view.md')}}];return x
    def test_full_figure_scope_bound_to_actual_main_figure(self):
        s=self.complete();self.add_figure(s);self.assertEqual(self.assess(s)['status'],'ready_for_content_review')
    def test_export_only_not_full_figure(self):
        s=self.complete();x=self.add_figure(s);x['mode']='function_only';x['steps']=['export'];self.assertEqual(self.assess(s)['status'],'research_in_progress')
    def test_separate_test_plot_does_not_count_for_main_plot(self):
        s=self.complete();x=self.add_figure(s);x['outputs']=[self.artifact('separate.svg')];self.assertTrue(any('separate test plot' in x for x in self.assess(s)['next_actions']))
    def test_visual_review_bound_to_current_figure(self):
        s=self.complete();self.add_figure(s);s['figures'][0]['visual_review']['output_sha256']='0'*64;self.assertEqual(self.assess(s)['status'],'research_in_progress')
    def test_no_figures_needed_for_theory_not_forced(self):
        s=self.complete();s['research_goal']['problem']='A formal theoretical question';self.assertEqual(self.assess(s)['status'],'ready_for_content_review')

class ContentTests(unittest.TestCase):
    def test_short_19_entries(self):
        entries=list((ROOT/'skills').glob('*/SKILL.md'));self.assertEqual(len(entries),19)
        for p in entries:self.assertLess(len(p.read_text()),800)
    def test_executor_and_research_model_are_separate_in_every_entry(self):
        for p in (ROOT/'skills').glob('*/SKILL.md'):
            text=p.read_text()
            self.assertIn('executor',text);self.assertIn('research_model',text)
            self.assertIn('computational-autonomous',text)
            self.assertNotIn('不寻找本地大模型',text)
    def test_original_code_allowed_without_host_switch(self):
        for p in (ROOT/'skills').glob('*/SKILL.md'):self.assertIn('改造或新写代码',p.read_text())
    def test_final_expression_preserves_comparison_truth(self):
        t=(ROOT/'src/common/references/final-expression.md').read_text();self.assertIn('不因结果不利而事后换主要指标',t);self.assertIn('实际应用于正式全文',t)
    def test_no_context_forced_all13(self):
        t=(ROOT/'src/common/references/provider-policy.md').read_text();self.assertIn('不要求全部使用',t)
    def test_not_all_publication_research_requires_ml(self):
        t=(ROOT/'src/common/references/research-quality.md').read_text();self.assertIn('理论明确命题',t);self.assertIn('描述研究、复现、零结果',t)
    def test_no_user_hardware_values_in_runtime(self):
        for p in (ROOT/'src/common').rglob('*'):
            if p.is_file() and p.suffix in {'.py','.md','.json'}:
                for term in ['m5max','m5 max','128gb','/users/luca']:
                    self.assertNotIn(term,p.read_text().lower())

if __name__=='__main__':unittest.main(verbosity=2)
