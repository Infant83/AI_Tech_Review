# -*- coding: utf-8 -*-
"""Archive the eight reviewed FTQC PDFs without rewriting educational pages.

Source edition digests and the completed independent review are explicit private
inputs. This command does not execute the source package. Renders stay outside
the public bundle. Frozen PDF editions cannot be overwritten by this command.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import fitz
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
PREFIX = '2026-11-27-photonic-fault-tolerant-computing'
DATE = '2026-11-27'
BASE = 'https://infant83.io/AI_Tech_Review/'
COLLECTION = BASE + 'lectures/photonic-fault-tolerant-computing/'
EDITIONS = [
    ('Level_01_Foundations_KO_v1.pdf', 'l001', 6, '양자정보의 기초 토대'),
    ('Level_02_Noise_and_FTQC_KO_v1.pdf', 'l002', 6, '노이즈와 내결함성의 필요성'),
    ('Level_03_QEC_Pipeline_KO_v1.pdf', 'l003', 6, '양자오류정정의 핵심 원리'),
    ('Level_04_Logical_Operations_KO_v1.pdf', 'l004', 5, '논리 연산과 매직 상태'),
    ('Level_05_2D_Color_Codes_KO_v1.pdf', 'l005', 5, '위상 양자 코드와 2차원 컬러 코드'),
    ('Level_06_MBQC_KO_v1.pdf', 'l006', 6, '측정기반 양자컴퓨팅'),
    ('Level_07_Photonic_Topological_MBQC_KO_v1.pdf', 'l007', 6, '광자 플랫폼과 위상학적 MBQC'),
    ('Quantum_FTQC_Color_Codes_Photonic_MBQC_Complete_KO_v1.pdf', 'complete', 42,
     '큐비트에서 광자 내결함성 계산까지'),
]
ACTION_PATTERNS = {
    'Launch': r'/S\s*/Launch\b', 'JavaScript': r'/S\s*/JavaScript\b',
    'OpenAction': r'/OpenAction\b', 'GoToR': r'/S\s*/GoToR\b',
    'EmbeddedFile': r'/EmbeddedFile\b', 'AA': r'/AA\b',
    'AcroForm': r'/AcroForm\b',
}
PRIVATE_PATTERN = re.compile(
    r'/(?:Users|home|private)/|mailto:|chatgpt\.com/share/|'
    r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def named_destinations(document):
    return {name: (value['page'], tuple(value['to']), value.get('zoom', 0))
            for name, value in document.resolve_names().items()}


def internal_link_signature(document):
    return [(index, link['kind'], tuple(link['from']), link.get('page'),
             link.get('nameddest'), tuple(link.get('to', [])), link.get('zoom'))
            for index, page in enumerate(document) for link in page.get_links()
            if link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED)]


def outline_signature(document):
    return [(level, title, page,
             {key: tuple(value) if key == 'to' else value
              for key, value in target.items() if key != 'xref'})
            for level, title, page, target in document.get_toc(False)]


def uri_signature(document, page_limit=None):
    return [(index, tuple(link['from']), link['uri'])
            for index, page in enumerate(document)
            if page_limit is None or index < page_limit
            for link in page.get_links() if 'uri' in link]


def visible_characters(page):
    return Counter((char['c'], tuple(char['bbox']))
                   for block in page.get_text('rawdict')['blocks']
                   for line in block.get('lines', [])
                   for span in line.get('spans', [])
                   for char in span.get('chars', []))


def raster(page, scale=1.5):
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def add_disclosure(doc, font, unit, original_pages, review):
    page = doc.new_page(width=595.276, height=841.89)
    page.insert_font(fontname='PublicNanum', fontfile=str(font))
    label = '통합본' if unit == 'complete' else 'Level ' + str(int(unit[1:]))
    assert page.insert_textbox(fitz.Rect(55, 55, 540, 110),
                              label + ' · 공개판 안내와 확인 범위',
                              fontname='PublicNanum', fontsize=18,
                              color=(.08, .21, .29)) >= 0
    scope = (
        'Agentic Tech Review Letters (ATRL) · 공개 보관본 · 2026-11-27\n'
        '책임 편집자 김현중 · AI 보조 OpenAI Codex\n\n'
        '자료 성격\n'
        '양자정보의 기초, 양자오류정정과 논리 연산, 컬러 코드, 측정기반 계산과 광자 '
        '플랫폼을 잇는 한국어 독립 학습 모노그래프다. 특정 기관의 공식 교재나 인증 '
        '과정으로 표시하지 않는다. 내결함성 양자컴퓨팅(FTQC)은 오류가 생기는 소자로 '
        '신뢰할 수 있는 논리 계산을 수행하는 방법을 다룬다.\n\n'
        '원판과 공개본\n'
        f'2026-11-27 v1 원판 {original_pages}쪽의 본문·수식·회로·도표·예시·참고문헌과 '
        '원래 쪽번호를 모두 보존했다. 원래 페이지의 보이는 내용은 수정하지 않았고, '
        '공개판 안내 1쪽만 뒤에 덧붙였다. 내부 목차·정의·각주 목적지와 외부 공개 링크도 '
        '보존했다. 제작 시각·생성 도구 등 메타데이터와 PDF 시작 동작만 정리했다. '
        '원판이 언급하는 LaTeX·검산 코드의 원본 묶음은 이번 공개 묶음에 포함하지 않는다.\n\n'
        '원 작성자의 검산 기록과 이번 확인\n'
        '원 작성자가 남긴 94개 고전 행렬·유한 오류패턴 검산과 전 페이지 점검은 원판의 '
        '제작 기록이다. 이번 아카이빙에서는 그 94개 검사 묶음을 재실행하지 않았다. '
        '이번 공개 작업의 독립 확인 범위는 다음과 같다. ' + review['scope_ko'] + '\n'
        '논문에서 보고한 임계값·장치 성능을 재현한 것으로 표시하지 않는다. SDK·QPU·'
        '하드웨어·광학 실험·디코더 대규모 실험을 실행하지 않았다.\n\n'
        '공개판 검수\n'
        '편집부(AEDAUT)의 ftqc_pdf가 원판과 공개판의 전 페이지 렌더링·문자·목차·'
        '내부 목적지·공개 URI의 보존과 메타데이터를 확인했다. ftqc_science가 전체 '
        '교육 내용을 읽고 위의 선택 고전 검산을 수행했으며, root가 등록·웹 목록·게시를 '
        '통합한다. 원문 94개 검사의 완전 재현이나 사람의 원고 감수를 수행한 것으로 '
        '표시하지 않는다. 개인 메일·원본 수집 파일·QA 화면과 내부 운영 기록은 공개하지 않는다.\n\n'
        '강의 묶음과 필기\n'
        'infant83.io/AI_Tech_Review/lectures/photonic-fault-tolerant-computing/\n'
        '같은 목록에서 통합본과 Level 1-7의 요약·PDF·필기 링크를 제공한다.\n\n'
        '편집 기준: AI Tech Review Editorial Harness 2026.08 · APS 인용 기준 · 과학 설명 준칙'
    )
    assert page.insert_textbox(fitz.Rect(55, 116, 540, 793), scope,
                              fontname='PublicNanum', fontsize=10,
                              lineheight=1.47, color=(.12, .20, .25)) >= 0
    rects = page.search_for('infant83.io/AI_Tech_Review/lectures/photonic-fault-tolerant-computing/')
    assert rects, 'Public collection URL must be visible on disclosure page'
    for rect in rects:
        page.insert_link({'kind': fitz.LINK_URI, 'from': rect, 'uri': COLLECTION})


def prepare(args, edition, expected, review):
    filename, unit, pages, title = edition
    source = args.source_dir / filename
    assert expected['filename'] == filename and expected['pages'] == pages
    assert source.stat().st_size == expected['bytes']
    assert re.fullmatch(r'[0-9a-f]{64}', expected['sha256'])
    assert sha256(source) == expected['sha256'], 'Unexpected source PDF edition'
    original, doc = fitz.open(source), fitz.open(source)
    assert len(original) == pages
    names = named_destinations(original)
    outlines = outline_signature(original)
    internal = internal_link_signature(original)
    public_links = uri_signature(original)
    uris = Counter(link['uri'] for page in original for link in page.get_links() if 'uri' in link)
    assert all(link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED, fitz.LINK_URI)
               for page in original for link in page.get_links()), 'Unreviewed link action'
    add_disclosure(doc, args.font, unit, pages, review)
    doc.set_metadata({'title': title + ' · 공개 보관본', 'author': '김현중',
                      'creator': 'Agentic Tech Review Letters (ATRL); OpenAI Codex-assisted archive',
                      'subject': 'Independent Korean FTQC study monograph; public edition 2026-11-27',
                      'keywords': '', 'producer': '', 'creationDate': '', 'modDate': ''})
    doc.del_xml_metadata()
    doc.xref_set_key(doc.pdf_catalog(), 'OpenAction', 'null')
    doc.update_object(doc.pdf_catalog(), re.sub(r'\s*/OpenAction\s+null\b', '',
                                               doc.xref_object(doc.pdf_catalog())))
    doc.subset_fonts()
    identifier = PREFIX + ('' if unit == 'complete' else '-' + unit) + '-notes-ko'
    output = ROOT / 'output/pdf' / (identifier + '.pdf')
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise FileExistsError('Public edition already exists; preserve the frozen PDF')
    qa = args.qa_dir / unit
    qa.mkdir(parents=True, exist_ok=True)
    candidate = qa / 'candidate.pdf'
    if candidate.exists():
        raise FileExistsError('Private candidate already exists; inspect that attempt first')
    # Avoid numeric-coordinate rewrites to original plotting content streams.
    doc.save(candidate, garbage=4, deflate=True, clean=False)
    final = fitz.open(candidate)
    assert len(final) == pages + 1
    assert named_destinations(final) == names
    assert outline_signature(final) == outlines
    assert internal_link_signature(final) == internal
    assert uri_signature(final, pages) == public_links
    for index in range(pages):
        assert visible_characters(original[index]) == visible_characters(final[index]), ('Character change', unit, index + 1)
        assert ImageChops.difference(raster(original[index]), raster(final[index])).getbbox() is None, ('Pixel change', unit, index + 1)
    final_uris = Counter(link['uri'] for page in final for link in page.get_links() if 'uri' in link)
    assert final_uris == uris + Counter({COLLECTION: len(final[-1].get_links())})
    objects = '\n'.join(final.xref_object(i) for i in range(1, final.xref_length()))
    text = '\n'.join(page.get_text() for page in final)
    actions = {key: len(re.findall(pattern, objects)) for key, pattern in ACTION_PATTERNS.items()}
    assert not any(actions.values()), 'Unreviewed active or embedded content'
    assert final.embfile_count() == 0
    assert not PRIVATE_PATTERN.search(objects + text)
    assert not final.metadata.get('creationDate') and not final.metadata.get('modDate')
    assert not final.get_xml_metadata()
    for index, page in enumerate(final):
        raster(page, 1.5).save(qa / f'public-{index + 1:02d}.png')
    record = {
        'identifier': identifier, 'unit': unit, 'source_pages': pages,
        'public_pages': len(final), 'public_sha256': sha256(candidate),
        'public_bytes': candidate.stat().st_size, 'file': output.name,
        'source_edition_verified_against_private_intake': True,
        'original_visible_content_edited': False,
        'all_original_page_pixels_equal': True,
        'all_original_characters_and_positions_equal': True,
        'original_named_destinations_preserved': len(names),
        'original_outline_entries_preserved': len(outlines),
        'original_internal_links_preserved': len(internal),
        'original_public_uri_annotations_preserved': sum(uris.values()),
        'added_public_collection_links': len(final[-1].get_links()),
        'action_scan': actions, 'embedded_files': 0,
        'metadata_review': {'source_dates_and_producer_removed': True,
                            'xmp_removed_or_absent': True, 'private_patterns_found': False},
    }
    final.close()
    doc.close()
    original.close()
    return record, candidate, output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--expected-source-manifest', type=Path, required=True,
                        help='Private receipt with PDFs filename/bytes/pages/sha256 fields')
    parser.add_argument('--independent-review', type=Path, required=True,
                        help='Private PASS record with actual check count and KO/EN scope')
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--qa-dir', type=Path, required=True)
    args = parser.parse_args()
    receipt = json.loads(args.expected_source_manifest.read_text(encoding='utf-8'))
    expected = {item['filename']: item for item in receipt['PDFs']}
    assert set(expected) == {edition[0] for edition in EDITIONS}
    review = json.loads(args.independent_review.read_text(encoding='utf-8'))
    assert review['status'] == 'PASS', 'Independent scientific review must pass first'
    assert isinstance(review['independent_selected_classical_checks'], int)
    assert review['independent_selected_classical_checks'] > 0
    assert review['scope_ko'].strip() and review['scope_en'].strip()
    prepared = [prepare(args, edition, expected[edition[0]], review) for edition in EDITIONS]
    # Only freeze outputs after all eight editions pass preservation checks.
    for record, candidate, output in prepared:
        if output.exists():
            raise FileExistsError('Public edition appeared during preparation')
        candidate.rename(output)
    records = [item[0] for item in prepared]
    report = {
        'date': DATE, 'source_edition': 'v1', 'editions': records,
        'source_total_pages': sum(record['source_pages'] for record in records),
        'public_total_pages': sum(record['public_pages'] for record in records),
        'source_zip_in_public_bundle': False,
        'original_validation_suite_rerun': False, 'original_checks_recorded': 94,
        'independent_selected_classical_checks': review['independent_selected_classical_checks'],
        'independent_classical_check_scope': review['scope_en'],
        'public_preparation_scope': 'Original educational pages pixel/character/link/destination/outline preservation; source metadata/start-action cleanup; one disclosure page per PDF. No SDK, QPU, optical hardware or threshold simulation execution.',
        'visual_inspection': 'Pending direct rendered-page review; separate final visual QA record required.',
    }
    reports = ROOT / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    (reports / 'pdf-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'pdf_count': len(records), 'public_total_pages': report['public_total_pages'],
                      'original_pixels_preserved': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
