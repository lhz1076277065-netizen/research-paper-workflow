#!/usr/bin/env python3
"""Bounded local work phases; never changes the host goal or certifies research.

State is a work receipt, not authorization. Caller must hold the user's actual
authorization. run monitors only the child process group it creates itself.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

STAGES = ('feasibility', 'design', 'research', 'manuscript', 'delivery')
TERMINAL = {'completed', 'closed_limit', 'route_closed', 'paused'}

class PhaseError(ValueError): pass

def now(): return time.time()
def iso(t): return datetime.fromtimestamp(t, timezone.utc).isoformat()
def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))
def save(path, state):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.' + uuid.uuid4().hex + '.tmp')
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    os.replace(tmp, p)

@contextmanager
def locked(path):
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    with p.with_name(p.name+'.lock').open('a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield

def number(v, name, allow_zero=False):
    if isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v) or v < 0 or (not allow_zero and v == 0):
        raise PhaseError(name+' must be finite and '+('nonnegative' if allow_zero else 'positive'))
    return v

def artifact(path, root):
    root=Path(root).resolve(); p=(root/path).resolve()
    if not p.is_relative_to(root) or not p.is_file() or not p.stat().st_size:
        raise PhaseError('Evidence missing, empty or outside project: '+str(path))
    return {'path':str(p.relative_to(root)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

def init(scope, objective, minutes=None, clock=None, authority=None):
    if scope not in {'full','focused','maintenance'} or not objective.strip(): raise PhaseError('Invalid scope/objective')
    if authority is not None and (not isinstance(authority,str) or not authority.strip() or minutes is None):
        raise PhaseError('A supplied total budget needs minutes and actual user authorization')
    t=now() if clock is None else clock
    duration=number(45 if minutes is None else minutes,'minutes')*60
    return {'schema_version':'research-phase-1', 'id':uuid.uuid4().hex,
        'scope':scope, 'objective':objective, 'latest_instruction':objective,
        'status':'active', 'stage':'feasibility' if scope=='full' else scope,
        'started_at':iso(t), 'deadline':t+duration, 'project_deadline':t+duration,
        'reserve_seconds':min(300,duration*.1), 'budget_kind':'authorized_total' if authority else 'initial_feasibility' if scope=='full' else 'local_task',
        'authorization':authority, 'token_limit':None, 'token_reserve':0,
        'meter':{'verified':False,'baseline':None,'latest':None,'source':None},
        'completed_tasks':[], 'artifacts':[], 'history':[], 'repairs':{},
        'unchanged_rounds':0, 'reassessment_required':False, 'next_action':None,
        'owned_processes':[], 'professional_pending':[], 'stage_started_at':iso(t), 'host_goal_state':'not_modified'}

def usage_delta(state):
    m=state['meter']
    if not m['verified'] or m['baseline'] is None or m['latest'] is None: return None
    a=m['baseline']; b=m['latest']
    values={k:b[k]-a[k] for k in ('input_tokens','cached_input_tokens','output_tokens')}
    if any(x<0 for x in values.values()): raise PhaseError('Meter reset: do not reset the phase budget')
    values['total_tokens']=values['input_tokens']+values['output_tokens']
    values['noncached_input_plus_output']=values['total_tokens']-values['cached_input_tokens']
    return values

def guard(state, estimated_seconds=0, estimated_tokens=0, clock=None):
    t=now() if clock is None else clock
    number(estimated_seconds,'estimated_seconds',True); number(estimated_tokens,'estimated_tokens',True)
    reasons=[]; delta=usage_delta(state)
    if state['status']!='active': reasons.append('phase_'+state['status'])
    if state.get('reassessment_required'): reasons.append('reassessment_required')
    cutoff=min(state['deadline'],state['project_deadline']-state['reserve_seconds'])
    if t+estimated_seconds >= cutoff: reasons.append('time_limit_or_delivery_reserve')
    if state['token_limit'] is not None:
        if delta is None: reasons.append('token_meter_unavailable')
        elif delta['total_tokens']+estimated_tokens+state['token_reserve'] >= state['token_limit']:
            reasons.append('token_limit_or_delivery_reserve')
    return {'allowed':not reasons, 'reasons':reasons, 'status':state['status'],
        'stage':state['stage'], 'seconds_to_work_cutoff':max(0,cutoff-t),
        'usage':delta,'token_meter_verified':state['meter']['verified'],
        'host_goal_state':'not_modified', 'scientific_completion_verified':False}

def enforce(state, **kwargs):
    result=guard(state,**kwargs)
    # An estimate that does not fit blocks that action; it does not exhaust the phase.
    current=guard(state,clock=kwargs.get('clock'))
    if state['status']=='active' and any(x.startswith(('time_limit','token_limit')) for x in current['reasons']):
        state['status']='closed_limit'; state['exit_reason']=current['reasons']
        state['history'].append({'at':iso(now()),'event':'closed_limit','reasons':current['reasons']})
    return result

def set_meter(state, sample, source):
    values={k:sample.get(k) for k in ('input_tokens','cached_input_tokens','output_tokens')}
    if any(type(v) is not int or v<0 for v in values.values()) or values['cached_input_tokens']>values['input_tokens']:
        raise PhaseError('Invalid actual usage sample')
    m=state['meter']
    if m['source'] not in {None,source}: raise PhaseError('Usage source changed; preserve the original baseline')
    if m['latest'] and any(values[k]<m['latest'][k] for k in values): raise PhaseError('Usage counter decreased')
    if m['baseline'] is None: m['baseline']=dict(values)
    m.update(verified=True,latest=values,source=source,observed_at=iso(now()))
    return usage_delta(state)

def meter_rollout(state, path):
    p=Path(path).resolve(); m=state['meter']; identity=str(p)
    if m.get('rollout_path') not in {None,identity}: raise PhaseError('Rollout changed')
    offset=m.get('offset',0)
    if p.stat().st_size<offset: raise PhaseError('Rollout truncated; usage cannot be verified')
    sample=None
    with p.open('rb') as f:
        f.seek(offset)
        while True:
            pos=f.tell(); line=f.readline()
            if not line: break
            if not line.endswith(b'\n'): f.seek(pos); break
            d=json.loads(line); payload=d.get('payload',{})
            if d.get('type')=='token_usage_record': sample=payload.get('thread_token_usage',sample)
        end=f.tell()
    if sample is not None: set_meter(state,sample,identity)
    m.update(rollout_path=identity,offset=end)
    return usage_delta(state)

def authorize(state, minutes, authority, token_limit=None, clock=None):
    if not authority.strip(): raise PhaseError('Record actual user authorization; this field does not grant it')
    if state['owned_processes']: raise PhaseError('Finish owned work before authorizing a new budget')
    if state['status']!='awaiting_budget': raise PhaseError('Only a completed feasibility phase can receive the planned budget')
    duration=number(minutes,'minutes')*60; t=now() if clock is None else clock
    if token_limit is not None:
        number(token_limit,'token_limit')
        if not state['meter']['verified']: raise PhaseError('Cannot promise a token ceiling without an actual meter')
        state['history'].append({'at':iso(t),'event':'feasibility_usage','usage':usage_delta(state),
            'meter_baseline':dict(state['meter']['baseline'])})
        state['meter']['baseline']=dict(state['meter']['latest'])
    state.update(status='active',stage='design',project_deadline=t+duration,deadline=t+duration,
        reserve_seconds=min(300,duration*.1),budget_kind='authorized_research',authorization=authority,
        token_limit=token_limit,token_reserve=min(2000,token_limit*.05) if token_limit else 0,stage_started_at=iso(t))
    state['history'].append({'at':iso(t),'event':'authorized_budget','minutes':minutes,'token_limit':token_limit})

def advance(state, stage, evidence, root, next_action, clock=None, minutes=None, skip_reason=None):
    if state['owned_processes']: raise PhaseError('Owned work must finish before transition')
    if not guard(state,clock=clock)['allowed']: raise PhaseError('Phase is not eligible to advance')
    ref=artifact(evidence,root)
    current=state['stage']
    t=now() if clock is None else clock
    if minutes is not None:number(minutes,'stage minutes')
    if skip_reason is not None and not (current=='design' and stage=='manuscript' and skip_reason.strip()):
        raise PhaseError('Only sufficient existing evidence can bypass new research from design to manuscript')
    if current=='feasibility':
        if stage!='design': raise PhaseError('Feasibility precedes design')
        if state.get('budget_kind')=='authorized_total':state['stage']=stage
        else:state['status']='awaiting_budget'
    else:
        evidence_sufficient=current=='design' and stage=='manuscript' and isinstance(skip_reason,str) and bool(skip_reason.strip())
        if not evidence_sufficient and (current not in STAGES or stage not in STAGES or STAGES.index(stage)!=STAGES.index(current)+1):
            raise PhaseError('Use the next stage; focused tasks do not acquire full-research stages')
        state['stage']=stage
    if state['status']=='active':
        state['deadline']=min(state['project_deadline'],t+number(minutes,'stage minutes')*60) if minutes is not None else state['project_deadline']
        state['stage_started_at']=iso(t)
    state['artifacts'].append(ref);state['next_action']=next_action
    state['history'].append({'at':iso(t),'event':'stage_exit','stage':current,'evidence':ref,'skip_reason':skip_reason})
    # Neither stage transitions nor retries reset project_deadline or token baseline.

def repair(state, blocker, approach):
    if not guard(state)['allowed']: raise PhaseError('No new repairs in a stopped phase')
    if not blocker.strip() or not approach.strip(): raise PhaseError('Specify blocker and materially different repair')
    attempts=state['repairs'].setdefault(blocker,[])
    if approach in attempts: raise PhaseError('Duplicate repair does not justify another attempt')
    if len(attempts)>=2: raise PhaseError('Repair limit reached: reassess or close this route')
    attempts.append(approach)

def round_result(state, changed, evidence, root):
    if not guard(state)['allowed']: raise PhaseError('No new research round in a stopped phase')
    ref=artifact(evidence,root)
    state['unchanged_rounds']=0 if changed else state['unchanged_rounds']+1
    state['reassessment_required']=state['unchanged_rounds']>=2
    state['artifacts'].append(ref)

def resume(state):
    return {k:state.get(k) for k in ('scope','objective','latest_instruction','stage','status',
        'project_deadline','deadline','authorization','completed_tasks','artifacts','next_action',
        'exit_reason','repairs','unchanged_rounds','reassessment_required','owned_processes','host_goal_state',
        'budget_kind','reserve_seconds','token_limit','token_reserve','meter','professional_steps',
        'professional_pending','stage_started_at')}

def register_professional(state, begun, started):
    context=begun.get('phase')
    if not context or any(context.get(k)!=state.get(k) for k in ('id','stage','latest_instruction')):
        raise PhaseError('Professional begin belongs to another phase or instruction')
    if not guard(state)['allowed']:raise PhaseError('No professional start in a stopped phase')
    if any(x['step_id']==begun['id'] for x in state.get('professional_pending',[])):
        raise PhaseError('Professional step is already registered; resume it')
    for x in state.get('professional_pending',[]):
        if x['status']!='cancelled' and x['stage']==state['stage'] and x['latest_instruction']==state['latest_instruction'] and x['capability']==begun['capability'] and x.get('task')==begun['task'] and x.get('inputs')==begun['inputs']:
            raise PhaseError('This professional task already has a current receipt; resume/check '+x['started'])
    state.setdefault('professional_pending',[]).append({'step_id':begun['id'],'capability':begun['capability'],
        'stage':state['stage'],'latest_instruction':state['latest_instruction'],'status':'started',
        'started':str(Path(started).resolve()),'finished':None,'task':begun['task'],'inputs':begun['inputs']})

def register_completion(state, begun, finished):
    if state.get('professional_pending') is None:return # Legacy records remain unknown.
    matches=[x for x in state['professional_pending'] if x['step_id']==begun['id']]
    if len(matches)!=1 or matches[0]['status'] not in {'started','completed'}:
        raise PhaseError('No registered current professional step')
    if matches[0].get('finished') and matches[0]['finished']!=str(Path(finished).resolve()):
        raise PhaseError('Professional completion already exists; check it')
    matches[0].update(status='completed',finished=str(Path(finished).resolve()))

def professional_exit(state, starts, finishes):
    """Check current step artifacts before the CLI records a research stage exit."""
    if state['scope']=='maintenance':return []
    if len(starts)!=len(finishes):raise PhaseError('Every professional step needs its begin/finish pair before this exit')
    import capabilities as C
    import professional_flow as F
    index=load(C.index_path());checked=[]
    if not starts:
        if state['scope']!='full' or state['stage']!='delivery' or 'professional_pending' not in state or any(x['status']!='cancelled' for x in state['professional_pending']):
            raise PhaseError('Every professional step needs its begin/finish pair before this exit')
        prior=[x for x in state.get('professional_steps',[]) if x.get('stage')=='manuscript']
        last_exit=next((x for x in reversed(state['history']) if x.get('event')=='stage_exit'),{})
        if not prior or last_exit.get('stage')!='manuscript':
            raise PhaseError('Delivery needs a verified completed manuscript stage')
        # Delivery may only collect existing artifacts; it must not repeat their professional work.
        for step in prior:
            start=Path(step['started']).resolve();finish=Path(step['finished']).resolve()
            begun_bytes=start.read_bytes();complete_bytes=finish.read_bytes()
            identity={'started_sha256':hashlib.sha256(begun_bytes).hexdigest(),'finished_sha256':hashlib.sha256(complete_bytes).hexdigest()}
            if any(step.get(k)!=v for k,v in identity.items()):
                raise PhaseError('Completed manuscript receipt identity is missing or changed')
            begun=json.loads(begun_bytes);context=begun.get('phase',{})
            if context.get('id')!=state['id'] or context.get('stage')!='manuscript' or context.get('latest_instruction')!=state['latest_instruction']:
                raise PhaseError('Completed manuscript belongs to another phase or instruction')
            result=F.check(index,begun,json.loads(complete_bytes))
            if step!={**result,'stage':'manuscript','started':str(start),'finished':str(finish),**identity}:
                raise PhaseError('Completed manuscript record changed')
        return []
    previous={x['step_id'] for x in state.get('professional_steps',[])}
    for start,finish in zip(starts,finishes):
        start=Path(start).resolve();finish=Path(finish).resolve()
        begun_bytes=start.read_bytes();complete_bytes=finish.read_bytes()
        begun=json.loads(begun_bytes);complete=json.loads(complete_bytes);r=F.check(index,begun,complete)
        context=begun.get('phase')
        if not context or context.get('id')!=state['id'] or context.get('stage')!=state['stage'] or context.get('latest_instruction')!=state['latest_instruction']:
            raise PhaseError('Professional step is not bound to this phase and latest instruction')
        if r['step_id'] in previous:raise PhaseError('A prior stage receipt cannot complete a new stage')
        previous.add(r['step_id'])
        # Supporting work (e.g. exploratory figures in research, reading during
        # writing) is source-gated by its actual capability, not a stage whitelist.
        registered=next((x for x in state.get('professional_pending',[]) if x['step_id']==r['step_id']),None)
        if registered and (registered['started']!=str(Path(start).resolve()) or registered.get('finished') not in {None,str(Path(finish).resolve())}):
            raise PhaseError('Receipt paths differ from the registered professional step')
        checked.append({**r,'stage':state['stage'],'started':str(start),'finished':str(finish),
            'started_sha256':hashlib.sha256(begun_bytes).hexdigest(),'finished_sha256':hashlib.sha256(complete_bytes).hexdigest()})
    if 'professional_pending' in state:
        pending={x['step_id'] for x in state['professional_pending'] if x['stage']==state['stage'] and x['status']!='cancelled'}
        if {x['step_id'] for x in checked}!=pending:
            raise PhaseError('Stage exit omits a registered professional step or includes an unregistered step')
    return checked

def consume_professional(state, steps):
    ids={x['step_id'] for x in steps}
    state.setdefault('professional_steps',[]).extend(steps)
    state['professional_pending']=[x for x in state.get('professional_pending',[]) if x['step_id'] not in ids]

def run(state_path, command, log_path, claim, decision, estimate=0, rollout=None):
    if not command or not claim.strip() or not decision.strip(): raise PhaseError('Command requires its supported claim and decision consequence')
    token=uuid.uuid4().hex
    with locked(state_path):
        state=load(state_path)
        if rollout: meter_rollout(state,rollout)
        if state['owned_processes']: raise PhaseError('Another phase-owned runner exists; inspect it, do not restart')
        result=enforce(state,estimated_seconds=estimate);save(state_path,state)
        if not result['allowed']: raise PhaseError('Work blocked: '+','.join(result['reasons']))
        log=Path(log_path);log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('ab') as output:
            child=subprocess.Popen(command,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        state['owned_processes']=[{'pid':child.pid,'runner_token':token,'command':command,'log':str(log)}]
        save(state_path,state)
    stopped=None
    previous_handler=signal.getsignal(signal.SIGTERM)
    def interrupted(signum, frame):
        raise KeyboardInterrupt('runner terminated')
    signal.signal(signal.SIGTERM,interrupted)
    try:
        while child.poll() is None:
            with locked(state_path):
                state=load(state_path)
                if rollout: meter_rollout(state,rollout)
                g=enforce(state);save(state_path,state)
            if not g['allowed']:
                stopped=g['reasons'];break
            time.sleep(.2)
    finally:
        if child.poll() is None:
            # child is this runner's Popen, not a PID supplied by the state file.
            os.killpg(child.pid,signal.SIGTERM)
            try:child.wait(timeout=2)
            except subprocess.TimeoutExpired:os.killpg(child.pid,signal.SIGKILL);child.wait()
        else: child.wait()
        # Also clean descendants when the leader exits first.
        try:os.killpg(child.pid,signal.SIGTERM)
        except ProcessLookupError:pass
        # An exited group leader can leave descendants that ignore SIGTERM.
        try:
            os.killpg(child.pid,0)
        except ProcessLookupError:pass
        else:
            time.sleep(.1)
            try:os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        with locked(state_path):
            state=load(state_path)
            state['owned_processes']=[p for p in state['owned_processes'] if p['runner_token']!=token]
            state['history'].append({'at':iso(now()),'event':'command_finished','command':command,
                'returncode':child.returncode,'claim':claim,'decision':decision,'stop_reasons':stopped})
            save(state_path,state)
        signal.signal(signal.SIGTERM,previous_handler)
    return {'returncode':child.returncode,'stop_reasons':stopped,'log':str(log),'host_goal_state':'not_modified'}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--state',required=True)
    sub=ap.add_subparsers(dest='op',required=True)
    a=sub.add_parser('init');a.add_argument('--scope',choices=['full','focused','maintenance'],required=True);a.add_argument('--objective',required=True);a.add_argument('--minutes',type=float);a.add_argument('--authority');a.add_argument('--token-limit',type=int);a.add_argument('--rollout')
    a=sub.add_parser('guard');a.add_argument('--estimated-seconds',type=float,default=0);a.add_argument('--estimated-tokens',type=int,default=0)
    sub.add_parser('resume')
    a=sub.add_parser('meter');a.add_argument('--rollout',required=True)
    a=sub.add_parser('authorize');a.add_argument('--minutes',type=float,required=True);a.add_argument('--authority',required=True);a.add_argument('--token-limit',type=int)
    a=sub.add_parser('advance');a.add_argument('--stage',choices=STAGES,required=True);a.add_argument('--minutes',type=float);a.add_argument('--skip-reason');a.add_argument('--evidence',required=True);a.add_argument('--root',required=True);a.add_argument('--next-action',required=True);a.add_argument('--professional-started',action='append',default=[]);a.add_argument('--professional-finished',action='append',default=[])
    a=sub.add_parser('repair');a.add_argument('--blocker',required=True);a.add_argument('--approach',required=True)
    a=sub.add_parser('round');a.add_argument('--changed',action='store_true');a.add_argument('--evidence',required=True);a.add_argument('--root',required=True)
    a=sub.add_parser('reassess');a.add_argument('--evidence',required=True);a.add_argument('--root',required=True);a.add_argument('--next-action',required=True)
    a=sub.add_parser('instruction');a.add_argument('--text',required=True)
    a=sub.add_parser('continue');a.add_argument('--authority',required=True)
    a=sub.add_parser('cancel-step');a.add_argument('--started',required=True);a.add_argument('--reason',required=True);a.add_argument('--evidence',required=True);a.add_argument('--root',required=True)
    a=sub.add_parser('close');a.add_argument('--status',choices=['completed','route_closed','paused'],required=True);a.add_argument('--reason',required=True);a.add_argument('--evidence',required=True);a.add_argument('--root',required=True);a.add_argument('--task-id',required=True);a.add_argument('--professional-started',action='append',default=[]);a.add_argument('--professional-finished',action='append',default=[])
    a=sub.add_parser('run');a.add_argument('--log',required=True);a.add_argument('--claim',required=True);a.add_argument('--decision',required=True);a.add_argument('--estimated-seconds',type=float,default=0);a.add_argument('--rollout');a.add_argument('--professional-started');a.add_argument('command',nargs=argparse.REMAINDER)
    args=ap.parse_args(argv)
    try:
        if args.op=='run':
            state=load(args.state)
            if state['scope']!='maintenance':
                if not args.professional_started:raise PhaseError('Research command needs its source-first professional begin receipt')
                import professional_flow as F
                import capabilities as C
                started=load(args.professional_started);F.validate_start(load(C.index_path()),started)
                context=started.get('phase')
                if not context or context['path']!=str(Path(args.state).resolve()) or context['id']!=state['id']:
                    raise PhaseError('Professional begin belongs to another phase')
            cmd=args.command[1:] if args.command[:1]==['--'] else args.command
            result=run(args.state,cmd,args.log,args.claim,args.decision,args.estimated_seconds,args.rollout)
            print(json.dumps(result,ensure_ascii=False));return 0 if not result['stop_reasons'] and result['returncode']==0 else 2
        with locked(args.state):
            if args.op=='init':
                if Path(args.state).exists(): raise PhaseError('State already exists; resume without resetting budgets')
                if args.authority is not None and not args.authority.strip():raise PhaseError('Empty authorization')
                state=init(args.scope,args.objective,args.minutes,authority=args.authority)
                if args.rollout:meter_rollout(state,args.rollout)
                if args.token_limit is not None:
                    if not args.authority or not state['meter']['verified']:raise PhaseError('An initial total token ceiling requires actual authorization and rollout meter')
                    number(args.token_limit,'token_limit');state.update(token_limit=args.token_limit,token_reserve=min(2000,args.token_limit*.05))
            else:
                state=load(args.state)
                if state.get('schema_version')!='research-phase-1': raise PhaseError('Legacy phase unknown; retain it and establish an explicit phase')
                if args.op=='guard':result=enforce(state,estimated_seconds=args.estimated_seconds,estimated_tokens=args.estimated_tokens)
                elif args.op=='meter':meter_rollout(state,args.rollout);enforce(state)
                elif args.op=='authorize':authorize(state,args.minutes,args.authority,args.token_limit)
                elif args.op=='advance':
                    steps=professional_exit(state,args.professional_started,args.professional_finished)
                    advance(state,args.stage,args.evidence,args.root,args.next_action,minutes=args.minutes,skip_reason=args.skip_reason)
                    consume_professional(state,steps)
                elif args.op=='repair':repair(state,args.blocker,args.approach)
                elif args.op=='round':round_result(state,args.changed,args.evidence,args.root)
                elif args.op=='instruction':state['latest_instruction']=args.text
                elif args.op=='continue':
                    if state['status']!='paused' or not args.authority.strip():raise PhaseError('Only an explicitly resumed paused phase can continue')
                    state['status']='active'
                    if not guard(state)['allowed']:raise PhaseError('Original budget has expired; continuation cannot renew it')
                    state['history'].append({'at':iso(now()),'event':'user_continued','authority':args.authority})
                elif args.op=='cancel-step':
                    begun=load(args.started);context=begun.get('phase',{})
                    pending=[x for x in state.get('professional_pending',[]) if x['step_id']==begun.get('id')]
                    if len(pending)!=1 or context.get('id')!=state['id'] or not args.reason.strip():raise PhaseError('Cancellation needs its own registered step and actual reason')
                    if pending[0]['status']=='cancelled':raise PhaseError('Step is already cancelled')
                    ref=artifact(args.evidence,args.root)
                    pending[0].update(status='cancelled',reason=args.reason,evidence=ref)
                    state['history'].append({'at':iso(now()),'event':'professional_cancelled',**pending[0]})
                elif args.op=='reassess':
                    if state['status']!='active' or not state['reassessment_required']:raise PhaseError('No active reassessment pending')
                    state['artifacts'].append(artifact(args.evidence,args.root));state['reassessment_required']=False;state['unchanged_rounds']=0;state['next_action']=args.next_action
                elif args.op=='close':
                    if state['owned_processes'] and args.status=='completed':raise PhaseError('Cannot complete with owned work still running')
                    if args.status=='completed' and state['scope']!='maintenance' and state['status']!='active':raise PhaseError('Stopped research cannot be marked newly completed')
                    if args.status=='completed' and state['scope']!='maintenance':
                        delta=usage_delta(state)
                        if now()>=state['project_deadline'] or (state['token_limit'] is not None and delta is not None and delta['total_tokens']>=state['token_limit']):
                            state.update(status='closed_limit',exit_reason=['Completion exceeded the actual total budget'])
                            save(args.state,state)
                            raise PhaseError('Total budget expired; deliver the saved scope and limit instead of a new completed state')
                    if args.status=='completed':
                        steps=professional_exit(state,args.professional_started,args.professional_finished)
                        consume_professional(state,steps)
                    ref=artifact(args.evidence,args.root)
                    if args.status=='completed' and args.task_id not in state['completed_tasks']:state['completed_tasks'].append(args.task_id)
                    state.update(status=args.status,exit_reason=args.reason);state['artifacts'].append(ref)
            if args.op=='resume':result={**resume(state),'guard':guard(state)}
            elif args.op!='guard':result={'status':state['status'],'stage':state['stage'],'usage':usage_delta(state),'host_goal_state':'not_modified'}
            if args.op!='resume':save(args.state,state)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 2 if result.get('allowed') is False or (args.op=='resume' and result['guard']['allowed'] is False) else 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'status':'needs_attention','error':str(e)},ensure_ascii=False),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
