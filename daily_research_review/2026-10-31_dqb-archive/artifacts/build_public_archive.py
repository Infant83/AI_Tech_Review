"""Build the reviewed public edition of the 2026-10-31 DQB.

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
SOURCE_SHA256 = 'c46bee84e6cc4e285bcbcf8313ccc5d1c7e34d5c058452575092d8f9e8692cf9'
REMOVALS = {0: [(61, 491, 546, 530)], 2: [(61, 437, 546, 475)],
            4: [(61, 446, 546, 594)]}
# Exact science-line prefixes identify the reviewed source. Privacy-only
# collection blocks are addressed by rectangles, never copied into this file.
REPLACEMENTS = [
    (0, 'VULCAN은 ADAPT-VQE의 Hamiltonian-gradient',
     'VULCAN의 주요 GPU 모사 비교는 ADAPT-VQE 대비 측정비용 5–20%를 보고했다. 32q C₃H₆에는 ENPT2가 필요했고, 별도의 H₂ 분자'),
    (0, '는 GPU statevector emulation이며,',
     '장치 예비실행도 보고됐다. Quntur는 32개 excitation gap에서 최선 ASF보다 MAE가 48% 낮았으나 4개 transition의 state character는'),
    (0, 'CASSCF workflow는 32개 singlet excitation',
     'reference와 달랐다. 기본 32개 session의 ORCA job은 사례당 1–15개였고, 두 질문의 반복 평가에서는 5–20개 job과'),
    (0, '31.6–236.6분의 실행 변동이 있었다.',
     '31.6–236.6분의 실행시간 변동이 있었다. 주요 자원 비교와 장치 예비실행, 숫자 일치와 상태 검증을 구분해 읽는다.'),
    (0, '실제 QPU 없음; GPU statevector·ENPT2 사용',
     'GPU 자원 비교; H₂ 장치 예비보고 별도'),
    (1, '124큐비트는 cc-pVTZ Be',
     '124큐비트 회로는 cc-pVTZ Be₂의 60 spatial orbital에 해당하는 120 data qubit와 4개 ancilla를 사용했다.'),
    (1, 'Be\x00 cc-pVDZ에서 VGSQD는 CCSD(T)',
     'Be₂ cc-pVDZ에서 VGSQD는 CCSD(T)의 2.611 Å보다 실험2.460 Å에 가까운 2.555 Å를 얻었다. cc-pVTZ는 SQD -29.2486 Ha로'),
    (3, 'VULCAN은 Variational Double Bracket Flow로',
     'VULCAN은 Variational Double Bracket Flow로 얻은 연산자와 minimal complete pool을 결합해 전체 pool을 layer로 붙여'),
    (3, 'ADAPT-VQE의 후보별 Hamiltonian-gradient',
     'ADAPT-VQE의 후보 선택용 Hamiltonian-gradient 측정을 없앤다. overlap gradient로 layer를 압축하고, determinant-generated'),
    (3, '측정비용은 circuit execution count의 모델이며',
     '측정비용은 누적 Pauli-term 평가 수의 모델이며 실제 shots·grouping·queue·error mitigation을 포함한 QPU wall-clock과 다르다.'),
    (3, '아니다. 모든 실험은 Hyperion GPU',
     '주요 자원 비교는 Hyperion GPU statevector 모사이고 integral은 OpenFermion-PySCF, mapping은 Jordan–Wigner를 사용했다.'),
    (3, '다. 32 logical qubits라는 수치는',
     '32q C₃H₆ 결과는 고전 모사이며, 별도의 H₂ 분자 Quantinuum 장치 예비실행과 구분한다.'),
    (3, 'GPT-5.6 Sol/Terra 기반 multi-agent harness',
     'gpt-5.6-sol / gpt-5.6-terra 기반 multi-agent harness가 orbital evidence, state character, failed calculation을 검토하며'),
    (3, '비용과 공정성은 따로 봐야 한다.',
     'Quntur의 32개 기본 session은 ORCA job 219개(사례당 1–15개)를 사용했다. 두 질문을 각각 4회 반복한 평가에서는 job 수가 5–20개,'),
    (3, '제출했다. 두 질문을 4회 반복했을 때',
     'wall-clock이 31.6–236.6분으로 달랐고 excitation gap 변동은 0.005 eV 이내였다. 최선 ASF와 Quntur는 모두 32개 gap을 보고했으며'),
    (3, '는 고정 protocol이고 실패에는',
     '48% MAE 차이는 양쪽의 실제 gap 기준이다. Quntur의 4개 transition은 reference와 state character가 달라 숫자 일치와'),
    (3, '으로 유지됐다. 정확도 향상은',
     '상태 검증을 구분해야 한다. 두 방법의 계산 budget도 같지 않다.'),
    (4, 'syndrome extraction의 nonlinear processing이',
     'syndrome extraction의 nonlinear processing이 이를 구분한다. 대가로 physical signal ε는 평균 logical phase φL=O(ε³)로 약'),
]


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


def restore(text):
    # Each lost glyph is resolved from the cited primary paper, not guessed.
    for old, new in [('9.6×10\x00', '9.6×10⁷'), ('BeH\x00', 'BeH₂'),
                     ('Be\x00', 'Be₂'), ('H\x00O', 'H₂O'),
                     ('C\x00H\x00', 'C₃H₆'), ('H\x00\x00', 'H₁₀'),
                     ('H\x00 0.18', 'H₈ 0.18'), ('H\x00', 'H₃')]:
        text = text.replace(old, new)
    text = text.replace('총자화 M\x00와 위치가중 자화 M\x00', '총자화 M₀와 위치가중 자화 M₁')
    # Keep the tiny original table within its existing column at the same size.
    text = text.replace('256k shots/reference', '256k shots/ref')
    return text


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


def appendix(regular, bold, reference_font, references):
    for name, path in [('DqbRegular', regular), ('DqbBold', bold), ('DqbReference', reference_font)]:
        pdfmetrics.registerFont(TTFont(name, str(path)))
    out = io.BytesIO()
    c = Canvas(out, pagesize=A4, invariant=1)
    w, h = A4
    y = h - 43

    def mixed(text):
        # ReportLab does not choose fallback fonts automatically.
        face = pdfmetrics.getFont('DqbRegular').face
        return ''.join(escape(ch) if ord(ch) in face.charToGlyph else
                       f'<font name="DqbReference">{escape(ch)}</font>' for ch in text)

    def para(text, size=9.7, leading=14.4, strong=False, after=6, color='#263a47', ref=False):
        nonlocal y
        style = ParagraphStyle('p', fontName='DqbReference' if ref else ('DqbBold' if strong else 'DqbRegular'),
                               fontSize=size, leading=leading, textColor=HexColor(color), wordWrap='CJK')
        p = Paragraph(text if ref else mixed(text), style)
        _, height = p.wrap(w - 110, h)
        y -= height
        p.drawOn(c, 55, y)
        y -= after

    para('DAILY QUANTUM BRIEF / 2026-10-31', 9, 12, after=7, color='#007e8c')
    para('공개 보관본 편집·서지 보완', 18, 24, True, after=6)
    para('원 DQB 5쪽 + 정정 기록·참고문헌 1쪽', 8.6, 12, color='#60717d', after=9)
    para('편집 기록과 결과를 읽는 조건', 10.5, 14, True, color='#007e8c', after=5)
    para('수집·메일·소셜 경위와 내부 메모를 삭제하고, 원제·전 저자·판본을 갖춘 APS 서지를 본문 최초 인용순 [1]-[5]로 수록했다. 손상된 분자식·지수·자화 첨자는 원전과 대조해 복원했다. 원 논문 PDF·도판은 재배포하지 않는다.')
    para('[1] Be₂의 60 spatial orbital은 120 data qubit에 해당하며 회로는 ancilla 4개를 더 쓴다. LUCJ의 CCSD 초기 파라미터는 추가 최적화하지 않았다. 최대 9.6×10⁷ determinant의 고전 계산에는 총378 vCPU·14노드(노드당230 GB)가 쓰였다. 최적 구조의 -29.2485 Ha(원 Table III)와 고정 R=2.385 Å의 -29.2486 Ha(Fig. 2)는 서로 다른 비교다. H₃ NEB는 image별 최초 표본을 재사용했고 image 간 공유는 제안 단계다.')
    para('[2] 두 자화는 M₀=Σsᵢ와 M₁=Σi sᵢ다. 5 ns anneal-time 매칭은 N=5-12에서 보고됐다. 성공률은 깨진 chain을 버리고 fast anneal에서 잘못 고정된 ancilla도 제외한 유효 표본에 조건부로 계산했다.')
    para('[3] 주요 비교는 무잡음 GPU statevector 모사다. 0.05%는 H₂O 26q의 한 layer+ENPT2 seed 비용을 ADAPT-QEB 누적 Pauli-term 평가 수와 비교한 값이며 고전 ENPT2 계산비용은 제외한다. ENPT2 분모 표본 비율 약0.0025-0.01%와 구분한다. C₃H₆ 32q ENPT2는 H100 한 장에서 11.8시간이며, 별도 H₂ 분자 장치 예비실행이 보고됐다. 별도 SI는 확보하지 못했다.')
    para('[4] 기본32사례와 두 질문의 반복실행 비용을 구분해 바로잡았다. MAE0.239 대0.459 eV는 양쪽32개 gap의 비교다. Quntur의 4개 transition은 reference와 다른 state character를 가져, 수치 일치만으로 모든 상태의 정확성을 확정할 수 없다. 잘못 적힌 원저자명을 아래에서 정정했다.')
    para('[5] ε³은 평균 논리 위상의 차수로 명확히 했다. 알려진 Poisson rate R에서 pulse area ε를 추정하는 이론·수치 모형이며, 약한 collective pulse·local Markov noise와 γ≫R 조건을 쓴다. Steane 예시는 완전한 syndrome 추출, gate-level noise 부재, σₜ≪δt≪1/(2γ)와 충분한 관측을 가정한다.')
    para('참고문헌', 10.5, 14, True, color='#007e8c', after=5)
    for row in references:
        para(f'[{row["number"]}] <link href="{escape(row["url"])}" color="#263a47">{escape(row["citation"])}</link>',
             9.2, 13.1, after=5, ref=True)
    para('책임 편집 김현중 · AI 보조 OpenAI Codex · 근거 기준일2026-10-31. root: [1] 전체19쪽과 핵심6쪽 렌더. dqb1031_chemistry: [3]20쪽·[4]통합 SI 포함51쪽 전체와 핵심12쪽 렌더. dqb1031_optimization_sensing: [2]27쪽·[5]본문7쪽+SM8쪽 전체와 핵심8쪽 렌더. dqb1031_pdf: 원 DQB5쪽·최종6쪽, 개인정보·PDF구조·일차 렌더 점검. 외부 코드·데이터 전체를 감사·실행하지 않았다. 정확한 실행 모델 식별자와 원 DQB 작성 에이전트 구성 미보존. 현행 편집·과학 설명·문체·APS 기준 적용. 논문의 실험·QPU·ORCA·benchmark 독립 재현이나 사람 독자 평가는 수행하지 않았다.',
         8.0, 11.4, color='#60717d', after=0)
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
    for flag in ('source-pdf', 'font-regular', 'font-bold', 'font-reference', 'qa-dir'):
        p.add_argument('--' + flag, required=True, type=Path)
    args = p.parse_args()
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
            right = 542 if x < 100 else (367.5 if x < 200 else 542)
            if x + width > right:
                raise ValueError(f'Page {index+1} line at {y}: right {x+width:.2f} exceeds {right}: {text}')
            # Mask both old and actual new glyph extents. Font size is preserved.
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
        public[index].apply_redactions(images=0, graphics=1 if index == 4 else 0, text=0)
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
    public[4].insert_text((62.7, 470), '편집 정정·조건 보완과 참고문헌 [1]-[5]의 정식 서지는 다음 쪽에 수록했다.',
                          fontname='DqbRegular', fontsize=9, color=(0, .49, .55))
    references = reference_list()
    note, bottom = appendix(args.font_regular, args.font_bold, args.font_reference, references)
    public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
    public.set_metadata({'title': 'Daily Quantum Brief 2026-10-31 - Public archive edition',
                         'author': 'Research Brief', 'subject': 'Variable-geometry SQD, Ising benchmarks, variational chemistry, scientific agents and rare-event sensing',
                         'creator': 'AI Tech Review public archive builder',
                         'creationDate': 'D:20261031000000Z', 'modDate': 'D:20261031000000Z'})
    public.del_xml_metadata()
    public.subset_fonts()
    cmap_destinations_normalized = normalize_to_unicode(public)
    path = ROOT / 'dist/2026-10-31-daily-quantum-brief.pdf'
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
        'no_private_collection_context': not any(t in text for t in ('수집 범위', 'Gmail', 'D-Wave 메일 점검', '연구자·산업계 소셜 신호', '출판 전 검증 메모', 'LinkedIn', 'webinar')),
        'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
        'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
        'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
        'no_xml_metadata': not final.get_xml_metadata(),
        'no_embedded_files': final.embfile_count() == 0,
        'no_widgets': not any(list(page.widgets() or []) for page in final),
        'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm|GoToR|RichMedia)\b', objects)),
        'expected_reference_links': list(dict.fromkeys(links)) == [r['url'] for r in references],
        'verified_glyphs_restored': all(s in text for s in ('9.6×10⁷', 'Be₂', 'H₂O', 'H₃', 'C₃H₆', 'M₀', 'M₁')),
        'vulcan_main_simulation_and_device_exception': '주요 자원 비교는 Hyperion GPU statevector' in text and 'H₂ 분자 Quantinuum 장치 예비실행' in text,
        'quntur_scope_and_state_identity': 'ORCA job 219개' in text and '4개 transition' in text,
        'mean_logical_phase_qualified': '평균 logical phase' in text,
        'page_count': len(final) == 6,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / f'public-{i+1}.png'))
    report = {'date': '2026-10-31', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
              'source_pages': 5, 'pages': len(final), 'page_checks': checks, 'inspection': predicates,
              'reference_urls': links, 'appendix_bottom_pt': bottom, 'visual_qa': {'status': 'pending'},
              'metadata': final.metadata, 'file_size_bytes': path.stat().st_size,
              'non_bmp_cmap_destinations_normalized': cmap_destinations_normalized,
              'independent_reproduction': False}
    (ROOT / 'notes/production-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': path.name, 'pages': len(final), 'sha256': report['sha256'], 'appendix_bottom_pt': bottom}))


if __name__ == '__main__':
    main()
