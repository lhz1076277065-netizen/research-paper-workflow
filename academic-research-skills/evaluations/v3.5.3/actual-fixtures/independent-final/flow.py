from pathlib import Path
import subprocess,json,time,os,sys,datetime,hashlib
ROOT=Path(__file__).resolve().parent
BASE=Path('/Users/luca/Documents/ChatGPT/学术skill/iteration-v340-20261004/repository/academic-research-skills/skills/research-paper-workflow')
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(ROOT/'.mpl'),XDG_CACHE_HOME=str(ROOT/'.cache'))
def run(script,*args):
 cmd=[sys.executable,str(BASE/'scripts'/script),*map(str,args)];t=time.monotonic()
 r=subprocess.run(cmd,cwd=ROOT,env=ENV,text=True,capture_output=True)
 with (ROOT/'actions.jsonl').open('a') as f:f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':cmd,'elapsed_seconds':time.monotonic()-t,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},ensure_ascii=False)+'\n')
 try:d=json.loads(r.stdout);print(json.dumps({k:d[k] for k in ('status','capability','guide_path','allowed','error') if k in d},ensure_ascii=False))
 except ValueError:d=r.stdout;print(r.stdout[:1500])
 if r.stderr:print(r.stderr,file=sys.stderr)
 if r.returncode:raise RuntimeError('Tool rejected action; evidence preserved')
 return d
def begin(key,cap,inputs):
 args=['begin','--capability',cap,'--task',ROOT/'request.md','--phase',ROOT/'phase.json','--cache','/Users/luca/.codex/academic-research-source-cache','--out',ROOT/(key+'-start.json')]
 for name in inputs:args+=['--input',ROOT/name]
 return run('professional_flow.py',*args)
def finish(key,actions,outputs,functions_run=False):
 s=json.loads((ROOT/(key+'-start.json')).read_text())
 (ROOT/(key+'-work.json')).write_text(json.dumps({'step_id':s['id'],'scope':'requested_step','omitted_required_work':[],'functions_run':functions_run,'actions':actions},ensure_ascii=False,indent=2))
 args=['finish','--started',ROOT/(key+'-start.json'),'--work-report',ROOT/(key+'-work.json'),'--out',ROOT/(key+'-finish.json')]
 for name in outputs:args+=['--output',ROOT/name]
 run('professional_flow.py',*args)
 return run('professional_flow.py','check','--started',ROOT/(key+'-start.json'),'--finished',ROOT/(key+'-finish.json'))
def action(key,name,excerpt,applied,source_file=None):
 s=json.loads((ROOT/(key+'-start.json')).read_text());rel=source_file or str(Path(s['source']['entry']).relative_to(s['source']['root']))
 return {'source_file':rel,'source_excerpt':excerpt,'applied':applied,'output':str(ROOT/name),'output_excerpt':(ROOT/name).read_text()}
