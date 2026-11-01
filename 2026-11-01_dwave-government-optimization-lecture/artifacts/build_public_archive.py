"""Prepare the two explicitly reviewed D-Wave v3 PDFs for public archiving.

Keep private source PDFs outside Git. This script removes collection records and
participant identifiers while preserving the scientific material, source links,
original page numbers and equations. It does not register or publish documents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

import fitz
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SPECS = {
    "Detailed_Notes": (13, "2026-11-01-dwave-government-optimization-notes-ko"),
    "Academic_Review": (8, "2026-11-01-dwave-government-optimization-academic-review-ko"),
}
SOURCE_HASHES = {
    "Detailed_Notes": "8dfbfc8984e0152d26447de88615a6ae3943c0f3e2232214566ba8a80acde339",
    "Academic_Review": "dff37d8353b58918e6c1bd9edc3e992bf2239796399a791bf9f66110601dc285",
}
TEAL = (35 / 255, 107 / 255, 114 / 255)
INK = (23 / 255, 51 / 255, 77 / 255)
DISCLOSURE = (
    "공개 보관본 · 2026-11-01\n"
    "책임 편집자 김현중 · AI 보조 OpenAI Codex\n"
    "원판의 정확한 실행 모델·원 작성 에이전트 식별자: 미보존.\n"
    "공개판 편집: root(정제·등록), archive_structure(게시 위치·공개 범위 검토).\n"
    "AI Tech Review Editorial Harness 2026.08 · 과학 설명 준칙 1.0.\n"
    "원판의 검증 범위를 유지하며, 사람의 문장별 심사를 수행한 것으로 표시하지 않는다.\n"
    "공개판에서는 내부 운영기록과 일반 질문자 식별정보를 제외했다."
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_links(doc):
    return [link["uri"] for page in doc for link in page.get_links() if "uri" in link]


def picture(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def prepare(kind, source, font, output_dir):
    expected_pages, document_id = SPECS[kind]
    assert sha(source) == SOURCE_HASHES[kind], "Input differs from the reviewed v3 source"
    original = fitz.open(source)
    doc = fitz.open(source)
    assert len(doc) == expected_pages
    operations = {i: [] for i in range(len(doc))}

    def replace(index, rect, text="", size=10.2, color=INK, align=0, origin=None):
        operations[index].append({"rect": list(rect), "text": text,
                                  "size": size, "color": color, "align": align, "origin": origin})

    for i in range(len(doc)):
        replace(i, (350, 24, 542, 39), "편집자 주석판 v3 · 공개 보관본", 7.5, TEAL, 2)
    replace(0, (54, 510, 542, 631), DISCLOSURE, 9, INK)

    if kind == "Detailed_Notes":
        replace(10, (53, 108, 543, 158),
                "plateau 질문의 추가 설명 요청과 QPU 선택 기능의 확인 유보는 답변이 남은 항목이다. "
                "아래 표는 녹화 내용의 해석과 성능 판단에 필요한 후속 자료를 정리한다.")
        replace(10, (53, 483, 543, 535),
                "자막 의미·출처·위치와 공식 정의를 대조한 범위의 검토 상태는 checked_with_open_items다. "
                "미해결 사항은 녹화 범위·자막 판독·성능 근거에 해당한다. "
                "이 PDF는 과학 내용·주석·근거 상대시각을 유지한 v3 공개 보관본이다.")
        # Recompose only the existing question lines that identify participants.
        for i in (7, 8):
            for block in original[i].get_text("blocks"):
                text = block[4].strip()
                cleaned = re.sub(r", [A-Za-z]+로 소개", "", text)
                cleaned = re.sub(r", [A-Za-z]+ 후속", ", 후속 질문", cleaned)
                if cleaned != text:
                    line = next(line for b in original[i].get_text("dict")["blocks"]
                                for line in b.get("lines", [])
                                if re.search(r", [A-Za-z]+(?:로 소개| 후속)", "".join(s["text"] for s in line["spans"]))
                                and abs(line["bbox"][1] - block[1]) < 1)
                    replace(i, (53, block[1] - 1, 544, block[3] + 1), cleaned, 10.2,
                            origin=line["spans"][0]["origin"])
    else:
        for hit in original[2].search_for("실시간 미참석 기록은 보존한다."):
            replace(2, tuple(hit + (-0.2, -0.3, 0.2, 0.3)))
        replace(3, (53, 60, 543, 126),
                "국방 관련 내용은 적용 분야와 검증 한계만 다루며 운영 방법·배치·추적 절차를 보충하지 않는다. "
                "R004(녹화 범위), R005(자막), R006(성능 근거), R007(제품·용어 정의)의 확인 범위를 구분한다. "
                "검토 상태는 checked_with_open_items다. 시연 성능 재현·원음/화면 대조·최적성 인증을 수행한 것으로 쓰지 않는다.")
        replace(5, (53, 108, 543, 195),
                "확인한 현행 D-Wave 문서(S013-S015·S017·S021) 바닥글은 Ocean SDK 9.5.0이다. "
                "행사 당시 구현 판본을 고정하는 자료로 소급하지 않는다. 예제 코드나 benchmark를 실행하지 않았고, "
                "원음·화면·시연의 최적성 인증도 재현하지 않았다. 자막 충돌·미해결 문답·기업 사례의 일차 보고 대조는 "
                "전문 리뷰에 묶었다. R004-R006은 녹화 범위·자막·성능 근거의 잔여 쟁점이며, R007은 제품 정의와 수학·시간 범위의 보충이다.")
        replace(6, (53, 184, 543, 750))
        sections = [
            (192, "R004 · 녹화 범위와 원음·화면 대조",
             "자막은 00:00에 이미 슬라이드 넘김 요청으로 시작한다. 원행사 전체가 포함됐는지 미확정이다. "
             "전체 영어 자막을 읽었지만 음성 직접 청취·전체 슬라이드 판독·시연 실행은 하지 않았다."),
            (288, "R005 · 자막의 수치·고유명·용어와 미답 문답",
             "9-12%/90%, Fort Otosan와 less than 5의 단위, 후기 4일→10분, Shinogi, plateau 및 "
             "Cubo and Cuba 등의 원음/원슬라이드가 미확정이다. 항만 증가값 지표와 QPU 선택 기능도 자막만으로 확정하지 않는다."),
            (400, "R006 · 성능·정확도·양자 기여",
             "공식 사례 보고 일부와 수치를 대조했지만 동일 입력·품질·고전 기준·시간 경계·전체 비용·반복 분포·최적성 인증은 "
             "확보하지 않았다. gate-model 대비 수치, AI surrogate 효과, 방어 데모 정확도, CQM/Stride 우열을 독립 검증하지 않았다."),
            (512, "R007 · 제품 정의·수학·시간 범위",
             "하이브리드/직접 QPU, 노드/변수/큐비트, MILP 선형성, 어닐링 비보장, QPU 시간/전체 시간, "
             "초기해/최적성 인증을 공식 정의와 대조했다. 현재 문서는 행사 당시 solver response가 아니다."),
        ]
        for y, title, body in sections:
            replace(6, (54, y, 542, y + 25), title, 11, TEAL)
            replace(6, (54, y + 29, 542, y + 95), body, 10.2)
        replace(6, (54, 644, 542, 713),
                "공개판 편집 안내\n원판의 과학적 검토 범위와 미해결 쟁점을 유지했다. "
                "원판의 내부 운영기록은 공개 학습자료에서 제외했다. R004-R007은 원판과의 대응을 위해 식별자를 유지한다.", 9)

    replace(len(doc) - 1, (53, 245, 543, 326),
            "판본 안내 · v3 공개 보관본\n"
            "공식 영상·문서에 관한 원판의 식별번호와 근거 상대시각을 유지했다. "
            "C는 주장, Q는 문답, S는 출처, R은 검토 항목을 가리킨다. "
            "작성·검증 범위는 표지와 학술 검토의 공개 안내를 따른다.", 9)

    for i, page in enumerate(doc):
        for op in operations[i]:
            page.add_redact_annot(fitz.Rect(op["rect"]), fill=(1, 1, 1))
        page.apply_redactions(images=0, graphics=0)
        page.insert_font(fontname="PublicNanum", fontfile=str(font))
        for op in operations[i]:
            if op["text"]:
                if op["origin"]:
                    page.insert_text(op["origin"], op["text"], fontname="PublicNanum",
                                     fontsize=op["size"], color=op["color"])
                    continue
                remaining = page.insert_textbox(
                    fitz.Rect(op["rect"]), op["text"], fontname="PublicNanum",
                    fontsize=op["size"], lineheight=1.5, color=op["color"], align=op["align"])
                if remaining < 0:
                    raise ValueError(f"Text overflow: {kind} page {i + 1}: {remaining}")
    doc.set_metadata({"title": "D-Wave Government Optimization - " + kind.replace("_", " ") + " - v3 Public Archive",
                      "author": "김현중", "subject": "Korean annotated webinar study material; public archive edition 2026-11-01",
                      "creator": "AI Tech Review; OpenAI Codex-assisted public edition"})
    doc.del_xml_metadata()
    doc.subset_fonts()
    output = output_dir / f"{document_id}.pdf"
    doc.save(output, garbage=4, deflate=True, clean=True)
    final = fitz.open(output)
    assert len(final) == len(original)
    assert public_links(final) == public_links(original), "Original public links changed"
    text = "\n".join(p.get_text() for p in final)
    objects = "\n".join(final.xref_object(i) for i in range(1, final.xref_length()))
    combined = text + json.dumps(final.metadata) + objects
    checks = {
        "no_personal_addresses": not bool(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", combined)),
        "no_local_paths": not bool(re.search(r"/(?:Users|home|private|tmp)/|file://|localhost", combined, re.I)),
        "no_collection_records": not any(s in text for s in ["S011", "S012", "R001", "R002", "R003", "R008", "A002", "checked_at"]),
        "no_participant_identifiers": not bool(re.search(r", [A-Za-z]+(?:로 소개| 후속)", text)),
        "no_embedded_files": final.embfile_count() == 0,
        "no_active_actions": not bool(re.search(r"/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm)\b", objects)),
        "no_xmp": not bool(final.get_xml_metadata()),
        "no_broken_text_glyphs": "\ufffd" not in text and "\x00" not in text,
    }
    assert all(checks.values()), checks
    unchanged_pages = []
    for i in range(len(final)):
        before, after = picture(original[i]), picture(final[i])
        diff = ImageChops.difference(before, after)
        draw = ImageDraw.Draw(diff)
        for op in operations[i]:
            x0, y0, x1, y1 = op["rect"]
            draw.rectangle((int(x0 * 2) - 3, int(y0 * 2) - 3,
                            int(x1 * 2) + 3, int(y1 * 2) + 3), fill="black")
        if diff.getbbox():
            raise ValueError(f"Unexpected pixels outside edited regions on {kind} page {i + 1}: {diff.getbbox()}")
        unchanged_pages.append(i + 1)
    return {"id": document_id, "source_sha256": sha(source), "public_sha256": sha(output),
            "pages": len(final), "checks": checks, "public_links": public_links(final),
            "pixels_unchanged_outside_edit_regions_pages": unchanged_pages,
            "edit_regions": {str(i + 1): [op["rect"] for op in ops] for i, ops in operations.items()},
            "visual_review": "pending"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--font", type=Path, required=True)
    args = parser.parse_args()
    output = ROOT / "output/pdf"
    qa = ROOT / "notes"
    output.mkdir(parents=True, exist_ok=True)
    qa.mkdir(exist_ok=True)
    results = []
    for kind in SPECS:
        source = args.source_dir / f"2026-10-30_D-Wave_Government_Optimization_{kind}_KO_v3.pdf"
        results.append(prepare(kind, source, args.font, output))
    (qa / "production-qa.json").write_text(json.dumps({"date": "2026-11-01", "documents": results}, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps([{k: r[k] for k in ("id", "pages", "public_sha256")} for r in results], indent=2))


if __name__ == "__main__":
    main()
