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

def request_anchor(path, message=None):
    """Select the actual grant, never silently pick an old request in a long chat."""
    requests=[]
    with Path(path).open(encoding='utf-8') as f:
        for line in f:
            d=json.loads(line);p=d.get('payload',{})
            if d.get('type')=='event_msg' and p.get('type')=='user_message':
                if message is None or p.get('message')==message:
                    stamp=datetime.fromisoformat(d['timestamp'].replace('Z','+00:00'))
                    if stamp.tzinfo is None:raise PhaseError('Request timestamp needs an explicit timezone')
                    requests.append(stamp.timestamp())
    if len(requests)!=1:
        raise PhaseError('Budget request missing or ambiguous; select its exact --request-message or verified --started-at from the actual log')
    return requests[0]

def init(scope, objective, minutes=None, clock=None, authority=None, started_at=None, anchor_basis=None, autonomous_plan=False):
    if scope not in {'full','focused','maintenance'} or not objective.strip(): raise PhaseError('Invalid scope/objective')
    if authority is not None and (not isinstance(authority,str) or not authority.strip() or minutes is None):
        raise PhaseError('A supplied total budget needs minutes and actual user authorization')
    t=now() if clock is None else clock
    anchor=t if started_at is None else number(started_at,'started_at',True)
    if anchor>t:raise PhaseError('The budget cannot start in the future')
    duration=number(45 if minutes is None else minutes,'minutes')*60
    return {'schema_version':'research-phase-1', 'id':uuid.uuid4().hex,
        'scope':scope, 'objective':objective, 'latest_instruction':objective,
        'status':'active', 'stage':'feasibility' if scope=='full' else scope,
        'started_at':iso(anchor), 'deadline':anchor+duration, 'project_deadline':anchor+duration,
        'workflow_version':'3.5.3', 'budget_anchor':{'started_at':iso(anchor),
            'basis':anchor_basis or 'controller_initialization_only','verified':started_at is not None},
        'reserve_seconds':min(300,duration*.1),'reserve_authority':'agent', 'budget_kind':'authorized_total' if authority else 'initial_feasibility' if scope=='full' else 'local_task',
        'authorization':authority, 'token_limit':None, 'token_reserve':0,'token_metric':'input_plus_output','token_reserve_authority':'agent',
        'budget_authority':'user' if authority else 'agent' if autonomous_plan else 'legacy',
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

def guard(state, estimated_seconds=0, estimated_tokens=0, clock=None, storage=False, estimated_bytes=0, transfer_bytes=0):
    t=now() if clock is None else clock
    number(estimated_seconds,'estimated_seconds',True); number(estimated_tokens,'estimated_tokens',True)
    reasons=[]; delta=usage_delta(state)
    capacity=None
    if storage and not state.get('storage') and (estimated_bytes or transfer_bytes):reasons.append('storage_plan_required')
    if storage and state.get('storage'):
        import research_storage as S
        try:
            identity=S.read(state['storage']['root'])
            if identity['id']!=state['storage']['id']:raise S.StorageError('Storage receipt changed')
            capacity=S.check(state['storage']['root'],identity,extra=estimated_bytes,transfer=transfer_bytes)
            reasons.extend(capacity['reasons'])
        except (ValueError,OSError,KeyError):reasons.append('storage_plan_needs_recovery')
    if state['status']!='active': reasons.append('phase_'+state['status'])
    if state.get('reassessment_required'): reasons.append('reassessment_required')
    # A controller default is a planning horizon, never a fabricated user limit.
    total_cutoff=float('inf') if state.get('budget_authority')=='agent' else state['project_deadline']-state['reserve_seconds']
    cutoff=min(state['deadline'],total_cutoff)
    if t+estimated_seconds >= total_cutoff: reasons.append('time_limit_or_delivery_reserve')
    elif t+estimated_seconds >= state['deadline']: reasons.append('stage_reassessment_required')
    if state['token_limit'] is not None:
        if delta is None: reasons.append('token_meter_unavailable')
        elif state.get('budget_anchor',{}).get('verified') and state['meter'].get('coverage')!='budget_anchor':
            reasons.append('initial_token_coverage_unknown')
        elif token_spent(state,delta)+estimated_tokens+state['token_reserve'] >= state['token_limit']:
            reasons.append('token_limit_or_delivery_reserve')
    action='continue_current_work'
    if state['status']!='active':action='deliver_or_follow_actual_user_resume; do_not_restart'
    elif 'initial_token_coverage_unknown' in reasons or 'token_meter_unavailable' in reasons:action='repair_actual_meter_without_resetting_baseline'
    elif any(x.startswith(('time_limit','token_limit')) for x in reasons):
        expired=(state.get('budget_authority')!='agent' and t>=state['project_deadline']) or (state['token_limit'] is not None and delta is not None and token_spent(state,delta)>=state['token_limit'])
        action='deliver_actual_total_limit' if expired else 'reassess_agent_reserve_or_choose_smaller_action; preserve_actual_total_budget'
    elif 'reassessment_required' in reasons or 'stage_reassessment_required' in reasons:action='diagnose_and_reassess_stage_with_evidence; continue_autonomously'
    elif 'storage_plan_required' in reasons or 'storage_plan_needs_recovery' in reasons:action='plan_or_recover_project_capacity_before_acquisition'
    elif capacity and not capacity['allowed']:action='repair_acquisition_plan_or_use_valid_smaller_subset'
    return {'allowed':not reasons, 'reasons':reasons, 'status':state['status'],'required_next_action':action,
        'stage':state['stage'], 'seconds_to_work_cutoff':max(0,cutoff-t),
        'usage':delta,'token_metric':state.get('token_metric','input_plus_output'),'token_meter_verified':state['meter']['verified'],
        'token_budget_coverage':state['meter'].get('coverage','unknown'),
        'strict_token_budget_verified':bool(delta is not None and state['meter']['verified'] and state.get('budget_anchor',{}).get('verified') and state['meter'].get('coverage')=='budget_anchor'),
        'host_goal_state':'not_modified', 'scientific_completion_verified':False, **({'storage':capacity} if storage else {})}

def enforce(state, **kwargs):
    result=guard(state,**kwargs)
    # An estimate that does not fit blocks that action; it does not exhaust the phase.
    current=guard(state,clock=kwargs.get('clock'))
    if state['status']=='active' and any(x.startswith(('time_limit','token_limit')) for x in current['reasons']):
        t=now() if kwargs.get('clock') is None else kwargs['clock'];delta=usage_delta(state)
        actual_expired=(state.get('budget_authority')!='agent' and t>=state['project_deadline']) or (state['token_limit'] is not None and delta is not None and token_spent(state,delta)>=state['token_limit'])
        if actual_expired or state.get('reserve_authority')!='agent' or state.get('budget_authority')=='legacy':
            state['status']='closed_limit'; state['exit_reason']=current['reasons']
            state['history'].append({'at':iso(t),'event':'closed_limit','reasons':current['reasons']})
        else:
            # Stop this action for reallocation or delivery, not the whole goal.
            state['delivery_required']=True
    elif state['status']=='active' and 'stage_reassessment_required' in current['reasons']:
        state['reassessment_required']=True
    result.update(status=state['status'],delivery_required=state.get('delivery_required',False))
    if state['status']=='closed_limit':result['required_next_action']='deliver_preserved_limit_no_new_work'
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
    sample=None;prior=None
    anchor=state.get('budget_anchor',{})
    anchor_time=datetime.fromisoformat(anchor['started_at']).timestamp() if anchor.get('verified') else None
    with p.open('rb') as f:
        f.seek(offset)
        while True:
            pos=f.tell(); line=f.readline()
            if not line: break
            if not line.endswith(b'\n'): f.seek(pos); break
            d=json.loads(line); payload=d.get('payload',{})
            if d.get('type')=='token_usage_record':
                sample=payload.get('thread_token_usage',sample)
                stamp=d.get('timestamp')
                if offset==0 and anchor_time is not None and stamp and datetime.fromisoformat(stamp.replace('Z','+00:00')).timestamp()<=anchor_time:
                    prior=sample
        end=f.tell()
    if sample is not None:
        if m['baseline'] is None:
            if prior is not None:set_meter(state,prior,identity)
            m['coverage']='budget_anchor' if prior is not None else 'since_first_sample'
        set_meter(state,sample,identity)
    m.update(rollout_path=identity,offset=end)
    return usage_delta(state)

def token_spent(state, delta):
    metric=state.get('token_metric','input_plus_output')
    if metric not in {'input_plus_output','noncached_input_plus_output'}:raise PhaseError('Unknown budget token metric')
    return delta['total_tokens'] if metric=='input_plus_output' else delta[metric]

def authorize(state, minutes, authority, token_limit=None, clock=None, token_metric=None):
    if token_metric is not None and token_metric not in {'input_plus_output','noncached_input_plus_output'}:
        raise PhaseError('Unknown token budget metric')
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
        budget_authority='user',budget_anchor={'basis':'controller_authorization_receipt_only','started_at':iso(t),'verified':False},
        token_limit=token_limit,token_reserve=min(2000,token_limit*.05) if token_limit else 0,stage_started_at=iso(t))
    state['history'].append({'at':iso(t),'event':'authorized_budget','minutes':minutes,'token_limit':token_limit})
    if token_metric is not None:
        state['token_metric']=token_metric

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
        if state.get('budget_kind')=='authorized_total' or state.get('budget_authority')=='agent':state['stage']=stage
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
    reviewed=next((x.get('repair_count',0) for x in reversed(state['history'])
        if x.get('event')=='reassessment' and x.get('blocker')==blocker),0)
    if len(attempts)-reviewed>=2: raise PhaseError('Two repairs tried: diagnose alternatives and record reassess --blocker before another distinct attempt')
    attempts.append(approach)

def reassess(state, evidence, root, next_action, blocker=None, minutes=None, stage=None, authority=None, clock=None, reserve_seconds=None, token_reserve=None):
    """Review a recoverable obstacle without renewing the user's total budget.

    Evidence must explain the diagnosis, alternatives and chosen next test. This
    tool validates the receipt and bounds; it cannot judge its scientific merits.
    """
    if state['status'] not in {'active','route_closed'}:
        raise PhaseError('Reassessment cannot override completion, a total limit, a user pause or an unapproved budget')
    if state['status']=='route_closed' and (not isinstance(authority,str) or not authority.strip()):
        raise PhaseError('A closed route needs actual user continuation; the authority field does not grant it')
    if authority is not None and (not isinstance(authority,str) or not authority.strip()):
        raise PhaseError('Record actual continuation, not an empty authority')
    if state['owned_processes']:raise PhaseError('Finish or checkpoint owned work before reassessment')
    if not isinstance(next_action,str) or not next_action.strip():raise PhaseError('Specify the actual next validation action')
    if blocker is not None and blocker not in state['repairs']:raise PhaseError('Reassess the recorded blocker; do not rename it to reset attempts')
    current=state['stage'];steps=[]
    if stage is not None:
        if state['scope']!='full' or current not in STAGES or stage not in STAGES or STAGES.index(stage)>STAGES.index(current):
            raise PhaseError('Reassessment may return to an earlier full-research stage; it cannot skip forward or expand a focused task')
        if stage!=current:
            pending=[x for x in state.get('professional_pending',[]) if x['status']!='cancelled']
            if any(x['status']!='completed' or x.get('stage')!=current or not x.get('finished') for x in pending):
                raise PhaseError('Finish or explicitly cancel current professional steps before changing stage')
            if pending:steps=professional_exit(state,[x['started'] for x in pending],[x['finished'] for x in pending])
    ref=artifact(evidence,root);t=now() if clock is None else clock
    candidate=dict(state);candidate.update(status='active',reassessment_required=False,unchanged_rounds=0,next_action=next_action)
    if reserve_seconds is not None:
        number(reserve_seconds,'reserve_seconds',True)
        if state.get('reserve_authority')!='agent':raise PhaseError('Cannot change a user or unknown delivery reserve')
        candidate['reserve_seconds']=reserve_seconds;candidate['delivery_required']=False
    if minutes is not None:
        planned=t+number(minutes,'stage minutes')*60
        if state.get('budget_authority')=='agent':candidate['project_deadline']=max(state['project_deadline'],planned)
        candidate['deadline']=min(candidate['project_deadline'],planned)
    if reserve_seconds is not None and reserve_seconds>=max(0,candidate['project_deadline']-t):raise PhaseError('Reserve must fit the remaining actual budget')
    if token_reserve is not None:
        number(token_reserve,'token_reserve',True)
        if state.get('token_reserve_authority')!='agent':raise PhaseError('Cannot change a user or unknown token reserve')
        candidate['token_reserve']=token_reserve;candidate['delivery_required']=False
    if stage is not None:candidate.update(stage=stage,stage_started_at=iso(t))
    if not guard(candidate,clock=t)['allowed']:
        raise PhaseError('Original budget does not permit this action; reallocate a stage within it or report the actual total limit')
    event={'at':iso(t),'event':'reassessment','evidence':ref,'next_action':next_action,
        'previous_status':state['status'],'previous_exit_reason':state.get('exit_reason'),
        'previous_stage':current,'stage':candidate['stage'],'previous_deadline':state['deadline'],
        'deadline':candidate['deadline'],'authority':authority,
        'previous_reserve_seconds':state['reserve_seconds'],'reserve_seconds':candidate['reserve_seconds'],
        'previous_token_reserve':state['token_reserve'],'token_reserve':candidate['token_reserve'],
        'professional_steps':[x['step_id'] for x in steps]}
    if blocker is not None:event.update(blocker=blocker,repair_count=len(state['repairs'][blocker]))
    candidate.pop('exit_reason',None)
    state.clear();state.update(candidate)
    if steps:consume_professional(state,steps)
    state['artifacts'].append(ref);state['history'].append(event)

def round_result(state, changed, evidence, root):
    if not guard(state)['allowed']: raise PhaseError('No new research round in a stopped phase')
    ref=artifact(evidence,root)
    state['unchanged_rounds']=0 if changed else state['unchanged_rounds']+1
    state['reassessment_required']=state['unchanged_rounds']>=2
    state['artifacts'].append(ref)

def resume(state, compact=False):
    result={k:state.get(k) for k in ('scope','objective','latest_instruction','stage','status',
        'project_deadline','deadline','authorization','completed_tasks','artifacts','next_action',
        'exit_reason','repairs','unchanged_rounds','reassessment_required','owned_processes','host_goal_state',
        'budget_kind','reserve_seconds','token_limit','token_reserve','token_metric','meter','professional_steps',
        'professional_pending','stage_started_at','storage','budget_anchor','workflow_version','current_unit','budget_authority','reserve_authority','token_reserve_authority','delivery_required')}
    if compact:
        for key in ('artifacts','completed_tasks','professional_steps'):
            rows=result.get(key) or [];result[key+'_count']=len(rows);result[key]=rows[-3:]
        pending=result.get('professional_pending') or []
        started=[x for x in pending if x['status']=='started']
        completed=[x for x in pending if x['status']=='completed']
        result['professional_pending_count']=len(started)
        result['professional_completed_unconsumed_count']=len(completed)
        result['professional_pending']=[{k:x.get(k) for k in ('step_id','capability','stage','status','started','finished')} for x in started[:3]]
        result['professional_completed_unconsumed']=[{k:x.get(k) for k in ('step_id','capability','stage','started','finished')} for x in completed[-3:]]
        result['current_work']=state.get('work_units',{}).get(state.get('current_unit'))
        routes=list(state.get('routes',{}).values())
        result['ready_routes']=[x for x in routes if x['status'] in {'ready','testing'}][:3]
        result['route_counts']={k:sum(x['status']==k for x in routes) for k in ('ready','testing','failed','useful','external_dependency')}
        result['resource_plans']=state.get('resource_plans',{})
        result['process_observations']=[process_observation(p) for p in state.get('owned_processes',[])]
        result['repairs']={k:{'attempt_count':len(v),'latest':v[-2:]} for k,v in (result.get('repairs') or {}).items()}
        result['details']='Read the phase state only for relevant older artifacts, failures or receipts; this snapshot never replaces the complete record.'
    return result

def process_observation(record):
    """PID existence is not ownership or success. Never kill a PID from a receipt."""
    pid=record.get('pid')
    if type(pid) is not int or pid<=0:return {'pid':pid,'state':'unknown'}
    try:os.kill(pid,0)
    except ProcessLookupError:
        try:os.killpg(pid,0)
        except ProcessLookupError:return {'pid':pid,'state':'absent','runner_token':record.get('runner_token')}
        except PermissionError:pass
        return {'pid':pid,'state':'group_requires_inspection'}
    except PermissionError:return {'pid':pid,'state':'unknown'}
    return {'pid':pid,'state':'exists_ownership_unverified'}

def reconcile_processes(state):
    removed=[];kept=[]
    for record in state['owned_processes']:
        observed=process_observation(record)
        if observed['state']=='absent':removed.append(record)
        else:kept.append(record)
    state['owned_processes']=kept
    if removed:state['history'].append({'event':'absent_process_reconciled','at':iso(now()),
        'records':removed,'success_verified':False,'next':'Inspect actual log/output; resume the unfinished step rather than repeat completed work'})
    return {'removed':len(removed),'remaining':[process_observation(p) for p in kept],'success_verified':False}

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
        result=enforce(state,estimated_seconds=estimate,storage=True);save(state_path,state)
        if not result['allowed']: raise PhaseError('Work blocked: '+','.join(result['reasons']))
        log=Path(log_path);log.parent.mkdir(parents=True,exist_ok=True)
        with log.open('ab') as output:
            child=subprocess.Popen(command,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        state['owned_processes']=[{'pid':child.pid,'runner_token':token,'command':command,'log':str(log)}]
        save(state_path,state)
    stopped=None;last_storage_check=0
    previous_handler=signal.getsignal(signal.SIGTERM)
    def interrupted(signum, frame):
        raise KeyboardInterrupt('runner terminated')
    signal.signal(signal.SIGTERM,interrupted)
    try:
        while child.poll() is None:
            with locked(state_path):
                state=load(state_path)
                if rollout: meter_rollout(state,rollout)
                inspect_storage=time.monotonic()-last_storage_check>=2
                g=enforce(state,storage=inspect_storage);save(state_path,state)
                if inspect_storage:last_storage_check=time.monotonic()
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
    a=sub.add_parser('init');a.add_argument('--scope',choices=['full','focused','maintenance'],required=True);a.add_argument('--objective',required=True);a.add_argument('--minutes',type=float);a.add_argument('--authority');a.add_argument('--token-limit',type=int);a.add_argument('--rollout');a.add_argument('--started-at',help='Verified ISO timestamp of the actual budget-granting request');a.add_argument('--request-rollout',help='Actual rollout containing the budget-granting user request');a.add_argument('--request-message',help='Exact actual budget-granting message when the rollout contains multiple user requests');a.add_argument('--require-budget',action='store_true',help='Use only when the user explicitly requires budget approval after feasibility')
    a.add_argument('--token-metric',choices=['input_plus_output','noncached_input_plus_output'],default='input_plus_output',help='Must match the actual user/host budget basis')
    a=sub.add_parser('guard');a.add_argument('--estimated-seconds',type=float,default=0);a.add_argument('--estimated-tokens',type=int,default=0);a.add_argument('--estimated-bytes',type=int,default=0);a.add_argument('--transfer-bytes',type=int,default=0)
    a=sub.add_parser('resume');a.add_argument('--full',action='store_true',help='Return all historical artifacts and professional receipts')
    sub.add_parser('reconcile-processes')
    a=sub.add_parser('storage');a.add_argument('--root',required=True)
    a=sub.add_parser('meter');a.add_argument('--rollout',required=True)
    a=sub.add_parser('authorize');a.add_argument('--minutes',type=float,required=True);a.add_argument('--authority',required=True);a.add_argument('--token-limit',type=int)
    a.add_argument('--token-metric',choices=['input_plus_output','noncached_input_plus_output'])
    a=sub.add_parser('advance');a.add_argument('--stage',choices=STAGES,required=True);a.add_argument('--minutes',type=float);a.add_argument('--skip-reason');a.add_argument('--evidence',required=True);a.add_argument('--root',required=True);a.add_argument('--next-action',required=True);a.add_argument('--professional-started',action='append',default=[]);a.add_argument('--professional-finished',action='append',default=[])
    a=sub.add_parser('repair');a.add_argument('--blocker',required=True);a.add_argument('--approach',required=True)
    a=sub.add_parser('round');a.add_argument('--changed',action='store_true');a.add_argument('--evidence',required=True);a.add_argument('--root',required=True)
    a=sub.add_parser('reassess');a.add_argument('--evidence',required=True);a.add_argument('--root',required=True);a.add_argument('--next-action',required=True);a.add_argument('--blocker');a.add_argument('--minutes',type=float);a.add_argument('--stage',choices=STAGES);a.add_argument('--authority');a.add_argument('--reserve-seconds',type=float)
    a.add_argument('--token-reserve',type=int)
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
                if args.started_at and args.request_rollout:raise PhaseError('Choose one actual budget anchor')
                if args.request_message and not args.request_rollout:raise PhaseError('Request selection needs its actual rollout')
                anchor=datetime.fromisoformat(args.started_at.replace('Z','+00:00')).timestamp() if args.started_at else request_anchor(args.request_rollout,args.request_message) if args.request_rollout else None
                if args.started_at and datetime.fromisoformat(args.started_at.replace('Z','+00:00')).tzinfo is None:raise PhaseError('Budget timestamp needs an explicit timezone')
                state=init(args.scope,args.objective,args.minutes,authority=args.authority,started_at=anchor,
                    anchor_basis='user_request:'+str(Path(args.request_rollout).resolve()) if args.request_rollout else 'verified_user_request_timestamp' if args.started_at else None,autonomous_plan=not args.require_budget)
                if args.rollout:meter_rollout(state,args.rollout)
                if args.token_limit is not None:
                    if not args.authority or not state['meter']['verified']:raise PhaseError('An initial total token ceiling requires actual authorization and rollout meter')
                    number(args.token_limit,'token_limit');state.update(token_limit=args.token_limit,token_reserve=min(2000,args.token_limit*.05))
                state['token_metric']=args.token_metric
            else:
                state=load(args.state)
                if state.get('schema_version')!='research-phase-1': raise PhaseError('Legacy phase unknown; retain it and establish an explicit phase')
                if args.op=='guard':result=enforce(state,estimated_seconds=args.estimated_seconds,estimated_tokens=args.estimated_tokens,storage=True,estimated_bytes=args.estimated_bytes,transfer_bytes=args.transfer_bytes)
                elif args.op=='storage':
                    import research_storage as S
                    root=str(Path(args.root).resolve());receipt=S.read(root)
                    if state.get('storage') and state['storage']!={'root':root,'id':receipt['id']}:raise PhaseError('A new phase cannot replace the original project quota')
                    state['storage']={'root':root,'id':receipt['id']}
                elif args.op=='meter':meter_rollout(state,args.rollout);enforce(state)
                elif args.op=='reconcile-processes':process_result=reconcile_processes(state)
                elif args.op=='authorize':authorize(state,args.minutes,args.authority,args.token_limit,token_metric=args.token_metric)
                elif args.op=='advance':
                    steps=professional_exit(state,args.professional_started,args.professional_finished)
                    advance(state,args.stage,args.evidence,args.root,args.next_action,minutes=args.minutes,skip_reason=args.skip_reason)
                    consume_professional(state,steps)
                elif args.op=='repair':repair(state,args.blocker,args.approach)
                elif args.op=='round':round_result(state,args.changed,args.evidence,args.root)
                elif args.op=='instruction':
                    if not args.text.strip():raise PhaseError('Latest user instruction cannot be empty')
                    if args.text!=state['latest_instruction']:
                        state['history'].append({'event':'instruction_changed','previous':state['latest_instruction'],'at':iso(now())})
                        state['latest_instruction']=args.text;state['next_action']=None;state['current_unit']=None
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
                    reassess(state,args.evidence,args.root,args.next_action,blocker=args.blocker,minutes=args.minutes,stage=args.stage,authority=args.authority,reserve_seconds=args.reserve_seconds,token_reserve=args.token_reserve)
                elif args.op=='close':
                    if args.status=='route_closed' and state.get('workflow_version')=='3.5.3' and state['scope']!='maintenance':
                        import work_units as W
                        W.validate_route_exit(state)
                    if state['owned_processes'] and args.status=='completed':raise PhaseError('Cannot complete with owned work still running')
                    if args.status=='completed' and state['scope']!='maintenance' and state['status']!='active':raise PhaseError('Stopped research cannot be marked newly completed')
                    if args.status=='completed' and state['scope']!='maintenance':
                        delta=usage_delta(state)
                        if (state.get('budget_authority')!='agent' and now()>=state['project_deadline']) or (state['token_limit'] is not None and delta is not None and token_spent(state,delta)>=state['token_limit']):
                            state.update(status='closed_limit',exit_reason=['Completion exceeded the actual total budget'])
                            save(args.state,state)
                            raise PhaseError('Total budget expired; deliver the saved scope and limit instead of a new completed state')
                    if args.status=='completed':
                        steps=professional_exit(state,args.professional_started,args.professional_finished)
                        consume_professional(state,steps)
                    ref=artifact(args.evidence,args.root)
                    if args.status=='completed' and args.task_id not in state['completed_tasks']:state['completed_tasks'].append(args.task_id)
                    state.update(status=args.status,exit_reason=args.reason,next_action=None);state['artifacts'].append(ref)
            if args.op=='resume':result={**resume(state,compact=not args.full),'state_path':str(Path(args.state).resolve()),'guard':guard(state,storage=True)}
            elif args.op!='guard':result={'status':state['status'],'stage':state['stage'],'usage':usage_delta(state),'host_goal_state':'not_modified',**({'processes':process_result} if args.op=='reconcile-processes' else {})}
            if args.op!='resume':save(args.state,state)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 2 if result.get('allowed') is False or (args.op=='resume' and result['guard']['allowed'] is False) else 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'status':'needs_attention','error':str(e)},ensure_ascii=False),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
