# Correction continuation operation

SYNTHETIC development artifacts. Same Agent, same without-skill condition, same descriptive methods and target weights. Request: `LOCAL_EVIDENCE_ROOT/continuations/chain-b.without-skill.0/correction/request.json`. Record generated UTC: 2026-09-30T15:30:36.984648+00:00.

## Authorized source and preservation

Read the correction request's user prompt and the approved correction using `run_host.py read --request .../correction/request.json --trace LOCAL_EVIDENCE_ROOT/runs/chain-b.without-skill.0/v2/resource_reads.jsonl --kind material .../approved-correction.json`. Earliest available frozen-source read timestamp: 2026-09-30T15:09:05.458475+00:00. The corrected ZIP was acquired as binary, checked for SHA256/ZIP/member integrity, copied and extracted in this `v2/` directory. Extracted members were read directly under the continuation's explicit instruction, with parent archive SHA256, member byte digest, range and real read time in `derived_resource_reads.jsonl`.

Corrected ZIP SHA256: `79b22107370676dc295fc00eb7f376b895baea4dfebf4ac2d781cf45bd588e07`. Authorization SHA256: `ea52cbde1af67ee7b218ad6be411549ee37547262bf4d3d0e116eaa8c2d2f379`. Predecessor ZIP SHA256: `078a354c60fa96ee7ceedca955517176765f7406bd409dec7512337f59018ef4`. The original materials and all 47 pre-existing output files remain byte-identical; `old_outputs_preservation.json` records each digest. All frozen original and correction material digests match the request. All new files are inside `v2/`; old code, results, figures, manuscript and the after-caption artifact were preserved.

`prepare.py` compares the retained original raw events with the authorized corrected events. Exactly three raw rows change: e040 4950→5950 subscore, e041 5050→6050 subscore, and the identical e041 copy receives the same change. This is two unique events; the other 40 raw rows and their fields are unchanged. `units.csv` and `LICENSE.txt` are byte-identical. The dictionary byte digest changes because an approved correction note was appended; its original definitions are an identical prefix. This distinction is recorded in `correction_dependency_audit.json`, rather than claiming every member is byte-identical.

## Actual affected dependencies

Reused the previous full `analysis.py` byte-for-byte: SHA256 `56339dc350f2d24acfc06af094074cb5a8106d4d60bde3754743df13a628b3be`. Event deduplication, score conversion, inclusive date-valid metadata matching, equal-precision within-unit/method averaging, independent-unit pairing, fixed 0.8/0.2 target weighting, exhaustive stratified paired percentile bootstrap, leave-one-unit-out, composition sensitivity, alternative Welch–Satterthwaite interval, and figure layout are unchanged.

The new preparation wrapper selects and verifies the corrected source and authorization, and audits their allowed differences. The updated check's expected values and evidence paths follow the corrected measurements. The actual numerical pipeline regenerated `prepared_events.csv`, `paired_units.csv`, data flow/profile, stratum summaries, `results.json`, bootstrap distributions, both robustness CSVs, and the main PNG/SVG plus preview/grayscale and QA receipts. The affected manuscript/abstract/table/robustness statements and caption were updated from those values, and source/claim/consistency records were regenerated. Unaffected manuscript sections, definitions and layout were reused. The exact prior caption sentence remains at its end: “All measurements in this figure are synthetic Skill-development inputs.”

| Quantity | Retained result | Corrected result |
|---|---:|---:|
| u08 B mean (score) | 5 | 6 |
| u08 A−B (score) | 6 | 5 |
| g2 mean B (score) | 6.5 | 6.75 |
| g2 mean A−B (score) | +3 | +2.75 |
| g2 percentile interval (score) | [1.5, 5] | [1.5, 4.25] |
| Target mean A/B (score) | 6.3 / 6.5 | 6.3 / 6.55 |
| Target mean A−B (score) | −0.20 | −0.25 |
| Target percentile interval (score) | [−0.65, 0.25] | [−0.65, 0.15] |
| Sample-mix mean A−B (score) | +1 | +0.875; figure label +0.88 |
| Sample-mix percentile interval (score) | [0.1875, 2] | [0.1875, 1.625] |
| Fixed-target leave-one-unit-out range (score) | [−0.4, −0.0666667] | [−0.4, −0.1166667] |
| Composition zero-crossing g1 weight | 0.75 | 11/15 = 0.7333333 |
| Alternative interval (score) | [−0.8747594, 0.4747594] | [−0.8284638, 0.3284638] |

The target shift is −0.05 score: the corrected B score increases by one score for one of four g2 units, whose target weight is 0.2. g1 values, every A score, all unit/technical-event counts, the two exact-event-copy exclusions, the target and sample composition, and the qualitative stratum disagreement remain unchanged. All eight leave-one-unit-out estimates are still negative, while both target intervals still cross zero. `correction_change_summary.json` enumerates changed result fields.

## Actual execution and checks

Executed preparation, analysis and the updated runnable check with the shared interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' 'LOCAL_EVIDENCE_ROOT/runs/chain-b.without-skill.0/v2/prepare.py'
PYTHONDONTWRITEBYTECODE=1 'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' 'LOCAL_EVIDENCE_ROOT/runs/chain-b.without-skill.0/v2/analysis.py'
PYTHONDONTWRITEBYTECODE=1 'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' 'LOCAL_EVIDENCE_ROOT/runs/chain-b.without-skill.0/v2/check.py'
```

Latest preparation/audit: 2026-09-30T15:17:36.139357+00:00; source-difference audit: 2026-09-30T15:17:36.137629+00:00.
Actual analysis internal start/end: 2026-09-30T15:12:25.554191+00:00 → 2026-09-30T15:12:26.481152+00:00.
Latest fact/numeric/text/figure/preservation check: 2026-09-30T15:30:36.669482+00:00, PASS.
Direct PNG and grayscale inspection recorded: 2026-09-30T15:30:36.984648+00:00, PASS; hashes in `figure_visual_review.json`.

An intermediate prose-update assertion stopped at a leave-one-unit-out phrase that belongs only in the manuscript and was absent from the caption. The next check detected the still-old caption interval. The caption-specific replacements were then applied, checks/readme synchronized, and the complete updated check passed. No old files were modified by these intermediate failures.

The figure remains nominally 180 mm × 100 mm with editable SVG text, all 8 paired units, clearly labeled approximate percentile intervals and a 600 dpi PNG. Font/layout/file checks report no issues, and direct image inspection confirms no clipped points, whiskers, labels or grayscale ambiguity. The updated evidence record contains 10 source records and 18 hashed claim blocks, with unknown human verification kept explicit.

## Reused professional workflows and unknown scope

Figure workflow: Haojae/scipilot-figure-skill commit `43098ddb9e6a6d142218540c114f9ed38922fc42`. Writing workflow: K-Dense-AI/scientific-agent-skills commit `65d6e786832e2c52832713117bbbf5096b56f77f`, scientific-writing metadata 2.1. The previously inspected pinned sources and byte-identical four figure scripts were reused; no new professional source lookup or installation was performed. The figure analysis again actually called data profiling, base style, preview rendering, layout audit and file checks; the writing evidence/consistency procedure was reused for the affected manuscript/caption assertions. `professional_source_receipt.json` retains the initial consultation record, while `analysis_receipt.json` records this execution's calls and observed software versions. The upstream writing CLI was not invoked. No project Skill, other-group result, alternative model/host, child Agent, external research, external message, paper submission or new experiment was used.

The numeric correction is authorized within the synthetic fixture. It does not validate real-world measurements, sampling, target provenance, transportability, calibration, causal identification, or population confidence coverage. Independence and technical precision remain fixture stipulations. Human authorship/scientific verification/approval remain unknown. Token usage: unknown. Cost: unknown. Full-session exact duration: unknown; only observed UTC timestamps are reported.
