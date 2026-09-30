#!/usr/bin/env python3
"""Engineering-only tests. Synthetic fixtures are NOT academic evidence.

Runs entirely with Python's standard library. Does not call any model, network,
external database, journal, or publication system.
"""
from __future__ import annotations
import copy
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(p for p in (ROOT/'skills').iterdir() if p.is_dir())
STAMP = '2026-09-29T00:00:00+00:00'

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def load_validator(skill):
    path=skill/'scripts/validate_run.py'
    spec=importlib.util.spec_from_file_location('validator_'+skill.name.replace('-','_'),path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def cli(skill,name,*args):
    return subprocess.run([sys.executable,'-S','-B',str(skill/'scripts'/name),*map(str,args)],
        capture_output=True,text=True,timeout=12,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})

def create_fixture(skill,run,completed=False):
    """Explicitly synthetic software test fixture; no scientific inference."""
    run.mkdir(parents=True)
    (run/'outputs').mkdir()
    cfg=read(skill/'assets/contract.json')
    d=read(skill/'assets/run.template.json')
    d.update(run_id='RUN-engineering-fixture',created_at=STAMP,updated_at=STAMP,
             request='Synthetic engineering test, not real research.',
             scope='Validate the record checker with fictional test payloads only.')
    (run/cfg['records_file']).write_text('',encoding='utf-8')
    if completed:
        v=load_validator(skill)
        d['sources']=[{'id':'SRC-fixture','kind':'user_material','locator':'synthetic:test-fixture',
            'title':'SYNTHETIC SOFTWARE FIXTURE, NOT A PAPER','version':'test-v1',
            'checked_at':STAMP,'access_level':'local test string','verification_status':'verified',
            'notes':'This only verifies a software test input; not a scientific source.'}]
        for i,o in enumerate(d['outputs']):
            path=f'outputs/fixture-{i}.txt'
            (run/path).write_text('SYNTHETIC SOFTWARE TEST ARTIFACT ONLY\n'+o['role']+'\n',encoding='utf-8')
            aid=f'ART-{i:03d}'
            d['artifacts'].append({'id':aid,'path':path,'role':o['role'],
                'sha256':v.sha256_file(run/path),'depends_on':['SRC-fixture'],
                'generation_method':'Deterministic synthetic engineering fixture.'})
            o.update(status='produced',artifact_id=aid)
        rec=read(skill/'assets/record.template.json')
        rec.update(id='REC-fixture',status='observed',created_at=STAMP,
                   source_refs=['SRC-fixture'],artifact_refs=[d['artifacts'][0]['id']])
        rec['fields']={k:'SYNTHETIC TEST VALUE, NOT RESEARCH' for k in rec['fields']}
        (run/cfg['records_file']).write_text(json.dumps(rec,ensure_ascii=False)+'\n',encoding='utf-8')
        for g in d['gates']:
            g.update(status='pass',reason='Synthetic gate statement used to exercise structure only.',
                     evidence_refs=['REC-fixture'])
        d['status']='completed'
    save(run/'run.json',d)
    return d

class IsolatedSkillTests(unittest.TestCase):
    pass

def make_isolation_test(original,mode):
    def test(self):
        with tempfile.TemporaryDirectory(prefix='academic-skill-isolated-') as temp:
            base=Path(temp)
            # No siblings or central shared directory are copied.
            skill=base/'only-skill'/original.name
            shutil.copytree(original,skill,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            self.assertFalse((base/'docs').exists())
            self.assertEqual(read(skill/'assets/contract.json')['required_other_skills'],[])
            if mode=='links_and_frontmatter':
                text=(skill/'SKILL.md').read_text()
                self.assertTrue(text.startswith('---\n'))
                front=text.split('---',2)[1]
                name=re.search(r'^name:\s*(.+)$',front,re.M).group(1).strip()
                self.assertEqual(name,skill.name)
                self.assertLessEqual(len(name),64)
                self.assertRegex(name,r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
                desc=json.loads(re.search(r'^description:\s*(.+)$',front,re.M).group(1))
                self.assertLessEqual(len(desc),1024)
                self.assertLess(len(text.splitlines()),500)
                for md in skill.rglob('*.md'):
                    for ref in re.findall(r'\]\(([^)]+)\)',md.read_text()):
                        if re.match(r'^(https?:|#|mailto:)',ref):continue
                        target=(md.parent/ref.split('#')[0]).resolve()
                        self.assertTrue(target.is_relative_to(skill.resolve()),(md,ref))
                        self.assertTrue(target.exists(),(md,ref))
                for py in skill.rglob('*.py'):
                    compile(py.read_text(),str(py),'exec')
                for js in skill.rglob('*.json'):read(js)
            elif mode=='initialize_and_check':
                run=base/'new-run'
                result=cli(skill,'init_run.py',run,'--request','Standalone structural smoke test')
                self.assertEqual(result.returncode,0,result.stderr)
                result=cli(skill,'validate_run.py',run)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                report=json.loads(result.stdout)
                self.assertEqual(report['status'],'structure_passed')
                self.assertFalse(report['scientific_validity_certified'])
                self.assertEqual(report['artifact_count'],0)
            elif mode=='empty_cannot_complete':
                run=base/'new-run'
                self.assertEqual(cli(skill,'init_run.py',run).returncode,0)
                result=cli(skill,'validate_run.py',run,'--completion')
                self.assertNotEqual(result.returncode,0)
                d=read(run/'run.json');d['status']='completed';save(run/'run.json',d)
                result=cli(skill,'validate_run.py',run)
                self.assertNotEqual(result.returncode,0)
            elif mode=='synthetic_completion_structure':
                run=base/'fixture'
                create_fixture(skill,run,completed=True)
                result=cli(skill,'validate_run.py',run,'--completion')
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                report=json.loads(result.stdout)
                self.assertEqual(report['status'],'recorded_completion_checks_passed')
                self.assertFalse(report['scientific_validity_certified'])
                self.assertFalse(report['external_sources_verified_by_this_script'])
    return test

for skill in SKILLS:
    for mode in ['links_and_frontmatter','initialize_and_check','empty_cannot_complete','synthetic_completion_structure']:
        setattr(IsolatedSkillTests,'test_'+skill.name.replace('-','_')+'__'+mode,make_isolation_test(skill,mode))

class ValidatorNegativeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='academic-negative-test-')
        self.root=Path(self.temp.name)
        self.skill=ROOT/'skills/paper-deep-reading'
        self.run=self.root/'fixture'
        self.data=create_fixture(self.skill,self.run,completed=True)
        self.v=load_validator(self.skill)
        self.cfg=read(self.skill/'assets/contract.json')
    def tearDown(self):self.temp.cleanup()
    def check_bad(self):
        save(self.run/'run.json',self.data)
        report=self.v.validate(self.run,self.skill,True)
        self.assertTrue(report['errors'],report)
        return report
    def record(self):return read(self.run/self.cfg['records_file'])
    def set_record(self,record):
        (self.run/self.cfg['records_file']).write_text(json.dumps(record,ensure_ascii=False)+'\n',encoding='utf-8')
    def test_checksum_tamper(self):
        (self.run/self.data['artifacts'][0]['path']).write_text('changed after registration')
        self.check_bad()
    def test_missing_artifact(self):
        (self.run/self.data['artifacts'][0]['path']).unlink();self.check_bad()
    def test_absolute_path(self):
        self.data['artifacts'][0]['path']='/tmp/elsewhere';self.check_bad()
    def test_windows_absolute_path(self):
        self.data['artifacts'][0]['path']='C:/Windows/file';self.check_bad()
    def test_parent_traversal(self):
        self.data['artifacts'][0]['path']='../outside';self.check_bad()
    def test_symlink_escape(self):
        outside=self.root/'outside.txt';outside.write_text('outside')
        (self.run/'escape').symlink_to(outside)
        self.data['artifacts'][0]['path']='escape';self.check_bad()
    def test_duplicate_artifact_id(self):
        self.data['artifacts'][1]['id']=self.data['artifacts'][0]['id'];self.check_bad()
    def test_duplicate_source_id(self):
        self.data['sources'].append(copy.deepcopy(self.data['sources'][0]));self.check_bad()
    def test_duplicate_physical_file(self):
        self.data['artifacts'][1]['path']=self.data['artifacts'][0]['path'];self.check_bad()
    def test_artifact_cycle(self):
        self.data['artifacts'][0]['depends_on']=[self.data['artifacts'][1]['id']]
        self.data['artifacts'][1]['depends_on']=[self.data['artifacts'][0]['id']]
        self.check_bad()
    def test_unknown_dependency(self):
        self.data['artifacts'][0]['depends_on']=['NOT-KNOWN'];self.check_bad()
    def test_self_dependency(self):
        self.data['artifacts'][0]['depends_on']=[self.data['artifacts'][0]['id']];self.check_bad()
    def test_missing_required_gate(self):
        self.data['gates'].pop();self.check_bad()
    def test_missing_output_declaration(self):
        self.data['outputs'].pop();self.check_bad()
    def test_unproduced_output(self):
        self.data['outputs'][0]['status']='planned';self.check_bad()
    def test_wrong_output_artifact(self):
        self.data['outputs'][0]['artifact_id']='NOT-KNOWN';self.check_bad()
    def test_output_role_mismatch(self):
        self.data['artifacts'][0]['role']='wrong-role';self.check_bad()
    def test_narrowed_scope_without_reason(self):
        self.data['outputs'][0].update(required=False,status='not_applicable',reason='');self.check_bad()
    def test_gate_unknown(self):
        self.data['gates'][0]['status']='unknown';self.check_bad()
    def test_gate_no_evidence(self):
        self.data['gates'][0]['evidence_refs']=[];self.check_bad()
    def test_gate_unresolved_reference(self):
        self.data['gates'][0]['evidence_refs']=['MISSING'];self.check_bad()
    def test_gate_no_reason(self):
        self.data['gates'][0]['reason']='';self.check_bad()
    def test_blocked_external_dependency(self):
        self.data['external_dependencies']=[{'description':'Missing required human approval',
            'status':'pending','blocks_current_scope':True,'required_action':'Confirm with actual authority','evidence_refs':[]}]
        self.check_bad()
    def test_no_records(self):
        (self.run/self.cfg['records_file']).write_text('');self.check_bad()
    def test_draft_record(self):
        r=self.record();r['status']='draft';self.set_record(r);self.check_bad()
    def test_template_record_not_observation(self):
        r=self.record();r['fields']={k:None for k in r['fields']};self.set_record(r);self.check_bad()
    def test_record_no_evidence(self):
        r=self.record();r['source_refs']=[];r['artifact_refs']=[];self.set_record(r);self.check_bad()
    def test_record_unknown_source(self):
        r=self.record();r['source_refs']=['MISSING'];self.set_record(r);self.check_bad()
    def test_record_missing_field(self):
        r=self.record();r['fields'].pop(next(iter(r['fields'])));self.set_record(r);self.check_bad()
    def test_wrong_contract(self):
        self.data['schema_version']='old';self.check_bad()
    def test_other_skill(self):
        self.data['skill']='another-skill';self.check_bad()
    def test_empty_request(self):
        self.data['request']='   ';self.check_bad()
    def test_timestamp_missing_zone(self):
        self.data['created_at']='2026-09-29T12:00:00';self.check_bad()
    def test_verified_source_requires_timestamp(self):
        self.data['sources'][0]['checked_at']=None;self.check_bad()
    def test_dependency_unknown_evidence(self):
        self.data['external_dependencies']=[{'description':'Test dependency',
            'status':'resolved','blocks_current_scope':False,'required_action':'',
            'evidence_refs':['NOT-KNOWN']}]
        self.check_bad()
    def test_input_dependency_is_recognized(self):
        self.data['inputs']=[{'id':'INPUT-test','locator':'synthetic:test-input',
            'version':'test-v1','access_notes':'Synthetic input, not actual data.'}]
        self.data['artifacts'][0]['depends_on']=['INPUT-test']
        save(self.run/'run.json',self.data)
        self.assertFalse(self.v.validate(self.run,self.skill,True)['errors'])
    def test_schema_rejects_unknown_keywords(self):
        self.assertTrue(self.v.check_schema({}, {'type':'object','madeUpValidation':True}))
    def test_schema_boolean_not_integer(self):
        self.assertTrue(self.v.check_schema(True,{'type':'integer'}))
    def test_init_refuses_overwrite(self):
        before=(self.run/'run.json').read_bytes()
        result=cli(self.skill,'init_run.py',self.run)
        self.assertNotEqual(result.returncode,0)
        self.assertEqual(before,(self.run/'run.json').read_bytes())
    def test_register_real_file_no_gate_changes(self):
        run=self.root/'draft';create_fixture(self.skill,run)
        (run/'outputs/a.md').write_text('SYNTHETIC TEST FILE')
        result=cli(self.skill,'register_artifact.py',run,'--path','outputs/a.md','--id','ART-new',
                   '--role',self.cfg['output_roles'][0])
        self.assertEqual(result.returncode,0,result.stderr)
        d=read(run/'run.json')
        self.assertEqual(d['status'],'draft')
        self.assertTrue(all(g['status']=='unknown' for g in d['gates']))
        self.assertEqual(d['artifacts'][0]['sha256'],self.v.sha256_file(run/'outputs/a.md'))
        self.assertFalse(self.v.validate(run,self.skill)['errors'])
    def test_register_refuses_duplicate(self):
        a=self.data['artifacts'][0]
        result=cli(self.skill,'register_artifact.py',self.run,'--path',a['path'],'--id',a['id'],'--role',a['role'])
        self.assertNotEqual(result.returncode,0)
    def test_register_refuses_existing_lock(self):
        lock=self.run/'.run-write.lock';lock.write_text('other writer')
        (self.run/'outputs/new.md').write_text('TEST')
        before=(self.run/'run.json').read_bytes()
        result=cli(self.skill,'register_artifact.py',self.run,'--path','outputs/new.md','--id','ART-new','--role','extra')
        self.assertNotEqual(result.returncode,0)
        self.assertTrue(lock.exists())
        self.assertEqual(before,(self.run/'run.json').read_bytes())
    def test_register_refuses_missing_file(self):
        result=cli(self.skill,'register_artifact.py',self.run,'--path','outputs/missing','--id','ART-new','--role','extra')
        self.assertNotEqual(result.returncode,0)
    def test_register_refuses_self_registration(self):
        result=cli(self.skill,'register_artifact.py',self.run,'--path','run.json','--id','ART-new','--role','extra')
        self.assertNotEqual(result.returncode,0)
    def test_register_refuses_path_escape(self):
        result=cli(self.skill,'register_artifact.py',self.run,'--path','../outside','--id','ART-new','--role','extra')
        self.assertNotEqual(result.returncode,0)

if __name__=='__main__':
    unittest.main(verbosity=2)
