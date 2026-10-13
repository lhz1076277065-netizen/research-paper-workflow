"""Review only: reconcile manuscript table to immutable experiment outputs."""
import json, pathlib, re, hashlib
R=pathlib.Path(__file__).resolve().parent
text=(R/'manuscript-draft.md').read_text()
rows=[line.split('|')[1:-1] for line in text.splitlines() if re.match(r'\| (Wine|Iris) \|',line)]
summary=json.loads((R/'results/summary.json').read_text())['summary']
assert len(rows)==len(summary)==10
for row,actual in zip(rows,summary):
    assert row[0].strip().lower()==actual['dataset']
    for cell,key in zip(row[2:],('balanced_accuracy_mean','balanced_accuracy_sd','accuracy_mean')):
        assert cell.strip()==f"{100*actual[key]:.2f}",(cell,key)
images=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',text)
assert len(images)==2 and all((R/p).is_file() for p in images)
assert all(s in text for s in ['No p-values were computed','three excess duplicate Iris','not independent prospective','-7.00 and -1.11'])
out={'manuscript_sha256':hashlib.file_digest((R/'manuscript-draft.md').open('rb'),'sha256').hexdigest(),'table_rows_checked':10,'numeric_cells_checked':30,'figure_links_resolved':images,'dependent_splits_negative_results_and_duplicate_limitations_present':True,'human_review_performed':False,'external_review_performed':False,'meaning_review':'See manuscript-review.md; syntax checks alone do not certify scientific validity.'}
(R/'review-checks.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
