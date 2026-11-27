"""Independent B2b2-V checks on disposable real no-change writer stores.

These tests observe local self-consistency, not an external history checkpoint,
source freshness, changed-result receipts, publication, or power-loss recovery.
"""
from contextlib import contextmanager, ExitStack
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import unittest
from unittest.mock import patch
import uuid

from scripts import admin_candidate_import as projection
from scripts import admin_projection_authority as authority
from scripts import admin_projection_jobs as writer
from scripts import admin_request_jobs as synthetic
from scripts import admin_source_intake as intake


class ProjectionAuthorityTests(unittest.TestCase):
    SUCCESS_FIELDS = {
        "schemaVersion", "ok", "status", "storeFormat", "identitySha256",
        "namespaceDigest", "observedEvidenceDigest", "inspectorCodeSha256",
        "stagedBaseCount", "completedNoChangeCount", "presentDerivedStateCount",
        "missingDerivedStateCount", "observedReadBytes", "sourceAdvanced",
        "continuityEstablished", "limits",
    }
    OLD_FILES = (
        "scripts/admin_requests.py", "scripts/admin_source_intake.py",
        "scripts/admin_candidate_import.py", "scripts/admin_projection_jobs.py",
        "tests/test_admin_projection_jobs.py", "tests/test_admin_candidate_import.py",
        ".automation/admin-readonly/README.md", "scripts/admin_projection_refs.py",
        "tests/test_admin_projection_refs.py",
    )

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.parent = Path(self.temporary.name).resolve()
        (self.parent / ".keep").write_bytes(b"")
        self.fixture = self.parent / "fixture"
        synthetic.initialize_sandbox(self.fixture)
        self.source = self.fixture / "repo"
        self.request = self.fixture / "example-request.json"
        self.baseline = self.fixture / "baseline/snapshot.json"
        self.projection = self.parent / "projection"
        self.writer = self.parent / "writer"
        self.repository = str(uuid.uuid4())
        self.principal = "trusted-local-authority-test"
        value = json.loads(self.request.read_bytes())
        registration = json.loads((self.source / "publication/reviews" /
                                   (synthetic.FOLDER + ".json")).read_bytes())
        value["patch"] = {"summary": registration["review"]["summary"]}
        self.request.write_bytes(synthetic._raw(value))
        projection.initialize_store(self.projection, self.source, self.repository, self.principal)
        self.imported = projection.import_projection(
            self.projection, self.source, self.request, self.baseline,
            self.repository, self.principal)
        self.digest = self.imported["projectionDigest"]
        writer.initialize_writer(self.writer, self.projection, self.source,
                                 self.baseline, self.repository, self.principal)

    def stage(self):
        return writer.stage_base(self.writer, self.projection, self.digest,
                                 self.repository, self.principal)

    def complete(self):
        self.stage()
        return writer.apply_no_change(self.writer, self.request, self.digest,
                                     self.source, self.baseline,
                                     self.repository, self.principal)

    @staticmethod
    def snapshot(root):
        """Bytes and relevant types/modes; deliberately exclude access times."""
        result = {}
        for path in sorted(root.rglob("*")):
            info = path.lstat()
            item = [stat.S_IFMT(info.st_mode), stat.S_IMODE(info.st_mode), info.st_nlink]
            if stat.S_ISREG(info.st_mode):
                item.extend([info.st_size, hashlib.sha256(path.read_bytes()).hexdigest()])
            elif stat.S_ISLNK(info.st_mode):
                item.append(os.readlink(path))
            result[path.relative_to(root).as_posix()] = tuple(item)
        return result

    @contextmanager
    def disposable_store(self):
        """Subcases corrupt only their own copy of this tiny fixture store."""
        with tempfile.TemporaryDirectory(dir=self.parent) as temporary:
            original = self.writer
            self.writer = Path(temporary) / "store"
            shutil.copytree(original, self.writer)
            try:
                yield
            finally:
                self.writer = original

    @contextmanager
    def read_only(self):
        """Observation must not enter a repair, request, Git, or network path."""
        def forbidden(*args, **kwargs):
            raise AssertionError("read-only authority observation entered a writer")
        with ExitStack() as stack:
            for module, name in [
                (writer, "_state"), (writer, "initialize_writer"),
                (writer, "stage_base"), (writer, "apply_no_change"),
                (projection, "initialize_store"), (projection, "import_projection"),
                (projection._Store, "new"), (projection._Store, "write"),
                (projection._Store, "pin"),
            ]:
                stack.enter_context(patch.object(module, name, side_effect=forbidden))
            stack.enter_context(patch("subprocess.Popen", side_effect=forbidden))
            stack.enter_context(patch("socket.create_connection", side_effect=forbidden))
            yield

    def observe(self, root=None, repository=None, principal=None):
        with self.read_only():
            return authority.observe_writer_authority(
                root or self.writer, repository or self.repository,
                principal or self.principal)

    def refused(self, expected=None, *, preserve=True, function=None):
        before = self.snapshot(self.writer) if preserve else None
        with self.assertRaises(authority.AuthorityError) as caught:
            (function or self.observe)()
        if expected is not None:
            self.assertIn(caught.exception.code,
                          {expected} if isinstance(expected, str) else set(expected))
        self.assertNotIn(str(self.parent), str(caught.exception))
        self.assertNotIn(self.principal, str(caught.exception))
        if preserve:
            self.assertEqual(before, self.snapshot(self.writer))
        return caught.exception.code

    def assert_report(self, report, bases, keys, present, missing):
        self.assertEqual(set(report), self.SUCCESS_FIELDS)
        self.assertIs(type(report["schemaVersion"]), int)
        self.assertEqual(report["schemaVersion"], 1)
        self.assertIs(report["ok"], True)
        self.assertEqual(report["status"], "writer_authority_observed_local")
        self.assertEqual(report["storeFormat"], writer.FORMAT)
        self.assertEqual(report["stagedBaseCount"], bases)
        self.assertEqual(report["completedNoChangeCount"], keys)
        self.assertEqual(report["presentDerivedStateCount"], present)
        self.assertEqual(report["missingDerivedStateCount"], missing)
        for name in ["identitySha256", "namespaceDigest", "observedEvidenceDigest",
                     "inspectorCodeSha256"]:
            self.assertRegex(report[name], r"\A[0-9a-f]{64}\Z")
        for name in ["stagedBaseCount", "completedNoChangeCount",
                     "presentDerivedStateCount", "missingDerivedStateCount", "observedReadBytes"]:
            self.assertIs(type(report[name]), int)
            self.assertGreaterEqual(report[name], 0)
        self.assertGreater(report["observedReadBytes"], 0)
        self.assertIsNone(report["sourceAdvanced"])
        self.assertIs(report["continuityEstablished"], False)
        self.assertIn("current_local_self_consistency_only", report["limits"])
        encoded = json.dumps(report, sort_keys=True).encode()
        request = json.loads(self.request.read_bytes())
        for private in [str(self.parent), self.principal, self.repository,
                        request["idempotencyKey"], request["patch"]["summary"]]:
            self.assertNotIn(private.encode(), encoded)

    def test_empty_staged_and_completed_store_are_observed_without_writes(self):
        for prepare, counts in [(lambda: None, (0, 0, 0, 0)),
                                (self.stage, (1, 0, 0, 0)),
                                (lambda: writer.apply_no_change(
                                    self.writer, self.request, self.digest, self.source,
                                    self.baseline, self.repository, self.principal), (1, 1, 1, 0))]:
            prepare()
            before = {str(root): self.snapshot(root)
                      for root in [self.writer, self.fixture, self.projection]}
            code = Path(__file__).resolve().parents[1]
            old_hashes = {p: hashlib.sha256((code / p).read_bytes()).hexdigest()
                          for p in self.OLD_FILES}
            report = self.observe()
            self.assert_report(report, *counts)
            self.assertEqual(before, {str(root): self.snapshot(root)
                                     for root in [self.writer, self.fixture, self.projection]})
            self.assertEqual(old_hashes, {p: hashlib.sha256((code / p).read_bytes()).hexdigest()
                                         for p in self.OLD_FILES})

    def test_multiple_imports_and_all_old_keys_are_counted(self):
        self.complete()
        old = synthetic._ref(self.source, "refs/heads/main")
        tree = synthetic._git(self.source, "rev-parse", old + "^{tree}").decode().strip()
        new = synthetic._commit(self.source, tree, {"synthetic": "authority second origin"}, old)
        synthetic._git(self.source, "update-ref", "refs/heads/main", new, old)
        request = json.loads(self.request.read_bytes())
        request["expectedSourceRevision"] = new
        request["idempotencyKey"] = str(uuid.uuid4())
        self.request.write_bytes(synthetic._raw(request))
        imported = projection.import_projection(self.projection, self.source, self.request,
                                               self.baseline, self.repository, self.principal)
        writer.stage_base(self.writer, self.projection, imported["projectionDigest"],
                          self.repository, self.principal)
        writer.apply_no_change(self.writer, self.request, imported["projectionDigest"],
                               self.source, self.baseline, self.repository, self.principal)
        self.assert_report(self.observe(), 2, 2, 2, 0)
        # An older, unrelated key must still be validated in a global observation.
        path = sorted((self.writer / "inventory").glob("*.json"))[0]
        value = json.loads(path.read_bytes()); value["operationId"] = "f" * 64
        path.write_bytes(writer._raw(value))
        self.refused("store_inconsistent")

    def test_history_is_independent_of_current_source_projection_validator_and_tool_hashes(self):
        self.complete()
        for root in [self.source, self.baseline.parent, self.projection]:
            root.rename(root.with_name(root.name + "-offline"))
        with patch.object(writer, "_tool_hashes", side_effect=OSError("private tool path")), \
                patch.object(projection, "_tool_hashes", side_effect=OSError("private current importer")), \
                patch.object(writer, "validate_review_registration", side_effect=ValueError("new validator")), \
                patch.object(intake, "_collect_intake", side_effect=AssertionError("no live source")):
            self.assert_report(self.observe(), 1, 1, 1, 0)
        self.assertNotIn("scripts/admin_projection_authority.py", projection._tool_paths())

    def test_missing_derived_state_is_reported_and_never_rebuilt(self):
        self.complete()
        path = next((self.writer / "states").glob("*.json")); path.unlink()
        before = self.snapshot(self.writer)
        report = self.observe()
        self.assert_report(report, 1, 1, 0, 1)
        self.assertEqual(before, self.snapshot(self.writer))
        self.assertFalse(path.exists())

    def test_wrong_state_values_extra_fields_and_scalar_versions_are_refused(self):
        self.complete()
        for field, value in [("version", True), ("version", 1.0),
                             ("status", "changed"), ("tombstoneSha256", "f" * 64),
                             ("unexpected", "private value")]:
            with self.subTest(field=field, value=value), self.disposable_store():
                path = next((self.writer / "states").glob("*.json"))
                current = json.loads(path.read_bytes()); current[field] = value
                path.write_bytes(writer._raw(current))
                self.refused("store_inconsistent")

    def test_missing_tombstone_is_unknown_and_orphan_history_is_inconsistent(self):
        self.complete()
        for directory, expected in [("tombstones", "outcome_unknown"),
                                    ("inventory", "store_inconsistent")]:
            with self.subTest(directory=directory), self.disposable_store():
                next((self.writer / directory).glob("*.json")).unlink()
                self.refused(expected)

    def test_epoch_namespace_key_and_strict_metadata_corruption_are_refused(self):
        self.complete()
        mutations = [
            ("identity.json", "writerEpoch", str(uuid.uuid4())),
            ("identity.json", "namespace", {}),
            ("identity.json", "version", True),
            ("inventory", "namespaceDigest", "f" * 64),
            ("inventory", "keyHash", "f" * 64),
            ("inventory", "version", 1.0),
            ("tombstones", "requestFingerprintVersion", True),
            ("tombstones", "afterSha256", "f" * 64),
            ("tombstones", "noChange", 1),
            ("tombstones", "sourceOriginRevision", "f" * 40),
            ("tombstones", "writerToolCodeSha256", {}),
        ]
        for location, field, value in mutations:
            with self.subTest(location=location, field=field), self.disposable_store():
                path = self.writer / location
                if path.is_dir():
                    path = next(path.glob("*.json"))
                current = json.loads(path.read_bytes()); current[field] = value
                raw = writer._raw(current); path.write_bytes(raw)
                # Preserve outer linkage so tombstone semantic corruption is exercised.
                if location == "tombstones":
                    index = self.writer / "inventory" / path.name
                    item = json.loads(index.read_bytes())
                    item["tombstoneSha256"] = hashlib.sha256(raw).hexdigest()
                    index.write_bytes(writer._raw(item))
                self.refused("store_inconsistent")

    def test_complete_base_evidence_pin_and_reachable_object_corruption_are_refused(self):
        self.stage()
        locations = [
            "bases/" + self.digest + "/identity.json",
            "bases/" + self.digest + "/intent.json",
            "bases/" + self.digest + "/mapping.json",
            "bases/" + self.digest + "/success.json",
            "bases/" + self.digest + "/base.json",
            "git/refs/adopt/bases/" + self.digest,
        ]
        for relative in locations:
            with self.subTest(relative=relative), self.disposable_store():
                path = self.writer / relative
                path.write_bytes(path.read_bytes() + b"private corruption")
                self.refused("store_inconsistent")
        for kind in ["commit", "tree", "blob"]:
            with self.subTest(kind=kind), self.disposable_store():
                selected = None
                with projection._Store(self.writer, projection._Budget()) as store:
                    for path in (self.writer / "git/objects").glob("*/*"):
                        oid = path.parent.name + path.name
                        if projection._read_object(store, oid)["kind"] == kind:
                            selected = path; break
                self.assertIsNotNone(selected)
                selected.write_bytes(selected.read_bytes() + b"trailing bytes")
                self.refused("store_inconsistent")

    def test_partial_unrelated_base_globally_blocks_without_repairing_valid_key(self):
        self.complete()
        partial = self.writer / "bases" / ("e" * 64)
        partial.mkdir(mode=0o700)
        self.refused("outcome_unknown")

    def test_operation_refs_pending_files_and_pending_directories_are_unsupported(self):
        self.complete()
        for name, directory in [("a" * 64, False), (".pending-" + "b" * 64, False),
                                (".pending-" + "c" * 64, True)]:
            with self.subTest(name=name), self.disposable_store():
                path = self.writer / "git/refs/adopt/operations" / name
                if directory:
                    path.mkdir(mode=0o700)
                else:
                    path.write_bytes(b"1" * 40 + b"\n"); path.chmod(0o600)
                self.refused("store_inconsistent")

    def test_unread_orphan_objects_are_not_claimed_as_validated_history(self):
        self.stage()
        before = self.observe()
        directory = self.writer / "git/objects/ee"
        directory.mkdir(mode=0o700, exist_ok=True)
        orphan = directory / ("f" * 38)
        orphan.write_bytes(b"not a reachable Git object"); orphan.chmod(0o600)
        snapshot = self.snapshot(self.writer)
        report = self.observe()
        self.assert_report(report, 1, 0, 0, 0)
        self.assertEqual(snapshot, self.snapshot(self.writer))
        self.assertEqual(report["continuityEstablished"], before["continuityEstablished"])

    def test_file_modes_symlinks_hardlinks_and_directory_modes_are_refused(self):
        self.complete()
        for mutation in ["mode", "symlink", "hardlink", "directory"]:
            with self.subTest(mutation=mutation), self.disposable_store():
                path = self.writer / "identity.json"
                canary = self.parent / ("canary-" + mutation)
                canary.write_bytes(path.read_bytes()); canary.chmod(0o600)
                if mutation == "mode":
                    path.chmod(0o644)
                elif mutation == "directory":
                    (self.writer / "states").chmod(0o755)
                else:
                    path.unlink()
                    if mutation == "symlink":
                        path.symlink_to(canary)
                    else:
                        os.link(canary, path)
                canary_before = canary.read_bytes()
                self.refused({"store_inconsistent", "observation_changed"})
                self.assertEqual(canary_before, canary.read_bytes())

    def test_final_membership_control_and_reachable_object_changes_refuse_success(self):
        self.complete()
        for mutation in ["member", "control", "object"]:
            with self.subTest(mutation=mutation), self.disposable_store():
                fired = []
                def change(stage):
                    if stage != "before_final_readset" or fired:
                        return
                    fired.append(stage)
                    if mutation == "member":
                        path = self.writer / "states" / ("f" * 64 + ".json")
                        path.write_bytes(b"{}\n"); path.chmod(0o600)
                    elif mutation == "control":
                        path = self.writer / "identity.json"
                        path.write_bytes(path.read_bytes() + b" ")
                    else:
                        path = next((self.writer / "git/objects").glob("*/*"))
                        path.write_bytes(path.read_bytes() + b" ")
                with patch.object(authority, "_checkpoint", side_effect=change):
                    self.refused({"observation_changed", "store_inconsistent"}, preserve=False)
                self.assertEqual(fired, ["before_final_readset"])

    def test_parent_replacement_never_reads_or_writes_replacement_canary(self):
        self.stage()
        original = self.writer
        moved = self.parent / "writer-original"
        canary = self.parent / "writer-canary"
        shutil.copytree(original, canary)
        marker = canary / "private-marker"
        marker.write_bytes(b"replacement must remain unchanged"); marker.chmod(0o600)
        before = self.snapshot(canary); fired = []
        def replace(stage):
            if stage == "after_authority" and not fired:
                fired.append(stage); original.rename(moved); original.symlink_to(canary)
        try:
            with patch.object(authority, "_checkpoint", side_effect=replace):
                self.refused({"observation_changed", "store_inconsistent"}, preserve=False)
            self.assertEqual(fired, ["after_authority"])
            self.assertEqual(before, self.snapshot(canary))
        finally:
            if original.is_symlink():
                original.unlink(); moved.rename(original)

    def test_read_and_lock_context_exit_errors_cannot_return_success(self):
        self.stage()
        original_lock = projection._locked
        @contextmanager
        def fail_unlock(store):
            with original_lock(store):
                yield
            raise OSError("private lock release detail")
        with patch.object(projection, "_locked", side_effect=fail_unlock):
            self.refused("outcome_unknown")
        with patch.object(authority, "_checkpoint", side_effect=lambda stage:
                          (_ for _ in ()).throw(OSError("private read detail"))
                          if stage == "after_authority" else None):
            self.refused("outcome_unknown")

    def test_observed_digest_is_repeatable_and_missing_state_is_part_of_readset(self):
        self.complete()
        first = self.observe(); second = self.observe()
        self.assertEqual(first["observedEvidenceDigest"], second["observedEvidenceDigest"])
        self.assertEqual(first["identitySha256"], second["identitySha256"])
        self.assertEqual(first["namespaceDigest"], second["namespaceDigest"])
        state = next((self.writer / "states").glob("*.json")); state.unlink()
        missing = self.observe()
        self.assertNotEqual(first["observedEvidenceDigest"], missing["observedEvidenceDigest"])
        self.assertEqual(missing["missingDerivedStateCount"], 1)

    def test_missing_store_lock_and_wrong_trusted_namespace_are_not_initialized(self):
        absent = self.parent / "absent"
        self.refused({"store_inconsistent", "outcome_unknown"},
                     function=lambda: self.observe(root=absent))
        self.assertFalse(absent.exists())
        self.refused("store_inconsistent", function=lambda: self.observe(repository=str(uuid.uuid4())))
        self.refused("store_inconsistent", function=lambda: self.observe(principal="other-trusted-local"))
        (self.writer / "lock").unlink()
        self.refused("store_inconsistent")
        self.assertFalse((self.writer / "lock").exists())

    def test_shared_read_deadline_and_small_caps_fail_without_writes(self):
        self.complete()
        cases = [("MAX_READ_BYTES", 1, "job_limit"), ("TOTAL_SECONDS", -1, "job_timeout"),
                 ("MAX_STORE_BYTES", 1, "store_limit"), ("MAX_STORE_FILES", 1, "store_limit"),
                 ("CONTROL_BYTES", 1, "control_limit"), ("EVIDENCE_BYTES", 1, "base_evidence_limit"),
                 ("MAX_KEYS", 0, "key_limit")]
        for name, value, reason in cases:
            with self.subTest(limit=name), patch.object(authority, name, value):
                self.refused(reason)

    def test_read_budget_exact_limit_and_one_less_include_revalidation_and_self_code(self):
        self.complete()
        actual_read = 0
        native_read = os.read
        def count_read(fd, size):
            nonlocal actual_read
            raw = native_read(fd, size); actual_read += len(raw)
            return raw
        with patch.object(authority.os, "read", side_effect=count_read):
            normal = self.observe()
        required = normal["observedReadBytes"]
        self.assertEqual(required, actual_read)
        with patch.object(authority, "MAX_READ_BYTES", required):
            exact = self.observe()
        self.assertEqual(exact["observedReadBytes"], required)
        with patch.object(authority, "MAX_READ_BYTES", required - 1):
            self.refused("job_limit")

    def test_coherently_rebound_provenance_still_requires_known_field_types(self):
        self.stage()
        for field in ["requestFingerprint", "counts.selectedFiles"]:
            with self.subTest(field=field), self.disposable_store():
                prefix = self.writer / "bases" / self.digest
                identity_raw = (prefix / "identity.json").read_bytes()
                intent = json.loads((prefix / "intent.json").read_bytes())
                provenance = intent["provenance"]
                if field == "requestFingerprint":
                    provenance[field] = None
                else:
                    provenance["counts"]["selectedFiles"] = True
                provenance["intakeDigest"] = intake._sha(intake._raw({
                    k: v for k, v in provenance.items() if k != "intakeDigest"}))
                intent["projectionDigest"] = projection._sha(projection._raw({
                    "identitySha256": intent["identitySha256"], "provenance": provenance,
                    "importerCodeSha256": intent["importerCodeSha256"]}))
                digest, _, tree, _, revision, commit = projection._validate_intent(
                    intent, projection._sha(identity_raw))
                intent_raw = projection._raw(intent)
                mapping = {"format": projection.FORMAT, "version": 1,
                    "projectionDigest": digest, "identitySha256": projection._sha(identity_raw),
                    "sourceOriginRevision": provenance["sourceOriginRevision"],
                    "sourceTree": provenance["sourceTree"], "candidateBaseRevision": revision,
                    "candidateTree": tree, "intentSha256": projection._sha(intent_raw)}
                mapping_raw = projection._raw(mapping)
                success_raw = projection._raw({"format": projection.FORMAT, "version": 1,
                    "projectionDigest": digest, "mappingSha256": projection._sha(mapping_raw),
                    "checkedAt": "2026-11-28T00:00:00Z"})
                identity = json.loads((self.writer / "identity.json").read_bytes())
                self.assertEqual(identity["projectionIdentitySha256"], projection._sha(identity_raw))
                raw_bundle = {"identity": identity_raw, "intent": intent_raw,
                              "mapping": mapping_raw, "success": success_raw}
                evidence_raw = projection._raw({"format": writer.FORMAT, "version": 1,
                    "identitySha256": projection._sha((self.writer / "identity.json").read_bytes()),
                    "projectionDigest": digest,
                    "evidenceSha256": {k: projection._sha(v) for k, v in raw_bundle.items()}})
                with projection._Store(self.writer, projection._Budget()) as store:
                    new = "bases/" + digest
                    store.directory(new, create=True)
                    for name, raw in {**raw_bundle, "base": evidence_raw}.items():
                        store.write(new + "/" + name + ".json", raw)
                    projection._write_object(store, "commit", [commit], len(commit), expected_oid=revision)
                    store.pin("git/refs/adopt/bases/" + digest, (revision + "\n").encode())
                shutil.rmtree(prefix)
                (self.writer / "git/refs/adopt/bases" / self.digest).unlink()
                self.refused("store_inconsistent")

    def test_self_code_changes_and_late_membership_or_context_faults_refuse_success(self):
        self.stage()
        fake_code = self.parent / "synthetic-inspector.py"
        fake_code.write_bytes(b"# fixed synthetic installed inspector\n")
        fake_code.chmod(0o600)
        for boundary in ["after_final_readset", "before_lock_exit"]:
            with self.subTest(boundary=boundary):
                original = fake_code.read_bytes(); fired = []
                def change(stage):
                    if stage == boundary and not fired:
                        fired.append(stage); fake_code.write_bytes(original + b"# changed\n")
                try:
                    with patch.object(authority, "__file__", str(fake_code)), \
                            patch.object(authority, "_checkpoint", side_effect=change):
                        self.refused("observation_changed")
                    self.assertEqual(fired, [boundary])
                finally:
                    fake_code.write_bytes(original)
        with patch.object(authority, "_checkpoint", side_effect=lambda stage:
                          (_ for _ in ()).throw(OSError("private exit fault"))
                          if stage == "after_lock_exit" else None):
            self.refused("outcome_unknown")

    def test_cli_exact_output_bound_nonsecret_failures_and_stdout_io_failure(self):
        self.complete()
        argv = ["--store", str(self.writer), "--repository-id", self.repository,
                "--principal", self.principal]
        class Output:
            def __init__(self, stream):
                self.stream = stream; self.flush_calls = 0
            def fileno(self):
                return self.stream.fileno()
            @property
            def buffer(self):
                raise AssertionError("stdout must use unbuffered FD writes")
            def flush(self):
                self.flush_calls += 1
                raise OSError("no buffered shutdown retry")
        def invoke(*, maximum=None, checkpoint=None, write=None):
            with tempfile.TemporaryFile() as stream, ExitStack() as stack:
                output = Output(stream)
                stack.enter_context(self.read_only())
                stack.enter_context(patch.object(sys, "stdout", output))
                if maximum is not None:
                    stack.enter_context(patch.object(authority, "MAX_STDOUT_BYTES", maximum))
                if checkpoint is not None:
                    stack.enter_context(patch.object(authority, "_checkpoint", side_effect=checkpoint))
                if write is not None:
                    stack.enter_context(patch.object(authority.os, "write", side_effect=write))
                status = authority.main(argv)
                stream.seek(0); raw = stream.read()
                self.assertEqual(output.flush_calls, 0)
                return status, raw
        status, raw = invoke()
        self.assertEqual(status, 0)
        self.assert_report(json.loads(raw), 1, 1, 1, 0)
        self.assertLessEqual(len(raw), authority.MAX_STDOUT_BYTES)
        self.assertEqual(invoke(maximum=len(raw))[0], 0)
        status, limited = invoke(maximum=len(raw) - 1)
        self.assertNotEqual(status, 0)
        self.assertEqual(json.loads(limited),
                         {"schemaVersion": 1, "ok": False, "reason": "stdout_limit"})
        def private_failure(stage):
            if stage == "after_authority":
                raise OSError("private raw key " + str(self.parent))
        status, failed = invoke(checkpoint=private_failure)
        self.assertNotEqual(status, 0)
        self.assertEqual(json.loads(failed),
                         {"schemaVersion": 1, "ok": False, "reason": "outcome_unknown"})
        self.assertNotIn(str(self.parent).encode(), failed)
        calls = []
        native_write = os.write
        def short_then_broken(fd, data):
            calls.append(bytes(data))
            if len(calls) == 1:
                return native_write(fd, data[:11])
            raise BrokenPipeError("private stdout failure")
        status, partial = invoke(write=short_then_broken)
        self.assertNotEqual(status, 0)
        self.assertEqual(len(calls), 2)
        self.assertEqual(partial, raw[:11])
        self.assertFalse(any(b'"ok":false' in chunk for chunk in calls))


if __name__ == "__main__":
    unittest.main()
