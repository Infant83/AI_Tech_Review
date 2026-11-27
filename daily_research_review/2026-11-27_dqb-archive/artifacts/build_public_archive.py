"""Build the reviewed 2026-11-27 DQB public derivative.

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
SOURCE_SHA256 = '53c6fba5e68656fe8d61ba60e1cc9a4c1f61642cb2354c594bb409eeaf98b75e'


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
    page_number = 4
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
        paragraph('DAILY QUANTUM BRIEF / 2026-11-27', 9, 12, after=8)
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
        locator = escape(row['locator'])
        if citation.count(locator) != 1 or not row['url'].startswith('https://'):
            raise ValueError('Ambiguous or non-public source citation')
        citation = citation.replace(locator, '<link href="' + escape(row['url']) + '" color="#007e8c">' + locator + '</link>')
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
    if [r['number'] for r in manifest['references']] != list(range(1, 6)):
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
    raw = args.source_pdf.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise ValueError('Input differs from the reviewed original')
    original = fitz.open(stream=raw, filetype='pdf')
    public = fitz.open(stream=raw, filetype='pdf')
    if len(original) != 3:
        raise ValueError('Expected three original pages')
    removals = {int(k): v for k, v in manifest['redaction_regions'].items()}
    removed_text = []
    for index, rectangles in removals.items():
        for rectangle in rectangles:
            rect = fitz.Rect(rectangle)
            removed_text.append(original[index].get_textbox(rect))
            public[index].add_redact_annot(rect, fill=None)
        public[index].apply_redactions(images=0, graphics=0, text=0)
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
    path = ROOT / 'dist/2026-11-27-daily-quantum-brief.pdf'
    public.save(path, garbage=4, deflate=True, no_new_id=True)
    final = fitz.open(path)
    strict = PdfReader(str(path), strict=True)
    text = '\n'.join(p.get_text() for p in final)
    objects = '\n'.join(final.xref_object(x, compressed=False) for x in range(1, final.xref_length()))
    original_links = [a['uri'] for p in original for a in p.get_links() if 'uri' in a]
    links = [a['uri'] for p in final for a in p.get_links() if 'uri' in a]
    retained = [a['uri'] for p in list(final)[:3] for a in p.get_links() if 'uri' in a]
    expected = Counter(original_links + [r['url'] for r in manifest['references']])
    checks = []
    for index in range(3):
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
        'no_private_collection_context': not any(t in text for t in removed_tokens),
        'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
        'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
        'no_null_or_replacement_glyphs': '\x00' not in text and '\ufffd' not in text,
        'no_xml_metadata': not final.get_xml_metadata(),
        'no_embedded_files': final.embfile_count() == 0 and not strict.attachments,
        'not_encrypted': not final.is_encrypted and not strict.is_encrypted,
        'no_widgets': not any(list(p.widgets() or []) for p in final),
        'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm|GoToR|RichMedia|XFA)\b', objects)),
        'expected_source_uri_counts': Counter(links) == expected,
        'all_13_original_uri_annotations_retained': len(retained) == 13 and Counter(retained) == Counter(original_links),
        'https_only': all(u.startswith('https://') for u in links),
        'source_name_credit_retained': final.metadata['author'] == 'Daily Quantum Brief',
        'issue_date_preserved': all('2026.11.27' in final[i].get_text() for i in range(3)),
        'original_images_retained': all([im[7] for im in original[i].get_images()] == [im[7] for im in final[i].get_images()] for i in range(3)),
        'source_audit_complete': bool(manifest['source_audit_complete']),
        'expected_page_count': len(final) == 3 + len(bottoms),
    }
    if not all(predicates.values()):
        raise ValueError(predicates)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for index, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(args.qa_dir / ('public-' + str(index + 1) + '.png')))
    report = {'date': '2026-11-27', 'source_sha256': SOURCE_SHA256, 'sha256': sha(path.read_bytes()),
              'source_pages': 3, 'pages': len(final), 'file_size_bytes': path.stat().st_size,
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
