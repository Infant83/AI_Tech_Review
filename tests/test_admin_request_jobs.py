"""B1 uses actual sacrificial Git repos, processes and injected crash boundaries."""
from __future__ import annotations

from contextlib import redirect_stdout
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


class JobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name).resolve()
        (self.parent / ".keep").write_bytes(b"")
        self.root = self.parent / "sandbox"
        self.initial = jobs.initialize_sandbox(self.root)
        self.repo, self.store = self.root / "repo", self.root / "store"
        self.request_path = self.root / "example-request.json"
        self.baseline = self.root / "baseline/snapshot.json"
        self.request = json.loads(self.request_path.read_text())
        self.base = self.initial["sourceRevision"]
        self.target = "publication/reviews/" + jobs.FOLDER + ".json"

    def apply(self):
        return jobs.run_job(self.root, self.request_path, self.baseline)

    def save_request(self):
        self.request_path.write_bytes(jobs._raw(self.request))

    def refs(self):
        return jobs._git(self.repo, "for-each-ref", "--format=%(refname) %(objectname)", jobs.PREFIX).decode().splitlines()

    def key(self):
        return next(iter(json.loads((self.store / "inventory.json").read_text())["keys"]))

    def claim(self):
        return json.loads((self.store / "claims" / (self.key() + ".json")).read_text())

    def snapshot(self):
        paths = [p for p in self.root.rglob("*") if p.is_file() and ".git" not in p.relative_to(self.root).parts
                 and "store" not in p.relative_to(self.root).parts]
        return {str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}

    def reject(self, reason=None, call=None):
        with self.assertRaises(jobs.JobError) as caught:
            (call or self.apply)()
        if reason:
            self.assertEqual(caught.exception.code, reason)
        for secret in [str(self.parent), "Synthetic B1 candidate summary", "example-request.json"]:
            self.assertNotIn(secret, str(caught.exception))
        return caught.exception.code

    def child(self, *, crash=None):
        code = """
import os,sys
from pathlib import Path
from scripts import admin_request_jobs as jobs
stage=sys.argv[2]
if stage:
    def stop(point):
        if point==stage: os._exit(86)
    jobs._checkpoint=stop
raise SystemExit(jobs.main(['apply','--sandbox',sys.argv[1],'--request',sys.argv[1]+'/example-request.json',
                           '--baseline-snapshot',sys.argv[1]+'/baseline/snapshot.json']))
"""
        return subprocess.Popen([sys.executable, "-B", "-c", code, str(self.root), crash or ""],
                                cwd=Path(jobs.__file__).resolve().parents[1], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

    def crash(self, stage):
        process = self.child(crash=stage)
        stdout, stderr = process.communicate(timeout=20)
        self.assertEqual(process.returncode, 86, (stdout, stderr))
        self.assertEqual(stderr, b"")

    def advance_main(self):
        tree = jobs._git(self.repo, "rev-parse", self.base + "^{tree}").decode().strip()
        commit = jobs._commit(self.repo, tree, {"synthetic": "unrelated main advancement"}, self.base)
        jobs._git(self.repo, "update-ref", "refs/heads/main", commit, self.base)
        return commit

    def test_explicit_init_actual_candidate_and_source_worktree_index_baseline_unchanged(self):
        before = self.snapshot(); index = (self.repo / ".git/index").read_bytes()
        result = self.apply()
        self.assertEqual(result["status"], "candidate_saved_local")
        self.assertFalse(result["replay"])
        self.assertEqual(self.snapshot(), before)
        self.assertEqual((self.repo / ".git/index").read_bytes(), index)
        self.assertEqual(jobs._ref(self.repo, "refs/heads/main"), self.base)
        self.assertEqual(len(self.refs()), 1)
        self.assertEqual(jobs._git(self.repo, "diff-tree", "--no-commit-id", "--name-only", "-r", self.base,
                                   result["candidateRevision"]).decode().splitlines(), [self.target])
        candidate = json.loads(jobs._blob(self.repo, result["candidateRevision"], self.target))
        original = json.loads((self.repo / self.target).read_text())
        self.assertEqual(candidate, {**original, "review": {**original["review"], **self.request["patch"]}})
        for secret in [str(self.parent), "Synthetic B1 candidate summary", "idempotencyKey"]:
            self.assertNotIn(secret, json.dumps(result))
        self.assertEqual(jobs._git(self.repo, "status", "--porcelain"), b"")

    def test_replay_returns_same_commit_even_after_source_advanced_and_baseline_disappears(self):
        first = self.apply(); claim = (self.store / "claims" / (self.key() + ".json")).read_bytes()
        self.advance_main(); self.baseline.unlink()
        with patch.object(jobs, "_preflight", side_effect=AssertionError("Replay must not run A")), \
             patch.object(jobs, "_commit", side_effect=AssertionError("Replay must not commit")):
            replay = self.apply()
        self.assertTrue(replay["replay"]); self.assertTrue(replay["sourceAdvanced"])
        self.assertEqual(replay["candidateRevision"], first["candidateRevision"])
        self.assertEqual((self.store / "claims" / (self.key() + ".json")).read_bytes(), claim)

    def test_same_key_different_patch_target_or_source_is_conflict_before_preflight(self):
        first = self.apply(); original = json.loads(self.request_path.read_text())
        variants = [{**original, "patch": {"summary": "Different"}},
                    {**original, "sourceId": "2026-11-21_another-target"},
                    {**original, "expectedSourceRevision": "b" * 40}]
        for request in variants:
            self.request = request; self.save_request()
            with patch.object(jobs, "_preflight", side_effect=AssertionError("Conflict must not run A")):
                self.reject("idempotency_conflict")
        self.assertEqual(self.refs()[0].split()[1], first["candidateRevision"])

    def test_two_actual_processes_same_key_return_one_authoritative_candidate(self):
        inode = (self.store / "lock").stat().st_ino
        processes = [self.child(), self.child()]
        results = []
        for process in processes:
            stdout, stderr = process.communicate(timeout=25)
            self.assertEqual(process.returncode, 0, (stdout, stderr)); self.assertEqual(stderr, b"")
            results.append(json.loads(stdout))
        self.assertEqual({r["candidateRevision"] for r in results}.__len__(), 1)
        self.assertEqual(sorted(r["replay"] for r in results), [False, True])
        self.assertEqual(len(self.refs()), 1)
        self.assertEqual(len(list((self.store / "claims").glob("*.json"))), 1)
        self.assertEqual((self.store / "lock").stat().st_ino, inode)

    def test_mutable_directory_scan_runs_under_the_actual_store_lock(self):
        import fcntl
        actual = jobs._scan
        seen = []
        def locked_scan(root):
            with (self.store / "lock").open("rb") as handle:
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    seen.append("locked")
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                    self.fail("Mutable scan ran before the store lock")
            return actual(root)
        with patch.object(jobs, "_scan", side_effect=locked_scan):
            self.assertEqual(self.apply()["status"], "candidate_saved_local")
        self.assertEqual(seen, ["locked"])

    def test_no_change_creates_only_tombstone_and_no_git_object_or_ref(self):
        self.request["patch"] = {"summary": "Synthetic original summary"}; self.save_request()
        objects = jobs._git(self.repo, "count-objects", "-v")
        result = self.apply(); replay = self.apply()
        self.assertEqual(result["status"], "no_change"); self.assertIsNone(result["candidateRevision"])
        self.assertTrue(replay["replay"]); self.assertEqual(self.refs(), [])
        self.assertEqual(jobs._git(self.repo, "count-objects", "-v"), objects)
        self.assertTrue(self.claim()["noChange"])
        state = self.store / "states" / (self.key() + ".json"); state.unlink()
        self.assertEqual(self.apply()["status"], "no_change")

    def test_no_change_claim_loss_is_unknown_and_not_a_fresh_key(self):
        self.request["patch"] = {"summary": "Synthetic original summary"}; self.save_request(); self.apply()
        (self.store / "claims" / (self.key() + ".json")).unlink()
        self.reject("outcome_unknown"); self.assertEqual(self.refs(), [])

    def test_no_change_inventory_claim_must_also_match_the_original_git_blob(self):
        self.request["patch"] = {"summary": "Synthetic original summary"}; self.save_request(); self.apply()
        key = self.key(); path = self.store / "claims" / (key + ".json")
        claim = self.claim(); claim["beforeSha256"] = claim["afterSha256"] = "b" * 64
        path.write_bytes(jobs._raw(claim))
        inventory = json.loads((self.store / "inventory.json").read_text())
        inventory["keys"][key] = jobs._sha(path.read_bytes())
        (self.store / "inventory.json").write_bytes(jobs._raw(inventory))
        self.reject("store_inconsistent"); self.assertEqual(self.refs(), [])

    def test_inventory_reservation_crash_stops_without_creating_claim_or_git_receipt(self):
        self.crash("after_inventory")
        self.assertEqual(len(json.loads((self.store / "inventory.json").read_text())["keys"]), 1)
        self.assertEqual(list((self.store / "claims").iterdir()), []); self.assertEqual(self.refs(), [])
        self.reject("outcome_unknown")

    def test_claim_crash_without_git_receipt_is_unknown_instead_of_reexecuting(self):
        self.crash("after_claim")
        self.assertEqual(len(list((self.store / "claims").iterdir())), 1); self.assertEqual(self.refs(), [])
        self.reject("outcome_unknown")

    def test_claimed_git_receipt_crash_can_resume_same_operation(self):
        self.crash("after_receipt")
        claim = self.claim(); ref = self.refs()[0].split()[0]
        self.assertEqual(jobs._receipt(self.repo, ref, claim)[0], "claimed")
        result = self.apply()
        self.assertEqual(result["operationId"], claim["operationId"])
        self.assertEqual(result["status"], "candidate_saved_local"); self.assertTrue(result["replay"])

    def test_candidate_object_before_ref_crash_resumes_deterministic_candidate(self):
        self.crash("after_candidate_object")
        before = jobs._git(self.repo, "count-objects", "-v")
        result = self.apply()
        self.assertEqual(result["status"], "candidate_saved_local")
        self.assertEqual(jobs._git(self.repo, "count-objects", "-v"), before)

    def test_result_ref_crash_reconciles_from_receipt_without_new_commit(self):
        self.crash("after_result_ref")
        saved = self.refs()[0].split()[1]
        with patch.object(jobs, "_commit", side_effect=AssertionError("Do not commit replay")):
            result = self.apply()
        self.assertEqual(result["candidateRevision"], saved); self.assertTrue(result["replay"])

    def test_git_success_then_journal_io_failure_is_unknown_and_retry_reconciles(self):
        def fail(stage):
            if stage == "before_state":
                raise OSError("Synthetic private failure")
        with patch.object(jobs, "_checkpoint", side_effect=fail):
            self.reject("outcome_unknown")
        candidate = self.refs()[0].split()[1]
        self.assertEqual(self.apply()["candidateRevision"], candidate)

    def test_missing_or_corrupt_view_is_rebuilt_from_git_not_trusted(self):
        candidate = self.apply()["candidateRevision"]
        state = self.store / "states" / (self.key() + ".json")
        for raw in [None, b"broken JSON", jobs._raw({"status": "published", "candidateRevision": "b" * 40})]:
            if raw is None:
                state.unlink()
            else:
                state.write_bytes(raw)
            self.assertEqual(self.apply()["candidateRevision"], candidate)
            self.assertEqual(json.loads(state.read_text())["status"], "candidate_saved_local")

    def test_lost_claim_and_receipt_remain_reserved_in_inventory(self):
        self.apply(); key = self.key(); ref, old = self.refs()[0].split()
        (self.store / "claims" / (key + ".json")).unlink()
        jobs._git(self.repo, "update-ref", "-d", ref, old)
        self.reject("outcome_unknown")
        self.assertIn(key, json.loads((self.store / "inventory.json").read_text())["keys"])

    def test_missing_receipt_or_corrupt_claim_never_allocates_again(self):
        self.apply(); ref, old = self.refs()[0].split()
        jobs._git(self.repo, "update-ref", "-d", ref, old)
        self.reject("outcome_unknown")
        (self.store / "claims" / (self.key() + ".json")).write_bytes(b"{}")
        self.reject("store_inconsistent")

    def test_actual_transaction_verifies_unrelated_main_at_commit_point(self):
        advanced = []
        def race(stage):
            if stage == "before_result_cas":
                advanced.append(self.advance_main())
        with patch.object(jobs, "_checkpoint", side_effect=race):
            self.reject("source_conflict")
        self.assertEqual(jobs._ref(self.repo, "refs/heads/main"), advanced[0])
        self.assertEqual(jobs._receipt(self.repo, self.refs()[0].split()[0], self.claim())[0], "claimed")

    def test_actual_transaction_expected_old_receipt_rejects_noncooperating_change(self):
        changed = []
        def race(stage):
            if stage == "before_result_cas":
                ref, old = self.refs()[0].split()
                tree = jobs._git(self.repo, "rev-parse", self.base + "^{tree}").decode().strip()
                foreign = jobs._commit(self.repo, tree, {"synthetic": "foreign receipt"}, self.base)
                jobs._git(self.repo, "update-ref", ref, foreign, old)
                changed.append(foreign)
        with patch.object(jobs, "_checkpoint", side_effect=race):
            self.reject("outcome_unknown")
        self.assertEqual(self.refs()[0].split()[1], changed[0])
        self.assertEqual(jobs._ref(self.repo, "refs/heads/main"), self.base)
        self.reject("store_inconsistent")

    def test_receipt_ref_must_name_actual_commit_instead_of_tag_tree_or_blob(self):
        result = self.apply(); candidate = result["candidateRevision"]
        ref = self.refs()[0].split()[0]
        tree = jobs._git(self.repo, "rev-parse", candidate + "^{tree}").decode().strip()
        blob = jobs._git(self.repo, "rev-parse", candidate + ":" + self.target).decode().strip()
        tag = jobs._git(self.repo, "mktag", raw=(
            "object " + candidate + "\ntype commit\ntag synthetic-receipt\n"
            "tagger Synthetic B1 <synthetic@example.invalid> 946684800 +0000\n\nSynthetic tag\n"
        ).encode()).decode().strip()
        for oid in [tag, tree, blob]:
            with self.subTest(kind=jobs._git(self.repo, "cat-file", "-t", oid).decode().strip()):
                jobs._git(self.repo, "update-ref", ref, oid, candidate)
                try:
                    self.reject("store_inconsistent")
                finally:
                    jobs._git(self.repo, "update-ref", ref, candidate, oid)
        self.assertEqual(self.apply()["candidateRevision"], candidate)

    def _mode_tree(self, tree, parts):
        out = []
        for row in jobs._git(self.repo, "ls-tree", "-z", tree).split(b"\0"):
            if not row:
                continue
            meta, name = row.split(b"\t", 1)
            if name == parts[0].encode():
                if len(parts) == 1:
                    meta = b"100755 blob " + meta.split()[2]
                else:
                    meta = b"040000 tree " + self._mode_tree(meta.split()[2].decode(), parts[1:]).encode()
            out.append(meta + b"\t" + name + b"\0")
        return jobs._git(self.repo, "mktree", "-z", raw=b"".join(out)).decode().strip()

    def test_forged_receipt_mode_parent_metadata_and_extra_path_are_rejected(self):
        result = self.apply(); candidate = result["candidateRevision"]; ref = self.refs()[0].split()[0]
        claim = self.claim(); tree = jobs._git(self.repo, "rev-parse", candidate + "^{tree}").decode().strip()
        metadata = jobs._metadata(claim, "candidate_saved_local")
        variants = [(self._mode_tree(tree, self.target.split("/")), metadata, self.base),
                    (tree, {**metadata, "requestFingerprint": "b" * 64}, self.base),
                    (tree, metadata, candidate)]
        source_files = {path.decode(): jobs._blob(self.repo, candidate, path.decode())
                        for path in jobs._git(self.repo, "ls-tree", "--name-only", "-r", "-z", candidate).split(b"\0") if path}
        source_files["outside-target.txt"] = b"Synthetic outside change"
        variants.append((jobs._tree(self.repo, source_files), metadata, self.base))
        empty = jobs._git(self.repo, "mktree", "-z", raw=b"").strip()
        with_empty = jobs._git(self.repo, "ls-tree", "-z", tree) + b"040000 tree " + empty + b"\toutside-empty\0"
        variants.append((jobs._git(self.repo, "mktree", "-z", raw=with_empty).decode().strip(), metadata, self.base))
        for altered_tree, altered_metadata, parent in variants:
            fake = jobs._commit(self.repo, altered_tree, altered_metadata, parent)
            jobs._git(self.repo, "update-ref", ref, fake, candidate)
            self.reject("store_inconsistent")
            jobs._git(self.repo, "update-ref", ref, candidate, fake)

    def test_replay_expected_full_tree_validation_does_not_write_git_objects_or_refs(self):
        first = self.apply(); before = jobs._git(self.repo, "count-objects", "-v"); refs = self.refs()
        real = jobs._git
        def reads_only(repo, *args, **kwargs):
            self.assertNotIn(args[0], {"mktree", "hash-object", "commit-tree", "update-ref", "read-tree", "update-index"})
            return real(repo, *args, **kwargs)
        with patch.object(jobs, "_git", side_effect=reads_only):
            self.assertEqual(self.apply()["candidateRevision"], first["candidateRevision"])
        self.assertEqual(jobs._git(self.repo, "count-objects", "-v"), before); self.assertEqual(self.refs(), refs)

    def test_request_reread_and_source_blob_reread_cannot_mix_after_A(self):
        actual = jobs._preflight
        def change_request(repo, path, baseline, frozen):
            changed = json.loads(path.read_text()); changed["patch"]["summary"] += " changed"
            path.write_bytes(jobs._raw(changed))
            return actual(repo, path, baseline, frozen)
        with patch.object(jobs, "_preflight", side_effect=change_request):
            self.reject("input_changed")
        self.assertEqual(self.refs(), [])
        self.assertEqual(json.loads((self.store / "inventory.json").read_text())["keys"], {})
        self.save_request()
        real_blob = jobs._blob
        with patch.object(jobs, "_blob", side_effect=lambda *args: real_blob(*args) + b" "):
            self.reject("input_changed")

    def test_remote_filter_include_hooks_attributes_replace_and_alternates_are_rejected(self):
        for key, value in [("remote.origin.url", "https://example.invalid/repository"), ("filter.test.clean", "never-run"),
                           ("include.path", str(self.parent / "not-loaded")), ("core.hooksPath", str(self.parent / "never-run"))]:
            jobs._git(self.repo, "config", "--local", key, value)
            self.reject("unsafe_git_config")
            jobs._git(self.repo, "config", "--local", "--unset", key)
        for relative in [".git/objects/info/alternates", ".git/info/attributes", ".gitattributes", ".git/hooks/reference-transaction"]:
            p = self.repo / relative; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b"not executed")
            self.reject("unsafe_sandbox"); p.unlink()
        replacement = self.repo / ".git/refs/replace" / self.base
        replacement.parent.mkdir(parents=True, exist_ok=True); replacement.write_text(self.base + "\n")
        self.reject("unsafe_sandbox")

    def test_inherited_git_and_template_global_config_injection_are_ignored(self):
        evil = self.parent / "evil-config"; evil.write_text('[filter "evil"]\nclean = never-execute\n[core]\nhooksPath = /never-execute\n')
        template = self.parent / "evil-template/hooks"; template.mkdir(parents=True)
        (template / "reference-transaction").write_text("never-execute")
        env = {"GIT_DIR": str(self.parent / "unrelated.git"), "GIT_WORK_TREE": str(self.parent),
               "GIT_CONFIG_GLOBAL": str(evil), "GIT_CONFIG_PARAMETERS": "malformed",
               "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(self.parent / "objects"), "GIT_TEMPLATE_DIR": str(template.parent)}
        with patch.dict(os.environ, env):
            fresh = self.parent / "another-sandbox"
            self.assertTrue(jobs.initialize_sandbox(fresh)["ok"])
            self.assertTrue(self.apply()["ok"])
        self.assertFalse((fresh / "repo/.git/hooks/reference-transaction").exists())
        self.assertFalse((self.parent / "unrelated.git").exists())

    def test_local_include_is_rejected_before_any_git_process_can_follow_it(self):
        with (self.repo / ".git/config").open("a") as handle:
            handle.write('\n[include]\npath = /private/never-open-config\n')
        with patch.object(jobs, "_git", side_effect=AssertionError("Git must not parse unsafe local config")):
            self.reject("unsafe_git_config")

    def test_symlink_linked_git_and_unmarked_source_are_rejected(self):
        link = self.parent / "alias"; link.symlink_to(self.root, target_is_directory=True)
        self.reject("unsafe_path", lambda: jobs.run_job(link, self.request_path, self.baseline))
        self.reject("sandbox_not_initialized", lambda: jobs.run_job(Path(jobs.__file__).parents[1], self.request_path, self.baseline))
        original_git = self.repo / ".git"; moved = self.root / "saved.git"; original_git.rename(moved)
        original_git.write_text("gitdir: " + str(moved) + "\n")
        self.reject("shared_git_rejected")

    def test_missing_store_identity_lock_or_inventory_is_not_reinitialized(self):
        for name in ["identity.json", "inventory.json", "lock"]:
            p = self.store / name; raw = p.read_bytes(); p.unlink()
            self.reject(); self.assertFalse(p.exists()); p.write_bytes(raw)
        self.reject("new_protected_sandbox_required", lambda: jobs.initialize_sandbox(self.root))

    def test_bounds_and_sanitized_cli_errors_do_not_create_keys(self):
        self.request_path.write_bytes(b" " * (jobs.MAX_REQUEST_BYTES + 1)); self.reject()
        self.assertEqual(json.loads((self.store / "inventory.json").read_text())["keys"], {})
        stream = io.StringIO()
        with redirect_stdout(stream):
            self.assertEqual(jobs.main(["apply", "--sandbox", "/private/synthetic"]), 1)
        self.assertEqual(json.loads(stream.getvalue()), {"schemaVersion": 1, "ok": False, "reason": "invalid_arguments"})

    def test_cli_initialization_and_apply_are_supported_explicit_routes(self):
        fresh = self.parent / "cli-fixture"
        script = Path(jobs.__file__)
        def command(args):
            result = subprocess.run([sys.executable, "-I", "-B", str(script), *args], capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr); self.assertEqual(result.stderr, b"")
            self.assertNotIn(str(self.parent).encode(), result.stdout)
            return json.loads(result.stdout)
        self.assertEqual(command(["init-fixture", "--sandbox", str(fresh)])["status"], "synthetic_sandbox_initialized")
        result = command(["apply", "--sandbox", str(fresh), "--request", str(fresh / "example-request.json"),
                          "--baseline-snapshot", str(fresh / "baseline/snapshot.json")])
        self.assertEqual(result["status"], "candidate_saved_local")


if __name__ == "__main__":
    unittest.main()
