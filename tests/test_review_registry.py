from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import unittest

from scripts.publish_public_site import PublicAgent, PublicReview, PublicTranslation, REVIEWS, ROOT
from scripts.review_registry import ReviewRegistrationError, load_review_registry


class ReviewRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def source(self, folder="2026-11-07_test-review", **changes):
        review = dict(folder=folder, title="리뷰", subtitle="공개 부제", date="2026-11-07",
                      updated="2026-11-07", category="Quantum Computing", tags=["Quantum"], summary="공개 요약")
        review.update(changes)
        return {"version": 1, "review": review}

    def write(self, source, name=None):
        path = self.directory / (name or source["review"]["folder"] + ".json")
        path.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
        return path

    def load(self):
        return load_review_registry(self.directory, PublicReview, PublicTranslation, PublicAgent)

    def test_historical_review_registrations_load_every_field_losslessly_and_preserve_order(self):
        registrations = [json.loads(path.read_text()) for path in (ROOT / "publication/reviews").glob("*.json")]
        historical = sorted((source for source in registrations if source.get("legacy_position") is not None),
                            key=lambda source: source["legacy_position"])
        by_folder = {row.folder: row for row in REVIEWS}
        self.assertTrue(historical)
        expected_folders = [source["review"]["folder"] for source in historical]
        self.assertEqual([row.folder for row in REVIEWS if row.folder in expected_folders], expected_folders)
        for source in historical:
            actual = json.loads(json.dumps(asdict(by_folder[source["review"]["folder"]])))
            self.assertEqual(actual, source["review"])

    def test_independent_new_registrations_use_defaults_without_shared_sequence(self):
        self.write(self.source())
        self.write(self.source("2026-11-07_second-review"))
        result = self.load()
        self.assertEqual({row.folder for row in result}, {"2026-11-07_test-review", "2026-11-07_second-review"})
        self.assertEqual(result[0].translations, ())
        self.assertEqual(result[0].responsible_editor, "김현중")

    def test_unknown_missing_or_wrong_type_fields_are_rejected(self):
        for mutation in ({"private_notes": "hidden"}, {"tags": "Quantum"}, {"primary_sources_checked": 1}, {"title": "line\nbreak"}, {"date": "2026-02-30"}):
            with self.subTest(mutation=mutation):
                self.write(self.source(**mutation))
                with self.assertRaises(ReviewRegistrationError):
                    self.load()
        source = self.source()
        del source["review"]["title"]
        self.write(source)
        with self.assertRaises(ReviewRegistrationError):
            self.load()

    def test_nested_translation_paths_duplicates_and_unknown_fields_are_rejected(self):
        row = {"language": "en", "subdir": "en", "label": "English"}
        for translations in ([{**row, "subdir": "../en"}], [row, row], [{**row, "private": "hidden"}]):
            with self.subTest(translations=translations):
                self.write(self.source(translations=translations))
                with self.assertRaises(ReviewRegistrationError):
                    self.load()

    def test_filename_identity_duplicate_json_and_symlinks_are_rejected(self):
        path = self.write(self.source(), "other.json")
        with self.assertRaises(ReviewRegistrationError):
            self.load()
        path.unlink()
        path = self.write(self.source())
        path.write_text('{"version":1,"version":1,"review":{}}')
        with self.assertRaises(ReviewRegistrationError):
            self.load()
        path.unlink()
        path.symlink_to(ROOT / "publication/reviews" / (REVIEWS[0].folder + ".json"))
        with self.assertRaises(ReviewRegistrationError):
            self.load()

    def test_legacy_positions_are_frozen_order_only_and_duplicates_rejected(self):
        a, b = self.source(), self.source("2026-11-07_second-review")
        a["legacy_position"], b["legacy_position"] = 0, 1
        self.write(a)
        self.write(b)
        self.assertEqual([row.folder for row in self.load()], [a["review"]["folder"], b["review"]["folder"]])
        b["legacy_position"] = 0
        self.write(b)
        with self.assertRaises(ReviewRegistrationError):
            self.load()


if __name__ == "__main__":
    unittest.main()
