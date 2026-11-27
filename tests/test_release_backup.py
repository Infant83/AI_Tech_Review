import hashlib
import copy
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch
import os
from contextlib import redirect_stdout
from types import SimpleNamespace
from scripts import release_artifact_retention as retention
from scripts.release_backup import create_backup, verify_backup, restore_backup, import_pages
from scripts.release_artifact_retention import deletion_plan


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(); self.site = self.root / "site"; self.site.mkdir()
        (self.site / "index.html").write_bytes(b"public article")
        catalog = b'{"revision":"' + b'a' * 40 + b'"}'
        (self.site / "reader-publications.json").write_bytes(catalog)
        seal = {"version": 1, "revision": "a" * 40, "catalog_sha256": hashlib.sha256(catalog).hexdigest(),
                "snapshot": {"files": {"index.html": {"sha256": hashlib.sha256(b"public article").hexdigest()}}}}
        (self.site / "publication-release.json").write_text(json.dumps(seal))

    def test_complete_release_roundtrip_with_same_bytes_and_exact_revision(self):
        backup = self.root / "recovery.tar.gz"
        self.assertTrue(create_backup(self.site, backup)["ok"])
        output = self.root / "restore"
        self.assertEqual(restore_backup(backup, output)["status"], "restored_only_not_deployed")
        for path in self.site.iterdir(): self.assertEqual((output / "site" / path.name).read_bytes(), path.read_bytes())
        self.assertEqual(verify_backup(backup)["revision"], "a" * 40)
        with self.assertRaises(ValueError): restore_backup(backup, output)

    def test_mutation_after_seal_and_links_cannot_enter_recovery_copy(self):
        (self.site / "index.html").write_bytes(b"not reviewed")
        with self.assertRaises(ValueError): create_backup(self.site, self.root / "bad.tar.gz")
        (self.site / "linked").symlink_to(self.site / "index.html")
        with self.assertRaises(ValueError): create_backup(self.site, self.root / "bad.tar.gz")

    def test_pages_import_rejects_path_traversal_and_links(self):
        for name, link in [("../outside", False), ("file", True)]:
            raw = self.root / ("link.tar" if link else "escape.tar")
            with tarfile.open(raw, "w") as archive:
                member = tarfile.TarInfo(name)
                if link: member.type = tarfile.SYMTYPE; member.linkname = "../outside"
                else: member.size = 4
                archive.addfile(member, None if link else io.BytesIO(b"data"))
            with self.assertRaises(ValueError): import_pages(raw, self.root / ("out-link" if link else "out-escape"))

    def test_new_seal_rejects_files_added_after_validation(self):
        path = self.site / "publication-release.json"; seal = json.loads(path.read_text())
        seal["artifact_files"] = {item.name: {"sha256": hashlib.sha256(item.read_bytes()).hexdigest(), "bytes": item.stat().st_size}
                                  for item in self.site.iterdir() if item.name != "publication-release.json"}
        path.write_text(json.dumps(seal))
        (self.site / "unexpected.txt").write_text("not in the sealed public artifact")
        with self.assertRaisesRegex(ValueError, "inventory differs"): create_backup(self.site, self.root / "new.tar.gz")

    def test_recovery_header_revision_cannot_mislabel_a_different_release(self):
        original = self.root / "original.tar.gz"
        create_backup(self.site, original)
        renamed = self.root / "mislabelled.tar.gz"
        with tarfile.open(original, "r:gz") as source, tarfile.open(renamed, "w:gz") as target:
            for member in source:
                data = source.extractfile(member).read()
                if member.name == "recovery.json":
                    value = json.loads(data); value["revision"] = "b" * 40
                    data = json.dumps(value).encode(); member.size = len(data)
                target.addfile(member, io.BytesIO(data))
        with self.assertRaisesRegex(ValueError, "do not agree"): verify_backup(renamed)

    def test_recovery_count_cleanup_ignores_pages_private_and_other_artifacts(self):
        rows = [{"id": i, "name": "publication-recovery", "created_at": f"2026-11-{i:02d}", "expired": False} for i in range(1, 6)]
        rows += [{"id": 99, "name": "github-pages"}, {"id": 98, "name": "private-backup"}]
        self.assertEqual(deletion_plan(rows), {"keep": [5, 4, 3], "delete": [2, 1]})
        with self.assertRaises(ValueError): deletion_plan(rows, 0)

    def test_apply_requires_current_upload_before_any_api_call(self):
        pages = [{"total_count": 0, "artifacts": []}]
        output = io.StringIO()
        with patch.object(retention.subprocess, "run", return_value=SimpleNamespace(stdout=json.dumps(pages))) as api:
            with redirect_stdout(output):
                result = retention.main(["--repository", "Example/Review", "--apply"])
        self.assertEqual(result, 1)
        self.assertEqual(json.loads(output.getvalue())["reason"], "current_upload_required")
        api.assert_not_called()

    def test_concurrent_backup_destination_is_never_overwritten(self):
        destination = self.root / "same-name.tar.gz"
        real_link = os.link
        def other_finished_first(source, target):
            destination.write_bytes(b"other completed backup")
            return real_link(source, target)
        with patch("scripts.release_backup.os.link", side_effect=other_finished_first):
            with self.assertRaises(FileExistsError): create_backup(self.site, destination)
        self.assertEqual(destination.read_bytes(), b"other completed backup")


class RetentionGuardTests(unittest.TestCase):
    """Mock only provider I/O; verify plans, refusals and partial outcomes."""
    revision = "a" * 40

    def setUp(self):
        self.now = patch.object(retention, "_utcnow", return_value=datetime(2026, 11, 22, tzinfo=timezone.utc))
        self.now.start(); self.addCleanup(self.now.stop)
        self.sleep = patch.object(retention.time, "sleep")
        self.wait = self.sleep.start(); self.addCleanup(self.sleep.stop)
        self.calls, self.deletes = [], []

    def artifact(self, identifier):
        return {"id": identifier, "name": retention.NAME, "expired": False,
                "size_in_bytes": 1000 + identifier,
                "created_at": f"2026-11-01T00:{identifier:02d}:00Z",
                "expires_at": "2026-12-01T00:00:00Z", "digest": "sha256:" + "c" * 64,
                "workflow_run": {"id": 100 + identifier, "head_sha": self.revision}}

    def rows(self):
        return [self.artifact(i) for i in range(1, 6)]

    def pages(self, rows):
        return [{"total_count": len(rows), "artifacts": rows}]

    def provider(self, listings, fail_delete=None):
        responses = iter(listings)
        def run(command, **kwargs):
            self.calls.append(command)
            self.assertEqual(command[:2], ["gh", "api"])
            self.assertTrue(kwargs["check"])
            self.assertTrue(kwargs["capture_output"])
            self.assertEqual(kwargs["timeout"], 30)
            if "DELETE" in command:
                identifier = int(command[-1].rsplit("/", 1)[1]); self.deletes.append(identifier)
                if identifier == fail_delete:
                    raise retention.subprocess.CalledProcessError(1, command,
                        output="private provider response", stderr="private credential diagnostic")
                return SimpleNamespace(stdout="")
            response = next(responses)
            if isinstance(response, Exception):
                raise response
            return SimpleNamespace(stdout=response if isinstance(response, str) else json.dumps(response))
        return patch.object(retention.subprocess, "run", side_effect=run)

    def apply(self, **kwargs):
        return retention.run_retention("Example/Review", apply=True,
            expected_artifact_id=5, expected_run_id=105,
            expected_source_revision=self.revision, **kwargs)

    def test_late_current_visibility_retries_then_keeps_this_upload(self):
        rows = self.rows(); old = rows[:-1]
        with self.provider([self.pages(old), self.pages(rows), self.pages(rows), self.pages([r for r in rows if r["id"] != 2])]):
            result = self.apply()
        self.assertEqual(result["keep"], [5, 4, 3])
        self.assertEqual(result["deleted"], [2, 1])
        self.assertEqual(self.deletes, [2, 1])
        self.assertEqual(result["listingAttempts"], 4)
        self.wait.assert_called_once_with(2)

    def test_missing_current_after_bounded_retries_deletes_nothing(self):
        old = self.pages(self.rows()[:-1])
        with self.provider([old, old, old]):
            with self.assertRaises(retention.RetentionError) as caught:
                self.apply()
        self.assertEqual(caught.exception.code, "current_artifact_not_visible")
        self.assertEqual(caught.exception.delete_attempted, [])
        self.assertEqual(self.deletes, [])
        self.assertEqual(self.wait.call_count, 2)

    def test_wrong_current_identity_expiry_size_and_types_are_not_retried(self):
        mutations = [lambda r: r.update(name="private-backup"), lambda r: r.update(expired=True),
            lambda r: r.update(size_in_bytes=0), lambda r: r.update(size_in_bytes=True),
            lambda r: r.update(expires_at="2026-11-02T00:00:00Z"),
            lambda r: r["workflow_run"].update(id=True), lambda r: r["workflow_run"].update(id=999),
            lambda r: r["workflow_run"].update(head_sha="b" * 40)]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                rows = self.rows(); mutate(rows[-1]); self.calls.clear(); self.wait.reset_mock()
                with self.provider([self.pages(rows)]):
                    with self.assertRaises(retention.RetentionError): self.apply()
                self.assertEqual(len(self.calls), 1)
                self.assertEqual(self.deletes, [])
                self.wait.assert_not_called()

    def test_complete_pagination_is_consumed_and_duplicates_or_missing_rows_fail(self):
        rows = self.rows()
        split = [{"total_count": 5, "artifacts": rows[:2]}, {"total_count": 5, "artifacts": rows[2:]}]
        with self.provider([split]):
            result = retention.run_retention("Example/Review")
        self.assertEqual(result["keep"], [5, 4, 3]); self.assertFalse(result["applied"])
        invalid = [split[:1], [{"total_count": True, "artifacts": rows}],
            [{"total_count": 5, "artifacts": rows}, {"total_count": 6, "artifacts": []}],
            [{"total_count": 6, "artifacts": rows + [rows[-1]]}],
            {"total_count": 5, "artifacts": rows}]
        for pages in invalid:
            with self.subTest(pages=pages), self.provider([pages]):
                with self.assertRaises(retention.RetentionError): self.apply()
        self.assertEqual(self.deletes, [])

    def test_snapshot_metadata_drift_with_same_plan_stops_before_delete(self):
        for field, value in [("size_in_bytes", 9999), ("digest", "sha256:" + "d" * 64),
                             ("expires_at", "2026-12-02T00:00:00Z")]:
            rows = self.rows(); changed = copy.deepcopy(rows); changed[0][field] = value
            with self.subTest(field=field), self.provider([self.pages(rows), self.pages(changed)]):
                with self.assertRaises(retention.RetentionError) as caught: self.apply()
            self.assertEqual(caught.exception.code, "metadata_changed")
            self.assertEqual(caught.exception.deleted, []); self.assertEqual(self.deletes, [])

    def test_other_actor_removal_does_not_trigger_stale_plan_deletion(self):
        rows = self.rows()
        with self.provider([self.pages(rows), self.pages(rows[1:])]):
            with self.assertRaises(retention.RetentionError) as caught: self.apply()
        self.assertEqual(caught.exception.code, "metadata_changed"); self.assertEqual(self.deletes, [])

    def test_successful_own_deletion_is_expected_by_next_fresh_check(self):
        rows = self.rows()
        with self.provider([self.pages(rows), self.pages(rows), self.pages([r for r in rows if r["id"] != 2])]):
            result = self.apply()
        self.assertEqual(result["deleted"], [2, 1]); self.assertTrue(result["currentArtifactVerified"])
        self.assertEqual(result["keep"], [5, 4, 3]); self.assertEqual(len(self.calls), 5)

    def test_failed_delete_reports_confirmed_and_uncertain_progress_without_raw_errors(self):
        rows = self.rows(); output = io.StringIO()
        args = ["--repository", "Example/Review", "--apply", "--expected-artifact-id", "5",
                "--expected-run-id", "105", "--expected-source-revision", self.revision]
        with self.provider([self.pages(rows), self.pages(rows), self.pages([r for r in rows if r["id"] != 2])], fail_delete=1):
            with redirect_stdout(output): result = retention.main(args)
        report = json.loads(output.getvalue())
        self.assertEqual(result, 1); self.assertEqual(report["reason"], "delete_outcome_unknown")
        self.assertEqual(report["deleted"], [2]); self.assertEqual(report["unconfirmed_delete"], [1])
        self.assertEqual(report["delete_attempted"], [2, 1]); self.assertNotIn("private", output.getvalue())

    def test_list_error_after_one_delete_preserves_partial_progress_and_stops(self):
        rows = self.rows()
        error = retention.subprocess.CalledProcessError(1, ["gh"], stderr="private provider diagnostic")
        with self.provider([self.pages(rows), self.pages(rows), error]):
            with self.assertRaises(retention.RetentionError) as caught: self.apply()
        self.assertEqual(caught.exception.code, "api_error")
        self.assertEqual(caught.exception.deleted, [2]); self.assertEqual(caught.exception.unconfirmed_delete, [])
        self.assertEqual(self.deletes, [2])

    def test_newer_uploads_cannot_move_current_outside_kept_copies(self):
        rows = self.rows() + [self.artifact(i) for i in (6, 7, 8)]
        with self.provider([self.pages(rows)]):
            with self.assertRaises(retention.RetentionError) as caught: self.apply()
        self.assertEqual(caught.exception.code, "current_artifact_not_retained"); self.assertEqual(self.deletes, [])

    def test_wrong_scope_and_expired_rows_never_enter_delete_targets(self):
        rows = self.rows(); unrelated = self.artifact(99); unrelated["name"] = "private-backup"
        expired = self.artifact(6); expired["expired"] = True
        with self.provider([self.pages(rows + [unrelated, expired])]):
            report = retention.run_retention("Example/Review")
        self.assertEqual(report["delete"], [2, 1]); self.assertEqual(self.deletes, [])

    def test_invalid_guard_inputs_or_lower_apply_keep_are_rejected_before_api(self):
        cases = [{"keep": 2}, {"expected_artifact_id": True}, {"expected_run_id": False},
                 {"expected_source_revision": "invalid"}, {"repository": "../Review"}, {"apply": "yes"}]
        for update in cases:
            args = dict(repository="Example/Review", keep=3, apply=True,
                        expected_artifact_id=5, expected_run_id=105, expected_source_revision=self.revision)
            args.update(update)
            with self.subTest(update=update), self.provider([]):
                with self.assertRaises(retention.RetentionError): retention.run_retention(**args)
        self.assertEqual(self.calls, [])

    def test_malformed_json_duplicate_keys_and_api_failure_are_sanitized(self):
        for response in ['[{"total_count":0,"total_count":0,"artifacts":[]}]', '[NaN]', 'private invalid body',
                         retention.subprocess.TimeoutExpired(["gh"], 30, stderr="private diagnostic")]:
            output = io.StringIO()
            with self.subTest(response=response), self.provider([response]), redirect_stdout(output):
                result = retention.main(["--repository", "Example/Review"])
            self.assertEqual(result, 1); self.assertNotIn("private", output.getvalue())
            self.assertEqual(json.loads(output.getvalue())["deleted"], [])

    def test_workflow_binds_actual_upload_receipt_run_and_source_without_new_permission(self):
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/pages.yml").read_text()
        job = workflow.split("  recovery-copy:\n", 1)[1].split("  notify-readers:\n", 1)[0]
        self.assertIn("id: recovery_upload", job)
        self.assertIn("${{ steps.recovery_upload.outputs.artifact-id }}", job)
        self.assertIn('--expected-artifact-id "$RECOVERY_ARTIFACT_ID"', job)
        self.assertIn('--expected-run-id "$GITHUB_RUN_ID"', job)
        self.assertIn('--expected-source-revision "$GITHUB_SHA"', job)
        self.assertLess(job.index("Verify and package"), job.index("id: recovery_upload"))
        self.assertLess(job.index("id: recovery_upload"), job.index("Retain the three"))


class RetentionCliTests(unittest.TestCase):
    """Exercise the real entrypoint while isolating provider I/O."""
    script = Path(__file__).resolve().parents[1] / "scripts/release_artifact_retention.py"

    def invoke(self, pages, *, apply=False):
        runner = (
            "import json,runpy,sys\n"
            "from types import SimpleNamespace\n"
            "from unittest.mock import patch\n"
            "script,pages,apply=sys.argv[1],json.loads(sys.argv[2]),sys.argv[3]=='1'\n"
            "sys.argv=[script,'--repository','Example/Review']\n"
            "if apply:\n"
            " sys.argv+=['--apply','--expected-artifact-id','5','--expected-run-id','105',"
            "'--expected-source-revision','a'*40]\n"
            "def provider(command,**kwargs):\n"
            " if 'DELETE' in command: raise AssertionError('Unexpected provider mutation')\n"
            " return SimpleNamespace(stdout=json.dumps(pages))\n"
            "with patch('subprocess.run',side_effect=provider):\n"
            " runpy.run_path(script,run_name='__main__')\n"
        )
        return subprocess.run([sys.executable, "-I", "-c", runner, str(self.script), json.dumps(pages),
                               "1" if apply else "0"],
                              capture_output=True, text=True, timeout=10)

    def test_refused_incomplete_listing_exits_nonzero_without_deleting(self):
        result = self.invoke([{"total_count": 1, "artifacts": []}])
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["reason"], "incomplete_metadata")
        self.assertEqual(report["deleted"], [])
        self.assertEqual(report["delete_attempted"], [])
        self.assertEqual(report["metadata_counts"], {"page_count": 1,
            "advertised_total_count": 1, "collected_row_count": 0})
        self.assertEqual(result.stderr, "")

    def test_successful_dry_run_keeps_zero_exit_and_json(self):
        result = self.invoke([{"total_count": 0, "artifacts": []}])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "dry_run")
        self.assertNotIn("metadata_counts", json.loads(result.stdout))
        self.assertEqual(result.stderr, "")

    def test_refused_page_container_diagnostics_do_not_echo_values(self):
        marker = "synthetic-private-provider-body"
        for pages in ({"private": marker}, marker, None):
            with self.subTest(container=type(pages).__name__):
                result = self.invoke(pages, apply=True)
                self.assertEqual(result.returncode, 1)
                report = json.loads(result.stdout)
                self.assertEqual(report["reason"], "incomplete_metadata")
                self.assertEqual(report["metadata_counts"], {"page_count": None,
                    "advertised_total_count": None, "collected_row_count": None})
                self.assertEqual(report["delete_attempted"], [])
                self.assertNotIn(marker, result.stdout)
                self.assertEqual(result.stderr, "")

    def test_refused_empty_or_excess_pages_only_reports_page_count(self):
        for pages in ([], [{"private": "synthetic-private-page"}] * 101):
            with self.subTest(page_count=len(pages)):
                result = self.invoke(pages, apply=True)
                self.assertEqual(result.returncode, 1)
                report = json.loads(result.stdout)
                self.assertEqual(report["reason"], "incomplete_metadata")
                self.assertEqual(report["metadata_counts"], {"page_count": len(pages),
                    "advertised_total_count": None, "collected_row_count": None})
                self.assertEqual(report["delete_attempted"], [])
                self.assertNotIn("synthetic-private-page", result.stdout)
                self.assertEqual(result.stderr, "")

    def test_refused_missing_rows_reports_safe_counts_without_deleting(self):
        marker = "synthetic-private-row"
        result = self.invoke([{"total_count": 5, "artifacts": [
            {"name": marker, "id": 987654321}]}], apply=True)
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["reason"], "incomplete_metadata")
        self.assertEqual(report["metadata_counts"], {"page_count": 1,
            "advertised_total_count": 5, "collected_row_count": 1})
        self.assertEqual(report["deleted"], [])
        self.assertEqual(report["delete_attempted"], [])
        self.assertNotIn(marker, result.stdout)
        self.assertNotIn("987654321", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_malformed_or_unsafe_counts_are_not_serialized(self):
        cases = [("synthetic-private-count", "invalid_metadata"),
                 (True, "invalid_metadata"), ((1 << 53), "incomplete_metadata")]
        for advertised, reason in cases:
            with self.subTest(reason=reason, type=type(advertised).__name__):
                result = self.invoke([{"total_count": advertised, "artifacts": []}], apply=True)
                self.assertEqual(result.returncode, 1)
                report = json.loads(result.stdout)
                self.assertEqual(report["reason"], reason)
                if reason == "incomplete_metadata":
                    self.assertEqual(report["metadata_counts"], {"page_count": 1,
                        "advertised_total_count": None, "collected_row_count": 0})
                else:
                    self.assertNotIn("metadata_counts", report)
                self.assertEqual(report["delete_attempted"], [])
                self.assertNotIn("synthetic-private-count", result.stdout)
                self.assertNotIn(str(1 << 53), result.stdout)
                self.assertEqual(result.stderr, "")
