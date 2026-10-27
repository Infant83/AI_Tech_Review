"""Make the explicitly reviewed six-page public edition of the 2026-10-27 DQB.

The caller supplies the private original and fonts. This builder never registers
or publishes files. It removes the collection-route paragraph, moves references
to a complete APS list, and adds source-checked reading conditions and a record.
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
SOURCE_SHA256 = '80bc40ea139508772312b6101c08accc25d3d36df9c4f8ce234e0a8a2ee64639'
EDITS = {0: [(61, 575.5, 535, 639)], 4: [(61, 621, 535, 704)]}
REFERENCES = [
 ('R. Harper, X. C. Kolesnikow, C. K. McLauchlan, G. M. Nixon, S. D. Bartlett, and B. J. Brown, Entangled logical qubits on a superconducting quantum processor, arXiv:2610.32347v1.', 'https://arxiv.org/abs/2610.32347v1'),
 ('S. Monaco, J. Slim, R. Xue, D. Krücker, and K. Borras, Classical pre-training of large shallow parametrized quantum circuits through Pauli propagation and deployment on quantum hardware, arXiv:2610.32571v1.', 'https://arxiv.org/abs/2610.32571v1'),
 ('P. Kammerlander et al., The compendium of super-quadratic computational quantum advantages, arXiv:2610.32595v1.', 'https://arxiv.org/abs/2610.32595v1'),
 ('J. Cotler, D. L. Danielson, and I. Kannan, Quantum advantage for sensing properties of classical fields, Phys. Rev. X 16, 041025 (2026).', 'https://doi.org/10.1103/6ps1-mw9l'),
 ('A. Erhard, G. Jacob, M. Hettrich, P. C. Holz, J. Ulmanis, and T. Feldker, LYNX - A trapped-ion quantum information processor, arXiv:2610.32518v1.', 'https://arxiv.org/abs/2610.32518v1'),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bitmap(page):
    p = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes('RGB', (p.width, p.height), p.samples)


def appendix(regular, bold):
    pdfmetrics.registerFont(TTFont('DqbRegular', str(regular)))
    pdfmetrics.registerFont(TTFont('DqbBold', str(bold)))
    out = io.BytesIO()
    c = Canvas(out, pagesize=A4, invariant=1)
    w, h = A4
    y = h - 52
    def para(text, size=9.3, leading=14, strong=False, after=8, color='#263a47', font=None):
        nonlocal y
        style = ParagraphStyle('p', fontName=font or ('DqbBold' if strong else 'DqbRegular'),
                               fontSize=size, leading=leading, textColor=HexColor(color), wordWrap='CJK')
        p = Paragraph(text, style)
        _, height = p.wrap(w - 110, h)
        y -= height
        p.drawOn(c, 55, y)
        y -= after
    para('DAILY QUANTUM BRIEF / 2026-10-27', 9, 12, after=12, color='#007e8c')
    para('공개 보관본 편집·서지 보완', 19, 25, True, after=10)
    para('원 DQB 5쪽 + 편집 기록·참고문헌 1쪽', 9, 13, color='#60717d', after=14)
    para('편집 기록', 11, 15, True, color='#007e8c', after=5)
    para('1쪽의 메일·검색 수집 경위 문단을 실제 삭제했다. 5쪽의 불완전한 서지 목록을 아래 APS 번호 목록으로 옮겨 원저자와 원제를 보완했다. 프리프린트는 확인한 v1에 연결하고, [4]의 잘못된 원문 링크를 정식 DOI 10.1103/6ps1-mw9l로 바로잡았다. 원 과학 본문·표·수치·쪽번호는 보존했다.')
    para('결과를 읽을 조건', 11, 15, True, color='#007e8c', after=5)
    para('[1]의 논리 메모리 오류율 1% 미만은 본문에서 보고한 선택된 배치·기저의 결과다. 부록 C의 Y-memory에는 1.690%도 보고되어 모든 기저의 보장으로 읽지 않는다. Teleportation의 상태 tomography와 게이트 process tomography도 구별한다.')
    para('[2]의 Table I에 있는 MMD² 점수 2.05±0.18 ×10⁻³은 잘린 고전 Pauli propagator로 계산한 기대값에서 평가했다. 3쪽의 약 12배 비교는 이 평가에 관한 것이며 QPU 생성 이미지에서 실측한 MMD²가 아니다. 실제 QPU 이미지 표본은 별도로 제시됐다(§III.2).')
    para('참고문헌', 11, 15, True, color='#007e8c', after=7)
    for n, (text, url) in enumerate(REFERENCES, 1):
        para(f'[{n}] <link href="{escape(url)}" color="#263a47">{escape(text)}</link>', 8.8, 12.7, after=7, font='Helvetica')
    para('책임 편집 김현중 · AI 보조 OpenAI Codex · 근거 기준일 2026-10-27. root: 원문 서지·출력·공개 등록 검토; dqb_20261027_research: 논리 연산·고전 사전학습의 독립 원문 대조와 후속 기획. 정확한 실행 모델 식별자 미보존. AI Tech Review Editorial Harness 2026.08과 현행 문체·APS 감사 기준 적용. 원 논문의 QPU 실험·대규모 학습을 독립 재현하거나 사람의 문장별 감수를 수행한 것은 아니다.', 7.5, 11, color='#60717d', after=0)
    if y < 59:
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
    p.add_argument('--qa-dir', required=True, type=Path)
    args = p.parse_args()
    raw = args.source_pdf.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise ValueError('Input is not the reviewed original')
    original = fitz.open(stream=raw, filetype='pdf')
    public = fitz.open(stream=raw, filetype='pdf')
    assert len(original) == 5
    for index, rects in EDITS.items():
        page = public[index]
        for rect in rects:
            page.add_redact_annot(fitz.Rect(rect), fill=None)
        page.apply_redactions(images=0, graphics=0, text=0)
    public[4].insert_font(fontname='DqbRegular', fontfile=str(args.font_regular))
    public[4].insert_text((62.7, 636), '참고문헌 [1]–[5]의 정식 서지와 원문 링크는 다음 쪽에 수록했다.',
                          fontname='DqbRegular', fontsize=9, color=(0, .49, .55))
    note, bottom = appendix(args.font_regular, args.font_bold)
    public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
    public.set_metadata({'title': 'Daily Quantum Brief 2026-10-27 - Public archive edition',
                         'author': 'Research Brief', 'subject': 'Logical entanglement and classical pre-training of quantum circuits',
                         'creator': 'AI Tech Review public archive builder'})
    public.del_xml_metadata()
    public.subset_fonts()
    path = ROOT / 'dist/2026-10-27-daily-quantum-brief.pdf'
    path.parent.mkdir(parents=True, exist_ok=True)
    public.save(path, garbage=4, deflate=True, no_new_id=True)
    final = fitz.open(path)
    checks = []
    for i in range(5):
        diff = ImageChops.difference(bitmap(original[i]), bitmap(final[i]))
        for rect in EDITS.get(i, []):
            x0, y0, x1, y1 = rect
            ImageDraw.Draw(diff).rectangle((math.floor((x0-1)*2), math.floor((y0-1)*2), math.ceil((x1+1)*2), math.ceil((y1+1)*2)), fill=(0, 0, 0))
        if diff.getbbox() is not None:
            raise ValueError(f'Unexpected pixel change on page {i+1}')
        checks.append({'page': i+1, 'pixels_identical_outside_declared_edits_144dpi': True, 'edit_rectangles': EDITS.get(i, [])})
    text = '\n'.join(page.get_text() for page in final)
    objects = '\n'.join(final.xref_object(x, compressed=False) for x in range(1, final.xref_length()))
    links = [a['uri'] for page in final for a in page.get_links() if 'uri' in a]
    predicates = {
        'no_private_collection_context': not any(t in text for t in ('수집 범위', 'Gmail', '지난 실행 이후')),
        'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
        'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
        'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
        'no_embedded_files': final.embfile_count() == 0,
        'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm)\b', objects)),
        'expected_reference_links': list(dict.fromkeys(links)) == [u for _, u in REFERENCES],
        'corrected_doi': '9lsm-lzwq' not in text + objects and '6ps1-mw9l' in text,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / f'public-{i+1}.png'))
    report = {'date': '2026-10-27', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
              'source_pages': 5, 'pages': 6, 'page_checks': checks, 'inspection': predicates,
              'reference_urls': links, 'appendix_bottom_pt': bottom,
              'visual_qa': {'status': 'pending'}, 'independent_qpu_or_training_reproduction': False}
    out = ROOT / 'notes/production-qa.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': path.name, 'pages': len(final), 'sha256': report['sha256'], 'appendix_bottom_pt': bottom}))


if __name__ == '__main__':
    main()
