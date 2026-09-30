#!/usr/bin/env python3
"""Build source/runtime ZIPs and per-file manifests without carrying environment caches."""
from pathlib import Path
import argparse,hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','.academic','.venv','__pycache__','.pytest_cache'}
FONTS={'.ttf','.otf','.woff','.woff2','.ttc'}
def chosen(kind):
    files=[]
    for f in sorted(ROOT.rglob('*')):
        rel=f.relative_to(ROOT)
        if f.is_symlink() or not f.is_file() or set(rel.parts)&EXCLUDED or f.suffix in FONTS or f.suffix=='.pyc' or f.name in {'.DS_Store','PACKAGE-MANIFEST.json'}:continue
        if kind=='runtime':
            if rel.parts[0] in {'src','tests','evaluations','history','previous-release','release'}:continue
            if rel.as_posix() in {'scripts/build_release.py','scripts/_v300_build_release.py','UPGRADE-RECEIPT.json','release/make_package.py','release/coverage-baseline.json','release/ci-matrix.example.yml'}:continue
            if rel.parts[0]=='test-results' and rel.name not in {'SUMMARY.json','SUMMARY.zh-CN.md','context-metrics.json','distribution-checks.json'}:continue
        files.append(f)
    return files

def pack(kind,out):
    name='academic-research-skills-v'+(ROOT/'VERSION').read_text().strip()
    target=Path(out)/(name+('-source' if kind=='source' else '')+'.zip');target.parent.mkdir(parents=True,exist_ok=True)
    files=chosen(kind);manifest={'version':(ROOT/'VERSION').read_text().strip(),'kind':kind,'files':{f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files},'note':'File identities, not a digital signature or scientific quality certificate.'}
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in files:z.write(f,name+'/'+f.relative_to(ROOT).as_posix())
        z.writestr(name+'/PACKAGE-MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:raise RuntimeError('ZIP integrity check failed')
        for rel,expected in manifest['files'].items():
            if hashlib.sha256(z.read(name+'/'+rel)).hexdigest()!=expected:raise RuntimeError('ZIP file digest mismatch: '+rel)
    return {'kind':kind,'file':target.name,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'files':len(files)+1,'zip_crc_verified':True,'file_sha256_verified':True}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);a=p.parse_args()
    result=[pack(k,a.out) for k in ['runtime','source']]
    print(json.dumps(result,ensure_ascii=False,indent=2))
    (Path(a.out)/'Academic_Research_Skills_v3_SHA256SUMS.txt').write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in result))
