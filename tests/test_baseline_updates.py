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


class BaselineUpdateTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.snapshot = {
            "version": 1, "reviews": {}, "archive": {}, "publications": {}, "external": {},
            "files": {}, "missing_files": [], "declared_hash_mismatches": [],
        }
        self.updates = {
            "version": 1,
            "pages": {"/AI_Tech_Review/reviews/example/": "a" * 64},
            "articles": [{
                "id": "example", "path": "/AI_Tech_Review/reviews/example/",
                "paths": ["/AI_Tech_Review/reviews/example/"], "title": "검증한 글",
                "publishedAt": "2026-11-01", "revision": "b" * 64,
                "updatedAt": "2026-11-03T01:02:03Z", "change": "updated",
            }],
        }
        # Non-ASCII and whitespace make the raw binding differ from a JSON
        # object's canonical serialization.
        self.updates_payload = self.encode(self.updates)
        self.catalog_payload = self.encode({"revision": "c" * 40, "articles": []})
        self.manifest = {
            "version": 1, "revision": "c" * 40, "snapshot": self.snapshot,
            "catalog_sha256": hashlib.sha256(self.catalog_payload).hexdigest(),
            "artifact_files": {}, "initial_payloads": {},
        }
        self.manifest = self.bind(self.updates_payload)

    @staticmethod
    def encode(value):
        return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    def bind(self, payload):
        manifest = copy.deepcopy(self.manifest)
        manifest["artifact_files"]["reader-updates.json"] = {
            "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload),
        }
        return manifest

    def bundle(self, name="baseline"):
        directory = self.root / name
        directory.mkdir()
        (directory / "snapshot.json").write_bytes(self.encode(self.snapshot))
        (directory / "release.json").write_bytes(self.encode(self.manifest))
        (directory / "reader-publications.json").write_bytes(self.catalog_payload)
        (directory / "reader-updates.json").write_bytes(self.updates_payload)
        return directory / "snapshot.json"

    def responses(self, *, final_release=None, final_catalog=None, updates=None):
        manifest = self.encode(self.manifest)
        return [io.BytesIO(payload) for payload in (
            self.catalog_payload, manifest,
            self.updates_payload if updates is None else updates,
            manifest if final_release is None else final_release,
            self.catalog_payload if final_catalog is None else final_catalog,
        )]

    def test_verification_returns_valid_metadata_without_changing_inputs(self):
        before = copy.deepcopy(self.manifest)
        result = release.verify_baseline_updates(self.manifest, self.snapshot, self.updates_payload)
        self.assertEqual(result, self.updates)
        self.assertEqual(self.manifest, before)

    def test_raw_hash_and_exact_size_both_bind_the_payload(self):
        for field, value in (("sha256", "d" * 64), ("bytes", len(self.updates_payload) + 1)):
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["artifact_files"]["reader-updates.json"][field] = value
                with self.assertRaises(ValueError):
                    release.verify_baseline_updates(manifest, self.snapshot, self.updates_payload)
        # Equivalent parsed JSON is insufficient: these bytes were not sealed.
        compact = json.dumps(self.updates, ensure_ascii=False).encode("utf-8")
        with self.assertRaises(ValueError):
            release.verify_baseline_updates(self.manifest, self.snapshot, compact)

    def test_size_limit_accepts_exact_boundary_and_rejects_larger_payload(self):
        maximum = 2_000_000
        padded = self.updates_payload + b" " * (maximum - len(self.updates_payload))
        self.assertEqual(release.verify_baseline_updates(self.bind(padded), self.snapshot, padded), self.updates)
        oversized = padded + b" "
        with self.assertRaises(ValueError):
            release.verify_baseline_updates(self.bind(oversized), self.snapshot, oversized)

    def test_invalid_release_or_file_descriptors_are_value_errors(self):
        mutations = (
            lambda document: document.update(version=True),
            lambda document: document.update(version=2),
            lambda document: document.update(revision="HEAD"),
            lambda document: document.update(revision="C" * 40),
            lambda document: document.update(revision=None),
            lambda document: document.update(snapshot={**self.snapshot, "reviews": {"other": {}}}),
            lambda document: document.update(artifact_files=None),
            lambda document: document["artifact_files"].clear(),
            lambda document: document["artifact_files"].update({"reader-updates.json": []}),
            lambda document: document["artifact_files"]["reader-updates.json"].pop("bytes"),
            lambda document: document["artifact_files"]["reader-updates.json"].update(bytes=True),
            lambda document: document["artifact_files"]["reader-updates.json"].update(bytes=-1),
            lambda document: document["artifact_files"]["reader-updates.json"].update(bytes=2_000_001),
            lambda document: document["artifact_files"]["reader-updates.json"].update(bytes="1"),
            lambda document: document["artifact_files"]["reader-updates.json"].update(bytes=1.0),
            lambda document: document["artifact_files"]["reader-updates.json"].update(sha256=None),
            lambda document: document["artifact_files"]["reader-updates.json"].update(sha256="z" * 64),
        )
        for number, mutate in enumerate(mutations):
            with self.subTest(case=number):
                manifest = copy.deepcopy(self.manifest)
                mutate(manifest)
                with self.assertRaises(ValueError):
                    release.verify_baseline_updates(manifest, self.snapshot, self.updates_payload)
        for manifest in (None, [], "release"):
            with self.subTest(release_type=type(manifest).__name__):
                with self.assertRaises(ValueError):
                    release.verify_baseline_updates(manifest, self.snapshot, self.updates_payload)

    def test_invalid_nested_update_types_are_normalized_to_value_errors(self):
        mutations = (
            lambda data: data.update(version=True),
            lambda data: data.update(version=1.0),
            lambda data: data.update(pages=[]),
            lambda data: data.update(pages={"/AI_Tech_Review/reviews/example/": 10 ** 63}),
            lambda data: data.update(articles={}),
            lambda data: data.update(articles=[None]),
            lambda data: data["articles"][0].update(publishedAt=None),
            lambda data: data["articles"][0].update(publishedAt="2026-02-30"),
            lambda data: data["articles"][0].update(updatedAt="2026-11-03T25:02:03Z"),
            lambda data: data["articles"][0].update(paths=[[]]),
            lambda data: data["articles"][0].update(path="/outside/example/"),
            lambda data: data["articles"][0].update(revision="not-a-hash"),
            lambda data: data["articles"][0].update(revision=10 ** 63),
            lambda data: data["articles"].append(copy.deepcopy(data["articles"][0])),
            lambda data: data["articles"].append({**data["articles"][0], "id": "other"}),
        )
        for number, mutate in enumerate(mutations):
            with self.subTest(case=number):
                updates = copy.deepcopy(self.updates)
                mutate(updates)
                payload = self.encode(updates)
                with self.assertRaises(ValueError):
                    release.verify_baseline_updates(self.bind(payload), self.snapshot, payload)

    def test_malformed_utf8_json_and_duplicate_keys_are_rejected_even_when_bound(self):
        duplicate = self.updates_payload.replace(b'"version": 1,', b'"version": 1, "version": 1,', 1)
        for payload in (b"\xff", b"{", b"null", b"[]", duplicate):
            with self.subTest(payload=payload[:50]):
                with self.assertRaises(ValueError):
                    release.verify_baseline_updates(self.bind(payload), self.snapshot, payload)

    def test_read_bundle_returns_exact_prior_bytes_without_network(self):
        snapshot_path = self.bundle()
        with patch.object(release, "urlopen") as network:
            actual = release.read_baseline_updates(snapshot_path, self.snapshot)
            network.assert_not_called()
        self.assertEqual(actual, self.updates_payload)

    def test_read_bundle_requires_every_regular_valid_sidecar(self):
        names = ("release.json", "reader-publications.json", "reader-updates.json")
        for operation in ("missing", "symlink", "malformed"):
            for number, name in enumerate(names):
                with self.subTest(operation=operation, sidecar=name):
                    snapshot_path = self.bundle(operation + str(number))
                    path = snapshot_path.parent / name
                    if operation == "missing":
                        path.unlink()
                    elif operation == "symlink":
                        target = path.with_suffix(".actual")
                        path.rename(target)
                        path.symlink_to(target)
                    else:
                        path.write_bytes(b"{broken")
                    with self.assertRaises(ValueError):
                        release.read_baseline_updates(snapshot_path, self.snapshot)

    def test_read_bundle_rejects_catalog_hash_revision_and_snapshot_mismatch(self):
        for number, failure in enumerate(("catalog_hash", "catalog_revision", "snapshot")):
            with self.subTest(failure=failure):
                snapshot_path = self.bundle("mismatch" + str(number))
                manifest = copy.deepcopy(self.manifest)
                if failure == "catalog_hash":
                    (snapshot_path.parent / "reader-publications.json").write_bytes(self.catalog_payload + b" ")
                elif failure == "catalog_revision":
                    catalog = self.encode({"revision": "d" * 40, "articles": []})
                    (snapshot_path.parent / "reader-publications.json").write_bytes(catalog)
                    manifest["catalog_sha256"] = hashlib.sha256(catalog).hexdigest()
                else:
                    manifest["snapshot"]["reviews"] = {"other": {}}
                (snapshot_path.parent / "release.json").write_bytes(self.encode(manifest))
                with self.assertRaises(ValueError):
                    release.read_baseline_updates(snapshot_path, self.snapshot)

    def test_read_bundle_rejects_duplicate_catalog_and_release_keys(self):
        for number, name in enumerate(("reader-publications.json", "release.json")):
            with self.subTest(sidecar=name):
                snapshot_path = self.bundle("duplicate" + str(number))
                path = snapshot_path.parent / name
                payload = path.read_bytes()
                key, value = (b"revision", b'"' + b"c" * 40 + b'"') if name.startswith("reader") else (b"version", b"1")
                payload = payload.replace(b"{", b'{"' + key + b'":' + value + b",", 1)
                path.write_bytes(payload)
                if name.startswith("reader"):
                    manifest = copy.deepcopy(self.manifest)
                    manifest["catalog_sha256"] = hashlib.sha256(payload).hexdigest()
                    (snapshot_path.parent / "release.json").write_bytes(self.encode(manifest))
                with self.assertRaises(ValueError):
                    release.read_baseline_updates(snapshot_path, self.snapshot)

    def test_live_baseline_preserves_verified_raw_bundle(self):
        output = self.root / "live"
        with patch.object(release, "urlopen", side_effect=self.responses()) as network:
            with patch.object(release, "extract_baseline") as extract:
                result = release.live_baseline(self.root, output)
                extract.assert_not_called()
        self.assertEqual(network.call_count, 5)
        self.assertEqual(result["source"], "deployed_artifact_snapshot")
        self.assertEqual((output / "release.json").read_bytes(), self.encode(self.manifest))
        self.assertEqual((output / "reader-publications.json").read_bytes(), self.catalog_payload)
        self.assertEqual((output / "reader-updates.json").read_bytes(), self.updates_payload)
        self.assertEqual(release.read_baseline_updates(output / "snapshot.json", self.snapshot), self.updates_payload)

    def test_live_same_revision_and_snapshot_artifact_race_does_not_publish_bundle(self):
        newer_updates = copy.deepcopy(self.updates)
        newer_updates["articles"][0]["updatedAt"] = "2026-11-04T01:02:03Z"
        newer_release = self.bind(self.encode(newer_updates))
        self.assertEqual(newer_release["revision"], self.manifest["revision"])
        self.assertEqual(newer_release["catalog_sha256"], self.manifest["catalog_sha256"])
        self.assertEqual(newer_release["snapshot"], self.manifest["snapshot"])
        output = self.root / "race"
        with patch.object(release, "urlopen", side_effect=self.responses(final_release=self.encode(newer_release))):
            with patch.object(release, "extract_baseline") as extract:
                with self.assertRaises(ValueError):
                    release.live_baseline(self.root, output)
                extract.assert_not_called()
        self.assertFalse(output.exists())

    def test_live_catalog_race_does_not_publish_bundle(self):
        output = self.root / "catalog-race"
        with patch.object(release, "urlopen", side_effect=self.responses(final_catalog=self.catalog_payload + b" ")):
            with self.assertRaises(ValueError):
                release.live_baseline(self.root, output)
        self.assertFalse(output.exists())

    def test_live_unsealed_updates_fail_before_output_and_never_use_source(self):
        output = self.root / "tampered"
        with patch.object(release, "urlopen", side_effect=self.responses(updates=self.updates_payload + b" ")):
            with patch.object(release, "extract_baseline") as extract:
                with self.assertRaises(ValueError):
                    release.live_baseline(self.root, output)
                extract.assert_not_called()
        self.assertFalse(output.exists())

    def test_live_missing_payload_metadata_cannot_complete_a_baseline(self):
        self.manifest.pop("initial_payloads")
        output = self.root / "missing-payloads"
        with patch.object(release, "urlopen", side_effect=self.responses()):
            with self.assertRaises(ValueError):
                release.live_baseline(self.root, output)
        self.assertFalse(output.exists())

    def test_bootstrap_exception_applies_only_when_the_release_itself_is_absent(self):
        catalog = self.encode({"revision": release.BOOTSTRAP_REVISION, "articles": []})
        manifest = copy.deepcopy(self.manifest)
        manifest.update(revision=release.BOOTSTRAP_REVISION,
                        catalog_sha256=hashlib.sha256(catalog).hexdigest())
        missing_updates = HTTPError(release.LIVE_UPDATES, 404, "Not Found", {}, None)
        with patch.object(release, "urlopen", side_effect=[
                io.BytesIO(catalog), io.BytesIO(self.encode(manifest)), missing_updates]):
            with patch.object(release, "extract_baseline") as extract:
                with self.assertRaises((ValueError, HTTPError)):
                    release.live_baseline(self.root, self.root / "modern-bootstrap")
                extract.assert_not_called()


if __name__ == "__main__":
    unittest.main()
