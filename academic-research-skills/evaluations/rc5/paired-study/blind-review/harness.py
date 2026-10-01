"""Task-local read/score recorder; no role in runtime skill execution."""
import argparse, hashlib, json, statistics, time
from pathlib import Path

HERE = Path(__file__).resolve().parent

def baseline(x, params):
    """Known two-sided clipped CUSUM; missing samples make no update."""
    calibration=[v for v in x[:64] if v is not None]
    mu=statistics.median(calibration)
    scale=max(.25,1.4826*statistics.median(abs(v-mu) for v in calibration))
    plus=minus=0.
    for t,v in enumerate(x[64:],64):
        if v is None: continue
        z=max(-params['clip'],min(params['clip'],(v-mu)/scale))
        plus=max(0.,plus+z-params['k']); minus=max(0.,minus-z-params['k'])
        if max(plus,minus)>params['h']: return t
    return -1

def evaluate(detector, params, data):
    rows=[]; start=time.perf_counter()
    for case in data:
        alarm=detector(case['x'],dict(params))
        if isinstance(alarm,bool) or not isinstance(alarm,int) or alarm < -1 or alarm >= len(case['x']):
            raise ValueError('detector must return first 0-based alarm or -1')
        tau=case['tau']; false=alarm>=0 and (tau is None or alarm<tau)
        delay=alarm-tau if tau is not None and alarm>=tau else None
        hit=delay is not None and delay<=60
        loss=90 if false or (tau is not None and not hit) else (delay if hit else 0)
        rows.append({'id':case['id'],'condition':case['condition'],'tau':tau,'alarm':alarm,
                     'false_alarm':false,'hit':hit,'delay':delay,'loss':loss})
    groups={}
    for group in sorted({r['condition'] for r in rows}):
        block=[r for r in rows if r['condition']==group]
        groups[group]={'n':len(block),'false_alarms':sum(r['false_alarm'] for r in block),
                      'hits':sum(r['hit'] for r in block),'mean_loss':statistics.mean(r['loss'] for r in block)}
    return {'mean_loss':statistics.mean(r['loss'] for r in rows),'false_alarms':sum(r['false_alarm'] for r in rows),
            'hits':sum(r['hit'] for r in rows),'runtime_seconds':time.perf_counter()-start,'groups':groups,'rows':rows}

def score(detector, params, data_path, output_dir, name):
    """Every validation evaluation appends an actual call record and saves all rows."""
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    path=Path(data_path); report=evaluate(detector,params,json.loads(path.read_text()))
    report.update(name=name,params=params,data_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    with (output_dir/'score-events.jsonl').open('a') as stream:
        stream.write(json.dumps({k:v for k,v in report.items() if k!='rows'})+'\n')
    (output_dir/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n')
    return {k:v for k,v in report.items() if k!='rows'}

def read_file(library, relative, output_dir):
    library=Path(library).resolve(); path=(library/relative).resolve()
    if library not in path.parents: raise ValueError('read must stay inside supplied library')
    body=path.read_text(); event={'path':relative,'characters_emitted':len(body),
                                 'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    with (output_dir/'read-events.jsonl').open('a') as stream: stream.write(json.dumps(event)+'\n')
    print(body)

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('library');p.add_argument('relative');p.add_argument('output_dir')
    a=p.parse_args(); read_file(a.library,a.relative,a.output_dir)
