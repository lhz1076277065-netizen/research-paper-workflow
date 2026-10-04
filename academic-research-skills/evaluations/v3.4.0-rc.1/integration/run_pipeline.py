import csv,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'integration';source=root/'repository/academic-research-skills/src/common/scripts'
def mod(name):
 s=importlib.util.spec_from_file_location(name,source/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
P=mod('phase_control');receipts=[]
def execute(uid,rel,args,timeout=60,cwd=None):
 d=json.loads((out/'prepared'/(uid+'.json')).read_text());cmd=[sys.executable,str(Path(d['root'])/rel),*map(str,args)];start=time.monotonic()
 env=dict(os.environ,MPLBACKEND='Agg',PAPER_SEARCH_TIMEOUT_SECONDS='12',PAPER_SEARCH_CONNECT_TIMEOUT_SECONDS='8',PAPER_SEARCH_MAX_ATTEMPTS='2',PAPER_SEARCH_SOURCE_TIMEOUT_SECONDS='40')
 p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout,cwd=cwd or out,env=env)
 (out/(uid+'-stdout.log')).write_text(p.stdout);(out/(uid+'-stderr.log')).write_text(p.stderr)
 receipts.append({'id':uid,'command':cmd,'returncode':p.returncode,'seconds':time.monotonic()-start,'stdout':uid+'-stdout.log','stderr':uid+'-stderr.log'})
 (out/'command-receipts.json').write_text(json.dumps(receipts,indent=2));return p
# Paired, deterministic software fixture; no scientific dataset or statistical claim.
rows=[];work=out/'launch-fixture';work.mkdir(exist_ok=True)
for i in range(12):
 expired=i<6
 for method in ['direct','phase_control']:
  marker=work/(str(i)+'-'+method+'.txt');marker.unlink(missing_ok=True)
  cmd=[sys.executable,'-c',f'from pathlib import Path;Path({str(marker)!r}).write_text("executed fixture command")']
  start=time.monotonic()
  if method=='direct':
   p=subprocess.run(cmd,capture_output=True);rc=p.returncode;allowed=True
  else:
   s=P.init('full','software launch acceptance fixture',minutes=1)
   if expired:s['deadline']=time.time()-1;s['project_deadline']=s['deadline']
   state=work/(str(i)+'.json');P.save(state,s)
   try:r=P.run(state,cmd,work/(str(i)+'.log'),'expired jobs must not start','reject start when expired',estimate=.05);rc=r['returncode'];allowed=True
   except P.PhaseError:rc=None;allowed=False
  rows.append({'trial':i,'state':'expired' if expired else 'active','method':method,'started':int(marker.exists()),'wall_seconds':time.monotonic()-start,'expected_controlled_start':int(not expired)})
with (out/'launch-results.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
assert sum(r['started'] for r in rows if r['method']=='phase_control' and r['state']=='expired')==0
assert sum(r['started'] for r in rows if r['method']=='phase_control' and r['state']=='active')==6
# Native upstream bounded CSV profile, not just a borrowed function.
p=execute('kdense-eda','skills/exploratory-data-analysis/scripts/tabular_profile.py',[out/'launch-results.csv','--root',out,'--output',out/'kdense-profile.json','--reveal-identifiers','--force']);assert p.returncode==0,p.stderr
p=execute('scipilot-figure','scripts/profile_data.py',[out/'launch-results.csv','--group','method']);assert p.returncode==0,p.stderr
# Real small metadata-source search; no original research topic.
p=execute('researchstudio-search','ResearchStudio-Idea/skills/paper_search/scripts/search_papers.py',['--query','reproducible computational research','--start-year','2010','--end-year','2026','--max-papers','3','--sources','crossref','--json',out/'search-results.json'],timeout=60)
print(json.dumps({'launch_rows':len(rows),'native_calls':receipts},ensure_ascii=False))
