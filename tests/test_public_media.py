from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.public_media import export_media, verify_export
import hashlib
import json


class PublicMediaTests(unittest.TestCase):
    def exported_fixture(self, root):
        site = root / "site"; site.mkdir()
        payload = b"%PDF-1.4 public data\n%%EOF"
        name = "archive/files/document.pdf"
        path = site / name; path.parent.mkdir(parents=True); path.write_bytes(payload)
        files = {name: {"sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}}
        output = root / "export"
        with patch("scripts.public_media.capture_site", return_value={"files": files}):
            export_media(site, output, validate=False)
        return output

    def test_duplicate_legacy_pdf_paths_export_once_and_corruption_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve(); site = root / "site"; site.mkdir()
            payload = b"%PDF-1.4 public data\n%%EOF"; digest = hashlib.sha256(payload).hexdigest()
            files = {}
            for name in ("reviews/article/review.pdf", "archive/files/document.pdf"):
                path = site / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(payload)
                files[name] = {"sha256": digest, "bytes": len(payload)}
            with patch("scripts.public_media.capture_site", return_value={"files": files}):
                result = export_media(site, root / "export", validate=False)
            self.assertEqual(result["pdf_aliases"], 2); self.assertEqual(result["unique_objects"], 1)
            self.assertTrue(verify_export(root / "export")["ok"])
            next((root / "export/objects").rglob("*.pdf")).write_bytes(b"corrupt")
            with self.assertRaises(ValueError): verify_export(root / "export")
            with self.assertRaises(ValueError): export_media(site, site / "unsafe", validate=False)

    def test_stale_worker_mapping_is_rejected_even_when_all_objects_are_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            output = self.exported_fixture(Path(temp))
            (output / "worker/manifest.mjs").write_text('export default {"aliases":{}};\n')
            with self.assertRaisesRegex(ValueError, "Worker media manifest differs"):
                verify_export(output)

    def test_changed_export_aliases_must_match_the_worker(self):
        with tempfile.TemporaryDirectory() as temp:
            output = self.exported_fixture(Path(temp))
            source = output / "media-manifest.json"
            manifest = json.loads(source.read_text())
            key = manifest["aliases"].pop("/AI_Tech_Review/archive/files/document.pdf")
            manifest["aliases"]["/AI_Tech_Review/archive/files/different.pdf"] = key
            source.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "Worker media manifest differs"):
                verify_export(output)

    def test_missing_worker_mapping_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            output = self.exported_fixture(Path(temp))
            (output / "worker/manifest.mjs").unlink()
            with self.assertRaisesRegex(ValueError, "regular files"):
                verify_export(output)

    def test_symlinked_manifest_or_worker_directory_is_rejected(self):
        for relative in ("media-manifest.json", "worker/manifest.mjs", "worker"):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                output = self.exported_fixture(root)
                path = output / relative
                moved = root / "moved"
                path.rename(moved)
                path.symlink_to(moved, target_is_directory=moved.is_dir())
                with self.assertRaisesRegex(ValueError, "regular files"):
                    verify_export(output)
