from pathlib import Path
import subprocess,json,datetime,os
ROOT=Path(__file__).resolve().parent
PY='/Users/luca/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
SK=Path('/Users/luca/Documents/ChatGPT/学术skill/iteration-v340-20261004/repository/academic-research-skills/skills/research-paper-workflow/scripts')
def run(label,args):
 r=subprocess.run(args,capture_output=True,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
 (ROOT/(label+'.stdout.json')).write_text(r.stdout);(ROOT/(label+'.stderr.txt')).write_text(r.stderr)
 with (ROOT/'execution.jsonl').open('a') as f:f.write(json.dumps({'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':label,'args':args,'returncode':r.returncode},ensure_ascii=False)+'\n')
 print(label,r.returncode,r.stdout,r.stderr)
 if r.returncode:raise RuntimeError(label)
 return json.loads(r.stdout) if r.stdout.lstrip().startswith("{") else r.stdout
def begin(label,cap,inputs,profile=None):
 args=[PY,str(SK/'professional_flow.py'),'begin','--compact','--capability',cap,'--task',str(ROOT/'request.md'),'--phase',str(ROOT/'phase.json'),'--out',str(ROOT/(label+'-start.json'))]
 for p in inputs:args+=['--input',str(ROOT/p)]
 if profile:args+=['--profile',profile]
 return run(label+'-begin',args)
def finish(label,output,excerpt,applied,source_excerpt,functions=False):
 s=json.loads((ROOT/(label+'-start.json')).read_text());rel=str(Path(s['source']['entry']).relative_to(s['source']['root']))
 report={'step_id':s['id'],'scope':'requested_step','omitted_required_work':[],'functions_run':functions,'actions':[{'source_file':rel,'source_excerpt':source_excerpt,'applied':applied,'output':str(ROOT/output),'output_excerpt':excerpt}]}
 (ROOT/(label+'-work.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 run(label+'-finish',[PY,str(SK/'professional_flow.py'),'finish','--started',str(ROOT/(label+'-start.json')),'--output',str(ROOT/output),'--work-report',str(ROOT/(label+'-work.json')),'--out',str(ROOT/(label+'-finish.json'))])
 run(label+'-check',[PY,str(SK/'professional_flow.py'),'check','--started',str(ROOT/(label+'-start.json')),'--finished',str(ROOT/(label+'-finish.json'))])
def advance(stage,evidence,labels):
 args=[PY,str(SK/'phase_control.py'),'--state',str(ROOT/'phase.json'),'advance','--stage',stage,'--evidence',str(ROOT/evidence),'--root',str(ROOT),'--next-action',stage+' bounded synthetic validation']
 for label in labels:args+=['--professional-started',str(ROOT/(label+'-start.json')),'--professional-finished',str(ROOT/(label+'-finish.json'))]
 return run('advance-'+stage,args)
