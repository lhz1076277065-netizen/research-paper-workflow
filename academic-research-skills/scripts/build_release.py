#!/usr/bin/env python3
"""Layered build: original v3 resources plus the maintained 3.1 overrides."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('_academic_v300_builder',ROOT/'scripts/_v300_build_release.py')
legacy=importlib.util.module_from_spec(spec);sys.modules[spec.name]=legacy;spec.loader.exec_module(legacy)
def generated(root=ROOT):
    root=Path(root);out=legacy.generated(root)
    source=root/'src/quality31/payload'
    names=[p.name for p in (root/'skills').iterdir() if p.is_dir()]
    for f in source.rglob('*'):
        if not f.is_file() or '__pycache__' in f.parts or f.suffix in {'.pyc','.pyo'}:continue
        rel=f.relative_to(source).as_posix();body=f.read_bytes();out[rel]=body
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--check',action='store_true');g.add_argument('--write',action='store_true');a=p.parse_args()
    expected=generated();drift=[]
    for rel,body in expected.items():
        target=ROOT/rel
        if not target.is_file() or target.read_bytes()!=body:
            drift.append(rel)
            if a.write:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
    if a.write:(ROOT/'GENERATED-FILES.json').write_text(json.dumps({'version':(ROOT/'VERSION').read_text().strip(),'generated_files':{k:hashlib.sha256(v).hexdigest() for k,v in expected.items()}},indent=2)+'\n')
    print(json.dumps({'status':'synchronized' if a.write else 'drift' if drift else 'clean','generated_files':len(expected),'paths':drift}))
    return 0 if a.write or not drift else 1
if __name__=='__main__':raise SystemExit(main())
