#!/usr/bin/env python3
"""Prepare/run paired host evaluations. No model, provider, or agent API is assumed.

The adapter receives --request/--output-equivalent paths via placeholders in an
explicit argv list and must write an answer file. Command success is not a quality
score. Requests are synthetic evaluation materials, not empirical findings.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys,time,random,shutil

CASES=[
 {'id':'local-edit','skill':'manuscript-writing','prompt':'只润色以下结果段，保留数值和关联解释，不扩写整篇论文。',
  'material':'合成评估材料，不是实测数据：在120条独立记录中，调整后关联估计为0.24，95%置信区间为0.10到0.38。原段：我们可能非常有限地发现了一种或许有意义的关系，但是这也可能有不少局限。'},
 {'id':'formal-proof','skill':'analysis-execution','prompt':'证明实数样本的平方偏差和由样本均值唯一最小化，n>=1；给出完整推导。无需数据下载或软件安装。','material':'定义 S(a)=sum_i (x_i-a)^2，x_i 为任意有限实数。'},
 {'id':'abstract-only','skill':'paper-deep-reading','prompt':'从给定摘要提取研究问题、方法和能确认的证据；说明哪些模型或图表细节需要原文。只处理这段材料。',
  'material':'合成摘要：本文比较两种河流温度预测方法，在三个站点采用按年份划分的外部时段评价。方法B的平均绝对误差低于方法A。此材料没有样本量、具体数值、模型名称、图像或全文。'},
 {'id':'journal-only','skill':'journal-intelligence','prompt':'仅根据研究简介提出两个适合进一步核查的期刊候选。可联网时核查当前官方scope并给来源；无法联网时不要假称已核查。不重写论文或启动实验。',
  'material':'合成研究简介：跨城市公开温度和土地利用数据的空间观察研究，目标读者是城市环境与可持续发展研究者；没有因果识别设计。'},
 {'id':'novel-route','skill':'topic-novelty','prompt':'提出两个值得验证的跨学科研究路线，说明机制、最近邻检索策略及最小验证。大胆构思，不把构思说成已证明新颖。',
  'material':'研究方向：借鉴控制理论改善科学计算中自适应数值精度的选择。仅有研究兴趣，没有已完成实验。'},
]

def save(p,obj):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def hashfile(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def snapshot(source,target,manifest):
    source=Path(source).resolve()
    for p in source.rglob('*'):
        if not p.resolve().is_relative_to(source):raise ValueError('Skill resource outside module')
    shutil.copytree(source,target,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo','.DS_Store'))
    files={p.relative_to(target).as_posix():hashfile(p) for p in sorted(target.rglob('*')) if p.is_file()}
    save(manifest,{'source':str(source),'root':str(target),'files':files})
    return {'root':str(target),'manifest':str(manifest),'manifest_sha256':hashfile(manifest)}

def verify_request(request):
    entry=request.get('skill_entry')
    if entry and hashfile(entry)!=request['skill_entry_sha256']:raise ValueError('Evaluation entry changed')
    identity=request.get('skill_snapshot')
    if identity:
        if hashfile(identity['manifest'])!=identity['manifest_sha256']:raise ValueError('Evaluation identity changed')
        for rel,digest in load(identity['manifest'])['files'].items():
            p=(Path(identity['root'])/rel).resolve()
            if not p.is_relative_to(Path(identity['root']).resolve()) or hashfile(p)!=digest:raise ValueError('Evaluation reference changed: '+rel)
    for ref in request.get('material_files',[]):
        if hashfile(ref['path'])!=ref['sha256']:raise ValueError('Evaluation material changed')

def read_resources(request,paths,trace,kind='project',line_start=1,line_end=None):
    if kind not in {'project','professional','material'}:raise ValueError('Unknown resource kind')
    if line_start<1 or line_end is not None and line_end<line_start:raise ValueError('Invalid line range')
    events=[];texts=[]
    identity=request.get('skill_snapshot')
    if identity and hashfile(identity['manifest'])!=identity['manifest_sha256']:raise ValueError('Evaluation identity changed')
    for path in paths:
        p=Path(path).resolve();raw=p.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        if kind=='project':
            if not identity or not p.is_relative_to(Path(identity['root']).resolve()):raise ValueError('Resource outside frozen Skill')
            rel=p.relative_to(Path(identity['root']).resolve()).as_posix()
            if load(identity['manifest'])['files'].get(rel)!=digest:raise ValueError('Evaluation reference changed: '+rel)
        elif kind=='material':
            expected={str(Path(r['path']).resolve()):r['sha256'] for r in request.get('material_files',[])}
            if expected.get(str(p))!=digest:raise ValueError('Resource outside frozen materials')
        elif identity and p.is_relative_to(Path(identity['root']).resolve()):raise ValueError('Use project kind for frozen Skill resources')
        body=raw.decode('utf-8');lines=body.splitlines(keepends=True)
        displayed=''.join(lines[line_start-1:line_end])
        events.append({'path':str(p),'kind':kind,'sha256':digest,'source_bytes':len(raw),
                       'line_start':line_start,'line_end':line_end,'displayed_chars':len(displayed),
                       'display_sha256':hashlib.sha256(displayed.encode()).hexdigest(),
                       'read_at':datetime.now(timezone.utc).isoformat()})
        texts.append(displayed)
    p=Path(trace);p.parent.mkdir(parents=True,exist_ok=True)
    # One append keeps a multi-file read together; each task owns its trace.
    with p.open('a',encoding='utf-8') as f:f.write(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events))
    return texts

def resource_metrics(trace,initial_text=''):
    events=[json.loads(line) for line in Path(trace).read_text().splitlines()] if Path(trace).is_file() else []
    unique={(e['path'],e['sha256']):e['source_bytes'] for e in events}
    displays={(e['path'],e['display_sha256']) for e in events}
    return {'coverage':'instrumented_reads_only','initial_entry_chars':len(initial_text),
            'read_events':len(events),'unique_resources':len(unique),'unique_resource_bytes':sum(unique.values()),
            'resource_display_chars':sum(e['displayed_chars'] for e in events),
            'exact_repeated_displays':len(events)-len(displays),
            'input_tokens':None,'cached_input_tokens':None,'output_tokens':None,
            'peak_context_tokens':None,'cost':None}

def prepare(skills,out,comparison=None,repetitions=1,cases_file=None,evaluation_kind='development'):
    if repetitions<1:raise ValueError('repetitions must be positive')
    if evaluation_kind not in {'development','same_version_repeat','unseen_material','deployment'}:raise ValueError('Unknown evaluation kind')
    cases=CASES
    material_files={}
    if cases_file:
        base=Path(cases_file).resolve().parent;cases=load(cases_file)
        if isinstance(cases,dict):cases=cases.get('cases')
        if not isinstance(cases,list) or not cases:raise ValueError('cases must be a nonempty array')
        import re
        seen=set()
        for i,case in enumerate(cases):
            if not isinstance(case,dict) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',str(case.get('id',''))) or case['id'] in seen:raise ValueError('Unique canonical case id required')
            seen.add(case['id'])
            if not isinstance(case.get('prompt'),str) or not case['prompt'].strip() or not isinstance(case.get('skill'),str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',case['skill']):raise ValueError('Case needs prompt and canonical skill name')
            paths=case.get('material_files',[])
            if not isinstance(paths,list) or any(not isinstance(x,str) for x in paths):raise ValueError('material_files must be an array of paths')
            if not isinstance(case.get('material',''),str):raise ValueError('material must be text')
            texts=[case.get('material','')];refs=[]
            for rel in paths:
                path=(base/rel).resolve()
                if not path.is_relative_to(base) or not path.is_file():raise ValueError('Material missing/outside cases directory')
                texts.append('## '+rel+'\n'+path.read_text(encoding='utf-8'));refs.append({'path':str(path),'sha256':hashfile(path)})
            case=dict(case);case['material']='\n\n'.join(texts);material_files[case['id']]=refs
            cases[i]=case
    root=Path(out).absolute()
    if root.exists():raise ValueError('Use a fresh evaluation directory')
    root.mkdir(parents=True)
    arms={'without-skill':None,'release':Path(skills).resolve()}
    if comparison:arms['comparison']=Path(comparison).resolve()
    jobs=[];snapshots={}
    for case in cases:
        for arm,skillroot in arms.items():
            for rep in range(repetitions):
                key=(arm,case['skill']);identity=None
                if skillroot:
                    if key not in snapshots:
                        target=root/'snapshots'/arm/case['skill']
                        snapshots[key]=snapshot(skillroot/case['skill'],target,root/'identities'/(arm+'.'+case['skill']+'.json'))
                    identity=snapshots[key]
                entry=Path(identity['root'])/'SKILL.md' if identity else None
                job={'case_id':case['id'],'condition':arm,'replicate':rep,'synthetic_material':True,
                     'evaluation_kind':evaluation_kind,'skill_snapshot':identity,
                     'user_prompt':case['prompt'],'material':case['material'],
                     'material_files':material_files.get(case['id'],[]),
                     'skill_entry':str(entry) if entry else None,'skill_entry_sha256':hashfile(entry) if entry else None,
                     'initial_skill_text':entry.read_text(encoding='utf-8') if entry else '',
                     'adapter_contract':'Supply the prompt/material and the condition entry only; expose equal tools and permissions. Record additional resource reads and tool calls if the host can. Do not pass other-arm answers.'}
                name=f"{case['id']}.{arm}.{rep}"
                path=root/'requests'/(name+'.json');save(path,job)
                jobs.append({'id':name,'request':str(path),'request_sha256':hashfile(path)})
    random.Random(7).shuffle(jobs)
    report={'schema':'host-evaluation-2','status':'prepared_not_run','evaluation_kind':evaluation_kind,'jobs':jobs,
      'controls':'Keep actual model/version, tools, permissions, budgets and sampling equal. Repeated fresh contexts; shared-context reading is not independent A/B.',
      'scoring':'Blindly inspect real answers and traces for task completion, correctness, unsupported claims, useful novelty, questions and context/tool cost. No automatic scientific quality claim.'}
    save(root/'suite.json',report);return report

def run(suite,command,out,host_label,model_label,timeout=180):
    import math
    if not math.isfinite(timeout) or timeout<=0:raise ValueError('timeout must be positive and finite')
    if not isinstance(command,list) or not command or any(not isinstance(x,str) for x in command):raise ValueError('command must be an argv list')
    if not any('{request}' in x for x in command) or not any('{output}' in x for x in command):raise ValueError('command needs {request} and {output} placeholders')
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
    from environment import _run
    root=Path(out).absolute()
    if root.exists():raise ValueError('Use a new run directory')
    root.mkdir(parents=True);rows=[];run_start=time.monotonic()
    for job in suite['jobs']:
        request=Path(job['request'])
        if hashfile(request)!=job['request_sha256']:raise ValueError('Evaluation input changed: '+job['id'])
        payload=load(request);verify_request(payload)
        work=root/job['id'];work.mkdir();output=work/'answer.txt'
        argv=[x.replace('{request}',str(request)).replace('{output}',str(output)) for x in command]
        start=time.monotonic()
        try:
            execution=_run(argv,work,'adapter',timeout)
            status='answer_received' if execution['status']=='passed' and output.is_file() and output.stat().st_size else 'adapter_failed_or_empty'
            code=execution['returncode']
        except (OSError,subprocess.TimeoutExpired) as exc:
            status='adapter_error';code=None;(work/'error.txt').write_text(str(exc))
        verify_request(payload)
        rows.append({'job':job['id'],'run_id':job['id'],'parent_run_id':root.name,'role':'user_task',
                     'evaluation_kind':payload.get('evaluation_kind','development'),
                     'status':status,'returncode':code,'elapsed_seconds':time.monotonic()-start,
                     'resource_metrics':resource_metrics(work/'resource_reads.jsonl',payload.get('initial_skill_text','')),
                     'answer_sha256':hashfile(output) if output.is_file() else None,'quality_evaluated':False})
    report={'status':'execution_recorded','host_label':host_label,'model_label':model_label,'identity_source':'operator_supplied',
            'runs':rows,'quality_evaluated':False,'ability_improvement_established':False,
            'wall_seconds':time.monotonic()-run_start,'cumulative_task_seconds':sum(r['elapsed_seconds'] for r in rows),
            'command_success_is_model_quality':False,'recorded_at':datetime.now(timezone.utc).isoformat()}
    save(root/'execution.json',report);return report

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('prepare');a.add_argument('--skills',required=True);a.add_argument('--comparison-skills');a.add_argument('--out',required=True);a.add_argument('--repetitions',type=int,default=1);a.add_argument('--cases');a.add_argument('--evaluation-kind',default='development')
    a=sub.add_parser('run');a.add_argument('--suite',required=True);a.add_argument('--command-json',required=True);a.add_argument('--out',required=True);a.add_argument('--host-label',required=True);a.add_argument('--model-label',required=True);a.add_argument('--timeout',type=float,default=180)
    a=sub.add_parser('read');a.add_argument('--request',required=True);a.add_argument('--trace',required=True);a.add_argument('--kind',choices=['project','professional','material'],default='project');a.add_argument('--line-start',type=int,default=1);a.add_argument('--line-end',type=int);a.add_argument('paths',nargs='+')
    a=p.parse_args()
    try:
        if a.action=='read':
            for body in read_resources(load(a.request),a.paths,a.trace,a.kind,a.line_start,a.line_end):print(body,end='' if body.endswith('\n') else '\n')
            return 0
        result=prepare(a.skills,a.out,a.comparison_skills,a.repetitions,a.cases,a.evaluation_kind) if a.action=='prepare' else run(load(a.suite),load(a.command_json),a.out,a.host_label,a.model_label,a.timeout)
        print(json.dumps({'status':result['status'],'jobs':len(result.get('jobs',result.get('runs',[]))),'record':str(Path(a.out)/('suite.json' if a.action=='prepare' else 'execution.json'))},ensure_ascii=False));return 3 if any(x['status']!='answer_received' for x in result.get('runs',[])) else 0
    except (ValueError,OSError,KeyError) as exc:print(json.dumps({'status':'error','error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
