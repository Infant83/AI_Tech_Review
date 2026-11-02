"""Build the reviewed public edition of the 2026-11-02 DQB.

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
SOURCE_SHA256 = 'ccfb504758a70f52d094c2230df892573d201bb23c3512998fafef7c8be2a438'
REMOVALS = {0: [(61, 494.8, 546, 531)], 3: [(55.8, 422.5, 539.5, 465.7)],
            4: [(61, 294, 546, 440)]}
# Prefixes identify scientific text only. Each replacement must match once.
REPLACEMENTS = [(0,
  'npj Quantum Information은 Pandora',
  'npj Quantum Information은 10월 30일 Pandora의 동료평가 채택 원고를 early shared 판본으로 공개했다. PostgreSQL과 병렬 worker로'),
 (0,
  '용해 수십억 gate 회로를 다루고,',
  '수십억 gate를 다룬다. 100×100 Fermi–Hubbard Clifford+T와 1024-bit Shor의 high-level 구성·CtrlScaleModAdd 분해를 보고했다.'),
 (0,
  'fault-tolerant resource workflow를 가능하게',
  'Pandora는 대규모 fault-tolerant resource workflow를 가능하게 하는 고전 소프트웨어이며 QPU 가속과는 별개다.'),
 (0,
  'real-time 조건에서는 threshold',
  'real-time 모사에서는 d=7·9 LER 곡선의 교점이 0.0067 대 0.0043이었다. H100·TPU에서 블록 지연도 측정했다. 11월 1일에는'),
 (0, 'O(d²) scaling; simulated', 'O(d²) scaling; d=7·9 교점 0.0067'),
 (2,
  '[동료평가 저널·고전 HPC/컴파일러]',
  '[동료평가 채택·고전 HPC/컴파일러] npj Quantum Information | early shared 2026-10-30 · arXiv 최초 공개 2025-08-07 [2]'),
 (2,
  'Pandora는 회로를 작은 gate window로',
  'Pandora는 회로 전체를 gate별 행과 이웃 포인터로 PostgreSQL에 저장하고, 독립적인 rewrite worker가 병렬로 변환하는 open-source'),
 (2,
  '다. 저자는 수십억 gate 규모에서',
  '다. 100×100 Fermi–Hubbard의 77억 Clifford+T gate와 1024-bit Shor의 high-level 구성·CtrlScaleModAdd 분해를 보고했다.'),
 (2, 'billions of gates; 10,000 gate', '선택 CNOT pattern rewrite; 10⁴–10⁵ gate 비교'),
 (2, 'Fermi–Hubbard 100×100, 1024-bit Shor', 'Fermi–Hubbard 100×100; Shor 부분회로 분해'),
 (2, '특정 32+ qubit 사례에서', '32큐비트 회로 10개·1000초 timeout 비교'),
 (3, '신경망 decoder의 복잡도는 줄었지만', '신경망 decoder의 복잡도를 줄이고'),
 (3, '제어 루프의 시간은 아직 측정되지 않았다', '가속기에서 블록 지연을 측정했다'),
 (3,
  '[동료평가 저널·고전 ML/QEC]',
  '[동료평가 채택·고전 ML/QEC] npj Quantum Information | early shared 2026-10-28 · arXiv 최초 공개 2025-10-26 [3]'),
 (3,
  'noise를 더하는 simulated real-time',
  'noise를 더하는 SI1000 모사에서는 인접 거리의 LER 곡선 교점을 비교했다. d=7·9 교점은 Mamba 0.0067 대'),
 (3, 'Transformer 0.0097이다.', 'Transformer 0.0043이었다. H100·TPU v6e에서 블록 지연도 측정했다. 전체 제어 루프는 별도 실증이 필요하다.'),
 (3, 'FPGA/GPU/ASIC control stack에', 'H100·TPU 블록 지연 측정; 제어 루프 전체·power 측정과 구별'),
 (3, '[동료평가 저널·이론] npj', '[동료평가 채택·이론] npj Quantum Information | early shared 2026-11-01 [4]'),
 (3,
  'auxiliary system을 prior에 넣어',
  'auxiliary system을 prior에 넣어 평균 entropy의 상·하한을 분석한다. 과거 quantum state 추정, sensing, continuous monitoring'),
 (3, '[동료평가 저널·이론/보안]', '[동료평가 채택·이론/보안] npj Quantum Information | early shared 2026-10-31 [5]'),
 (3,
  'multi-basis position-verification protocol의',
  'multi-basis protocol에서 state preparation과 channel loss를 구분한다. 입력·공유 난수에 따른 손실 선택을 공격자에게 허용하면'),
 (3, '를 포함해 보안 분석을 강화한다.', '증명으로 보장되는 손실 허용 범위가 좁아진다. QKD의 고전 통신 인증 응용을 제안한다. 보안 증명은 유한 양자 기억·결합 출력 차원 등'),
 (3, 'adversary model, loss budget,', '명시된 공격자 모형을 따른다. 이론적 프로토콜·보안 분석이며 실제 네트워크 배치 결과는 제공하지 않는다.'),
 (2, 'repo 기준 Clifford+T 10억', 'Clifford+T 10억 gate당 약 100 GB 디스크'),
 (3, 'code distance d≤9에서 scaling 확인', 'SI1000 d=3·5·7·9 모사; 고정 크기 model'),
 (2, '회로 family와 partition 구조에 의존', '무작위 CNOT 회로와 단일 게이트 누락 조건')]

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

    para('DAILY QUANTUM BRIEF / 2026-11-02', 9, 12, after=7, color='#007e8c')
    para('공개 보관본 편집·서지 보완', 18, 24, True, after=6)
    para('원 DQB 5쪽 + 정정 기록·참고문헌 1쪽', 8.6, 12, color='#60717d', after=8)
    para('편집 기록과 결과를 읽는 조건', 10.5, 14, True, color='#007e8c')
    for index, note in enumerate(manifest['edition_notes']):
        para(note, links=manifest.get('edition_note_links', {}).get(str(index), []))
    para('참고문헌', 10.5, 14, True, color='#007e8c')
    for row in manifest['references']:
        citation = escape(row['citation'])
        locator = escape('doi:' + row['url'].removeprefix('https://doi.org/'))
        if citation.count(locator) != 1:
            raise ValueError('Expected one DOI locator per APS entry')
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
    x, y = line['origin']
    tables = {0: (395, 490, (181, 366)), 1: (230, 285, (170, 375)),
              2: (200, 252, (170, 363)), 3: (215, 251, (295, 542)),
              4: (230, 290, (190, 363))}
    if index in tables:
        top, bottom, (first, second) = tables[index]
        if top <= y <= bottom:
            return first if x < first else (second if x < second else 542)
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
        public[index].apply_redactions(images=0, graphics=1 if index == 3 else 0, text=0)
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
    public[4].insert_text((62.7, 316), '편집 정정·조건 보완과 참고문헌 [1]-[5]의 정식 서지는 다음 쪽에 수록했다.',
                          fontname='DqbRegular', fontsize=9, color=(0, .49, .55))
    references = reference_list()
    manifest = json.loads((ROOT / 'reports/reference-manifest.json').read_text())
    note, bottom = appendix(args.font_regular, args.font_bold, args.font_reference, manifest)
    public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
    public.set_metadata({'title': 'Daily Quantum Brief 2026-11-02 - Public archive edition',
                         'author': 'Research Brief',
                         'subject': 'Reaction-center electronic dynamics, quantum circuit compilation, neural quantum error correction, smoothing and position verification',
                         'creator': 'AI Tech Review public archive builder',
                         'creationDate': 'D:20261102000000Z', 'modDate': 'D:20261102000000Z'})
    public.del_xml_metadata()
    public.subset_fonts()
    normalized = normalize_to_unicode(public)
    path = ROOT / 'dist/2026-11-02-daily-quantum-brief.pdf'
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
        'no_private_collection_context': not any(t in text for t in ('Gmail', '수집 메모', '연구자·산업계 소셜 신호', '메일에서 발견한', '출판 전 검증 메모', 'LinkedIn', 'newsroom')),
        'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
        'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
        'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
        'no_xml_metadata': not final.get_xml_metadata(),
        'no_embedded_files': final.embfile_count() == 0,
        'no_widgets': not any(list(page.widgets() or []) for page in final),
        'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm|GoToR|RichMedia)\b', objects)),
        'expected_reference_links': list(dict.fromkeys(links)) == expected_links,
        'source_access_links_retained': len(links) == 8,
        'corrected_early_shared_status': 'early shared' in text and 'version of record' not in text,
        'corrected_qec_version': '0.0067' in text and '0.0043' in text and '0.0104' not in text and '0.0097' not in text,
        'corrected_block_latency_scope': '블록 지연' in text,
        'corrected_shor_component_scope': 'CtrlScaleModAdd' in text,
        'page_count': len(final) == 6,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / f'public-{i+1}.png'))
    report = {'date': '2026-11-02', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
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
