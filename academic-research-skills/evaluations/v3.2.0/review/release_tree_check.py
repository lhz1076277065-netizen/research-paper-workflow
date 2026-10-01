#!/usr/bin/env python3
"""Read-only release/interface preservation and user-document package projection."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
REPO = ROOT.parent
BASE = '9813b193a2cd6504205ede70393c22c7683e22c6'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO)


def original(path):
    return git('show', BASE + ':' + path.relative_to(REPO).as_posix())


def local_links(path):
    for target in re.findall(r'\]\(([^\s)]+)\)', path.read_text()):
        parsed = urlsplit(target.strip('<>'))
        if not parsed.scheme and not parsed.netloc and parsed.path:
            yield target, (path.parent / unquote(parsed.path)).resolve()


def main():
    scripts = sorted((ROOT / 'src/common/scripts').glob('*.py'))
    entries = sorted((ROOT / 'src/quality31/payload/skills').glob('*/SKILL.md'))
    protocols = sorted((ROOT / 'skills').glob('*/references/protocol.md'))
    checks = {
        'version_is_3_2_0': (ROOT / 'VERSION').read_text().strip() == '3.2.0',
        'runtime_identical_except_version': all(p.read_bytes() == original(p).replace(b'3.2.0-rc.5', b'3.2.0') for p in scripts),
        'entries_identical_except_version': len(entries) == 19 and all(p.read_bytes() == original(p).replace(b'3.2.0-rc.5', b'3.2.0') for p in entries),
        'protocols_unchanged': len(protocols) == 19 and all(p.read_bytes() == original(p) for p in protocols),
        'result_task_return_schemas_unchanged': all((ROOT / 'src/common/assets' / n).read_bytes() == original(ROOT / 'src/common/assets' / n)
                                                 for n in ['result-links.schema.json', 'task.schema.json', 'result.schema.json']),
    }
    profiles = json.loads((ROOT / 'src/common/assets/research-profiles.json').read_text())
    policy = json.loads((ROOT / 'src/common/assets/research31-policy.json').read_text())
    counts = {'capabilities': len(list((ROOT / 'skills').glob('*/SKILL.md'))), 'profiles': len(profiles['profiles']),
              'routes': len(profiles['computational_routes']), 'sources': len(policy['sources'])}
    checks['counts_preserved'] = counts == {'capabilities': 19, 'profiles': 16, 'routes': 14, 'sources': 13}
    for filename in ['research-profiles.json', 'research31-policy.json', 'environment-profiles.json']:
        path = ROOT / 'src/common/assets' / filename
        checks[filename + '_metadata_only'] = path.read_bytes() == original(path).replace(b'3.2.0-rc.5', b'3.2.0')
    retained = git('ls-tree', '-rz', BASE, '--', 'academic-research-skills/evaluations/rc5').split(b'\0')
    changed = []
    for item in filter(None, retained):
        identity, path = item.split(b'\t', 1)
        digest = identity.split()[2].decode()
        actual = REPO / path.decode()
        body = actual.read_bytes() if actual.is_file() else None
        if body is None or hashlib.sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest() != digest:
            changed.append(path.decode())
    checks['all_existing_rc5_evaluation_bytes_preserved'] = not changed
    spec = importlib.util.spec_from_file_location('review_package_projection', ROOT / 'release/make_package.py')
    package = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(package)
    runtime = {p.resolve() for p in package.chosen('runtime')}
    broken = []
    for path in sorted(runtime):
        if path.suffix != '.md' or (path.parent != ROOT and path.relative_to(ROOT).parts[0] not in {'docs', 'evaluations'}):
            continue
        for target, resolved in local_links(path):
            if resolved.is_relative_to(ROOT) and (not resolved.exists() or (resolved.is_file() and resolved not in runtime)):
                broken.append({'from': path.relative_to(ROOT).as_posix(), 'target': target})
    checks['runtime_user_document_file_links_resolve'] = not broken
    root_broken = [{'from': 'README.md', 'target': target} for target, resolved in local_links(REPO / 'README.md') if not resolved.exists()]
    checks['root_readme_file_links_resolve'] = not root_broken
    installer_relative = [target for target, _ in local_links(ROOT / 'INSTALLATION.zh-CN.md')]
    checks['one_click_copied_tutorial_has_no_missing_relative_links'] = not installer_relative
    for path in [REPO / 'README.md', ROOT / 'INSTALLATION.zh-CN.md', REPO / 'installation/RELEASE_CHECKLIST.zh-CN.md']:
        checks[path.relative_to(REPO).as_posix() + '_install_ref_current'] = 'v3.2.0-rc.' not in path.read_text()
    build = subprocess.run([sys.executable, str(ROOT / 'scripts/build_release.py'), '--check'], capture_output=True, text=True)
    build_report = json.loads(build.stdout)
    checks['generated_build_clean'] = build.returncode == 0 and build_report['status'] == 'clean' and build_report['generated_files'] == 937
    result = {'base': BASE, 'python': sys.version, 'checks': checks, 'passed': all(checks.values()), 'counts': counts,
              'preserved_rc5_files': len(list(filter(None, retained))), 'changed_rc5_files': changed,
              'runtime_user_document_broken_links': broken, 'root_readme_broken_links': root_broken,
              'one_click_tutorial_relative_links': installer_relative, 'build': build_report,
              'result_links_sha256': hashlib.sha256((ROOT / 'src/common/scripts/result_links.py').read_bytes()).hexdigest(),
              'reviewed_navigation_sha256': {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in [REPO / 'README.md', ROOT / 'README.md', ROOT / 'README.zh-CN.md', ROOT / 'MIGRATION.zh-CN.md',
                            ROOT / 'INSTALLATION.zh-CN.md', ROOT / 'docs/COMPATIBILITY.zh-CN.md', ROOT / 'release/make_package.py']},
              'scope': 'Local frozen source and runtime selection projection, not final ZIP, remote default branch or GitHub release verification.'}
    Path(sys.argv[1]).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'passed': result['passed'], 'failed': [k for k, v in checks.items() if not v], 'preserved_rc5_files': result['preserved_rc5_files']}))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
