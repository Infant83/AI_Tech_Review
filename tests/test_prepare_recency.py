"""Candidate recency must come from the selected, verified prior publication.

These small, offline sites exercise the real preparation, metadata validation,
snapshot and reader enrichment paths. Only the full publication builder is
replaced with a callback that writes the fixture's final public files.
"""
from contextlib import ExitStack
from dataclasses import asdict
from datetime import datetime
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import prepare_publication as prepare
from scripts import publication_release as release
from scripts import publish_public_site as publisher
from scripts import reader_engagement_publish as reader
from scripts.publication_intent import source_digest
from scripts.publication_snapshot import capture_site


class PrepareRecencyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.source = self.root / "site"
        self.source.mkdir()
        self.frontend = reader.FRONTEND_DIR
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.review = publisher.PublicReview(
            folder="2026-11-01_fixture", title="Reviewed scientific result",
            subtitle="Fixture subtitle", date="2026-11-01", updated="2026-11-01",
            category="Physics", tags=("Physics",), summary="Fixture summary")
        self.href = "reviews/" + self.review.folder + "/index.html"
        self.en_href = "reviews/" + self.review.folder + "/en/index.html"
        self.pdf = "reviews/" + self.review.folder + "/result.pdf"
        self.figure = "reviews/" + self.review.folder + "/figure.svg"
        self.manifest = [{
            "folder": self.review.folder, "title": self.review.title,
            "date": self.review.date, "updated": self.review.updated,
            "href": self.href, "assets": ["result.pdf", "figure.svg"],
            "translations": [{"language": "en", "href": self.en_href, "assets": []}],
        }]
        self.final_files = {
            "index.html": self.html("Public journal index"),
            self.href: self.html("Current reviewed result: 2.0 eV"),
            self.en_href: self.html("Current English result: 2.0 eV"),
            self.pdf: b"%PDF-1.4\nReviewed fixture result: 2.0 eV\n%%EOF\n",
            self.figure: b'<svg xmlns="http://www.w3.org/2000/svg"><text>2.0 eV</text></svg>',
        }
        for name, value in (("ROOT", self.root), ("SITE_DIR", self.source),
                            ("REVIEWS_DIR", self.source / "reviews"),
                            ("ASSETS_DIR", self.source / "assets"),
                            ("REVIEWS", (self.review,))):
            self.stack.enter_context(patch.object(publisher, name, value))
        # Keep any repository display-migration declarations out of this small
        # independent fixture, while reading the actual checked frontend bytes.
        self.stack.enter_context(patch.object(reader, "ROOT", self.root))
        old_files = {**self.final_files, self.href: self.html("Old seeded result: 1.0 eV")}
        self.write_site(self.source, old_files)
        self.enrich(self.source, "1" * 40, "2026-11-02T00:00:00Z")
        self.seed_updates = (self.source / reader.UPDATES_NAME).read_bytes()
        self.live = self.root / "approved-site"
        shutil.copytree(self.source, self.live)
        self.write_site(self.live, self.final_files)
        self.enrich(self.live, "2" * 40, "2026-11-10T08:09:10Z")
        self.prior_updates = (self.live / reader.UPDATES_NAME).read_bytes()
        self.prior = json.loads(self.prior_updates)
        self.assertNotEqual(self.seed_updates, self.prior_updates)
        self.prior_article = self.prior["articles"][0]
        self.assertEqual(self.prior_article["updatedAt"], "2026-11-10T08:09:10Z")
        dist = self.root / self.review.folder / "dist"
        dist.mkdir(parents=True)
        (dist / "index.html").write_bytes(self.final_files[self.href])
        registrations = self.root / "publication/reviews"
        registrations.mkdir(parents=True)
        self.write_json(registrations / (self.review.folder + ".json"), {
            "version": 1, "source_sha256": source_digest(dist), "review": asdict(self.review)})
        self.bundle = self.make_bundle(self.root / "sealed-baseline")
        self.source_before = self.file_bytes(self.source)

    @staticmethod
    def html(body):
        return ('<!doctype html><html><head><title>Scientific fixture</title></head>'
                '<body><main>' + body + '</main></body></html>').encode()

    @staticmethod
    def write_json(path, value):
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def file_bytes(directory):
        return {path.relative_to(directory).as_posix(): path.read_bytes()
                for path in directory.rglob("*") if path.is_file()}

    def write_site(self, site, files, manifest=None):
        for name, payload in files.items():
            target = site / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
        self.write_json(site / "manifest.json", self.manifest if manifest is None else manifest)

    def enrich(self, site, revision, now):
        instant = datetime.fromisoformat(now.replace("Z", "+00:00"))

        class FixedDatetime(datetime):
            @classmethod
            def now(cls, tz=None):
                return instant if tz else instant.replace(tzinfo=None)

        with patch.object(reader, "datetime", FixedDatetime):
            return reader.enrich_site(site, revision=revision, frontend_dir=self.frontend)

    def make_bundle(self, directory):
        directory.mkdir()
        snapshot = capture_site(self.live)
        catalog = (self.live / reader.CATALOG_NAME).read_bytes()
        self.write_json(directory / "snapshot.json", snapshot)
        self.write_json(directory / "release.json", {
            "version": 1, "revision": "2" * 40, "snapshot": snapshot,
            "catalog_sha256": hashlib.sha256(catalog).hexdigest(),
            "artifact_files": {reader.UPDATES_NAME: {
                "sha256": hashlib.sha256(self.prior_updates).hexdigest(),
                "bytes": len(self.prior_updates)}},
        })
        (directory / reader.CATALOG_NAME).write_bytes(catalog)
        (directory / reader.UPDATES_NAME).write_bytes(self.prior_updates)
        return directory / "snapshot.json"

    def builder(self, now, *, expected_prior=None, changes=None, manifest=None):
        expected_prior = self.prior_updates if expected_prior is None else expected_prior

        def build(arguments):
            stage = publisher.SITE_DIR
            # This assertion runs before writing or enriching the final files:
            # preparation must replace the old checkout's recency first.
            self.assertEqual((stage / reader.UPDATES_NAME).read_bytes(), expected_prior)
            self.write_site(stage, {**self.final_files, **(changes or {})}, manifest)
            self.enrich(stage, arguments[arguments.index("--revision") + 1], now)
            return 0

        return build

    def candidate(self, name, now, *, changes=None, manifest=None):
        output = self.root / name
        with patch.object(publisher, "main", side_effect=self.builder(now, changes=changes, manifest=manifest)) as build:
            report = prepare.prepare_candidate(output, revision="3" * 40, baseline_snapshot=self.bundle)
        build.assert_called_once()
        self.assertEqual(self.file_bytes(self.source), self.source_before)
        updates = json.loads((output / "site" / reader.UPDATES_NAME).read_text())
        self.assert_html_versions(output / "site", updates)
        return report, updates

    def assert_html_versions(self, site, updates):
        for row in json.loads((site / "manifest.json").read_text()):
            article = next(item for item in updates["articles"] if item["id"] == row["folder"])
            for variant in [row, *row.get("translations", [])]:
                text = (site / variant["href"]).read_text()
                match = re.search(r'id="reader-engagement-config">(.*?)</script>', text)
                self.assertIsNotNone(match)
                config = json.loads(match[1])
                self.assertEqual(config["articleVersion"], article["revision"])
                self.assertEqual(config["article"]["id"], article["id"])
                self.assertEqual(config["pageVersion"], reader.content_digest(site / variant["href"]))

    def test_two_rebuild_times_preserve_verified_live_recency_and_reader_versions(self):
        for index, now in enumerate(("2026-11-12T11:00:00Z", "2026-11-14T21:22:23Z")):
            with self.subTest(now=now):
                report, updates = self.candidate("unchanged-" + str(index), now)
                self.assertEqual(report["baseline_updates_source"], "sealed_release_bundle")
                self.assertEqual(updates, self.prior)
                self.assertEqual(updates["articles"][0]["revision"], self.prior_article["revision"])
                self.assertEqual(updates["articles"][0]["updatedAt"], self.prior_article["updatedAt"])

    def test_actual_html_pdf_figure_or_translation_change_gets_a_new_revision_and_time(self):
        mutations = {
            self.href: self.html("A new scientific conclusion: 3.0 eV"),
            self.pdf: b"%PDF-1.4\nNew reviewed fixture result: 3.0 eV\n%%EOF\n",
            self.figure: b'<svg xmlns="http://www.w3.org/2000/svg"><text>3.0 eV</text></svg>',
            self.en_href: self.html("A revised English scientific conclusion: 3.0 eV"),
        }
        now = "2026-11-12T12:34:56Z"
        for index, (name, payload) in enumerate(mutations.items()):
            with self.subTest(asset=name):
                _, updates = self.candidate("changed-" + str(index), now, changes={name: payload})
                article = updates["articles"][0]
                self.assertNotEqual(article["revision"], self.prior_article["revision"])
                self.assertEqual(article["updatedAt"], now)
                self.assertEqual(article["publishedAt"], self.prior_article["publishedAt"])
                self.assertEqual(article["change"], "updated")

    def test_new_article_uses_its_original_date_while_existing_article_keeps_prior_recency(self):
        identifier = "2026-11-09_new-fixture"
        href = "reviews/" + identifier + "/index.html"
        addition = {"folder": identifier, "title": "New reviewed article", "date": "2026-11-09",
                    "href": href, "assets": [], "translations": []}
        _, updates = self.candidate("new-article", "2026-11-12T12:34:56Z",
                                    changes={href: self.html("New article content")},
                                    manifest=[*self.manifest, addition])
        by_id = {item["id"]: item for item in updates["articles"]}
        self.assertEqual(by_id[self.review.folder], self.prior_article)
        self.assertEqual(by_id[identifier]["updatedAt"], "2026-11-09T00:00:00Z")
        self.assertEqual(by_id[identifier]["change"], "new")

    def test_missing_or_invalid_sealed_metadata_stops_before_build_or_candidate_output(self):
        def alter_json(directory, name, mutate):
            path = directory / name
            document = json.loads(path.read_text())
            mutate(document)
            self.write_json(path, document)

        mutations = (
            ("missing-release", lambda d: (d / "release.json").unlink()),
            ("missing-catalog", lambda d: (d / reader.CATALOG_NAME).unlink()),
            ("missing-updates", lambda d: (d / reader.UPDATES_NAME).unlink()),
            ("invalid-release", lambda d: (d / "release.json").write_text("{invalid")),
            ("updates-bytes", lambda d: (d / reader.UPDATES_NAME).write_bytes(self.prior_updates + b" ")),
            ("catalog-bytes", lambda d: (d / reader.CATALOG_NAME).write_bytes((d / reader.CATALOG_NAME).read_bytes() + b" ")),
            ("snapshot-mismatch", lambda d: alter_json(d, "release.json", lambda r: r["snapshot"].update(version=2))),
            ("catalog-revision", lambda d: alter_json(d, "release.json", lambda r: r.update(revision="f" * 40))),
        )
        for name, mutate in mutations:
            with self.subTest(case=name):
                directory = self.root / ("invalid-" + name)
                shutil.copytree(self.bundle.parent, directory)
                mutate(directory)
                output = self.root / ("rejected-" + name)
                with patch.object(publisher, "main") as build:
                    with self.assertRaises(ValueError):
                        prepare.prepare_candidate(output, revision="3" * 40,
                                                  baseline_snapshot=directory / "snapshot.json")
                build.assert_not_called()
                self.assertFalse(output.exists())
                self.assertFalse((output / ".publication-candidate.json").exists())
                self.assertEqual(self.file_bytes(self.source), self.source_before)

    def test_explicit_local_baseline_is_offline_and_its_updates_replace_the_seed(self):
        local = self.root / "selected-local-site"
        shutil.copytree(self.live, local)
        chosen = copy.deepcopy(self.prior)
        chosen["articles"][0]["updatedAt"] = "2026-11-11T01:02:03Z"
        chosen_bytes = (json.dumps(chosen, indent=2) + "\n").encode()
        (local / reader.UPDATES_NAME).write_bytes(chosen_bytes)
        output = self.root / "local-candidate"
        # Even an accidental attempt to retrieve a live baseline is a failure.
        with patch.object(release, "urlopen", side_effect=AssertionError("Offline baseline accessed the network")) as network, \
                patch.object(publisher, "main", side_effect=self.builder(
                    "2026-11-15T12:34:56Z", expected_prior=chosen_bytes)) as build:
            self.assertEqual(prepare.main(["--output", str(output), "--revision", "4" * 40,
                                           "--baseline-site", str(local)]), 0)
        network.assert_not_called()
        build.assert_called_once()
        updates = json.loads((output / "site" / reader.UPDATES_NAME).read_text())
        self.assertEqual(updates, chosen)
        self.assert_html_versions(output / "site", updates)
        self.assertEqual(json.loads((output / "report.json").read_text())["baseline_updates_source"], "explicit_local_site")
        self.assertEqual(self.file_bytes(self.source), self.source_before)


if __name__ == "__main__":
    unittest.main()
