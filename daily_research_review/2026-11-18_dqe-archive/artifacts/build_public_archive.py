"""Make the reviewed public derivative from a caller-supplied private source.

Requires PyMuPDF 1.26.4, pypdf, fonttools 4.60.1 and a caller-supplied Korean
TrueType font.
Only the subtitle and reference/history areas of page 4 are replaced. Originals and rendered
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

EDIT_RECTS = [(43, 94, 553, 114), (43, 371, 553, 780)]
SUBTITLE = "출처와 공개 보관판"
HHL_PREPRINT = "https://arxiv.org/abs/0811.3171"
REFERENCES = [
    ('[1] CVX Group, Portfolio optimization, CVX Short Course (accessed 19 November 2026).', 'https://www.cvxgrp.org/cvx_short_course/docs/applications/notebooks/portfolio_optimization.html'),
    ('[2] A. W. Harrow, A. Hassidim, and S. Lloyd, Quantum algorithm for linear systems of equations, Phys. Rev. Lett. 103, 150502 (2009).', 'https://doi.org/10.1103/PhysRevLett.103.150502'),
    ('[3] X.-D. Cai, C. Weedbrook, Z.-E. Su, M.-C. Chen, M. Gu, M.-J. Zhu, L. Li, N.-L. Liu, C.-Y. Lu, and J.-W. Pan, Experimental quantum computing to solve systems of linear equations, Phys. Rev. Lett. 110, 230501 (2013).', 'https://doi.org/10.1103/PhysRevLett.110.230501'),
]
NOTES = [
    '원호 발행일: 2026-11-18. 원호에 기재된 출처 확인일: 2026-11-18.',
    '공개판 편집 · 2026-11-19 / ATRL 편집부(AEDAUT)',
    '원호 Daily Quantum Exercise의 문제·해설과 과학 설명을 보존했습니다. 참고문헌의 전체 저자명과 정식 제목·서지를 보완하고 원 출처 연결을 유지했습니다. 이전 주제 목록과 내부 수집 이력은 제외했습니다.',
    'Codex가 AI 보조 편집과 전 페이지 출력 검수를 수행했습니다. 사람의 문장별 검토는 수행하지 않았습니다. 기업·자산 수·시간·허용오차는 교육용 가정이며, 이 호에서 QPU 실험을 재현하지 않았습니다.',
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
    ap.add_argument("--expected-source-sha256", required=True)
    ap.add_argument("--qa-dir", type=Path, required=True)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = root / "dist/2026-11-18-daily-quantum-exercise.pdf"
    assert sha(args.source_pdf) == args.expected_source_sha256, "Unreviewed source version"
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    # Keep only used Unicode values so CMap aliases and unused non-BMP ranges
    # cannot produce incorrect extraction mappings in inserted Korean text.
    opts = subset.Options()
    sf = subset.load_font(str(args.font), opts)
    sub = subset.Subsetter(options=opts)
    sub.populate(text="".join(citation+url for citation, url in REFERENCES)+"".join(NOTES)+SUBTITLE+HHL_PREPRINT+"원호 [2]의 공개 원문: ")
    sub.subset(sf)
    subset_font = args.qa_dir / "public-note-font.ttf"
    subset.save_font(sf, str(subset_font), opts)
    original = fitz.open(args.source_pdf)
    assert len(original) == 4
    public = fitz.open(args.source_pdf)
    page = public[3]
    source_links = [link["uri"] for p in original for link in p.get_links()]
    assert source_links == [REFERENCES[0][1], HHL_PREPRINT, REFERENCES[2][1]]
    for rect in EDIT_RECTS:
        page.add_redact_annot(fitz.Rect(rect), fill=(1, 1, 1))
    page.apply_redactions(images=2, graphics=1, text=0)
    page.insert_font(fontname="DqePublic", fontfile=str(subset_font))
    font = fitz.Font(fontfile=str(subset_font))
    assert all(font.has_glyph(ord(ch)) for ch in "".join(c+u for c, u in REFERENCES)+"".join(NOTES)+SUBTITLE+HHL_PREPRINT+"원호 [2]의 공개 원문: ")
    ink = (0.075, 0.16, 0.22)
    teal = (0, 0.42, 0.4)
    page.insert_text((46, 107), SUBTITLE, fontname="DqePublic", fontsize=11, color=(66/255, 92/255, 110/255))
    y = 383
    for citation, url in REFERENCES:
        for line in wrap(citation, font, 9.1, 503):
            page.insert_text((46, y), line, fontname="DqePublic", fontsize=9.1, color=ink)
            y += 13.2
        label = url.removeprefix("https://")
        page.insert_text((46, y), label, fontname="DqePublic", fontsize=8.8, color=teal)
        page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(46, y-10, 46+font.text_length(label, fontsize=8.8), y+3), "uri": url})
        y += 20
    label = "원호 [2]의 공개 원문: " + HHL_PREPRINT
    page.insert_text((46, y), label, fontname="DqePublic", fontsize=8.8, color=teal)
    page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(46, y-10, 46+font.text_length(label, fontsize=8.8), y+3), "uri": HHL_PREPRINT})
    y += 24
    for text in NOTES:
        for line in wrap(text, font, 9, 501, cjk=True):
            page.insert_text((46, y), line, fontname="DqePublic", fontsize=9, color=teal if text.startswith("공개판") else ink)
            y += 13.4
        y += 5
    assert y < 775, y
    public.set_metadata({"title": "Daily Quantum Exercise | 양자 선형계의 해를 주문 비중으로", "author": "Daily Quantum Exercise", "subject": "2026-11-18 | 공개 보관판: 문제와 해설, 서지 보완", "creator": "ATRL AEDAUT / Codex-assisted public archive", "producer": "PyMuPDF 1.26.4", "creationDate": "", "modDate": "", "keywords": ""})
    public.del_xml_metadata()
    public.subset_fonts()
    output.parent.mkdir(parents=True, exist_ok=True)
    public.save(output, garbage=4, deflate=True, clean=True, no_new_id=True)
    public.close()
    final = fitz.open(output)
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    assert len(final) == 4 and final.embfile_count() == 0
    public_links = [link["uri"] for p in final for link in p.get_links()]
    assert set(source_links).issubset(public_links)
    assert len(public_links) == 4 and public_links.count(REFERENCES[1][1]) == 1
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
                    if i < 4 or not any(2*x0 <= xx < 2*x1 and 2*y0 <= yy < 2*y1 for x0,y0,x1,y1 in EDIT_RECTS):
                        differences_outside += 1
        assert differences_outside == 0, (i, differences_outside)
        pixels.append({"page": i, "changed_pixels": differences, "changed_pixels_outside_declared_edit": differences_outside})
    reader = PdfReader(output, strict=True)
    assert not final.metadata.get("creationDate") and not final.metadata.get("modDate")
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|/Users/|file:/{2}|authuser=|unsubscribe|mail\.google", str(reader.metadata), re.I)
    actions = []
    for pdf_page in reader.pages:
        for annot_ref in pdf_page.get("/Annots", []):
            annot = annot_ref.get_object()
            assert annot["/Subtype"] == "/Link"
            action = annot["/A"].get_object()
            assert action["/S"] == "/URI" and str(action["/URI"]).startswith("https://")
            actions.append(str(action["/S"]))
    assert actions == ["/URI"] * 4
    extracted = "\n".join(p.extract_text() for p in reader.pages)
    assert "공개판 편집" in extracted and "Experimental quantum computing" in " ".join(extracted.split())
    assert "출처와 공개 보관판" in extracted
    source_reader = PdfReader(args.source_pdf, strict=True)
    assert all(old.extract_text() == new.extract_text() for old,new in zip(source_reader.pages[:3], reader.pages[:3]))
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
        "document_id": "2026-11-18-daily-quantum-exercise", "source_sha256": "retained in private run record",
        "public_sha256": sha(output), "page_count": 4, "source_page_count": 4,
        "render_and_edit_tool": "PyMuPDF 1.26.4", "font_subset_tool": "fonttools 4.60.1", "font_sha256": sha(args.font),
        "edit_page": 4, "edit_rectangles_points_top_left": EDIT_RECTS,
        "edits": ["Removed recent-topic table and internal collection/history note", "Expanded all three references to verified complete author lists and published titles; retained original numbering", "Added canonical DOI for HHL reference [2] while retaining its original public preprint link outside the bibliography", "Replaced page-4 subtitle to describe retained public content", "Added public derivative and actual AI-assisted review disclosure", "Replaced metadata with publication-safe title, source credit and derivative description; omitted original creation timestamps"],
        "preserved": ["All scientific exercise, solution and explanatory prose on pages 1-4", "Three original public source URI targets", "Four-page count and original issue date", "Pixel identity of pages 1-3 and all page-4 pixels outside declared rectangles at 144 dpi"],
        "source_uris_preserved": source_links, "uris": public_links, "uri_count": len(public_links), "strict_parse": "passed", "embedded_files": 0, "pages_1_to_3_extracted_text_identical": True,
        "prohibited_action_keys": sorted(found), "annotation_action_types": actions,
        "personal_address_or_private_path_scan": "passed for extracted body and metadata",
        "xmp_metadata": False, "original_creation_timestamps_removed": True,
        "pixel_comparison_144_dpi": pixels,
        "visual_review": {"pages_rendered": [1, 2, 3, 4], "status": "pending actual image inspection", "human_sentence_review": "not performed"},
        "rights_scope": "User-authorized publication of supplied educational issue; no third-party paper figures reproduced; font embedding provenance recorded separately",
        "limitations": ["Does not independently reproduce hardware or operational benchmarks", "Original source and QA images remain private; not included in public distribution"]
    }
    (root / "artifacts/public-pdf-qa.json").write_text(json.dumps(info, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({"pages": len(final), "public_sha256": sha(output), "note_bottom": round(y, 2), "changed_pixels_outside_edit": [p["changed_pixels_outside_declared_edit"] for p in pixels]}))


if __name__ == "__main__":
    main()
