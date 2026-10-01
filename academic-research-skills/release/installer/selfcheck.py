#!/usr/bin/env python3
"""Run installation and preservation checks in temporary user folders only."""
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import install


def snapshot(root):
    values = {}
    for p in root.rglob('*'):
        if p.is_symlink():
            values[str(p.relative_to(root))] = 'link:' + os.readlink(p)
        elif p.is_file():
            values[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return values


def run(home, *args):
    installer = Path.home() / '.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py'
    with patch.object(sys, 'argv', ['install.py', '--home', str(home), '--installer', str(installer), *map(str, args)]):
        return install.main()


def main():
    cases = []
    with tempfile.TemporaryDirectory(prefix='academic-install-check-') as temp, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()), patch.dict(os.environ):
        os.environ.pop('CODEX_HOME', None)
        home = Path(temp) / '用户 空间'; home.mkdir()
        for root in [home / '.agents/skills', home / '.codex/skills']:
            p = root / 'research-paper-workflow'; p.mkdir(parents=True)
            (p / 'SKILL.md').write_text('existing user Skill\n', encoding='utf-8')
            (p / 'notes.txt').write_text(str(root) + '\nuser changes', encoding='utf-8')
        untouched = home / '.agents/skills/other-skill/keep.txt'
        untouched.parent.mkdir(); untouched.write_bytes(b'unrelated files')
        broken = home / '.codex/skills/paper-deep-reading'
        broken.symlink_to(home / 'missing-old-skill')
        originals = {str(root): snapshot(root) for root in [home / '.agents/skills', home / '.codex/skills']}
        assert run(home) == 0
        receipts = list((home / '.codex/academic-research-skills-backups').glob('*/receipt.json'))
        assert len(receipts) == 1
        backup = receipts[0].parent
        assert len(json.loads(receipts[0].read_text())['originals']) == 3
        assert run(home, '--check') == 0 and untouched.read_bytes() == b'unrelated files'
        cases.append('all_19_installed_verified_old_copies_and_broken_link_backed_up')
        cache = home / '.agents/skills/journal-intelligence/__pycache__/generated.pyc'
        cache.parent.mkdir(); cache.write_bytes(b'generated cache')
        (cache.parent.parent / '.DS_Store').write_bytes(b'Finder cache')
        assert run(home, '--check') == 0
        cases.append('python_and_finder_cache_do_not_fake_source_edits')
        before = snapshot(home / '.agents/skills')
        assert run(home) == 0 and snapshot(home / '.agents/skills') == before
        assert len(list((home / '.codex/academic-research-skills-backups').glob('*/receipt.json'))) == 1
        cases.append('same_version_repeat_is_idempotent')
        entry = home / '.agents/skills/journal-intelligence/SKILL.md'
        original = entry.read_bytes(); entry.write_bytes(original + b'\nuser edit\n')
        edited = snapshot(home / '.agents/skills')
        try:
            run(home, '--restore', backup)
        except ValueError:
            pass
        else:
            raise AssertionError('Modified current Skill should prevent restore')
        assert snapshot(home / '.agents/skills') == edited
        result = subprocess.run([sys.executable, '-O', str(install.BASE / 'install.py'), '--home', str(home), '--restore', str(backup)], text=True, capture_output=True)
        assert result.returncode == 1 and snapshot(home / '.agents/skills') == edited
        cases.append('python_optimized_mode_does_not_bypass_restore_guard')
        entry.write_bytes(original)
        cases.append('restore_preserves_post_install_user_edits')
        assert run(home, '--restore', backup) == 0
        for root, values in originals.items(): assert snapshot(Path(root)) == values
        assert len(list((backup / 'new-after-restore').glob('*/SKILL.md'))) == 19
        cases.append('restore_recovers_exact_old_copies_and_keeps_new_version')
        replace = os.replace
        def fail_second(source, target):
            if '/ready/citation-audit' in str(source):
                raise OSError('Controlled commit failure')
            return replace(source, target)
        with patch.object(install.os, 'replace', side_effect=fail_second):
            try: run(home)
            except OSError: pass
            else: raise AssertionError('Expected controlled failure')
        for root, values in originals.items(): assert snapshot(Path(root)) == values
        states = [json.loads(p.read_text())['status'] for p in (home / '.codex/academic-research-skills-backups').glob('*/receipt.json')]
        assert 'rolled_back' in states
        cases.append('mid_commit_failure_restores_all_old_bytes')
        bad = Path(temp) / 'bad'; bad.mkdir()
        (bad / (install.STEM + '.zip')).write_bytes(b'not the pinned archive')
        with patch.object(install, 'BASE', bad):
            try: run(home)
            except ValueError: pass
            else: raise AssertionError('Expected digest rejection')
        for root, values in originals.items(): assert snapshot(Path(root)) == values
        cases.append('wrong_zip_rejected_before_skill_mutation')
        assert run(home, '--skill', 'journal-intelligence') == 0
        assert run(home, '--check', '--skill', 'journal-intelligence') == 0
        assert (home / '.agents/skills/research-paper-workflow/SKILL.md').read_text() == 'existing user Skill\n'
        cases.append('single_capability_install_preserves_other_names')
    result = {'passed': len(cases), 'cases': cases, 'python': sys.version.split()[0], 'scope': 'Temporary isolated home; actual Codex installer copy/validation helpers; no global Skill installation, model call or network needed.'}
    (Path(__file__).parent / 'selfcheck-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
