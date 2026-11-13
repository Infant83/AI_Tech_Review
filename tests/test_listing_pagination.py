from __future__ import annotations

from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import json
from urllib.parse import urljoin

from scripts.listing_pagination import page_count, page_path, page_prefix, pagination, generated_paths
from scripts.hub_layout import render_hub
from scripts.document_archive_site import render_archive
from scripts.briefing_site import render_briefings


class Cards(HTMLParser):
    def __init__(self, text, class_name, key):
        super().__init__()
        self.ids, self.links = [], []
        self.class_name, self.key = class_name, key
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.class_name in attrs.get("class", "").split():
            self.ids.append(attrs[self.key])
        if tag == "a":
            self.links.append(attrs.get("href", ""))


class ListingPaginationTests(unittest.TestCase):
    def documents(self, count):
        result = []
        for number in range(count):
            day = (date(2026, 11, 7) - timedelta(days=number)).isoformat()
            result.append({"id": day + "-brief", "date": day, "title": f"Brief {number}", "title_en": f"Brief {number}", "summary": f"Summary {number}", "summary_en": f"Summary {number}", "language": "ko", "series": "daily-quantum", "tags": ["QML"], "href": "archive/files/" + day + "-brief.pdf", "size_bytes": 1000})
        return result

    def test_paths_and_prefixes_resolve_every_language_and_page_to_same_root(self):
        root = "https://example.test/AI_Tech_Review/"
        for area in ("reviews", "archive", "briefings"):
            for language in ("ko", "en"):
                for number in (1, 2, 10):
                    path = page_path(area, language, number)
                    self.assertEqual(urljoin(root + path, page_prefix(area, language, number) + "assets/site.css"), root + "assets/site.css")

    def test_pager_links_remain_small_and_reachable_for_large_collections(self):
        text = pagination("reviews", "ko", 600, 10000)
        parsed = Cards(text, "unused", "id")
        self.assertLessEqual(len(parsed.links), 8)
        self.assertIn('rel="next"', text)
        self.assertIn('rel="prev"', text)
        self.assertEqual(page_count(55, "reviews"), 10)
        self.assertEqual(page_count(119, "archive"), 10)

    def test_research_briefings_count_towards_generated_list_pages(self):
        docs = self.documents(12)
        research = {**docs[0], "id": "2026-11-07-research", "series": "daily-research"}
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "manifest.json").write_text("[]")
            (root / "archive-manifest.json").write_text(json.dumps({"documents": docs + [research]}))
            paths = generated_paths(root)
            self.assertIn("briefings/page/2/index.html", paths)
            self.assertIn("briefings/en/page/2/index.html", paths)

    def test_review_html_contains_only_the_requested_six_and_covers_every_id_once(self):
        documents = self.documents(19)
        reviews = [{"folder": "r" + str(i), "title": doc["title"], "summary": doc["summary"], "subtitle": "Subtitle", "category": "Quantum Computing", "tags": [], "date": doc["date"], "href": f"reviews/r{i}/index.html", "metric_path": f"/AI_Tech_Review/reviews/r{i}/"} for i, doc in enumerate(documents)]
        with TemporaryDirectory() as directory:
            for language in ("ko", "en"):
                found = []
                for number in range(1, page_count(len(reviews), "reviews") + 1):
                    source = render_hub(reviews, [], [], site_dir=Path(directory), language=language, css_version="c", js_version="j", preferences_version="p", library_version="l", page_number=number)
                    ids = Cards(source, "review-card", "data-article-id").ids
                    self.assertLessEqual(len(ids), 6)
                    self.assertEqual(ids, [item["folder"] for item in reviews[(number - 1) * 6:number * 6]])
                    found.extend(ids)
                    if number > 1:
                        self.assertNotIn('class="latest-update"', source)
                self.assertEqual(found, [item["folder"] for item in reviews])

    def test_archive_and_briefings_have_twelve_real_cards_per_static_page(self):
        docs = self.documents(31)
        for area, renderer, class_name, key in (("archive", render_archive, "document-card", "data-document-id"), ("briefings", render_briefings, "briefing-row", "data-id")):
            for language in ("ko", "en"):
                found = []
                for number in range(1, page_count(len(docs), area) + 1):
                    source = renderer(docs, "https://example.test/AI_Tech_Review/", language, page_number=number)
                    ids = Cards(source, class_name, key).ids
                    self.assertLessEqual(len(ids), 12)
                    self.assertEqual(ids, [doc["id"] for doc in docs[(number - 1) * 12:number * 12]])
                    found.extend(ids)
                self.assertEqual(found, [doc["id"] for doc in docs])


if __name__ == "__main__":
    unittest.main()
