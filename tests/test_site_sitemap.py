"""Small registered-public HTML fixtures; no network/PDF/source rendering."""
from html import escape
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts import site_sitemap as sitemap


class SitemapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.site = Path(self.temp.name)
        self.reviews = []
        self.archive = {"documents": [], "external_resources": []}
        self.registries()

    def registries(self):
        (self.site / "manifest.json").write_text(json.dumps(self.reviews))
        (self.site / "archive-manifest.json").write_text(json.dumps(self.archive))

    def page(self, name, canonical=None, extra=""):
        target = self.site / name; target.parent.mkdir(parents=True, exist_ok=True)
        canonical = canonical or sitemap.BASE_URL + name.removesuffix("index.html")
        target.write_text('<!doctype html><html><head><link rel="canonical" href="' +
                          escape(canonical, quote=True) + '">' + extra + '</head><body>same source</body></html>')
        return target

    def registered(self, name="reviews/a/index.html", **kwargs):
        self.reviews.append({"folder": name.split('/')[1], "href": name, **kwargs})
        self.registries(); return self.page(name)

    def urls(self):
        root = ET.fromstring((self.site / "sitemap.xml").read_bytes())
        return [node.text for node in root.findall('{'+sitemap.NAMESPACE+'}url/{'+sitemap.NAMESPACE+'}loc')]

    def test_registered_languages_study_editorial_and_core_paths_keep_exact_mapping(self):
        self.registered(translations=[{"language": "en", "href": "reviews/a/en/index.html", "assets": []}])
        self.page("reviews/a/en/index.html")
        self.archive["documents"] = [{"id": "lesson", "href": "archive/files/lesson.pdf",
            "study_href": "lectures/lesson/", "study_assets": {"chapter.html": "unused"},
            "editorial_href": "briefings/lesson/index.html", "editorial_en_href": "briefings/lesson/en/index.html"}]
        for name in ["lectures/lesson/index.html", "lectures/lesson/chapter.html",
                     "briefings/lesson/index.html", "briefings/lesson/en/index.html", "index.html", "en/index.html"]:
            self.page(name)
        self.registries()
        result = sitemap.build_sitemap(self.site)
        self.assertEqual(result["urls"], 8)
        self.assertIn(sitemap.BASE_URL + "reviews/a/en/", self.urls())
        self.assertIn(sitemap.BASE_URL + "lectures/lesson/chapter.html", self.urls())
        self.assertNotIn(".pdf", (self.site / "sitemap.xml").read_text())

    def test_canonical_alias_dedup_noindex_googlebot_refresh_and_unregistered_html(self):
        self.registered(assets=["alias.html", "blocked.html", "refresh.html", "googlebot.html"])
        self.page("reviews/a/alias.html", sitemap.BASE_URL + "reviews/a/")
        self.page("reviews/a/blocked.html", extra='<meta name="robots" content="noindex, follow">')
        self.page("reviews/a/googlebot.html", extra='<meta name="googlebot" content="none">')
        self.page("reviews/a/refresh.html", extra='<meta http-equiv="refresh" content="0;url=/">')
        self.page("output/private/index.html")
        self.page("reviews/a/unregistered.html")
        sitemap.build_sitemap(self.site)
        self.assertEqual(self.urls(), [sitemap.BASE_URL + "reviews/a/"])

    def test_utf8_XML_escape_stable_order_and_no_invented_lastmod(self):
        self.registered("reviews/z&별/index.html")
        self.registered("reviews/a/index.html")
        sitemap.build_sitemap(self.site)
        first = (self.site / "sitemap.xml").read_bytes()
        self.assertIn(b"&amp;", first)
        self.assertIn("%EB%B3%84", first.decode())
        self.assertNotIn(b"lastmod", first)
        self.assertEqual(self.urls(), sorted(self.urls()))
        self.assertFalse(sitemap.build_sitemap(self.site)["changed"])
        self.assertEqual(first, (self.site / "sitemap.xml").read_bytes())

    def test_foreign_outside_query_fragment_or_unregistered_canonical_refused_before_write(self):
        target = self.registered()
        sitemap.build_sitemap(self.site); original = (self.site / "sitemap.xml").read_bytes()
        for url in ["https://elsewhere.invalid/a/", "https://infant83.io/private/",
                    sitemap.BASE_URL + "reviews/a/?q=x", sitemap.BASE_URL + "reviews/a/#part",
                    sitemap.BASE_URL + "output/private/", sitemap.BASE_URL + "reviews/missing/"]:
            with self.subTest(url=url):
                self.page("reviews/a/index.html", url)
                with self.assertRaises(sitemap.SitemapError): sitemap.build_sitemap(self.site)
                self.assertEqual(original, (self.site / "sitemap.xml").read_bytes())
        target.unlink()
        with self.assertRaises(sitemap.SitemapError): sitemap.build_sitemap(self.site)

    def test_registered_private_paths_and_symlink_inputs_or_output_are_refused(self):
        self.reviews = [{"folder": "bad", "href": "output/private/index.html"}]
        self.registries()
        with self.assertRaises(sitemap.SitemapError): sitemap.build_sitemap(self.site)
        self.reviews = []; self.registries(); target = self.registered()
        other = self.site / "canary.html"; other.write_bytes(target.read_bytes())
        target.unlink(); target.symlink_to(other)
        with self.assertRaises(sitemap.SitemapError): sitemap.build_sitemap(self.site)
        target.unlink(); self.page("reviews/a/index.html")
        (self.site / "sitemap.xml").symlink_to(other)
        before = other.read_bytes()
        with self.assertRaises(sitemap.SitemapError): sitemap.build_sitemap(self.site)
        self.assertEqual(before, other.read_bytes())

    def test_body_canonical_is_ignored_and_canonical_cycles_refused(self):
        target = self.registered()
        target.write_text('<html><head></head><body><link rel="canonical" href="'+sitemap.BASE_URL+'reviews/a/"></body></html>')
        self.assertEqual(sitemap.build_sitemap(self.site)["urls"], 0)
        self.registered("reviews/b/index.html")
        self.page("reviews/a/index.html", sitemap.BASE_URL + "reviews/b/")
        self.page("reviews/b/index.html", sitemap.BASE_URL + "reviews/a/")
        with self.assertRaises(sitemap.SitemapError): sitemap.build_sitemap(self.site)

    def test_second_listing_pages_are_discovered_from_current_registration_count(self):
        for number in range(7):
            self.registered('reviews/a'+str(number)+'/index.html')
        for name in ('page/2/index.html', 'en/page/2/index.html'):
            self.page(name)
        sitemap.build_sitemap(self.site)
        self.assertIn(sitemap.BASE_URL+'page/2/', self.urls())
        self.assertIn(sitemap.BASE_URL+'en/page/2/', self.urls())


if __name__ == "__main__":
    unittest.main()
