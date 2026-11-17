"""Build the reviewed Korean NTCA exercise PDF from explicit manuscript pages.

Inputs: reports/pdf-content.json, caller-supplied Korean regular/bold TrueType
fonts and a mathematical fallback font. Requires reportlab, pypdf and PyMuPDF.
Font files and rendered QA images are caller-owned private working assets.
"""
import argparse
import hashlib
import html
import io
import json
import platform
import re
from collections import Counter
from importlib.metadata import version
from pathlib import Path

import fitz
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
DOC_ID = "2026-11-17-daily-quantum-exercise-ntca"
INK = colors.HexColor("#152B3B")
TEAL = colors.HexColor("#00786F")
MUTED = colors.HexColor("#426473")
RULE = colors.HexColor("#C6DDDB")
PALE = colors.HexColor("#EAF5F2")
PAGE = colors.HexColor("#FDFFFD")
W, H = A4
MARGIN = 46
WIDTH = W - 2 * MARGIN
BOTTOM = 65
INLINE_TAG = re.compile(r"</?(?:b|strong|i|em|u|sub|super|sup|font|br|link|a)\b[^>]*>", re.I)
HYPHENS = str.maketrans({c: "-" for c in "‐‑‒–—"})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plain(value):
    return html.unescape(re.sub(r"<[^>]*>", "", str(value)))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--content", type=Path, default=ROOT / "reports/pdf-content.json")
    ap.add_argument("--font-regular", type=Path, required=True)
    ap.add_argument("--font-bold", type=Path, required=True)
    ap.add_argument("--font-math", type=Path, required=True)
    ap.add_argument("--qa-dir", type=Path, required=True)
    args = ap.parse_args()
    data = json.loads(args.content.read_text())
    pages = data["pages"]
    assert 2 <= len(pages) <= 20 and pages[0].get("label")
    fonts = {"DqeRegular": args.font_regular, "DqeBold": args.font_bold, "DqeMath": args.font_math}
    for name, path in fonts.items():
        pdfmetrics.registerFont(TTFont(name, str(path)))
    pdfmetrics.registerFontFamily("DqeRegular", normal="DqeRegular", bold="DqeBold", italic="DqeRegular", boldItalic="DqeBold")
    glyphs = {name: pdfmetrics.getFont(name).face.charToGlyph for name in fonts}
    fallback = Counter()

    def mixed(value, face="DqeRegular"):
        value = str(value).translate(HYPHENS)
        pieces, pos = [], 0

        def encode(text):
            result = []
            for ch in html.unescape(text):
                escaped = html.escape(ch, quote=False)
                if ch in "\n\r\t":
                    result.append(" " if ch != "\n" else "<br/>")
                elif ord(ch) in glyphs[face]:
                    result.append(escaped)
                elif ord(ch) in glyphs["DqeMath"]:
                    result.append('<font name="DqeMath">' + escaped + '</font>')
                    fallback[ch] += 1
                else:
                    raise ValueError(f"Missing glyph U+{ord(ch):04X}: {ch!r}")
            return "".join(result)

        for match in INLINE_TAG.finditer(value):
            pieces.append(encode(value[pos:match.start()]))
            tag = match.group().replace("<sup>", "<super>").replace("</sup>", "</super>")
            pieces.append(tag)
            pos = match.end()
        pieces.append(encode(value[pos:]))
        return "".join(pieces)

    def paragraph(text, size=10.2, leading=15.4, bold=False, color=INK, align=TA_LEFT, small=False):
        face = "DqeBold" if bold else "DqeRegular"
        style = ParagraphStyle("p", fontName=face, fontSize=size, leading=leading,
                               textColor=color, wordWrap="CJK", alignment=align,
                               allowWidows=0, allowOrphans=0)
        return Paragraph(mixed(text, face), style)

    def make_block(block):
        kind = block.get("type", "p")
        text = block.get("text", "")
        if kind in {"heading", "h2", "h3"}:
            return paragraph(text, size=12.4, leading=17.5, bold=True, color=TEAL), 9, 5
        if kind in {"p", "paragraph", "small", "reference"}:
            size = float(block.get("size", 9.1 if kind in {"small", "reference"} else 10.2))
            leading = float(block.get("leading", size * 1.49))
            return paragraph(text, size=size, leading=leading), 0, 8 if kind != "reference" else 6
        if kind in {"formula", "callout", "code"}:
            size = float(block.get("size", 10.5 if kind == "formula" else 9.9))
            content = text
            if block.get("title"):
                content = "<b>" + block["title"] + "</b><br/>" + content
            p = paragraph(content, size=size, leading=float(block.get("leading", size*1.49)),
                          color=TEAL if kind == "formula" else INK,
                          align=TA_CENTER if block.get("align") == "center" else TA_LEFT)
            table = Table([[p]], colWidths=[WIDTH])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("LINEBEFORE", (0, 0), (0, -1), 2.5, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 11),
                ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]))
            return table, 3, 10
        if kind == "table":
            headers = block.get("headers", [])
            rows = block["rows"]
            column_count = len(headers) if headers else len(rows[0])
            assert column_count and all(len(row) == column_count for row in rows)
            weights = block.get("widths", [1] * column_count)
            assert len(weights) == column_count and all(v > 0 for v in weights)
            col_widths = [WIDTH * value / sum(weights) for value in weights]
            size = float(block.get("size", 9.2))
            formatted = []
            if headers:
                formatted.append([paragraph(cell, size=size, leading=size*1.42, bold=True, color=colors.white) for cell in headers])
            formatted.extend([[paragraph(cell, size=size, leading=size*1.42) for cell in row] for row in rows])
            table = Table(formatted, colWidths=col_widths, hAlign="LEFT")
            instructions = [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LINEBELOW", (0, -1), (-1, -1), .6, RULE),
            ]
            if headers:
                instructions.append(("BACKGROUND", (0, 0), (-1, 0), TEAL))
            for row in range(1 if headers else 0, len(formatted)):
                if (row - bool(headers)) % 2 == 1:
                    instructions.append(("BACKGROUND", (0, row), (-1, row), PALE))
            table.setStyle(TableStyle(instructions))
            return table, 3, 10
        if kind in {"list", "bullets", "steps"}:
            items = block["items"]
            rows = []
            for i, item in enumerate(items, 1):
                mark = f"{i:02d}" if kind == "steps" or block.get("ordered") else "•"
                rows.append([paragraph(mark, size=9.6, leading=14.7, bold=True, color=TEAL),
                             paragraph(item, size=float(block.get("size", 10.0)), leading=15)])
            table = Table(rows, colWidths=[23, WIDTH-23])
            table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"),
                                       ("LEFTPADDING", (0,0),(-1,-1),0),
                                       ("RIGHTPADDING", (0,0),(-1,-1),0),
                                       ("TOPPADDING", (0,0),(-1,-1),1),
                                       ("BOTTOMPADDING", (0,0),(-1,-1),6)]))
            return table, 0, 4
        if kind == "spacer":
            return None, float(block.get("height", 5)), 0
        raise ValueError(f"Unknown content block type: {kind}")

    raw = io.BytesIO()
    c = canvas.Canvas(raw, pagesize=A4, invariant=1, pageCompression=1)
    page_metrics = []
    for page_number, spec in enumerate(pages, 1):
        c.setFillColor(PAGE)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(TEAL)
        c.rect(0, H-8, W, 8, fill=1, stroke=0)
        c.setFont("DqeBold", 9)
        c.drawString(MARGIN, H-37, "DAILY QUANTUM EXERCISE")
        label = paragraph(data.get("date", "2026-11-17") + " / " + spec.get("label", ""), size=8.5, leading=12, color=TEAL, align=TA_RIGHT)
        label.wrap(WIDTH/2, 30)
        label.drawOn(c, W-MARGIN-WIDTH/2, H-39)
        y = H - 63
        title = paragraph(spec.get("title", data["title"]), size=float(spec.get("title_size", 22)), leading=29, bold=True)
        _, h = title.wrap(WIDTH, H)
        title.drawOn(c, MARGIN, y-h)
        y -= h+7
        subtitle = spec.get("subtitle", data.get("subtitle", "") if page_number == 1 else "")
        if subtitle:
            sub = paragraph(subtitle, size=10.3, leading=14.7, color=MUTED)
            _, h = sub.wrap(WIDTH, H)
            sub.drawOn(c, MARGIN, y-h)
            y -= h+10
        c.setStrokeColor(RULE)
        c.setLineWidth(.7)
        c.line(MARGIN, y-3, W-MARGIN, y-3)
        y -= 20
        top = y
        for index, block in enumerate(spec["blocks"], 1):
            flowable, before, after = make_block(block)
            y -= before
            if flowable is None:
                continue
            _, h = flowable.wrap(WIDTH, H)
            if y-h < BOTTOM:
                raise ValueError(f"Page {page_number} block {index} overflows by {BOTTOM-(y-h):.1f} points; edit page composition, do not clip")
            flowable.drawOn(c, MARGIN, y-h)
            y -= h+after
        c.setStrokeColor(RULE)
        c.line(MARGIN, 48, W-MARGIN, 48)
        c.setFillColor(MUTED)
        c.setFont("DqeRegular", 7.6)
        c.drawString(MARGIN, 34, "DAILY QUANTUM EXERCISE / " + data.get("date", "2026-11-17"))
        c.drawRightString(W-MARGIN, 34, f"{page_number:02d} / {len(pages):02d}")
        page_metrics.append({"page": page_number, "label": spec.get("label", ""), "body_top": round(top,2), "body_bottom": round(y,2), "remaining_points": round(y-BOTTOM,2)})
        c.showPage()
    c.save()
    writer = PdfWriter(clone_from=io.BytesIO(raw.getvalue()))
    writer.metadata = None
    meta = data.get("metadata", {})
    writer.add_metadata({"/Title": data["title"], "/Author": meta.get("author", "ATRL Editorial and Authoring Team (AEDAUT)"),
                         "/Subject": meta.get("subject", "Daily Quantum Exercise | 2026-11-17 | NTCA monomial learning guide"),
                         "/Creator": "ATRL AEDAUT / Codex-assisted exercise authoring",
                         "/Producer": "ReportLab and pypdf"})
    output = ROOT / "dist" / (DOC_ID + ".pdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    writer.write(output)
    final = fitz.open(output)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    assert len(final) == len(pages) and final.embfile_count() == 0 and not final.get_xml_metadata()
    uris = []
    for i, p in enumerate(final, 1):
        p.get_pixmap(matrix=fitz.Matrix(2,2), alpha=False).save(args.qa_dir / f"public-{i}.png")
        for link in p.get_links():
            assert link["kind"] == fitz.LINK_URI and link["uri"].startswith("https://")
            uris.append(link["uri"])
    reader = PdfReader(output, strict=True)
    extracted = "\n".join(p.extract_text() for p in reader.pages)
    assert "PennyLane" in extracted and "Qiskit" in extracted and "Classiq" in extracted
    combined = extracted + str(reader.metadata) + "\n".join(uris)
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|/Users/|file:/{2}|authuser=|unsubscribe|mail\.google", combined, re.I)
    forbidden = {"/OpenAction", "/AA", "/JS", "/JavaScript", "/Launch", "/EmbeddedFiles", "/XFA", "/AcroForm", "/RichMedia"}
    found, seen = set(), set()
    def walk(obj):
        if hasattr(obj, "get_object"):
            obj = obj.get_object()
        if id(obj) in seen:
            return
        seen.add(id(obj))
        if isinstance(obj, dict):
            found.update(forbidden.intersection(obj))
            for value in obj.values():
                walk(value)
        elif isinstance(obj, (list, tuple)):
            for value in obj:
                walk(value)
    walk(reader.trailer)
    assert not found
    action_counts = Counter()
    for p in reader.pages:
        for ref in p.get("/Annots", []):
            annot = ref.get_object()
            assert annot["/Subtype"] == "/Link"
            action = annot["/A"].get_object()
            assert action["/S"] == "/URI"
            action_counts[str(action["/S"])] += 1
    qa = {"document_id": DOC_ID, "date": data.get("date", "2026-11-17"),
          "pdf_sha256": sha(output), "manuscript_sha256": sha(args.content),
          "build_runtime": {"python": platform.python_version(), "reportlab": version("reportlab"), "pypdf": version("pypdf"), "PyMuPDF": version("PyMuPDF")},
          "page_count": len(final), "pages": page_metrics,
          "glyph_coverage": "complete; checked every visible manuscript character before drawing",
          "fallback_glyphs": {f"U+{ord(ch):04X}": count for ch,count in fallback.items()},
          "fonts": {name: {"sha256":sha(path)} for name,path in fonts.items()},
          "uris": uris, "uri_count": len(uris), "strict_parse": "passed", "embedded_files": 0,
          "xmp_metadata": False, "prohibited_action_keys": sorted(found), "annotation_action_types": dict(action_counts),
          "personal_address_or_private_path_scan": "passed for body, metadata and URI targets",
          "authoring_scope": "Original educational exercise and three-platform implementation guide based on credited sources; no source-paper figures reproduced",
          "visual_review": {"pages_rendered":list(range(1,len(final)+1)),"status":"pending actual image inspection","human_sentence_review":"not performed"}}
    (ROOT / "artifacts/public-pdf-qa.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"pages":len(final),"sha256":sha(output),"bytes":output.stat().st_size,"uri_count":len(uris)},ensure_ascii=False))


if __name__ == "__main__":
    main()
