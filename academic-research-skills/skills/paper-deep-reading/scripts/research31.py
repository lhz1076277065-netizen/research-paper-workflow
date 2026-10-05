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
    role=details.get('role','executor')
    if role not in {'executor','research_model'}:raise ResearchError('action role must be executor or research_model')
    assistant_change=name in switches and (role=='executor' or name!='discover_local_llm')
    outside=details.get('actor_scope','current_host')!='current_host' or target not in {None,'current_host'} or assistant_change
    model_authorization=None
    if role=='research_model':
        model_authorization=all(details.get(k) is True for k in ['local','free_to_use','license_allows_research']) and bool(details.get('purpose'))
        outside=outside or not model_authorization
    return {'action':name,'permitted_by_project_scope':not outside,
            'action_classification':'assistant_scope_change' if outside else 'current_host_operation',
            'role':role,'research_model_authorization_recorded':model_authorization,
            'action_semantics_verified':False,
            'host_scope':'current_host','os_sandbox_enforced':False,
            'note':'Scientific computation may use justified models; this does not authorize discovery or switching of the executing assistant.'}

def select_role(role,candidates,requirements=None,config=None):
    """Compare inspected entries; match facts supplied by the host, no quality score."""
    config=config or policy();requirements=requirements or {}
    if not isinstance(role,str) or not role:raise ResearchError('A research role is required')
    if not isinstance(candidates,list) or any(not isinstance(x,dict) for x in candidates):raise ResearchError('candidates must be objects')
    if not isinstance(requirements,dict):raise ResearchError('requirements must be an object')
    viable=[];excluded=[];seen=set()
    for c in candidates:
        uid=c.get('id')
        if not isinstance(uid,str) or not uid or uid in seen:raise ResearchError('Candidate IDs must be nonempty and unique')
        seen.add(uid);allowed_repo(c.get('repository'),config)
        reasons=[]
        if not c.get('entry') or not re.fullmatch('[0-9a-f]{40}',str(c.get('commit',''))):reasons.append('Inspect the actual entry and source version')
        if c.get('available') is not True:reasons.append('Current availability is not verified')
        if c.get('missing_dependencies'):reasons.append('Resolve the stated dependencies')
        for key in ['roles','domains','tasks','materials','outputs']:
            if not isinstance(c.get(key,[]),list) or any(not isinstance(x,str) for x in c.get(key,[])):raise ResearchError(key+' must be a string list')
        if role not in c.get('roles',[]):reasons.append('Role is not covered')
        for key in ['domains','tasks','materials','outputs']:
            wanted=requirements.get(key,[])
            if not isinstance(wanted,list) or any(not isinstance(x,str) for x in wanted):raise ResearchError('requirement '+key+' must be a string list')
            if wanted and not set(wanted)<=set(c.get(key,[])):reasons.append('Task mismatch: '+key)
        if reasons:excluded.append({'id':uid,'reasons':reasons})
        else:viable.append(c)
    viable.sort(key=lambda c:c.get('installed') is not True)
    primary=next((c for c in viable if not c.get('complement_role')),None)
    complements=[c for c in viable if c is not primary and c.get('complement_role') in {'complementary_coverage','independent_evaluation','fallback'} and isinstance(c.get('selection_reason'),str) and c['selection_reason'].strip()]
    return {'role':role,'primary':primary,'complements':complements,'excluded':excluded,
            'unselected':[c['id'] for c in viable if c is not primary and c not in complements],
            'selection_basis':'Verified task match, dependencies and availability; matching installed entry first; complements need an explicit purpose',
            'guidance_read':False,'research_work_done':False,'functions_run':False,'scientific_quality_certified':False}

def use_progress(use):
    declared=use.get('progress')
    if declared is not None:
        if not isinstance(declared,dict) or any(type(declared.get(k)) is not bool for k in ['guidance_read','research_work_done','functions_run']):
            raise ResearchError('progress requires separate guidance_read/research_work_done/functions_run booleans')
        return dict(declared)
    # Legacy executed records keep their work association; reading/function execution are unknown.
    return {'guidance_read':None,'research_work_done':use.get('status')=='executed' and use.get('mode') in {'native_in_host','adapted_in_host'},
            'functions_run':use.get('status')=='executed' if use.get('mode')=='function_only' else None}

def audit(data,root):
    # Import the co-located runtime so installed copies retain the same contract.
    import importlib.util
    path=Path(__file__).with_name('provider_runtime.py')
    spec=importlib.util.spec_from_file_location('_research31_provider_runtime',path)
    runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
    return runtime.audit_payload(data,root)

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
    config=config or policy();problems=[];next_steps=[];verified={};uses={};progress={};evidence_checks=[]
    if not isinstance(state,dict):raise ResearchError('state must be an object')
    for key in ['documents','research_goal','final_expression','research_context','applicability']:
        if not isinstance(state.get(key,{}),dict):raise ResearchError(key+' must be an object')
    end=state.get('final_expression',{})
    if not isinstance(end.get('operation',{}),dict):raise ResearchError('final_expression.operation must be an object')
    required_repository=allowed_repo(end['required_repository'],config) if 'required_repository' in end else None
    def sequence(obj,key,item_type):
        value=obj.get(key,[])
        if not isinstance(value,list) or any(not isinstance(x,item_type) for x in value):
            raise ResearchError(key+' must be a list of '+('objects' if item_type is dict else 'strings'))
        return value
    for key in ['inputs','outputs','evidence']:sequence(end.get('operation',{}),key,dict)
    sequence(end.get('operation',{}),'steps',str)
    sequence(state,'additional_skill_roles',str)
    actions=state.get('host_actions',[])
    if not isinstance(actions,list) or any(not isinstance(x,(str,dict)) for x in actions):raise ResearchError('host_actions must be a list of action names or objects')
    sequence(state.get('research_context',{}),'study_types',str)
    for key in ['provider_uses','figures','evidence_checks']:sequence(state,key,dict)
    queues={key:sequence(state,key,str)[:] for key in ['research_work','artifact_work','external_items']}
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
    def missing(message,queue='research_work'):
        if message not in next_steps:next_steps.append(message)
        if message not in queues[queue]:queues[queue].append(message)
    def check_ref(ref,label):
        try:return artifact(ref,root)
        except (ResearchError,OSError) as exc:problems.append(label+': '+str(exc));return None
    source_flow={'status':'unknown','accepted_steps':[],'semantic_work_verified_by_tool':False}
    if 'professional_steps' in state:
        import capabilities as C
        import professional_flow as F
        pairs=sequence(state,'professional_steps',dict)
        source_flow['status']='checked' if pairs else 'incomplete'
        if not pairs:missing('Invoke and complete the actual source-first professional steps')
        for pair in pairs:
            try:
                started=(Path(root)/pair['started']).resolve();finished=(Path(root)/pair['finished']).resolve()
                if not started.is_relative_to(Path(root).resolve()) or not finished.is_relative_to(Path(root).resolve()):
                    raise ResearchError('Professional records must belong to this project')
                checked=F.check(load(C.index_path()),load(started),load(finished))
                source_flow['accepted_steps'].append(checked)
            except (ValueError,OSError,KeyError,TypeError) as exc:
                source_flow['status']='incomplete';missing('Professional source step not complete: '+str(exc))
    if state.get('host_scope','current_host')!='current_host':problems.append('Research host scope must remain current_host')
    for action in state.get('host_actions',[]):
        if not host_action(action)['permitted_by_project_scope']:problems.append('Unrequested assistant/host action: '+str(action))
    for role,ref in state.get('documents',{}).items():
        verified[role]=check_ref(ref,'document '+role)
    for use in state.get('provider_uses',[]):
        uid=use.get('id')
        if not isinstance(uid,str) or not uid or uid in uses:problems.append('Provider use ID missing/duplicate');continue
        uses[uid]=use
        progress[uid]=use_progress(use)
        if progress[uid]['research_work_done'] is True and progress[uid]['guidance_read'] is False:
            missing(uid+': read the selected professional guidance before claiming library-guided work')
        try:allowed_repo(use.get('repository'),config)
        except ResearchError as exc:problems.append(str(exc))
        if use.get('actor_scope')!='current_host':problems.append(uid+': provider must execute in current host')
        if use.get('mode') not in {'native_in_host','adapted_in_host','function_only','reference_only'}:problems.append(uid+': unknown execution mode')
        if not re.fullmatch('[0-9a-f]{40}',str(use.get('commit',''))):problems.append(uid+': actual source commit required')
        if not use.get('entry'):problems.append(uid+': actual source entry required')
        if use.get('mode')!='reference_only' and progress[uid]['research_work_done'] is not True and use.get('mode')!='function_only':missing(uid+': complete the selected research work; reading and software execution are separate')
        receipts=use.get('evidence',[])
        if not receipts:missing(uid+': attach actual operation/input/output evidence')
        for ref in receipts:check_ref(ref,uid+' evidence')
        for ref in use.get('inputs',[])+use.get('outputs',[]):check_ref(ref,uid+' material')
        for role,ref in use.get('document_bindings',{}).items():check_ref(ref,uid+' document binding '+role)
        if use.get('mode')=='adapted_in_host' and not use.get('adaptation'):missing(uid+': describe the actual adaptation once')
    for check in state.get('evidence_checks',[]):
        checked=audit(check,root);evidence_checks.append(checked)
        if not checked.get('passed'):problems.extend('evidence check: '+str(x) for x in checked.get('errors',[]))
        for item in checked.get('pending',[]):missing('Resolve evidence association: '+str(item),'artifact_work')
        for key in checked.get('unlinked',[]):
            if key not in checked.get('pending',[]):missing('Associate the actual result with its occurrence: '+str(key),'artifact_work')
        if not checked.get('passed') and not any(checked.get(k) for k in ['errors','pending','unlinked']):
            problems.append('evidence check failed without a resolved diagnostic: '+str(checked.get('kind')))
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
            if not verified.get(role):missing('Produce and inspect '+role+' for the actual scientific question','artifact_work' if role in {'manuscript','scientific_review','journal_fit'} else 'research_work')
        if stage=='delivery' and not protocol and state.get('scope_achievement')!='main_research':missing('Pilot/smoke output cannot finish the original publication-research objective')
        if stage=='delivery':
            # Coverage is stated per applicable research route; no all-19 invocation quota.
            roles=list(dict.fromkeys(['literature','reading','novelty','writing']+state.get('additional_skill_roles',[])))
            for role in roles:
                matching=[x for x in uses.values() if role in x.get('roles',[]) and progress[x['id']]['research_work_done'] is True and x.get('mode') in {'native_in_host','adapted_in_host'} and x.get('evidence')]
                if role in {'literature','reading','novelty'}:
                    # A version-bound association permits reuse; a role label alone does not.
                    expected={k:verified.get(k) for k in ['research_brief','prior_art']}
                    matching=[x for x in matching if all(same_artifact(x.get('document_bindings',{}).get(k),ref) for k,ref in expected.items())]
                if role=='writing':
                    end_use=uses.get(end.get('provider_use'),end.get('operation',{}))
                    manuscript_versions=[verified.get('manuscript')]+end_use.get('inputs',[])
                    identities={(x['path'],x['sha256']) for x in manuscript_versions if x and 'path' in x and 'sha256' in x}
                    matching=[x for x in matching if x.get('scope')=='full_manuscript' and any((f.get('path'),f.get('sha256')) in identities for f in x.get('outputs',[]))]
                if not matching:missing('Complete a library-guided '+role+' operation on this research, or resolve its specific applicability','artifact_work' if role in {'writing','figure','final_expression'} else 'research_work')
    for f in state.get('figures',[]):
        record=check_ref(f.get('artifact'), 'figure');use=uses.get(f.get('provider_use'))
        if mode!='publication_research':continue
        if not f.get('claim'):missing('State the scientific job of each main figure','artifact_work')
        if not use:missing('Connect the main figure to the selected library figure workflow','artifact_work');continue
        if 'figure' not in use.get('roles',[]) or use.get('mode') not in {'native_in_host','adapted_in_host'}:missing('Export/profile alone does not cover main-figure production','artifact_work')
        required={'plan','select','produce','numeric_review','visual_review'}
        if not required<=set(use.get('steps',[])):missing('Finish main-figure reasoning, production, and numeric/visual review','artifact_work')
        if record and (record['path'],record['sha256']) not in [(x.get('path'),x.get('sha256')) for x in use.get('outputs',[])]:missing('Use evidence must cover this exact final figure, not a separate test plot','artifact_work')
        for kind in ['numeric_review','visual_review']:
            review=f.get(kind,{})
            if not isinstance(review,dict) or review.get('output_sha256')!=(record or {}).get('sha256'):missing('Review the final figure version: '+kind,'artifact_work');continue
            check_ref(review.get('report'),kind)
        if not verified.get('figure_plan'):missing('Document the main-figure evidence structure and compare suitable visual choices','artifact_work')
    full_text=stage=='delivery' and mode=='publication_research'
    if full_text:
        use=uses.get(end.get('provider_use'));operation=use or end.get('operation')
        if required_repository and (not use or allowed_repo(use.get('repository'),config)!=required_repository):
            missing('Complete the explicitly user-required final expression Skill: '+required_repository,'external_items')
        if not operation:missing('Perform evidence-preserving argument revision and factual review on the final manuscript','artifact_work')
        else:
            if use:
                if 'final_expression' not in use.get('roles',[]) or progress[use['id']]['research_work_done'] is not True or use.get('mode') not in {'native_in_host','adapted_in_host'}:missing('Perform the final expression pass on this manuscript','artifact_work')
            else:
                if operation.get('actor_scope')!='current_host':problems.append('final_expression.operation must execute in current host')
                if not {'argument_review','evidence_preservation'}<=set(sequence(operation,'steps',str)):missing('Complete evidence-preserving argument revision on the full manuscript','artifact_work')
                if not sequence(operation,'evidence',dict):missing('Provide evidence of the actual final expression operation','artifact_work')
                for key in ['inputs','outputs','evidence']:
                    for ref in sequence(operation,key,dict):check_ref(ref,'final expression '+key)
            if operation.get('scope')!='full_manuscript':missing('Apply final expression to the full manuscript, not only an excerpt or abstract','artifact_work')
            if not operation.get('inputs'):missing('Retain the pre-expression manuscript','artifact_work')
            main=verified.get('manuscript')
            if main and (main['path'],main['sha256']) not in [(x.get('path'),x.get('sha256')) for x in operation.get('outputs',[])]:missing('Expression pass must cover this final manuscript version','artifact_work')
            if 'facts_rechecked' in end and type(end['facts_rechecked']) is not bool:problems.append('facts_rechecked must be a boolean')
            if end.get('facts_rechecked') is not True:missing('Recheck claims, numbers, comparisons and important counterevidence after rewriting','artifact_work')
            review=check_ref(end.get('review'),'post-expression factual review') if end.get('review') else None
            if not review:missing('Provide the actual post-expression review result','artifact_work')
            else:
                subjects=sequence(end['review'],'subjects',dict)
                checked=[check_ref(ref,'post-expression reviewed subject') for ref in subjects]
                if not main or main not in checked:missing('Bind the post-expression review to this final manuscript version; repeat affected review after changes','artifact_work')
    if mode in {'smoke','engineering_audit'}:
        missing('Engineering outcome only; publication-research completion is not evaluated')
    for key in ['research_work','artifact_work']:
        for item in queues[key]:missing(item,key)
    return {'status':'record_error' if problems else 'research_in_progress' if next_steps else 'ready_for_content_review',
            'record_errors':problems,'next_actions':next_steps,'verified_documents':verified,
            'provider_progress':progress,'evidence_checks':evidence_checks,**queues,
            'professional_source_flow':source_flow,
            'scientific_quality_certified':False,'top_journal_ready':None,
            'semantic_review_performed_by_this_tool':False,'host_scope':'current_host',
            'delivery_scope':'protocol' if protocol else requested,
            'empirical_research_completion_evaluated':not protocol and mode=='publication_research',
            'note':'This checks records and artifact identity; current-agent scientific and visual judgements still require actual evidence.'}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
    a=sub.add_parser('sources');a.add_argument('--role')
    a=sub.add_parser('capabilities');a.add_argument('--role')
    a=sub.add_parser('phase');a.add_argument('args',nargs=argparse.REMAINDER)
    a=sub.add_parser('action');a.add_argument('action')
    a=sub.add_parser('select');a.add_argument('--role',required=True);a.add_argument('--input',required=True);a.add_argument('--out')
    a=sub.add_parser('audit');a.add_argument('--input',required=True);a.add_argument('--root',required=True);a.add_argument('--out')
    a=sub.add_parser('assess');a.add_argument('--state',required=True);a.add_argument('--root',required=True);a.add_argument('--out')
    a=sub.add_parser('upstream');a.add_argument('args',nargs=argparse.REMAINDER)
    args=ap.parse_args(argv)
    try:
        if args.command=='sources':
            sources=policy()['sources'];result={'sources':[s for s in sources if not args.role or args.role in s['roles']],'entry_paths':'Discover the current entry in the selected repository','execution_started':False}
        elif args.command=='capabilities':
            import capabilities
            result=capabilities.listing(load(capabilities.index_path()),args.role)
        elif args.command=='phase':
            return subprocess.run([sys.executable,str(Path(__file__).with_name('phase_control.py')),*args.args],check=False).returncode
        elif args.command=='action':result=host_action(args.action)
        elif args.command=='select':
            data=load(args.input);result=select_role(args.role,data['candidates'],data.get('requirements'))
        elif args.command=='audit':result=audit(load(args.input),args.root)
        elif args.command=='upstream':
            validate_upstream_command(args.args)
            script=Path(__file__).with_name('upstream.py')
            if not script.is_file():raise ResearchError('Original v3 upstream.py is required; apply this upgrade to the full local base')
            return subprocess.run([sys.executable,str(script),*args.args],check=False).returncode
        else:
            result=assess(load(args.state),args.root)
        if getattr(args,'out',None):
            target=Path(args.out);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 2 if result.get('status')=='record_error' or result.get('passed') is False else 0
    except (ValueError,OSError,TypeError,KeyError) as exc:
        print(json.dumps({'status':'needs_attention','error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
