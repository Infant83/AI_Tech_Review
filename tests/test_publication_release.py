from __future__ import annotations

import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from scripts import publication_release as release


class ReleaseGuardTests(unittest.TestCase):
    def setUp(self):
        checksum = hashlib.sha256(b"old").hexdigest()
        self.old = {"version": 1, "reviews": {"review": {
            "href": "reviews/review/index.html", "metric_path": "/AI_Tech_Review/reviews/review/",
            "date": "2026-11-01", "translations": {}, "references": ["reviews/review/index.html"]}},
            "archive": {}, "publications": {}, "external": {},
            "files": {name: {"sha256": checksum, "content_sha256": checksum, "bytes": 3}
                      for name in ["index.html", "reviews/review/index.html", "reviews/review/figure.svg"]},
            "missing_files": [], "declared_hash_mismatches": []}
        self.new = copy.deepcopy(self.old)

    def change(self, name):
        digest = hashlib.sha256(b"new").hexdigest()
        self.new["files"][name].update(sha256=digest, content_sha256=digest)

    def test_unmodified_release_passes(self):
        self.assertTrue(release.validate_release(self.old, self.new)["ok"])

    def test_generated_navigation_change_is_allowed(self):
        self.change("index.html")
        self.assertTrue(release.validate_release(self.old, self.new)["ok"])

    def test_only_generated_thumbnail_cache_can_be_retired(self):
        name = "assets/listing-images/" + "a" * 64 + "-w480.webp"
        self.old["files"][name] = copy.deepcopy(self.old["files"]["index.html"])
        self.assertTrue(release.validate_release(self.old, self.new)["ok"])
        del self.new["files"]["reviews/review/figure.svg"]
        self.assertFalse(release.validate_release(self.old, self.new)["ok"])

    def test_old_article_and_figure_changes_require_exact_declaration(self):
        for path in ["reviews/review/index.html", "reviews/review/figure.svg"]:
            self.change(path)
        self.assertFalse(release.validate_release(self.old, self.new)["ok"])
        declarations = {path: {"before": self.old["files"][path]["content_sha256"],
                               "after": self.new["files"][path]["content_sha256"]}
                        for path in self.new["files"] if path != "index.html"}
        self.assertTrue(release.validate_release(self.old, self.new, declarations)["ok"])
        declarations["reviews/review/index.html"]["before"] = "a" * 64
        self.assertFalse(release.validate_release(self.old, self.new, declarations)["ok"])

    def test_adding_translation_keeps_prior_identity(self):
        record = self.new["reviews"]["review"]
        record["translations"]["en"] = {"href": "reviews/review/en/index.html", "metric_path": None}
        record["references"].append("reviews/review/en/index.html")
        self.assertTrue(release.validate_release(self.old, self.new)["ok"])

    def test_removing_reference_or_changing_date_is_blocked(self):
        for key, value in [("references", []), ("date", "2026-11-02"), ("metric_path", "/AI_Tech_Review/reviews/other/")]:
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.new)
                candidate["reviews"]["review"][key] = value
                self.assertFalse(release.validate_release(self.old, candidate)["ok"])

    def test_coherent_removal_is_blocked(self):
        self.new["reviews"] = {}
        self.assertFalse(release.validate_release(self.old, self.new)["ok"])

    def test_declaration_path_traversal_duplicate_and_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data = {"version": 1, "reason": "Editorial correction", "files": {
                "../private": {"before": "a" * 64, "after": "b" * 64}}}
            path = root / "change.json"
            path.write_text(json.dumps(data))
            with self.assertRaises(ValueError): release.declarations(root)
            data["files"] = {"reviews/review/index.html": {"before": "a" * 64, "after": "b" * 64}}
            path.write_text(json.dumps(data))
            (root / "duplicate.json").write_text(json.dumps(data))
            with self.assertRaises(ValueError): release.declarations(root)
            (root / "duplicate.json").unlink()
            (root / "link.json").symlink_to(path)
            with self.assertRaises(ValueError): release.declarations(root)

    def test_baseline_rejects_nonrevision_and_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            with self.assertRaises(ValueError): release.extract_baseline(path, path / "out", "HEAD")
            with self.assertRaises(ValueError): release.extract_baseline(path, path, "a" * 40)

    def test_actual_artifact_snapshot_keeps_source_only_publications(self):
        catalog_bytes = json.dumps({"revision": "b" * 40, "articles": []}).encode()
        # This publication exists in the deployed artifact, independently of
        # what a historical committed site/ directory happened to contain.
        self.new["reviews"]["artifact-only"] = copy.deepcopy(self.new["reviews"]["review"])
        wrapper = {"version": 1, "revision": "b" * 40, "snapshot": self.new,
                   "catalog_sha256": hashlib.sha256(catalog_bytes).hexdigest(),
                   "initial_payloads": {"index.html": 5000}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(release, "urlopen", side_effect=[io.BytesIO(catalog_bytes), io.BytesIO(json.dumps(wrapper).encode())]), patch.object(release, "extract_baseline") as extract:
                result = release.live_baseline(root, root / "baseline")
                extract.assert_not_called()
            self.assertEqual(result["source"], "deployed_artifact_snapshot")
            snapshot = json.loads((root / "baseline/snapshot.json").read_text())
            self.assertIn("artifact-only", snapshot["reviews"])
            self.assertFalse(release.validate_release(snapshot, self.old)["ok"])

    def test_mismatched_deployment_cannot_fall_back_to_source_archive(self):
        catalog = json.dumps({"revision": "b" * 40}).encode()
        wrapper = json.dumps({"version": 1, "revision": "c" * 40}).encode()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(release, "urlopen", side_effect=[io.BytesIO(catalog), io.BytesIO(wrapper)]), patch.object(release, "extract_baseline") as extract:
                with self.assertRaises(ValueError): release.live_baseline(root, root / "out")
                extract.assert_not_called()

    def test_missing_modern_deployment_snapshot_is_blocked(self):
        catalog = json.dumps({"revision": "b" * 40}).encode()
        error = HTTPError(release.LIVE_RELEASE, 404, "Not Found", {}, None)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(release, "urlopen", side_effect=[io.BytesIO(catalog), error]), patch.object(release, "extract_baseline") as extract:
                with self.assertRaises(ValueError): release.live_baseline(root, root / "out")
                extract.assert_not_called()


if __name__ == "__main__":
    unittest.main()
