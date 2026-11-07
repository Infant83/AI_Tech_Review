from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import time
import unittest

from PIL import Image

from scripts.listing_images import build_listing_images, image_attributes


class ListingImagesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name)
        self.source = self.site / "reviews" / "example" / "cover.png"
        self.source.parent.mkdir(parents=True)
        image = Image.new("RGB", (1600, 900), "#eeccaa")
        # Preserve visible edge landmarks: a crop would remove one side.
        for xs, color in [(range(32), (240, 0, 0)), (range(1568, 1600), (0, 0, 240))]:
            for x in xs:
                for y in range(900):
                    image.putpixel((x, y), color)
        image.save(self.source)
        self.href = self.source.relative_to(self.site).as_posix()

    def build(self, **kwargs):
        return build_listing_images(self.site, [self.href], **kwargs)

    def test_raster_dimensions_aspect_ratio_and_original_are_preserved(self):
        before = self.source.read_bytes()
        result = self.build(highlight_hrefs=[self.href])
        variants = result["images"][self.href]["variants"]
        self.assertEqual([(v["width"], v["height"]) for v in variants], [(480, 270), (960, 540), (1200, 675)])
        for variant in variants:
            with Image.open(self.site / variant["href"]) as image:
                self.assertEqual(image.size, (variant["width"], variant["height"]))
                self.assertGreater(image.getpixel((0, image.height // 2))[0], image.getpixel((0, image.height // 2))[2])
                self.assertGreater(image.getpixel((image.width - 1, image.height // 2))[2], image.getpixel((image.width - 1, image.height // 2))[0])
        self.assertEqual(self.source.read_bytes(), before)

    def test_unchanged_build_reuses_bytes_and_does_not_touch_files(self):
        result = self.build()
        paths = [self.site / v["href"] for v in result["images"][self.href]["variants"]]
        paths.append(self.site / "assets/listing-images/manifest.json")
        state = [(p.stat().st_mtime_ns, p.read_bytes()) for p in paths]
        time.sleep(0.01)
        self.assertEqual(self.build(), result)
        self.assertEqual([(p.stat().st_mtime_ns, p.read_bytes()) for p in paths], state)

    def test_source_change_has_new_urls_and_keeps_previous_derivatives(self):
        old = self.build()
        Image.new("RGB", (1600, 900), "green").save(self.source)
        new = self.build()
        old_urls = {v["href"] for v in old["images"][self.href]["variants"]}
        new_urls = {v["href"] for v in new["images"][self.href]["variants"]}
        self.assertTrue(old_urls.isdisjoint(new_urls))
        self.assertTrue(all((self.site / href).is_file() for href in old_urls))

    def test_corrupt_cached_file_is_repaired(self):
        result = self.build()
        variant = result["images"][self.href]["variants"][0]
        path = self.site / variant["href"]
        path.write_bytes(b"corruption")
        rebuilt = self.build()
        self.assertEqual(rebuilt, result)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), variant["sha256"])

    def test_vectors_remain_exact_vectors(self):
        source = self.source.with_suffix(".svg")
        original = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 9"><circle cx="8" cy="4" r="2"/></svg>'
        source.write_bytes(original)
        href = source.relative_to(self.site).as_posix()
        result = build_listing_images(self.site, [href])
        self.assertTrue(result["images"][href]["original_vector"])
        self.assertEqual(image_attributes(href, site_dir=self.site), {})
        self.assertEqual(source.read_bytes(), original)

    def test_no_upscale_and_no_duplicate_srcset_widths(self):
        Image.new("RGB", (100, 75), "red").save(self.source)
        self.build(highlight_hrefs=[self.href])
        attrs = image_attributes(self.href, role="highlight", site_dir=self.site)
        self.assertEqual((attrs["width"], attrs["height"]), (100, 75))
        self.assertEqual(attrs["srcset"].count("100w"), 1)

    def test_indexed_transparency_is_retained(self):
        image = Image.new("P", (600, 300), color=0)
        image.putpalette([0, 0, 0, 255, 0, 0] + [0] * (768 - 6))
        image.putpixel((300, 150), 1)
        image.save(self.source, transparency=0)
        result = self.build()
        path = self.site / result["images"][self.href]["variants"][0]["href"]
        with Image.open(path) as exported:
            self.assertEqual(exported.mode, "RGBA")
            self.assertEqual(exported.getpixel((0, 0))[3], 0)

    def test_role_prefix_and_missing_manifest_fallback(self):
        self.assertEqual(image_attributes(self.href, site_dir=self.site), {})
        self.build(highlight_hrefs=[self.href])
        attrs = image_attributes(self.href, prefix="../", site_dir=self.site)
        self.assertTrue(attrs["src"].startswith("../assets/listing-images/"))
        self.assertIn("480w", attrs["srcset"])
        self.assertIn("960w", attrs["srcset"])
        self.assertNotIn("1200w", attrs["srcset"])
        self.assertIn("1200w", image_attributes(self.href, role="highlight", site_dir=self.site)["srcset"])

    def test_unsafe_sources_and_symlink_targets_rejected(self):
        for href in ["../secret.png", "/tmp/secret.png", "https://example.org/cover.png", "reviews/%2e%2e/private.png", "reviews//cover.png"]:
            with self.subTest(href=href), self.assertRaises(ValueError):
                build_listing_images(self.site, [href])
        linked = self.source.with_name("linked.png")
        linked.symlink_to(self.source)
        with self.assertRaises(ValueError):
            build_listing_images(self.site, [linked.relative_to(self.site).as_posix()])

    def test_symlink_output_rejected(self):
        target = self.site / "external"
        target.mkdir()
        (self.site / "assets").mkdir()
        (self.site / "assets/listing-images").symlink_to(target, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.build()


if __name__ == "__main__":
    unittest.main()
