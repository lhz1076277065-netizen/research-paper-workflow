"""Verify current generated resources and actually run each standalone copy."""
import hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE='ed4c86ec00593de48d2cb88109afe4191d1bfe04'

def old(relative):
    return subprocess.check_output(['git','show',BASE+':academic-research-skills/'+relative],cwd=ROOT)

def main():
    out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
    common=ROOT/'src/common';skills=sorted((ROOT/'skills').iterdir());checks={};copies=[]
    ui=ROOT.parent/'research-paper-workflow/agents/openai.yaml'
    checks['existing_root_UI_unchanged']=ui.read_bytes()==subprocess.check_output(['git','show',BASE+':research-paper-workflow/agents/openai.yaml'],cwd=ROOT)
    checks['nineteen_modules']=len([p for p in skills if p.is_dir()])==19
    for name in ['research-profiles.json','repository-sources.json']:
        a=json.loads(old('src/common/assets/'+name));b=json.loads((common/'assets'/name).read_text())
        a.pop('version',None);b.pop('version',None);checks[name+'_contents_retained']=a==b
    for skill in skills:
        if not skill.is_dir():continue
        protocol=skill/'references/protocol.md';checks[skill.name+'_protocol_unchanged']=protocol.read_bytes()==old(str(protocol.relative_to(ROOT)))
        entry=skill/'SKILL.md';checks[skill.name+'_entry_body_unchanged']=entry.read_bytes()==old(str(entry.relative_to(ROOT))).replace(b'3.2.0-rc.4',b'3.2.0-rc.5')
        for folder in ('scripts','references','assets'):
            for source in (common/folder).iterdir():
                if not source.is_file() or source.suffix not in {'.py','.md','.json'}:continue
                generated=skill/folder/source.name
                if not generated.is_file() or generated.read_bytes()!=source.read_bytes():raise AssertionError('Shared drift '+str(generated))
        with tempfile.TemporaryDirectory() as temp:
            standalone=Path(temp)/skill.name;shutil.copytree(skill,standalone,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
            result=subprocess.run([sys.executable,str(standalone/'scripts/selftest.py'),'--out',str(Path(temp)/'out')],capture_output=True,text=True)
            data=json.loads((Path(temp)/'out/selftest.json').read_text())
            if result.returncode or not data['passed']:raise AssertionError((skill.name,result.stdout,result.stderr))
            copies.append({'module':skill.name,'standalone_copy':True,'basic_checks':len(data['checks']),'passed':data['passed']})
    entries={}
    for skill in skills:
        if skill.is_dir():entries[skill.name]={'before_characters':len(old(str((skill/'SKILL.md').relative_to(ROOT))).decode()),'after_characters':len((skill/'SKILL.md').read_text())}
    metrics={'version':(ROOT/'VERSION').read_text().strip(),'scope':'Actual isolated module execution and static Unicode counts; reading events are separately reported, no token/cost inference.',
        'entries':entries,'quality_core_before':len(old('src/common/references/research-quality.md').decode()),'quality_core_after':len((common/'references/research-quality.md').read_text()),'examples_shards':3,'checks':checks,'standalone':copies,'passed':all(checks.values())}
    (out/'distribution.json').write_text(json.dumps(metrics,indent=2)+'\n')
    print(json.dumps({'passed':metrics['passed'],'standalone_modules':len(copies),'basic_checks':sum(c['basic_checks'] for c in copies),'quality_core_before':metrics['quality_core_before'],'quality_core_after':metrics['quality_core_after']}))
    if not metrics['passed']:raise AssertionError(checks)

if __name__=='__main__':main()
