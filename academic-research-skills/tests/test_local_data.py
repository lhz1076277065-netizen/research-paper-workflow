"""Actual receipts/files/process gates; fixtures are not scientific validation."""
import contextlib, io, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import artifact_io as A
import capabilities as C
import professional_flow as F
import phase_control as P
import local_data as D
import research_storage as S

class LocalFlow(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve();self.n=0
        self.task=self.root/'request.md';self.task.write_text('Fixture: complete a two-dataset local study.')
        self.material=self.root/'materials.md';self.material.write_text('Fixture supplied constraints.')
        self.guide='Read the actual inputs and report a reproducible comparison with limitations.'
        caps=['topic-novelty','research-design','data-discovery','data-preparation','analysis-execution','robustness-reproducibility','scientific-visualization','manuscript-writing','citation-audit','manuscript-review','final-expression']
        cap=dict(id='fixture',repository='owner/repo',commit='a'*40,tree='b'*40,entry='SKILL.md',kind='skill_protocol',roles=['research'],dependencies=[],host_adaptation='Software fixture',required_files=[dict(path='SKILL.md',blob=C.blob(self.guide.encode()))])
        self.idx={'capabilities':[cap],'professional_routes':{k:dict(primary='fixture',alternatives=[],work='Use inputs',boundary='Fixture only') for k in caps}}
        self.index=self.root/'index.json';P.save(self.index,self.idx)
        self.cache=self.root/'cache';p=self.cache/'fixture'/('a'*40)/'SKILL.md';p.parent.mkdir(parents=True);p.write_text(self.guide)
        self.phase=self.root/'phase.json';P.save(self.phase,P.init('full','Fixture local research',autonomous_plan=True,workflow='local-data'))
        self.mock_index=patch.object(C,'index_path',return_value=self.index);self.mock_index.start()
        self.step('topic-novelty');self.advance('design')
        self.planfile=self.root/'research-plan.md';self.step('research-design',outputs={self.planfile:'Fixture plan: evaluate both A and B using the specified model and split.'})
        self.advance('data')
        self.discovery=self.begin('data-discovery',inputs=[self.planfile])
        self.spec=self.root/'spec.json';P.save(self.spec,{'datasets':[{'id':k,'purpose':'Fixture '+k,'files':[{'path':k+'.csv','format':'csv','required_columns':['x','target'],'numeric_columns':['x','target'],'expected_rows':2}]} for k in ('a','b')]})
        state=P.load(self.phase);D.plan(state,self.root,self.spec,self.planfile);P.save(self.phase,state)
        S.plan(self.root,{'needs':[{'purpose':'Fixture both datasets','subset':'two small tables','access':'fixture files'}],'expected_download_bytes':10000,'expected_peak_project_bytes':10_000_000})
        state=P.load(self.phase);state['storage']={'root':str(self.root),'id':S.read(self.root)['id']};P.save(self.phase,state)
    def tearDown(self):self.mock_index.stop();self.tmp.cleanup()
    def begin(self,cap,inputs=None):
        if inputs is None and cap in D.INPUT_GROUPS:
            inputs=[];state=P.load(self.phase);rows=state.get('professional_steps',[])+state.get('professional_pending',[])
            for group in D.INPUT_GROUPS[cap]:
                row=next((x for x in reversed(rows) if x['capability'] in group and x.get('finished')),None)
                if row:inputs.extend(Path(x['path']) for x in P.load(row['finished'])['outputs'])
        self.n+=1;name=f'{self.n}-{cap}';start=F.begin(self.idx,cap,self.task,inputs or [self.material],self.cache,phase=self.phase)
        p=self.root/(name+'-start.json');F.persist(start,p);return start,p,name
    def step(self,cap,outputs=None,inputs=None):
        return self.finish(self.begin(cap,inputs),outputs)
    def finish(self,begun,outputs=None):
        start,p,name=begun
        outputs=outputs or {self.root/(name+'.md'):'Fixture result with reproducible constraints and limitations.'}
        for f,v in outputs.items():f.parent.mkdir(parents=True,exist_ok=True);f.write_text(v)
        work=self.root/(name+'-work.json');P.save(work,dict(step_id=start['id'],scope='requested_step',omitted_required_work=[],functions_run=False,actions=[dict(source_file='SKILL.md',source_excerpt=self.guide,applied='Read supplied fixture constraints and computed the fixture result.',output=str(f),output_excerpt=v) for f,v in outputs.items()]))
        done=F.finish(self.idx,start,list(outputs),work,'adapted_in_host');end=self.root/(name+'-finish.json');F.persist(done,end,start)
        return p,end
    def advance(self,following):
        state=P.load(self.phase);rows=[x for x in state['professional_pending'] if x['status']!='cancelled']
        evidence=self.root/('exit-'+state['stage']+'.md');evidence.write_text('Fixture stage artifacts are ready for the requested next work.')
        checked=P.professional_exit(state,[x['started'] for x in rows],[x['finished'] for x in rows])
        P.advance(state,following,evidence,self.root,'Continue fixture work');P.consume_professional(state,checked);P.save(self.phase,state)
    def acquire(self):
        meta=self.root/'metadata.md';selection=self.root/'selection.md'
        start,end=self.finish(self.discovery,outputs={meta:'Fixture source schema and coverage for both tables.',selection:'Fixture comparison selected both tables for distinct planned tests.'})
        state=P.load(self.phase)
        for k in ('a','b'):
            (self.root/(k+'.csv')).write_text('x,target\n1,0\n2,1\n')
            D.source(state,k,meta,selection,start,end,'Fixture publisher','Fixture v1','https://example.org/fixture')
        return state
    def research(self):
        self.acquire();self.step('data-preparation',inputs=[self.root/'a.csv',self.root/'b.csv']);self.advance('research');return P.load(self.phase)
    def manuscript(self):
        self.research()
        for cap in ('analysis-execution','robustness-reproducibility','scientific-visualization'):self.step(cap)
        self.advance('manuscript');return P.load(self.phase)
    def test_missing_second_required_dataset_prevents_preparation(self):
        state=self.acquire();(self.root/'b.csv').unlink()
        self.assertFalse(D.check(state,False)['ready'])
        with self.assertRaises(D.DataError):self.begin('data-preparation')
        self.assertEqual(P.load(self.phase)['status'],'active')
    def test_missing_source_is_not_local_readiness(self):
        (self.root/'a.csv').write_text('x,target\n1,0\n2,1\n')
        self.assertFalse(D.check(P.load(self.phase),False)['ready'])
    def test_local_only_does_not_certify_parse(self):
        state=self.acquire();(self.root/'b.csv').write_text('x,target\n1,0\ntruncated\n')
        self.assertTrue(D.check(state,False)['ready']);self.assertFalse(D.check(state)['ready'])
    def test_missing_variables_rejects_experiment_stage(self):
        state=self.acquire();(self.root/'b.csv').write_text('wrong,target\n1,0\n2,1\n')
        self.step('data-preparation')
        with self.assertRaises(D.DataError):self.advance('research')
        self.assertEqual(P.load(self.phase)['stage'],'data')
    def test_all_required_local_files_and_preparation_allow_real_process(self):
        self.research();start,path,_=self.begin('analysis-execution');marker=self.root/'ran'
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            rc=P.main(['--state',str(self.phase),'run','--log',str(self.root/'run.log'),'--claim','Fixture claim','--decision','Fixture test','--professional-started',str(path),'--',sys.executable,'-c',f'from pathlib import Path; Path({str(marker)!r}).write_text("ran")'])
        self.assertEqual(rc,0);self.assertEqual(marker.read_text(),'ran')
    def test_removed_data_blocks_process_even_after_analysis_begin(self):
        self.research();_,path,_=self.begin('analysis-execution');(self.root/'b.csv').unlink();marker=self.root/'must-not-run'
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            rc=P.main(['--state',str(self.phase),'run','--log',str(self.root/'run.log'),'--claim','Fixture','--decision','Fixture','--professional-started',str(path),'--',sys.executable,'-c',f'from pathlib import Path; Path({str(marker)!r}).touch()'])
        self.assertEqual(rc,2);self.assertFalse(marker.exists());self.assertEqual(P.load(self.phase)['status'],'active')
    def test_data_drift_requires_versioned_repair(self):
        state=self.acquire();self.assertTrue(D.check(state)['ready']);(self.root/'b.csv').write_text('x,target\n3,0\n4,1\n')
        self.assertFalse(D.check(state)['ready'])
    def test_refresh_detects_same_size_restored_timestamp_change(self):
        state=self.acquire();D.check(state);f=self.root/'b.csv';s=f.stat();f.write_text('x,target\n3,0\n4,1\n');os.utime(f,ns=(s.st_atime_ns,s.st_mtime_ns))
        cached=D.check(state);self.assertEqual(cached['local_files_checked'][1]['verification_basis'],'unchanged_file_stat_since_full_hash')
        self.assertFalse(D.check(state,refresh=True)['ready'])
    def test_full_parse_coverage_and_checksum(self):
        state=self.acquire();r=D.check(state,refresh=True)
        self.assertTrue(r['ready']);self.assertEqual([x['inspection']['rows'] for x in r['local_files_checked']],[2,2]);self.assertFalse(r['scientific_authority_or_completeness_certified_by_tool'])
    def test_source_evidence_change_invalidates_readiness(self):
        state=self.acquire();(self.root/'metadata.md').write_text('Changed source schema');self.assertFalse(D.check(state)['ready'])
    def test_plan_change_cannot_reuse_previous_receipts(self):
        state=self.acquire();self.planfile.write_text('A different unreviewed study plan')
        with self.assertRaises(D.DataError):D.load(state)
    def test_plan_must_be_real_design_output(self):
        f=self.root/'invented.md';f.write_text('Unbound plan')
        with self.assertRaises(D.DataError):D.plan(P.load(self.phase),self.root,self.spec,f,'Changed')
    def test_repeat_plan_preserves_id_and_capacity(self):
        state=P.load(self.phase);before=json.loads(json.dumps(state['local_data']));storage=S.read(self.root)
        self.assertEqual(D.plan(state,self.root,self.spec,self.planfile)['status'],'unchanged')
        self.assertEqual(before,state['local_data']);self.assertEqual(storage,S.read(self.root))
    def test_discovery_can_create_and_complete_its_own_initial_manifest(self):
        state=self.acquire();self.assertEqual(P.load(self.root/D.NAME)['planning_step_id'],self.discovery[0]['id'])
        self.assertNotIn('local_data_id',self.discovery[0]['phase'])
        self.assertTrue(D.check(state)['ready']);self.assertEqual(D.completed(state,'data-discovery')['step_id'],self.discovery[0]['id'])
    def test_revision_preserves_quota_and_requires_current_preparation(self):
        self.acquire();self.step('data-preparation');state=P.load(self.phase);previous=state['local_data']['id'];anchor=state['budget_anchor'];storage=S.read(self.root)
        diagnosis=self.root/'diagnosis.md';diagnosis.write_text('Fixture acquisition error requires a corrected immutable version of table A.')
        self.discovery=self.begin('data-discovery',inputs=[self.planfile,diagnosis])
        revised=self.root/'spec-v2.json';spec=P.load(self.spec);spec['datasets'][0]['files'][0]['path']='a-v2.csv';P.save(revised,spec)
        state=P.load(self.phase);D.plan(state,self.root,revised,self.planfile,'Correct an acquired file with a documented version');P.save(self.phase,state)
        self.assertNotEqual(state['local_data']['id'],previous);self.assertEqual(storage,S.read(self.root));self.assertEqual(anchor,state['budget_anchor'])
        meta=self.root/'metadata-v2.md';selection=self.root/'selection-v2.md'
        start,end=self.finish(self.discovery,{meta:'Fixture corrected schema.',selection:'Fixture selection retains both required datasets.'})
        (self.root/'a-v2.csv').write_text('x,target\n3,0\n4,1\n')
        for k in ('a','b'):D.source(state,k,meta,selection,start,end,'Fixture publisher','v2','https://example.org/fixture')
        self.assertTrue(D.check(state)['ready'])
        with self.assertRaises(D.DataError):D.completed(state,'data-preparation')
        self.step('data-preparation',inputs=[self.root/'a-v2.csv',self.root/'b.csv']);self.advance('research')
        history=P.load(self.root/D.NAME)['history'];self.assertEqual(len(history),1);self.assertTrue((self.root/history[0]['previous_manifest']['path']).exists())
    def test_unbound_revised_spec_does_not_reset_acquisition(self):
        self.acquire();revised=self.root/'spec-v2.json';P.save(revised,P.load(self.spec));state=P.load(self.phase);old=state['local_data'].copy()
        with self.assertRaises(D.DataError):D.plan(state,self.root,revised,self.planfile,'Unbound revision')
        self.assertEqual(state['local_data'],old)
    def test_stopped_state_cannot_plan_new_downloads(self):
        state=P.load(self.phase);state['status']='paused'
        with self.assertRaises(D.DataError):D.plan(state,self.root,self.spec,self.planfile)
        self.assertEqual(state['status'],'paused')
    def test_capacity_repair_can_continue_without_resetting_transfer(self):
        state=self.acquire();storage=S.read(self.root);storage['downloaded_bytes']=123;S.save(self.root,storage)
        with patch.object(S,'check',return_value={'allowed':False,'reasons':['Insufficient disk reserve']}):self.assertFalse(D.check(state)['ready'])
        self.assertTrue(D.check(state)['ready']);self.assertEqual(S.read(self.root)['downloaded_bytes'],123);self.assertEqual(state['status'],'active')
    def test_capacity_failure_precedes_large_data_reading(self):
        state=self.acquire();storage=S.read(self.root);storage['downloaded_bytes']=S.LIMIT+1;S.save(self.root,storage)
        with patch.object(D,'inspect',side_effect=AssertionError('must not read')):
            self.assertFalse(D.check(state)['ready'])
    def test_wrong_storage_root_cannot_hide_project_usage(self):
        state=self.acquire();state['storage']['id']='unrelated';self.assertFalse(D.check(state)['ready'])
    def test_figures_require_actual_analysis_and_robustness(self):
        self.research()
        with self.assertRaises(D.DataError):self.begin('scientific-visualization')
        self.step('analysis-execution')
        with self.assertRaises(D.DataError):self.begin('scientific-visualization')
        self.step('robustness-reproducibility');self.step('scientific-visualization')
    def test_figures_and_models_must_consume_real_predecessor_outputs(self):
        self.research()
        with self.assertRaises(D.DataError):self.begin('analysis-execution',inputs=[self.material])
        self.step('analysis-execution');self.step('robustness-reproducibility')
        with self.assertRaises(D.DataError):self.begin('scientific-visualization',inputs=[self.material])
    def test_old_figure_does_not_complete_new_experiment_results(self):
        self.research();self.step('analysis-execution');self.step('robustness-reproducibility');self.step('scientific-visualization')
        prep=D.completed(P.load(self.phase),'data-preparation');qa=Path(P.load(prep['finished'])['outputs'][0]['path'])
        diagnosis=self.root/'analysis-diagnosis.md';diagnosis.write_text('Fixture new analysis inputs after a substantive diagnosed implementation error.')
        self.step('analysis-execution',inputs=[qa,diagnosis])
        with self.assertRaises(D.DataError):D.completed(P.load(self.phase),'robustness-reproducibility')
        self.step('robustness-reproducibility')
        with self.assertRaises(D.DataError):D.completed(P.load(self.phase),'scientific-visualization')
    def test_writing_cannot_bypass_data_and_figures(self):
        with self.assertRaises(D.DataError):self.begin('manuscript-writing')
        self.research();self.step('analysis-execution');self.step('robustness-reproducibility')
        with self.assertRaises(D.DataError):self.advance('manuscript')
    def test_polishing_requires_written_and_reviewed_manuscript(self):
        self.manuscript()
        with self.assertRaises(D.DataError):self.begin('final-expression')
        self.step('manuscript-writing')
        with self.assertRaises(D.DataError):self.begin('final-expression')
        self.step('manuscript-review');self.step('final-expression')
        with self.assertRaises(D.DataError):self.advance('delivery') # Citation audit is still required.
        self.step('citation-audit');self.advance('delivery')
    def test_complete_six_stage_flow_preserves_budget_and_closes(self):
        before=P.load(self.phase);self.manuscript()
        for cap in ('manuscript-writing','citation-audit','manuscript-review','final-expression'):self.step(cap)
        self.advance('delivery');state=P.load(self.phase);D.stage_exit(state,'completed');P.professional_exit(state,[],[])
        self.assertEqual(before['budget_anchor'],state['budget_anchor']);self.assertEqual(P.resume(state)['local_data'],state['local_data'])
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            rc=P.main(['--state',str(self.phase),'close','--status','completed','--reason','Fixture delivery ready','--evidence','exit-manuscript.md','--root',str(self.root),'--task-id','fixture'])
        self.assertEqual(rc,0);self.assertEqual(P.load(self.phase)['status'],'completed')
    def test_full_local_study_cannot_use_evidence_skip(self):
        state=P.load(self.phase)
        with self.assertRaises(P.PhaseError):P.advance(state,'manuscript',self.planfile,self.root,'Skip',skip_reason='Existing result')
    def test_headerless_tables_are_read_completely(self):
        f=self.root/'headerless';f.write_text('1,0\n2,1\n')
        self.assertEqual(D.inspect(f,dict(format='csv',header=False,columns=['x','target'],numeric_columns=['x'],expected_rows=2))['rows'],2)
    def test_external_format_needs_actual_source_gated_reader(self):
        state=self.acquire();manifest=P.load(self.root/D.NAME);manifest['datasets'][0]['files'][0]['format']='external';P.save(self.root/D.NAME,manifest)
        self.assertFalse(D.check(state)['ready'])
        start,end=self.step('data-preparation',inputs=[self.root/'a.csv',self.root/'b.csv'])
        D.external_inspection(P.load(self.phase),start,end);self.assertTrue(D.check(P.load(self.phase))['ready'])
    def test_legacy_and_focused_do_not_inherit_full_pipeline(self):
        for state in (P.init('full','Legacy'),P.init('focused','Edit supplied paragraph')):
            D.gate(state,'final-expression');D.stage_exit(state,'completed')
    def test_stream_digest_and_large_text_do_not_read_entire_file(self):
        f=self.root/'large.txt'
        with f.open('wb') as h:
            for _ in range(9):h.write(b'x'*1024*1024)
        with patch.object(Path,'read_bytes',side_effect=AssertionError('whole file read')):
            self.assertEqual(len(A.digest(f)),64);self.assertIsNone(A.output_text(f));self.assertEqual(F.ref(f)['sha256'],A.digest(f))

if __name__=='__main__':unittest.main()
