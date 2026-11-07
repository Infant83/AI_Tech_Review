import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from scripts.archive_documents import import_document, document_version, load_documents
from scripts.pdf_editions import historical_editions, preserve_previous, stage_editions, validate_editions


class PDFEditionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve(); self.archive = self.root / "archive"; self.archive.mkdir()
        (self.archive / "manifest.json").write_text('{"version":2,"entries":"entries"}')
        (self.archive / "entries").mkdir()
        self.doc = {"id": "2026-11-07-edition-example", "date": "2026-11-07", "series": "lecture-notes",
                    "title": "강의", "summary": "판본 보존 검사", "language": "ko", "file": "files/2026-11-07-edition-example.pdf",
                    "tags": [], "public_reviewed": True}
        self.first = self.root / "first.pdf"; self.first.write_bytes(b"%PDF-1.4 old edition\n%%EOF")
        self.second = self.root / "second.pdf"; self.second.write_bytes(b"%PDF-1.4 new edition\n%%EOF")

    def test_replace_keeps_original_bytes_and_legacy_id_with_separate_note_fingerprint(self):
        import_document(self.first, self.doc, self.archive)
        token = document_version(self.archive, self.doc)
        import_document(self.second, self.doc, self.archive, replace=True, expected_version=token)
        digest = hashlib.sha256(self.second.read_bytes()).hexdigest()
        historical = historical_editions(self.archive, self.doc["id"], digest)
        self.assertEqual(len(historical), 1)
        self.assertEqual(historical[0]["sha256"], hashlib.sha256(self.first.read_bytes()).hexdigest())
        self.assertEqual((self.archive / self.doc["file"]).read_bytes(), self.second.read_bytes())
        self.assertEqual(load_documents(self.archive)[0]["id"], self.doc["id"])
        # Replacing metadata or importing the same bytes doesn't mint editions.
        import_document(self.second, self.doc, self.archive, replace=True, expected_version=document_version(self.archive, self.doc))
        self.assertEqual(historical_editions(self.archive, self.doc["id"], digest), historical)
        site = self.root / "site"; stage = site / "archive"; stage.mkdir(parents=True)
        row = {"id": self.doc["id"], "sha256": digest}
        stage_editions(self.archive, stage, [row])
        self.assertEqual(validate_editions(site, row), [])
        (site / row["editions"][0]["href"]).write_bytes(self.second.read_bytes())
        self.assertTrue(validate_editions(site, row))

    def test_hash_named_editions_cannot_be_mutated_or_escape_archive(self):
        target = preserve_previous(self.archive, self.doc["id"], self.first)
        target.write_bytes(b"%PDF-corrupt")
        with self.assertRaises(ValueError): preserve_previous(self.archive, self.doc["id"], self.first)
        with self.assertRaises(ValueError): historical_editions(self.archive, self.doc["id"], "a" * 64)
        with self.assertRaises(ValueError): preserve_previous(self.archive, "../private", self.first)

    def test_prior_reader_fixture_without_editions_is_unchanged(self):
        self.assertEqual(validate_editions(self.root, {"id": "legacy"}), [])
