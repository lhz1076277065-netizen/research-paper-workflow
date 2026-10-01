#!/usr/bin/env python3
"""Build source/runtime ZIPs and per-file manifests without carrying environment caches."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,zipfile
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'.git','.academic','.venv','__pycache__','.pytest_cache'}
FONTS={'.ttf','.otf','.woff','.woff2','.ttc'}
def chosen(kind):
    files=[]
    for f in sorted(ROOT.rglob('*')):
        rel=f.relative_to(ROOT)
        if f.is_symlink() or not f.is_file() or set(rel.parts)&EXCLUDED or f.suffix in FONTS or f.suffix=='.pyc' or f.name=='.DS_Store' or rel.as_posix()=='PACKAGE-MANIFEST.json':continue
        if kind=='runtime':
            reports={'evaluations/rc5/VALIDATION.zh-CN.md','evaluations/rc5/paired-study/COMPARISON.zh-CN.md','evaluations/rc5/paired-study/independent-review.md'}
            if rel.parts[0] in {'src','tests','evaluations','history','previous-release','release','source-diffs'} and rel.as_posix() not in reports:continue
            if rel.as_posix() in {'scripts/build_release.py','scripts/_v300_build_release.py','UPGRADE-RECEIPT.json','release/make_package.py','release/coverage-baseline.json','release/ci-matrix.example.yml'}:continue
            if rel.parts[0]=='test-results' and rel.name not in {'SUMMARY.json','SUMMARY.zh-CN.md','context-metrics.json','distribution-checks.json'}:continue
        files.append(f)
    return files

def pack(kind,out):
    name='academic-research-skills-v'+(ROOT/'VERSION').read_text().strip()
    target=Path(out)/(name+('-source' if kind=='source' else '')+'.zip');target.parent.mkdir(parents=True,exist_ok=True)
    try:
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True,stderr=subprocess.DEVNULL).strip()
        dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','.'],cwd=ROOT,text=True).strip()
        if dirty:raise ValueError('Commit the release source before packaging; its manifest must identify the actual commit')
        tracked=set(subprocess.check_output(['git','ls-files','-z','--','.'],cwd=ROOT).decode().split('\0'))
    except (subprocess.CalledProcessError,FileNotFoundError):
        commit=None;tracked=None
    files=[f for f in chosen(kind) if tracked is None or f.relative_to(ROOT).as_posix() in tracked]
    manifest={'version':(ROOT/'VERSION').read_text().strip(),'release_tag':'v'+(ROOT/'VERSION').read_text().strip(),'source_commit':commit,'kind':kind,'files':{f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files},'note':'File identities, not a digital signature or scientific quality certificate.'}
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for f in files:z.write(f,name+'/'+f.relative_to(ROOT).as_posix())
        z.writestr(name+'/PACKAGE-MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:raise RuntimeError('ZIP integrity check failed')
        for rel,expected in manifest['files'].items():
            if hashlib.sha256(z.read(name+'/'+rel)).hexdigest()!=expected:raise RuntimeError('ZIP file digest mismatch: '+rel)
    return {'kind':kind,'file':target.name,'release_tag':manifest['release_tag'],'source_commit':commit,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'files':len(files)+1,'zip_crc_verified':True,'file_sha256_verified':True}

def one_click(runtime,out):
    version=(ROOT/'VERSION').read_text().strip();name='academic-research-skills-v'+version+'-one-click'
    folder=Path(out)/name;folder.mkdir()
    for source in (ROOT/'release/installer').iterdir():
        if not source.is_file() or source.suffix=='.pyc':continue
        body=source.read_text().replace('@VERSION@',version).replace('@RUNTIME_SHA256@',runtime['sha256'])
        (folder/source.name).write_text(body)
        (folder/source.name).chmod(source.stat().st_mode & 0o777)
    shutil.copy2(ROOT/'INSTALLATION.zh-CN.md',folder/'README.zh-CN.md')
    shutil.copy2(Path(out)/runtime['file'],folder/runtime['file'])
    (folder/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in sorted(folder.iterdir()) if p.is_file() and p.name!='SHA256SUMS.txt'))
    target=Path(out)/(name+'.zip')
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(folder.iterdir()):
            if p.is_file():z.write(p,name+'/'+p.name)
    with zipfile.ZipFile(target) as z:
        if z.testzip() is not None:raise RuntimeError('Installer ZIP integrity check failed')
    return {'kind':'one-click','file':target.name,'release_tag':runtime['release_tag'],'source_commit':runtime['source_commit'],'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'zip_crc_verified':True}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);a=p.parse_args()
    result=[pack(k,a.out) for k in ['runtime','source']]
    result.append(one_click(result[0],a.out))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    (Path(a.out)/('academic-research-skills-v'+(ROOT/'VERSION').read_text().strip()+'-SHA256SUMS.txt')).write_text(''.join(x['sha256']+'  '+x['file']+'\n' for x in result))
