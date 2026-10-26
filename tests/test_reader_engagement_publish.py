from __future__ import annotations

import copy
import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from scripts import reader_engagement_publish as reader

REVISION = "a" * 40
NEW_REVISION = "b" * 40
ARTICLE = {"id": "example", "path": "/AI_Tech_Review/reviews/example/",
           "title": "Example", "publishedAt": "2026-10-23", "topic": "review"}
CATALOG = {"revision": REVISION, "articles": [ARTICLE]}


class ReaderEnrichmentTests(unittest.TestCase):
    def test_injection_is_idempotent_and_preserves_existing_bytes(self):
        original = '<html>\r\n<head><link rel="icon" href="old.ico">\r\n  </head>\r\n<body><h1>원본</h1>\r\n  </body></html>'
        once = reader.enrich_html(original, "reviews/example/en/index.html", ARTICLE)
        self.assertEqual(reader.enrich_html(once, "reviews/example/en/index.html", ARTICLE), once)
        self.assertEqual(reader.strip_engagement(once), original)
        self.assertIn('href="../../../app.webmanifest"', once)
        self.assertIn('src="../../../assets/reader-engagement.js"', once)
        self.assertNotIn("window.READER_ENGAGEMENT", once)

    def test_configuration_cannot_end_its_script_tag(self):
        article = {**ARTICLE, "title": '</script><img src=x onerror="evil()">'}
        output = reader.enrich_html("<head></head><body></body>", "index.html", article)
        config = output.split('id="reader-engagement-config">')[1].split("</script>")[0]
        self.assertNotIn("<", config)
        self.assertEqual(json.loads(config)["article"]["title"], article["title"])

    def test_optional_asset_versions_change_only_reader_asset_links(self):
        original = '<html><head><link rel="icon" href="old.ico"></head><body>Original</body></html>'
        versions = {"reader-engagement.js": "123456abcdef", "reader-engagement.css": "abcdef123456"}
        result = reader.enrich_html(original, "reviews/example/en/index.html", ARTICLE, asset_versions=versions)
        self.assertIn('src="../../../assets/reader-engagement.js?v=123456abcdef"', result)
        self.assertIn('href="../../../assets/reader-engagement.css?v=abcdef123456"', result)
        self.assertIn('href="../../../app.webmanifest"', result)
        self.assertEqual(reader.strip_engagement(result), original)
        self.assertEqual(reader.enrich_html(result, "reviews/example/en/index.html", ARTICLE, asset_versions=versions), result)

    def test_enrichment_versions_follow_source_content_independently(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            js_hash = hashlib.sha256((frontend / "reader-engagement.js").read_bytes()).hexdigest()[:12]
            css_hash = hashlib.sha256((frontend / "reader-engagement.css").read_bytes()).hexdigest()[:12]
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            first = (site / "index.html").read_text()
            sw = (site / "sw.js").read_bytes()
            manifest = (site / "app.webmanifest").read_bytes()
            self.assertIn(f"reader-engagement.js?v={js_hash}", first)
            self.assertIn(f"reader-engagement.css?v={css_hash}", first)
            (frontend / "reader-engagement.css").write_text("updated CSS only")
            changed_hash = hashlib.sha256((frontend / "reader-engagement.css").read_bytes()).hexdigest()[:12]
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            updated = (site / "index.html").read_text()
            self.assertIn(f"reader-engagement.js?v={js_hash}", updated)
            self.assertIn(f"reader-engagement.css?v={changed_hash}", updated)
            self.assertNotIn(f"reader-engagement.css?v={css_hash}", updated)
            self.assertEqual(reader.strip_engagement(updated), reader.strip_engagement(first))
            self.assertEqual((site / "sw.js").read_bytes(), sw)
            self.assertEqual((site / "app.webmanifest").read_bytes(), manifest)
            self.assertEqual(reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)["html_changed"], 0)

    def test_publication_paths_reject_offsite_traversal_and_wrong_topics(self):
        for href in ["../private.html", "https://example.org/", "/other/", "reviews/%2e%2e/", "reviews//x/", "reviews/a/?redirect=x", "reviews/a/#x"]:
            with self.subTest(href=href), self.assertRaises(ValueError):
                reader.public_path(href)
        with self.assertRaises(ValueError):
            reader.publication("review", "lectures/a/", "Title", "2026-10-23", "review")
        with self.assertRaises(ValueError):
            reader.publication("different-id", "reviews/example/index.html", "Title", "2026-10-23", "review")

    def test_backend_catalog_and_title_limits_are_enforced_before_upload(self):
        with self.assertRaises(ValueError):
            reader.publication("example", "reviews/example/", "X" * 241, "2026-10-23", "review")
        with self.assertRaises(ValueError):
            reader.validate_catalog({"revision": REVISION, "articles": [ARTICLE] * 501})
        oversized = [{**ARTICLE, "id": f"entry-{i}", "path": f"/AI_Tech_Review/reviews/entry-{i}/", "title": "가" * 240} for i in range(500)]
        with self.assertRaises(ValueError):
            reader.validate_catalog({"revision": REVISION, "articles": oversized})

    def fixture(self, root: Path):
        site, frontend = root / "site", root / "frontend"
        site.mkdir()
        frontend.mkdir()
        for name in reader.ASSETS:
            (frontend / name).write_text("asset " + name)
        reviews = [{"folder": ARTICLE["id"], "href": "reviews/example/index.html", "title": ARTICLE["title"],
                    "date": ARTICLE["publishedAt"], "translations": [{"href": "reviews/example/en/index.html"}]}]
        documents = [
            {"id": "lecture-one", "series": "lecture-notes", "date": "2026-10-20", "title": "Lecture",
             "href": "archive/files/lecture.pdf", "study_href": "lectures/course/", "study_assets": {"index.html": "old"}},
            {"id": "lecture-pdf", "series": "lecture-notes", "date": "2026-10-16", "title": "PDF Lecture", "href": "archive/files/lecture.pdf"},
            {"id": "brief", "series": "daily-quantum", "date": "2026-10-25", "title": "No push", "href": "archive/files/brief.pdf"}]
        (site / "manifest.json").write_text(json.dumps(reviews))
        (site / "archive-manifest.json").write_text(json.dumps({"documents": documents}))
        for name in ["index.html", "reviews/example/index.html", "reviews/example/en/index.html", "lectures/course/index.html"]:
            path = site / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("<html><head><title>Original</title></head><body>Original content</body></html>")
        for name in ["archive/files/lecture.pdf", "archive/files/brief.pdf"]:
            path = site / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"%PDF-1.4 fixture " + name.encode())
        return site, frontend

    def test_updates_bootstrap_uses_editorial_dates_and_has_all_document_types(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            updates = json.loads((site / reader.UPDATES_NAME).read_text())
            self.assertEqual(updates["version"], 1)
            self.assertIn(reader.SCOPE, updates["pages"])
            records = {item["id"]: item for item in updates["articles"]}
            self.assertEqual(set(records), {"example", "lecture:lecture-one", "archive:brief"})
            self.assertEqual(records["example"]["updatedAt"], "2026-10-23T00:00:00Z")
            self.assertEqual(records["example"]["change"], "new")
            self.assertEqual(records["example"]["paths"], [reader.SCOPE + "reviews/example/", reader.SCOPE + "reviews/example/en/"])
            self.assertIn(reader.SCOPE + "archive/files/lecture.pdf", records["lecture:lecture-one"]["paths"])
            original = reader.strip_engagement((site / "reviews/example/en/index.html").read_text())
            self.assertEqual(updates["pages"][reader.SCOPE + "reviews/example/en/"], hashlib.sha256(original.encode()).hexdigest())
            config = json.loads((site / "reviews/example/en/index.html").read_text().split('id="reader-engagement-config">')[1].split("</script>")[0])
            self.assertEqual(config["pageVersion"], updates["pages"][reader.SCOPE + "reviews/example/en/"])
            self.assertEqual(config["articleVersion"], records["example"]["revision"])
            self.assertEqual(config["updatesUrl"], reader.SITE_ROOT + reader.UPDATES_NAME)

    def test_updates_are_stable_across_enrichment_and_reader_ui_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            first = (site / reader.UPDATES_NAME).read_bytes()
            (frontend / "reader-engagement.js").write_text("UI changed without article edits")
            (frontend / "reader-updates.js").write_text("Updated freshness module")
            reader.enrich_site(site, revision=NEW_REVISION, frontend_dir=frontend)
            self.assertEqual((site / reader.UPDATES_NAME).read_bytes(), first)
            self.assertEqual(reader.enrich_site(site, revision=NEW_REVISION, frontend_dir=frontend)["html_changed"], 0)

    def test_updates_change_only_edited_article_with_one_stable_timestamp(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            previous = json.loads((site / reader.UPDATES_NAME).read_text())
            path = site / "reviews/example/en/index.html"
            path.write_text(path.read_text().replace("Original content", "Updated English content"))
            updates = reader.build_updates(site, previous, now="2026-10-27T01:02:03Z")
            before = {item["id"]: item for item in previous["articles"]}
            after = {item["id"]: item for item in updates["articles"]}
            self.assertNotEqual(before["example"]["revision"], after["example"]["revision"])
            self.assertEqual(after["example"]["updatedAt"], "2026-10-27T01:02:03Z")
            self.assertEqual(after["example"]["change"], "updated")
            self.assertEqual(before["archive:brief"], after["archive:brief"])
            self.assertEqual(reader.build_updates(site, updates, now="2026-10-28T00:00:00Z"), updates)

    def test_archive_copies_of_review_pdfs_share_original_identity_and_asset_revision(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            manifest = json.loads((site / "manifest.json").read_text())
            manifest[0]["assets"] = ["review.pdf"]
            (site / "manifest.json").write_text(json.dumps(manifest))
            pdf = site / "reviews/example/review.pdf"
            pdf.write_bytes(b"%PDF-review revision one")
            archive = json.loads((site / "archive-manifest.json").read_text())
            archive["documents"].append({"id": "example-ko", "date": "2026-10-23", "series": "article", "title": "Example PDF", "href": "archive/files/example-ko.pdf"})
            copy = site / "archive/files/example-ko.pdf"
            copy.write_bytes(pdf.read_bytes())
            (site / "archive-manifest.json").write_text(json.dumps(archive))
            first = reader.build_updates(site)
            record = next(item for item in first["articles"] if item["id"] == "example")
            self.assertIn(reader.SCOPE + "archive/files/example-ko.pdf", record["paths"])
            self.assertFalse(any(item["id"] == "archive:example-ko" for item in first["articles"]))
            pdf.write_bytes(b"%PDF-review revision two")
            copy.write_bytes(pdf.read_bytes())
            second = reader.build_updates(site, first, now="2026-10-27T01:02:03Z")
            changed = next(item for item in second["articles"] if item["id"] == "example")
            self.assertNotEqual(record["revision"], changed["revision"])
            self.assertEqual(first["pages"], second["pages"])
            self.assertEqual(changed["updatedAt"], "2026-10-27T01:02:03Z")

    def test_updated_date_bootstrap_does_not_use_deployment_time(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, _ = self.fixture(Path(temporary))
            manifest = json.loads((site / "manifest.json").read_text())
            manifest[0]["updated"] = "2026-10-26"
            (site / "manifest.json").write_text(json.dumps(manifest))
            updates = reader.build_updates(site, now="2026-12-01T01:02:03Z")
            record = next(item for item in updates["articles"] if item["id"] == "example")
            self.assertEqual(record["updatedAt"], "2026-10-26T00:00:00Z")
            self.assertEqual(record["change"], "updated")

    def test_update_validation_rejects_tampering_cross_scope_and_duplicate_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            output = site / reader.UPDATES_NAME
            original = json.loads(output.read_text())
            for mutate in [
                lambda data: data["pages"].update({"https://foreign.invalid/": "a" * 64}),
                lambda data: data["pages"].update({reader.SCOPE: "b" * 64}),
                lambda data: data["articles"][0]["paths"].append(data["articles"][0]["paths"][0]),
                lambda data: data["articles"][0].update({"updatedAt": "tomorrow"}),
                lambda data: data["articles"][0].update({"title": "Unapproved title"}),
            ]:
                data = copy.deepcopy(original)
                mutate(data)
                output.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    reader.validate_public_artifact(site)
            output.write_text(json.dumps(original))
            reader.validate_public_artifact(site)

    def test_existing_output_enrichment_tracks_lecture_checksums_and_stable_ids(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            original = (site / "reviews/example/index.html").read_text()
            result = reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            self.assertEqual(result["articles"], 3)
            catalog = json.loads((site / reader.CATALOG_NAME).read_text())
            self.assertEqual([a["id"] for a in catalog["articles"]], [ARTICLE["id"], "lecture:lecture-one", "lecture:lecture-pdf"])
            en = (site / "reviews/example/en/index.html").read_text()
            config = json.loads(en.split('id="reader-engagement-config">')[1].split("</script>")[0])
            self.assertEqual(config["article"]["id"], ARTICLE["id"])
            self.assertEqual(config["article"]["path"], ARTICLE["path"])
            archive = json.loads((site / "archive-manifest.json").read_text())
            checksum = hashlib.sha256((site / "lectures/course/index.html").read_bytes()).hexdigest()
            self.assertEqual(archive["documents"][0]["study_assets"]["index.html"], checksum)
            self.assertEqual(reader.strip_engagement((site / "reviews/example/index.html").read_text()), original)
            self.assertEqual(reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)["html_changed"], 0)

    def test_missing_asset_does_not_modify_pages(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            original = (site / "index.html").read_bytes()
            (frontend / "sw.js").unlink()
            with self.assertRaises(ValueError):
                reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            self.assertEqual((site / "index.html").read_bytes(), original)
            self.assertFalse((site / "assets/reader-engagement.js").exists())

    def test_public_artifact_accepts_approved_content_and_rejects_private_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            self.assertEqual(reader.validate_public_artifact(site)["articles"], 3)
            for name in [".env", "assets/private.pem", "assets/state.sqlite", "backend/config.json", "reviews/example/private.pdf"]:
                with self.subTest(name=name):
                    path = site / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("private fixture")
                    with self.assertRaises(ValueError):
                        reader.validate_public_artifact(site)
                    path.unlink()

    def test_secret_detection_never_includes_the_value_in_its_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            secret = "ghp_" + "A" * 36
            (site / "assets/config.json").write_text(json.dumps({"credential": secret}))
            with self.assertRaises(ValueError) as error:
                reader.validate_public_artifact(site)
            self.assertIn("assets/config.json", str(error.exception))
            self.assertNotIn(secret, str(error.exception))

    def test_embedded_raster_data_does_not_false_flag_but_svg_text_is_scanned(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            pixels = b"\x89PNG\r\n\x1a\n\x00" + base64.b64decode("/srv/AAAAAAA")
            encoded = base64.b64encode(pixels).decode()
            self.assertIn("/srv/", encoded)
            icon = site / "assets/icon.svg"
            icon.write_text(f'<svg><image href="data:image/png;base64,{encoded}"/></svg>')
            reader.validate_public_artifact(site)
            icon.write_text(icon.read_text().replace("</svg>", "<text>ghp_" + "A" * 36 + "</text></svg>"))
            with self.assertRaises(ValueError):
                reader.validate_public_artifact(site)

    def test_symlinks_and_invented_publication_metadata_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            linked = site / "assets/linked.txt"
            linked.symlink_to(site / "index.html")
            with self.assertRaises(ValueError):
                reader.validate_public_artifact(site)
            linked.unlink()
            catalog = json.loads((site / reader.CATALOG_NAME).read_text())
            catalog["articles"][0]["title"] = "Not in approved manifest"
            (site / reader.CATALOG_NAME).write_text(json.dumps(catalog))
            with self.assertRaises(ValueError):
                reader.validate_public_artifact(site)

    def test_legacy_image_exception_accepts_only_the_exact_reviewed_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            site, frontend = self.fixture(Path(temporary))
            reader.enrich_site(site, revision=REVISION, frontend_dir=frontend)
            legacy = site / "reviews/example/previous.webp"
            legacy.write_bytes(b"RIFFxxxxWEBPprevious reviewed pixels")
            exceptions = Path(temporary) / "exceptions.json"
            exceptions.write_text(json.dumps({legacy.relative_to(site).as_posix(): hashlib.sha256(legacy.read_bytes()).hexdigest()}))
            with patch.object(reader, "ASSET_EXCEPTIONS", exceptions):
                reader.validate_public_artifact(site)
                legacy.write_bytes(b"replacement bytes are not approved")
                with self.assertRaises(ValueError):
                    reader.validate_public_artifact(site)


class PublicationSyncTests(unittest.TestCase):
    def run_sync(self, responder, **kwargs):
        with patch.object(reader, "request_json", side_effect=responder), patch.object(reader, "assert_live_article") as live:
            result = reader.sync_publications(copy.deepcopy(CATALOG), REVISION, "Infant83/AI_Tech_Review", "github-secret", "publish-secret", attempts=1, delay=0, **kwargs)
            return result, live

    def test_stale_revision_never_fetches_public_pages_or_posts(self):
        calls = []
        def respond(url, **kwargs):
            calls.append((url, kwargs))
            return {"object": {"sha": NEW_REVISION}}
        result, live = self.run_sync(respond)
        self.assertIn("skipped", result)
        self.assertEqual(len(calls), 1)
        live.assert_not_called()

    def test_deployed_revision_must_match_trusted_workflow_revision(self):
        with patch.object(reader, "request_json") as request, self.assertRaises(ValueError):
            reader.sync_publications(CATALOG, NEW_REVISION, "Infant83/AI_Tech_Review", "g", "p")
        request.assert_not_called()

    def test_public_artifact_mismatch_prevents_sync(self):
        calls = []
        def respond(url, **kwargs):
            calls.append((url, kwargs))
            if "/git/ref/" in url:
                return {"object": {"sha": REVISION}}
            return {"revision": NEW_REVISION, "articles": [ARTICLE]}
        with self.assertRaises(ValueError):
            self.run_sync(respond)
        self.assertFalse(any(item[1].get("body") for item in calls))

    def test_valid_live_deployment_sends_exact_catalog_after_url_checks(self):
        calls = []
        def respond(url, **kwargs):
            calls.append((url, kwargs))
            if "/git/ref/" in url:
                return {"object": {"sha": REVISION}}
            if url.startswith(reader.SITE_ROOT):
                return CATALOG
            return {"ok": True}
        result, live = self.run_sync(respond)
        self.assertTrue(result["ok"])
        live.assert_called_once_with(ARTICLE, REVISION)
        self.assertEqual(calls[-1], (reader.API_BASE + "/v1/publications/sync", {"token": "publish-secret", "body": CATALOG}))
        self.assertIn("&check=", calls[1][0])

    def test_source_advancing_during_url_checks_prevents_sync(self):
        refs = iter([REVISION, NEW_REVISION])
        calls = []
        def respond(url, **kwargs):
            calls.append((url, kwargs))
            return {"object": {"sha": next(refs)}} if "/git/ref/" in url else CATALOG
        result, _ = self.run_sync(respond)
        self.assertIn("skipped", result)
        self.assertFalse(any(item[1].get("body") for item in calls))

    def test_article_get_failure_withholds_registration(self):
        def respond(url, **kwargs):
            return {"object": {"sha": REVISION}} if "/git/ref/" in url else CATALOG
        with patch.object(reader, "request_json", side_effect=respond) as request, patch.object(reader, "assert_live_article", side_effect=ValueError("not live")):
            with self.assertRaises(ValueError):
                reader.sync_publications(CATALOG, REVISION, "Infant83/AI_Tech_Review", "g", "p", attempts=1)
        self.assertFalse(any(c.kwargs.get("body") for c in request.call_args_list))

    def test_backend_conflict_is_retried_with_public_and_stale_guards(self):
        posts = []
        def respond(url, **kwargs):
            if "/git/ref/" in url:
                return {"object": {"sha": REVISION}}
            if url.startswith(reader.SITE_ROOT):
                return CATALOG
            posts.append(kwargs)
            if len(posts) == 1:
                raise HTTPError(url, 409, "CDN not current", {}, None)
            return {"ok": True}
        with patch.object(reader.time, "sleep") as sleep:
            result, _ = self.run_sync(respond)
        self.assertTrue(result["ok"])
        self.assertEqual(len(posts), 2)
        sleep.assert_called_once_with(5)

    def test_backend_conflict_does_not_retry_a_superseded_revision(self):
        refs = iter([REVISION, REVISION, NEW_REVISION])
        posts = []
        def respond(url, **kwargs):
            if "/git/ref/" in url:
                return {"object": {"sha": next(refs)}}
            if url.startswith(reader.SITE_ROOT):
                return CATALOG
            posts.append(kwargs)
            raise HTTPError(url, 409, "CDN not current", {}, None)
        with patch.object(reader.time, "sleep"):
            result, _ = self.run_sync(respond)
        self.assertIn("skipped", result)
        self.assertEqual(len(posts), 1)

    def test_public_catalog_advancing_during_article_gets_prevents_sync(self):
        reads = iter([CATALOG, {"revision": NEW_REVISION, "articles": [ARTICLE]}])
        posts = []
        def respond(url, **kwargs):
            if "/git/ref/" in url:
                return {"object": {"sha": REVISION}}
            if url.startswith(reader.SITE_ROOT):
                return next(reads)
            posts.append(kwargs)
            return {"ok": True}
        result, _ = self.run_sync(respond)
        self.assertIn("skipped", result)
        self.assertEqual(posts, [])


if __name__ == "__main__":
    unittest.main()
