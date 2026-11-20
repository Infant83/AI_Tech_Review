"""Local preflight contract on temporary Git repositories; no live providers."""
from __future__ import annotations

import copy
from contextlib import ExitStack, redirect_stdout
import hashlib
import inspect
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import admin_requests as requests
from scripts.admin_inventory import PublicReview, PublicTranslation, PublicAgent
from scripts.publication_intent import review_inputs
from scripts.review_registry import validate_review_registration, load_review_registry


class RequestPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        # macOS tempfile may use a /var alias; Git reports the physical root.
        self.base = Path(self.temp.name).resolve()
        self.root, self.baseline = self.base / "source", self.base / "baseline"
        self.root.mkdir(); self.baseline.mkdir()
        self.folder = "2026-11-01_example-review"
        for name in ["scripts", "publication/reviews", "publication/requests", "publication_changes"]:
            (self.root / name).mkdir(parents=True)
        models = "from __future__ import annotations\nfrom dataclasses import dataclass\n\n" + "\n\n".join(
            inspect.getsource(model) for model in (PublicTranslation, PublicAgent, PublicReview))
        (self.root / "scripts/publish_public_site.py").write_text(models, encoding="utf-8")
        self.registration = {"version": 1, "review": {
            "folder": self.folder, "title": "Protected title", "subtitle": "Original subtitle",
            "date": "2026-11-01", "updated": "2026-11-01", "category": "Quantum", "tags": ["science"],
            "summary": "Original summary", "translations": [{"language": "en", "subdir": "en", "label": "English"}]}}
        self.registration_path = self.root / "publication/reviews" / (self.folder + ".json")
        self.save(self.registration_path, self.registration)
        dist = self.root / self.folder / "dist"
        (dist / "en").mkdir(parents=True)
        (dist / "index.html").write_text("Private synthetic source manuscript", encoding="utf-8")
        (dist / "en/index.html").write_text("Private synthetic translated manuscript", encoding="utf-8")
        self.intent_path = self.root / "publication/requests" / (self.folder + ".json")
        self.save(self.intent_path, {"version": 2, "review": self.folder, **review_inputs(self.root, self.folder)})
        self.references = ["reviews/" + self.folder + suffix for suffix in ["/index.html", "/en/index.html"]]
        sha = hashlib.sha256(b"Reviewed public bytes").hexdigest()
        self.change_path = self.root / "publication_changes/review.json"
        self.change = {"version": 1, "reason": "Synthetic reviewed output binding", "files": {
            name: {"before": sha, "after": sha} for name in self.references}}
        self.save(self.change_path, self.change)
        self.snapshot = {"version": 1, "reviews": {self.folder: {
            "href": self.references[0], "metric_path": "/AI_Tech_Review/reviews/" + self.folder + "/",
            "translations": {"en": {"href": self.references[1], "metric_path": None}},
            "date": "2026-11-01", "references": self.references}}, "archive": {}, "external": {},
            "publications": {self.folder: {"path": "/AI_Tech_Review/reviews/" + self.folder + "/",
                                           "topic": "review", "publishedAt": "2026-11-01"}},
            "files": {name: {"sha256": sha, "content_sha256": sha, "bytes": 21} for name in self.references},
            "missing_files": [], "declared_hash_mismatches": []}
        self.catalog = {"revision": "a" * 40, "articles": [{"id": self.folder,
                        "path": "/AI_Tech_Review/reviews/" + self.folder + "/", "topic": "review",
                        "title": "Protected title", "publishedAt": "2026-11-01"}]}
        self.updates = {"version": 1, "pages": {}, "articles": []}
        self.write_baseline()
        self.git("init", "-q")
        self.commit()
        self.request_path = self.base / "request.json"
        self.request = {"schemaVersion": 1, "operation": requests.OPERATION, "sourceId": self.folder,
                        "expectedSourceRevision": self.head(), "expectedInputs": review_inputs(self.root, self.folder),
                        "expectedReleaseRevision": self.catalog["revision"], "expectedReleaseEvidence": self.evidence(),
                        "patch": {"summary": "A revised summary"},
                        "idempotencyKey": "8b831813-81ca-4b64-a5b3-ea6c93cffbc0"}
        self.save_request()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.DEVNULL, text=True).strip()

    def commit(self):
        self.git("add", "--all")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "-c", "core.hooksPath=/dev/null",
                 "commit", "-qm", "Fixture inputs")

    def head(self):
        return self.git("rev-parse", "HEAD")

    def save(self, path, value):
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def save_request(self):
        self.save(self.request_path, self.request)

    def evidence(self):
        return {key: hashlib.sha256((self.baseline / name).read_bytes()).hexdigest() for key, name in [
            ("releaseSha256", "release.json"), ("catalogSha256", "reader-publications.json"),
            ("updatesSha256", "reader-updates.json")]}

    def write_baseline(self):
        self.save(self.baseline / "snapshot.json", self.snapshot)
        self.save(self.baseline / "reader-publications.json", self.catalog)
        self.save(self.baseline / "reader-updates.json", self.updates)
        release = {"version": 1, "revision": self.catalog["revision"], "snapshot": self.snapshot,
                   "catalog_sha256": hashlib.sha256((self.baseline / "reader-publications.json").read_bytes()).hexdigest(),
                   "initial_payloads": {}, "artifact_files": {
                       name: {"sha256": record["sha256"], "bytes": record["bytes"]}
                       for name, record in self.snapshot["files"].items()}}
        for name in ["reader-publications.json", "reader-updates.json"]:
            raw = (self.baseline / name).read_bytes()
            release["artifact_files"][name] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        self.save(self.baseline / "release.json", release)

    def run_preflight(self):
        return requests.preflight_request(self.root, self.request_path, self.baseline / "snapshot.json")

    def rejected(self, reason=None, call=None):
        with self.assertRaises(requests.PreflightError) as caught:
            (call or self.run_preflight)()
        if reason:
            self.assertEqual(caught.exception.code, reason)
        message = str(caught.exception)
        for forbidden in [str(self.base), "Private synthetic", "A revised summary", "Protected title"]:
            self.assertNotIn(forbidden, message)
        return caught.exception.code

    def files(self):
        return {str(p.relative_to(self.base)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.base.rglob("*") if p.is_file() and ".git" not in p.parts}

    def test_valid_request_is_local_and_all_inputs_and_git_remain_unchanged(self):
        before, head = self.files(), self.head()
        real_run = subprocess.run
        def readonly_git(command, **kwargs):
            self.assertEqual(command[0], "git")
            self.assertIn(command[1], ["rev-parse", "ls-tree"])
            return real_run(command, **kwargs)
        with ExitStack() as stack:
            for target in ["pathlib.Path.write_text", "pathlib.Path.write_bytes", "os.replace", "socket.create_connection",
                           "urllib.request.urlopen"]:
                stack.enter_context(patch(target, side_effect=AssertionError("Unexpected side effect")))
            stack.enter_context(patch("subprocess.run", side_effect=readonly_git))
            result = self.run_preflight()
        self.assertEqual(result["status"], "validated_preflight_only")
        self.assertEqual(result["changedFields"], ["summary"])
        self.assertEqual(result["baselineOrigin"], "provided_local_verified_bundle")
        self.assertEqual(result["sourceRevision"], head)
        self.assertNotEqual(result["sourceRevision"], result["releaseRevision"])
        for forbidden in [str(self.base), "Private synthetic", "A revised summary", "Protected title", "idempotencyKey"]:
            self.assertNotIn(forbidden, json.dumps(result))
        self.assertEqual(self.files(), before); self.assertEqual(self.head(), head)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_same_patch_returns_no_change_and_keys_do_not_change_fingerprint(self):
        self.request["patch"] = {"summary": "Original summary"}; self.save_request()
        result = self.run_preflight(); self.assertEqual(result["status"], "no_change")
        self.assertEqual(result["changedFields"], [])
        self.request["idempotencyKey"] = "b709cc2b-5579-482b-ab9f-120fcf747493"; self.save_request()
        self.assertEqual(self.run_preflight()["requestFingerprint"], result["requestFingerprint"])
        self.request["patch"]["summary"] += " "; self.save_request()
        self.assertNotEqual(self.run_preflight()["requestFingerprint"], result["requestFingerprint"])

    def test_fingerprint_ignores_json_key_order_but_keeps_exact_editorial_unicode(self):
        first = self.run_preflight()["requestFingerprint"]
        self.request_path.write_text(json.dumps(self.request, sort_keys=True, separators=(",", ":")))
        self.assertEqual(self.run_preflight()["requestFingerprint"], first)
        self.request["patch"] = {"summary": "é"}; self.save_request(); composed = self.run_preflight()["requestFingerprint"]
        self.request["patch"] = {"summary": "e\u0301"}; self.save_request()
        self.assertNotEqual(self.run_preflight()["requestFingerprint"], composed)

    def test_parser_rejects_duplicates_constants_utf8_surrogates_unknown_and_types(self):
        valid = json.dumps(self.request).encode()
        bad = [b"\xff", b"{", b"[]", valid.replace(b'"schemaVersion": 1', b'"schemaVersion": true'),
               valid[:-1] + b',"schemaVersion":1}', valid.replace(b'"summary": "A revised summary"', b'"summary": NaN'),
               valid.replace(b'"summary": "A revised summary"', b'"summary": Infinity'),
               valid.replace(b'"summary": "A revised summary"', b'"summary": "\\ud800"')]
        for raw in bad:
            with self.subTest(raw=raw[:40]):
                self.rejected("invalid_request", lambda: requests.parse_request(raw))
        for key, value in [("actor", "editor"), ("sourceId", "review:" + self.folder), ("sourceId", "../source"),
                           ("expectedInputs", {}), ("expectedReleaseEvidence", {}), ("idempotencyKey", "not-a-uuid"),
                           ("expectedSourceRevision", True), ("schemaVersion", "1")]:
            bad_request = {**self.request, key: value}
            self.rejected("invalid_request", lambda: requests.parse_request(json.dumps(bad_request).encode()))

    def test_patch_limits_types_and_protected_fields_fail_without_truncation(self):
        for patch_value in [{}, {"title": "Forbidden"}, {"summary": None}, {"summary": 4}, {"tags": "tag"},
                            {"tags": [False]}, {"tags": ["x"] * 41}, {"tags": ["x" * 201]},
                            {"summary": "x" * 8001}, {"subtitle": "x" * 1001}, {"category": "x" * 201}]:
            value = {**self.request, "patch": patch_value}
            self.rejected(call=lambda: requests.parse_request(json.dumps(value).encode()))
        for field in requests.FIELD_LIMITS:
            self.request["patch"] = {field: "x" * requests.FIELD_LIMITS[field]}; self.save_request()
            self.assertTrue(self.run_preflight()["ok"])
        self.request["patch"] = {"tags": ["x" * 200] * 40}; self.save_request()
        self.assertTrue(self.run_preflight()["ok"])
        self.rejected("request_limit", lambda: requests.parse_request(b" " * 32001))
        self.request_path.write_bytes(b" " * 32001); self.rejected("request_limit")

    def test_native_merged_validation_rejects_empty_control_and_invalid_tags(self):
        before = self.files()
        for bad_patch in [{"summary": ""}, {"summary": "line\nbreak"}, {"tags": [""]}, {"category": "\x00"}]:
            self.request["patch"] = bad_patch; self.save_request(); self.rejected("invalid_request")
        self.assertEqual({k: v for k, v in self.files().items() if k != "request.json"},
                         {k: v for k, v in before.items() if k != "request.json"})

    def test_source_revision_and_each_target_hash_are_separate_conflicts(self):
        original = copy.deepcopy(self.request)
        self.request["expectedSourceRevision"] = "b" * 40; self.save_request(); self.rejected("source_conflict")
        for key in requests.INPUT_KEYS:
            self.request = copy.deepcopy(original); self.request["expectedInputs"][key] = "b" * 64
            self.save_request(); self.rejected("input_conflict")

    def test_initialization_and_current_source_must_be_verified(self):
        (self.root / ".git").rename(self.root / ".git-unavailable")
        self.rejected("source_not_verified")
        (self.root / "scripts/publish_public_site.py").unlink()
        self.rejected("required_input_missing")

    def test_missing_v1_and_changed_protected_intents_require_real_revalidation(self):
        original = self.intent_path.read_bytes()
        self.intent_path.unlink(); self.rejected("revalidation_required")
        record = json.loads(original); record["version"] = 1; del record["article_registration_sha256"]
        self.save(self.intent_path, record); self.rejected("revalidation_required")
        record = json.loads(original); record["source_sha256"] = "b" * 64
        self.save(self.intent_path, record); self.rejected("revalidation_required")

    def test_changed_hub_metadata_can_keep_v2_article_binding_but_dirty_source_is_not_a_commit(self):
        self.registration["review"]["subtitle"] = "A previously revised hub subtitle"
        self.save(self.registration_path, self.registration)
        self.request["expectedInputs"] = review_inputs(self.root, self.folder); self.save_request()
        self.rejected("source_not_verified")
        self.commit(); self.request["expectedSourceRevision"] = self.head(); self.save_request()
        self.assertEqual(self.run_preflight()["status"], "validated_preflight_only")

    def test_missing_partial_wrong_declarations_or_unpublished_target_are_not_invented(self):
        original = self.change_path.read_bytes()
        self.change_path.unlink(); self.rejected("revalidation_required")
        for names in [[self.references[0]], self.references]:
            value = copy.deepcopy(self.change); value["files"] = {k: v for k, v in value["files"].items() if k in names}
            if names == self.references:
                value["files"][names[0]]["after"] = "b" * 64
            self.save(self.change_path, value); self.rejected("revalidation_required")
        self.change_path.write_bytes(original)
        del self.snapshot["reviews"][self.folder]; self.write_baseline()
        self.request["expectedReleaseEvidence"] = self.evidence(); self.save_request()
        self.rejected("revalidation_required")

    def test_unchanged_undeclared_attachment_does_not_need_a_new_review_declaration(self):
        payload = b"<svg>Unchanged reviewed source figure</svg>"
        (self.root / self.folder / "dist/figure.svg").write_bytes(payload)
        self.save(self.intent_path, {"version": 2, "review": self.folder, **review_inputs(self.root, self.folder)})
        self.commit(); self.request["expectedSourceRevision"] = self.head()
        self.request["expectedInputs"] = review_inputs(self.root, self.folder)
        asset = "reviews/" + self.folder + "/figure.svg"
        sha = hashlib.sha256(payload).hexdigest()
        self.snapshot["reviews"][self.folder]["references"].append(asset)
        self.snapshot["files"][asset] = {"sha256": sha, "content_sha256": sha, "bytes": len(payload)}
        self.write_baseline(); self.request["expectedReleaseEvidence"] = self.evidence(); self.save_request()
        self.assertTrue(self.run_preflight()["ok"])
        # Once an asset has an explicit reviewed after hash, disagreement fails.
        self.change["files"][asset] = {"before": sha, "after": "b" * 64}
        self.save(self.change_path, self.change); self.rejected("revalidation_required")

    def test_same_source_revision_different_raw_bundle_rejects_until_explicitly_refreshed(self):
        original = self.request["expectedReleaseEvidence"].copy()
        # Valid metadata whitespace changes its raw seal without changing revision.
        release = json.loads((self.baseline / "release.json").read_text())
        (self.baseline / "release.json").write_text(json.dumps(release, separators=(",", ":")))
        self.rejected("release_changed")
        self.request["expectedReleaseEvidence"] = self.evidence(); self.save_request()
        refreshed = self.run_preflight(); self.assertEqual(refreshed["releaseRevision"], "a" * 40)
        self.assertNotEqual(refreshed["releaseEvidence"], original)
        self.request["expectedReleaseRevision"] = "b" * 40; self.save_request(); self.rejected("release_changed")

    def test_each_raw_release_hash_and_missing_corrupt_mixed_baseline_fail(self):
        for key in requests.RELEASE_KEYS:
            old = self.request["expectedReleaseEvidence"][key]
            self.request["expectedReleaseEvidence"][key] = "b" * 64; self.save_request(); self.rejected("release_changed")
            self.request["expectedReleaseEvidence"][key] = old
        self.save_request()
        p = self.baseline / "reader-updates.json"; raw = p.read_bytes()
        p.unlink(); self.rejected()
        p.write_bytes(b"{}"); self.rejected()
        p.write_bytes(raw)
        release = json.loads((self.baseline / "release.json").read_text()); release["snapshot"]["reviews"][self.folder]["date"] = "2026-11-02"
        self.save(self.baseline / "release.json", release); self.rejected()

    def test_symlinks_for_request_source_root_and_baseline_are_rejected(self):
        alias = self.base / "request-link.json"; alias.symlink_to(self.request_path)
        self.rejected("input_symlink", lambda: requests.preflight_request(self.root, alias, self.baseline / "snapshot.json"))
        alias = self.base / "root-link"; alias.symlink_to(self.root, target_is_directory=True)
        self.rejected("input_symlink", lambda: requests.preflight_request(alias, self.request_path, self.baseline / "snapshot.json"))
        raw = (self.baseline / "snapshot.json").read_bytes(); (self.baseline / "snapshot.json").unlink()
        other = self.base / "copy.json"; other.write_bytes(raw); (self.baseline / "snapshot.json").symlink_to(other)
        self.rejected("input_symlink")

    def test_reading_time_file_and_registration_membership_changes_fail(self):
        original = requests._Inputs.verify
        def change(tracker):
            self.registration_path.write_text(self.registration_path.read_text() + " ")
            return original(tracker)
        with patch.object(requests._Inputs, "verify", change):
            self.rejected("input_changed")
        # Restore the registered bytes, then inject another entry during final check.
        self.save(self.registration_path, self.registration)
        def add(tracker):
            self.save(self.root / "publication/reviews/new.json", {})
            return original(tracker)
        with patch.object(requests._Inputs, "verify", add):
            self.rejected("input_changed")

    def test_head_changes_during_preflight_do_not_pass_with_old_expected_revision(self):
        original = requests._Inputs.verify
        def advance(tracker):
            original(tracker)
            (self.root / "unrelated.txt").write_text("Concurrent change")
            self.commit()
        with patch.object(requests._Inputs, "verify", advance):
            self.rejected("input_changed")

    def aba_native_read(self, kind):
        """Only fixture files temporarily change while the native reader runs."""
        native = requests.review_inputs
        target = (self.root / self.folder / "dist/index.html" if kind == "source"
                  else self.registration_path)
        original = target.read_bytes()
        if kind == "source":
            transient = original + b" transient source edit"
        else:
            edited = copy.deepcopy(self.registration)
            edited["review"]["subtitle" if kind == "hub" else "title"] += " transient edit"
            transient = (json.dumps(edited, ensure_ascii=False, indent=2) + "\n").encode()
        def read_transient(root, folder):
            self.assertEqual(target.read_bytes(), original)
            target.write_bytes(transient)
            try:
                return native(root, folder)
            finally:
                target.write_bytes(original)
        inputs_b = read_transient(self.root, self.folder)
        # Source/protected cases retain a v2 record for B while Git/file bytes
        # contain A. Previously a transient native B read could certify it.
        if kind != "hub":
            self.save(self.intent_path, {"version": 2, "review": self.folder, **inputs_b})
            self.commit()
        self.request["expectedSourceRevision"] = self.head()
        self.request["expectedInputs"] = inputs_b
        self.request["patch"] = {"summary": self.registration["review"]["summary"]}
        self.save_request()
        before, head, status = self.files(), self.head(), self.git("status", "--porcelain")
        with patch.object(requests, "review_inputs", side_effect=read_transient) as called:
            self.rejected("input_changed")
        self.assertEqual(called.call_count, 1)
        self.assertEqual(self.files(), before)
        self.assertEqual(self.head(), head)
        self.assertEqual(self.git("status", "--porcelain"), status)

    def test_hub_registration_aba_native_read_is_not_the_tracked_registration(self):
        self.aba_native_read("hub")

    def test_protected_registration_aba_native_read_is_not_the_tracked_protected_input(self):
        self.aba_native_read("protected")

    def test_source_aba_native_read_is_not_the_tracked_source_input(self):
        self.aba_native_read("source")

    def test_native_path_component_sort_with_directory_and_hyphen_file_remains_valid(self):
        (self.root / self.folder / "dist/en-guide.png").write_bytes(b"Reviewed shared-prefix source file")
        self.save(self.intent_path, {"version": 2, "review": self.folder, **review_inputs(self.root, self.folder)})
        self.commit()
        self.request["expectedSourceRevision"] = self.head()
        self.request["expectedInputs"] = review_inputs(self.root, self.folder)
        self.save_request()
        self.assertTrue(self.run_preflight()["ok"])

    def test_native_pure_validator_does_not_mutate_inputs_or_seen_sets(self):
        source = copy.deepcopy(self.registration); folders, positions = set(), set()
        row = validate_review_registration(source, self.folder + ".json", PublicReview, PublicTranslation, PublicAgent,
                                           folders=folders, positions=positions)
        self.assertEqual(source, self.registration); self.assertEqual((folders, positions), (set(), set()))
        self.assertEqual(row[2], load_review_registry(self.root / "publication/reviews", PublicReview, PublicTranslation, PublicAgent)[0])

    def test_cli_stdout_is_sanitized_and_never_creates_an_output_file(self):
        script = Path(requests.__file__)
        before = self.files()
        result = subprocess.run([sys.executable, str(script), "--root", str(self.root), "--request", str(self.request_path),
                                 "--baseline-snapshot", str(self.baseline / "snapshot.json")], capture_output=True, text=True,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, check=False)
        self.assertEqual(result.returncode, 0, result.stderr); self.assertEqual(result.stderr, "")
        self.assertEqual(json.loads(result.stdout)["status"], "validated_preflight_only")
        self.assertNotIn(str(self.base), result.stdout); self.assertNotIn("A revised summary", result.stdout)
        self.assertEqual(self.files(), before)
        stream = io.StringIO()
        with redirect_stdout(stream):
            self.assertEqual(requests.main(["--root", "/private/synthetic-path"]), 1)
        self.assertEqual(json.loads(stream.getvalue()), {"schemaVersion": 1, "ok": False, "reason": "invalid_arguments"})


if __name__ == "__main__":
    unittest.main()
