from __future__ import annotations

from contextlib import ExitStack, redirect_stdout
import hashlib
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import publish_public_site as publisher
from scripts.document_archive_site import publish_archive, validate_archive


PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
BASE_URL = "https://infant83.github.io/AI_Tech_Review/"
METRICS_ENDPOINT = "https://published-metrics.example.com"
BEACON_TOKEN = "published-public-token"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"a", "link"}:
            self.links.append(dict(attrs))


def archive_document(document_id: str = "2026-10-16-quantum-review") -> dict:
    return {
        "id": document_id,
        "date": document_id[:10],
        "series": "daily-quantum",
        "title": '양자 <b>연구</b> & "리뷰"',
        "title_en": 'Quantum <b>research</b> & "review"',
        "summary": "연구 결과 <script>alert(1)</script>에 관한 설명입니다.",
        "summary_en": "A summary of <script>alert(1)</script> research.",
        "language": "ko",
        "file": f"files/{document_id}.pdf",
        "tags": ['Quantum & "science"'],
        "source_title": "Daily Quantum Brief",
        "public_reviewed": True,
    }


class DocumentArchiveSiteTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.archive = self.root / "archive"
        self.site = self.root / "site"
        (self.archive / "files").mkdir(parents=True)
        (self.site / "assets").mkdir(parents=True)

    def registry(self, documents: list[dict]) -> None:
        for document in documents:
            (self.archive / document["file"]).write_bytes(PDF_BYTES)
        (self.archive / "manifest.json").write_text(
            json.dumps({"version": 1, "documents": documents}, ensure_ascii=False),
            encoding="utf-8",
        )

    def publish(self) -> list[dict]:
        return publish_archive(self.archive, self.site, BASE_URL, lambda text, prefix: text)

    def test_publication_copies_only_registered_files_and_escapes_display_text(self) -> None:
        document = archive_document()
        self.registry([document])
        (self.archive / "files" / "private-unlisted.pdf").write_bytes(b"private unregistered PDF")
        (self.archive / "intake.json").write_text('{"mail_id":"private"}', encoding="utf-8")

        published = self.publish()

        expected = {"index.html", "en/index.html", f"files/{document['id']}.pdf"}
        actual = {
            path.relative_to(self.site / "archive").as_posix()
            for path in (self.site / "archive").rglob("*")
            if path.is_file()
        }
        self.assertEqual(actual, expected)
        self.assertEqual(len(published), 1)
        self.assertNotIn("file", published[0])
        self.assertNotIn("public_reviewed", published[0])
        serialized = (self.site / "archive-manifest.json").read_text(encoding="utf-8")
        self.assertNotIn("private", serialized)
        self.assertNotIn(str(self.root), serialized)
        for language, relative in (("ko", "index.html"), ("en", "en/index.html")):
            with self.subTest(language=language):
                page = (self.site / "archive" / relative).read_text(encoding="utf-8")
                self.assertNotIn("<b>", page)
                self.assertNotIn("<script>alert(1)</script>", page)
                self.assertIn("&lt;b&gt;", page)
                self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
                self.assertIn("&amp;", page)
                self.assertIn("&quot;", page)
                self.assertIn(f'<html lang="{language}">', page)
        self.assertEqual(validate_archive(self.site), [])

    def test_bilingual_catalog_metadata_and_direct_pdf_links_resolve(self) -> None:
        translated = archive_document()
        untranslated = archive_document("2026-10-09-weekly-review")
        untranslated.update(series="weekly-review", title="주간 연구 리뷰", summary="주간 연구 결과를 정리합니다.")
        del untranslated["title_en"]
        del untranslated["summary_en"]
        self.registry([untranslated, translated])
        published = self.publish()

        self.assertEqual(published[0]["href"], f"archive/files/{translated['id']}.pdf")
        for language, relative in (("ko", "index.html"), ("en", "en/index.html")):
            with self.subTest(language=language):
                page_path = self.site / "archive" / relative
                page = page_path.read_text(encoding="utf-8")
                parser = LinkParser()
                parser.feed(page)
                canonical = next(link["href"] for link in parser.links if link.get("rel") == "canonical")
                self.assertEqual(canonical, BASE_URL + "archive/" + ("en/" if language == "en" else ""))
                alternates = {link.get("hreflang"): link["href"] for link in parser.links if link.get("rel") == "alternate"}
                self.assertEqual(alternates, {"ko": BASE_URL + "archive/", "en": BASE_URL + "archive/en/", "x-default": BASE_URL + "archive/"})
                pdf_links = [link for link in parser.links if str(link.get("href", "")).endswith(".pdf")]
                self.assertEqual(len(pdf_links), 6)
                self.assertEqual(sum("download" in link for link in pdf_links), 2)
                for link in pdf_links:
                    target = (page_path.parent / str(link["href"])).resolve()
                    self.assertTrue(target.is_relative_to(self.site))
                    self.assertEqual(target.read_bytes(), PDF_BYTES)
        english = (self.site / "archive/en/index.html").read_text(encoding="utf-8")
        self.assertIn('<h2 lang="en">', english)
        self.assertIn('<h2 lang="ko">', english)
        self.assertIn("Korean PDF", english)

    def test_manifest_hashes_and_output_are_stable_across_identical_builds(self) -> None:
        self.registry([archive_document("2026-10-09-weekly-review"), archive_document()])
        first = self.publish()
        before = {
            path.relative_to(self.site).as_posix(): path.read_bytes()
            for path in self.site.rglob("*")
            if path.is_file()
        }

        second = self.publish()

        after = {
            path.relative_to(self.site).as_posix(): path.read_bytes()
            for path in self.site.rglob("*")
            if path.is_file()
        }
        self.assertEqual(second, first)
        self.assertEqual(after, before)
        for document in second:
            payload = (self.site / document["href"]).read_bytes()
            self.assertEqual(document["sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(document["size_bytes"], len(payload))

    def test_rebuild_removes_stale_generated_documents_and_unlisted_files(self) -> None:
        older = archive_document("2026-10-09-weekly-review")
        current = archive_document()
        self.registry([older, current])
        self.publish()
        (self.site / "archive/files/unlisted.pdf").write_bytes(PDF_BYTES)
        (self.site / "archive/obsolete").mkdir()
        (self.site / "archive/obsolete/internal.txt").write_text("old private output", encoding="utf-8")
        self.registry([current])

        self.publish()

        self.assertFalse((self.site / f"archive/files/{older['id']}.pdf").exists())
        self.assertFalse((self.site / "archive/files/unlisted.pdf").exists())
        self.assertFalse((self.site / "archive/obsolete").exists())
        self.assertEqual(validate_archive(self.site), [])

    def test_checksum_validator_detects_same_size_pdf_corruption(self) -> None:
        self.registry([archive_document()])
        published = self.publish()
        path = self.site / published[0]["href"]
        path.write_bytes(PDF_BYTES.replace(b"Catalog", b"Corrupt"))

        errors = validate_archive(self.site)

        self.assertTrue(any("checksum mismatch" in error for error in errors), errors)

    def test_failed_page_render_does_not_replace_existing_archive(self) -> None:
        self.registry([archive_document()])
        self.publish()
        before = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in self.site.rglob("*") if path.is_file()}

        with self.assertRaisesRegex(RuntimeError, "render failed"):
            publish_archive(self.archive, self.site, BASE_URL, lambda text, prefix: (_ for _ in ()).throw(RuntimeError("render failed")))

        after = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in self.site.rglob("*") if path.is_file()}
        self.assertEqual(after, before)

    def published_index(self) -> str:
        return (
            '<!doctype html><html><head></head><body>'
            '<script>window.AI_TECH_REVIEW_METRICS='
            + json.dumps({"endpoint": METRICS_ENDPOINT, "siteId": "ai-tech-review", "basePath": "/AI_Tech_Review/"})
            + ';</script><script data-cf-beacon=\'{&quot;token&quot;:&quot;'
            + BEACON_TOKEN
            + '&quot;}\'></script></body></html>'
        )

    def publisher_paths(self) -> ExitStack:
        stack = ExitStack()
        for name, value in (("ROOT", self.root), ("SITE_DIR", self.site), ("REVIEWS_DIR", self.site / "reviews"), ("ASSETS_DIR", self.site / "assets")):
            stack.enter_context(patch.object(publisher, name, value))
        return stack

    def test_hub_only_preserves_36_review_trees_and_restores_existing_analytics(self) -> None:
        self.registry([archive_document()])
        reviews = []
        for number in range(36):
            folder = f"2026-10-16-review-{number:02d}"
            review_dir = self.site / "reviews" / folder
            (review_dir / "en").mkdir(parents=True)
            (review_dir / "index.html").write_bytes(f"Korean review {number}".encode())
            (review_dir / "en/index.html").write_bytes(f"English review {number}".encode())
            (review_dir / "figure.svg").write_bytes(f"<svg>{number}</svg>".encode())
            reviews.append({
                "folder": folder, "title": f"Review {number}", "subtitle": "Review subtitle",
                "summary": "Review summary", "date": "2026-10-16", "updated": "2026-10-16",
                "category": "Quantum Computing", "tags": ["Quantum"], "thumbnail": "",
                "href": f"reviews/{folder}/index.html", "metric_path": f"/AI_Tech_Review/reviews/{folder}/",
                "assets": ["figure.svg"], "translations": [{"language": "en", "label": "English", "href": f"reviews/{folder}/en/index.html"}],
            })
        manifest_path = self.site / "manifest.json"
        manifest_path.write_text(json.dumps(reviews, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (self.site / "index.html").write_text(self.published_index(), encoding="utf-8")
        before = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in (self.site / "reviews").rglob("*") if path.is_file()}
        manifest_before = manifest_path.read_bytes()

        with self.publisher_paths(), patch.dict(os.environ, {}, clear=True), ExitStack() as stack:
            publish_review = stack.enter_context(patch.object(publisher, "publish_review", side_effect=AssertionError("review mutation")))
            preserve_review = stack.enter_context(patch.object(publisher, "preserve_published_review", side_effect=AssertionError("review mutation")))
            stack.enter_context(patch.object(publisher, "copy_icon_assets"))
            validate = stack.enter_context(patch.object(publisher, "validate_public_site", return_value=[]))
            with redirect_stdout(io.StringIO()):
                result = publisher.main(["--hub-only"])
            self.assertEqual(os.environ[publisher.PUBLIC_METRICS_ENDPOINT_ENV], METRICS_ENDPOINT)
            self.assertEqual(os.environ[publisher.CLOUDFLARE_WEB_ANALYTICS_TOKEN_ENV], BEACON_TOKEN)

        self.assertEqual(result, 0)
        publish_review.assert_not_called()
        preserve_review.assert_not_called()
        self.assertEqual(validate.call_args.args[0], reviews)
        self.assertEqual(manifest_path.read_bytes(), manifest_before)
        after = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in (self.site / "reviews").rglob("*") if path.is_file()}
        self.assertEqual(after, before)
        for relative, asset_prefix in (("index.html", ""), ("archive/index.html", "../"), ("archive/en/index.html", "../../")):
            with self.subTest(page=relative):
                page = (self.site / relative).read_text(encoding="utf-8")
                self.assertEqual(page.count("window.AI_TECH_REVIEW_METRICS="), 1)
                self.assertEqual(page.count("data-cf-beacon="), 1)
                self.assertIn(METRICS_ENDPOINT, page)
                self.assertIn(BEACON_TOKEN, page)
                self.assertIn(f'src="{asset_prefix}assets/public-metrics.js"', page)
        self.assertEqual(validate_archive(self.site), [])

    def test_analytics_restore_respects_explicit_current_and_legacy_configuration(self) -> None:
        (self.site / "index.html").write_text(self.published_index(), encoding="utf-8")
        for endpoint_key in (publisher.PUBLIC_METRICS_ENDPOINT_ENV, publisher.LEGACY_PUBLIC_METRICS_ENDPOINT_ENV):
            with self.subTest(endpoint_key=endpoint_key):
                explicit = {endpoint_key: "https://configured-metrics.example.com", publisher.CLOUDFLARE_WEB_ANALYTICS_TOKEN_ENV: "configured-beacon"}
                with self.publisher_paths(), patch.dict(os.environ, explicit, clear=True):
                    publisher.restore_published_analytics()
                    self.assertEqual(publisher.public_metrics_endpoint(), explicit[endpoint_key])
                    self.assertEqual(os.environ[publisher.CLOUDFLARE_WEB_ANALYTICS_TOKEN_ENV], "configured-beacon")
                    if endpoint_key == publisher.LEGACY_PUBLIC_METRICS_ENDPOINT_ENV:
                        self.assertNotIn(publisher.PUBLIC_METRICS_ENDPOINT_ENV, os.environ)


if __name__ == "__main__":
    unittest.main()
