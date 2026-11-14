"""Make the reviewed public derivative from a caller-supplied private source.

Requires PyMuPDF 1.26.4, pypdf, fonttools 4.60.1 and a caller-supplied Korean
TrueType font.
Only the reference/history area of page 4 is replaced. Originals and rendered
QA images stay outside the repository. No source or font path is embedded.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

import fitz
from fontTools import subset
from pypdf import PdfReader

SOURCE_SHA256 = "b7d090ad55bf7a058dbbc602dec55e6eba9623b0147ece6a26af17d22549cbfb"
EDIT_RECT = (43, 399, 552, 780)
REFERENCES = [
    ("[1] C. Holland, J. Levis, R. Nuggehalli, B. Santilli, and J. Winters, UPS optimizes delivery routes, Interfaces 47, 8-23 (2017).",
     "https://doi.org/10.1287/inte.2016.0875"),
    ("[2] Google, Vehicle routing problem with time windows, OR-Tools documentation (accessed 14 November 2026).",
     "https://developers.google.com/optimization/routing/vrptw"),
    ("[3] M. Desrochers, J. Desrosiers, and M. Solomon, A new optimization algorithm for the vehicle routing problem with time windows, Oper. Res. 40, 342-354 (1992).",
     "https://doi.org/10.1287/opre.40.2.342"),
    ("[4] S. Feld, C. Roch, T. Gabor, C. Seidel, F. Neukart, I. Galter, W. Mauerer, and C. Linnhoff-Popien, A hybrid solution method for the capacitated vehicle routing problem using a quantum annealer, Front. ICT 6, 13 (2019).",
     "https://doi.org/10.3389/fict.2019.00013"),
]
NOTES = [
    "[4]의 시간 비교 근거: §5.2.3, 표 4. 원문 확인일: 2026-11-14.",
    "공개판 편집 · 2026-11-14 / ATRL 편집부(AEDAUT)",
    "원호 Daily Quantum Exercise의 문제·해설과 출처 연결을 보존했습니다. 서지를 정식 저자명·제목으로 보완하고 [4]의 절 번호를 정정했습니다. 이전 주제 목록과 내부 수집 기록은 제외했습니다.",
    "Codex가 AI 보조 편집과 전 페이지 출력 검수를 수행했습니다. 사람의 문장별 검토는 수행하지 않았습니다. 운영 수치와 소규모 경로는 교육용 가정입니다.",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wrap(text, font, size, width, cjk=False):
    words = list(text) if cjk else text.split(" ")
    lines, line = [], ""
    for word in words:
        candidate = (line + ("" if cjk or not line else " ") + word)
        if font.text_length(candidate, fontsize=size) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-pdf", type=Path, required=True)
    ap.add_argument("--font", type=Path, required=True)
    ap.add_argument("--qa-dir", type=Path, required=True)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = root / "dist/2026-11-14-daily-quantum-exercise.pdf"
    assert sha(args.source_pdf) == SOURCE_SHA256, "Unreviewed source version"
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    # Keep only used Unicode values so CMap aliases and unused non-BMP ranges
    # cannot produce incorrect extraction mappings in inserted Korean text.
    opts = subset.Options()
    sf = subset.load_font(str(args.font), opts)
    sub = subset.Subsetter(options=opts)
    sub.populate(text="".join(citation+url for citation, url in REFERENCES)+"".join(NOTES))
    sub.subset(sf)
    subset_font = args.qa_dir / "public-note-font.ttf"
    subset.save_font(sf, str(subset_font), opts)
    original = fitz.open(args.source_pdf)
    assert len(original) == 4
    public = fitz.open(args.source_pdf)
    page = public[3]
    source_links = [link["uri"] for p in original for link in p.get_links()]
    assert source_links == [url for _, url in REFERENCES]
    page.add_redact_annot(fitz.Rect(EDIT_RECT), fill=(253 / 255,) * 3)
    page.apply_redactions(images=2, graphics=1, text=0)
    page.insert_font(fontname="DqePublic", fontfile=str(subset_font))
    font = fitz.Font(fontfile=str(subset_font))
    assert all(font.has_glyph(ord(ch)) for ch in "".join(c+u for c, u in REFERENCES)+"".join(NOTES))
    ink = (0.075, 0.16, 0.22)
    teal = (0, 0.42, 0.4)
    y = 414
    for citation, url in REFERENCES:
        top = y - 10
        for line in wrap(citation, font, 9.1, 501):
            page.insert_text((47, y), line, fontname="DqePublic", fontsize=9.1, color=ink)
            y += 13.2
        label = url.removeprefix("https://")
        page.insert_text((47, y), label, fontname="DqePublic", fontsize=8.8, color=teal)
        page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(47, y-10, 47+font.text_length(label, fontsize=8.8), y+3), "uri": url})
        y += 20
    y += 2
    for text in NOTES:
        for line in wrap(text, font, 9, 501, cjk=True):
            page.insert_text((47, y), line, fontname="DqePublic", fontsize=9, color=teal if text.startswith("공개판") else ink)
            y += 13.4
        y += 5
    assert y < 775, y
    public.set_metadata({"title": "Daily Quantum Exercise | 배송 마감 직전의 배차", "author": "Daily Quantum Exercise", "subject": "2026-11-14 | 공개 보관판: 문제와 해설, 서지 보완", "creator": "ATRL AEDAUT / Codex-assisted public archive", "producer": "PyMuPDF 1.26.4", "creationDate": "", "modDate": "", "keywords": ""})
    public.del_xml_metadata()
    public.subset_fonts()
    output.parent.mkdir(parents=True, exist_ok=True)
    public.save(output, garbage=4, deflate=True, clean=True, no_new_id=True)
    public.close()
    final = fitz.open(output)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    assert len(final) == 4 and final.embfile_count() == 0
    assert [link["uri"] for p in final for link in p.get_links()] == source_links
    text = "\n".join(p.get_text() for p in final)
    assert "최근 주제" not in text and "Gmail" not in text and "이전 발송본" not in text
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|/Users/|file:/{2}|authuser=|unsubscribe|mail\.google", text, re.I)
    pixels = []
    for i, (old, new) in enumerate(zip(original, final), 1):
        before = old.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        after = new.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        after.save(args.qa_dir / f"public-{i}.png")
        assert before.width == after.width and before.height == after.height
        old_bytes, new_bytes = before.samples, after.samples
        differences = differences_outside = 0
        for yy in range(before.height):
            for xx in range(before.width):
                start = (yy * before.width + xx) * 3
                if old_bytes[start:start+3] != new_bytes[start:start+3]:
                    differences += 1
                    if i < 4 or not (86 <= xx < 1104 and 798 <= yy < 1560):
                        differences_outside += 1
        assert differences_outside == 0, (i, differences_outside)
        pixels.append({"page": i, "changed_pixels": differences, "changed_pixels_outside_declared_edit": differences_outside})
    reader = PdfReader(output, strict=True)
    assert not final.metadata.get("creationDate") and not final.metadata.get("modDate")
    extracted = "\n".join(p.extract_text() for p in reader.pages)
    assert "공개판 편집" in extracted and "§5.2.3" in extracted
    assert "최근 주제" not in extracted and "Gmail" not in extracted
    prohibited_keys = {"/OpenAction", "/AA", "/JS", "/JavaScript", "/Launch", "/EmbeddedFiles", "/XFA", "/AcroForm", "/RichMedia"}
    found = set()
    seen = set()
    def walk(obj):
        if hasattr(obj, "get_object"):
            obj = obj.get_object()
        ident = id(obj)
        if ident in seen:
            return
        seen.add(ident)
        if isinstance(obj, dict):
            found.update(prohibited_keys.intersection(obj))
            for value in obj.values():
                walk(value)
        elif isinstance(obj, (list, tuple)):
            for value in obj:
                walk(value)
    walk(reader.trailer)
    assert not found, found
    info = {
        "document_id": "2026-11-14-daily-quantum-exercise", "source_sha256": SOURCE_SHA256,
        "public_sha256": sha(output), "page_count": 4, "source_page_count": 4,
        "render_and_edit_tool": "PyMuPDF 1.26.4", "font_subset_tool": "fonttools 4.60.1", "font_sha256": sha(args.font),
        "edit_page": 4, "edit_rectangle_points_top_left": list(EDIT_RECT),
        "edits": ["Removed recent-topic table and internal collection/history note", "Expanded references [1], [3], [4] to verified full author lists and article titles; retained original reference numbering", "Corrected Feld timing location from section 5.3 to section 5.2.3 and Table 4", "Added public derivative and actual AI-assisted review disclosure", "Replaced metadata with publication-safe title, source credit and derivative description; omitted original creation timestamps"],
        "preserved": ["All scientific exercise, solution and explanatory prose on pages 1-4", "Four original public source URI targets", "Four-page count and original issue date", "Pixel identity of pages 1-3 and all page-4 pixels outside declared rectangle at 144 dpi"],
        "uris": source_links, "uri_count": 4, "strict_parse": "passed", "embedded_files": 0,
        "prohibited_action_keys": sorted(found), "personal_address_or_private_path_scan": "passed", "xmp_metadata": False,
        "pixel_comparison_144_dpi": pixels,
        "visual_review": {"pages_rendered": [1, 2, 3, 4], "status": "pending actual image inspection", "human_sentence_review": "not performed"},
        "rights_scope": "User-requested publication of supplied educational issue; no third-party paper figures reproduced",
        "limitations": ["Does not independently reproduce hardware or operational benchmarks", "Original source and QA images remain private; not included in public distribution"]
    }
    (root / "artifacts/public-pdf-qa.json").write_text(json.dumps(info, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({"pages": len(final), "public_sha256": sha(output), "note_bottom": round(y, 2), "changed_pixels_outside_edit": [p["changed_pixels_outside_declared_edit"] for p in pixels]}))


if __name__ == "__main__":
    main()
