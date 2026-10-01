"""Actual Git/ZIP identity checks; no network or user installation."""
import importlib.util,json,subprocess,tempfile,unittest,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rc4_pack',ROOT/'release/make_package.py')
pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)

class PackageIdentity(unittest.TestCase):
    def test_commit_binding_excludes_ignored_files_and_rejects_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'VERSION').write_text('3.2.0-rc.4\n')
            (root/'.gitignore').write_text('validation-report.json\nout/\n')
            (root/'entry.md').write_text('committed release source\n')
            (root/'evaluations/rc4').mkdir(parents=True);(root/'evaluations/rc4/VALIDATION.zh-CN.md').write_text('source evidence scope\n')
            (root/'history').mkdir();(root/'history/PACKAGE-MANIFEST.json').write_text('historical identity\n')
            def git(*args):
                return subprocess.check_output(['git',*args],cwd=root,stderr=subprocess.DEVNULL,text=True).strip()
            git('init');git('add','.')
            git('-c','user.name=Package Test','-c','user.email=test@example.invalid','commit','-m','Synthetic release')
            (root/'validation-report.json').write_text('uncommitted ignored file\n')
            old=pack.ROOT;pack.ROOT=root
            try:
                self.assertIn(root/'history/PACKAGE-MANIFEST.json',pack.chosen('source'))
                receipt=pack.pack('runtime',root/'out')
                with zipfile.ZipFile(root/'out'/receipt['file']) as archive:
                    manifest=json.loads(archive.read('academic-research-skills-v3.2.0-rc.4/PACKAGE-MANIFEST.json'))
                    self.assertEqual(manifest['source_commit'],git('rev-parse','HEAD'))
                    self.assertNotIn('validation-report.json',manifest['files'])
                    self.assertIn('evaluations/rc4/VALIDATION.zh-CN.md',manifest['files'])
                    self.assertEqual(archive.read('academic-research-skills-v3.2.0-rc.4/entry.md'),b'committed release source\n')
                (root/'entry.md').write_text('uncommitted source change\n')
                with self.assertRaisesRegex(ValueError,'Commit the release source'):
                    pack.pack('runtime',root/'other-out')
            finally:pack.ROOT=old

    def test_one_click_refuses_preexisting_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            version=(pack.ROOT/'VERSION').read_text().strip()
            folder=Path(tmp)/('academic-research-skills-v'+version+'-one-click')
            folder.mkdir();(folder/'user-file.txt').write_text('preserve this')
            with self.assertRaises(FileExistsError):pack.one_click({},tmp)
            self.assertEqual((folder/'user-file.txt').read_text(),'preserve this')
