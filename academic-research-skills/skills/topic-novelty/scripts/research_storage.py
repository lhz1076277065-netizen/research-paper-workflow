#!/usr/bin/env python3
"""Project-scoped acquisition quota. Does not intercept other tools or sandbox I/O."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
import shutil
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import zipfile

LIMIT = 200_000_000_000  # decimal GB; both cumulative transfer and project footprint
RESERVE = 10_000_000_000
NAME = '.research-storage.json'
CHUNK = 256 * 1024

class StorageError(ValueError): pass

def integer(value, name, positive=False):
    if type(value) is not int or value < (1 if positive else 0):
        raise StorageError(name+' must be an integer '+('> 0' if positive else '>= 0'))
    return value

def read(root):
    root=Path(root).resolve(); path=root/NAME
    if not path.is_file() or path.is_symlink(): raise StorageError('Plan storage at the project root before acquiring data')
    state=json.loads(path.read_text())
    if state.get('schema')!='research-storage-1' or state.get('root')!=str(root):
        raise StorageError('Storage receipt belongs to another project; do not reset counters')
    integer(state['limit_bytes'],'limit',True)
    if state['limit_bytes']>LIMIT: raise StorageError('The research ceiling is 200 GB')
    integer(state['downloaded_bytes'],'downloaded');integer(state['reserve_bytes'],'reserve')
    return state

def save(root, state):
    path=Path(root)/NAME; temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    temporary.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    os.replace(temporary,path)

@contextmanager
def locked(root):
    root=Path(root).resolve();root.mkdir(parents=True,exist_ok=True)
    lock=root/(NAME+'.lock')
    if lock.is_symlink(): raise StorageError('Unsafe quota lock')
    with lock.open('a') as handle:
        try: fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: raise StorageError('Another managed acquisition is active; reuse it or wait') from None
        yield root

def footprint(root):
    """Conservative logical bytes; hard links count again, external caches are not inferred."""
    total=0
    for base,dirs,files in os.walk(root,followlinks=False):
        for name in dirs+files:
            path=Path(base)/name
            if path.is_symlink(): raise StorageError('External/symlink storage must be accounted for explicitly; use a project-local acquisition root')
        for name in files:
            if name in {NAME,NAME+'.lock'} or re.fullmatch(re.escape(NAME)+r'\.[a-f0-9]{32}\.tmp',name): continue
            total+=(Path(base)/name).stat().st_size
    return total

def check(root, state=None, extra=0, transfer=0, used=None, planned=True):
    state=read(root) if state is None else state
    integer(extra,'extra');integer(transfer,'transfer')
    used=footprint(root) if used is None else used
    free=shutil.disk_usage(root).free
    reasons=[]
    if used+extra>state['limit_bytes']: reasons.append('project_footprint_limit')
    if state['downloaded_bytes']+transfer>state['limit_bytes']: reasons.append('cumulative_download_limit')
    if free-extra<state['reserve_bytes']: reasons.append('disk_headroom')
    if planned and state.get('plan'):
        if used+extra>state['plan']['expected_peak_project_bytes']:reasons.append('peak_estimate_needs_update')
        if state['downloaded_bytes']-state.get('plan_transfer_baseline',0)+transfer>state['plan']['expected_download_bytes']:
            reasons.append('transfer_estimate_needs_update')
    return {'allowed':not reasons,'reasons':reasons,'limit_bytes':state['limit_bytes'],
            'downloaded_bytes':state['downloaded_bytes'],'project_bytes':used,'free_bytes':free,
            'reserve_bytes':state['reserve_bytes'],'transfer_remaining_bytes':max(0,state['limit_bytes']-state['downloaded_bytes']),
            'preplan_download_bytes':state.get('preplan_download_bytes'),
            'accounting_scope':'managed and explicitly recorded transfers since the first plan; unknown history is not zero'}

def require(result):
    if not result['allowed']: raise StorageError('Replan acquisition: '+','.join(result['reasons']))

def plan(root, specification, limit=LIMIT, reserve=RESERVE):
    integer(limit,'limit',True);integer(reserve,'reserve')
    if limit>LIMIT: raise StorageError('The research ceiling is 200 GB')
    needs=specification.get('needs')
    if not isinstance(needs,list) or not needs: raise StorageError('Plan needs with scientific purpose, subset and access route')
    for item in needs:
        if not isinstance(item,dict) or any(not isinstance(item.get(k),str) or not item[k].strip() for k in ('purpose','subset','access')):
            raise StorageError('Each need requires purpose, subset and access')
    for k in ('expected_download_bytes','expected_peak_project_bytes'):
        integer(specification.get(k),k)
    with locked(root) as root:
        used=footprint(root)
        if specification['expected_peak_project_bytes']<used: raise StorageError('Peak estimate omits existing project files')
        if (root/NAME).exists():
            state=read(root)
            if limit!=state['limit_bytes'] or reserve!=state['reserve_bytes']:
                raise StorageError('Replanning preserves the original ceiling and disk reserve')
        else:
            state={'schema':'research-storage-1','id':uuid.uuid4().hex,'root':str(root),
                   'limit_bytes':limit,'reserve_bytes':reserve,'downloaded_bytes':0,
                   'preplan_download_bytes':None if used else 0,'operations':[]}
        require(check(root,state,extra=max(0,specification['expected_peak_project_bytes']-used),
                      transfer=specification['expected_download_bytes'],used=used,planned=False))
        state['plan']=specification;state['plan_transfer_baseline']=state['downloaded_bytes'];state['planned_at']=time.time();save(root,state)
        return check(root,state,used=used)

def target(root, relative):
    rel=PurePosixPath(relative)
    if not relative or rel.is_absolute() or any(x in {'..',''} for x in rel.parts) or '\\' in relative:
        raise StorageError('Output must be a new project-relative path')
    candidate=Path(root)/relative
    if not candidate.resolve().is_relative_to(Path(root).resolve()): raise StorageError('Output escapes project')
    if any(p.is_symlink() for p in [candidate,*candidate.parents]): raise StorageError('Output path contains a symlink')
    if candidate.exists(): raise StorageError('Existing output preserved; verify/reuse it or choose another name')
    if candidate.name.startswith(NAME):raise StorageError('Quota metadata is reserved')
    return candidate

def phase_guard(phase, root=None):
    if phase:
        import phase_control as P
        state=P.load(phase)
        if root is not None:
            receipt=read(root)
            if state.get('storage')!={'root':str(Path(root).resolve()),'id':receipt['id']}:
                raise StorageError('Bind the original project storage receipt to this phase before acquisition')
        result=P.guard(state)
        if not result['allowed']: raise StorageError('Phase requires action: '+','.join(result['reasons']))
        return result['seconds_to_work_cutoff']
    return 30

def record_transfer(root, byte_count, evidence, need):
    """Record a bounded external tool's actual receipt. Never conceal already-incurred excess."""
    integer(byte_count,'byte_count')
    with locked(root) as root:
        state=read(root);path=(root/evidence).resolve()
        if not path.is_relative_to(root) or not path.is_file() or not path.stat().st_size:
            raise StorageError('External transfer requires nonempty project-local, nonsecret evidence')
        if type(need) is not int or need<0 or need>=len(state['plan']['needs']):raise StorageError('External transfer must reference its planned need')
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if any(x.get('evidence_sha256')==digest for x in state['operations']):raise StorageError('Transfer receipt already recorded; do not duplicate counters')
        state['downloaded_bytes']+=byte_count
        state['operations'].append({'kind':'external_reported_transfer','bytes':byte_count,'need':need,
                                    'evidence':str(path.relative_to(root)),'evidence_sha256':digest,
                                    'actual_bytes_independently_verified':False})
        save(root,state);return check(root,state)

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed=urllib.parse.urlsplit(newurl)
        if parsed.scheme!='https' and not (parsed.scheme=='http' and parsed.hostname in {'localhost','127.0.0.1','::1'}):
            raise StorageError('Unsafe download redirect')
        if parsed.username or parsed.password: raise StorageError('Credentials in redirect URL')
        out=super().redirect_request(req,fp,code,msg,headers,newurl)
        old=urllib.parse.urlsplit(req.full_url)
        if (old.scheme,old.hostname,old.port)!=(parsed.scheme,parsed.hostname,parsed.port):
            out.remove_header('Authorization');out.remove_header('Cookie')
        return out

def download(root, url, output, max_bytes, need, token_env=None, phase=None):
    integer(max_bytes,'max_bytes',True)
    parsed=urllib.parse.urlsplit(url)
    if parsed.scheme!='https' and not (parsed.scheme=='http' and parsed.hostname in {'localhost','127.0.0.1','::1'}):
        raise StorageError('Use HTTPS for remote research data')
    if parsed.username or parsed.password: raise StorageError('Use a scoped credential environment variable, not URL credentials')
    # URL queries can contain signed tokens: no query/fragment or headers in receipts/errors.
    source=urllib.parse.urlunsplit((parsed.scheme,parsed.netloc,parsed.path,'',''))
    headers={'User-Agent':'academic-research-skills','Accept-Encoding':'identity'}
    if token_env:
        secret=os.environ.get(token_env)
        if not secret: raise StorageError('Scoped credential unavailable; recover another authorized access route')
        headers['Authorization']='Bearer '+secret
    with locked(root) as root:
        state=read(root);destination=target(root,output)
        if type(need) is not int or need<0 or need>=len(state['plan']['needs']): raise StorageError('Download must reference a planned scientific need')
        used=footprint(root);require(check(root,state,extra=max_bytes,transfer=max_bytes,used=used))
        timeout=max(.01,min(30,phase_guard(phase,root)))
        destination.parent.mkdir(parents=True,exist_ok=True)
        partial=destination.with_name(destination.name+'.'+uuid.uuid4().hex+'.partial')
        op={'kind':'download','source':source,'need':need,'output':output,'bytes':0,'status':'running'}
        state['operations'].append(op);save(root,state);digest=hashlib.sha256();last_scan=time.monotonic()
        try:
            opener=urllib.request.build_opener(SafeRedirect())
            with opener.open(urllib.request.Request(url,headers=headers),timeout=timeout) as response:
                length=response.headers.get('Content-Length')
                declared=int(length) if length is not None else None
                if declared is not None and (declared<0 or declared>max_bytes): raise StorageError('Remote payload exceeds planned per-file bound; request a subset or replan')
                content_type=response.headers.get('Content-Type','').lower()
                if 'text/html' in content_type: raise StorageError('Login/terms page returned instead of data; resolve access or use an equivalent source')
                with partial.open('xb',buffering=0) as handle:
                    while True:
                        phase_guard(phase,root)
                        if time.monotonic()-last_scan>2:used=footprint(root);last_scan=time.monotonic()
                        require(check(root,state,used=used))
                        remaining=min(max_bytes-op['bytes'],state['limit_bytes']-state['downloaded_bytes'],
                                      state['limit_bytes']-used,shutil.disk_usage(root).free-state['reserve_bytes'])
                        if declared is not None and op['bytes']==declared: break
                        if remaining<=0: raise StorageError('Streaming bound reached; partial retained, replan without resetting counters')
                        chunk=response.read(min(CHUNK,remaining))
                        if not chunk: break
                        op['bytes']+=len(chunk);state['downloaded_bytes']+=len(chunk);save(root,state)
                        # Recheck actual disk headroom before this write; count received bytes even if writing fails.
                        require(check(root,state,extra=len(chunk),used=used))
                        handle.write(chunk);digest.update(chunk);used+=len(chunk)
                if declared is not None and declared!=op['bytes']: raise StorageError('Truncated payload retained for diagnosis; transfer already counted')
            os.replace(partial,destination)
            op.update(status='completed',sha256=digest.hexdigest());save(root,state)
            return {**op,'storage':check(root,state)}
        except BaseException as error:
            reason=('http_'+str(error.code)) if isinstance(error,urllib.error.HTTPError) else str(error) if isinstance(error,StorageError) else type(error).__name__
            if isinstance(error,urllib.error.HTTPError):error.close()
            op.update(status='interrupted',reason=reason,partial=str(partial.relative_to(root)) if partial.exists() else None)
            save(root,state)
            if isinstance(error,(KeyboardInterrupt,SystemExit)):raise
            raise StorageError('Acquisition interrupted: '+reason+'; retain receipt and recover within the same quota') from None

def extract(root, archive, members, output, phase=None):
    """Stream only explicitly selected regular ZIP/TAR members, with archive + output coexistence charged."""
    if not members or len(set(members))!=len(members): raise StorageError('Select the required archive members explicitly')
    with locked(root) as root:
        state=read(root);path=(root/archive).resolve()
        if not path.is_relative_to(root) or not path.is_file(): raise StorageError('Archive must be inside the project quota')
        destination=target(root,output);used=footprint(root)
        container=zipfile.ZipFile(path) if zipfile.is_zipfile(path) else tarfile.open(path,'r:*')
        with container:
            chosen=[]
            for name in members:
                rel=PurePosixPath(name)
                if rel.is_absolute() or '..' in rel.parts or '\\' in name or name.startswith(NAME): raise StorageError('Unsafe archive member')
                if isinstance(container,zipfile.ZipFile):
                    rows=[x for x in container.infolist() if x.filename==name]
                    if len(rows)!=1 or rows[0].is_dir() or ((rows[0].external_attr>>16)&0o170000)==0o120000:
                        raise StorageError('Member missing, duplicated or not a regular file')
                    info=rows[0];size=info.file_size
                else:
                    rows=[x for x in container.getmembers() if x.name==name]
                    if len(rows)!=1 or not rows[0].isfile(): raise StorageError('Member missing, duplicated or not a regular file')
                    info=rows[0];size=info.size
                integer(size,'member_size');chosen.append((name,info,size))
            require(check(root,state,extra=sum(x[2] for x in chosen),used=used));phase_guard(phase,root)
            destination.mkdir(parents=True)
            op={'kind':'extract','archive':archive,'output':output,'members':members,'bytes':0,'status':'running'}
            state['operations'].append(op);save(root,state)
            try:
                for name,info,size in chosen:
                    out=target(destination,name);out.parent.mkdir(parents=True,exist_ok=True)
                    reader=container.open(info) if isinstance(container,zipfile.ZipFile) else container.extractfile(info)
                    count=0
                    with reader, out.open('xb',buffering=0) as handle:
                        while count<size:
                            phase_guard(phase,root)
                            want=min(CHUNK,size-count);require(check(root,state,extra=want,used=used))
                            chunk=reader.read(want)
                            if not chunk: raise StorageError('Truncated archive member')
                            handle.write(chunk);count+=len(chunk);used+=len(chunk);op['bytes']+=len(chunk)
                            save(root,state)
                op['status']='completed';save(root,state)
                return {**op,'storage':check(root,state)}
            except BaseException as error:
                op.update(status='interrupted',reason=type(error).__name__);save(root,state)
                raise

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',required=True)
    sub=parser.add_subparsers(dest='op',required=True)
    p=sub.add_parser('plan');p.add_argument('--spec',required=True);p.add_argument('--limit-bytes',type=int,default=LIMIT);p.add_argument('--reserve-bytes',type=int,default=RESERVE)
    p=sub.add_parser('check');p.add_argument('--extra-bytes',type=int,default=0);p.add_argument('--transfer-bytes',type=int,default=0)
    p=sub.add_parser('record');p.add_argument('--bytes',type=int,required=True);p.add_argument('--evidence',required=True);p.add_argument('--need',type=int,required=True)
    p=sub.add_parser('download');p.add_argument('--url',required=True);p.add_argument('--output',required=True);p.add_argument('--max-bytes',type=int,required=True);p.add_argument('--need',type=int,required=True);p.add_argument('--token-env');p.add_argument('--phase')
    p=sub.add_parser('extract');p.add_argument('--archive',required=True);p.add_argument('--member',action='append',required=True);p.add_argument('--output',required=True);p.add_argument('--phase')
    args=parser.parse_args(argv)
    try:
        if args.op=='plan': result=plan(args.root,json.loads(Path(args.spec).read_text()),args.limit_bytes,args.reserve_bytes)
        elif args.op=='check': result=check(args.root,extra=args.extra_bytes,transfer=args.transfer_bytes)
        elif args.op=='record': result=record_transfer(args.root,args.bytes,args.evidence,args.need)
        elif args.op=='download': result=download(args.root,args.url,args.output,args.max_bytes,args.need,args.token_env,args.phase)
        else:result=extract(args.root,args.archive,args.member,args.output,args.phase)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result.get('allowed',True) else 2
    except (ValueError,OSError,KeyError,tarfile.TarError,zipfile.BadZipFile) as error:
        message=str(error) if isinstance(error,StorageError) else type(error).__name__
        print(json.dumps({'status':'replan_acquisition','error':message},ensure_ascii=False));return 2

if __name__=='__main__':raise SystemExit(main())
