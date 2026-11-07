import json
from pathlib import Path
import tempfile
import unittest

from scripts.publication_intent import pending_review_intents, review_inputs, source_digest, write_review_intent


class PublicationIntentTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.folder = "2026-11-07_test-review"
        self.dist = self.root / self.folder / "dist"
        self.dist.mkdir(parents=True)
        (self.dist / "index.html").write_text("reviewed HTML")
        (self.dist / "figure.svg").write_text("reviewed figure")
        registrations = self.root / "publication/reviews"
        registrations.mkdir(parents=True)
        self.registration = registrations / (self.folder + ".json")
        self.registration.write_text(json.dumps({"version": 1, "source_sha256": source_digest(self.dist), "review": {}}))

    def pending(self, explicit=()):
        return pending_review_intents(self.root, {self.folder}, set(explicit), {self.folder})

    def test_changed_existing_source_requires_explicit_intent_and_stale_intent_is_rejected(self):
        self.assertEqual(self.pending(), {})
        (self.dist / "figure.svg").write_text("revised figure")
        with self.assertRaisesRegex(ValueError, "explicit reviewed update"):
            self.pending()
        inputs = self.pending([self.folder])[self.folder]
        write_review_intent(self.root, self.folder, inputs)
        self.assertEqual(self.pending()[self.folder], inputs)
        (self.dist / "index.html").write_text("further unchecked HTML")
        with self.assertRaisesRegex(ValueError, "inputs changed after validation"):
            self.pending()
        self.assertNotEqual(self.pending([self.folder])[self.folder], inputs)

    def test_v2_metadata_edits_preserve_the_checked_article_and_keep_the_full_fingerprint(self):
        inputs = review_inputs(self.root, self.folder)
        write_review_intent(self.root, self.folder, inputs)
        source = json.loads(self.registration.read_text())
        source["review"].update(summary="New reviewed hub summary", subtitle="New subtitle",
                                category="Materials AI", tags=["Materials", "AI"])
        self.registration.write_text(json.dumps(source))
        updated = self.pending()[self.folder]
        self.assertEqual(updated["source_sha256"], inputs["source_sha256"])
        self.assertEqual(updated["article_registration_sha256"], inputs["article_registration_sha256"])
        self.assertNotEqual(updated["registration_sha256"], inputs["registration_sha256"])

    def test_v2_protected_registration_changes_still_require_explicit_article_review(self):
        original = self.registration.read_text()
        inputs = review_inputs(self.root, self.folder)
        write_review_intent(self.root, self.folder, inputs)
        for changes in ({"title": "Unchecked title"}, {"translations": [{"language": "en", "subdir": "en", "label": "English"}]},
                        {"date": "2026-11-08"}, {"updated": "2026-11-08"}, {"ai_system": "Unchecked provenance"}):
            with self.subTest(changes=changes):
                source = json.loads(original)
                source["review"].update(changes)
                self.registration.write_text(json.dumps(source))
                with self.assertRaisesRegex(ValueError, "inputs changed"):
                    self.pending()
                self.assertNotEqual(self.pending([self.folder])[self.folder]["article_registration_sha256"],
                                    inputs["article_registration_sha256"])
        source = json.loads(original)
        source["source_sha256"] = "a" * 64
        self.registration.write_text(json.dumps(source))
        with self.assertRaisesRegex(ValueError, "inputs changed"):
            self.pending()

    def test_v2_semantically_identical_registration_formatting_is_harmless(self):
        inputs = review_inputs(self.root, self.folder)
        write_review_intent(self.root, self.folder, inputs)
        self.registration.write_text(self.registration.read_text() + "\n")
        self.assertEqual(self.pending()[self.folder]["article_registration_sha256"], inputs["article_registration_sha256"])

    def test_legacy_request_requires_exact_input_until_safe_migration(self):
        inputs = review_inputs(self.root, self.folder)
        requests = self.root / "publication/requests"
        requests.mkdir()
        path = requests / (self.folder + ".json")
        path.write_text(json.dumps({"version": 1, "review": self.folder,
            "source_sha256": inputs["source_sha256"], "registration_sha256": inputs["registration_sha256"]}))
        migrated = self.pending()[self.folder]
        self.assertEqual(migrated, inputs)
        self.registration.write_text(self.registration.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "inputs changed"):
            self.pending()
        migrated = self.pending([self.folder])[self.folder]
        write_review_intent(self.root, self.folder, migrated)
        self.assertEqual(json.loads(path.read_text())["version"], 2)
        self.assertEqual(self.pending()[self.folder], migrated)

    def test_source_digest_tracks_names_and_bytes_but_ignores_os_metadata(self):
        before = source_digest(self.dist)
        (self.dist / ".DS_Store").write_bytes(b"desktop metadata")
        self.assertEqual(source_digest(self.dist), before)
        (self.dist / "figure.svg").rename(self.dist / "renamed.svg")
        self.assertNotEqual(source_digest(self.dist), before)

    def test_linked_sources_requests_and_unknown_reviews_are_rejected(self):
        (self.dist / "linked.html").symlink_to(self.dist / "index.html")
        with self.assertRaises(ValueError):
            source_digest(self.dist)
        (self.dist / "linked.html").unlink()
        with self.assertRaisesRegex(ValueError, "Unknown review"):
            pending_review_intents(self.root, {self.folder}, {"unknown"}, set())
        inputs = review_inputs(self.root, self.folder)
        write_review_intent(self.root, self.folder, inputs)
        request = self.root / "publication/requests" / (self.folder + ".json")
        data = json.loads(request.read_text())
        data["private_notes"] = "hidden"
        request.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Invalid review publication request"):
            self.pending()


if __name__ == "__main__":
    unittest.main()
