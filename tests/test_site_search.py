from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.site_search import build_records, build_search, validate_search, search_form, search_results


class SiteSearchTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.reviews = [{"folder": "review", "title": "TabPFN OLED", "summary": "제조 데이터를 학습합니다.", "subtitle": "표 데이터", "category": "AI", "tags": ["OLED"], "date": "2026-11-01", "href": "reviews/review/index.html", "metric_path": "/reviews/review/", "translations": [{"language": "en", "href": "reviews/review/en/index.html"}]}]
        self.documents = [{"id": "lecture", "series": "lecture-notes", "date": "2026-10-20", "title": "양자 머신러닝", "title_en": "Quantum machine learning", "summary": "강의 요약", "tags": ["QML"], "href": "archive/lecture.pdf", "study_href": "lectures/qml/"}]
        for relative, text in {"reviews/review/index.html": "<h1>TabPFN OLED</h1>", "reviews/review/en/index.html": '<meta name="description" content="Learning materials."><h1>English TabPFN title</h1>', "lectures/qml/index.html": '<nav><h2>Ignore navigation</h2></nav><h2 id="gradient">Barren plateau</h2><script><h2>Private script text</h2></script>', "archive/lecture.pdf": "%PDF-1.4"}.items():
            p = self.root / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        self.write_catalogs()

    def write_catalogs(self):
        (self.root / "manifest.json").write_text(json.dumps(self.reviews))
        (self.root / "archive-manifest.json").write_text(json.dumps({"documents": self.documents, "external_resources": []}))

    def test_bilingual_variants_are_one_record_and_only_public_study_headings_are_indexed(self):
        records = build_records(self.root)
        self.assertEqual(len(records), 2)
        review = next(item for item in records if item["id"] == "review")
        self.assertEqual(review["title_en"], "English TabPFN title")
        self.assertEqual(review["url_en"], "reviews/review/en/index.html")
        lecture = next(item for item in records if item["id"] == "lecture")
        self.assertEqual(lecture["headings"], "Barren plateau")

    def test_generated_assets_and_catalog_are_checked_against_current_sources(self):
        build_search(self.root)
        self.assertEqual(validate_search(self.root), [])
        self.documents[0]["summary"] = "Changed public summary"
        self.write_catalogs()
        self.assertIn("search records do not match public catalogs", validate_search(self.root))
        build_search(self.root)
        (self.root / "assets/site-search.js").write_text("tampered")
        self.assertTrue(any("site-search.js" in item for item in validate_search(self.root)))

    def test_private_unregistered_html_is_not_discovered(self):
        (self.root / "private.html").write_text("PRIVATE_INTAKE")
        build_search(self.root)
        self.assertNotIn("PRIVATE_INTAKE", (self.root / "assets/search-records.json").read_text())

    def test_missing_link_and_duplicate_identity_fail(self):
        self.reviews.append(dict(self.reviews[0]))
        self.write_catalogs()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            build_records(self.root)
        self.reviews.pop()
        self.reviews[0]["href"] = "../private.html"
        self.write_catalogs()
        with self.assertRaisesRegex(ValueError, "relative public"):
            build_records(self.root)

    def test_symlinked_search_heading_source_is_rejected(self):
        p = self.root / "lectures/qml/index.html"
        p.unlink()
        p.symlink_to(self.root / "reviews/review/index.html")
        with self.assertRaisesRegex(ValueError, "inside public"):
            build_records(self.root)

    def test_build_rejects_symlinked_asset_output_before_writing(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / "assets").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlinked search assets"):
            build_search(self.root)
        self.assertEqual(list(outside.iterdir()), [])

    def test_compact_control_has_named_scope_submit_and_no_section_button_row(self):
        markup = search_form("../", "ko", "lectures")
        self.assertIn('select name="scope"', markup)
        self.assertIn('value="lectures" selected', markup)
        self.assertIn('button type="submit"', markup)
        self.assertEqual(markup.count('<button'), 1)
        self.assertIn('data-site-search-results hidden', search_results())


if __name__ == "__main__":
    unittest.main()
