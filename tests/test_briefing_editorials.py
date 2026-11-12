from __future__ import annotations

import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts import briefing_editorials, briefing_site


BASE_URL = "https://example.org/AI_Tech_Review/"
IDENTITY = "2026-11-12-daily-quantum-brief"


def document() -> dict:
    return {
        "id": IDENTITY, "date": "2026-11-12", "series": "daily-quantum",
        "title": "표본에서 계산으로", "title_en": "From samples to computation",
        "summary": "처리량과 계산의 효용을 함께 읽습니다.",
        "summary_en": "Reading throughput alongside computational value.",
        "tags": ["Quantum"], "language": "ko",
        "href": f"archive/files/{IDENTITY}.pdf",
    }


class BriefingEditorialTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "repo"
        self.staging = Path(self.temporary.name) / "staging"
        self.repo.mkdir()
        self.document = document()
        self.spec = {
            "version": 1, "id": IDENTITY, "updated": "2026-11-13",
            "evidence_cutoff": "2026-11-12", "ko": "editorials/ko.html", "en": "editorials/en.html",
        }

    def register(self) -> None:
        registry = self.repo / "publication/briefings"
        registry.mkdir(parents=True, exist_ok=True)
        (registry / f"{IDENTITY}.json").write_text(json.dumps(self.spec), encoding="utf-8")
        for language in ("ko", "en"):
            source = self.repo / f"editorials/{language}.html"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text('<p>본문 <strong>관측량</strong> <a href="reviews/existing/">기존 글</a> <a href="#ref-one">[1]</a></p><h2 id="ref-one">출처</h2><p><a href="https://arxiv.org/abs/2611.14214v1">원문</a></p>', encoding="utf-8")

    def stage(self) -> dict:
        return briefing_editorials.stage_editorials(self.repo, self.staging, [self.document], BASE_URL, lambda text, prefix: text)

    def test_unregistered_editorial_preserves_pdf_only_behavior(self) -> None:
        original = copy.deepcopy(self.document)
        self.assertEqual(self.stage(), {})
        self.assertEqual(self.document, original)
        self.assertFalse(self.staging.exists())
        (self.repo / "editorials").mkdir()
        (self.repo / "editorials/unregistered.html").write_text("<script>unreviewed()</script>")
        self.assertEqual(self.stage(), {})

    def test_registered_bilingual_pages_retain_pdf_and_separate_all_dates(self) -> None:
        self.register()
        pdf = self.staging / self.document["href"]
        pdf.parent.mkdir(parents=True)
        pdf.write_bytes(b"original registered PDF")
        original_digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
        prefixes = []
        assets = briefing_editorials.stage_editorials(
            self.repo, self.staging, [self.document], BASE_URL,
            lambda text, prefix: prefixes.append(prefix) or text,
        )
        self.assertEqual(prefixes, ["../../", "../../../"])
        self.assertEqual(set(assets), {"briefings/2026-11-12/index.html", "briefings/2026-11-12/en/index.html"})
        self.assertEqual(assets, self.document["editorial_assets"])
        self.assertEqual(self.document["editorial_updated"], "2026-11-13")
        self.assertEqual(hashlib.sha256(pdf.read_bytes()).hexdigest(), original_digest)
        for language, prefix in (("ko", "../../"), ("en", "../../../")):
            relative = self.document["editorial_en_href" if language == "en" else "editorial_href"]
            content = (self.staging / relative).read_text(encoding="utf-8")
            self.assertEqual(hashlib.sha256(content.encode()).hexdigest(), assets[relative])
            self.assertIn(self.document["title_en" if language == "en" else "title"], content)
            self.assertIn(self.document["summary_en" if language == "en" else "summary"], content)
            self.assertIn(f'href="{prefix}reviews/existing/"', content)
            self.assertIn(f'href="{prefix}methods/"', content)
            self.assertIn(f'href="{prefix}{self.document["href"]}"', content)
            self.assertIn('datetime="2026-11-13"', content)
            self.assertIn('datetime="2026-11-12"', content)
            self.assertIn("AI", content)
            self.assertNotIn("editorials/ko.html", content)
            self.assertNotIn(str(self.repo), content)
            other = self.document["editorial_href" if language == "en" else "editorial_en_href"]
            self.assertIn(f'href="{prefix}{other}"', content)

    def test_unknown_or_nonbriefing_registry_cannot_publish(self) -> None:
        self.register()
        original = copy.deepcopy(self.document)
        self.spec["id"] = "2026-11-12-unknown"
        (self.repo / "publication/briefings" / f"{IDENTITY}.json").write_text(json.dumps(self.spec))
        with self.assertRaises(ValueError):
            self.stage()
        self.assertEqual(self.document, original)
        self.assertFalse(self.staging.exists())
        self.spec["id"] = IDENTITY
        self.register()
        self.document["series"] = "article"
        with self.assertRaises(ValueError):
            self.stage()

    def test_multiple_registered_editorials_keep_their_own_update_dates(self) -> None:
        self.register()
        earlier = document()
        earlier.update(id="2026-11-11-daily-quantum-brief", date="2026-11-11", href="archive/files/2026-11-11-daily-quantum-brief.pdf")
        spec = {**self.spec, "id": earlier["id"], "updated": "2026-11-12"}
        (self.repo / "publication/briefings" / f"{earlier['id']}.json").write_text(json.dumps(spec))
        assets = briefing_editorials.stage_editorials(self.repo, self.staging, [self.document, earlier], BASE_URL, lambda text, prefix: text)
        self.assertEqual(len(assets), 4)
        self.assertEqual(earlier["editorial_updated"], "2026-11-12")
        self.assertEqual(self.document["editorial_updated"], "2026-11-13")

    def test_registry_requires_complete_dates_and_both_manuscripts(self) -> None:
        for field, value in (("version", True), ("updated", "2026-11-11"), ("updated", "2026-02-30"),
                             ("evidence_cutoff", "2026-11-14"), ("ko", "missing.html")):
            with self.subTest(field=field, value=value):
                spec = copy.deepcopy(self.spec)
                self.spec[field] = value
                self.register()
                with self.assertRaises(ValueError):
                    self.stage()
                self.spec = spec
        self.register()
        self.document["date"] = "2026-11-11"
        with self.assertRaises(ValueError):
            self.stage()
        self.document["date"] = "2026-11-12"
        (self.repo / "editorials/en.html").unlink()
        with self.assertRaises(ValueError):
            self.stage()

    def test_absolute_private_parent_and_symlink_sources_are_rejected(self) -> None:
        for value in ("/tmp/source.html", "../source.html", "private/source.html", "editorials/../ko.html", "https://example.org/source.html"):
            with self.subTest(value=value):
                self.spec["ko"] = value
                self.register()
                with self.assertRaises(ValueError):
                    self.stage()
        self.spec["ko"] = "editorials/ko.html"
        self.register()
        source = self.repo / self.spec["ko"]
        source.unlink()
        source.symlink_to(self.repo / "editorials/en.html")
        with self.assertRaises(ValueError):
            self.stage()

    def test_active_private_or_malformed_fragments_are_rejected(self) -> None:
        unsafe = (
            '<p onclick="run()">text</p>', '<script>alert(1)</script><p>text</p>',
            '<p style="color:red">text</p>', '<iframe src="https://example.org"></iframe>',
            '<p><a href="javascript:alert(1)">link</a></p>',
            '<p><a href="&#106;avascript:alert(1)">link</a></p>',
            '<p><a href="//example.org/">link</a></p>', '<p><a href="http://example.org/">link</a></p>',
            '<p><a href="https://127.0.0.1/">link</a></p>',
            '<p><a href="https://127.1/">link</a></p>',
            '<p><a href="https://example.org/?access_token=secret">link</a></p>',
            '<p><a href="../private/research.html">link</a></p>',
            '<p><a href="reviews/%2e%2e/private/file.html">link</a></p>',
            '<p>/Users/person/private/research.md</p>', '<p>PRIVATE_MAIL_ID</p>',
            '<p>private@example.org</p>', '<!-- internal memo --><p>text</p>',
            '<p><strong>unbalanced</p>', '<p id="ref" id="other">text</p>',
        )
        for fragment in unsafe:
            with self.subTest(fragment=fragment):
                with self.assertRaises(ValueError):
                    briefing_editorials.validate_fragment(fragment)

    def test_allowed_fragment_preserves_science_links_and_escapes_text(self) -> None:
        fragment = '<h2 id="references">Sources</h2><p class="note">A &amp; B<br><em>phase</em> <code>E &lt; 0</code> <span>text</span> <a href="#references">[1]</a></p><ol><li><a href="https://arxiv.org/abs/2611.14214v1">Paper</a></li></ol><ul><li>Point</li></ul>'
        self.assertIn('href="https://arxiv.org/abs/2611.14214v1"', briefing_editorials.validate_fragment(fragment))
        self.assertIn("E &lt; 0", briefing_editorials.validate_fragment(fragment))
        self.assertEqual(briefing_editorials.validate_fragment("<p>Private quantum queries are a research topic.</p>"), "<p>Private quantum queries are a research topic.</p>")

    def test_public_payload_and_all_reading_surfaces_use_language_specific_page(self) -> None:
        self.register()
        self.stage()
        selected = briefing_site.briefing_documents([self.document], "../")[0]
        self.assertEqual(selected["editorial_href"], "../briefings/2026-11-12/index.html")
        self.assertEqual(selected["editorial_en_href"], "../briefings/2026-11-12/en/index.html")
        self.assertNotIn("editorial_assets", selected)
        for language in ("ko", "en"):
            reading = self.document["editorial_en_href" if language == "en" else "editorial_href"]
            self.assertIn(f'href="{reading}"', briefing_site.render_calendar([self.document], "2026-11", language))
            detail = briefing_site.render_detail([self.document], language)
            self.assertIn(f'href="{reading}"', detail)
            self.assertIn(f'href="{self.document["href"]}"', detail)
            self.assertIn("download", detail)
            listing = briefing_site.render_briefings([self.document], BASE_URL, language)
            prefix = "../../" if language == "en" else "../"
            self.assertIn(f'href="{prefix}{reading}"', listing)
            self.assertIn(f'href="{prefix}{self.document["href"]}" download', listing)
            self.assertNotIn("editorial_assets", listing)

    def test_web_reading_stays_in_current_tab_while_pdf_actions_keep_their_behavior(self) -> None:
        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.anchors = []

            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    self.anchors.append(dict(attrs))

        self.register()
        self.stage()
        for language in ("ko", "en"):
            reading = self.document["editorial_en_href" if language == "en" else "editorial_href"]
            surfaces = [briefing_site.render_calendar([self.document], "2026-11", language),
                        briefing_site.render_detail([self.document], language),
                        briefing_site.render_briefings([self.document], BASE_URL, language)]
            for markup in surfaces:
                parser = Links()
                parser.feed(markup)
                web = [anchor for anchor in parser.anchors if anchor.get("href", "").endswith(reading)]
                self.assertTrue(web)
                self.assertTrue(all("target" not in anchor for anchor in web))
                pdf = [anchor for anchor in parser.anchors if anchor.get("href", "").endswith(self.document["href"])]
                self.assertTrue(all(anchor.get("target") == "_blank" for anchor in pdf if "download" not in anchor))
            parser = Links()
            parser.feed(briefing_site.render_briefings([document()], BASE_URL, language))
            legacy = [anchor for anchor in parser.anchors if anchor.get("href", "").endswith(self.document["href"])]
            self.assertTrue(any("download" in anchor for anchor in legacy))
            self.assertTrue(all(anchor.get("target") == "_blank" for anchor in legacy if "download" not in anchor))

    def test_output_allowlist_accepts_only_registered_pages_with_matching_hashes(self) -> None:
        self.register()
        self.stage()
        for language in ("ko", "en"):
            target = self.staging / "briefings" / ("en/index.html" if language == "en" else "index.html")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(briefing_site.render_briefings([self.document], BASE_URL, language), encoding="utf-8")
        (self.staging / "assets").mkdir()
        for name in ("briefings.css", "briefings.js"):
            shutil.copyfile(Path(briefing_site.__file__).parent / "assets" / name, self.staging / "assets" / name)
        self.assertEqual(briefing_site.validate_briefings(self.staging, [self.document]), [])
        page = self.staging / self.document["editorial_href"]
        page.write_text(page.read_text() + "tamper", encoding="utf-8")
        self.assertTrue(any("missing or changed" in error for error in briefing_site.validate_briefings(self.staging, [self.document])))
        (self.staging / "briefings/unregistered.html").write_text("unregistered")
        self.assertIn("briefing output differs from allowlist", briefing_site.validate_briefings(self.staging, [self.document]))

    def test_snapshot_and_reader_updates_keep_archive_identity_and_track_both_web_editions(self) -> None:
        from scripts.publication_snapshot import capture_site
        from scripts.reader_engagement_publish import build_updates

        self.register()
        pdf = self.staging / self.document["href"]
        pdf.parent.mkdir(parents=True)
        pdf.write_bytes(b"preserved registered PDF")
        self.document["sha256"] = hashlib.sha256(pdf.read_bytes()).hexdigest()
        (self.staging / "manifest.json").write_text("[]")
        catalog = self.staging / "archive-manifest.json"
        catalog.write_text(json.dumps({"documents": [self.document], "external_resources": []}))
        snapshot_before = capture_site(self.staging)
        updates_before = build_updates(self.staging)
        self.stage()
        catalog.write_text(json.dumps({"documents": [self.document], "external_resources": []}))
        snapshot_after = capture_site(self.staging)
        updates_after = build_updates(self.staging, updates_before)
        before, after = updates_before["articles"][0], updates_after["articles"][0]
        for key in ("id", "path", "publishedAt"):
            self.assertEqual(after[key], before[key])
        self.assertEqual(after["id"], "archive:" + IDENTITY)
        self.assertEqual(set(after["paths"]) - set(before["paths"]), {
            "/AI_Tech_Review/briefings/2026-11-12/", "/AI_Tech_Review/briefings/2026-11-12/en/",
        })
        self.assertNotEqual(after["revision"], before["revision"])
        self.assertEqual(snapshot_after["declared_hash_mismatches"], [])
        self.assertEqual(set(snapshot_after["archive"][IDENTITY]["references"]) - set(snapshot_before["archive"][IDENTITY]["references"]), set(self.document["editorial_assets"]))
        self.assertEqual(hashlib.sha256(pdf.read_bytes()).hexdigest(), self.document["sha256"])
        english = self.staging / self.document["editorial_en_href"]
        english.write_text(english.read_text().replace("본문", "Revised English body"), encoding="utf-8")
        self.assertNotEqual(build_updates(self.staging, updates_after)["articles"][0]["revision"], after["revision"])


if __name__ == "__main__":
    unittest.main()
