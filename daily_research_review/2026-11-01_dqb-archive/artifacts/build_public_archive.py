"""Build the reviewed public edition of the 2026-11-01 DQB.

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
SOURCE_SHA256 = 'd73ac203ae1654ea0ecb328120374dd0ec500395d2301edeb59ff3ba573dac7b'
REMOVALS = {0: [(61, 494, 546, 541)], 4: [(61, 339, 546, 516)]}
# Prefixes identify science lines, never private mail metadata.
REPLACEMENTS = [
    (0, '양자·재료 분야 LLM 논문 228편의 88%',
     '양자·재료 LLM 논문 228편의 88%에 AI referee가 중대 문제를 지적했다. QAOA·DFT·하드웨어 성과도'),
    (0, '도 실제 QPU, statevector,',
     '실제 QPU, statevector, 고전 후처리의 역할과 평가 조건을 구분해 읽어야 한다.'),
    (0, '지난 실행 이후 Gmail에서 확인한',
     'Akhmerov의 Journal Club 자료는 2026년 4월 18일–10월 18일 공개된 응집물질·재료·양'),
    (0, 'MaxCut에서 고전 multistart local-search 기준의',
     'MaxCut에서 최종 local search 전 고전 multistart 기준의 95.6%를 얻었다. depth-1 statevector QAOA와 heuristic light-cone'),
    (0, 'truncation, 고전 local refinement를',
     'truncation을 쓴 수치 연구다. 별도 소규모 finite-sampling 분석과 달리 이 큰 문제 결과에는 실제 QPU·유한샷·wall-clock 평가가 없다.'),
    (0, '중대한 문제 88%; 재현자료 미공개',
     'AI referee 지적률 88%; 재현자료 51%'),
    (0, 'p=1 statevector·고전 refinement;',
     'p=1 statevector; 최종 local search 전'),
    (0, '고전 ML/DFT benchmark; SCF·소재',
     'QH9 SCF 초기화 평가; 소재 screening 미검증'),
    (0, 'multi-atom 1%까지 64.8 μs;',
     'multi-atom 1%까지 64.8 μs; 58.2% single filling'),
    (1, 'Gmail로 도착한 Journal Club 자료는',
     'Journal Club 자료는 2026년 4월 18일–10월 18일 arXiv 프리프린트 중 제목·초록에 LLM 또는 agent의 사용·제안이'),
    (1, '드러난 228편, 1,426명을 모았다.',
     '드러난 228편·저자 1,426명을 모았다. 논문 내 최신 범용 model 출시→첫 arXiv 제출 간격은 189편에서 중앙96일이었다. 물리 세계 자체를'),
    (1, 'control에서도 major issue가 76%',
     'control의 major issue 지적률은 76%, 같은 분야 AI 130편은 84%였다. substantial/severe overclaiming은 각각 22%와 38%였다.'),
    (2, '10 instances; weighted 3-regular;',
     '10 instances; pre-LS; ≤10 qubits/circuit'),
    (2, '13 leaf blocks; heuristic',
     '13 leaf blocks; pre-LS; truncated light cones'),
    (2, 'exact enumeration, lifting 뒤에는',
     'exact enumeration과 선택적 고전 정련을 쓴다. 위 N=500·1000 비율은 최종 local search 전이며, N=40 수치는 정련 후다. 별도 N=16'),
    (2, 'shots·noise·queue·number of circuit',
     'finite-sampling 모사도 있다. 큰 문제의 장치 잡음·총 회로 실행 수·end-to-end wall-clock 성능은 평가하지 않았다.'),
    (2, 'shift, occupied–virtual mixing, occupied',
     'shift, occupied–virtual mixing, 내부 회전으로 나눈다. density-blind 방향 비율은 QH9-stable에서 중앙값 69.0%다.'),
    (2, '든 orbital-energy shift에 blind하다.',
     '이는 4,000분자의 방향 개수 기준이며 오류 norm 비율이 아니다. FermiScope는 누적 국소상태밀도 N(r,E)를'),
    (3, '고, 2D에서는 atom number에 대해',
     '고, 2D의 N=L² 모드와 보조열을 쓰는 HVH 구성에서 O(√N) 회로 깊이를 제안했다. intensity noise와 addressing'),
    (2, 'QH9의 세 architecture, 네 split에서',
     'QH9에서는 pretrained 대비 세 architecture·네 split의 12개 조합이 개선됐다. standard split의 HOMO–LUMO gap error는'),
    (2, '36–77% 감소했지만 WALoss는',
     '36–77% 감소했지만 WALoss는 9개 shifted setting 중 3개에서 악화됐다. QH9의 SCF 초기화 평가도 있으며, 기존 학습 모형과 비슷한'),
    (2, 'screening의 SCF 회수율,',
     '결과다. 실제 OLED/material screening의 성능·계산비용으로 확대하려면 새로운 대상과 기준법을 비교해야 한다.'),
]


def restore(text):
    return text.replace('\x00ZiZj\x00', '⟨ZᵢZⱼ⟩')


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
    if [r['number'] for r in rows] != list(range(1, 7)):
        raise ValueError('Keep original scientific first-use order [1]-[6]')
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

    def para(text, size=9.5, leading=13.7, strong=False, after=5, color='#263a47', ref=False):
        nonlocal y
        style = ParagraphStyle('p', fontName='DqbReference' if ref else ('DqbBold' if strong else 'DqbRegular'),
                               fontSize=size, leading=leading, textColor=HexColor(color), wordWrap='CJK')
        p = Paragraph(text if ref else mixed(text), style)
        _, height = p.wrap(w - 110, h)
        y -= height
        p.drawOn(c, 55, y)
        y -= after

    para('DAILY QUANTUM BRIEF / 2026-11-01', 9, 12, after=7, color='#007e8c')
    para('공개 보관본 편집·서지 보완', 18, 24, True, after=6)
    para('원 DQB 5쪽 + 정정 기록·참고문헌 1쪽', 8.6, 12, color='#60717d', after=8)
    para('편집 기록과 결과를 읽는 조건', 10.5, 14, True, color='#007e8c')
    for note in manifest['edition_notes']:
        para(note)
    para('참고문헌', 10.5, 14, True, color='#007e8c')
    for row in manifest['references']:
        para(f'[{row["number"]}] <link href="{escape(row["url"])}" color="#263a47">{escape(row["citation"])}</link>',
             9.1, 12.7, after=5, ref=True)
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
    tables = {0: (390, 492, (181, 366)), 1: (186, 281, (227, 307)),
              2: (186, 251, (187, 347)), 4: (242, 337, (173, 358))}
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
    public[4].insert_text((62.7, 360), '편집 정정·조건 보완과 참고문헌 [1]-[6]의 정식 서지는 다음 쪽에 수록했다.',
                          fontname='DqbRegular', fontsize=9, color=(0, .49, .55))
    references = reference_list()
    manifest = json.loads((ROOT / 'reports/reference-manifest.json').read_text())
    note, bottom = appendix(args.font_regular, args.font_bold, args.font_reference, manifest)
    public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
    public.set_metadata({'title': 'Daily Quantum Brief 2026-11-01 - Public archive edition',
                         'author': 'Research Brief',
                         'subject': 'Scientific AI evaluation, hierarchical optimization, electronic-structure learning and quantum hardware',
                         'creator': 'AI Tech Review public archive builder',
                         'creationDate': 'D:20261101000000Z', 'modDate': 'D:20261101000000Z'})
    public.del_xml_metadata()
    public.subset_fonts()
    normalized = normalize_to_unicode(public)
    path = ROOT / 'dist/2026-11-01-daily-quantum-brief.pdf'
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
    predicates = {
        'no_private_collection_context': not any(t in text for t in ('Gmail', '수집 메모', '연구자·산업계 소셜 신호', '메일에서 발견한', '출판 전 검증 메모', 'LinkedIn', 'newsroom')),
        'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
        'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
        'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
        'no_xml_metadata': not final.get_xml_metadata(),
        'no_embedded_files': final.embfile_count() == 0,
        'no_widgets': not any(list(page.widgets() or []) for page in final),
        'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm|GoToR|RichMedia)\b', objects)),
        'expected_reference_links': list(dict.fromkeys(links)) == [r['url'] for r in references],
        'verified_correlation_glyphs': '⟨ZᵢZⱼ⟩' in text,
        'ai_referee_scope': 'AI referee' in text and '189편' in text,
        'headline_pre_local_search_scope': '최종 local search 전' in text,
        'scf_initialization_present': 'SCF 초기화 평가' in text,
        'filling_not_retention': 'single filling' in text and 'single retention' not in text,
        'page_count': len(final) == 6,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / f'public-{i+1}.png'))
    report = {'date': '2026-11-01', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
              'source_pages': 5, 'pages': len(final), 'page_checks': checks, 'inspection': predicates,
              'reference_urls': links, 'appendix_bottom_pt': bottom, 'visual_qa': {'status': 'pending'},
              'metadata': final.metadata, 'file_size_bytes': path.stat().st_size,
              'non_bmp_cmap_destinations_normalized': normalized,
              'independent_reproduction': False}
    (ROOT / 'notes/production-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    entry_path = ROOT / 'reports/archive-entry.json'
    entry = json.loads(entry_path.read_text())
    entry['public_reviewed'] = False
    entry_path.write_text(json.dumps(entry, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': path.name, 'pages': len(final), 'sha256': report['sha256'], 'appendix_bottom_pt': bottom}))


if __name__ == '__main__':
    main()
