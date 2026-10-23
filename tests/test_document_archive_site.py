from __future__ import annotations

from contextlib import ExitStack, redirect_stdout
import hashlib
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from scripts import publish_public_site as publisher
from scripts import document_archive_site as archive_site
from scripts.document_archive_site import publish_archive, validate_archive


PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
BASE_URL = "https://infant83.github.io/AI_Tech_Review/"
METRICS_ENDPOINT = "https://published-metrics.example.com"
BEACON_TOKEN = "published-public-token"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str | None]] = []
        self.metadata: dict[str, str | None] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"a", "link"}:
            self.links.append(dict(attrs))
        elif tag == "meta":
            values = dict(attrs)
            key = values.get("property") or values.get("name")
            if key:
                self.metadata[key] = values.get("content")


class NavigationParser(LinkParser):
    """Retain visible link labels without depending on a card's CSS layout."""

    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[dict] = []
        self._anchor: dict | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        super().handle_starttag(tag, attrs)
        if tag == "a":
            self._anchor = {**dict(attrs), "text": ""}
            self.anchors.append(self._anchor)

    def handle_data(self, data: str) -> None:
        if self._anchor is not None:
            self._anchor["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._anchor is not None:
            self._anchor["text"] = " ".join(self._anchor["text"].split())
            self._anchor = None


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

    def test_external_book_links_are_searchable_bilingual_and_never_publish_private_pdf(self) -> None:
        from test_external_resources import resource
        document = archive_document()
        self.registry([document])
        item = resource()
        item["title"] = 'Quantum Algorithms <First Principles> & "Derivations"'
        (self.archive / "external-resources.json").write_text(json.dumps({"version": 1, "resources": [item]}), encoding="utf-8")
        (self.archive / "private").mkdir()
        private_payload = b"%PDF-1.7\nprivate copyrighted book contents"
        (self.archive / "private/book.pdf").write_bytes(private_payload)

        published = self.publish()

        self.assertEqual(len(published), 1)
        self.assertEqual((self.site / published[0]["href"]).read_bytes(), PDF_BYTES)
        manifest = json.loads((self.site / "archive-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["documents"], published)
        self.assertEqual(manifest["external_resources"], [{key: value for key, value in item.items() if key != "public_reviewed"}])
        for relative in ("index.html", "en/index.html"):
            page = (self.site / "archive" / relative).read_text(encoding="utf-8")
            start = page.index(f'<article id="{item["id"]}"')
            card = page[start:page.index("</article>", start)]
            parser = LinkParser()
            parser.feed(card)
            self.assertEqual({link["href"] for link in parser.links}, {item["author_url"], item["book_url"]})
            self.assertFalse(any("download" in link for link in parser.links))
            self.assertIn('data-series="external-book"', card)
            self.assertIn("Muhammad Faryad", card)
            self.assertIn("&lt;First Principles&gt; &amp; &quot;Derivations&quot;", card)
            self.assertIn('<h2 lang="en">', card)
            self.assertNotIn(f"files/{item['id']}.pdf", page)
        for path in self.site.rglob("*"):
            if path.is_file():
                self.assertNotIn(private_payload, path.read_bytes())
        self.assertEqual(validate_archive(self.site), [])
        english = self.site / "archive/en/index.html"
        english.write_text(english.read_text(encoding="utf-8").replace(item["author_url"] + '"', 'https://example.com/"'), encoding="utf-8")
        self.assertTrue(any("external book link absent" in error for error in validate_archive(self.site)))

    def test_invalid_external_registry_does_not_replace_published_archive(self) -> None:
        from test_external_resources import resource
        self.registry([archive_document()])
        self.publish()
        before = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in self.site.rglob("*") if path.is_file()}
        item = resource()
        item["book_url"] += "?token=private"
        (self.archive / "external-resources.json").write_text(json.dumps({"version": 1, "resources": [item]}), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "HTTPS"):
            self.publish()

        self.assertEqual({path.relative_to(self.site).as_posix(): path.read_bytes() for path in self.site.rglob("*") if path.is_file()}, before)

    def test_failed_page_render_does_not_replace_existing_archive(self) -> None:
        self.registry([archive_document()])
        self.publish()
        before = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in self.site.rglob("*") if path.is_file()}

        with self.assertRaisesRegex(RuntimeError, "render failed"):
            publish_archive(self.archive, self.site, BASE_URL, lambda text, prefix: (_ for _ in ()).throw(RuntimeError("render failed")))

        after = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in self.site.rglob("*") if path.is_file()}
        self.assertEqual(after, before)

    def lecture_fixture(self) -> tuple[dict, dict, Path]:
        document = archive_document("2026-10-20-quantum-machine-learning-lecture-notes-ko")
        document.update(series="lecture-notes", title="양자 머신러닝 자율학습", title_en="Quantum machine learning self-study")
        source = self.root / "src" / "dist"
        (source / "labs").mkdir(parents=True)
        (source / "index.html").write_text(
            '<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            '<title>양자 머신러닝 자율학습</title><link rel="stylesheet" href="notes.css">'
            '</head><body><aside class="sidebar"><div class="brand">QUANTUM MACHINE LEARNING</div>'
            '<h2>양자 머신러닝 자율학습</h2></aside><main class="workspace"><h1>양자 머신러닝 자율학습</h1>'
            '<section id="doc-study-guide"><h2>학습 안내</h2></section>'
            '<a href="notes.pdf">통합 PDF</a><a href="labs/demo.py">실습 코드</a>'
            '</main></body></html>',
            encoding="utf-8",
        )
        (source / "notes.css").write_text("main { max-width: 70ch; }\n", encoding="utf-8")
        (source / "notes.pdf").write_bytes(PDF_BYTES)
        (source / "labs/demo.py").write_text('print("educational lab")\n', encoding="utf-8")
        bundle = {
            document["id"]: {
                "source": str(source),
                "href": "lectures/quantum-machine-learning/",
                "files": ("index.html", "notes.css", "notes.pdf", "labs/demo.py"),
            }
        }
        return document, bundle, source

    def test_lecture_publication_copies_reviewed_allowlist_and_adds_public_navigation(self) -> None:
        document, bundles, source = self.lecture_fixture()
        self.registry([document])
        (source / "private-intake.json").write_text('{"private": "intake"}', encoding="utf-8")
        (source / "labs/private.env").write_text("PRIVATE_EXAMPLE=do-not-publish\n", encoding="utf-8")

        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            published = self.publish()
            self.assertEqual(validate_archive(self.site), [])

        lecture_dir = self.site / "lectures/quantum-machine-learning"
        self.assertEqual(
            {path.relative_to(lecture_dir).as_posix() for path in lecture_dir.rglob("*") if path.is_file()},
            set(bundles[document["id"]]["files"]),
        )
        self.assertEqual((lecture_dir / "notes.pdf").read_bytes(), PDF_BYTES)
        self.assertEqual((lecture_dir / "labs/demo.py").read_bytes(), (source / "labs/demo.py").read_bytes())
        self.assertEqual(published[0]["study_href"], "lectures/quantum-machine-learning/")
        self.assertEqual(set(published[0]["study_assets"]), set(bundles[document["id"]]["files"]))
        for relative, digest in published[0]["study_assets"].items():
            self.assertEqual(hashlib.sha256((lecture_dir / relative).read_bytes()).hexdigest(), digest)
        serialized = (self.site / "archive-manifest.json").read_text(encoding="utf-8")
        self.assertNotIn(str(self.root), serialized)
        self.assertNotIn('"source":', serialized)
        self.assertNotIn("private-intake", serialized)

        study_page = (lecture_dir / "index.html").read_text(encoding="utf-8")
        links = LinkParser()
        links.feed(study_page)
        canonical = [link["href"] for link in links.links if link.get("rel") == "canonical"]
        self.assertEqual(canonical, [BASE_URL + "lectures/quantum-machine-learning/"])
        self.assertEqual(links.metadata.get("og:url"), canonical[0])
        self.assertEqual(links.metadata.get("og:title"), document["title"])
        self.assertIn(links.metadata.get("og:type"), {"article", "website"})
        return_links = [link for link in links.links if str(link.get("href", "")).rstrip("/") in {
            BASE_URL.rstrip("/"), "../..", "../../index.html", "../../lectures"
        }]
        self.assertTrue(return_links, "Lecture page needs a link back to the Tech Review hub or lecture catalog")
        self.assertIn('href="../../lectures/"', study_page)
        self.assertNotIn('href="../../archive/?series=lecture-notes"', study_page)

        for relative, study_href, study_label in (
            ("index.html", "../lectures/quantum-machine-learning/", "강의 노트 읽기"),
            ("en/index.html", "../../lectures/quantum-machine-learning/", "Korean study notes"),
        ):
            with self.subTest(catalog=relative):
                page_path = self.site / "archive" / relative
                page = page_path.read_text(encoding="utf-8")
                parser = LinkParser()
                parser.feed(page)
                study_links = [link for link in parser.links if link.get("href") == study_href]
                self.assertEqual(len(study_links), 2, "Title and explicit study action should open the HTML notes")
                self.assertTrue((page_path.parent / study_href / "index.html").resolve().is_file())
                self.assertIn(study_label, page)
                pdf_links = [link for link in parser.links if str(link.get("href", "")).endswith(".pdf")]
                self.assertEqual(len(pdf_links), 2, "PDF open and download should remain available")
                self.assertEqual(sum("download" in link for link in pdf_links), 1)

    def test_unregistered_lecture_bundle_is_not_published_or_required(self) -> None:
        document, bundles, source = self.lecture_fixture()
        self.registry([archive_document()])
        bundles[document["id"]]["source"] = str(source / "not-present")

        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            published = self.publish()
            self.assertEqual(validate_archive(self.site), [])

        self.assertTrue(all("study_href" not in document for document in published))
        self.assertFalse((self.site / "lectures/quantum-machine-learning").exists())

    def classiq_fixture(self) -> tuple[dict, dict, Path]:
        document = archive_document("2026-10-22-classiq-talk-series-notes-ko")
        document.update(series="lecture-notes", title="Classiq 최근 토크시리즈 상세 학습 노트",
                        title_en="Classiq replay study notes", summary="네 회의 다시보기와 질문·그림 해설.")
        spec = dict(archive_site.LECTURE_BUNDLES[document["id"]])
        source = self.root / "classiq" / "dist"
        for name in spec["files"]:
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(PDF_BYTES if name == "notes.pdf" else f"Reviewed public asset: {name}".encode())
        (source / "index.html").write_text(
            '<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>Classiq</title></head>'
            '<body><aside class="sidebar"></aside><main>'
            + ''.join(f'<section id="chapter-{i}"><h1>Chapter {i}</h1></section>' for i in range(9))
            + '<a href="notes.pdf">PDF</a></main></body></html>', encoding="utf-8")
        spec["source"] = str(source)
        return document, {document["id"]: spec}, source

    def test_classiq_bundle_publishes_only_illustrated_allowlist_with_consistent_metadata(self) -> None:
        document, bundles, source = self.classiq_fixture()
        self.registry([document])
        (source / "research").mkdir()
        (source / "research/replay-transcript.txt").write_text("PRIVATE_TRANSCRIPT", encoding="utf-8")
        (source / "figures/screens/unreviewed.png").write_bytes(b"PRIVATE_UNREVIEWED_SCREEN")
        (source.parent / "private-intake.json").write_text("PRIVATE_MAIL_METADATA", encoding="utf-8")

        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            published = self.publish()
            self.assertEqual(validate_archive(self.site), [])

        spec = bundles[document["id"]]
        destination = self.site / spec["href"]
        actual = {path.relative_to(destination).as_posix() for path in destination.rglob("*") if path.is_file()}
        self.assertEqual(actual, set(spec["files"]))
        self.assertEqual(len(actual), 26)
        self.assertEqual(len([name for name in actual if name.startswith("figures/concepts/")]), 6)
        self.assertEqual(len([name for name in actual if name.startswith("figures/screens/")]), 13)
        page = (destination / "index.html").read_text(encoding="utf-8")
        parser = NavigationParser()
        parser.feed(page)
        canonical = [link["href"] for link in parser.links if link.get("rel") == "canonical"]
        self.assertEqual(canonical, [BASE_URL + spec["href"]])
        self.assertEqual(parser.metadata["og:url"], canonical[0])
        self.assertEqual(parser.metadata["og:title"], document["title"])
        self.assertEqual(parser.metadata["og:description"], document["summary"])
        self.assertEqual((destination / "notes.pdf").read_bytes(), (self.site / published[0]["href"]).read_bytes())
        self.assertIn("2026-10-22 · OpenAI Codex의 root", page)
        self.assertIn("publish_audit가 공개 자산과 아카이브 연결을 독립 검토", page)
        self.assertIn("독립 보충 해설과 손계산은 원발표와 구분", page)
        self.assertNotIn("2026-10-20", page)
        self.assertNotIn("doc-labs-readme", page)
        for anchor in parser.anchors:
            href = str(anchor.get("href", ""))
            if href.startswith("#"):
                self.assertIn(f'id="{href[1:]}"', page)
        public_manifest = (self.site / "archive-manifest.json").read_text(encoding="utf-8")
        for private in (str(self.root), "PRIVATE_", "research/", "unreviewed.png", "private-intake"):
            self.assertNotIn(private, public_manifest)

    def test_classiq_catalog_uses_real_chapters_and_describes_illustrated_notes(self) -> None:
        document, bundles, _source = self.classiq_fixture()
        self.registry([document])
        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            self.publish()
        for language, relative in (("ko", "index.html"), ("en", "en/index.html")):
            with self.subTest(language=language):
                path = self.site / "lectures" / relative
                page = path.read_text(encoding="utf-8")
                parser = NavigationParser()
                parser.feed(page)
                for metric in (["4 replays", "61-page PDF", "19 figures"] if language == "en" else ["다시보기 4회", "PDF 61쪽", "그림 19개"]):
                    self.assertIn(metric, page)
                primary = next(anchor for anchor in parser.anchors if "lecture-primary" in anchor.get("class", "").split())
                self.assertEqual(urlsplit(primary["href"]).fragment, "chapter-0")
                chapter_links = [anchor for anchor in parser.anchors if urlsplit(anchor.get("href", "")).fragment.startswith("chapter-")]
                self.assertEqual({urlsplit(anchor["href"]).fragment for anchor in chapter_links},
                                 {"chapter-0", "chapter-1", "chapter-2", "chapter-3", "chapter-4", "chapter-7"})
                for anchor in chapter_links:
                    url = urlsplit(anchor["href"])
                    target = (path.parent / url.path / "index.html").resolve()
                    self.assertEqual(target, self.site / "lectures/classiq-talk-series/index.html")
                    self.assertIn(f'id="{url.fragment}"', target.read_text(encoding="utf-8"))
                self.assertNotIn("doc-study-guide", page)
                self.assertNotIn("Online notes + labs" if language == "en" else "온라인 노트 · 실습", page)

    def test_missing_custom_lecture_anchor_rejects_build_before_replacing_output(self) -> None:
        self.registry([archive_document()])
        self.publish()
        before = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in self.site.rglob("*") if path.is_file()}
        document, bundles, source = self.classiq_fixture()
        self.registry([document])
        index = source / "index.html"
        index.write_text(index.read_text(encoding="utf-8").replace('id="chapter-7"', 'id="missing-chapter"'), encoding="utf-8")
        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            with self.assertRaisesRegex(ValueError, "Missing lecture navigation anchor: chapter-7"):
                self.publish()
        after = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in self.site.rglob("*") if path.is_file()}
        self.assertEqual(after, before)

    def test_lecture_pdf_mismatch_rejects_build_without_replacing_published_archive(self) -> None:
        self.registry([archive_document()])
        self.publish()
        before = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in self.site.rglob("*") if path.is_file()}
        document, bundles, source = self.lecture_fixture()
        self.registry([document])
        (source / "notes.pdf").write_bytes(PDF_BYTES + b"\n%different edition\n")

        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            with self.assertRaisesRegex(ValueError, "(?i)pdf|mismatch|differ"):
                self.publish()

        after = {path.relative_to(self.site).as_posix(): path.read_bytes() for path in self.site.rglob("*") if path.is_file()}
        self.assertEqual(after, before)

    def test_lecture_validator_rejects_extra_output_and_pdf_tampering(self) -> None:
        document, bundles, _source = self.lecture_fixture()
        self.registry([document])
        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            self.publish()
            lecture_dir = self.site / "lectures/quantum-machine-learning"
            extra = lecture_dir / "private-support.txt"
            extra.write_text("not approved for publication", encoding="utf-8")
            errors = validate_archive(self.site)
            self.assertTrue(errors, "Unlisted lecture output must fail validation")
            self.assertTrue(any("private-support.txt" in error or "allowlist" in error for error in errors), errors)
            extra.unlink()
            (lecture_dir / "notes.pdf").write_bytes(PDF_BYTES.replace(b"Catalog", b"Corrupt"))
            errors = validate_archive(self.site)
            self.assertTrue(any("pdf" in error.lower() or "checksum" in error.lower() or "mismatch" in error.lower() for error in errors), errors)

    def test_lecture_asset_hashes_detect_same_size_script_corruption(self) -> None:
        document, bundles, _source = self.lecture_fixture()
        self.registry([document])
        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            self.publish()
            script = self.site / "lectures/quantum-machine-learning/labs/demo.py"
            script.write_bytes(script.read_bytes().replace(b"educational", b"unreviewed!"))

            errors = validate_archive(self.site)

        self.assertTrue(errors, "Same-size changes to a downloadable lab must fail validation")
        self.assertTrue(any("demo.py" in error for error in errors), errors)

    def test_missing_approved_lecture_file_rejects_publication(self) -> None:
        document, bundles, source = self.lecture_fixture()
        self.registry([document])
        (source / "labs/demo.py").unlink()

        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            with self.assertRaisesRegex(ValueError, "(?i)missing|unavailable|demo.py|not.*file"):
                self.publish()

        self.assertFalse((self.site / "archive").exists())
        self.assertFalse((self.site / "lectures/quantum-machine-learning").exists())

    def test_symlink_in_approved_lecture_files_is_rejected(self) -> None:
        document, bundles, source = self.lecture_fixture()
        self.registry([document])
        outside = self.root / "private-code.py"
        outside.write_text('print("private source")\n', encoding="utf-8")
        target = source / "labs/demo.py"
        target.unlink()
        target.symlink_to(outside)

        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            with self.assertRaisesRegex(ValueError, "(?i)symlink|linked"):
                self.publish()

        self.assertFalse((self.site / "archive").exists())
        self.assertFalse((self.site / "lectures/quantum-machine-learning").exists())

    def test_library_navigation_orders_learning_before_secondary_document_storage(self) -> None:
        documents = [archive_document(), {**archive_document("2026-10-16-lecture"), "series": "lecture-notes"}]
        for language, prefix in (("ko", "../"), ("en", "../../")):
            for area in ("reviews", "lectures", "briefings", "archive"):
                with self.subTest(language=language, area=area):
                    parser = NavigationParser()
                    parser.feed(archive_site.render_library_navigation(documents, area, language, prefix))
                    anchors = parser.anchors
                    self.assertEqual(len(anchors), 4)
                    self.assertTrue(anchors[0]["text"].startswith("Review hub" if language == "en" else "리뷰허브"))
                    self.assertTrue(anchors[1]["text"].startswith("Lecture notes" if language == "en" else "렉처 노트"))
                    self.assertTrue(anchors[2]["text"].startswith("Briefings" if language == "en" else "브리핑"))
                    self.assertIn("hub-utility", anchors[3].get("class", "").split())
                    self.assertNotIn("hub-utility", anchors[0].get("class", "").split())
                    self.assertNotIn("hub-utility", anchors[1].get("class", "").split())
                    self.assertNotIn("hub-utility", anchors[2].get("class", "").split())
                    self.assertEqual(anchors[1]["href"], prefix + "lectures/" + ("en/" if language == "en" else ""))
                    self.assertEqual(anchors[2]["href"], prefix + "briefings/" + ("en/" if language == "en" else ""))
                    self.assertEqual(anchors[3]["href"], prefix + "archive/" + ("en/" if language == "en" else ""))
                    current = [anchor for anchor in anchors if anchor.get("aria-current") == "page"]
                    self.assertEqual(current, [anchors[("reviews", "lectures", "briefings", "archive").index(area)]])

    def test_lecture_landing_publication_is_bilingual_and_contains_only_learning_documents(self) -> None:
        study, bundles, _source = self.lecture_fixture()
        pdf_only = archive_document("2026-10-16-condensed-matter-lecture")
        pdf_only.update(series="lecture-notes", title="응집물질 PDF 강의", title_en="Condensed matter PDF lecture")
        review = archive_document("2026-10-15-daily-research")
        review.update(title="학습 목록에 없는 일일 리뷰", title_en="Daily review outside the learning catalog")
        self.registry([review, pdf_only, study])

        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            self.publish()
            self.assertEqual(validate_archive(self.site), [])

        for language, relative in (("ko", "index.html"), ("en", "en/index.html")):
            with self.subTest(language=language):
                page = (self.site / "lectures" / relative).read_text(encoding="utf-8")
                parser = NavigationParser()
                parser.feed(page)
                canonical = [link["href"] for link in parser.links if link.get("rel") == "canonical"]
                self.assertEqual(canonical, [BASE_URL + "lectures/" + ("en/" if language == "en" else "")])
                alternates = {link.get("hreflang"): link["href"] for link in parser.links if link.get("rel") == "alternate"}
                self.assertEqual(alternates, {"ko": BASE_URL + "lectures/", "en": BASE_URL + "lectures/en/", "x-default": BASE_URL + "lectures/"})
                self.assertIn(study["title_en" if language == "en" else "title"], page)
                self.assertIn(pdf_only["title_en" if language == "en" else "title"], page)
                self.assertNotIn(review["title"], page)
                self.assertNotIn(review["title_en"], page)
                for control in ("archive-search", "archive-month", "archive-sort", "collection-filters"):
                    self.assertNotIn(control, page, "The learning catalog must not inherit archive controls")
                current = [anchor for anchor in parser.anchors if anchor.get("aria-current") == "page"]
                self.assertEqual(len(current), 1)
                self.assertTrue(current[0]["text"].startswith("Lecture notes" if language == "en" else "렉처 노트"))
                self.assertIn("Korean" if language == "en" else "한국어", page)

    def test_lecture_actions_open_web_study_and_pdf_only_materials_without_broken_paths(self) -> None:
        study, bundles, _source = self.lecture_fixture()
        pdf_only = archive_document("2026-10-16-condensed-matter-lecture")
        pdf_only.update(series="lecture-notes", title="응집물질 PDF 강의", title_en="Condensed matter PDF lecture")
        self.registry([study, pdf_only])

        with patch.dict(archive_site.LECTURE_BUNDLES, bundles, clear=True):
            self.publish()

        for language, relative in (("ko", "index.html"), ("en", "en/index.html")):
            with self.subTest(language=language):
                page_path = self.site / "lectures" / relative
                parser = NavigationParser()
                parser.feed(page_path.read_text(encoding="utf-8"))
                start = [anchor for anchor in parser.anchors if anchor["text"].startswith("Start learning" if language == "en" else "학습 시작")]
                pdf_start = [anchor for anchor in parser.anchors if "lecture-primary" in anchor.get("class", "").split() and anchor["text"].startswith("Read PDF" if language == "en" else "PDF 읽기")]
                self.assertEqual(len(start), 1)
                self.assertEqual(len(pdf_start), 1)
                study_url = urlsplit(start[0]["href"])
                study_path = (page_path.parent / study_url.path / "index.html").resolve()
                self.assertEqual(study_path, self.site / "lectures/quantum-machine-learning/index.html")
                self.assertEqual(study_url.fragment, "doc-study-guide")
                self.assertIn(f'id="{study_url.fragment}"', study_path.read_text(encoding="utf-8"))
                self.assertEqual((page_path.parent / pdf_start[0]["href"]).resolve(), self.site / "archive" / pdf_only["file"])
                pdf_links = [anchor for anchor in parser.anchors if str(anchor.get("href", "")).endswith(".pdf")]
                self.assertGreaterEqual(len(pdf_links), 4)
                downloads = [anchor for anchor in pdf_links if "download" in anchor]
                self.assertEqual(len(downloads), 1)
                self.assertEqual((page_path.parent / downloads[0]["href"]).resolve(), self.site / "archive" / pdf_only["file"])
                for anchor in pdf_links:
                    target = (page_path.parent / anchor["href"]).resolve()
                    self.assertTrue(target.is_relative_to(self.site))
                    self.assertEqual(target.read_bytes(), PDF_BYTES)

    def test_lecture_landing_escapes_registry_content_and_handles_an_empty_catalog(self) -> None:
        document = archive_document()
        document.update(series="lecture-notes", href="archive/files/example.pdf", size_bytes=len(PDF_BYTES))
        for language in ("ko", "en"):
            with self.subTest(language=language):
                page = archive_site.render_lectures([document], BASE_URL, language)
                self.assertNotIn("<b>", page)
                self.assertNotIn("<script>alert(1)</script>", page)
                self.assertIn("&lt;b&gt;", page)
                self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)
                parser = NavigationParser()
                parser.feed(archive_site.render_lectures([], BASE_URL, language))
                self.assertEqual(sum(anchor.get("aria-current") == "page" for anchor in parser.anchors), 1)
                self.assertFalse(any(str(anchor.get("href", "")).endswith(".pdf") for anchor in parser.anchors))

    def test_briefing_landing_is_bilingual_and_lists_only_published_briefing_series(self) -> None:
        daily = archive_document("2026-10-20-daily-briefing")
        daily.update(title="양자 오류 정정 브리핑", title_en="Quantum error correction briefing")
        weekly = archive_document("2026-10-16-weekly-briefing")
        weekly.update(series="weekly-review", title="주간 양자 연구 브리핑", title_en="Weekly quantum research briefing")
        older = archive_document("2026-09-30-daily-briefing")
        older.update(title="9월 양자 네트워크 브리핑", title_en="September quantum network briefing")
        article = archive_document("2026-10-19-research-article")
        article.update(series="article", title="수시 아티클 전용 제목", title_en="An article outside the briefing catalog")
        lecture = archive_document("2026-10-18-standalone-lecture")
        lecture.update(series="lecture-notes", title="렉처 노트 전용 제목", title_en="A lecture outside the briefing catalog")
        self.registry([daily, weekly, older, article, lecture])

        self.publish()

        for language, relative in (("ko", "index.html"), ("en", "en/index.html")):
            with self.subTest(language=language):
                page_path = self.site / "briefings" / relative
                page = page_path.read_text(encoding="utf-8")
                parser = NavigationParser()
                parser.feed(page)
                canonical = [link["href"] for link in parser.links if link.get("rel") == "canonical"]
                self.assertEqual(canonical, [BASE_URL + "briefings/" + ("en/" if language == "en" else "")])
                alternates = {link.get("hreflang"): link["href"] for link in parser.links if link.get("rel") == "alternate"}
                self.assertEqual(alternates, {
                    "ko": BASE_URL + "briefings/", "en": BASE_URL + "briefings/en/", "x-default": BASE_URL + "briefings/",
                })
                self.assertIn(f'<html lang="{language}">', page)
                self.assertNotIn(article["title"], page)
                self.assertNotIn(article["title_en"], page)
                self.assertNotIn(lecture["title"], page)
                self.assertNotIn(lecture["title_en"], page)
                current = [anchor for anchor in parser.anchors if anchor.get("aria-current") == "page"]
                self.assertEqual(len(current), 1)
                self.assertTrue(current[0]["text"].startswith("Briefings" if language == "en" else "브리핑"))
                pdf_links = [anchor for anchor in parser.anchors if str(anchor.get("href", "")).endswith(".pdf")]
                targets = {(page_path.parent / anchor["href"]).resolve() for anchor in pdf_links}
                for document in (daily, weekly, older):
                    self.assertIn(self.site / "archive" / document["file"], targets, "Every registered briefing needs a readable list link even without JavaScript")
                for target in targets:
                    self.assertTrue(target.is_relative_to(self.site))
                    self.assertEqual(target.read_bytes(), PDF_BYTES)
                self.assertIn("2026-10", page)
                self.assertIn("2026-09", page)
        self.assertEqual(validate_archive(self.site), [])

    def test_briefing_landing_escapes_registry_text_and_keeps_source_fields_private(self) -> None:
        document = archive_document()
        document["source_title"] = "PRIVATE_SOURCE_METADATA_DO_NOT_RENDER"
        self.registry([document])
        (self.archive / "intake.json").write_text('{"mail_id":"PRIVATE_MAIL_ID_DO_NOT_RENDER"}', encoding="utf-8")

        self.publish()

        for relative in ("index.html", "en/index.html"):
            with self.subTest(page=relative):
                page = (self.site / "briefings" / relative).read_text(encoding="utf-8")
                self.assertNotIn("<b>", page)
                self.assertNotIn("<script>alert(1)</script>", page)
                self.assertNotIn("PRIVATE_SOURCE_METADATA_DO_NOT_RENDER", page)
                self.assertNotIn("PRIVATE_MAIL_ID_DO_NOT_RENDER", page)
                self.assertNotIn(str(self.root), page)
                self.assertIn("&lt;b&gt;", page)
                self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", page)

    def test_briefing_landing_has_useful_empty_state_when_only_other_documents_exist(self) -> None:
        article = archive_document()
        article.update(series="article", title="수시 연구 아티클", title_en="Research article")
        self.registry([article])

        self.publish()

        for relative in ("index.html", "en/index.html"):
            with self.subTest(page=relative):
                page = (self.site / "briefings" / relative).read_text(encoding="utf-8")
                parser = NavigationParser()
                parser.feed(page)
                self.assertFalse(any(str(anchor.get("href", "")).endswith(".pdf") for anchor in parser.anchors))
                self.assertEqual(sum(anchor.get("aria-current") == "page" for anchor in parser.anchors), 1)
                self.assertNotIn(article["title"], page)
                self.assertNotIn(article["title_en"], page)
                self.assertNotIn("undefined", page)
                self.assertNotIn("NaN", page)
        self.assertEqual(validate_archive(self.site), [])

    def test_briefing_validator_rejects_unlisted_output_and_mismatched_public_data(self) -> None:
        self.registry([archive_document()])
        self.publish()
        unexpected = self.site / "briefings" / "private-intake.txt"
        unexpected.write_text("private material", encoding="utf-8")

        errors = validate_archive(self.site)

        self.assertTrue(any("briefing" in error and "allowlist" in error for error in errors), errors)
        unexpected.unlink()
        page_path = self.site / "briefings" / "index.html"
        original = page_path.read_text(encoding="utf-8")
        start = original.index('<script type="application/json" id="briefing-data">') + len('<script type="application/json" id="briefing-data">')
        end = original.index("</script>", start)
        payload = json.loads(original[start:end])
        payload["documents"] = []
        page_path.write_text(original[:start] + json.dumps(payload) + original[end:], encoding="utf-8")

        errors = validate_archive(self.site)

        self.assertTrue(any("briefing" in error and "registry" in error for error in errors), errors)

    def test_briefing_validator_reports_missing_language_page(self) -> None:
        self.registry([archive_document()])
        self.publish()
        (self.site / "briefings" / "en" / "index.html").unlink()

        errors = validate_archive(self.site)

        self.assertTrue(any("missing briefing page" in error and "en/index.html" in error for error in errors), errors)

    @unittest.skipUnless(shutil.which("node"), "Node.js is required to exercise the published legacy-link routing")
    def test_legacy_section_links_route_to_primary_sections_but_preserve_archive_searches(self) -> None:
        cases = [
            {"lang": language, "query": query}
            for language in ("ko", "en")
            for query in (
                "?series=lecture-notes", "?series=lecture-notes&q=kernel", "?series=lecture-notes&q=",
                "?series=lecture-notes&month=2026-10", "?series=lecture-notes&sort=oldest", "?series=lecture-notes&sort=newest",
                "?series=daily-quantum", "?series=daily-quantum&q=kernel", "?series=daily-quantum&q=",
                "?series=daily-quantum&month=2026-10", "?series=daily-quantum&sort=oldest", "?series=daily-quantum&sort=newest",
                "?series=weekly-review", "?series=weekly-review&q=kernel", "?series=weekly-review&month=2026-10", "?series=weekly-review&sort=oldest", "",
            )
        ]
        harness = r"""
const vm = require('node:vm');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const results = input.cases.map(item => {
  let destination = null;
  const location = {search: item.query, pathname: item.lang === 'en' ? '/AI_Tech_Review/archive/en/' : '/AI_Tech_Review/archive/', hash: '', replace(value) { destination = value; }};
  const context = {URLSearchParams, URL, location, window: {location}, document: {documentElement: {lang: item.lang}, querySelector() {return null;}}};
  vm.runInNewContext(input.script, context);
  return destination;
});
process.stdout.write(JSON.stringify(results));
"""
        result = subprocess.run([shutil.which("node"), "-e", harness], input=json.dumps({"script": archive_site.ARCHIVE_JS, "cases": cases}), text=True, capture_output=True, check=True)
        results = json.loads(result.stdout)
        for case, destination in zip(cases, results):
            with self.subTest(**case):
                destination_section = {
                    "?series=lecture-notes": "lectures",
                    "?series=daily-quantum": "briefings",
                    "?series=weekly-review": "briefings",
                }.get(case["query"])
                expected = (
                    ("../../" if case["lang"] == "en" else "../") + destination_section + ("/en/" if case["lang"] == "en" else "/")
                    if destination_section else None
                )
                self.assertEqual(destination, expected)

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
        for relative, asset_prefix in (("index.html", ""), ("archive/index.html", "../"), ("archive/en/index.html", "../../"), ("lectures/index.html", "../"), ("lectures/en/index.html", "../../"), ("briefings/index.html", "../"), ("briefings/en/index.html", "../../")):
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
