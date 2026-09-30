#!/usr/bin/env python3
"""Run all local regression cases exactly once and save per-case results."""
from pathlib import Path
from datetime import datetime,timezone
import io,json,platform,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
class Result(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.cases=[]
    def addSuccess(self,test):super().addSuccess(test);self.cases.append({'id':test.id(),'status':'passed'})
    def addFailure(self,test,err):super().addFailure(test,err);self.cases.append({'id':test.id(),'status':'failed'})
    def addError(self,test,err):super().addError(test,err);self.cases.append({'id':test.id(),'status':'error'})
    def addSkip(self,test,reason):super().addSkip(test,reason);self.cases.append({'id':test.id(),'status':'skipped','reason':reason})
def main():
    out=ROOT/'test-results';out.mkdir(exist_ok=True);stream=io.StringIO()
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern='test_*.py')
    r=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(suite)
    (out/'regression.txt').write_text(stream.getvalue(),encoding='utf-8')
    groups={}
    for case in r.cases:
        k=case['id'].split('.')[0];groups[k]=groups.get(k,0)+1
    d={'version':(ROOT/'VERSION').read_text().strip(),'generated_at':datetime.now(timezone.utc).isoformat(),
       'tests_run':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skipped':len(r.skipped),
       'passed':r.wasSuccessful(),'groups':groups,'platform':platform.system(),'architecture':platform.machine(),
       'python':sys.version.split()[0],'cases':r.cases,
       'scope':'Local software regression. HTTP/source responses are synthetic fixtures unless separately reported.',
       'native_agent_behavior_evaluated':False,'real_paper_lifecycle_tested':False,'macos_native_tested':platform.system()=='Darwin'}
    (out/'regression.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in d.items() if k!='cases'},ensure_ascii=False,indent=2))
    if not r.wasSuccessful():print(stream.getvalue())
    return 0 if r.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
