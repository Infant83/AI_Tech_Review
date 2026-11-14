from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.public_media import export_media, verify_export, worker_manifest_bytes
import hashlib
import json


class PublicMediaTests(unittest.TestCase):
    def versioned_fixture(self, root, label, documents, previous=(), legacy=False):
        site = root / (label + "-site"); site.mkdir()
        files = {}
        for name, payload in documents.items():
            path = site / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(payload)
            files[name] = {"sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
        output = root / (label + "-export")
        with patch("scripts.public_media.capture_site", return_value={"files": files}):
            export_media(site, output, validate=False, previous_exports=previous)
        if legacy:
            manifest = json.loads((output / "media-manifest.json").read_text())
            manifest["version"] = 1
            manifest["aliases"] = {path: row["editions"][row["current"]] for path, row in manifest["aliases"].items()}
            self.write_manifest(output, manifest)
        return output

    def write_manifest(self, output, manifest):
        (output / "media-manifest.json").write_text(json.dumps(manifest))
        (output / "worker/manifest.mjs").write_bytes(worker_manifest_bytes(manifest))

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

    def test_verified_v1_and_v2_history_retains_only_still_public_path_editions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            a, b, removed = "archive/a.pdf", "reviews/b.pdf", "archive/removed.pdf"
            first = self.versioned_fixture(root, "first", {a: b"%PDF-first-a", b: b"%PDF-first-b", removed: b"%PDF-removed"}, legacy=True)
            second = self.versioned_fixture(root, "second", {a: b"%PDF-second-a", b: b"%PDF-second-b"}, [first])
            third = self.versioned_fixture(root, "third", {a: b"%PDF-third-a", b: b"%PDF-second-b"}, [second, first])
            manifest = json.loads((third / "media-manifest.json").read_text())
            self.assertEqual(manifest["version"], 2)
            self.assertEqual(set(manifest["aliases"]), {"/AI_Tech_Review/" + a, "/AI_Tech_Review/" + b})
            for name, payloads in ((a, [b"%PDF-first-a", b"%PDF-second-a", b"%PDF-third-a"]), (b, [b"%PDF-first-b", b"%PDF-second-b"])):
                entry = manifest["aliases"]["/AI_Tech_Review/" + name]
                hashes = [hashlib.sha256(payload).hexdigest() for payload in payloads]
                self.assertEqual(set(entry["editions"]), set(hashes))
                self.assertEqual(entry["current"], hashes[-1])
            self.assertEqual(len(manifest["objects"]), 5)
            self.assertTrue(verify_export(first)["ok"])
            self.assertTrue(verify_export(third)["ok"])
            self.assertEqual((root / "third-site" / a).read_bytes(), b"%PDF-third-a")

    def test_corrupt_previous_export_fails_before_output_is_created(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); old = self.exported_fixture(root)
            obj = next((old / "objects").rglob("*.pdf"))
            payload = obj.read_bytes(); obj.write_bytes(payload.replace(b"public", b"broken"))
            self.assertEqual(obj.stat().st_size, len(payload))
            site = root / "new-site"; site.mkdir()
            with self.assertRaisesRegex(ValueError, "corrupt media object"):
                export_media(site, root / "new-export", validate=False, previous_exports=[old])
            self.assertFalse((root / "new-export").exists())

    def test_object_directory_symlink_is_rejected_before_previous_import(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); old = self.exported_fixture(root)
            objects = old / "objects"; moved = root / "moved-objects"; objects.rename(moved)
            objects.symlink_to(moved, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "corrupt media object"):
                verify_export(old)
            site = root / "new-site"; site.mkdir()
            with self.assertRaises(ValueError):
                export_media(site, root / "new-export", validate=False, previous_exports=[old])
            self.assertFalse((root / "new-export").exists())

    def test_schema_rejects_orphans_wrong_keys_editions_paths_and_sizes(self):
        for kind in ("orphan", "wrong_key", "missing_current", "edition_sha", "unsafe_path", "size_bool", "size_zero", "version", "scope"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                output = self.exported_fixture(Path(temp)); manifest = json.loads((output / "media-manifest.json").read_text())
                path, entry = next(iter(manifest["aliases"].items())); key, row = next(iter(manifest["objects"].items()))
                if kind == "orphan": manifest["aliases"] = {}
                elif kind == "wrong_key":
                    wrong = key + ".pdf"; manifest["objects"][wrong] = manifest["objects"].pop(key); entry["editions"][entry["current"]] = wrong
                elif kind == "missing_current": entry["current"] = "0" * 64
                elif kind == "edition_sha": entry["editions"] = {"0" * 64: key}; entry["current"] = "0" * 64
                elif kind == "unsafe_path": manifest["aliases"] = {path.replace("document.pdf", "%2e%2e/document.pdf"): entry}
                elif kind == "size_bool": row["size_bytes"] = True
                elif kind == "size_zero": row["size_bytes"] = 0
                elif kind == "version": manifest["version"] = 3
                elif kind == "scope": manifest["scope"] = "/another/"
                self.write_manifest(output, manifest)
                with self.assertRaises(ValueError): verify_export(output)

    def test_duplicate_json_keys_are_not_silently_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            output = self.exported_fixture(Path(temp))
            source = output / "media-manifest.json"
            source.write_text(source.read_text().replace('"version": 2', '"version": 2, "version": 2'))
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                verify_export(output)

    def test_tampered_generated_prior_mapping_cannot_be_imported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); prior = self.exported_fixture(root)
            (prior / "worker/manifest.mjs").write_text("export default {};\n")
            site = root / "new-site"; site.mkdir()
            with self.assertRaisesRegex(ValueError, "Worker media manifest differs"):
                export_media(site, root / "new-export", validate=False, previous_exports=[prior])
            self.assertFalse((root / "new-export").exists())
