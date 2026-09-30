# Input-correction operation record

This is the same Agent's input-correction continuation of the synthetic development task. It is not an independent stability replicate. The frozen correction request is `LOCAL_EVIDENCE_ROOT/continuations/chain-b.comparison.0/correction/request.json` (SHA-256 `64b3b32ef20cbd9b6a3c21d2164ca17fe557884da63df2ad59c29cedae914beb`). The original request, original inputs and all 45 previously existing run files, including the caption continuation, are retained byte-for-byte. New complete related artifacts are in `v2/`; this record is supplied there and as a new root-level `operation-correction.md`. No other condition, score, root check or answer was read. No subagent, model/host switch, installation, messaging, external research, new experiment or submission occurred.

## Authorised input and actual changes

Corrected archive SHA-256: `79b22107370676dc295fc00eb7f376b895baea4dfebf4ac2d781cf45bd588e07`. Approval SHA-256: `ea52cbde1af67ee7b218ad6be411549ee37547262bf4d3d0e116eaa8c2d2f379`. Prior archive SHA-256: `078a354c60fa96ee7ceedca955517176765f7406bd409dec7512337f59018ef4`.

`prepare.py` verifies these identities, ZIP CRC, member paths and member bytes before extraction. Old and corrected measurements are compared row by row: raw CSV lines 41, 42 and 44 change by exactly +1,000 subscore, affecting e040 and e041 and the identical e041 copy, all u08 B. Every other raw field is identical. `units.csv` and `LICENSE.txt` are byte-identical. The dictionary's original 906-byte definition text is byte-retained; its corrected 1,099-byte member appends the explicit correction annotation. It is therefore accurate to say definitions are retained, but not that the dictionary member is byte-identical. `correction_audit.json` stores each changed row and all old/new member hashes. `archive_identity.json` and `derived_member_reads.jsonl` store the corrected ZIP digest, each member digest and actual full half-open byte read ranges. Extracted members were read directly, not forced through frozen-material mode.

The first stricter guard rejected the dictionary byte change. Inspection identified the appended annotation; the guard was repaired to require both the intact original prefix and the exact approved note. This was an input-validation adjustment, with no measurement exception or method change.

## Dependency update and checks

Event deduplication, score conversion, inclusive date-valid metadata matching, technical averaging, eight paired independent units, fixed target weights, exact stratified conditional bootstrap, inverse-CDF percentile intervals, unit-deletion influence and the alternative-target weight curve are retained. `analysis.py` actually rebuilds preparation, pairs, full PMFs, uncertainty, robustness and figure outputs from the corrected archive. Unit u08 B becomes 6 score and A−B becomes 5; all other paired data remain unchanged.

| Dependent result | Previous | Corrected |
|---|---|---|
| Stratum 2 mean A−B | 3 | 2.75 |
| Stratum 2 conditional interval | [1.5, 5] | [1.5, 4.25] |
| Target A−B | −0.20 | −0.25 |
| Target mean B | 6.50 | 6.55 |
| Target conditional interval | [−0.65, 0.25] | [−0.65, 0.15] |
| Sample-composition A−B | 1 | 0.875 |
| Sample mean B | 6.50 | 6.625 |
| Sample conditional interval | [0.1875, 2] | [0.1875, 1.625] |
| Unit-deletion target range | [−0.40, −0.0666667] | [−0.40, −0.1166667] |
| Alternative-weight zero crossing | 0.75 | 11/15≈0.7333333 |

Stratum 1 remains −1, and every unit-deletion target point estimate remains negative. The target conditional interval still includes zero. `correction_changes.json` records numerical dependency changes, including unit deletions. The figure's weight curve, crossing tick/annotation, stratum summaries and target/sample markers derive from recalculated values. The original design and nominal 180 × 103 mm size are retained.

Both complete manuscript versions, abstract, source Methods, Results, influence interpretation, weight-sensitivity interpretation, discussion, conclusion, caption and supporting outline/route/figure decisions are reconciled. Evidence E011 records approval; corrected source hashes replace affected identities. The caption still ends with the exact prior sentence, “All measurements in this figure are synthetic Skill-development inputs.” The inherited bibliography and retrieval receipt are copied without any new external lookup.

Final `verify.py` passed at **2026-09-30T15:53:53.751316+00:00**. An independent rational multinomial count-vector algorithm matches the entire bootstrap distributions and quantiles. Conflicting event duplicates and ambiguous active metadata are rejected; the prescribed weights, corrected row scope, old-file preservation, editable SVG text, no embedded raster, PNG DPI and physical size pass. The corrected preview, final PNG and grayscale images were actually viewed. Final SVG is 180 × 103 mm; the 600-dpi PNG is 4251 × 2433 pixels (179.959 × 102.997 mm after pixel/DPI rounding). Twenty-one factual paragraph occurrences bind to evidence; final-expression numerical tokens and inferential scope are unchanged. The exact checked scientific file hashes are in `fact_semantic_check.json`.

## Professional implementation and scope

The frozen Skill version `3.2.0-rc.1` and previously selected capability resources are inherited; the bundle remains manual evaluation composition, not native automatic discovery. There were zero new professional text reads. The 33 earlier reader events are preserved separately in `resource_reads_inherited.jsonl`; the one new audited material read is the correction approval in `resource_reads.jsonl`. Professional source hashes were checked again against the previously recorded pinned cache. No repository heads were newly queried.

SciPilot commit `43098ddb9e6a6d142218540c114f9ed38922fc42` was actually reused through `profile_data()`, `render_report()`, `setup_style()`, `add_panel_labels()`, `audit_layout()`, `render_preview()` and `check_figure()` on the corrected pairs and actual final figure. Scope: corrected profile, main PNG/SVG, caption, layout/file audits and visual inspection.

K-Dense scientific-writing commit `65d6e786832e2c52832713117bbbf5096b56f77f` (entry metadata 2.1) supplied the retained evidence outline, full IMRAD structure and affected-method/result reconciliation. Anti-defensive-writing English commit `102c8b21acf5eda3a0aef3d9779a65db646c8980` supplied the retained evidence-preserving expression decisions. Their affected full-manuscript dependencies and final claim scope were reviewed in this Agent; optional upstream writing CLIs were not run and a completely fresh professional research route is not claimed. Source file versions/hashes and runtime are in `operation_receipt.json`. No professional source was modified.

## Reproduction, time and limits

```sh
PYTHONDONTWRITEBYTECODE=1 'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' 'LOCAL_EVIDENCE_ROOT/runs/chain-b.comparison.0/v2/analysis.py'
PYTHONDONTWRITEBYTECODE=1 'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' 'LOCAL_EVIDENCE_ROOT/runs/chain-b.comparison.0/v2/verify.py'
```

The analysis command regenerates preparation, numerical analyses, robustness, profiles and figures; the full manuscript and caption are separately supplied editable authored artifacts. Existing runtime: Python 3.12.14, NumPy 2.5.3, SciPy 1.18.1, Matplotlib 3.11.2, pandas 3.0.6 and Pillow 12.3.0. Bytecode remains disabled and Matplotlib's cache is inside `v2/`.

First successful audited correction read: **2026-09-30T15:26:07.214332+00:00**. Prior-file snapshot: **2026-09-30T15:31:18.971620+00:00**. This receipt was recorded at **2026-09-30T15:56:52.800278+00:00**, 1845.585946 elapsed wall-clock seconds after that read. This includes continuation and coordination time; it is not measured compute or billing time. Exact API model identity, tokens and monetary cost are **unknown**.

All scientific data/results/prose are synthetic. Real population coverage, representativeness, practical importance and target-weight uncertainty remain unknown. The conditional intervals and retained descriptive conclusions do not establish causal superiority. No human scientific verification, independent real external validation or submission approval occurred. Complete changed related files, provenance, numerical outputs, scientific drafts and checks are in `v2/`, with older outputs preserved.
