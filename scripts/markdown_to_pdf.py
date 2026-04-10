from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer


FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
FONT_MONO = "Courier"


def register_fonts() -> None:
    global FONT_REGULAR, FONT_BOLD
    font_dir = Path(r"C:\Windows\Fonts")
    regular = font_dir / "malgun.ttf"
    bold = font_dir / "malgunbd.ttf"
    if regular.exists():
        pdfmetrics.registerFont(TTFont("MalgunGothic", str(regular)))
        FONT_REGULAR = "MalgunGothic"
    if bold.exists():
        pdfmetrics.registerFont(TTFont("MalgunGothicBold", str(bold)))
        FONT_BOLD = "MalgunGothicBold"


def build_styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "TitlePdf",
            parent=base["Title"],
            fontName=FONT_BOLD,
            fontSize=21,
            leading=28,
            textColor=colors.HexColor("#0f172a"),
            alignment=TA_CENTER,
            spaceAfter=10,
            wordWrap="CJK",
        ),
        "h1": ParagraphStyle(
            "H1Pdf",
            parent=base["Heading1"],
            fontName=FONT_BOLD,
            fontSize=16,
            leading=21,
            textColor=colors.HexColor("#111827"),
            spaceBefore=12,
            spaceAfter=6,
            wordWrap="CJK",
        ),
        "h2": ParagraphStyle(
            "H2Pdf",
            parent=base["Heading2"],
            fontName=FONT_BOLD,
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#1f2937"),
            spaceBefore=8,
            spaceAfter=4,
            wordWrap="CJK",
        ),
        "body": ParagraphStyle(
            "BodyPdf",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=10.5,
            leading=16,
            textColor=colors.HexColor("#111827"),
            spaceAfter=6,
            wordWrap="CJK",
        ),
        "meta": ParagraphStyle(
            "MetaPdf",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#6b7280"),
            spaceAfter=8,
            alignment=TA_CENTER,
            wordWrap="CJK",
        ),
    }
    return styles


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        parts = text.split("\n")
        for idx in range(1, len(parts)):
            if parts[idx].strip() == "---":
                return "\n".join(parts[idx + 1 :]).lstrip()
    return text


def inline_markup(text: str) -> str:
    tokens: dict[str, str] = {}

    def stash(markup: str) -> str:
        key = f"__MDPDFTOKEN{len(tokens)}__"
        tokens[key] = markup
        return key

    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda m: stash(
            f'<link href="{html.escape(m.group(2), quote=True)}" color="blue">{html.escape(m.group(1))}</link>'
        ),
        text,
    )
    text = re.sub(
        r"`([^`]+)`",
        lambda m: stash(
            f'<font face="{FONT_REGULAR}" backcolor="#eef2f7" color="#1f2937">{html.escape(m.group(1))}</font>'
        ),
        text,
    )
    text = re.sub(
        r"==(.+?)==",
        lambda m: stash(
            f'<font face="{FONT_REGULAR}" backcolor="#fef3c7">{html.escape(m.group(1))}</font>'
        ),
        text,
    )
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda m: stash(f'<font face="{FONT_BOLD}">{html.escape(m.group(1))}</font>'),
        text,
    )
    text = re.sub(
        r"(?<!\*)\*([^*]+)\*(?!\*)",
        lambda m: stash(f"<i>{html.escape(m.group(1))}</i>"),
        text,
    )

    text = html.escape(text)
    for key, markup in tokens.items():
        text = text.replace(key, markup)
    return text


def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_REGULAR, 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawRightString(doc.pagesize[0] - 18 * mm, 10 * mm, str(canvas.getPageNumber()))
    canvas.restoreState()


def parse_to_story(text: str, source_name: str):
    styles = build_styles()
    story = []
    lines = strip_frontmatter(text).splitlines()

    title = None
    meta_lines = []
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            idx += 1
            continue
        if line.startswith("# "):
            title = line[2:].strip()
            idx += 1
            break
        if line.startswith("title:") or line.startswith("date:"):
            meta_lines.append(line)
        idx += 1

    if title is None:
        title = source_name

    story.append(Paragraph(inline_markup(title), styles["title"]))
    if meta_lines:
        story.append(Paragraph(inline_markup(" | ".join(meta_lines)), styles["meta"]))
    story.append(Spacer(1, 4))

    buffer: list[str] = []

    def flush_paragraph():
        if buffer:
            story.append(Paragraph(inline_markup(" ".join(buffer).strip()), styles["body"]))
            buffer.clear()

    while idx < len(lines):
        raw = lines[idx].rstrip()
        line = raw.strip()

        if not line:
            flush_paragraph()
            story.append(Spacer(1, 2))
            idx += 1
            continue

        if line.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[2:].strip()), styles["h1"]))
            idx += 1
            continue

        if line.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[3:].strip()), styles["h1"]))
            idx += 1
            continue

        if line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[4:].strip()), styles["h2"]))
            idx += 1
            continue

        if re.match(r"^[-*] ", line):
            flush_paragraph()
            items = []
            while idx < len(lines):
                current = lines[idx].strip()
                if not re.match(r"^[-*] ", current):
                    break
                items.append(
                    ListItem(Paragraph(inline_markup(current[2:].strip()), styles["body"]))
                )
                idx += 1
            story.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    bulletFontName=FONT_REGULAR,
                    bulletFontSize=8,
                    leftIndent=14,
                )
            )
            story.append(Spacer(1, 4))
            continue

        if re.match(r"^\d+\. ", line):
            flush_paragraph()
            items = []
            start = int(line.split(".", 1)[0])
            while idx < len(lines):
                current = lines[idx].strip()
                if not re.match(r"^\d+\. ", current):
                    break
                items.append(
                    ListItem(Paragraph(inline_markup(current.split(". ", 1)[1]), styles["body"]))
                )
                idx += 1
            story.append(
                ListFlowable(
                    items,
                    bulletType="1",
                    start=start,
                    leftIndent=16,
                )
            )
            story.append(Spacer(1, 4))
            continue

        buffer.append(line)
        idx += 1

    flush_paragraph()
    return story


def markdown_to_pdf(src: Path, dst: Path) -> None:
    text = src.read_text(encoding="utf-8")
    story = parse_to_story(text, src.stem)
    doc = SimpleDocTemplate(
        str(dst),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title=src.stem,
        author="Codex",
    )
    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python scripts/markdown_to_pdf.py <input.md> [<input2.md> ...]")
        return 1

    register_fonts()

    for item in argv[1:]:
        src = Path(item)
        if not src.exists():
            raise FileNotFoundError(src)
        dst = src.with_suffix(".pdf")
        markdown_to_pdf(src, dst)
        print(dst)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
