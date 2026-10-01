#!/usr/bin/env python3
"""Internal worker: calls existing upstream code; does not implement search or EDA."""
import argparse
import importlib.util
import inspect
import json
import math
import sys
from pathlib import Path

def strict_clean(value):
    # Preserve an undefined numeric output as null, never as 0 or a successful value.
    if isinstance(value,float) and not math.isfinite(value):return None
    if isinstance(value,dict):return {str(k):strict_clean(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [strict_clean(v) for v in value]
    return value

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--adapter',choices=['researchstudio-search','scipilot-profile'],required=True)
    p.add_argument('--script',required=True);p.add_argument('--request',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();script=Path(a.script).resolve();request=json.loads(Path(a.request).read_text(encoding='utf-8-sig'))
    if not isinstance(request,dict):raise ValueError('request must be an object')
    if not script.is_file():raise FileNotFoundError('Selected upstream script does not exist')
    out=Path(a.out)
    if out.exists():raise FileExistsError('Do not overwrite upstream output')
    sys.path.insert(0,str(script.parent))
    spec=importlib.util.spec_from_file_location('academic_upstream',script)
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=module
    spec.loader.exec_module(module)
    if a.adapter=='researchstudio-search':
        query=request.get('query');start=request.get('start_year');end=request.get('end_year')
        if not isinstance(query,str) or not query.strip():raise ValueError('query must be a nonempty string')
        if type(start) is not int or type(end) is not int or not 1000<=start<=end<=9999:raise ValueError('Invalid years')
        maximum=request.get('max_results',10)
        if type(maximum) is not int or maximum<=0:raise ValueError('Positive integer max_results required')
        sources=request.get('sources')
        if not isinstance(sources,list) or not sources or any(not isinstance(s,str) for s in sources):raise ValueError('Choose actual sources explicitly')
        if set(sources)&{'model_knowledge','model-recall'}:raise ValueError('Model recall is not an API connector')
        parallel=request.get('parallel',False)
        if type(parallel) is not bool:raise ValueError('parallel must be boolean')
        kwargs=dict(query=query,start_year=start,end_year=end,max_results=maximum,sources=sources,parallel=parallel)
        for field in ['start_date','end_date']:
            if request.get(field) is not None:kwargs[field]=request[field]
        inspect.signature(module.search_papers).bind(**kwargs)
        result=module.search_papers(**kwargs)
    else:
        groups=request.get('groups',[])
        if not isinstance(groups,list) or any(not isinstance(g,str) for g in groups):raise ValueError('groups must be string list')
        source=Path(request['input']).resolve()
        if not source.is_file():raise FileNotFoundError('Profile input does not exist')
        inspect.signature(module.profile_data).bind(str(source),group_cols=groups)
        result=module.profile_data(str(source),group_cols=groups)
    with out.open('x',encoding='utf-8') as f:f.write(json.dumps(strict_clean(result),ensure_ascii=False,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':main()
