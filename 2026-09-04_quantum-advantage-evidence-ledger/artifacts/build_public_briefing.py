"""Regenerate the reviewed public edition of the 4 September 2026 DQB.

Supply the private original PDF, Korean regular/bold fonts, a Unicode
reference font and an external QA directory. Originals are hash-checked.
The builder performs true text redactions, bounded scientific corrections
and an explicitly dated ATRL appendix. It does not register or publish files.
Rebuilding invalidates visual review; inspect every rendered page afterwards.
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
MANIFEST = ROOT / 'reports/briefing-publication-manifest.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bitmap(page):
    p = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes('RGB', (p.width, p.height), p.samples)


def source_lines(page):
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            spans = line['spans']
            yield {'text': ''.join(s['text'] for s in spans), 'bbox': line['bbox'],
                   'origin': spans[0]['origin'], 'size': spans[0]['size'], 'color': spans[0]['color']}


def font_runs(text, regular, reference):
    out = []
    for ch in text:
        face = 'DqbRegular' if regular.has_glyph(ord(ch)) else 'DqbReference'
        font = regular if face == 'DqbRegular' else reference
        if not font.has_glyph(ord(ch)):
            raise ValueError(f'Unsupported glyph {ch!r}')
        if out and out[-1][0] == face:
            out[-1] = (face, out[-1][1] + ch)
        else:
            out.append((face, ch))
    return out


def normalize_cmaps(doc):
    changed, seen = 0, set()
    for xref in range(1, doc.xref_length()):
        kind, value = doc.xref_get_key(xref, 'ToUnicode')
        if kind != 'xref':
            continue
        cmap = int(value.split()[0])
        if cmap in seen:
            continue
        seen.add(cmap)
        before = doc.xref_stream(cmap)
        def utf16(match):
            return b'<' + chr(int(match.group(1), 16)).encode('utf-16-be').hex().encode('ascii') + b'>'
        after, count = re.subn(rb'<([0-9A-Fa-f]{5,6})>', utf16, before)
        if count:
            doc.update_stream(cmap, after)
            changed += count
    return changed


def appendix(issue, regular, bold, reference):
    for name, path in [('DqbRegular', regular), ('DqbBold', bold), ('DqbReference', reference)]:
        pdfmetrics.registerFont(TTFont(name, str(path)))
    width, height = A4
    buffer = io.BytesIO()
    canvas = Canvas(buffer, pagesize=A4, invariant=1)
    y, number, bottoms = height - 45, 1, []
    def mixed(text):
        face = pdfmetrics.getFont('DqbRegular').face
        return ''.join(escape(ch) if ord(ch) in face.charToGlyph else
                       f'<font name="DqbReference">{escape(ch)}</font>' for ch in text)
    def paragraph(text, size=10, leading=15, bold=False, after=8, reference=False):
        nonlocal y
        style = ParagraphStyle('p', fontName='DqbReference' if reference else ('DqbBold' if bold else 'DqbRegular'),
                               fontSize=size, leading=leading, textColor=HexColor('#263a47'), wordWrap='CJK')
        p = Paragraph(text if reference else mixed(text), style)
        _, h = p.wrap(width - 106, height)
        if y - h < 63:
            footer()
            heading('공개 감수 부록 · 계속')
        y -= h
        p.drawOn(canvas, 53, y)
        y -= after
    def footer():
        nonlocal number
        if y < 56:
            raise ValueError('Appendix overflow')
        bottoms.append(y)
        canvas.setStrokeColor(HexColor('#c9d8dc'))
        canvas.line(53, 41, width - 53, 41)
        canvas.setFont('DqbRegular', 7.5)
        canvas.setFillColor(HexColor('#60717d'))
        canvas.drawString(53, 28, 'AGENTIC TECH REVIEW LETTERS / 2026-11-15')
        canvas.drawRightString(width - 53, 28, 'A' + str(number))
        number += 1
        canvas.showPage()
    def heading(title):
        nonlocal y
        y = height - 43
        paragraph('DAILY QUANTUM BRIEF / ' + issue['date'], 9, 12, after=8)
        paragraph(title, 18, 23, bold=True, after=12)
    heading('공개 감수본 · 정정과 조건 보완')
    paragraph(issue['edition_intro'])
    for note in issue['edition_notes']:
        paragraph(note)
    paragraph(issue['production_disclosure'], 8.5, 12, after=0)
    footer()
    heading('참고문헌 · 최초 등장 순서')
    for row in issue['references']:
        text = escape(row['citation'])
        loc = escape(row['locator'])
        if text.count(loc) != 1 or not row['url'].startswith('https://'):
            raise ValueError('Reference needs one exact public locator')
        for link in [{'locator': row['locator'], 'url': row['url']}] + row.get('additional_locators', []):
            locator = escape(link['locator'])
            if text.count(locator) != 1 or not link['url'].startswith('https://'):
                raise ValueError('Additional source locator must be exact and public')
            text = text.replace(locator, f'<link href="{escape(link["url"])}" color="#007e8c">{locator}</link>')
        paragraph(f'[{row["number"]}] {text}', 9, 13, after=10, reference=True)
    paragraph('원 공개 출처 진입점', 10, 14, bold=True)
    for item in issue['original_entry_points']:
        paragraph(f'<link href="{escape(item["url"])}" color="#007e8c">{escape(item["label"])}</link>', 8.5, 12, after=4, reference=True)
    footer()
    canvas.save()
    return buffer.getvalue(), bottoms


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ['source', 'font-regular', 'font-bold', 'font-reference', 'qa-dir']:
        parser.add_argument('--' + flag, type=Path, required=True)
    args = parser.parse_args()
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    repository = ROOT.parent.resolve()
    for path in [args.source, args.qa_dir]:
        if path.resolve().is_relative_to(repository):
            raise ValueError('Keep originals and QA outside the public repository')
    manifest = json.loads(MANIFEST.read_text())
    if not manifest.get('source_audit_complete'):
        raise ValueError('Independent primary-source review must be complete before public production')
    manifest['review_status'] = 'pending_rebuild_visual_review'
    manifest['review_verification'] = {'status': 'pending_rebuild'}
    manifest.pop('public_outputs', None)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    regular = fitz.Font(fontfile=str(args.font_regular))
    fallback = fitz.Font(fontfile=str(args.font_reference))
    fonts = {'DqbRegular': regular, 'DqbReference': fallback}
    reports = []
    for issue in manifest['issues']:
        source = args.source
        raw = source.read_bytes()
        if sha(raw) != issue['original_sha256']:
            raise ValueError('Unexpected source edition: ' + issue['date'])
        original = fitz.open(stream=raw, filetype='pdf')
        public = fitz.open(stream=raw, filetype='pdf')
        if len(original) != issue['original_pages']:
            raise ValueError('Unexpected original page count')
        edits = {int(k): list(v) for k, v in issue['removals'].items()}
        # Remove complete collection boxes and reference underlines within
        # explicitly declared removal areas, while retaining surrounding artwork.
        for page_index, rectangles in edits.items():
            for rectangle in rectangles:
                public[page_index].add_redact_annot(fitz.Rect(rectangle), fill=None)
            public[page_index].apply_redactions(images=0, graphics=1, text=0)
        pending, matched = [], set()
        for i, page in enumerate(original):
            for line in source_lines(page):
                if any(fitz.Rect(r).contains(fitz.Rect(line['bbox'])) for r in edits.get(i, [])):
                    continue
                hits = [(n, r) for n, r in enumerate(issue['line_replacements'])
                        if r['page'] == i and line['text'] == r['old']]
                if not hits:
                    continue
                if len(hits) != 1 or hits[0][0] in matched:
                    raise ValueError('Ambiguous scientific replacement')
                n, replacement = hits[0]
                matched.add(n)
                size = replacement.get('size', line['size'])
                rr = font_runs(replacement['new'], regular, fallback)
                x, y = line['origin']
                right = replacement.get('right', 538)
                length = sum(fonts[face].text_length(text, fontsize=size) for face, text in rr)
                if x + length > right:
                    raise ValueError(f'{issue["date"]} p{i+1} width {x+length:.2f}>{right}: {replacement["new"]}')
                rect = (line['bbox'][0] - .5, min(line['bbox'][1] - .5, y - size * 1.1),
                        max(line['bbox'][2], x + length) + .6,
                        max(line['bbox'][3] + .5, y + size * .3))
                edits.setdefault(i, []).append(rect)
                pending.append((i, line, size, rr))
        if matched != set(range(len(issue['line_replacements']))):
            raise ValueError('Unmatched corrections: ' + str(set(range(len(issue['line_replacements']))) - matched))
        for i, rects in edits.items():
            for rect in rects:
                public[i].add_redact_annot(fitz.Rect(rect), fill=None)
            public[i].apply_redactions(images=0, graphics=0, text=0)
        # Collection text is truly removed above. Clear only its now-empty
        # decorative frame within the declared removal rectangle.
        for rectangle in issue.get('clear_removed_frames', []):
            public[rectangle['page']].draw_rect(fitz.Rect(rectangle['rect']), color=None, fill=(1, 1, 1), overlay=True)
        for i, line, size, rr in pending:
            x, y = line['origin']
            color = tuple(((line['color'] >> k) & 255) / 255 for k in (16, 8, 0))
            for face, path in [('DqbRegular', args.font_regular), ('DqbReference', args.font_reference)]:
                if any(f == face for f, _ in rr):
                    public[i].insert_font(fontname=face, fontfile=str(path))
            for face, value in rr:
                public[i].insert_text((x, y), value, fontname=face, fontsize=size, color=color)
                x += fonts[face].text_length(value, fontsize=size)
        for item in issue.get('inserts', []):
            page = public[item['page']]
            page.insert_font(fontname='DqbRegular', fontfile=str(args.font_regular))
            page.insert_text(tuple(item['origin']), item['text'], fontname='DqbRegular',
                             fontsize=item.get('size', 9), color=(0, .49, .55))
            edits.setdefault(item['page'], []).append(item['rectangle'])
        original_links = [link['uri'] for page in original for link in page.get_links() if 'uri' in link]
        if any(not uri.startswith('https://') for uri in original_links):
            raise ValueError('Original URI requires manual review')
        if set(original_links) != {row['url'] for row in issue['original_entry_points']}:
            raise ValueError('Original source entry points must be explicitly reviewed')
        note, bottoms = appendix(issue, args.font_regular, args.font_bold, args.font_reference)
        public.insert_pdf(fitz.open(stream=note, filetype='pdf'))
        metadata = dict(original.metadata)
        metadata.update({'author': '', 'creator': 'Agentic Tech Review Letters public edition builder',
                         'subject': 'Reviewed public edition; original issue date ' + issue['date'],
                         'modDate': 'D:20261115000000Z'})
        public.set_metadata({k: v for k, v in metadata.items() if k not in ('format', 'encryption') and v is not None})
        public.del_xml_metadata()
        for i in range(public.embfile_count() - 1, -1, -1):
            public.embfile_del(i)
        public.subset_fonts()
        normalized = normalize_cmaps(public)
        output = Path(__file__).with_name(issue['filename'])
        public.save(output, garbage=4, deflate=True, no_new_id=True)
        final = fitz.open(output)
        pixels = []
        for i in range(len(original)):
            diff = ImageChops.difference(bitmap(original[i]), bitmap(final[i]))
            for x0, y0, x1, y1 in edits.get(i, []):
                ImageDraw.Draw(diff).rectangle((math.floor((x0-1)*2), math.floor((y0-1)*2),
                                               math.ceil((x1+1)*2), math.ceil((y1+1)*2)), fill=(0, 0, 0))
            if diff.getbbox() is not None:
                raise ValueError(f'Undeclared pixel change {issue["date"]} p{i+1}')
            pixels.append({'page': i+1, 'pixels_identical_outside_declared_edits_144dpi': True, 'rectangles': edits.get(i, [])})
        text = '\n'.join(p.get_text() for p in final)
        objects = '\n'.join(final.xref_object(i, compressed=False) for i in range(1, final.xref_length()))
        uris = [a['uri'] for p in final for a in p.get_links() if 'uri' in a]
        expected = set(original_links + [r['url'] for r in issue['references']] + [link['url'] for row in issue['references'] for link in row.get('additional_locators', [])])
        checks = {'source_pages_preserved': len(final) == len(original) + len(bottoms),
                  'no_collection_notes': not any(s in text for s in ('수집 메모', 'Community 메일', 'Slack 초대', '지난 확인 이후', 'accepted QML 본논문', '뉴스레터·소셜 확인', 'Classiq challenge', 'webinar 초청', 'LinkedIn')),
                  'no_email': not bool(re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text + objects)),
                  'no_private_paths': not bool(re.search(r'/(?:Users|home|private|tmp)/|file://|localhost', text + objects, re.I)),
                  'no_missing_glyphs': '\x00' not in text and '\ufffd' not in text,
                  'no_xml_metadata': not final.get_xml_metadata(), 'no_embedded_files': final.embfile_count() == 0,
                  'no_widgets': not any(list(p.widgets() or []) for p in final),
                  'no_active_actions': not bool(re.search(r'/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm|GoToR|RichMedia)\b', objects)),
                  'source_uris_retained': set(original_links).issubset(set(uris)), 'uri_allowlist': set(uris) == expected,
                  'original_title_preserved': final.metadata['title'] == original.metadata['title'],
                  'original_issue_date_preserved': issue['date'] in text,
                  'appendix_revision_date': '2026-11-15' in text}
        from pypdf import PdfReader
        strict = PdfReader(output, strict=True)
        for page in strict.pages:
            page.extract_text()
        checks['strict_parser_all_pages'] = len(strict.pages) == len(final)
        if not all(checks.values()):
            raise ValueError(checks)
        folder = args.qa_dir / issue['date']
        folder.mkdir(parents=True, exist_ok=True)
        for i, page in enumerate(final):
            page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(str(folder / f'public-{i+1}.png'))
        (folder / 'public-text.txt').write_text(text)
        report = {'date': issue['date'], 'source_sha256': issue['original_sha256'], 'sha256': sha(output.read_bytes()),
                  'pages': len(final), 'source_pages': len(original), 'inspection': checks, 'pixel_checks': pixels,
                  'uris': uris, 'metadata': final.metadata, 'appendix_bottom_pt': bottoms,
                  'cmap_destinations_normalized': normalized, 'visual_qa': {'status': 'pending_every_page_review'},
                  'independent_experimental_reproduction': False}
        (folder / 'production-qa.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        import shutil
        for destination in [ROOT / 'dist' / output.name, ROOT / 'dist/en' / output.name]:
            shutil.copyfile(output, destination)
        reports.append({'date': issue['date'], 'filename': output.name, 'pages': len(final), 'sha256': report['sha256']})
    print(json.dumps(reports, ensure_ascii=False))

if __name__ == '__main__':
    main()
