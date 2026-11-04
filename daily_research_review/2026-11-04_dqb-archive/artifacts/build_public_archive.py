"""Build the reviewed public edition of the 2026-11-04 DQB.

The four-page private original and fonts are caller-supplied. This performs
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
SOURCE_SHA256 = 'c94d9a5ba8649c702db656f01e5b6905af84d0c73596e506cf60f82118be7dbc'
REMOVALS = {0: [(61, 483, 546, 518)], 3: [(61, 462, 546, 586)]}
# Each reviewed source-line prefix must match exactly once.
REPLACEMENTS = [(0, '단일-shot 피드백이', '단일-shot 피드백이 bistable qubit의 오류를 줄였고, 고전 Pauli propagation은 100큐비트 다체문'),
 (1, '시간에 따른 최악', '최대 0.28%와 평균 0.065%의 비교'),
 (0, '흔들리는 큐비트를', '큐비트의 주파수 변화를 따라가다'),
 (0, '제를 2분에', '제의 에너지를 약 2.5분에 근사해 하드웨어와 알고리즘의 두 병목을 함께 드러냈다.'),
 (0, 'Applied Physics Reviews가', '10월 30일 Appl. Phys. Rev. 논문과 11월 3일 기관 발표는 강결합 TLS로 추정되는 결함에 따라 두 주파수 사이를 오가는'),
 (0,
  'superconducting qubit를',
  'superconducting qubit의 control frame을 single-shot 1-bit FPGA feedback으로 바꿔 동작을 안정화했다. branch를 판별한 뒤 frame'),
 (0, '을 바꾸고, 약 136', '을 갱신하고, 약 136 kHz estimation bandwidth에서 평균 gate error를 0.14%에서 0.065%로 낮췄다. 이는 한 큐비트의 bistable noise'),
 (0,
  'single CPU thread에서',
  '단일 CPU thread에서 약 2.5분에 계산했고, 64-thread DMRG의 약 53.6시간과 비교했다. 84-qubit hexabenzocoronene pi active space'),
 (0, '100-qubit Heisenberg 약', '100-qubit Heisenberg 약 2.5분; 84-qubit HBC'),
 (1, 'TLS가 바꾼 공진주파수를', '두 주파수 사이의 전환을'),
 (1, '고체 qubit 주변의', 'qubit 공진주파수는 두 값 사이에서 불규칙하게 전환됐고, 저자들은 이를 강결합 two-level-system(TLS)과 연관된 현상으로 해석했다.'),
 (1, '환된다. 같은 microwave', '같은 microwave pulse를 계속 쓰면 gate error가 커진다. 연구팀은 계산 직전 qubit을 준비하고 짧게 진화시킨 뒤 한 번 측정해 현재'),
 (1, '뒤 한 번 측정해', 'frequency branch를 판별하고 FPGA controller가 control frame을 선택하도록 했다. 두 주파수와 판별 sequence는 사전에 정한다.'),
 (2, '10x10은 single CPU', '10x10은 single CPU thread 약 2.5분'),
 (2, '약 2분', '약 2.5분'),
 (2, '논문 DMRG:', '논문 DMRG: 64 threads, 약 53.6시간'),
 (2, '2분 대 50시간', '2.5분 대 53.6시간은 해당 implementation·정확도·hardware의 비교다. DMRG bond dimension, boundary condition,'),
 (2, 'vDBF는 double-bracket', 'vDBF는 double-bracket flow의 operator를 greedy하게 고르고 Pauli 계수를 전파하며, 작은 계수의 Pauli fluctuation을 절단한다.'),
 (2, '여러 threshold 결과를', '고정 threshold의 최적화 trajectory에서 energy와 보정 variance를 얻어 zero-variance로 외삽한다. 각 threshold 계산은 따로 비교한다.'),
 (2, '증에 쓰이던 Pauli', '양자 회로의 고전 검증에 쓰이던 Pauli propagation을 직접 many-body solver로 전환한 연구다.'),
 (2, '최대 128 qubits', '최대 100 qubits; sub-1% relative energy error'),
 (2, 'QMC가 어려운 sign-problem', '64 sites / 128 JW qubits; sign-problem 영역'),
 (2,
  'hexabenzocoronene처럼',
  'hexabenzocoronene처럼 큰 pi-system active space가 single CPU에서 근사 가능해지면, 84-qubit 표현 자체보다 고전 근사의 정확도와 비용이'),
 (2, '기 어렵다. OLED', '중요해진다. OLED·유기 반도체에서는 geometry·excited state·SOC·force까지 어떤 비용과 정확도로 계산되는지가 다음 기준이다.'),
 (3, '[동료평가 저널·이론', '[동료평가 채택본·이론/시뮬레이션] npj Quantum Information | 온라인 공개 2026-11-02 [3]'),
 (3,
  'extraction, stochastic',
  'extraction, stochastic+coherent noise를 함께 추적하는 extended stabilizer simulation을 제시했다. 동료평가 채택본은 [[14,1,3]]'),
 (3, 'code 표기와 최종', 'code 표기와 채택본의 표기가 달라 판본별 결과를 구분해야 한다.'),
 (3, '[PoC/로드맵·재료]', '[PoC/로드맵·재료] UCSB 설명 기사 2026-11-03 [4]'),
 (3,
  '연간 최대 $1M,',
  '연 최대 $1M을 지향하며 sensing, secure communication, materials discovery, theoretical modeling, electronic properties의'),
 (3, '다섯 축을 시작한다.', '다섯 연구축을 둔다. 20년은 에너지 저장 관련 quantum sensing·모델링의 장기 전망이다. QPU, quantum advantage,'),
 (3, 'vehicle KPI,', 'vehicle KPI나 배터리 후보 성능은 공개되지 않았다. 제조 PoC보다 초기 연구 portfolio로 분류해야 한다.'),
 (3,
  'silicon barrier,',
  'silicon barrier, 제일원리 결함 계산과 qubit test를 결합한다. silicon-fin junction은 transmon footprint를 100배 넘게 줄일 가능성을'),
 (0, 'extraction을 제안했다.', 'extraction을 제안했다. Princeton 주도 NSF MARQUIS의 UCSB 연구팀과 UChicago-Toyota는 각각 junction material과'),
 (0, '$27.9M, 5년;', '$27.9M, 5년; junction 결함·epitaxy·제일원리 계산'),
 (0, 'coherent noise 보존', 'CE 제약 보존 gate·syndrome framework')]

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
    if [r['number'] for r in rows] != list(range(1, 6)):
        raise ValueError('Keep original scientific first-use order [1]-[5]')
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

    para('DAILY QUANTUM BRIEF / 2026-11-04', 9, 12, after=7, color='#007e8c')
    para('공개 보관본 편집·서지 보완', 18, 24, True, after=6)
    para('원 DQB 4쪽 + 정정 기록·참고문헌 1쪽', 8.6, 12, color='#60717d', after=8)
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
    c.drawRightString(w - 55, 27, '5')
    c.showPage()
    c.save()
    return out.getvalue(), y


def line_right(index, line):
    x, y = line['origin']
    if line['size'] < 6.3:
        bounds = {0: (180, 365), 1: (180, 356), 2: (182, 373), 3: (182, 356)}[index]
        if x < 180: return bounds[0]
        if x < 360: return bounds[1]
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
    if len(original) != 4:
        raise ValueError('Expected four source pages')
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
    public[3].insert_font(fontname='DqbRegular', fontfile=str(args.font_regular))
    public[3].insert_text((62.7, 482), '편집 정정·조건 보완과 참고문헌 [1]-[5]의 정식 서지는 다음 쪽에 수록했다.',
                          fontname='DqbRegular', fontsize=9, color=(0, .49, .55))
    references = reference_list()
    manifest = json.loads((ROOT / 'reports/reference-manifest.json').read_text())
    note, bottom = appendix(args.font_regular, args.font_bold, args.font_reference, manifest)
    public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
    public.set_metadata({'title': 'Daily Quantum Brief 2026-11-04 - Public archive edition',
                         'author': 'Research Brief',
                         'subject': 'Single-shot qubit feedback, classical Pauli propagation, constant-excitation error correction and research roadmaps',
                         'creator': 'AI Tech Review public archive builder',
                         'creationDate': 'D:20261104000000Z', 'modDate': 'D:20261104000000Z'})
    public.del_xml_metadata()
    public.subset_fonts()
    normalized = normalize_to_unicode(public)
    path = ROOT / 'dist/2026-11-04-daily-quantum-brief.pdf'
    path.parent.mkdir(parents=True, exist_ok=True)
    (ROOT / 'notes').mkdir(parents=True, exist_ok=True)
    public.save(path, garbage=4, deflate=True, no_new_id=True)
    final = fitz.open(path)
    checks = []
    for i in range(4):
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
        'source_access_links_retained': len(set(links)) == 6,
        'corrected_feedback_scope': 'control frame' in text and 'TLS로 추정' in text,
        'corrected_pauli_timing': '2.5분' in text and '53.6시간' in text,
        'page_count': len(final) == 5,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / f'public-{i+1}.png'))
    report = {'date': '2026-11-04', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
              'source_pages': 4, 'pages': len(final), 'page_checks': checks, 'inspection': predicates,
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
