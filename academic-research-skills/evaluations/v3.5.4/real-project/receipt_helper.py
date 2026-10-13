"""Record applied guidance and invoke the official finish/check commands.
This helper creates no professional output and cannot start a step retrospectively.
"""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
S=pathlib.Path('/Users/luca/Documents/ChatGPT/学术skill/iteration-v340-20261004/repository/academic-research-skills/scripts')

def finish(stem,outputs,excerpt,applied,source_file=None,functions_run=False):
    start=ROOT/(stem+'-start.json'); data=json.loads(start.read_text())
    entry=pathlib.Path(data['source']['entry']); origin=pathlib.Path(data['source']['root'])
    sf=source_file or entry.relative_to(origin).as_posix()
    assert excerpt in (origin/sf).read_text(),(sf,excerpt)
    actions=[]
    for name in outputs:
        p=ROOT/name; a={'source_file':sf,'source_excerpt':excerpt,'applied':applied,'output':str(p)}
        try: t=p.read_text()
        except UnicodeError: t=None
        if t is not None and len(t)>0 and len(t)<8*1024*1024:
            a['output_excerpt']=t[:min(200,len(t))]
        else:
            a['output_sha256']=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
            a['observation']=applied+' Artifact checked at '+str(p)
        actions.append(a)
    w=ROOT/(stem+'-work.json'); w.write_text(json.dumps({'step_id':data['id'],'scope':'requested_step','omitted_required_work':[], 'functions_run':functions_run,'actions':actions},indent=2))
    f=ROOT/(stem+'-finish.json')
    args=[sys.executable,str(S/'professional_flow.py'),'finish','--started',str(start),'--work-report',str(w),'--out',str(f)]
    for n in outputs: args+=['--output',str(ROOT/n)]
    subprocess.run(args,check=True)
    subprocess.run([sys.executable,str(S/'professional_flow.py'),'check','--started',str(start),'--finished',str(f)],check=True)
