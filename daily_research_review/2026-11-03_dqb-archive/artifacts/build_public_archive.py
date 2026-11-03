"""Build the reviewed public edition of the 2026-11-03 DQB.

The five-page private original and fonts are caller-supplied. This performs
true redactions and verified scientific corrections, not archive registration
or publication. Rebuilding resets visual review to pending.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
from xml.sax.saxutils import escape

import fitz
from PIL import Image, ImageChops, ImageDraw
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = 'ca114eb8687003275cfdeb9aaa25f6381afc43377fe42df5f0de0bf0d4c8978d'
REMOVALS = {0: [(61, 509, 546, 543)], 4: [(61, 389, 546, 521)]}
# Prefixes identify scientific text only. Each replacement must match once.
REPLACEMENTS = [
 (0, 'D-Wave-FAU 폐암 QML [6]', 'D-Wave-FAU 폐암 QML [6,7]'),
 (0, '평가 저널]', '[산업 발표+동료평가 저널]'),
 (4, '[산업/제품·후속 발표]', '[산업/제품·후속 발표] D-Wave 공식 발표 2026-11-02 · 원 논문 version of record 2026-09-09 [6,7]'),
 (1, '저자는 finite sampling이', '실제 시간순 실행에서는 hardware feature의 이득이 관측되지 않았다. Outcome-sorted replay의 이득은 job-purged split에서'),
 (1, 'fidelity-kernel 계산은', '사라졌다. QPU 호출 수, shots, queue, calibration drift와 feature caching 비용은 accuracy와 함께 살펴야 한다.'),
 (1, 'caching이 모두 숨는다.', ''),
 (0, 'IBM Heron 129큐비트에서', 'IBM Heron 129큐비트의 공개 파생 과제에서 null circuit의 job fingerprint는 outcome 순서로 재배치된 자료의 예측 신호처럼'),
 (0, '낼 수 있음을 보였다.', '보일 수 있었다. 무작위 job 배정과 실제 시간순 pipeline에서는 hardware feature의 이득이 관측되지 않았고, outcome-sorted'),
 (0, 'feature는 shot noise', 'replay의 이득은 job-purged backtest에서 사라졌다. 원래의 비공개 채권 자료를 직접 재현하지 않은 공개 파생 과제의 결과이며,'),
 (0, 'leakage를 검출하는', 'job 배정·검증 분할이 만드는 leakage를 검출하는 audit protocol을 제시한다.'),
 (1, 'analog task를 만들었다.', 'analog task를 만들었다. 129개 IBM Heron qubit chain에서 측정 feature를 수집한 뒤, 같은 hardware job 안의 records가 공유하는'),
 (1, 'Natural/replayed order', 'Chronological / replay'),
 (1, 'outcome-ordered batch와', '시간순 실제 실행과 outcome-sorted replay 구별'),
 (4, 'QPU execution 0.5-6 s', 'QPU execution time'),
 (4, '논문은 hardware QSVM이', 'Fig.9 고전 기준선과의 비교에서 91.90%가 가장 낮음'),
 (3, 'Real-time BP decoding for', 'Real-time BP decoding of a high-rate QEC code'),
 (3, 'IBM ibm_miami Nighthawk', 'IBM ibm_miami Nighthawk R1의 4x4 배열에서 flux 1/2 Kapit-Mueller model의 target state를 준비했다. 4-boson ground'),
 (3, 'quasihole state의 classically', 'state와 3-boson+2 quasihole state의 exact target을 고전적으로 구하고, classically optimized shallow circuit을 QPU에 실행했다.'),
 (3, 'fidelity는 0.95였다.', 'Noiseless target fidelity는 0.95였다.'),
 (3, '[[512,174,8]] 3D product', '[[512,174,8]] 3D product qLDPC용 row-wise serial min-sum decoder를 FPGA에 배치했다. 단일 core의 정확도는 BP+OSD-CS10에,'),
 (3, 'core ensemble은 Relay-BP에', '모사상 세 core ensemble은 Relay-BP에 맞췄다. p=10⁻³에서 논리큐비트·round당 오류율 약 5×10⁻⁷·effective distance 6이다.'),
 (3, 'latency는 실제 FPGA에서', 'FPGA core 지연은 실제 측정했으며, 입력 syndrome은 모사로 생성했다. 별도 Windows 1-Gb Ethernet 인터페이스는 34 us,'),
 (3, 'neutral-atom·trapped-ion 제어', '합성 맥락의 on-chip power는 14.2 W로 보고했다. 5.1/97.9 us는 host 통신을 제외한 core 지연이다. live QPU feedback과'),
 (3, 'superconducting용 ASIC 지연은', '전체 제어 루프, superconducting용 ASIC 지연은 검증되지 않았다.')]

def restore(text):
    return text


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bitmap(page):
    p = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes('RGB', (p.width, p.height), p.samples)


def source_lines(page):
    rows = []
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            spans = line['spans']
            rows.append({'text': ''.join(s['text'] for s in spans),
                         'bbox': line['bbox'], 'origin': spans[0]['origin'],
                         'size': spans[0]['size'], 'color': spans[0]['color']})
    return rows


def runs(text, regular, reference):
    out = []
    for ch in text:
        face = 'DqbRegular' if regular.has_glyph(ord(ch)) else 'DqbReference'
        font = regular if face == 'DqbRegular' else reference
        if not font.has_glyph(ord(ch)):
            raise ValueError(f'Unsupported public glyph: {ch!r}')
        if out and out[-1][0] == face:
            out[-1] = (face, out[-1][1] + ch)
        else:
            out.append((face, ch))
    return out


def reference_list():
    rows = json.loads((ROOT / 'reports/reference-manifest.json').read_text())['references']
    if [r['number'] for r in rows] != list(range(1, 8)):
        raise ValueError('Keep original scientific first-use order [1]-[7]')
    if any(not r['citation'] or not r['url'].startswith('https://') for r in rows):
        raise ValueError('Incomplete citation or source URI')
    return rows


def normalize_to_unicode(doc):
    """Encode non-BMP CMap destinations as proper UTF-16BE surrogate pairs.

    Some font inserters emit five-digit scalar values in unused CMap entries.
    Correcting these mappings preserves page pixels and strict-reader parsing.
    """
    changed = 0
    seen = set()
    for xref in range(1, doc.xref_length()):
        kind, value = doc.xref_get_key(xref, 'ToUnicode')
        if kind != 'xref':
            continue
        cmap_xref = int(value.split()[0])
        if cmap_xref in seen:
            continue
        seen.add(cmap_xref)
        before = doc.xref_stream(cmap_xref)
        def utf16(match):
            codepoint = int(match.group(1), 16)
            return b'<' + chr(codepoint).encode('utf-16-be').hex().encode('ascii') + b'>'
        after, count = re.subn(rb'<([0-9A-Fa-f]{5,6})>', utf16, before)
        if count:
            doc.update_stream(cmap_xref, after)
            changed += count
    return changed


def appendix(regular, bold, reference_font, manifest):
    for name, path in [('DqbRegular', regular), ('DqbBold', bold), ('DqbReference', reference_font)]:
        pdfmetrics.registerFont(TTFont(name, str(path)))
    out = io.BytesIO()
    c = Canvas(out, pagesize=A4, invariant=1)
    w, h = A4
    y = h - 43

    def mixed(text):
        face = pdfmetrics.getFont('DqbRegular').face
        return ''.join(escape(ch) if ord(ch) in face.charToGlyph else
                       f'<font name="DqbReference">{escape(ch)}</font>' for ch in text)

    def para(text, size=9.5, leading=13.7, strong=False, after=5, color='#263a47', ref=False, links=None):
        nonlocal y
        style = ParagraphStyle('p', fontName='DqbReference' if ref else ('DqbBold' if strong else 'DqbRegular'),
                               fontSize=size, leading=leading, textColor=HexColor(color), wordWrap='CJK')
        rendered = text if ref else mixed(text)
        for link in links or []:
            label = mixed(link['text'])
            if rendered.count(label) != 1 or not link['url'].startswith('https://'):
                raise ValueError('Ambiguous source-link label or non-public URI')
            rendered = rendered.replace(label, f'<link href="{escape(link["url"])}" color="#007e8c">{label}</link>')
        p = Paragraph(rendered, style)
        _, height = p.wrap(w - 110, h)
        y -= height
        p.drawOn(c, 55, y)
        y -= after

    para('DAILY QUANTUM BRIEF / 2026-11-03', 9, 12, after=7, color='#007e8c')
    para('공개 보관본 편집·서지 보완', 18, 24, True, after=6)
    para('원 DQB 5쪽 + 정정 기록·참고문헌 1쪽', 8.6, 12, color='#60717d', after=8)
    para('편집 기록과 결과를 읽는 조건', 10.5, 14, True, color='#007e8c')
    for index, note in enumerate(manifest['edition_notes']):
        para(note, links=manifest.get('edition_note_links', {}).get(str(index), []))
    para('참고문헌', 10.5, 14, True, color='#007e8c')
    for row in manifest['references']:
        citation = escape(row['citation'])
        locator = escape(row['locator'])
        if citation.count(locator) != 1:
            raise ValueError('Expected one exact source locator per APS entry')
        citation = citation.replace(locator, f'<link href="{escape(row["url"])}" color="#263a47">{locator}</link>')
        para(f'[{row["number"]}] {citation}', 9.1, 12.7, after=5, ref=True)
    para(manifest['production_disclosure'], 8.0, 11.1, color='#60717d', after=0)
    if y < 57:
        raise ValueError(f'Appendix overflow: bottom={y}')
    c.setStrokeColor(HexColor('#cadadd'))
    c.line(55, 40, w - 55, 40)
    c.setFont('DqbRegular', 7.5)
    c.setFillColor(HexColor('#60717d'))
    c.drawString(55, 27, 'AI TECH REVIEW / PUBLIC EDITION')
    c.drawRightString(w - 55, 27, '6')
    c.showPage()
    c.save()
    return out.getvalue(), y


def line_right(index, line):
    return 542


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for flag in ('source-pdf', 'font-regular', 'font-bold', 'font-reference', 'qa-dir'):
        p.add_argument('--' + flag, required=True, type=Path)
    args = p.parse_args()
    # Invalidate prior review before any attempted rebuild, including failures.
    entry_path = ROOT / 'reports/archive-entry.json'
    entry = json.loads(entry_path.read_text())
    entry['public_reviewed'] = False
    entry_path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + '\n')
    qa_path = ROOT / 'notes/production-qa.json'
    if qa_path.exists():
        prior = json.loads(qa_path.read_text())
        prior['visual_qa'] = {'status': 'pending_rebuild'}
        prior['independent_review'] = {'status': 'pending_rebuild'}
        qa_path.write_text(json.dumps(prior, ensure_ascii=False, indent=2) + '\n')
    repository = ROOT.parents[1].resolve()
    for path in (args.source_pdf, args.qa_dir):
        if path.resolve().is_relative_to(repository):
            raise ValueError('Private source and QA must remain outside the public repository')
    raw = args.source_pdf.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise ValueError('Input is not the reviewed original')
    original = fitz.open(stream=raw, filetype='pdf')
    public = fitz.open(stream=raw, filetype='pdf')
    if len(original) != 5:
        raise ValueError('Expected five source pages')
    font = fitz.Font(fontfile=str(args.font_regular))
    fallback = fitz.Font(fontfile=str(args.font_reference))
    fonts = {'DqbRegular': font, 'DqbReference': fallback}
    edits = {i: list(rects) for i, rects in REMOVALS.items()}
    pending = []
    replaced = set()
    for index, page in enumerate(original):
        for line in source_lines(page):
            if any(fitz.Rect(r).contains(fitz.Rect(line['bbox'])) for r in REMOVALS.get(index, [])):
                continue
            text = restore(line['text'])
            for n, (target, prefix, new) in enumerate(REPLACEMENTS):
                if target == index and line['text'].startswith(prefix):
                    if n in replaced:
                        raise ValueError('Ambiguous replacement prefix')
                    replaced.add(n)
                    text = new
            if text == line['text']:
                continue
            x, y = line['origin']
            rr = runs(text, font, fallback)
            width = sum(fonts[face].text_length(value, fontsize=line['size']) for face, value in rr)
            right = line_right(index, line)
            if x + width > right:
                raise ValueError(f'Page {index+1} line at {y}: right {x+width:.2f} exceeds {right}: {text}')
            rect = (line['bbox'][0] - .6, min(line['bbox'][1] - .6, y - line['size'] * 1.05),
                    max(line['bbox'][2], x + width) + .7,
                    max(line['bbox'][3] + .6, y + line['size'] * .30))
            edits.setdefault(index, []).append(rect)
            pending.append((index, line, rr))
    if replaced != set(range(len(REPLACEMENTS))):
        raise ValueError(f'Missing replacement prefixes: {set(range(len(REPLACEMENTS))) - replaced}')
    for index, rects in edits.items():
        for rect in rects:
            public[index].add_redact_annot(fitz.Rect(rect), fill=None)
        public[index].apply_redactions(images=0, graphics=0, text=0)
    for index, line, rr in pending:
        page = public[index]
        for face, path in [('DqbRegular', args.font_regular), ('DqbReference', args.font_reference)]:
            page.insert_font(fontname=face, fontfile=str(path))
        x, y = line['origin']
        color = tuple(((line['color'] >> k) & 255) / 255 for k in (16, 8, 0))
        for face, value in rr:
            page.insert_text((x, y), value, fontname=face, fontsize=line['size'], color=color)
            x += fonts[face].text_length(value, fontsize=line['size'])
    public[4].insert_font(fontname='DqbRegular', fontfile=str(args.font_regular))
    public[4].insert_text((62.7, 406), '편집 정정·조건 보완과 참고문헌 [1]-[7]의 정식 서지는 다음 쪽에 수록했다.',
                          fontname='DqbRegular', fontsize=9, color=(0, .49, .55))
    references = reference_list()
    manifest = json.loads((ROOT / 'reports/reference-manifest.json').read_text())
    note, bottom = appendix(args.font_regular, args.font_bold, args.font_reference, manifest)
    public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
    public.set_metadata({'title': 'Daily Quantum Brief 2026-11-03 - Public archive edition',
                         'author': 'Research Brief',
                         'subject': 'Hardware quantum machine learning controls, orbital embedding, molecular encoding, fractional Chern states and FPGA decoding',
                         'creator': 'AI Tech Review public archive builder',
                         'creationDate': 'D:20261103000000Z', 'modDate': 'D:20261103000000Z'})
    public.del_xml_metadata()
    public.subset_fonts()
    normalized = normalize_to_unicode(public)
    path = ROOT / 'dist/2026-11-03-daily-quantum-brief.pdf'
    path.parent.mkdir(parents=True, exist_ok=True)
    (ROOT / 'notes').mkdir(parents=True, exist_ok=True)
    public.save(path, garbage=4, deflate=True, no_new_id=True)
    final = fitz.open(path)
    checks = []
    for i in range(5):
        diff = ImageChops.difference(bitmap(original[i]), bitmap(final[i]))
        for x0, y0, x1, y1 in edits.get(i, []):
            ImageDraw.Draw(diff).rectangle((math.floor((x0-1)*2), math.floor((y0-1)*2),
                                           math.ceil((x1+1)*2), math.ceil((y1+1)*2)), fill=(0, 0, 0))
        if diff.getbbox() is not None:
            raise ValueError(f'Unexpected pixel change on page {i+1}')
        checks.append({'page': i+1, 'pixels_identical_outside_declared_edits_144dpi': True,
                       'edit_rectangles': edits.get(i, [])})
    text = '\n'.join(page.get_text() for page in final)
    objects = '\n'.join(final.xref_object(x, compressed=False) for x in range(1, final.xref_length()))
    links = [a['uri'] for page in final for a in page.get_links() if 'uri' in a]
    support_links = [link['url'] for links in manifest.get('edition_note_links', {}).values() for link in links]
    expected_links = support_links + [r['url'] for r in references]
    predicates = {
        'no_private_collection_context': not any(t in text for t in ('Gmail', '수집 메모', '연구자·산업계 소셜 신호', '메일에서 발견한', '출판 전 검증 메모', 'LinkedIn')),
        'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
        'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
        'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
        'no_xml_metadata': not final.get_xml_metadata(),
        'no_embedded_files': final.embfile_count() == 0,
        'no_widgets': not any(list(page.widgets() or []) for page in final),
        'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm|GoToR|RichMedia)\b', objects)),
        'expected_reference_links': list(dict.fromkeys(links)) == expected_links,
        'source_access_links_retained': len(set(links)) == 7,
        'corrected_fpga_power_and_interface': '14.2 W' in text and '34 us' in text and 'host 통신' in text,
        'corrected_qml_sampling': '5x107' not in text and '한 자릿수 이상 크게' not in text,
        'corrected_fci_target_scope': 'target state를 준비했다' in text,
        'page_count': len(final) == 6,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / f'public-{i+1}.png'))
    report = {'date': '2026-11-03', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
              'source_pages': 5, 'pages': len(final), 'page_checks': checks, 'inspection': predicates,
              'reference_urls': links, 'appendix_bottom_pt': bottom, 'visual_qa': {'status': 'pending'},
              'metadata': final.metadata, 'file_size_bytes': path.stat().st_size,
              'non_bmp_cmap_destinations_normalized': normalized,
              'independent_review': {'status': 'pending'}, 'independent_reproduction': False}
    (ROOT / 'notes/production-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    entry_path = ROOT / 'reports/archive-entry.json'
    entry = json.loads(entry_path.read_text())
    entry['public_reviewed'] = False
    entry_path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': path.name, 'pages': len(final), 'sha256': report['sha256'], 'appendix_bottom_pt': bottom}))


if __name__ == '__main__':
    main()
