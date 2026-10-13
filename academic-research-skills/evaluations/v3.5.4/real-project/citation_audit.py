import json,pathlib,re
R=pathlib.Path(__file__).resolve().parent
m=json.loads((R/'source-manifest.json').read_text())
chosen=[s for s in m['sources'] if s['evidence_id'] in ['E001','E002','E007','E008']]
entries=[]
for s in chosen:
    key=s['evidence_id']; fields={'author':' and '.join(s['authors']),'title':s['title'],'url':s['identifiers']['url'],'note':'Accessed 13 October 2026; metadata checked against the opened official record'}
    if s['year'] is not None:fields['year']=str(s['year'])
    if s['identifiers']['doi']:fields['doi']=s['identifiers']['doi']
    if key in ('E001','E002'):fields['howpublished']='UCI Machine Learning Repository dataset'
    if key=='E008':fields.update(eprint='2609.00065',archivePrefix='arXiv')
    entries.append('@misc{'+key+',\n'+',\n'.join('  '+k+' = {'+v+'}' for k,v in fields.items())+'\n}')
(R/'references-extracted.bib').write_text('\n\n'.join(entries)+'\n')
text=(R/'manuscript-draft.md').read_text();body,refs=text.split('## References')
assert set(re.findall(r'^\[(\d+)\]',refs,re.M))=={'1','2','3','4'}
assert all(str(n) in re.findall(r'\d+',','.join(re.findall(r'\[([0-9,]+)\]',body))) for n in range(1,5))
checks=[{'reference':'1','evidence_id':'E001','bibliographic_source':'https://archive.ics.uci.edu/dataset/109/winedataset','proposition_locator':'Additional Variable Information; Dataset Files; citation/license; original wine.names sections 4–9','checked_proposition':'Original dataset size/schema/classes and scaling suggestion, not method superiority','agent_checked':True,'human_verified':False},
{'reference':'2','evidence_id':'E002','bibliographic_source':'https://archive.ics.uci.edu/dataset/53/iris','proposition_locator':'Dataset Information; Variables Table; citation/license; original iris.names sections 4–9','checked_proposition':'150 records/4 cm features/3 balanced classes and historical original-version discrepancy','agent_checked':True,'human_verified':False},
{'reference':'3','evidence_id':'E007','bibliographic_source':'https://scikit-learn.org/stable/common_pitfalls.html','proposition_locator':'12.2 Data leakage; 12.2.1 How to avoid data leakage','checked_proposition':'Split before preprocessing; learned transform fitted on training only, applied consistently to train/test','agent_checked':True,'human_verified':False},
{'reference':'4','evidence_id':'E008','bibliographic_source':'https://arxiv.org/abs/2609.00065','proposition_locator':'Title, five-author list, submission/version history and DOI fields','checked_proposition':'Software/procedural resource attribution only, no performance assertion based on abstract','agent_checked':True,'human_verified':False}]
(R/'citation-audit.json').write_text(json.dumps({'references':checks,'in_text_reference_mapping':'all four used and all defined','manuscript_numbers_verified_by':'robustness-verification.json and consistency-manifest.json','source_type_syntax_repair':'website corrected to documented webpage enum before writing handoff','native_validate_citations':'unavailable because requests is absent; no native success claimed','unavailable_metadata':'Journal volume/pages are not applicable to the two data records, live documentation and cited arXiv record; documentation year not inferred from access date','no_bibliographic_fabrication':True},indent=2))
