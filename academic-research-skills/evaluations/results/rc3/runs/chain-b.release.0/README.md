# SYNTHETIC deliverables

This directory contains a completed local computational report on manufactured paired measurements. It is a Skill-development fixture, not real academic research or a submission-ready paper.

| Purpose | Files |
|---|---|
| Reader-facing result | `manuscript.md`, `caption.md`, `main_figure.png`, `main_figure.svg` |
| Exact numeric evidence | `results.json`, `figure_source.csv`, `target_bootstrap_mass.csv`, `bootstrap_arrays.npz` |
| Actual robustness | `leave_one_unit_out.csv`, `composition_sensitivity.csv` |
| Preparation and reproducible analysis | `prepare.py`, `analyze.py`, `figure.py`, `verify.py`, `reproduce.py`, `derived/` |
| Original source and member identity | `raw/original.zip`, `raw/extracted/`, `archive_receipt.json`, `derived_member_reads.jsonl` |
| Full writing revision and audit | `manuscript.before-expression.md`, `manuscript.expression.diff`, `writing_review.md`, `fact_check.md`, `fact_check.json`, `source_manifest.json`, `claims.csv` |
| Figure decisions and inspection | `figure_design.md`, `profile_report.md`, `profile.json`, `visual_review.md`, `figure_qa.json`, grayscale and preview PNGs |
| Actual operation and timing | `operation.md`, `operation_metrics.json`, `professional_selection.json`, `professional_calls.jsonl`, `resource_reads.jsonl`, `execution_log.jsonl` |

The target contrast is A-minus-B = -0.20 score at stipulated weights 0.8/0.2, with conditional 95% paired-unit percentile interval [-0.65,+0.25]. The same paired units at sampled weights 0.5/0.5 give +1.00. Stratum directions disagree. All single-unit omission point estimates remain negative, but interval zero inclusion is sensitive to omission. None of these results establishes real-world or causal superiority.

Reproduce in the provided environment:

```sh
PYTHONDONTWRITEBYTECODE=1 'LOCAL_USER_ROOT/Documents/ChatGPT/学术skill/acceptance-20260930-091827/environment/.venv/bin/python' 'LOCAL_EVIDENCE_ROOT/runs/chain-b.release.0/reproduce.py'
```

The command rechecks the original ZIP, rebuilds the prepared paired data and exact numerical outputs, regenerates the figure, and runs the independent numeric verification. The supplied shared professional cache is required by `figure.py`; the original material archive is required by `prepare.py`. No global installation is needed. Writing and semantic-review records are preserved; code reruns do not invent a new human or visual review. Material changes require review of affected figure and manuscript claims.
