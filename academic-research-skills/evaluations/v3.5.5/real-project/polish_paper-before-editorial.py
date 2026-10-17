from pathlib import Path
import json,difflib,re,hashlib
P=Path(__file__).resolve().parent;old=(P/'manuscript-v2.md').read_text()
edits=[('For these 178 records, the answer to the overall question is a positive, moderately sized descriptive association: Pearson r was 0.546 and the slope was 1.560.','For these 178 records, the overall association is positive: Pearson r was 0.546 and the slope was 1.560.','Removes a subjective magnitude label; retains the same fixed dataset, positive direction, r and slope. No stronger claim is introduced.'),('Rank and omission checks make a single outlier or a purely linear scaling explanation less compelling as the sole explanation of the positive direction, but they do not identify a mechanism.','The positive direction was retained with rank correlations and after every single-record omission from the pooled and adjusted fits. These checks do not identify a mechanism.','Replaces a vague explanation with exact checks already performed and reported. Does not claim every class-specific omission was fitted; explicitly says pooled and adjusted. Retains the no-mechanism boundary.')]
new=old
for before,after,assess in edits:assert before in new;new=new.replace(before,after)
(P/'manuscript-final.md').write_text(new)
coverage=json.loads((P/'manuscript-coverage-v2.json').read_text())
for q in coverage['questions']:
 q['conclusion']['path']='manuscript-final.md'
 for before,after,_ in edits:q['conclusion']['quote']=q['conclusion']['quote'].replace(before,after)
for e in coverage['experiments']:
 for kind in ['methods','results']:e[kind]['path']='manuscript-final.md'
coverage['reviewed_coverage']='manuscript-coverage-v2.json';(P/'manuscript-coverage-final.json').write_text(json.dumps(coverage,indent=2))
report={'unresolved_required':[],'meaning_checks':[{'before':a,'after':b,'assessment':c} for a,b,c in edits],'unchanged_checks':{'objects':'alcohol, color intensity and numeric cultivar classes unchanged','scope':'complete original178historicalrecords, descriptive no causal/population unchanged','direction':'overall/class/adjusted positive retained','numbers':'all numerical tokens identical in sequence','methods':'all primary and robustness methods retained','null_vs_untested':'no untested relation changed into zero/absence; broad quadraticCI and interactionp retained','citations':'same three exactreferences and every citation retained','experiment_coverage':'E1/E2 exactMethods/Resultslocations unchanged; both conclusions still present','internal_process':'No Skill receipts or phase/budget narrative added'},'review_scope':'Only actual two optional expression edits from completed professional review; no new fullreview or external/humanverification','before_sha256':hashlib.sha256(old.encode()).hexdigest(),'after_sha256':hashlib.sha256(new.encode()).hexdigest()}
nums=lambda s:re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:\^-?\d+)?',s)
assert nums(old)==nums(new)
(P/'expression-meaning-checks.json').write_text(json.dumps(report,indent=2))
(P/'expression-actual.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='manuscript-v2.md',tofile='manuscript-final.md')))
(P/'expression-record.md').write_text('# Final expression and meaning review\nApplied source principles of coherent evidence-bound narrative and keeping implementation logs outside the paper, subject to the fixed-question/scientific-integrity contract. Retained every required result, nonpositive/uncertain diagnostic, actual limitation and reference; did not apply source suggestions to change the question or suppress inconvenient evidence. Two reviewedprecisionedits only. Exactnumericsequence equality checked in code, and actualbefore/afterclaims inspected for objects,scope,direction,causalstrength,methods,untestedversusnull and experimentcoverage. These are Agent assessments, not human approval. Fullactualdiff and quote-spanassessments preserved.\n')
