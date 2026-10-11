import os,json,subprocess,urllib.request,datetime
from pathlib import Path
root=Path(__file__).resolve().parent
script=Path('/Users/luca/Documents/ChatGPT/学术skill/iteration-v340-20261004/repository/academic-research-skills/skills/data-discovery/scripts/research_storage.py')
request=urllib.request.Request('http://127.0.0.1:51068/session',data=json.dumps({'account':'fixture-researcher','accept_free_research_terms':True}).encode(),headers={'Content-Type':'application/json'},method='POST')
with urllib.request.urlopen(request,timeout=10) as response:
    data=response.read(4097)
    if len(data)>4096: raise ValueError('Oversized session response')
    session=json.loads(data)
    token=session.get('token') or session.get('access_token')
    if not token: raise ValueError('Session token absent')
os.environ['RESEARCH_DATA_TOKEN']=token
subprocess.run(['python3',str(script),'--root',str(root),'download','--url','http://127.0.0.1:51068/bundle','--output','raw/bundle.zip','--max-bytes','2307','--need','0','--token-env','RESEARCH_DATA_TOKEN','--phase',str(root/'phase.json')],check=True)
subprocess.run(['python3',str(script),'--root',str(root),'extract','--archive','raw/bundle.zip','--member','observations.csv','--output','derived','--phase',str(root/'phase.json')],check=True)
os.environ.pop('RESEARCH_DATA_TOKEN',None)
(root/'access-log.json').write_text(json.dumps({'authenticated':True,'session_endpoint':'/session','terms':'Free local fixture access; no real account or contract.','metadata_bytes':(root/'service-metadata.txt').stat().st_size,'session_response_bytes':len(data),'download_endpoint':'/bundle','selected_members':['observations.csv'],'excluded_members':['other-region.bin'],'access_time':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
