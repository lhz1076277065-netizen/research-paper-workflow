#!/usr/bin/env python3
"""Run alpha.4 setup tests in bounded class-level processes and aggregate evidence."""
from pathlib import Path
from datetime import datetime,timezone
import argparse
import io
import json
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
SUITES=['SelectionTests','InstallTests','ResearchTypeTests','PortableTests']
SCOPES={
 'SelectionTests':'Task-specific dependency selection, preflight and permission boundaries; actual local interpreter probes.',
 'InstallTests':'Actual venv, offline pip install of a SYNTHETIC wheel, import, reuse, explicit script execution and failure/timeout prevention. Not an upstream scientific package.',
 'ResearchTypeTests':'16 project-defined research profiles and structured nonnumeric evidence routing; not scientific validity or natural-language agent testing.',
 'PortableTests':'Actual file copy/text export/local Git mirror fixture plus preflight/profile checks in 19 isolated module copies. Not native host installation.'}
class Recorded(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cases=[]
    def startTest(self,t):super().startTest(t);print(t.id(),flush=True)
    def addSuccess(self,t):super().addSuccess(t);self.cases.append({'test':t.id(),'status':'passed'})
    def addFailure(self,t,e):super().addFailure(t,e);self.cases.append({'test':t.id(),'status':'failed'})
    def addError(self,t,e):super().addError(t,e);self.cases.append({'test':t.id(),'status':'error'})
    def addSkip(self,t,r):super().addSkip(t,r);self.cases.append({'test':t.id(),'status':'skipped','reason':r})

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--suite',choices=SUITES);args=p.parse_args()
    out=ROOT/'test-results';out.mkdir(exist_ok=True)
    if args.suite:
        import test_portability
        stream=io.StringIO()
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(getattr(test_portability,args.suite))
        r=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Recorded).run(suite)
        report={'version':(ROOT/'VERSION').read_text().strip(),'timestamp':datetime.now(timezone.utc).isoformat(),'python':sys.version.split()[0],
         'suite':args.suite,'scope':SCOPES[args.suite],'tests_run':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped),'passed':r.wasSuccessful(),
         'real_local_venv_and_pip_executed':args.suite=='InstallTests','installed_fixture_is_scientific_package':False,
         'native_host_installation_verified':False,'scientific_validity_certified':False,'cases':r.cases}
        suffix='-'+args.suite
        (out/('portability-validation'+suffix+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (out/('portability-tests'+suffix+'.txt')).write_text(stream.getvalue(),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k!='cases'},ensure_ascii=False,indent=2))
        if not r.wasSuccessful():print(stream.getvalue())
        return 0 if r.wasSuccessful() else 1
    reports=[];runner_errors=[]
    for name in SUITES:
        print('Running '+name,flush=True)
        target=out/('portability-validation-'+name+'.json')
        # Avoid reading a prior successful summary if this child never completes.
        if target.exists():target.unlink()
        try:
            process=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--suite',name],capture_output=True,text=True,encoding='utf-8',timeout=120)
            (out/('portability-runner-'+name+'.txt')).write_text(process.stdout+process.stderr,encoding='utf-8')
            if target.exists():reports.append(json.loads(target.read_text(encoding='utf-8')))
            if process.returncode:runner_errors.append({'suite':name,'returncode':process.returncode})
        except subprocess.TimeoutExpired:runner_errors.append({'suite':name,'status':'runner_timeout'})
    result={'version':(ROOT/'VERSION').read_text().strip(),'timestamp':datetime.now(timezone.utc).isoformat(),
            'scope':'Four separately executed local software test classes; no synthetic content is scientific evidence.',
            'tests_run':sum(x['tests_run'] for x in reports),'failures':sum(x['failures'] for x in reports),
            'errors':sum(x['errors'] for x in reports)+len(runner_errors),'skipped':sum(x['skipped'] for x in reports),
            'passed':len(reports)==len(SUITES) and not runner_errors and all(x['passed'] for x in reports),
            'runner_errors':runner_errors,'cases':[c for x in reports for c in x['cases']],
            'real_local_venv_and_pip_executed':any(x.get('real_local_venv_and_pip_executed') for x in reports),
            'native_host_installation_verified':False,'scientific_validity_certified':False}
    (out/'portability-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},ensure_ascii=False,indent=2))
    return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
