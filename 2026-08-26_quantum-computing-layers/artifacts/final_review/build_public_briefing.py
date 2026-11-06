"""Remove collection context from the existing four-page briefing.

The caller supplies the private original and a private QA directory. This does
not revise historical scientific claims, register an archive document, or publish.
Requires PyMuPDF, Pillow and pypdf. Rebuilding resets visual review to pending.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re

import fitz
from PIL import Image, ImageChops, ImageDraw
from pypdf import PdfReader

TOPIC = Path(__file__).resolve().parents[2]
SOURCE_SHA256 = "20eebeba1ebc401c2672b0136bd1d6adde7a4603550e0f4f8fd4e61dd26a66a0"
# PDF points. Only collection, social-discovery and internal-editorial blocks.
REMOVALS = {
    0: [(52, 483.5, 543, 542)],
    3: [(52, 551.6, 543, 610), (52, 657, 543, 668)],
}
FORBIDDEN_ACTION = re.compile(
    r"/(?:OpenAction|AA|JavaScript|JS|Launch|GoToR|SubmitForm|ImportData|"
    r"EmbeddedFiles|RichMedia|XFA)\b"
)
PRIVATE_TEXT = re.compile(
    r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|"
    r"/(?:Users|home|tmp)/|[A-Za-z]:\\(?:Users|Temp)\\|"
    r"(?:access_token|refresh_token|api_key)\s*[:=]",
    re.IGNORECASE,
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bitmap(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def outside_words(page, rectangles):
    result = []
    for word in page.get_text("words"):
        box = fitz.Rect(word[:4])
        if not any(box.intersects(fitz.Rect(rect)) for rect in rectangles):
            result.append(tuple(round(value, 3) for value in word[:4]) + (word[4],))
    return Counter(result)


def links(page):
    return sorted(
        (item.get("kind"), item.get("uri", ""), tuple(round(v, 3) for v in item["from"]))
        for item in page.get_links()
    )


def inspect(document):
    text = "\n".join(page.get_text() for page in document)
    metadata = json.dumps(document.metadata, ensure_ascii=False)
    bad_actions = []
    for xref in range(1, document.xref_length()):
        if FORBIDDEN_ACTION.search(document.xref_object(xref, compressed=False)):
            bad_actions.append(xref)
    return {
        "no_personal_author_metadata": not document.metadata.get("author"),
        "no_private_text_or_paths": not PRIVATE_TEXT.search(text + metadata),
        "no_xml_metadata": document.xref_xml_metadata() == 0,
        "no_embedded_files": document.embfile_count() == 0,
        "no_widgets": all(not list(page.widgets() or ()) for page in document),
        "no_active_actions": not bad_actions,
        "no_replacement_or_null_glyphs": "\ufffd" not in text and "\x00" not in text,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=TOPIC / "artifacts/public-assets/daily_quantum_brief_2026-08-26.pdf")
    parser.add_argument("--qa-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=TOPIC / "artifacts/final_review/briefing-publication-qa.json")
    args = parser.parse_args()
    if args.qa_dir.resolve().is_relative_to(TOPIC.parent.resolve()):
        raise ValueError("Keep original and QA renders outside the repository")
    raw = args.source.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise ValueError("Unexpected original briefing version")
    source = fitz.open(stream=raw, filetype="pdf")
    if len(source) != 4:
        raise ValueError("Expected the original four-page briefing")
    public = fitz.open(stream=raw, filetype="pdf")
    removed_lines = []
    for number, rectangles in REMOVALS.items():
        page = public[number]
        for rect in rectangles:
            for block in source[number].get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    if fitz.Rect(line["bbox"]).intersects(fitz.Rect(rect)):
                        removed_lines.append("".join(span["text"] for span in line["spans"]).strip())
            page.add_redact_annot(fitz.Rect(rect), fill=(1, 1, 1))
        page.apply_redactions(images=0, graphics=0, text=0)
    allowed_metadata = {"title", "author", "subject", "keywords", "creator", "producer", "creationDate", "modDate", "trapped"}
    public.set_metadata({key: ("" if key == "author" else value) for key, value in source.metadata.items() if key in allowed_metadata})
    public.del_xml_metadata()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    public.save(args.output, garbage=4, deflate=True, clean=True)
    public.close()
    public = fitz.open(args.output)
    if len(public) != len(source):
        raise ValueError("Page count changed")
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    checks = []
    for number, (before, after) in enumerate(zip(source, public)):
        rectangles = REMOVALS.get(number, [])
        a, b = bitmap(before), bitmap(after)
        a.save(args.qa_dir / f"original-{number + 1}.png")
        b.save(args.qa_dir / f"public-{number + 1}.png")
        a_mask, b_mask = a.copy(), b.copy()
        for rect in rectangles:
            pixel_rect = (math.floor(rect[0] * 2), math.floor(rect[1] * 2), math.ceil(rect[2] * 2), math.ceil(rect[3] * 2))
            ImageDraw.Draw(a_mask).rectangle(pixel_rect, fill="white")
            ImageDraw.Draw(b_mask).rectangle(pixel_rect, fill="white")
        row = {
            "page": number + 1,
            "declared_removal_rectangles_pt": rectangles,
            "pixels_identical_outside_removals_144dpi": ImageChops.difference(a_mask, b_mask).getbbox() is None,
            "text_and_positions_identical_outside_removals": outside_words(before, rectangles) == outside_words(after, rectangles),
            "all_uri_annotations_and_positions_preserved": links(before) == links(after),
            "full_text_identical": before.get_text() == after.get_text() if not rectangles else None,
        }
        if not all(row[key] for key in ("pixels_identical_outside_removals_144dpi", "text_and_positions_identical_outside_removals", "all_uri_annotations_and_positions_preserved")):
            raise ValueError(f"Unexpected scientific-content change on page {number + 1}: {row}")
        checks.append(row)
    text = "\n".join(page.get_text() for page in public)
    if any(line and line in text for line in removed_lines):
        raise ValueError("Removed collection-context text remains extractable")
    inspection = inspect(public)
    if not all(inspection.values()):
        raise ValueError(inspection)
    reader = PdfReader(args.output, strict=True)
    if len(reader.pages) != 4 or any(not page.extract_text().strip() for page in reader.pages):
        raise ValueError("Strict PDF reader rejected page content")
    source_author = source.metadata.get("author", "")
    if source_author and source_author.encode() in args.output.read_bytes():
        raise ValueError("Original author metadata remains in raw PDF bytes")
    uris = [item.get("uri") for page in public for item in page.get_links()]
    report = {
        "date": "2026-11-06",
        "operation": "Privacy-only public edition of the historical 2026-08-26 briefing",
        "source_sha256": SOURCE_SHA256,
        "public_sha256": sha(args.output.read_bytes()),
        "source_pages": len(source),
        "public_pages": len(public),
        "public_bytes": args.output.stat().st_size,
        "page_checks": checks,
        "uri_annotation_count": len(uris),
        "unique_source_urls": sorted(set(uris)),
        "all_scientific_content_outside_removals_preserved": True,
        "removed_blocks_not_extractable": True,
        "author_metadata_removed": True,
        "inspection": inspection,
        "strict_reader": {"library": "pypdf", "strict": True, "all4pages_readable": True},
        "scientific_claims_rewritten": False,
        "independent_reproduction": False,
        "visual_qa": {"status": "pending", "human_reader_test": False},
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (args.qa_dir / "public.txt").write_text(text)
    (args.qa_dir / "removed-lines-private.json").write_text(json.dumps(removed_lines, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"public_sha256": report["public_sha256"], "pages": 4, "bytes": report["public_bytes"], "uri_annotations": len(uris), "checks_passed": True}))


if __name__ == "__main__":
    main()
