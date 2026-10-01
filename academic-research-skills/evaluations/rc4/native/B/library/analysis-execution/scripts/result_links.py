#!/usr/bin/env python3
"""Read-only, bounded result occurrence and render dependency audits.

Frozen JSON/CSV outputs own the result values. Links own only manuscript locations
and display rules. Text extraction and declared semantic matching are not proof of
scientific truth, claim completeness or visual layout.
"""
from __future__ import annotations
import csv
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN, ROUND_HALF_UP, localcontext
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import unicodedata
import zipfile
from xml.etree import ElementTree as ET

SEMANTICS = ('unit', 'direction', 'denominator', 'outcome', 'population', 'sample',
             'time', 'comparison', 'model', 'split', 'uncertainty', 'effect_type')
DIRECTIONS = {'increase': ('increase', 'increased', 'increases', 'higher', 'positive'),
              'decrease': ('decrease', 'decreased', 'decreases', 'lower', 'negative'),
              'no-change': ('no-change', 'no change', 'unchanged')}
# Only dimensional conversions whose meaning is unambiguous are automatic.
UNITS = {'ratio': ('fraction', Decimal(1)), 'proportion': ('fraction', Decimal(1)),
         'percent': ('fraction', Decimal('.01')), '%': ('fraction', Decimal('.01')),
         'percentage': ('fraction', Decimal('.01')),
         'percentage-point': ('percentage-point', Decimal(1)), 'pp': ('percentage-point', Decimal(1)),
         's': ('time', Decimal(1)), 'second': ('time', Decimal(1)),
         'ms': ('time', Decimal('.001')), 'millisecond': ('time', Decimal('.001')),
         'g': ('mass', Decimal(1)), 'mg': ('mass', Decimal('.001')),
         'm': ('length', Decimal(1)), 'cm': ('length', Decimal('.01')), 'mm': ('length', Decimal('.001'))}


def _object(value, label):
    if not isinstance(value, dict):
        raise ValueError(label + ' must be an object')
    return value


def _list(value, label, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError(label + ' must be ' + ('a nonempty' if nonempty else 'a') + ' list')
    return value


def _string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must be a nonempty string')
    return value


def _path(root, relative):
    _string(relative, 'path')
    if Path(relative).is_absolute() or '\\' in relative or ':' in relative:
        raise ValueError('Invalid relative path: ' + relative)
    path = (root / relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Path escapes declared root: ' + relative)
    return path


def _sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def _artifact(spec, root, coverage):
    spec = _object(spec, 'artifact')
    path = _path(root, spec.get('path'))
    digest = spec.get('sha256')
    if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
        raise ValueError('Invalid sha256: ' + spec['path'])
    if not path.is_file() or not path.stat().st_size:
        raise ValueError('Missing or empty artifact: ' + spec['path'])
    actual = _sha(path)
    coverage.append({'path': spec['path'], 'role': spec.get('role'), 'expected_sha256': digest, 'actual_sha256': actual,
                     'matched': actual == digest})
    if actual != digest:
        raise ValueError('Artifact version mismatch: ' + spec['path'])
    return path


def _positive(value, label):
    if type(value) is not int or value < 1:
        raise ValueError(label + ' must be a positive integer (1-based)')
    return value


def _lines(text, locator):
    lines = text.splitlines()
    first = _positive(locator.get('line', locator.get('line_start')), 'line')
    last = _positive(locator.get('line_end', first), 'line_end')
    if last < first or last > len(lines):
        raise ValueError('Line locator outside actual text')
    return '\n'.join(lines[first - 1:last])


def _pdf_pages(path):
    binary = shutil.which('pdftotext')
    if binary:
        result = subprocess.run([binary, '-layout', '-enc', 'UTF-8', str(path), '-'],
                                capture_output=True, timeout=30)
        if result.returncode:
            raise ValueError('PDF text extraction failed: ' + path.name)
        return result.stdout.decode('utf-8').split('\f')
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ValueError('PDF extraction needs installed pdftotext or pypdf; no PDF occurrence was checked') from None
    return [page.extract_text() or '' for page in PdfReader(str(path)).pages]


def _located(path, locator, cache):
    locator = _object(locator, 'locator')
    extension = path.suffix.lower()
    if path not in cache:
        if extension == '.pdf':
            cache[path] = _pdf_pages(path)
        elif extension == '.docx':
            with zipfile.ZipFile(path) as archive:
                member = archive.getinfo('word/document.xml')
                if member.file_size > 64 * 1024 * 1024:
                    raise ValueError('DOCX document XML exceeds 64 MiB extraction limit')
                cache[path] = ET.fromstring(archive.read(member))
        elif extension in {'.md', '.markdown', '.tex', '.txt'}:
            cache[path] = path.read_text(encoding='utf-8-sig')
        else:
            raise ValueError('Occurrence format must be Markdown, LaTeX, text, DOCX or PDF')
    content = cache[path]
    if extension == '.pdf':
        page = _positive(locator.get('page'), 'page')
        if page > len(content) or not content[page - 1].strip():
            raise ValueError('Missing or unextractable PDF page')
        return _lines(content[page - 1], locator)
    if extension == '.docx':
        ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        if 'paragraph' in locator:
            items = list(content.iter(ns + 'p'))
            index = _positive(locator['paragraph'], 'paragraph')
            if index > len(items):
                raise ValueError('DOCX paragraph outside document')
            node = items[index - 1]
        else:
            body = content.find(ns + 'body')
            tables = [] if body is None else body.findall(ns + 'tbl')
            table = _positive(locator.get('table'), 'table')
            row = _positive(locator.get('row'), 'row')
            cell = _positive(locator.get('cell'), 'cell')
            if table > len(tables):
                raise ValueError('DOCX table outside document')
            rows = tables[table - 1].findall(ns + 'tr')
            if row > len(rows) or cell > len(rows[row - 1].findall(ns + 'tc')):
                raise ValueError('DOCX cell outside table')
            node = rows[row - 1].findall(ns + 'tc')[cell - 1]
        return ''.join(n.text or '' for n in node.iter(ns + 't'))
    return _lines(content, locator)


def _normal(value):
    text = unicodedata.normalize('NFKC', str(value)).casefold().replace('−', '-')
    text = re.sub(r'\\([%&_#$])', r'\1', text).replace('~', ' ')
    text = re.sub(r'\b(months|years|days|seconds|milliseconds|percentage points)\b',
                  lambda m: m.group(0)[:-1], text)
    return ' '.join(text.split())


def _present(text, token):
    pattern = re.escape(_normal(token))
    if token and str(token)[0].isalnum():
        pattern = r'(?<!\w)' + pattern
    if token and str(token)[-1].isalnum():
        pattern += r'(?!\w)'
    return re.search(pattern, _normal(text)) is not None


def _number(value, label):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError(label + ' must be finite numeric')
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise ValueError(label + ' must be finite numeric') from None
    if not number.is_finite():
        raise ValueError(label + ' must be finite numeric')
    return number


def _records(path):
    if path.suffix.lower() == '.csv':
        with path.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)) or any(not h for h in reader.fieldnames):
                raise ValueError('CSV needs unique nonempty headers')
            data = list(reader)
            if any(None in row or any(v is None for v in row.values()) for row in data):
                raise ValueError('CSV rows must match header width')
    elif path.suffix.lower() == '.json':
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        if isinstance(data, dict) and isinstance(data.get('results'), list):
            data = data['results']
    else:
        raise ValueError('Frozen results must be actual JSON or CSV outputs')
    if isinstance(data, dict):
        if 'result_id' in data:
            data = [data]
        else:
            if any(isinstance(row,dict) and row.get('result_id',rid)!=rid for rid,row in data.items()):
                raise ValueError('Result key and stored result_id disagree')
            data = [dict(_object(row, 'result record'), result_id=rid) for rid, row in data.items()]
    records = {}
    for row in _list(data, 'source result records', True):
        row = _object(row, 'result record')
        rid = _string(row.get('result_id'), 'result_id')
        if rid in records:
            raise ValueError('Duplicate result_id in frozen output: ' + rid)
        records[rid] = row
    return records


def _semantic_source(record):
    values = dict(_object(record.get('semantics', {}), 'source semantics'))
    for field in SEMANTICS:
        if field in record:
            values.setdefault(field, record[field])
    if 'sample_n' in record:
        values.setdefault('denominator', record['sample_n'])
    if 'uncertainty_type' in record:
        values.setdefault('uncertainty', record['uncertainty_type'])
    return values


def _value_and_labels(expected):
    if isinstance(expected, dict):
        value = expected.get('value')
        labels = _list(expected.get('labels', [str(value)]), 'source labels', True)
    else:
        value, labels = expected, [str(expected)]
    if value is None or isinstance(value, (dict, list, bool)) or any(not isinstance(s, str) or not s.strip() for s in labels):
        raise ValueError('Source semantic values must be scalar with nonempty source-defined labels')
    return value, labels


def _unit(value):
    normal = _normal(value)
    return UNITS.get(normal, (normal, Decimal(1)))


def _semantics(record, link, text, path, cache, coverage):
    expected = _semantic_source(record)
    mapped = _object(link.get('semantics', {}), 'link semantics')
    if set(mapped) - set(expected):
        raise ValueError('Semantic mapping lacks source meaning: ' + ','.join(sorted(set(mapped) - set(expected))))
    missing = set(expected) - set(mapped)
    if missing:
        raise ValueError('Missing semantic occurrence mappings: ' + ','.join(sorted(missing)))
    for field, original in expected.items():
        value, labels = _value_and_labels(original)
        mapping = _object(mapped[field], field + ' mapping')
        token = _string(mapping.get('text'), field + ' text')
        actual = mapping.get('value')
        scoped = _located(path, mapping['locator'], cache) if 'locator' in mapping else text
        if not _present(scoped, token):
            raise ValueError(field + ' text not found at actual locator: ' + token)
        if field == 'unit':
            label_match = _normal(actual)==_normal(value) and _normal(token) in {_normal(s) for s in labels}
            if _unit(value)[0] != _unit(actual)[0] or (_unit(actual) != _unit(token) and not label_match):
                raise ValueError('Unit mismatch or undeclared conversion')
        elif field == 'direction':
            def canonical(item):
                return next((key for key, words in DIRECTIONS.items() if _normal(item) in words), _normal(item))
            if canonical(value) != canonical(actual) or canonical(token) != canonical(value):
                raise ValueError('Direction mismatch')
        elif field == 'denominator':
            denominator = _number(value, 'source denominator')
            if denominator <= 0 or denominator != denominator.to_integral_value():
                raise ValueError('Denominator must be a positive integer count')
            if denominator != _number(actual, 'mapped denominator'):
                raise ValueError('Denominator mismatch')
            numbers = re.findall(r'(?<![\w.])[+-]?\d+(?:\.\d+)?(?![\w.])', token)
            if len(numbers) != 1 or _number(numbers[0], 'denominator text') != _number(value, 'denominator'):
                raise ValueError('Denominator text mismatch')
        else:
            if _normal(value) != _normal(actual) or _normal(token) not in {_normal(s) for s in labels}:
                raise ValueError(field + ' canonical meaning/text mismatch')
        coverage.append({'result_id': link['result_id'], 'role': link['role'], 'path': link['artifact']['path'],
                         'locator': mapping.get('locator', link['locator']), 'field': field,
                         'source_value': value, 'text': token})
    return expected, mapped


def _numeric(record, link, text, expected, mapped, sources, coverage):
    numbers = _list(link.get('numeric', []), 'numeric mappings', True)
    if record.get('lower') not in (None, '') and record.get('upper') not in (None, ''):
        lower, upper = _number(record['lower'], 'lower bound'), _number(record['upper'], 'upper bound')
        estimate = record.get('value', record.get('estimate'))
        if lower > upper or (estimate is not None and not lower <= _number(estimate, 'estimate') <= upper):
            raise ValueError('Source uncertainty interval is inconsistent')
    fields = set()
    for mapping in numbers:
        mapping = _object(mapping, 'numeric mapping')
        field = _string(mapping.get('field'), 'numeric field')
        if field in fields:
            raise ValueError('Duplicate numeric field mapping: ' + field)
        fields.add(field)
        raw = _number(record.get(field), 'source ' + field)
        token = _string(mapping.get('text'), 'numeric text')
        displayed = _number(token, 'displayed number')
        # A range separator is not the sign of its upper endpoint; preserve offsets.
        numeric_text = re.sub(r'(?<=[\d%])[-–—](?=\d)', ' ', text.replace('−', '-'))
        matches = list(re.finditer(r'(?<![\w.+-])' + re.escape(token) + r'(?![\w.])', numeric_text))
        offset = mapping.get('offset')
        if offset is not None:
            if type(offset) is not int or offset < 0 or not any(m.start() == offset for m in matches):
                raise ValueError('Numeric offset does not locate the actual token')
        elif len(matches) != 1:
            raise ValueError('Numeric token absent or ambiguous at locator: ' + token)
        factor = Decimal(1)
        if 'unit' not in expected:
            raise ValueError('Numeric source must declare unit, including dimensionless')
        source_unit = _value_and_labels(expected['unit'])[0]
        target_unit = mapped['unit']['value']
        factor = _unit(source_unit)[1] / _unit(target_unit)[1]
        unit_map = mapped['unit']
        if 'locator' not in unit_map:
            normalized = _normal(text)
            pair = str(unit_map['text']) + ' ' + token if unit_map.get('position') == 'prefix' else token + ' ' + str(unit_map['text'])
            if not re.search(re.escape(_normal(pair)).replace(r'\ ', r'\s*'), normalized):
                raise ValueError('Unit is not attached to the actual numeric occurrence')
        decimals = mapping.get('decimals')
        rounding = mapping.get('rounding', 'half-even')
        if rounding not in {'half-even', 'half-up'}:
            raise ValueError('Rounding must be half-even or half-up')
        with localcontext() as context:
            context.prec = max(50, len(raw.as_tuple().digits) + abs(raw.adjusted()) + 20)
            formatted = raw * factor
            if decimals is not None:
                if type(decimals) is not int or not 0 <= decimals <= 12:
                    raise ValueError('Display decimals must be an integer from 0 to 12')
                formatted = formatted.quantize(Decimal(1).scaleb(-decimals),
                    rounding=ROUND_HALF_EVEN if rounding == 'half-even' else ROUND_HALF_UP)
                if formatted.is_zero():
                    formatted = abs(formatted)
                if token != format(formatted, '.' + str(decimals) + 'f'):
                    raise ValueError('Displayed value/rounding mismatch: ' + field)
            elif displayed != formatted:
                raise ValueError('Displayed value mismatch: ' + field)
        tolerance = _object(mapping.get('tolerance', {}), 'numeric tolerance')
        absolute = _number(tolerance.get('abs', 0), 'absolute tolerance')
        relative = _number(tolerance.get('rel', 0), 'relative tolerance')
        if absolute < 0 or relative < 0:
            raise ValueError('Numeric tolerances must be nonnegative')
        recomputed = mapping.get('recomputed')
        if tolerance and recomputed is None:
            raise ValueError('Tolerance belongs to a hash-bound recomputation, not manuscript display')
        if recomputed is not None:
            recomputed = _object(recomputed, 'recomputed reference')
            source = sources.get(recomputed.get('source_id'))
            if source is None:
                raise ValueError('Unknown recomputation source_id')
            other = source['records'].get(recomputed.get('result_id', link['result_id']))
            if other is None:
                raise ValueError('Unknown recomputed result_id')
            value = _number(other.get(recomputed.get('field', field)), 'recomputed value')
            if abs(raw - value) > max(absolute, relative * max(abs(raw), abs(value))):
                raise ValueError('Recomputed numeric value exceeds tolerance: ' + field)
        coverage.append({'result_id': link['result_id'], 'role': link['role'], 'path': link['artifact']['path'],
                         'locator': link['locator'], 'field': field, 'source_value': str(raw),
                         'display_text': token, 'unit_factor': str(factor), 'decimals': decimals,
                         'rounding': rounding, 'recomputation_checked': recomputed is not None})
    for bound in ('lower', 'upper'):
        if record.get(bound) not in (None, '') and bound not in fields:
            raise ValueError('Missing uncertainty bound occurrence: ' + bound)


def _evidence(record, root, cache, byte_coverage, semantic_coverage):
    kind = record.get('type', 'numeric')
    if kind == 'theory':
        evidence = [record.get('proof')]
    elif kind == 'interpretive':
        evidence = _list(record.get('snippets'), 'interpretive source snippets', True)
    else:
        return
    for spec in evidence:
        spec = _object(spec, 'proof/source snippet')
        path = _artifact(dict(spec,role='proof' if kind=='theory' else 'source-snippet'), root, byte_coverage)
        text = _located(path, spec.get('locator'), cache)
        quote = _string(spec.get('text'), 'proof/source snippet text')
        if not _present(text, quote):
            raise ValueError('Proof/source snippet not found at source locator')
        semantic_coverage.append({'result_id': record['result_id'], 'role': 'proof' if kind=='theory' else 'source-snippet',
                                  'source_evidence': spec['path'], 'locator': spec['locator'], 'text': quote})


def _report(kind):
    return {'kind': kind, 'passed': False, 'errors': [], 'pending': [], 'checks': [],
            'coverage': {'bytes': [], 'numeric': [], 'declared_semantic': []},
            'scientific_validity_certified': False, 'semantic_truth_certified': False,
            'actual_visual_inspection_performed': False}


AUDIT_ERRORS = (OSError, ValueError, TypeError, KeyError, IndexError, InvalidOperation,
                zipfile.BadZipFile, ET.ParseError, subprocess.SubprocessError)


def audit_links(data, root):
    """Audit actual occurrences; invalid mappings return diagnostics, never execute."""
    report = _report('result-links')
    root = Path(root).resolve()
    sources, cache, checked_versions, successful = {}, {}, set(), []
    try:
        data = _object(data, 'result-links payload')
        for source in _list(data.get('sources'), 'sources', True):
            source = _object(source, 'source')
            sid = _string(source.get('id'), 'source id')
            if sid in sources:
                raise ValueError('Duplicate source id: ' + sid)
            path = _artifact(dict(source,role='frozen-results:'+sid), root, report['coverage']['bytes'])
            sources[sid] = {'records': _records(path), 'versions': source.get('versions', {})}
        links = _list(data.get('links'), 'links', True)
        for index, link in enumerate(links, 1):
            label = 'link ' + str(index)
            try:
                link = _object(link, label)
                rid = _string(link.get('result_id'), 'result_id')
                label += ' (' + rid + ')'
                sid = link.get('source_id', next(iter(sources)) if len(sources) == 1 else None)
                if sid not in sources or rid not in sources[sid]['records']:
                    raise ValueError('Unknown source_id/result_id')
                record = sources[sid]['records'][rid]
                path = _artifact(dict(_object(link.get('artifact'),'artifact'),role=link.get('role')), root, report['coverage']['bytes'])
                text = _located(path, link.get('locator'), cache)
                _string(link.get('role'), 'occurrence role')
                expected, mapped = _semantics(record, link, text, path, cache, report['coverage']['declared_semantic'])
                kind = record.get('type', 'numeric')
                if kind == 'numeric':
                    _numeric(record, link, text, expected, mapped, sources, report['coverage']['numeric'])
                elif kind in {'theory', 'interpretive'}:
                    required = ('proposition', 'conditions') if kind == 'theory' else ('interpretation',)
                    for field in required:
                        original = record.get(field)
                        mapping = _object(_object(link.get('bindings'), 'bindings').get(field), field + ' binding')
                        labels = original if isinstance(original, list) else [original]
                        tokens = mapping.get('texts', [mapping.get('text')])
                        if not labels or not isinstance(tokens, list) or len(tokens) != len(labels):
                            raise ValueError('Bind every ' + field + ' to actual target text')
                        for original, token in zip(labels, tokens):
                            _string(original, 'source ' + field)
                            _string(token, field + ' text')
                            if _normal(original) != _normal(token) or not _present(text, token):
                                raise ValueError(field + ' source/occurrence mismatch')
                            report['coverage']['declared_semantic'].append({'result_id': rid, 'role': link['role'],
                                'path': link['artifact']['path'], 'locator': link['locator'], 'field': field, 'text': token})
                else:
                    raise ValueError('Unknown result type')
                version_key = (sid, rid)
                if version_key not in checked_versions:
                    versions = _object(record.get('versions', sources[sid]['versions']), 'source versions')
                    if kind == 'numeric':
                        report['pending'].extend(rid + ': source version unbound: ' + name
                                                 for name in ('data', 'code', 'execution') if name not in versions)
                    for name, version in versions.items():
                        _artifact(dict(_object(version,'source version'),role='source-version:'+str(name)), root, report['coverage']['bytes'])
                    _evidence(record, root, cache, report['coverage']['bytes'], report['coverage']['declared_semantic'])
                    checked_versions.add(version_key)
                successful.append(link)
            except AUDIT_ERRORS as error:
                report['errors'].append(label + ': ' + str(error))
        claims = _list(data.get('claims', []), 'claims')
        claim_ids = set()
        for claim in claims:
            claim = _object(claim, 'claim')
            cid = _string(claim.get('id'), 'claim id')
            if cid in claim_ids:
                raise ValueError('Duplicate claim id: ' + cid)
            claim_ids.add(cid)
            path = _artifact(claim.get('artifact'), root, report['coverage']['bytes'])
            text = _located(path, claim.get('locator'), cache)
            if not _present(text, _string(claim.get('text'), 'claim text')):
                raise ValueError('Claim text not found: ' + cid)
            ids = _list(claim.get('result_ids', []), 'claim result_ids')
            bound = {l['result_id'] for l in successful if l.get('claim_id') == cid
                     and l['artifact'] == claim['artifact'] and l['locator'] == claim['locator']}
            if not ids or not set(ids).issubset(bound):
                report['pending'].append({'claim_id': cid, 'path': claim['artifact']['path'],
                    'locator': claim['locator'], 'text': claim['text'], 'action': 'Link this critical claim to frozen result(s) at this occurrence'})
        if any(link.get('claim_id') not in claim_ids for link in links if isinstance(link, dict) and 'claim_id' in link):
            report['errors'].append('Link references an undeclared claim_id')
        report['claim_inventory_complete'] = False
        report['checks'].append('Actual hash-bound occurrences; coverage is declared links/claims only, not automatic claim discovery')
    except AUDIT_ERRORS as error:
        report['errors'].append(str(error))
    report['unlinked'] = [item for item in report['pending'] if isinstance(item,dict) and 'claim_id' in item]
    report['checks'].append('Byte identity, numeric display/recomputation and source-defined semantic text are separate; no visual or scientific certification')
    report['passed'] = not report['errors'] and not report['pending']
    return report


def audit_render(data, root):
    """Hash actual render inputs/outputs and propagate stale versions through a DAG."""
    report = _report('render-dependencies')
    report.update(impacted_rebuild_targets=[], rebuild_order=[], commands_executed=False)
    root, artifacts, producers, changed = Path(root).resolve(), {}, {}, set()
    try:
        data = _object(data, 'render-dependencies payload')
        for spec in _list(data.get('artifacts'), 'artifacts', True):
            spec = _object(spec, 'render artifact')
            identity = _string(spec.get('id'), 'artifact id')
            if identity in artifacts:
                raise ValueError('Duplicate render artifact id: ' + identity)
            path = _path(root, spec.get('path'))
            if any(item['path'] == spec['path'] for item in artifacts.values()):
                raise ValueError('Same render path has multiple identities')
            digest = spec.get('sha256')
            if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
                raise ValueError('Invalid artifact digest: ' + identity)
            actual = _sha(path) if path.is_file() and path.stat().st_size else None
            artifacts[identity] = dict(spec, actual_sha256=actual)
            report['coverage']['bytes'].append({'id': identity, 'path': spec['path'],
                'expected_sha256': digest, 'actual_sha256': actual, 'matched': actual == digest})
            if actual != digest:
                changed.add(identity)
                report['errors'].append('Render artifact changed or missing: ' + identity + ' (' + spec['path'] + ')')
        for step in _list(data.get('renders'), 'renders', True):
            step = _object(step, 'render step')
            output = _string(step.get('output'), 'render output')
            if output not in artifacts or output in producers:
                raise ValueError('Unknown or duplicate render output: ' + output)
            inputs = _object(step.get('inputs'), 'render input digest map')
            if not inputs:
                raise ValueError('Render step needs actual input snapshots')
            renderer = _object(step.get('renderer'), 'renderer')
            _string(renderer.get('name'), 'renderer name')
            _string(renderer.get('version'), 'renderer version')
            for identity, digest in inputs.items():
                if identity not in artifacts or not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):
                    raise ValueError('Unknown input or invalid render input snapshot: ' + str(identity))
            output_digest=step.get('output_sha256', artifacts[output]['sha256'])
            if not isinstance(output_digest,str) or not re.fullmatch('[0-9a-f]{64}',output_digest):
                raise ValueError('Invalid render output snapshot: ' + output)
            producers[output] = step
        visited, active, ordered = set(), set(), []
        def visit(identity):
            if identity in active:
                raise ValueError('Render dependency cycle: ' + identity)
            if identity in visited:
                return
            active.add(identity)
            if identity in producers:
                for dependency in producers[identity]['inputs']:
                    visit(dependency)
                ordered.append(identity)
            active.remove(identity)
            visited.add(identity)
        for output in producers:
            visit(output)
        for output in ordered:
            stale_inputs = [identity for identity,digest in producers[output]['inputs'].items()
                            if identity in changed or artifacts[identity]['actual_sha256']!=digest]
            output_changed=artifacts[output]['actual_sha256']!=producers[output].get('output_sha256',artifacts[output]['sha256'])
            if output in changed or stale_inputs or output_changed:
                changed.add(output)
                report['impacted_rebuild_targets'].append({'id': output, 'path': artifacts[output]['path'],
                    'changed_inputs': stale_inputs, 'output_bytes_changed': output_changed})
                report['rebuild_order'].append(output)
                if stale_inputs:
                    report['errors'].append('Stale render: ' + output + '; changed dependency: ' + ','.join(stale_inputs))
                elif output_changed:
                    report['errors'].append('Render output differs from recorded build: ' + output)
        report['checks'].append('Actual input/output hashes and transitive render DAG; rebuild order is reported, no recorded command is executed')
    except AUDIT_ERRORS as error:
        report['errors'].append(str(error))
    report['passed'] = not report['errors']
    return report
