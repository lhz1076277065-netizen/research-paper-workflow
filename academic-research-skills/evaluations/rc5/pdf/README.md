# Actual PDF backend acceptance

Executed locally on 2026-10-01 with Python 3.12.14 on macOS arm64. These are engineering fixtures with constructed result values, not scientific or visual certification. Remote GitHub Actions jobs have not been run in this acceptance record.

| Actual environment | Observed result |
|---|---|
| Installed `/opt/homebrew/bin/pdftotext` 26.08.0, bundled pypdf 6.10.0 | Both backend tests and the former skipped PDF case passed: 3 tests, 0 skips. |
| Fresh virtual environment, only pip and pypdf 6.10.0, subprocess `PATH=''` | pypdf fallback and former skipped PDF case passed. The pdftotext-specific test was intentionally skipped: 3 tests, 1 skip. |
| Same pypdf-only environment, old PDF case alone | 1 test passed, 0 skips; no pdftotext was discoverable. |
| Existing root suite and offline fixture | 30 root tests passed; a new `validation-report.json` was generated and passed. |

Both actual PDF paths extracted the located text, audited all three declared numeric occurrences and declared semantic context, and rejected a malformed PDF and page 99. The `pypdf/` and `pdftotext/` folders preserve actual input PDFs, links, frozen inputs, subprocess logs and raw result-link JSON reports. Their acceptance reports bind the exact audit source SHA256. `source-at-acceptance/` records that source and test/workflow snapshots; its source hash matches both reports.

The original fallback probe exposed a real uncaught `pypdf.errors.PdfReadError`. `before-fix.*` retain that observation. The repaired source wraps pypdf extraction errors into an audit diagnostic; final logs and JSON record the passing behavior. The independently installed wheel and minimal package inventory are recorded in `pypdf-install-report.json`, installation logs and `pypdf-only-packages.json`. No environment binaries or package caches are archived.

The CI workflow uses Python 3.11 with actual `poppler-utils` and Python 3.13 with only pypdf for PDF extraction. It removes historical reports, preserves the root suite, runs the existing complete-library `tests/run_all.py`, and uploads its complete JSON/text results plus actual PDF/result-link reports. The reporter requires the selected backend test and the old PDF case to have passed; a skipped selected backend cannot satisfy it. The opposite backend's dedicated test can be skipped when that backend is absent. The complete-library regression is performed by the final integration run and is not claimed by these focused local checks.

Replay from the repository uses `python academic-research-skills/tests/report_pdf_links.py --backend pdftotext --out NEW_DIRECTORY` or an absolute pypdf-only interpreter with `PATH=''` and `--backend pypdf`. CI additionally supplies `--regression academic-research-skills/test-results/regression.json`. New output directories preserve earlier records.

Official references: [pypdf text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html), [pypdf extraction errors](https://pypdf.readthedocs.io/en/stable/modules/errors.html), [pypdf 6.10.0 distribution metadata](https://pypi.org/pypi/pypdf/6.10.0/json) (BSD-3-Clause; Python >=3.9), [Ubuntu poppler-utils](https://packages.ubuntu.com/noble/poppler-utils), and [GitHub Actions matrix syntax](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#jobsjob_idstrategymatrix). The pypdf pin is the version actually tested here.
