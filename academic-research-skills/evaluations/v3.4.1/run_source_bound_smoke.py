#!/usr/bin/env python3
"""Five-stage synthetic software flow, not a paper or scientific validation.

Uses pinned real guides, actual CSV count execution, strict handoff/phase CLIs,
and a stopped-run denial. Explicit fixture scope avoids external research.
"""
import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys
import time

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--suite',required=True);ap.add_argument('--output',required=True)
    a=ap.parse_args();suite=Path(a.suite).resolve();root=Path(a.output).resolve();root.mkdir(parents=True,exist_ok=False)
    scripts=suite/'scripts';phase=root/'phase.json';events=[];began=time.time()
    def run(label,script,*args,expected=0):
        cmd=[sys.executable,str(scripts/script),*map(str,args)];p=subprocess.run(cmd,capture_output=True,text=True,timeout=20)
        (root/(label+'.stdout.json')).write_text(p.stdout);(root/(label+'.stderr.txt')).write_text(p.stderr)
        events.append(dict(command=cmd,returncode=p.returncode,at=time.time()))
        if p.returncode!=expected:raise RuntimeError(label+': '+p.stderr+p.stdout)
        return json.loads(p.stdout) if p.stdout else None
    request=root/'request.md';request.write_text('Synthetic software validation only. Describe no-show proportions in twenty generated appointment rows; no randomization record or inference requested. Do not assert causality/significance/generalization, search literature or train models. Close the five-stage professional flow with traceable artifacts.')
    data=root/'appointments.csv'
    with data.open('w') as f:
        writer=csv.writer(f);writer.writerow(['appointment_id','group','no_show'])
        for g,n in [('reminder',1),('control',3)]:
            for i in range(10):writer.writerow([g+'-'+str(i+1),g,int(i<n)])
    run('phase-init','phase_control.py','--state',phase,'init','--scope','full','--objective','Authorized small synthetic skill behavior validation; no real research','--minutes','5','--authority','User authorized a five-minute total synthetic acceptance test')
    used=[]
    def step(name,capability,inputs,filename,text,quote,action,extra_outputs=()):
        start=root/(name+'-start.json');finish=root/(name+'-finish.json');out=root/filename
        r=run(name+'-begin','professional_flow.py','begin','--capability',capability,'--task',request,'--phase',phase,
            *sum((['--input',x] for x in inputs),[]),'--out',start)
        # The actual guide is preserved before the current output is written.
        guide=r['guide'];assert quote in guide
        if callable(text):text=text(start)
        out.write_text(text)
        outputs=[out]+list(extra_outputs)
        report=root/(name+'-work.json');actions=[]
        for output in outputs:
            actions.append(dict(source_file=json.loads(start.read_text())['source']['entry'].split(json.loads(start.read_text())['source']['root']+'/')[1],
                source_excerpt=quote,applied=action,output=str(output),output_excerpt=output.read_text()[:160]))
        report.write_text(json.dumps(dict(step_id=r['id'],scope='requested_step',omitted_required_work=[],functions_run=callable(text),actions=actions),indent=2)+'\n')
        run(name+'-finish','professional_flow.py','finish','--started',start,*sum((['--output',x] for x in outputs),[]),'--work-report',report,'--out',finish)
        run(name+'-check','professional_flow.py','check','--started',start,'--finished',finish)
        used.append(dict(capability=capability,source=r['source']['id'],started=str(start),finished=str(finish),output=str(out)))
        return out,start,finish
    def advance(stage,out,start,finish):
        run('to-'+stage,'phase_control.py','--state',phase,'advance','--stage',stage,'--evidence',out.name,'--root',root,
            '--next-action','Continue only the declared synthetic validation','--professional-started',start,'--professional-finished',finish)
    brief,s,f=step('intake','research-intake',[data],'question-card.md',
        '# Synthetic Research Question Card\nQuestion: what are the two descriptive no-show fractions?\nUnits: generated appointment rows, not real independent study participants.\nEvidence: the twenty-row CSV only.\nSupport: exact counts and denominators agree with raw rows.\nFalsification: duplicate IDs, missing outcomes or inconsistent counts invalidate the summary.\nCost: one local count; no external dependencies.\nNo innovation, causal or significance claim.\n',
        'support criteria, falsification criteria, and minimal next action',
        'Produced the fixed-question card with explicit units, evidence, support/falsification criteria and a single local next action.')
    advance('design',brief,s,f)
    design,s,f=step('design','research-design',[brief,data],'design.md',
        '# Claim-to-evidence plan for software fixture\nPrimary claim: CSV-derived descriptive fractions agree with the raw rows.\nAnti-claim to rule out: a denominator silently excludes appointments, or a count is called a causal/significant benefit.\nEvidence: unique IDs, twenty binary outcomes, counts per group and fixed ten-row denominators.\nCore block 1: validate IDs, values, missingness and group counts before calculating fractions.\nCore block 2: compare every reported value with the frozen output; stop on mismatch.\nRun order: validate -> count -> draft -> factual expression review.\nNo ablations, seeds, model training or additional benchmark needed for this declared task.\n',
        'Minimum convincing evidence',
        'Applied the claim/evidence and anti-claim workflow to two essential checks; excluded unrelated experiment blocks.')
    advance('research',design,s,f)
    def analyze(start):
        code=root/'count.py';result=root/'counts.json'
        code.write_text("import csv,json,sys\nfrom collections import Counter\nrows=list(csv.DictReader(open(sys.argv[1])))\nassert len(rows)==20 and len({r['appointment_id'] for r in rows})==20\nassert all(r['no_show'] in {'0','1'} and r['group'] in {'reminder','control'} for r in rows)\ncounts={g:{'n':sum(r['group']==g for r in rows),'no_show':sum(int(r['no_show']) for r in rows if r['group']==g)} for g in ['reminder','control']}\nassert all(v['n']==10 for v in counts.values())\nfor v in counts.values():v['fraction']=v['no_show']/v['n']\nopen(sys.argv[2],'w').write(json.dumps(counts,indent=2)+'\\n')\n")
        run('actual-count','phase_control.py','--state',phase,'run','--log',root/'count.log','--claim','Validate exact descriptive counts',
            '--decision','Mismatch closes the fixture route','--professional-started',start,'--',sys.executable,code,data,result)
        counts=json.loads(result.read_text());assert counts=={'reminder':{'n':10,'no_show':1,'fraction':.1},'control':{'n':10,'no_show':3,'fraction':.3}}
        return '# Descriptive-only analysis\nValidated twenty unique generated appointment IDs, binary outcomes and complete group labels. Reminder: 1/10 = 10%; control: 3/10 = 30%. Four of twenty total. No independent-study sampling or randomization record is established. No inferential test or causal effect was requested or estimated. Exact fractions come from counts.json and count.py; no scientific winner claim.\n'
    analysis,s,f=step('analysis','analysis-execution',[design,data],'analysis.md',analyze,
        'Frame the question before touching the data.',
        'Framed the requested descriptive estimand, checked units/IDs/missingness, actually executed CSV counts, and declined unsupported inferential/causal claims.')
    advance('manuscript',analysis,s,f)
    draft,s,f=step('writing','manuscript-writing',[analysis,root/'counts.json'],'draft.md',
        'In this synthetic example, four of twenty appointments were no-shows: one of ten in the reminder group and three of ten in the control group. These are descriptive counts; the supplied record does not establish random assignment, statistical significance, a causal benefit or applicability to real schools. This is a local test draft, not an approved scientific manuscript.\n',
        'Do not convert association into causation or non-significance into equivalence.',
        'Drafted only from the frozen exact counts; retained denominators and design/approval limits, with no fabricated inference.')
    advance('delivery',draft,s,f)
    final,s,f=step('expression','final-expression',[draft,root/'counts.json'],'final.md',
        'The synthetic reminder group had one no-show in ten appointments, compared with three in ten for the control group; the total was four in twenty. The record supports these descriptive counts. It does not establish random assignment, statistical significance, causality or applicability to real schools. The text remains a local validation draft.\n',
        '只提出证据能牢固支撑的主张。',
        'Led with the supported comparison, condensed repeated limitations once, and rechecked every numerator/denominator without removing material uncertainty.')
    run('complete','phase_control.py','--state',phase,'close','--status','completed','--reason','Synthetic source-bound five-stage fixture delivered; not a paper',
        '--evidence',final.name,'--root',root,'--task-id','synthetic-source-flow','--professional-started',s,'--professional-finished',f)
    marker=root/'restarted'
    run('restart-denied','phase_control.py','--state',phase,'run','--log',root/'restart.log','--claim','fixture','--decision','must stay stopped',
        '--professional-started',s,'--',sys.executable,'-c',f'open({str(marker)!r},"w").write("bad")',expected=2)
    assert not marker.exists() and not (root/'restart.log').exists()
    final_state=json.loads(phase.read_text());assert final_state['status']=='completed' and len(final_state['professional_steps'])==5
    receipt=dict(scope='Synthetic software flow only; not scientific validation',elapsed_seconds=time.time()-began,
        professional_steps=used,source_first_steps_completed=5,real_count_command_executed=True,terminal_restart_denied=True,
        state=final_state,commands=events,scientific_validity_certified=False)
    (root/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k not in {'commands','state'}}))

if __name__=='__main__':main()
