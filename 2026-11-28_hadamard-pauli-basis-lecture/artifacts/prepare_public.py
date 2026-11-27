# -*- coding: utf-8 -*-
"""Preserve the five-page v2 essay and add scoped public archival credits.

Private source digest, completed scientific review and authoring-time public
model records are caller inputs. Original authoring settings are not inferred
from the archival workers. QA renders and intermediate candidates stay private.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import fitz
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
IDENTIFIER = '2026-11-28-hadamard-pauli-basis-notes-ko'
TITLE = '그림의 규칙을 양자회로로 옮기는 법'
REGION = (52, 686, 543.276, 780)
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


def raster(page, scale=1.7):
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def characters(page, excluded=()):
    return Counter((char['c'], tuple(char['bbox']))
                   for block in page.get_text('rawdict')['blocks']
                   for line in block.get('lines', [])
                   for span in line.get('spans', [])
                   for char in span.get('chars', [])
                   if not any(fitz.Rect(char['bbox']).intersects(fitz.Rect(box)) for box in excluded))


def links(document):
    return [(number, link['kind'], tuple(link['from']), link.get('uri'),
             link.get('page'), link.get('nameddest'), tuple(link.get('to', [])), link.get('zoom'))
            for number, page in enumerate(document) for link in page.get_links()]


def destinations(document):
    return {name: (item['page'], tuple(item['to']), item.get('zoom', 0))
            for name, item in document.resolve_names().items()}


def model_records(paths):
    rows = []
    for path in paths:
        item = json.loads(path.read_text(encoding='utf-8'))
        assert item['version'] == 1 and item['system'] == 'OpenAI Codex'
        assert item['scope'] == 'recorded_editorial_work'
        for row in item['roles']:
            assert set(row) == {'role', 'model_id', 'reasoning_effort', 'evidence_kind'}
            assert row['evidence_kind'] == 'turn_context'
            if row not in rows:
                rows.append(row)
    assert {'editing', 'source-review', 'scientific-review'} <= {row['role'] for row in rows}
    settings = {(row['model_id'], row['reasoning_effort']) for row in rows}
    # This reviewed compact colophon names the common setting only when all
    # participating roles actually have that same recorded model and effort.
    assert len(settings) == 1, 'Different worker settings require a revised scoped colophon'
    return rows, next(iter(settings))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--expected-source-sha256', required=True)
    parser.add_argument('--scientific-review', type=Path, required=True)
    parser.add_argument('--ai-provenance', type=Path, action='append', required=True)
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--qa-dir', type=Path, required=True)
    args = parser.parse_args()
    assert re.fullmatch(r'[0-9a-f]{64}', args.expected_source_sha256)
    assert sha256(args.source) == args.expected_source_sha256, 'Unreviewed source edition'
    review = json.loads(args.scientific_review.read_text(encoding='utf-8'))
    assert review['status'] == 'PASS'
    assert review['independent_selected_classical_checks'] == 11
    assert review['max_matrix_dimension'] == 4
    assert review['max_residual'] <= review['tolerance']
    models, (model, effort) = model_records(args.ai_provenance)
    original, doc = fitz.open(args.source), fitz.open(args.source)
    assert len(doc) == 5 and original.metadata['title'] == TITLE
    original_links, original_names, original_toc = links(original), destinations(original), original.get_toc(False)
    assert len(original_links) == 3 and all(item[1] == fitz.LINK_URI for item in original_links)
    assert all(not fitz.Rect(box['bbox']).intersects(fitz.Rect(REGION))
               for box in original[4].get_text('dict')['blocks']), 'Credit region must be blank'
    colophon = (
        '공개 보관본 · Agentic Tech Review Letters (ATRL) · 2026.11.28 / 책임 편집자 김현중\n'
        '원판 v2(2026.11.27)의 5쪽·도해 5개·참고문헌 3개 보존. 제작 메타데이터만 정리했다.\n'
        '원저술 AI 모델·추론 설정과 원저자의 검산 실행 내역: 확인 기록 없음.\n'
        f'이번 편집·자료 감수·선택 검산: OpenAI Codex, {model} (추론 {effort}). 별도 사람 원고 감수 미확인.\n'
        '별도 4×4 이하 행렬 검산 11항목으로 Walsh 계수·Z 문자열 전개·위상/CX 회로의 공통 위상·'
        '상태/연산자 기저를 점검했다. SDK·QPU·물리 실험은 하지 않았다.'
    )
    doc[4].insert_font(fontname='PublicNanum', fontfile=str(args.font))
    remainder = doc[4].insert_textbox(fitz.Rect(REGION), colophon,
                                    fontname='PublicNanum', fontsize=8.3,
                                    lineheight=1.28, color=(.30, .37, .40))
    assert remainder >= 0, 'Public archival colophon must fit without overflow'
    doc.set_metadata({'title': TITLE + ' · 공개 보관본 v2',
                      'author': '과학 에세이; 공개판 책임 편집자 김현중',
                      'subject': original.metadata['subject'],
                      'creator': 'Agentic Tech Review Letters (ATRL); OpenAI Codex-assisted public archive',
                      'producer': '', 'creationDate': '', 'modDate': '', 'keywords': ''})
    doc.del_xml_metadata()
    doc.subset_fonts()
    output = ROOT / 'output/pdf' / (IDENTIFIER + '.pdf')
    if output.exists():
        raise FileExistsError('Preserve the frozen public edition; do not overwrite it')
    output.parent.mkdir(parents=True, exist_ok=True)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    candidate = args.qa_dir / 'candidate.pdf'
    if candidate.exists():
        raise FileExistsError('Inspect the existing private candidate before another attempt')
    doc.save(candidate, garbage=4, deflate=True, clean=False)
    final = fitz.open(candidate)
    assert len(final) == 5
    assert links(final) == original_links
    assert destinations(final) == original_names and final.get_toc(False) == original_toc
    for number in range(5):
        excluded = [REGION] if number == 4 else []
        assert characters(final[number], excluded) == characters(original[number], excluded), ('Character change', number + 1)
        diff = ImageChops.difference(raster(final[number]), raster(original[number]))
        if number == 4:
            # Mask only the declared blank credit region. Source content never
            # enters this rectangle; no formula/figure/reference masks exist.
            x0, y0, x1, y1 = REGION
            ImageDraw.Draw(diff).rectangle((int(x0 * 1.7) - 2, int(y0 * 1.7) - 2,
                                           int(x1 * 1.7) + 2, int(y1 * 1.7) + 2), fill='black')
        assert diff.getbbox() is None, ('Unreviewed visible change', number + 1, diff.getbbox())
        raster(final[number]).save(args.qa_dir / f'public-{number + 1:02d}.png')
    objects = '\n'.join(final.xref_object(i) for i in range(1, final.xref_length()))
    text = '\n'.join(page.get_text() for page in final)
    actions = {name: len(re.findall(pattern, objects)) for name, pattern in ACTION_PATTERNS.items()}
    assert not any(actions.values()) and final.embfile_count() == 0
    assert not PRIVATE_PATTERN.search(objects + text)
    assert not final.metadata.get('creationDate') and not final.metadata.get('modDate')
    assert not final.metadata.get('producer') and not final.get_xml_metadata()
    record = {
        'status': 'AWAITING_FINAL_VISUAL_REVIEW', 'identifier': IDENTIFIER,
        'file': output.name, 'source_edition': 'v2', 'source_pages': 5, 'public_pages': 5,
        'public_sha256': sha256(candidate), 'public_bytes': candidate.stat().st_size,
        'source_digest_verified_against_private_intake': True,
        'original_educational_text_and_positions_preserved': True,
        'original_page_regions_outside_added_credits_pixel_equal': True,
        'added_credit_region': {'page': 5, 'rectangle_pt': REGION, 'font_size_pt': 8.3},
        'original_public_link_annotations_preserved': 3,
        'original_named_destinations_preserved': len(original_names),
        'original_outline_entries_preserved': len(original_toc),
        'metadata_production_dates_and_tool_removed': True,
        'private_patterns_found': False, 'embedded_files': 0, 'action_scan': actions,
        'original_authoring_model_and_executed_checks': 'No confirming record supplied',
        'current_archival_model_roles': models,
        'independent_selected_classical_checks': review['independent_selected_classical_checks'],
        'independent_check_count_definition': review['check_count_definition'],
        'independent_classical_check_scope': review['scope_en'],
        'source_author_validation_suite_rerun': False,
        'sdk_qpu_or_physical_experiment_run': False,
        'additional_human_manuscript_review_confirmed': False,
        'qa_images_public': False,
    }
    final.close()
    doc.close()
    original.close()
    candidate.rename(output)
    reports = ROOT / 'reports'
    reports.mkdir(parents=True, exist_ok=True)
    (reports / 'pdf-qa.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'identifier': IDENTIFIER, 'pages': 5, 'sha256': record['public_sha256'],
                      'public_bytes': record['public_bytes'], 'original_regions_preserved': True}, ensure_ascii=False))


if __name__ == '__main__':
    main()
