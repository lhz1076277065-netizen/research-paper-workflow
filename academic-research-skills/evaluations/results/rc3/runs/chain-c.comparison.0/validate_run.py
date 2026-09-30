"""One local consistency check; file success is not scientific validation."""
import csv
import hashlib
import importlib.util
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
BASE = Path('LOCAL_EVIDENCE_ROOT')
REQUEST = BASE / 'transfer-suite/requests/chain-c.comparison.0.json'
request = json.loads(REQUEST.read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
main = (OUT / 'manuscript-v3-anonymous.md').read_text()
checks = {}
for name in ['README.md', 'answer.md', 'scientific-review.md', 'response-to-reviewers.md', 'caption-v3.md', 'supplement-v3.md', 'author-queries.md', 'title-page-draft.md', 'declarations-draft.md', 'cover-letter-draft.md', 'correction-note-v1-draft.md', 'data-access-request-draft.md', 'figure-1.svg', 'figure-1.pdf', 'manuscript-v2-to-v3.diff', 'final-expression.diff']:
    assert (OUT / name).stat().st_size > 0, name
checks['actual_deliverables_exist'] = True
word_count = len(main.split())
assert word_count == 896 and word_count <= 2500
assert 'Mira Example' not in main and 'Synthetic Unit Laboratory' not in main
assert '[1]' not in main and '[2]' not in main
assert 'g2 has A−B = +3.00' in main and 'g2 favors B' in main
assert 'technical repetitions' in main.lower() and 'not treated as additional independent units' in main
assert '[−0.60, 0.20]' in main and 'No equivalence margin' in main
checks['anonymous_text_and_claim_repairs'] = True
baseline_hashes = {}
for name in ['draft-v2.md', 'caption-v2.md', 'supplement-v2.md', 'published-snapshot-v1.md', 'references.json']:
    source = BASE / 'materials/chain-c' / name
    assert (OUT / 'baseline' / name).read_bytes() == source.read_bytes(), name
    baseline_hashes[name] = sha(source)
assert baseline_hashes['published-snapshot-v1.md'] == 'fe70fc7ea3069c4507b59737a781ded7bda8d96f45eda8ed8de1e52d98ac6caf'
checks['v1_and_v2_original_bytes_preserved'] = True
rows = list(csv.DictReader((OUT / 'aggregate-results-v2.csv').open()))
assert [float(r['mean_A_minus_B_score']) for r in rows] == [-1, 3, 1, -0.2]
assert [r['quantity'] for r in rows if r['ci_lower']] == ['target mixture']
assert [int(r['independent_paired_units']) for r in rows] == [4, 4, 8, 8]
assert abs(0.8 * -1 + 0.2 * 3 - -0.2) < 1e-12 and 0.5 * -1 + 0.5 * 3 == 1
svg = (OUT / 'figure-1.svg').read_text()
assert '<image' not in svg and '+3.00' in svg and 'g2 (n = 4)' in svg
checks['aggregate_arithmetic_and_complete_vector_display'] = True
response = (OUT / 'response-to-reviewers.md').read_text()
assert all(f'## R{i} ' in response for i in range(1, 6))
lines = main.splitlines()
conclusion_heading = lines.index('## Conclusion')
conclusion_line = conclusion_heading + 2
assert f'Conclusion line {conclusion_line}' in response and conclusion_line == 29
assert all(str(i) in response for i in [3, 6, 9, 12, 16, 19, 21, 24, 26, 29])
checks['five_comments_and_final_markdown_locations'] = True
native = json.loads((OUT / 'native-document-check.json').read_text())
assert len(native['documents']) == 9
assert all(record['text_round_trip'] for record in native['documents'].values())
assert json.loads((OUT / 'figure-qa.json').read_text())['layout_issues'] == []
for name in ['manuscript-v3-anonymous', 'caption-v3', 'supplement-v3']:
    with zipfile.ZipFile(OUT / 'editable' / (name + '.docx')) as z:
        for entry in z.namelist():
            if entry.endswith('.xml'):
                content = z.read(entry).decode('utf-8')
                assert 'Mira Example' not in content and 'Synthetic Unit Laboratory' not in content, (name, entry)
        core = ET.fromstring(z.read('docProps/core.xml'))
        for node in core:
            if node.tag.endswith('creator') or node.tag.endswith('lastModifiedBy'):
                assert not (node.text or '').strip()
checks['editable_round_trip_anonymity_and_render_checks'] = True
reads = [json.loads(line) for line in (OUT / 'resource_reads.jsonl').read_text().splitlines()]
catalog = {record['local_path']: record for record in json.loads((BASE / 'professional/sources.json').read_text())}
used = []
for record in reads:
    assert sha(record['path']) == record['sha256'], record['path']
    if record['kind'] == 'professional':
        source = catalog[record['path']]
        assert source['sha256'] == record['sha256'], record['path']
        used.append({**record, 'repository': source['repository'], 'commit': source['commit']})
checks['read_resource_hashes_and_pinned_professional_versions'] = True
spec = importlib.util.spec_from_file_location('chain_c_frozen_host', BASE / 'work/academic-research-skills/evaluations/run_host.py')
host = importlib.util.module_from_spec(spec); spec.loader.exec_module(host)
host.verify_request(request)
checks['verify_request'] = True
end = datetime.now(timezone.utc).isoformat()
receipt = {'case_id': 'chain-c', 'condition': 'comparison', 'replicate': 0, 'synthetic_material': True, 'start_utc': '2026-09-30T15:44:21+00:00', 'end_utc': end, 'request_sha256': sha(REQUEST), 'checks': checks, 'word_count_conservative': word_count, 'snapshot_sha256': baseline_hashes['published-snapshot-v1.md'], 'scientific_results': 'supplied memo v2; no bootstrap replication', 'scientific_validation_or_human_approval': False, 'submission_status': 'ready_for_author_review; not submission-ready', 'external_actions': []}
(OUT / 'validation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
(OUT / 'verification.json').write_text(json.dumps({'checked_at_utc': end, 'verify_request': 'PASS', 'baseline_hashes': baseline_hashes, 'read_resources': len(reads), 'professional_version_checks': 'PASS', 'frozen_bundle_and_material_unchanged': True}, ensure_ascii=False, indent=2) + '\n')
unique = {record['path']: record for record in used}
resource_lines = '\n'.join(f"- {r['repository']} @ {r['commit']}: `{Path(r['path']).relative_to(BASE / 'professional')}`; SHA-256 `{r['sha256']}`." for r in unique.values())
operation = f'''# Operation receipt — chain-c.comparison.0

SYNTHETIC Skill-development run, not real research or submission. Scientific reasoning is in scientific-review.md; manuscript, author questions and operation receipts are separate.

- UTC start: 2026-09-30T15:44:21+00:00 (clock tool observed).
- UTC end: {end} (captured immediately after successful final verify_request).
- Request: `{REQUEST}`; SHA-256 `{sha(REQUEST)}`.
- Frozen comparison Skill: research-paper-workflow 3.2.0-rc.1; entry SHA-256 `{request['skill_entry_sha256']}`; identity manifest SHA-256 `{request['skill_snapshot']['manifest_sha256']}`.
- Related frozen capabilities actually read and applied: journal-intelligence, ethics-protocol, citation-audit, manuscript-review, submission-packaging, peer-review-response and publication-stewardship, all supplied version 3.2.0-rc.1. Their entry/protocol hashes and exact selections, and lifecycle/quality/provider/final-expression/handoff reads, are in resource_reads.jsonl.
- All eleven frozen material files were read completely through run_host read with kind material. Request metadata and initial_skill_text were read directly as task metadata. No memory, other condition/answer, score, candidate-maintenance source or root-task check was used.
- Python: `{sys.executable}`, {sys.version.split()[0]}. Native document converter: {native['office_version']}. Matplotlib version is recorded in figure-qa.json. No dependency or model was installed or switched.

## Professional resources actually consumed
Selection stayed within the common thirteen-repository pool. The locally supplied source cache was checked against sources.json; live-head flags describe the cache preparation and are not a new live check in this run.

{resource_lines}

## Actual actions and adaptation
1. Resumed supplied v2; identified universal/causal/equivalence, g2 sign, citation and declaration/access conflicts. Reported supplied result values and locally checked weighted arithmetic; did not regenerate data or uncertainty.
2. Selected fictional Lens Technical Note under current supplied v2 (2026-09-01), excluded Apex on evidence/type and Replica on license conflict, removed the author line from review files and kept a separate title page.
3. Wrote the complete scientific revision, then actually applied anti-defensive-writing-en to title, Abstract, Introduction, Discussion flow and Conclusion. Retained negative g2, both mixtures, interval crossing zero, inferential unit and causal/equivalence bounds. Original v2, pre-expression v3, final v3 and both actual diffs are retained.
4. Applied K-Dense scientific-writing, citation-management and peer-review guidance in the current native Agent (`adapted_in_host`). This was authorized synthetic developmental editing, not an assigned external peer review. Its human-verification/intake approval states were not fabricated or marked passed. Live search/enrichment, full-text retrieval and native full pipelines were not performed. An additional unverified software-paper citation requested upstream was not inserted into this closed bibliography; repository/version acknowledgment is provided here instead.
5. Applied SciPilot to choose a horizontal aggregate point/interval display, rather than pretending to have raw distributions. Its selected error-bar recipe informed the implementation and its actual visual_qa module ran locally. Only the supplied target interval appears; no new raw data, draws or significance symbols were generated. Profile-data EDA was not run because aggregate rows are not independent observations. Lens supplied no dimensions/fonts, so the chosen size and font are local defaults.
6. Read the color and grayscale preview images against the eight visual-review items: symbols readable; no clipping/overlap; all points and interval caps visible; zero reference and units clear; labels/shapes readable in grayscale; multi-panel alignment/spacing/cross-panel items not applicable to this single plot. Vector PDF/SVG and 300-DPI PNG exported after that inspection.
7. Wrote actual R1–R5 responses with final-source locations: accepted R1/R5; declined R2/R3/R4 with evidence. No additional experiment or approved response was claimed. A location check corrected the R5 Conclusion pointer to final Markdown line 29 and regenerated the Word copy.
8. Created nine editable DOCX counterparts with the installed native office converter, cleared core author metadata, and compared complete extracted paragraph/table text to the Markdown sources. During conversion, a false mismatch from joining separate Word text runs was fixed by paragraph-based extraction; then actual table overflow from HTML viewport widths was fixed in the shared conversion path by fitting DOCX tables to page-body width. Final round-trip and page-bound checks pass for all nine documents ({sum(r['pdf_pages'] for r in native['documents'].values())} PDF pages). The three contact sheets were visually inspected; tables/text are now inside page bounds and scientific symbols/numbers remain readable. The corrected final R5 page was checked again after regeneration.
9. Preserved the supplied v1 source and archived a byte-identical copy. Prepared the actual correction text for −0.30 → −0.20 plus universal/causal/equivalence/open-raw-data interpretation changes; numerical root cause remains undocumented. No publisher notice was sent and no snapshot was overwritten.
10. Ran validate_run.py's single local integration check and, at the end, run_host.verify_request(request). All request bundle/material hashes and the original snapshot remain unchanged. Software checks are file/format/consistency receipts, not scientific-quality scores.

## Final products
README.md indexes the anonymous manuscript, editable caption/SVG, supporting material, title page, unapproved declarations/access/cover letter, exact reviewer responses, author questions, substantive v1 correction draft, preserved baselines, expression/scientific diffs, editable Word files, native renders and local code. inventory.json binds stable output versions to SHA-256. validation.json and verification.json record final scope and file checks.

## Unobtained and unapproved scope
No numerical unit dataset, original bootstrap script, bootstrap draws, resample count, seed, analysis software version, technical-repeat counts or conversion rules were supplied. Efron's original text and both article full texts were not obtained; Rosenbaum/Rubin content was limited to the supplied bounded abstract paraphrase. Referenced auxiliary professional resources not in the supplied selected cache were not fetched; native full-workflow execution and live publication/correction/retraction checks remain unperformed/unknown. Author list/order/contact/ORCID/approval, contributions, funding, conflicts, ethics/human-participant/consent determination, data-holder/contact and license-compatible access approval, submission exclusivity, fees/publication permissions and signatures remain UNKNOWN. No external service, message, submission, deposit, signature, reviewer contact or publisher action occurred.

Scientific result reporting is complete within the fictional memo, with causal/equivalence and replication limits intact. Local package preparation is complete for author review. Human verification, required declarations and real submission readiness are not established.
'''
(OUT / 'operation.md').write_text(operation)
inventory = []
for path in sorted(OUT.rglob('*')):
    if not path.is_file() or any(part.startswith('.') or part == 'native-office-profile' for part in path.relative_to(OUT).parts):
        continue
    if path.name == 'inventory.json':
        continue
    inventory.append({'path': str(path.relative_to(OUT)), 'sha256': sha(path), 'bytes': path.stat().st_size, 'version': 'v1-preserved' if path.name == 'published-snapshot-v1.md' else ('v2-preserved' if 'baseline' in path.parts else 'local-development-v3'), 'submission': 'unsubmitted author-review package'})
(OUT / 'inventory.json').write_text(json.dumps({'created_at_utc': end, 'files': inventory, 'self_excluded_from_hash_inventory': True}, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'checks': checks, 'end_utc': end, 'stable_outputs': len(inventory), 'word_count': word_count}, ensure_ascii=False))
