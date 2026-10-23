from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.archive_documents import ArchiveValidationError
from scripts.external_resources import load_external_resources, validate_resources


def resource(resource_id: str = "2026-10-23-faryad-quantum-algorithms") -> dict:
    return {
        "id": resource_id,
        "date": resource_id[:10],
        "series": "external-book",
        "title": "Quantum Algorithms from First Principles",
        "summary": "Muhammad Faryad의 양자 알고리즘 원서를 저자 공식 배포처에서 확인합니다.",
        "summary_en": "Read about Muhammad Faryad's quantum algorithms book at the author's official site.",
        "language": "en",
        "author": "Muhammad Faryad",
        "author_url": "https://maven.com/faryad",
        "book_url": "https://maven.com/faryad/o/05455f",
        "tags": ["Quantum algorithms", "Quantum chemistry"],
        "public_reviewed": True,
    }


class ExternalResourcesTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.archive = self.root / "archive"
        self.archive.mkdir()
        self.registry = self.archive / "external-resources.json"

    def write_registry(self, resources: list[dict], **top_fields) -> None:
        self.registry.write_text(
            json.dumps({"version": 1, "resources": resources, **top_fields}, ensure_ascii=False),
            encoding="utf-8",
        )

    def test_load_preserves_reviewed_metadata_and_sorts_without_reading_private_files(self) -> None:
        older = resource("2026-10-22-another-book")
        latest_a = resource("2026-10-23-a-book")
        latest_z = resource("2026-10-23-z-book")
        latest_z["title_en"] = "Quantum algorithms book"
        supplied = [older, latest_a, latest_z]
        before = deepcopy(supplied)
        self.write_registry(supplied)
        (self.archive / "private").mkdir()
        (self.archive / "private" / "book.pdf").write_bytes(b"private book contents")

        expected = [latest_z, latest_a, older]
        self.assertEqual(validate_resources(supplied), expected)
        self.assertEqual(load_external_resources(self.archive), expected)
        self.assertEqual(supplied, before)
        self.assertNotIn("private book contents", json.dumps(expected))

    def test_absent_and_empty_registries_are_optional(self) -> None:
        self.assertEqual(load_external_resources(self.root / "missing-archive"), [])
        self.assertEqual(load_external_resources(self.archive), [])
        self.write_registry([])
        self.assertEqual(load_external_resources(self.archive), [])
        self.assertEqual(validate_resources([]), [])

    def test_registry_shape_version_and_unknown_top_level_fields_are_rejected(self) -> None:
        for payload in (
            "{", "[]", '{"version": 2, "resources": []}',
            '{"version": true, "resources": []}',
            '{"resources": []}', '{"version": 1}',
            '{"version": 1, "resources": {}}',
            '{"version": 1, "resources": [], "private_notes": "hidden"}',
        ):
            with self.subTest(payload=payload):
                self.registry.write_text(payload, encoding="utf-8")
                with self.assertRaises(ArchiveValidationError):
                    load_external_resources(self.archive)

    def test_duplicate_json_keys_and_duplicate_resource_ids_are_rejected(self) -> None:
        self.registry.write_text('{"version": 1, "resources": [], "resources": []}', encoding="utf-8")
        with self.assertRaises(ArchiveValidationError):
            load_external_resources(self.archive)
        item_json = json.dumps(resource())
        duplicated_item_key = item_json.replace('"language": "en"', '"language": "ko", "language": "en"')
        self.registry.write_text('{"version": 1, "resources": [' + duplicated_item_key + '] }', encoding="utf-8")
        with self.assertRaises(ArchiveValidationError):
            load_external_resources(self.archive)
        with self.assertRaises(ArchiveValidationError):
            validate_resources([resource(), resource()])

    def test_explicit_public_review_is_required_and_must_be_boolean(self) -> None:
        for value in (None, False, 1, "true"):
            with self.subTest(value=value):
                item = resource()
                if value is None:
                    del item["public_reviewed"]
                else:
                    item["public_reviewed"] = value
                with self.assertRaises(ArchiveValidationError):
                    validate_resources([item])

    def test_missing_fields_unknown_fields_and_non_resource_values_are_rejected(self) -> None:
        for field in resource():
            with self.subTest(missing=field):
                item = resource()
                del item[field]
                with self.assertRaises(ArchiveValidationError):
                    validate_resources([item])
        for extra in (
            {"file": "private/book.pdf"}, {"email_subject": "private mail"},
            {"download_url": "https://example.com/access?token=secret"},
        ):
            with self.subTest(extra=extra):
                with self.assertRaises(ArchiveValidationError):
                    validate_resources([{**resource(), **extra}])
        for malformed in (None, {}, "book", [None], ["book"]):
            with self.subTest(malformed=malformed):
                with self.assertRaises(ArchiveValidationError):
                    validate_resources(malformed)

    def test_invalid_dates_ids_types_and_public_metadata_are_rejected(self) -> None:
        for mutation in (
            {"id": "2026-10-23-Uppercase"},
            {"date": "2026-10-22"},
            {"date": "2026-02-30", "id": "2026-02-30-book"},
            {"series": "article"}, {"language": "jp"},
            {"title": ""}, {"summary_en": ""}, {"author": ""},
            {"summary": "First line\nSecond line"},
            {"tags": "Quantum"}, {"tags": ["Quantum", "Quantum"]},
        ):
            with self.subTest(mutation=mutation):
                with self.assertRaises(ArchiveValidationError):
                    validate_resources([{**resource(), **mutation}])

    def test_public_text_cannot_contain_private_paths_mail_addresses_or_embedded_urls(self) -> None:
        for field, text in (
            ("summary", "/Users/someone/private/book.pdf"),
            ("summary_en", r"C:\Users\someone\private\book.pdf"),
            ("author", "private@example.com"),
            ("summary", "Read https://mail.google.com/mail/u/0/"),
            ("title_en", "/tmp/private/book.pdf"),
        ):
            with self.subTest(field=field, text=text):
                with self.assertRaises(ArchiveValidationError):
                    validate_resources([{**resource(), field: text}])

    def test_urls_are_public_https_landing_pages_without_access_tokens(self) -> None:
        invalid_urls = (
            "http://maven.com/faryad", "javascript:alert(1)",
            "file:///Users/someone/book.pdf", "//maven.com/faryad",
            "https://user:password@maven.com/faryad",
            "https://maven.com:443/faryad", "https://maven.com/faryad?token=secret",
            "https://maven.com/faryad#private-token",
            "https://localhost/book", "https://127.0.0.1/book",
            "https://book.local/", "https://book.internal/",
            "https://10.1.2.3/book", "https://192.168.1.1/book",
            "https://169.254.169.254/book", "https://[::1]/book",
            "https://[broken/book",
            "https://maven.com/book.pdf", "https://maven.com/book.PDF",
        )
        for field in ("author_url", "book_url"):
            for url in invalid_urls:
                with self.subTest(field=field, url=url):
                    with self.assertRaises(ArchiveValidationError):
                        validate_resources([{**resource(), field: url}])

    def test_symlink_registry_is_rejected(self) -> None:
        outside = self.root / "private-registry.json"
        outside.write_text(json.dumps({"version": 1, "resources": [resource()]}), encoding="utf-8")
        self.registry.symlink_to(outside)
        with self.assertRaises(ArchiveValidationError):
            load_external_resources(self.archive)


if __name__ == "__main__":
    unittest.main()
