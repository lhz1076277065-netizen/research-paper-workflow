#!/usr/bin/env python3
"""Mandatory source-first professional work; file checks do not judge science.

begin emits the actual pinned guide before work. finish requires source-linked
actions in the current output. check rejects preparation-only and stale work.
No host_fallback, dependency installation, external assistant or research loop.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import uuid
import capabilities as C

class FlowError(ValueError): pass

def ref(path):
    p=Path(path).resolve()
    if not p.is_file() or not p.stat().st_size: raise FlowError('Missing or empty artifact: '+str(path))
    return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def verify(r):
    if ref(r['path'])!=r: raise FlowError('Artifact changed: '+r['path'])

def save_new(path, receipt):
    """Publish a complete receipt without overwriting another invocation."""
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=p.parent,prefix='.professional-')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
        os.link(tmp,p)
    finally:os.unlink(tmp)

def persist(receipt, output, started=None):
    context=receipt.get('phase') if started is None else started.get('phase')
    if not context:
        save_new(output,receipt);return
    import phase_control as P
    with P.locked(context['path']):
        state=P.load(context['path'])
        # Recheck after source preparation; a pause or steering may arrive during it.
        if any(state.get(k)!=context.get(k) for k in ('id','stage','latest_instruction')):
            raise FlowError('Phase changed before receipt could be saved')
        if state['status']!='active':raise FlowError('Phase stopped before receipt could be saved')
        if started is None:P.register_professional(state,receipt,output)
        else:P.register_completion(state,started,output)
        save_new(output,receipt)
        P.save(context['path'],state)

def routes(index): return index['professional_routes']

def begin(index, capability, task, inputs, cache, selected=None, allow_network=False, phase=None, profile=None):
    route=routes(index).get(capability)
    if not route: raise FlowError('No verified professional route; stop this step: '+capability)
    context=None
    if phase:
        import phase_control as P
        state=P.load(phase)
        if state['scope']=='maintenance' or not P.guard(state)['allowed']:raise FlowError('Research source step is not permitted in this phase')
        context={'path':str(Path(phase).resolve()),'id':state['id'],'stage':state['stage'],'latest_instruction':state['latest_instruction']}
        profile=profile or state['scope']
    uid=selected or route.get('profiles',{}).get(profile,route['primary'])
    if uid not in [route['primary']]+route.get('alternatives',[]):
        raise FlowError('Source is not verified for this step; verify a matching entry before work')
    cap=C.entry(index,uid)
    if cap['repository'] not in {c['repository'] for c in index['capabilities']}:
        raise FlowError('Source outside the fourteen approved repositories')
    task_ref=ref(task); input_refs=[ref(p) for p in inputs]
    if not input_refs:raise FlowError('Actual task inputs are required')
    if phase:
        cutoff=min(state['deadline'],state['project_deadline']-state['reserve_seconds'])
        def still_current():
            current=P.load(phase)
            return P.guard(current)['allowed'] and all(current.get(k)==context[k] for k in ('id','stage','latest_instruction'))
        prepared=C.prepare(cap,cache,allow_network,deadline=cutoff,guard=still_current)
    else:prepared=C.prepare(cap,cache,allow_network)
    guide=Path(prepared['entry']).read_text(encoding='utf-8')
    return {'schema_version':'professional-step-1','id':uuid.uuid4().hex,
        'capability':capability,'status':'awaiting_professional_work','started_ns':time.time_ns(),
        'task':task_ref,'inputs':input_refs,'source':prepared,'guide':guide,
        'required_work':route['work'],'boundary':route['boundary'],
        'phase':context,'profile':profile,'handoff_scope':'requested_step_only',
        'professional_work_done':False,'host_fallback_allowed':False}

def validate_start(index, start, current_phase=True):
    if not isinstance(start,dict):raise FlowError('Begin receipt must be an object')
    if start.get('schema_version')!='professional-step-1' or start.get('status')!='awaiting_professional_work':
        raise FlowError('A source-first begin receipt is required')
    route=routes(index).get(start['capability'],{})
    uid=start['source']['id']
    if uid not in [route.get('primary')]+route.get('alternatives',[]): raise FlowError('Route identity changed')
    if start.get('required_work')!=route['work'] or start.get('boundary')!=route['boundary']:
        raise FlowError('Route work changed; preserve old work and begin the revised step')
    cap=C.entry(index,uid)
    if start['source']['commit']!=cap['commit'] or start['source']['repository']!=cap['repository']:
        raise FlowError('Source identity changed')
    source=C.prepare(cap,Path(start['source']['root']).parents[1],False)
    if source!=start['source'] or Path(source['entry']).read_text(encoding='utf-8')!=start['guide']:
        raise FlowError('Prepared source changed')
    verify(start['task'])
    if not start['inputs']: raise FlowError('No actual inputs')
    for r in start['inputs']: verify(r)
    if start.get('phase'):
        context=start['phase'];state=C.load(context['path'])
        keys=['id','stage','latest_instruction'] if current_phase else ['id']
        if any(state.get(k)!=context[k] for k in keys):
            raise FlowError('Phase or latest instruction changed; do not reuse an unrelated step')
        if current_phase and state.get('status')!='active':raise FlowError('No new professional completion in a stopped phase')
        if current_phase and any(x['step_id']==start['id'] and x['status']=='cancelled' for x in state.get('professional_pending',[])):
            raise FlowError('Professional step was cancelled; preserve it without completing it')
    return cap

def finish(index, start, outputs, report, mode, current_phase=True):
    cap=validate_start(index,start,current_phase)
    if mode not in {'adapted_in_host','native_in_host'}:
        raise FlowError('Reading, reference-only or function-only work cannot complete a professional step')
    if not outputs: raise FlowError('No professional output')
    refs=[ref(p) for p in outputs]
    input_paths={r['path'] for r in start['inputs']+[start['task']]}
    for r in refs:
        p=Path(r['path'])
        if r['path'] in input_paths: raise FlowError('Preserve inputs; return a separate current output')
        if p.stat().st_mtime_ns<start['started_ns']: raise FlowError('Earlier output cannot complete this new step')
    report_ref=ref(report); work=C.load(report)
    if not isinstance(work,dict):raise FlowError('Work report must be an object')
    if work.get('step_id')!=start['id']: raise FlowError('Work report belongs to another step')
    if work.get('scope')!='requested_step' or work.get('omitted_required_work')!=[]:
        raise FlowError('Partial work cannot complete the requested professional step')
    actions=work.get('actions',[])
    if not isinstance(actions,list) or not actions: raise FlowError('No source-guided actions')
    output_map={}
    for r in refs:
        try:output_map[r['path']]=Path(r['path']).read_text(encoding='utf-8')
        except UnicodeDecodeError:output_map[r['path']]=None
    texts={f['path']:C.path_under(start['source']['root'],f['path']).read_text(encoding='utf-8',errors='replace')
        for f in cap['required_files']}
    covered=set()
    for a in actions:
        if not isinstance(a,dict): raise FlowError('Invalid action')
        excerpt=a.get('source_excerpt',''); result=a.get('output_excerpt','')
        source=a.get('source_file'); out=str(Path(a.get('output','')).resolve())
        if source not in texts or len(excerpt.strip())<8 or excerpt not in texts[source]:
            raise FlowError('Action is not anchored to the prepared professional source')
        connected=out in output_map and ((output_map[out] is not None and len(result.strip())>=8 and result in output_map[out]) or
            (output_map[out] is None and a.get('output_sha256')==ref(out)['sha256'] and len(a.get('observation','').strip())>=8))
        if not connected:
            raise FlowError('Action is not connected to this step output')
        if not isinstance(a.get('applied'),str) or not a['applied'].strip(): raise FlowError('Missing actual professional action')
        covered.add(out)
    if covered!=set(output_map): raise FlowError('Every returned output needs a source-guided action')
    use=C.usage(cap,start['source'],[r['path'] for r in start['inputs']],outputs,
        [a['applied'] for a in actions],mode,work.get('functions_run') is True)
    completed={'schema_version':'professional-completion-1','status':'completed_for_handoff',
        'step_id':start['id'],'capability':start['capability'],'task':start['task'],
        'inputs':start['inputs'],'outputs':refs,'work_report':report_ref,'use':use,
        'semantic_work_verified_by_tool':False,'scientific_validity_certified':False}
    if start.get('handoff_scope'):
        completed.update(handoff_scope=start['handoff_scope'],submission_readiness='not_assessed')
    return completed

def check(index, start, completion):
    validate_start(index,start,False)
    if not isinstance(completion,dict):raise FlowError('Completion receipt must be an object')
    if completion.get('schema_version')!='professional-completion-1' or completion.get('status')!='completed_for_handoff':
        raise FlowError('Professional work has not completed; source preparation alone is insufficient')
    if completion.get('step_id')!=start['id'] or completion.get('capability')!=start['capability']:
        raise FlowError('Completion belongs to another step')
    if completion.get('task')!=start['task'] or completion.get('inputs')!=start['inputs']:
        raise FlowError('Task/input identity changed')
    verify(completion['work_report'])
    for r in completion['outputs']: verify(r)
    actual=finish(index,start,[r['path'] for r in completion['outputs']],completion['work_report']['path'],completion['use']['mode'],False)
    if actual!=completion: raise FlowError('Completion receipt changed')
    return {'status':'eligible_for_handoff','step_id':start['id'],'capability':start['capability'],
        'outputs':completion['outputs'],'semantic_work_verified_by_tool':False}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--index',default=str(C.index_path()))
    sub=p.add_subparsers(dest='op',required=True)
    a=sub.add_parser('begin');a.add_argument('--capability',required=True);a.add_argument('--task',required=True)
    a.add_argument('--input',action='append',required=True);a.add_argument('--source');a.add_argument('--allow-network',action='store_true')
    a.add_argument('--cache',default=str(Path.home()/'.codex/academic-research-source-cache'));a.add_argument('--phase');a.add_argument('--profile',choices=['focused','full']);a.add_argument('--compact',action='store_true');a.add_argument('--out',required=True)
    a=sub.add_parser('finish');a.add_argument('--started',required=True);a.add_argument('--output',action='append',required=True)
    a.add_argument('--work-report',required=True);a.add_argument('--mode',choices=['adapted_in_host','native_in_host'],default='adapted_in_host');a.add_argument('--out',required=True)
    a=sub.add_parser('check');a.add_argument('--started',required=True);a.add_argument('--finished',required=True)
    a=p.parse_args(argv)
    try:
        idx=C.load(a.index)
        if getattr(a,'out',None) and Path(a.out).exists(): raise FlowError('Receipt exists; check/resume it instead of overwriting')
        if a.op=='begin': r=begin(idx,a.capability,a.task,a.input,a.cache,a.source,a.allow_network,a.phase,a.profile)
        elif a.op=='finish':
            started=C.load(a.started);r=finish(idx,started,a.output,a.work_report,a.mode)
        else:r=check(idx,C.load(a.started),C.load(a.finished))
        if getattr(a,'out',None):
            persist(r,a.out,started if a.op=='finish' else None)
        shown=r
        if a.op=='begin':
            shown={**r,'source':{k:v for k,v in r['source'].items() if k!='files'},
                'support_file_count':len(r['source']['files']),'full_receipt':str(Path(a.out).resolve())}
            if a.compact:
                shown.pop('guide')
                shown.update(guide_path=r['source']['entry'],guide_read_required=True,
                    next_action='Read the actual entry and needed mode/support resources, then perform the professional work. This receipt is preparation only.')
        print(json.dumps(shown,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'status':'blocked_source_step','error':str(e),'host_fallback_allowed':False},ensure_ascii=False),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
