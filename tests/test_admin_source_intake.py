"""Actual small source Git fixtures; no provider/network or production mutations."""
from contextlib import redirect_stdout
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import admin_request_jobs as jobs
from scripts import admin_source_intake as intake
from scripts import admin_requests
from scripts import admin_inventory
from scripts.publication_intent import review_inputs


class SourceIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name).resolve(); (self.parent / ".keep").write_bytes(b"")
        self.fixture = self.parent / "fixture"; jobs.initialize_sandbox(self.fixture)
        self.source = self.fixture / "repo"; self.request = self.fixture / "example-request.json"
        self.baseline = self.fixture / "baseline/snapshot.json"
        self.data = json.loads(self.request.read_text()); self.number = 0

    def call(self, source=None):
        self.number += 1; output = self.parent / ("output-" + str(self.number))
        report = intake.create_intake(source or self.source, self.request, self.baseline, output)
        return report, json.loads((output / "descriptor.json").read_text())

    def reject(self, reason=None):
        with self.assertRaises(intake.IntakeError) as caught:
            self.call()
        if reason: self.assertEqual(caught.exception.code, reason)
        self.assertNotIn(str(self.parent), str(caught.exception))
        return caught.exception.code

    def snapshot(self):
        return {p.relative_to(self.fixture).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.fixture.rglob("*") if p.is_file()}

    def commit(self):
        # Fixture-only source edits become new immutable Git objects explicitly.
        files = {p.relative_to(self.source).as_posix(): p.read_bytes()
                 for p in self.source.rglob("*") if p.is_file() and ".git" not in p.relative_to(self.source).parts}
        tree = jobs._tree(self.source, files)
        old = jobs._ref(self.source, "refs/heads/main")
        revision = jobs._commit(self.source, tree, {"synthetic": "test change"}, old)
        jobs._git(self.source, "update-ref", "refs/heads/main", revision, old)
        jobs._git(self.source, "read-tree", revision)
        return revision

    def test_same_frozen_native_inputs_deterministic_descriptor_and_source_unchanged(self):
        original = self.snapshot()
        expected = admin_requests.preflight_request(self.source, self.request, self.baseline)
        one, first = self.call(); two, second = self.call()
        self.assertEqual(one["intakeDigest"], two["intakeDigest"])
        self.assertEqual(first["checkedInputs"], expected["checkedInputs"])
        self.assertEqual(first["checkedInputs"], review_inputs(self.source, jobs.FOLDER))
        self.assertEqual(first["releaseEvidence"], expected["releaseEvidence"])
        self.assertEqual(first["sourceOriginRevision"], expected["sourceRevision"])
        self.assertEqual(first["requestFingerprint"], expected["requestFingerprint"])
        self.assertEqual(original, self.snapshot())
        for value in [str(self.parent), "Synthetic B1 candidate summary", "idempotencyKey", "candidateRevision"]:
            self.assertNotIn(value, json.dumps(first))
        self.assertEqual(len(first["inputs"]), 6)
        self.assertLess(len(json.dumps(one)), intake.MAX_STDOUT_BYTES)

    def test_linked_worktree_is_supported_without_sharing_candidate_or_writing_source(self):
        linked = self.parent / "linked"
        jobs._git(self.source, "worktree", "add", "--detach", str(linked), self.data["expectedSourceRevision"])
        original = self.snapshot()
        _, standalone = self.call()
        _, descriptor = self.call(linked)
        self.assertEqual(descriptor["sourceOriginRevision"], self.data["expectedSourceRevision"])
        self.assertEqual(original, self.snapshot())
        self.assertEqual(standalone["intakeDigest"], descriptor["intakeDigest"])

    def test_dirty_selected_input_and_untracked_ledger_member_are_refused(self):
        path = self.source / "publication/reviews" / (jobs.FOLDER + ".json")
        original = path.read_bytes(); value = json.loads(original)
        value["review"]["summary"] = "Uncommitted synthetic edit"; path.write_bytes(jobs._raw(value))
        self.reject(); path.write_bytes(original)
        extra = path.parent / "extra.txt"; extra.write_bytes(b"untracked")
        self.reject(); extra.unlink()
        unrelated = self.source / "unrelated-foreign.txt"; unrelated.write_bytes(b"preserve")
        self.assertTrue(self.call()[0]["ok"]); self.assertEqual(unrelated.read_bytes(), b"preserve")

    def test_head_advancement_is_not_silently_rebased(self):
        self.commit(); self.reject("source_conflict")

    def test_source_change_during_final_revalidation_is_refused(self):
        real = intake._BoundedInputs.verify
        def advance(reader):
            result = real(reader); self.commit(); return result
        with patch.object(intake._BoundedInputs, "verify", side_effect=advance, autospec=True):
            self.reject("source_conflict")

    def test_baseline_missing_or_same_revision_different_raw_bundle_never_reuses_descriptor(self):
        self.call()
        path = self.baseline.parent / "reader-publications.json"; raw = path.read_bytes()
        path.unlink(); self.reject(); path.write_bytes(raw + b" "); self.reject()
        path.write_bytes(raw)
        self.data["expectedReleaseEvidence"]["releaseSha256"] = "b" * 64
        self.request.write_bytes(jobs._raw(self.data)); self.reject("release_changed")

    def test_model_is_AST_data_never_imported_and_schema_drift_is_refused(self):
        model = self.source / "scripts/publish_public_site.py"
        model.write_bytes(model.read_bytes() + b'\nraise RuntimeError("NEVER EXECUTE SOURCE")\n')
        self.data["expectedSourceRevision"] = self.commit(); self.request.write_bytes(jobs._raw(self.data))
        self.assertTrue(self.call()[0]["ok"])
        model.write_bytes(model.read_bytes().replace(b"    title: str", b"    title: int"))
        self.data["expectedSourceRevision"] = self.commit(); self.request.write_bytes(jobs._raw(self.data))
        self.reject("review_model_schema_changed")

    def test_unsafe_source_config_rejected_before_git_and_inherited_settings_ignored(self):
        config = self.source / ".git/config"; original = config.read_bytes()
        config.write_bytes(original + b'\n[include]\npath=/never-open-private-config\n')
        with patch.object(intake._GitSource, "run", side_effect=AssertionError("Git must not parse unsafe config")):
            self.reject("unsafe_git_config")
        config.write_bytes(original)
        with patch.dict(os.environ, {"GIT_DIR": "/never-open.git", "GIT_CONFIG_PARAMETERS": "malformed",
                "GIT_CONFIG_GLOBAL": "/never-open", "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/never-read"}):
            self.assertTrue(self.call()[0]["ok"])

    def test_promisor_alternates_replace_and_missing_object_are_refused(self):
        config = self.source / ".git/config"; original = config.read_bytes()
        config.write_bytes(original + b'\n[remote "origin"]\nurl=https://example.invalid/never-fetch\npromisor=true\n')
        self.reject("unsafe_git_config"); config.write_bytes(original)
        alternate = self.source / ".git/objects/info/alternates"; alternate.write_text("/never-read\n")
        self.reject("unsafe_source_objects"); alternate.unlink()
        jobs._git(self.source, "update-ref", "refs/replace/" + self.data["expectedSourceRevision"], self.data["expectedSourceRevision"])
        self.reject("unsafe_source_objects")
        jobs._git(self.source, "update-ref", "-d", "refs/replace/" + self.data["expectedSourceRevision"])
        oid = jobs._git(self.source, "rev-parse", self.data["expectedSourceRevision"] + ":scripts/publish_public_site.py").decode().strip()
        object_path = self.source / ".git/objects" / oid[:2] / oid[2:]
        object_path.unlink(); self.reject()

    def test_source_actual_commit_type_and_dirty_mode_are_refused(self):
        head = self.source / ".git/HEAD"; old = head.read_bytes()
        tag = jobs._git(self.source, "mktag", raw=(f'object {self.data["expectedSourceRevision"]}\ntype commit\ntag wrapper\n'
            'tagger Synthetic <fixture@example.invalid> 946684800 +0000\n\nwrapper\n').encode()).strip()
        head.write_bytes(tag + b"\n"); self.reject("source_commit_required"); head.write_bytes(old)
        path = self.source / "scripts/publish_public_site.py"; path.chmod(0o755)
        self.reject("source_not_verified")

    def test_tree_dist_blob_IO_descriptor_and_deadline_budgets_fail_closed(self):
        limits = [("MAX_TREE_ENTRIES", 1), ("MAX_TREE_BYTES", 100), ("MAX_DIST_FILES", 1),
                  ("MAX_DIST_BYTES", 1), ("MAX_BLOB_BYTES", 1), ("MAX_READ_BYTES", 1),
                  ("MAX_DESCRIPTOR_BYTES", 1), ("TOTAL_SECONDS", -1)]
        for name, value in limits:
            with self.subTest(name=name), patch.object(intake, name, value):
                self.reject()

    def test_no_output_overwrite_and_partial_output_remains_protected(self):
        output = self.parent / "existing"; output.mkdir(); (output / "marker").write_bytes(b"preserve")
        with self.assertRaises(intake.IntakeError):
            intake.create_intake(self.source, self.request, self.baseline, output)
        self.assertEqual((output / "marker").read_bytes(), b"preserve")
        with patch.object(intake.os, "link", side_effect=OSError("private synthetic fault")):
            self.reject("invalid_intake_input")
        partial = self.parent / ("output-" + str(self.number))
        self.assertTrue((partial / ".keep").exists()); self.assertTrue((partial / ".descriptor.partial").exists())
        self.assertFalse((partial / "descriptor.json").exists())

    def test_exact_descriptor_and_selected_path_limits_accept_then_one_less_refuses(self):
        report, descriptor = self.call()
        size = (self.parent / "output-1/descriptor.json").stat().st_size
        with patch.object(intake, "MAX_DESCRIPTOR_BYTES", size), \
             patch.object(intake, "MAX_DIST_FILES", descriptor["counts"]["distFiles"]), \
             patch.object(intake, "MAX_DIST_BYTES", descriptor["counts"]["distBytes"]):
            self.assertEqual(self.call()[0]["intakeDigest"], report["intakeDigest"])
        with patch.object(intake, "MAX_DESCRIPTOR_BYTES", size - 1):
            self.reject("descriptor_limit")

    def test_actual_child_timeout_is_killed_without_source_writes(self):
        original = self.snapshot()
        actual = subprocess.Popen
        def slow(command, **kwargs):
            return actual([sys.executable, "-B", "-c", "import time;time.sleep(5)"], **kwargs)
        with patch.object(intake.subprocess, "Popen", side_effect=slow), patch.object(intake, "GIT_SECONDS", .05):
            self.reject("git_timeout")
        self.assertEqual(original, self.snapshot())

    def test_frozen_native_paths_avoid_second_registry_hash_declaration_reads(self):
        with patch.object(admin_requests, "load_review_registry", side_effect=AssertionError("no native reread")), \
             patch.object(admin_requests, "declarations", side_effect=AssertionError("no native reread")):
            self.assertTrue(self.call()[0]["ok"])

    def test_frozen_registry_duplicates_and_declaration_schema_match_native(self):
        path = self.source / "publication_changes/fixture.json"; value = json.loads(path.read_text())
        value["unknown"] = True; path.write_bytes(jobs._raw(value))
        self.reject("invalid_change_declaration")
        # This reaches in-memory native registration validation before Git binding.
        registration = self.source / "publication/reviews" / (jobs.FOLDER + ".json")
        original = json.loads(registration.read_text()); original["legacy_position"] = 1
        registration.write_bytes(jobs._raw(original)); other = copy.deepcopy(original)
        other["review"]["folder"] = "2026-11-21_other-review"
        (registration.parent / "2026-11-21_other-review.json").write_bytes(jobs._raw(other))
        self.reject()

    def test_CLI_error_is_small_and_never_echoes_paths_or_values(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = intake.main(["--root", "/private/synthetic-location"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(stream.getvalue())["reason"], "invalid_arguments")
        self.assertNotIn("private", stream.getvalue()); self.assertLess(len(stream.getvalue()), intake.MAX_STDOUT_BYTES)

    def test_shared_reader_bounds_JSON_growth_before_initial_hash_read(self):
        for already in [0, 14]:
            with self.subTest(already=already):
                path = self.parent / ("growth-" + str(already) + ".json"); path.write_bytes(b"{}")
                budget = intake._Budget(); reader = intake._BoundedInputs(self.source, budget)
                reader.json_total = already
                actual = reader._chunks; grown = []
                def grow(p, limit=None):
                    if not grown:
                        path.write_bytes(b'{"x":123456789}'); grown.append(True)
                    yield from actual(p, limit)
                with patch.object(intake, "MAX_JSON_FILE_BYTES", 8), \
                     patch.object(admin_inventory, "MAX_JSON_FILE_BYTES", 8), \
                     patch.object(admin_inventory, "MAX_JSON_TOTAL_BYTES", 16), \
                     patch.object(reader, "_chunks", side_effect=grow):
                    with self.assertRaises(ValueError): reader.json(path, boundary=self.parent)
                self.assertLessEqual(budget.read_bytes, min(8, 16 - already) + 1)

    def test_shared_reader_streams_directory_enumeration_and_caps_unique_entries(self):
        with patch.object(Path, "iterdir", side_effect=AssertionError("B2 directory reads must stream")):
            self.assertTrue(self.call()[0]["ok"])
        reader = intake._BoundedInputs(self.source, intake._Budget())
        one, two = self.parent / "wide-one", self.parent / "wide-two"
        for directory in [one, two]:
            directory.mkdir()
            for name in ["a", "b"]: (directory / name).write_bytes(b"")
        with patch.object(intake, "MAX_TREE_ENTRIES", 3):
            reader.directory(one, boundary=self.parent)
            with self.assertRaises(intake.IntakeError): reader.directory(two, boundary=self.parent)


if __name__ == "__main__":
    unittest.main()
