import tempfile
import hashlib
import json
from pathlib import Path
import unittest

from scripts.site_payload_budget import check_budget, page_payload


class PayloadBudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name)
        (self.site / "assets").mkdir()
        (self.site / "index.html").write_text('<html><script src="assets/ui.js"></script></html>')
        (self.site / "assets/ui.js").write_text('document.title="Sample";')

    def test_small_ui_passes_without_eager_search_index(self):
        self.assertTrue(check_budget(self.site)["ok"])

    def test_eager_search_runtime_and_preload_are_rejected(self):
        (self.site / "assets/minisearch.js").write_text("runtime")
        for markup in ['<script src="assets/minisearch.js"></script>', '<link rel="preload" href="assets/minisearch.js">']:
            (self.site / "index.html").write_text(markup)
            self.assertFalse(check_budget(self.site)["ok"])

    def test_external_resource_is_reported_not_counted_as_local_zero(self):
        (self.site / "index.html").write_text('<link rel="stylesheet" href="https://fonts.example/css">')
        report = page_payload(self.site, "index.html")
        self.assertEqual(report["external_resources"], ["https://fonts.example/css"])

    def test_missing_resource_does_not_pass_as_small(self):
        (self.site / "assets/ui.js").unlink()
        with self.assertRaises(ValueError): page_payload(self.site, "index.html")

    def test_widget_requires_all_lazy_assets(self):
        (self.site / "index.html").write_text('<form data-site-search></form>')
        report = check_budget(self.site)
        self.assertFalse(report["ok"])
        self.assertEqual(sum("requires missing" in failure for failure in report["failures"]), 3)
        for name in ("minisearch.js", "site-search-core.js", "search-records.json"):
            (self.site / "assets" / name).write_text("{}")
        self.assertTrue(check_budget(self.site)["ok"])

    def test_deployed_payload_map_controls_initial_limit(self):
        report = check_budget(self.site, baseline_payload={"index.html": 0})
        self.assertEqual(report["pages"]["index.html"]["max_gzip_bytes"], 5_000)
        capped = check_budget(self.site, baseline_payload={"index.html": 99_000})
        self.assertEqual(capped["pages"]["index.html"]["max_gzip_bytes"], 100_000)
        for invalid in [{"other.html": 4}, {"index.html": -1}, {"index.html": True}, []]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                check_budget(self.site, baseline_payload=invalid)

    def listing_fixture(self, *, small=10_000, large=20_000, highlight=True):
        article = self.site / "reviews/example/index.html"
        article.parent.mkdir(parents=True)
        article.write_text("<html>Reviewed article</html>")
        original = article.parent / "cover.png"
        original.write_bytes(b"o" * 100_000)
        variants = []
        directory = self.site / "assets/listing-images"
        directory.mkdir()
        for width, size in [(480, small), (960, large)]:
            path = directory / ("a" * 64 + f"-w{width}.webp")
            data = bytes([width % 256]) * size
            path.write_bytes(data)
            variants.append({"href": path.relative_to(self.site).as_posix(), "width": width,
                             "height": width * 9 // 16, "bytes": size,
                             "sha256": hashlib.sha256(data).hexdigest()})
        (self.site / "manifest.json").write_text(json.dumps([{"folder": "example", "href": "reviews/example/index.html", "thumbnail": "reviews/example/cover.png"}]))
        (directory / "manifest.json").write_text(json.dumps({"version": 1, "images": {
            "reviews/example/cover.png": {"source_sha256": hashlib.sha256(original.read_bytes()).hexdigest(), "variants": variants}}}))
        srcset = ", ".join(f'{v["href"]} {v["width"]}w' for v in variants)
        card = f'<article class="review-card" data-article-id="example"><a class="thumb"><img src="{variants[0]["href"]}" srcset="{srcset}"></a></article>'
        hero = f'<a class="latest-media" href="reviews/example/index.html"><img src="{variants[1]["href"]}" srcset="{srcset}"></a>' if highlight else ""
        markup = card + hero
        (self.site / "index.html").write_text(markup)
        return markup, variants

    def test_listing_budget_counts_defaults_and_viewport_choices(self):
        self.listing_fixture()
        report = check_budget(self.site)
        self.assertTrue(report["ok"])
        listing = report["pages"]["index.html"]["listing_images"]
        self.assertEqual(listing["default_bytes"], 30_000)
        self.assertEqual(listing["viewport_360_1x_bytes"], 10_000)
        self.assertEqual(listing["viewport_1280_1x_bytes"], 30_000)
        self.assertEqual(listing["viewport_1280_2x_bytes"], 20_000)

    def test_original_cover_regression_is_rejected_even_after_sixth_card(self):
        markup, _ = self.listing_fixture(highlight=False)
        original = '<article class="review-card" data-article-id="example"><a class="thumb"><img src="reviews/example/cover.png"></a></article>'
        (self.site / "index.html").write_text(markup * 6 + original)
        with self.assertRaisesRegex(ValueError, "Large original"):
            check_budget(self.site)

    def test_broken_variant_or_wrong_srcset_width_is_rejected(self):
        markup, variants = self.listing_fixture()
        (self.site / "index.html").write_text(markup.replace("480w", "600w"))
        with self.assertRaisesRegex(ValueError, "srcset width"):
            check_budget(self.site)
        (self.site / "index.html").write_text(markup)
        (self.site / variants[0]["href"]).write_bytes(b"modified")
        with self.assertRaisesRegex(ValueError, "Modified listing-image"):
            check_budget(self.site)

    def test_default_image_budget_blocks_bloat_and_retina_budget_warns(self):
        self.listing_fixture(small=300_001, large=400_001)
        report = check_budget(self.site)
        self.assertFalse(report["ok"])
        self.assertTrue(any("650KB" in failure for failure in report["failures"]))

    def test_retina_budget_is_a_quality_review_warning(self):
        self.listing_fixture(small=10_000, large=900_000, highlight=False)
        report = check_budget(self.site)
        self.assertTrue(report["ok"])
        self.assertTrue(any("800KB" in warning for warning in report["warnings"]))

    def test_original_tiny_raster_or_svg_can_remain_direct(self):
        self.listing_fixture(highlight=False)
        original = self.site / "reviews/example/cover.png"
        original.write_bytes(b"tiny")
        (self.site / "assets/listing-images/manifest.json").unlink()
        (self.site / "index.html").write_text('<article class="review-card" data-article-id="example"><a class="thumb"><img src="reviews/example/cover.png"></a></article>')
        self.assertTrue(check_budget(self.site)["ok"])

    def test_translated_highlight_maps_to_same_original_cover(self):
        markup, _ = self.listing_fixture()
        translation = self.site / "reviews/example/en/index.html"
        translation.parent.mkdir()
        translation.write_text("<html>English article</html>")
        manifest = json.loads((self.site / "manifest.json").read_text())
        manifest[0]["translations"] = [{"language": "en", "href": "reviews/example/en/index.html"}]
        (self.site / "manifest.json").write_text(json.dumps(manifest))
        page = self.site / "en/index.html"
        page.parent.mkdir()
        page.write_text(markup.replace('href="reviews/example/index.html"', 'href="../reviews/example/en/index.html"').replace('src="assets/', 'src="../assets/').replace('srcset="assets/', 'srcset="../assets/').replace(', assets/', ', ../assets/'))
        self.assertTrue(check_budget(self.site)["ok"])


if __name__ == "__main__":
    unittest.main()
