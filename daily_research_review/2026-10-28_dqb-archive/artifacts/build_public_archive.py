"""Build the reviewed six-page public edition of the 2026-10-28 DQB.

The caller supplies the private original, fonts and private QA directory. This
builder performs no archive registration or publication. Its declared edits
remove collection context, correct source-checked attributions and comparisons,
and move references to a complete APS list on an added editorial page.
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
SOURCE_SHA256 = '5cba0b0888b793946afd6171c4615ebea34a34552a88166a5087b9f87ce3e260'
REMOVALS = {0: [(61, 535, 536, 596)], 3: [(61, 502.5, 535, 552)],
            4: [(61, 513, 536, 626)]}
REPLACEMENTS = [
    (0, 'solver 비교는 공개되지 않았다. “양자 가속”보다 “하이브리드 서비스의 time-to-solution 우위”로 읽는 것이 맞다.',
     'solver 비교는 공개되지 않았다. 시간 감소율은 논문 설정의 하이브리드 서비스 비교이며 해의 품질도 함께 봐야 한다.'),
    (1, '[프리프린트·하이브리드 양자–고전] Richter et al. | arXiv:2610.35478 v1 | 제출 2026-10-26 [1]',
     '[프리프린트·하이브리드 양자–고전] Wu et al. | arXiv:2610.35478 v1 | 제출 2026-10-26 [1]'),
    (1, 'large C2에서 GA 약 1일, PSO 3일 이상', 'C2: GA 약 6시간, PSO 3일 이상'),
    (1, 'complete problem 직접 풀이; HNLM이', 'complete problem 직접 풀이; HNLM은'),
    (1, '78.6%에서 최단시간', '하이브리드 4방법 중 11/14에서 최단'),
    (2, '[프리프린트·고전 계산] arXiv:2610.35498 | 문서일 2026-10-27 [2]',
     '[프리프린트·고전 계산] arXiv:2610.35498 | 문서일 2026-10-26 [2]'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bitmap(page):
    p = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes('RGB', (p.width, p.height), p.samples)


def reference_list():
    rows = json.loads((ROOT / 'reports/reference-manifest.json').read_text())['references']
    assert [r['number'] for r in rows] == list(range(1, 8))
    return rows


def appendix(regular, bold, reference_font, references):
    for name, path in [('DqbRegular', regular), ('DqbBold', bold), ('DqbReference', reference_font)]:
        pdfmetrics.registerFont(TTFont(name, str(path)))
    out = io.BytesIO()
    c = Canvas(out, pagesize=A4, invariant=1)
    w, h = A4
    y = h - 48

    def para(text, size=9.3, leading=14, strong=False, after=7, color='#263a47', font=None):
        nonlocal y
        style = ParagraphStyle('p', fontName=font or ('DqbBold' if strong else 'DqbRegular'),
                               fontSize=size, leading=leading, textColor=HexColor(color), wordWrap='CJK')
        p = Paragraph(text, style)
        _, height = p.wrap(w - 110, h)
        y -= height
        p.drawOn(c, 55, y)
        y -= after

    para('DAILY QUANTUM BRIEF / 2026-10-28', 9, 12, after=10, color='#007e8c')
    para('공개 보관본 편집·서지 보완', 18, 24, True, after=8)
    para('원 DQB 5쪽 + 정정 기록·참고문헌 1쪽', 8.6, 12, color='#60717d', after=11)
    para('편집 기록과 비교 조건', 10.5, 14, True, color='#007e8c', after=5)
    para('1·4쪽의 자료 수집 경위와 5쪽의 수집·출판 메모를 삭제하고, 간략 서지를 아래 APS 목록으로 옮겼다. 2쪽 [1]의 저자를 Wu 등으로 정정했다. 3쪽 [2]의 원문 문서일은 2026-10-26이다.')
    para('[1] Table 5의 C2에서 GA 시간은 21,866.68초(약 6.07시간)다. 원 논문 본문의 “almost one day”와 표가 달라 표에 맞춰 2쪽 값을 정정했다. HNLM의 11/14(78.6%) 최단시간은 하이브리드 네 방법 내부 비교다. 전체 일곱 방법에서는 10/14(71.4%)다.')
    para('C2의 94.51% 시간 감소는 HNLM 70.14초와 TBSA 1,278초의 비교다. 목적함수는 각각 132,791,292와 127,246,239로 해의 품질이 같지 않다. 이에 1쪽의 time-to-solution 우위 표현을 논문 설정의 계산시간 비교로 한정했다. 17.41% 목적값 개선과 81.34% 시간 감소는 A3의 IBQM 대 PSO 비교다.')
    para('[2]의 trapping·bias 개선은 보고된 고전 잡음·디코더 실험 조건에서 관측한 결과다. 일반 코드·디코더 조합의 무편향성이나 ergodicity를 증명한 것은 아니며, circuit-level noise 검증은 남아 있다.')
    para('[4]의 trace-norm 오차는 정규화된 Choi 상태 사이의 오차이며 일반 채널의 최악경우 diamond-norm 보장과 같지 않다. [6]의 비단열 실시간 동역학은 함께 개발한 QED-NEO-TDCI 변형에 해당한다. [7]의 공식 일정은 리뷰 공개 11월 5일, 최종 결정 12월 16일(AOE)이다. 이는 전체 학회 채택 현황을 조사한 결과가 아니다.')
    para('참고문헌', 10.5, 14, True, color='#007e8c', after=6)
    for r in references:
        para(f'[{r["number"]}] <link href="{escape(r["url"])}" color="#263a47">{escape(r["citation"])}</link>',
             8.8, 12.7, after=6, font='DqbReference')
    para('책임 편집 김현중 · AI 보조 OpenAI Codex · 근거 기준일 2026-10-28. root: 통합·공개 등록 검토; dqb_20261028_research: 공장 최적화·Intel 원문 대조; dqb_20261028_secondary: 오류정정·채널·화학·일정 서지 대조; dqb_20261028_pdf: 공개 사본·렌더 검수. 정확한 실행 모델 식별자 미보존. AI Tech Review Editorial Harness 2026.08과 현행 문체·APS 기준 적용. [4]는 정식 서지·초록과 선행 원고, [6]은 출판사 등록 초록·서지 범위에서 대조했다. QPU·대규모 계산의 독립 재현이나 사람의 문장별 감수는 수행하지 않았다.',
         7.5, 11, color='#60717d', after=0)
    if y < 58:
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
    assert len(original) == 5
    edits = {i: list(rects) for i, rects in REMOVALS.items()}
    pending = []
    font = fitz.Font(fontfile=str(args.font_regular))
    for index, old, new in REPLACEMENTS:
        spans = [s for b in original[index].get_text('dict')['blocks'] for l in b.get('lines', [])
                 for s in l['spans'] if s['text'] == old]
        if len(spans) != 1:
            raise ValueError(f'Expected one source line on page {index+1}: {old}')
        s = spans[0]
        x, y = s['origin']
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
    public[4].insert_font(fontname='DqbRegular', fontfile=str(args.font_regular))
    public[4].insert_text((62.7, 532), '참고문헌 [1]-[7]의 정식 서지와 원문 링크는 다음 쪽에 수록했다.',
                          fontname='DqbRegular', fontsize=9, color=(0, .49, .55))
    references = reference_list()
    note, bottom = appendix(args.font_regular, args.font_bold, args.font_reference, references)
    public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
    public.set_metadata({'title': 'Daily Quantum Brief 2026-10-28 - Public archive edition',
                         'author': 'Research Brief', 'subject': 'Factory optimization, error correction and quantum computing stacks',
                         'creator': 'AI Tech Review public archive builder'})
    public.del_xml_metadata()
    public.subset_fonts()
    path = ROOT / 'dist/2026-10-28-daily-quantum-brief.pdf'
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
        'no_private_collection_context': not any(t in text for t in ('수집 범위', 'Gmail', '지난 실행 이후', '연구자·산업계 소셜 신호')),
        'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
        'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
        'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
        'no_embedded_files': final.embfile_count() == 0,
        'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm)\b', objects)),
        'expected_reference_links': list(dict.fromkeys(links)) == [r['url'] for r in references],
        'corrected_author': 'Richter' not in text and 'Wu et al.' in text,
        'corrected_mcmc_date': '문서일 2026-10-27' not in text and '문서일 2026-10-26' in text,
        'corrected_ga_time': 'GA 약 1일' not in text and 'GA 약 6시간' in text,
        'qualified_hnlm_denominator': '하이브리드 4방법 중 11/14' in text,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / f'public-{i+1}.png'))
    report = {'date': '2026-10-28', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
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
