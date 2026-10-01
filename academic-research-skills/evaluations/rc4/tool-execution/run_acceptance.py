import importlib.util,json,urllib.request
from pathlib import Path
SCRIPT=Path('/Users/luca/Documents/ChatGPT/学术skill/iteration-20260930061350/repository/academic-research-skills/src/common/scripts/environment.py')
spec=importlib.util.spec_from_file_location('rc4_environment',SCRIPT);e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
root=Path(__file__).parent
metadata=json.loads((root/'pypi-metadata.json').read_text())
if e.resources()['os']=='Darwin' and e.resources()['architecture']=='arm64':
    remote=json.load(urllib.request.urlopen('https://pypi.org/pypi/mlx/json',timeout=30))
    metadata['mlx']={'version':remote['info']['version'],'license':remote['info'].get('license'),'license_expression':remote['info'].get('license_expression'),'requires_python':remote['info'].get('requires_python')}
    e.write(root/'pypi-metadata.json',metadata)
packages=[{'spec':name+'=='+row['version'],'import':{'scikit-learn':'sklearn'}.get(name,name)} for name,row in metadata.items()]
task={'request':'Representative rc.4 installation and scientific software execution acceptance; manufactured checks, not an original scientific claim','service':'execute','runtime':{'backend':'python','packages':packages},'executor':{'role':'executor','actor_scope':'current_host'},'research_model':{'role':'research_model','purpose':'Train and evaluate a local Ridge prediction algorithm on manufactured analytic data','source':'https://scikit-learn.org/stable/modules/linear_model.html#ridge-regression-and-classification','revision':metadata['scikit-learn']['version'],'license':'BSD-3-Clause','local':True,'free_to_use':True,'license_allows_research':True}}
e.write(root/'task.json',task)
e.write(root/'preflight.json',e.plan(task))
result=e.ensure(task,root,apply=True,allow_network=True,force_isolated=True,timeout=300)
e.write(root/'environment.json',result)
print(json.dumps({'status':result['status'],'missing_before':result['observed']['missing_packages'],'installation_executed':result['installation_executed'],'python':result.get('python'),'logs':result.get('logs')}),flush=True)
if not result.get('ready'):raise SystemExit(1)
for backend in ['cpu','numpy']+(['mlx-cpu','mlx-gpu'] if 'mlx' in metadata else []):
    value=e.calibrate(task,root,backend,48 if backend=='cpu' else 128,force_isolated=True,timeout=90)
    e.write(root/(backend+'-calibration.json'),value)
    print(json.dumps({'backend':backend,'execution':value['research_execution'],'numeric':value.get('calibration')}),flush=True)
script=root/'professional_chain.py'
value=e.run_command(task,root,['{python}',str(script)],outputs=['symbolic-result.json','molecule-project.sdf','molecule-descriptors.csv','research-model.json','heldout-predictions.csv','software-result.json'],force_isolated=True,timeout=90)
e.write(root/'professional-execution.json',value)
print(json.dumps({'execution':value['research_execution'],'outputs':value.get('outputs'),'stdout':value.get('execution',{}).get('stdout')}),flush=True)
if value['research_execution']!='passed':raise SystemExit(1)
