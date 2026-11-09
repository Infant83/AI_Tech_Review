"""Preserve L005's reviewed educational pages in a distinct public edition.

The original is an explicit private input. This command does not execute the
authoring package or regenerate previous units. QA renders remain private.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re

import fitz
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
IDENTIFIER = '2026-11-09-classiq-qae-l005-notes-ko'
TITLE = '샷을 몇 번 쏴야 결과를 믿을 수 있는가'
SOURCE_SHA256 = '17f8fe26e9f77ae0fbc8557b2fa6788a81579fcdaff85689cf316fc2478eeaef'
EDITION_DATE = '2026-11-09'
BASE = 'https://infant83.io/AI_Tech_Review/'
PREVIOUS = {
    '2026-11-03_Classiq_QAE_Lecture02_KO_v1.pdf': '2026-11-03-classiq-qae-l002-notes-ko',
    '2026-11-07_Classiq_QAE_Lecture04_KO_v1.pdf': '2026-11-07-classiq-qae-l004-notes-ko',
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def named_destinations(document):
    # Freeze value copies: named destinations must retain page and coordinates.
    return {name: (value['page'], tuple(value['to']), value.get('zoom', 0))
            for name, value in document.resolve_names().items()}


def internal_link_signature(document):
    return [(index, link['kind'], tuple(link['from']), link.get('page'),
             link.get('nameddest'), tuple(link.get('to', [])), link.get('zoom'))
            for index, page in enumerate(document) for link in page.get_links()
            if link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED)]


def raster(page, scale=1.5):
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def outside_characters(page, regions):
    """Count the original visible characters outside declared edited boxes."""
    result = Counter()
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                for char in span.get('chars', []):
                    box = fitz.Rect(char['bbox'])
                    if not any(box.intersects(fitz.Rect(region)) for region in regions):
                        result[char['c']] += 1
    return result


def replace_line(page, rectangle, text, font, position, size=9.5):
    page.add_redact_annot(rectangle, fill=(1, 1, 1))
    page.apply_redactions(images=0, graphics=0)
    page.insert_font(fontname='PublicNanum', fontfile=str(font))
    page.insert_text(position, text, fontname='PublicNanum', fontsize=size,
                     color=(.12, .25, .30))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--qa-dir', type=Path, required=True)
    args = parser.parse_args()
    assert sha256(args.source) == SOURCE_SHA256, 'Unexpected source PDF edition'
    original, doc = fitz.open(args.source), fitz.open(args.source)
    assert len(original) == 17
    original_names = named_destinations(original)
    original_internal_links = internal_link_signature(original)
    original_uris = [link['uri'] for page in original for link in page.get_links() if 'uri' in link]
    regions = {i: [] for i in range(17)}

    # Generalize personal background without altering the scientific comparison.
    cover_context = fitz.Rect(58, 774, 537, 792)
    replace_line(doc[0], cover_context,
                 '이 과정의 SCM은 계산화학 회사와 AMS/ADF를 뜻한다.', args.font,
                 (59.528, 785.197))
    regions[0].append(list(cover_context))

    # The five prerequisite links now open public HTTPS PDFs, not local files.
    prerequisite_note = fitz.Rect(309, 123, 452, 138)
    replace_line(doc[1], prerequisite_note, '이전 PDF는 웹 링크로 연다.', args.font,
                 (309.956, 134.197), size=9.2)
    regions[1].append(list(prerequisite_note))

    cover_note = fitz.Rect(59, 536, 536, 634)
    doc[0].insert_font(fontname='PublicNanum', fontfile=str(args.font))
    note = ('공개 보관본 · 2026-11-09\n'
            'Agentic Tech Review Letters (ATRL)\n'
            'Classiq 공식 강의가 아닌 독립 학습 과정이다.\n'
            '원판 교육 내용과 이번 공개 검수의 범위는 마지막 쪽에서 구분한다.')
    assert doc[0].insert_textbox(cover_note, note, fontname='PublicNanum', fontsize=9.5,
                               lineheight=1.5, color=(.10, .30, .35)) >= 0
    regions[0].append(list(cover_note))

    rewritten = []
    for index, page in enumerate(doc):
        for link in page.get_links():
            if link['kind'] not in (fitz.LINK_LAUNCH, fitz.LINK_GOTOR):
                continue
            filename, sep, fragment = link.get('file', '').partition('#')
            assert filename in PREVIOUS, 'Unreviewed external file link'
            previous_id = PREVIOUS[filename]
            previous = fitz.open(REPO / 'archive/files' / (previous_id + '.pdf'))
            if sep:
                assert fragment.startswith('nameddest=')
                destination = fragment.removeprefix('nameddest=')
                assert destination in previous.resolve_names(), 'Missing prerequisite destination'
            else:
                assert link['kind'] == fitz.LINK_GOTOR and link.get('page') == 0
            uri = BASE + 'archive/files/' + previous_id + '.pdf' + ('#' + fragment if sep else '')
            page.delete_link(link)
            page.insert_link({'kind': fitz.LINK_URI, 'from': link['from'], 'uri': uri})
            rewritten.append({'page': index + 1, 'uri': uri, 'destination_verified': True})
    assert len(rewritten) == 5

    appendix = doc.new_page(width=595.276, height=841.89)
    appendix.insert_font(fontname='PublicNanum', fontfile=str(args.font))
    assert appendix.insert_textbox(fitz.Rect(55, 58, 540, 110), 'L005 · 공개판 안내와 확인 범위',
                                  fontname='PublicNanum', fontsize=19, color=(.08, .21, .29)) >= 0
    disclosure = (
        'Agentic Tech Review Letters (ATRL) · 공개 보관본 · 2026-11-09\n'
        '책임 편집자 김현중 · AI 보조 OpenAI Codex\n\n'
        '자료 성격\n'
        '공개 교재·공식 문서에 근거해 자체 집필한 한국어 독립 학습 과정이다. '
        '공식 Classiq 강의·인증 과정이나 Classiq의 승인을 받은 자료로 표시하지 않는다. '
        'QAE는 Quantum Application Engineer이며 진폭 추정 알고리즘 AE/IQAE와 구별한다.\n\n'
        '원판과 공개본\n'
        '2026-11-09 v1.0의 교육 내용 17쪽, 수식·도표·8개 자습문제와 해설·용어색인·참고문헌 및 '
        '원래 쪽번호를 보존했다. 개인화된 배경 표현을 일반화하고 메타데이터를 정리했다. '
        '선수 개념과 이전 회차로 이동하는 파일 링크 5개는 공개 HTTPS PDF와 확인한 정의 목적지로 바꾸었다. '
        '개인 메일·원문 수집 파일·운영 기록과 제3자 교재 원문은 이 공개 PDF에 포함하지 않는다.\n\n'
        '검산과 확인 범위\n'
        '본문의 Python 3.12.14·NumPy 2.3.5 및 57개 이름 붙인 고전 검사는 원판 제작자의 수행 기록이다. '
        '이번 공개판 작업은 그 검사 전체나 Classiq 예제를 새로 실행한 기록이 아니다. '
        '이번에는 교육 페이지의 문자·내부 목적지·원 공개 URI를 대조하고, 명시한 편집 영역 밖의 전 페이지 '
        '렌더링 동일성, 개인정보·메타데이터·링크 동작과 실제 조판을 검사했다. '
        '원판과 이번 공개판 모두 실제 Classiq SDK·합성·클라우드 backend·QPU·실물 DFT/분자 계산이나 사람의 원고 감수를 '
        '수행한 것으로 표시하지 않는다. 원판 소스 ZIP도 공개 배포하지 않는다.\n\n'
        '작성·검수 공개\n'
        '원판의 자료 열람·과학 검토·실제 고전 계산 범위는 각 본문과 참고문헌에 남은 제작 기록을 따른다. '
        '이번 공개판의 정제·페이지 보존·링크 및 조판 검수는 qae_l005_public이 수행하고 root가 '
        '통합·등록·게시한다. 이번에 원 교재·논문 전체를 새로 읽거나 원판 수치 검증을 모두 재현한 '
        '것으로 소급 표시하지 않는다.\n\n'
        '공개 학습 입구와 후속 회차\n'
        'infant83.io/AI_Tech_Review/lectures/classiq-qae-onboarding/\n'
        '회차별 공개판과 필기 링크는 같은 시리즈 목록에서 제공한다.\n\n'
        '편집·출처 기준: AI Tech Review Editorial Harness 2026.08 · APS 인용 기준 · 과학 설명 준칙'
    )
    assert appendix.insert_textbox(fitz.Rect(55, 119, 540, 785), disclosure,
                                  fontname='PublicNanum', fontsize=10.1, lineheight=1.5,
                                  color=(.12, .20, .25)) >= 0
    web = appendix.search_for('infant83.io/AI_Tech_Review/lectures/classiq-qae-onboarding/')[0]
    appendix.insert_link({'kind': fitz.LINK_URI, 'from': web,
                         'uri': BASE + 'lectures/classiq-qae-onboarding/'})
    doc.set_metadata({'title': 'Classiq QAE L005 · ' + TITLE + ' · 공개 보관본',
                      'author': '김현중', 'creator': 'Agentic Tech Review Letters (ATRL); OpenAI Codex-assisted archive',
                      'subject': 'Independent Korean study notes; public edition 2026-11-09'})
    doc.del_xml_metadata()
    doc.xref_set_key(doc.pdf_catalog(), 'OpenAction', 'null')
    doc.update_object(doc.pdf_catalog(), re.sub(r'\s*/OpenAction\s+null\b', '', doc.xref_object(doc.pdf_catalog())))
    doc.subset_fonts()
    output = ROOT / 'output/pdf' / (IDENTIFIER + '.pdf')
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output, garbage=4, deflate=True, clean=True)
    final = fitz.open(output)
    assert len(final) == 18
    assert named_destinations(final) == original_names
    assert internal_link_signature(final) == original_internal_links
    characters_preserved = []
    for index in range(17):
        assert outside_characters(original[index], regions[index]) == outside_characters(final[index], regions[index]), ('Character change', index + 1)
        characters_preserved.append(index + 1)
        diff = ImageChops.difference(raster(original[index]), raster(final[index]))
        mask = ImageDraw.Draw(diff)
        for x0, y0, x1, y1 in regions[index]:
            mask.rectangle((math.floor(x0 * 1.5) - 3, math.floor(y0 * 1.5) - 3,
                            math.ceil(x1 * 1.5) + 3, math.ceil(y1 * 1.5) + 3), fill='black')
        assert diff.getbbox() is None, ('Unexpected rendering change', index + 1, diff.getbbox())
    assert all(uri in [link.get('uri') for page in final for link in page.get_links()] for uri in original_uris)
    objects = '\n'.join(final.xref_object(i) for i in range(1, final.xref_length()))
    text = '\n'.join(page.get_text() for page in final)
    assert final.embfile_count() == 0
    assert not re.search(r'/S\s*/(?:Launch|JavaScript)|/OpenAction\b|/EmbeddedFile\b|/(?:Users|home|private)/|mailto:|chatgpt\.com/share/', objects)
    assert not re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text + objects)
    assert not any(term in re.sub(r'\s+', '', text) for term in ['사용자배경의', '같은폴더에두어야'])
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for index, page in enumerate(final):
        raster(page, 1.15).save(args.qa_dir / f'L005-page-{index + 1:02d}.png')
    dist = ROOT / 'dist' / output.name
    dist.write_bytes(output.read_bytes())
    record = {'unit': 'L005', 'date': '2026-11-09', 'title': TITLE,
              'source_pages': 17, 'public_pages': 18, 'source_sha256': SOURCE_SHA256,
              'public_sha256': sha256(output), 'file': output.name,
              'redaction_and_added_regions': {str(i + 1): boxes for i, boxes in regions.items() if boxes},
              'rewritten_links': rewritten, 'unchanged_original_page_regions_pixel_equal': True,
              'original_page_characters_outside_edits_preserved': characters_preserved,
              'internal_named_destinations_preserved': len(original_names),
              'internal_link_annotations_preserved': len(original_internal_links),
              'original_public_uris_preserved': len(original_uris),
              'embedded_files': 0, 'launch_or_script_actions': 0}
    report = {'date': EDITION_DATE, 'units': [record], 'source_zip_in_public_bundle': False,
              'original_validation_suite_rerun': False, 'original_checks_recorded': 57,
              'public_preparation_scope': 'Preservation, privacy, metadata, cross-PDF destinations and full-page rendering; no new SDK or physical experiment'}
    (ROOT / 'reports/pdf-L005-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'unit': 'L005', 'pages': 18, 'sha256': record['public_sha256'],
                      'named_destinations': len(original_names), 'rewritten_links': len(rewritten)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
