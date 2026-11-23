# -*- coding: utf-8 -*-
"""Preserve L014's reviewed educational pages in a distinct public edition.

The original is an explicit private input. This command does not execute the
authoring package or regenerate previous units. QA renders remain private.
"""
import argparse
from collections import Counter
import hashlib
import html
import json
import math
from pathlib import Path
import re

import fitz
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
IDENTIFIER = '2026-11-23-classiq-qae-l014-notes-ko'
TITLE = '회로를 얕게 만들면 계산 비용도 줄어드는가'
EDITION_DATE = '2026-11-23'
BASE = 'https://infant83.io/AI_Tech_Review/'
PREVIOUS = {
    '2026-11-13_Classiq_QAE_Lecture07_KO_v1.pdf': '2026-11-13-classiq-qae-l007-notes-ko',
    '2026-11-22_Classiq_QAE_Lecture13_KO_v1.pdf': '2026-11-22-classiq-qae-l013-notes-ko',
}
INDEPENDENT_CHECKS = 41
INDEPENDENT_SCOPE_KO = ('깨끗한 작업공간의 기저·복소 상태 계약과 더러운 보조선의 작용, CCX·CZ의 정확 분해·위상·자원 집계, ' 'ASAP·DAG 깊이와 폭·Pareto 후보, 13CX 경로와 SWAP을 대조했다. 연산자 오차·TV 경계와 합성 전체시간·재사용의 작은 예시를 별도 계산하고, SDK 예제에는 AST 문법 확인만 적용했다.')
INDEPENDENT_SCOPE_EN = ('Python3.9.6 stdlib:41 independently written named conditions; full clean/dirty-workspace basis maps and complex states, exact CCX/CZ phase/decomposition/resource counts, ASAP/DAG scheduling, width/Pareto,13CX routing/SWAP, operator telescope/TV bounds, synthetic whole-time/reuse ledgers and SDK example AST only. Original30-check suite and source-author reproduction runs not rerun. No SDK import/model/synthesis/metric request/backend/QPU/actual materials or human manuscript review.')



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
    parser.add_argument('--expected-source-sha256', required=True,
                        help='Expected edition digest from the private intake record')
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--qa-dir', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{64}', args.expected_source_sha256):
        parser.error('Expected source SHA-256 must contain 64 lowercase hexadecimal characters')
    if sha256(args.source) != args.expected_source_sha256:
        raise ValueError('Unexpected source PDF edition')
    original, doc = fitz.open(args.source), fitz.open(args.source)
    assert len(original) == 15
    original_names = named_destinations(original)
    original_internal_links = internal_link_signature(original)
    original_uris = [link['uri'] for page in original for link in page.get_links() if 'uri' in link]
    regions = {i: [] for i in range(15)}

    # Remove only the wrapped local-file instruction, keeping adjacent definitions.
    instruction_head = fitz.Rect(454.3, 157.9, 536.1, 170.1)
    doc[1].add_redact_annot(instruction_head, fill=(1, 1, 1))
    doc[1].apply_redactions(images=0, graphics=0)
    regions[1].append(list(instruction_head))
    instruction_tail = fitz.Rect(59.0, 172.4, 221.0, 185.2)
    replace_line(doc[1], instruction_tail, '이전 PDF는 웹 링크로 연다.', args.font,
                 (59.528, 181.89), size=10.1)
    regions[1].append(list(instruction_tail))

    cover_note = fitz.Rect(59, 480, 536, 580)
    doc[0].insert_font(fontname='PublicNanum', fontfile=str(args.font))
    note = ('공개 보관본 · 2026-11-23\n'
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
    assert len(rewritten) == 8

    appendix = doc.new_page(width=595.276, height=841.89)
    appendix.insert_font(fontname='PublicNanum', fontfile=str(args.font))
    assert appendix.insert_textbox(fitz.Rect(55, 58, 540, 110), 'L014 · 공개판 안내와 확인 범위',
                                  fontname='PublicNanum', fontsize=19, color=(.08, .21, .29)) >= 0
    disclosure = (
        'Agentic Tech Review Letters (ATRL) · 공개 보관본 · 2026-11-23\n'
        '책임 편집자 김현중 · AI 보조 OpenAI Codex\n\n'
        '자료 성격\n공개 교재·공식 문서에 근거해 자체 집필한 한국어 독립 학습 과정이다. '
        '공식 Classiq 강의·인증 과정이나 Classiq의 승인을 받은 자료로 표시하지 않는다. '
        'QAE는 Quantum Application Engineer이며 진폭 추정 알고리즘 AE/IQAE와 구별한다.\n\n'
        '원판과 공개본\n2026-11-23 v1.0의 교육 내용 15쪽, 수식·도표·8개 자습문제와 해설·31개 '
        '개념색인·9개 참고문헌 및 원래 쪽번호를 보존했다. 로컬 파일 배치 안내를 웹 링크 안내로 바꾸고 '
        '메타데이터를 정리했다. 선수 개념의 파일 링크 8개는 실제 공개 HTTPS PDF와 확인한 정의 목적지로 '
        '바꾸었다. 개인 메일·원문 수집 파일·운영 기록·QA 화면과 제3자 교재 원문은 공개하지 않는다. '
        '원판이 언급한 재현 소스 ZIP은 이 공개 묶음에 포함하지 않으며, 공개 PDF의 유도·문제·해설로 '
        '학습할 수 있다.\n\n'
        '검산과 확인 범위\n원판 제작자의 30개 명명 고전 검사, 다른 Python 환경의 복사 재실행·별도 '
        '방법 대조와 통합 담당의 재실행은 원판의 수행 기록이다. 이번 공개 작업에서는 원판의 검사 묶음이나 '
        '미실행 Classiq 예제를 실행하지 않았다. '
        f'이번에는 별도로 작성한 Python 표준 라이브러리의 {INDEPENDENT_CHECKS}개 명명 조건을 검산했다. '
        + INDEPENDENT_SCOPE_KO + '\n'
        '교육 페이지의 문자·내부 목적지·원 공개 URI와 명시한 편집 영역 밖의 전 페이지 렌더링 동일성, '
        '개인정보·메타데이터·링크 동작 및 실제 조판을 검사했다. 원판과 이번 공개판 모두 Classiq SDK '
        'import·모델 생성·합성·metric 원격 요청·backend/QPU·실제 물성 계산이나 사람의 원고 감수를 '
        '수행한 것으로 표시하지 않는다. 작성자 회로의 자원 집계, 공식 문서에 저장된 값과 미실행 SDK '
        '요청을 새 플랫폼 합성·장치 실행 결과로 합치지 않는다.\n\n'
        '작성·검수 공개\n원판의 자료 열람·과학 검토·실제 고전 계산 범위는 각 본문과 참고문헌의 제작 '
        '기록을 따른다. 이번 공개판의 정제·페이지 보존·링크 및 조판 검수는 qae_l014_public, 선택 검산은 '
        'qae_l014_science가 수행하고 root가 통합·등록·게시한다. 원 교재·논문 전체를 이번에 새로 읽거나 '
        '원판 수치 검증을 모두 재현한 것으로 소급 표시하지 않는다.\n\n'
        '공개 학습 입구와 후속 회차\ninfant83.io/AI_Tech_Review/lectures/classiq-qae-onboarding/\n'
        '회차별 공개판과 필기 링크는 같은 시리즈 목록에서 제공한다.\n\n'
        '편집·출처 기준: AI Tech Review Editorial Harness 2026.08 · APS 인용 기준 · 과학 설명 준칙'
    )
    assert appendix.insert_textbox(fitz.Rect(55, 119, 540, 785), disclosure,
                                  fontname='PublicNanum', fontsize=10.1, lineheight=1.5,
                                  color=(.12, .20, .25)) >= 0
    web = appendix.search_for('infant83.io/AI_Tech_Review/lectures/classiq-qae-onboarding/')[0]
    appendix.insert_link({'kind': fitz.LINK_URI, 'from': web,
                         'uri': BASE + 'lectures/classiq-qae-onboarding/'})
    doc.set_metadata({'title': 'Classiq QAE L014 · ' + TITLE + ' · 공개 보관본',
                      'author': '김현중', 'creator': 'Agentic Tech Review Letters (ATRL); OpenAI Codex-assisted archive',
                      'subject': 'Independent Korean study notes; public edition 2026-11-23',
                      'keywords': '', 'producer': '',
                      'creationDate': '', 'modDate': ''})
    doc.del_xml_metadata()
    doc.xref_set_key(doc.pdf_catalog(), 'OpenAction', 'null')
    doc.update_object(doc.pdf_catalog(), re.sub(r'\s*/OpenAction\s+null\b', '', doc.xref_object(doc.pdf_catalog())))
    doc.subset_fonts()
    output = ROOT / 'output/pdf' / (IDENTIFIER + '.pdf')
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output, garbage=4, deflate=True, clean=True)
    final = fitz.open(output)
    assert len(final) == 16
    assert named_destinations(final) == original_names
    assert internal_link_signature(final) == original_internal_links
    characters_preserved = []
    for index in range(15):
        assert outside_characters(original[index], regions[index]) == outside_characters(final[index], regions[index]), ('Character change', index + 1)
        characters_preserved.append(index + 1)
        diff = ImageChops.difference(raster(original[index]), raster(final[index]))
        mask = ImageDraw.Draw(diff)
        for x0, y0, x1, y1 in regions[index]:
            mask.rectangle((math.floor(x0 * 1.5) - 3, math.floor(y0 * 1.5) - 3,
                            math.ceil(x1 * 1.5) + 3, math.ceil(y1 * 1.5) + 3), fill='black')
        assert diff.getbbox() is None, ('Unexpected rendering change', index + 1, diff.getbbox())
    final_uri_counts = Counter(link['uri'] for page in final for link in page.get_links() if 'uri' in link)
    expected_uri_counts = Counter(original_uris) + Counter(link['uri'] for link in rewritten)
    expected_uri_counts[BASE + 'lectures/classiq-qae-onboarding/'] += 1
    assert final_uri_counts == expected_uri_counts
    objects = '\n'.join(final.xref_object(i) for i in range(1, final.xref_length()))
    text = '\n'.join(page.get_text() for page in final)
    action_patterns = {'Launch': r'/S\s*/Launch\b', 'JavaScript': r'/S\s*/JavaScript\b',
                       'OpenAction': r'/OpenAction\b', 'GoToR': r'/S\s*/GoToR\b',
                       'EmbeddedFile': r'/EmbeddedFile\b', 'AA': r'/AA\b', 'AcroForm': r'/AcroForm\b'}
    action_scan = {key: len(re.findall(pattern, objects)) for key, pattern in action_patterns.items()}
    assert not any(action_scan.values()), 'Unexpected active or embedded PDF content'
    assert final.embfile_count() == 0
    assert not final.metadata.get('creationDate') and not final.metadata.get('modDate')
    assert not re.search(r'/S\s*/(?:Launch|JavaScript|GoToR)|/OpenAction\b|/EmbeddedFile\b|/(?:Users|home|private)/|mailto:|chatgpt\.com/share/', objects)
    assert not re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text + objects)
    assert not any(term in re.sub(r'\s+', '', text) for term in ['사용자배경의', '이전PDF를같은폴더에둔다', 'AMS/ADF경험과연결하면'])
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for index, page in enumerate(final):
        raster(page, 1.2).save(args.qa_dir / f'L014-page-{index + 1:02d}.png')
    record = {'unit': 'L014', 'date': '2026-11-23', 'title': TITLE,
              'source_pages': 15, 'public_pages': 16, 'source_edition_verified_against_private_intake': True,
              'public_sha256': sha256(output), 'file': output.name,
              'redaction_and_added_regions': {str(i + 1): boxes for i, boxes in regions.items() if boxes},
              'rewritten_links': rewritten, 'unchanged_original_page_regions_pixel_equal': True,
              'original_page_characters_outside_edits_preserved': characters_preserved,
              'internal_named_destinations_preserved': len(original_names),
              'internal_link_annotations_preserved': len(original_internal_links),
              'original_public_uris_preserved': len(original_uris),
              'embedded_files': 0, 'launch_or_script_actions': 0,
              'public_bytes': output.stat().st_size,
              'action_scan': action_scan,
              'metadata_review': {'title': final.metadata['title'], 'source_metadata_dates_removed': True,
                                  'source_producer_removed': True, 'source_keywords_removed': True,
                                  'xmp_removed': not final.get_xml_metadata(), 'embedded_files': 0,
                                  'unsafe_actions': 0, 'private_contacts_and_paths_found': False}}
    report = {'date': EDITION_DATE, 'units': [record], 'source_zip_in_public_bundle': False,
              'original_validation_suite_rerun': False, 'original_checks_recorded': 30,
              'independent_selected_classical_checks': INDEPENDENT_CHECKS,
              'independent_classical_check_scope': INDEPENDENT_SCOPE_EN,
              'public_preparation_scope': 'Preservation, privacy, metadata, cross-PDF destinations and full-page rendering; no new SDK, synthesis, metrics or physical experiment'}
    (ROOT / 'reports/pdf-L014-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'unit': 'L014', 'pages': 16, 'sha256': record['public_sha256'],
                      'named_destinations': len(original_names), 'rewritten_links': len(rewritten)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
