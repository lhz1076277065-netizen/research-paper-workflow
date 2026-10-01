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
             'time', 'comparison', 'model', 'implementation', 'split', 'uncertainty', 'effect_type')
IDENTITY = ('outcome', 'population', 'comparison', 'split', 'time', 'effect_type')
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
        from pypdf.errors import PyPdfError
    except ImportError:
        raise ValueError('PDF extraction needs installed pdftotext or pypdf; no PDF occurrence was checked') from None
    try:
        return [page.extract_text() or '' for page in PdfReader(str(path)).pages]
    except PyPdfError as error:
        raise ValueError('PDF text extraction failed: ' + path.name + ': ' + str(error)) from error


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


def _direction(value):
    return next((key for key, words in DIRECTIONS.items() if _normal(value) in words), _normal(value))


def _recomputed(record, other, field, other_field, pending, location):
    """Compare a declared scientific identity before comparing converted raw values."""
    if other.get('type', 'numeric') != 'numeric':
        raise ValueError('Recomputed result must be numeric')
    if field != other_field and {field, other_field} != {'value', 'estimate'}:
        raise ValueError('Recomputed numeric field role differs')
    original, repeated = _semantic_source(record), _semantic_source(other)
    if 'unit' not in original or 'unit' not in repeated:
        raise ValueError('Recomputed result must declare its unit')
    source_unit = _unit(_value_and_labels(original['unit'])[0])
    other_unit = _unit(_value_and_labels(repeated['unit'])[0])
    if source_unit[0] != other_unit[0]:
        raise ValueError('Recomputed unit dimensions differ')
    checked = []
    for name in sorted((set(original) | set(repeated)) - {'unit'}):
        if name not in original or name not in repeated:
            raise ValueError('Recomputed semantic identity missing: ' + name)
        value = _value_and_labels(original[name])[0]
        actual = _value_and_labels(repeated[name])[0]
        equal = (_number(value, name) == _number(actual, name)) if name == 'denominator' else (
            _direction(value) == _direction(actual) if name == 'direction' else _normal(value) == _normal(actual))
        if not equal and name in {'model', 'implementation'} and isinstance(original[name], dict):
            aliases = _list(original[name].get('equivalent_values', []), 'frozen equivalent_values')
            equal = _normal(actual) in {_normal(_string(alias, 'equivalent value')) for alias in aliases}
        if not equal:
            raise ValueError('Recomputed semantic identity mismatch: ' + name)
        checked.append(name)
    missing = sorted(set(IDENTITY) - set(original))
    if missing:
        pending.append(dict(location, reason='recomputation_identity_unbound', fields=missing,
                            action='Bind applicable scientific identity in both frozen results, including explicit not-applicable values'))
    value = _number(other.get(other_field), 'recomputed value') * other_unit[1] / source_unit[1]
    return value, sorted(checked), str(other_unit[1] / source_unit[1])


def _negated(token, scoped):
    for match in re.finditer(re.escape(_normal(token)), _normal(scoped)):
        prefix = _normal(scoped)[:match.start()]
        if re.search(r"(?:\b(?:not|never|no|without)\b|n't)\s+(?:(?:a|an|the|significantly|statistically|necessarily|actually|clearly)\s+){0,3}$", prefix):
            raise ValueError('Negated actual occurrence: ' + str(token))


def _unresolved_negation(scoped, tokens):
    remainder=_normal(scoped)
    for token in tokens:
        token=_normal(token)
        if re.search(r'\b(?:not|no|without)\b',token):remainder=remainder.replace(token,'')
    remainder=re.sub(r'\bno missing (?:data|values|observations)\b','',remainder)
    return re.search(r"\b(?:not|never|no|without|neither|nor|cannot)\b|\b\w+n['’]t\b|不是|并非|未",remainder) is not None


def _semantics(record, link, text, path, cache, coverage, pending):
    expected = _semantic_source(record)
    mapped = _object(link.get('semantics', {}), 'link semantics')
    if set(mapped) - set(expected):
        raise ValueError('Semantic mapping lacks source meaning: ' + ','.join(sorted(set(mapped) - set(expected))))
    # A caption can cover a point value while another occurrence covers its design.
    for field, mapping in mapped.items():
        original = expected[field]
        value, labels = _value_and_labels(original)
        mapping = _object(mapping, field + ' mapping')
        token = _string(mapping.get('text'), field + ' text')
        actual = mapping.get('value')
        scoped = _located(path, mapping['locator'], cache) if 'locator' in mapping else text
        if not _present(scoped, token):
            raise ValueError(field + ' text not found at actual locator: ' + token)
        _negated(token,scoped)
        if 'locator' in mapping and _unresolved_negation(scoped,[token]):
            pending.append({'result_id':link['result_id'],'role':link['role'],'path':link['artifact']['path'],
                'locator':mapping['locator'],'field':field,'reason':'semantic_negation_scope_unresolved',
                'action':'Read the actual semantic scope and resolve its negation'})
        if field == 'unit':
            label_match = _normal(actual)==_normal(value) and _normal(token) in {_normal(s) for s in labels}
            if _unit(value)[0] != _unit(actual)[0] or (_unit(actual) != _unit(token) and not label_match):
                raise ValueError('Unit mismatch or undeclared conversion')
        elif field == 'direction':
            if _direction(value) != _direction(actual) or _direction(token) != _direction(value):
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


def _numeric(record, link, text, expected, mapped, sources, coverage, pending):
    numbers = _list(link.get('numeric', []), 'numeric mappings', True)
    if record.get('lower') not in (None, '') and record.get('upper') not in (None, ''):
        lower, upper = _number(record['lower'], 'lower bound'), _number(record['upper'], 'upper bound')
        estimate = record.get('value', record.get('estimate'))
        if lower > upper or (estimate is not None and not lower <= _number(estimate, 'estimate') <= upper):
            raise ValueError('Source uncertainty interval is inconsistent')
    fields, positions = set(), {}
    location = {'result_id': link['result_id'], 'role': link['role'], 'path': link['artifact']['path'], 'locator': link['locator']}
    for mapping in numbers:
        mapping = _object(mapping, 'numeric mapping')
        field = _string(mapping.get('field'), 'numeric field')
        if field in fields:
            raise ValueError('Duplicate numeric field mapping: ' + field)
        fields.add(field)
        raw = _number(record.get(field), 'source ' + field)
        token = _string(mapping.get('text'), 'numeric text')
        displayed = _number(token, 'displayed number')
        # A compact range separator is not the sign of its upper endpoint; preserve offsets.
        numeric_text = re.sub(r'(?<=[\d%])[-–—](?=\d)', ' ', text.replace('−', '-'))
        unit_text = mapped.get('unit', {}).get('text')
        if unit_text:
            pattern = r'(?<![\w.])[+-]?\d+(?:\.\d+)?\s*' + re.escape(unit_text) + r'([-–—])(?=\d)'
            for separator in re.finditer(pattern, numeric_text):
                start, end = separator.span(1)
                numeric_text = numeric_text[:start] + ' ' + numeric_text[end:]
        matches = list(re.finditer(r'(?<![\w.+-])' + re.escape(token) + r'(?![\w.])', numeric_text))
        offset = mapping.get('offset')
        if offset is not None:
            if type(offset) is not int or offset < 0 or not any(m.start() == offset for m in matches):
                raise ValueError('Numeric offset does not locate the actual token')
        elif len(matches) != 1:
            raise ValueError('Numeric token absent or ambiguous at locator: ' + token)
        positions[field] = next(m.span() for m in matches if offset is None or m.start()==offset)
        factor = Decimal(1)
        if 'unit' not in expected:
            raise ValueError('Numeric source must declare unit, including dimensionless')
        source_unit = _value_and_labels(expected['unit'])[0]
        target_unit = mapped.get('unit', {}).get('value', source_unit)
        factor = _unit(source_unit)[1] / _unit(target_unit)[1]
        unit_map = mapped.get('unit')
        if unit_map is None:
            pending.append(dict(location,reason='occurrence_unit_unbound',action='Bind the displayed unit at this occurrence or its actual table header'))
        elif 'locator' not in unit_map:
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
        if set(tolerance)-{'abs','rel'}:
            raise ValueError('Unknown numeric tolerance field')
        absolute = _number(tolerance.get('abs', 0), 'absolute tolerance')
        relative = _number(tolerance.get('rel', 0), 'relative tolerance')
        if absolute < 0 or relative < 0:
            raise ValueError('Numeric tolerances must be nonnegative')
        recomputed = mapping.get('recomputed')
        if tolerance and recomputed is None:
            raise ValueError('Tolerance belongs to a hash-bound recomputation, not manuscript display')
        recomputation = None
        if recomputed is not None:
            recomputed = _object(recomputed, 'recomputed reference')
            source = sources.get(recomputed.get('source_id'))
            if source is None:
                raise ValueError('Unknown recomputation source_id')
            other = source['records'].get(recomputed.get('result_id', link['result_id']))
            if other is None:
                raise ValueError('Unknown recomputed result_id')
            value, identity, converted = _recomputed(record, other, field, recomputed.get('field', field), pending, location)
            if abs(raw - value) > max(absolute, relative * max(abs(raw), abs(value))):
                raise ValueError('Recomputed numeric value exceeds tolerance: ' + field)
            recomputation = {'identity_fields': identity, 'unit_factor_to_source': converted,
                             'converted_value': str(value), 'absolute_tolerance_unit': str(source_unit)}
        coverage.append({'result_id': link['result_id'], 'role': link['role'], 'path': link['artifact']['path'],
                         'locator': link['locator'], 'field': field, 'source_value': str(raw),
                         'display_text': token, 'unit_factor': str(factor), 'decimals': decimals,
                         'rounding': rounding, 'recomputation_checked': recomputed is not None,
                         'recomputation': recomputation})
    return positions


def _relations(record, link, text, positions, sources, report):
    """Check local literal relationships, leaving unsupported language for review."""
    # ponytail: scoped literal/English grammar only; complex phrasing goes to located review.
    normal = _normal(text)
    location = {'result_id': link['result_id'], 'role': link['role'],
                'path': link['artifact']['path'], 'locator': link['locator']}
    spans = {}
    for mapping in link['numeric']:
        first, last = positions[mapping['field']]
        start = len(_normal(text[:first])) + (1 if first and text[first-1].isspace() else 0)
        spans[mapping['field']] = (start, start + len(_normal(mapping['text'])))
    boundaries = [0] + [m.end() for m in re.finditer(r'[.!?](?=\s|$)', normal)] + [len(normal)]
    def statement(span):
        return next((a,b) for a,b in zip(boundaries,boundaries[1:]) if a<=span[0]<b)
    def pending(reason, **details):
        report['pending'].append(dict(location,reason=reason,action='Read the actual located statement and bind this relationship',**details))
    for field,span in spans.items():
        a,b = statement(span)
        _negated(normal[span[0]:span[1]], normal[a:b])
    for field,mapping in link.get('semantics',{}).items():
        if 'locator' not in mapping:
            _negated(mapping['text'], normal)
    if {'lower','upper'}.issubset(spans):
        low, high = spans['lower'], spans['upper']
        labels = {'lower':r'(?:lower|lower bound|下限)\s*[:=]?\s*$',
                  'upper':r'(?:upper|upper bound|上限)\s*[:=]?\s*$'}
        explicit = all(re.search(labels[name],normal[max(0,spans[name][0]-35):spans[name][0]]) for name in labels)
        if high[0]<low[0] and not explicit:
            raise ValueError('Actual uncertainty endpoints are reversed')
        if not explicit:
            if statement(low)!=statement(high):
                pending('interval_relationship_unresolved')
            else:
                bridge=normal[low[1]:high[0]]
                unit=link.get('semantics',{}).get('unit',{}).get('text','')
                bridge=bridge.replace(_normal(unit),'') if unit else bridge
                bridge=re.sub(r'\b(?:to|through|and)\b|[\s,;:()[\]{}%–—-]','',bridge)
                if bridge:
                    pending('interval_relationship_unresolved')
                else:
                    report['coverage']['relationships'].append(dict(location,relationship='interval_order',status='checked'))
        else:
            report['coverage']['relationships'].append(dict(location,relationship='explicit_endpoint_labels',status='checked'))
    primary = next((name for name in ('value','estimate') if name in spans),None)
    if primary is None:
        return
    a,b = statement(spans[primary]);sentence=normal[a:b]
    mapped=link.get('semantics',{})
    subject=link.get('subject_field',next((name for name in ('model','implementation','outcome') if name in mapped),None))
    if subject not in {'model','implementation','outcome','population'}:
        if subject is not None:
            raise ValueError('Unknown subject_field')
        pending('primary_subject_unbound')
    elif subject not in mapped:
        pending('primary_subject_relationship_unresolved',field=subject)
    elif 'locator' in mapped[subject]:
        value_locator,subject_locator=link['locator'],mapped[subject]['locator']
        same_table=value_locator.get('table') is not None and value_locator.get('table')==subject_locator.get('table')
        same_row=same_table and value_locator.get('row')==subject_locator.get('row') and subject_locator.get('cell')==value_locator.get('cell',0)-1
        header=same_table and value_locator.get('cell')==subject_locator.get('cell') and subject_locator.get('row')==1 and value_locator.get('row',0)>1
        if (subject in {'model','implementation','population'} and same_row) or (subject=='outcome' and header):
            report['coverage']['relationships'].append(dict(location,relationship='table_subject_coordinates',field=subject,status='checked'))
        else:
            pending('primary_subject_relationship_unresolved',field=subject)
    else:
        expected=_value_and_labels(_semantic_source(record)[subject])[0]
        candidates=[]
        for source in sources.values():
            for row in source['records'].values():
                source_semantics=_semantic_source(row)
                if subject not in source_semantics:continue
                value,labels=_value_and_labels(source_semantics[subject])
                for label in labels:
                    for match in re.finditer(r'(?<!\w)'+re.escape(_normal(label))+r'(?!\w)',sentence):
                        candidates.append((match.start()+a,match.end()+a,value))
        before=[item for item in candidates if item[1]<=spans[primary][0]]
        selected=max(before,key=lambda item:item[1]) if before else None
        if selected is None:
            after=[item for item in candidates if item[0]>=spans[primary][1]
                   and re.search(r'\b(?:using|for|from|by|of)\s*$',normal[a:item[0]])]
            selected=min(after,key=lambda item:item[0]) if after else None
        if selected is None:
            pending('primary_subject_relationship_unresolved',field=subject)
        elif _normal(selected[2])!=_normal(expected):
            raise ValueError('Primary value belongs to a different ' + subject)
        else:
            first,last=(selected[1],spans[primary][0]) if selected[1]<=spans[primary][0] else (spans[primary][1],selected[0])
            bridge=normal[first:last]
            for name,span in spans.items():
                if name!=primary:
                    bridge=bridge.replace(normal[span[0]:span[1]],'')
            for mapping in sorted(mapped.values(),key=lambda item:len(_normal(item['text'])),reverse=True):
                bridge=bridge.replace(_normal(mapping['text']),'')
            if re.search(r'(?<![\w.])\d+(?:\.\d+)?(?![\w.])',bridge):
                pending('primary_subject_relationship_ambiguous',field=subject)
            else:
                residue=re.sub(r'\b(?:is|was|were|equals|equal|mean|estimate|estimated|of|has|had|at|to|for|using|in|on|versus|against|with|the|a|an|than|from|by|and|ci|n|bound|bounds|confidence|interval|increased|decreased|higher|lower)\b|[\s=,:;()[\]{}%–—-]','',bridge)
                if residue:
                    pending('primary_subject_connector_unresolved',field=subject,text=normal[first:last])
                else:
                    report['coverage']['relationships'].append(dict(location,relationship='primary_subject',field=subject,status='checked'))
    # Source-defined negative metadata (e.g. "not supplied") is not a negated result.
    if _unresolved_negation(sentence,[mapping['text'] for mapping in mapped.values()]):
        pending('negation_scope_unresolved',text=sentence)


def build_links(root, sources, occurrences, claims=()):
    """Reuse manuscript build rows; do not discover claims or write another ledger.

    Example after a real build (paths and locators come from that build):
      rows = [{"path":"draft.md", "locator":{"line":1}, "result_id":"R1",
               "role":"body", "unit":"percent",
               "numeric":[{"field":"value", "decimals":2}]}]
      payload = build_links(root, [{"id":"analysis", "path":"results.json",
          "versions":{"data":{"path":"data.csv"}, "code":{"path":"run.py"},
                      "execution":{"path":"execution.json"}}}], rows)
      report = audit_links(payload, root)

    Frozen sources define meaning. Only labels found at each actual locator are
    linked; absent fields and uncertain relationships stay in report.pending,
    coverage_gaps and coverage.occurrences. This does not certify claim truth.
    An existing sha256 is checked, never silently refreshed to hide source drift.
    """
    root=Path(root).resolve();cache={};records={};output=[]
    def artifact(spec):
        spec=dict(_object(spec,'build artifact'))
        path=_path(root,spec.get('path'))
        spec.setdefault('sha256',_sha(path))
        _artifact(spec,root,[])
        return spec
    for source in _list(sources,'sources',True):
        source=artifact(source);sid=_string(source.get('id'),'source id')
        if sid in records:raise ValueError('Duplicate source id: '+sid)
        source['versions']={name:artifact(spec) for name,spec in _object(source.get('versions',{}),'source versions').items()}
        records[sid]=_records(_path(root,source['path']));output.append(source)
    links=[]
    for row in _list(occurrences,'build occurrences',True):
        row=_object(row,'build occurrence');sid=row.get('source_id',next(iter(records)) if len(records)==1 else None)
        rid=_string(row.get('result_id'),'result_id')
        if sid not in records or rid not in records[sid]:raise ValueError('Unknown build source_id/result_id')
        original=records[sid][rid];source_semantics=_semantic_source(original)
        target=artifact(row.get('artifact',{'path':row.get('path')}))
        text=_located(_path(root,target['path']),row.get('locator'),cache)
        link={name:row[name] for name in ('claim_id','subject_field','bindings') if name in row}
        link.update(result_id=rid,source_id=sid,role=_string(row.get('role'),'role'),artifact=target,locator=row['locator'])
        mapped={}
        target_unit=row.get('unit',_value_and_labels(source_semantics['unit'])[0] if 'unit' in source_semantics else None)
        for field,expected in source_semantics.items():
            value,labels=_value_and_labels(expected)
            if field=='unit':
                value=target_unit
                labels=[label for label in UNITS if _unit(label)==_unit(target_unit)]+(labels if _normal(value)==_normal(_value_and_labels(expected)[0]) else [])
            elif field=='direction':
                labels=DIRECTIONS.get(_direction(value),labels)
            elif field=='denominator':
                n=str(_number(value,'denominator'))
                found=re.search(r'\b[nN]\s*=\s*'+re.escape(n)+r'(?![\w.])',text)
                labels=[found.group()] if found else []
            token=next((label for label in sorted(labels,key=len,reverse=True) if _present(text,label)),None)
            if token is not None:mapped[field]={'value':value,'text':token}
        mapped.update(_object(row.get('semantics',{}),'build semantic overrides'))
        link['semantics']=mapped
        if original.get('type','numeric')=='numeric':
            numeric=[]
            for item in _list(row.get('numeric',[{'field':row.get('field','value'),**({'decimals':row['decimals']} if 'decimals' in row else {})}]),'build numeric fields',True):
                item=dict(_object(item,'build numeric field'));field=_string(item.get('field'),'numeric field')
                value=_number(original.get(field),'source '+field)
                unit=_value_and_labels(source_semantics.get('unit'))[0]
                if _unit(unit)[0]!=_unit(target_unit)[0]:raise ValueError('Build unit dimensions differ')
                value=value*_unit(unit)[1]/_unit(target_unit)[1]
                decimals=item.get('decimals');rounding=item.get('rounding','half-even')
                if rounding not in {'half-even','half-up'}:raise ValueError('Unknown build rounding')
                if decimals is not None:
                    if type(decimals)is not int or not 0<=decimals<=12:raise ValueError('Invalid build decimals')
                    value=value.quantize(Decimal(1).scaleb(-decimals),rounding=ROUND_HALF_EVEN if rounding=='half-even' else ROUND_HALF_UP)
                if value.is_zero():value=abs(value)
                item.setdefault('text',format(value,'.'+str(decimals)+'f') if decimals is not None else format(value,'f'))
                numeric.append(item)
            link['numeric']=numeric
        links.append(link)
    return {'kind':'result-links','sources':output,'links':links,'claims':list(claims)}


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
            'coverage': {'bytes': [], 'numeric': [], 'declared_semantic': [], 'relationships': [], 'occurrences': []},
            'coverage_gaps': [],
            'scientific_validity_certified': False, 'semantic_truth_certified': False,
            'actual_visual_inspection_performed': False}


AUDIT_ERRORS = (OSError, ValueError, TypeError, KeyError, IndexError, InvalidOperation,
                zipfile.BadZipFile, ET.ParseError, subprocess.SubprocessError)


def audit_links(data, root):
    """Audit actual occurrences; invalid mappings return diagnostics, never execute."""
    report = _report('result-links')
    root = Path(root).resolve()
    sources, cache, checked_versions, successful, manuscript = {}, {}, set(), [], {}
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
                expected, mapped = _semantics(record, link, text, path, cache, report['coverage']['declared_semantic'],report['pending'])
                kind = record.get('type', 'numeric')
                if kind == 'numeric':
                    positions = _numeric(record, link, text, expected, mapped, sources, report['coverage']['numeric'], report['pending'])
                    _relations(record, link, text, positions, sources, report)
                    required=set(expected)|{field for field in ('value','estimate','lower','upper') if record.get(field) not in (None,'')}
                    covered=set(mapped)|set(positions)
                    key=(sid,rid,link['artifact']['path'])
                    group=manuscript.setdefault(key,{'expected':required,'covered':set(),'roles':set()})
                    group['covered'].update(covered);group['roles'].add(link['role'])
                    report['coverage']['occurrences'].append({'result_id':rid,'source_id':sid,'role':link['role'],
                        'path':link['artifact']['path'],'locator':link['locator'],'covered_fields':sorted(covered),
                        'fields_not_in_this_occurrence':sorted(required-covered)})
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
        for (sid,rid,path),group in manuscript.items():
            missing=sorted(group['expected']-group['covered'])
            if missing:
                gap={'source_id':sid,'result_id':rid,'path':path,'roles':sorted(group['roles']),
                     'reason':'manuscript_fields_uncovered','fields':missing,
                     'action':'Link these applicable fields elsewhere in this manuscript or record a located semantic review'}
                report['coverage_gaps'].append(gap);report['pending'].append(gap)
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
    report['checks'].append('Occurrence roles and manuscript field coverage are separate; literal relationships beyond automatic scope remain located pending')
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
