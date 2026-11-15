"""The insights catalog reuses publication identity and reviewed metadata."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import reader_engagement_publish as reader
from scripts import reader_insights_site as insights


class InsightsSiteTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.review = {"folder": "review-one", "title": "한국어 <제목>", "date": "2026-11-01", "href": "reviews/review-one/index.html", "category": "Quantum Computing", "translations": [{"language": "en", "href": "reviews/review-one/en/index.html"}]}
        self.lecture = {"id": "lecture-one", "date": "2026-11-02", "series": "lecture-notes", "title": "렉처", "title_en": "Lecture", "href": "archive/files/lecture-one.pdf", "tags": ["Quantum Computing"]}
        (self.root / "manifest.json").write_text(json.dumps([self.review]), encoding="utf-8")
        (self.root / "archive-manifest.json").write_text(json.dumps({"documents": [self.lecture]}), encoding="utf-8")
        for relative, content in [(self.review["href"], "<html><head><meta name='description' content='소개'></head><body><h1>한국어 &lt;제목&gt;</h1></body></html>"), (self.review["translations"][0]["href"], "<html lang='en'><head><meta name='description' content='Published summary'></head><body><h1>English title</h1></body></html>")]:
            path = self.root / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding="utf-8")
        self.articles, _ = reader.load_publications(self.root)

    def tearDown(self):
        self.temporary.cleanup()

    def test_locales_share_ids_and_use_published_titles_and_only_existing_category(self):
        result = insights.catalogs(self.root, self.articles)
        self.assertEqual([row["id"] for row in result["ko"]], [row["id"] for row in result["en"]])
        en_review = next(row for row in result["en"] if row["topic"] == "review")
        self.assertEqual(en_review["title"], "English title")
        self.assertEqual(en_review["path"], "/AI_Tech_Review/reviews/review-one/en/")
        ko_review = next(row for row in result["ko"] if row["topic"] == "review")
        self.assertEqual(ko_review["categoryLabel"], "양자 컴퓨팅")
        for language in result:
            lecture = next(row for row in result[language] if row["topic"] == "lecture")
            self.assertIsNone(lecture["category"])
            self.assertEqual(lecture["path"], "/AI_Tech_Review/archive/files/lecture-one.pdf")

    def test_generation_is_deterministic_escaped_and_not_instrumented(self):
        payloads = {"assets/reader-insights.js": b"test js", "assets/reader-insights.css": b"test css"}
        self.assertEqual(insights.generate(self.root, self.articles, asset_payloads=payloads), 2)
        self.assertEqual(insights.generate(self.root, self.articles, asset_payloads=payloads), 0)
        for name in insights.PAGES:
            html = (self.root / name).read_text(encoding="utf-8")
            self.assertIn("reader-insights-config", html)
            self.assertNotIn("<제목>", html)
            self.assertNotIn("reader-engagement.js", html)
            self.assertEqual(reader.enrich_html(html, name, None), html)
            self.assertIn("<table>", html)
            self.assertIn("methods/#reader-metrics", html)
            self.assertIn("insights-theme", html)
        self.assertIn("en/insights/", (self.root / "insights/index.html").read_text(encoding="utf-8"))

    def test_generated_symlink_is_rejected(self):
        (self.root / "insights").mkdir()
        (self.root / "insights/index.html").symlink_to(self.root / self.review["href"])
        with self.assertRaises(ValueError):
            insights.generate(self.root, self.articles, asset_payloads={"assets/reader-insights.js": b"js", "assets/reader-insights.css": b"css"})


if __name__ == "__main__":
    unittest.main()
