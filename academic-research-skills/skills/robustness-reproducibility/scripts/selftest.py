#!/usr/bin/env python3
"""Local portable smoke checks; optional real scientific-library computation.

No network, installs, model calls, or fixed hardware. A smoke report is not a
research-validation or native-host-activation certificate.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import os

def scientific(out):
    """Exercise actual installed libraries against known analytic identities."""
    import numpy as np
    import pandas as pd
    from scipy import integrate, stats
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    x=np.linspace(-2.0,2.0,21);y=2.0*x+1.0
    table=pd.DataFrame({'x':x,'y':y})
    table.to_csv(out/'analytic-input.csv',index=False)
    fit=stats.linregress(table.x,table.y)
    value,error=integrate.quad(np.sin,0.0,np.pi)
    assert abs(fit.slope-2.0)<1e-12 and abs(fit.intercept-1.0)<1e-12
    assert abs(value-2.0)<1e-12
    results={'material_kind':'manufactured analytic verification; not empirical research',
             'n':len(table),'slope':float(fit.slope),'intercept':float(fit.intercept),
             'integral_sin_0_pi':value,'quadrature_error_estimate':error}
    (out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    fig,ax=plt.subplots(figsize=(6,4))
    ax.plot(table.x,table.y,marker='o',label='Analytic verification data')
    ax.set(xlabel='x (dimensionless)',ylabel='y = 2x + 1',title='Local execution smoke test')
    ax.legend();fig.tight_layout()
    fig.savefig(out/'figure.svg');fig.savefig(out/'figure.png',dpi=150);plt.close(fig)
    (out/'report.md').write_text(
        '# Local computation smoke test\n\n'
        'These are manufactured analytic test inputs, not measured research data.\n\n'
        f'{len(table)} points from y=2x+1 give slope {fit.slope:.12g} and intercept {fit.intercept:.12g}. '
        f'The computed integral of sin(x) on [0, pi] is {value:.12g}.\n\n'
        'Sources: analytic-input.csv and results.json. Figure: figure.svg.\n'
        'This checks software and a small output chain; it is not a journal manuscript.\n')
    return results

def run(out,scientific_smoke=False):
    import environment as e
    import research31 as q
    import provider_runtime as b
    home=Path(__file__).resolve().parents[1]
    out=Path(out).expanduser().absolute();out.mkdir(parents=True,exist_ok=True)
    checks=[]
    def check(name,fn):
        try:
            detail=fn();checks.append({'name':name,'status':'passed','detail':detail})
        except Exception as exc:checks.append({'name':name,'status':'failed','error':str(exc)})
    def compile_files():
        files=list((home/'scripts').glob('*.py'))
        for p in files:compile(p.read_text(encoding='utf-8'),str(p),'exec')
        return {'files':len(files)}
    check('local_python_scripts',compile_files)
    check('mandatory_pinned_provider_registry',lambda: pinned_registry(b))
    check('designated_skill_source_scope',lambda: source_scope(q))
    task={'capability':'journal-intelligence','service':'matching','operation':'plan','request':'Local software check only'}
    check('focused_environment_needs_no_statistical_stack',lambda: no_packages(e,task))
    if scientific_smoke:
        req={'request':'Run numerical smoke check','service':'profile',
             'runtime':{'backend':'python','packages':[{'spec':n,'import':n} for n in ['numpy','pandas','scipy','matplotlib']]}}
        check('scientific_imports',lambda: verify_environment(e,req,out))
        if checks[-1]['status']=='passed':
            check('analytic_compute_plot_report',lambda: scientific(out))
            if checks[-1]['status']=='passed':
                check('analytic_artifact_consistency',lambda: output_handoff(b,out))
    passed=all(c['status']=='passed' for c in checks)
    result={'version':e.VERSION,'checked_at':datetime.now(timezone.utc).isoformat(),
            'platform':platform.system(),'architecture':platform.machine(),'python':sys.version.split()[0],
            'passed':passed,'checks':checks,'scientific_smoke_requested':scientific_smoke,
            'native_host_activation_tested':False,'model_ability_measured':False,
            'real_paper_lifecycle_tested':False,'output_directory':str(out)}
    (out/'selftest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

def source_scope(q):
    config=q.policy()
    for source in config['sources']:q.allowed_repo(source['repository'],config)
    try:q.allowed_repo('outside-library/research-skill',config)
    except q.ResearchError:return {'selected_sources':len(config['sources']),'outside_library_rejected':True,'ordinary_scientific_software_restricted':False}
    raise ValueError('Outside-library Skill was silently accepted')

def pinned_registry(b):
    import capabilities as C
    data=b.load(b.registry_path())
    index=C.load(C.index_path());approved={x['repository'] for x in index['capabilities']}
    if len(approved)!=14 or data.get('professional_source_policy')!='required_before_every_professional_step_no_host_fallback':
        raise ValueError('Mandatory designated-source registry is missing')
    expected={x['id'] for x in index['capabilities']+index.get('additional_entries',[])}
    providers=data['providers']
    if len(providers)!=len(expected) or {x['id'] for x in providers}!=expected:raise ValueError('Pinned source entries are missing or duplicated')
    for p in providers:
        c=C.entry(index,p['id'])
        if p['repository'] not in approved or p['commit']!=c['commit'] or p['entrypoint']!=c['entry']:
            raise ValueError('Provider identity differs from the verified source index')
    return {'sources':len(approved),'entries':len(expected),'policy':'mandatory source-first, no host fallback','source_execution_verified':False}

def no_packages(e,task):
    d=e.requirements_for(task)
    if d['packages']:raise ValueError('Unrelated packages selected')
    return 'no packages needed'

def verify_environment(e,task,out):
    d=e.ensure(task,out,apply=False)
    if d['status']!='environment_verified':raise ValueError('Required imports unavailable; prepare the selected environment first: '+d['status'])
    return {'status':d['status'],'python':d['python']}

def output_handoff(b,out):
    # A maintenance fixture does not impersonate source-guided professional work.
    files=[('results','results.json'),('figure','figure.svg'),('report','report.md')]
    results=json.loads((out/'results.json').read_text());report=(out/'report.md').read_text()
    for text in [f"{results['n']} points",f"slope {results['slope']:.12g}",f"intercept {results['intercept']:.12g}",f"is {results['integral_sin_0_pi']:.12g}"]:
        if text not in report:raise ValueError('Analytic report differs from the actual result: '+text)
    for _,path in files:
        if not (out/path).is_file() or not (out/path).stat().st_size:raise ValueError('Missing analytic artifact: '+path)
    receipt={'status':'engineering_fixture_checked','outputs':[{'role':role,'path':path,'sha256':b.sha(out/path)} for role,path in files],
        'professional_workflow_completed':False,'semantic_or_visual_review_performed_here':False,'scientific_validity_certified':False}
    b.write(out/'acceptance.json',receipt)
    return receipt

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out');parser.add_argument('--scientific-smoke',action='store_true')
    args=parser.parse_args()
    out=Path(args.out).expanduser() if args.out else Path(tempfile.mkdtemp(prefix='academic-selftest-'))
    if args.out and out.exists() and any(out.iterdir()):
        parser.error('Use a new output directory for this test run')
    result=run(out,args.scientific_smoke)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
