import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import os
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

    def test_concurrent_backup_destination_is_never_overwritten(self):
        destination = self.root / "same-name.tar.gz"
        real_link = os.link
        def other_finished_first(source, target):
            destination.write_bytes(b"other completed backup")
            return real_link(source, target)
        with patch("scripts.release_backup.os.link", side_effect=other_finished_first):
            with self.assertRaises(FileExistsError): create_backup(self.site, destination)
        self.assertEqual(destination.read_bytes(), b"other completed backup")
