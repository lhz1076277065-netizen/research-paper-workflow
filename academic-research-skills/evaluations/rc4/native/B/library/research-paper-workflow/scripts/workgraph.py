#!/usr/bin/env python3
"""Optional local research dependency checker. No agents, networks or job scheduler.

A graph records ONLY the requested tasks. It never fabricates the full lifecycle.
Changes invalidate declared consumers; scientific meaning is a host decision.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

STATES={'pending','running','checked','failed','blocked','stale','skipped'}
KINDS={'data','method','results','citations','presentation','journal_policy','unknown'}

class GraphError(ValueError):pass

def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def resolve(root, rel):
    if not isinstance(rel,str) or not rel or Path(rel).is_absolute() or '\\' in rel:raise GraphError('Expected project-relative path')
    root=Path(root).resolve();p=(root/rel).resolve()
    if not p.is_relative_to(root):raise GraphError('Path outside project')
    return p

def topology(graph):
    if graph.get('schema_version')!='workgraph-1':raise GraphError('Unknown workgraph version')
    if type(graph.get('revision')) is not int or graph['revision']<0:raise GraphError('Invalid revision')
    tasks=graph.get('tasks',[])
    if not tasks:raise GraphError('At least one explicitly requested task is required')
    ids=[t.get('id') for t in tasks]
    if any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):raise GraphError('Unique task IDs required')
    by={t['id']:t for t in tasks}
    for t in tasks:
        if t.get('status','pending') not in STATES:raise GraphError('Unknown task status')
        if type(t.get('applicable',True)) is not bool:raise GraphError('applicable must be boolean')
        if not t.get('applicable',True) and not t.get('skip_reason'):raise GraphError('Non-applicable task needs reason')
        dependencies=t.get('depends_on',[])
        if not isinstance(dependencies,list) or any(x not in by for x in dependencies):raise GraphError('Dependency not in graph')
        if len(set(dependencies))!=len(dependencies):raise GraphError('Duplicate dependency')
        if type(t.get('attempts',0)) is not int or t.get('attempts',0)<0:raise GraphError('Invalid attempt budget')
        if 'max_attempts' in t and (type(t['max_attempts']) is not int or t['max_attempts']<=0):raise GraphError('Invalid attempt budget')
    order=[];pending=set(ids)
    while pending:
        ready=[i for i in ids if i in pending and set(by[i].get('depends_on',[])).issubset(order)]
        if not ready:raise GraphError('Dependency cycle')
        order.extend(ready);pending.difference_update(ready)
    return order,by

def assess(graph,root):
    order,by=topology(graph);rows={};ready=[];reuse=[]
    for i in order:
        t=by[i];state=t.get('status','pending');reasons=[]
        if not t.get('applicable',True):
            rows[i]={'status':'skipped','reasons':[t['skip_reason']]};continue
        parents=t.get('depends_on',[])
        unmet=[p for p in parents if rows[p]['status']!='reusable']
        stale_inputs=[]
        for a in t.get('inputs',[]):
            p=resolve(root,a['path'])
            if not p.is_file() or digest(p)!=a.get('sha256'):stale_inputs.append(a['path'])
        if stale_inputs:reasons.append('input_changed_or_missing:'+','.join(stale_inputs))
        if state=='checked':
            outputs=t.get('outputs',[])
            if not outputs:reasons.append('checked_task_without_outputs')
            for a in outputs:
                p=resolve(root,a['path'])
                if not p.is_file() or digest(p)!=a.get('sha256'):reasons.append('output_changed_or_missing:'+a['path'])
            receipt=t.get('acceptance_report')
            if not receipt:reasons.append('checked_task_without_acceptance_report')
            else:
                p=resolve(root,receipt['path'])
                if not p.is_file() or digest(p)!=receipt.get('sha256'):reasons.append('acceptance_report_missing_or_changed')
                else:
                    report=load(p)
                    if report.get('status')!='checked_for_handoff' or report.get('passed') is not True:reasons.append('acceptance_incomplete')
                    returned={a['path']:a['sha256'] for a in report.get('artifacts',[])}
                    if any(returned.get(a['path'])!=a.get('sha256') for a in outputs):reasons.append('acceptance_output_version_mismatch')
            if unmet:reasons.append('upstream_not_reusable:'+','.join(unmet))
            status='stale' if reasons else 'reusable'
            if status=='reusable':reuse.append(i)
        elif state=='running':status='running';reasons.append('host_manages_running_job')
        elif state=='skipped':
            status='blocked';reasons.append('skipped_task_is_still_applicable')
        elif state=='blocked':status='blocked';reasons.extend(t.get('blockers',['external_condition_unresolved']))
        elif unmet:status='waiting';reasons.append('upstream_not_reusable:'+','.join(unmet))
        elif reasons:status='needs_rebind'
        elif 'max_attempts' in t and t.get('attempts',0)>=t['max_attempts']:status='budget_exhausted'
        else:status='ready';ready.append(i)
        rows[i]={'status':status,'reasons':reasons}
    conflicts=[]
    active=[i for i in order if rows[i]['status'] in {'ready','running'}]
    for idx,a in enumerate(active):
        for b in active[idx+1:]:
            overlap=[]
            for x in by[a].get('write_paths',[]):
                px=resolve(root,x)
                for y in by[b].get('write_paths',[]):
                    py=resolve(root,y)
                    if px==py or px.is_relative_to(py) or py.is_relative_to(px):overlap.append((x,y))
            if overlap:conflicts.append({'tasks':[a,b],'overlaps':overlap,'action':'serialize_or_isolate_writes'})
    return {'schema_version':'workgraph-assessment-1','ready':ready,'reusable':reuse,'tasks':rows,
            'write_conflicts':conflicts,'execution_started':False,'scientific_validity_certified':False,
            'note':'Ready means declared predecessors and local bindings allow work, not scientific approval. No job is launched.'}

def invalidate(graph,changes,reason,expected_revision):
    """Create a NEW state revision. Caller owns the original file and single-writer policy."""
    order,by=topology(graph)
    if expected_revision!=graph['revision']:raise GraphError('Revision conflict; reread before merging')
    if not isinstance(reason,str) or not reason.strip():raise GraphError('Explain the actual change')
    if not isinstance(changes,list) or not changes:raise GraphError('Explicit changes required')
    changed={}
    for item in changes:
        if item.get('task_id') not in by or item.get('kind') not in KINDS:raise GraphError('Unknown change task/kind')
        changed.setdefault(item['task_id'],set()).add(item['kind'])
    out=copy.deepcopy(graph);newby={t['id']:t for t in out['tasks']};impact={}
    for i in order:
        kinds=set(changed.get(i,[]))
        t=newby[i]
        for parent in t.get('depends_on',[]):
            incoming=impact.get(parent,set())
            # Conservative edge semantics: all declared descendants, never ancestors.
            # Host should split tasks when only a portion consumes this output.
            kinds.update(incoming)
        if kinds:
            impact[i]=kinds
            if t.get('applicable',True):t['status']='stale'
            t['stale_reason']=reason
            # No output deleted, no completed result retroactively changed.
    out['revision']+=1
    out.setdefault('change_log',[]).append({'revision':out['revision'],'reason':reason,'changes':changes,
           'affected_tasks':list(impact),'time':datetime.now(timezone.utc).isoformat()})
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('assess');a.add_argument('--state',required=True);a.add_argument('--root',required=True)
    a=sub.add_parser('invalidate');a.add_argument('--state',required=True);a.add_argument('--changes',required=True)
    a.add_argument('--reason',required=True);a.add_argument('--expected-revision',type=int,required=True);a.add_argument('--out',required=True)
    a=p.parse_args()
    try:
        g=load(a.state)
        if a.action=='assess':report=assess(g,a.root)
        else:
            report=invalidate(g,load(a.changes),a.reason,a.expected_revision)
            out=Path(a.out)
            if out.exists():raise GraphError('Write a new state path; do not overwrite another revision')
            if load(a.state).get('revision')!=a.expected_revision:raise GraphError('State revision changed')
            with out.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
        print(json.dumps(report,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError) as e:
        print(json.dumps({'status':'invalid_or_blocked','error':str(e)},ensure_ascii=False));return 2

if __name__=='__main__':raise SystemExit(main())
