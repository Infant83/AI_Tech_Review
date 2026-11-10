"""Prepare an eight-page public supplement while preserving its educational pages.

The reviewed source PDF and font are explicit local inputs. Source collection
material and visual QA remain outside the public dist directory.
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
SOURCE_SHA256 = 'afca4603b61f9eef3df4714e90ea8b5bdaaa46b9018a5d3646b0e672771be4fd'
EDITION_DATE = '2026-11-10'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def named_destinations(document):
    return {name: (value['page'], tuple(value['to']), value.get('zoom', 0))
            for name, value in document.resolve_names().items()}


def link_signature(document):
    return [(index, link['kind'], tuple(link['from']), link.get('page'),
             link.get('uri'), link.get('nameddest'), tuple(link.get('to', [])),
             link.get('zoom'))
            for index, page in enumerate(document) for link in page.get_links()]


def raster(page, scale=1.5):
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def outside_characters(page, regions):
    result = Counter()
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                for char in span.get('chars', []):
                    box = fitz.Rect(char['bbox'])
                    if not any(box.intersects(fitz.Rect(region)) for region in regions):
                        result[char['c']] += 1
    return result


def replace_box(page, rectangle, text, font, size, color):
    page.add_redact_annot(rectangle, fill=(1, 1, 1))
    page.apply_redactions(images=0, graphics=0)
    page.insert_font(fontname='PublicNanum', fontfile=str(font))
    remaining = page.insert_textbox(rectangle, text, fontname='PublicNanum',
                                    fontsize=size, lineheight=1.35, color=color)
    assert remaining >= 0, ('Public text does not fit', rectangle, remaining)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--font', type=Path, required=True)
    parser.add_argument('--qa-dir', type=Path, required=True)
    args = parser.parse_args()
    assert digest(args.source) == SOURCE_SHA256, 'Unexpected source PDF edition'
    assert not args.qa_dir.resolve().is_relative_to((ROOT / 'dist').resolve())
    original, document = fitz.open(args.source), fitz.open(args.source)
    assert len(original) == 8
    names, links, outline = named_destinations(original), link_signature(original), original.get_toc()
    regions = {index: [] for index in range(8)}

    # Publication dates remain; private receipt and collection times do not.
    first_note = fitz.Rect(56, 457, 539, 497)
    replace_box(document[0], first_note,
                '자료 확인일은 2026-11-10이다. QAOA 논문 v1의 실제 투고일은 2026-09-12이다.\n'
                '자료 확인 시점과 연구 발표일을 구분한다. 공개 근거는 고정 판본의 원문·코드·데이터로 연결한다.\n'
                '개인 메일 원문·전달 정보·계정 정보·추적 링크는 공개하지 않는다.',
                args.font, 8.6, (.306, .4, .439))
    regions[0].append(list(first_note))

    # Retain the source-map identifier without publishing private provenance.
    source_note = fitz.Rect(84.5, 142, 539, 168)
    replace_box(document[7], source_note,
                '자료 확인 기준(2026-11-10). 공개 주장과 자체 검산의 근거는 S002–S007의\n'
                '고정 판본 원문·코드·데이터다. 비공개 원문과 전달 정보는 공개하지 않는다.',
                args.font, 8.6, (.094, .216, .278))
    regions[7].append(list(source_note))

    package_note = fitz.Rect(56, 382, 539, 424)
    replace_box(document[7], package_note,
                '첨부 패키지. 보충 PDF와 간결한 웹 학습 안내, 원본 노트북 14개와 공개 JSON 6개, 연결표 CSV, '
                '자체 검산 코드·결과, 라이선스·출처·해시 목록을 제공한다. 원저자 코드와 데이터를 변경 없이 '
                '구분해 담았으며, 웹 안내는 JavaScript·외부 수식 CDN 없이 읽을 수 있다.',
                args.font, 9.4, (.094, .216, .278))
    regions[7].append(list(package_note))

    publication_note = fitz.Rect(56, 489, 539, 517)
    replace_box(document[7], publication_note,
                '공개 자료의 관계. 기존 QML 18강에 연결하는 독립 보충자료다. 기존 147쪽 PDF와\n'
                '개인 필기 기준은 보존하고, 이 보충 PDF의 필기는 별도 문서로 저장한다.',
                args.font, 9.4, (.094, .216, .278))
    regions[7].append(list(publication_note))

    disclosure = fitz.Rect(56, 532, 539, 626)
    document[7].insert_font(fontname='PublicNanum', fontfile=str(args.font))
    assert document[7].insert_textbox(disclosure,
        '공개판 편집·검수 · 2026-11-10\n'
        '책임 편집자 김현중 · AI 보조 OpenAI Codex. faryad_pdf_review가 이 PDF의 정제·교육 내용 보존·'
        '링크·전체 8쪽 조판을 검수하고 root가 등록·게재를 통합한다. 본문에 적힌 원 작성자의 계산과 검토는 '
        '제작 당시 수행 기록이다. 이번 공개판에서는 원저자 노트북·장치 실험을 새로 실행하지 않았다. '
        '사람의 문장별 원고 감수는 미실시다.',
        fontname='PublicNanum', fontsize=8.8, lineheight=1.4,
        color=(.094, .216, .278)) >= 0
    regions[7].append(list(disclosure))

    document.set_metadata({
        'title': 'QML 실습 보충: Faryad의 알고리즘 노트북과 QAOA 실행예산 · 공개판',
        'author': '김현중',
        'creator': 'Agentic Tech Review Letters (ATRL); OpenAI Codex-assisted public edition',
        'subject': 'Independent supplement to the QML 18-lecture course; public edition 2026-11-10',
    })
    document.del_xml_metadata()
    document.xref_set_key(document.pdf_catalog(), 'OpenAction', 'null')
    document.update_object(document.pdf_catalog(), re.sub(
        r'\s*/OpenAction\s+null\b', '', document.xref_object(document.pdf_catalog())))
    document.subset_fonts()
    output = ROOT / 'dist/supplement.pdf'
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output, garbage=4, deflate=True, clean=True)
    final = fitz.open(output)
    assert len(final) == 8
    assert named_destinations(final) == names
    assert link_signature(final) == links
    assert final.get_toc() == outline
    characters_preserved = []
    for index in range(8):
        assert outside_characters(original[index], regions[index]) == outside_characters(final[index], regions[index]), ('Character change', index + 1)
        characters_preserved.append(index + 1)
        diff = ImageChops.difference(raster(original[index]), raster(final[index]))
        mask = ImageDraw.Draw(diff)
        for x0, y0, x1, y1 in regions[index]:
            mask.rectangle((math.floor(x0 * 1.5) - 3, math.floor(y0 * 1.5) - 3,
                            math.ceil(x1 * 1.5) + 3, math.ceil(y1 * 1.5) + 3), fill='black')
        assert diff.getbbox() is None, ('Unexpected rendering change', index + 1, diff.getbbox())

    objects = '\n'.join(final.xref_object(index) for index in range(1, final.xref_length()))
    text = '\n'.join(page.get_text() for page in final)
    assert final.embfile_count() == 0
    assert not re.search(r'/S\s*/(?:Launch|JavaScript)|/OpenAction\b|/EmbeddedFile\b|/(?:Users|home|private)/|mailto:|chatgpt\.com/share/', objects)
    assert not re.search(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', text + objects, re.I)
    assert not any(term in re.sub(r'\s+', '', text) for term in ['03:04', '00:16', 'KST수신', '나중에첨부하기위한준비자료'])
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for index, page in enumerate(final):
        raster(page).save(args.qa_dir / f'public-page-{index + 1:02d}.png')
    (ROOT / 'output/pdf').mkdir(parents=True, exist_ok=True)
    (ROOT / 'output/pdf/supplement.pdf').write_bytes(output.read_bytes())
    report = {
        'date': EDITION_DATE, 'source_sha256': SOURCE_SHA256,
        'public_sha256': digest(output), 'source_pages': 8, 'public_pages': 8,
        'public_bytes': output.stat().st_size, 'file': 'supplement.pdf',
        'edited_and_added_regions': {str(index + 1): boxes for index, boxes in regions.items() if boxes},
        'unchanged_original_page_regions_pixel_equal': True,
        'original_page_characters_outside_edits_preserved': characters_preserved,
        'internal_named_destinations_preserved': len(names),
        'original_link_annotations_preserved': len(links),
        'original_public_uris_preserved': sum('uri' in link for page in original for link in page.get_links()),
        'embedded_files': 0, 'launch_or_script_actions': 0, 'default_open_action_removed': True,
        'privacy_edits': ['Private receipt/collection metadata generalized on page 1.',
                          'Private source provenance generalized under S001 on page 8.',
                          'Preparation-only status replaced by neutral public supplement relationship on page 8.'],
        'package_scope_edit': 'Page 8 describes the public PDF, concise web guide, unchanged notebooks and data, CSV, audit code/results, licenses, sources and hashes; no duplicate full HTML or internal integration instructions are claimed.',
        'publication_disclosure': 'Page 8 records responsible editor, Codex assistance, faryad_pdf_review preservation/privacy/link/render QA, root integration and no human manuscript review.',
        'execution_scope': 'Original calculation and inspection claims remain their original production record. No notebook or QPU experiment was rerun in this public PDF preparation.',
        'navigation': {'mapping_pdf_page': 2, 'errata_pdf_page': 3,
                       'qaoa_budget_pdf_page': 4, 'comparison_scope_pdf_page': 5,
                       'ledger_audit_pdf_page': 6, 'exercises_pdf_page': 7,
                       'source_scope_pdf_page': 8},
    }
    (ROOT / 'reports').mkdir(exist_ok=True)
    (ROOT / 'reports/pdf-publication-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'pages': 8, 'sha256': report['public_sha256'],
                      'bytes': report['public_bytes'], 'preserved_links': len(links)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
