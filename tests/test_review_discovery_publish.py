from __future__ import annotations

import hashlib
import re
import unittest
from html.parser import HTMLParser
from unittest.mock import patch

from scripts import publish_public_site as publisher


def review(**changes):
    value = dict(folder="sample-review", title="A scientific title", subtitle="A concrete comparison", summary="A source-grounded explanation", date="2026-10-20", updated="2026-10-25", category="Quantum", tags=["Circuit", "Learning"], href="reviews/sample-review/index.html", metric_path="/AI_Tech_Review/reviews/sample-review/", thumbnail="", translations=[])
    value.update(changes)
    return value


class Cards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "article" and values.get("class") == "review-card":
            self.cards.append(values)


class ReviewDiscoveryPublicationTests(unittest.TestCase):
    def test_cards_use_stable_identity_original_publication_date_and_escaped_content_search(self):
        item = review(title='A "quoted" <term>', summary="A <script> term and test")
        text = publisher.render_review_card(item)
        parsed = Cards()
        parsed.feed(text)
        card = parsed.cards[0]
        self.assertEqual(card["data-article-id"], "sample-review")
        self.assertEqual(card["data-published"], "2026-10-20")
        self.assertIn(item["title"], card["data-search"])
        self.assertIn(item["summary"], card["data-search"])
        self.assertNotIn("좋아요", card["data-search"])
        self.assertNotIn("<script>", text)
        self.assertIn('data-discovery-field="opens">—', text)
        self.assertIn('data-discovery-field="likes">—', text)

    def test_hub_exposes_accessible_sort_period_pagination_and_public_contact(self):
        text = publisher.render_index([review()])
        for identifier in ["review-sort", "review-period", "discovery-from", "discovery-to", "review-results", "review-empty", "review-more"]:
            self.assertIn(f'id="{identifier}"', text)
        self.assertIn("관심 집계 기간", text)
        self.assertIn('id="discovery-dates" hidden', text)
        self.assertIn('aria-label="리뷰 목록"', text)
        self.assertIn('mailto:angpangmokjang@gmail.com', text)
        self.assertIn("카드 수치는 누적값", text)
        self.assertNotIn('id="review-grid" aria-live="polite"', text)

    def test_hub_asset_versions_follow_content_and_do_not_reuse_old_cached_scripts(self):
        text = publisher.render_index([review()])
        js_hash = hashlib.sha256(publisher.SITE_JS.encode()).hexdigest()[:12]
        self.assertIn(f'src="assets/site.js?v={js_hash}" defer', text)
        with patch.object(publisher, "SITE_JS", publisher.SITE_JS + "\n// content changes"):
            changed = publisher.render_index([review()])
        self.assertNotEqual(re.search(r'assets/site.js\?v=([a-f0-9]+)', text).group(1), re.search(r'assets/site.js\?v=([a-f0-9]+)', changed).group(1))


if __name__ == "__main__":
    unittest.main()
