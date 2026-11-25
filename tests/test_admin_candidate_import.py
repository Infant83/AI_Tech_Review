"""Small real source Git fixtures and local projection failure boundaries."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

from scripts import admin_candidate_import as importer
from scripts import admin_request_jobs as jobs
from scripts import admin_source_intake as intake


class CandidateImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name).resolve()
        (self.parent / ".keep").write_bytes(b"")
        self.fixture = self.parent / "fixture"; jobs.initialize_sandbox(self.fixture)
        self.source = self.fixture / "repo"; self.request = self.fixture / "example-request.json"
        self.baseline = self.fixture / "baseline/snapshot.json"
        self.store = self.parent / "projection-store"
        self.repository_id = str(uuid.uuid4()); self.principal = "trusted-local-test"
        self.initialize()

    def initialize(self):
        return importer.initialize_store(self.store, self.source, self.repository_id, self.principal)

    def call(self, source=None):
        return importer.import_projection(self.store, source or self.source, self.request, self.baseline,
                                          self.repository_id, self.principal)

    def inspect(self, digest, source=None):
        return importer.inspect_projection(self.store, digest, self.repository_id, self.principal, source)

    def snapshot(self, root=None):
        root = root or self.fixture
        return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob("*") if p.is_file()}

    def reject(self, reason=None):
        with self.assertRaises(importer.ImportError) as caught:
            self.call()
        if reason:
            self.assertEqual(caught.exception.code, reason)
        self.assertNotIn(str(self.parent), str(caught.exception))
        return caught.exception.code

    def git(self, *args):
        return jobs._git(self.source, "--git-dir=" + str(self.store / "git"), *args)

    def origin_advance(self):
        old = jobs._ref(self.source, "refs/heads/main")
        tree = jobs._git(self.source, "rev-parse", old + "^{tree}").decode().strip()
        new = jobs._commit(self.source, tree, {"synthetic": "unrelated source advance"}, old)
        jobs._git(self.source, "update-ref", "refs/heads/main", new, old)
        return new

    def commit_files(self):
        files = {p.relative_to(self.source).as_posix(): p.read_bytes() for p in self.source.rglob("*")
                 if p.is_file() and ".git" not in p.relative_to(self.source).parts}
        tree = jobs._tree(self.source, files); old = jobs._ref(self.source, "refs/heads/main")
        new = jobs._commit(self.source, tree, {"synthetic": "source stream fixture"}, old)
        jobs._git(self.source, "update-ref", "refs/heads/main", new, old)
        jobs._git(self.source, "read-tree", new)
        request = json.loads(self.request.read_text()); request["expectedSourceRevision"] = new
        self.request.write_bytes(jobs._raw(request)); return new

    def test_actual_projection_git_tree_modes_origin_mapping_and_source_preservation(self):
        before = self.snapshot(); result = self.call()
        self.assertEqual(result["status"], "source_projection_saved_local")
        self.assertNotEqual(result["sourceOriginRevision"], result["candidateBaseRevision"])
        self.assertEqual(before, self.snapshot())
        digest = result["projectionDigest"]
        intent = json.loads((self.store / "imports" / digest / "intent.json").read_text())
        raw = self.git("cat-file", "commit", result["candidateBaseRevision"])
        self.assertNotIn(b"\nparent ", raw)
        self.assertEqual(self.git("cat-file", "-t", result["candidateBaseRevision"]), b"commit\n")
        rows = self.git("ls-tree", "-r", "-l", "-z", result["candidateBaseRevision"])
        files = {}
        for row in rows.split(b"\0"):
            if row:
                meta, name = row.split(b"\t"); mode, kind, oid, size = meta.split()
                files[name.decode()] = (mode.decode(), oid.decode(), int(size))
        self.assertEqual(files, {e["path"]: (e["mode"], e["blob"], e["bytes"]) for e in intent["provenance"]["inputs"]})
        for entry in intent["provenance"]["inputs"]:
            raw = self.git("cat-file", "blob", entry["blob"])
            self.assertEqual(hashlib.sha256(raw).hexdigest(), entry["sha256"])
        self.assertEqual(self.git("fsck", "--strict", "--no-reflogs"), b"")
        self.assertTrue(self.inspect(digest)["attested"])
        for forbidden in [b"idempotencyKey", b"Synthetic B1 candidate summary", str(self.parent).encode()]:
            self.assertNotIn(forbidden, json.dumps(result).encode())
        self.assertFalse((self.store / "git/objects/info/alternates").exists())
        for path in self.store.rglob("*"):
            if path.is_file():
                self.assertEqual(path.stat().st_nlink, 1)

    def test_repeated_new_import_revalidates_then_inspects_same_projection_without_new_files(self):
        one = self.call(); before = self.snapshot(self.store)
        two = self.call()
        self.assertEqual(two["status"], "source_projection_already_present_local")
        self.assertEqual(one["candidateBaseRevision"], two["candidateBaseRevision"])
        self.assertEqual(before, self.snapshot(self.store))
        self.origin_advance(); self.reject("source_conflict")
        observed = self.inspect(one["projectionDigest"], self.source)
        self.assertTrue(observed["sourceAdvanced"])
        self.assertEqual(observed["status"], "historical_projection_present_local")

    def test_linked_source_is_read_without_candidate_sharing(self):
        linked = self.parent / "linked"
        revision = json.loads(self.request.read_text())["expectedSourceRevision"]
        jobs._git(self.source, "worktree", "add", "--detach", str(linked), revision)
        before = self.snapshot()
        result = self.call(linked)
        self.assertEqual(before, self.snapshot())
        common = self.git("rev-parse", "--git-common-dir").decode().strip()
        self.assertEqual(Path(common), self.store / "git")
        self.assertTrue(self.inspect(result["projectionDigest"])["attested"])

    def test_no_change_import_does_not_accept_key_or_apply_patch(self):
        data = json.loads(self.request.read_text())
        record = json.loads((self.source / "publication/reviews" / (jobs.FOLDER + ".json")).read_text())
        data["patch"] = {"summary": record["review"]["summary"]}
        self.request.write_bytes(jobs._raw(data))
        before = self.snapshot(); result = self.call()
        self.assertEqual(before, self.snapshot())
        self.assertTrue(result["attested"])
        self.assertFalse(any(p.name in {"claims", "inventory.json", "receipt.json"} for p in self.store.rglob("*")))
        intent = (self.store / "imports" / result["projectionDigest"] / "intent.json").read_text()
        self.assertNotIn(data["idempotencyKey"], intent)
        self.assertNotIn("idempotencyKey", intent)

    def test_dirty_input_baseline_mutation_and_origin_candidate_confusion_refused(self):
        path = self.source / "publication/reviews" / (jobs.FOLDER + ".json")
        raw = path.read_bytes(); path.write_bytes(raw + b" ")
        self.reject(); path.write_bytes(raw)
        result = self.call()
        data = json.loads(self.request.read_text()); data["expectedSourceRevision"] = result["candidateBaseRevision"]
        self.request.write_bytes(jobs._raw(data)); self.reject("source_conflict")
        data["expectedSourceRevision"] = result["sourceOriginRevision"]
        self.request.write_bytes(jobs._raw(data))
        path = self.baseline.parent / "reader-publications.json"; path.write_bytes(path.read_bytes() + b" ")
        self.reject()

    def test_store_namespace_epoch_and_other_source_are_not_reinitialized(self):
        result = self.call(); before = self.snapshot(self.store)
        with self.assertRaises(importer.ImportError):
            importer.inspect_projection(self.store, result["projectionDigest"], str(uuid.uuid4()), self.principal)
        with self.assertRaises(importer.ImportError):
            self.initialize()
        self.assertEqual(before, self.snapshot(self.store))
        another = self.parent / "another"; jobs.initialize_sandbox(another)
        with self.assertRaises(importer.ImportError) as caught:
            importer.import_projection(self.store, another / "repo", another / "example-request.json",
                another / "baseline/snapshot.json", self.repository_id, self.principal)
        self.assertEqual(caught.exception.code, "source_identity_conflict")
        identity = self.store / "identity.json"; identity.unlink()
        self.reject()
        self.assertFalse(identity.exists())

    def test_import_failures_preserve_intent_pin_mapping_and_require_explicit_inspect(self):
        for stage in ["after_intent", "after_objects", "after_pin", "after_mapping", "before_attestation", "after_attestation"]:
            with self.subTest(stage=stage):
                self.store = self.parent / ("store-" + stage); self.initialize()
                before = self.snapshot()
                def failure(at):
                    if at == stage:
                        raise OSError("private synthetic output fault")
                with patch.object(importer, "_checkpoint", side_effect=failure):
                    self.reject("outcome_unknown" if stage in {"after_pin", "after_mapping", "before_attestation", "after_attestation"} else "import_incomplete")
                self.assertEqual(before, self.snapshot())
                intents = list((self.store / "imports").glob("*/intent.json")); self.assertEqual(len(intents), 1)
                digest = intents[0].parent.name
                if stage in {"after_mapping", "before_attestation", "after_attestation"}:
                    result = self.inspect(digest)
                    self.assertEqual(result["attested"], stage == "after_attestation")
                    if stage != "after_attestation":
                        self.reject("outcome_unknown")
                else:
                    with self.assertRaises(importer.ImportError):
                        self.inspect(digest)
                self.assertTrue((self.store / ".keep").exists())

    def test_source_final_change_keeps_mapping_without_success_attestation(self):
        def advance(stage):
            if stage == "after_mapping":
                self.origin_advance()
        with patch.object(importer, "_checkpoint", side_effect=advance):
            self.reject("source_conflict")
        intent = next((self.store / "imports").glob("*/intent.json"))
        result = self.inspect(intent.parent.name, self.source)
        self.assertFalse(result["attested"]); self.assertTrue(result["sourceAdvanced"])
        self.assertFalse((intent.parent / "success.json").exists())

    def test_candidate_config_alternates_hardlink_missing_pin_and_corruption_refused(self):
        result = self.call(); original = self.snapshot(self.store)
        config = self.store / "git/config"; raw = config.read_bytes()
        config.write_bytes(raw + b'[remote "origin"]\nurl=https://example.invalid/never\n')
        self.reject("store_inconsistent"); config.write_bytes(raw)
        alternate = self.store / "git/objects/info"; alternate.mkdir(mode=0o700)
        with self.assertRaises(importer.ImportError):
            self.inspect(result["projectionDigest"])
        alternate.rmdir()
        intent = json.loads((self.store / "imports" / result["projectionDigest"] / "intent.json").read_text())
        oid = intent["provenance"]["inputs"][0]["blob"]
        object_path = self.store / "git/objects" / oid[:2] / oid[2:]
        extra = self.parent / "object-hardlink"; os.link(object_path, extra)
        with self.assertRaises(importer.ImportError):
            self.inspect(result["projectionDigest"])
        extra.unlink()
        ref = self.store / "git/refs/adopt/imports" / result["projectionDigest"]
        ref.unlink()
        with self.assertRaises(importer.ImportError):
            self.inspect(result["projectionDigest"])
        self.assertFalse(ref.exists())

    def test_exact_selected_limits_and_cumulative_write_store_deadline_are_fail_closed(self):
        for index, (name, value) in enumerate([("MAX_SELECTED_FILES", 1), ("MAX_SELECTED_BYTES", 1),
                ("MAX_READ_BYTES", 1), ("MAX_WRITE_BYTES", 1), ("MAX_STORE_BYTES", 1),
                ("MAX_STORE_FILES", 1), ("TOTAL_SECONDS", -1)]):
            with self.subTest(limit=name):
                self.store = self.parent / ("limits-" + str(index)); self.initialize()
                before = self.snapshot()
                with patch.object(importer, name, value):
                    self.reject()
                self.assertEqual(before, self.snapshot())

    def test_cli_sanitizes_failure_and_never_uses_untrusted_path_git(self):
        fakebin = self.parent / "bin"; fakebin.mkdir(); marker = self.parent / "bad-git-called"
        fake = fakebin / "git"; fake.write_text("#!/bin/sh\n: > '" + str(marker) + "'\nexit 99\n"); fake.chmod(0o755)
        env = dict(os.environ, PATH=str(fakebin) + os.pathsep + os.environ.get("PATH", ""), PYTHONDONTWRITEBYTECODE="1")
        args = [sys.executable, "-B", str(Path(importer.__file__)), "import", "--store", str(self.store),
                "--root", str(self.source), "--request", str(self.request), "--baseline-snapshot", str(self.baseline),
                "--repository-id", self.repository_id, "--principal", self.principal]
        result = subprocess.run(args, env=env, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(json.loads(result.stdout)["ok"]); self.assertEqual(result.stderr, b"")
        self.assertFalse(marker.exists())
        result = subprocess.run(args + ["--unrecognized-private-path", str(self.parent)], env=env,
                                capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["reason"], "invalid_arguments")
        self.assertNotIn(str(self.parent).encode(), result.stdout + result.stderr)

    def test_multichunk_blob_exact_selected_budget_and_truncated_stream_refusal(self):
        model = self.source / "scripts/publish_public_site.py"
        model.write_bytes(model.read_bytes() + b"\n#" + b"x" * 170000 + b"\n")
        self.commit_files()
        seen = []; original = importer._read_source_blob
        def chunks(*args):
            for chunk in original(*args):
                seen.append(len(chunk)); yield chunk
        with patch.object(importer, "_read_source_blob", side_effect=chunks):
            result = self.call()
        self.assertGreater(len(seen), 7); self.assertLessEqual(max(seen), 65536)
        intent = json.loads((self.store / "imports" / result["projectionDigest"] / "intent.json").read_text())
        entries = intent["provenance"]["inputs"]
        self.store = self.parent / "exact-bounds"; self.initialize()
        with patch.object(importer, "MAX_SELECTED_FILES", len(entries)), patch.object(importer, "MAX_SELECTED_BYTES", sum(e["bytes"] for e in entries)):
            self.assertTrue(self.call()["attested"])
        self.store = self.parent / "truncated"; self.initialize()
        def truncated(source, entry, budget):
            for chunk in original(source, entry, budget):
                yield chunk[:-1]
        with patch.object(importer, "_read_source_blob", side_effect=truncated):
            self.reject("input_changed")
        self.assertTrue(list((self.store / "git/objects").glob(".object-*")))
        self.assertFalse(list((self.store / "imports").glob("*/success.json")))

    def test_output_parent_replacement_and_tool_change_fail_without_redirecting_writes(self):
        holder = self.parent / "holder"; holder.mkdir(mode=0o700)
        self.store = holder / "store"; self.initialize()
        other = self.parent / "other-parent"; other.mkdir(mode=0o700)
        moved = self.parent / "saved-holder"
        def change(stage):
            if stage == "after_intent":
                holder.rename(moved); holder.symlink_to(other, target_is_directory=True)
        with patch.object(importer, "_checkpoint", side_effect=change):
            self.reject()
        self.assertEqual(list(other.iterdir()), [])
        self.assertTrue((moved / "store/.keep").exists())
        holder.unlink()
        self.store = self.parent / "tool-change"; self.initialize()
        original = importer._tool_hashes; calls = []
        def tools(budget=None):
            result = original(budget=budget); calls.append(True)
            # Intent shape validation is now I/O-free; the second hash read is
            # the final source check, not a redundant schema-name lookup.
            if len(calls) >= 2:
                result["scripts/admin_candidate_import.py"] = "a" * 64
            return result
        with patch.object(importer, "_tool_hashes", side_effect=tools):
            self.reject("tool_changed")
        self.assertFalse(list((self.store / "imports").glob("*/success.json")))

    def test_directory_metadata_error_closes_opened_descriptors(self):
        real_open = os.open; real_fstat = os.fstat; opened = []; closed = []
        real_close = os.close
        def tracked_open(path, flags, *args, **kwargs):
            fd = real_open(path, flags, *args, **kwargs)
            if flags & os.O_DIRECTORY:
                opened.append(fd)
            return fd
        def tracked_close(fd):
            closed.append(fd); return real_close(fd)
        def fail_leaf(fd):
            info = real_fstat(fd)
            if info.st_ino == self.store.stat().st_ino:
                raise OSError("synthetic metadata failure")
            return info
        with patch.object(importer.os, "open", side_effect=tracked_open), patch.object(importer.os, "close", side_effect=tracked_close), patch.object(importer.os, "fstat", side_effect=fail_leaf):
            self.reject("import_incomplete")
        self.assertTrue(opened); self.assertTrue(set(opened).issubset(closed))

    def test_valid_epoch_replacement_cannot_fork_completed_import_history(self):
        result = self.call(); before_source = self.snapshot()
        identity = self.store / "identity.json"; original = identity.read_bytes()
        changed = json.loads(original); changed["storeEpoch"] = str(uuid.uuid4())
        identity.write_bytes(importer._raw(changed))
        before_store = self.snapshot(self.store)
        self.reject("store_inconsistent")
        self.assertEqual(before_store, self.snapshot(self.store))
        self.assertEqual(before_source, self.snapshot())
        for name in ["intent", "mapping", "success"]:
            self.assertEqual(len(list((self.store / "imports").glob("*/" + name + ".json"))), 1)
        self.assertEqual(len(list((self.store / "git/refs/adopt/imports").iterdir())), 1)
        identity.write_bytes(original)
        self.assertEqual(self.call()["candidateBaseRevision"], result["candidateBaseRevision"])

    def test_existing_mapping_identity_and_projection_prefix_are_bound_before_new_import(self):
        result = self.call(); path = self.store / "imports" / result["projectionDigest"] / "mapping.json"
        raw = path.read_bytes()
        for field in ["identitySha256", "projectionDigest", "intentSha256"]:
            with self.subTest(field=field):
                value = json.loads(raw); value[field] = "a" * 64
                path.write_bytes(importer._raw(value)); before = self.snapshot(self.store)
                self.reject("store_inconsistent")
                self.assertEqual(before, self.snapshot(self.store))
                path.write_bytes(raw)

    def test_known_baseline_parent_and_store_overlap_are_refused_before_import(self):
        self.store = self.baseline.parent / "projection-store"
        self.initialize(); before = self.snapshot(self.store)
        self.reject("unsafe_store_location")
        self.assertEqual(before, self.snapshot(self.store))
        self.store = self.parent / "store-with-baseline"; self.initialize()
        copied = self.store / "copied-baseline"
        shutil.copytree(self.baseline.parent, copied, ignore=shutil.ignore_patterns("projection-store"))
        self.baseline = copied / "snapshot.json"; before = self.snapshot(self.store)
        self.reject("unsafe_store_location")
        self.assertEqual(before, self.snapshot(self.store))

    def test_current_pin_is_rechecked_before_success_and_acknowledgement(self):
        for stage in ["after_pin", "after_mapping", "before_attestation", "after_attestation"]:
            with self.subTest(stage=stage):
                self.store = self.parent / ("changed-pin-" + stage); self.initialize()
                before = self.snapshot()
                def change(at):
                    if at == stage:
                        ref = next((self.store / "git/refs/adopt/imports").iterdir())
                        ref.write_bytes(b"0" * 40 + b"\n")
                with patch.object(importer, "_checkpoint", side_effect=change):
                    self.reject("store_inconsistent")
                self.assertEqual(before, self.snapshot())

    def test_current_identity_cannot_change_during_import(self):
        for stage in ["after_pin", "after_mapping", "before_attestation", "after_attestation"]:
            with self.subTest(stage=stage):
                self.store = self.parent / ("changed-epoch-" + stage); self.initialize()
                before = self.snapshot()
                def change(at):
                    if at == stage:
                        path = self.store / "identity.json"
                        value = json.loads(path.read_text()); value["storeEpoch"] = str(uuid.uuid4())
                        path.write_bytes(importer._raw(value))
                with patch.object(importer, "_checkpoint", side_effect=change):
                    self.reject("store_inconsistent")
                self.assertEqual(before, self.snapshot())

    def test_different_projection_refuses_corrupt_previous_ref_commit_or_success(self):
        original_request = self.request.read_bytes()
        for kind in ["ref", "commit", "success"]:
            with self.subTest(kind=kind):
                self.request.write_bytes(original_request)
                self.store = self.parent / ("history-" + kind); self.initialize()
                old = self.call(); digest = old["projectionDigest"]
                if kind == "ref":
                    (self.store / "git/refs/adopt/imports" / digest).write_bytes(b"0" * 40 + b"\n")
                elif kind == "commit":
                    oid = old["candidateBaseRevision"]
                    (self.store / "git/objects" / oid[:2] / oid[2:]).unlink()
                else:
                    path = self.store / "imports" / digest / "success.json"
                    value = json.loads(path.read_text()); value["mappingSha256"] = "a" * 64
                    path.write_bytes(importer._raw(value))
                request = json.loads(original_request)
                request["patch"]["summary"] += " Different projection."
                self.request.write_bytes(jobs._raw(request))
                before_store, before_source = self.snapshot(self.store), self.snapshot()
                self.reject()
                self.assertEqual(before_store, self.snapshot(self.store))
                self.assertEqual(before_source, self.snapshot())

    def test_outer_read_budget_applies_inside_source_collection(self):
        consumed_after_limit = []
        def collect(root, request, baseline, budget):
            budget.check(10_001)
            consumed_after_limit.append(True)
            raise intake.IntakeError("probe_completed_after_outer_limit")
        with patch.object(importer, "MAX_READ_BYTES", 10_000), patch.object(intake, "_collect_intake", side_effect=collect):
            self.reject("import_limit")
        self.assertEqual(consumed_after_limit, [])

    def test_already_present_result_rechecks_store_after_final_source_validation(self):
        original = importer._final_source
        for kind in ["ref", "epoch"]:
            with self.subTest(kind=kind):
                self.store = self.parent / ("repeat-change-" + kind); self.initialize()
                result = self.call(); before = self.snapshot()
                def change(*args):
                    original(*args)
                    if kind == "ref":
                        (self.store / "git/refs/adopt/imports" / result["projectionDigest"]).write_bytes(b"0" * 40 + b"\n")
                    else:
                        path = self.store / "identity.json"
                        value = json.loads(path.read_text()); value["storeEpoch"] = str(uuid.uuid4())
                        path.write_bytes(importer._raw(value))
                with patch.object(importer, "_final_source", side_effect=change):
                    self.reject("store_inconsistent")
                self.assertEqual(before, self.snapshot())

    def test_outer_deadline_applies_inside_source_collection(self):
        continued_after_deadline = []
        def collect(root, request, baseline, budget):
            future = importer.time.monotonic() + 2
            with patch.object(importer.time, "monotonic", return_value=future):
                budget.check()
            continued_after_deadline.append(True)
            raise intake.IntakeError("probe_completed_after_outer_deadline")
        with patch.object(importer, "TOTAL_SECONDS", 1), patch.object(intake, "_collect_intake", side_effect=collect):
            self.reject("import_timeout")
        self.assertEqual(continued_after_deadline, [])


if __name__ == "__main__":
    unittest.main()
