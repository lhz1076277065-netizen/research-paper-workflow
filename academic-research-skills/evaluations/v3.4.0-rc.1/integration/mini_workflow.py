"""Small complete SOFTWARE workflow: real stages and fresh output, no paper claim."""
import importlib.util,json,sys,subprocess
from pathlib import Path
out=Path(__file__).parent.resolve();root=out/'mini-flow-confirmed';root.mkdir(exist_ok=True)
p=out.parent/'repository/academic-research-skills/src/common/scripts/phase_control.py';s=importlib.util.spec_from_file_location('phase',p);P=importlib.util.module_from_spec(s);s.loader.exec_module(P)
state=root/'phase.json';assert not state.exists(),'Preserve prior test; do not reset'
(root/'feasibility.md').write_text('Question: does an active controlled local command create the promised artifact? Fixed software scope, no scholarly novelty. Decisive check: write event.json through runner, inspect value. Dependency: stdlib Python, available. Cost <1 second, budget 5 minutes. Failure: deliver software blocker, do not start research.\n')
s=P.init('full','miniature software delivery test only; no academic topic',minutes=3);P.advance(s,'design','feasibility.md',root,'software test budget');P.authorize(s,5,'User approved plan includes small complete software workflow validation')
(root/'design.md').write_text('Claim C1: an active allowed runner creates its fixed JSON output. Anti-claim: state says success but no artifact. Must-run: one real command; metric: event file exists and matches expected. No optional tests or models.\n');P.advance(s,'research','design.md',root,'execute fixed command',minutes=2);P.save(state,s)
cmd=[sys.executable,'-c',f'import json;from pathlib import Path;Path({str(root/"event.json")!r}).write_text(json.dumps({{"executed":True,"scope":"software"}}))']
r=P.run(state,cmd,root/'run.log','C1 actual execution','missing file ends validation',estimate=1);assert r['returncode']==0
assert json.loads((root/'event.json').read_text())=={'executed':True,'scope':'software'}
s=P.load(state);P.advance(s,'manuscript','event.json',root,'draft software result',minutes=1)
(root/'report.md').write_text('The active controlled command created event.json with executed=true and scope=software. Evidence is the actual artifact and child exit0. This validates one software path, not scholarly novelty, autonomous research quality or all host tools. Evidence sufficient for this short report; no additional experiments.\n')
P.advance(s,'delivery','report.md',root,'deliver source and evidence',minutes=1);P.save(state,s)
closed=subprocess.run([sys.executable,str(p),'--state',str(state),'close','--status','completed','--reason','artifact-bound report delivered, no new research','--evidence','report.md','--root',str(root),'--task-id','software-mini-flow'],capture_output=True,text=True);assert closed.returncode==0,closed.stderr;s=P.load(state)
try:P.run(state,cmd,root/'duplicate.log','no restart','terminal completion')
except P.PhaseError:pass
else:raise AssertionError('Completed flow restarted')
assert not (root/'duplicate.log').exists();(root/'observations.json').write_text(json.dumps({'fresh_command_executed':True,'artifact_checked':True,'stages':[x['stage'] for x in s['history'] if x['event']=='stage_exit']+['delivery'],'terminal_restart_denied':True,'host_goal_state':s['host_goal_state'],'scientific_paper_completed':False},indent=2))
print('complete software flow and terminal refusal verified')
