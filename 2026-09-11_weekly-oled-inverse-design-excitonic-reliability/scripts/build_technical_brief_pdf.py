"""Build this issue's newly authored revised English technical brief.

This adapter reuses scripts/markdown_to_pdf.py's styles and inline markup.
It does not recover, reproduce, register or publish the damaged earlier PDF.
The caller supplies Unicode fonts and a private SVG raster-cache directory.
No network access is needed. Existing outputs require --replace-output.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

import pypdf
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, TextStringObject
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image, KeepTogether, ListFlowable, ListItem, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[2]
TOPIC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import markdown_to_pdf as shared

ORIGINAL_DATE = "2026-09-11"
EVIDENCE_DATE = "2026-09-10"
EDITION_DATE = "2026-11-26"
ISSUE = "Agentic Tech Review Letters | Week 37 | 11 September 2026"
ASSETS = {
    "excitonic_reliability_hero-web.webp": "a3832c1e95950ea8b05e6dfd4bc7b05e3075ab5255d881d900973d4115c28ef5",
    "evidence_map.svg": "2985aa791ee2750e6a4d45e9f2ecf0bb56a511092b6a2dc2a871673760c6a477",
    "proposed_workflow.svg": "40bdfaaa2e7459fbe9415e07f2919fbcf7c63e63d39c1149e98ca822f6639b1e",
}
REFERENCE_URLS = {
    "https://arxiv.org/abs/" + identifier for identifier in (
        "2609.06742v1", "2609.08333v1", "2609.08399v1", "2609.09990v1",
        "2609.09280v1", "2609.06655v1", "2609.07284v1", "2609.08170v1",
    )
}
REFERENCE_IDS = {f"ref-{number}" for number in range(1, 9)}
REFERENCE_SPAN = re.compile(r'<span\s+id=[\"\'](ref-\d+)[\"\']\s*>\s*</span>')
CITATION = re.compile(r'\[(\[?\d+\]?)\]\(#(ref-\d+)\)')
IMAGE_LINE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
WIDTH = A4[0] - 36 * mm
SUBSCRIPTS = str.maketrans("₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎", "0123456789+-=()")
SUPERSCRIPTS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾", "0123456789+-=()")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_fonts(args) -> dict:
    supplied = {
        "BriefRegular": args.font_regular,
        "BriefBold": args.font_bold,
    }
    if args.font_italic:
        supplied["BriefItalic"] = args.font_italic
    if args.font_bold_italic:
        supplied["BriefBoldItalic"] = args.font_bold_italic
    if args.font_symbols:
        supplied["BriefSymbols"] = args.font_symbols
    for name, path in supplied.items():
        if not path.is_file():
            raise ValueError("Missing supplied font: " + path.name)
        pdfmetrics.registerFont(TTFont(name, str(path)))
    italic = "BriefItalic" if args.font_italic else "BriefRegular"
    bold_italic = "BriefBoldItalic" if args.font_bold_italic else "BriefBold"
    pdfmetrics.registerFontFamily("BriefRegular", normal="BriefRegular", bold="BriefBold",
                                  italic=italic, boldItalic=bold_italic)
    pdfmetrics.registerFontFamily("BriefBold", normal="BriefBold", bold="BriefBold",
                                  italic=bold_italic, boldItalic=bold_italic)
    if args.font_symbols:
        pdfmetrics.registerFontFamily("BriefSymbols", normal="BriefSymbols", bold="BriefSymbols",
                                      italic="BriefSymbols", boldItalic="BriefSymbols")
    shared.FONT_REGULAR, shared.FONT_BOLD = "BriefRegular", "BriefBold"
    return {name: {"name": path.name, "sha256": digest(path)}
            for name, path in supplied.items()}


def styles() -> dict:
    result = shared.build_styles()
    for style in result.values():
        style.wordWrap = None
        style.allowWidows = 0
        style.allowOrphans = 0
    result["title"].alignment = TA_LEFT
    result["title"].fontSize, result["title"].leading = 19, 24
    result["title"].spaceAfter = 10
    result["body"].fontSize, result["body"].leading = 10.3, 14.6
    result["h1"].fontSize, result["h1"].leading = 13.8, 18.5
    result["h1"].keepWithNext = True
    result["h2"].keepWithNext = True
    result["caption"] = ParagraphStyle(
        "BriefCaption", parent=result["body"], fontSize=8.4, leading=11.4,
        textColor=colors.HexColor("#53636c"), spaceAfter=9,
    )
    result["reference"] = ParagraphStyle(
        "BriefReference", parent=result["body"], fontSize=9.2, leading=12.7,
        spaceAfter=7, leftIndent=17, firstLineIndent=-17,
    )
    result["table"] = ParagraphStyle(
        "BriefTable", parent=result["body"], fontSize=8.3, leading=11.3,
        spaceAfter=0,
    )
    return result


def supported_text(markup: str, symbols: bool) -> str:
    """Fallback only text nodes; never alter a link or formatting attribute."""
    regular = pdfmetrics.getFont("BriefRegular").face.charToGlyph
    bold = pdfmetrics.getFont("BriefBold").face.charToGlyph
    fallback = pdfmetrics.getFont("BriefSymbols").face.charToGlyph if symbols else {}
    parts = re.split(r"(<[^>]+>)", markup)
    for index in range(0, len(parts), 2):
        pieces = []
        for char in html.unescape(parts[index]):
            code = ord(char)
            escaped = html.escape(char)
            if code in regular and code in bold:
                pieces.append(escaped)
            elif code in fallback:
                pieces.append(f'<font face="BriefSymbols">{escaped}</font>')
            else:
                raise ValueError(f"Supplied fonts do not cover U+{code:04X} ({char!r})")
        parts[index] = "".join(pieces)
    return "".join(parts)


def inline(text: str, symbols: bool) -> str:
    tokens = {}

    def stash(value):
        key = f"BRIEFMARKUPTOKEN{len(tokens)}END"
        tokens[key] = value
        return key

    # Ordinary hyphens avoid ambiguous nonbreaking-hyphen PDF mappings.
    text = re.sub("[\u2010-\u2015]", "-", text)
    text = re.sub(r"(\d[\d.,]*) (mHa|Ha|meV|eV|GB|hours|degrees)\b", lambda m: m[1] + "\u00a0" + m[2], text)
    text = CITATION.sub(
        lambda m: stash(f'<link href="#{m[2]}" color="#007b85">[{m[1].strip("[]")}]</link>'),
        text,
    )
    text = re.sub(r'<(sub|sup|super|i|b|em|strong)>.*?</\1>',
                  lambda m: stash(m[0].replace("<sup>", "<super>").replace("</sup>", "</super>")
                                  .replace("<em>", "<i>").replace("</em>", "</i>")
                                  .replace("<strong>", "<b>").replace("</strong>", "</b>")),
                  text)
    text = re.sub(r"[₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎]+",
                  lambda m: stash("<sub>" + m[0].translate(SUBSCRIPTS) + "</sub>"), text)
    text = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾]+",
                  lambda m: stash("<super>" + m[0].translate(SUPERSCRIPTS) + "</super>"), text)
    text = re.sub(r"10\^\{?(-?\d+)\}?",
                  lambda m: stash("10<super>" + m[1] + "</super>"), text)
    rendered = shared.inline_markup(text)
    for key, value in tokens.items():
        rendered = rendered.replace(key, value)
    return supported_text(rendered, symbols)


def validate_source(text: str) -> tuple[str, dict]:
    body = shared.strip_frontmatter(text)
    title = re.search(r"^# (.+)$", body, re.M)
    if not title or len(re.findall(r"^# ", body, re.M)) != 1:
        raise ValueError("Expected exactly one manuscript title")
    anchors = REFERENCE_SPAN.findall(body)
    if len(anchors) != 8 or set(anchors) != REFERENCE_IDS:
        raise ValueError("Expected one reference anchor for each of the eight references")
    citations = list(CITATION.finditer(body))
    if {m[2] for m in citations} != REFERENCE_IDS:
        raise ValueError("Every reference needs an explicit internal citation")
    if any(m[1].strip("[]") != m[2][4:] for m in citations):
        raise ValueError("Citation label does not match its reference destination")
    external = set(re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", body))
    if external != REFERENCE_URLS:
        raise ValueError("Keep exactly the eight consulted arXiv v1 HTTPS source links")
    figures = [IMAGE_LINE.fullmatch(line.strip()) for line in body.splitlines()
               if line.strip().startswith("![")]
    if len(figures) != 3 or any(m is None for m in figures):
        raise ValueError("Expected three standalone existing figure lines")
    names = [Path(urlsplit(m[2]).path).name for m in figures]
    if names != list(ASSETS):
        raise ValueError("Keep the three original figures in their reviewed order")
    for name in names:
        if digest(TOPIC / "artifacts" / name) != ASSETS[name]:
            raise ValueError("An existing figure changed: " + name)
    return title[1], {"citation_count": len(citations), "reference_count": 8,
                       "source_urls": sorted(external), "figure_sha256": ASSETS}


def raster_image(name: str, cache_dir: Path) -> Path:
    source = TOPIC / "artifacts" / name
    if source.suffix != ".svg":
        return source
    raw = source.read_bytes()
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("Do not process SVG document declarations")
    tree = ET.fromstring(raw)
    for element in tree.iter():
        for key, value in element.attrib.items():
            if key.rsplit("}", 1)[-1] == "href" and not value.startswith("#"):
                raise ValueError("Figure SVG may not fetch another resource")
    cached = cache_dir / f"{source.stem}-{ASSETS[name][:12]}-2400.png"
    provenance = cached.with_suffix(".json")
    if cached.is_symlink() or provenance.is_symlink():
        raise ValueError("Raster-cache files must be ordinary files")
    reusable = False
    if cached.is_file() and provenance.is_file():
        try:
            prior = json.loads(provenance.read_text())
            reusable = (prior.get("source_sha256") == ASSETS[name]
                        and prior.get("raster_sha256") == digest(cached)
                        and prior.get("output_width") == 2400)
        except (ValueError, OSError):
            reusable = False
    if not reusable:
        import cairosvg
        # Rasterization occurs only when the caller explicitly runs the builder.
        # Source SVGs and all their geometry/labels remain unchanged.
        cached.write_bytes(cairosvg.svg2png(bytestring=raw, output_width=2400))
        provenance.write_text(json.dumps({
            "source_sha256": ASSETS[name], "raster_sha256": digest(cached),
            "output_width": 2400, "renderer": "CairoSVG " + cairosvg.__version__,
        }, indent=2) + "\n")
    return cached


def figure_block(name: str, caption: str, cache_dir: Path, sheet: dict,
                 symbols: bool):
    image = Image(str(raster_image(name, cache_dir)))
    factor = min(WIDTH / image.imageWidth, 300 / image.imageHeight)
    image.drawWidth = image.imageWidth * factor
    image.drawHeight = image.imageHeight * factor
    image.hAlign = "CENTER"
    return KeepTogether([image, Spacer(1, 5), Paragraph(inline(caption, symbols), sheet["caption"])])


def table_rows(line: str) -> list[str]:
    return [cell.strip().replace(r"\|", "|")
            for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def parse_story(text: str, cache_dir: Path, symbols: bool):
    sheet = styles()
    lines = shared.strip_frontmatter(text).splitlines()
    story, buffer = [], []
    in_references = False
    title_seen = False

    def paragraph(value, style="body"):
        return Paragraph(inline(value, symbols), sheet[style])

    def flush():
        if buffer:
            story.append(paragraph(" ".join(buffer)))
            buffer.clear()

    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            flush()
            index += 1
            continue
        heading = re.match(r"^(#{1,3}) (.+)$", line)
        if heading:
            flush()
            level, label = len(heading[1]), heading[2]
            if level == 1:
                if title_seen:
                    raise ValueError("Only one top-level title is supported")
                title_seen = True
                story.append(paragraph(label, "title"))
            else:
                in_references = label.lower() == "references"
                story.append(paragraph(label, "h1" if level == 2 else "h2"))
            index += 1
            continue
        match = IMAGE_LINE.fullmatch(line)
        if match:
            flush()
            name = Path(urlsplit(match[2]).path).name
            index += 1
            while index < len(lines) and not lines[index].strip():
                index += 1
            if index == len(lines) or not re.fullmatch(r"\*Figure \d+\..+\*", lines[index].strip()):
                raise ValueError("Every figure needs its immediately following Figure caption")
            caption = lines[index].strip()[1:-1]
            story.append(figure_block(name, caption, cache_dir, sheet, symbols))
            index += 1
            continue
        reference = re.match(r"^(\d+)\. (.+)$", line) if in_references else None
        if reference:
            flush()
            number, content = reference.groups()
            anchor = REFERENCE_SPAN.search(content)
            if anchor is None or anchor[1] != f"ref-{number}":
                raise ValueError("Reference number and destination differ")
            content = REFERENCE_SPAN.sub("", content)
            value = f'<a name="ref-{number}"/>[{number}] ' + inline(content, symbols)
            story.append(Paragraph(value, sheet["reference"]))
            index += 1
            continue
        if line.startswith("|"):
            flush()
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                row = table_rows(lines[index])
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in row):
                    rows.append(row)
                index += 1
            if not rows or any(len(row) != len(rows[0]) for row in rows):
                raise ValueError("Malformed Markdown table")
            table = Table([[paragraph(cell, "table") for cell in row] for row in rows],
                          colWidths=[WIDTH / len(rows[0])] * len(rows[0]), repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9f1f2")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LINEBELOW", (0, 0), (-1, -1), .3, colors.HexColor("#ccdadd")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend([table, Spacer(1, 7)])
            continue
        bullet = re.match(r"^[-*] (.+)$", line)
        ordered = re.match(r"^(\d+)\. (.+)$", line)
        if bullet or ordered:
            flush()
            items, numbered = [], bool(ordered)
            start = int(ordered[1]) if ordered else None
            while index < len(lines):
                item = re.match(r"^\d+\. (.+)$" if numbered else r"^[-*] (.+)$",
                                lines[index].strip())
                if not item:
                    break
                items.append(ListItem(paragraph(item[1])))
                index += 1
            options = {"bulletType": "1" if numbered else "bullet", "leftIndent": 15,
                       "bulletFontName": "BriefRegular", "bulletFontSize": 8}
            if numbered:
                options["start"] = start
            story.extend([ListFlowable(items, **options), Spacer(1, 4)])
            continue
        if line.startswith("<"):
            raise ValueError("Unsupported block HTML; keep manuscript prose, figures and reference spans")
        buffer.append(line)
        index += 1
    flush()
    return story


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("BriefRegular", 7.5)
    canvas.setFillColor(colors.HexColor("#60717d"))
    canvas.drawString(18 * mm, A4[1] - 11 * mm, ISSUE)
    canvas.setStrokeColor(colors.HexColor("#cadadd"))
    canvas.line(18 * mm, 15 * mm, A4[0] - 18 * mm, 15 * mm)
    canvas.drawString(18 * mm, 10 * mm, "New editorial PDF edition | 26 November 2026")
    canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    canvas.restoreState()


def verify_pdf(data: bytes, source: dict) -> dict:
    reader = PdfReader(io.BytesIO(data), strict=True)
    external, internal = [], 0
    for page in reader.pages:
        for ref in page.get("/Annots", []):
            annotation = ref.get_object()
            action = annotation.get("/A")
            if action:
                action = action.get_object()
                if action.get("/S") == "/URI":
                    external.append(str(action["/URI"]))
                elif action.get("/S") == "/GoTo":
                    internal += 1
                else:
                    raise ValueError("Unexpected PDF annotation action")
            elif "/Dest" in annotation:
                internal += 1
        text = page.extract_text()
        if "\x00" in text or "\ufffd" in text:
            raise ValueError("Invalid extracted character in generated PDF")
    if set(external) != REFERENCE_URLS or internal < source["citation_count"]:
        raise ValueError("Generated PDF is missing source or internal citation links")
    root = reader.trailer["/Root"]
    if reader.is_encrypted or any(key in root for key in ["/OpenAction", "/AA", "/AcroForm"]):
        raise ValueError("Unexpected active document structure")
    return {"pages": len(reader.pages), "external_source_urls": sorted(set(external)),
            "internal_citation_links": internal, "metadata": dict(reader.metadata)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=TOPIC / "reports/technical_brief_en.md")
    parser.add_argument("--output", type=Path,
                        default=TOPIC / "artifacts/oled_inverse_design_weekly_brief_2026-09-11.pdf")
    parser.add_argument("--font-regular", type=Path, required=True)
    parser.add_argument("--font-bold", type=Path, required=True)
    parser.add_argument("--font-italic", type=Path)
    parser.add_argument("--font-bold-italic", type=Path)
    parser.add_argument("--font-symbols", type=Path,
                        help="Optional Unicode TrueType fallback for mathematical symbols")
    parser.add_argument("--image-cache-dir", type=Path, required=True,
                        help="Private directory for unchanged SVG rasterizations")
    parser.add_argument("--qa-report", type=Path, help="Optional private machine-readable production report")
    parser.add_argument("--replace-output", action="store_true")
    parser.add_argument("--created-at", help="Timezone-aware ISO creation instant; retain it when reproducing an edition")
    args = parser.parse_args()
    created_at = datetime.fromisoformat(args.created_at.replace("Z", "+00:00")) if args.created_at else datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        parser.error("--created-at requires a timezone")
    created_at = created_at.astimezone(timezone.utc).replace(microsecond=0)
    pdf_date = created_at.strftime("D:%Y%m%d%H%M%SZ")
    if not args.input.is_file():
        parser.error("Input manuscript is missing")
    if args.output.exists() and not args.replace_output:
        parser.error("Output already exists; choose a new candidate path or explicitly --replace-output")
    if args.output.is_symlink() or args.output.resolve() == args.input.resolve():
        parser.error("Output must be a separate regular PDF destination")
    for private in [args.image_cache_dir, args.qa_report]:
        if private is not None and private.resolve().is_relative_to(ROOT.resolve()):
            parser.error("Raster cache and QA report must remain outside the public repository")
    text = args.input.read_text(encoding="utf-8")
    title, source = validate_source(text)
    fonts = register_fonts(args)
    args.image_cache_dir.mkdir(parents=True, exist_ok=True)
    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
        title=title, author="Hyun-Jung Kim", pageCompression=1,
    )
    document.build(parse_story(text, args.image_cache_dir, bool(args.font_symbols)),
                   onFirstPage=footer, onLaterPages=footer)
    writer = PdfWriter()
    writer.clone_document_from_reader(PdfReader(io.BytesIO(buffer.getvalue()), strict=True))
    writer.add_metadata({
        "/Title": title, "/Author": "Hyun-Jung Kim",
        "/Subject": (f"Revised English technical brief; original publication {ORIGINAL_DATE}; "
                     f"evidence cutoff {EVIDENCE_DATE}; new editorial PDF edition {EDITION_DATE}. "
                     "Newly authored revision, not recovery of the damaged earlier PDF."),
        "/Creator": "ATRL topic-specific technical brief adapter using shared Markdown styles",
        "/Producer": f"ReportLab {reportlab.Version}; pypdf {pypdf.__version__}",
        "/CreationDate": pdf_date, "/ModDate": pdf_date,
    })
    writer.root_object[NameObject("/Lang")] = TextStringObject("en")
    final = io.BytesIO()
    writer.write(final)
    data = final.getvalue()
    inspection = verify_pdf(data, source)
    if any(digest(TOPIC / "artifacts" / name) != value for name, value in ASSETS.items()):
        raise ValueError("Existing source figures changed during production")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Produce a complete checked file before an explicit replacement is installed.
    fd, temporary = tempfile.mkstemp(prefix=".technical-brief-", suffix=".pdf", dir=args.output.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        if args.replace_output:
            os.replace(temporary, args.output)
        else:
            os.link(temporary, args.output)
    finally:
        Path(temporary).unlink(missing_ok=True)
    result = {
        "edition": "newly authored revised English technical brief",
        "original_publication": ORIGINAL_DATE, "evidence_cutoff": EVIDENCE_DATE,
        "editorial_PDF_edition": EDITION_DATE,
        "created_at": created_at.isoformat(),
        "pdf_sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
        "manuscript_sha256": digest(args.input), "builder_sha256": digest(Path(__file__)),
        "shared_converter_sha256": digest(ROOT / "scripts/markdown_to_pdf.py"),
        "fonts": fonts, "source": source, "inspection": inspection,
        "visual_qa": "pending; caller must render and open every final page",
        "original_five_page_recovery_or_equivalence_claimed": False,
    }
    if args.qa_report:
        args.qa_report.parent.mkdir(parents=True, exist_ok=True)
        args.qa_report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": args.output.name, "pages": inspection["pages"],
                      "bytes": len(data), "sha256": result["pdf_sha256"],
                      "visual_qa": result["visual_qa"]}))


if __name__ == "__main__":
    main()
