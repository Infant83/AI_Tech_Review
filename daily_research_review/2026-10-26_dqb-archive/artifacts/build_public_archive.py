"""Build the source-checked public corrected edition of the 2026-10-26 DQB.

The private source and QA images stay outside the distribution. Only the listed
collection block, broken formula glyphs and reference [3] change; a visible
correction page is appended. Requires PyMuPDF, ReportLab, Pillow and Poppler.
This builder never registers documents or publishes a site.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
from xml.sax.saxutils import escape
import fitz
from PIL import Image, ImageChops, ImageDraw
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = "14e04db9d6b85bb5cabbf8765a1e667615896e43642c3d5ef93e95174c4d73af"
# Coordinates in points from top-left. The table rule is y=564.5007, while the
# collection heading starts y=565.7848 and the last collection line ends y=614.6808.
COLLECTION_RECT = (61.0, 565.0, 534.0, 618.0)
LINKS = ["https://www.nature.com/articles/s42005-026-02924-w",
         "https://arxiv.org/abs/2610.31070", "https://arxiv.org/abs/2610.29779",
         "https://arxiv.org/abs/2610.31330", "https://arxiv.org/abs/2610.31260"]
REPAIRS = [(r"ReAg\x00Cl\x00", "ReAg2Cl6"), (r"BeH\x00", "BeH2"),
           (r"H\x00O", "H2O"), (r"NH\x00", "NH3"), (r"H\x00", "H2"),
           (r"10\x00\x00", "10^-6"), (r"2\x00", "2^n"), (r"N\x00", "N^d")]
REFERENCE_3 = "[3] Petronilo et al. Mamba Quantum Eigensolver (MQE). arXiv:2610.29779 v1 (2026-10-21)."
NOTE_SECTIONS = [
 ("1. 공개 범위", "원 DQB 1쪽의 ‘수집 범위’ 제목과 메일·검색 경위 문단을 제거했다. 과학 본문과 직접 링크 5개는 보존하며, 아래에 명시한 화학식·지수 표기와 참고문헌만 바로잡았다."),
 ("2. 깨진 화학식·지수 복원", "원 PDF의 일부 첨자가 실제 화면에서도 교차 상자로 나타났다. 원문을 대조해 ReAg2Cl6, H2, BeH2, H2O, NH3와 에너지 오차의 지수 10^-6을 복원했다. Fokker-Planck 모형은 좌표당 N=2^n개의 격자점, 전체 분포 벡터는 N^d개 성분이며 레지스터는 dn 큐비트다. 복원 구간에는 글꼴 호환성을 위해 ASCII 숫자·지수 표기를 사용했다."),
 ("3. Mamba 논문의 저자·제목 정정", "참고문헌 [3]의 저자를 G. X. A. Petronilo, M. R. Araújo, Erico S. Teixeira, Clebson Cruz로 바로잡았다. 전체 제목은 Mamba Quantum Eigensolver (MQE): A Selective State Space Model for Scalable Ground State Simulations in Quantum Chemistry다. 원문 v1의 저자·제목을 확인했으며, 본문 참고문헌 행은 짧은 제목으로 표기했다."),
 ("4. 결과를 읽을 조건", "Mamba-QE의 chemical accuracy는 H2 / STO-3G / CAS(2,2)의 평가 구조 16개에 관한 보고다. <3×10^-6 Ha는 최소 에너지 오차이며 모든 구조의 오차가 그 값보다 작다는 뜻이 아니다(원문 §III, Table 1, 결론). 평탄 Chern 밴드 논문은 2026년 10월 25일 공개된 동료심사 후 accepted 원고를 대조했다. 재료의 실험 관측이 아닌 전자구조·다체 계산 예측이며, 같은 연구의 이전 프리프린트가 있다."),
 ("5. 정정 근거와 보존 검사", "재료 화학식: DOI 10.1038/s42005-026-02924-w. Mamba 저자·제목·에너지 오차: arXiv:2610.29779v1의 서지, §III, Table 1 및 결론. 분포 격자·성분 수: arXiv:2610.31330v1 §II. 변경 좌표 밖의 원 본문·표·쪽번호를 픽셀로 비교하고, 원문 링크·메타데이터·첨부와 실행 동작을 점검했다. 원 논문의 계산·QPU 실험을 독립 재현한 것은 아니다."),
]
DISCLOSURE = ("책임 편집 김현중 · AI 보조 OpenAI Codex · 근거 기준일 2026-10-26. "
 "root: 원문 대조·정정 검토·게시; dqb_archive_workflow: 보관본 정제·정정 조판·출력 검사. "
 "정확한 실행 모델 식별자 미보존. AI Tech Review Editorial Harness 2026.08 · 과학 설명 준칙 1.0. "
 "사람의 문장별 전체 검토 완료를 뜻하지 않는다.")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def links(page):
    return [x["uri"] for x in page.get_links() if "uri" in x]

def image(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

def note_pdf(regular, bold, fallback):
    for name, path in (("NoteRegular", regular), ("NoteBold", bold), ("NoteFallback", fallback)):
        pdfmetrics.registerFont(TTFont(name, str(path)))
    stream = io.BytesIO()
    canvas = Canvas(stream, pagesize=A4, invariant=1)
    canvas.setTitle("Daily Quantum Brief 2026-10-26 - Public edition corrections")
    canvas.setAuthor("Hyun-Jung Kim")
    width, height = A4
    y = height - 52
    def para(text, size=10.2, leading=15, bold=False, after=7, color="#263a47"):
        nonlocal y
        font = "NoteBold" if bold else "NoteRegular"
        face = pdfmetrics.getFont(font).face.charToGlyph
        text = "".join(escape(c) if ord(c) in face else f'<font name="NoteFallback">{escape(c)}</font>' for c in text)
        item = Paragraph(text, ParagraphStyle("note", fontName=font, fontSize=size, leading=leading,
                                              textColor=HexColor(color), wordWrap="CJK"))
        _, h = item.wrap(width - 110, height)
        y -= h
        item.drawOn(canvas, 55, y)
        y -= after
    para("DAILY QUANTUM BRIEF / 2026-10-26", 9, 12, color="#007e8c", after=12)
    para("공개 보관본 편집·정정 기록", 19, 25, True, after=6)
    para("원 DQB 4쪽 + 정정 기록 1쪽", 9, 13, color="#60717d", after=5)
    para("책임 편집 김현중 · AI 보조 Codex · 근거 기준일 2026-10-26", 8.3, 12, color="#60717d", after=16)
    for heading, body in NOTE_SECTIONS:
        para(heading, 11, 15, True, after=4, color="#007e8c")
        para(body, after=11)
    para(DISCLOSURE, 8.2, 11.8, color="#60717d", after=0)
    if y < 60:
        raise ValueError(f"Correction note exceeds one page: {y}")
    canvas.setStrokeColor(HexColor("#cadadd"))
    canvas.line(55, 40, width - 55, 40)
    canvas.setFont("NoteRegular", 7.5)
    canvas.setFillColor(HexColor("#60717d"))
    canvas.drawString(55, 27, "AI TECH REVIEW / PUBLIC EDITION CORRECTIONS")
    canvas.drawRightString(width - 55, 27, "5")
    canvas.showPage()
    canvas.save()
    return stream.getvalue(), y

def find_repairs(page):
    operations = []
    for block in page.get_text("rawdict")["blocks"]:
        for line in block.get("lines", []):
            chars = []
            for span in line["spans"]:
                chars.extend({**c, "size": span["size"], "color": span["color"]} for c in span["chars"])
            text = "".join(c["c"] for c in chars)
            covered = set()
            for pattern, replacement in REPAIRS:
                for match in re.finditer(pattern, text):
                    if covered.intersection(range(match.start(), match.end())):
                        continue
                    selected = chars[match.start():match.end()]
                    rect = fitz.Rect(selected[0]["bbox"])
                    for c in selected[1:]:
                        rect |= fitz.Rect(c["bbox"])
                    first = selected[0]
                    color = first["color"]
                    operations.append({"rect": list(rect), "origin": list(first["origin"]),
                     "size": first["size"], "color": [(color >> 16 & 255) / 255, (color >> 8 & 255) / 255, (color & 255) / 255],
                     "replacement": replacement, "kind": "source-checked formula glyph repair"})
                    covered.update(range(match.start(), match.end()))
    return operations

def inspect(document):
    text = "\n".join(p.get_text() for p in document)
    original_body = "\n".join(document[i].get_text() for i in range(4))
    metadata = json.dumps(document.metadata)
    objects = "\n".join(document.xref_object(x, compressed=False) for x in range(1, document.xref_length()))
    checks = {
     "no_null_or_replacement_glyphs": "\x00" not in text and "\ufffd" not in text,
     "collection_context_removed": not any(t in original_body for t in ("수집 범위", "Gmail", "LinkedIn", "지난 회차 이후")),
     "incorrect_reference_authors_removed": "Bhattacharya" not in text and "Sampath" not in text,
     "no_email": not bool(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text + metadata + objects)),
     "no_private_paths": not bool(re.search(r"/(?:Users|home|private|tmp)/|file://|localhost", text + metadata + objects, re.I)),
     "no_embedded_files": document.embfile_count() == 0,
     "no_active_actions": not bool(re.search(r"/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm)\b", objects)),
     "no_xmp_metadata": not bool(document.get_xml_metadata()),
     "all_original_reference_links_unchanged": [u for p in document for u in links(p)] == LINKS,
    }
    if not all(checks.values()):
        raise ValueError(f"PDF inspection failed: {checks}")
    return {"checks_passed": checks, "uri_annotations": len(LINKS), "unique_public_uris": LINKS,
            "embedded_files": document.embfile_count(), "metadata": document.metadata}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-pdf", type=Path, required=True)
    parser.add_argument("--repair-font", type=Path, required=True)
    parser.add_argument("--font-regular", type=Path, required=True)
    parser.add_argument("--font-bold", type=Path, required=True)
    parser.add_argument("--font-fallback", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "dist/2026-10-26-daily-quantum-brief.pdf")
    parser.add_argument("--qa-dir", type=Path, default=ROOT / "tmp/pdfs")
    parser.add_argument("--qa-report", type=Path, default=ROOT / "notes/production-qa.json")
    args = parser.parse_args()
    raw = args.source_pdf.read_bytes()
    if digest(raw) != SOURCE_SHA256:
        raise ValueError("Input differs from the explicitly reviewed four-page source")
    original = fitz.open(stream=raw, filetype="pdf")
    output = fitz.open(stream=raw, filetype="pdf")
    assert len(original) == 4
    assert [u for p in original for u in links(p)] == LINKS
    all_ops = []
    repair_font = fitz.Font(fontfile=str(args.repair_font))
    for index, page in enumerate(output):
        operations = find_repairs(original[index])
        assert len(operations) == [4, 5, 6, 1][index], (index, len(operations))
        if index == 0:
            operations.append({"rect": list(COLLECTION_RECT), "kind": "remove private collection-context block"})
        if index == 3:
            ref = next(s for b in original[index].get_text("dict")["blocks"] for l in b.get("lines", [])
                       for s in l["spans"] if s["text"].startswith("[3] Bhattacharya"))
            # Preserve the original separate '원문' link and its annotation.
            operations.append({"rect": [ref["bbox"][0], ref["bbox"][1], 370.9, ref["bbox"][3]],
             "origin": list(ref["origin"]), "size": ref["size"], "color": [96/255, 113/255, 125/255],
             "replacement": REFERENCE_3, "kind": "correct reference 3 authors and short title"})
        for op in operations:
            r = fitz.Rect(op["rect"])
            page.add_redact_annot(fitz.Rect(r.x0+.025, r.y0+.025, r.x1-.025, r.y1-.025), fill=None)
        page.apply_redactions(images=0, graphics=0, text=0)
        page.insert_font(fontname="DqbRepair", fontfile=str(args.repair_font))
        for op in operations:
            if "replacement" not in op:
                continue
            size = op["size"]
            width = op["rect"][2] - op["rect"][0]
            length = repair_font.text_length(op["replacement"], fontsize=size)
            if length > width:
                size *= width / length
            if op["kind"].startswith("source") and size < .86 * op["size"]:
                raise ValueError(f"Formula repair would be too small: {op['replacement']}")
            op["inserted_font_size"] = size
            page.insert_text(op["origin"], op["replacement"], fontname="DqbRepair", fontsize=size, color=op["color"])
        all_ops.append(operations)
    note, bottom = note_pdf(args.font_regular, args.font_bold, args.font_fallback)
    output.insert_pdf(fitz.open(stream=note, filetype="pdf"))
    output.set_metadata({"title": "Daily Quantum Brief 2026-10-26 - Public corrected edition",
     "author": "Research Brief", "subject": "Flat Chern bands and structure-aware quantum algorithms",
     "creator": "AI Tech Review public archive builder", "producer": f"PyMuPDF {fitz.VersionBind}; ReportLab"})
    output.del_xml_metadata()
    output.subset_fonts()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.save(args.output, garbage=4, deflate=True, no_new_id=True)
    final = fitz.open(args.output)
    page_checks = []
    for i in range(4):
        assert links(original[i]) == links(final[i])
        diff = ImageChops.difference(image(original[i]), image(final[i]))
        for op in all_ops[i]:
            r = fitz.Rect(op["rect"]) + (-.7, -.7, .7, .7)
            ImageDraw.Draw(diff).rectangle((math.floor(r.x0*2), math.floor(r.y0*2), math.ceil(r.x1*2), math.ceil(r.y1*2)), fill=(0,0,0))
        assert diff.getbbox() is None, f"Unexpected pixel changes outside edits on page {i+1}"
        page_checks.append({"page": i+1, "pixel_identical_outside_declared_edit_rectangles_144_dpi": True,
                            "original_reference_links_preserved": True, "edits": all_ops[i]})
    args.qa_dir.mkdir(parents=True, exist_ok=True)
    executable = shutil.which("pdftoppm")
    if not executable:
        raise RuntimeError("Poppler pdftoppm is required")
    subprocess.run([executable, "-r", "144", "-png", str(args.output), str(args.qa_dir/"public")], check=True)
    report = {"date": "2026-10-26", "public_file": args.output.name, "pages": len(final),
     "sha256": digest(args.output.read_bytes()), "size_bytes": args.output.stat().st_size,
     "source_sha256": SOURCE_SHA256, "source_pages": 4, "appended_correction_pages": 1,
     "source_glyph_defects": "Visible source crossed boxes restored with source-checked ASCII formula notation",
     "formula_repair_groups": sum(sum(op["kind"].startswith("source") for op in ops) for ops in all_ops),
     "source_null_glyphs": sum(p.get_text().count("\x00") for p in original),
     "public_null_glyphs": sum(p.get_text().count("\x00") for p in final),
     "page_checks": page_checks, "public_pdf_inspection": inspect(final),
     "correction_page_content_bottom_pt": bottom,
     "visual_qa": {"status": "pending", "rendering": "Poppler at 144 dpi; final five pages require inspection"},
     "scientific_results_independently_reproduced": False,
     "source_comparison": "Root checked primary-paper HTML and approved restored symbols and reference correction",
     "mailbox_action": "none", "registry_or_site_modified_by_builder": False}
    args.qa_report.parent.mkdir(parents=True, exist_ok=True)
    args.qa_report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"pages": len(final), "sha256": report["sha256"], "size_bytes": report["size_bytes"]}))

if __name__ == "__main__":
    main()
