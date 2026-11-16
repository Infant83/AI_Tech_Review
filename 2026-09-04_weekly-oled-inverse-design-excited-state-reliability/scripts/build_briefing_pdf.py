"""Rebuild this issue's existing English technical brief with the shared parser."""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Spacer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import markdown_to_pdf as shared


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-regular", type=Path, required=True,
                        help="Unicode TrueType font covering the credited author names")
    parser.add_argument("--font-bold", type=Path, required=True)
    args = parser.parse_args()
    if bool(args.font_regular) != bool(args.font_bold):
        parser.error("Provide both font files, or use the built-in Latin fonts.")
    if args.font_regular:
        pdfmetrics.registerFont(TTFont("BriefRegular", str(args.font_regular)))
        pdfmetrics.registerFont(TTFont("BriefBold", str(args.font_bold)))
        shared.FONT_REGULAR = "BriefRegular"
        shared.FONT_BOLD = "BriefBold"

    original_styles = shared.build_styles

    def styles():
        result = original_styles()
        for style in result.values():
            style.wordWrap = None
        result["body"].leading = 14.2
        result["body"].allowWidows = 0
        result["body"].allowOrphans = 0
        result["h1"].fontSize = 14
        result["h1"].leading = 19
        return result

    shared.build_styles = styles
    topic = Path(__file__).resolve().parents[1]
    source = topic / "artifacts" / "oled_inverse_design_weekly_brief_2026-09-04.md"
    destination = source.with_suffix(".pdf")
    title = "Weekly OLED Inverse Design Brief - 4 September 2026"

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(shared.FONT_REGULAR, 8)
        canvas.setFillColor(colors.HexColor("#6b7280"))
        canvas.drawString(18 * mm, 10 * mm, "ATRL | Editorial revision 16 November 2026")
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
        canvas.restoreState()

    buffer = io.BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="Hyun-Jung Kim",
        subject="Agentic Tech Review Letters; original issue 2026-09-04; editorial revision 2026-11-16",
    )
    story = shared.parse_to_story(source.read_text(encoding="utf-8"), source.stem)
    for index, flowable in enumerate(story):
        if getattr(getattr(flowable, "style", None), "name", None) in {"H1Pdf", "H2Pdf"}:
            flowable.keepWithNext = True
            next_index = index + 1
            while next_index < len(story) and isinstance(story[next_index], Spacer):
                story[next_index].keepWithNext = True
                next_index += 1
    document.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer,
    )
    writer = PdfWriter()
    writer.clone_document_from_reader(PdfReader(buffer))
    writer.add_metadata({
        "/Title": title,
        "/Author": "Hyun-Jung Kim",
        "/Subject": "Agentic Tech Review Letters; original issue 2026-09-04; editorial revision 2026-11-16",
        "/Creator": "ATRL editorial publication builder",
        "/CreationDate": "D:20261116000000Z",
        "/ModDate": "D:20261116000000Z",
    })
    with destination.open("wb") as stream:
        writer.write(stream)
    print(destination.relative_to(ROOT))


if __name__ == "__main__":
    main()
