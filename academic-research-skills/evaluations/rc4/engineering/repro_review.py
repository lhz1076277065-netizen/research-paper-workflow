"""Run with Python 3.10+; synthetic software-contract reproductions only."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path('/Users/luca/Documents/ChatGPT/学术skill/iteration-20260930061350/repository/academic-research-skills')

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

audit = module('review_result_links', ROOT / 'src/common/scripts/result_links.py')
bridge = module('review_provider_runtime', ROOT / 'src/common/scripts/provider_runtime.py')

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    def artifact(name):
        return {'path': name, 'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest()}
    for name in ('data.csv', 'code.py', 'execution.json'):
        (root / name).write_text('synthetic version binding')
    (root / 'results.json').write_text(json.dumps({'R1': {'value': '.12', 'lower': '.10', 'upper': '.15', 'unit': 'ratio'}}))
    (root / 'draft.md').write_text('The estimate is 99.00% (10.00%-15.00%).\n')
    payload = {'kind': 'result-links', 'sources': [dict(artifact('results.json'), id='frozen', versions={key: artifact(name) for key, name in [('data', 'data.csv'), ('code', 'code.py'), ('execution', 'execution.json')]})],
        'links': [{'result_id': 'R1', 'role': 'body', 'artifact': artifact('draft.md'), 'locator': {'line': 1},
            'numeric': [{'field': 'lower', 'text': '10.00', 'decimals': 2}, {'field': 'upper', 'text': '15.00', 'decimals': 2}],
            'semantics': {'unit': {'value': 'percent', 'text': '%'}}}]}
    result = audit.audit_links(payload, root)
    assert not result['passed'] and any('value' in message for message in result['errors']), result
    print(json.dumps({'omitted_estimate_passed': result['passed'], 'checked_fields': [r['field'] for r in result['coverage']['numeric']], 'source_estimate': '12%', 'manuscript_estimate': '99%'}))
    task = {'capability': 'manuscript-writing', 'request': 'Synthetic result audit only', 'requested_outputs': ['draft'], 'facts': {'has_verified_results': True}}
    handoff = root / 'handoff'
    bridge.prepare_handoff(task, {}, {'capabilities': ['manuscript-writing'], 'providers': []}, handoff)
    envelope = {'capability': task['capability'], 'task_sha256': bridge.sha(handoff / 'task.json'), 'provider_id': 'host_fallback', 'execution_mode': 'host_fallback', 'execution_status': 'executed', 'outputs': [dict(artifact('draft.md'), role='draft')], 'result_links': payload}
    accepted = bridge.accept_result(handoff, envelope, root)
    assert not accepted['passed'], accepted
    print(json.dumps({'wrong_estimate_accept_result_passed': accepted['passed'], 'status': accepted['status']}))

with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    package = root / 'academic-research-skills'
    (package / 'release').mkdir(parents=True)
    shutil.copyfile(ROOT / 'release/make_package.py', package / 'release/make_package.py')
    (package / 'VERSION').write_text('3.2.0-rc.4\n')
    (root / '.gitignore').write_text('__pycache__/\n*.py[cod]\nvalidation-report.json\n')
    def git(*args):
        return subprocess.check_output(['git', *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    git('init')
    git('add', '.')
    git('-c', 'user.name=Synthetic Review', '-c', 'user.email=review@example.invalid', 'commit', '-m', 'Synthetic package fixture')
    (package / 'validation-report.json').write_text('{"local_uncommitted_content": true}\n')
    assert git('status', '--porcelain', '--untracked-files=all') == ''
    pack = module('review_make_package', package / 'release/make_package.py')
    report = pack.pack('runtime', root / 'out')
    with zipfile.ZipFile(root / 'out' / report['file']) as z:
        included = any(name.endswith('/validation-report.json') for name in z.namelist())
    assert not included, report
    print(json.dumps({'clean_git_package_includes_ignored_uncommitted_file': included, 'claimed_source_commit': report['source_commit']}))
    shutil.copytree(ROOT / 'release/installer', package / 'release/installer')
    shutil.copyfile(ROOT / 'INSTALLATION.zh-CN.md', package / 'INSTALLATION.zh-CN.md')
    stale = root / 'out/academic-research-skills-v3.2.0-rc.4-one-click'
    stale.mkdir()
    (stale / 'uncommitted-old-file.py').write_text('synthetic stale file')
    try:
        installer = pack.one_click(report, root / 'out')
    except (ValueError, FileExistsError):
        print(json.dumps({'one_click_existing_folder': 'refused'}))
    else:
        with zipfile.ZipFile(root / 'out' / installer['file']) as z:
            inherited = any(name.endswith('/uncommitted-old-file.py') for name in z.namelist())
        assert not inherited, 'one_click inherited a non-source file from an existing output folder'
        print(json.dumps({'one_click_inherited_non_source_file': inherited}))
