import subprocess, sys, json, datetime
from pathlib import Path
root=Path(__file__).resolve().parent.parent
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
p=subprocess.run(sys.argv[1:],cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
record={'started':started,'argv':sys.argv[1:],'exit_code':p.returncode,'output':p.stdout,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat()}
with (root/'logs'/'commands.jsonl').open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
print(p.stdout,end='')
raise SystemExit(p.returncode)
