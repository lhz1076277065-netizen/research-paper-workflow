from pathlib import Path
import subprocess,json,time,os,sys,datetime,hashlib
ROOT=Path(__file__).resolve().parent
BASE=Path('/Users/luca/Documents/ChatGPT/学术skill/iteration-v340-20261004/repository/academic-research-skills/skills/research-paper-workflow')
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',MPLCONFIGDIR=str(ROOT/'.mpl'),XDG_CACHE_HOME=str(ROOT/'.cache'))
def run(script,*args):
 cmd=[sys.executable,str(BASE/'scripts'/script),*map(str,args)]
 t=time.time(); r=subprocess.run(cmd,cwd=ROOT,env=ENV,text=True,capture_output=True)
 with (ROOT/'actions.jsonl').open('a') as f: f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':cmd,'elapsed_seconds':time.time()-t,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},ensure_ascii=False)+'\n')

 if r.stdout.strip().startswith('{'):
  try:
   shown=json.loads(r.stdout);print(json.dumps({k:shown[k] for k in ['status','capability','guide_path','returncode','allowed','error'] if k in shown},ensure_ascii=False))
  except ValueError:print(r.stdout[:1000])
 else:print(r.stdout[:1000])
 print(r.stderr,file=sys.stderr)
 if r.returncode:raise RuntimeError('Command failed; original evidence retained')
 return json.loads(r.stdout) if r.stdout.strip().startswith('{') else r.stdout

def begin(key,cap,inputs,source=None):
 args=['begin','--capability',cap,'--task',ROOT/'request.md','--phase',ROOT/'phase.json','--cache','/Users/luca/.codex/academic-research-source-cache','--out',ROOT/(key+'-start.json')]
 for path in inputs:args += ['--input',ROOT/path]
 if source:args += ['--source',source]
 return run('professional_flow.py',*args)

def finish(key,source_text,applied,outputs,excerpts=None,functions_run=False):
 s=json.loads((ROOT/(key+'-start.json')).read_text()); rel=str(Path(s['source']['entry']).relative_to(s['source']['root']))
 actions=[]
 for idx,name in enumerate(outputs):
  p=ROOT/name;a={'source_file':rel,'source_excerpt':source_text,'applied':applied,'output':str(p)}
  try:
   body=p.read_text();a['output_excerpt']=excerpts[idx] if excerpts else body
  except UnicodeDecodeError:
   a.update(output_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),observation=applied+'；已读取产物实际数字或最终画面。')
  actions.append(a)
 (ROOT/(key+'-work.json')).write_text(json.dumps({'step_id':s['id'],'scope':'requested_step','omitted_required_work':[],'functions_run':functions_run,'actions':actions},ensure_ascii=False,indent=2)+'\n')
 args=['finish','--started',ROOT/(key+'-start.json'),'--work-report',ROOT/(key+'-work.json'),'--out',ROOT/(key+'-finish.json')]
 for name in outputs:args+=['--output',ROOT/name]
 run('professional_flow.py',*args)
 return run('professional_flow.py','check','--started',ROOT/(key+'-start.json'),'--finished',ROOT/(key+'-finish.json'))
if __name__=='__main__':
 if sys.argv[1]=='begin':begin(sys.argv[2],sys.argv[3],sys.argv[4:])
 else:run(sys.argv[1],*sys.argv[2:])
