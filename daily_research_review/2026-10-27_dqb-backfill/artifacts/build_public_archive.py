"""Prepare three explicitly reviewed DQB archive editions, without publishing.

The input directory and QA images are private caller-supplied locations. Only
the selected collection-context blocks and the source-checked October 24 QAOA
reference/date change. All other scientific pages and direct-source URIs stay
unchanged. PyMuPDF and Pillow are required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

import fitz
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ISSUES = {
    "2026-10-23": {"sha256": "09c5f369426330561bc1cddaf5e023e48775824ffe20d5ab8879620c6406c03e", "pages": 5, "collection": [61, 615, 534, 659]},
    "2026-10-24": {"sha256": "98674a76e76ec3d779aa4119b1fc871d294956bae88eba213459de5fece9cd0b", "pages": 5, "collection": [61, 615, 534, 659]},
    "2026-10-25": {"sha256": "d6a99b7a468d20fc97dce31f56d38f2ebe3d9235d5ed5d3ebfdce292c70f9224", "pages": 4, "collection": [61, 530, 534, 584]},
}
REFERENCE_7 = "[7] G. A. Bridi, F. de L. Marquezino, and A. Ambainis, On the role of problem structure in single-layer QAOA, arXiv:2610.30511v1 (2026)."


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def uris(document):
    return [link["uri"] for page in document for link in page.get_links() if "uri" in link]


def image(page):
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def matching_date_operation(page):
    """Select only the incorrect date in the identified QAOA source line."""
    for block in page.get_text("rawdict")["blocks"]:
        for line in block.get("lines", []):
            chars = [dict(c, size=span["size"], color=span["color"]) for span in line["spans"] for c in span["chars"]]
            text = "".join(c["c"] for c in chars)
            if "2610.30511" not in text:
                continue
            start = text.index("2026-10-22")
            chosen = chars[start:start+10]
            rect = fitz.Rect(chosen[0]["bbox"])
            for char in chosen[1:]:
                rect |= fitz.Rect(char["bbox"])
            return {"rect": list(rect), "origin": list(chosen[0]["origin"]), "size": chosen[0]["size"],
                    "replacement": "2026-10-21", "kind": "source-checked QAOA submission-date correction"}
    raise ValueError("Expected October 24 QAOA source/date line not found")


def inspect(document, original_uris):
    text = "\n".join(page.get_text() for page in document)
    metadata = json.dumps(document.metadata)
    objects = "\n".join(document.xref_object(i, compressed=False) for i in range(1, document.xref_length()))
    combined = text + metadata + objects
    checks = {
        "no_private_collection_context": not any(x in text for x in ("수집 범위", "Gmail", "LinkedIn", "새 메일", "지난 회차 이후")),
        "no_email": not bool(re.search(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", combined)),
        "no_private_paths": not bool(re.search(r"/(?:Users|home|private|tmp)/|file://|localhost", combined, re.I)),
        "no_secret_query_strings": not bool(re.search(r"[?&](?:token|sig|signature|access_token|auth)=", combined, re.I)),
        "no_null_or_replacement_glyphs": "\x00" not in text and "\ufffd" not in text,
        "no_embedded_files": document.embfile_count() == 0,
        "no_active_actions": not bool(re.search(r"/(?:JavaScript|JS|Launch|OpenAction|AA|EmbeddedFile|SubmitForm)\b", objects)),
        "no_xmp_metadata": not bool(document.get_xml_metadata()),
        "original_source_uris_preserved": uris(document) == original_uris,
    }
    if not all(checks.values()):
        raise ValueError(f"Public inspection failed: {checks}")
    return checks


def build(date, spec, source_dir, font, qa_dir, output_dir):
    raw = (source_dir/date/"original.pdf").read_bytes()
    assert sha256(raw) == spec["sha256"], "Input differs from explicitly reviewed source"
    original = fitz.open(stream=raw, filetype="pdf")
    document = fitz.open(stream=raw, filetype="pdf")
    assert len(document) == spec["pages"]
    source_uris = uris(original)
    edits = [[] for _ in document]
    rect = fitz.Rect(spec["collection"])
    page = document[0]
    page.add_redact_annot(rect, fill=(1, 1, 1))
    page.apply_redactions(images=0, graphics=0, text=0)
    page.insert_font(fontname="PublicNote", fontfile=str(font))
    y = rect.y0 + 12
    notes = ["공개 보관본 · 2026-10-27", "자료 수집 경위 문단을 삭제했으며 과학 본문·원문 링크는 유지했다."]
    if date == "2026-10-24":
        notes.append("참고문헌 [7]의 원제·저자와 제출일을 원문에 맞춰 바로잡았다.")
    for note in notes:
        page.insert_text((62.69, y), note, fontsize=8, fontname="PublicNote", color=(0.376, 0.443, 0.490))
        y += 12
    edits[0].append({"rect": list(rect), "kind": "remove private collection context and add public-edition note"})
    if date == "2026-10-24":
        op = matching_date_operation(original[2])
        document[2].add_redact_annot(fitz.Rect(op["rect"]) + (0.03, 0.03, -0.03, -0.03), fill=None)
        document[2].apply_redactions(images=0, graphics=0, text=0)
        document[2].insert_text(op["origin"], op["replacement"], fontsize=op["size"], fontname="helv", color=(.376, .443, .490))
        edits[2].append(op)
        page = document[4]
        ref_rect = fitz.Rect(61, 686, 534, 698)
        page.add_redact_annot(ref_rect, fill=(1, 1, 1))
        page.apply_redactions(images=0, graphics=0, text=0)
        page.insert_text((62.69, 693.689), REFERENCE_7, fontsize=6.7, fontname="helv", color=(.376, .443, .490))
        x = 62.69 + fitz.Font("helv").text_length(REFERENCE_7, fontsize=6.7) + 3
        page.insert_font(fontname="PublicNote", fontfile=str(font))
        page.insert_text((x, 693.689), "원문", fontsize=6.7, fontname="PublicNote", color=(0, .5, .55))
        page.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(x, 687, x+15, 696), "uri": source_uris[-1]})
        edits[4].append({"rect": list(ref_rect), "kind": "source-checked original title and full author credit for reference 7"})
    metadata = dict(document.metadata)
    metadata.update({"title": f"Daily Quantum Brief {date} - Public archive edition", "author": "Research Brief",
                     "subject": "Public archive edition; source-specific editorial changes recorded in document", "creator": "AI Tech Review public archive builder",
                     "producer": "PyMuPDF", "creationDate": "", "modDate": ""})
    document.set_metadata(metadata)
    document.del_xml_metadata()
    document.subset_fonts()
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir/f"{date}-daily-quantum-brief.pdf"
    document.save(output, garbage=4, deflate=True, no_new_id=True)
    final = fitz.open(output)
    checks = inspect(final, source_uris)
    qa = qa_dir/date
    qa.mkdir(parents=True, exist_ok=True)
    pages = []
    for i, page in enumerate(final):
        diff = ImageChops.difference(image(original[i]), image(page))
        for op in edits[i]:
            r = fitz.Rect(op["rect"]) + (-.7, -.7, .7, .7)
            ImageDraw.Draw(diff).rectangle((math.floor(r.x0*2), math.floor(r.y0*2), math.ceil(r.x1*2), math.ceil(r.y1*2)), fill=(0,0,0))
        assert diff.getbbox() is None, f"Unexpected pixel change outside declared edits: {date}, page {i+1}"
        image(page).save(qa/f"public-{i+1}.png")
        pages.append({"page": i+1, "pixel_identical_outside_declared_edits_144_dpi": True, "edits": edits[i]})
    return {"date": date, "file": output.name, "sha256": sha256(output.read_bytes()), "source_sha256": spec["sha256"],
            "pages": len(final), "source_pages": len(original), "checks": checks, "source_uris": source_uris,
            "page_checks": pages, "visual_inspection": "pending", "independent_scientific_reproduction": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--font-regular", type=Path, required=True)
    parser.add_argument("--qa-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT/"dist")
    args = parser.parse_args()
    report = {"version": 1, "prepared_at": "2026-10-27", "issues": [build(date, spec, args.source_dir, args.font_regular, args.qa_dir, args.output_dir) for date, spec in ISSUES.items()]}
    (ROOT/"notes").mkdir(parents=True, exist_ok=True)
    (ROOT/"notes/production-qa.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    print("Prepared three archive editions; visual inspection remains pending.")


if __name__ == "__main__":
    main()
