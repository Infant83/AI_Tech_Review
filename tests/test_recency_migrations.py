import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.recency_migrations import load_recency_migrations, preserve_display_recency


class RecencyMigrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.directory = self.root / "publication/display-revisions"
        self.directory.mkdir(parents=True)
        self.article = {
            "id": "2026-11-06_example",
            "path": "/AI_Tech_Review/reviews/2026-11-06_example/",
            "paths": ["/AI_Tech_Review/reviews/2026-11-06_example/",
                      "/AI_Tech_Review/reviews/2026-11-06_example/en/"],
            "title": "Reviewed article", "publishedAt": "2026-11-06",
            "before_revision": "a" * 64, "after_revision": "b" * 64,
            "updatedAt": "2026-11-08T10:20:30Z", "change": "updated",
        }
        self.document = {"version": 1, "reason": "Reviewed current journal name display only",
                         "baseline": {"revision": "c" * 40, "updates_sha256": "d" * 64},
                         "articles": [self.article]}

    def write(self, document=None, name="brand.json"):
        (self.directory / name).write_text(json.dumps(self.document if document is None else document), encoding="utf-8")

    def current(self, **changes):
        result = {key: copy.deepcopy(value) for key, value in self.article.items()
                  if key not in {"before_revision", "after_revision"}}
        result.update(revision=self.article["after_revision"], updatedAt="2026-11-09T03:00:00Z", change="new")
        result.update(changes)
        return result

    def test_missing_directory_and_empty_directory_have_no_migrations(self):
        self.assertEqual(load_recency_migrations(self.root), {})
        self.directory.rmdir()
        self.assertEqual(load_recency_migrations(self.root), {})

    def test_exact_reviewed_revision_inherits_dates_without_mutating_content_or_identity(self):
        self.write()
        migrations = load_recency_migrations(self.root)
        current = self.current()
        original = copy.deepcopy(current)
        inherited = preserve_display_recency(current, migrations)
        self.assertEqual(current, original)
        self.assertEqual(inherited, {**original, "revision": self.article["before_revision"],
                                     "updatedAt": self.article["updatedAt"], "change": "updated"})
        self.assertEqual(preserve_display_recency(inherited, migrations), inherited)
        self.assertEqual(preserve_display_recency(current, {}), original)

    def test_fresh_raw_after_digest_always_maps_to_the_same_editorial_revision(self):
        self.write()
        migrations = load_recency_migrations(self.root)
        first = preserve_display_recency(self.current(), migrations)
        rebuilt = self.current(updatedAt=first["updatedAt"], change=first["change"])
        self.assertEqual(preserve_display_recency(rebuilt, migrations), first)
        self.assertEqual(first["revision"], self.article["before_revision"])
        self.assertEqual(migrations[self.article["id"]]["after_revision"], self.article["after_revision"])

    def test_identical_complete_edition_can_restore_its_verified_live_date(self):
        self.article["before_revision"] = self.article["after_revision"]
        self.write()
        migrations = load_recency_migrations(self.root)
        current = self.current()
        restored = preserve_display_recency(current, migrations)
        self.assertEqual(restored["revision"], current["revision"])
        self.assertEqual(restored["updatedAt"], self.article["updatedAt"])
        self.assertEqual(restored["change"], self.article["change"])
        self.assertEqual(preserve_display_recency(restored, migrations), restored)
        changed = self.current(revision="e" * 64)
        self.assertEqual(preserve_display_recency(changed, migrations), changed)

    def test_complete_identity_and_all_aliases_must_match(self):
        self.write()
        migrations = load_recency_migrations(self.root)
        for changes in (
            {"id": "2026-11-06_other"},
            {"path": self.article["paths"][1]},
            {"paths": [self.article["path"]]},
            {"title": "Different title"},
            {"publishedAt": "2026-11-07"},
        ):
            with self.subTest(changes=changes):
                current = self.current(**changes)
                self.assertEqual(preserve_display_recency(current, migrations), current)

    def test_old_seed_and_changed_body_or_figure_never_inherit_display_dates(self):
        source = self.root / "article"
        source.mkdir()
        html = source / "index.html"
        figure = source / "figure.svg"
        html.write_text("<title>Old journal</title><main>Reviewed scientific result</main>")
        figure.write_text('<svg><text>1.0 eV</text></svg>')

        def revision():
            assets = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.iterdir())}
            payload = json.dumps({"title": self.article["title"], "content": assets}, sort_keys=True).encode()
            return hashlib.sha256(payload).hexdigest()

        self.article["before_revision"] = revision()
        html.write_text("<title>Current journal</title><main>Reviewed scientific result</main>")
        self.article["after_revision"] = revision()
        self.write()
        migrations = load_recency_migrations(self.root)
        self.assertEqual(preserve_display_recency(self.current(), migrations)["updatedAt"], self.article["updatedAt"])
        old_seed = self.current(revision=self.article["before_revision"])
        self.assertEqual(preserve_display_recency(old_seed, migrations), old_seed)
        for target, content in ((html, "<title>Current journal</title><main>A new scientific conclusion</main>"),
                                (figure, '<svg><text>2.0 eV</text></svg>')):
            with self.subTest(asset=target.name):
                original = target.read_bytes()
                target.write_text(content)
                changed = self.current(revision=revision())
                self.assertNotEqual(changed["revision"], self.article["after_revision"])
                self.assertEqual(preserve_display_recency(changed, migrations), changed)
                target.write_bytes(original)

    def test_invalid_document_or_baseline_is_rejected(self):
        mutations = (
            lambda d: d.update(extra="not permitted"),
            lambda d: d.pop("reason"),
            lambda d: d.update(version=True),
            lambda d: d.update(reason="   "),
            lambda d: d.update(articles={}),
            lambda d: d["baseline"].update(extra="not permitted"),
            lambda d: d["baseline"].update(revision="c" * 39),
            lambda d: d["baseline"].update(updates_sha256="Z" * 64),
        )
        for mutate in mutations:
            document = copy.deepcopy(self.document)
            mutate(document)
            with self.subTest(document=document):
                self.write(document)
                with self.assertRaises(ValueError):
                    load_recency_migrations(self.root)

    def test_invalid_article_fields_dates_and_hashes_are_rejected(self):
        mutations = (
            lambda a: a.update(extra="not permitted"),
            lambda a: a.pop("before_revision"),
            lambda a: a.update(id="../other"),
            lambda a: a.update(title=" "),
            lambda a: a.update(publishedAt="2026-02-30"),
            lambda a: a.update(publishedAt="20261106"),
            lambda a: a.update(updatedAt="2026-11-08T25:20:30Z"),
            lambda a: a.update(updatedAt="2026-11-08T10:20:30+00:00"),
            lambda a: a.update(updatedAt="2026-11-08T10:20:30.123Z"),
            lambda a: a.update(change="cosmetic"),
            lambda a: a.update(change=[]),
            lambda a: a.update(before_revision="a" * 63),
            lambda a: a.update(after_revision="B" * 64),
            lambda a: a.update(paths=a["paths"][::-1]),
            lambda a: a.update(paths=[a["path"], a["path"]]),
            lambda a: a.update(paths=[]),
            lambda a: a.update(paths=a["path"]),
            lambda a: a.update(path="/AI_Tech_Review/reviews/absent/"),
        )
        for mutate in mutations:
            document = copy.deepcopy(self.document)
            mutate(document["articles"][0])
            with self.subTest(article=document["articles"][0]):
                self.write(document)
                with self.assertRaises(ValueError):
                    load_recency_migrations(self.root)

    def test_invalid_scoped_or_noncanonical_paths_are_rejected(self):
        for path in ("https://example.org/review", "/other/review/", "/AI_Tech_Review/../private/",
                     "/AI_Tech_Review/reviews/%2e%2e/", "/AI_Tech_Review/reviews/a/?redirect=x",
                     "/AI_Tech_Review/reviews/a/#section", "/AI_Tech_Review/reviews//a/",
                     "/AI_Tech_Review/reviews/a/index.html", "/AI_Tech_Review/reviews/\\a/"):
            with self.subTest(path=path):
                document = copy.deepcopy(self.document)
                document["articles"][0].update(path=path, paths=[path])
                self.write(document)
                with self.assertRaises(ValueError):
                    load_recency_migrations(self.root)

    def test_duplicate_ids_and_paths_within_or_across_files_are_rejected(self):
        duplicate = copy.deepcopy(self.document)
        duplicate["articles"].append(copy.deepcopy(self.article))
        self.write(duplicate)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            load_recency_migrations(self.root)
        self.write()
        self.write(name="second.json")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            load_recency_migrations(self.root)
        duplicate = copy.deepcopy(self.document)
        duplicate["articles"][0]["id"] = "2026-11-06_other"
        self.write(duplicate, name="second.json")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            load_recency_migrations(self.root)

    def test_duplicate_json_keys_invalid_json_and_json_directories_are_rejected(self):
        self.write()
        path = self.directory / "brand.json"
        path.write_text(path.read_text().replace('"version": 1', '"version": 1, "version": 1', 1))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            load_recency_migrations(self.root)
        path.write_text("{malformed")
        with self.assertRaises(ValueError):
            load_recency_migrations(self.root)
        path.unlink()
        path.mkdir()
        with self.assertRaisesRegex(ValueError, "regular file"):
            load_recency_migrations(self.root)

    def test_symlink_files_and_input_directories_are_rejected(self):
        self.write()
        outside = self.root / "outside.json"
        outside.write_text((self.directory / "brand.json").read_text())
        link = self.directory / "linked.json"
        link.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink"):
            load_recency_migrations(self.root)
        link.unlink()
        (self.directory / "brand.json").unlink()
        self.directory.rmdir()
        outside_directory = self.root / "elsewhere"
        outside_directory.mkdir()
        self.directory.symlink_to(outside_directory, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            load_recency_migrations(self.root)
        self.directory.unlink()
        (self.root / "publication").rmdir()
        (self.root / "publication").symlink_to(outside_directory, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            load_recency_migrations(self.root)


if __name__ == "__main__":
    unittest.main()
