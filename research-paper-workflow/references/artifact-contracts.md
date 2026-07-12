# Research Artifact Contracts

Use these contracts for every project created or validated by this skill. The CSV headers and JSON fields in `assets/templates/` are authoritative.

## Public Commands

Initialize a project:

```bash
python scripts/init_research_project.py --profile PROFILE --dest PROJECT_ROOT
```

Refresh reference metadata or parse exports:

```bash
python scripts/refresh_literature_metadata.py PROJECT_ROOT --import references.ciw --online
```

Validate the complete package:

```bash
python scripts/validate_research_package.py PROJECT_ROOT --profile auto --report validation/report.json
```

Exit codes: `0` means every hard gate passed, `1` means at least one gate failed, and `2` is reserved for invalid invocation or unrecoverable runtime input.

## Manifest

`research_manifest.json` controls project identity, schema version, article type, manuscript files, reference export, citation cache and native SEM model artifacts. Schema version must be `2.0`. Artifact paths must resolve inside the project root; copy external evidence into the package and use relative paths.

## Ledgers

- `claim_evidence_ledger.csv`: claim priority, status, sources, result IDs, manuscript location and limitation.
- `literature_matrix.csv`: inspected source metadata, WoS/JCR evidence, claim mapping and retraction status.
- `journal_metrics.csv`: JCR year, category and quartile linked to a preserved legitimate export.
- `data_manifest.csv`: data version, dates, coverage, files, checksum, freshness, bias and frozen status.
- `results_ledger.csv`: authoritative displayed values, uncertainty, sample size, rounding, source and manuscript target.
- `experiment_manifest.csv`: experiment class, command, environment, output, acceptance criterion and status.
- `figure_manifest.csv`: final figure, caption, callout, source result, editable source, generation command and quality target.
- `domain_knowledge_map.csv`: specialist knowledge element, source, alternatives, relevance, uncertainty and verification.
- `analysis_diagnostics.csv`: profile-required assumption, validity, uncertainty, robustness, fit or prediction evidence.

Semicolon or vertical bar separates multiple IDs inside a CSV field. IDs must be stable and unique within their ledger.

## Validation Report

The report contains:

```json
{
  "decision": "ready | not_ready",
  "profile": "article-type profile",
  "gates": {"gate": "pass | warning | fail"},
  "errors": [],
  "warnings": [],
  "artifacts_checked": [],
  "required_actions": []
}
```

Warnings require review but do not alone create `not_ready`. Any error creates `not_ready`. A missing manifest, manuscript, required ledger, source artifact or profile-specific evidence is an error.

## Online and Licensed Evidence

- CI validates frozen artifacts offline.
- Crossref and OpenAlex may refresh public citation metadata, but their output does not establish JCR quartile.
- JCR evidence must come from a legitimate user-provided export.
- Proprietary software is not rerun in CI; genuine native model files, settings, exports and diagnostics must be preserved.
