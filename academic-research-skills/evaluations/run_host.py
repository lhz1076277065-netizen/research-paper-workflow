#!/usr/bin/env python3
"""Prepare/run paired host evaluations. No model, provider, or agent API is assumed.

The adapter receives --request/--output-equivalent paths via placeholders in an
explicit argv list and must write an answer file. Command success is not a quality
score. Requests are synthetic evaluation materials, not empirical findings.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys,time,random

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

def prepare(skills,out,comparison=None,repetitions=1,cases_file=None):
    if repetitions<1:raise ValueError('repetitions must be positive')
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
    jobs=[]
    for case in cases:
        for arm,skillroot in arms.items():
            for rep in range(repetitions):
                entry=skillroot/case['skill']/'SKILL.md' if skillroot else None
                job={'case_id':case['id'],'condition':arm,'replicate':rep,'synthetic_material':True,
                     'user_prompt':case['prompt'],'material':case['material'],
                     'material_files':material_files.get(case['id'],[]),
                     'skill_entry':str(entry) if entry else None,'skill_entry_sha256':hashfile(entry) if entry else None,
                     'initial_skill_text':entry.read_text(encoding='utf-8') if entry else '',
                     'adapter_contract':'Supply the prompt/material and the condition entry only; expose equal tools and permissions. Record additional resource reads and tool calls if the host can. Do not pass other-arm answers.'}
                name=f"{case['id']}.{arm}.{rep}"
                path=root/'requests'/(name+'.json');save(path,job)
                jobs.append({'id':name,'request':str(path),'request_sha256':hashfile(path)})
    random.Random(7).shuffle(jobs)
    report={'schema':'host-evaluation-1','status':'prepared_not_run','jobs':jobs,
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
    root.mkdir(parents=True);rows=[]
    for job in suite['jobs']:
        request=Path(job['request'])
        if hashfile(request)!=job['request_sha256']:raise ValueError('Evaluation input changed: '+job['id'])
        for ref in load(request).get('material_files',[]):
            if hashfile(ref['path'])!=ref['sha256']:raise ValueError('Evaluation material changed: '+job['id'])
        work=root/job['id'];work.mkdir();output=work/'answer.txt'
        argv=[x.replace('{request}',str(request)).replace('{output}',str(output)) for x in command]
        start=time.monotonic()
        try:
            execution=_run(argv,work,'adapter',timeout)
            status='answer_received' if execution['status']=='passed' and output.is_file() and output.stat().st_size else 'adapter_failed_or_empty'
            code=execution['returncode']
        except (OSError,subprocess.TimeoutExpired) as exc:
            status='adapter_error';code=None;(work/'error.txt').write_text(str(exc))
        rows.append({'job':job['id'],'status':status,'returncode':code,'elapsed_seconds':time.monotonic()-start,
                     'answer_sha256':hashfile(output) if output.is_file() else None,'quality_evaluated':False})
    report={'status':'execution_recorded','host_label':host_label,'model_label':model_label,'identity_source':'operator_supplied',
            'runs':rows,'quality_evaluated':False,'ability_improvement_established':False,
            'command_success_is_model_quality':False,'recorded_at':datetime.now(timezone.utc).isoformat()}
    save(root/'execution.json',report);return report

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    a=sub.add_parser('prepare');a.add_argument('--skills',required=True);a.add_argument('--comparison-skills');a.add_argument('--out',required=True);a.add_argument('--repetitions',type=int,default=1);a.add_argument('--cases')
    a=sub.add_parser('run');a.add_argument('--suite',required=True);a.add_argument('--command-json',required=True);a.add_argument('--out',required=True);a.add_argument('--host-label',required=True);a.add_argument('--model-label',required=True);a.add_argument('--timeout',type=float,default=180)
    a=p.parse_args()
    try:
        result=prepare(a.skills,a.out,a.comparison_skills,a.repetitions,a.cases) if a.action=='prepare' else run(load(a.suite),load(a.command_json),a.out,a.host_label,a.model_label,a.timeout)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 3 if any(x['status']!='answer_received' for x in result.get('runs',[])) else 0
    except (ValueError,OSError,KeyError) as exc:print(json.dumps({'status':'error','error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
