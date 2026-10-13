"""Apply the bounded review to a new report; preserve measurable facts."""
import collections,difflib,hashlib,json,pathlib,re
R=pathlib.Path(__file__).resolve().parent
original=(R/'manuscript-draft.md').read_text(); final=original
edits=[
('Training-only standardization and fixed distance classifiers: a reproducible Wine and Iris teaching reanalysis','Training only standardization and fixed distance classifiers in Wine and Iris'),
('Completed empirical teaching report · 13 October 2026 · Agent-assisted, human source verification and submission approval unverified','Empirical teaching reanalysis · 13 October 2026 · Agent assisted'),
('We compared fixed unscaled and training-standardized nearest-centroid and five-nearest-neighbor classifiers, with a majority reference, on the complete original UCI Wine and Iris tables.','Preprocessing choices can affect the same classifier differently across datasets. We compared fixed unscaled and training-standardized nearest-centroid and five-nearest-neighbor classifiers, with a majority reference, on the complete original UCI Wine and Iris tables.'),
('These dependent historical-data comparisons illustrate dataset-specific preprocessing behavior and an auditable research workflow, without claiming a new method, statistical population inference or universal algorithm superiority.','The comparison shows dataset-specific preprocessing effects under a reproducible fixed protocol. It is a teaching reanalysis; the dependent historical-data partitions support descriptive results, not population inference or universal algorithm superiority.'),
('It supplies a teaching replication, not a claim that these established datasets or algorithms constitute a new research gap.','The teaching replication tests whether a fixed preprocessing choice has the same directional effect in both datasets; it introduces no new algorithm.'),
('The scientific design was locked in research-plan-v1.md before acquisition or fitting. An ensuing version repaired missing procedural-support references and retained the same hypotheses, data scope, five fixed arms, seeds and metrics. Both UCI datasets were then linked to the repaired execution plan, without redownloading or changing their bytes. There was no protocol registration or human approval claim.','The written design in research-plan-v1.md specified the hypotheses, data scope, five fixed arms, seeds and metrics before acquisition or fitting. A later repair to procedural references left this scientific design unchanged. Both UCI datasets are linked to the execution plan with their original acquired bytes. The plan was not formally preregistered.'),
('Both panels share the 0–100% accuracy scale.','Both panels share the 0–100% balanced-accuracy scale.'),
('Actual main and sensitivity fitting took approximately 0.07 and 0.08 seconds respectively on this host; these timings exclude source acquisition, documentation and review and are not cross-hardware benchmarks.','The local main and sensitivity experiment runs took approximately 0.07 and 0.08 seconds respectively on this host, including repeated table loading, fitting and summary calculation. These timings exclude source acquisition, documentation and review and are not cross-hardware benchmarks.'),
('The observed comparison does not support an unqualified scaling benefit. Both Wine classifier families improved on average, whereas both Iris families declined on average; the smaller Iris 5-NN change included many unchanged partitions.','Scaling improved mean performance for both fixed Wine classifier families and reduced it for both Iris families. The smaller Iris 5-NN change included many unchanged partitions. The direction therefore depended on the dataset under this protocol.'),
('The study is deliberately narrow. Historical source versions, small record counts, shared observations across partitions and Iris duplicate feature vectors restrict generalization.','Historical source versions, small record counts, shared observations across partitions and Iris duplicate feature vectors restrict generalization.'),
('These limitations qualify the demonstrated teaching comparison without concealing its negative results.','The result supports a specific teaching lesson: preprocessing must be evaluated for the data and decision rule being used.')]
for before,after in edits:
    assert final.count(before)==1,before
    final=final.replace(before,after)
numeric=lambda s:collections.Counter(re.findall(r'(?<![A-Za-z])[-+]?\d+(?:[.,]\d+)*(?:e[-+]?\d+)?',s))
tables=lambda s:[v for v in s.splitlines() if v.startswith('|')]
cites=lambda s:collections.Counter(re.findall(r'\[(?:\d+,?)+\]',s))
links=lambda s:re.findall(r'!\[[^\]]*\]\(([^)]+)\)',s)
assert numeric(original)==numeric(final),'Changed numerical facts'
assert tables(original)==tables(final),'Changed scientific table'
assert cites(original)==cites(final),'Changed citation mapping'
assert links(original)==links(final),'Changed figures'
assert original.split('## References\n',1)[1]==final.split('## References\n',1)[1]
assert all(v in final for v in ['No p-values were computed','no independent external dataset','remain unverified','-7.00 and -1.11','reduced it for both Iris families','not population inference'])
(R/'manuscript-final.md').write_text(final)
(R/'polish-diff.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),final.splitlines(True),fromfile='manuscript-draft.md',tofile='manuscript-final.md')))
facts={'edits':len(edits),'numeric_token_multiset_preserved':True,'table_all_cells_preserved':True,'citation_occurrences_and_reference_section_preserved':True,'figure_links_preserved':True,'negative_results_material_uncertainty_and_human_status_preserved':True,'review_resolutions':{'W1':'README.md supplied during review; commands describe original runs without claiming an extra rebuild','W2':'Timing now correctly includes table reading and summary work','W3':'Figure caption correctly names balanced accuracy','W4':'Results-led abstract and discussion; removed process narrative without changing the scientific design'},'raw_sha256':hashlib.sha256(original.encode()).hexdigest(),'final_sha256':hashlib.sha256(final.encode()).hexdigest(),'semantic_check':'All changed passages read against reviewed draft: no new performance, novelty, causal or journal-readiness claims; source instructions to hide disadvantage were bounded by the mandatory evidence-preservation adapter.'}
(R/'polish-fact-check.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
