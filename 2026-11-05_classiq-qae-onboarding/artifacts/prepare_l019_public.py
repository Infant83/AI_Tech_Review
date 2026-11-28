# -*- coding: utf-8 -*-
"""Create L019's public archival edition without regenerating its education.

The source, prior source-page renders, reviewed model records and scientific
disclosure are explicit inputs. Original material and QA images stay private.
This command never executes the producer package or changes earlier units.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil

import fitz
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
IDENTIFIER = '2026-11-28-classiq-qae-l019-notes-ko'
TITLE = '각 게이트가 정확한데도 에너지가 왜 틀리는가'
EDITION_DATE = '2026-11-28'
BASE = 'https://infant83.io/AI_Tech_Review/'
PREVIOUS = {
    '2026-11-05_Classiq_QAE_Lecture03_KO_v1.pdf': '2026-11-05-classiq-qae-l003-notes-ko',
    '2026-11-20_Classiq_QAE_Lecture11_KO_v1.pdf': '2026-11-20-classiq-qae-l011-notes-ko',
    '2026-11-23_Classiq_QAE_Lecture14_KO_v1.pdf': '2026-11-23-classiq-qae-l014-notes-ko',
    '2026-11-27_Classiq_QAE_Lecture18_KO_v1.pdf': '2026-11-27-classiq-qae-l018-notes-ko',
}
ACTION_PATTERNS = {
    'Launch': r'/S\s*/Launch\b', 'JavaScript': r'/S\s*/JavaScript\b',
    'OpenAction': r'/OpenAction\b', 'GoToR': r'/S\s*/GoToR\b',
    'EmbeddedFile': r'/EmbeddedFile\b', 'AA': r'/AA\b', 'AcroForm': r'/AcroForm\b',
}


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


def outside_characters(page, regions):
    result = Counter()
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                for char in span.get('chars', []):
                    if not any(fitz.Rect(char['bbox']).intersects(fitz.Rect(region)) for region in regions):
                        result[char['c']] += 1
    return result


def raster(page, scale):
    pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes('RGB', (pixmap.width, pixmap.height), pixmap.samples)


def visual_page_identity(document, index):
    """Bind reused renders to the same decoded content and rendering resources."""
    page = document[index]
    fonts = []
    for xref, extension, kind, name, alias, encoding, referencer in page.get_fonts(full=True):
        data = document.extract_font(xref)[3]
        fonts.append((extension, kind, name, alias, encoding, hashlib.sha256(data).hexdigest()))
    images = []
    for item in page.get_images(full=True):
        xref = item[0]
        images.append((item[2:9], hashlib.sha256(document.xref_stream(xref)).hexdigest()))
    xobjects = []
    for xref, name, invoker, rectangle in page.get_xobjects():
        xobjects.append((name, tuple(rectangle), hashlib.sha256(document.xref_stream(xref)).hexdigest()))
    return (tuple(page.rect), tuple(page.mediabox), tuple(page.cropbox), page.rotation,
            tuple(document.xref_stream(xref) for xref in page.get_contents()),
            tuple(fonts), tuple(images), tuple(xobjects), page.get_text('rawdict'))


def model_record(path):
    spec = importlib.util.spec_from_file_location('l019_saved_model_provenance', REPO / 'scripts/ai_model_provenance.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    record = module.validate_public_provenance(json.loads(path.read_text(encoding='utf-8')))
    return record, module.render_disclosure(record, 'ko').replace('`', '')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--expected-source-sha256', required=True)
    parser.add_argument('--source-render-dir', type=Path, required=True)
    parser.add_argument('--source-render-manifest', type=Path, required=True)
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--qa-dir', type=Path, required=True)
    parser.add_argument('--ai-provenance', type=Path, required=True)
    parser.add_argument('--original-ai-provenance', type=Path, required=True)
    parser.add_argument('--science-disclosure', type=Path, required=True)
    parser.add_argument('--replace-existing-sha256')
    parser.add_argument('--reuse-public-qa-dir', type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-f]{64}', args.expected_source_sha256):
        parser.error('Expected source SHA-256 must be 64 lowercase hexadecimal characters')
    if sha256(args.source) != args.expected_source_sha256:
        raise ValueError('Unexpected source edition')
    source_render = json.loads(args.source_render_manifest.read_text(encoding='utf-8'))
    assert source_render['source_sha256'] == args.expected_source_sha256
    assert source_render['pages'] == 20 and source_render['scale'] == 1.5
    assert set(source_render['image_sha256']) == {f'page-{index:02d}.png' for index in range(1, 21)}
    for name, digest in source_render['image_sha256'].items():
        assert sha256(args.source_render_dir / name) == digest
    assert len(source_render['image_sha256']) == 20
    science = json.loads(args.science_disclosure.read_text(encoding='utf-8'))
    assert science['scientific_approval'].startswith('No scientific publication blocker found;')
    assert science['counts']['source_author_check_groups'] == 26
    assert science['counts']['source_author_program_rerun_here'] is False
    assert science['counts']['max_matrix_dimension'] == 4
    count = science['counts']['new_independent_check_groups']
    assert type(count) is int and count > 0
    assert isinstance(science['ko'], str) and science['ko'].strip()
    assert isinstance(science['en'], str) and science['en'].strip()
    archival_models, archival_text = model_record(args.ai_provenance)
    original_models, original_text = model_record(args.original_ai_provenance)
    output = ROOT / 'output/pdf' / (IDENTIFIER + '.pdf')
    previous = None
    if output.exists() and args.replace_existing_sha256:
        assert sha256(output) == args.replace_existing_sha256
        assert args.reuse_public_qa_dir is not None
        previous = fitz.open(output)
        previous_qa = json.loads((args.reuse_public_qa_dir / 'pdf-build-qa.json').read_text(encoding='utf-8'))
        assert previous_qa['units'][0]['public_sha256'] == args.replace_existing_sha256
        assert (args.reuse_public_qa_dir / 'public-visual-review.json').exists()
    elif output.exists():
        raise FileExistsError('Preserve the already frozen public PDF; use a new reviewed edition')
    else:
        assert not args.replace_existing_sha256 and args.reuse_public_qa_dir is None
    args.qa_dir.mkdir(parents=True, exist_ok=False)
    original, document = fitz.open(args.source), fitz.open(args.source)
    assert len(original) == 20
    original_names = named_destinations(original)
    original_toc = original.get_toc()
    original_internal = internal_link_signature(original)
    original_uris = [link['uri'] for page in original for link in page.get_links() if 'uri' in link]
    regions = {index: [] for index in range(20)}

    # This edition's SCM/AMS/ADF footer is an impersonal definition used by §13.
    # It stays intact. The only educational-page addition occupies empty cover space.
    cover_note = fitz.Rect(59, 480, 536, 580)
    document[0].insert_font(fontname='PublicNanum', fontfile=str(args.font))
    cover_text = ('공개 보관본 · 2026-11-28\n'
                  '책임 편집자 김현중 · AI 보조 OpenAI Codex\n'
                  'Agentic Tech Review Letters (ATRL)\n'
                  'Classiq 공식 강의가 아닌 독립 학습 과정이다.\n'
                  '원판 교육 내용과 이번 공개 검수의 범위는 마지막 쪽에서 구분한다.')
    assert document[0].insert_textbox(cover_note, cover_text, fontname='PublicNanum', fontsize=9.5,
                                      lineheight=1.45, color=(.10, .30, .35)) >= 0
    regions[0].append(list(cover_note))

    rewritten = []
    for index, page in enumerate(document):
        for link in page.get_links():
            if link['kind'] not in (fitz.LINK_LAUNCH, fitz.LINK_GOTOR):
                continue
            filename, separator, fragment = link.get('file', '').partition('#')
            assert filename in PREVIOUS and separator and fragment.startswith('nameddest=')
            identifier = PREVIOUS[filename]
            prerequisite = fitz.open(REPO / 'archive/files' / (identifier + '.pdf'))
            destination = fragment.removeprefix('nameddest=')
            assert destination in prerequisite.resolve_names()
            uri = BASE + 'archive/files/' + identifier + '.pdf#' + fragment
            page.delete_link(link)
            page.insert_link({'kind': fitz.LINK_URI, 'from': link['from'], 'uri': uri})
            rewritten.append({'page': index + 1, 'uri': uri, 'destination_verified': True})
    assert len(rewritten) == 7

    appendix = document.new_page(width=595.276, height=841.89)
    appendix.insert_font(fontname='PublicNanum', fontfile=str(args.font))
    assert appendix.insert_textbox(fitz.Rect(55, 58, 540, 110), 'L019 · 공개판 안내와 확인 범위',
                                  fontname='PublicNanum', fontsize=19, color=(.08, .21, .29)) >= 0
    # NanumGothic lacks some Unicode superscript digits. Use interoperable ASCII
    # scientific notation in the appended disclosure, leaving source pages intact.
    science_ko = science['ko'].replace('2.53×10⁻¹⁴', '2.53e-14').replace('10⁻¹²', '1e-12')
    disclosure = (
        'Agentic Tech Review Letters (ATRL) · 공개 보관본 · 2026-11-28\n'
        '책임 편집자 김현중 · AI 보조 OpenAI Codex\n\n'
        '자료 성격과 보존\n공개 교재·논문·공식 문서에 근거해 자체 집필한 한국어 독립 학습 과정이다. '
        '공식 Classiq 강의·인증이나 Classiq의 승인을 받은 자료로 표시하지 않는다. '
        'QAE는 Quantum Application Engineer다. 원판 v1.0 교육20쪽, 수식·도표·문제8개와 해설·'
        '용어색인45개·문헌6개 및 원래 쪽번호를 보존했다. q0을 왼쪽/MSB로 둔 원 규약도 유지했다. '
        '표지의 빈 영역에 공개판 안내를 더하고 메타데이터를 정리했다. 선수 파일 링크7개를 실제 '
        '공개 HTTPS PDF의 확인한 정의 목적지로 바꿨다. 원판이 언급한 재현 ZIP·개인 메일·수집 원문·'
        '운영 파일·검수 화면은 공개 묶음에 포함하지 않는다.\n\n'
        '검산 범위\n원판 제작자의26개 검사와 같은 작성자의 SU(2) quaternion 대조·별도 Python '
        '환경 재실행은 원판 제작 기록이다. 이번 아카이빙에서 그 검사 묶음이나 Classiq 예제를 '
        '실행한 것으로 세지 않는다. 이번에는 별도 작성한 고전 계산의 '
        f'{count}개 명명 조건을 확인했다. ' + science_ko + '\n'
        '원판20쪽과 공개판21쪽의 실제 조판, 문자·내부 목적지·원 공개 URI와 명시한 표지 추가 영역 '
        '밖 전 페이지 픽셀 동일성을 확인했다. SDK import·모델 생성·합성·backend/provider simulator·'
        'QPU·새 난수 샷·실물 DFT/물성 계산·사람의 원고 감수를 수행한 것으로 표시하지 않는다.\n\n'
        '작성·검수 기록\n원판 집필 세션의 보존된 턴설정을 공개 아카이빙 때 대조했다. 이는 제작 시점에 '
        '새로 기록한 설정이나 다른 원판 감수자의 설정을 추정한 것이 아니다.\n' + original_text + '\n'
        '이번 공개 작업의 정제·페이지 보존·링크·조판 검수는 qae_l019_pdf, 별도 선택 검산은 '
        'qae_l019_science, 시리즈·요약·발행 연속성 검수는 qae_1128_archive_audit, 통합·등록·게시 '
        '담당은 root다. 원 교재·논문 전체를 이번에 재독·재현한 것으로 소급 표시하지 않는다.\n'
        + archival_text + '\n\n'
        '학습 입구와 후속 회차\ninfant83.io/AI_Tech_Review/lectures/classiq-qae-onboarding/\n'
        '회차별 공개판과 필기 링크는 같은 목록에 제공한다. 다음 L020 Block encoding·LCU·qubitization은 '
        '미발행 계획이다. 편집·출처 기준: AI Tech Review Editorial Harness 2026.08 · APS 인용 기준 · 과학 설명 준칙'
    )
    assert appendix.insert_textbox(fitz.Rect(55, 119, 540, 785), disclosure, fontname='PublicNanum',
                                  fontsize=9.9, lineheight=1.34, color=(.12, .20, .25)) >= 0, 'Public scope page overflows'
    box = appendix.search_for('infant83.io/AI_Tech_Review/lectures/classiq-qae-onboarding/')[0]
    appendix.insert_link({'kind': fitz.LINK_URI, 'from': box, 'uri': BASE + 'lectures/classiq-qae-onboarding/'})
    document.set_metadata({'title': 'Classiq QAE L019 · ' + TITLE + ' · 공개 보관본',
                           'author': '김현중', 'creator': 'Agentic Tech Review Letters (ATRL); OpenAI Codex-assisted archive',
                           'subject': 'Independent Korean study notes; Hamiltonian time evolution and Trotter; public edition 2026-11-28',
                           'keywords': '', 'producer': '', 'creationDate': '', 'modDate': ''})
    document.del_xml_metadata()
    document.xref_set_key(document.pdf_catalog(), 'OpenAction', 'null')
    document.update_object(document.pdf_catalog(), re.sub(r'\s*/OpenAction\s+null\b', '', document.xref_object(document.pdf_catalog())))
    document.subset_fonts()
    candidate = args.qa_dir / 'public-candidate.pdf'
    document.save(candidate, garbage=4, deflate=True, clean=False)
    final = fitz.open(candidate)
    assert len(final) == 21
    assert named_destinations(final) == original_names
    assert final.get_toc() == original_toc
    assert internal_link_signature(final) == original_internal
    characters_preserved, pixels_preserved, cached_render_pages, freshly_rendered_pages = [], [], [], []
    for index, page in enumerate(final):
        render_name = f'L019-page-{index + 1:02d}.png'
        if previous is not None and index < 20 and visual_page_identity(final, index) == visual_page_identity(previous, index):
            prior_png = args.reuse_public_qa_dir / render_name
            prior_visual = json.loads((args.reuse_public_qa_dir / 'public-visual-review.json').read_text(encoding='utf-8'))
            assert prior_visual['status'] == 'PASS' and prior_visual['public_pdf_sha256'] == args.replace_existing_sha256
            assert index + 1 in prior_visual['pages_individually_viewed']
            assert sha256(prior_png) == prior_visual['image_sha256'][render_name]
            shutil.copyfile(prior_png, args.qa_dir / render_name)
            rendered = Image.open(prior_png).convert('RGB')
            cached_render_pages.append(index + 1)
        else:
            assert previous is None or index in (0, 20), ('Unexpected education-page identity change', index + 1)
            rendered = raster(page, 1.5)
            rendered.save(args.qa_dir / render_name)
            freshly_rendered_pages.append(index + 1)
        if index >= 20:
            continue
        assert outside_characters(original[index], regions[index]) == outside_characters(page, regions[index]), ('Character change', index + 1)
        characters_preserved.append(index + 1)
        before = Image.open(args.source_render_dir / f'page-{index + 1:02d}.png').convert('RGB')
        assert before.size == rendered.size
        difference = ImageChops.difference(before, rendered)
        mask = ImageDraw.Draw(difference)
        for x0, y0, x1, y1 in regions[index]:
            mask.rectangle((math.floor(x0 * 1.5) - 3, math.floor(y0 * 1.5) - 3,
                            math.ceil(x1 * 1.5) + 3, math.ceil(y1 * 1.5) + 3), fill='black')
        assert difference.getbbox() is None, ('Unexpected rendering change', index + 1, difference.getbbox())
        pixels_preserved.append(index + 1)
    final_uris = Counter(link['uri'] for page in final for link in page.get_links() if 'uri' in link)
    expected_uris = Counter(original_uris) + Counter(link['uri'] for link in rewritten)
    expected_uris[BASE + 'lectures/classiq-qae-onboarding/'] += 1
    assert final_uris == expected_uris
    objects = '\n'.join(final.xref_object(number) for number in range(1, final.xref_length()))
    text = '\n'.join(page.get_text() for page in final)
    actions = {key: len(re.findall(pattern, objects)) for key, pattern in ACTION_PATTERNS.items()}
    assert not any(actions.values()) and final.embfile_count() == 0
    assert not re.search(r'/(?:Users|home|private)/|mailto:|chatgpt\.com/share/', objects + text)
    assert not re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', objects + text)
    assert not final.metadata.get('creationDate') and not final.metadata.get('modDate')
    assert not final.metadata.get('producer') and not final.metadata.get('keywords') and not final.get_xml_metadata()
    assert '\ufffd' not in text
    assert '\x00' not in text, 'Unsupported glyph in extracted PDF text'
    appendix_text = final[20].get_text()
    # Source TeX fonts map some visually correct tall math delimiters to control
    # codes. Preserve those source mappings; reject controls in our new page.
    assert not any(ord(character) < 32 and character not in '\n\r\t' for character in appendix_text), 'Control character in appended disclosure'
    assert '2.53e-14' in appendix_text and '1e-12' in appendix_text
    fonts = []
    for xref in sorted({row[0] for page in final for row in page.get_fonts(full=True)}):
        name, extension, kind, data = final.extract_font(xref)
        assert data, ('Nonembedded font', name)
        fonts.append({'name': name, 'type': kind, 'format': extension, 'embedded_bytes': len(data)})
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(candidate, output)
    record = {'unit': 'L019', 'date': EDITION_DATE, 'title': TITLE, 'source_pages': 20, 'public_pages': 21,
              'source_edition': 'v1.0', 'source_edition_verified_against_private_intake': True,
              'public_sha256': sha256(output), 'public_bytes': output.stat().st_size, 'file': output.name,
              'redaction_and_added_regions': {str(index + 1): boxes for index, boxes in regions.items() if boxes},
              'educational_page_redactions': [], 'original_cover_footer_definitions_preserved': True,
              'rewritten_links': rewritten, 'unchanged_original_page_regions_pixel_equal': True,
              'original_source_renders_reused': True,
              'cached_public_render_pages_verified_content_resource_identity': cached_render_pages,
              'current_build_pages_freshly_rendered': freshly_rendered_pages,
              'original_page_characters_outside_edits_preserved': characters_preserved,
              'source_pages_pixel_compared': pixels_preserved,
              'internal_named_destinations_preserved': len(original_names),
              'outline_entries_preserved': len(original_toc), 'internal_link_annotations_preserved': len(original_internal),
              'original_public_uris_preserved': len(original_uris), 'embedded_files': 0,
              'launch_or_script_actions': 0, 'action_scan': actions, 'fonts_embedded': fonts,
              'metadata_review': {'title': final.metadata['title'], 'source_metadata_dates_removed': True,
                                  'source_subject_genericized': True, 'source_producer_removed': True,
                                  'source_keywords_removed': True, 'xmp_removed': True,
                                  'unsafe_actions': 0, 'private_contacts_and_paths_found': False,
                                  'null_glyph_characters': 0, 'appended_disclosure_control_characters': 0,
                                  'appended_scientific_notation_verified': ['2.53e-14', '1e-12']}}
    report = {'date': EDITION_DATE, 'status': 'AWAITING_FINAL_INDIVIDUAL_VISUAL_REVIEW', 'units': [record],
              'source_zip_in_public_bundle': False, 'original_validation_suite_rerun': False,
              'original_checks_recorded': 26, 'independent_selected_classical_checks': count,
              'independent_classical_check_scope': science['en'],
              'source_author_model_provenance': original_models,
              'source_author_model_scope': 'Retrospective comparison of preserved authoring-turn settings; not current defaults or inferred source-reviewer settings.',
              'archival_model_provenance': archival_models,
              'public_preparation_scope': 'Educational-page preservation, empty-cover public note, metadata, verified cross-PDF destinations, appended scope page and full-page rendering; no original SDK/QPU/physical execution'}
    (args.qa_dir / 'pdf-build-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'unit': 'L019', 'pages': 21, 'sha256': record['public_sha256'],
                      'public_bytes': record['public_bytes'], 'named_destinations': len(original_names),
                      'rewritten_links': len(rewritten), 'status': report['status']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
