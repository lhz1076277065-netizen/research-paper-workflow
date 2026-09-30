#!/usr/bin/env python3
"""Record OFFLINE integration-policy tests separately from native agent evaluations."""
from pathlib import Path
from datetime import datetime,timezone
import io,json,sys,unittest
import test_integration
class Recorded(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cases=[]
    def addSuccess(self,t):super().addSuccess(t);self.cases.append({'test':t.id(),'status':'passed'})
    def addFailure(self,t,e):super().addFailure(t,e);self.cases.append({'test':t.id(),'status':'failed'})
    def addError(self,t,e):super().addError(t,e);self.cases.append({'test':t.id(),'status':'error'})
    def addSkip(self,t,r):super().addSkip(t,r);self.cases.append({'test':t.id(),'status':'skipped','reason':r})
root=Path(__file__).resolve().parents[1];stream=io.StringIO()
suite=unittest.defaultTestLoader.loadTestsFromModule(test_integration)
r=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Recorded).run(suite)
out=root/'test-results';out.mkdir(exist_ok=True)
report={'version':'3.0.0-alpha.4','timestamp':datetime.now(timezone.utc).isoformat(),'python':sys.version.split()[0],
 'scope':'Offline structured routing/contract tests and real local subprocess adapter tests with SYNTHETIC STUBS, not real upstream services',
 'tests_run':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped),'passed':r.wasSuccessful(),
 'standalone_modules_tested':len(test_integration.SKILLS),'real_upstream_scripts_executed':False,'live_network_backends_tested':False,
 'natural_language_agent_evaluations_executed':False,'host_native_installation_tested':False,'real_paper_end_to_end_executed':False,
 'synthetic_data_is_scientific_evidence':False,'scientific_validity_certified':False,'cases':r.cases}
(out/'integration-policy-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'integration-policy-tests.txt').write_text(stream.getvalue())
print(json.dumps({k:v for k,v in report.items() if k!='cases'},ensure_ascii=False,indent=2))
if not r.wasSuccessful():print(stream.getvalue())
raise SystemExit(0 if r.wasSuccessful() else 1)
