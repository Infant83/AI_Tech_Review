"""Build the six-page reviewed public edition of the 2026-10-29 DQB.

Inputs include the private original and local fonts. No mailbox operation,
archive registration or publication is performed. Rebuilding resets visual QA.
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
SOURCE_SHA256 = '608c9b6b5cd18a832a8b2d87a0c8e5c8182f39d02849354a685bba717ae1e65f'
REMOVALS = {
    0: [(61, 532, 536, 581)],
    4: [(61, 455, 536, 503), (61, 507, 536, 615)],
}
REPLACEMENTS = [
    (1, 'unital channel r=0.5의 best-of-samples 효과',
     'unital r=0.5; 최빈값·동률 시 더 큰 cut'),
    (3, 'magnetization으로 고르면 Slater determinant basis가 되지만 total-spin quantum number로 고르면',
     'magnetization으로 고르면 Slater determinant 기저다. total-spin 기저에는'),
    (3, 'entangled·non-Gaussian state가 된다. Hund density interaction을 넣으면 ground space가 spin-reversal pair로 줄어든다.',
     '얽힌·비가우시안 상태와 Slater 상태가 함께 있다. Hund 항을 넣으면 ground space가 spin-reversal pair로 줄어든다.'),
]
ERDOS_RECT = (148.795, 162.5, 200.52, 172.0)
ERDOS_ORIGIN = (148.78976440429688, 170.43896484375)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bitmap(page):
    p = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes('RGB', (p.width, p.height), p.samples)


def reference_list():
    data = json.loads((ROOT / 'reports/reference-manifest.json').read_text())
    rows = data['references']
    if [r['number'] for r in rows] != list(range(1, 8)):
        raise ValueError('References must follow original first-use order, then code [7]')
    for row in rows:
        if not row['citation'] or not row['url'].startswith('https://'):
            raise ValueError('Missing citation or public HTTPS source')
    return rows


def appendix(regular, bold, reference_font, references):
    for name, path in [('DqbRegular', regular), ('DqbBold', bold), ('DqbReference', reference_font)]:
        pdfmetrics.registerFont(TTFont(name, str(path)))
    out = io.BytesIO()
    c = Canvas(out, pagesize=A4, invariant=1)
    w, h = A4
    y = h - 46

    def para(text, size=9.1, leading=13.3, strong=False, after=6, color='#263a47', font=None):
        nonlocal y
        style = ParagraphStyle('p', fontName=font or ('DqbBold' if strong else 'DqbRegular'),
                               fontSize=size, leading=leading, textColor=HexColor(color), wordWrap='CJK')
        p = Paragraph(text, style)
        _, height = p.wrap(w - 110, h)
        y -= height
        p.drawOn(c, 55, y)
        y -= after

    para('DAILY QUANTUM BRIEF / 2026-10-29', 9, 12, after=9, color='#007e8c')
    para('공개 보관본 편집·서지 보완', 18, 24, True, after=8)
    para('원 DQB 5쪽 + 정정 기록·참고문헌 1쪽', 8.6, 12, color='#60717d', after=10)
    para('편집 기록과 결과를 읽는 조건', 10.5, 14, True, color='#007e8c', after=5)
    para('1·5쪽의 수집·소셜·내부 작업 메모를 삭제하고, 간략 서지를 아래 APS 목록으로 옮겼다. 2쪽의 깨진 <font name="DqbReference">Erdős–Rényi</font> 글꼴과 QAOA 기준선 설명, 4쪽의 total-spin 상태 설명을 정정했다.')
    para('[1]의 approximation ratio는 AR=C(z*)/Copt다. 최종 16,384샷에서 가장 자주 나온 bitstring을 z*로 택하고, 동률이면 cut이 더 큰 것을 쓴다. 따라서 최적 샷만 고르는 best-of-samples가 아니다. 0.815±0.062는 unital r=0.5 모사 기준선의 보고값이며 단일 무작위 샷의 평균이 아니다. 기준선의 집계 분모는 추정하지 않았다.')
    para('[4]의 total-spin 기저에는 얽힌·비가우시안 상태와 Slater 상태가 함께 있다. S=2, M=±2인 극단 상태는 Slater determinant다. 같은 바닥공간의 에너지가 같아도 상태 선택에 따라 상관 해석이 달라진다. [3]의 4차 moment는 수락확률과 출력 분모에, 3·5차 moment는 출력 분자에 들어간다.')
    para('[5]의 공식 저장소 README [7]는 QAI 2026 채택을 저자 보고한다. 정식 proceedings 서지는 확인하지 못해 arXiv v1을 인용했다. 저장소의 채택 주장과 정식 출판 완료를 구별한다.')
    para('참고문헌', 10.5, 14, True, color='#007e8c', after=6)
    for row in references:
        para(f'[{row["number"]}] <link href="{escape(row["url"])}" color="#263a47">{escape(row["citation"])}</link>',
             8.7, 12.4, after=5, font='DqbReference')
    para('책임 편집 김현중 · AI 보조 OpenAI Codex · 근거 기준일 2026-10-29. root: 통합·공개 등록 검토. dqb_20261029_algorithms: [1]·[2]·[5] 전체 37쪽과 관련 코드; dqb_20261029_chemistry_magic: [3]·[4] 전체 27쪽 대조. 원논문 다섯 편의 본문·부록·참고문헌을 읽고 핵심 수식·표·도판을 렌더 대조했다. 별도 보충파일 전체를 확인한 것은 아니다. dqb_20261029_pdf: 원 DQB 전체 5쪽과 D-Wave 발표 전문 확인, 공개 사본 제작·일차 렌더 검수. 정확한 실행 모델 식별자 미보존. AI Tech Review Editorial Harness 2026.08과 현행 문체·APS 기준 적용. 계산·QPU 실험의 독립 재현이나 사람의 문장별 심사는 수행하지 않았다.',
         7.4, 10.7, color='#60717d', after=0)
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


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-pdf', required=True, type=Path)
    p.add_argument('--font-regular', required=True, type=Path)
    p.add_argument('--font-bold', required=True, type=Path)
    p.add_argument('--font-reference', required=True, type=Path)
    p.add_argument('--qa-dir', required=True, type=Path)
    args = p.parse_args()
    raw = args.source_pdf.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise ValueError('Input is not the reviewed original')
    original = fitz.open(stream=raw, filetype='pdf')
    public = fitz.open(stream=raw, filetype='pdf')
    if len(original) != 5:
        raise ValueError('Expected five source pages')
    edits = {i: list(rects) for i, rects in REMOVALS.items()}
    edits[1] = [ERDOS_RECT]
    pending = []
    font = fitz.Font(fontfile=str(args.font_regular))
    for index, old, new in REPLACEMENTS:
        spans = [s for b in original[index].get_text('dict')['blocks'] for l in b.get('lines', [])
                 for s in l['spans'] if s['text'] == old]
        if len(spans) != 1:
            raise ValueError(f'Expected one source line on page {index+1}: {old}')
        s = spans[0]
        x, _ = s['origin']
        width = font.text_length(new, fontsize=s['size'])
        if x + width > 536:
            raise ValueError(f'Replacement exceeds its column on page {index+1}: {x+width}')
        rect = (s['bbox'][0] - .7, s['bbox'][1] - 1,
                max(s['bbox'][2], x + width) + 1, s['bbox'][3] + 1)
        edits.setdefault(index, []).append(rect)
        pending.append((index, s['origin'], s['size'], s['color'], new))
    for index, rects in edits.items():
        for rect in rects:
            public[index].add_redact_annot(fitz.Rect(rect), fill=None)
        public[index].apply_redactions(images=0, graphics=0, text=0)
    for index, origin, size, color, new in pending:
        public[index].insert_font(fontname='DqbRegular', fontfile=str(args.font_regular))
        rgb = tuple(((color >> k) & 255) / 255 for k in (16, 8, 0))
        public[index].insert_text(origin, new, fontname='DqbRegular', fontsize=size, color=rgb)
    public[1].insert_font(fontname='DqbReference', fontfile=str(args.font_reference))
    public[1].insert_text(ERDOS_ORIGIN, 'Erdős–Rényi', fontname='DqbReference', fontsize=8.35,
                          color=(38/255, 58/255, 71/255))
    public[4].insert_font(fontname='DqbRegular', fontfile=str(args.font_regular))
    public[4].insert_text((62.7, 522), '참고문헌 [1]-[7]의 정식 서지와 원문 링크는 다음 쪽에 수록했다.',
                          fontname='DqbRegular', fontsize=9, color=(0, .49, .55))
    references = reference_list()
    note, bottom = appendix(args.font_regular, args.font_bold, args.font_reference, references)
    public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
    public.set_metadata({'title': 'Daily Quantum Brief 2026-10-29 - Public archive edition',
                         'author': 'Research Brief',
                         'subject': 'QAOA noise, quantum simulations, correlated resources and iron oxides',
                         'creator': 'AI Tech Review public archive builder'})
    public.del_xml_metadata()
    public.subset_fonts()
    path = ROOT / 'dist/2026-10-29-daily-quantum-brief.pdf'
    path.parent.mkdir(parents=True, exist_ok=True)
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
        'no_private_collection_context': not any(t in text for t in ('수집 범위', 'Gmail', '지난 실행 이후', '연구자·산업계 소셜 신호', '출판 전 검증 메모')),
        'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
        'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
        'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
        'no_embedded_files': final.embfile_count() == 0,
        'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm|GoToR|RichMedia)\b', objects)),
        'expected_reference_links': list(dict.fromkeys(links)) == [r['url'] for r in references],
        'corrected_erdos_glyph': 'Erdős–Rényi' in text,
        'corrected_qaoa_representative_sample': 'best-of-samples 효과' not in text and '최빈값·동률 시 더 큰 cut' in text,
        'corrected_total_spin_scope': 'Slater 상태가 함께 있다' in text and 'S=2, M=±2' in text,
        'magic_moment_denominator_disclosed': '수락확률과 출력 분모' in text,
        'qml_acceptance_qualified': '정식 proceedings 서지는 확인하지 못해' in text,
        'page_count': len(final) == 6,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / f'public-{i+1}.png'))
    report = {'date': '2026-10-29', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
              'source_pages': 5, 'pages': 6, 'page_checks': checks, 'inspection': predicates,
              'reference_urls': links, 'appendix_bottom_pt': bottom,
              'visual_qa': {'status': 'pending'}, 'independent_qpu_or_training_reproduction': False}
    out = ROOT / 'notes/production-qa.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': path.name, 'pages': len(final), 'sha256': report['sha256'],
                      'appendix_bottom_pt': bottom}))


if __name__ == '__main__':
    main()
