from pathlib import Path
import hashlib,json,csv,zipfile
r=Path(__file__).resolve().parent
manifest=json.loads((r/'.research-data.json').read_text())
for name in ('wine','iris'):
    old=json.loads((r/'sources'/f'{name}-metadata.json').read_text())
    p=r/'raw'/name/(name+'.data')
    actual=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
    assert actual==old['raw_sha256']
    with zipfile.ZipFile(r/'raw'/(name+'.zip')) as z:assert z.testzip() is None
    assert sum(bool(x) for x in csv.reader(p.open()))==old['expected_rows']
    old.update(revalidated_under_manifest=manifest['id'],revalidation='Full current SHA256, original archive CRC and complete row counts; unchanged original official bytes reused without transfer',scientific_scope_changed=False)
    (r/'sources'/f'{name}-metadata-v2.json').write_text(json.dumps(old,indent=2))
s=(r/'retrieval-contract.md').read_text()+'\n\n## Version 2 actual source re-evaluation\n\nThe repaired design retains both complete original UCI tables, all features/labels, no extra populations and the same metrics. Compared access modes remain scientifically appropriate. The newly bound manifest needs exactly these existing tables; full current SHA256 matches original acquisition, archive CRC passes and all 178/150 rows are present. Reusing already downloaded authoritative bytes is the selected lowest-cost complete acquisition path. No transfer was repeated. Official data dictionaries remain available locally and are required for preparation. The missing-design-reference repair changes procedural support, not data, estimands or methods.\n'
(r/'sources'/'selection-v2.md').write_text(s)
