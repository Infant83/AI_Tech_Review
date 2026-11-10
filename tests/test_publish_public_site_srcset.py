from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts.publish_public_site import (
    REVIEWS,
    SITE_DIR,
    sanitize_for_public,
    srcset_candidates,
    validate_local_references,
)


class PublicSiteSrcsetTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.dist = self.directory / "dist"
        self.public = self.directory / "public"
        self.dist.mkdir()
        self.public.mkdir()
        self.review = REVIEWS[0]
        for name in ("desktop.svg", "mobile.svg", "mobile-high.svg"):
            (self.dist / name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg"><title>{name}</title></svg>\n')

    def publish(self, srcset: str):
        source = (
            '<html lang="ko"><head><title>Review</title></head><body><main>'
            f'<h1>{self.review.title}</h1><picture>'
            f'<source media="(max-width:600px)" srcset="{srcset}">'
            '<img src="desktop.svg" alt="Same explanation at both widths">'
            '</picture></main></body></html>'
        )
        return sanitize_for_public(
            source, self.dist, self.public, self.review, "ko",
            SITE_DIR / "reviews" / self.review.folder,
        )

    def test_picture_single_mobile_candidate_is_copied_and_keeps_its_reference(self):
        text, assets = self.publish("mobile.svg")
        self.assertEqual(set(assets), {"desktop.svg", "mobile.svg"})
        self.assertIn('srcset="mobile.svg"', text)
        self.assertIn('src="desktop.svg"', text)
        self.assertEqual((self.public / "mobile.svg").read_bytes(), (self.dist / "mobile.svg").read_bytes())
        picture = text[text.index("<picture>"):text.index("</picture>") + len("</picture>")]
        self.assertEqual(validate_local_references(self.public / "index.html", picture), [])

    def test_multiple_width_and_density_candidates_are_individual_assets(self):
        for srcset in (
            "mobile.svg 390w, mobile-high.svg 780w",
            "mobile.svg 1x, mobile-high.svg 2x",
        ):
            with self.subTest(srcset=srcset):
                text, assets = self.publish(srcset)
                self.assertEqual(set(assets), {"desktop.svg", "mobile.svg", "mobile-high.svg"})
                self.assertIn(f'srcset="{srcset}"', text)
                picture = text[text.index("<picture>"):text.index("</picture>") + len("</picture>")]
                self.assertEqual(validate_local_references(self.public / "index.html", picture), [])

    def test_query_and_fragment_are_preserved_without_becoming_filenames(self):
        text, assets = self.publish("mobile.svg?v=23#layer 1x, mobile-high.svg?v=23 2x")
        self.assertEqual(set(assets), {"desktop.svg", "mobile.svg", "mobile-high.svg"})
        self.assertIn('srcset="mobile.svg?v=23#layer 1x, mobile-high.svg?v=23 2x"', text)

    def test_outside_private_missing_or_unapproved_srcset_fails(self):
        (self.directory / "outside.svg").write_text("<svg/>")
        (self.dist / "working.json").write_text('{"private":true}')
        for srcset in (
            "../outside.svg", "%2e%2e/outside.svg", "working.json", "missing.svg",
            "/Users/private/figure.svg", "http://intranet.local/figure.svg",
            "mobile.svg 1x, ../outside.svg 2x",
        ):
            with self.subTest(srcset=srcset), self.assertRaises(ValueError):
                self.publish(srcset)
        self.assertFalse((self.public / "outside.svg").exists())
        self.assertFalse((self.public / "working.json").exists())

    def test_missing_or_invalid_srcset_is_found_by_local_reference_validation(self):
        page = self.public / "index.html"
        for srcset in ("missing.svg", "mobile.svg 1x, missing.svg 2x", "mobile.svg oops"):
            with self.subTest(srcset=srcset):
                self.assertTrue(validate_local_references(page, f'<source srcset="{srcset}">'))

    def test_parser_keeps_commas_in_external_urls_and_rejects_invalid_descriptors(self):
        data = "data:image/svg+xml,%3Csvg%3E%3C/svg%3E"
        self.assertEqual(srcset_candidates(data + " 1x, mobile.svg 2x"), [(data, "1x"), ("mobile.svg", "2x")])
        self.assertEqual(srcset_candidates("mobile.svg, mobile-high.svg"), [("mobile.svg", ""), ("mobile-high.svg", "")])
        for value in ("", "mobile.svg 0x", "mobile.svg 0w", "mobile.svg 1x 2x", "mobile.svg nope"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                srcset_candidates(value)

    def test_existing_external_and_anchor_attributes_remain_byte_exact(self):
        anchors = (
            '<a href="https://example.org/paper?a=1&amp;b=2">Source</a>'
            '<a href="#condition">Condition</a>'
            "<a href='https://example.org/other?a=1&amp;b=2'>Other</a>"
            '<a href="https://example.org/legacy&quot;">Legacy entity</a>'
            '<img src="https://example.org/image.svg?a=1&amp;b=2" alt="External">'
        )
        source = ('<html lang="ko"><head><title>Review</title></head><body><main>'
                  f'<h1>{self.review.title}</h1>{anchors}</main></body></html>')
        text, assets = sanitize_for_public(
            source, self.dist, self.public, self.review, "ko",
            SITE_DIR / "reviews" / self.review.folder,
        )
        self.assertIn(anchors, text)
        self.assertNotIn("&amp;amp;", text)
        self.assertEqual(assets, [])


if __name__ == "__main__":
    unittest.main()
