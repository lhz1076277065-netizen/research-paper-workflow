#!/usr/bin/env python3
"""Task-scoped Python dependency preflight, managed install, verification and run.

Python >=3.10, standard-library bootstrap. Uses venv/pip rather than a new package
manager. No global installs, automatic system installer, API keys or LLM runtime.
Plan/doctor do not install. ensure --apply installs only an explicitly selected
recipe, within a project-owned venv, with network or an offline wheelhouse.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid

VERSION='3.2.0-rc.3'
SPEC=re.compile(r'^([A-Za-z0-9][A-Za-z0-9._-]*)(?:(>=|==)([0-9]+(?:\.[0-9]+)*))?$')
MODULE=re.compile(r'^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$')
TEXT_SERVICES={'read','extract','translate','draft','revise','review','figure-review','figure-plan','method-plan','landscape','matching','journal-match','ideate','novelty-check','synthesize','derive','prove','interpret','source-criticism'}
BACKENDS={'host','python','r','julia','node','latex','licensed','external'}

class EnvironmentError(ValueError):
    pass

def now():return datetime.now(timezone.utc).isoformat()
def load(path):return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path, value):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def profiles():return load(Path(__file__).resolve().parents[1]/'assets/environment-profiles.json')
def python_path(path):
    # Do not resolve symlinks: venv/bin/python may link to the base interpreter.
    p=Path(path).expanduser().absolute()
    if not p.is_file():raise EnvironmentError('Python interpreter does not exist: '+str(p))
    return str(p)
def venv_python(root, system=None):
    return Path(root)/('Scripts/python.exe' if (system or os.name)=='nt' else 'bin/python')

def validate_packages(packages):
    if not isinstance(packages,list):raise EnvironmentError('packages must be a list')
    out=[];seen={}
    def version(v):return tuple(int(x) for x in (v or '0').split('.'))
    def cmp(a,b):
        n=max(len(a),len(b));return (a+(0,)*(n-len(a))) >= (b+(0,)*(n-len(b)))
    for item in packages:
        if not isinstance(item,dict) or not isinstance(item.get('spec'),str) or not isinstance(item.get('import'),str):
            raise EnvironmentError('Each package needs spec and import')
        match=SPEC.fullmatch(item['spec'])
        if not match or not MODULE.fullmatch(item['import']):
            raise EnvironmentError('Use named packages with numeric >= or == here; complex requirements can use the upstream package manager')
        name=re.sub(r'[-_.]+','-',match.group(1).lower())
        row={'spec':item['spec'],'import':item['import'],'distribution':match.group(1)}
        if name in seen:
            position=seen[name];previous=out[position]
            if previous['import']!=row['import']:raise EnvironmentError('Conflicting import declarations: '+name)
            old=SPEC.fullmatch(previous['spec']);oo,ov=old.group(2),old.group(3);no,nv=match.group(2),match.group(3)
            if no is None:continue
            if oo is None:out[position]=row;continue
            if oo=='==' and no=='==':
                if not (cmp(version(ov),version(nv)) and cmp(version(nv),version(ov))):raise EnvironmentError('Conflicting dependency pins: '+name)
            elif oo=='==':
                if not cmp(version(ov),version(nv)):raise EnvironmentError('Pinned dependency below required minimum: '+name)
            elif no=='==':
                if not cmp(version(nv),version(ov)):raise EnvironmentError('Pinned dependency below required minimum: '+name)
                out[position]=row
            elif cmp(version(nv),version(ov)):out[position]=row
            continue
        seen[name]=len(out);out.append(row)
    return out

def requirements_for(task, book=None):
    if not isinstance(task,dict) or not isinstance(task.get('request'),str) or not task['request'].strip():raise EnvironmentError('A nonempty task request is required')
    book=book or profiles();runtime=task.get('runtime',{})
    if not isinstance(runtime,dict):raise EnvironmentError('runtime must be an object')
    service=task.get('service','');operation=task.get('operation','execute')
    if operation not in {'execute','produce','plan','review'}:raise EnvironmentError('Unknown operation')
    backend=runtime.get('backend')
    if backend is None:
        backend='host' if service in TEXT_SERVICES or operation in {'plan','review'} or task.get('capability')=='journal-intelligence' else 'python' if service in {'profile','plot','table','analyze'} else 'host'
    if backend not in BACKENDS:raise EnvironmentError('Unsupported backend; use host/external for other verified tools')
    groups=runtime.get('python_groups')
    explicit=groups is not None or 'packages' in runtime
    notes=[]
    if groups is not None and (not isinstance(groups,list) or any(not isinstance(x,str) for x in groups)):
        raise EnvironmentError('python_groups must be a list')
    if groups is None:
        groups=[]
        if backend=='python' and not explicit:
            if service=='profile':groups=['tabular']
            elif service=='plot':groups=['scipilot-plot'] if task.get('preferred_provider')=='scipilot.figure' else ['plotting']
            elif service=='table':groups=['tabular']
            elif service=='analyze':
                method=task.get('research_context',{}).get('method_family')
                group={'regression':'statistics','statistical':'statistics','prediction':'prediction','bayesian':'bayesian','symbolic':'symbolic'}.get(method)
                if group:groups=[group]
                else:notes.append('Select actual method/provider dependencies before Python analysis; no default statistical method is assumed.')
    unknown=set(groups)-set(book['groups'])
    if unknown:raise EnvironmentError('Unknown dependency groups: '+', '.join(sorted(unknown)))
    raw=[p for group in groups for p in book['groups'][group]]+runtime.get('packages',[])
    packages=validate_packages(raw)
    if backend!='python' and packages:raise EnvironmentError('Python packages require backend=python; do not install them for a non-Python route')
    binaries=runtime.get('required_binaries',[])
    if not isinstance(binaries,list) or any(not isinstance(x,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.+-]*',x) for x in binaries):
        raise EnvironmentError('required_binaries must be executable names, not shell commands')
    default_binary={'r':'Rscript','julia':'julia','node':'node','latex':'latexmk'}.get(backend)
    if default_binary:binaries=list(dict.fromkeys([default_binary]+binaries))
    return {'backend':backend,'groups':list(dict.fromkeys(groups)),'packages':packages,'binaries':binaries,
            'notes':notes,'dependency_selection':'explicit' if explicit else 'operation-based minimal recipe',
            'upstream_manifest_review_required':True}

# Isolated trusted-interpreter probe. No user source or provider is imported here.
PROBE=r'''
import importlib.util, importlib.metadata, json, sys, platform
payload=json.loads(sys.argv[1]); rows=[]
for p in payload:
    try:version=importlib.metadata.version(p['distribution'])
    except importlib.metadata.PackageNotFoundError:version=None
    try:available=importlib.util.find_spec(p['import']) is not None
    except (ValueError,ImportError,ModuleNotFoundError):available=False
    rows.append({'spec':p['spec'],'import':p['import'],'version':version,'module_available':available})
print(json.dumps({'executable':sys.executable,'python':list(sys.version_info[:3]),'prefix':sys.prefix,'base_prefix':sys.base_prefix,'platform':platform.system(),'machine':platform.machine(),'packages':rows,'venv_available':importlib.util.find_spec('venv') is not None,'pip_available':importlib.util.find_spec('pip') is not None}))
'''

def version_ok(version,spec):
    match=SPEC.fullmatch(spec);op,want=match.group(2),match.group(3)
    if version is None:return False
    if op is None:return True
    # Conservative numeric release comparison. Prerelease/custom versions require
    # an explicit verified recipe, not an optimistic guessed compatibility claim.
    release=version.split('+',1)[0]
    if not re.fullmatch(r'\d+(?:\.\d+)*',release):return False
    a=tuple(map(int,release.split('.')));b=tuple(map(int,want.split('.')))
    size=max(len(a),len(b));a=a+(0,)*(size-len(a));b=b+(0,)*(size-len(b))
    return a==b if op=='==' else a>=b

def probe(interpreter,requirements,timeout=30):
    command=[python_path(interpreter),'-I','-c',PROBE,json.dumps(requirements['packages'])]
    try:
        process=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=timeout)
    except (OSError,subprocess.TimeoutExpired) as e:raise EnvironmentError('Interpreter probe failed: '+str(e)) from e
    if process.returncode:raise EnvironmentError('Interpreter probe failed: '+process.stderr[-2000:])
    try:result=json.loads(process.stdout)
    except ValueError as e:raise EnvironmentError('Interpreter did not return a valid probe record') from e
    result['missing_packages']=[x['spec'] for x in result['packages'] if not x['module_available'] or not version_ok(x['version'],x['spec'])]
    result['missing_binaries']=[x for x in requirements['binaries'] if not shutil.which(x)]
    result['python_compatible']=tuple(result['python'][:2]) >= (3,10)
    result['checked_at']=now()
    result['probe_depth']='distribution metadata and module discoverability; not backend execution'
    result['host_features']={'vision':'not_probed','network':'not_probed','native_skill_loading':'not_probed','subagents':'not_required'}
    return result

def plan(task,interpreter=None,book=None):
    req=requirements_for(task,book)
    host=task.get('host',{})
    if not isinstance(host,dict):raise EnvironmentError('host must be an object')
    if host.get('mode')=='text-only':
        return {'schema_version':'environment-plan-1','version':VERSION,'task_sha256':digest(task),
                'requirements':req,'observed':{},'status':'needs_external_executor',
                'blockers':['A text-only model cannot install or execute. Use an authorized host/operator; protocol-only work can continue.'],
                'installation_executed':False,'ready':False,'scientific_validity_certified':False}
    observed=probe(interpreter or sys.executable,req)
    blocked=[]
    if not observed['python_compatible']:blocked.append('Python >=3.10 is required by the bootstrap')
    if observed['missing_binaries']:blocked.append('Install/authorize external runtime: '+', '.join(observed['missing_binaries']))
    if req['notes']:blocked.extend(req['notes'])
    if req['backend'] in {'licensed','external'}:blocked.append('External/ licensed runtime must be checked by the host; it cannot be installed by pip')
    if req['backend'] in {'r','julia','node','latex'}:blocked.append('Host must verify selected non-Python packages and actual tool execution; bundled installer manages Python only')
    return {'schema_version':'environment-plan-1','version':VERSION,'task_sha256':digest(task),
        'requirements':req,'observed':observed,'status':'needs_host_setup' if blocked else 'install_needed' if observed['missing_packages'] else 'preflight_ready',
        'blockers':blocked,'installation_executed':False,'scientific_validity_certified':False,
        'scope':'Selected local runtime only. Host tool permissions, provider APIs and scientific evidence require their own checks.'}

def _managed_dir(workspace,relative):
    root=Path(workspace).expanduser().resolve()
    target=(root/relative).resolve()
    if not target.is_relative_to(root) or target==root:raise EnvironmentError('Managed environment path escapes project')
    return target

def _run(command,logdir,label,timeout,env=None):
    if not math.isfinite(timeout) or timeout<=0:raise EnvironmentError('timeout must be positive and finite')
    logdir=Path(logdir);logdir.mkdir(parents=True,exist_ok=True)
    start=now();out=logdir/(label+'.stdout.log');err=logdir/(label+'.stderr.log')
    code=None;status='failed'
    with out.open('w',encoding='utf-8') as sout,err.open('w',encoding='utf-8') as serr:
        process=subprocess.Popen(command,stdout=sout,stderr=serr,cwd=str(logdir),env=env,start_new_session=(os.name=='posix'))
        try:
            code=process.wait(timeout=timeout);status='passed' if code==0 else 'failed'
        except subprocess.TimeoutExpired:
            if os.name=='posix':
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            else:
                # Host-level isolation is still required; terminate known Windows children.
                try:subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True,timeout=10)
                except (OSError,subprocess.SubprocessError):process.kill()
            process.wait();status='timeout'
    return {'command':command,'status':status,'returncode':code,'started_at':start,'finished_at':now(),
            'stdout':str(out),'stderr':str(err),'scope':'Actual subprocess, not scientific validation'}

def verify(interpreter,req,logdir,timeout=60,managed=False):
    checks=[]
    # Imports exercise the actual environment; this is stronger than discovery.
    code='import importlib, json; mods='+repr([x['import'] for x in req['packages']])+'; [importlib.import_module(x) for x in mods]; print(json.dumps({"imported":mods}))'
    checks.append(_run([python_path(interpreter),'-I','-c',code],logdir,'import-smoke',timeout))
    obs=probe(interpreter,req)
    if obs['pip_available'] and managed:
        checks.append(_run([python_path(interpreter),'-I','-m','pip','--isolated','check'],logdir,'pip-check',timeout))
    ready=all(x['status']=='passed' for x in checks) and not obs['missing_packages'] and not obs['missing_binaries'] and obs['python_compatible']
    return {'status':'environment_verified' if ready else 'verification_failed','checks':checks,'observed':obs,'ready':ready,'dependency_check_scope':'full pip check' if managed else 'selected imports and version bounds; shared interpreter unrelated package conflicts are not assessed'}

def ensure(task,workspace,*,interpreter=None,apply=False,allow_network=False,wheelhouse=None,force_isolated=False,timeout=300,book=None):
    if not math.isfinite(timeout) or timeout<=0:raise EnvironmentError('timeout must be positive and finite')
    initial=plan(task,interpreter,book);req=initial['requirements']
    if initial['status'] in {'needs_host_setup','needs_external_executor'}:return initial
    current=initial['observed']['executable']
    need_install=bool(initial['observed']['missing_packages']) or force_isolated
    if need_install and not apply:
        return {**initial,'status':'install_needed','next_action':'ensure --apply plus --allow-network or --wheelhouse; no installation has occurred'}
    identity={'requirements':req,'python':initial['observed']['python'],'base_python':current,'platform':initial['observed']['platform'],'machine':initial['observed']['machine']}
    planned_env=_managed_dir(workspace,'.academic/envs/'+digest(identity)[:16])
    managed_python=venv_python(planned_env)
    if need_install and req['packages'] and not allow_network and wheelhouse is None:
        marker=planned_env/'.academic-managed.json'
        reusable=marker.is_file() and load(marker).get('identity')==identity and managed_python.is_file()
        if not reusable or probe(managed_python,req)['missing_packages']:
            return {**initial,'status':'blocked_network_authorization','next_action':'Use an authorized index or an existing offline wheelhouse; no files installed'}
    wheelpath=Path(wheelhouse).expanduser().resolve() if wheelhouse else None
    if wheelpath and not wheelpath.is_dir():raise EnvironmentError('Wheelhouse must be an existing directory')
    root=Path(workspace).expanduser().resolve();root.mkdir(parents=True,exist_ok=True)
    logs=_managed_dir(root,'.academic/setup-runs/'+uuid.uuid4().hex[:12]);logs.mkdir(parents=True)
    steps=[];target=current;created=False;reused_managed=False
    if need_install:
        identity={'requirements':req,'python':initial['observed']['python'],'base_python':current,'platform':initial['observed']['platform'],'machine':initial['observed']['machine']}
        envroot=_managed_dir(root,'.academic/envs/'+digest(identity)[:16]);marker=envroot/'.academic-managed.json'
        if envroot.exists():
            if not marker.is_file() or load(marker).get('identity')!=identity:raise EnvironmentError('Refusing to reuse an unmanaged or mismatched environment')
            reused_managed=True
        else:
            envroot.mkdir(parents=True);write(marker,{'identity':identity,'status':'creating','created_at':now()})
            steps.append(_run([current,'-I','-m','venv',str(envroot)],logs,'create-venv',timeout));created=True
            if steps[-1]['status']!='passed':
                report={**initial,'status':'installation_failed','steps':steps,'logs':str(logs),'installation_executed':True}
                write(logs/'environment.json',report);return report
        target=str(venv_python(envroot))
        if not Path(target).is_file() and reused_managed:
            steps.append(_run([current,'-I','-m','venv',str(envroot)],logs,'repair-venv',timeout))
            if steps[-1]['status']!='passed':
                report={**initial,'status':'installation_failed','steps':steps,'logs':str(logs),'installation_executed':True}
                write(logs/'environment.json',report);return report
        # A previous unsuccessful install can be retried only in this owned slot.
        envobs=probe(target,req)
        if envobs['missing_packages']:
            command=[target,'-I','-m','pip','--isolated','install','--disable-pip-version-check','--no-input','--only-binary=:all:']
            help_check=_run([target,'-I','-m','pip','--isolated','help','install'],logs,'pip-capabilities',min(timeout,60))
            report_supported=help_check['status']=='passed' and '--report' in Path(help_check['stdout']).read_text(encoding='utf-8')
            if report_supported:command+=['--report',str(logs/'pip-install-report.json')]
            else:write(logs/'pip-report-unavailable.json',{'status':'not_supported_or_unverified','note':'Install logs and distribution snapshot retained; no fabricated pip report.'})
            if wheelpath:command+=['--no-index','--find-links',str(wheelpath)]
            else:command+=['--index-url','https://pypi.org/simple','--retries','1','--timeout','20']
            command += [x['spec'] for x in req['packages']]
            # Avoid unrelated pip environment configuration; do not inspect/log secrets.
            process_env={k:v for k,v in os.environ.items() if not k.startswith('PIP_')}
            process_env['PIP_CONFIG_FILE']=os.devnull
            steps.append(_run(command,logs,'pip-install',timeout,process_env))
            if steps[-1]['status']!='passed':
                report={**initial,'status':'installation_failed','steps':steps,'logs':str(logs),'python':target,'installation_executed':True}
                write(marker,{'identity':identity,'status':'failed','last_report':str(logs/'environment.json')});write(logs/'environment.json',report);return report
        checked=verify(target,req,logs,min(timeout,120),managed=True)
        write(marker,{'identity':identity,'status':checked['status'],'last_report':str(logs/'environment.json')})
    else:
        checked=verify(target,req,logs,min(timeout,120))
    # Freeze only local distributions; it is a snapshot, not a cross-platform hash lock.
    snapshot=[]
    frozen=_run([target,'-I','-c','import importlib.metadata as m,json; print(json.dumps(sorted([(d.metadata["Name"],d.version) for d in m.distributions()])))'],logs,'distribution-snapshot',min(timeout,60))
    if frozen['status']=='passed':
        try:snapshot=json.loads(Path(frozen['stdout']).read_text())
        except ValueError:pass
    report={**initial,'status':checked['status'],'ready':checked['ready'],'python':target,'logs':str(logs),
            'verification':checked,'installation_executed':bool(steps),'created_venv':created,'reused_managed_venv':reused_managed,
            'steps':steps,'resolved_distributions':snapshot,'reproducibility':'observed environment snapshot, not a complete wheel hash lock',
            'provider_executed':False,'native_host_installation_verified':False}
    write(logs/'environment.json',report)
    return report

def run_script(task,workspace,script,args=(),**options):
    path=Path(script).expanduser().resolve()
    if not path.is_file() or path.suffix!='.py':raise EnvironmentError('run requires an explicit existing local Python script')
    if task.get('runtime',{}).get('backend','python') not in {'python','host'}:raise EnvironmentError('Python run cannot execute another backend')
    # An explicit run chooses Python; raw provider instructions cannot cause this call.
    task=json.loads(json.dumps(task));task.setdefault('runtime',{})['backend']='python'
    report=ensure(task,workspace,**options)
    if report.get('ready') is not True:return {**report,'research_execution':'not_started'}
    before=file_sha(path)
    command=[report['python'],str(path)]+list(args)
    execution=_run(command,Path(report['logs'])/'execution','script',options.get('timeout',300))
    execution['script_sha256']=before;execution['script_unchanged']=path.is_file() and file_sha(path)==before
    result={**report,'research_execution':execution['status'],'execution':execution,'scientific_validity_certified':False}
    write(Path(report['logs'])/'execution.json',result);return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='action',required=True)
    for act in ['doctor','plan','ensure','run']:
        sub=subs.add_parser(act);sub.add_argument('--task',required=True);sub.add_argument('--python',dest='interpreter');sub.add_argument('--report')
        if act in {'ensure','run'}:
            sub.add_argument('--workspace',required=True);sub.add_argument('--apply',action='store_true');sub.add_argument('--allow-network',action='store_true');sub.add_argument('--wheelhouse');sub.add_argument('--isolated',action='store_true');sub.add_argument('--timeout',type=float,default=300)
        if act=='run':sub.add_argument('--script',required=True);sub.add_argument('script_args',nargs=argparse.REMAINDER)
    a=p.parse_args(argv)
    try:
        task=load(a.task)
        if a.action in {'doctor','plan'}:result=plan(task,a.interpreter)
        else:
            opts={'interpreter':a.interpreter,'apply':a.apply,'allow_network':a.allow_network,'wheelhouse':a.wheelhouse,'force_isolated':a.isolated,'timeout':a.timeout}
            if a.action=='ensure':result=ensure(task,a.workspace,**opts)
            else:
                args=a.script_args[1:] if a.script_args[:1]==['--'] else a.script_args
                result=run_script(task,a.workspace,a.script,args,**opts)
        if a.report:write(a.report,result)
        print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
        good=result['status'] in {'preflight_ready','environment_verified'} and result.get('research_execution','passed')=='passed'
        return 0 if good else 3
    except (OSError,ValueError,TypeError,KeyError,subprocess.SubprocessError) as e:
        report={'status':'error','error':str(e),'scientific_validity_certified':False}
        if a.report:write(a.report,report)
        print(json.dumps(report,ensure_ascii=False));return 2
if __name__=='__main__':raise SystemExit(main())
