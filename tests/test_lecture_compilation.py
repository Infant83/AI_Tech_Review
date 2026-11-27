"""Contracts for a compiled PDF that owns a series of separate lesson PDFs."""
from __future__ import annotations

from copy import deepcopy
import hashlib
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest

from scripts import document_archive_site as archive_site


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.links.append(dict(attrs))


class LectureCompilationTests(unittest.TestCase):
    def fixture(self) -> tuple[dict, list[dict], dict]:
        owner_id = "2026-11-27-example-course-notes-ko"
        owner = {
            "id": owner_id, "date": "2026-11-27", "series": "lecture-notes", "language": "ko",
            "title": "통합 강의 <기초>", "title_en": "Compiled course <foundations>",
            "summary": "통합 문서 소개", "summary_en": "Compiled document summary",
            "href": f"archive/files/{owner_id}.pdf", "sha256": "c" * 64,
            "study_href": "lectures/example-course/",
        }
        documents = [owner]
        units = []
        for number in range(1, 8):
            identifier = f"2026-11-27-example-course-l{number:03d}-notes-ko"
            document = {
                **owner, "id": identifier, "title": f"기초 {number}", "title_en": f"Foundation {number}",
                "href": f"archive/files/{identifier}.pdf", "sha256": str(number) * 64,
            }
            document.pop("study_href")
            documents.append(document)
            units.append({
                "id": f"L{number:03d}", "archive_id": identifier,
                "title": document["title"], "title_en": document["title_en"],
                "summary": f"단원 요약 {number}", "summary_en": f"Lesson summary {number}",
                "pdf": f"{identifier}.pdf", "sha256": document["sha256"], "public_pages": number,
            })
        registry = {
            "format": "ai-tech-review-course-registry", "version": 1,
            "series_id": "example-course", "title": "일곱 단계 강의", "title_en": "Seven-level course",
            "summary": "전체 과정의 학습 내용", "summary_en": "What the whole course teaches",
            "latest_unit": "L007", "units": units,
            "compilation_archive_id": owner_id, "compilation_public_pages": 42,
        }
        return registry, documents, owner

    def test_separate_compilation_is_bound_to_its_registered_lecture(self) -> None:
        registry, documents, owner = self.fixture()
        metadata = archive_site.lecture_series_metadata(registry, documents, owner["id"])
        self.assertEqual(metadata["compilation"], {
            "document_id": owner["id"], "title": owner["title"], "title_en": owner["title_en"],
            "pages": 42, "sha256": owner["sha256"], "href": owner["href"],
        })
        self.assertEqual([unit["number"] for unit in metadata["units"]], [f"L{n:03d}" for n in range(1, 8)])
        self.assertEqual(sum(unit["pages"] for unit in metadata["units"]), 28)
        self.assertEqual(metadata["latest_unit"], "L007")

    def test_separate_primary_requires_an_explicit_binding(self) -> None:
        registry, documents, owner = self.fixture()
        registry.pop("compilation_archive_id")
        registry.pop("compilation_public_pages")
        with self.assertRaisesRegex(ValueError, "registered primary PDF"):
            archive_site.lecture_series_metadata(registry, documents, owner["id"])

    def test_binding_rejects_another_owner_unknown_pdf_or_nonlecture(self) -> None:
        registry, documents, owner = self.fixture()
        for invalid_id in (None, "missing-pdf", documents[1]["id"]):
            with self.subTest(compilation_archive_id=invalid_id):
                invalid = {**registry, "compilation_archive_id": invalid_id}
                with self.assertRaisesRegex(ValueError, "compilation binding"):
                    archive_site.lecture_series_metadata(invalid, documents, owner["id"])
        for invalid_documents in (documents[1:], [{**owner, "series": "article"}, *documents[1:]]):
            with self.subTest(primary_present=owner["id"] in [d["id"] for d in invalid_documents]):
                with self.assertRaisesRegex(ValueError, "compilation binding"):
                    archive_site.lecture_series_metadata(registry, invalid_documents, owner["id"])
        # A compilation is separate from the lesson count, even when the ID exists.
        invalid = {**registry, "compilation_archive_id": documents[1]["id"]}
        with self.assertRaisesRegex(ValueError, "compilation binding"):
            archive_site.lecture_series_metadata(invalid, documents, documents[1]["id"])

    def test_compilation_page_count_requires_a_positive_integer_and_binding(self) -> None:
        registry, documents, owner = self.fixture()
        for invalid_pages in (None, 0, -1, True, "42"):
            with self.subTest(compilation_public_pages=invalid_pages):
                invalid = {**registry, "compilation_public_pages": invalid_pages}
                with self.assertRaisesRegex(ValueError, "compilation binding"):
                    archive_site.lecture_series_metadata(invalid, documents, owner["id"])
        registry.pop("compilation_archive_id")
        with self.assertRaisesRegex(ValueError, "compilation binding"):
            archive_site.lecture_series_metadata(registry, documents, owner["id"])

    def test_grouped_catalog_keeps_seven_lessons_and_three_compilation_actions(self) -> None:
        registry, documents, owner = self.fixture()
        owner["study_series"] = archive_site.lecture_series_metadata(registry, documents, owner["id"])
        self.assertEqual(archive_site.grouped_lectures(documents), [owner])
        for language in ("ko", "en"):
            with self.subTest(language=language):
                en = language == "en"
                prefix = "../../" if en else "../"
                page = archive_site.render_lectures(documents, "https://example.com/", language)
                self.assertEqual(page.count('class="lecture-card'), 1)
                self.assertEqual(page.count("data-lecture-unit="), 7)
                self.assertIn("1 resources · 8 PDFs" if en else "1개 자료 · PDF 8편", page)
                self.assertIn("7 units · PDF 28 pages" if en else "7회차 · PDF 28쪽", page)
                self.assertIn("PDF 42 pages" if en else "PDF 42쪽", page)
                summary = registry["summary_en" if en else "summary"]
                self.assertLess(page.index(summary), page.index("</summary>"))
                self.assertLess(page.index("</summary>"), page.index("data-lecture-compilation="))
                self.assertLess(page.index("data-lecture-compilation="), page.index('class="lecture-units"'))
                self.assertNotIn('data-lecture-unit="L008"', page)
                parser = Links()
                parser.feed(page)
                reader = archive_site.lecture_reader_href(owner["id"], prefix=prefix, language=language)
                annotation = [link for link in parser.links if link.get("href") == reader]
                pdfs = [link for link in parser.links if link.get("href") == prefix + owner["href"]]
                self.assertEqual(len(annotation), 1)
                self.assertEqual(annotation[0]["class"], "lecture-primary")
                self.assertEqual(len(pdfs), 2)
                self.assertEqual(sum("download" in link for link in pdfs), 1)
                self.assertEqual(sum(link.get("target") == "_blank" for link in pdfs), 1)
                for link in annotation + pdfs:
                    self.assertIn("Combined edition" if en else "통합본", link["aria-label"])
                self.assertIn("&lt;foundations&gt;" if en else "&lt;기초&gt;", page)

    def test_existing_series_retains_its_metadata_and_has_no_compilation_actions(self) -> None:
        registry, documents, _owner = self.fixture()
        registry.pop("compilation_archive_id")
        registry.pop("compilation_public_pages")
        owner = documents[1]
        owner["study_href"] = "lectures/example-course/"
        metadata = archive_site.lecture_series_metadata(registry, documents, owner["id"])
        self.assertEqual(set(metadata), {
            "series_id", "title", "title_en", "summary", "summary_en", "units", "latest_unit", "latest_date",
        })
        owner["study_series"] = metadata
        for language in ("ko", "en"):
            page = archive_site.render_lecture_series(owner, "../", language)
            self.assertNotIn("compilation", page)
            self.assertEqual(page.count("data-lecture-unit="), 7)
            self.assertIn("7 units · PDF 28 pages" if language == "en" else "7회차 · PDF 28쪽", page)

    def test_latest_pdf_still_selects_last_lesson_instead_of_compilation(self) -> None:
        registry, _documents, _owner = self.fixture()
        registry = deepcopy(registry)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for unit in registry["units"]:
                payload = unit["id"].encode("ascii")
                (root / unit["pdf"]).write_bytes(payload)
                unit["sha256"] = hashlib.sha256(payload).hexdigest()
            (root / "combined.pdf").write_bytes(b"combined edition")
            self.assertEqual(archive_site.series_latest_pdf(root, registry), root / registry["units"][-1]["pdf"])


if __name__ == "__main__":
    unittest.main()
