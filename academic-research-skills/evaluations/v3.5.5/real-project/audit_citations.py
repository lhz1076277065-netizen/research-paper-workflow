from pathlib import Path
import json,sys,importlib.util,subprocess,re
P=Path(__file__).resolve().parent;s=json.loads((P/'citations-start.json').read_text());B=Path(s['source']['entry']).parent
spec=importlib.util.spec_from_file_location('citation_common',B/'scripts/_common.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
entries=[];metadata=[]
for k in ['wine','skills']:
 a=json.loads((P/'sources'/f'{k}-datacite.json').read_text())['data']['attributes']
 # UCI's DataCite creator is malformed as a single combined personal name; official landing has two named authors.
 authors='Aeberhard, Stefan and Forina, M.' if k=='wine' else ' and '.join(v['name'] for v in a['creators'])
 fields={'author':authors,'title':a['titles'][0]['title'],'year':str(a['publicationYear']),'doi':a['doi'],'url':'https://doi.org/'+a['doi'],'howpublished':a['publisher']}
 entries.append(m.render_entry('misc',m.citation_key(authors,fields['year'],fields['title']),fields));metadata.append({'key':k,'raw_source':'sources/'+k+'-datacite.json','bibliographic_fields':fields,'human_verification':'unverified','agent_checked_against':'official UCI landing/dictionary for Wine, arXiv author/date/DOI/version record for Skills'})
fields={'author':'{statsmodels developers}','title':'OLSResults.HC3\_se','url':'https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.HC3_se.html','note':'Official documentation, accessed 18 October 2026; publication date not specified; formula source only'}
entries.append(m.render_entry('misc','StatsmodelsHC3',fields))
raw='\n\n'.join(entries)+'\n';assert len(m.parse_bibtex(raw))==3
(P/'references-raw.bib').write_text(raw);(P/'citation-metadata-v1.json').write_text(json.dumps(metadata,indent=2))
cmd=[sys.executable,str(B/'scripts/format_bibtex.py'),str(P/'references-raw.bib'),'--output',str(P/'references.bib'),'--deduplicate'];r=subprocess.run(cmd,capture_output=True,text=True)
(P/'citation-format-execution.json').write_text(json.dumps({'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'functions_executed':['citation_key','render_entry','parse_bibtex','format_bibtex.py main']},indent=2));assert r.returncode==0
text=(P/'manuscript-v1.md').read_text().replace('Scientific Agent Skills A Library of Procedural Knowledge for Research Agents. 2026.','Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents. 2026.')
(P/'manuscript-v2.md').write_text(text)
(P/'citation-audit-v1.md').write_text('''# Citation and claim support audit
Audited every in-text reference and bibliography entry against actual primary records and local results. [1] UCI official page/dictionary supports dataset scope, feature order, count, class interpretation and license; managed DataCite metadata confirms1992/DOI/title. DataCite creator is incorrectly combined into one personal record; resolved using UCI official suggested citation with two authors rather than propagating the malformed parse. Donation1991 and dictionary update1998 are not observation dates. Unknown units and sampling/batch details remain unknown.

[2] official statsmodels HC3_se documentation Notes explicitly states (X.T X)^-1 X.T diag(e_i^2/(1-h_ii)^2) X (X.T X)^-1. Formula matches code; reference does not assert statsmodels software execution. Publication year not supplied; accessdate recorded and no invented year/pages/journal. [3] live arXiv and managed DataCite agree on five authors, exact title,2026 and DOI; arXiv current v2 revised2September2026. No journal reference identified in those records; retained preprint and unversioned current DOI. Corrected missing colon in the literal cited paper title in manuscript-v2.md. No scientific claims changed.

Numerical manuscript claims map to actual results/E1-v1.json,E2-v1.json and robustness-v1.json, not to external literature. No unsupported novelty, chemical mechanism or population claim. Three references all cited, no dangling citations. Fullprecision results versus rounded text/table checked manually. Native source citation_key/render_entry/parse_bibtex and format_bibtex.py executed. validate_citations.py actually could not import requests (recorded runtime dependency); no remote validation pass claimed. Source-guided primary-record comparison and local parsing/formatting completed instead. Human verification unperformed and source_manifest remains unverified rather than fabricating a named human.\n''')
print((P/'references.bib').read_text())
