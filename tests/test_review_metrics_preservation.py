from contextlib import ExitStack
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from scripts import publish_public_site as publisher


class ReviewMetricsPreservationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.site = self.root / "site"
        self.review = publisher.PublicReview(
            folder="2026-08-27-example", title="Recorded experiment", subtitle="Batch selection",
            date="2026-08-27", updated="2026-11-08", category="Materials AI", tags=(),
            summary="An experiment.",
            translations=(publisher.PublicTranslation("en", "en", "English"),),
        )
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name, value in (("ROOT", self.root), ("SITE_DIR", self.site),
                            ("REVIEWS_DIR", self.site / "reviews"),
                            ("ASSETS_DIR", self.site / "assets")):
            self.stack.enter_context(patch.object(publisher, name, value))
        self.stack.enter_context(patch.dict(os.environ, {}, clear=True))
        self.stack.enter_context(patch.object(publisher, "DEFAULT_PUBLIC_METRICS_ENDPOINT", ""))
        # A redesigned hub need not carry the older per-article counter.
        self.site.mkdir()
        (self.site / "index.html").write_text("<html><head></head><body>Hub</body></html>")
        for subdir in ("", "en"):
            dist = self.root / self.review.folder / "dist" / subdir
            dist.mkdir(parents=True)
            (dist / "index.html").write_text(self.html("Revised scientific text."))

    @staticmethod
    def html(body, config=None):
        script = "" if config is None else (
            "<script>window.AI_TECH_REVIEW_METRICS=" + json.dumps(config) + ";</script>"
        )
        return "<!doctype html><html><head><title>Experiment</title></head><body><h1>Experiment</h1><p>" + body + "</p>" + script + "</body></html>"

    @staticmethod
    def config(endpoint):
        return {"endpoint": endpoint, "basePath": "/AI_Tech_Review/", "siteId": "ai-tech-review"}

    def seed(self, ko="https://ko-counter.example.com", en="https://en-counter.example.com"):
        for subdir, endpoint in (("", ko), ("en", en)):
            public = self.review.public_dir / subdir
            public.mkdir(parents=True)
            (public / "index.html").write_text(self.html("Original scientific text.", self.config(endpoint)))

    def actual_config(self, subdir=""):
        text = (self.review.public_dir / subdir / "index.html").read_text()
        configs = re.findall(r"window\.AI_TECH_REVIEW_METRICS=(\{.*?\});", text)
        self.assertEqual(len(configs), 1)
        return json.loads(configs[0]), text

    def test_republication_preserves_each_existing_language_without_mutating_global_config(self):
        self.seed()
        publisher.restore_published_analytics()
        publisher.publish_review(self.review)
        for subdir, endpoint, prefix in (("", "https://ko-counter.example.com", "../../"),
                                         ("en", "https://en-counter.example.com", "../../../")):
            with self.subTest(language=subdir or "ko"):
                config, text = self.actual_config(subdir)
                self.assertEqual(config, self.config(endpoint))
                self.assertIn("Revised scientific text.", text)
                self.assertNotIn("Original scientific text.", text)
                self.assertIn(f'src="{prefix}assets/public-metrics.js"', text)
        self.assertNotIn(publisher.PUBLIC_METRICS_ENDPOINT_ENV, os.environ)

    def test_explicit_current_and_legacy_endpoint_configuration_still_wins(self):
        for key in (publisher.PUBLIC_METRICS_ENDPOINT_ENV, publisher.LEGACY_PUBLIC_METRICS_ENDPOINT_ENV):
            with self.subTest(key=key), patch.dict(os.environ, {key: "https://configured.example.com"}, clear=True):
                self.seed_if_missing()
                publisher.publish_review(self.review)
                for subdir in ("", "en"):
                    self.assertEqual(self.actual_config(subdir)[0], self.config("https://configured.example.com"))

    def seed_if_missing(self):
        if not self.review.public_dir.exists():
            self.seed()

    def test_new_dist_script_is_not_adopted_as_published_configuration(self):
        for subdir in ("", "en"):
            dist = self.root / self.review.folder / "dist" / subdir / "index.html"
            dist.write_text(self.html("New article.", self.config("https://unreviewed-counter.example.com")))
        publisher.publish_review(self.review)
        for subdir in ("", "en"):
            text = (self.review.public_dir / subdir / "index.html").read_text()
            self.assertNotIn("window.AI_TECH_REVIEW_METRICS", text)
            self.assertNotIn("unreviewed-counter", text)

    def test_refresh_of_existing_variant_retains_published_counter(self):
        self.seed()
        text = publisher.refresh_existing_public_variant(self.review, self.review.public_dir, "ko")
        self.assertEqual(self.actual_config()[0], self.config("https://ko-counter.example.com"))
        self.assertIn("Original scientific text.", text)

    def test_ordinary_article_text_does_not_become_metrics_configuration(self):
        prose = self.html('The API uses <code>window.AI_TECH_REVIEW_METRICS</code>.')
        self.assertIsNone(publisher.published_variant_metrics_config(prose))

    def test_private_or_ambiguous_historical_settings_fail_instead_of_being_copied(self):
        for endpoint in ("file:///secret", "https://user:password@example.com", "http://127.0.0.1",
                         "https://counter.internal", "https://counter.example.com?token=private"):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    publisher.published_variant_metrics_config(self.html("old", self.config(endpoint)))
        config = self.config("https://counter.example.com")
        for changed in ({**config, "siteId": "another-site"}, {**config, "basePath": "/another/"},
                        {**config, "unexpected": "field"}):
            with self.assertRaises(ValueError):
                publisher.published_variant_metrics_config(self.html("old", changed))
        with self.assertRaises(ValueError):
            publisher.published_variant_metrics_config(self.html("old", config) + self.html("duplicate", config))


if __name__ == "__main__":
    unittest.main()
