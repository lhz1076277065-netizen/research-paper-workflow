#!/usr/bin/env python3
"""Content-bound research questions and manuscript coverage, not scientific truth.

The host supplies actual user-request evidence. Exact quotes and source receipts
are checked here; neither a local file nor this tool manufactures authorization.
Scientific interpretation is performed by the source-guided professional review.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid
import artifact_io as A

VERSION = '3.5.5'
SCIENCE = ('objects','relationship','scope','completion_criteria','questions')
ANSWER_STATES = {'unanswered','answered','inconclusive'}
EXECUTION_STATES = {'not_run','working','completed','failed'}

class CommitmentError(ValueError): pass

def _text(value, name):
    if not isinstance(value,str) or not value.strip():raise CommitmentError(name+' needs actual text')
    return value.strip()

def _load(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def _ref(root, path):
    root=Path(root).resolve();p=(root/path).resolve()
    if not p.is_relative_to(root) or not p.is_file() or not p.stat().st_size:
        raise CommitmentError('Missing, empty or outside-project research artifact: '+str(path))
    return {'path':str(p.relative_to(root)),'sha256':A.digest(p)}

def _verify(root, row):
    if _ref(root,row['path'])!=row:raise CommitmentError('Research artifact changed; preserve and version it: '+row['path'])

def _identity(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def _active(state):
    if state.get('status')!='active':raise CommitmentError('A paused or terminal study cannot be changed by this tool; preserve its actual host state')

def _science_identity(spec):return _identity({k:spec[k] for k in SCIENCE})

def _experiment_fingerprints(row):return {e['id']:_identity(e) for e in row['primary_experiments']}

def _observation(root,row):
    p=(Path(root)/row['path']).resolve();s=p.stat()
    return {'path':row['path'],'size':s.st_size,'mtime_ns':s.st_mtime_ns,'inode':s.st_ino}

def _spec(value):
    if not isinstance(value,dict):raise CommitmentError('Research specification must be an object')
    title=_text(value.get('title'),'title')
    science={k:value.get(k) for k in SCIENCE+('primary_experiments',)}
    for key in ('objects','completion_criteria'):
        if not isinstance(science[key],list) or not science[key]:raise CommitmentError(key+' needs explicit research content')
        science[key]=[_text(x,key) for x in science[key]]
    for key in ('relationship','scope'):science[key]=_text(science[key],key)
    questions=science['questions'];experiments=science['primary_experiments']
    if not isinstance(questions,list) or not questions:raise CommitmentError('Specify the questions that the research must answer')
    qids=set();normalized=[]
    for q in questions:
        if not isinstance(q,dict):raise CommitmentError('Invalid research question')
        qid=_text(q.get('id'),'question id')
        if qid in qids:raise CommitmentError('Question IDs must be unique')
        required=q.get('required',True)
        if not isinstance(required,bool):raise CommitmentError('Question required must be a boolean')
        qids.add(qid);normalized.append({'id':qid,'text':_text(q.get('text'),'question'),'required':required})
    if not any(q['required'] for q in normalized):raise CommitmentError('A fixed study needs at least one required question')
    science['questions']=normalized
    if not isinstance(experiments,list) or not experiments:raise CommitmentError('Declare the primary experiments needed to answer the questions')
    eids=set();normalized=[]
    for e in experiments:
        if not isinstance(e,dict):raise CommitmentError('Invalid primary experiment')
        eid=_text(e.get('id'),'experiment id');ids=e.get('question_ids')
        if eid in eids or not isinstance(ids,list) or not ids or not set(ids)<=qids:
            raise CommitmentError('Each primary experiment needs a unique ID and known question IDs')
        item={'id':eid,'question_ids':list(dict.fromkeys(ids)),'purpose':_text(e.get('purpose'),'experiment purpose')}
        if 'method' in e:item['method']=_text(e['method'],'experiment method')
        eids.add(eid);normalized.append(item)
    science['primary_experiments']=normalized
    covered={qid for e in normalized for qid in e['question_ids']}
    if any(q['required'] and q['id'] not in covered for q in science['questions']):
        raise CommitmentError('Each required question needs a planned primary test; optional extensions are not completion requirements')
    return title,science

def _request(root, request, quote):
    row=_ref(root,request);quote=_text(quote,'exact user-request quote')
    content=A.output_text(Path(root)/row['path'])
    if content is None:raise CommitmentError('Supply bounded actual user-request evidence')
    # Structured records must actually identify the quoted message as user text.
    if Path(request).suffix in {'.json','.jsonl'}:
        try:
            values=[json.loads(x) for x in content.splitlines() if x.strip()] if Path(request).suffix=='.jsonl' else [json.loads(content)]
        except ValueError:raise CommitmentError('Invalid structured user-request evidence')
        def user(v):
            if isinstance(v,list):return any(user(x) for x in v)
            if not isinstance(v,dict):return False
            payload=v.get('payload',{})
            def contains(text):
                if isinstance(text,str):return quote in text
                if isinstance(text,list):return any(contains(x) for x in text)
                if isinstance(text,dict):return any(contains(text[k]) for k in ('text','content') if k in text)
                return False
            if v.get('role')=='user' and contains(v.get('content','')):return True
            if isinstance(payload,dict) and payload.get('type')=='user_message' and quote in str(payload.get('message','')):return True
            return any(user(v[k]) for k in ('messages','items') if k in v)
        if not any(user(v) for v in values):raise CommitmentError('The selected quote is not identified as a user message in this record')
    elif quote not in content:raise CommitmentError('The exact request quote must occur in the supplied actual user-request evidence')
    return row,quote

def bind(state,root,specification,request,brief,request_quote,science_revision=False,revision_reason=None,implementation_reason=None):
    """Lock selected science. A title-only revision retains the scientific ID."""
    _active(state);root=Path(root).resolve();spec_ref=_ref(root,specification);brief_ref=_ref(root,brief)
    request_ref,quote=_request(root,request,request_quote)
    title,science=_spec(_load(root/spec_ref['path']));fingerprint=_science_identity(science)
    old=check_context(state)
    if old and Path(old['root'])!=root:raise CommitmentError('Retain the project root and original research history')
    same_science=bool(old and old['scientific_fingerprint']==fingerprint)
    same_implementation=bool(same_science and old['primary_experiments']==science['primary_experiments'])
    if same_implementation:
        state['research_commitment'].update(title=title,presentation=spec_ref)
        return state['research_commitment']
    if old and not same_science:
        if not science_revision or not revision_reason or not revision_reason.strip():
            raise CommitmentError('The fixed scientific question changed; preserve it or supply the actual new user request and a science-revision reason')
        if request_ref['sha256']==old['request']['sha256'] or quote==old['request_quote']:
            raise CommitmentError('A science revision needs the new actual user instruction, not the original request relabeled as permission')
    if same_science and not _text(implementation_reason,'Implementation revision reason'):
        raise CommitmentError('Record why the implementation changed while preserving the original question')
    version=(old['version'] if same_science else old['version']+1) if old else 1
    row={'schema_version':'research-commitment-1','id':old['id'] if same_science else uuid.uuid4().hex,'version':version,
        'phase_id':state['id'],'root':str(root),'specification':spec_ref,'request':request_ref,
        'brief':brief_ref,'request_quote':quote,'scientific_fingerprint':fingerprint,
        'title':title,**science,'implementation_version':old.get('implementation_version',1)+1 if same_science else 1,'authority_verified_by_tool':False}
    if old:row.update(previous_id=old['id'],revision_reason=implementation_reason.strip() if same_science else revision_reason.strip())
    record=root/'.research-commitments'/('v'+str(version)+'-'+uuid.uuid4().hex+'.json')
    record.parent.mkdir(parents=True,exist_ok=True)
    with record.open('x',encoding='utf-8') as handle:handle.write(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
    binding={**row,'record':_ref(root,record),'presentation':spec_ref}
    if old:state.setdefault('research_commitment_history',[]).append(state['research_commitment'])
    state['research_commitment']=binding
    state.pop('research_results',None);state.pop('research_delivery',None)
    state.setdefault('history',[]).append({'event':'research_implementation_revised' if same_science else 'research_commitment_revised' if old else 'research_commitment_bound',
        'id':row['id'],'version':version,'request':request_ref,'request_quote':quote})
    return binding

def check_context(state):
    binding=state.get('research_commitment')
    if not binding:return None
    root=Path(binding['root']);_verify(root,binding['record']);record=_load(root/binding['record']['path'])
    if record.get('phase_id')!=state['id'] or record.get('schema_version')!='research-commitment-1':
        raise CommitmentError('Research commitment belongs to another task')
    if any(binding.get(k)!=v for k,v in record.items() if k!='title'):
        raise CommitmentError('Research commitment identity changed; recover the immutable record')
    for key in ('specification','request','brief','presentation'):_verify(root,binding[key])
    _,science=_spec(_load(root/binding['presentation']['path']))
    if _science_identity(science)!=record['scientific_fingerprint'] or science['primary_experiments']!=record['primary_experiments']:
        raise CommitmentError('Presentation edit changed the fixed question or implementation; preserve and version the affected plan')
    return binding

def context(state):
    row=check_context(state)
    return {'commitment_id':row['id'],'commitment_version':row['version'],'experiment_fingerprints':_experiment_fingerprints(row)} if row else {}

def match_context(state,other):
    row=check_context(state)
    return bool(row and other.get('commitment_id')==row['id'] and other.get('commitment_version',row['version'])==row['version'])

def validate_work(state,question_ids=None,kind='primary',purpose='formal',execution='working',answer='unanswered',validity='unknown',results=None,root=None,experiment_id=None):
    row=check_context(state)
    if not row:return {} # Legacy absence remains unknown, never retroactively certified.
    if kind not in {'primary','supporting','exploration'} or purpose not in {'formal','diagnostic'}:
        raise CommitmentError('Use an explicit work kind and formal or diagnostic purpose')
    ids=list(dict.fromkeys(question_ids or []));known={q['id'] for q in row['questions']}
    if not set(ids)<=known or (not ids and kind!='exploration'):
        raise CommitmentError('Bind this work to known fixed question IDs, or label a genuine exploration explicitly')
    if execution not in EXECUTION_STATES or answer not in ANSWER_STATES or validity not in {'unknown','valid','invalid'}:
        raise CommitmentError('Record execution, answer and scientific validity separately')
    refs=[_ref(root or row['root'],p) for p in (results or [])]
    if root and Path(root).resolve()!=Path(row['root']):raise CommitmentError('Results must belong to this research project')
    if experiment_id:
        experiment=next((e for e in row['primary_experiments'] if e['id']==experiment_id),None)
        if not experiment or set(ids)!=set(experiment['question_ids']) or kind!='primary':
            raise CommitmentError('Primary experiment identity or its fixed question links changed')
    if answer=='answered' and (execution!='completed' or validity!='valid' or purpose!='formal' or not refs or kind=='exploration'):
        raise CommitmentError('An answer needs a completed, valid formal test with actual results; diagnostics and failure cannot answer the study')
    return {'commitment_id':row['id'],'question_ids':ids,'kind':kind,'purpose':purpose,
        'execution_state':execution,'answer_state':answer,'validity':validity,
        'result_refs':refs,'experiment_id':experiment_id,
        'experiment_fingerprint':_experiment_fingerprints(row).get(experiment_id),
        'result_observations':[_observation(row['root'],r) for r in refs]}

def _inputs(inputs):return {(str(Path(x['path']).resolve()),x['sha256']) for x in inputs}

def _require_inputs(root,inputs,rows,what):
    actual=_inputs(inputs)
    if any((str((Path(root)/x['path']).resolve()),x['sha256']) not in actual for x in rows):
        raise CommitmentError(what+' must actually consume the fixed commitment, plan, result index and complete primary results')

def validate_step(state,capability,inputs,question_ids=None,purpose='formal',kind='primary'):
    row=check_context(state)
    if not row:return {'purpose':purpose} if purpose!='formal' else {}
    if purpose not in {'formal','diagnostic'} or kind not in {'primary','supporting','exploration'}:raise CommitmentError('Unknown professional step purpose or work kind')
    ids=list(dict.fromkeys(question_ids if question_ids is not None else [q['id'] for q in row['questions']]))
    if (not ids and kind!='exploration') or not set(ids)<={q['id'] for q in row['questions']}:raise CommitmentError('Professional work must retain known research-question IDs or explicitly identify exploration')
    if capability=='manuscript-writing' and state.get('scope')=='full' and purpose=='formal':
        bound=_results(state)
        _require_inputs(row['root'],inputs,[row['record'],bound['research_plan'],bound['result_index']]+bound['result_refs'],'Full manuscript writing')
    return {**context(state),'question_ids':ids,'purpose':purpose,'kind':kind}

def _latest_experiment_unit(state,experiment):
    row=check_context(state);fingerprint=_identity(experiment);candidates=[]
    for i,(key,unit) in enumerate(state.get('work_units',{}).items()):
        if unit.get('commitment_id')==row['id'] and unit.get('experiment_id')==experiment['id'] and unit.get('experiment_fingerprint')==fingerprint:
            candidates.append((unit.get('at',''),i,key,unit))
    return max(candidates,key=lambda x:(x[0],x[1]))[2:] if candidates else (None,None)

def _source_files(state,capabilities,required,question_ids=None,experiment_id=None,experiment_fingerprint=None):
    """Verify actual outputs of registered formal source work, without judging it."""
    import capabilities as C
    import professional_flow as F
    actual=set();wanted=_inputs(required);rows=state.get('professional_steps',[])+state.get('professional_pending',[])
    for row in reversed(rows):
        if row.get('capability') not in capabilities or row.get('status') not in {'completed','eligible_for_handoff'} or not row.get('finished'):continue
        begin=_load(row['started']);done=_load(row['finished']);ctx=begin.get('phase') or {}
        if ctx.get('id')!=state['id'] or not match_context(state,ctx) or begin.get('purpose',ctx.get('purpose','formal'))!='formal':continue
        if capabilities=={'research-design'} and ctx.get('experiment_fingerprints')!=_experiment_fingerprints(check_context(state)):continue
        if question_ids and not set(question_ids)<=set(begin.get('question_ids',ctx.get('question_ids',[]))):continue
        if experiment_id and ctx.get('experiment_fingerprints',{}).get(experiment_id)!=experiment_fingerprint:continue
        outputs=_inputs(done.get('outputs',[]))
        if not outputs.intersection(wanted):continue
        F.check(_load(C.index_path()),begin,done);actual.update(outputs)
        if wanted<=actual:return
    raise CommitmentError('Use the actual current formal source-gated '+ '/'.join(sorted(capabilities))+' outputs; standalone files or checkpoint assertions are insufficient')

def _unit(state,key):
    row=check_context(state);unit=state.get('work_units',{}).get(key)
    if not isinstance(unit,dict) or unit.get('commitment_id')!=row['id']:
        raise CommitmentError('Result index points to missing or superseded scientific work: '+str(key))
    extra=validate_work(state,unit.get('question_ids'),unit.get('kind','primary'),unit.get('purpose','formal'),
        unit.get('execution_state','not_run'),unit.get('answer_state','unanswered'),unit.get('validity','unknown'),
        [x['path'] for x in unit.get('result_refs',[])],row['root'],unit.get('experiment_id'))
    if extra['result_refs']!=unit.get('result_refs'):
        raise CommitmentError('Actual result changed after checkpoint; recompute/reassess the affected answer')
    if extra['answer_state']!='answered':raise CommitmentError('The original question remains unanswered; execute or repair the decisive formal test')
    experiment=next((e for e in row['primary_experiments'] if e['id']==unit.get('experiment_id')),None)
    if experiment:
        latest,_=_latest_experiment_unit(state,experiment)
        if unit.get('experiment_fingerprint')!=_identity(experiment) or latest!=key:
            raise CommitmentError('A revised or later primary test supersedes this answer; repair the current experiment rather than reuse an old success')
    _source_files(state,{'analysis-execution','robustness-reproducibility'},
        [{'path':str(Path(row['root'])/r['path']),'sha256':r['sha256']} for r in unit['result_refs']],unit['question_ids'],unit.get('experiment_id'),unit.get('experiment_fingerprint'))
    return unit

def _result_content(state,root,index):
    row=check_context(state)
    if not isinstance(index,dict):raise CommitmentError('Result index must be an object')
    qs=index.get('questions',[]);es=index.get('experiments',[])
    if not isinstance(qs,list) or not isinstance(es,list):raise CommitmentError('Result index needs question and experiment rows')
    qmap={q.get('id'):q for q in qs};emap={e.get('id'):e for e in es}
    if len(qmap)!=len(qs) or len(emap)!=len(es):raise CommitmentError('Result-index IDs must be unique')
    knownq={q['id'] for q in row['questions']};knowne={e['id'] for e in row['primary_experiments']}
    if not set(qmap)<=knownq or not set(emap)<=knowne:raise CommitmentError('Unrelated results cannot replace the fixed research questions or primary experiments')
    result_refs={}
    for q in row['questions']:
        if q['id'] not in qmap:
            if q['required']:raise CommitmentError('Required original question is absent from the result index: '+q['id'])
            continue
        answer=qmap[q['id']];_text(answer.get('answer'),'Evidence-supported answer')
        keys=answer.get('work_units')
        if not isinstance(keys,list) or not keys:raise CommitmentError('Each claimed answer needs actual scientific work')
        for key in keys:
            unit=_unit(state,key)
            if q['id'] not in unit['question_ids']:raise CommitmentError('The cited test answers a different question')
    for e in row['primary_experiments']:
        item=emap.get(e['id'])
        if not item:raise CommitmentError('Primary experiment missing from results: '+e['id'])
        unit=_unit(state,item.get('work_unit'))
        if unit.get('experiment_id')!=e['id'] or set(unit['question_ids'])!=set(e['question_ids']):
            raise CommitmentError('Primary experiment was replaced by a different test')
        paths=item.get('results')
        if not isinstance(paths,list) or not paths:raise CommitmentError('Primary experiment needs its actual result files')
        actual=[_ref(root,p) for p in paths]
        if sorted(actual,key=lambda r:r['path'])!=sorted(unit['result_refs'],key=lambda r:r['path']):
            raise CommitmentError('Result index does not include the exact primary experiment outputs')
        for r in actual:result_refs[r['path']]=r
    return sorted(result_refs.values(),key=lambda r:r['path'])

def bind_results(state,root,research_plan,result_index):
    _active(state)
    row=check_context(state)
    if not row:raise CommitmentError('Bind the research commitment before indexing answers')
    if Path(root).resolve()!=Path(row['root']):raise CommitmentError('Results belong to another project')
    rp=_ref(root,research_plan);ri=_ref(root,result_index)
    _source_files(state,{'research-design'},[{'path':str(Path(root).resolve()/rp['path']),'sha256':rp['sha256']}])
    refs=_result_content(state,root,_load(Path(root)/ri['path']))
    result={'commitment_id':row['id'],'root':str(Path(root).resolve()),'research_plan':rp,'result_index':ri,'result_refs':refs}
    state['research_results']=result
    return result

def _results(state):
    row=check_context(state);bound=state.get('research_results')
    if not row or not bound or bound.get('commitment_id')!=row['id']:raise CommitmentError('Index the actual answers and primary experiments before writing the full manuscript')
    root=bound['root']
    for key in ('research_plan','result_index'):_verify(root,bound[key])
    _source_files(state,{'research-design'},[{'path':str(Path(root)/bound['research_plan']['path']),'sha256':bound['research_plan']['sha256']}])
    if _result_content(state,root,_load(Path(root)/bound['result_index']['path']))!=bound['result_refs']:
        raise CommitmentError('Primary results changed; repair the affected result index')
    return bound

def _location(root,manuscript,location,kind):
    if not isinstance(location,dict) or _ref(root,location.get('path',''))!=manuscript:
        raise CommitmentError('Each '+kind+' location must point to the actual manuscript')
    quote=_text(location.get('quote'),kind+' exact manuscript quote')
    content=A.output_text(Path(root)/manuscript['path'])
    if content is None or quote not in content:raise CommitmentError('Manuscript location quote is missing or changed: '+kind)
    headings=list(re.finditer(r'(?m)^(#{1,6})\s+(.+?)\s*$',content))
    patterns={'methods':r'method|方法','results':r'result|结果','conclusion':r'conclu|结论|discussion|讨论'}
    wanted=location.get('section')
    valid=False
    for i,h in enumerate(headings):
        title=h.group(2);level=len(h.group(1))
        if (title!=wanted if wanted is not None else not re.search(patterns[kind],title,re.I)):continue
        # A named section supplies the declared scientific role; professional
        # review judges it. Nested sample/estimation headings remain in Methods.
        end=next((later.start() for later in headings[i+1:] if len(later.group(1))<=level),len(content))
        if quote in content[h.end():end]:valid=True
    if not valid:raise CommitmentError('Place the actual scientific '+kind+' passage in its manuscript section, not only in logs or an unrelated paragraph')
    return location

def _coverage(state,root,manuscript,coverage):
    row=check_context(state);data=_load(Path(root)/coverage['path'])
    qs=data.get('questions',[]);es=data.get('experiments',[])
    if not isinstance(qs,list) or not isinstance(es,list):raise CommitmentError('Manuscript coverage needs question and experiment locations')
    qmap={q.get('id'):q for q in qs};emap={e.get('id'):e for e in es}
    if len(qmap)!=len(qs) or len(emap)!=len(es):raise CommitmentError('Duplicate manuscript coverage IDs')
    for q in row['questions']:
        if q['required'] and q['id'] not in qmap:raise CommitmentError('Original question missing from manuscript conclusions: '+q['id'])
        if q['id'] in qmap:_location(root,manuscript,qmap[q['id']].get('conclusion'),'conclusion')
    for e in row['primary_experiments']:
        if e['id'] not in emap:raise CommitmentError('Primary experiment missing from manuscript: '+e['id'])
        for kind in ('methods','results'):_location(root,manuscript,emap[e['id']].get(kind),kind)
    return data

def _professional(state,started,finished,capability):
    import capabilities as C
    import professional_flow as F
    begin=_load(started);done=_load(finished);ctx=begin.get('phase') or {}
    if begin.get('capability')!=capability or begin.get('purpose',ctx.get('purpose','formal'))!='formal' or ctx.get('id')!=state['id'] or not match_context(state,ctx):
        raise CommitmentError('Use this study\'s actual formal source-gated '+capability+' receipt')
    checked=F.check(_load(C.index_path()),begin,done)
    return begin,done,{'started':str(Path(started).resolve()),'finished':str(Path(finished).resolve()),
        'started_sha256':A.digest(started),'finished_sha256':A.digest(finished),'step_id':checked['step_id']}

def _semantic_report(done,questions,experiments,expression=False):
    for ref in done['outputs']:
        try:report=_load(ref['path'])
        except (ValueError,UnicodeError):continue
        if not isinstance(report,dict) or report.get('unresolved_required')!=[]:continue
        if expression:
            checks=report.get('meaning_checks')
            if not isinstance(checks,list):continue
            for item in checks:
                for key in ('before','after','assessment'):_text(item.get(key),'Polish meaning '+key)
            return ref,report
        qs=report.get('question_checks');es=report.get('experiment_checks')
        if not isinstance(qs,list) or not isinstance(es,list):continue
        if {x.get('id') for x in qs}!=set(questions) or {x.get('id') for x in es}!=set(experiments):continue
        for item in qs+es:
            _text(item.get('assessment'),'Scientific review assessment');_text(item.get('resolution'),'Scientific review resolution')
        for key in ('narrative_assessment','internal_process_assessment'):_text(report.get(key),key)
        return ref,report
    raise CommitmentError('Actual professional output must contain the semantic '+('polish-difference' if expression else 'question, experiment and narrative')+' review with no unresolved required issue; a passed boolean is insufficient')

def _meaning_coverage(before,after,checks):
    """Assess quote spans, independent of physical lines or Markdown wrapping."""
    def tokens(text):
        text=re.sub(r'(?m)^\s{0,3}#{1,6}\s+','',text)
        for pattern in (r'\*\*(.+?)\*\*',r'__(.+?)__',r'`([^`]+)`',r'(?<!\*)\*([^*\n]+)\*(?!\*)'):
            text=re.sub(pattern,r'\1',text,flags=re.S)
        return re.findall(r'\w+|[^\w\s]',text)
    old=tokens(before);new=tokens(after);covered={}
    for key,words in (('before',old),('after',new)):
        mask=[False]*len(words)
        for check in checks:
            quote=tokens(check[key]);size=len(quote)
            if not size:continue
            for i,word in enumerate(words):
                if word==quote[0] and words[i:i+size]==quote:mask[i:i+size]=[True]*size
        covered[key]=mask
    for tag,a,b,c,d in difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes():
        if tag!='equal' and (not all(covered['before'][a:b]) or not all(covered['after'][c:d])):
            raise CommitmentError('Every substantive manuscript change needs coverage by an assessed actual before/after quote span; an unrelated checked edit cannot cover a changed conclusion')

def _delivery(state,root,research_plan,result_index,manuscript,coverage,review_started,review_finished,expression_started=None,expression_finished=None):
    row=check_context(state);bound=_results(state)
    if _ref(root,research_plan)!=bound['research_plan'] or _ref(root,result_index)!=bound['result_index']:
        raise CommitmentError('Use the current bound execution plan and result index')
    manuscript=_ref(root,manuscript);coverage=_ref(root,coverage);data=_coverage(state,root,manuscript,coverage)
    begun,done,review=_professional(state,review_started,review_finished,'manuscript-review')
    base=[row['record'],bound['research_plan'],bound['result_index']]+bound['result_refs']
    _require_inputs(root,begun['inputs'],base,'Scientific manuscript review')
    required=[q['id'] for q in row['questions'] if q['required']];experiments=[e['id'] for e in row['primary_experiments']]
    semantic,_=_semantic_report(done,required,experiments);semantic=_ref(root,semantic['path'])
    delivered={'commitment_id':row['id'],'root':str(Path(root).resolve()),'manuscript':manuscript,'coverage':coverage,'review':review,'semantic_report':semantic}
    if expression_started or expression_finished:
        if not expression_started or not expression_finished:raise CommitmentError('Provide both actual expression receipts')
        prior=_ref(root,data.get('reviewed_coverage',''));old=_load(Path(root)/prior['path'])
        locations=[q['conclusion'] for q in old.get('questions',[])]+[e['methods'] for e in old.get('experiments',[])]
        if not locations:raise CommitmentError('Retain the reviewed manuscript coverage for incremental polish verification')
        old_manuscript=_ref(root,locations[0]['path']);_coverage(state,root,old_manuscript,prior)
        _require_inputs(root,begun['inputs'],[prior],'Scientific manuscript review')
        if (str((Path(root)/old_manuscript['path']).resolve()),old_manuscript['sha256']) not in _inputs(begun['inputs']+done['outputs']):
            raise CommitmentError('The reviewed manuscript must be an actual review input or revised output')
        eb,ed,expression=_professional(state,expression_started,expression_finished,'final-expression')
        _require_inputs(root,eb['inputs'],[old_manuscript,prior,semantic],'Incremental polishing')
        outputs=_inputs(ed['outputs'])
        if any((str((Path(root)/x['path']).resolve()),x['sha256']) not in outputs for x in (manuscript,coverage)):
            raise CommitmentError('Final manuscript and coverage must be actual polishing outputs')
        diff,report=_semantic_report(ed,required,experiments,True);diff=_ref(root,diff['path'])
        before=A.output_text(Path(root)/old_manuscript['path']);after=A.output_text(Path(root)/manuscript['path'])
        if before!=after and not report['meaning_checks']:raise CommitmentError('Changed wording needs actual before/after meaning checks, not just equal numbers')
        for item in report['meaning_checks']:
            if item['before'] not in before or item['after'] not in after:raise CommitmentError('Polish meaning check must quote the actual before and after manuscripts')
        _meaning_coverage(before,after,report['meaning_checks'])
        delivered.update(expression=expression,meaning_report=diff,reviewed_manuscript=old_manuscript,reviewed_coverage=prior)
    else:
        _require_inputs(root,begun['inputs'],[coverage],'Scientific manuscript review')
        if (str((Path(root)/manuscript['path']).resolve()),manuscript['sha256']) not in _inputs(begun['inputs']+done['outputs']):
            raise CommitmentError('Final manuscript must be actually read or revised by the professional review')
    return delivered

def bind_delivery(state,root,research_plan,result_index,manuscript,coverage,review_started,review_finished,expression_started=None,expression_finished=None):
    """Bind existing actual professional review; this never re-runs the review."""
    _active(state);bind_results(state,root,research_plan,result_index)
    delivered=_delivery(state,root,research_plan,result_index,manuscript,coverage,review_started,review_finished,expression_started,expression_finished)
    state['research_delivery']=delivered
    return delivered

def closure(state):
    row=check_context(state)
    if not row:
        if state.get('alignment_required'):raise CommitmentError('Recover/bind the original research agreement; legacy absence is unknown, not complete')
        return {'status':'unknown','reason':'legacy_missing_commitment','scientific_validity_certified':False}
    bound=_results(state);delivery=state.get('research_delivery')
    if not delivery or delivery.get('commitment_id')!=row['id']:raise CommitmentError('Attach actual question–experiment–manuscript coverage and professional semantic review before completion')
    for key in ('manuscript','coverage','semantic_report','meaning_report','reviewed_manuscript','reviewed_coverage'):
        if key in delivery:_verify(delivery['root'],delivery[key])
    for key in ('review','expression'):
        if key in delivery:
            r=delivery[key]
            if A.digest(r['started'])!=r['started_sha256'] or A.digest(r['finished'])!=r['finished_sha256']:
                raise CommitmentError('Professional review receipt changed')
    review=delivery['review'];expression=delivery.get('expression',{})
    actual=_delivery(state,delivery['root'],bound['research_plan']['path'],bound['result_index']['path'],delivery['manuscript']['path'],delivery['coverage']['path'],
        review['started'],review['finished'],expression.get('started'),expression.get('finished'))
    if actual!=delivery:raise CommitmentError('Scientific delivery attachment changed')
    return {'status':'covered_by_actual_work_and_review','commitment_id':row['id'],'required_questions':sum(q['required'] for q in row['questions']),
        'primary_experiments':len(row['primary_experiments']),'scientific_validity_certified':False,'semantic_truth_verified_by_tool':False}

def snapshot(state):
    try:row=check_context(state)
    except (ValueError,OSError,KeyError,TypeError) as error:
        # Preserve the original questions during recovery even when their exact
        # artifact cannot currently be verified. This copy grants no readiness.
        stored=state.get('research_commitment') or {}
        return {'status':'needs_recovery','id':stored.get('id'),'version':stored.get('version'),
            'title':stored.get('title'),'objects':stored.get('objects'),'relationship':stored.get('relationship'),
            'scope':stored.get('scope'),'completion_criteria':stored.get('completion_criteria'),
            'questions':[{k:q.get(k) for k in ('id','text','required')} |
                {'answer_state':'unknown','key_results':[],'verification':'unverified_stored_recovery_copy'}
                for q in stored.get('questions',[]) if isinstance(q,dict)],
            'record':stored.get('record'),'artifact_error':str(error),'identity_verified':False,
            'next_action':'Recover the exact missing or changed commitment artifacts while retaining these original questions; do not grant readiness from this unverified copy',
            'scientific_validity_certified':False}
    if not row:return {'status':'unknown','reason':'legacy_missing_commitment','questions':[]}
    units=state.get('work_units',{})
    questions=[]
    for q in row['questions']:
        experiments=[e for e in row['primary_experiments'] if q['id'] in e['question_ids']]
        statuses=[];answered=[];latest=[]
        for experiment in experiments:
            key,unit=_latest_experiment_unit(state,experiment)
            status={'id':experiment['id'],'execution_state':unit.get('execution_state','not_run') if unit else 'not_run',
                'answer_state':unit.get('answer_state','unanswered') if unit else 'unanswered'}
            if unit:
                latest.append(unit)
                if status['answer_state']=='answered':
                    try:
                        if unit.get('purpose')!='formal' or unit.get('execution_state')!='completed' or unit.get('validity')!='valid' or not unit.get('result_refs'):
                            raise CommitmentError('This recorded test does not answer the question')
                        if [_observation(row['root'],r) for r in unit['result_refs']]!=unit.get('result_observations'):
                            raise CommitmentError('Recorded result changed')
                        answered.append(unit)
                        status['verification']='recorded_with_unchanged_result_stats; full_hash_and_source_checks_at_readiness_or_closure'
                    except (ValueError,OSError,KeyError,TypeError):status.update(answer_state='unanswered',verification='affected_evidence_needs_reassessment')
            statuses.append(status)
        answer='answered' if statuses and all(s['answer_state']=='answered' for s in statuses) else 'inconclusive' if any(s['answer_state']=='inconclusive' for s in statuses) else 'unanswered'
        questions.append({**q,'answer_state':answer,'primary_experiments':statuses,
            'key_results':[r for u in answered for r in u.get('result_refs',[])],
            'next_action':next((u.get('next_action') for u in reversed(latest) if u.get('next_action')),
                'Execute or repair the planned primary test for '+q['id'])})
    return {'status':'bound','id':row['id'],'version':row['version'],'title':row['title'],'objects':row['objects'],'relationship':row['relationship'],
        'scope':row['scope'],'completion_criteria':row['completion_criteria'],'questions':questions,
        'record':row['record'],'next_action':state.get('next_action'),'scientific_validity_certified':False}

def main(argv=None):
    import phase_control as P
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--state',required=True)
    sub=parser.add_subparsers(dest='op',required=True)
    b=sub.add_parser('bind')
    for arg in ('root','specification','request','brief','request-quote'):b.add_argument('--'+arg,required=True)
    b.add_argument('--science-revision',action='store_true');b.add_argument('--revision-reason');b.add_argument('--implementation-reason')
    for op in ('results','delivery'):
        b=sub.add_parser(op)
        for arg in ('root','research-plan','result-index'):b.add_argument('--'+arg,required=True)
        if op=='delivery':
            for arg in ('manuscript','coverage','review-started','review-finished'):b.add_argument('--'+arg,required=True)
            b.add_argument('--expression-started');b.add_argument('--expression-finished')
    sub.add_parser('check');sub.add_parser('snapshot')
    args=parser.parse_args(argv)
    try:
        with P.locked(args.state):
            state=P.load(args.state)
            if args.op=='bind':result=bind(state,args.root,args.specification,args.request,args.brief,args.request_quote,args.science_revision,args.revision_reason,args.implementation_reason)
            elif args.op=='results':result=bind_results(state,args.root,args.research_plan,args.result_index)
            elif args.op=='delivery':result=bind_delivery(state,args.root,args.research_plan,args.result_index,args.manuscript,args.coverage,args.review_started,args.review_finished,args.expression_started,args.expression_finished)
            elif args.op=='check':result=closure(state)
            else:result=snapshot(state)
            if args.op in {'bind','results','delivery'}:P.save(args.state,state)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError) as error:
        print(json.dumps({'status':'alignment_repair_needed','error':str(error),'next_action':'Repair the affected evidence, test or manuscript while preserving the fixed original question; this tool does not close the research goal'},ensure_ascii=False),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
