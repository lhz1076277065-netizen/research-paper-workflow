#!/usr/bin/env python3
"""Save actual PDF/result-link reports and require the CI backend to have run."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import sys

from test_pdf_extract import SCRIPT, prepare_project, probe


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', choices=['pdftotext', 'pypdf'], required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--regression', type=Path)
    args = parser.parse_args(argv)
    root = args.out.resolve()
    if root.exists() and any(root.iterdir()):
        parser.error('Use a new output directory to retain prior acceptance records')
    root.mkdir(parents=True, exist_ok=True)
    prepare_project(root)
    result = probe(root, args.backend)
    checks = {'valid_pdf_audit': result['valid']['passed'],
              'numeric_occurrences_checked': len(result['valid']['coverage']['numeric']) == 3,
              'declared_semantic_occurrences_checked': bool(result['valid']['coverage']['declared_semantic']),
              'malformed_pdf_rejected': not result['malformed']['passed'] and bool(result['malformed']['errors']),
              'missing_pdf_page_rejected': not result['page_outside']['passed'] and bool(result['page_outside']['errors'])}
    if args.regression:
        regression = json.loads(args.regression.read_text())
        ids = ['test_result_links.Links.test_actual_pdf_page_line',
               'test_pdf_extract.PdfExtraction.test_' + args.backend + ('_only' if args.backend == 'pypdf' else '') + '_actual_pdf_and_malformed_boundary']
        cases = {case['id']: case['status'] for case in regression['cases']}
        checks['complete_library_regression_passed'] = regression['passed']
        for id in ids:
            checks[id] = cases.get(id) == 'passed'
        regression_identity = {'path': str(args.regression), 'sha256': hashlib.sha256(args.regression.read_bytes()).hexdigest(),
                               'tests_run': regression['tests_run'], 'skipped': regression['skipped']}
    else:
        regression_identity = None
    for name in ['valid', 'malformed', 'page_outside']:
        (root / ('result-links-' + name + '.json')).write_text(json.dumps(result[name], indent=2) + '\n')
    summary = {'generated_at': datetime.now(timezone.utc).isoformat(), 'backend': args.backend,
               'python': sys.version.split()[0], 'platform': platform.platform(),
               'audit_script_sha256': hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
               'pdftotext_path': result['pdftotext_path'], 'pypdf_version': result['pypdf_version'],
               'passed': all(checks.values()), 'checks': checks, 'regression': regression_identity,
               'scope': 'Actual PDF extraction and declared result-link engineering fixtures; no scientific/visual certification',
               'execution_environment': 'github_actions' if os.environ.get('GITHUB_ACTIONS') == 'true' else 'local',
               'github_run_id': os.environ.get('GITHUB_RUN_ID') if os.environ.get('GITHUB_ACTIONS') == 'true' else None}
    (root / 'pdf-acceptance.json').write_text(json.dumps(summary, indent=2) + '\n')
    manifest = [hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name
                for path in sorted(root.iterdir()) if path.is_file() and path.name != 'SHA256SUMS']
    (root / 'SHA256SUMS').write_text('\n'.join(manifest) + '\n')
    print(json.dumps(summary, indent=2))
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
