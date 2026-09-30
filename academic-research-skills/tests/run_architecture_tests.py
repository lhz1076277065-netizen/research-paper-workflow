#!/usr/bin/env python3
"""Run alpha.3 tests and preserve precise, bounded evidence."""
from pathlib import Path
from datetime import datetime,timezone
import io,json,sys,unittest
import test_architecture
class Recorded(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cases=[]
    def addSuccess(self,t):super().addSuccess(t);self.cases.append({'test':t.id(),'status':'passed'})
    def addFailure(self,t,e):super().addFailure(t,e);self.cases.append({'test':t.id(),'status':'failed'})
    def addError(self,t,e):super().addError(t,e);self.cases.append({'test':t.id(),'status':'error'})
    def addSkip(self,t,r):super().addSkip(t,r);self.cases.append({'test':t.id(),'status':'skipped','reason':r})
root=Path(__file__).resolve().parents[1];stream=io.StringIO()
r=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Recorded).run(unittest.defaultTestLoader.loadTestsFromModule(test_architecture))
out=root/'test-results';out.mkdir(exist_ok=True)
report={'version':'3.0.0-alpha.4','timestamp':datetime.now(timezone.utc).isoformat(),'python':sys.version.split()[0],
 'scope':'Offline operation routing, native result-envelope acceptance, dependency graph, reproducible build, real subprocess import/signature tests with synthetic upstream stubs; 19 isolated standalone return-contract checks',
 'tests_run':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped),'passed':r.wasSuccessful(),
 'real_upstream_scripts_executed':False,'native_agent_behavior_evaluated':False,'scientific_validity_certified':False,'cases':r.cases}
(out/'architecture-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'architecture-tests.txt').write_text(stream.getvalue())
print(json.dumps({k:v for k,v in report.items() if k!='cases'},ensure_ascii=False,indent=2))
if not r.wasSuccessful():print(stream.getvalue())
raise SystemExit(0 if r.wasSuccessful() else 1)
