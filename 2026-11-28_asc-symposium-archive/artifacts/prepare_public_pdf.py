"""Prepare an ASC archival PDF from reviewed inputs, preserving its original pages.

The received source and its source-page renders remain private. This helper only
changes metadata and local-file annotations, then appends approved scope/credit
pages. It does not execute the author's source package or scientific programs.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

import fitz
from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
IDENTIFIER = '2026-11-28-asc-symposium2026-notes-ko'
TITLE = 'ASC Symposium 2026: 원자·분자 계산과 AI 연구 노트'
SOURCE_PAGES = 44
PRIVATE_MARKERS = (r'/Users/', r'file://', r'archive/private/', r'(?i)mailto:',
                   r'[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
                   r'(?i)https?://[^\s]*(?:zoom\.us|teams\.microsoft|meet\.google)')
ACTION_PATTERNS = {'Launch': r'/S\s*/Launch\b', 'JavaScript': r'/S\s*/JavaScript\b',
                   'OpenAction': r'/OpenAction\b', 'GoToR': r'/S\s*/GoToR\b',
                   'EmbeddedFile': r'/EmbeddedFile\b', 'AA': r'/AA\b',
                   'AcroForm': r'/AcroForm\b'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(document):
    return {key: (value['page'], tuple(value['to']), value.get('zoom', 0))
            for key, value in document.resolve_names().items()}


def named_links(document, limit):
    return [(i, link['kind'], tuple(link['from']), link.get('nameddest'),
             link.get('page'), tuple(link.get('to', [])), link.get('zoom'))
            for i in range(limit) for link in document[i].get_links()
            if link['kind'] == fitz.LINK_NAMED]


def image_streams(document, limit):
    return [(i, item[2:9], hashlib.sha256(document.xref_stream(item[0])).hexdigest())
            for i in range(limit) for item in document[i].get_images(full=True)]


def public_model(path, role):
    spec = importlib.util.spec_from_file_location('asc_saved_model', REPO / 'scripts/ai_model_provenance.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    record = module.validate_public_provenance(json.loads(path.read_text(encoding='utf-8')))
    assert any(row['role'] == role for row in record['roles']), 'Required model role missing'
    return record, module.render_disclosure(record, 'ko').replace('`', '')


def private_qa_path(path):
    absolute = path.resolve()
    if absolute.is_relative_to(REPO / 'archive/private'):
        return True
    return not any((parent / '.git').exists() for parent in (absolute, *absolute.parents))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--expected-source-sha256', required=True)
    parser.add_argument('--source-render-dir', required=True, type=Path)
    parser.add_argument('--appendix', required=True, type=Path)
    parser.add_argument('--font', required=True, type=Path)
    parser.add_argument('--original-ai-provenance', required=True, type=Path)
    parser.add_argument('--ai-provenance', required=True, type=Path)
    parser.add_argument('--qa-dir', required=True, type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-f0-9]{64}', args.expected_source_sha256):
        parser.error('Expected source SHA256 must be 64 lowercase hexadecimal characters')
    if not private_qa_path(args.qa_dir) or args.qa_dir.exists():
        parser.error('QA output must be a fresh private directory')
    assert digest(args.source) == args.expected_source_sha256, 'Unexpected source edition'
    manifest = json.loads((args.source_render_dir / 'manifest.json').read_text())
    assert manifest['source_sha256'] == args.expected_source_sha256
    assert manifest['pages'] == SOURCE_PAGES and manifest['engine'] == 'pdftoppm' and manifest['dpi'] == 108
    for name, expected in manifest['image_sha256'].items():
        assert digest(args.source_render_dir / name) == expected
    assert len(manifest['image_sha256']) == SOURCE_PAGES
    appendix = json.loads(args.appendix.read_text(encoding='utf-8'))
    pages = appendix['pages']
    assert isinstance(pages, list) and len(pages) >= 2
    scope_index = next(i for i, value in enumerate(pages) if value['kind'] == 'scope')
    credit_index = next(i for i, value in enumerate(pages) if value['kind'] == 'credits')
    original_record, original_text = public_model(args.original_ai_provenance, 'authoring')
    archival_record, archival_text = public_model(args.ai_provenance, 'editing')
    font = fitz.Font(fontfile=str(args.font))
    combined = '\n'.join(value['body'] for value in pages)
    assert combined.count('{{ORIGINAL_MODEL_DISCLOSURE}}') == 1
    assert combined.count('{{ARCHIVAL_MODEL_DISCLOSURE}}') == 1
    prepared_pages = []
    for index, value in enumerate(pages):
        body = value['body'].replace('{{ORIGINAL_MODEL_DISCLOSURE}}', original_text)
        body = body.replace('{{ARCHIVAL_MODEL_DISCLOSURE}}', archival_text)
        footer = f'공개 안내 {index + 1}/{len(pages)} · 전체 PDF {SOURCE_PAGES + index + 1}/{SOURCE_PAGES + len(pages)}'
        prepared_pages.append(dict(value, body=body, footer=footer))
    required_text = ''.join(value['title'] + value['body'] + value['footer'] for value in prepared_pages)
    missing = sorted({char for char in required_text
                      if not char.isspace() and not font.has_glyph(ord(char))})
    assert not missing, ('Appendix font lacks approved characters', missing)
    args.qa_dir.mkdir(parents=True)
    font_subset_path = args.qa_dir / 'appendix-font.otf'
    appendix_font = TTFont(args.font)
    options = subset.Options()
    options.name_IDs = ['*']
    options.name_languages = ['*']
    options.name_legacy = True
    subsetter = subset.Subsetter(options=options)
    required_codepoints = {ord(char) for char in required_text if char not in '\r\n\t'}
    required_codepoints.add(32)
    subsetter.populate(unicodes=required_codepoints)
    subsetter.subset(appendix_font)
    appendix_font.save(font_subset_path)
    subset_font = fitz.Font(fontfile=str(font_subset_path))
    assert all(char.isspace() or subset_font.has_glyph(ord(char)) for char in required_text)
    original = fitz.open(args.source)
    assert len(original) == SOURCE_PAGES
    old_names, old_toc = names(original), original.get_toc()
    old_named_links = named_links(original, SOURCE_PAGES)
    old_images = image_streams(original, SOURCE_PAGES)
    old_text = [page.get_text() for page in original]
    old_public_uris = Counter(link['uri'] for page in original for link in page.get_links()
                              if link['kind'] == fitz.LINK_URI)
    assert len(old_names) == 189 and len(old_toc) == 64 and len(old_images) == 26
    assert len(old_named_links) == 64 and sum(old_public_uris.values()) == 7
    document = fitz.open(args.source)
    for appendix_index, value in enumerate(prepared_pages):
        page = document.new_page(width=595.276, height=841.89)
        page.insert_font(fontname='ArchiveText', fontfile=str(font_subset_path))
        assert page.insert_textbox(fitz.Rect(52, 48, 543, 98), value['title'],
                                  fontname='ArchiveText', fontsize=17,
                                  color=(.08, .21, .29)) >= 0, 'Appendix title overflows'
        body = value['body']
        assert not any(re.search(pattern, body) for pattern in PRIVATE_MARKERS), 'Private appendix marker'
        assert not any(ord(char) < 32 and char not in '\n\t' for char in body)
        assert page.insert_textbox(fitz.Rect(52, 112, 543, 785), body,
                                  fontname='ArchiveText', fontsize=10.5,
                                  lineheight=1.35, color=(.12, .20, .25)) >= 0, 'Appendix body overflows; split the approved text'
        page.insert_text((52, 815), value['footer'],
                         fontname='ArchiveText', fontsize=8.5, color=(.35, .42, .45))
        for link in value.get('links', []):
            assert link['url'].startswith('https://') and not any(re.search(pattern, link['url']) for pattern in PRIVATE_MARKERS)
            rectangles = page.search_for(link['label'])
            assert rectangles, 'Appendix link label missing'
            for rectangle in rectangles:
                page.insert_link({'kind': fitz.LINK_URI, 'from': rectangle, 'uri': link['url']})
    remapped = []
    for index in range(SOURCE_PAGES):
        page = document[index]
        for link in page.get_links():
            if not link.get('file'):
                continue
            target_kind = 'credits' if index == 2 and 'figure_manifest_v2.json' in link['file'] else 'scope'
            target = SOURCE_PAGES + (credit_index if target_kind == 'credits' else scope_index)
            page.delete_link(link)
            page.insert_link({'kind': fitz.LINK_GOTO, 'from': link['from'], 'page': target,
                              'to': fitz.Point(52, 48)})
            remapped.append({'source_page': index + 1, 'public_target': target_kind,
                             'public_target_page': target + 1})
    assert len(remapped) == 13 and sum(row['public_target'] == 'credits' for row in remapped) == 1
    document.set_metadata({'title': TITLE, 'author': '김현중',
                           'subject': 'Independent Korean ASC Symposium2026 study notes; public archival edition2026-11-28',
                           'creator': 'Agentic Tech Review Letters (ATRL); OpenAI Codex-assisted archive',
                           'producer': '', 'keywords': '', 'creationDate': '', 'modDate': ''})
    document.del_xml_metadata()
    catalog = document.pdf_catalog()
    document.xref_set_key(catalog, 'OpenAction', 'null')
    document.update_object(catalog, re.sub(r'\s*/OpenAction\s+null\b', '', document.xref_object(catalog)))
    candidate = args.qa_dir / 'public-candidate.pdf'
    document.save(candidate, garbage=4, deflate=True, clean=False)
    final = fitz.open(candidate)
    assert len(final) == SOURCE_PAGES + len(pages)
    assert names(final) == old_names and final.get_toc() == old_toc
    assert named_links(final, SOURCE_PAGES) == old_named_links
    assert image_streams(final, SOURCE_PAGES) == old_images
    assert [final[i].get_text() for i in range(SOURCE_PAGES)] == old_text
    current_uris = Counter(link['uri'] for i in range(SOURCE_PAGES) for link in final[i].get_links()
                           if link['kind'] == fitz.LINK_URI)
    assert current_uris == old_public_uris
    objects = '\n'.join(final.xref_object(i) for i in range(1, final.xref_length()))
    assert args.expected_source_sha256 not in objects + ''.join(page.get_text() for page in final)
    assert not any(re.search(pattern, objects) for pattern in PRIVATE_MARKERS), 'Private annotation/object marker'
    actions = {label: len(re.findall(pattern, objects)) for label, pattern in ACTION_PATTERNS.items()}
    assert not any(actions.values()), actions
    assert all(not link.get('file') for page in final for link in page.get_links())
    assert all('\x00' not in page.get_text() and '\ufffd' not in page.get_text() for page in final)
    subprocess.run(['pdftoppm', '-r', '108', '-png', str(candidate), str(args.qa_dir / 'page')], check=True)
    pixels_equal = []
    for index in range(SOURCE_PAGES):
        filename = f'page-{index + 1:02d}.png'
        before = Image.open(args.source_render_dir / filename).convert('RGB')
        after = Image.open(args.qa_dir / filename).convert('RGB')
        assert before.size == after.size and ImageChops.difference(before, after).getbbox() is None, ('Original page pixels changed', index + 1)
        pixels_equal.append(index + 1)
    public_sha = digest(candidate)
    report = {'date': '2026-11-28', 'status': 'AUTOMATED_PRESERVATION_PASS_VISUAL_REVIEW_PENDING',
              'document_id': IDENTIFIER, 'original_edition': 'final_v2_illustrated',
              'original_pages': SOURCE_PAGES, 'public_pages': len(final),
              'public_sha256': public_sha, 'public_bytes': candidate.stat().st_size,
              'original_pages_text_and_pixels_equal': pixels_equal,
              'original_images_preserved': len(old_images), 'original_named_destinations_preserved': len(old_names),
              'original_outline_entries_preserved': len(old_toc), 'original_named_link_annotations_preserved': len(old_named_links),
              'original_HTTPS_annotations_preserved': sum(old_public_uris.values()),
              'file_annotations_replaced_with_internal_GoTo': remapped,
              'source_metadata_dates_producer_and_open_action_removed': True,
              'private_contacts_or_paths_found': False, 'action_scan': actions,
              'source_author_model_provenance': original_record, 'archival_model_provenance': archival_record,
              'original_source_package_or_validation_suite_rerun': False,
              'SDK_DFT_QPU_or_physical_execution': False,
              'appendix_font': {'family': subset_font.name,
                                'full_font_bytes': args.font.stat().st_size,
                                'new_subset_font_bytes': font_subset_path.stat().st_size,
                                'required_characters': len(set(required_text)),
                                'original_source_fonts_rewritten': False},
              'appended_scope_and_credit_pages': len(pages), 'full_individual_visual_review': 'pending'}
    (args.qa_dir / 'pdf-build-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'pages': len(final), 'sha256': public_sha,
                      'bytes': candidate.stat().st_size}, ensure_ascii=False))


if __name__ == '__main__':
    main()
