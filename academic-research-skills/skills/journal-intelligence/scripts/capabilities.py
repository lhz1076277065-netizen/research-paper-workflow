#!/usr/bin/env python3
"""Pinned professional entrypoints, verified local preparation and artifact uses.

Preparation downloads source files, not dependencies or agents. A receipt never
certifies that an agent followed a protocol or that a scientific claim is true.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile
from urllib.parse import quote
from urllib.request import Request, urlopen

class CapabilityError(ValueError): pass
def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def index_path(): return Path(__file__).resolve().parents[1]/'assets/capability-index.json'
def blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def path_under(root, rel):
    if not isinstance(rel,str) or not rel or '\\' in rel or ':' in rel: raise CapabilityError('Invalid source path')
    p=PurePosixPath(rel)
    if p.is_absolute() or '..' in p.parts or str(p)!=rel: raise CapabilityError('Noncanonical source path')
    dest=(Path(root)/rel).resolve()
    if not dest.is_relative_to(Path(root).resolve()): raise CapabilityError('Source path escapes root')
    return dest
def entry(index, uid):
    matches=[x for x in index['capabilities'] if x['id']==uid]
    if len(matches)!=1: raise CapabilityError('Unknown or duplicate capability: '+uid)
    return matches[0]
def listing(index, role=None):
    return {'schema_version':index['schema_version'], 'capabilities':[x for x in index['capabilities'] if role is None or role in x['roles']],
        'execution_started':False, 'scientific_quality_certified':False}
def prepare(capability, root, allow_network=False):
    # Separate subfolders prevent one repo's shared dependencies overwriting another.
    base=Path(root)/capability['id']/capability['commit'];refs=[]
    import re
    if not re.fullmatch(r'[A-Za-z0-9_-]+',capability['id']) or not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+',capability['repository']) or not re.fullmatch(r'[a-f0-9]{40}',capability['commit']):
        raise CapabilityError('Invalid repository or pinned commit')
    for f in capability['required_files']:
        target=path_under(base,f['path'])
        if target.exists():
            if not target.is_file() or blob(target.read_bytes())!=f['blob']:raise CapabilityError('Cache changed; preserve it and choose a fresh cache root: '+f['path'])
        else:
            if not allow_network: raise CapabilityError('Source not cached; enable network explicitly: '+f['path'])
            url='https://raw.githubusercontent.com/'+capability['repository']+'/'+capability['commit']+'/'+quote(f['path'],safe='/')
            req=Request(url,headers={'User-Agent':'academic-research-skills/3.4'})
            with urlopen(req,timeout=30) as response: data=response.read(4*1024*1024+1)
            if len(data)>4*1024*1024:raise CapabilityError('Source file exceeds 4 MiB; inspect separately')
            if blob(data)!=f['blob']:raise CapabilityError('Upstream blob mismatch: '+f['path'])
            target.parent.mkdir(parents=True,exist_ok=True)
            fd,tmp=tempfile.mkstemp(dir=target.parent,prefix='.prepare-')
            try:
                with os.fdopen(fd,'wb') as output:output.write(data)
                # Do not overwrite another preparer's cache.
                try:os.link(tmp,target)
                except FileExistsError:
                    if blob(target.read_bytes())!=f['blob']:raise CapabilityError('Concurrent cache mismatch')
            finally:os.unlink(tmp)
        refs.append({'path':f['path'],'blob':f['blob'],'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    return {'status':'source_prepared','id':capability['id'],'repository':capability['repository'],
        'commit':capability['commit'],'tree':capability['tree'],'entry':str(path_under(base,capability['entry'])),
        'root':str(base.resolve()),'files':refs,'kind':capability['kind'],
        'dependency_installation_performed':False,'research_work_done':False,
        'host_adaptation':capability['host_adaptation'],'known_requirements':capability['dependencies']}
def usage(capability, receipt, inputs, outputs, steps, mode, functions_run=False):
    if mode not in {'adapted_in_host','native_in_host','reference_only','function_only'}:raise CapabilityError('Unknown mode')
    if receipt.get('status')!='source_prepared' or receipt.get('commit')!=capability['commit'] or receipt.get('id')!=capability['id']:
        raise CapabilityError('Preparation identity mismatch')
    if not inputs or not outputs or not steps:raise CapabilityError('Actual input, output and steps required')
    if receipt.get('repository')!=capability['repository'] or receipt.get('tree')!=capability['tree']:
        raise CapabilityError('Preparation source identity mismatch')
    expected={f['path']:f['blob'] for f in capability['required_files']}
    if len(receipt.get('files',[]))!=len(expected) or {f['path']:f['blob'] for f in receipt.get('files',[])}!=expected:
        raise CapabilityError('Preparation support file identities incomplete or changed')
    base=Path(receipt['root'])
    for ref in capability['required_files']:
        p=path_under(base,ref['path'])
        if not p.is_file() or blob(p.read_bytes())!=ref['blob']:raise CapabilityError('Prepared source changed')
    def refs(paths):
        out=[]
        for name in paths:
            p=Path(name).resolve()
            if not p.is_file() or not p.stat().st_size:raise CapabilityError('Missing/empty task artifact: '+name)
            out.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        return out
    return {'id':capability['id'],'repository':capability['repository'],'entry':capability['entry'],
        'commit':capability['commit'],'actor_scope':'current_host','mode':mode,'roles':capability['roles'],
        'inputs':refs(inputs),'outputs':refs(outputs),'steps':steps,
        'progress':{'guidance_read':True,'research_work_done':mode in {'native_in_host','adapted_in_host'},'functions_run':functions_run},
        'status':'executed','semantic_execution_verified_by_tool':False,
        'adaptation':capability['host_adaptation'] if mode=='adapted_in_host' else None}
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--index',default=str(index_path()))
    sub=p.add_subparsers(dest='op',required=True)
    a=sub.add_parser('list');a.add_argument('--role')
    a=sub.add_parser('prepare');a.add_argument('--id',required=True);a.add_argument('--root',default=str(Path.home()/'.codex/academic-research-source-cache'));a.add_argument('--allow-network',action='store_true');a.add_argument('--out',required=True)
    a=sub.add_parser('use');a.add_argument('--id',required=True);a.add_argument('--prepared',required=True);a.add_argument('--input',action='append',required=True);a.add_argument('--output',action='append',required=True);a.add_argument('--step',action='append',required=True);a.add_argument('--mode',required=True);a.add_argument('--functions-run',action='store_true');a.add_argument('--out',required=True)
    a=p.parse_args(argv)
    try:
        idx=load(a.index)
        if a.op=='list':r=listing(idx,a.role)
        elif a.op=='prepare':r=prepare(entry(idx,a.id),a.root,a.allow_network)
        else:r=usage(entry(idx,a.id),load(a.prepared),a.input,a.output,a.step,a.mode,a.functions_run)
        if getattr(a,'out',None):
            target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(r,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'status':'needs_attention','error':str(e)},ensure_ascii=False),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
