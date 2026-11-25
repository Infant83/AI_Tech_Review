"""First B2b2 slice on tiny real Git fixtures, never actual publication data."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

from scripts import admin_candidate_import as projection
from scripts import admin_projection_jobs as writer
from scripts import admin_request_jobs as synthetic
from scripts import admin_requests, admin_source_intake as intake


class ProjectionJobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name).resolve()
        (self.parent / ".keep").write_bytes(b"")
        self.fixture = self.parent / "fixture"; synthetic.initialize_sandbox(self.fixture)
        self.source = self.fixture / "repo"
        self.request = self.fixture / "example-request.json"
        self.baseline = self.fixture / "baseline/snapshot.json"
        self.projection = self.parent / "projection"
        self.writer = self.parent / "writer"
        self.repository = str(uuid.uuid4()); self.principal = "trusted-local-test"
        request = json.loads(self.request.read_bytes())
        record = json.loads((self.source / "publication/reviews" / (synthetic.FOLDER + ".json")).read_bytes())
        request["patch"] = {"summary": record["review"]["summary"]}
        self.request.write_bytes(synthetic._raw(request))
        projection.initialize_store(self.projection, self.source, self.repository, self.principal)
        self.imported = projection.import_projection(self.projection, self.source, self.request, self.baseline, self.repository, self.principal)
        self.digest = self.imported["projectionDigest"]
        self.initialize()

    def initialize(self):
        return writer.initialize_writer(self.writer, self.projection, self.source, self.baseline, self.repository, self.principal)

    def stage(self):
        return writer.stage_base(self.writer, self.projection, self.digest, self.repository, self.principal)

    def apply(self, digest=None, source=None, baseline=None):
        return writer.apply_no_change(self.writer, self.request, digest or self.digest,
            source or self.source, baseline or self.baseline, self.repository, self.principal)

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob("*") if p.is_file()}

    def reject(self, function, reason):
        with self.assertRaises(writer.JobError) as caught:
            function()
        self.assertEqual(caught.exception.code, reason)
        self.assertNotIn(str(self.parent), str(caught.exception))

    def origin_advance(self):
        old = synthetic._ref(self.source, "refs/heads/main")
        tree = synthetic._git(self.source, "rev-parse", old + "^{tree}").decode().strip()
        new = synthetic._commit(self.source, tree, {"synthetic": "unrelated advance"}, old)
        synthetic._git(self.source, "update-ref", "refs/heads/main", new, old)
        return new

    def projection_with_schema_version(self, value):
        """Own-fixture proof with linked hashes, exercising the v1 reader gap."""
        original = self.projection / "imports" / self.digest / "intent.json"
        intent = json.loads(original.read_bytes())
        provenance = intent["provenance"]; provenance["schemaVersion"] = value
        provenance["intakeDigest"] = intake._sha(intake._raw({key: item for key, item in provenance.items() if key != "intakeDigest"}))
        intent["projectionDigest"] = projection._sha(projection._raw({"identitySha256": intent["identitySha256"],
            "provenance": provenance, "importerCodeSha256": intent["importerCodeSha256"]}))
        digest, _, tree, _, revision, commit = projection._validate_intent(intent, intent["identitySha256"])
        mapping = {"format": projection.FORMAT, "version": 1, "projectionDigest": digest,
            "identitySha256": intent["identitySha256"], "sourceOriginRevision": provenance["sourceOriginRevision"],
            "sourceTree": provenance["sourceTree"], "candidateBaseRevision": revision,
            "candidateTree": tree, "intentSha256": projection._sha(projection._raw(intent))}
        with projection._Store(self.projection, projection._Budget()) as store, projection._locked(store):
            prefix = "imports/" + digest; store.directory(prefix, create=True)
            store.write(prefix + "/intent.json", projection._raw(intent))
            projection._write_object(store, "commit", [commit], len(commit), expected_oid=revision)
            store.pin("git/refs/adopt/imports/" + digest, (revision + "\n").encode())
            store.write(prefix + "/mapping.json", projection._raw(mapping))
            store.write(prefix + "/success.json", projection._raw({"format": projection.FORMAT, "version": 1,
                "projectionDigest": digest, "mappingSha256": projection._sha(projection._raw(mapping)),
                "checkedAt": "2026-11-26T00:00:00Z"}))
        return digest

    def test_explicit_stage_copies_exact_objects_provenance_and_preserves_original(self):
        source = self.snapshot(self.fixture); original = self.snapshot(self.projection)
        result = self.stage()
        self.assertEqual(result["status"], "projection_base_staged_local")
        self.assertTrue(result["attested"])
        self.assertEqual(source, self.snapshot(self.fixture)); self.assertEqual(original, self.snapshot(self.projection))
        prefix = self.writer / "bases" / self.digest
        self.assertEqual((prefix / "identity.json").read_bytes(), (self.projection / "identity.json").read_bytes())
        for name in ["intent", "mapping", "success"]:
            self.assertEqual((prefix / (name + ".json")).read_bytes(),
                             (self.projection / "imports" / self.digest / (name + ".json")).read_bytes())
        for path in (self.projection / "git/objects").rglob("*"):
            if path.is_file():
                copied = self.writer / "git/objects" / path.relative_to(self.projection / "git/objects")
                self.assertEqual(copied.read_bytes(), path.read_bytes())
                self.assertNotEqual((copied.stat().st_dev, copied.stat().st_ino), (path.stat().st_dev, path.stat().st_ino))
                self.assertEqual(copied.stat().st_nlink, 1)
        self.assertFalse((self.writer / "git/objects/info/alternates").exists())
        self.assertEqual(synthetic._git(self.source, "--git-dir=" + str(self.writer / "git"), "fsck", "--strict", "--no-reflogs"), b"")
        before = self.snapshot(self.writer); repeated = self.stage()
        self.assertTrue(repeated["replay"]); self.assertEqual(before, self.snapshot(self.writer))

    def test_no_implicit_stage_or_init_and_changed_request_never_reserves_key(self):
        before = self.snapshot(self.writer)
        self.reject(self.apply, "projection_not_staged")
        self.assertEqual(before, self.snapshot(self.writer))
        self.stage()
        request = json.loads(self.request.read_bytes()); request["patch"]["summary"] += " changed"
        self.request.write_bytes(synthetic._raw(request)); before = self.snapshot(self.writer)
        self.reject(self.apply, "changed_candidate_not_implemented")
        self.assertEqual(before, self.snapshot(self.writer))
        missing = self.parent / "not-created"
        self.reject(lambda: writer.apply_no_change(missing, self.request, self.digest, self.source,
            self.baseline, self.repository, self.principal), "outcome_unknown")
        self.assertFalse(missing.exists())

    def test_no_change_original_bytes_tombstone_zero_git_writes_and_no_value_leak(self):
        self.stage(); git_before = self.snapshot(self.writer / "git")
        source = self.snapshot(self.fixture); original = self.snapshot(self.projection)
        result = self.apply()
        self.assertEqual(result["status"], "no_change"); self.assertFalse(result["replay"])
        self.assertEqual(result["beforeSha256"], result["afterSha256"])
        self.assertIsNone(result["candidateRevision"]); self.assertFalse(result["sourceAdvanced"])
        self.assertEqual(git_before, self.snapshot(self.writer / "git"))
        self.assertEqual(source, self.snapshot(self.fixture)); self.assertEqual(original, self.snapshot(self.projection))
        request = json.loads(self.request.read_bytes())
        for directory in ["inventory", "tombstones", "states"]:
            self.assertEqual(len(list((self.writer / directory).glob("*.json"))), 1)
            for path in (self.writer / directory).glob("*.json"):
                for forbidden in [request["idempotencyKey"].encode(), request["patch"]["summary"].encode(), str(self.parent).encode()]:
                    self.assertNotIn(forbidden, path.read_bytes())
        self.assertFalse(any((self.writer / "git/refs/adopt/operations").iterdir()))

    def test_replay_survives_source_advance_baseline_and_projection_unavailable_hint_ignored(self):
        self.stage(); one = self.apply(); before = self.snapshot(self.writer)
        self.origin_advance(); self.baseline.unlink()
        moved = self.parent / "projection-offline"; self.projection.rename(moved)
        two = self.apply(digest="bad hint is not opened")
        self.assertTrue(two["replay"]); self.assertTrue(two["sourceAdvanced"])
        self.assertEqual(one["operationId"], two["operationId"])
        self.assertEqual(one["projectionDigest"], two["projectionDigest"])
        self.assertEqual(before, self.snapshot(self.writer))
        three = self.apply(source=self.parent / "offline-source", baseline=self.parent / "offline-baseline")
        self.assertTrue(three["replay"]); self.assertIsNone(three["sourceAdvanced"])
        self.assertEqual(before, self.snapshot(self.writer))

    def test_same_key_conflicts_before_current_source_or_new_hint_and_key_namespace_stable(self):
        self.stage(); one = self.apply()
        request = json.loads(self.request.read_bytes())
        request["sourceId"] = "2026-11-22_other-target"
        self.request.write_bytes(synthetic._raw(request))
        namespace = json.loads((self.writer / "identity.json").read_bytes())["namespace"]
        self.assertEqual(writer._key(namespace, request)[1], one["keyHash"])
        self.reject(lambda: self.apply(digest="invalid", source=self.parent / "absent"), "idempotency_conflict")
        request["sourceId"] = synthetic.FOLDER; request["expectedSourceRevision"] = "f" * 40
        self.request.write_bytes(synthetic._raw(request))
        self.reject(lambda: self.apply(source=self.parent / "absent"), "idempotency_conflict")
        request["expectedReleaseEvidence"]["releaseSha256"] = "f" * 64
        self.request.write_bytes(synthetic._raw(request))
        self.reject(self.apply, "idempotency_conflict")

    def test_request_strict_parse_once_and_frozen_nested_values_cannot_change(self):
        self.stage()
        original = admin_requests.parse_request
        calls = []
        def parse(raw):
            calls.append(raw); return original(raw)
        with patch.object(admin_requests, "parse_request", side_effect=parse):
            self.apply()
        self.assertEqual(calls, [self.request.read_bytes()])
        frozen = admin_requests._FrozenRequest(self.request.read_bytes())
        copy = frozen.value(); copy["patch"]["summary"] = "changed"
        self.assertNotEqual(copy, frozen.value())
        with self.assertRaises(AttributeError):
            frozen.payload = b"changed"

    def test_historical_replay_does_not_read_current_tools_or_run_current_validator(self):
        self.stage(); one = self.apply()
        with patch.object(writer, "_tool_hashes", side_effect=OSError("current tools unavailable")), \
                patch.object(projection, "_tool_hashes", side_effect=OSError("current importer unavailable")), \
                patch.object(writer, "validate_review_registration", side_effect=ValueError("new validator changed")), \
                patch.object(intake, "_collect_intake", side_effect=AssertionError("historical replay must not rerun A")):
            two = self.apply(source=self.parent / "unavailable")
        self.assertTrue(two["replay"]); self.assertIsNone(two["sourceAdvanced"])
        self.assertEqual(one["operationId"], two["operationId"])

    def test_final_source_baseline_request_and_control_changes_prevent_tombstone(self):
        for kind in ["source", "baseline", "request", "identity"]:
            with self.subTest(kind=kind):
                if kind != "source":
                    # Each case gets independent real fixture state and namespace.
                    self.tearDown(); self.setUp()
                self.stage()
                def mutate(stage):
                    if stage != "before_final_check":
                        return
                    if kind == "source":
                        self.origin_advance()
                    elif kind == "baseline":
                        path = self.baseline.parent / "reader-publications.json"; path.write_bytes(path.read_bytes() + b" ")
                    elif kind == "request":
                        self.request.write_bytes(self.request.read_bytes() + b" ")
                    else:
                        path = self.writer / "identity.json"
                        value = json.loads(path.read_bytes()); value["writerEpoch"] = str(uuid.uuid4()); path.write_bytes(writer._raw(value))
                with patch.object(writer, "_checkpoint", side_effect=mutate):
                    with self.assertRaises(writer.JobError):
                        self.apply()
                self.assertEqual(list((self.writer / "tombstones").glob("*.json")), [])

    def test_inventory_only_outcome_unknown_and_completed_tombstone_reconciles_lost_state(self):
        self.stage()
        def fail(stage):
            if stage == "after_inventory":
                raise OSError("private injected fault")
        with patch.object(writer, "_checkpoint", side_effect=fail):
            self.reject(self.apply, "outcome_unknown")
        before = self.snapshot(self.writer); self.reject(self.apply, "outcome_unknown")
        self.assertEqual(before, self.snapshot(self.writer))
        # A separate writer for the ordinary post-tombstone response-loss case.
        self.writer = self.parent / "writer-lost-response"; self.initialize(); self.stage()
        def fail_after_tombstone(stage):
            if stage == "after_tombstone":
                raise OSError("private injected fault")
        with patch.object(writer, "_checkpoint", side_effect=fail_after_tombstone):
            self.reject(self.apply, "outcome_unknown")
        before = self.snapshot(self.writer / "git"); result = self.apply()
        self.assertTrue(result["replay"]); self.assertEqual(before, self.snapshot(self.writer / "git"))
        self.assertEqual(len(list((self.writer / "states").glob("*.json"))), 1)

    def test_partial_base_is_preserved_refused_not_auto_repaired(self):
        def fail(stage):
            if stage == "after_base_pin":
                raise OSError("private stage fault")
        with patch.object(writer, "_checkpoint", side_effect=fail):
            self.reject(self.stage, "outcome_unknown")
        before = self.snapshot(self.writer)
        self.reject(self.stage, "outcome_unknown"); self.reject(self.apply, "outcome_unknown")
        self.assertEqual(before, self.snapshot(self.writer)); self.assertTrue((self.writer / ".keep").exists())

    def test_unattested_projection_cannot_become_attested_writer_base(self):
        (self.projection / "imports" / self.digest / "success.json").unlink()
        before = self.snapshot(self.writer)
        self.reject(self.stage, "projection_not_attested")
        self.assertEqual(before, self.snapshot(self.writer))

    def test_epoch_config_object_and_tombstone_corruption_refused(self):
        self.stage(); self.apply()
        paths = [self.writer / "identity.json", self.writer / "git/config",
                 next((self.writer / "git/objects").glob("*/*")), next((self.writer / "tombstones").glob("*.json"))]
        for path in paths:
            with self.subTest(name=path.name):
                original = path.read_bytes()
                if path.name == "identity.json":
                    value = json.loads(original); value["writerEpoch"] = str(uuid.uuid4()); changed = writer._raw(value)
                else:
                    changed = original + b" "
                path.write_bytes(changed)
                with self.assertRaises(writer.JobError):
                    self.apply()
                path.write_bytes(original)
        self.assertTrue(self.apply()["replay"])

    def test_orphan_base_pin_and_old_other_key_metadata_damage_refused_before_new_key(self):
        self.stage(); self.apply()
        pin = self.writer / "git/refs/adopt/bases" / ("f" * 64)
        pin.write_bytes((self.imported["candidateBaseRevision"] + "\n").encode()); pin.chmod(0o600)
        self.reject(self.apply, "store_inconsistent"); pin.unlink()
        tombstone = next((self.writer / "tombstones").glob("*.json"))
        value = json.loads(tombstone.read_bytes()); value["sourceTree"] = "f" * 40
        tombstone.write_bytes(writer._raw(value))
        reservation_path = next((self.writer / "inventory").glob("*.json"))
        reservation = json.loads(reservation_path.read_bytes()); reservation["tombstoneSha256"] = writer._sha(tombstone.read_bytes())
        reservation_path.write_bytes(writer._raw(reservation))
        request = json.loads(self.request.read_bytes()); request["idempotencyKey"] = str(uuid.uuid4())
        self.request.write_bytes(synthetic._raw(request))
        self.reject(self.apply, "store_inconsistent")

    def test_same_namespace_multiple_keys_and_distinct_prepared_bases(self):
        self.stage(); one = self.apply()
        old_base = self.snapshot(self.writer / "bases" / self.digest)
        request = json.loads(self.request.read_bytes())
        request["expectedSourceRevision"] = self.origin_advance(); request["idempotencyKey"] = str(uuid.uuid4())
        self.request.write_bytes(synthetic._raw(request))
        new_projection = projection.import_projection(self.projection, self.source, self.request, self.baseline,
                                                      self.repository, self.principal)
        second_digest = new_projection["projectionDigest"]
        writer.stage_base(self.writer, self.projection, second_digest, self.repository, self.principal)
        two = self.apply(digest=second_digest)
        self.assertNotEqual(one["keyHash"], two["keyHash"])
        self.assertNotEqual(one["operationId"], two["operationId"])
        self.assertNotEqual(one["projectionDigest"], two["projectionDigest"])
        self.assertEqual(len(list((self.writer / "inventory").glob("*.json"))), 2)
        self.assertEqual(old_base, self.snapshot(self.writer / "bases" / self.digest))

    def test_store_overlap_controlled_modes_and_existing_writer_not_reinitialized(self):
        before = self.snapshot(self.writer)
        self.reject(self.initialize, "outcome_unknown")
        self.assertEqual(before, self.snapshot(self.writer))
        for root in [self.source / "output/writer", self.projection / "writer", self.baseline.parent / "writer"]:
            with self.subTest(root=root.name):
                self.reject(lambda: writer.initialize_writer(root, self.projection, self.source, self.baseline,
                    self.repository, self.principal), "unsafe_store_location")
                self.assertFalse(root.exists())
        (self.writer / "identity.json").chmod(0o644)
        self.reject(self.apply, "store_inconsistent")

    def test_scaled_read_write_store_key_evidence_and_deadline_limits_fail_closed(self):
        before = self.snapshot(self.writer)
        with patch.object(writer, "EVIDENCE_BYTES", 1):
            self.reject(self.stage, "base_evidence_limit")
        self.assertEqual(before, self.snapshot(self.writer))
        self.stage()
        for name, value in [("MAX_READ_BYTES", 1), ("MAX_WRITE_BYTES", 1), ("MAX_STORE_BYTES", 1),
                            ("MAX_STORE_FILES", 1), ("MAX_KEYS", 0), ("TOTAL_SECONDS", -1)]:
            with self.subTest(limit=name):
                before = self.snapshot(self.writer)
                with patch.object(writer, name, value):
                    with self.assertRaises(writer.JobError):
                        self.apply()
                self.assertEqual(before, self.snapshot(self.writer))

    def test_installed_tool_reads_charge_outer_remaining_plus_one_and_deadline(self):
        budget = writer._Budget()
        with patch.object(writer, "MAX_READ_BYTES", 7):
            with self.assertRaises(writer.JobError) as caught:
                writer._tool_hashes(budget=projection._SourceBudget(budget))
        self.assertEqual(caught.exception.code, "job_limit")
        self.assertEqual(budget.read_bytes, 8)
        budget = writer._Budget(); budget.deadline = -1
        with self.assertRaises(writer.JobError) as caught:
            writer._tool_hashes(budget=projection._SourceBudget(budget))
        self.assertEqual(caught.exception.code, "job_timeout")
        self.assertEqual(budget.read_bytes, 0)

    def test_frozen_internal_context_rejects_changed_current_request_without_reparse(self):
        frozen = admin_requests._FrozenRequest(self.request.read_bytes())
        self.request.write_bytes(self.request.read_bytes() + b" ")
        with patch.object(admin_requests, "parse_request", side_effect=AssertionError("must not parse again")):
            with self.assertRaises(intake.IntakeError) as caught:
                intake._collect_intake(self.source, self.request, self.baseline, intake._Budget(), frozen_request=frozen)
        self.assertEqual(caught.exception.code, "input_changed")

    def test_scalar_stored_base_and_mapping_versions_refused_before_key_reservation(self):
        self.stage()
        prefix = self.writer / "bases" / self.digest
        paths = {name: prefix / (name + ".json") for name in ["base", "mapping", "success"]}
        originals = {name: path.read_bytes() for name, path in paths.items()}
        for target in ["base", "mapping"]:
            for invalid in [True, 1.0]:
                with self.subTest(control=target, invalid=invalid):
                    value = json.loads(originals[target]); value["version"] = invalid
                    paths[target].write_bytes(writer._raw(value))
                    if target == "mapping":
                        # Keep the evidence hashes consistent so a type error
                        # cannot be hidden by an unrelated raw-hash rejection.
                        success = json.loads(originals["success"])
                        success["mappingSha256"] = writer._sha(paths["mapping"].read_bytes())
                        paths["success"].write_bytes(writer._raw(success))
                        base = json.loads(originals["base"])
                        for name in ["mapping", "success"]:
                            base["evidenceSha256"][name] = writer._sha(paths[name].read_bytes())
                        paths["base"].write_bytes(writer._raw(base))
                    before = self.snapshot(self.writer)
                    self.reject(self.apply, "store_inconsistent")
                    self.assertEqual(before, self.snapshot(self.writer))
                    self.assertEqual(list((self.writer / "inventory").glob("*.json")), [])
                    for name, raw in originals.items():
                        paths[name].write_bytes(raw)

    def test_scalar_existing_inventory_tombstone_fingerprint_and_state_versions_refused(self):
        self.stage(); self.apply()
        paths = {name: next((self.writer / name).glob("*.json")) for name in ["inventory", "tombstones", "states"]}
        originals = {name: path.read_bytes() for name, path in paths.items()}
        for target, field in [("inventory", "version"), ("tombstones", "version"),
                              ("tombstones", "requestFingerprintVersion"), ("states", "version")]:
            for invalid in [True, 1.0]:
                with self.subTest(control=target, field=field, invalid=invalid):
                    value = json.loads(originals[target]); value[field] = invalid
                    paths[target].write_bytes(writer._raw(value))
                    if target == "tombstones":
                        digest = writer._sha(paths[target].read_bytes())
                        for name in ["inventory", "states"]:
                            bound = json.loads(originals[name]); bound["tombstoneSha256"] = digest
                            paths[name].write_bytes(writer._raw(bound))
                    before = self.snapshot(self.writer)
                    self.reject(self.apply, "store_inconsistent")
                    self.assertEqual(before, self.snapshot(self.writer))
                    for name, raw in originals.items():
                        paths[name].write_bytes(raw)

    def test_scalar_projection_mapping_version_refused_before_any_stage_write(self):
        prefix = self.projection / "imports" / self.digest
        mapping_path, success_path = prefix / "mapping.json", prefix / "success.json"
        mapping_raw, success_raw = mapping_path.read_bytes(), success_path.read_bytes()
        for invalid in [True, 1.0]:
            with self.subTest(invalid=invalid):
                mapping = json.loads(mapping_raw); mapping["version"] = invalid
                mapping_path.write_bytes(writer._raw(mapping))
                # The B2b1 reader compares a dict and hashes its canonical int
                # reconstruction. Keeping that original success hash exercises
                # the writer's pre-copy type guard, rather than an earlier
                # unrelated B2b1 hash refusal.
                before = self.snapshot(self.writer)
                self.reject(self.stage, "store_inconsistent")
                self.assertEqual(before, self.snapshot(self.writer))
                self.assertEqual(list((self.writer / "bases").iterdir()), [])
                mapping_path.write_bytes(mapping_raw); success_path.write_bytes(success_raw)

    def test_scalar_projection_provenance_schema_version_refused_before_any_stage_write(self):
        for invalid in [True, 1.0]:
            with self.subTest(invalid=invalid):
                digest = self.projection_with_schema_version(invalid)
                before = self.snapshot(self.writer)
                self.reject(lambda: writer.stage_base(self.writer, self.projection, digest,
                                                      self.repository, self.principal), "store_inconsistent")
                self.assertEqual(before, self.snapshot(self.writer))
                self.assertEqual(list((self.writer / "bases").iterdir()), [])

    def test_real_cli_no_change_and_sanitized_changed_refusal(self):
        self.stage()
        command = [sys.executable, str(Path(writer.__file__).resolve()), "apply-no-change", "--store", str(self.writer),
            "--request", str(self.request), "--projection-digest", self.digest, "--root", str(self.source),
            "--baseline-snapshot", str(self.baseline), "--repository-id", self.repository, "--principal", self.principal]
        result = subprocess.run(command, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)["status"], "no_change")
        request = json.loads(self.request.read_bytes()); request["idempotencyKey"] = str(uuid.uuid4())
        request["patch"]["summary"] = "private supplied new wording"
        self.request.write_bytes(synthetic._raw(request))
        result = subprocess.run(command, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)["reason"], "changed_candidate_not_implemented")
        self.assertEqual(result.stderr, b"")
        for forbidden in [request["patch"]["summary"].encode(), request["idempotencyKey"].encode(), str(self.parent).encode()]:
            self.assertNotIn(forbidden, result.stdout)


if __name__ == "__main__":
    unittest.main()
