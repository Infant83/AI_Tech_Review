from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import lecture_chapters as chapters
from scripts import reader_engagement_publish as reader


SOURCE = '''<!doctype html><html lang="ko"><head><title>Course</title><link rel="stylesheet" href="notes.css"></head><body><aside class="sidebar"><details id="navigation"><a href="#doc-first">First</a><a href="#term-test">Term</a></details></aside><main><section id="front-cover" class="cover"><h1>Course</h1></section><section class="document" id="doc-first" data-source="first.md"><h1>First chapter</h1><p>원래 설명 &amp; 조건은 그대로다.</p><span class="math-inline"><svg><defs><path id="math-path" d="M1 2L3 4"/></defs><use xlink:href="#math-path"/></svg></span><a href="#doc-second">Next</a><a href="https://example.com/paper#section">Paper</a><img src="diagram.svg"></section><section class="document" id="doc-second" data-source="second.md"><h1>Second chapter</h1><div id="term-test">용어 정의</div><a href="#doc-first">First</a><a href="notes.pdf">PDF</a></section></main><script>const termQuery=document.getElementById('term-query');</script></body></html>'''


class LectureChapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def build(self, source=SOURCE):
        return chapters.build_chapters(self.root, source, source, "https://example.com/AI_Tech_Review/lectures/quantum-machine-learning/")

    def test_split_keeps_every_original_section_and_exact_scientific_markup(self):
        manifest = self.build()
        self.assertEqual(chapters.validate_chapters(self.root, SOURCE), [])
        original = chapters.source_plan(SOURCE)
        self.assertEqual(len(manifest["pages"]), 2)
        for record in original["records"]:
            page = (self.root / record["href"]).read_text()
            self.assertIn(chapters.retarget_fragments(record["html"], original["anchors"]), page)
        first = (self.root / "first.html").read_text()
        self.assertIn('<use xlink:href="#math-path"/>', first)
        self.assertIn('<path id="math-path" d="M1 2L3 4"/>', first)
        self.assertIn('href="second.html#doc-second"', first)
        self.assertIn('href="https://example.com/paper#section"', first)
        self.assertIn('src="diagram.svg"', first)

    def test_course_entry_does_not_duplicate_scientific_body_and_all_old_fragments_have_links(self):
        manifest = self.build()
        entry = (self.root / "index.html").read_text()
        self.assertNotIn('d="M1 2L3 4"', entry)
        self.assertNotIn('용어 정의', entry)
        entry_ids = set(chapters.Identifiers(entry).ids)
        self.assertTrue(set(manifest["anchors"]).issubset(entry_ids))
        self.assertIn('id="term-test"', entry)
        self.assertIn('href="second.html#term-test"', entry)
        self.assertIn('data-qml-course-index', entry)
        self.assertIn('course-navigation.js', entry)

    def test_formula_or_text_tampering_cannot_be_hidden_by_a_forged_manifest(self):
        manifest = self.build()
        page = self.root / "first.html"
        page.write_text(page.read_text().replace('M1 2L3 4', 'M1 2L9 9'))
        manifest["pages"][0]["rendered_section_sha256"] = hashlib.sha256(page.read_bytes()).hexdigest()
        (self.root / chapters.MANIFEST).write_text(json.dumps(manifest))
        self.assertTrue(any("scientific section changed" in error for error in chapters.validate_chapters(self.root, SOURCE)))

    def test_changed_source_or_missing_chapter_fails_preservation_check(self):
        self.build()
        changed = SOURCE.replace('원래 설명', '달라진 설명')
        self.assertTrue(chapters.validate_chapters(self.root, changed))
        (self.root / "second.html").unlink()
        self.assertTrue(chapters.validate_chapters(self.root, SOURCE))

    def test_duplicate_anchor_invalid_page_and_unresolved_link_are_rejected(self):
        for source in [SOURCE.replace('id="doc-second"', 'id="doc-first"'),
                       SOURCE.replace('id="doc-second"', 'id="../second"')]:
            with self.subTest(source=source[:80]), self.assertRaises(ValueError):
                chapters.source_plan(source)
        with self.assertRaises(ValueError):
            self.build(SOURCE.replace('href="#doc-second"', 'href="#nonexistent"'))

    def test_navigation_assets_are_pinned_and_linked_outputs_are_rejected(self):
        self.build()
        (self.root / chapters.NAVIGATION_JS).write_text('unreviewed navigation')
        self.assertTrue(chapters.validate_chapters(self.root, SOURCE))
        self.build()
        (self.root / "first.html").unlink()
        (self.root / "first.html").symlink_to(self.root / "second.html")
        self.assertTrue(chapters.validate_chapters(self.root, SOURCE))

    def test_new_chapter_views_keep_one_publication_identity(self):
        (self.root / "manifest.json").write_text('[]')
        archive = {"documents": [{"id": "2026-10-20-quantum-machine-learning-lecture-notes-ko",
                    "date": "2026-10-20", "series": "lecture-notes", "title": "Course",
                    "href": "archive/files/course.pdf", "study_href": chapters.COURSE_HREF,
                    "study_assets": {"index.html": "", "first.html": "", "second.html": "", "notes.pdf": "", "chapter-manifest.json": ""}}]}
        (self.root / "archive-manifest.json").write_text(json.dumps(archive))
        articles, pages = reader.load_publications(self.root)
        self.assertEqual(len(articles), 1)
        expected = "lecture:2026-10-20-quantum-machine-learning-lecture-notes-ko"
        for name in ["index.html", "first.html", "second.html"]:
            self.assertEqual(pages[chapters.COURSE_HREF + name]["id"], expected)
            self.assertEqual(pages[chapters.COURSE_HREF + name]["path"], "/AI_Tech_Review/" + chapters.COURSE_HREF)
        archive["documents"][0]["study_assets"].pop("chapter-manifest.json")
        (self.root / "archive-manifest.json").write_text(json.dumps(archive))
        _articles, legacy_pages = reader.load_publications(self.root)
        self.assertNotIn(chapters.COURSE_HREF + "second.html", legacy_pages)

    def test_real_source_is_split_into_every_document_once_without_rewriting(self):
        source_path = Path(__file__).resolve().parents[1] / chapters.SOURCE_RELATIVE
        source = source_path.read_text()
        manifest = self.build(source)
        self.assertEqual(chapters.validate_chapters(self.root, source), [])
        original = chapters.source_plan(source)
        self.assertEqual({r["id"] for r in manifest["pages"]}, {r["id"] for r in original["records"]})
        self.assertEqual(sum(r["id"].startswith("doc-lectures-") for r in manifest["pages"]), 18)
        entry = (self.root / "index.html").read_text()
        self.assertLess(len(entry.encode()), 100_000)
        self.assertLess(chapters.Identifiers(entry).elements, 1200)
        self.assertLess(max(r["source_elements"] for r in manifest["pages"]), 6000)


if __name__ == "__main__":
    unittest.main()
