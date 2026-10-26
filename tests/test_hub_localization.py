from __future__ import annotations

from copy import deepcopy
import html
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.hub_localization import extract_english_text, localize_manifest


class HubLocalizationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "site"
        self.article = self.root / "reviews" / "sample-review" / "en" / "index.html"
        self.article.parent.mkdir(parents=True)
        self.item = {
            "folder": "sample-review", "title": "한국어 제목", "subtitle": "짧은 부제",
            "summary": "한국어 리뷰 요약", "href": "reviews/sample-review/index.html",
            "metric_path": "/AI_Tech_Review/reviews/sample-review/", "category": "Quantum",
            "tags": ["Circuit"], "date": "2026-10-20", "updated": "2026-10-25",
            "thumbnail": "reviews/sample-review/hero.webp",
            "translations": [{"language": "en", "href": "reviews/sample-review/en/index.html", "assets": ["hero.webp"]}],
        }

    def write_article(self, content=None):
        self.article.write_text(content or '''<html lang="en"><head><meta name="description" content="The published English summary."></head><body><h1>A <em>published</em> English title</h1><p class="dek">A distinct short subtitle.</p><h2>Body</h2><p class="subtitle">Not an introductory subtitle.</p></body></html>''', encoding="utf-8")

    def test_localization_uses_published_text_without_changing_identity_or_input(self):
        self.write_article()
        before = deepcopy(self.item)
        translated = localize_manifest([self.item], self.root, "en")[0]
        self.assertEqual(translated["title"], "A published English title")
        self.assertEqual(translated["subtitle"], "A distinct short subtitle.")
        self.assertEqual(translated["summary"], "The published English summary.")
        self.assertEqual(translated["href"], "reviews/sample-review/en/index.html")
        for field in ("folder", "metric_path", "category", "date", "updated", "thumbnail"):
            self.assertEqual(translated[field], self.item[field])
        self.assertEqual(translated["content_language"], "en")
        self.assertTrue(translated["english_available"])
        self.assertIn("한국어 리뷰 요약", translated["search_text"])
        self.assertIn("published English title", translated["search_text"])
        translated["translations"][0]["assets"].append("other.webp")
        translated["tags"].append("Other")
        self.assertEqual(self.item, before)

    def test_korean_page_retains_korean_copy_and_searches_published_english(self):
        self.write_article()
        item = localize_manifest([self.item], self.root, "ko")[0]
        self.assertEqual(item["title"], "한국어 제목")
        self.assertEqual(item["href"], self.item["href"])
        self.assertEqual(item["content_language"], "ko")
        self.assertIn("The published English summary", item["search_text"])

    def test_equal_intro_and_metadata_are_not_repeated_as_subtitle(self):
        value = extract_english_text('''<meta name="description" content="A summary &amp; a result."><h1>Title</h1><p class="dek"> A summary &amp; a result. </p>''')
        self.assertEqual(value["summary"], "A summary & a result.")
        self.assertEqual(value["subtitle"], "")

    def test_published_distinct_intro_is_used_instead_of_duplicate_dek(self):
        value = extract_english_text('''<meta name="description" content="Full summary."><h1>Title</h1><p class="dek">Full summary.</p><p class="subtitle">Distinct published subtitle.</p><h2>Body</h2><p class="standfirst">Not introductory.</p>''')
        self.assertEqual(value["subtitle"], "Distinct published subtitle.")

    def test_visible_published_intro_can_supply_missing_meta_summary(self):
        value = extract_english_text('<h1>Title</h1><p class="standfirst">Published overview.</p>')
        self.assertEqual(value, {"title": "Title", "subtitle": "", "summary": "Published overview."})

    def test_reviewed_summary_uses_current_korean_source_and_preserves_published_title_and_link(self):
        self.write_article()
        mapping = {"sample-review": {"source": self.item["summary"], "text": "Why the actual result matters to a reader."}}
        with patch("scripts.hub_localization.HUB_SUMMARIES_EN", mapping):
            english = localize_manifest([self.item], self.root, "en")[0]
            korean = localize_manifest([self.item], self.root, "ko")[0]
        self.assertEqual(english["summary"], mapping["sample-review"]["text"])
        self.assertEqual(english["title"], "A published English title")
        self.assertEqual(english["href"], self.item["translations"][0]["href"])
        self.assertEqual(korean["summary"], self.item["summary"])
        self.assertIn(mapping["sample-review"]["text"], korean["search_text"])
        self.assertEqual(english["metric_path"], self.item["metric_path"])

    def test_changed_korean_summary_does_not_reuse_a_stale_english_introduction(self):
        self.write_article()
        mapping = {"sample-review": {"source": self.item["summary"], "text": "Earlier reviewed introduction."}}
        changed = deepcopy(self.item)
        changed["summary"] += " Updated scientific scope."
        with patch("scripts.hub_localization.HUB_SUMMARIES_EN", mapping):
            value = localize_manifest([changed], self.root, "en")[0]
        self.assertEqual(value["summary"], "The published English summary.")
        self.assertNotIn("Earlier reviewed introduction.", value["search_text"])

    def test_reviewed_copy_does_not_imply_that_an_english_article_exists(self):
        mapping = {"sample-review": {"source": self.item["summary"], "text": "Reviewed English copy."}}
        with patch("scripts.hub_localization.HUB_SUMMARIES_EN", mapping):
            value = localize_manifest([self.item], self.root, "en")[0]
        self.assertFalse(value["english_available"])
        self.assertEqual(value["summary"], self.item["summary"])
        self.assertEqual(value["href"], self.item["href"])

    def test_source_matched_hub_subtitle_fills_a_duplicate_published_intro(self):
        self.write_article('<meta name="description" content="Published summary."><h1>English title</h1><p class="dek">Published summary.</p>')
        mapping = {"sample-review": {"source": self.item["subtitle"], "text": "A faithful translated subtitle."}}
        with patch("scripts.hub_localization.HUB_SUBTITLES_EN", mapping):
            value = localize_manifest([self.item], self.root, "en")[0]
        self.assertEqual(value["subtitle"], "A faithful translated subtitle.")
        self.assertEqual(value["summary"], "Published summary.")
        self.assertIn("A faithful translated subtitle.", value["search_text"])

    def test_stale_hub_subtitle_is_ignored_after_korean_source_changes(self):
        self.write_article('<meta name="description" content="Published summary."><h1>English title</h1><p class="dek">Published summary.</p>')
        mapping = {"sample-review": {"source": self.item["subtitle"], "text": "A faithful translated subtitle."}}
        changed = deepcopy(self.item)
        changed["subtitle"] += " 수정"
        with patch("scripts.hub_localization.HUB_SUBTITLES_EN", mapping):
            value = localize_manifest([changed], self.root, "en")[0]
        self.assertEqual(value["subtitle"], "")
        self.assertEqual(value["summary"], "Published summary.")
        self.assertTrue(value["english_available"])

    def test_published_distinct_subtitle_has_precedence_over_hub_translation(self):
        self.write_article()
        mapping = {"sample-review": {"source": self.item["subtitle"], "text": "A faithful translated subtitle."}}
        with patch("scripts.hub_localization.HUB_SUBTITLES_EN", mapping):
            value = localize_manifest([self.item], self.root, "en")[0]
        self.assertEqual(value["subtitle"], "A distinct short subtitle.")

    def test_hub_subtitle_cannot_duplicate_the_published_summary(self):
        self.write_article('<meta name="description" content="Published summary."><h1>English title</h1><p class="dek">Published summary.</p>')
        mapping = {"sample-review": {"source": self.item["subtitle"], "text": "Published summary."}}
        with patch("scripts.hub_localization.HUB_SUBTITLES_EN", mapping):
            value = localize_manifest([self.item], self.root, "en")[0]
        self.assertEqual(value["subtitle"], "")

    def test_missing_or_incomplete_translation_falls_back_as_one_korean_entry(self):
        for document in (None, '<h1>English title without any summary</h1>'):
            if document is not None:
                self.write_article(document)
            item = localize_manifest([self.item], self.root, "en")[0]
            self.assertEqual((item["title"], item["subtitle"], item["summary"], item["href"]), (self.item["title"], self.item["subtitle"], self.item["summary"], self.item["href"]))
            self.assertEqual(item["content_language"], "ko")
            self.assertFalse(item["english_available"])

    def test_text_is_plain_and_can_be_escaped_once_without_active_markup(self):
        self.write_article('''<meta name="description" content="A &quot;quoted&quot; &lt;img src=x onerror=bad()&gt; result."><h1>Title &lt;script&gt;<script>bad()</script> &amp; value</h1><p class="dek">A distinct <strong>published</strong> subtitle.</p>''')
        item = localize_manifest([self.item], self.root, "en")[0]
        self.assertEqual(item["title"], "Title <script> & value")
        self.assertNotIn("bad()", item["title"])
        self.assertEqual(item["summary"], 'A "quoted" <img src=x onerror=bad()> result.')
        self.assertNotIn("<img", html.escape(item["summary"], quote=True))
        self.assertIn("&lt;img", html.escape(item["summary"], quote=True))

    def test_translation_paths_cannot_escape_or_switch_review_identity(self):
        self.write_article()
        unsafe = ["../../outside.html", "reviews/sample-review/en/%2e%2e/%2e%2e/other/index.html", "https://example.com/index.html", "https://[invalid", "javascript:bad()", "/reviews/sample-review/en/index.html", "reviews/sample-review/en/index.html?x=1", "reviews/another-review/en/index.html", "reviews/sample-review/en/%00index.html"]
        other = self.root / "reviews" / "another-review" / "en" / "index.html"
        other.parent.mkdir(parents=True)
        other.write_text(self.article.read_text(), encoding="utf-8")
        for href in unsafe:
            with self.subTest(href=href):
                item = deepcopy(self.item)
                item["translations"][0]["href"] = href
                value = localize_manifest([item], self.root, "en")[0]
                self.assertFalse(value["english_available"])
                self.assertEqual(value["href"], self.item["href"])

    def test_folder_identity_cannot_name_a_parent_directory(self):
        self.write_article()
        item = deepcopy(self.item)
        item["folder"] = ".."
        self.assertFalse(localize_manifest([item], self.root, "en")[0]["english_available"])

    def test_unsupported_language_is_rejected(self):
        with self.assertRaises(ValueError):
            localize_manifest([self.item], self.root, "fr")


if __name__ == "__main__":
    unittest.main()
