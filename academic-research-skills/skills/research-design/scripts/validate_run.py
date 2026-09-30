#!/usr/bin/env python3
"""Check local run structure and recorded delivery conditions; never certify science.

Standard-library only. The schema checker deliberately supports only the subset
used by the bundled schemas and fails on unknown validation keywords.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path, PureWindowsPath
from typing import Any

SCHEMA_KEYS = {'$schema', '$id', 'title', 'description', 'type', 'required',
               'properties', 'additionalProperties', 'items', 'enum', 'const',
               'minLength', 'minItems', 'pattern', 'minimum', 'uniqueItems',
               'examples', 'default'}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_path(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('Expected a nonempty POSIX relative path')
    rel = Path(value)
    if rel.is_absolute() or PureWindowsPath(value).is_absolute() or '..' in rel.parts:
        raise ValueError('Absolute paths and parent traversal are forbidden')
    target = (root / rel).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Path or symlink escapes the run directory')
    return target


def matches_type(value: Any, kind: str) -> bool:
    return {
        'object': isinstance(value, dict),
        'array': isinstance(value, list),
        'string': isinstance(value, str),
        'integer': isinstance(value, int) and not isinstance(value, bool),
        'number': isinstance(value, (int, float)) and not isinstance(value, bool),
        'boolean': isinstance(value, bool),
        'null': value is None,
    }.get(kind, False)


def check_schema(value: Any, schema: dict[str, Any], location: str = '$') -> list[str]:
    errors: list[str] = []
    unknown = set(schema) - SCHEMA_KEYS
    if unknown:
        return [f'{location}: unsupported schema keywords {sorted(unknown)}']
    kinds = schema.get('type', [])
    kinds = [kinds] if isinstance(kinds, str) else kinds
    if kinds and not any(matches_type(value, kind) for kind in kinds):
        return [f'{location}: expected {kinds}, got {type(value).__name__}']
    if 'const' in schema and value != schema['const']:
        errors.append(f'{location}: incorrect constant')
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{location}: value is not in allowed enum')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                errors.append(f'{location}: missing required field {key}')
        props = schema.get('properties', {})
        if schema.get('additionalProperties') is False:
            for key in value.keys() - props.keys():
                errors.append(f'{location}: unexpected field {key}')
        for key, sub in props.items():
            if key in value:
                errors.extend(check_schema(value[key], sub, f'{location}.{key}'))
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            errors.append(f'{location}: too few items')
        if schema.get('uniqueItems'):
            encoded = [json.dumps(x, sort_keys=True, ensure_ascii=False) for x in value]
            if len(encoded) != len(set(encoded)):
                errors.append(f'{location}: duplicate array items')
        if 'items' in schema:
            for idx, item in enumerate(value):
                errors.extend(check_schema(item, schema['items'], f'{location}[{idx}]'))
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0):
            errors.append(f'{location}: empty or too short')
        if 'pattern' in schema and re.search(schema['pattern'], value) is None:
            errors.append(f'{location}: pattern mismatch')
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if 'minimum' in schema and value < schema['minimum']:
            errors.append(f'{location}: below minimum')
    return errors


def check_timestamp(value: str) -> bool:
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).tzinfo is not None
    except (TypeError, ValueError):
        return False


def validate(root: Path, skill_root: Path, completion: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    report: dict[str, Any] = {
        'validator': 'academic-run-structural-checker', 'version': '3.2.0-rc.1',
        'run_directory': str(root.resolve()), 'checks': [
            'bundled_schema_subset', 'file_existence_and_hashes',
            'local_reference_resolution', 'declared_gate_and_output_consistency'],
        'scientific_validity_certified': False,
        'external_sources_verified_by_this_script': False,
        'human_approvals_verified_by_this_script': False,
        'errors': errors, 'warnings': warnings,
    }
    try:
        cfg = read_json(skill_root / 'assets/contract.json')
        data = read_json(root / 'run.json')
        schema = read_json(skill_root / 'assets/run.schema.json')
        record_schema = read_json(skill_root / 'assets/record.schema.json')
    except (OSError, ValueError, TypeError) as exc:
        errors.append(f'Cannot load run or bundled contract: {exc}')
        report['status'] = 'failed'
        return report
    errors.extend(check_schema(data, schema))
    if errors:
        report['status'] = 'failed'
        return report
    if data['skill'] != cfg['skill']:
        errors.append('Run belongs to a different skill')
    if data['schema_version'] != cfg['schema_version']:
        errors.append('Contract version mismatch')
    for key in ('created_at', 'updated_at'):
        if not check_timestamp(data[key]):
            errors.append(f'{key}: timezone-aware ISO timestamp required')
    strict = completion or data['status'] == 'completed'
    if completion and data['status'] != 'completed':
        errors.append('Completion check requested but run is not marked completed')

    ids: set[str] = set()
    artifact_ids: set[str] = set()
    source_ids: set[str] = set()
    record_ids: set[str] = set()
    files: set[str] = set()
    for item in data['inputs']:
        if item['id'] in ids:
            errors.append(f'Duplicate object ID: {item["id"]}')
        ids.add(item['id'])
    for item in data['sources']:
        sid = item['id']
        if sid in ids:
            errors.append(f'Duplicate object ID: {sid}')
        ids.add(sid); source_ids.add(sid)
        if item['verification_status'] == 'verified' and item['checked_at'] is None:
            errors.append(f'Source {sid}: verified claim needs a recorded check time')
        if item['checked_at'] is not None and not check_timestamp(item['checked_at']):
            errors.append(f'Source {sid}: invalid timestamp')
    for item in data['artifacts']:
        aid = item['id']
        if aid in ids:
            errors.append(f'Duplicate object ID: {aid}')
        ids.add(aid); artifact_ids.add(aid)
        try:
            path = safe_path(root, item['path'])
            if not path.is_file():
                errors.append(f'Artifact {aid}: file does not exist')
            else:
                if str(path) in files:
                    errors.append(f'Artifact {aid}: same file registered more than once')
                files.add(str(path))
                if sha256_file(path) != item['sha256']:
                    errors.append(f'Artifact {aid}: checksum mismatch')
        except (ValueError, OSError) as exc:
            errors.append(f'Artifact {aid}: {exc}')

    records: list[dict[str, Any]] = []
    try:
        path = safe_path(root, cfg['records_file'])
        with path.open(encoding='utf-8-sig') as f:
            for line_no, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                    problems = check_schema(record, record_schema, f'record:{line_no}')
                    errors.extend(problems)
                    if problems:
                        continue
                    rid = record['id']
                    if rid in ids:
                        errors.append(f'Duplicate object ID: {rid}')
                    ids.add(rid); record_ids.add(rid); records.append(record)
                except (ValueError, TypeError) as exc:
                    errors.append(f'record:{line_no}: invalid JSON: {exc}')
    except (OSError, ValueError) as exc:
        errors.append(f'Record file unavailable: {exc}')
    if strict and not records:
        errors.append('A completed run needs at least one actual task record')
    if strict and not data['request'].strip():
        errors.append('A completed run needs the actual user request/scope')

    for item in data['artifacts']:
        for ref in item['depends_on']:
            if ref not in ids:
                errors.append(f'Artifact {item["id"]}: unknown dependency {ref}')
        if item['id'] in item['depends_on']:
            errors.append(f'Artifact {item["id"]}: self dependency')
    # A completed evidence artifact graph must be acyclic.
    graph = {a['id']: [x for x in a['depends_on'] if x in artifact_ids]
             for a in data['artifacts']}
    visited: set[str] = set(); active: set[str] = set()
    def visit(node: str) -> None:
        if node in active:
            errors.append(f'Artifact dependency cycle includes {node}')
            return
        if node in visited:
            return
        active.add(node)
        for child in graph.get(node, []):
            visit(child)
        active.remove(node); visited.add(node)
    for node in graph:
        visit(node)
    for item in records:
        for ref in item['source_refs']:
            if ref not in source_ids:
                errors.append(f'Record {item["id"]}: unknown source {ref}')
        for ref in item['artifact_refs']:
            if ref not in artifact_ids:
                errors.append(f'Record {item["id"]}: unknown artifact {ref}')
        if not check_timestamp(item['created_at']):
            errors.append(f'Record {item["id"]}: invalid timestamp')
        if item['status'] in ('observed', 'assessed') and not (
                item['source_refs'] or item['artifact_refs']):
            errors.append(f'Record {item["id"]}: assessment/observation needs evidence references')
        if item['status'] in ('observed', 'assessed') and not any(
                v is not None and v != '' and v != [] and v != {}
                for v in item['fields'].values()):
            errors.append(f'Record {item["id"]}: empty template is not an observation')
        if strict and item['status'] == 'draft':
            errors.append(f'Record {item["id"]}: unresolved draft task record')
    by_role = {o['role']: o for o in data['outputs']}
    if len(by_role) != len(data['outputs']):
        errors.append('Duplicate output role')
    for role in cfg['output_roles']:
        if role not in by_role:
            errors.append(f'Required output declaration removed: {role}')
    for item in data['outputs']:
        if item['role'] not in cfg['output_roles']:
            warnings.append(f'Extra output role: {item["role"]}')
        if item['status'] == 'produced' and item['artifact_id'] not in artifact_ids:
            errors.append(f'Output {item["role"]}: produced without registered artifact')
        if item['status'] == 'produced' and item['artifact_id'] in artifact_ids:
            artifact = next(a for a in data['artifacts'] if a['id'] == item['artifact_id'])
            if artifact['role'] != item['role']:
                errors.append(f'Output {item["role"]}: artifact role mismatch')
        if not item['required'] and not item['reason']:
            errors.append(f'Output {item["role"]}: narrowed scope needs a reason')
        if strict and item['required'] and item['status'] != 'produced':
            errors.append(f'Output {item["role"]}: required output not produced')
    by_gate = {g['id']: g for g in data['gates']}
    if len(by_gate) != len(data['gates']):
        errors.append('Duplicate gate ID')
    for key in cfg['gates']:
        if key not in by_gate:
            errors.append(f'Required gate removed: {key}')
    for gate in data['gates']:
        for ref in gate['evidence_refs']:
            if ref not in ids:
                errors.append(f'Gate {gate["id"]}: unknown evidence {ref}')
        if gate['status'] in ('pass', 'not_applicable'):
            if not gate['reason'] or not gate['evidence_refs']:
                errors.append(f'Gate {gate["id"]}: claimed outcome needs reason and evidence')
        if strict and gate['status'] not in ('pass', 'not_applicable'):
            errors.append(f'Gate {gate["id"]}: not resolved')
    for item in data['external_dependencies']:
        for ref in item['evidence_refs']:
            if ref not in ids:
                errors.append(f'External dependency: unknown evidence {ref}')
    if strict and data['external_dependencies']:
        for item in data['external_dependencies']:
            if item['blocks_current_scope'] and item['status'] != 'resolved':
                errors.append(f'Unresolved blocking dependency: {item["description"]}')
    report['record_count'] = len(records)
    report['artifact_count'] = len(artifact_ids)
    report['status'] = 'failed' if errors else (
        'recorded_completion_checks_passed' if strict else 'structure_passed')
    if not errors:
        warnings.append('Passing this checker does not establish factual truth, scientific validity, or journal readiness.')
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_directory', type=Path)
    parser.add_argument('--completion', action='store_true')
    parser.add_argument('--report', type=Path, help='Optional JSON report path; parent must exist')
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    report = validate(args.run_directory.resolve(), skill_root, args.completion)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.report:
        try:
            args.report.write_text(payload + '\n', encoding='utf-8')
        except OSError as exc:
            print(f'Cannot write report: {exc}', file=sys.stderr)
            return 2
    print(payload)
    return 1 if report['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
