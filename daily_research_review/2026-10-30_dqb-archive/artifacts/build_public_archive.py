"""Build the six-page reviewed public edition of the 2026-10-30 DQB.

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
SOURCE_SHA256 = 'a08d70590b22db69c1a665b5cf21721c4ce22f3d0ddc05e72b5fd8c245f8921f'
REMOVALS = {
    0: [(61, 534, 546, 581)],
    4: [(61, 434, 546, 593)],
}
# Page-5 collection-only row, social/production notes and short bibliography
# are actually removed. The six scientific references move to the appendix.
REPLACEMENTS = [
    (1, 'raw VQE', '무잡음 VQE'),
    (0, '선별 재료계; runtime/energy 비교 미공개',
     '선별 재료계; DFT 대비 가속·소비에너지 비교 없음'),
    (3, '[동료평가 저널·고전 전자구조] JCTC, DOI 10.1021/acs.jctc.6c01397 | 온라인 2026-10-29 [3]',
     '[동료평가 저널·고전 전자구조] JCTC, DOI 10.1021/acs.jctc.6c01397 | 출판사 목록 2026-10-29 [3]'),
    (3, 'wall-clock·energy·DFT speedup 미공개',
     'SCF 시간 보고; DFT 대비 가속·소비에너지 비교 없음'),
    (0, 'cat-qubit rare-event trajectory를 약 10배 단축',
     'cat-qubit: 같은 정밀도까지 누적 전파시간 약10배 감소'),
    (2, '을 쓴다. noisy emulation에서 finite difference의 error floor를 피했고, compiler selector는 design space의 88.3%에서 더 싼 방식',
     '을 쓴다. noisy emulation에서 finite difference의 error floor를 피했다. 무잡음 7-qubit cost plane에서 selector는 88.3%의'),
    (2, '을 맞혔다. 1,000-qubit structured program에서도 derivative branch 하나의 추가 compilation time은 최대 0.3%였다.',
     'cell에서 더 싼 규칙을 골랐다. 1,000-qubit schedule compiler의 branch당 추가 시간은 최대0.3%였다(펄스 합성 제외).'),
    (4, '면서 Layer I+II가 약 10배, reduced eigenspace가 다시 약 10배를 줄였다. two-mode dissipative cat의 rare bit-flip decay rate는 표',
     '면서 Layer I+II가 약10배, reduced eigenspace가 다시 약10배를 줄였다. two-mode cat의 rare bit-flip rate 추정은'),
    (4, '준 unraveling보다 약 한 자릿수 order 빠르게 계산했다.',
     '20% 정밀도까지 누적 전파시간이 약10배 줄었다(일회성 설정비 제외).'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bitmap(page):
    p = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes('RGB', (p.width, p.height), p.samples)


def reference_list():
    data = json.loads((ROOT / 'reports/reference-manifest.json').read_text())
    rows = data['references']
    if [r['number'] for r in rows] != list(range(1, 7)):
        raise ValueError('References must preserve original scientific first-use order [1]-[6]')
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

    para('DAILY QUANTUM BRIEF / 2026-10-30', 9, 12, after=9, color='#007e8c')
    para('공개 보관본 편집·서지 보완', 18, 24, True, after=8)
    para('원 DQB 5쪽 + 정정 기록·참고문헌 1쪽', 8.6, 12, color='#60717d', after=10)
    para('편집 기록과 결과를 읽는 조건', 10.5, 14, True, color='#007e8c', after=5)
    para('1쪽의 수집 경위와 5쪽의 소셜·내부 작업 메모 및 수집 판정 행을 삭제했다. 간략 서지는 아래 APS 목록으로 옮겼다. 과학 본문의 최초 인용순 [1]-[6]을 유지하며, 수집 확인용 newsroom 목록은 제외했다.')
    para('[1]의 VQE 회로 파라미터는 무잡음 Qiskit statevector로 고전 최적화했다. 2쪽 표의 99.1% ground-space weight와 0.173 eV 에너지 오차는 이 최적화 상태의 결과다. IBM QPU에서는 고정한 LUCJ 회로로 표본을 수집했다. 2쪽 행 이름을 무잡음 VQE로 바꾸어 두 단계를 구분했다.')
    para('[2]의 큰 PAH 자원 추정에서 tensor factorization 오차 1 cm^-1은 작은 분자에서 정한 heuristic proxy다. 큰 계의 실제 에너지 오차에 대한 엄밀한 보장을 뜻하지 않는다. triangular LCU 기준선은 비교 논문의 수치를 그대로 옮긴 것이 아니라 저자들이 구현해 비교한 값이다.')
    para('[4]는 8,194원자 장치에서 Vg=0.73 V일 때 20회 SCF에 약4.14시간(512 Xeon 8375C CPU cores)을 보고했다. overlap 고유분해·<font name="DqbReference">Löwdin</font> 변환의 일회성 설정비는 별도다. 1·4쪽에 SCF 시간 보고와 DFT 대비 가속·소비에너지 비교를 구분해 적었다.')
    para('[5]의 88.3%는 7-qubit의 350개 cost-plane cell에서 무잡음 Hamiltonian-level selector가 더 싼 규칙을 고른 비율이다. 1,000-qubit 결과는 schedule operation·PulseLedger를 만드는 compiler 비용이며 최종 pulse-shape 합성을 제외한다.')
    para('[6]의 cat-qubit 예시에서 약10배 개선은 decay-rate의 20% 정밀도까지 걸린 누적 전파시간이다. 더 많은 궤적이 필요해도 궤적당 계산이 가벼워졌다. 일회성 고유분해·QR 설정비를 제외한 timing으로, 전체 wall-clock을 독립 측정한 값은 아니다.')
    para('참고문헌', 10.5, 14, True, color='#007e8c', after=6)
    for row in references:
        para(f'[{row["number"]}] <link href="{escape(row["url"])}" color="#263a47">{escape(row["citation"])}</link>',
             8.7, 12.4, after=5, font='DqbReference')
    para('책임 편집 김현중 · AI 보조 OpenAI Codex · 근거 기준일 2026-10-30. root: 통합, [3] 공식 초록·출판사 목록·서지와 [4] 전체 17쪽 대조. dqb_20261030_sqd_resources: [1]·[2] 전체 55쪽(통합 SI·부록 포함), 핵심 11쪽 렌더와 선별 코드 대조. dqb_20261030_compiler_trajectories: [5]·[6] 전체 55쪽, 핵심 8쪽 렌더와 선별 코드 대조. [3] 본문·SI, 별도 보충파일·특허는 확인하지 않았다. 코드는 정적으로 읽었으며 실행하지 않았다. dqb_20261030_pdf: 원 DQB 전체 5쪽과 본문·메타데이터·URI·첨부·실행 동작 점검, 공개 사본 제작·일차 렌더 검수. 정확한 실행 모델 식별자와 원 DQB 작성 세션의 에이전트 구성 미보존. AI Tech Review Editorial Harness 2026.08과 현행 문체·APS 기준 적용. 원 논문의 실험·DFT·QPU·학습 재현이나 사람의 문장별 심사는 수행하지 않았다.',
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
    repository = ROOT.parents[1].resolve()
    if args.source_pdf.resolve().is_relative_to(repository):
        raise ValueError('The private source must remain outside the public repository')
    if args.qa_dir.resolve().is_relative_to(repository):
        raise ValueError('QA renders must remain outside the public repository')
    raw = args.source_pdf.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise ValueError('Input is not the reviewed original')
    original = fitz.open(stream=raw, filetype='pdf')
    public = fitz.open(stream=raw, filetype='pdf')
    if len(original) != 5:
        raise ValueError('Expected five source pages')
    edits = {i: list(rects) for i, rects in REMOVALS.items()}
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
        public[index].apply_redactions(images=0, graphics=1 if index == 4 else 0, text=0)
    for index, origin, size, color, new in pending:
        public[index].insert_font(fontname='DqbRegular', fontfile=str(args.font_regular))
        rgb = tuple(((color >> k) & 255) / 255 for k in (16, 8, 0))
        public[index].insert_text(origin, new, fontname='DqbRegular', fontsize=size, color=rgb)
    public[4].insert_font(fontname='DqbRegular', fontfile=str(args.font_regular))
    public[4].insert_text((62.7, 470), '참고문헌 [1]-[6]의 정식 서지와 원문 링크는 다음 쪽에 수록했다.',
                          fontname='DqbRegular', fontsize=9, color=(0, .49, .55))
    references = reference_list()
    note, bottom = appendix(args.font_regular, args.font_bold, args.font_reference, references)
    public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
    public.set_metadata({'title': 'Daily Quantum Brief 2026-10-30 - Public archive edition',
                         'author': 'Research Brief',
                         'subject': 'FeO SQD, vibrational block encoding, multistate DFT, polar Hamiltonians and trajectory simulation',
                         'creator': 'AI Tech Review public archive builder',
                         'creationDate': 'D:20261030000000Z', 'modDate': 'D:20261030000000Z'})
    public.del_xml_metadata()
    public.subset_fonts()
    path = ROOT / 'dist/2026-10-30-daily-quantum-brief.pdf'
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
        'no_private_collection_context': not any(t in text for t in ('수집 범위', 'Gmail', '지난 실행 이후', '연구자·산업계 소셜 신호', '출판 전 검증 메모', 'LinkedIn', '억지로 항목 수를 채우지 않음')),
        'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
        'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
        'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
        'no_embedded_files': final.embfile_count() == 0,
        'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm|GoToR|RichMedia)\b', objects)),
        'expected_reference_links': list(dict.fromkeys(links)) == [r['url'] for r in references],
        'corrected_noiseless_vqe_label': 'raw VQE' not in text and '무잡음 VQE' in text,
        'qpu_sampling_and_classical_optimization_distinguished': '무잡음 Qiskit statevector' in text and '고정한 LUCJ 회로' in text,
        'vibrational_error_proxy_qualified': 'heuristic proxy' in text and '엄밀한 보장' in text,
        'deeph_runtime_and_comparison_distinguished': 'SCF 시간 보고' in text and '4.14시간' in text and '512 Xeon 8375C' in text,
        'publisher_listing_date_attributed': '출판사 목록 2026-10-29' in text,
        'analog_selector_and_compiler_scope_disclosed': '무잡음 7-qubit cost plane' in text and '펄스 합성 제외' in text,
        'trajectory_timing_denominator_disclosed': '20% 정밀도까지 누적 전파시간' in text and '일회성 설정비 제외' in text,
        'collection_only_newsroom_reference_omitted': not any('dwavequantum.com' in uri for uri in links),
        'page_count': len(final) == 6,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / f'public-{i+1}.png'))
    report = {'date': '2026-10-30', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
              'source_pages': 5, 'pages': 6, 'page_checks': checks, 'inspection': predicates,
              'reference_urls': links, 'appendix_bottom_pt': bottom,
              'visual_qa': {'status': 'pending'},
              'metadata': {**final.metadata, 'xml_metadata_empty': not final.get_xml_metadata()},
              'file_size_bytes': path.stat().st_size,
              'independent_qpu_or_training_reproduction': False}
    out = ROOT / 'notes/production-qa.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': path.name, 'pages': len(final), 'sha256': report['sha256'],
                      'appendix_bottom_pt': bottom}))


if __name__ == '__main__':
    main()
