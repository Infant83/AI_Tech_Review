from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.archive_documents import ArchiveValidationError, import_document, load_documents


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "archive_documents.py"
PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"


def document(document_id: str = "2026-10-16-quantum-review") -> dict:
    return {
        "id": document_id,
        "date": document_id[:10],
        "series": "daily-quantum",
        "title": "양자 연구 리뷰",
        "summary": "양자컴퓨팅 연구의 주요 결과를 소개합니다.",
        "language": "ko",
        "file": f"files/{document_id}.pdf",
        "tags": ["Quantum"],
        "public_reviewed": True,
    }


class ArchiveDocumentsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.archive = self.root / "archive"
        self.archive.mkdir()
        (self.archive / "files").mkdir()

    def write_registry(self, documents: list[dict], **top_fields) -> None:
        for item in documents:
            path = self.archive / "files" / f"{item['id']}.pdf"
            path.write_bytes(PDF_BYTES)
        manifest = {"version": 1, "documents": documents, **top_fields}
        (self.archive / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    def test_only_registered_files_are_loaded_and_values_are_preserved(self) -> None:
        older = document("2026-10-09-weekly-review")
        older["series"] = "weekly-review"
        newer = document()
        newer["source_title"] = "Daily Quantum Review"
        self.write_registry([older, newer])
        (self.archive / "files" / "private-unlisted.pdf").write_bytes(b"private email contents")

        result = load_documents(self.archive)

        self.assertEqual(result, [newer, older])
        self.assertNotIn("private-unlisted", json.dumps(result))

    def test_missing_and_empty_registries_load_as_empty(self) -> None:
        self.assertEqual(load_documents(self.root / "new-archive"), [])
        self.assertEqual(load_documents(self.archive), [])
        (self.archive / "manifest.json").write_text("\n", encoding="utf-8")
        self.assertEqual(load_documents(self.archive), [])
        self.write_registry([])
        self.assertEqual(load_documents(self.archive), [])

    def test_explicit_public_review_is_required_and_must_be_boolean(self) -> None:
        for value in (None, False, 1, "true"):
            with self.subTest(value=value):
                item = document()
                if value is None:
                    del item["public_reviewed"]
                else:
                    item["public_reviewed"] = value
                self.write_registry([item])
                with self.assertRaises(ArchiveValidationError):
                    load_documents(self.archive)

    def test_unknown_private_fields_and_unknown_top_fields_are_rejected(self) -> None:
        for extra in ({"email_subject": "hidden"}, {"source_url": "https://mail.example.com/inbox"}):
            with self.subTest(extra=extra):
                item = {**document(), **extra}
                self.write_registry([item])
                with self.assertRaises(ArchiveValidationError):
                    load_documents(self.archive)
        self.write_registry([], private_notes="hidden")
        with self.assertRaises(ArchiveValidationError):
            load_documents(self.archive)

    def test_email_urls_and_local_paths_are_rejected_in_public_text(self) -> None:
        for text in ("Contact private@example.com", "Open https://mail.google.com/mail/u/0/", "/Users/someone/private.pdf", r"C:\Users\somebody\private.pdf"):
            with self.subTest(text=text):
                item = document()
                item["summary"] = text
                self.write_registry([item])
                with self.assertRaises(ArchiveValidationError):
                    load_documents(self.archive)

    def test_traversal_absolute_and_id_mismatched_paths_are_rejected(self) -> None:
        for file_name in ("../private.pdf", "/tmp/private.pdf", "files/other.pdf", "files/../private.pdf"):
            with self.subTest(file=file_name):
                item = document()
                item["file"] = file_name
                self.write_registry([item])
                with self.assertRaises(ArchiveValidationError):
                    load_documents(self.archive)

    def test_symlink_pdf_and_symlink_directory_are_rejected(self) -> None:
        item = document()
        self.write_registry([item])
        pdf_path = self.archive / item["file"]
        external_pdf = self.root / "external.pdf"
        external_pdf.write_bytes(PDF_BYTES)
        pdf_path.unlink()
        pdf_path.symlink_to(external_pdf)
        with self.assertRaises(ArchiveValidationError):
            load_documents(self.archive)
        pdf_path.unlink()
        (self.archive / "files").rmdir()
        outside = self.root / "outside-files"
        outside.mkdir()
        (outside / pdf_path.name).write_bytes(PDF_BYTES)
        (self.archive / "files").symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ArchiveValidationError):
            load_documents(self.archive)

    def test_symlink_manifest_and_archive_root_are_rejected(self) -> None:
        manifest = self.root / "external-manifest.json"
        manifest.write_text('{"version": 1, "documents": []}', encoding="utf-8")
        (self.archive / "manifest.json").symlink_to(manifest)
        with self.assertRaises(ArchiveValidationError):
            load_documents(self.archive)
        linked = self.root / "linked-archive"
        linked.symlink_to(self.archive, target_is_directory=True)
        with self.assertRaises(ArchiveValidationError):
            load_documents(linked)

    def test_duplicate_ids_are_rejected(self) -> None:
        self.write_registry([document(), document()])
        with self.assertRaisesRegex(ArchiveValidationError, "Duplicate document id"):
            load_documents(self.archive)

    def test_invalid_date_id_series_language_and_text_are_rejected(self) -> None:
        mutations = (
            {"date": "2026-02-30", "id": "2026-02-30-quantum-review"},
            {"date": "2026-1-1"},
            {"date": "2026-10-15"},
            {"id": "2026-10-16-Uppercase"},
            {"series": "unknown"},
            {"language": "jp"},
            {"title": ""},
            {"title": "x" * 241},
            {"summary": "x" * 1601},
            {"tags": ["Quantum", "Quantum"]},
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                item = {**document(), **mutation}
                self.write_registry([item])
                with self.assertRaises(ArchiveValidationError):
                    load_documents(self.archive)

    def test_invalid_and_missing_pdf_are_rejected(self) -> None:
        item = document()
        self.write_registry([item])
        (self.archive / item["file"]).write_bytes(b"not a PDF")
        with self.assertRaisesRegex(ArchiveValidationError, "PDF header"):
            load_documents(self.archive)
        (self.archive / item["file"]).unlink()
        with self.assertRaises(ArchiveValidationError):
            load_documents(self.archive)

    def test_duplicate_json_fields_and_boolean_version_are_rejected(self) -> None:
        manifest_path = self.archive / "manifest.json"
        manifest_path.write_text('{"version": 1, "version": 1, "documents": []}', encoding="utf-8")
        with self.assertRaises(ArchiveValidationError):
            load_documents(self.archive)
        manifest_path.write_text('{"version": true, "documents": []}', encoding="utf-8")
        with self.assertRaises(ArchiveValidationError):
            load_documents(self.archive)

    def cli(self, source: Path, *extra: str, public_reviewed: bool = True) -> subprocess.CompletedProcess[str]:
        args = [sys.executable, str(SCRIPT), str(source), "--archive-dir", str(self.archive), "--date", "2026-10-16", "--series", "article", "--title", "공개 아티클", "--summary", "사용자가 제공한 공개 리뷰입니다.", "--language", "ko", "--id", "2026-10-16-user-article"]
        if public_reviewed:
            args.append("--public-reviewed")
        return subprocess.run([*args, *extra], capture_output=True, text=True, check=False)

    def test_cli_import_duplicate_and_explicit_replace(self) -> None:
        source = self.root / "user.pdf"
        source.write_bytes(PDF_BYTES)
        first = self.cli(source)
        self.assertEqual(first.returncode, 0, first.stderr)
        loaded = load_documents(self.archive)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["series"], "article")
        self.assertEqual((self.archive / loaded[0]["file"]).read_bytes(), PDF_BYTES)
        self.assertEqual(source.read_bytes(), PDF_BYTES)
        previous_manifest = (self.archive / "manifest.json").read_bytes()
        source.write_bytes(PDF_BYTES + b"\n% revised\n")

        duplicate = self.cli(source)
        self.assertNotEqual(duplicate.returncode, 0)
        self.assertIn("--replace", duplicate.stderr)
        self.assertEqual((self.archive / "manifest.json").read_bytes(), previous_manifest)
        self.assertEqual((self.archive / loaded[0]["file"]).read_bytes(), PDF_BYTES)

        replaced = self.cli(source, "--replace", "--tag", "Research")
        self.assertEqual(replaced.returncode, 0, replaced.stderr)
        self.assertEqual(len(load_documents(self.archive)), 1)
        self.assertEqual(load_documents(self.archive)[0]["tags"], ["Research"])
        self.assertEqual((self.archive / loaded[0]["file"]).read_bytes(), source.read_bytes())
        self.assertFalse(list(self.archive.glob(".manifest-*")))
        self.assertFalse(list((self.archive / "files").glob(".*.pdf")))

    def test_cli_requires_review_flag_and_rejects_invalid_pdf(self) -> None:
        source = self.root / "user.pdf"
        source.write_bytes(PDF_BYTES)
        result = self.cli(source, public_reviewed=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--public-reviewed", result.stderr)
        source.write_bytes(b"not a PDF")
        result = self.cli(source)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(load_documents(self.archive), [])
        self.assertFalse((self.archive / "manifest.json").exists())

    def test_import_does_not_overwrite_unregistered_file_even_with_replace(self) -> None:
        item = document()
        orphan = self.archive / item["file"]
        orphan.write_bytes(b"private unregistered file")
        source = self.root / "user.pdf"
        source.write_bytes(PDF_BYTES)
        with self.assertRaisesRegex(ArchiveValidationError, "unregistered"):
            import_document(source, item, self.archive, replace=True)
        self.assertEqual(orphan.read_bytes(), b"private unregistered file")
        self.assertFalse((self.archive / "manifest.json").exists())

    def test_import_rejects_symlink_source_and_source_directory(self) -> None:
        source = self.root / "user.pdf"
        source.write_bytes(PDF_BYTES)
        linked_source = self.root / "linked.pdf"
        linked_source.symlink_to(source)
        with self.assertRaises(ArchiveValidationError):
            import_document(linked_source, document(), self.archive)
        source_dir = self.root / "source-dir"
        source_dir.mkdir()
        (source_dir / "user.pdf").write_bytes(PDF_BYTES)
        linked_dir = self.root / "linked-dir"
        linked_dir.symlink_to(source_dir, target_is_directory=True)
        with self.assertRaises(ArchiveValidationError):
            import_document(linked_dir / "user.pdf", document(), self.archive)

    def test_failed_manifest_write_rolls_back_pdf_on_import_and_replace(self) -> None:
        source = self.root / "user.pdf"
        source.write_bytes(PDF_BYTES + b"\n% revised\n")
        item = document()
        with patch("scripts.archive_documents._write_manifest_atomic", side_effect=OSError("write failed")):
            with self.assertRaises(OSError):
                import_document(source, item, self.archive)
        self.assertFalse((self.archive / item["file"]).exists())
        self.assertEqual(load_documents(self.archive), [])
        self.write_registry([deepcopy(item)])
        previous_manifest = (self.archive / "manifest.json").read_bytes()
        with patch("scripts.archive_documents._write_manifest_atomic", side_effect=OSError("write failed")):
            with self.assertRaises(OSError):
                import_document(source, item, self.archive, replace=True)
        self.assertEqual((self.archive / item["file"]).read_bytes(), PDF_BYTES)
        self.assertEqual((self.archive / "manifest.json").read_bytes(), previous_manifest)


if __name__ == "__main__":
    unittest.main()
