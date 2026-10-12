#!/usr/bin/env python3
"""Scientific work checkpoints and content-bound review reuse; no host goal changes.

Plans created by the agent are revisable. User limits and provider constraints
remain external authority; this receipt cannot manufacture permission or evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import phase_control as P

VERSION = '3.5.3'

def refs(paths, root):
    if not paths: raise P.PhaseError('Supply actual nonempty evidence files')
    return sorted([P.artifact(p, root) for p in paths], key=lambda r:r['path'])

def identity(rows):
    return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def checkpoint(state, key, claim, next_action, evidence, root, outcome='working'):
    if state['status']!='active': raise P.PhaseError('Checkpoint cannot resume a terminal phase')
    if not all(isinstance(v,str) and v.strip() for v in (key,claim,next_action)):
        raise P.PhaseError('A work unit needs its scientific claim and actual next action')
    if outcome not in {'working','supported','refuted','inconclusive'}:raise P.PhaseError('Unknown scientific outcome')
    rows=refs(evidence,root)
    units=state.setdefault('work_units',{})
    previous=units.get(key)
    if previous and previous['claim']!=claim:raise P.PhaseError('A changed claim needs a distinct unit, not a rewritten result')
    unit={'key':key,'claim':claim,'stage':state['stage'],'instruction':state['latest_instruction'],
        'outcome':outcome,'evidence':rows,'next_action':next_action,'at':P.iso(P.now())}
    units[key]=unit;state['current_unit']=key;state['next_action']=next_action
    state['history'].append({'event':'work_checkpoint',**unit})
    return unit

def plan(state, key, limit, used, origin, rationale, evidence, root):
    if not P.guard(state)['allowed']:raise P.PhaseError('Replan within the actual budget; reassess an expired stage first')
    if not key.strip() or not rationale.strip():raise P.PhaseError('Describe the resource and scientific reason')
    P.number(limit,'limit');P.number(used,'used',True)
    if origin not in {'agent','user','provider'}:raise P.PhaseError('Unknown limit provenance')
    old=state.setdefault('resource_plans',{}).get(key)
    if old and old['origin']!='agent':raise P.PhaseError('This tool cannot change a user or provider limit')
    if old and origin!='agent':raise P.PhaseError('Do not relabel an agent plan as external authority')
    row={'key':key,'limit':limit,'used':used,'origin':origin,'rationale':rationale,
        'evidence':refs(evidence,root),'at':P.iso(P.now()),'enforced_by_this_tool':False}
    state['resource_plans'][key]=row
    state['history'].append({'event':'resource_plan','previous':old,**row})
    return row

def route(state, key, claim, action, evidence, root, status='ready', estimated_seconds=0):
    if state['status']!='active':raise P.PhaseError('A route does not reopen a stopped task')
    if not all(x.strip() for x in (key,claim,action)):raise P.PhaseError('A route needs the claim and decisive test')
    if status not in {'ready','testing','failed','useful','external_dependency'}:raise P.PhaseError('Unknown route status')
    P.number(estimated_seconds,'estimated_seconds',True)
    row={'key':key,'claim':claim,'action':action,'status':status,'estimated_seconds':estimated_seconds,
        'evidence':refs(evidence,root),'root':str(Path(root).resolve()),'at':P.iso(P.now())}
    state.setdefault('routes',{})[key]=row
    state['history'].append({'event':'route_update',**row})
    if status in {'ready','testing'}:state['next_action']=action
    return row

def validate_route_exit(state):
    rows=list(state.get('routes',{}).values())
    if not rows:raise P.PhaseError('Record actual candidate tests before closing the whole route; a missing-file audit is insufficient')
    if any(x['status'] in {'ready','testing'} for x in rows):
        raise P.PhaseError('A candidate test remains actionable; continue it rather than close the task')
    for row in rows:
        if refs([r['path'] for r in row['evidence']],row['root'])!=row['evidence']:
            raise P.PhaseError('Route evidence changed; reassess the actual obstacle')
    return {'candidate_count':len(rows),'scientific_exhaustion_verified_by_tool':False}

def review_status(state, unit, paths, root):
    rows=refs(paths,root);fingerprint=identity(rows)
    record=state.get('reviews',{}).get(unit)
    if record and record['fingerprint']==fingerprint and record['instruction']==state['latest_instruction']:
        # Recheck both source receipt and content; an edited receipt is not reusable.
        try:
            checked=check_review(record['started'],record['finished'],rows,root,state)
            if checked!=record['receipt']:raise P.PhaseError('Review receipt changed')
        except (ValueError,OSError,KeyError,TypeError):return {'reusable':False,'reason':'review_receipt_changed','fingerprint':fingerprint}
        return {'reusable':True,'fingerprint':fingerprint,'record':record}
    return {'reusable':False,'reason':'new_or_changed_evidence_or_instruction','fingerprint':fingerprint,'evidence':rows}

def check_review(start, finish, rows, root, state):
    import capabilities as C
    import professional_flow as F
    begun=P.load(start);complete=P.load(finish)
    if begun.get('capability') not in {'manuscript-review','robustness-reproducibility','citation-audit'}:
        raise P.PhaseError('A review needs the appropriate source-gated review capability')
    context=begun.get('phase') or {}
    if context.get('id')!=state['id'] or context.get('latest_instruction')!=state['latest_instruction']:
        raise P.PhaseError('Review belongs to another task or instruction')
    inputs={(str(Path(x['path']).resolve()),x['sha256']) for x in begun['inputs']}
    if any((str((Path(root)/r['path']).resolve()),r['sha256']) not in inputs for r in rows):
        raise P.PhaseError('Review must actually consume every file in this review unit')
    checked=F.check(P.load(C.index_path()),begun,complete)
    return {**checked,'started_sha256':hashlib.sha256(Path(start).read_bytes()).hexdigest(),
        'finished_sha256':hashlib.sha256(Path(finish).read_bytes()).hexdigest()}

def review_record(state, unit, paths, root, started, finished):
    rows=refs(paths,root)
    receipt=check_review(started,finished,rows,root,state)
    record={'unit':unit,'fingerprint':identity(rows),'evidence':rows,'instruction':state['latest_instruction'],
        'started':str(Path(started).resolve()),'finished':str(Path(finished).resolve()),'receipt':receipt}
    state.setdefault('reviews',{})[unit]=record
    state['history'].append({'event':'review_recorded','unit':unit,'fingerprint':record['fingerprint']})
    return record

def adopt(state, authority):
    if not authority.strip():raise P.PhaseError('Record the actual user instruction; this tool grants no permission')
    previous=state.get('workflow_version','unknown')
    state['workflow_version']=VERSION
    state['autonomy_instruction']=authority
    state.setdefault('budget_anchor',{'basis':'legacy_unknown','started_at':state.get('started_at'),
        'verified':False})
    state['history'].append({'event':'workflow_adopted','previous_version':previous,'version':VERSION,
        'authority':authority,'project_deadline_preserved':state['project_deadline']})
    return {'version':VERSION,'previous_version':previous,'status':state['status'],
        'budget_anchor':state['budget_anchor'],'next_action':state.get('next_action')}

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--state',required=True)
    sub=ap.add_subparsers(dest='op',required=True)
    p=sub.add_parser('adopt');p.add_argument('--authority',required=True)
    for op in ('checkpoint','plan','route','review-status','review-record'):
        p=sub.add_parser(op);p.add_argument('--key',required=True);p.add_argument('--root',required=True)
        p.add_argument('--evidence',action='append',required=True)
        if op=='checkpoint':
            p.add_argument('--claim',required=True);p.add_argument('--next-action',required=True)
            p.add_argument('--outcome',default='working')
        elif op=='plan':
            p.add_argument('--limit',type=float,required=True);p.add_argument('--used',type=float,default=0)
            p.add_argument('--origin',choices=['agent','user','provider'],default='agent');p.add_argument('--rationale',required=True)
        elif op=='route':
            p.add_argument('--claim',required=True);p.add_argument('--action',required=True)
            p.add_argument('--status',default='ready');p.add_argument('--estimated-seconds',type=float,default=0)
        elif op=='review-record':p.add_argument('--started',required=True);p.add_argument('--finished',required=True)
    a=ap.parse_args(argv)
    try:
        with P.locked(a.state):
            s=P.load(a.state)
            if s.get('schema_version')!='research-phase-1':raise P.PhaseError('Unknown legacy schema; retain the original record')
            if a.op=='adopt':r=adopt(s,a.authority)
            elif a.op=='checkpoint':r=checkpoint(s,a.key,a.claim,a.next_action,a.evidence,a.root,a.outcome)
            elif a.op=='plan':r=plan(s,a.key,a.limit,a.used,a.origin,a.rationale,a.evidence,a.root)
            elif a.op=='route':r=route(s,a.key,a.claim,a.action,a.evidence,a.root,a.status,a.estimated_seconds)
            elif a.op=='review-status':r=review_status(s,a.key,a.evidence,a.root)
            else:r=review_record(s,a.key,a.evidence,a.root,a.started,a.finished)
            if a.op!='review-status':P.save(a.state,s)
        print(json.dumps(r,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'error':str(e)},ensure_ascii=False),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
