"""Create a reviewed public derivative from caller-supplied private inputs.

Preserves the source exercise, two synthetic graph diagrams, source credit and
original issue date. Only the declared page-3 recent-topic block is removed.
A fourth public appendix gives formal references, source correction, actual
review scope and a caller-supplied captured model disclosure. Private inputs,
source hash and rendered QA are not embedded in the public PDF or QA record.
"""
import argparse
import hashlib
import io
import json
import re
import sys
from pathlib import Path

import fitz
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from ai_model_provenance import render_disclosure, validate_public_provenance

EDIT_RECTS = [(39, 575, 557, 608)]
TITLE = "참고문헌과 공개판 안내"
REFERENCES = [
    ("[1] Cisco, Radio resource management, Cisco Wireless Controller Configuration Guide, Release 8.5 (updated 9 June 2021; accessed 28 November 2026).", "https://www.cisco.com/c/en/us/td/docs/wireless/controller/8-5/config-guide/b_cg85/radio_resource_management.html"),
    ("[2] Zuse Institute Berlin, What is frequency assignment? (last modified 15 February 2005; accessed 28 November 2026).", "https://fap.zib.de/flavors/content.html"),
    ("[3] M. P. Harrigan et al., Quantum approximate optimization of non-planar graph problems on a planar superconducting processor, Nat. Phys. 17, 332-336 (2021).", "https://doi.org/10.1038/s41567-020-01105-y"),
]
ORIGINAL_GOOGLE_URI = "https://research.google/pubs/quantum-approximate-optimization-of-non-planar-graph-problems-on-a-planar-superconducting-processor/"
NOTES = [
    "원호 발행일: 2026-11-28. 공개판 편집: 2026-11-28 / ATRL 편집부(AEDAUT).",
    "Daily Quantum Exercise의 문제·해설과 교육용 그래프 2개를 보존했습니다. 원 3쪽의 후미 학습 이력을 삭제하고 이 부록을 추가했습니다. 원 1-3쪽의 1/3-3/3 표시는 원호의 구성을 뜻하며, 이 부록은 공개판의 4번째 쪽입니다.",
    "원 3쪽 ZIB 목록의 A Classification of Frequency Assignment Problems는 연결된 웹페이지의 하위 절 제목입니다. 참고문헌 [2]에는 전체 페이지 제목과 마지막 수정일을 표기했습니다. 마지막 수정일을 논문 발행일로 해석하지 않습니다.",
    "그림 1·2는 원호의 가상 통신망을 직접 그린 교육용 합성 도식입니다. 원문·과학 감수의 실제 열람 범위는 함께 게시한 한영 안내와 작성 기록에 남겼습니다. 사람의 문장별 검토나 실제 QPU·무선망 성능 시험은 이번 공개판 작업에서 수행하지 않았습니다.",
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
        fb.setupNameTable({"copyright": names[0], "familyName": "Noto Sans KR Public", "styleName": "Regular", "uniqueFontIdentifier": "NotoSansKRPublic-DQE28", "fullName": "Noto Sans KR Public Regular", "psName": "NotoSansKRPublic-Regular", "version": names[5] + "; document subset cubic-to-quadratic", "licenseDescription": names[13], "licenseInfoURL": names[14]})
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
    ap.add_argument("--ai-provenance", "--model-provenance", dest="ai_provenance", type=Path, required=True)
    ap.add_argument("--qa-dir", type=Path, required=True)
    args = ap.parse_args()
    assert sha(args.source_pdf) == args.expected_source_sha256, "Unreviewed source version"
    model = validate_public_provenance(json.loads(args.ai_provenance.read_text()))
    disclosure = render_disclosure(model, "ko").replace("`", "")
    model_note = "이번 공개판의 편집·감수 설정 / " + disclosure
    root = Path(__file__).resolve().parents[1]
    output = root / "dist/2026-11-28-daily-quantum-exercise.pdf"
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    labels = ["원문 열기", "[3] 원호의 저자 기관 공개 진입점"]
    note_text = "".join(NOTES) + TITLE + "참고문헌공개판 편집과 확인 범위" + "".join(labels) + model_note + "DAILY QUANTUM EXERCISE2026-11-28 / 공개판 부록4 / 4"
    latin_text = "".join(c for c, _ in REFERENCES) + "DAILY QUANTUM EXERCISE4 / 4"
    korean, latin = args.qa_dir / "public-note-font.ttf", args.qa_dir / "public-reference-font.ttf"
    subset_font(args.font, korean, note_text, convert_cff=True)
    subset_font(args.font_latin, latin, latin_text)
    font, latin_font = fitz.Font(fontfile=str(korean)), fitz.Font(fontfile=str(latin))
    assert all(font.has_glyph(ord(ch)) for ch in note_text)
    assert all(latin_font.has_glyph(ord(ch)) for ch in latin_text)
    original, public = fitz.open(args.source_pdf), fitz.open(args.source_pdf)
    assert len(original) == 3
    source_links = [x["uri"] for p in original for x in p.get_links()]
    assert source_links == [REFERENCES[0][1], REFERENCES[1][1], ORIGINAL_GOOGLE_URI]
    for rect in EDIT_RECTS:
        public[2].add_redact_annot(fitz.Rect(rect), fill=(1, 1, 1))
    public[2].apply_redactions(images=2, graphics=1, text=0)
    page = public.new_page(width=original[0].rect.width, height=original[0].rect.height)
    page.insert_font(fontname="DqePublic", fontfile=str(korean))
    page.insert_font(fontname="DqeLatin", fontfile=str(latin))
    ink, teal = (0.075, 0.16, 0.22), (0, 0.42, 0.4)
    page.insert_text((42, 39), "DAILY QUANTUM EXERCISE", fontname="DqeLatin", fontsize=9, color=teal)
    header = "2026-11-28 / 공개판 부록"
    page.insert_text((553-font.text_length(header, fontsize=9), 39), header, fontname="DqePublic", fontsize=9, color=teal)
    page.draw_line((42, 51), (553, 51), color=(0.60, 0.78, 0.74), width=0.6)
    page.insert_text((42, 86), TITLE, fontname="DqePublic", fontsize=21, color=ink)
    page.insert_text((42, 122), "참고문헌", fontname="DqePublic", fontsize=12.3, color=teal)
    y = 143
    for citation, url in REFERENCES:
        for line in wrap(citation, latin_font, 9.3, 507):
            page.insert_text((44, y), line, fontname="DqeLatin", fontsize=9.3, color=ink)
            y += 13.6
        label = "원문 열기"
        page.insert_text((44, y), label, fontname="DqePublic", fontsize=9, color=teal)
        page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(44, y-10, 44+font.text_length(label, fontsize=9), y+3), "uri": url})
        y += 24
    label = labels[1]
    page.insert_text((44, y), label, fontname="DqePublic", fontsize=9, color=teal)
    page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(44, y-10, 44+font.text_length(label, fontsize=9), y+3), "uri": ORIGINAL_GOOGLE_URI})
    y += 35
    page.insert_text((42, y), "공개판 편집과 확인 범위", fontname="DqePublic", fontsize=12.3, color=teal)
    y += 23
    for text in NOTES + [model_note]:
        for line in wrap(text, font, 9.2, 507):
            page.insert_text((44, y), line, fontname="DqePublic", fontsize=9.2, color=ink)
            y += 14
        y += 8
    assert y < 780, y
    page.draw_line((42, 799), (553, 799), color=(0.60, 0.78, 0.74), width=0.6)
    page.insert_text((42, 816), "2026-11-28 / 공개판 부록", fontname="DqePublic", fontsize=8, color=teal)
    page.insert_text((529, 816), "4 / 4", fontname="DqeLatin", fontsize=8, color=teal)
    public.set_metadata({"title": "Daily Quantum Exercise | 두 채널로 네 접속점의 간섭을 줄일 수 있을까", "author": "Daily Quantum Exercise", "subject": "2026-11-28 | 공개 보관판: 원호 3쪽과 참고문헌·AI 활용 안내 부록", "creator": "ATRL AEDAUT / Codex-assisted public archive", "producer": "PyMuPDF 1.26.4", "creationDate": "", "modDate": "", "keywords": ""})
    public.del_xml_metadata()
    public.subset_fonts()
    output.parent.mkdir(parents=True, exist_ok=True)
    public.save(output, garbage=4, deflate=True, clean=True, no_new_id=True)
    public.close()
    final = fitz.open(output)
    reader, source_reader = PdfReader(output, strict=True), PdfReader(args.source_pdf, strict=True)
    extracted = "\n".join(p.extract_text() for p in reader.pages)
    assert len(final) == 4 and final.embfile_count() == 0 and not final.get_xml_metadata()
    assert not final.metadata.get("creationDate") and not final.metadata.get("modDate")
    assert not re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|/Users/|file:/{2}|authuser=|unsubscribe|mail\.google|최근 주제", extracted + str(reader.metadata), re.I)
    assert all(o.extract_text() == n.extract_text() for o, n in zip(source_reader.pages[:2], reader.pages[:2]))
    public_links = [x["uri"] for p in final for x in p.get_links()]
    assert set(public_links) == set(source_links + [REFERENCES[2][1]]) and len(public_links) == 7
    assert "What is frequency assignment?" in " ".join(extracted.split())
    for role in model["roles"]:
        if role.get("model_id"):
            assert role["model_id"] in extracted
    pixels = []
    for i, (old, new) in enumerate(zip(original, final), 1):
        before, after = old.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False), new.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        after.save(args.qa_dir / f"public-{i}.png")
        assert before.width == after.width and before.height == after.height
        a, b = before.samples, after.samples
        if i < 3:
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
    final[3].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False).save(args.qa_dir / "public-4.png")
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
    assert actions == ["/URI"] * 7
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
    info = {"document_id": "2026-11-28-daily-quantum-exercise", "source_sha256": "retained in private run record", "public_sha256": sha(output), "public_bytes": output.stat().st_size, "page_count": 4, "source_page_count": 3, "edit_page": 3, "edit_rectangles_points_top_left": EDIT_RECTS, "appendix_page": 4, "edits": ["Removed only page-3 recent-topic history", "Added fourth-page appendix with formal APS references, exact source titles/date types and source review disclosure", "Retained original scientific source links and added published DOI for the original Harrigan paper", "Added captured allowlisted editorial model and reasoning disclosure", "Removed source timestamps/XMP and replaced anonymous metadata with source credit/original issue date"], "preserved": ["Scientific problem, solutions, tables and two original vector graph diagrams", "Exact144dpi pixels/text ofpages1-2 andpixels outside declaredpage3 edit", "Original issue date andoriginalpagefooters1/3 through3/3; appendix explicitly4/4", "Three original public HTTPS source targets"], "source_uris_preserved": source_links, "uris": public_links, "unique_uri_count": len(set(public_links)), "uri_action_count": len(public_links), "strict_parse": "passed", "embedded_files": 0, "pages_1_to_2_extracted_text_identical": True, "prohibited_action_keys": sorted(found), "annotation_action_types": actions, "personal_address_or_private_path_scan": "passed for body and metadata", "xmp_metadata": False, "original_creation_timestamps_removed": True, "pixel_comparison_144_dpi": pixels, "visual_review": {"original_pages_rendered": [1, 2, 3], "public_pages_rendered": [1, 2, 3, 4], "status": "pending actual final image inspection", "human_sentence_review": "not performed"}, "ai_model_provenance": model, "ai_model_provenance_sha256": sha(args.ai_provenance), "rights_scope": "User-authorized publication of supplied educational issue. Two original diagrams explicitly labeled synthetic in source; no third-party figures copied. Embedded document font subsets only, no standalone font redistribution.", "font_embedding_review": {"source_korean_font_sha256": sha(args.font), "source_latin_font_sha256": sha(args.font_latin), "korean_source_names": name_records(TTFont(args.font)), "latin_source_names": name_records(TTFont(args.font_latin)), "modified_korean_subset": "Noto Sans KR Public; used cubic glyphs converted to quadratic outlines with <=1 font-unit approximation and renamed; copyright/version/OFL metadata retained", "embedded_fonts": fonts, "source_document_fonts": "Original supplied embedded document subsets retained; exact full source-font identity is not asserted from stripped subset names"}, "limitations": ["No actual QPU or radio network performance measurement executed", "Original source, model identities and render QA remain private"]}
    (root / "artifacts/public-pdf-qa.json").write_text(json.dumps(info, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"public_sha256": sha(output), "public_bytes": output.stat().st_size, "pages": len(final), "appendix_bottom": y, "outside_edit_pixels": [p["changed_pixels_outside_declared_edit"] for p in pixels]}))


if __name__ == "__main__":
    main()
