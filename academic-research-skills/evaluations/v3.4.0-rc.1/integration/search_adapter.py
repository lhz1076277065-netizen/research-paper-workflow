import contextlib,importlib.util,json,sys
from pathlib import Path
out=Path(__file__).parent
r=json.loads((out/'prepared/researchstudio-search.json').read_text())
p=Path(r['entry']).parent/'scripts/search_papers.py';sys.path.insert(0,str(p.parent))
s=importlib.util.spec_from_file_location('upstream_search',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
with (out/'search-function-stdout.log').open('w') as f,contextlib.redirect_stdout(f):
 result=m.search_papers('reproducible computational research',2010,2026,max_results=3,sources=['crossref'],parallel=False)
(out/'search-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'sources':list(result),'record_count':sum(len(v) for v in result.values()),'function':str(p)}))
