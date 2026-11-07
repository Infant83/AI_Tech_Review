from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.public_media import export_media, verify_export
import hashlib


class PublicMediaTests(unittest.TestCase):
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
