"""Make a privacy-only public copy of the historical five-page DQB.

The caller supplies the private original, Korean fonts and a private QA folder.
Scientific prose, numbers, publication labels, author credits and nine public
source links are retained. No archive registration or publication is performed.
Requires PyMuPDF, Pillow and pypdf. Every rebuild resets root review to pending.
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
from pypdf.generic import IndirectObject, StreamObject

TOPIC = Path(__file__).resolve().parents[1]
REPOSITORY = TOPIC.parent
SOURCE_SHA256 = "cacfc0c727044c7ff8b57980f925eb71ac2277ac9d0050fd849591308f7314dd"
DEFAULT_REPORT = REPOSITORY / ".automation/writing-reviews/legacy-refresh/2026-11-11-stack/briefing-publication-qa.json"
# Zero-based pages and PDF points. The scientific checklist on page 5 stays.
REMOVALS = {
    0: [(56.5, 500.8, 539.0, 520.2)],
    4: [(56.5, 482.5, 539.0, 501.8)],
}
REPLACEMENTS = [
    {"page": 0, "find": "이메일", "text": "공고", "rect": (266.6, 329.9, 286.3, 338.9), "bold": False, "center": False},
    {"page": 1, "find": "공식 이메일 수신", "text": "[산업/제품] 공식 공고", "rect": (217.3, 89.6, 377.9, 98.4), "bold": True, "center": True},
    {"page": 4, "find": "6. 연구자·산업계 소셜 신호와 체크리스트", "text": "6. 연구 메모와 체크리스트", "rect": (56.5, 59.2, 341.3, 79.9), "bold": True, "center": False},
    {"page": 4, "find": "검증된 소셜 신호", "text": "[저자 해설] 공개 연구 게시물", "rect": (211.9, 108.1, 383.4, 116.9), "bold": True, "center": True},
    {"page": 4, "find": "이메일에", "text": "공고에", "rect": (157.0, 462.2, 183.0, 471.3), "bold": False, "center": False},
]
FORBIDDEN_ACTION = re.compile(rb"/(?:OpenAction|AA|JavaScript|JS|Launch|GoToR|SubmitForm|ImportData|EmbeddedFiles|RichMedia|XFA)\b")
PRIVATE_TEXT = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|/(?:Users|home|tmp)/|[A-Za-z]:\\(?:Users|Temp)\\|(?:access_token|refresh_token|api_key)\s*[:=]", re.IGNORECASE)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bitmap(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def outside_words(page, rectangles):
    return Counter(tuple(round(v, 3) for v in word[:4]) + (word[4],)
        for word in page.get_text("words")
        if not any(fitz.Rect(word[:4]).intersects(fitz.Rect(rect)) for rect in rectangles))


def links(page):
    return sorted((link.get("kind"), link.get("uri", ""), tuple(round(v, 3) for v in link["from"]))
                  for link in page.get_links())


def find_line(page, needle):
    matches = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"])
            if needle in text:
                matches.append((line, text))
    if len(matches) != 1:
        raise ValueError("Expected one historical source label")
    return matches[0][0]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("--output", type=Path, default=TOPIC / "artifacts/daily_quantum_brief_2026-08-30.pdf")
    p.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    p.add_argument("--qa-dir", type=Path, required=True)
    p.add_argument("--font-regular", type=Path, required=True)
    p.add_argument("--font-bold", type=Path, required=True)
    args = p.parse_args()
    if any(path.resolve().is_relative_to(REPOSITORY.resolve()) for path in (args.source, args.qa_dir)):
        raise ValueError("Private input and QA must remain outside the public repository")
    raw = args.source.read_bytes()
    if sha(raw) != SOURCE_SHA256:
        raise ValueError("Unexpected historical source PDF")
    source = fitz.open(stream=raw, filetype="pdf")
    public = fitz.open(stream=raw, filetype="pdf")
    if len(source) != 5:
        raise ValueError("Expected five historical source pages")
    rectangles = {page: list(regions) for page, regions in REMOVALS.items()}
    replacements = []
    for item in REPLACEMENTS:
        line = find_line(source[item["page"]], item["find"])
        span = line["spans"][0]
        matches = source[item["page"]].search_for(item["find"])
        if len(matches) != 1:
            raise ValueError("Expected one exact historical label match")
        x = matches[0].x0
        origin = (x, span["origin"][1])
        font = fitz.Font(fontfile=str(args.font_bold if item["bold"] else args.font_regular))
        width = font.text_length(item["text"], fontsize=span["size"])
        if item["center"]:
            origin = ((item["rect"][0] + item["rect"][2] - width) / 2, origin[1])
        if origin[0] + width > item["rect"][2]:
            raise ValueError("Replacement source-type label is too wide")
        color = span["color"]
        rgb = (((color >> 16) & 255) / 255, ((color >> 8) & 255) / 255, (color & 255) / 255)
        replacements.append({**item, "origin": origin, "size": span["size"], "color": rgb})
        rectangles.setdefault(item["page"], []).append(item["rect"])
    removed_lines = []
    for number, regions in rectangles.items():
        for rect in regions:
            removed_lines += [line for line in source[number].get_textbox(fitz.Rect(rect)).splitlines() if line]
            # Transparent redaction leaves the original table/badge vector fill.
            public[number].add_redact_annot(fitz.Rect(rect), fill=None)
        public[number].apply_redactions(images=0, graphics=0, text=0)
    for item in replacements:
        name = "PublicBold" if item["bold"] else "PublicRegular"
        public[item["page"]].insert_font(fontname=name, fontfile=str(args.font_bold if item["bold"] else args.font_regular))
        public[item["page"]].insert_text(item["origin"], item["text"], fontname=name, fontsize=item["size"], color=item["color"])
    allowed = {key: value for key, value in source.metadata.items()
               if key in {"title", "subject", "keywords", "creator", "producer", "trapped"}}
    public.set_metadata({**allowed, "author": "", "creationDate": "", "modDate": ""})
    public.del_xml_metadata()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    public.subset_fonts()
    identifier = sha((SOURCE_SHA256 + ":privacy-only-2026-11-11-v1").encode())[:32]
    public.xref_set_key(-1, "ID", f"[<{identifier}><{identifier}>]")
    public.save(args.output, garbage=4, deflate=True, clean=True, no_new_id=True)
    public.close()
    public = fitz.open(args.output)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    page_checks = []
    for number, (before, after) in enumerate(zip(source, public)):
        regions = rectangles.get(number, [])
        a, b = bitmap(before), bitmap(after)
        a.save(args.qa_dir / f"original-{number+1}.png")
        b.save(args.qa_dir / f"public-{number+1}.png")
        for rect in regions:
            pixels = (math.floor(rect[0]*2), math.floor(rect[1]*2), math.ceil(rect[2]*2), math.ceil(rect[3]*2))
            ImageDraw.Draw(a).rectangle(pixels, fill="white")
            ImageDraw.Draw(b).rectangle(pixels, fill="white")
        check = {"page": number+1, "declared_edit_rectangles_pt": regions,
            "pixels_identical_outside_edits_144dpi": ImageChops.difference(a, b).getbbox() is None,
            "text_and_positions_identical_outside_edits": outside_words(before, regions) == outside_words(after, regions),
            "all_uri_annotations_and_positions_preserved": links(before) == links(after),
            "full_text_identical": before.get_text() == after.get_text() if not regions else None}
        if not all(check[key] for key in ("pixels_identical_outside_edits_144dpi", "text_and_positions_identical_outside_edits", "all_uri_annotations_and_positions_preserved")):
            raise ValueError(f"Unexpected content change on page{number+1}: {check}")
        page_checks.append(check)
    all_text = "\n".join(page.get_text() for page in public)
    forbidden_terms = ("이메일", "공식 메일이 도착", "지난 실행", "Quantum Advantage Tracker", "소셜 신호", "KST")
    object_count, stream_count, bad_active = 0, 0, []
    for xref in range(1, public.xref_length()):
        data = public.xref_object(xref, compressed=False).encode()
        object_count += 1
        if public.xref_is_stream(xref):
            data += b"\n" + public.xref_stream(xref)
            stream_count += 1
        if FORBIDDEN_ACTION.search(data):
            bad_active.append(xref)
    inspection = {"no_author_or_exact_production_time": not any(public.metadata.get(k) for k in ("author", "creationDate", "modDate")),
        "no_private_text_or_paths": not PRIVATE_TEXT.search(all_text + json.dumps(public.metadata, ensure_ascii=False)),
        "no_collection_or_run_status_text": not any(term in all_text for term in forbidden_terms),
        "no_xml_metadata": public.xref_xml_metadata() == 0, "no_embedded_files": public.embfile_count() == 0,
        "no_widgets": all(not list(page.widgets() or ()) for page in public), "no_active_actions_in_objects_or_decoded_streams": not bad_active,
        "no_null_or_replacement_glyphs": "\x00" not in all_text and "\ufffd" not in all_text,
        "all5pages_retained": len(public) == 5,
        "public_author_post_credits_retained": all(t in all_text for t in ("Danish Khan", "Anima Anandkumar", "[3] Danish Khan", "[4] Anima Anandkumar")),
        "scientific_checklist_retained": all(t in all_text for t in ("오늘의 연구자 체크리스트", "SCF convergence", "physical qubit-time"))}
    if not all(inspection.values()):
        raise ValueError(inspection)
    strict = PdfReader(args.output, strict=True)
    if len(strict.pages) != 5 or any(not page.extract_text().strip() for page in strict.pages):
        raise ValueError("Strict PDF parsing failed")
    strict_objects, strict_streams = 0, 0
    references = {(number, generation) for generation, objects in strict.xref.items()
                  for number in objects if number != 0}
    references |= {(number, 0) for number in strict.xref_objStm}
    for number, generation in sorted(references):
        obj = strict.get_object(IndirectObject(number, generation, strict))
        strict_objects += 1
        if isinstance(obj, StreamObject):
            obj.get_data()
            strict_streams += 1
    for private_marker in ("지난 실행", "OpenAI Codex"):
        if private_marker.encode() in args.output.read_bytes():
            raise ValueError("Removed metadata/collection bytes remain")
    uris = [link["uri"] for page in public for link in page.get_links()]
    if len(uris) != 9 or any(not uri.startswith("https://") for uri in uris):
        raise ValueError("Expected nine public HTTPS source links")
    report = {"date": "2026-11-11", "operation": "Privacy-only public copy of the historical2026-08-30DQB",
        "source_sha256": SOURCE_SHA256, "public_sha256": sha(args.output.read_bytes()),
        "source_pages": 5, "public_pages": len(public), "public_bytes": args.output.stat().st_size,
        "page_checks": page_checks, "uri_annotation_count": len(uris), "unique_source_urls": sorted(set(uris)),
        "all_scientific_content_outside_edits_preserved": True, "scientific_claims_rewritten": False,
        "collection_context_removed": True, "source_type_labels_generalized": True,
        "author_metadata_removed": True, "exact_production_timestamps_removed": True,
        "public_author_credits_and_scientific_checklist_preserved": True,
        "inspection": inspection, "strict_reader": {"library": "pypdf", "strict": True, "all5pages_readable": True,
            "all_indirect_objects_resolved": strict_objects, "all_streams_decoded": strict_streams},
        "pdf_structure": {"objects_inspected": object_count, "decoded_streams_inspected": stream_count},
        "visual_qa": {"status": "pending_root_review", "sanitizer_author_read_all_original5pages": True,
            "human_reader_test": False},
        "independent_reproduction": False}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (args.qa_dir / "public.txt").write_text(all_text)
    (args.qa_dir / "removed-lines-private.json").write_text(json.dumps(removed_lines, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"public_sha256": report["public_sha256"], "pages": 5, "bytes": report["public_bytes"], "uri_annotations": 9, "checks_passed": True}))


if __name__ == "__main__":
    main()
