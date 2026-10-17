"""Research identity/coverage checks with actual files and pinned-source receipts.

These software fixtures do not certify the scientific validity of the study.
"""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src/common/scripts'))
import artifact_io as A
import capabilities as C
import phase_control as P
import professional_flow as F
import research_commitment as R

class ResearchCommitment(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve();self.n=0
        self.request=self.write('request.md','Study the relationship between A and B within population W.')
        self.brief=self.write('brief.md','A and B are measured in W. Association does not establish causation.')
        self.spec={'title':'A–B association in W','objects':['A','B'],'relationship':'observational association',
            'scope':'Population W and the supplied measurements','completion_criteria':['Estimate the relationship and assess the stated sensitivity'],
            'questions':[{'id':'Q1','text':'How are A and B related in W?','required':True}],
            'primary_experiments':[{'id':'E1','question_ids':['Q1'],'purpose':'Estimate the primary relationship with uncertainty'}]}
        self.specfile=self.json('specification.json',self.spec)
        self.state=P.init('full','Study A and B',autonomous_plan=True)
        R.bind(self.state,self.root,self.specfile,self.request,self.brief,self.request.read_text())
        self.phase=self.root/'phase.json';P.save(self.phase,self.state)
        self.guide='Read each research question, actual method and result; revise unsupported conclusions and explain the changes.'
        cap={'id':'fixture','repository':'fixture/science','commit':'a'*40,'tree':'b'*40,'entry':'SKILL.md','kind':'skill_protocol',
            'roles':['research'],'dependencies':[],'host_adaptation':'Test fixture only',
            'required_files':[{'path':'SKILL.md','blob':C.blob(self.guide.encode())}]}
        self.idx={'capabilities':[cap],'professional_routes':{c:{'primary':'fixture','alternatives':[],'work':'Read the actual supplied artifacts','boundary':'Fixture only'} for c in ('research-design','analysis-execution','manuscript-review','final-expression')}}
        self.index=self.json('index.json',self.idx);self.cache=self.root/'cache'
        self.write('cache/fixture/'+('a'*40)+'/SKILL.md',self.guide)
        self.patch=patch.object(C,'index_path',return_value=self.index);self.patch.start()
    def tearDown(self):self.patch.stop();self.tmp.cleanup()
    def write(self,name,value):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(value,encoding='utf-8');return path
    def json(self,name,value):return self.write(name,json.dumps(value,ensure_ascii=False,indent=2))
    def result(self,answer='answered',execution='completed',validity='valid',purpose='formal'):
        self.plan=self.root/'research-plan.md'
        self.source_step('research-design',[self.brief],{self.plan:'Use the documented estimator on W and examine the specified sensitivity.'})
        self.resultfile=self.root/'results/association.json'
        self.source_step('analysis-execution',[self.plan,self.brief],{self.resultfile:json.dumps({'estimate':0.0,'uncertainty':[-0.1,0.1],'sample_size':30})})
        unit={'key':'test-A-B','claim':'Estimate A–B association','next_action':'Write the observed relationship',
            **R.validate_work(self.state,['Q1'],'primary',purpose,execution,answer,validity,[self.resultfile],self.root,'E1')}
        self.state['work_units']={'test-A-B':unit}
        self.resultindex=self.json('result-index.json',{'questions':[{'id':'Q1','work_units':['test-A-B'],'answer':'The fitted relationship is compatible with the prespecified negligible range.'}],
            'experiments':[{'id':'E1','work_unit':'test-A-B','results':['results/association.json']}]})
        return unit
    def paper(self,name='paper.md'):
        manuscript=self.write(name,'# A–B association\n\n## Methods\nWe estimated the A–B relationship in W using the documented estimator.\n\n## Results\nThe estimate was 0.0 with the stated uncertainty range.\n\n## Conclusion\nThe observations are compatible with the specified negligible relationship in W.\n')
        coverage=self.json(name+'.coverage.json',{'questions':[{'id':'Q1','conclusion':{'path':name,'quote':'The observations are compatible with the specified negligible relationship in W.'}}],
            'experiments':[{'id':'E1','methods':{'path':name,'quote':'We estimated the A–B relationship in W using the documented estimator.'},
                'results':{'path':name,'quote':'The estimate was 0.0 with the stated uncertainty range.'}}]})
        return manuscript,coverage
    def report(self):
        return {'question_checks':[{'id':'Q1','assessment':'The actual formal test estimates the original A–B relationship in W.',
            'resolution':'The conclusion is restricted to the observed association and uncertainty.'}],
            'experiment_checks':[{'id':'E1','assessment':'The main estimator and its results are both described in the manuscript.',
                'resolution':'The required method and result passages are present in the appropriate sections.'}],
            'narrative_assessment':'The question motivates the test, whose result supports the bounded conclusion.',
            'internal_process_assessment':'The manuscript presents scientific methods; operational receipts remain in delivery records.',
            'unresolved_required':[]}
    def source_step(self,capability,inputs,outputs,purpose='formal'):
        P.save(self.phase,self.state);self.n+=1;name=f'step-{self.n}'
        start=F.begin(self.idx,capability,self.request,inputs,self.cache,phase=self.phase,question_ids=['Q1'],purpose=purpose)
        begun=self.root/(name+'-started.json');F.persist(start,begun)
        paths=[]
        for path,content in outputs.items():
            paths.append(self.write(str(path.relative_to(self.root)),content))
        work=self.json(name+'-work.json',{'step_id':start['id'],'scope':'requested_step','omitted_required_work':[],
            'functions_run':False,'actions':[{'source_file':'SKILL.md','source_excerpt':self.guide,
                'applied':'Read the supplied scientific artifacts, evaluated their correspondence, and wrote the requested review or revision.',
                'output':str(path),'output_excerpt':path.read_text()} for path in paths]})
        done=F.finish(self.idx,start,paths,work,'adapted_in_host');finished=self.root/(name+'-finished.json');F.persist(done,finished,start)
        self.state=P.load(self.phase)
        return begun,finished
    def delivery(self,report=None):
        self.result();R.bind_results(self.state,self.root,self.plan,self.resultindex);paper,coverage=self.paper()
        binding=self.state['research_commitment'];inputs=[self.root/binding['record']['path'],self.plan,self.resultindex,self.resultfile,paper,coverage]
        semantic=self.root/'semantic-review.json'
        started,finished=self.source_step('manuscript-review',inputs,{semantic:json.dumps(report or self.report(),ensure_ascii=False,indent=2)})
        return paper,coverage,started,finished,semantic
    def attach(self,parts):
        return R.bind_delivery(self.state,self.root,self.plan,self.resultindex,*parts[:4])

    def test_immutable_original_binding_and_complete_recovery(self):
        row=R.check_context(self.state);self.assertEqual(row['questions'][0]['id'],'Q1')
        self.state['artifacts']=[{'path':str(i)} for i in range(80)]
        self.state['work_units']={'side':{'commitment_id':row['id'],'question_ids':[],'kind':'exploration'}}
        snapshot=R.snapshot(self.state)
        self.assertEqual(snapshot['questions'][0]['text'],'How are A and B related in W?')
        self.assertEqual(snapshot['questions'][0]['answer_state'],'unanswered')
        self.assertFalse(row['authority_verified_by_tool'])
    def test_title_only_revision_keeps_scientific_identity_and_prior_results(self):
        self.result();R.bind_results(self.state,self.root,self.plan,self.resultindex);old=R.context(self.state)
        changed={**self.spec,'title':'A clearer title about the same relationship'}
        new=self.json('specification-title.json',changed)
        R.bind(self.state,self.root,new,self.request,self.brief,self.request.read_text())
        self.assertEqual(R.context(self.state),old);self.assertIn('research_results',self.state)
        self.assertEqual(R.snapshot(self.state)['title'],changed['title'])
    def test_changing_science_requires_new_actual_user_quote(self):
        changed={**self.spec,'relationship':'causal effect'};new=self.json('causal.json',changed)
        for kw in ({},{'science_revision':True,'revision_reason':'Try to switch without a new user request'}):
            with self.assertRaises(R.CommitmentError):R.bind(self.state,self.root,new,self.request,self.brief,self.request.read_text(),**kw)
        req=self.write('new-request.md','Change the scientific target to the causal effect of A on B.')
        old=R.context(self.state);R.bind(self.state,self.root,new,req,self.brief,req.read_text(),True,'The user explicitly changed the scientific target')
        self.assertEqual(self.state['research_commitment']['version'],2);self.assertFalse(R.match_context(self.state,old))
        self.assertEqual(len(self.state['research_commitment_history']),1)
    def test_same_question_allows_autonomous_method_revision_and_preserves_history(self):
        self.result();R.bind_results(self.state,self.root,self.plan,self.resultindex);original=R.context(self.state)
        changed=copy.deepcopy(self.spec);changed['primary_experiments'][0]['method']='A more suitable robust estimator for the same A–B question'
        path=self.json('method-revision.json',changed)
        with self.assertRaises(R.CommitmentError):R.bind(self.state,self.root,path,self.request,self.brief,self.request.read_text())
        R.bind(self.state,self.root,path,self.request,self.brief,self.request.read_text(),implementation_reason='The pilot revealed estimator instability; use the suitable alternative')
        self.assertEqual(self.state['research_commitment']['id'],original['commitment_id'])
        self.assertEqual(self.state['research_commitment']['version'],original['commitment_version'])
        self.assertEqual(self.state['research_commitment']['implementation_version'],2)
        self.assertNotIn('research_results',self.state);self.assertEqual(R.snapshot(self.state)['questions'][0]['answer_state'],'unanswered')
        with self.assertRaises(R.CommitmentError):R.bind_results(self.state,self.root,self.plan,self.resultindex)
    def test_later_failed_required_test_supersedes_old_answer(self):
        self.result();R.bind_results(self.state,self.root,self.plan,self.resultindex)
        self.state['work_units']['later-test']={'key':'later-test','next_action':'Repair the current estimator',
            **R.validate_work(self.state,['Q1'],execution='failed',answer='inconclusive',validity='invalid',results=[self.resultfile],root=self.root,experiment_id='E1')}
        snapshot=R.snapshot(self.state);self.assertEqual(snapshot['questions'][0]['answer_state'],'inconclusive')
        with self.assertRaises(R.CommitmentError):R.bind_results(self.state,self.root,self.plan,self.resultindex)
    def test_mutating_operations_respect_pause_and_terminal_status(self):
        parts=self.delivery();self.attach(parts)
        for status in ('paused','completed','closed_limit','route_closed'):
            self.state['status']=status
            with self.assertRaises(R.CommitmentError):R.bind(self.state,self.root,self.specfile,self.request,self.brief,self.request.read_text())
            with self.assertRaises(R.CommitmentError):R.bind_results(self.state,self.root,self.plan,self.resultindex)
            with self.assertRaises(R.CommitmentError):self.attach(parts)
            # Read-only checks do not resume or rewrite the host state.
            before=copy.deepcopy(self.state);self.assertEqual(R.closure(self.state)['required_questions'],1);self.assertEqual(before,self.state)
    def test_arbitrary_plan_or_result_files_cannot_replace_professional_execution(self):
        self.result();self.state['professional_pending']=[]
        with self.assertRaises(R.CommitmentError):R.bind_results(self.state,self.root,self.plan,self.resultindex)
    def test_diagnostic_source_output_cannot_be_promoted_by_formal_checkpoint(self):
        self.result();rows=self.state['professional_pending'];rows[:]=[r for r in rows if r['capability']!='analysis-execution']
        diagnostic=self.root/'results/diagnostic.json'
        self.source_step('analysis-execution',[self.plan,self.brief],{diagnostic:json.dumps({'estimate':0.0,'uncertainty':[-0.1,0.1]})},purpose='diagnostic')
        self.state['work_units']['test-A-B'].update(R.validate_work(self.state,['Q1'],execution='completed',answer='answered',validity='valid',results=[diagnostic],root=self.root,experiment_id='E1'))
        index=P.load(self.resultindex);index['experiments'][0]['results']=['results/diagnostic.json'];P.save(self.resultindex,index)
        # Actual diagnostic receipt exists, but self-reporting its result as formal is insufficient.
        with self.assertRaises(R.CommitmentError):R.bind_results(self.state,self.root,self.plan,self.resultindex)
    def test_unchanged_primary_test_reusable_after_another_method_changes(self):
        spec=copy.deepcopy(self.spec);spec['primary_experiments'].append({'id':'E2','question_ids':['Q1'],'purpose':'Sensitivity for the same question'})
        state=P.init('full','A and B');path=self.json('two-experiments.json',spec)
        R.bind(state,self.root,path,self.request,self.brief,self.request.read_text());self.state=state;self.result()
        original=copy.deepcopy(self.state['work_units']['test-A-B'])
        changed=copy.deepcopy(spec);changed['primary_experiments'][1]['method']='A repaired sensitivity estimator'
        revised=self.json('second-method-revision.json',changed)
        R.bind(self.state,self.root,revised,self.request,self.brief,self.request.read_text(),implementation_reason='Repair only E2 while retaining the E1 result')
        # E1's source receipt and exact result remain valid; E2 has not answered yet.
        self.assertEqual(R._unit(self.state,'test-A-B'),original)
        snapshot=R.snapshot(self.state)['questions'][0]
        self.assertEqual(snapshot['answer_state'],'unanswered')
        self.assertEqual(snapshot['primary_experiments'][0]['answer_state'],'answered')
    def test_invented_or_assistant_quote_not_user_authority(self):
        with self.assertRaises(R.CommitmentError):R.bind(self.state,self.root,self.specfile,self.request,self.brief,'An invented request')
        req=self.json('assistant.json',{'role':'assistant','content':'Study A and B'})
        with self.assertRaises(R.CommitmentError):R.bind(self.state,self.root,self.specfile,req,self.brief,'Study A and B')
    def test_structured_user_quote_preserves_actual_quotes_and_newlines(self):
        message='Study "A"\nand B.';req=self.json('user.json',{'messages':[{'role':'user','content':message}]})
        state=P.init('full','A and B');R.bind(state,self.root,self.specfile,req,self.brief,message)
        self.assertEqual(R.check_context(state)['request_quote'],message)
    def test_mutated_contract_specification_or_request_cannot_be_reused(self):
        self.request.write_text('Study C and D instead.')
        with self.assertRaises(R.CommitmentError):R.check_context(self.state)
    def test_manual_binding_field_change_rejected(self):
        self.state['research_commitment']['relationship']='C–D'
        with self.assertRaises(R.CommitmentError):R.check_context(self.state)
    def test_new_work_cannot_rename_the_fixed_question(self):
        with self.assertRaises(R.CommitmentError):R.validate_work(self.state,['C-D'])
        with self.assertRaises(R.CommitmentError):R.validate_work(self.state,[])
        exploratory=R.validate_work(self.state,[],kind='exploration',purpose='diagnostic')
        self.assertEqual(exploratory['kind'],'exploration')
    def test_execution_success_does_not_mean_question_answered(self):
        self.result(answer='inconclusive');self.assertEqual(R.snapshot(self.state)['questions'][0]['answer_state'],'inconclusive')
        with self.assertRaises(R.CommitmentError):R.bind_results(self.state,self.root,self.plan,self.resultindex)
    def test_failed_unrun_invalid_or_diagnostic_result_cannot_answer(self):
        self.resultfile=self.json('actual.json',{'estimate':0})
        for changes in ({'execution':'failed'},{'execution':'not_run'},{'validity':'unknown'},{'validity':'invalid'},{'purpose':'diagnostic'}):
            kw={'execution':'completed','answer':'answered','validity':'valid','purpose':'formal',**changes}
            with self.assertRaises(R.CommitmentError):R.validate_work(self.state,['Q1'],results=[self.resultfile],root=self.root,experiment_id='E1',**kw)
    def test_reliable_zero_and_reverse_results_are_allowed_answers(self):
        self.result();R.bind_results(self.state,self.root,self.plan,self.resultindex)
        self.assertEqual(R.snapshot(self.state)['questions'][0]['answer_state'],'answered')
        # The tool deliberately does not prescribe a favorable direction or p-value.
        reverse=self.json('results/reverse.json',{'estimate':-1.0,'uncertainty':[-1.2,-0.8]})
        self.assertEqual(R.validate_work(self.state,['Q1'],execution='completed',answer='answered',validity='valid',results=[reverse],root=self.root,experiment_id='E1')['answer_state'],'answered')
    def test_legacy_no_contract_is_readable_unknown(self):
        state=P.init('full','Legacy');state['work_units']={'old':{'outcome':'inconclusive'}}
        self.assertEqual(R.snapshot(state)['status'],'unknown');self.assertEqual(R.closure(state)['status'],'unknown')
        self.assertEqual(R.validate_work(state,['missing']),{})
        state['alignment_required']=True
        with self.assertRaises(R.CommitmentError):R.closure(state)
    def test_optional_question_does_not_create_an_extra_completion_requirement(self):
        spec=copy.deepcopy(self.spec);spec['questions'].append({'id':'Q2','text':'An optional future question','required':False})
        path=self.json('optional-spec.json',spec);state=P.init('full','A and B')
        R.bind(state,self.root,path,self.request,self.brief,self.request.read_text());self.state=state
        parts=self.delivery();self.attach(parts);self.assertEqual(R.closure(self.state)['required_questions'],1)
    def test_unanswered_original_cannot_be_replaced_by_easier_question(self):
        self.result();index=P.load(self.resultindex);index['questions'][0]['id']='Q-CD';P.save(self.resultindex,index)
        with self.assertRaises(R.CommitmentError):R.bind_results(self.state,self.root,self.plan,self.resultindex)
    def test_exact_primary_outputs_required_not_a_summary_substitution(self):
        self.result();other=self.json('summary.json',{'summary':'An easier result'})
        index=P.load(self.resultindex);index['experiments'][0]['results']=[other.name];P.save(self.resultindex,index)
        with self.assertRaises(R.CommitmentError):R.bind_results(self.state,self.root,self.plan,self.resultindex)
    def test_missing_primary_experiment_prevents_whole_paper_readiness(self):
        self.result();index=P.load(self.resultindex);index['experiments']=[];P.save(self.resultindex,index)
        with self.assertRaises(R.CommitmentError):R.bind_results(self.state,self.root,self.plan,self.resultindex)
    def test_result_mutation_invalidates_bound_answer(self):
        self.result();R.bind_results(self.state,self.root,self.plan,self.resultindex)
        self.resultfile.write_text('{"estimate":100}')
        with self.assertRaises(R.CommitmentError):R.validate_step(self.state,'manuscript-writing',[])
        self.assertEqual(R.snapshot(self.state)['questions'][0]['answer_state'],'unanswered')
    def test_compact_recovery_does_not_rehash_full_research_input_chain(self):
        self.result();R.bind_results(self.state,self.root,self.plan,self.resultindex)
        with patch.object(F,'check',side_effect=AssertionError('Recovery must not repeat source/input validation')):
            snapshot=R.snapshot(self.state)
        self.assertEqual(snapshot['questions'][0]['answer_state'],'answered')
        self.assertIn('recorded_with_unchanged_result_stats',snapshot['questions'][0]['primary_experiments'][0]['verification'])
    def test_full_writing_consumes_actual_plan_contract_index_and_every_result(self):
        self.result();R.bind_results(self.state,self.root,self.plan,self.resultindex)
        binding=self.state['research_commitment'];paths=[self.root/binding['record']['path'],self.plan,self.resultindex,self.resultfile]
        inputs=[F.ref(p) for p in paths]
        with self.assertRaises(R.CommitmentError):R.validate_step(self.state,'manuscript-writing',inputs[:-1])
        self.assertEqual(R.validate_step(self.state,'manuscript-writing',inputs)['commitment_id'],binding['id'])
    def test_method_notes_can_be_drafted_without_claiming_whole_paper_complete(self):
        self.state['scope']='focused'
        self.assertEqual(R.validate_step(self.state,'manuscript-writing',[F.ref(self.brief)])['purpose'],'formal')
        self.state['scope']='full'
        self.assertEqual(R.validate_step(self.state,'manuscript-writing',[F.ref(self.brief)],purpose='diagnostic')['purpose'],'diagnostic')
    def test_actual_semantic_review_and_scientific_passages_allow_completion(self):
        parts=self.delivery();self.attach(parts);result=R.closure(self.state)
        self.assertEqual(result['status'],'covered_by_actual_work_and_review')
        self.assertFalse(result['scientific_validity_certified']);self.assertFalse(result['semantic_truth_verified_by_tool'])
    def test_self_written_passed_boolean_is_not_actual_semantic_review(self):
        parts=self.delivery({'passed':True,'unresolved_required':[]})
        with self.assertRaises(R.CommitmentError):self.attach(parts)
    def test_required_unresolved_semantic_issue_prevents_completion(self):
        report=self.report();report['unresolved_required']=['The conclusion changes not-tested into no relationship.']
        parts=self.delivery(report)
        with self.assertRaises(R.CommitmentError):self.attach(parts)
    def test_claim_in_log_or_wrong_section_is_not_manuscript_experiment_coverage(self):
        parts=self.delivery();paper,coverage=parts[:2]
        data=P.load(coverage);data['experiments'][0]['results']['quote']='We estimated the A–B relationship in W using the documented estimator.';P.save(coverage,data)
        # It is an exact real quote, but occurs only in Methods rather than Results.
        with self.assertRaises(R.CommitmentError):self.attach(parts)
    def test_missing_primary_methods_in_body_is_detected_before_review_reuse(self):
        parts=self.delivery();coverage=parts[1];data=P.load(coverage);data['experiments']=[];P.save(coverage,data)
        with self.assertRaises(R.CommitmentError):self.attach(parts)
    def test_explicit_custom_section_can_locate_experimental_methods(self):
        manuscript,coverage=self.paper();manuscript.write_text(manuscript.read_text().replace('## Methods','## Experimental setup'))
        data=P.load(coverage);data['experiments'][0]['methods']['section']='Experimental setup';P.save(coverage,data)
        checked=R._coverage(self.state,self.root,R._ref(self.root,manuscript),R._ref(self.root,coverage))
        self.assertEqual(checked['experiments'][0]['methods']['section'],'Experimental setup')
    def test_methods_parent_includes_sample_and_estimation_subsections(self):
        manuscript,coverage=self.paper()
        manuscript.write_text(manuscript.read_text().replace('## Methods\n','## Methods\n### Sample\nThe observations came from population W.\n### Estimation\n'))
        checked=R._coverage(self.state,self.root,R._ref(self.root,manuscript),R._ref(self.root,coverage))
        self.assertEqual(checked['experiments'][0]['methods']['quote'],'We estimated the A–B relationship in W using the documented estimator.')
    def test_explicit_section_cannot_substitute_for_missing_actual_passage(self):
        manuscript,coverage=self.paper();data=P.load(coverage)
        data['experiments'][0]['methods'].update(section='Methods',quote='This claimed experimental passage is absent from the manuscript.')
        P.save(coverage,data)
        with self.assertRaises(R.CommitmentError):R._coverage(self.state,self.root,R._ref(self.root,manuscript),R._ref(self.root,coverage))
    def test_current_manuscript_cannot_be_swapped_after_actual_review(self):
        parts=self.delivery();self.attach(parts);parts[0].write_text(parts[0].read_text().replace('compatible with','proof of'))
        with self.assertRaises(R.CommitmentError):R.closure(self.state)
    def test_review_must_consume_complete_result_index_and_actual_primary_outputs(self):
        self.result();R.bind_results(self.state,self.root,self.plan,self.resultindex);paper,coverage=self.paper()
        binding=self.state['research_commitment'];inputs=[self.root/binding['record']['path'],self.plan,self.resultindex,paper,coverage]
        started,finished=self.source_step('manuscript-review',inputs,{self.root/'semantic-review.json':json.dumps(self.report())})
        with self.assertRaises(R.CommitmentError):R.bind_delivery(self.state,self.root,self.plan,self.resultindex,paper,coverage,started,finished)
    def expression(self,empty_checks=False,extra_change=False):
        parts=self.delivery();paper,coverage,started,finished,semantic=parts
        old=paper.read_text();new=old.replace('The estimate was 0.0 with the stated uncertainty range.','The estimated association was 0.0, with uncertainty reported above.')
        if extra_change:new=new.replace('The observations are compatible with the specified negligible relationship in W.','The observations prove the complete absence of a relationship in W.')
        final=self.root/'paper-polished.md';cover=self.root/'coverage-polished.json';data=P.load(coverage)
        for q in data['questions']:
            q['conclusion']['path']=final.name
            if extra_change:q['conclusion']['quote']='The observations prove the complete absence of a relationship in W.'
        for e in data['experiments']:
            for key in ('methods','results'):e[key]['path']=final.name
            e['results']['quote']='The estimated association was 0.0, with uncertainty reported above.'
        data['reviewed_coverage']=coverage.name
        diff={'meaning_checks':[] if empty_checks else [{'before':'The estimate was 0.0 with the stated uncertainty range.',
            'after':'The estimated association was 0.0, with uncertainty reported above.',
            'assessment':'Only wording changed; the estimator, numerical result and uncertainty claim retain the original scope.'}], 'unresolved_required':[]}
        es,ef=self.source_step('final-expression',[paper,coverage,semantic],{final:new,cover:json.dumps(data),self.root/'polish-meaning.json':json.dumps(diff)})
        return parts,final,cover,es,ef
    def test_incremental_polish_chain_preserves_review_without_second_full_review(self):
        parts,paper,coverage,es,ef=self.expression()
        R.bind_delivery(self.state,self.root,self.plan,self.resultindex,paper,coverage,parts[2],parts[3],es,ef)
        self.assertEqual(R.closure(self.state)['primary_experiments'],1)
        self.assertEqual(len([r for r in self.state['professional_pending'] if r['capability']=='manuscript-review']),1)
    def test_equal_numbers_without_actual_meaning_difference_check_are_insufficient(self):
        parts,paper,coverage,es,ef=self.expression(empty_checks=True)
        with self.assertRaises(R.CommitmentError):R.bind_delivery(self.state,self.root,self.plan,self.resultindex,paper,coverage,parts[2],parts[3],es,ef)
    def test_reviewed_small_edit_cannot_hide_another_changed_conclusion(self):
        parts,paper,coverage,es,ef=self.expression(extra_change=True)
        # Numerical values are unchanged and one real edit was checked, but the
        # separate stronger conclusion must also be actually read and assessed.
        with self.assertRaises(R.CommitmentError):R.bind_delivery(self.state,self.root,self.plan,self.resultindex,paper,coverage,parts[2],parts[3],es,ef)
    def test_one_assessed_sentence_can_cover_edits_inside_a_long_paragraph(self):
        before='Unchanged background. The estimate was small. More unchanged detail in the same physical line.'
        after='Unchanged background. The estimate was close to zero. More unchanged detail in the same physical line.'
        R._meaning_coverage(before,after,[{'before':'The estimate was small.','after':'The estimate was close to zero.','assessment':'The revised wording refers to the same estimated magnitude.'}])
    def test_layout_only_changes_do_not_create_semantic_review_bookkeeping(self):
        before='# Results\nThe estimated association was **small** and `bounded`.\n'
        after='## Results\n\nThe estimated association\nwas small and bounded.\n'
        R._meaning_coverage(before,after,[])
    def test_review_receipt_cannot_be_changed_after_attachment(self):
        parts=self.delivery();self.attach(parts);done=P.load(parts[3]);done['scientific_validity_certified']=True;P.save(parts[3],done)
        with self.assertRaises(R.CommitmentError):R.closure(self.state)
    def test_all_questions_recovered_even_when_more_than_three(self):
        spec=copy.deepcopy(self.spec)
        for i in range(2,9):spec['questions'].append({'id':'Q'+str(i),'text':'Additional necessary question '+str(i),'required':True});spec['primary_experiments'].append({'id':'E'+str(i),'question_ids':['Q'+str(i)],'purpose':'A necessary decisive test'})
        path=self.json('many-spec.json',spec);state=P.init('full','A and B')
        R.bind(state,self.root,path,self.request,self.brief,self.request.read_text())
        self.assertEqual(len(R.snapshot(state)['questions']),8)
    def test_missing_contract_recovers_all_stored_questions_without_granting_answers(self):
        spec=copy.deepcopy(self.spec)
        for i in range(2,6):
            spec['questions'].append({'id':'Q'+str(i),'text':'Original necessary question '+str(i),'required':True})
            spec['primary_experiments'].append({'id':'E'+str(i),'question_ids':['Q'+str(i)],'purpose':'A necessary original test'})
        path=self.json('recover-spec.json',spec);state=P.init('full','Original relationship')
        binding=R.bind(state,self.root,path,self.request,self.brief,self.request.read_text())
        state['work_units']={'old-success':{'commitment_id':binding['id'],'question_ids':['Q1'],'answer_state':'answered'}}
        (self.root/binding['record']['path']).unlink()
        snapshot=R.snapshot(state)
        self.assertEqual(snapshot['status'],'needs_recovery');self.assertFalse(snapshot['identity_verified'])
        self.assertEqual(snapshot['objects'],['A','B']);self.assertEqual(snapshot['scope'],spec['scope'])
        self.assertEqual([q['text'] for q in snapshot['questions']],[q['text'] for q in spec['questions']])
        self.assertTrue(all(q['answer_state']=='unknown' for q in snapshot['questions']))
        self.assertIn('artifact_error',snapshot)
        self.assertEqual(P.resume(state,compact=True)['research_focus'],snapshot)
        with self.assertRaises((R.CommitmentError,OSError)):R.closure(state)

if __name__=='__main__':unittest.main()
