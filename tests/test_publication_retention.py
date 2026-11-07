from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import publication_retention as retention


class CandidateRetentionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name).resolve()
        self.root = self.workspace / "output"
        self.root.mkdir()
        self.now = datetime(2026, 11, 30, 12, tzinfo=timezone.utc)

    def candidate(self, name, days):
        path = self.root / name
        (path / "site").mkdir(parents=True)
        (path / "site/index.html").write_text("Verified generated page")
        (path / retention.MARKER).write_text(json.dumps({
            "version": 1, "kind": "publication-candidate", "revision": "a" * 40,
            "created_at": (self.now - timedelta(days=days)).isoformat().replace("+00:00", "Z"),
            "status": "verified-local", "site": "site"}))
        (path / "report.json").write_text(json.dumps({"revision": "a" * 40,
            "status": "candidate_only_requires_release_policy_and_browser_review"}))
        return path

    def run_retention(self, **kwargs):
        return retention.retain_candidates(self.root, now=self.now, workspace=self.workspace, **kwargs)

    @staticmethod
    def rows(report):
        return {row["path"]: row for row in report["candidates"]}

    def three_old(self):
        return [self.candidate("newest", 8), self.candidate("second", 9), self.candidate("oldest", 10)]

    def test_default_is_read_only_and_keeps_the_newest_two_by_marker_date(self):
        paths = self.three_old()
        # Filesystem timestamp changes do not make the old candidate newest.
        (paths[-1] / "site/new-generated-file.txt").write_text("later file timestamp")
        report = self.run_retention()
        rows = self.rows(report)
        self.assertEqual(report["mode"], "dry-run")
        self.assertEqual(rows["newest"]["reason"], "newest_candidates")
        self.assertEqual(rows["second"]["reason"], "newest_candidates")
        self.assertEqual(rows["oldest"]["action"], "would_delete")
        self.assertGreater(report["planned_bytes"], 0)
        self.assertEqual(report["deleted_bytes"], 0)
        self.assertTrue(all(path.exists() for path in paths))
        self.assertFalse((self.root / ".publication-retention.lock").exists())

    def test_apply_deletes_only_the_old_verified_candidate(self):
        newest, second, oldest = self.three_old()
        unknown = self.root / "unrelated-research"
        unknown.mkdir()
        (unknown / "important.txt").write_text("Keep unrelated data")
        report = self.run_retention(apply=True)
        self.assertTrue(newest.is_dir())
        self.assertTrue(second.is_dir())
        self.assertFalse(oldest.exists())
        self.assertEqual((unknown / "important.txt").read_text(), "Keep unrelated data")
        self.assertEqual(self.rows(report)["oldest"]["action"], "deleted")
        self.assertEqual(report["deleted_bytes"], report["planned_bytes"])

    def test_candidates_younger_than_seven_days_are_kept_beyond_two(self):
        for name, age in [("one", 1), ("two", 2), ("three", 6)]:
            self.candidate(name, age)
        report = self.run_retention(apply=True)
        self.assertEqual(report["deleted_bytes"], 0)
        self.assertEqual(self.rows(report)["three"]["reason"], "younger_than_minimum_age")

    def test_seven_day_boundary_is_eligible_after_two_newer_candidates(self):
        self.candidate("one", 1)
        self.candidate("two", 2)
        old = self.candidate("seven-days", 7)
        self.run_retention(apply=True)
        self.assertFalse(old.exists())

    def test_explicit_protection_and_candidate_keep_marker_preserve_active_previews(self):
        _, _, old = self.three_old()
        (old / ".keep").touch()
        self.assertEqual(self.rows(self.run_retention(apply=True))["oldest"]["reason"], "keep_marker")
        (old / ".keep").unlink()
        report = self.run_retention(apply=True, protect=[old / "site/index.html"])
        self.assertEqual(self.rows(report)["oldest"]["reason"], "protected_path")
        self.assertTrue(old.is_dir())

    def test_collection_keep_marker_preserves_every_candidate(self):
        self.three_old()
        (self.root / ".keep").touch()
        report = self.run_retention(apply=True)
        self.assertEqual(report["deleted_bytes"], 0)
        self.assertTrue(all(row["reason"] == "root_keep_marker" for row in report["candidates"]))

    def test_unknown_markers_report_mismatch_and_future_dates_are_preserved(self):
        self.three_old()
        for name in ["missing-marker", "unverified", "mismatched-report", "future"]:
            path = self.candidate(name, -1 if name == "future" else 100)
            if name == "missing-marker":
                (path / retention.MARKER).unlink()
            elif name == "unverified":
                data = json.loads((path / retention.MARKER).read_text())
                data["status"] = "failed"
                (path / retention.MARKER).write_text(json.dumps(data))
            elif name == "mismatched-report":
                (path / "report.json").write_text(json.dumps({"revision": "b" * 40}))
        report = self.run_retention(apply=True)
        for name in ["missing-marker", "unverified", "mismatched-report", "future"]:
            self.assertTrue((self.root / name).is_dir())
            self.assertEqual(self.rows(report)[name]["reason"], "unknown_or_linked_directory")

    def test_symlink_candidate_and_nested_symlinks_are_never_removed(self):
        self.three_old()
        outside = self.workspace / "outside"
        outside.mkdir()
        (outside / "original.txt").write_text("Original")
        (self.root / "linked-candidate").symlink_to(outside, target_is_directory=True)
        nested = self.candidate("nested-link", 100)
        (nested / "site/original").symlink_to(outside, target_is_directory=True)
        report = self.run_retention(apply=True)
        self.assertEqual(self.rows(report)["linked-candidate"]["reason"], "unknown_or_linked_directory")
        self.assertEqual(self.rows(report)["nested-link"]["reason"], "contains_symlink")
        self.assertEqual((outside / "original.txt").read_text(), "Original")
        self.assertTrue(nested.is_dir())

    def test_embedded_git_checkout_is_preserved(self):
        self.three_old()
        old = self.candidate("embedded-worktree", 100)
        (old / "site/.git").write_text("gitdir: /outside/repository")
        report = self.run_retention(apply=True)
        self.assertTrue(old.is_dir())
        self.assertEqual(self.rows(report)[old.name]["reason"], "contains_git_checkout")

    def test_source_site_outside_scope_missing_and_linked_roots_are_refused(self):
        for name in ["site", "source"]:
            path = self.workspace / name
            path.mkdir()
            with self.assertRaises(ValueError):
                retention.retain_candidates(path, workspace=self.workspace, now=self.now, apply=True)
        with self.assertRaises(ValueError):
            retention.retain_candidates(self.root / "missing", workspace=self.workspace, now=self.now)
        link = self.root / "linked-collection"
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            retention.retain_candidates(link, workspace=self.workspace, now=self.now)
        leaf = self.candidate("leaf-candidate", 100)
        with self.assertRaises(ValueError):
            retention.retain_candidates(leaf, workspace=self.workspace, now=self.now)

    def test_minimum_keep_age_and_protection_typos_are_refused(self):
        for kwargs in [{"keep": 0}, {"keep": 1}, {"min_age_days": 6}, {"keep": True}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.run_retention(**kwargs)
        with self.assertRaises(ValueError): self.run_retention(protect=[self.root / "typo"])
        with self.assertRaises(ValueError): self.run_retention(protect=[self.workspace])

    def test_protection_added_after_plan_is_rechecked_before_deletion(self):
        _, _, old = self.three_old()
        remove = retention._remove_candidate
        def protect_then_remove(path, *args):
            (path / ".keep").touch()
            return remove(path, *args)
        with patch.object(retention, "_remove_candidate", side_effect=protect_then_remove):
            report = self.run_retention(apply=True)
        self.assertTrue(old.is_dir())
        self.assertEqual(self.rows(report)["oldest"]["action"], "protected_after_plan")
        self.assertEqual(report["deleted_bytes"], 0)

    def test_deletion_failure_is_reported_without_removing_other_data(self):
        _, _, old = self.three_old()
        with patch.object(retention.shutil, "rmtree", side_effect=PermissionError("denied")):
            report = self.run_retention(apply=True)
        self.assertEqual(report["errors"], ["oldest"])
        self.assertTrue(old.is_dir())


if __name__ == "__main__":
    unittest.main()
