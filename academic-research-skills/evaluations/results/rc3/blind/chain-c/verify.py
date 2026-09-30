"""Read only the anonymous Chain C packet; write checks beside this script."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from decimal import Decimal as D
from datetime import datetime, timezone
import hashlib
import json
import re
import struct

PACKET = Path('LOCAL_EVIDENCE_ROOT/blind-packets/chain-c')
OUT = Path(__file__).resolve().parent
W = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
SVG = {'s': 'http://www.w3.org/2000/svg'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain_md(path):
    blocks = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('|'):
            cells = [x.strip() for x in line.strip('|').split('|')]
            if all(re.fullmatch(r':?-+:?', x) for x in cells):
                continue
            blocks.extend(x.replace('`', '') for x in cells)
        else:
            line = re.sub(r'^(?:#{1,6}\s+|>\s*)', '', line)
            blocks.append(line.replace('`', ''))
    return blocks


def docx_blocks(path):
    with ZipFile(path) as z:
        errors = z.testzip()
        assert errors is None, (path.name, errors)
        root = ET.fromstring(z.read('word/document.xml'))
        blocks = [''.join(t.text or '' for t in p.findall('.//w:t', W))
                  for p in root.findall('.//w:p', W)]
        xmls = {name: z.read(name).decode('utf-8') for name in z.namelist()
                if name.startswith(('word/', 'docProps/')) and name.endswith('.xml')}
        core = ET.fromstring(z.read('docProps/core.xml'))
        props = {e.tag.split('}')[-1]: e.text for e in core}
        return blocks, xmls, props


def intro(text):
    return re.search(r'## (?:1\. )?Introduction\n(.*?)\n## (?:2\. )?Methods', text, re.S)[1].strip()


def uses_x(root, gid):
    g = root.find(f'.//s:g[@id="{gid}"]', SVG)
    return [float(x.attrib['x']) for x in g.findall('.//s:use', SVG)]


def figure_check(sample, zero_id, one_id, ids, expected):
    root = ET.fromstring((PACKET/sample/'figure.svg').read_bytes())
    zero = uses_x(root, zero_id)[0]
    step = uses_x(root, one_id)[0] - zero
    points = [(uses_x(root, gid)[0] - zero) / step for gid in ids]
    path = root.find('.//s:g[@id="LineCollection_1"]/s:path', SVG).attrib['d']
    coords = [float(x) for x in re.findall(r'-?\d+(?:\.\d+)?', path)]
    interval = [(coords[i] - zero) / step for i in (0, 2)]
    for observed, value in zip(points, expected):
        assert abs(observed-value) < 1e-6, (sample, observed, value)
    assert all(abs(x-y) < 1e-6 for x,y in zip(interval, [-.6, .2]))
    assert len(root.findall('.//s:g[@id="LineCollection_1"]/s:path', SVG)) == 1
    data = (PACKET/sample/'figure.png').read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    return {'points_from_svg_coordinates': points,
            'target_interval_from_svg_coordinates': interval,
            'png_dimensions': list(struct.unpack('>II', data[16:24])),
            'svg_text': [''.join(x.itertext()) for x in root.findall('.//s:text', SVG)],
            'png_visual_inspection': 'Viewed by the reviewing agent through view_image in this review.'}


def main():
    files = sorted(p for scope in ['raw','S1','S2','S3'] for p in (PACKET/scope).rglob('*') if p.is_file())
    before = {str(p.relative_to(PACKET)): sha(p) for p in files}
    target = D('.8')*D('-1') + D('.2')*D('3')
    sampled = D('.5')*D('-1') + D('.5')*D('3')
    assert target == D('-.20') and sampled == D('1.00')
    assert target-sampled == D('-1.20')
    raw_intro = intro((PACKET/'raw/draft-v2.md').read_text())
    result = {'utc_check_observed_at': datetime.now(timezone.utc).isoformat(),
              'scope': 'raw and anonymous S1/S2/S3 only; no original run/source/mapping read',
              'arithmetic': {'target': str(target), 'sampled': str(sampled), 'difference': str(target-sampled),
                             'v1_to_current_change': str(target-D('-.30'))},
              'raw_intro_whitespace_words': len(raw_intro.split()), 'samples': {},
              'input_sha256_before': before}
    maps = {
        'S1': {'PACKAGE-NOTE.docx':'package-note.md','cover-letter-v3-draft.docx':'cover-letter.md',
               'declarations-v3-draft.docx':'declarations.md','figure-1-caption-v3.docx':'caption.md',
               'manuscript-v3-anonymous.docx':'manuscript.md','responses-v3-draft.docx':'responses.md',
               'supplement-s1-v3.docx':'supplement.md','title-page-v3.docx':'title-page.md',
               'version-correction-v1-to-v3-draft.docx':'correction-draft.md'},
        'S3': {'caption-v3.docx':'caption.md','correction-note-v1-draft.docx':'correction-draft.md',
               'cover-letter-draft.docx':'cover-letter.md','data-access-request-draft.docx':'data-access-request.md',
               'declarations-draft.docx':'declarations.md','manuscript-v3-anonymous.docx':'manuscript.md',
               'response-to-reviewers.docx':'responses.md','supplement-v3.docx':'supplement.md',
               'title-page-draft.docx':'title-page.md'}}
    geometry = {
        'S1': ('line2d_2','line2d_3',['line2d_10','line2d_11','line2d_12','line2d_13'],[-1,3,1,-.2]),
        'S2': ('line2d_2','line2d_3',['line2d_10','line2d_11','line2d_12','line2d_13'],[-1,3,-.2,1]),
        'S3': ('line2d_3','line2d_4',['line2d_11','line2d_12','line2d_13','line2d_14'],[-1,3,1,-.2])}
    for sample in ['S1','S2','S3']:
        p = PACKET/sample
        manuscript = (p/'manuscript.md').read_text()
        item = {'intro_whitespace_words': len(intro(manuscript).split()),
                'manuscript_all_whitespace_words': len(manuscript.split()),
                'v1_byte_identical': (p/'preserved-v1.md').read_bytes() == (PACKET/'raw/published-snapshot-v1.md').read_bytes(),
                'figure': figure_check(sample, *geometry[sample]),
                'native_copies_applicable': sample in maps, 'native_parity': []}
        assert item['v1_byte_identical']
        for anon in ['manuscript.md','caption.md','supplement.md','responses.md']:
            text = (p/anon).read_text()
            assert 'Mira Example' not in text and 'Synthetic Unit Laboratory' not in text
        actual_docs = {x.name for x in (p/'editable-copies').glob('*.docx')}
        assert actual_docs == set(maps.get(sample, {})), (sample, actual_docs)
        for doc, md in maps.get(sample, {}).items():
            blocks, xmls, props = docx_blocks(p/'editable-copies'/doc)
            expected = plain_md(p/md)
            equal = blocks == expected
            rec = {'docx': doc, 'markdown': md, 'paragraph_and_cell_text_equal': equal,
                   'native_blocks': len(blocks), 'markdown_blocks': len(expected), 'core_properties': props}
            if not equal:
                rec['mismatches'] = [{'index': i+1, 'native': x, 'markdown': y} for i,(x,y) in enumerate(zip(blocks, expected)) if x != y]
            if md in ['manuscript.md','caption.md','supplement.md','responses.md']:
                all_xml = ''.join(xmls.values())
                rec['identity_absent_from_word_and_properties_xml'] = 'Mira Example' not in all_xml and 'Synthetic Unit Laboratory' not in all_xml
                assert rec['identity_absent_from_word_and_properties_xml']
            item['native_parity'].append(rec)
        result['samples'][sample] = item
    after = {str(p.relative_to(PACKET)): sha(p) for p in files}
    assert before == after, 'Packet changed while checking.'
    result['input_hashes_unchanged_during_check'] = True
    result['native_parity_all_equal'] = all(r['paragraph_and_cell_text_equal'] for s in result['samples'].values() for r in s['native_parity'])
    assert result['native_parity_all_equal']
    (OUT/'checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'arithmetic': result['arithmetic'], 'raw_intro_words': len(raw_intro.split()),
                      'samples': {s: {'intro_words': x['intro_whitespace_words'], 'all_manuscript_words': x['manuscript_all_whitespace_words'],
                                      'v1_equal': x['v1_byte_identical'], 'docx_checked': len(x['native_parity']),
                                      'docx_parity': all(r['paragraph_and_cell_text_equal'] for r in x['native_parity']) if x['native_parity'] else None,
                                      'mismatches': [r for r in x['native_parity'] if not r['paragraph_and_cell_text_equal']]}
                                  for s,x in result['samples'].items()},
                      'hashes_unchanged': result['input_hashes_unchanged_during_check']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
