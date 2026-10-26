from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.hub_layout import render_card, render_hub


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


class _HubParser(HTMLParser):
    """Keep control descendants so icon labels can be checked without a browser."""
    void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self, source):
        super().__init__()
        self.nodes = []
        self.stack = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag, "attrs": dict(attrs), "children": [], "text": ""}
        self.nodes.append(node)
        if self.stack:
            self.stack[-1]["children"].append(node)
        if tag not in self.void_tags:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.void_tags:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        if self.stack:
            self.stack[-1]["text"] += data


class HubToolbarTests(unittest.TestCase):
    def render(self, language):
        with TemporaryDirectory() as directory:
            return _HubParser(render_hub(
                [], [], [], site_dir=Path(directory), language=language,
                css_version="test-css", js_version="test-js",
                preferences_version="test-preferences", library_version="test-library",
            ))

    def descendants(self, node):
        result = []
        for child in node["children"]:
            result.append(child)
            result.extend(self.descendants(child))
        return result

    def test_profile_mail_and_guidance_links_remain_named_when_they_use_icons(self):
        for language, prefix in (("ko", ""), ("en", "../")):
            parsed = self.render(language)
            expected = {
                "https://infant83.io/", f"{prefix}methods/",
                f"{prefix}methods/#reader-metrics", "mailto:angpangmokjang@gmail.com",
            }
            links = [node for node in parsed.nodes if node["tag"] == "a" and node["attrs"].get("href") in expected]
            with self.subTest(language=language):
                self.assertEqual({node["attrs"]["href"] for node in links}, expected)
                for link in links:
                    self.assertTrue(link["attrs"].get("aria-label", "").strip())
                    self.assertTrue(link["attrs"].get("title", "").strip())
                    self.assertEqual(link["text"].strip(), "", "long functional labels should not remain visible")
                    icons = [node for node in self.descendants(link) if node["tag"] == "svg"]
                    self.assertEqual(len(icons), 1)
                    self.assertEqual(icons[0]["attrs"].get("aria-hidden"), "true")
                    self.assertEqual(icons[0]["attrs"].get("focusable"), "false")

    def test_language_and_brightness_are_independent_accessible_binary_controls(self):
        for language in ("ko", "en"):
            parsed = self.render(language)
            with self.subTest(language=language):
                for attribute, checked in (("data-hub-language-toggle", "true" if language == "en" else "false"),
                                           ("data-hub-theme-toggle", "false")):
                    controls = [node for node in parsed.nodes if attribute in node["attrs"]]
                    self.assertEqual(len(controls), 1)
                    control = controls[0]
                    self.assertEqual(control["tag"], "button")
                    self.assertEqual(control["attrs"].get("type"), "button")
                    self.assertEqual(control["attrs"].get("role"), "switch")
                    self.assertEqual(control["attrs"].get("aria-checked"), checked)
                    self.assertTrue(control["attrs"].get("aria-label", "").strip())
                    self.assertTrue(control["attrs"].get("title", "").strip())
                self.assertFalse(any("data-hub-language-select" in node["attrs"] for node in parsed.nodes))
                self.assertFalse(any("data-hub-theme" in node["attrs"] for node in parsed.nodes))


if __name__ == "__main__":
    unittest.main()
