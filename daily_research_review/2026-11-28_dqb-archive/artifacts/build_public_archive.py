"""Build the reviewed 2026-11-28 DQB public derivative.

The private source PDF, fonts and private QA destination are caller supplied.
This performs actual text redaction, preserves the scientific pages and adds
the reviewed ATRL notes. It does not register, publish or approve the result.
Every rebuild resets visual and independent review to pending.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
from xml.sax.saxutils import escape

import fitz
from PIL import Image, ImageChops, ImageDraw
from pypdf import PdfReader
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'artifacts/public-archive-manifest.json'
SOURCE_SHA256 = '83a0fde46e663856735084f6abb516524f66b5c24bc2b35337f461afb1cbfc30'

sys.path.insert(0, str(ROOT.parents[1]))
from scripts.ai_model_provenance import render_disclosure, validate_public_provenance


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bitmap(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def appendix(manifest, regular, bold, reference):
    for name, path in [('DqbRegular', regular), ('DqbBold', bold), ('DqbReference', reference)]:
        pdfmetrics.registerFont(TTFont(name, str(path)))
    face = pdfmetrics.getFont('DqbRegular').face
    fallback = pdfmetrics.getFont('DqbReference').face
    out = io.BytesIO()
    canvas = Canvas(out, pagesize=A4, invariant=1)
    width, height = A4
    y = height - 43
    page_number = 3
    bottoms = []

    def mixed(text):
        result = []
        for char in text:
            if ord(char) in face.charToGlyph:
                result.append(escape(char))
            elif ord(char) in fallback.charToGlyph:
                result.append('<font name="DqbReference">' + escape(char) + '</font>')
            else:
                raise ValueError('Missing public glyph: ' + repr(char))
        return ''.join(result)

    def paragraph(text, size=9.3, leading=13.4, after=7, strong=False, reference_text=False):
        nonlocal y
        style = ParagraphStyle('p', fontName='DqbReference' if reference_text else ('DqbBold' if strong else 'DqbRegular'),
                               fontSize=size, leading=leading, textColor=HexColor('#263a47'),
                               wordWrap=None if reference_text else 'CJK')
        content = text if reference_text else mixed(text)
        p = Paragraph(content, style)
        _, box_height = p.wrap(width - 110, height)
        if y - box_height < 58:
            raise ValueError('Appendix overflow on page ' + str(page_number))
        y -= box_height
        p.drawOn(canvas, 55, y)
        y -= after

    def fits(text, size=9.3, leading=13.4, after=7):
        p = Paragraph(mixed(text), ParagraphStyle('measure', fontName='DqbRegular', fontSize=size,
                                                leading=leading, wordWrap='CJK'))
        return p.wrap(width - 110, height)[1] + after <= y - 58

    def footer():
        nonlocal page_number
        bottoms.append(y)
        canvas.setStrokeColor(HexColor('#cadadd'))
        canvas.line(55, 40, width - 55, 40)
        canvas.setFont('DqbRegular', 7.5)
        canvas.setFillColor(HexColor('#60717d'))
        canvas.drawString(55, 27, 'AGENTIC TECH REVIEW LETTERS / PUBLIC EDITION')
        canvas.drawRightString(width - 55, 27, str(page_number))
        canvas.showPage()
        page_number += 1

    def heading(title):
        nonlocal y
        y = height - 43
        paragraph('DAILY QUANTUM BRIEF / 2026-11-28', 9, 12, after=8)
        paragraph(title, 18, 24, after=12, strong=True)

    heading('공개 편집주 · 계산 조건과 개정 기록')
    paragraph(manifest['editorial_credit'], 8.6, 12.4, after=10)
    for note in manifest['edition_notes']:
        if not fits(note):
            footer()
            heading('계산 조건 · 계속')
        paragraph(note)
    footer()
    heading('참고문헌과 작성·검토 범위')
    for row in manifest['references']:
        citation = escape(row['citation'])
        for item in [{'locator': row['locator'], 'url': row['url']}] + row.get('additional_links', []):
            locator = escape(item['locator'])
            if citation.count(locator) != 1 or not item['url'].startswith('https://'):
                raise ValueError('Ambiguous or non-public source citation')
            citation = citation.replace(locator, '<link href="' + escape(item['url']) + '" color="#007e8c">' + locator + '</link>')
        paragraph('[' + str(row['number']) + '] ' + citation, 9.4, 13.6, after=11, reference_text=True)
    paragraph(manifest['production_disclosure'], 8.6, 12.4, after=11)
    paragraph(manifest['rights_note'], 8.4, 12.2, after=0)
    footer()
    canvas.save()
    return out.getvalue(), bottoms


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source-pdf', 'font-regular', 'font-bold', 'font-reference', 'qa-dir'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    provenance_path = ROOT / manifest['ai_provenance']
    provenance_bytes = provenance_path.read_bytes()
    provenance = validate_public_provenance(json.loads(provenance_bytes))
    token = '{{AI_MODEL_DISCLOSURE}}'
    if manifest['production_disclosure'].count(token) != 1:
        raise ValueError('Expected exactly one saved-provenance disclosure token')
    manifest['production_disclosure'] = manifest['production_disclosure'].replace(token, render_disclosure(provenance, 'ko').replace(chr(96), ''))
    if [r['number'] for r in manifest['references']] != list(range(1, 5)):
        raise ValueError('APS references must follow scientific first use')
    repository = ROOT.parents[1].resolve()
    for path in (args.source_pdf, args.qa_dir):
        if path.resolve().is_relative_to(repository):
            raise ValueError('Private original and QA must stay outside the public repository')
    public_qa = ROOT / 'artifacts/public-pdf-qa.json'
    if public_qa.exists():
        prior = json.loads(public_qa.read_text())
        prior.update(visual_qa={'status': 'pending_rebuild'}, independent_review={'status': 'pending_rebuild'})
        public_qa.write_text(json.dumps(prior, ensure_ascii=False, indent=2) + '\n')
    if not manifest.get('source_audit_complete') or any('PENDING' in str(manifest.get(k, '')) for k in ('edition_notes','references','production_disclosure','rights_note','editorial_credit')):
        raise ValueError('Source review and editorial text must be finalized before PDF generation')
    raw = args.source_pdf.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise ValueError('Input differs from the reviewed original')
    original = fitz.open(stream=raw, filetype='pdf')
    public = fitz.open(stream=raw, filetype='pdf')
    if len(original) != 2:
        raise ValueError('Expected two original pages')
    removals = {int(k): v for k, v in manifest['redaction_regions'].items()}
    removed_text = []
    for index, rectangles in removals.items():
        for rectangle in rectangles:
            rect = fitz.Rect(rectangle)
            removed_text.append(original[index].get_textbox(rect))
            public[index].add_redact_annot(rect, fill=None)
        public[index].apply_redactions(images=0, graphics=0, text=0)
    for row in manifest.get('text_replacements', []):
        public[row['page']].insert_text(tuple(row['origin']), row['replacement'], fontsize=row['font_size'], fontfile=str(args.font_regular), fontname='DqbSourceReplacement', color=tuple(row['color']))
    extra, bottoms = appendix(manifest, args.font_regular, args.font_bold, args.font_reference)
    public.insert_pdf(fitz.open(stream=extra, filetype='pdf'))
    metadata = dict(original.metadata)
    metadata.update(title=metadata['title'] + ' | Public archive edition', subject=manifest['pdf_subject'],
                    creator='Agentic Tech Review Letters public archive builder',
                    modDate=datetime.now(timezone.utc).strftime('D:%Y%m%d%H%M%SZ'))
    metadata.pop('format', None)
    metadata.pop('encryption', None)
    public.set_metadata(metadata)
    public.del_xml_metadata()
    public.subset_fonts()
    cmap_repairs = []
    seen_maps = set()
    for font_xref in range(1, public.xref_length()):
        object_text = public.xref_object(font_xref, compressed=False)
        for map_text in re.findall(r'/ToUnicode\s+(\d+)\s+0\s+R', object_text):
            map_xref = int(map_text)
            if map_xref in seen_maps:
                continue
            seen_maps.add(map_xref)
            before = public.xref_stream(map_xref)
            values = re.findall(rb'<([0-9a-fA-F]{5,6})>', before)
            if not values:
                continue
            if b'/CMapType 2' not in before or not all(0x10000 <= int(x, 16) <= 0x10ffff for x in values):
                raise ValueError('Unexpected supplementary Unicode target in font map')
            ranges = re.findall(rb'(?m)^[ \t]*<([0-9a-fA-F]{4})>[ \t]+<([0-9a-fA-F]{4})>[ \t]+<([0-9a-fA-F]{5,6})>[ \t]*$', before)
            for first, last, codepoint in ranges:
                count = int(last, 16) - int(first, 16) + 1
                if not 0 < count <= 1024 or (int(codepoint, 16) - 0x10000) % 1024 + count > 1024:
                    raise ValueError('Supplementary font-map range needs an explicit array')
            def encode_target(match):
                return b'<' + chr(int(match.group(1), 16)).encode('utf-16-be').hex().encode('ascii') + b'>'
            after = re.sub(rb'<([0-9a-fA-F]{5,6})>', encode_target, before)
            if re.search(rb'<[0-9a-fA-F]{5,6}>', after):
                raise ValueError('Incomplete supplementary font-map normalization')
            public.update_stream(map_xref, after)
            cmap_repairs.append({'target_values': len(values), 'ranges': len(ranges),
                                 'before_sha256': sha(before), 'after_sha256': sha(after),
                                 'same_Unicode_mapping_with_standard_UTF16BE': True,
                                 'page_content_and_glyph_programs_changed': False})
    path = ROOT / 'dist/2026-11-28-daily-quantum-brief.pdf'
    public.save(path, garbage=4, deflate=True, no_new_id=True)
    final = fitz.open(path)
    strict = PdfReader(str(path), strict=True)
    text = '\n'.join(p.get_text() for p in final)
    objects = '\n'.join(final.xref_object(x, compressed=False) for x in range(1, final.xref_length()))
    original_links = [a['uri'] for p in original for a in p.get_links() if 'uri' in a]
    links = [a['uri'] for p in final for a in p.get_links() if 'uri' in a]
    retained = [a['uri'] for p in list(final)[:2] for a in p.get_links() if 'uri' in a]
    expected = Counter(original_links + [u for r in manifest['references'] for u in [r['url']] + [x['url'] for x in r.get('additional_links', [])]])
    checks = []
    for index in range(2):
        diff = ImageChops.difference(bitmap(original[index]), bitmap(final[index]))
        for x0, y0, x1, y1 in removals.get(index, []):
            ImageDraw.Draw(diff).rectangle((math.floor((x0 - 1)*2), math.floor((y0 - 1)*2),
                                           math.ceil((x1 + 1)*2), math.ceil((y1 + 1)*2)), fill=(0, 0, 0))
        if diff.getbbox() is not None:
            raise ValueError('Unexpected scientific-page pixel change: ' + str(index + 1))
        checks.append({'page': index + 1, 'pixels_identical_outside_declared_edits_144dpi': True,
                       'edit_rectangles': removals.get(index, [])})
    removed_tokens = ('검증 체크리스트와 수집 범위', 'Gmail', 'LinkedIn', '지난 발송 이후', '비공개 피드')
    predicates = {
        'strict_independent_parser': len(strict.pages) == len(final),
        'no_private_collection_context': not any(t in text for t in removed_tokens) and '\uB274\uC2A4\uB808\uD130 \uC218\uC2E0' not in text,
        'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
        'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
        'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
        'no_xml_metadata': not final.get_xml_metadata(),
        'no_embedded_files': final.embfile_count() == 0 and not strict.attachments,
        'not_encrypted': not final.is_encrypted and not strict.is_encrypted,
        'no_widgets': not any(list(p.widgets() or []) for p in final),
        'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm|GoToR|RichMedia|XFA)\b', objects)),
        'expected_source_uri_counts': Counter(links) == expected,
        'all_10_original_uri_annotations_retained': len(retained) == 10 and Counter(retained) == Counter(original_links),
        'https_only': all(u.startswith('https://') for u in links),
        'source_name_credit_retained': final.metadata['author'] == original.metadata['author'],
        'issue_date_preserved': all('2026.11.28' in final[i].get_text() for i in range(2)),
        'original_images_retained': all([(im[2:6], sha(original.extract_image(im[0])['image'])) for im in original[i].get_images()] == [(im[2:6], sha(final.extract_image(im[0])['image'])) for im in final[i].get_images()] for i in range(2)),
        'source_audit_complete': bool(manifest['source_audit_complete']),
        'expected_page_count': len(final) == 2 + len(bottoms),
        'saved_provenance_auto_referenced': bool(provenance['roles']) and 'GPT-6.1 Sol' in text and 'gpt-6.1-sol' in text and 'ultra' in text,
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for index, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / ('public-' + str(index + 1) + '.png')))
    report = {'date': '2026-11-28', 'source_sha256': SOURCE_SHA256,
              'ai_provenance_sha256': sha(provenance_bytes), 'ai_provenance_file': manifest['ai_provenance'],
              'font_ToUnicode_UTF16BE_normalization': cmap_repairs, 'sha256': sha(path.read_bytes()),
              'source_pages': 2, 'pages': len(final), 'file_size_bytes': path.stat().st_size,
              'page_checks': checks, 'inspection': predicates, 'reference_urls': links,
              'original_uri_count': len(original_links), 'original_unique_uri_count': len(set(original_links)),
              'appendix_bottom_pt': bottoms, 'metadata': final.metadata,
              'visual_qa': {'status': 'pending'}, 'independent_review': {'status': 'pending'},
              'independent_reproduction': False}
    public_qa.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    private = dict(report, private_removed_text=removed_text)
    (args.qa_dir / 'production-qa.json').write_text(json.dumps(private, ensure_ascii=False, indent=2) + '\n')
    (args.qa_dir / 'public-full.txt').write_text(text)
    print(json.dumps({'output': path.name, 'pages': len(final), 'sha256': report['sha256'],
                      'bytes': report['file_size_bytes'], 'appendix_bottom_pt': bottoms}))


if __name__ == '__main__':
    main()
