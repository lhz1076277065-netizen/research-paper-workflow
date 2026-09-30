#!/usr/bin/env python3
"""Build self-contained skill folders from shared local source; --check is read-only."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def encoded(obj):return (json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def sha(b):return hashlib.sha256(b).hexdigest()
def generated(root=ROOT):
    root=Path(root);common=root/'src/common'
    skills=sorted(p for p in (root/'skills').iterdir() if p.is_dir())
    version=(root/'VERSION').read_text().strip()
    capabilities=[s.name for s in skills]+['presentation','dissemination','workbench']
    # Deliberately empty: providers are discovered and selected for the actual task.
    catalog={'schema_version':'runtime-providers-1','package_version':version,
             'capabilities':capabilities,'providers':[],
             'discovery':'Use installed skills or current GitHub entries; source URLs are optional seeds.'}
    out={'docs/provider-catalog.json':encoded(catalog)}
    for f in (common/'scripts').glob('*.py'):
        if f.name not in {'init_run.py','register_artifact.py','validate_run.py'}:
            out['scripts/'+f.name]=f.read_bytes()
        for s in skills:out[f'skills/{s.name}/scripts/{f.name}']=f.read_bytes()
    for f in (common/'references').glob('*.md'):
        out['docs/'+f.name]=f.read_bytes()
        for s in skills:out[f'skills/{s.name}/references/{f.name}']=f.read_bytes()
    for f in (common/'assets').glob('*.json'):
        out['assets/'+f.name]=f.read_bytes()
        for s in skills:out[f'skills/{s.name}/assets/{f.name}']=f.read_bytes()
    for s in skills:out[f'skills/{s.name}/assets/providers.json']=encoded({**catalog,'capability':s.name})
    graph=root/'scripts/workgraph.py'
    if graph.is_file():out['skills/research-paper-workflow/scripts/workgraph.py']=graph.read_bytes()
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--check',action='store_true');g.add_argument('--write',action='store_true');a=p.parse_args()
    expected=generated();drift=[]
    for rel,content in expected.items():
        f=ROOT/rel
        if not f.is_file() or f.read_bytes()!=content:
            drift.append(rel)
            if a.write:f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(content)
    if a.write:(ROOT/'GENERATED-FILES.json').write_bytes(encoded({'version':(ROOT/'VERSION').read_text().strip(),'generated_files':{k:sha(v) for k,v in sorted(expected.items())}}))
    print(json.dumps({'status':'synchronized' if a.write else 'clean' if not drift else 'drift','generated_files':len(expected),'changed_or_drifted':len(drift),'paths':drift},ensure_ascii=False))
    return 0 if a.write or not drift else 1
if __name__=='__main__':raise SystemExit(main())
