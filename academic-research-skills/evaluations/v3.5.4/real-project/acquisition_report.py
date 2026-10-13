import csv, hashlib, json, pathlib, zipfile
r=pathlib.Path(__file__).resolve().parent
(r/'sources').mkdir(exist_ok=True)
rows=[]
for name,ident,expected in [('wine',109,178),('iris',53,150)]:
    p=r/'raw'/name/(name+'.data'); z=r/'raw'/(name+'.zip')
    with zipfile.ZipFile(z) as f: assert f.testzip() is None
    data=[v for v in csv.reader(p.open()) if v]
    assert len(data)==expected
    record={'dataset':name,'publisher':'UCI Machine Learning Repository','dataset_id':ident,
      'landing_page':f'https://archive.ics.uci.edu/dataset/{ident}/{name}',
      'download_url':f'https://archive.ics.uci.edu/static/public/{ident}/{name}.zip',
      'access_date':'2026-10-13','license':'CC BY 4.0',
      'citation':('Aeberhard, S. & Forina, M. (1992). Wine [Dataset].' if name=='wine' else 'Fisher, R. (1936). Iris [Dataset].'),
      'doi':('10.24432/C5PC7J' if name=='wine' else '10.24432/C56C76'),
      'version':f'Original {name}.data, official static archive retrieved 2026-10-13',
      'expected_rows':expected,'retrieved_rows':len(data),'removed_rows':0,
      'feature_columns':13 if name=='wine' else 4,
      'raw_sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),
      'raw_bytes':p.stat().st_size,'archive_bytes':z.stat().st_size,
      'archive_crc':'all members verified','dictionary_path':f'raw/{name}/{name}.names',
      'historical_correction_policy':('Preserve original iris.data; dictionary identifies differences at samples 35 and 38. No silent corrections.' if name=='iris' else 'Preserve original wine.data; units not supplied for every chemical variable, so do not invent them.')}
    (r/'sources'/f'{name}-metadata.json').write_text(json.dumps(record,indent=2))
    rows.append(record)
(r/'download-reconciliation.json').write_text(json.dumps({'datasets':rows,'managed_data_download_bytes':9776,'all_required_tables_downloaded':True,'headerless':True,'source_checksum_published':False},indent=2))
