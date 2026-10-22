"""Build the explicitly reviewed DQB public edition from a private source PDF.

The input PDF and QA rasters stay outside the public distribution. Runtime and
font locations are supplied by the caller; no local paths enter the output.
Requires ReportLab and PyMuPDF. This builder does not register or publish files.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

import fitz
import reportlab
from PIL import Image, ImageChops
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph


TOPIC = Path(__file__).resolve().parents[1]
INK = HexColor("#173c4c")
MUTED = HexColor("#526b75")
ACCENT = HexColor("#007e8c")
RULE = HexColor("#c9d9dd")
# Coordinates are in PDF points from the original page's upper-left corner.
# This one block contains the collection heading and collection-route prose.
COLLECTION_RECT = (60.5, 576.0, 538.0, 626.0)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def font_markup(text: str, primary: str) -> str:
    """Preserve Korean, the source's subscript 2, and Mitrić's diacritic."""
    face = pdfmetrics.getFont(primary).face
    fallback = pdfmetrics.getFont("DqbFallback").face
    fragments = []
    for character in text:
        if ord(character) in face.charToGlyph:
            fragments.append(escape(character))
        elif ord(character) in fallback.charToGlyph:
            fragments.append(f'<font name="DqbFallback">{escape(character)}</font>')
        else:
            raise ValueError(f"Font cannot render U+{ord(character):04X}")
    return "".join(fragments)


def make_preface(content: dict) -> tuple[bytes, dict]:
    from reportlab.pdfgen.canvas import Canvas

    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=A4, invariant=1)
    canvas.setTitle(f"Daily Quantum Brief {content['date']} - Editor's preface")
    canvas.setAuthor("Hyun-Jung Kim")
    width, height = A4
    left, right = 53.0, 53.0
    usable = width - left - right
    y = height - 47.0
    layout = []

    def paragraph(text: str, size: float, leading: float, *, bold: bool = False,
                  color=INK, after: float = 0, link: str | None = None) -> None:
        nonlocal y
        font = "DqbBold" if bold else "DqbRegular"
        markup = font_markup(text, font)
        if link:
            markup = f'<link href="{escape(link)}" color="#007e8c">{markup}</link>'
        style = ParagraphStyle("preface", fontName=font, fontSize=size,
                               leading=leading, textColor=color, alignment=TA_LEFT,
                               wordWrap="CJK", splitLongWords=True)
        item = Paragraph(markup, style)
        _, actual_height = item.wrap(usable, height)
        y -= actual_height
        item.drawOn(canvas, left, y)
        layout.append({"font_size": size, "leading": leading,
                       "top": round(height - y - actual_height, 3),
                       "bottom": round(height - y, 3)})
        y -= after

    paragraph(f"DAILY QUANTUM BRIEF / {content['date']}", 8.8, 11, color=ACCENT, after=8)
    paragraph(content["archive_title"], 11.0, 15.0, color=MUTED, after=13)
    paragraph(content["heading"], 18.2, 25.0, bold=True, after=9)
    paragraph(content["label"], 9.0, 12.0, color=ACCENT, after=5)
    paragraph(f"책임 편집 김현중 · AI 보조 Codex · 근거 기준일 {content['date']}",
              8.1, 12.0, color=MUTED, after=11)
    for text in content["paragraphs"]:
        paragraph(text, 10.5, 15.5, after=8.5)
    paragraph(content["next_heading"], 10.5, 14.0, bold=True, color=ACCENT, after=4)
    paragraph(content["next_text"], 10.5, 15.5, after=10)
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(left, y, width - right, y)
    y -= 8
    for source in content["sources"]:
        paragraph(source["label"], 8.0, 11.0, color=MUTED, after=2, link=source["url"])
    y -= 4
    paragraph(content["edition_note"], 8.0, 11.2, color=MUTED, after=5)
    paragraph(content["disclosure"], 7.8, 10.8, color=MUTED, after=3)
    if content.get("methods_url"):
        paragraph("작성·검증 원칙", 7.8, 10.8, color=ACCENT, link=content["methods_url"])
    if y < 48:
        raise ValueError(f"Preface exceeds one page (content bottom {y:.1f} pt)")
    canvas.setStrokeColor(RULE)
    canvas.line(left, 38, width - right, 38)
    canvas.setFillColor(MUTED)
    canvas.setFont("DqbRegular", 7.5)
    canvas.drawString(left, 26, "AI TECH REVIEW / EDITOR'S PREFACE")
    canvas.drawRightString(width - right, 26, "i")
    canvas.showPage()
    canvas.save()
    return stream.getvalue(), {"content_bottom_pt": round(y, 3),
                              "body_font_pt": 10.5, "body_leading_pt": 15.5,
                              "blocks": layout}


def same_render(a: fitz.Page, b: fitz.Page) -> bool:
    pa = a.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pb = b.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return (pa.width, pa.height, pa.samples) == (pb.width, pb.height, pb.samples)


def inspect_pdf(document: fitz.Document) -> dict:
    visible = "\n".join(page.get_text() for page in document)
    metadata = json.dumps(document.metadata, ensure_ascii=False)
    # Test document objects and decoded content streams, not embedded font bytes.
    object_text = []
    content_xrefs = {xref for page in document for xref in page.get_contents()}
    for xref in range(1, document.xref_length()):
        object_text.append(document.xref_object(xref, compressed=False))
        if xref in content_xrefs and document.xref_is_stream(xref):
            object_text.append(document.xref_stream(xref).decode("latin1", errors="replace"))
    structural = "\n".join(object_text)
    checks = {
        "email_addresses_in_text_or_metadata": not bool(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", visible + metadata)),
        "local_paths_in_text_or_metadata": not bool(re.search(r"/(?:Users|home|private|tmp)/|file://|localhost", visible + metadata, re.I)),
        "collection_route_removed": all(term not in visible for term in ("Classiq", "수집 범위", "OpenReview", "LinkedIn", "D-Wave 뉴스레터")),
        "embedded_files_absent": document.embfile_count() == 0,
        "active_actions_absent": not bool(re.search(r"/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile)\b", structural)),
    }
    # These keys express passed checks; a False value always fails the build.
    if not all(checks.values()):
        raise ValueError(f"Public PDF inspection failed: {checks}")
    links = [item["uri"] for page in document for item in page.get_links() if "uri" in item]
    return {"checks_passed": checks, "pages": document.page_count,
            "embedded_files": document.embfile_count(), "uri_annotations": len(links),
            "unique_public_uris": list(dict.fromkeys(links)), "metadata": document.metadata}


def build(args: argparse.Namespace) -> None:
    content_bytes = args.preface.read_bytes()
    content = json.loads(content_bytes)
    for name, path in (("DqbRegular", args.font_regular), ("DqbBold", args.font_bold),
                       ("DqbFallback", args.font_fallback)):
        pdfmetrics.registerFont(TTFont(name, str(path)))
    original = fitz.open(args.source_pdf)
    if original.page_count != 4:
        raise ValueError("This reviewed source must have four pages")
    source_links = [[item["uri"] for item in page.get_links() if "uri" in item] for page in original]
    source_text = original[0].get_text()
    if "수집 범위" not in source_text or "Classiq 메일" not in source_text:
        raise ValueError("Collection block differs from the reviewed source")
    clean_source = fitz.open(stream=original.tobytes(), filetype="pdf")
    clean_source[0].add_redact_annot(fitz.Rect(COLLECTION_RECT), fill=(1, 1, 1))
    clean_source[0].apply_redactions(images=0, graphics=0, text=0)
    preface_pdf, layout = make_preface(content)
    preface = fitz.open(stream=preface_pdf, filetype="pdf")
    output = fitz.open()
    output.insert_pdf(preface)
    output.insert_pdf(clean_source)
    output.set_metadata({"title": f"Daily Quantum Brief {content['date']} - Computational Science Preface",
                         "author": "Hyun-Jung Kim", "subject": content["heading"],
                         "keywords": "Daily Quantum Brief, computational materials, electronic structure, DMFT",
                         "creator": "AI Tech Review public archive builder",
                         "producer": f"ReportLab {reportlab.Version}; PyMuPDF {fitz.VersionBind}"})
    output.del_xml_metadata()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.output, garbage=4, deflate=True)
    output.close()
    final = fitz.open(args.output)
    assert final.page_count == 5
    original_checks = []
    for i in range(4):
        links = [item["uri"] for item in final[i + 1].get_links() if "uri" in item]
        assert links == source_links[i], f"Original source links changed on page {i + 1}"
        item = {"source_page": i + 1, "public_page": i + 2,
                "public_links_preserved": True,
                "original_footer_preserved": f"{i + 1}" in final[i + 1].get_text()}
        if i:
            item["text_identical"] = original[i].get_text() == final[i + 1].get_text()
            item["render_identical_144_dpi"] = same_render(original[i], final[i + 1])
            assert item["text_identical"] and item["render_identical_144_dpi"]
        original_checks.append(item)
    # The original first-page prose is unchanged outside the actual redaction.
    retained_blocks = [block[4] for block in original[0].get_text("blocks")
                       if not fitz.Rect(block[:4]).intersects(fitz.Rect(COLLECTION_RECT))]
    retained = final[1].get_text()
    assert all(block in retained for block in retained_blocks)
    before = original[0].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    after = final[1].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    a = Image.frombytes("RGB", (before.width, before.height), before.samples)
    b = Image.frombytes("RGB", (after.width, after.height), after.samples)
    difference = ImageChops.difference(a, b).getbbox()
    assert difference is not None
    changed_points = tuple(value / 2 for value in difference)
    assert fitz.Rect(COLLECTION_RECT).contains(fitz.Rect(changed_points))
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    for i, page in enumerate(final):
        page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(args.qa_dir / f"public-page-{i + 1:02d}.png")
    report = {"date": content["date"], "edition": "one-page editorial preface plus four-page DQB",
              "public_file": args.output.name, "sha256": sha256(args.output.read_bytes()),
              "size_bytes": args.output.stat().st_size,
              "preface_json_sha256": sha256(content_bytes),
              "source_page_count": 4, "public_page_count": 5,
              "source_edits": ["Removed only the collection heading and collection-route prose on original page 1"],
              "original_scientific_body_and_values_preserved": True,
              "original_page_1_outside_redaction_pixel_identical_144_dpi": True,
              "original_page_1_changed_bbox_pt": list(changed_points),
              "original_link_annotations_preserved": sum(map(len, source_links)),
              "original_unique_public_links": len(set(url for urls in source_links for url in urls)),
              "original_pages": original_checks, "preface_layout": layout,
              "pdf_inspection": inspect_pdf(final),
              "visual_review": "Pending inspection of all five rendered pages",
              "independent_scientific_reproduction": False,
              "fonts_sha256": {"regular": sha256(args.font_regular.read_bytes()),
                               "bold": sha256(args.font_bold.read_bytes()),
                               "fallback": sha256(args.font_fallback.read_bytes())}}
    args.qa_report.parent.mkdir(parents=True, exist_ok=True)
    args.qa_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pages": final.page_count, "sha256": report["sha256"],
                      "preface_bottom_pt": layout["content_bottom_pt"]}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--font-regular", type=Path, required=True)
    parser.add_argument("--font-bold", type=Path, required=True)
    parser.add_argument("--font-fallback", type=Path, required=True)
    parser.add_argument("--preface", type=Path, default=TOPIC / "reports/preface.json")
    parser.add_argument("--output", type=Path, default=TOPIC / "dist/2026-10-22-daily-quantum-brief.pdf")
    parser.add_argument("--qa-dir", type=Path, default=TOPIC / "tmp/pdfs")
    parser.add_argument("--qa-report", type=Path, default=TOPIC / "notes/production-qa.json")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
