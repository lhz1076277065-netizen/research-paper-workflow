#!/usr/bin/env python3
"""Run standard-library engineering tests and persist honest scope/results."""
from pathlib import Path
import datetime
import io
import json
import sys
import unittest
import test_suite

class RecordedResult(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.cases=[]
    def addSuccess(self,test):
        super().addSuccess(test);self.cases.append({'test':test.id(),'status':'passed'})
    def addFailure(self,test,err):
        super().addFailure(test,err);self.cases.append({'test':test.id(),'status':'failed'})
    def addError(self,test,err):
        super().addError(test,err);self.cases.append({'test':test.id(),'status':'error'})
    def addSkip(self,test,reason):
        super().addSkip(test,reason);self.cases.append({'test':test.id(),'status':'skipped','reason':reason})

def main():
    root=Path(__file__).resolve().parents[1]
    output=root/'test-results';output.mkdir(exist_ok=True)
    stream=io.StringIO()
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_suite)
    result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=RecordedResult).run(suite)
    (output/'engineering-tests.txt').write_text(stream.getvalue(),encoding='utf-8')
    report={'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'python_version':sys.version.split()[0], 'scope':'Engineering structure and isolated filesystem tests only',
      'skill_directories_tested':len(test_suite.SKILLS),'tests_run':result.testsRun,
      'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
      'passed':result.wasSuccessful(),'cases':result.cases,
      'synthetic_fixtures_are_research_evidence':False,
      'agent_behavior_evaluations_executed':False,'real_paper_end_to_end_executed':False,
      'journal_or_dataset_integrations_tested':False,
      'host_installation_tested':False,'scientific_validity_certified':False}
    (output/'engineering-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='cases'},ensure_ascii=False,indent=2))
    if not result.wasSuccessful():print(stream.getvalue())
    return 0 if result.wasSuccessful() else 1

if __name__=='__main__':raise SystemExit(main())
