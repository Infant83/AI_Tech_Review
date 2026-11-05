"""Build the reviewed public edition of the 2026-11-05 DQB.

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
SOURCE_SHA256 = '6872c3bfb74be19e314666712dc5952dbb9ecc07ac87c216259e211ecc40c6ed'
REMOVALS = {0: [(61, 448, 546, 483)], 3: [(61, 481, 546, 613)]}
# Reviewed exact-line replacements, populated after primary-source audit.
REPLACEMENTS = [(0, '같은 날 공개된 두 프리프린트는', '11월 3일 공개된 두 프리프린트는 VQC 설계와 QML 검증을 다룬다. 하나는 데이터 Fourier coefficient, QFIM rank, readout dimension'), (0, '지만, 실제 IBM 장치에서는', '지만, IBM 장치에서는 두 짧은 문장쌍의 attention overlap을 읽었다. evidence 측정은 v1에서 실패했고 후속 코드는 조건을 보완했다.'), (0, '뮬레이션에서 좋은 목적함수를', '뮬레이션에서 좋은 목적함수를 보였지만 실제 QPU는 없고, convergence 실험 평균 49.36 million shots 상당의 sampling과 repair가 포함됐다.'), (0, '전체 모델·evidence QPU 실행 실패;', 'v1 evidence 측정 실패; 후속 코드는 조건 보완'), (0, 'Pandora [4] [동료평가 저널·고전 HPC]', 'Pandora [4] [동료평가 채택본·고전 HPC]'), (2, '첫 규칙은 label function의', '첫 규칙은 정한 encoding·product Fourier basis·선형 diagonal readout 아래, 얽힘 없는 회로의 support별 Fourier tensor가 rank≤1임을 쓴다.'), (2, 'entanglement가 필요하며,', 'rank가 2 이상이면 그 모형에서 얽힘이 필요하지만 rank one만으로 표현 가능성이 보장되지는 않는다. singular-value tail은 MSE 하한을 준다.'), (2, 'dynamical Lie algebra ceiling에서', '둘째는 QFIM rank의 포화를 depth 선택의 출발점으로 쓴다. 셋째는 한 computational-basis shot batch에서 모든 2^N-1 Pauli-Z product를'), (2, 'Pauli-Z product를 얻어', '추정한다. 이는 확률 단체의 2^N-1개 방향이며, 임의 상태의 모든 정보를 읽는다는 뜻은 아니다.'), (2, '78.5%', '78.5% ± 1.8% (5 seeds)'), (2, 'architecture search cost를 줄인 사례', '구조 탐색의 출발점; 최적 성능 보장은 아님'), (3, 'millions of shots를 요구하는 실험', 'millions of shots를 요구하는 모사'), (3, 'Ultra-large-scale compilation with Pandora', 'Ultra-large-scale compilation and manipulation of quantum circuits with Pandora'), (3, '[동료평가 저널·고전 HPC]', '[동료평가 채택본·고전 HPC] npj Quantum Information · 온라인 공개 2026-10-30 [4]'), (3, 'manipulation·equivalence checking·resource', 'manipulation·equivalence checking·resource estimation한다. Fermi-Hubbard 100×100의 약 77억 Clifford+T gate를 컴파일했다.'), (3, '했고, 10,000 gates 이상에서', '1024-bit Shor는 고수준 회로와 부분 연산 하나의 분해·캐싱이다. 특정 희소 CNOT rewrite와 32-qubit 동등성 검사 비교도 제시했다.'), (3, '이는 고전 compiler/HPC 성능이다.', '이는 고전 compiler/HPC 성능이다. 약 100 GB/10억 gate는 디스크 표현량이며, rewrite 시간은 회로 생성과 DB 적재를 제외한다. gate count'), (3, 'bounded circuit를 매우 많이 반복', '20 runs 평균; 실제 QPU shot 아님'), (3, '가장 큰 overall resource 사용', 'convergence 실험; fixed-5000s 표와 구별'), (0, 'circuit rewrite와 Fermi–Hubbard', 'circuit rewrite와 Fermi-Hubbard 100×100의 full compilation, Shor의 고수준 회로·부분 연산 분해를 다룬다. QAOA-QWS는 Aer MPS 시'), (0, 'e-SNLI 76.98%; IBM overlap', 'e-SNLI 76.98%; pair3763 overlap r=0.992'), (2, '양자 경계는 좁다. IBM', 'IBM ibm_kingston에서는 4 data qubits와 ancilla 1개로 attention overlap만 읽고, encoding·정규화·FFN·readout은 고전 계산했다.'), (2, '산했다. 두 짧은 문장쌍에서', 'r=0.992는 pair3763 첫 block의 overlap 256개다. v1 evidence 보정 실패와 software v2.0의 조건 보완은 5쪽에서 구별한다.'), (2, '23 qubits·852 CNOT의', '23 qubits·852 CNOT은 별도 coherent attention layer의 컴파일·statevector 결과이며, 전체 모델의 QPU 학습·추론은 아니다.'), (3, '뒤 classical feasibility', '뒤 classical feasibility repair를 적용했다. 공통 5,000초 실험에서 S5의 관광객당 평균 효용은 0.866±0.022로'), (3, '1024 shots/update;', '1024 shots/update; S5 평균 49.36M QAOA shots'), (3, '약 5,842 s, 33.8 GB', '수렴 실험: 5,842 s, 33.8 GB (평균)'), (2, 'Born rule로 attention,', '분모를 입력값으로 고정한 경로에서 word evidence의 합은 class probability와 무정보 기준값의 차이와 정확히 같다. e-SNLI')]

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

    bottoms = []

    def footer(number):
        if y < 57:
            raise ValueError(f'Appendix overflow on page {number}: bottom={y}')
        bottoms.append(y)
        c.setStrokeColor(HexColor('#cadadd'))
        c.line(55, 40, w - 55, 40)
        c.setFont('DqbRegular', 7.5)
        c.setFillColor(HexColor('#60717d'))
        c.drawString(55, 27, 'AI TECH REVIEW / PUBLIC EDITION')
        c.drawRightString(w - 55, 27, str(number))
        c.showPage()

    para('DAILY QUANTUM BRIEF / 2026-11-05', 9, 12, after=7, color='#007e8c')
    para('공개 보관본 편집·조건 보완', 18, 24, True, after=6)
    para('원 DQB 4쪽 + 정정 기록 1쪽 + APS 참고문헌 1쪽', 8.6, 12, color='#60717d', after=8)
    for index, note in enumerate(manifest['edition_notes']):
        para(note, links=manifest.get('edition_note_links', {}).get(str(index), []))
    para(manifest['production_disclosure'], 8.0, 11.1, color='#60717d', after=0)
    footer(5)
    y = h - 43
    para('DAILY QUANTUM BRIEF / 2026-11-05', 9, 12, after=7, color='#007e8c')
    para('참고문헌', 18, 24, True, after=12)
    for row in manifest['references']:
        citation = escape(row['citation'])
        for link in [{'locator': row['locator'], 'url': row['url']}] + row.get('additional_locators', []):
            locator = escape(link['locator'])
            if citation.count(locator) != 1:
                raise ValueError('Expected one exact source locator per APS source')
            citation = citation.replace(locator, f'<link href="{escape(link["url"])}" color="#263a47">{locator}</link>')
        para(f'[{row["number"]}] {citation}', 10, 15, after=12, ref=True)
    footer(6)
    c.save()
    return out.getvalue(), bottoms


def line_right(index, line):
    x, y = line['origin']
    if line['size'] < 6.3:
        bounds = {0: (182, 366), 1: (196, 377), 2: (187, 343), 3: (187, 363)}[index]
        if x < 180: return bounds[0]
        if x < 300: return bounds[1]
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
    public[3].insert_text((62.7, 499), '편집 정정·조건 보완과 참고문헌 [1]-[5]의 정식 서지는 다음 쪽에 수록했다.',
                          fontname='DqbRegular', fontsize=9, color=(0, .49, .55))
    references = reference_list()
    manifest = json.loads((ROOT / 'reports/reference-manifest.json').read_text())
    note, bottom = appendix(args.font_regular, args.font_bold, args.font_reference, manifest)
    public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
    public.set_metadata({'title': 'Daily Quantum Brief 2026-11-05 - Public archive edition',
                         'author': 'Research Brief',
                         'subject': 'Hybrid optimization, data-informed VQC design, Born-measured attention, circuit compilation and QAOA simulation',
                         'creator': 'AI Tech Review public archive builder',
                         'creationDate': 'D:20261105000000Z', 'modDate': 'D:20261105000000Z'})
    public.del_xml_metadata()
    public.subset_fonts()
    normalized = normalize_to_unicode(public)
    path = ROOT / 'dist/2026-11-05-daily-quantum-brief.pdf'
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
    reference_links = [link['url'] for row in references for link in [{'url': row['url']}] + row.get('additional_locators', [])]
    expected_links = list(dict.fromkeys(support_links + reference_links))
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
        'source_access_links_retained': set(reference_links).issubset(set(links)),
        'primary_source_audit_complete': bool(manifest.get('source_audit_complete')),
        'corrected_issue_date': '2026-11-05' in text,
        'page_count': len(final) == 6,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / f'public-{i+1}.png'))
    report = {'date': '2026-11-05', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
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
