"""Real PDF backend checks; synthetic result values do not prove scientific truth."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import test_result_links as fixtures

SCRIPT = Path(__file__).resolve().parents[1] / 'src/common/scripts/result_links.py'


def prepare_project(root):
    """Reuse the existing result/semantic fixture and actual PDF bytes."""
    root = Path(root)
    fixture = fixtures.Links()
    fixture.setUp()
    try:
        for source in fixture.root.iterdir():
            if source.is_file():
                shutil.copyfile(source, root / source.name)
        (root / 'draft.pdf').write_bytes(fixtures.pdf_bytes(fixture.TEXT))
        payload = copy.deepcopy(fixture.payload)
        payload['links'][0].update(artifact={
            'path': 'draft.pdf', 'sha256': hashlib.sha256((root / 'draft.pdf').read_bytes()).hexdigest()},
            locator={'page': 1, 'line': 1})
        (root / 'links.json').write_text(json.dumps(payload, indent=2) + '\n')
        (root / 'broken.pdf').write_bytes(b'%PDF-1.4\nnot a PDF object tree\n%%EOF\n')
    finally:
        fixture.tearDown()


PROBE = r'''
import copy,hashlib,importlib.util,json,shutil,sys
from pathlib import Path
script,root,backend=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
binary=shutil.which('pdftotext')
if backend=='pypdf':
    assert binary is None, 'pypdf-only probe must have no pdftotext on PATH'
    import pypdf
    version=pypdf.__version__
else:
    assert binary is not None, 'pdftotext probe requires the real executable'
    version=None
spec=importlib.util.spec_from_file_location('pdf_backend_audit',script)
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
payload=json.loads((root/'links.json').read_text())
text=audit._located(root/'draft.pdf',{'page':1,'line':1},{})
valid=audit.audit_links(payload,root)
bad=copy.deepcopy(payload)
bad['links'][0]['artifact']={'path':'broken.pdf','sha256':hashlib.sha256((root/'broken.pdf').read_bytes()).hexdigest()}
malformed=audit.audit_links(bad,root)
outside=copy.deepcopy(payload);outside['links'][0]['locator']['page']=99
boundary=audit.audit_links(outside,root)
print(json.dumps({'backend':backend,'pdftotext_path':binary,'pypdf_version':version,
                  'extracted_text':text,'valid':valid,'malformed':malformed,'page_outside':boundary},ensure_ascii=False))
'''


def probe(root, backend):
    env = os.environ.copy()
    if backend == 'pypdf':
        env['PATH'] = ''  # Real subprocess isolation; no mocked discovery or extraction.
    result = subprocess.run([sys.executable, '-I', '-c', PROBE, str(SCRIPT), str(root), backend],
                            env=env, capture_output=True, text=True, timeout=60)
    (Path(root) / 'probe.stdout.log').write_text(result.stdout, encoding='utf-8')
    (Path(root) / 'probe.stderr.log').write_text(result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Actual PDF probe failed: ' + result.stderr[-4000:])
    return json.loads(result.stdout)


class PdfExtraction(unittest.TestCase):
    def run_backend(self, backend):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            prepare_project(root)
            result = probe(root, backend)
        self.assertTrue(result['valid']['passed'], result['valid'])
        self.assertIn('12.35%', result['extracted_text'])
        self.assertEqual(len(result['valid']['coverage']['numeric']), 3)
        self.assertTrue(result['valid']['coverage']['declared_semantic'])
        self.assertFalse(result['malformed']['passed'])
        self.assertTrue(result['malformed']['errors'])
        self.assertFalse(result['page_outside']['passed'])
        self.assertIn('PDF page', str(result['page_outside']['errors']))
        return result

    @unittest.skipUnless(importlib.util.find_spec('pypdf'), 'pypdf is not installed')
    def test_pypdf_only_actual_pdf_and_malformed_boundary(self):
        result = self.run_backend('pypdf')
        self.assertIsNone(result['pdftotext_path'])
        self.assertTrue(result['pypdf_version'])

    @unittest.skipUnless(shutil.which('pdftotext'), 'pdftotext is not installed')
    def test_pdftotext_actual_pdf_and_malformed_boundary(self):
        result = self.run_backend('pdftotext')
        self.assertTrue(Path(result['pdftotext_path']).is_file())


if __name__ == '__main__':
    unittest.main(verbosity=2)
