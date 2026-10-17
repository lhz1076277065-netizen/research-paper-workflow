from pathlib import Path
import subprocess,json,sys,hashlib,time
ROOT=Path(__file__).resolve().parent
REPO=Path('/Users/luca/Documents/ChatGPT/学术skill/iteration-v340-20261004/repository/academic-research-skills')
PY='/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
def run(script,*args):
 cmd=[PY,str(REPO/'scripts'/script),*map(str,args)]
 r=subprocess.run(cmd,capture_output=True,text=True)
 with (ROOT/'commands.jsonl').open('a') as f:f.write(json.dumps({'time_ns':time.time_ns(),'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr},ensure_ascii=False)+'\n')
 print(json.dumps({"script":script,"rc":r.returncode,"summary":(r.stdout or r.stderr)[:900]},ensure_ascii=False))
 if r.returncode:raise RuntimeError('command failed; preserved in commands.jsonl')
 return json.loads(r.stdout)
def finish(name,outputs,excerpt,applied,functions=False):
 s=json.loads((ROOT/(name+'-start.json')).read_text());source=Path(s['source']['entry']).relative_to(s['source']['root']).as_posix()
 actions=[]
 for out in outputs:
  p=ROOT/out
  try:txt=p.read_text();binary=False
  except UnicodeDecodeError:binary=True
  a={'source_file':source,'source_excerpt':excerpt,'applied':applied,'output':str(p)}
  if binary:a.update(output_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),observation='Opened/rendered binary output and checked its intended scientific content; see associated text output.')
  else:a['output_excerpt']=txt[:min(250,len(txt))]
  actions.append(a)
 report={'step_id':s['id'],'scope':'requested_step','omitted_required_work':[],'functions_run':functions,'actions':actions}
 (ROOT/(name+'-work.json')).write_text(json.dumps(report,indent=2))
 opts=[]
 for o in outputs:opts+=['--output',ROOT/o]
 run('professional_flow.py','finish','--started',ROOT/(name+'-start.json'),*opts,'--work-report',ROOT/(name+'-work.json'),'--mode','adapted_in_host','--out',ROOT/(name+'-finish.json'))
 run('professional_flow.py','check','--started',ROOT/(name+'-start.json'),'--finished',ROOT/(name+'-finish.json'))
def begin(name,cap,inputs,purpose='formal',source=None):
 opts=[]
 for i in inputs:opts+=['--input',ROOT/i]
 if source:opts+=['--source',source]
 return run('professional_flow.py','begin','--capability',cap,'--phase',ROOT/'phase.json','--task',ROOT/'request.md',*opts,'--purpose',purpose,'--profile','full','--cache','/Users/luca/.codex/academic-research-source-cache','--allow-network','--out',ROOT/(name+'-start.json'))
if __name__=='__main__':pass
