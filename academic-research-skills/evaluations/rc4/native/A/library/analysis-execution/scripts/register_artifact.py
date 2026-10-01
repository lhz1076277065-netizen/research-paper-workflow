#!/usr/bin/env python3
"""Register an actual local output and its hash. Does not mark any gate passed.

Writers using this helper take an exclusive local lock. Other writers must also
respect it; this is not a distributed concurrency-control system.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from validate_run import read_json, safe_path, sha256_file


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('run_directory', type=Path)
    p.add_argument('--path', required=True, help='File path relative to run directory')
    p.add_argument('--id', required=True)
    p.add_argument('--role', required=True)
    p.add_argument('--depends-on', action='append', default=[])
    a = p.parse_args()
    root = a.run_directory.resolve()
    lock = root / '.run-write.lock'
    acquired = False
    tmpname: str | None = None
    try:
        target = safe_path(root, a.path)
        if not target.is_file():
            raise ValueError('The actual artifact file must exist')
        if target == (root / 'run.json').resolve():
            raise ValueError('run.json cannot register itself as an output')
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd); acquired = True
        data = read_json(root / 'run.json')
        if any(x['id'] == a.id for x in data['artifacts'] + data['sources']):
            raise ValueError('ID already exists; create a new version instead of overwriting')
        if any(x['path'] == a.path for x in data['artifacts']):
            raise ValueError('File already registered; use a new version/path')
        data['artifacts'].append({'id':a.id, 'path':a.path, 'role':a.role,
                                  'sha256':sha256_file(target), 'depends_on':a.depends_on,
                                  'generation_method':'registered existing file; provenance must be described in task records'})
        for output in data['outputs']:
            if output['role'] == a.role:
                output.update(status='produced', artifact_id=a.id)
        data['updated_at'] = datetime.now(timezone.utc).isoformat()
        fd, tmpname = tempfile.mkstemp(prefix='.run-', suffix='.json', dir=root)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2); f.write('\n')
            f.flush(); os.fsync(f.fileno())
        os.replace(tmpname, root / 'run.json'); tmpname = None
        print(json.dumps({'registered':a.id,'sha256':sha256_file(target),'gates_unchanged':True},ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Artifact registration failed: {exc}', file=sys.stderr)
        return 2
    finally:
        if tmpname:
            Path(tmpname).unlink(missing_ok=True)
        if acquired:
            lock.unlink(missing_ok=True)


if __name__ == '__main__':
    raise SystemExit(main())
