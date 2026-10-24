#!/usr/bin/env python3
"""Plan-bound local datasets and source-gated sequencing, not a science certificate."""
from __future__ import annotations
import argparse, csv, json, math, re
from pathlib import Path
import artifact_io as A
import phase_control as P

NAME='.research-data.json'
STAGES=('feasibility','design','data','research','manuscript','delivery')
class DataError(ValueError):pass

# Each group requires a real output of at least one listed predecessor. This
# checks file lineage, not whether an algorithm or scientific claim is correct.
INPUT_GROUPS={
    'analysis-execution':[['data-preparation']],
    'robustness-reproducibility':[['analysis-execution']],
    'scientific-visualization':[['analysis-execution','robustness-reproducibility']],
    'manuscript-writing':[['analysis-execution','robustness-reproducibility'],['scientific-visualization']],
    'citation-audit':[['manuscript-writing']],
    'manuscript-review':[['manuscript-writing','citation-audit']],
    # A real review can revise the manuscript; its current output is the
    # immediate predecessor, without decorative original-draft inputs.
    'final-expression':[['manuscript-review']]}

def input_lineage(state,capability,inputs,purpose='formal'):
    if state.get('workflow')!='local-data' or purpose=='diagnostic':return
    actual={(x['path'],x['sha256']) for x in inputs}
    rows=state.get('professional_steps',[])+state.get('professional_pending',[])
    for group in INPUT_GROUPS.get(capability,[]):
        candidates=set()
        for cap in group:
            for row in reversed(rows):
                if row.get('capability')!=cap or row.get('status') not in {'completed','eligible_for_handoff'} or not row.get('finished'):continue
                begun=P.load(row['started']);ctx=begun.get('phase',{})
                import professional_flow as F
                try:F.require_current(state,begun)
                except F.FlowError:continue
                if begun.get('purpose','formal')!='formal' or not P.context_matches(state,ctx,False) or ctx.get('local_data_id')!=state.get('local_data',{}).get('id'):continue
                # Citation correction is a legitimate intermediate manuscript
                # revision only while it still descends from current writing.
                if cap=='citation-audit':
                    try:input_lineage(state,cap,begun['inputs'])
                    except DataError:continue
                candidates.update((x['path'],x['sha256']) for x in P.load(row['finished'])['outputs']);break
        if not actual.intersection(candidates):raise DataError('Consume a current actual output from '+ '/'.join(group)+'; unrelated inputs or an earlier result version cannot complete this step')

def path(root,name):
    root=Path(root).resolve();p=(root/name).resolve()
    if not p.is_relative_to(root) or not p.is_file() or not p.stat().st_size:
        raise DataError('Required local file missing, empty or outside project: '+str(name))
    if p.suffix in {'.partial','.tmp'}:raise DataError('Incomplete download is not a dataset')
    return p

def ref(root,name):
    p=path(root,name)
    return {'path':str(p.relative_to(Path(root).resolve())),'sha256':A.digest(p)}

def completed(state,capability,stage=None):
    import capabilities as C
    import professional_flow as F
    rows=state.get('professional_steps',[])+state.get('professional_pending',[])
    eligible=[x for x in rows if x.get('capability')==capability and x.get('finished') and
        x.get('status') in {'completed','eligible_for_handoff'} and (stage is None or x.get('stage')==stage)]
    for row in reversed(eligible):
        begun=P.load(row['started']);context=begun.get('phase',{})
        if begun.get('purpose','formal')!='formal':continue
        try:F.require_current(state,begun)
        except F.FlowError:continue
        if capability!='research-design' and state.get('local_data') and context.get('local_data_id')!=state['local_data']['id']:
            if capability!='data-discovery' or not planned_by(state,begun):continue
        if P.context_matches(state,context,False):
            F.check(P.load(C.index_path()),begun,P.load(row['finished']))
            input_lineage(state,capability,begun['inputs'])
            return row
    raise DataError('Complete the actual source-gated '+capability+' step'+(' in '+stage if stage else '')+' before continuing')

def load(state):
    binding=state.get('local_data')
    if not binding:raise DataError('Plan the complete necessary dataset list; local data is not yet ready')
    root=Path(binding['root']);d=P.load(root/NAME)
    if d['id']!=binding['id'] or d['phase_id']!=state['id']:raise DataError('Local dataset manifest belongs to another project')
    if d['instruction']!=P.instruction_key(state):raise DataError('Scientific commitment changed; reassess the required datasets without resetting capacity')
    for k in ('research_plan','specification'):
        if ref(root,d[k]['path'])!=d[k]:raise DataError(k+' changed; version the plan and revise the dataset requirements')
    return root,d

def planned_by(state,begun):
    """The discovery step may create the requirements it is about to acquire."""
    if begun.get('capability')!='data-discovery':return False
    _,d=load(state)
    return d.get('planning_step_id')==begun.get('id')

def plan(state,root,specification,research_plan,revision_reason=None):
    root=Path(root).resolve()
    if state.get('workflow')!='local-data' or state['stage']!='data' or not P.guard(state)['allowed']:
        raise DataError('Complete study design and enter the local-data stage before planning acquisition')
    design=completed(state,'research-design','design')
    spec=ref(root,specification);rp=ref(root,research_plan);items=P.load(root/spec['path']).get('datasets')
    design_outputs={(x['path'],x['sha256']) for x in P.load(design['finished'])['outputs']}
    if (str(root/rp['path']),rp['sha256']) not in design_outputs:raise DataError('Use the actual completed research-design plan output')
    if state.get('local_data') and Path(state['local_data']['root']).resolve()!=root:raise DataError('Keep the same research root and cumulative capacity receipt')
    if not isinstance(items,list) or not items:raise DataError('List every dataset actually required by the research plan')
    seen=set();files=set()
    for item in items:
        if not isinstance(item,dict) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]*',item.get('id','')) or item['id'] in seen:
            raise DataError('Each required dataset needs a unique stable id')
        seen.add(item['id'])
        if not isinstance(item.get('purpose'),str) or not item['purpose'].strip() or not item.get('files'):
            raise DataError('Bind each dataset to an experiment and all necessary local files')
        if not isinstance(item['files'],list):raise DataError('Dataset files must be a list')
        for f in item['files']:
            if not isinstance(f,dict) or not isinstance(f.get('path'),str):raise DataError('Each local file needs a string path and format')
            name=f.get('path','');p=Path(name)
            if not name or p.is_absolute() or '..' in p.parts or '\\' in name or name in files or p.name.startswith('.research'):
                raise DataError('Unique project-relative dataset paths are required')
            files.add(name)
            if f.get('format') not in {'csv','tsv','json','jsonl','external'}:raise DataError('Select an actual parser or a source-gated external format inspection')
            if 'expected_rows' in f and (type(f['expected_rows']) is not int or f['expected_rows']<=0):raise DataError('Expected rows must come from the actual selected coverage')
    previous=None
    if (root/NAME).exists():
        previous=P.load(root/NAME)
        if previous['research_plan']==rp and previous['specification']==spec and previous['phase_id']==state['id'] and previous['instruction']==P.instruction_key(state):
            state['local_data']={'root':str(root),'id':previous['id'],'required_count':len(items)}
            return {'status':'unchanged','datasets':len(items)}
        if not revision_reason or not revision_reason.strip():raise DataError('Keep the original requirements; revisions need a reason and versioned plan/specification')
    # The initial data assessment itself is source-first. A design can include
    # the machine-readable list, or an active discovery step creates it.
    planning_step=None
    if (str(root/spec['path']),spec['sha256']) not in design_outputs:
        import capabilities as C
        import professional_flow as F
        for row in reversed(state.get('professional_pending',[])):
            if row.get('capability')!='data-discovery' or row.get('status')!='started':continue
            begun=P.load(row['started']);context=begun.get('phase',{})
            if not P.context_matches(state,context):continue
            if (str(root/rp['path']),rp['sha256']) not in {(x['path'],x['sha256']) for x in begun['inputs']}:continue
            if (root/spec['path']).stat().st_mtime_ns<begun['started_ns']:continue
            F.validate_start(P.load(C.index_path()),begun)
            planning_step=begun['id'];break
        if not planning_step:raise DataError('Begin data-discovery on the completed research plan before evaluating and writing the dataset specification')
    import uuid
    history=[]
    if previous is not None:
        old=root/('.research-data-history/'+A.digest(root/NAME)+'.json')
        old.parent.mkdir(exist_ok=True)
        if not old.exists():P.save(old,previous)
        history=previous.get('history',[])+[{'event':'requirements_revised','reason':revision_reason,'previous_manifest':ref(root,str(old.relative_to(root)))}]
    d={'schema':'local-research-data-1','id':uuid.uuid4().hex,'phase_id':state['id'],
        'instruction':P.instruction_key(state),'latest_instruction_at_planning':state['latest_instruction'],'research_plan':rp,'specification':spec,'datasets':items,
        'sources':{},'inspections':{},'history':history,'planning_step_id':planning_step}
    P.save(root/NAME,d);state['local_data']={'root':str(root),'id':d['id'],'required_count':len(items)}
    state['history'].append({'event':'local_dataset_requirements','id':d['id'],'required_count':len(items),'revision_reason':revision_reason})
    return {'status':'planned','datasets':len(items),'next_action':'Select authoritative sources and acquire all planned contents within the original storage quota'}

def source(state,dataset,metadata,selection,started,finished,publisher,version,url):
    import capabilities as C
    import professional_flow as F
    from urllib.parse import urlsplit
    root,d=load(state)
    if state['stage']!='data' or not P.guard(state)['allowed']:raise DataError('Source binding belongs to the active data stage')
    if dataset not in {x['id'] for x in d['datasets']}:raise DataError('Unplanned dataset')
    if not publisher.strip() or not version.strip() or urlsplit(url).scheme!='https' or not urlsplit(url).hostname or urlsplit(url).query or urlsplit(url).fragment or urlsplit(url).username:
        raise DataError('Record the actual publisher/version and a public HTTPS landing URL without credentials')
    begun=P.load(started);done=P.load(finished);context=begun.get('phase',{})
    if begun.get('capability')!='data-discovery' or not P.context_matches(state,context,False) or (context.get('local_data_id')!=d['id'] and not planned_by(state,begun)):
        raise DataError('Use this study’s actual data-discovery professional receipt')
    F.require_current(state,begun)
    F.check(P.load(C.index_path()),begun,done)
    rows=[ref(root,metadata),ref(root,selection)]
    outputs={(x['path'],x['sha256']) for x in done['outputs']}
    if any((str(root/x['path']),x['sha256']) not in outputs for x in rows):raise DataError('Metadata and source selection must be actual discovery outputs')
    inputs={(x['path'],x['sha256']) for x in begun['inputs']}
    if not any((str(root/d[k]['path']),d[k]['sha256']) in inputs for k in ('research_plan','specification')):
        raise DataError('Source selection must consume this research plan or dataset specification')
    d['sources'][dataset]={'publisher':publisher,'version':version,'landing_url':url,'evidence':rows,
        'started':str(Path(started).resolve()),'finished':str(Path(finished).resolve()),
        'started_sha256':A.digest(started),'finished_sha256':A.digest(finished)}
    P.save(root/NAME,d)
    return {'status':'source_bound','dataset':dataset,'authority_certified_by_tool':False}

def inspect(p,f):
    kind=f['format'];count=0;columns=None
    if kind in {'csv','tsv'}:
        with p.open(encoding=f.get('encoding','utf-8'),newline='') as h:
            reader=csv.reader(h,delimiter=f.get('delimiter','\t' if kind=='tsv' else ','))
            columns=next(reader,None) if f.get('header',True) else f.get('columns')
            if not columns or len(set(columns))!=len(columns):raise DataError('Actual CSV header or documented headerless schema required')
            required=f.get('required_columns',[])
            if not set(required).issubset(columns):raise DataError('Required variables missing')
            numeric=f.get('numeric_columns',[])
            if not set(numeric).issubset(columns):raise DataError('Numeric variables missing')
            for row in reader:
                if not row or all(not x.strip() for x in row):continue
                if len(row)!=len(columns):raise DataError('Malformed or truncated CSV row')
                for col in numeric:
                    value=row[columns.index(col)].strip()
                    if value in f.get('missing_values',['','NA','NaN']):
                        if f.get('allow_missing',True):continue
                        raise DataError('Missing value violates the selected dataset contract')
                    if not math.isfinite(float(value)):raise DataError('Nonfinite numeric value')
                count+=1
    elif kind=='jsonl':
        with p.open(encoding='utf-8') as h:
            for line in h:
                if line.strip():json.loads(line);count+=1
    elif kind=='json':
        if p.stat().st_size>8*1024*1024:raise DataError('Use an actual streaming external-format reader for large JSON; retain the complete local dataset')
        with p.open(encoding='utf-8') as h:value=json.load(h)
        count=len(value) if isinstance(value,(dict,list)) else 1
    else:raise DataError('External format needs an actual source-gated reader/inspection receipt; do not relabel it CSV')
    if count==0 or ('expected_rows' in f and count!=f['expected_rows']):raise DataError('Dataset row coverage differs from the selected research requirement')
    return {'format':kind,'rows':count,'columns':columns,'parser_scope':'whole_file','scientific_coverage_certified':False}

def external_inspection(state,started,finished):
    import capabilities as C
    import professional_flow as F
    root,d=load(state);begun=P.load(started);done=P.load(finished)
    context=begun.get('phase',{})
    if begun.get('capability')!='data-preparation' or not P.context_matches(state,context,False) or context.get('local_data_id')!=d['id']:
        raise DataError('Use the actual format reader’s data-preparation receipt')
    F.require_current(state,begun)
    F.check(P.load(C.index_path()),begun,done)
    inputs={(x['path'],x['sha256']) for x in begun['inputs']}
    bound=[]
    for item in d['datasets']:
        for f in item['files']:
            if f['format']=='external':
                row=ref(root,f['path'])
                if (str(root/row['path']),row['sha256']) in inputs:
                    d['inspections'][f['path']]={'file':row,'started':str(Path(started).resolve()),
                        'finished':str(Path(finished).resolve()),'started_sha256':A.digest(started),'finished_sha256':A.digest(finished)}
                    bound.append(f['path'])
    if not bound:raise DataError('Reader must actually consume the external-format files')
    P.save(root/NAME,d)
    return {'inspected_files':bound,'semantic_readability_verified_by_tool':False}

def receipt_valid(row):
    import capabilities as C
    import professional_flow as F
    if A.digest(row['started'])!=row['started_sha256'] or A.digest(row['finished'])!=row['finished_sha256']:
        raise DataError('Dataset professional receipt changed')
    F.check(P.load(C.index_path()),P.load(row['started']),P.load(row['finished']))

def check(state,validated=True,refresh=False,only=None):
    root,d=load(state);issues=[];rows=[]
    import research_storage as S
    try:
        storage=S.read(root)
        if state.get('storage')!={'root':str(root),'id':storage['id']}:raise DataError('Bind the same project capacity receipt before data acquisition')
        capacity=S.check(root,storage)
        if not capacity['allowed']:issues.append({'capacity':capacity['reasons']})
    except (ValueError,OSError,KeyError) as e:issues.append({'capacity':str(e)})
    if issues:return {'ready':False,'required_datasets':len(d['datasets']),'local_files_checked':[],'issues':issues,
        'next_action':'Repair the acquisition/capacity plan within the original quota before inspecting or experimenting'}
    for item in d['datasets']:
        selected=[f for f in item['files'] if only is None or f['path'] in only]
        if not selected:continue
        try:
            src=d['sources'].get(item['id'])
            if not src:raise DataError('Authoritative source selection not completed')
            receipt_valid(src)
            for e in src['evidence']:
                if ref(root,e['path'])!=e:raise DataError('Source evidence changed')
            for f in selected:
                p=path(root,f['path']);stat=p.stat();fingerprint=[stat.st_ino,stat.st_size,stat.st_mtime_ns]
                old=d.setdefault('checks',{}).get(f['path'])
                reused=bool(old and old['stat']==fingerprint and not refresh)
                digest=old['sha256'] if reused else A.digest(p)
                if old and old['sha256']!=digest:raise DataError('Dataset changed; preserve old evidence and revise/revalidate its version')
                if f.get('expected_sha256') and f['expected_sha256']!=digest:raise DataError('Expected dataset checksum mismatch')
                if f.get('expected_bytes') is not None and f['expected_bytes']!=stat.st_size:raise DataError('Dataset length mismatch')
                details=None
                if validated:
                    if f['format']=='external':
                        audit=d['inspections'].get(f['path'])
                        if not audit or audit['file']!={'path':f['path'],'sha256':digest}:raise DataError('Execute the appropriate local format inspection')
                        receipt_valid(audit);details={'format':'external','parser_scope':'source_gated_professional_inspection','semantic_readability_verified_by_tool':False}
                    else:details=old.get('inspection') if reused and old.get('inspection') else inspect(p,f)
                d['checks'][f['path']]={'stat':fingerprint,'sha256':digest,'inspection':details or (old or {}).get('inspection')}
                rows.append({'dataset':item['id'],'path':f['path'],'bytes':stat.st_size,'sha256':digest,'inspection':details,
                    'verification_basis':'unchanged_file_stat_since_full_hash' if reused else 'current_full_hash'})
        except (ValueError,OSError,KeyError,UnicodeError,csv.Error) as e:issues.append({'dataset':item['id'],'error':str(e)})
    P.save(root/NAME,d)
    return {'ready':not issues,'required_datasets':len(d['datasets']),'local_files_checked':rows,'issues':issues,
        'purpose':'formal' if only is None else 'diagnostic','all_required_data_checked':only is None,
        'level':'validated' if validated else 'local','next_action':'continue' if not issues else 'Autonomously repair acquisition, coverage or decoding within the unchanged goal and quota; do not start formal experiments',
        'scientific_authority_or_completeness_certified_by_tool':False}

def require_ready(state,validated=True,refresh=False):
    result=check(state,validated,refresh)
    if not result['ready']:raise DataError(json.dumps(result,ensure_ascii=False))
    return result

def diagnostic_ready(state,capability,inputs,refresh=False):
    if capability not in {'data-preparation','analysis-execution','scientific-visualization'} or state['stage'] not in {'data','research'}:
        raise DataError('Diagnostic work is limited to data/model/figure diagnosis in the data or research stage; it cannot replace a formal paper')
    root,d=load(state)
    actual={x['path'] for x in inputs or []}
    selected={f['path'] for item in d['datasets'] for f in item['files'] if str(root/f['path']) in actual}
    # A validated preparation output is a legitimate diagnostic input. Follow
    # its actual source receipt instead of requiring decorative raw-file inputs.
    if not selected:
        import capabilities as C
        import professional_flow as F
        actual_refs={(x['path'],x['sha256']) for x in inputs or []}
        for row in reversed(state.get('professional_steps',[])+state.get('professional_pending',[])):
            if row.get('capability')!='data-preparation' or not row.get('finished') or row.get('status') not in {'completed','eligible_for_handoff'}:continue
            begun=P.load(row['started']);done=P.load(row['finished']);context=begun.get('phase',{})
            if not P.context_matches(state,context,False) or context.get('local_data_id')!=d['id']:continue
            try:F.require_current(state,begun)
            except F.FlowError:continue
            if not actual_refs.intersection((x['path'],x['sha256']) for x in done['outputs']):continue
            F.check(P.load(C.index_path()),begun,done)
            prepared_inputs={x['path'] for x in begun['inputs']}
            selected.update(f['path'] for item in d['datasets'] for f in item['files'] if str(root/f['path']) in prepared_inputs)
    if not selected:raise DataError('Include the actual ready planned local data files in diagnostic inputs; a URL or method note is not diagnostic data')
    # Readers must be allowed to establish external-format readability rather
    # than require their own yet-to-be-created inspection receipt before begin.
    result=check(state,capability!='data-preparation',refresh,selected)
    if not result['ready']:raise DataError(json.dumps(result,ensure_ascii=False))
    return result

def gate(state,capability,refresh=False,purpose='formal',inputs=None):
    if state.get('workflow')!='local-data':return
    if purpose=='diagnostic':return diagnostic_ready(state,capability,inputs,refresh)
    stage=state['stage']
    stages={'research-design':{'design'},'data-discovery':{'data'},'data-preparation':{'data'},
        'analysis-execution':{'research'},'robustness-reproducibility':{'research'},'scientific-visualization':{'research'},
        'manuscript-writing':{'manuscript'},'manuscript-review':{'manuscript'},'final-expression':{'manuscript'}}
    if capability in stages and stage not in stages[capability]:raise DataError('Use the corresponding local research stage before '+capability)
    if capability=='data-preparation':require_ready(state,False,refresh)
    if capability in {'analysis-execution','robustness-reproducibility','scientific-visualization','manuscript-writing','manuscript-review','final-expression'}:
        require_ready(state,True,refresh);completed(state,'data-preparation','data')
    if capability in {'robustness-reproducibility','scientific-visualization','manuscript-writing','manuscript-review','final-expression'}:completed(state,'analysis-execution','research')
    if capability in {'scientific-visualization','manuscript-writing','manuscript-review','final-expression'}:completed(state,'robustness-reproducibility','research')
    if capability in {'manuscript-writing','manuscript-review','final-expression'}:completed(state,'scientific-visualization','research')
    if capability in {'manuscript-review','final-expression'}:completed(state,'manuscript-writing','manuscript')
    if capability=='final-expression':completed(state,'manuscript-review','manuscript')

def stage_exit(state,following):
    if state.get('workflow')!='local-data':return
    current=state['stage']
    needed={'design':['research-design'],'data':['data-discovery','data-preparation'],
        'research':['analysis-execution','robustness-reproducibility','scientific-visualization'],
        'manuscript':['manuscript-writing','citation-audit','manuscript-review','final-expression']}
    if following=='completed' and current!='delivery':raise DataError('Complete local experiments, figures, manuscript and polishing before delivery')
    for cap in needed.get(current,[]):completed(state,cap,current)
    if current in {'data','research','manuscript','delivery'}:require_ready(state,True,True)

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--state',required=True)
    sub=ap.add_subparsers(dest='op',required=True)
    a=sub.add_parser('plan');a.add_argument('--root',required=True);a.add_argument('--spec',required=True);a.add_argument('--research-plan',required=True);a.add_argument('--revision-reason')
    a=sub.add_parser('source');a.add_argument('--dataset',required=True);a.add_argument('--metadata',required=True);a.add_argument('--selection',required=True);a.add_argument('--started',required=True);a.add_argument('--finished',required=True);a.add_argument('--publisher',required=True);a.add_argument('--version',required=True);a.add_argument('--url',required=True)
    a=sub.add_parser('inspect-external');a.add_argument('--started',required=True);a.add_argument('--finished',required=True)
    a=sub.add_parser('check');a.add_argument('--local-only',action='store_true');a.add_argument('--refresh',action='store_true')
    a=ap.parse_args(argv)
    try:
        with P.locked(a.state):
            s=P.load(a.state)
            if a.op=='plan':r=plan(s,a.root,a.spec,a.research_plan,a.revision_reason);P.save(a.state,s)
            elif a.op=='source':r=source(s,a.dataset,a.metadata,a.selection,a.started,a.finished,a.publisher,a.version,a.url)
            elif a.op=='inspect-external':r=external_inspection(s,a.started,a.finished)
            else:r=check(s,not a.local_only,a.refresh)
        print(json.dumps(r,ensure_ascii=False,indent=2));return 2 if r.get('ready') is False else 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'error':str(e),'next_action':'Diagnose and repair the relevant local data step; preserve actual budgets and existing outputs'},ensure_ascii=False),file=__import__('sys').stderr);return 2
if __name__=='__main__':raise SystemExit(main())
