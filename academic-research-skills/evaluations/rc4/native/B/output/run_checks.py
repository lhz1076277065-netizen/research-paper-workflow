from pathlib import Path
from fractions import Fraction as F
import csv, json, math, platform, time

ROOT=Path(__file__).resolve().parent
def save(rel, obj):
    path=ROOT/rel; path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def write_csv(path, rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=list(rows[0]));out.writeheader();out.writerows(rows)
def multiply(A,B):
    return [[sum(a*b for a,b in zip(row,col)) for col in zip(*B)] for row in A]

def theory():
    P=[[F(0),F(1)],[F(1),F(0)]]; I=[[F(1),F(0)],[F(0),F(1)]]
    assert multiply(P,P)==I and P!=I
    A=I; powers=[]
    for n in range(7):
        powers.append({'n':n,'P_n':[[str(x) for x in row] for row in A]}); A=multiply(A,P)
    save('theory-known-principle/input.json', {'P':[[0,1],[1,0]],'epsilon_grid':[0,.001,.01,.1,.5,1],'horizon':100})
    save('theory-known-principle/result.json',{'counterexample_powers':powers,'known_formula':[{'epsilon':e,'TV_error_at_n100':abs(2*e-1)**100/2} for e in [0,.001,.01,.1,.5,1]],'checks':'Exact fraction P^2=I, P!=I passed'})

def networks():
    graphs={'A_closure':[(0,1),(1,2),(2,0),(3,4),(4,5),(5,3)],'B_integration':[(0,1),(1,2),(2,3),(3,4),(4,5),(5,0)]}
    save('equal-predictions/input.json',{'vertices':list(range(6)),'graphs':graphs,'operation':'deterministic synchronous SI, one seed, transmission probability 1, no recovery','steps':3,'seeds':list(range(6))})
    rows=[]; degrees={}
    for name,edges in graphs.items():
        neighbors={i:set() for i in range(6)}
        for u,v in edges: neighbors[u].add(v);neighbors[v].add(u)
        degrees[name]=sorted(map(len,neighbors.values()))
        for seed in range(6):
            infected={seed}
            for t in range(4):
                rows.append({'mechanism':name,'seed':seed,'t':t,'infected':len(infected)})
                infected |= set().union(*(neighbors[i] for i in infected))
    assert degrees['A_closure']==degrees['B_integration']==[2]*6
    assert {r['infected'] for r in rows if r['mechanism']=='A_closure' and r['t']==3}=={3}
    assert {r['infected'] for r in rows if r['mechanism']=='B_integration' and r['t']==3}=={6}
    write_csv(ROOT/'equal-predictions/result.csv',rows)
    save('equal-predictions/result.json',{'degree_sequences':degrees,'size_at_t3':{'A':3,'B':6},'changed_judgment':'Degree distributions cannot distinguish these models; controlled propagation distinguishes them. No empirical mechanism attribution is made.','checks':'All 6 seed locations enumerated; assertions passed'})

def initial():
    original={'source':'cases.json synthetic aggregate only','new_mean_error':1.12,'baseline_mean_error':1.00,'cost_ratio':2,'formal_test_opened':False}
    save('initial-failure/input.json',original)
    # Aggregate-compatible worlds are reasoning examples, not recovered pilot data.
    worlds={'uniform_worse':[(.2,1.12,1),(.8,1.12,1)],'boundary_advantage':[(.2,.6,1),(.8,1.25,1)]}
    summaries={k:{'new_mean':sum(p*n for p,n,b in v),'baseline_mean':sum(p*b for p,n,b in v),'groups':v} for k,v in worlds.items()}
    for v in summaries.values(): assert math.isclose(v['new_mean'],1.12) and math.isclose(v['baseline_mean'],1)
    save('initial-failure/result.json',{'error_increase_fraction':.12,'cost_increase_fraction':1,'aggregate_pareto_dominated':True,'compatible_synthetic_worlds':summaries,'next_action':'Recover paired development residuals and costs, validate identical inputs/splits/metric/budgets and implementation, then inspect prespecified failure regimes and remove expensive component in an ablation; keep formal test sealed.','not_inferable':'variance, paired uncertainty, significance, subgroup advantage, cause of failure, actual ablation result'})

def bike():
    folder=ROOT/'direction-no-data'
    rows=list(csv.DictReader((folder/'hour.csv').open()))
    assert rows and all(int(r['cnt'])==int(r['casual'])+int(r['registered']) for r in rows)
    groups={w:[r for r in rows if r['weathersit']==w] for w in sorted({r['weathersit'] for r in rows})}
    selected=rows[:5]+[g[0] for g in groups.values()]
    write_csv(folder/'sample.csv',selected)
    details={w:{'hours':len(g),'dates':len({r['dteday'] for r in g}),'mean_rental_count':sum(int(r['cnt']) for r in g)/len(g),'year_hours':{y:sum(r['yr']==y for r in g) for y in ['0','1']}} for w,g in groups.items()}
    timestamps={(r['dteday'],r['hr']) for r in rows}
    assert len(timestamps)==len(rows)
    save('direction-no-data/result.json',{'observed_records':len(rows),'first_date':min(r['dteday'] for r in rows),'last_date':max(r['dteday'] for r in rows),'unique_dates':len({r['dteday'] for r in rows}),'unique_hour_keys':len(timestamps),'weather_support':details,'checks':'All count identities and unique hour keys passed','unit':'one system-hour; dates/weather episodes are dependent blocks, not 17k independent experimental units','risk':'Current-hour observed weather is not an advance weather forecast; casual/registered leak target; total observed rentals may be censored by supply'})

def human():
    folder=ROOT/'human-collection'
    data={}
    for v in ['28_0','29_0']:
        rows=list(csv.DictReader((folder/v/'Task Statements.txt').open(encoding='utf-8-sig'),delimiter='\t'))
        data[v]={(r['O*NET-SOC Code'],r['Task ID']):r for r in rows}
        write_csv(folder/f'sample_{v}.csv',rows[:5])
    a,b=data.values(); common=set(a)&set(b)
    changed=[{'occupation':k[0],'task_id':k[1],'before':a[k]['Task'],'after':b[k]['Task'],'old_date':a[k].get('Date'),'new_date':b[k].get('Date')} for k in sorted(common) if a[k]['Task']!=b[k]['Task']]
    added=sorted(set(b)-set(a)); removed=sorted(set(a)-set(b))
    automation=['automat','robot','computer','programm','machine']
    examples=[r for r in changed if any(x in (r['before']+' '+r['after']).lower() for x in automation)]
    save('human-collection/result.json',{'version_record_counts':{v:len(rows) for v,rows in data.items()},'common_keys':len(common),'wording_changed':len(changed),'added_keys':len(added),'removed_keys':len(removed),'automation_keyword_changed':len(examples),'keyword_definition':automation,'pilot_scope':'Archive difference, not a causal estimate or validated automation label','automation_change_examples':examples[:10],'all_first_changes':changed[:10],'added_examples':[b[k] for k in added[:5]],'removed_examples':[a[k] for k in removed[:5]]})
    if changed: write_csv(folder/'changed_tasks.csv',changed)
    save('human-collection/added_removed.json',{'added':[b[k] for k in added],'removed':[a[k] for k in removed]})

if __name__=='__main__':
    start=time.monotonic()
    theory();networks();initial();bike();human()
    save('run_log.json',{'command':'python3 output/run_checks.py','python':platform.python_version(),'platform':platform.platform(),'elapsed_seconds':time.monotonic()-start,'exit_status':0,'checks':'All assertions passed','research_model':None})
    print((ROOT/'run_log.json').read_text())
