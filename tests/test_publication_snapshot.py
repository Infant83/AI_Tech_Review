from __future__ import annotations

import copy
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts import publication_snapshot as snapshots
from scripts import reader_engagement_publish as reader


class PublicationSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.site = self.root / "site"
        self.site.mkdir()
        self.review = {"folder": "example", "href": "reviews/example/index.html",
                       "metric_path": "/AI_Tech_Review/reviews/example/",
                       "assets": ["hero.webp"], "translations": [{"language": "en",
                       "href": "reviews/example/en/index.html",
                       "metric_path": "/AI_Tech_Review/reviews/example/en/", "assets": []}]}
        self.document = {"id": "lecture", "href": "archive/files/lecture.pdf",
                         "sha256": hashlib.sha256(b"public PDF").hexdigest()}
        self.article = {"id": "example", "path": "/AI_Tech_Review/reviews/example/", "topic": "review"}
        for name, value in {"index.html": b"<html>Home</html>",
                            self.review["href"]: b"<html><head></head><body>Public article</body></html>",
                            "reviews/example/en/index.html": b"<html>English</html>",
                            "reviews/example/hero.webp": b"public image",
                            self.document["href"]: b"public PDF"}.items():
            path = self.site / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value)
        self.write_registries()

    def write_registries(self, reviews=None, documents=None, articles=None):
        for name, value in {"manifest.json": reviews if reviews is not None else [self.review],
                            "archive-manifest.json": {"documents": documents if documents is not None else [self.document]},
                            "reader-publications.json": {"revision": "a" * 40,
                             "articles": articles if articles is not None else [self.article]}}.items():
            (self.site / name).write_text(json.dumps(value), encoding="utf-8")

    def baseline(self):
        return snapshots.capture_site(self.site)

    def test_capture_is_deterministic_read_only_and_contains_no_root_path(self):
        original = {path.relative_to(self.site).as_posix(): path.read_bytes()
                    for path in self.site.rglob("*") if path.is_file()}
        first = self.baseline()
        self.assertEqual(first, self.baseline())
        self.assertNotIn(str(self.root), json.dumps(first))
        self.assertEqual(original, {path.relative_to(self.site).as_posix(): path.read_bytes()
                                   for path in self.site.rglob("*") if path.is_file()})

    def test_coherent_catalog_drop_is_still_detected(self):
        baseline = self.baseline()
        self.write_registries(reviews=[], articles=[])
        result = snapshots.compare_snapshots(baseline, self.baseline())
        self.assertFalse(result["structural_ok"])
        self.assertIn({"kind": "record_removed", "group": "reviews", "id": "example"}, result["blockers"])

    def test_metric_identity_change_blocks_even_with_unchanged_files(self):
        baseline = self.baseline()
        self.review["metric_path"] = "/AI_Tech_Review/reviews/renamed/"
        self.write_registries()
        self.assertFalse(snapshots.compare_snapshots(baseline, self.baseline())["structural_ok"])

    def test_translation_removal_blocks_even_when_html_is_left_on_disk(self):
        baseline = self.baseline()
        self.review["translations"] = []
        self.write_registries()
        self.assertFalse(snapshots.compare_snapshots(baseline, self.baseline())["structural_ok"])

    def test_missing_declared_image_and_pdf_block(self):
        baseline = self.baseline()
        for name in ("reviews/example/hero.webp", self.document["href"]):
            (self.site / name).unlink()
        result = snapshots.compare_snapshots(baseline, self.baseline())
        self.assertFalse(result["structural_ok"])
        self.assertTrue(any(item["kind"] == "missing_file" for item in result["blockers"]))

    def test_new_publication_is_allowed(self):
        baseline = self.baseline()
        addition = {"folder": "second", "href": "reviews/second/index.html", "assets": []}
        target = self.site / addition["href"]
        target.parent.mkdir(parents=True)
        target.write_text("<html>New article</html>")
        self.write_registries(reviews=[self.review, addition])
        result = snapshots.compare_snapshots(baseline, self.baseline())
        self.assertTrue(result["structural_ok"])
        self.assertIn({"group": "reviews", "id": "second"}, result["additions"])

    def test_article_content_change_requires_review_but_is_not_identity_failure(self):
        baseline = self.baseline()
        (self.site / self.review["href"]).write_text("<html>Revised article</html>")
        result = snapshots.compare_snapshots(baseline, self.baseline())
        self.assertTrue(result["structural_ok"])
        self.assertTrue(result["content_review_required"])
        self.assertIn(self.review["href"], result["content_changes"])

    def test_injection_changes_are_separate_from_article_content(self):
        path = self.site / self.review["href"]
        original = path.read_text()
        path.write_text(reader.enrich_html(original, self.review["href"], self.article))
        baseline = self.baseline()
        path.write_text(reader.enrich_html(original, self.review["href"], self.article,
                                          asset_versions={"reader-engagement.js": "123456abcdef"}))
        result = snapshots.compare_snapshots(baseline, self.baseline())
        self.assertTrue(result["structural_ok"])
        self.assertFalse(result["content_review_required"])
        self.assertIn(self.review["href"], result["instrumentation_only_changes"])

    def test_reader_identity_drift_blocks_without_manifest_change(self):
        path = self.site / self.review["href"]
        original = path.read_text()
        path.write_text(reader.enrich_html(original, self.review["href"], self.article))
        baseline = self.baseline()
        path.write_text(reader.enrich_html(original, self.review["href"], {**self.article, "id": "wrong"}))
        result = snapshots.compare_snapshots(baseline, self.baseline())
        self.assertIn({"kind": "reader_identity_changed", "path": self.review["href"]}, result["blockers"])

    def test_duplicate_id_and_traversal_are_rejected(self):
        self.write_registries(reviews=[self.review, copy.deepcopy(self.review)])
        with self.assertRaises(snapshots.SnapshotError):
            self.baseline()
        self.review["assets"] = ["../private.txt"]
        self.write_registries()
        with self.assertRaises(snapshots.SnapshotError):
            self.baseline()

    def test_declared_checksum_mismatch_blocks(self):
        baseline = self.baseline()
        (self.site / self.document["href"]).write_bytes(b"changed PDF without updating its registry")
        result = snapshots.compare_snapshots(baseline, self.baseline())
        self.assertIn({"kind": "declared_hash_mismatch", "path": self.document["href"]}, result["blockers"])

    def test_duplicate_urls_are_rejected_even_for_distinct_ids(self):
        second = {**self.review, "folder": "second"}
        self.write_registries(reviews=[self.review, second])
        with self.assertRaises(snapshots.SnapshotError):
            self.baseline()

    def test_malformed_baseline_file_hash_is_rejected(self):
        baseline = self.baseline()
        baseline["files"][self.review["href"]] = "not a hash record"
        with self.assertRaises(snapshots.SnapshotError):
            snapshots.compare_snapshots(baseline, self.baseline())

    def test_shared_counter_reader_and_font_assets_are_tracked(self):
        names = ["assets/reader-engagement.js", "assets/public-metrics.js", "assets/type.woff2",
                 "lectures/reader/reader.mjs"]
        for name in names:
            path = self.site / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"original")
        baseline = self.baseline()
        (self.site / names[0]).write_bytes(b"new counter code")
        (self.site / names[3]).write_bytes(b"new reader code")
        (self.site / names[2]).unlink()
        result = snapshots.compare_snapshots(baseline, self.baseline())
        self.assertIn(names[0], result["content_changes"])
        self.assertIn(names[3], result["content_changes"])
        self.assertIn({"kind": "reference_missing", "path": names[2]}, result["blockers"])

    def test_symlinked_json_registry_is_rejected(self):
        path = self.site / "manifest.json"
        outside = self.root / "other.json"
        outside.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(outside)
        with self.assertRaises(snapshots.SnapshotError):
            self.baseline()

    def test_original_publication_date_drift_blocks(self):
        baseline = self.baseline()
        self.review["date"] = "2026-11-07"
        self.document["date"] = "2026-11-07"
        self.article["publishedAt"] = "2026-11-07"
        self.write_registries()
        result = snapshots.compare_snapshots(baseline, self.baseline())
        changed = {item.get("group") for item in result["blockers"]}
        self.assertTrue({"reviews", "archive", "publications"}.issubset(changed))

    def briefing_document(self):
        self.document.update(id="2026-11-12-daily-quantum-brief", date="2026-11-12", series="daily-quantum",
                             href="archive/files/2026-11-12-daily-quantum-brief.pdf")
        (self.site / self.document["href"]).write_bytes(b"public PDF")
        self.write_registries()

    def register_editorial(self):
        self.document.update(editorial_href="briefings/2026-11-12/index.html",
                             editorial_en_href="briefings/2026-11-12/en/index.html")
        assets = {}
        for language in ("ko", "en"):
            name = self.document["editorial_en_href" if language == "en" else "editorial_href"]
            page = self.site / name
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(f"<html><body>Reviewed {language} editorial</body></html>")
            assets[name] = hashlib.sha256(page.read_bytes()).hexdigest()
        self.document["editorial_assets"] = assets
        self.write_registries()

    def test_first_registered_editorial_pair_is_a_narrow_structural_append(self):
        self.briefing_document()
        baseline = self.baseline()
        self.register_editorial()
        current = self.baseline()
        identity = self.document["id"]
        expected = sorted(self.document["editorial_assets"])
        self.assertNotIn("editorial_references", baseline["archive"][identity])
        self.assertEqual(current["archive"][identity]["editorial_references"], expected)
        result = snapshots.compare_snapshots(baseline, current)
        self.assertTrue(result["structural_ok"], result["blockers"])
        self.assertTrue(snapshots.compare_snapshots(current, current)["structural_ok"])
        self.assertEqual(set(current["archive"][identity]["references"]) - set(baseline["archive"][identity]["references"]), set(expected))

    def test_research_editorial_append_uses_its_own_route_and_still_preserves_pdf(self):
        self.briefing_document()
        self.document.update(id="2026-11-12-daily-research-brief", series="daily-research",
                             href="archive/files/2026-11-12-daily-research-brief.pdf")
        (self.site / self.document["href"]).write_bytes(b"public PDF")
        self.write_registries()
        baseline = self.baseline()
        self.register_editorial()
        # A research briefing cannot take the existing quantum date route.
        with self.assertRaises(snapshots.SnapshotError):
            self.baseline()
        self.document.update(editorial_href="briefings/research/2026-11-12/index.html",
                             editorial_en_href="briefings/research/2026-11-12/en/index.html")
        assets = {}
        for name in (self.document["editorial_href"], self.document["editorial_en_href"]):
            page = self.site / name
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text("<html><body>Research editorial</body></html>")
            assets[name] = hashlib.sha256(page.read_bytes()).hexdigest()
        self.document["editorial_assets"] = assets
        self.write_registries()
        current = self.baseline()
        self.assertTrue(snapshots.compare_snapshots(baseline, current)["structural_ok"])
        changed = copy.deepcopy(current)
        changed["files"][self.document["href"]]["sha256"] = "f" * 64
        self.assertFalse(snapshots.compare_snapshots(baseline, changed)["structural_ok"])

    def test_first_append_does_not_allow_identity_drift_or_extra_references(self):
        self.briefing_document()
        baseline = self.baseline()
        self.register_editorial()
        current = self.baseline()
        identity = self.document["id"]
        for field, value in (("date", "2026-11-11"), ("href", "archive/files/renamed.pdf"),
                             ("study_href", "lectures/unrelated/"),
                             ("references", current["archive"][identity]["references"] + ["archive/files/other.pdf"])):
            with self.subTest(field=field):
                changed = copy.deepcopy(current)
                changed["archive"][identity][field] = value
                self.assertFalse(snapshots.compare_snapshots(baseline, changed)["structural_ok"])
        changed = copy.deepcopy(current)
        changed["files"][self.document["href"]]["sha256"] = "f" * 64
        self.assertFalse(snapshots.compare_snapshots(baseline, changed)["structural_ok"])

    def test_existing_editorial_removal_or_movement_remains_blocked(self):
        self.briefing_document()
        self.register_editorial()
        baseline = self.baseline()
        for key in ("editorial_href", "editorial_en_href", "editorial_assets"):
            self.document.pop(key)
        self.write_registries()
        self.assertFalse(snapshots.compare_snapshots(baseline, self.baseline())["structural_ok"])
        self.register_editorial()
        self.document["editorial_href"] = "briefings/2026-11-13/index.html"
        self.write_registries()
        with self.assertRaises(snapshots.SnapshotError):
            self.baseline()

    def test_editorial_capture_requires_matching_id_date_path_and_exact_two_hashes(self):
        self.briefing_document()
        self.register_editorial()
        valid = copy.deepcopy(self.document)
        invalid = [
            {"id": "2026-11-11-daily-quantum-brief"}, {"date": "2026-99-99"},
            {"series": "article"}, {"href": "archive/files/other.pdf"},
            {"editorial_assets": {self.document["editorial_href"]: "a" * 64}},
            {"editorial_assets": {key: "not-a-hash" for key in self.document["editorial_assets"]}},
            {"editorial_assets": {**self.document["editorial_assets"], "archive/files/other.pdf": "a" * 64}},
        ]
        for change in invalid:
            with self.subTest(change=change):
                self.document = {**copy.deepcopy(valid), **change}
                self.write_registries()
                with self.assertRaises(snapshots.SnapshotError):
                    self.baseline()

    def test_missing_or_tampered_editorial_cannot_pass_the_first_append(self):
        self.briefing_document()
        baseline = self.baseline()
        self.register_editorial()
        page = self.site / self.document["editorial_en_href"]
        original = page.read_bytes()
        page.write_bytes(b"tampered body")
        result = snapshots.compare_snapshots(baseline, self.baseline())
        self.assertTrue(any(item["kind"] == "declared_hash_mismatch" for item in result["blockers"]))
        page.write_bytes(original)
        page.unlink()
        result = snapshots.compare_snapshots(baseline, self.baseline())
        self.assertFalse(result["structural_ok"])
        self.assertTrue(any(item["kind"] == "missing_file" for item in result["blockers"]))

    def test_cli_writes_outside_public_site_and_returns_failure_on_removal(self):
        baseline_path = self.root / "baseline.json"
        self.assertEqual(snapshots.main(["capture", "--site", str(self.site), "--output", str(baseline_path)]), 0)
        self.write_registries(reviews=[], articles=[])
        self.assertEqual(snapshots.main(["compare", "--baseline", str(baseline_path), "--site", str(self.site),
                                         "--output", str(self.root / "comparison.json")]), 1)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(snapshots.main(["capture", "--site", str(self.site),
                                             "--output", str(self.site / "snapshot.json")]), 2)
        self.assertFalse((self.site / "snapshot.json").exists())


if __name__ == "__main__":
    unittest.main()
