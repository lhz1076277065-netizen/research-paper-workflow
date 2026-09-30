#!/usr/bin/env python3
"""Current-host, user-library routing and OPTIONAL research record checks.

This tool never launches a model/agent and does not grade scientific novelty.
Record checks do not prove that a recorded human/agent judgement is correct.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlparse

class ResearchError(ValueError):pass

def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def policy_path():
    home=Path(__file__).resolve().parents[1]
    choices=[home/'assets/research31-policy.json',home/'docs/research31-policy.json',home/'src/common/assets/research31-policy.json']
    return next((p for p in choices if p.is_file()),choices[0])
def policy():return load(policy_path())
def repo_name(value):
    if not isinstance(value,str):raise ResearchError('Repository must be a string')
    if '://' in value:
        u=urlparse(value)
        if u.scheme!='https' or u.netloc.lower()!='github.com' or u.query or u.fragment:raise ResearchError('Use a GitHub repository URL or owner/name')
        value=u.path.strip('/')
    value=value.removesuffix('.git')
    if not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+',value):raise ResearchError('Expected owner/repository, not a host endpoint or entry URL')
    return value

def allowed_repo(value,config=None):
    config=config or policy();repo=repo_name(value)
    aliases={k.lower():v for k,v in config.get('source_aliases',{}).items()}
    repo=aliases.get(repo.lower(),repo)
    approved={s['repository'].lower():s['repository'] for s in config['sources']}
    if repo.lower() not in approved:raise ResearchError('External Skill is outside the user-designated library: '+repo)
    return approved[repo.lower()]

def host_action(action):
    details=action if isinstance(action,dict) else {'action':action}
    name=details.get('action')
    if not isinstance(name,str) or not name.strip():raise ResearchError('host_actions requires a nonempty action name')
    target=details.get('assistant_target')
    if target is not None and not isinstance(target,str):raise ResearchError('assistant_target must be a string or null')
    # Scope concerns the executing assistant, not a vocabulary of research verbs.
    switches={'launch_other_host','discover_local_llm','switch_assistant','discover_assistant_endpoint'}
    outside=details.get('actor_scope','current_host')!='current_host' or target not in {None,'current_host'} or name in switches
    return {'action':name,'permitted_by_project_scope':not outside,
            'action_classification':'assistant_scope_change' if outside else 'current_host_operation',
            'action_semantics_verified':False,
            'host_scope':'current_host','os_sandbox_enforced':False,
            'note':'Scientific computation may use justified models; this does not authorize discovery or switching of the executing assistant.'}

def validate_upstream_command(args,config=None):
    if not args or args[0] not in {'discover','read','fetch','bind'}:raise ResearchError('Use an actual upstream discover/read/fetch/bind operation')
    def value(flag):
        positions=[i for i,x in enumerate(args) if x==flag or x.startswith(flag+'=')]
        if len(positions)>1:raise ResearchError('Repeated '+flag)
        if not positions:return None
        i=positions[0]
        if args[i].startswith(flag+'='):result=args[i].split('=',1)[1]
        elif i+1<len(args) and not args[i+1].startswith('--'):result=args[i+1]
        else:raise ResearchError('Missing '+flag+' value')
        if not result:raise ResearchError('Missing '+flag+' value')
        return result
    repo=value('--repo')
    index=value('--index')
    if repo is None and index:
        source=load(index)
        if not isinstance(source,dict):raise ResearchError('Source index must be an object')
        repo=source.get('repository')
    if repo is None:raise ResearchError('Explicit repository or source index required')
    return allowed_repo(repo,config)

def artifact(ref,root):
    """Check bytes, not semantic accuracy. Only actual project-root files are read."""
    if not isinstance(ref,dict) or not isinstance(ref.get('path'),str) or not ref['path']:raise ResearchError('Artifact requires path and sha256')
    base=Path(root).resolve();path=(base/ref['path']).resolve()
    if not path.is_relative_to(base) or not path.is_file():raise ResearchError('Artifact missing/outside project: '+ref['path'])
    if path.stat().st_size==0:raise ResearchError('Empty artifact: '+ref['path'])
    if not re.fullmatch('[0-9a-f]{64}',str(ref.get('sha256',''))) or sha(path)!=ref['sha256']:raise ResearchError('Artifact version mismatch: '+ref['path'])
    return {'path':ref['path'],'sha256':ref['sha256']}

def same_artifact(a,b):
    return isinstance(a,dict) and isinstance(b,dict) and all(a.get(k)==b.get(k) for k in ['path','sha256'])

def assess(state,root,config=None):
    config=config or policy();problems=[];next_steps=[];verified={};uses={}
    if not isinstance(state,dict):raise ResearchError('state must be an object')
    for key in ['documents','research_goal','final_expression','research_context','applicability']:
        if not isinstance(state.get(key,{}),dict):raise ResearchError(key+' must be an object')
    def sequence(obj,key,item_type):
        value=obj.get(key,[])
        if not isinstance(value,list) or any(not isinstance(x,item_type) for x in value):
            raise ResearchError(key+' must be a list of '+('objects' if item_type is dict else 'strings'))
        return value
    sequence(state,'additional_skill_roles',str)
    actions=state.get('host_actions',[])
    if not isinstance(actions,list) or any(not isinstance(x,(str,dict)) for x in actions):raise ResearchError('host_actions must be a list of action names or objects')
    sequence(state.get('research_context',{}),'study_types',str)
    for key in ['provider_uses','figures']:sequence(state,key,dict)
    for use in state.get('provider_uses',[]):
        for key in ['roles','steps']:sequence(use,key,str)
        for key in ['inputs','outputs','evidence']:sequence(use,key,dict)
        if not isinstance(use.get('document_bindings',{}),dict):raise ResearchError('document_bindings must be an object')
    for role,choice in state.get('applicability',{}).items():
        if not isinstance(choice,dict) or type(choice.get('applicable')) is not bool or not isinstance(choice.get('reason'),str) or not choice['reason'].strip():
            raise ResearchError('applicability '+role+' requires a boolean applicable and a reason')
    mode=state.get('mode','publication_research')
    if mode not in {'focused','publication_research','smoke','engineering_audit'}:raise ResearchError('Unknown mode')
    stage=state.get('stage','planning')
    if stage not in {'planning','research','delivery'}:raise ResearchError('Unknown stage')
    def missing(message):
        if message not in next_steps:next_steps.append(message)
    def check_ref(ref,label):
        try:return artifact(ref,root)
        except (ResearchError,OSError) as exc:problems.append(label+': '+str(exc));return None
    if state.get('host_scope','current_host')!='current_host':problems.append('Research host scope must remain current_host')
    for action in state.get('host_actions',[]):
        if not host_action(action)['permitted_by_project_scope']:problems.append('Unrequested assistant/host action: '+str(action))
    for role,ref in state.get('documents',{}).items():
        verified[role]=check_ref(ref,'document '+role)
    for use in state.get('provider_uses',[]):
        uid=use.get('id')
        if not isinstance(uid,str) or not uid or uid in uses:problems.append('Provider use ID missing/duplicate');continue
        uses[uid]=use
        try:allowed_repo(use.get('repository'),config)
        except ResearchError as exc:problems.append(str(exc))
        if use.get('actor_scope')!='current_host':problems.append(uid+': provider must execute in current host')
        if use.get('mode') not in {'native_in_host','adapted_in_host','function_only','reference_only'}:problems.append(uid+': unknown execution mode')
        if not re.fullmatch('[0-9a-f]{40}',str(use.get('commit',''))):problems.append(uid+': actual source commit required')
        if not use.get('entry'):problems.append(uid+': actual source entry required')
        if use.get('status')!='executed':missing(uid+': complete the selected operation, not just discovery/download')
        receipts=use.get('evidence',[])
        if not receipts:missing(uid+': attach actual operation/input/output evidence')
        for ref in receipts:check_ref(ref,uid+' evidence')
        for ref in use.get('inputs',[])+use.get('outputs',[]):check_ref(ref,uid+' material')
        for role,ref in use.get('document_bindings',{}).items():check_ref(ref,uid+' document binding '+role)
        if use.get('mode')=='adapted_in_host' and not use.get('adaptation'):missing(uid+': describe the actual adaptation once')
    context=state.get('research_context',{})
    protocol=context.get('article_type') in {'protocol-design','study-protocol','registered-report-stage1'}
    requested=state.get('requested_deliverable','protocol' if protocol else 'research_manuscript')
    if not isinstance(requested,str) or not requested.strip():raise ResearchError('requested_deliverable must be a nonempty string')
    if protocol and requested not in {'protocol','registered_report_stage1'}:
        problems.append('Protocol article type conflicts with the requested empirical/research deliverable')
        protocol=False
    if mode=='publication_research':
        ambition=state.get('research_goal',{})
        for name in ['problem','importance','knowledge_delta','decisive_test']:
            if not isinstance(ambition.get(name),str) or not ambition[name].strip():missing('Develop the research goal: '+name)
        required=['research_brief','prior_art','design']
        if stage in {'research','delivery'} and not protocol:required+=['research_results','validation']
        if stage=='delivery':required+=['manuscript','scientific_review','journal_fit']
        for role in required:
            if not verified.get(role):missing('Produce and inspect '+role+' for the actual scientific question')
        if stage=='delivery' and not protocol and state.get('scope_achievement')!='main_research':missing('Pilot/smoke output cannot finish the original publication-research objective')
        if stage=='delivery':
            # Coverage is stated per applicable research route; no all-19 invocation quota.
            roles=list(dict.fromkeys(['literature','reading','novelty','writing']+state.get('additional_skill_roles',[])))
            for role in roles:
                matching=[x for x in uses.values() if role in x.get('roles',[]) and x.get('status')=='executed' and x.get('mode') in {'native_in_host','adapted_in_host'} and x.get('evidence')]
                if role in {'literature','reading','novelty'}:
                    # A version-bound association permits reuse; a role label alone does not.
                    expected={k:verified.get(k) for k in ['research_brief','prior_art']}
                    matching=[x for x in matching if all(same_artifact(x.get('document_bindings',{}).get(k),ref) for k,ref in expected.items())]
                if role=='writing':
                    end_use=uses.get(state.get('final_expression',{}).get('provider_use'),{})
                    manuscript_versions=[verified.get('manuscript')]+end_use.get('inputs',[])
                    identities={(x['path'],x['sha256']) for x in manuscript_versions if x and 'path' in x and 'sha256' in x}
                    matching=[x for x in matching if x.get('scope')=='full_manuscript' and any((f.get('path'),f.get('sha256')) in identities for f in x.get('outputs',[]))]
                if not matching:missing('Complete a library-guided '+role+' operation on this research, or resolve its specific applicability')
    for f in state.get('figures',[]):
        record=check_ref(f.get('artifact'), 'figure');use=uses.get(f.get('provider_use'))
        if mode!='publication_research':continue
        if not f.get('claim'):missing('State the scientific job of each main figure')
        if not use:missing('Connect the main figure to the selected library figure workflow');continue
        if 'figure' not in use.get('roles',[]) or use.get('mode') not in {'native_in_host','adapted_in_host'}:missing('Export/profile alone does not cover main-figure production')
        required={'plan','select','produce','numeric_review','visual_review'}
        if not required<=set(use.get('steps',[])):missing('Finish main-figure reasoning, production, and numeric/visual review')
        if record and (record['path'],record['sha256']) not in [(x.get('path'),x.get('sha256')) for x in use.get('outputs',[])]:missing('Use evidence must cover this exact final figure, not a separate test plot')
        for kind in ['numeric_review','visual_review']:
            review=f.get(kind,{})
            if not isinstance(review,dict) or review.get('output_sha256')!=(record or {}).get('sha256'):missing('Review the final figure version: '+kind);continue
            check_ref(review.get('report'),kind)
        if not verified.get('figure_plan'):missing('Document the main-figure evidence structure and compare suitable visual choices')
    full_text=stage=='delivery' and mode=='publication_research'
    if full_text:
        end=state.get('final_expression',{});use=uses.get(end.get('provider_use'))
        if not use:missing('Apply the designated anti-defensive writing Skill to the final manuscript')
        else:
            try:repository=allowed_repo(use.get('repository'),config)
            except ResearchError:repository=None
            if repository!=config['final_expression_repository']:missing('Use the designated anti-defensive writing source, not a token substitute')
            if 'final_expression' not in use.get('roles',[]) or use.get('status')!='executed' or use.get('mode') not in {'native_in_host','adapted_in_host'}:missing('Perform the final expression pass on this manuscript')
            if use.get('scope')!='full_manuscript':missing('Apply final expression to the full manuscript, not only an excerpt or abstract')
            if not use.get('inputs'):missing('Retain the pre-expression manuscript')
            main=verified.get('manuscript')
            if main and (main['path'],main['sha256']) not in [(x.get('path'),x.get('sha256')) for x in use.get('outputs',[])]:missing('Expression pass must cover this final manuscript version')
            if 'facts_rechecked' in end and type(end['facts_rechecked']) is not bool:problems.append('facts_rechecked must be a boolean')
            if end.get('facts_rechecked') is not True:missing('Recheck claims, numbers, comparisons and important counterevidence after rewriting')
            review=check_ref(end.get('review'),'post-expression factual review') if end.get('review') else None
            if not review:missing('Provide the actual post-expression review result')
            else:
                subjects=sequence(end['review'],'subjects',dict)
                checked=[check_ref(ref,'post-expression reviewed subject') for ref in subjects]
                if not main or main not in checked:missing('Bind the post-expression review to this final manuscript version; repeat affected review after changes')
    if mode in {'smoke','engineering_audit'}:
        missing('Engineering outcome only; publication-research completion is not evaluated')
    return {'status':'record_error' if problems else 'research_in_progress' if next_steps else 'ready_for_content_review',
            'record_errors':problems,'next_actions':next_steps,'verified_documents':verified,
            'scientific_quality_certified':False,'top_journal_ready':None,
            'semantic_review_performed_by_this_tool':False,'host_scope':'current_host',
            'delivery_scope':'protocol' if protocol else requested,
            'empirical_research_completion_evaluated':not protocol and mode=='publication_research',
            'note':'This checks records and artifact identity; current-agent scientific and visual judgements still require actual evidence.'}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    a=sub.add_parser('sources');a.add_argument('--role')
    a=sub.add_parser('action');a.add_argument('action')
    a=sub.add_parser('assess');a.add_argument('--state',required=True);a.add_argument('--root',required=True);a.add_argument('--out')
    a=sub.add_parser('upstream');a.add_argument('args',nargs=argparse.REMAINDER)
    args=ap.parse_args(argv)
    try:
        if args.command=='sources':
            sources=policy()['sources'];result={'sources':[s for s in sources if not args.role or args.role in s['roles']],'entry_paths':'Discover the current entry in the selected repository','execution_started':False}
        elif args.command=='action':result=host_action(args.action)
        elif args.command=='upstream':
            validate_upstream_command(args.args)
            script=Path(__file__).with_name('upstream.py')
            if not script.is_file():raise ResearchError('Original v3 upstream.py is required; apply this upgrade to the full local base')
            return subprocess.run([sys.executable,str(script),*args.args],check=False).returncode
        else:
            result=assess(load(args.state),args.root)
            if args.out:
                target=Path(args.out);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 2 if result.get('status')=='record_error' else 0
    except (ValueError,OSError,TypeError,KeyError) as exc:
        print(json.dumps({'status':'needs_attention','error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
