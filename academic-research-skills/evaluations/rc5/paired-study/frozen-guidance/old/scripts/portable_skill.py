#!/usr/bin/env python3
"""Copy one portable skill to an explicit location, or export its text protocol.

No guessed host paths, no modification of global agent settings, no network.
An installed folder is not evidence that a host has discovered or executed it.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import os
import math
import subprocess

class PortableError(ValueError):pass

def inventory(source):
    source=Path(source).expanduser().resolve()
    entry=source/'SKILL.md'
    if not entry.is_file():raise PortableError('source must be one skill directory containing SKILL.md')
    text=entry.read_text(encoding='utf-8')
    if not text.startswith('---\n'):raise PortableError('SKILL.md requires YAML frontmatter')
    parts=text.split('\n---',2)
    if len(parts)<2:raise PortableError('SKILL.md frontmatter is not closed')
    front=parts[0][4:]
    match=re.search(r'^name:[ \t]*(.+?)[ \t]*$',front,re.M)
    value=match.group(1).strip() if match else ''
    if value[:1] in {'"', "'"}:
        if len(value)<2 or value[-1]!=value[0]:raise PortableError('Invalid quoted Skill name')
        value=value[1:-1]
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',value) or value!=source.name:
        raise PortableError('Skill name must match the directory')
    if len(value)>64:raise PortableError('Skill name is too long')
    description=re.search(r'^description:[ \t]*(.*)$',front,re.M)
    if description is None or not description.group(1).strip() or description.group(1).strip() in {'""', "''"}:
        raise PortableError('SKILL.md requires a nonempty description')
    files={}
    for p in sorted(source.rglob('*')):
        rel=p.relative_to(source)
        if any(x in {'.git','.academic','.venv','__pycache__'} for x in rel.parts) or p.suffix=='.pyc' or p.name=='.DS_Store':continue
        if p.is_symlink():raise PortableError('Symlink in portable skill; resolve packaging explicitly: '+str(rel))
        if p.is_file():files[rel.as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    return source,value,files

def install(source,destination,apply=False):
    src,name,files=inventory(source);dest=Path(destination).expanduser().absolute()/name
    resolved=dest.resolve()
    if resolved==src or resolved.is_relative_to(src) or src.is_relative_to(resolved):raise PortableError('Destination overlaps source')
    if dest.is_symlink():raise PortableError('Destination must not be a symlink')
    if dest.exists():
        _,_,other=inventory(dest)
        if other==files:return {'status':'files_already_present','name':name,'destination':str(dest),'native_host_verified':False,'files':len(files)}
        raise PortableError('Destination contains a different version; choose a new directory or explicitly migrate it')
    report={'status':'copy_planned','name':name,'destination':str(dest),'files':len(files),'native_host_verified':False}
    if apply:
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.mkdir()  # fail rather than overwrite a concurrent installation
        try:
            for rel,expected in files.items():
                data=(src/rel).read_bytes()
                if hashlib.sha256(data).hexdigest()!=expected:raise PortableError('Source changed during copy')
                p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
                shutil.copymode(src/rel,p)
        except Exception:
            # Only this function's newly created directory, never preexisting content.
            shutil.rmtree(dest);raise
        report['status']='files_installed'
    return report

def export_prompt(source,output,study_types=(),detail=False):
    src,name,files=inventory(source)
    required=['SKILL.md']
    if detail:required+=['references/protocol.md']
    bodies=['# Academic skill core: '+name,
       '使用当前任务的真实材料和实际工具执行；仅按需要展开被引用的专业参考。']
    included=[]
    for rel in required:
        p=src/rel
        if not p.is_file():raise PortableError('Missing export resource: '+rel)
        bodies+=['\n---\n## Resource: '+rel,p.read_text(encoding='utf-8')];included.append(rel)
    book=json.loads((src/'assets/research-profiles.json').read_text(encoding='utf-8')) if study_types else {'profiles':{}}
    for t in study_types:
        if t not in book['profiles']:raise PortableError('Unknown study type: '+t)
        bodies+=['\n## Selected study-type guidance: '+t,json.dumps(book['profiles'][t],ensure_ascii=False,indent=2)]
    out=Path(output).expanduser().absolute()
    if out.exists():raise PortableError('Refusing to overwrite an existing prompt export')
    if out.resolve().is_relative_to(src):raise PortableError('Keep prompt exports outside the installed skill')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text('\n\n'.join(bodies)+'\n',encoding='utf-8')
    return {'status':'prompt_exported','path':str(out),'name':name,'included_resources':included,
            'source_sha256':{x:files[x] for x in included},'execution_performed':False,'host_tools_created':False}

def fetch_provider(provider_id,commit,destination,*,apply=False,allow_network=False,mirror=None,registry=None,timeout=120):
    """Acquire one source snapshot; reuse a clean checkout without resetting local work.

    This is source acquisition, not installation, source review, or skill execution.
    A user-edited snapshot is returned intact so the host can use another directory.
    """
    if not math.isfinite(timeout) or timeout<=0:raise PortableError('timeout must be positive and finite')
    if not re.fullmatch(r'[0-9a-fA-F]{40}',commit):raise PortableError('A full 40-character commit SHA is required; no moving branch')
    commit=commit.lower()
    if registry is None:
        home=Path(__file__).resolve().parents[1];path=home/'assets/providers.json'
        registry=json.loads((path if path.exists() else home/'docs/provider-catalog.json').read_text(encoding='utf-8'))
    candidate=next((x for x in registry['providers'] if x['id']==provider_id),None)
    if candidate is None:raise PortableError('Provider is not in this module registry')
    repo=candidate['repo']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise PortableError('Invalid public repository identifier')
    source=str(Path(mirror).expanduser().resolve()) if mirror else 'https://github.com/'+repo+'.git'
    if mirror and not Path(source).is_dir():raise PortableError('Offline mirror must be a local repository directory')
    destination=Path(destination).expanduser().absolute()
    if destination.is_symlink():raise PortableError('Destination must not be a symlink')
    report={'status':'source_fetch_planned','provider_id':provider_id,'repository':repo,'commit':commit,
            'destination':str(destination),'source_reviewed':False,'runtime_installed':False,'native_host_verified':False,
            'source_mode':'explicit_local_mirror' if mirror else 'public_github','steps':[],'timeout_seconds':timeout}
    if not apply:return report
    if shutil.which('git') is None:return {**report,'status':'git_required'}
    marker=destination/'.academic-source.json';identity={'repository':repo,'commit':commit,'source':source}
    env={**os.environ,'GIT_CONFIG_GLOBAL':os.devnull,'GIT_CONFIG_NOSYSTEM':'1','GIT_TERMINAL_PROMPT':'0'}
    def call(command):
        try:
            proc=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout,env=env)
            return {'command':command,'returncode':proc.returncode,'stdout':proc.stdout[-6000:],'stderr':proc.stderr[-6000:]}
        except (OSError,subprocess.TimeoutExpired) as exc:
            return {'command':command,'returncode':None,'error':str(exc)}
    def missing_paths():
        missing=[]
        for rel in candidate['required_paths']:
            target=(destination/rel).resolve()
            if not target.is_relative_to(destination.resolve()) or not target.exists():missing.append(rel)
        return missing
    def config():return {'providers':{provider_id:{'root':str(destination),'layout':'repository'}}}
    if destination.exists():
        if not marker.is_file() or json.loads(marker.read_text()).get('identity')!=identity:
            raise PortableError('Refusing to overwrite an unrelated source directory')
        if (destination/'.git').exists():
            head=call(['git','-C',str(destination),'rev-parse','HEAD'])
            state=call(['git','-C',str(destination),'status','--porcelain','--untracked-files=all'])
            report['steps']=[head,state]
            # Do not reset changed tracked files or discard added working files on resume.
            own={'.academic-source.json','.academic-fetch-report.json'}
            dirty=[line for line in state.get('stdout','').splitlines() if line[3:] not in own]
            if state['returncode']!=0 or dirty or (head['returncode']==0 and head['stdout'].strip()!=commit):
                return {**report,'status':'source_local_changes','local_changes':dirty,
                        'next_action':'Keep this checkout; use a new destination for a clean snapshot.'}
            if head['returncode']==0:
                missing=missing_paths()
                return {**report,'status':'source_missing_required_paths' if missing else 'source_reused_needs_review',
                        'missing_paths':missing,'configuration_fragment':config(),'network_used':False}
    if not mirror and not allow_network:return {**report,'status':'blocked_network_authorization'}
    destination.mkdir(parents=True,exist_ok=True)
    marker.write_text(json.dumps({'identity':identity,'status':'fetching'},indent=2)+'\n')
    commands=[['git','init','--template=',str(destination)],
              ['git','-C',str(destination),'-c','core.hooksPath='+str(destination/'.disabled-hooks'),'fetch','--depth','1',source,commit],
              ['git','-C',str(destination),'-c','core.hooksPath='+str(destination/'.disabled-hooks'),'checkout','--detach','FETCH_HEAD'],
              ['git','-C',str(destination),'rev-parse','HEAD']]
    records=[]
    for command in commands:
        row=call(command);records.append(row)
        if row['returncode']!=0:break
    valid=len(records)==4 and records[-1]['returncode']==0 and records[-1]['stdout'].strip()==commit
    status='source_checked_out_needs_review' if valid else 'source_fetch_failed'
    missing=missing_paths() if valid else []
    if missing:status='source_missing_required_paths'
    result={**report,'status':status,'steps':records,'missing_paths':missing,
            'configuration_fragment':config() if valid else None,'network_used':not bool(mirror)}
    marker.write_text(json.dumps({'identity':identity,'status':status},indent=2)+'\n')
    (destination/'.academic-fetch-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('install');a.add_argument('--source',required=True);a.add_argument('--destination',required=True);a.add_argument('--apply',action='store_true')
    a=sub.add_parser('export');a.add_argument('--source',required=True);a.add_argument('--out',required=True);a.add_argument('--study-type',action='append',default=[]);a.add_argument('--detail',action='store_true')
    a=sub.add_parser('fetch-provider');a.add_argument('--provider',required=True);a.add_argument('--commit',required=True);a.add_argument('--destination',required=True);a.add_argument('--apply',action='store_true');a.add_argument('--allow-network',action='store_true');a.add_argument('--mirror')
    args=p.parse_args()
    try:
        if args.action=='install':result=install(args.source,args.destination,args.apply)
        elif args.action=='export':result=export_prompt(args.source,args.out,args.study_type,args.detail)
        else:result=fetch_provider(args.provider,args.commit,args.destination,apply=args.apply,allow_network=args.allow_network,mirror=args.mirror)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 3 if result['status'] in {'blocked_network_authorization','git_required','source_fetch_failed','source_missing_required_paths'} else 0
    except (OSError,ValueError,TypeError,KeyError) as e:
        print(json.dumps({'status':'error','error':str(e)},ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
