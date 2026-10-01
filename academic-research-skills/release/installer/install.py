#!/usr/bin/env python3
"""Install the pinned release with Codex's existing local copy helpers."""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
import shutil
import stat
import sys
import tempfile
import uuid
import zipfile

VERSION = '@VERSION@'
STEM = 'academic-research-skills-v' + VERSION
ARCHIVE_SHA = '@RUNTIME_SHA256@'
NAMES = '''analysis-execution citation-audit data-discovery data-preparation ethics-protocol
journal-intelligence literature-discovery manuscript-review manuscript-writing paper-deep-reading
peer-review-response publication-stewardship research-design research-intake research-paper-workflow
robustness-reproducibility scientific-visualization submission-packaging topic-novelty'''.split()
BASE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exists(path):
    return os.path.lexists(path)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def write(path, data):
    pending = path.with_suffix('.tmp')
    pending.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(pending, path)


def package():
    path = BASE / (STEM + '.zip')
    if sha(path) != ARCHIVE_SHA:
        raise ValueError('安装包 SHA-256 不匹配；未修改已安装的 Skill。请重新取得完整安装包。')
    with zipfile.ZipFile(path) as z:
        manifest = json.loads(z.read(STEM + '/PACKAGE-MANIFEST.json'))
        require(manifest['version'] == VERSION and manifest['kind'] == 'runtime', '发行包版本或类型不符。')
        expected = {STEM + '/' + p for p in manifest['files']} | {STEM + '/PACKAGE-MANIFEST.json'}
        require(len(z.infolist()) == len(expected) and set(z.namelist()) == expected, '发行包文件集合不符。')
        for info in z.infolist():
            p = PurePosixPath(info.filename)
            require(not p.is_absolute() and '..' not in p.parts and p.parts[0] == STEM, '不安全的归档路径。')
            require(stat.S_IFMT(info.external_attr >> 16) != stat.S_IFLNK, '归档中存在符号链接。')
        for rel, digest in manifest['files'].items():
            require(hashlib.sha256(z.read(STEM + '/' + rel)).hexdigest() == digest, '文件摘要不符：' + rel)
        require(z.testzip() is None, 'ZIP CRC 检查失败。')
    identities = {}
    for name in NAMES:
        prefix = 'skills/' + name + '/'
        identities[name] = {p[len(prefix):]: dig for p, dig in manifest['files'].items() if p.startswith(prefix)}
        require('SKILL.md' in identities[name], '缺少能力入口：' + name)
    return path, identities


def matches(folder, identities):
    if folder.is_symlink() or not folder.is_dir():
        return False
    files = list(folder.rglob('*'))
    if any(p.is_symlink() for p in files):
        return False
    actual = {p.relative_to(folder).as_posix(): sha(p) for p in files if p.is_file() and '__pycache__' not in p.relative_to(folder).parts and p.suffix != '.pyc' and p.name != '.DS_Store'}
    return actual == identities


def helper(path):
    if not path.is_file():
        raise ValueError('未找到 Codex 的系统 skill-installer。请先安装并打开 Codex；教程另有手动安装步骤。')
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location('_academic_codex_installer', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    # ponytail: reuse two existing helper interfaces; abort on change, CLI is the fallback.
    for name in ('_validate_skill', '_copy_skill'):
        if not callable(getattr(module, name, None)):
            raise ValueError('系统安装器接口已改变。尚未修改原目录；请使用教程中的官方安装器命令。')
    return module


def roots(home, codex_home):
    result = []
    for p in (home / '.agents/skills', codex_home / 'skills', home / '.codex/skills'):
        if not any(p.resolve() == q.resolve() for q in result):
            result.append(p)
    return result


def undo(receipt, backup, allowed_roots):
    target = Path(receipt['target'])
    require(target.resolve() in {p.resolve() for p in allowed_roots}, '收据的目标目录不符。')
    require(receipt['version'] == VERSION and receipt['status'] == 'installed', '该收据不能用于恢复。')
    for name in receipt['installed']:
        require(name in NAMES and matches(target / name, receipt['identities'][name]), '当前 Skill 已被修改，停止恢复并保留所有文件：' + name)
    for original in receipt['originals']:
        p, old = Path(original['path']), Path(original['backup'])
        require(p.name in NAMES and p.parent.resolve() in {r.resolve() for r in allowed_roots}, '旧目录路径不符。')
        require(old.is_relative_to(backup) and '..' not in old.parts and exists(old), '旧目录备份缺失或路径不符。')
        require(not exists(p) or (p.parent.resolve() == target.resolve() and p.name in receipt['installed']), '旧目录位置已出现其他文件。')
    saved = backup / 'new-after-restore'
    saved.mkdir(exist_ok=True)
    for name in receipt['installed']:
        os.replace(target / name, saved / name)
    for original in reversed(receipt['originals']):
        p = Path(original['path']); p.parent.mkdir(parents=True, exist_ok=True)
        os.replace(original['backup'], p)
    receipt['status'] = 'restored'
    write(backup / 'receipt.json', receipt)
    print('旧目录已恢复。新版本副本保留于：' + str(saved))


def install(home, codex_home, installer, selected):
    archive, identities = package()
    locations = roots(home, codex_home)
    target = locations[0]
    if all(matches(target / name, identities[name]) for name in selected) and not any(exists(p / name) for p in locations[1:] for name in selected):
        print('所选 Skill 已是完整 ' + VERSION + '，无需重复安装。'); return
    copier = helper(installer)
    target.parent.mkdir(parents=True, exist_ok=True)
    # ponytail: one installer transaction at a time; no background service needed.
    backup_root = codex_home / 'academic-research-skills-backups'
    backup = backup_root / (VERSION + '-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:6])
    with tempfile.TemporaryDirectory(prefix='.academic-skill-stage-', dir=target.parent) as tmp:
        stage = Path(tmp)
        with zipfile.ZipFile(archive) as z:
            z.extractall(stage / 'release')
        source = stage / 'release' / STEM
        ready = stage / 'ready'
        for name in selected:
            copier._validate_skill(str(source / 'skills' / name), str(source))
            copier._copy_skill(str(source / 'skills' / name), str(ready / name))
            require(matches(ready / name, identities[name]), '暂存文件不符：' + name)
        target.mkdir(parents=True, exist_ok=True)
        require(target.stat().st_dev == backup_root.stat().st_dev, 'Skill 目录和备份目录位于不同磁盘；请采用手动安装。')
        for root in locations:
            for name in selected:
                p = root / name
                if exists(p):
                    require(p.parent.stat().st_dev == backup_root.stat().st_dev, '旧 Skill 与备份目录位于不同磁盘。')
        backup.mkdir()
        record = {'version': VERSION, 'status': 'installing', 'archive_sha256': ARCHIVE_SHA, 'target': str(target), 'selected': selected, 'installed': [], 'originals': [], 'identities': {n: identities[n] for n in selected}}
        write(backup / 'receipt.json', record)
        try:
            for i, root in enumerate(locations):
                for name in selected:
                    old = root / name
                    if exists(old):
                        dest = backup / 'old' / str(i) / name
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        os.replace(old, dest)
                        record['originals'].append({'path': str(old), 'backup': str(dest)})
                        write(backup / 'receipt.json', record)
            for name in selected:
                os.replace(ready / name, target / name)
                record['installed'].append(name)
                write(backup / 'receipt.json', record)
            require(all(matches(target / n, identities[n]) for n in selected), '安装后文件摘要不符。')
            record['status'] = 'installed'
            write(backup / 'receipt.json', record)
        except BaseException:
            failed = backup / 'failed-new'; failed.mkdir(exist_ok=True)
            for name in reversed(record['installed']):
                os.replace(target / name, failed / name)
            for original in reversed(record['originals']):
                os.replace(original['backup'], original['path'])
            record['status'] = 'rolled_back'
            write(backup / 'receipt.json', record)
            raise
    print('安装完成：' + str(len(selected)) + ' 个 Skill，版本 ' + VERSION)
    print('安装位置：' + str(target))
    print('旧版本备份与安装收据：' + str(backup))
    print('下一轮在 Codex 中使用；如果未出现，请重启 Codex。')


def main():
    if sys.version_info < (3, 9):
        raise ValueError('本安装脚本需要 Python 3.9 或以上；科学工具另需 Python 3.10 或以上。')
    parser = argparse.ArgumentParser(description='一键安装完整通用学术 Skill，默认安装全部 19 项。')
    parser.add_argument('--home', type=Path, default=Path.home(), help='用于隔离安装测试，默认当前用户目录')
    parser.add_argument('--installer', type=Path, help='已有 Codex 系统安装器路径')
    parser.add_argument('--skill', nargs='+', choices=NAMES, help='仅安装所选能力；默认全部')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='只读检查当前目录与原版字节')
    mode.add_argument('--restore', type=Path, help='按备份目录内 receipt.json 恢复')
    args = parser.parse_args()
    home = args.home.expanduser().absolute()
    codex_home = Path(os.environ.get('CODEX_HOME', str(home / '.codex'))).expanduser().absolute()
    locations = roots(home, codex_home)
    selected = list(dict.fromkeys(args.skill or NAMES))
    if args.check:
        _, identities = package()
        bad = [n for n in selected if not matches(locations[0] / n, identities[n])]
        duplicates = [str(p / n) for p in locations[1:] for n in selected if exists(p / n)]
        print(json.dumps({'version': VERSION, 'target': str(locations[0]), 'selected': len(selected), 'matching': len(selected) - len(bad), 'missing_or_changed': bad, 'other_user_copies': duplicates, 'scope': '必需文件及源码摘要，忽略 Python/Finder 缓存；Codex 的实际加载另按教程确认'}, ensure_ascii=False, indent=2))
        return int(bool(bad or duplicates))
    backup_root = codex_home / 'academic-research-skills-backups'
    backup_root.mkdir(parents=True, exist_ok=True)
    with (backup_root / '.install.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('另一安装或恢复操作正在运行，请等待其完成。')
        if args.restore:
            backup = args.restore.expanduser().absolute()
            require(backup.resolve().is_relative_to(backup_root.resolve()) and not backup.is_symlink(), '请选择本安装器创建的备份目录。')
            undo(json.loads((backup / 'receipt.json').read_text(encoding='utf-8')), backup, locations)
        else:
            installer = args.installer or codex_home / 'skills/.system/skill-installer/scripts/install-skill-from-github.py'
            if not installer.is_file() and not args.installer:
                installer = home / '.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py'
            install(home, codex_home, installer, selected)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Exception, KeyboardInterrupt) as error:
        print('未完成：' + str(error), file=sys.stderr)
        raise SystemExit(1)
