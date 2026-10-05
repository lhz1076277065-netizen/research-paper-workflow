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
    # Pinned seed entries are prepared explicitly; source preparation is not execution.
    index_path=common/'assets/capability-index.json'
    index=json.loads(index_path.read_text()) if index_path.exists() else {}
    seeds=index.get('capabilities',[])+index.get('additional_entries',[])
    routes=index.get('professional_routes',{})
    roles={'literature':'literature-discovery','reading':'paper-deep-reading','data':'data-preparation','analysis':'analysis-execution','methods':'research-design','figure':'scientific-visualization','figure_reference':'scientific-visualization','review':'manuscript-review','writing':'manuscript-writing','final_expression':'manuscript-writing','experiment':'analysis-execution','ideation':'topic-novelty','novelty':'topic-novelty','presentation':'presentation','workbench':'workbench'}
    providers=[]
    for c in seeds:
        files={f['path']:f['blob'] for f in c['required_files']}
        providers.append({'id':c['id'],'repository':c['repository'],'repo':c['repository'],
            'entrypoint':c['entry'],'required_paths':list(files),'entry_git_blob_sha':files[c['entry']],
            'discovered_file_blob_sha':files,'kind':c['kind'],'roles':c['roles'],
            'capabilities':list(dict.fromkeys([roles[r] for r in c['roles'] if r in roles]+[k for k,v in routes.items() if c['id'] in [v['primary']]+v.get('alternatives',[])])),
            'purpose':c['host_adaptation'],'source_review_status':'pinned_entry_and_support_verified','source_url':'https://github.com/'+c['repository']+'/blob/'+c['commit']+'/'+c['entry'],'license':'See upstream license file/metadata; no blanket permission claim','notes':c['host_adaptation'],'adaptations':[c['host_adaptation']],'phase':1,'mode':'adapted-protocol' if c['kind'] in {'skill_protocol','workbench_protocol'} else 'reference-only',
            'default_candidate':any(c['id']==v['primary'] for v in routes.values()),'requires_host':['local-files'],'requires_facts':[],
            'resolve_pinned_cache':True,
            'dependencies':c['dependencies'],'commit':c['commit'],'tree':c['tree']})
    catalog={'schema_version':'runtime-providers-1','package_version':version,
             'capabilities':capabilities,'providers':providers,'professional_routes':routes,
             'professional_source_policy':index.get('professional_source_policy'),
             'discovery':'Source-first professional steps are mandatory; missing matching source blocks the step. Preparation alone is not execution.'}
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
    for s in skills:out[f'skills/{s.name}/assets/providers.json']=encoded({**catalog,'capability':s.name,'providers':[p for p in providers if s.name=='research-paper-workflow' or s.name in p['capabilities']]})
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
