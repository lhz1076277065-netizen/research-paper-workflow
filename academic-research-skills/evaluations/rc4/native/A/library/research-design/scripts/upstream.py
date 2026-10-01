#!/usr/bin/env python3
"""Discover skills at the current GitHub ref; read/fetch a stable run snapshot.

Standard library. No repository allowlist, model runtime, or provider installer.
A saved index fixes one run's source version; another discover sees later updates.
"""
from __future__ import annotations
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
import math
from pathlib import Path, PurePosixPath
import re
import sys
import time
from urllib.error import HTTPError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

class UpstreamError(ValueError):
    pass

def stamp():
    return datetime.now(timezone.utc).isoformat()

def repository(value):
    """Accept any explicit public GitHub repository, not just seed sources."""
    if not isinstance(value, str):
        raise UpstreamError('repository must be owner/repo or a GitHub repository URL')
    if '://' in value:
        u = urlparse(value)
        if u.scheme != 'https' or u.netloc.lower() != 'github.com' or u.query or u.fragment:
            raise UpstreamError('Use a repository URL such as https://github.com/owner/repo')
        value = u.path.strip('/')
    value = value.removesuffix('.git')
    if not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', value) or value.split('/')[1] in {'.','..'}:
        raise UpstreamError('Expected owner/repo; pass branch and entry separately')
    return value

def relpath(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or '\x00' in value:
        raise UpstreamError('Invalid repository path')
    p = PurePosixPath(value)
    if p.is_absolute() or value=='.' or '..' in p.parts or str(p) != value:
        raise UpstreamError('Expected a canonical repository-relative path')
    return value

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def save_json(path, value):
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')

def _sha(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-fA-F]{40}', value):
        raise UpstreamError('Expected an actual GitHub SHA, not a placeholder')
    return value.lower()

class GitHubAPI:
    def __init__(self, allow_network=False, timeout=30, token=None, max_attempts=2):
        if not math.isfinite(timeout) or timeout <= 0:
            raise UpstreamError('timeout must be positive')
        if type(max_attempts) is not int or max_attempts<1:raise UpstreamError('max_attempts must be positive')
        self.allow_network, self.timeout, self.token = allow_network, timeout, token
        self.max_attempts = max_attempts
    def __call__(self, endpoint):
        if not self.allow_network:
            raise UpstreamError('Network not enabled; use the host connector or --allow-network')
        if not endpoint.startswith('/repos/'):
            raise UpstreamError('Only repository endpoints are used')
        headers = {'Accept':'application/vnd.github+json','User-Agent':'academic-skills-source-discovery'}
        if self.token:
            headers['Authorization'] = 'Bearer '+self.token
        req = Request('https://api.github.com'+endpoint, headers=headers)
        for attempt in range(self.max_attempts):
            try:
                with urlopen(req, timeout=self.timeout) as response:
                    return json.load(response)
            except HTTPError as exc:
                limited=exc.code==429 or (exc.code==403 and exc.headers.get('x-ratelimit-remaining')=='0')
                retry=limited or exc.code in {500,502,503,504}
                delay=exc.headers.get('Retry-After')
                try:delay=float(delay) if delay else 0.5*(attempt+1)
                except (TypeError,ValueError):delay=self.timeout+1
                if retry and attempt+1<self.max_attempts and math.isfinite(delay) and 0<=delay<=min(self.timeout,5):
                    time.sleep(delay);continue
                category='rate limited; reuse a saved source or retry later' if limited else 'HTTP '+str(exc.code)
                raise UpstreamError('GitHub '+category) from exc
            except Exception as exc:
                raise UpstreamError('GitHub request failed: '+str(exc)) from exc

def index_tree(repo, commit, tree_sha, entries, *, checked_at=None, requested_ref=None,
               default_branch=None, complete=True, unresolved=()):
    repo, commit, tree_sha = repository(repo), _sha(commit), _sha(tree_sha)
    files, skill_paths = {}, []
    for row in entries:
        if row.get('type') != 'blob' or row.get('mode') not in {'100644','100755'}:
            continue  # symlinks and submodule pointers are not executable skill files
        path = relpath(row['path'])
        item = {'path':path,'blob_sha':_sha(row['sha']),'size':row.get('size')}
        if path in files and files[path] != item:
            raise UpstreamError('Conflicting paths in tree response: '+path)
        files[path] = item
        if PurePosixPath(path).name == 'SKILL.md':
            skill_paths.append(path)
    return {'schema_version':'upstream-index-1','repository':repo,
            'url':'https://github.com/'+repo,'requested_ref':requested_ref,
            'default_branch':default_branch,'commit':commit,'tree_sha':tree_sha,
            'checked_at':checked_at or stamp(),'complete':bool(complete),
            'unresolved_trees':list(unresolved),'skills':sorted(set(skill_paths)),
            'files':files,'execution_performed':False}

def discover(repo, *, ref=None, api=None, max_tree_calls=100):
    """Resolve the ref once. Fetch non-recursive subtrees if GitHub truncates."""
    repo = repository(repo)
    if max_tree_calls < 1:
        raise UpstreamError('max_tree_calls must be positive')
    api = api or GitHubAPI()
    meta = api('/repos/'+repo)
    canonical = repository(meta.get('full_name', repo))
    branch = meta.get('default_branch')
    resolved_ref = ref or branch
    if not isinstance(resolved_ref,str) or not resolved_ref:
        raise UpstreamError('Repository has no resolvable default branch')
    commit_record = api('/repos/'+canonical+'/commits/'+quote(resolved_ref,safe=''))
    commit = _sha(commit_record['sha'])
    tree_sha = _sha(commit_record['commit']['tree']['sha'])
    prefix = '/repos/'+canonical+'/git/trees/'
    tree = api(prefix+tree_sha+'?recursive=1')
    entries, calls, queue = tree.get('tree',[]), 1, []
    if tree.get('truncated', False):
        entries = []
        queue = [('',tree_sha)]
        while queue and calls < max_tree_calls:
            directory, sha = queue.pop(0)
            node = api(prefix+sha)
            calls += 1
            if node.get('truncated',False):
                queue.insert(0,(directory,sha))
                break
            for row in node.get('tree',[]):
                path = directory+row['path']
                if row['type'] == 'tree':
                    queue.append((path+'/', _sha(row['sha'])))
                else:
                    entries.append({**row,'path':path})
    result = index_tree(canonical,commit,tree_sha,entries,requested_ref=ref,
                        default_branch=branch,complete=not queue,unresolved=queue)
    result['tree_calls'] = calls
    return result

def read_source(index, entry, *, api=None, cache=None):
    """Read the indexed version even if default branch moves in the meantime."""
    repo, commit, entry = repository(index['repository']), _sha(index['commit']), relpath(entry)
    row = index.get('files',{}).get(entry)
    if row is None:
        raise UpstreamError('Path is absent from this index; check current layout or incomplete tree')
    cached=Path(cache).expanduser() if cache is not None else None
    if cached is not None and cached.exists():
        content=cached.read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
        if actual!=_sha(row['blob_sha']):raise UpstreamError('Existing source differs from the indexed version; retain it and choose a new output path')
        try:return content.decode('utf-8')
        except UnicodeDecodeError as exc:raise UpstreamError('Cached source is not UTF-8 text') from exc
    client=api or GitHubAPI()
    data = client('/repos/'+repo+'/contents/'+quote(entry,safe='/')+'?ref='+commit)
    if data.get('type') != 'file':raise UpstreamError('Selected source is not a file')
    if data.get('encoding')=='none':
        data=client('/repos/'+repo+'/git/blobs/'+_sha(row['blob_sha']))
    if data.get('encoding') != 'base64':
        raise UpstreamError('API cannot supply this file; use the checkout/host file tool')
    try:
        content = base64.b64decode(''.join(data['content'].split()), validate=True)
    except (ValueError, KeyError) as exc:
        raise UpstreamError('Malformed content response') from exc
    actual = hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
    if actual != row['blob_sha'] or actual != data.get('sha'):
        raise UpstreamError('File differs from indexed source version; rediscover explicitly')
    try:
        text=content.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise UpstreamError('Selected source is binary, not a text skill') from exc
    if cached is not None:
        cached.parent.mkdir(parents=True,exist_ok=True)
        with cached.open('xb') as f:f.write(content)
    return text

def provider_id(index, entry):
    """One stable identity for discover/bind/fetch/config; commit remains per-run."""
    return repository(index['repository'])+'::'+relpath(entry)


def fetch_snapshot(index,entry,destination,*,apply=False,allow_network=False,mirror=None,timeout=120,support=()):
    from portable_skill import fetch_provider
    entry=relpath(entry)
    required=list(dict.fromkeys([entry]+[relpath(x) for x in support]))
    if any(x not in index['files'] for x in required):raise UpstreamError('Entry or support absent from index')
    candidate={'id':provider_id(index,entry),'repo':repository(index['repository']),'required_paths':required}
    result=fetch_provider(candidate['id'],_sha(index['commit']),destination,apply=apply,
        allow_network=allow_network,mirror=mirror,registry={'providers':[candidate]},timeout=timeout)
    if result.get('status') in {'source_checked_out_needs_review','source_reused_needs_review'}:
        # Verify only the selected entry/support; other dependencies are read as needed.
        mismatches=[]
        for rel in required:
            data=(Path(destination).expanduser()/rel).read_bytes()
            actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            if actual!=index['files'][rel]['blob_sha']:mismatches.append(rel)
        if mismatches:result.update(status='source_index_mismatch',mismatched_paths=mismatches,configuration_fragment=None)
    return result


def bind(index, entry, capability, service, *, requires_host=(), requires_facts=(), support=(), adapter=None, script=None):
    """Make a run-local native provider descriptor. The host decides suitability."""
    entry = relpath(entry)
    if entry not in index['files']:
        raise UpstreamError('Entry is not in this run index')
    if PurePosixPath(entry).name != 'SKILL.md':
        raise UpstreamError('Use non-SKILL resources as reference or an explicit script, not native Skill')
    if not capability or not service:
        raise UpstreamError('Declare current capability and operation')
    required = list(dict.fromkeys([entry]+[relpath(p) for p in support]))
    missing = [p for p in required if p not in index['files']]
    if missing:
        raise UpstreamError('Declared support files absent: '+', '.join(missing))
    if adapter:
        if adapter not in {'researchstudio-search','scipilot-profile'} or not script:
            raise UpstreamError('Select a supported function interface and its actual script path')
        script=relpath(script)
        if script not in index['files']:raise UpstreamError('Script absent from index')
        required=list(dict.fromkeys(required+[script]))
    elif script:
        raise UpstreamError('Script requires a named adapter interface')
    pid = provider_id(index,entry)
    provider = {'id':pid,'repo':index['repository'],'entrypoint':entry,
                'capabilities':[capability],'mode':'native','phase':1,'default_candidate':True,
                'source_review_status':'discovered_needs_task_reading','required_paths':required,
                'requires_host':list(requires_host),'requires_facts':list(requires_facts),
                'entry_git_blob_sha':None,  # discovery is not a semantic/source review
                'discovered_blob_sha':index['files'][entry]['blob_sha'],
                'discovered_file_blob_sha':{path:_sha(index['files'][path]['blob_sha']) for path in required},
                'resolved_commit':index['commit'],'script':None,
                'purpose':'Run-local selection for '+service,'notes':'Read selected current source and actual dependencies.',
                'adaptations':[],
                'services':{service:{'capabilities':[capability],'requires_host':list(requires_host),
                                     'requires_facts':list(requires_facts),'mode':'native'}}}
    if adapter:
        provider['mode']='script-adapter'
        provider['services'][service]['mode']='script-adapter'
        provider['script']={'adapter':adapter,'path':script,'git_blob_sha':None,'network':adapter=='researchstudio-search'}
    return {'schema_version':'runtime-providers-1','capabilities':[capability],'providers':[provider],
            'source_index':{k:index[k] for k in ['repository','commit','checked_at','complete']}}

def candidates(index, query='', limit=12):
    if limit < 1:
        raise UpstreamError('limit must be positive')
    words = query.lower().split()
    paths = sorted(index['skills'],key=lambda p:(-sum(w in p.lower() for w in words), p))
    return {'repository':index['repository'],'commit':index['commit'],
            'complete':index['complete'],'total_skills':len(paths),'shown':paths[:limit],
            'remaining':max(0,len(paths)-limit),'ranking':'path hint only; host reads selected metadata'}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action',required=True)
    d = sub.add_parser('discover');d.add_argument('--repo',required=True);d.add_argument('--ref')
    d.add_argument('--out',required=True);d.add_argument('--query',default='');d.add_argument('--limit',type=int,default=12)
    d.add_argument('--max-tree-calls',type=int,default=100)
    d = sub.add_parser('read');d.add_argument('--index',required=True);d.add_argument('--entry',required=True);d.add_argument('--out',required=True)
    d = sub.add_parser('bind');d.add_argument('--index',required=True);d.add_argument('--entry',required=True)
    d.add_argument('--capability',required=True);d.add_argument('--service',required=True);d.add_argument('--out',required=True)
    d.add_argument('--adapter');d.add_argument('--script');d.add_argument('--support',action='append',default=[]);d.add_argument('--requires-host',action='append',default=[])
    d.add_argument('--requires-fact',action='append',default=[])
    d = sub.add_parser('fetch');d.add_argument('--index',required=True);d.add_argument('--entry',required=True)
    d.add_argument('--destination',required=True);d.add_argument('--apply',action='store_true');d.add_argument('--mirror');d.add_argument('--support',action='append',default=[])
    for name in ['discover','read','fetch']:
        obj = sub.choices[name];obj.add_argument('--allow-network',action='store_true')
        obj.add_argument('--token-env');obj.add_argument('--timeout',type=float,default=30)
    a = p.parse_args(argv)
    try:
        token = os.environ.get(a.token_env) if getattr(a,'token_env',None) else None
        api = GitHubAPI(getattr(a,'allow_network',False),getattr(a,'timeout',30),token)
        if a.action == 'discover':
            if Path(a.out).exists():raise UpstreamError('Keep the existing run index; use a new output path for a new source version')
            index = discover(a.repo,ref=a.ref,api=api,max_tree_calls=a.max_tree_calls)
            save_json(a.out,index);result = {**candidates(index,a.query,a.limit),'index':str(Path(a.out).absolute())}
        elif a.action == 'read':
            index = read_json(a.index);out=Path(a.out).expanduser();reused=out.exists()
            text = read_source(index,a.entry,api=api,cache=out)
            result = {'status':'source_reused' if reused else 'source_read','path':str(out.absolute()),'commit':index['commit'],
                      'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'characters':len(text),'cache_reused':reused,'execution_performed':False}
        elif a.action == 'bind':
            result = bind(read_json(a.index),a.entry,a.capability,a.service,requires_host=a.requires_host,
                          requires_facts=a.requires_fact,support=a.support,adapter=a.adapter,script=a.script)
            save_json(a.out,result)
        else:
            result = fetch_snapshot(read_json(a.index),a.entry,a.destination,apply=a.apply,
                       allow_network=a.allow_network,mirror=a.mirror,timeout=a.timeout,support=a.support)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 3 if result.get('status','') in {'source_fetch_failed','source_missing_required_paths','git_required','blocked_network_authorization','source_local_changes','source_index_mismatch'} else 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({'status':'needs_attention','error':str(exc),'execution_performed':False},ensure_ascii=False),file=sys.stderr)
        return 2
if __name__ == '__main__':
    raise SystemExit(main())
