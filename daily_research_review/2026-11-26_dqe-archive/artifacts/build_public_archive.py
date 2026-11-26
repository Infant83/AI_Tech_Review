"""Create a reviewed public derivative from caller-supplied private inputs.

Only the declared page-5 heading/reference/history areas change. The original
and rendered QA stay private. Source paths and the original hash are not stored
in the public PDF or QA record. Requires the pinned PDF dependencies and supplied
OFL Korean OpenType and Latin TrueType fonts.
"""
import argparse
import hashlib
import io
import json
import re
from pathlib import Path

import fitz
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from pypdf import PdfReader

EDIT_RECTS = [(400, 27, 555, 42), (41, 53, 555, 108), (41, 126, 555, 780)]
TITLE = "참고문헌과 공개 보관판"
SUBTITLE = "Daily Quantum Exercise / 원호 2026-11-26"
HEADING = "참고문헌"
REFERENCES = [
    ("[1] Gurobi Optimization, Pharmaceuticals: Using optimization to mitigate risks across global supply chains (accessed 26 November 2026).", "https://www.gurobi.com/resources/case-studies/pharmaceuticals-using-optimization-to-mitigate-risks-across-global-supply-chains"),
    ("[2] Gurobi Optimization, Multiple scenarios, Gurobi Optimizer Reference Manual 14.0 (accessed 26 November 2026).", "https://docs.gurobi.com/projects/optimizer/en/current/features/multiscenario.html"),
    ("[3] D-Wave, Reformulating a problem, D-Wave Quantum Computing Products documentation, Ocean SDK 9.5.0 (accessed 26 November 2026).", "https://docs.dwavequantum.com/en/latest/quantum_research/reformulating.html"),
    ("[4] D-Wave, Basic workflow: Models and sampling, D-Wave Quantum Computing Products documentation, Ocean SDK 9.5.0 (accessed 26 November 2026).", "https://docs.dwavequantum.com/en/latest/industrial_optimization/workflow.html"),
]
NOTES = [
    "원호 발행일·원문 확인일: 2026-11-26.",
    "공개판 편집 · 2026-11-26 / ATRL 편집부(AEDAUT)",
    "Daily Quantum Exercise의 문제·해설·비교 설명 1-4쪽을 그대로 보존했습니다. 5쪽은 원 출처 연결과 번호를 유지하며 정식 자료명·문서 판본을 보완했습니다. 개인 전달 이력과 내부 작업 메모는 제외했습니다.",
    "[1]은 Gurobi가 공개한 ICRON 솔루션 적용 사례입니다. 공급업체 보고와 교육용 가정의 차이는 4쪽에서 설명합니다.",
    "Codex가 AI 보조 편집과 전 페이지 출력 검수를 수행했습니다. 사람의 문장별 검토는 수행하지 않았습니다. 주문·비용·확률·시간은 교육용 가정이며 실제 QPU 실행이나 산업 성능 시험을 수행하지 않았습니다.",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wrap(text, font, size, width, cjk=False):
    lines, line = [], ""
    for word in list(text) if cjk else text.split(" "):
        candidate = line + ("" if cjk or not line else " ") + word
        if font.text_length(candidate, fontsize=size) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def name_records(font):
    return {str(i): sorted({n.toUnicode() for n in font["name"].names if n.nameID == i}) for i in [0, 1, 2, 5, 13, 14]}


def subset_font(source, output, text, convert_cff=False):
    opts = subset.Options()
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]
    opts.name_languages = [0x409]
    opts.name_legacy = True
    font = subset.load_font(str(source), opts)
    sub = subset.Subsetter(options=opts)
    sub.populate(text=text)
    sub.subset(font)
    if convert_cff:
        # Keep copyright/version/OFL names in a TrueType SFNT embedded subset.
        # The source cubic outlines are approximated at <=1 font-unit error.
        # The modified family receives a distinct public-subset name.
        glyphset = font.getGlyphSet()
        glyfs = {}
        for name in font.getGlyphOrder():
            pen = TTGlyphPen(glyphset)
            glyphset[name].draw(Cu2QuPen(pen, max_err=1.0, reverse_direction=True))
            glyfs[name] = pen.glyph()
        fb = FontBuilder(font["head"].unitsPerEm, isTTF=True)
        fb.setupGlyphOrder(font.getGlyphOrder())
        fb.setupCharacterMap(font.getBestCmap())
        fb.setupGlyf(glyfs)
        fb.setupHorizontalMetrics(font["hmtx"].metrics)
        fb.setupHorizontalHeader(ascent=font["hhea"].ascent, descent=font["hhea"].descent)
        names = {i: next(n.toUnicode() for n in font["name"].names if n.nameID == i) for i in [0, 5, 13, 14]}
        fb.setupNameTable({"copyright": names[0], "familyName": "Noto Sans KR Public", "styleName": "Regular", "uniqueFontIdentifier": "NotoSansKRPublic-DQE26", "fullName": "Noto Sans KR Public Regular", "psName": "NotoSansKRPublic-Regular", "version": names[5] + "; document subset cubic-to-quadratic", "licenseDescription": names[13], "licenseInfoURL": names[14]})
        fb.setupOS2(sTypoAscender=font["OS/2"].sTypoAscender, sTypoDescender=font["OS/2"].sTypoDescender, usWinAscent=font["OS/2"].usWinAscent, usWinDescent=font["OS/2"].usWinDescent, fsType=0)
        fb.setupPost(keepGlyphNames=False)
        fb.save(output)
    else:
        subset.save_font(font, str(output), opts)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-pdf", type=Path, required=True)
    ap.add_argument("--font", type=Path, required=True)
    ap.add_argument("--font-latin", type=Path, required=True)
    ap.add_argument("--expected-source-sha256", required=True)
    ap.add_argument("--qa-dir", type=Path, required=True)
    args = ap.parse_args()
    assert sha(args.source_pdf) == args.expected_source_sha256, "Unreviewed source version"
    root = Path(__file__).resolve().parents[1]
    output = root / "dist/2026-11-26-daily-quantum-exercise.pdf"
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    note_text = "".join(NOTES) + TITLE + SUBTITLE + HEADING + "2026-11-26 / 공개판원문 열기"
    latin_text = "".join(c for c, _ in REFERENCES)
    korean = args.qa_dir / "public-note-font.ttf"
    latin = args.qa_dir / "public-reference-font.ttf"
    subset_font(args.font, korean, note_text, convert_cff=True)
    subset_font(args.font_latin, latin, latin_text)
    font, latin_font = fitz.Font(fontfile=str(korean)), fitz.Font(fontfile=str(latin))
    assert all(font.has_glyph(ord(ch)) for ch in note_text)
    assert all(latin_font.has_glyph(ord(ch)) for ch in latin_text)
    original = fitz.open(args.source_pdf)
    public = fitz.open(args.source_pdf)
    assert len(original) == 5
    source_links = [x["uri"] for p in original for x in p.get_links()]
    assert source_links == [u for _, u in REFERENCES]
    page = public[4]
    for rect in EDIT_RECTS:
        page.add_redact_annot(fitz.Rect(rect), fill=(1, 1, 1))
    page.apply_redactions(images=2, graphics=1, text=0)
    page.insert_font(fontname="DqePublic", fontfile=str(korean))
    page.insert_font(fontname="DqeLatin", fontfile=str(latin))
    ink, teal = (0.075, 0.16, 0.22), (0, 0.42, 0.4)
    header = "2026-11-26 / 공개판"
    page.insert_text((551-font.text_length(header, fontsize=9), 37), header, fontname="DqePublic", fontsize=9, color=teal)
    page.insert_text((44, 77), TITLE, fontname="DqePublic", fontsize=22, color=ink)
    page.insert_text((44, 101), SUBTITLE, fontname="DqePublic", fontsize=10, color=(66/255, 92/255, 110/255))
    page.insert_text((44, 142), HEADING, fontname="DqePublic", fontsize=12.3, color=teal)
    y = 163
    for citation, url in REFERENCES:
        for line in wrap(citation, latin_font, 9.3, 503):
            page.insert_text((46, y), line, fontname="DqeLatin", fontsize=9.3, color=ink)
            y += 13.6
        label = "원문 열기"
        page.insert_text((46, y), label, fontname="DqePublic", fontsize=9, color=teal)
        page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(46, y-10, 46+font.text_length(label, fontsize=9), y+3), "uri": url})
        y += 24
    y += 14
    for text in NOTES:
        for line in wrap(text, font, 9.3, 501):
            page.insert_text((46, y), line, fontname="DqePublic", fontsize=9.3, color=teal if text.startswith("공개판") else ink)
            y += 14
        y += 7
    assert y < 775, y
    public.set_metadata({"title": "Daily Quantum Exercise | 공급사를 늘리면 납기 위험이 줄어들까", "author": "Daily Quantum Exercise", "subject": "2026-11-26 | 공개 보관판: 문제와 해설, 서지 보완", "creator": "ATRL AEDAUT / Codex-assisted public archive", "producer": "PyMuPDF 1.26.4", "creationDate": "", "modDate": "", "keywords": ""})
    public.del_xml_metadata()
    public.subset_fonts()
    output.parent.mkdir(parents=True, exist_ok=True)
    public.save(output, garbage=4, deflate=True, clean=True, no_new_id=True)
    public.close()
    final = fitz.open(output)
    reader = PdfReader(output, strict=True)
    extracted = "\n".join(p.extract_text() for p in reader.pages)
    assert len(final) == 5 and final.embfile_count() == 0
    assert not final.metadata.get("creationDate") and not final.metadata.get("modDate")
    assert not final.get_xml_metadata()
    prohibited_text = r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|/Users/|file:/{2}|authuser=|unsubscribe|mail\.google|최근 주제|보낸 메일|사용자 답안|감수:"
    assert not re.search(prohibited_text, extracted + str(reader.metadata), re.I)
    public_links = [x["uri"] for p in final for x in p.get_links()]
    assert public_links == source_links
    assert "참고문헌과 공개 보관판" in extracted and "Gurobi Optimizer Reference Manual 14.0" in " ".join(extracted.split())
    source_reader = PdfReader(args.source_pdf, strict=True)
    assert all(o.extract_text() == n.extract_text() for o, n in zip(source_reader.pages[:4], reader.pages[:4]))
    pixels = []
    for i, (old, new) in enumerate(zip(original, final), 1):
        before, after = old.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False), new.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        after.save(args.qa_dir / f"public-{i}.png")
        assert before.width == after.width and before.height == after.height
        a, b = before.samples, after.samples
        if i < 5:
            assert a == b
            changed = outside = 0
        else:
            changed = outside = 0
            for yy in range(before.height):
                start, end = yy*before.width*3, (yy+1)*before.width*3
                if a[start:end] == b[start:end]:
                    continue
                for xx in range(before.width):
                    k = start + xx*3
                    if a[k:k+3] != b[k:k+3]:
                        changed += 1
                        if not any(2*x0 <= xx < 2*x1 and 2*y0 <= yy < 2*y1 for x0,y0,x1,y1 in EDIT_RECTS):
                            outside += 1
            assert outside == 0, outside
        pixels.append({"page": i, "changed_pixels": changed, "changed_pixels_outside_declared_edit": outside})
    prohibited_keys = {"/OpenAction", "/AA", "/JS", "/JavaScript", "/Launch", "/EmbeddedFiles", "/XFA", "/AcroForm", "/RichMedia"}
    found, seen, actions = set(), set(), []
    def walk(obj):
        if hasattr(obj, "get_object"):
            obj = obj.get_object()
        if id(obj) in seen:
            return
        seen.add(id(obj))
        if isinstance(obj, dict):
            found.update(prohibited_keys.intersection(obj))
            for value in obj.values():
                walk(value)
        elif isinstance(obj, (list, tuple)):
            for value in obj:
                walk(value)
    walk(reader.trailer)
    assert not found
    for p in reader.pages:
        for ref in p.get("/Annots", []):
            an = ref.get_object()
            assert an["/Subtype"] == "/Link"
            action = an["/A"].get_object()
            assert action["/S"] == "/URI" and str(action["/URI"]).startswith("https://")
            actions.append(str(action["/S"]))
    assert actions == ["/URI"] * 4
    fonts, seen_xrefs = [], set()
    for p in final:
        for xref, _, _, name, *_ in p.get_fonts(full=True):
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)
            _, _, _, raw = final.extract_font(xref)
            if not raw:
                continue
            tf = TTFont(io.BytesIO(raw))
            rec = name_records(tf)
            fonts.append({"embedded_name": name, "font_program_sha256": hashlib.sha256(raw).hexdigest(), "fsType": tf["OS/2"].fsType, "name_records": rec})
            if name.startswith("Noto"):
                assert all(rec[str(i)] for i in [0, 5, 13, 14]) and tf["OS/2"].fsType == 0
    info = {"document_id": "2026-11-26-daily-quantum-exercise", "source_sha256": "retained in private run record", "public_sha256": sha(output), "public_bytes": output.stat().st_size, "page_count": 5, "source_page_count": 5, "edit_page": 5, "edit_rectangles_points_top_left": EDIT_RECTS, "edits": ["Removed recent-topic table and internal collection, correspondence and assessment notes", "Replaced page-5 heading and completed official reference names, corporate attribution and actual document versions", "Preserved all four original scientific source URI targets and numbering", "Added original issue date, public derivative history and actual AI-assisted review disclosure", "Removed source creation timestamps and XMP; kept publication-safe source credit"], "preserved": ["All scientific exercise, solutions and comparisons on pages 1-4", "Five-page count and original issue date", "All four original HTTPS URI targets", "Exact extracted text and 144 dpi pixels for pages 1-4; pixels outside declared page-5 edits"], "source_uris_preserved": source_links, "uris": public_links, "uri_count": 4, "strict_parse": "passed", "embedded_files": 0, "pages_1_to_4_extracted_text_identical": True, "prohibited_action_keys": sorted(found), "annotation_action_types": actions, "personal_address_or_private_path_scan": "passed for body and metadata", "xmp_metadata": False, "original_creation_timestamps_removed": True, "pixel_comparison_144_dpi": pixels, "visual_review": {"original_pages_rendered": [1, 2, 3, 4, 5], "public_pages_rendered": [1, 2, 3, 4, 5], "status": "pending final image inspection", "human_sentence_review": "not performed"}, "rights_scope": "User-authorized publication of supplied educational issue; no third-party figures reproduced; embedded document font subsets only, no standalone font redistribution", "font_embedding_review": {"source_korean_font_sha256": sha(args.font), "source_latin_font_sha256": sha(args.font_latin), "korean_source_names": name_records(TTFont(args.font)), "latin_source_names": name_records(TTFont(args.font_latin)), "modified_korean_subset": "Noto Sans KR Public; used cubic glyphs converted to quadratic outlines with <=1 font-unit approximation and renamed; copyright/version/OFL metadata retained", "embedded_fonts": fonts, "source_document_fonts": "Original embedded subsets retained under their print-and-preview fsType4 flags; stripped original version and license names do not establish full source-font identity"}, "limitations": ["No actual QPU, industrial solver or operational benchmark executed", "Original source and render QA remain private"]}
    (root / "artifacts/public-pdf-qa.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"public_sha256": sha(output), "public_bytes": output.stat().st_size, "pages": len(final), "note_bottom": y, "outside_edit_pixels": [p["changed_pixels_outside_declared_edit"] for p in pixels]}))


if __name__ == "__main__":
    main()
