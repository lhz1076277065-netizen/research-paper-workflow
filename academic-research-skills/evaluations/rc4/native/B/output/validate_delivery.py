from pathlib import Path
import csv, hashlib, json

ROOT=Path(__file__).resolve().parent
execution=json.loads((ROOT/'execution.json').read_text())
original=json.loads((ROOT.parent/'cases.json').read_text())
assert original==json.loads((ROOT/'original_requests.json').read_text())
assert len(execution['subcases'])==8
for case in execution['subcases']:
    assert Path(case['response_path']).is_file()
    assert all(Path(p).is_file() for p in case['artifacts'])
    assert (ROOT/case['id']/'request.txt').read_text().strip()==case['request']
assert json.loads((ROOT/'direction-no-data/result.json').read_text())['observed_records']==17379
assert json.loads((ROOT/'human-collection/result.json').read_text())['wording_changed']==44
assert json.loads((ROOT/'equal-predictions/result.json').read_text())['size_at_t3']=={'A':3,'B':6}
paragraph=(ROOT/'focused-paragraph/revision.md').read_text()
assert all(x in paragraph for x in ['0.757','0.898','白葡萄酒','留出分区','尚未做跨来源验证'])
assert (ROOT/'citation-time/revision.md').read_text().startswith('在第六个月评估时，两组参与者的表现存在组间差异。')
assert json.loads((ROOT/'author-pending/sync_audit.json').read_text())['delivery_status']=='not_submission_ready'

material={
'direction-no-data':[('direction-no-data/hour.csv','programmatic full CSV parse'),('direction-no-data/Readme.txt','Agent full text inspection'),('direction-no-data/sample.csv','Agent full text inspection'),('direction-no-data/result.json','Agent full text inspection')],
'human-collection':[('human-collection/28_0/Task Statements.txt','programmatic full TSV parse'),('human-collection/29_0/Task Statements.txt','programmatic full TSV parse'),('human-collection/changed_tasks.csv','Agent full text inspection'),('human-collection/result.json','Agent full text inspection')],
'theory-known-principle':[('theory-known-principle/input.json','generated and checked by executed script')],
'equal-predictions':[('equal-predictions/input.json','generated and checked by executed script')],
'initial-failure':[('initial-failure/input.json','generated from supplied synthetic request')],
'citation-time':[('citation-time/request.txt','supplied request reused in current context')],
'focused-paragraph':[('focused-paragraph/request.txt','supplied request reused in current context')],
'author-pending':[('author-pending/sync_input.json','generated and audited by script')]}
for case in execution['subcases']:
    entries=[]
    for relative,mode in material[case['id']]:
        p=ROOT/relative
        entries.append({'path':str(p),'characters':len(p.read_text(encoding='utf-8-sig')),'mode':mode})
    case['material_file_reads']=entries
    case['attached_skill_functions_run']=False
    case['custom_script_executed']=case.pop('functions_run',case.get('custom_script_executed',False))
execution['reading_count_note']='Unicode character counts refer to complete file sizes for deduplicated inspected guidance. Tool output truncation and rereads are noted; no token or cumulative display-count estimate is implied. Programmatic full reads are separated from Agent text inspection. Web readings are listed separately with read scope.'
execution['web_reads']=[
{'url':'https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset','scope':'dataset description, variables, file metadata and license'},
{'url':'https://www.onetcenter.org/db_releases.html','scope':'archive dates and available text package links'},
{'url':'https://www.onetcenter.org/license_db.html','scope':'CC BY4.0 and previous-version coverage'},
{'url':'https://www.onetcenter.org/dictionary/29.0/text/task_statements.html','scope':'fields, date semantics and example rows'},
{'url':'https://arxiv.org/html/2412.03307v1','scope':'abstract and full-text datasets/experiments sections III-IV'},
{'url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC9746329/','scope':'search-provided abstract summary and page identity; further reads CAPTCHA blocked'},
{'url':'https://www.netlab.tkk.fi/opetus/s38215/k04/Lectures/ch1.pdf','scope':'search-extracted theorem and PDF metadata; expanded reads returned Internal Error'},
{'url':'https://www.bls.gov/bls/congressional-reports/assessing-the-impact-of-new-technologies-on-the-labor-market.htm','scope':'overview pp web lines236-247'}]
execution['validation']={'command':'python3 output/validate_delivery.py','exit_status':0,'checks':'original request preservation, all8 output paths, core computed counts, network prediction difference, rewritten sentence/paragraph scope and not-ready manuscript status passed'}
(ROOT/'validation.log').write_text(execution['validation']['checks']+'\n')
execution['artifact_manifest']=[]
for p in sorted(ROOT.rglob('*')):
    if p.is_file() and p.name!='execution.json':
        raw=p.read_bytes();execution['artifact_manifest'].append({'path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
(ROOT/'execution.json').write_text(json.dumps(execution,ensure_ascii=False,indent=2))
print(execution['validation']['checks'])
