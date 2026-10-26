from __future__ import annotations

from html.parser import HTMLParser
import unittest

from scripts.hub_layout import render_card


class _CardParser(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.elements = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


class HubCardSummaryTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "folder": "sample-review", "title": "Review title", "subtitle": "Short subtitle",
            "summary": "Complete review summary <with> quoted & unquoted findings.",
            "href": "reviews/sample-review/index.html", "metric_path": "/AI_Tech_Review/reviews/sample-review/",
            "date": "2026-10-25", "category": "Quantum Computing", "tags": [],
            "thumbnail": "reviews/sample-review/cover.png",
        }

    def test_complete_summary_remains_visible_without_javascript_and_inactive_toggle_is_hidden(self):
        source = render_card(self.item)
        parsed = _CardParser(source)
        summary = next(attrs for tag, attrs in parsed.elements if attrs.get("class") == "review-summary")
        button = next(attrs for tag, attrs in parsed.elements if "data-summary-toggle" in attrs)
        self.assertNotIn("data-summary-collapsed", summary)
        self.assertNotIn("hidden", summary)
        self.assertIn("Complete review summary &lt;with&gt; quoted &amp; unquoted findings.", source)
        self.assertIn("Short subtitle", source)
        self.assertIn("hidden", button)
        self.assertEqual(button["aria-controls"], summary["id"])
        self.assertEqual(button["aria-expanded"], "false")

    def test_summary_identity_survives_language_changes_and_button_text_is_localized(self):
        ko, en = render_card(self.item, "ko"), render_card(self.item, "en", "../")
        self.assertIn('id="review-summary-sample-review"', ko)
        self.assertIn('id="review-summary-sample-review"', en)
        self.assertIn("요약 더 보기", ko)
        self.assertIn("Read full summary", en)

    def test_empty_summary_does_not_create_an_unusable_toggle(self):
        self.item["summary"] = ""
        self.assertNotIn("data-summary-toggle", render_card(self.item))


if __name__ == "__main__":
    unittest.main()
