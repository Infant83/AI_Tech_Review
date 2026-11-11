from contextlib import ExitStack
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import prepare_publication as prepare
from scripts import publish_public_site as publisher


class PreparePublicationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.source = self.root / "site"
        self.source.mkdir()
        (self.source / "manifest.json").write_text("[]\n")
        (self.source / "index.html").write_text("original public index")
        self.output = self.root / "candidate"
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        for name, value in (("ROOT", self.root), ("SITE_DIR", self.source),
                            ("REVIEWS_DIR", self.source / "reviews"),
                            ("ASSETS_DIR", self.source / "assets"), ("REVIEWS", ())):
            self.stack.enter_context(patch.object(publisher, name, value))
        self.stack.enter_context(patch.object(prepare, "validate_public_artifact", return_value={}))

    def test_candidate_is_independent_and_stamp_and_validation_arguments_are_passed(self):
        def build(arguments):
            self.assertEqual(arguments, ["--preserve-existing", "--revision", "a" * 40])
            self.assertEqual(publisher.SITE_DIR, self.output / "site")
            (publisher.SITE_DIR / "index.html").write_text("new generated index")
            return 0
        with patch.object(publisher, "main", side_effect=build):
            report = prepare.prepare_candidate(self.output, revision="a" * 40)
        self.assertEqual((self.source / "index.html").read_text(), "original public index")
        self.assertEqual((self.output / "site/index.html").read_text(), "new generated index")
        self.assertEqual(publisher.SITE_DIR, self.source)
        self.assertTrue(report["comparison"]["structural_ok"])
        self.assertEqual(json.loads((self.output / "report.json").read_text())["revision"], "a" * 40)
        marker = json.loads((self.output / ".publication-candidate.json").read_text())
        self.assertEqual(marker["kind"], "publication-candidate")
        self.assertEqual(marker["revision"], "a" * 40)
        self.assertEqual(marker["site"], "site")
        self.assertFalse((self.output / "site/.publication-candidate.json").exists())
        self.assertEqual(prepare.validate_public_artifact.call_args.kwargs,
                         {"verify_search": False, "verify_reader_source": False})

    def test_build_failure_preserves_source_and_restores_publisher_paths(self):
        with patch.object(publisher, "main", return_value=2):
            with self.assertRaisesRegex(ValueError, "generation or validation failed"):
                prepare.prepare_candidate(self.output, revision="a" * 40)
        self.assertEqual((self.source / "index.html").read_text(), "original public index")
        self.assertEqual(publisher.SITE_DIR, self.source)
        self.assertFalse((self.output / "report.json").exists())
        self.assertFalse((self.output / ".publication-candidate.json").exists())

    def test_existing_output_and_paths_inside_site_are_rejected_before_building(self):
        self.output.mkdir()
        with self.assertRaises(ValueError):
            prepare.prepare_candidate(self.output, revision="a" * 40)
        with self.assertRaises(ValueError):
            prepare.prepare_candidate(self.source / "candidate", revision="a" * 40)
        link = self.root / "site-link"
        link.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises(ValueError):
            prepare.prepare_candidate(link / "candidate", revision="a" * 40)

    def test_invalid_revision_and_conflicting_baselines_are_rejected(self):
        with self.assertRaises(ValueError):
            prepare.prepare_candidate(self.output, revision="main")
        with self.assertRaisesRegex(ValueError, "either"):
            prepare.prepare_candidate(self.output, revision="a" * 40,
                                       baseline_site=self.source, baseline_snapshot=self.root / "baseline.json")

    def test_explicit_registered_pdf_change_generates_exact_declaration_without_manual_hashes(self):
        identifier = "2026-11-07-test-document"
        old, new = b"%PDF-1.4\nold reviewed PDF", b"%PDF-1.4\nnew reviewed PDF"
        public_name = "archive/files/" + identifier + ".pdf"
        original_pdf = self.source / public_name
        original_pdf.parent.mkdir(parents=True)
        original_pdf.write_bytes(old)
        source_archive = self.root / "archive"
        (source_archive / "files").mkdir(parents=True)
        (source_archive / "files" / (identifier + ".pdf")).write_bytes(new)
        document = {"id": identifier, "date": "2026-11-07", "series": "article",
                    "title": "검토한 PDF", "summary": "공개 PDF 개정", "language": "ko",
                    "tags": [], "file": "files/" + identifier + ".pdf", "public_reviewed": True}
        (source_archive / "manifest.json").write_text(json.dumps({"version": 1, "documents": [document]}))
        public_row = {"id": identifier, "date": document["date"], "href": public_name,
                      "sha256": hashlib.sha256(old).hexdigest()}
        (self.source / "archive-manifest.json").write_text(json.dumps({"version": 1, "documents": [public_row]}))
        def build(arguments):
            (publisher.SITE_DIR / public_name).write_bytes(new)
            (publisher.SITE_DIR / "archive-manifest.json").write_text(json.dumps({"version": 1,
                "documents": [{**public_row, "sha256": hashlib.sha256(new).hexdigest()}]}))
            return 0
        with patch.object(publisher, "main", side_effect=build):
            report = prepare.prepare_candidate(self.output, revision="a" * 40, documents=[identifier])
        declaration = json.loads((self.root / "publication_changes" / ("document-" + identifier + ".json")).read_text())
        self.assertEqual(declaration["files"], {public_name: {"before": hashlib.sha256(old).hexdigest(),
                                                               "after": hashlib.sha256(new).hexdigest()}})
        self.assertEqual(report["selected_documents"], [identifier])
        self.assertEqual(original_pdf.read_bytes(), old)

    def test_unknown_document_is_rejected_before_candidate_build(self):
        with self.assertRaisesRegex(ValueError, "Unknown document"):
            prepare.prepare_candidate(self.output, revision="a" * 40, documents=["2026-11-07-missing"])
        self.assertFalse(self.output.exists())

    def review_fixture(self):
        review = publisher.PublicReview(folder="2026-11-07_test-review", title="검토한 기사",
            subtitle="공개 부제", date="2026-11-07", updated="2026-11-07",
            category="Quantum Computing", tags=("Quantum",), summary="검토한 요약")
        self.stack.enter_context(patch.object(publisher, "REVIEWS", (review,)))
        dist = self.root / review.folder / "dist"
        dist.mkdir(parents=True)
        (dist / "index.html").write_text("new reviewed scientific article")
        registrations = self.root / "publication/reviews"
        registrations.mkdir(parents=True)
        (registrations / (review.folder + ".json")).write_text(json.dumps({"version": 1,
            "source_sha256": "0" * 64, "review": asdict(review)}))
        href = "reviews/" + review.folder + "/index.html"
        path = self.source / href
        path.parent.mkdir(parents=True)
        path.write_text("original scientific article")
        (self.source / "manifest.json").write_text(json.dumps([{"folder": review.folder,
            "href": href, "date": review.date, "title": review.title, "subtitle": review.subtitle,
            "category": review.category, "tags": list(review.tags), "summary": review.summary,
            "translations": [], "assets": []}]))
        return review, dist, href

    def test_review_request_is_persistent_and_future_build_reapplies_the_same_checked_revision(self):
        review, dist, href = self.review_fixture()
        def build(arguments):
            self.assertIn(review.folder, arguments)
            (publisher.SITE_DIR / href).write_bytes((dist / "index.html").read_bytes())
            return 0
        with patch.object(publisher, "main", side_effect=build):
            prepare.prepare_candidate(self.output, revision="a" * 40, reviews=[review.folder])
            # A later CI build starts from the old committed site seed but uses
            # the persistent request and the actually deployed candidate hashes.
            later = self.root / "next-candidate"
            report = prepare.prepare_candidate(later, revision="b" * 40,
                                                baseline_snapshot=self.output / "candidate.json")
        self.assertEqual(report["selected_reviews"], [review.folder])
        self.assertEqual(report["comparison"]["content_changes"], [])
        self.assertEqual((later / "site" / href).read_text(), "new reviewed scientific article")
        declaration = json.loads((self.root / "publication_changes" / (review.folder + ".json")).read_text())
        self.assertEqual(set(declaration["files"]), {href})

    def test_first_ci_replays_checked_request_when_seed_and_deployed_baseline_are_both_old(self):
        review, dist, href = self.review_fixture()
        original_article = (self.source / href).read_bytes()

        def publish_checked(arguments):
            self.assertIn(review.folder, arguments)
            (publisher.SITE_DIR / href).write_bytes((dist / "index.html").read_bytes())
            return 0

        with patch.object(publisher, "main", side_effect=publish_checked):
            prepare.prepare_candidate(self.output, revision="a" * 40, reviews=[review.folder])
            # Preparing a candidate intentionally leaves site/ unchanged. The
            # first CI run therefore has both an old committed seed and an old
            # deployed baseline, plus the checked request and after hashes.
            later = self.root / "first-ci-candidate"
            report = prepare.prepare_candidate(later, revision="b" * 40,
                                                baseline_snapshot=self.output / "baseline.json")

        self.assertEqual(report["rebuilt_reviews"], [review.folder])
        self.assertEqual(report["comparison"]["content_changes"], [href])
        self.assertEqual((later / "site" / href).read_bytes(), (dist / "index.html").read_bytes())
        self.assertEqual((self.source / href).read_bytes(), original_article)

    def test_replayed_request_cannot_succeed_without_its_checked_after_content(self):
        review, dist, href = self.review_fixture()

        def publish_checked(arguments):
            (publisher.SITE_DIR / href).write_bytes((dist / "index.html").read_bytes())
            return 0

        with patch.object(publisher, "main", side_effect=publish_checked):
            prepare.prepare_candidate(self.output, revision="a" * 40, reviews=[review.folder])

        later = self.root / "no-op-ci-candidate"
        with patch.object(publisher, "main", return_value=0):
            with self.assertRaisesRegex(ValueError, "reviewed after hashes"):
                prepare.prepare_candidate(later, revision="b" * 40,
                                            baseline_snapshot=self.output / "baseline.json")
        self.assertFalse((later / "report.json").exists())
        self.assertFalse((later / ".publication-candidate.json").exists())

    def test_unbound_published_request_fails_closed_before_reusing_an_old_seed(self):
        review, dist, href = self.review_fixture()

        def publish_checked(arguments):
            (publisher.SITE_DIR / href).write_bytes((dist / "index.html").read_bytes())
            return 0

        with patch.object(publisher, "main", side_effect=publish_checked):
            prepare.prepare_candidate(self.output, revision="a" * 40, reviews=[review.folder])
        (self.root / "publication_changes" / (review.folder + ".json")).unlink()
        later = self.root / "unbound-ci-candidate"
        with patch.object(publisher, "main") as build:
            with self.assertRaisesRegex(ValueError, "lacks reviewed after hashes.*--review"):
                prepare.prepare_candidate(later, revision="b" * 40,
                                            baseline_snapshot=self.output / "baseline.json")
        build.assert_not_called()
        self.assertFalse(later.exists())

    def test_explicit_no_op_records_output_binding_and_next_metadata_build_reuses_it(self):
        review, dist, href = self.review_fixture()
        (dist / "index.html").write_bytes((self.source / href).read_bytes())

        def publish_checked(arguments):
            self.assertIn(review.folder, arguments)
            (publisher.SITE_DIR / href).write_bytes((dist / "index.html").read_bytes())
            return 0

        with patch.object(publisher, "main", side_effect=publish_checked):
            report = prepare.prepare_candidate(self.output, revision="a" * 40, reviews=[review.folder])
        self.assertEqual(report["comparison"]["content_changes"], [])
        declaration = json.loads((self.root / "publication_changes" / (review.folder + ".json")).read_text())
        self.assertEqual(declaration["files"][href]["before"], declaration["files"][href]["after"])

        def metadata_only(arguments):
            self.assertNotIn(review.folder, arguments)
            return 0

        with patch.object(publisher, "main", side_effect=metadata_only):
            later = prepare.prepare_candidate(self.root / "no-op-metadata-candidate", revision="b" * 40,
                                                baseline_snapshot=self.output / "candidate.json")
        self.assertEqual(later["rebuilt_reviews"], [])

    def test_new_registration_auto_selects_unchanged_review_without_erasing_bilingual_pdf_history(self):
        review, dist, href = self.review_fixture()
        prefix = "reviews/" + review.folder + "/"
        relative_names = ("index.html", "en/index.html", "review_ko.pdf", "en/review_en.pdf")
        for name in relative_names:
            for directory, label in ((self.source / prefix, "original"), (dist, "checked")):
                path = directory / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((label + " " + name).encode())
        old_manifest = json.loads((self.source / "manifest.json").read_text())
        old_manifest[0]["assets"] = ["review_ko.pdf"]
        old_manifest[0]["translations"] = [{"language": "en", "href": prefix + "en/index.html",
                                              "assets": ["review_en.pdf"]}]
        (self.source / "manifest.json").write_text(json.dumps(old_manifest))

        def publish_checked(arguments):
            self.assertIn(review.folder, arguments)
            shutil.copytree(dist, publisher.SITE_DIR / prefix, dirs_exist_ok=True)
            return 0

        with patch.object(publisher, "main", side_effect=publish_checked):
            prepare.prepare_candidate(self.output, revision="a" * 40, reviews=[review.folder],
                                      change_reason="Checked bilingual article and PDF revision")
        declaration_path = self.root / "publication_changes" / (review.folder + ".json")
        original_declaration = declaration_path.read_bytes()
        self.assertEqual(set(json.loads(original_declaration)["files"]),
                         {prefix + name for name in relative_names})

        # A later checkout's committed seed can omit an artifact-only review
        # from its manifest while its persistent request and live baseline exist.
        (self.source / "manifest.json").write_text("[]")
        addition = replace(review, folder="2026-11-08_new-review", title="New checked review")
        addition_dist = self.root / addition.folder / "dist"
        addition_dist.mkdir(parents=True)
        (addition_dist / "index.html").write_text("new checked article")
        (self.root / "publication/reviews" / (addition.folder + ".json")).write_text(json.dumps({
            "version": 1, "source_sha256": "0" * 64, "review": asdict(addition)}))
        addition_href = "reviews/" + addition.folder + "/index.html"

        def publish_both(arguments):
            self.assertIn(review.folder, arguments)
            self.assertIn(addition.folder, arguments)
            shutil.copytree(dist, publisher.SITE_DIR / prefix, dirs_exist_ok=True)
            new_path = publisher.SITE_DIR / addition_href
            new_path.parent.mkdir(parents=True, exist_ok=True)
            new_path.write_bytes((addition_dist / "index.html").read_bytes())
            (publisher.SITE_DIR / "manifest.json").write_text(json.dumps([
                *old_manifest, {"folder": addition.folder, "href": addition_href,
                                "date": addition.date, "assets": [], "translations": []}]))
            return 0

        with patch.object(publisher, "REVIEWS", (review, addition)), \
                patch.object(publisher, "main", side_effect=publish_both):
            baseline = self.output / "candidate.json"
            for index in range(2):
                later = self.root / ("new-registration-candidate-" + str(index))
                report = prepare.prepare_candidate(later, revision="b" * 40,
                                                    baseline_snapshot=baseline)
                self.assertEqual(report["rebuilt_reviews"], sorted([review.folder, addition.folder]))
                self.assertEqual(report["comparison"]["content_changes"], [])
                self.assertEqual(declaration_path.read_bytes(), original_declaration)
                for name in relative_names:
                    self.assertEqual((later / "site" / prefix / name).read_bytes(), (dist / name).read_bytes())
                baseline = later / "candidate.json"
        self.assertTrue((self.root / "publication/requests" / (addition.folder + ".json")).is_file())
        self.assertEqual((self.source / "manifest.json").read_text(), "[]")

    def test_explicit_no_op_replaces_stale_after_binding_with_current_checked_output(self):
        review, dist, href = self.review_fixture()
        (dist / "index.html").write_bytes((self.source / href).read_bytes())
        prepare.write_change_declaration(self.root, review.folder,
            {href: {"before": "1" * 64, "after": "2" * 64}}, "Earlier revision")
        with patch.object(publisher, "main", return_value=0):
            report = prepare.prepare_candidate(self.output, revision="a" * 40,
                reviews=[review.folder], change_reason="Checked current no-op")
        expected = hashlib.sha256((dist / "index.html").read_bytes()).hexdigest()
        declaration = json.loads((self.root / "publication_changes" / (review.folder + ".json")).read_text())
        self.assertEqual(report["comparison"]["content_changes"], [])
        self.assertEqual(declaration, {"version": 1, "reason": "Checked current no-op",
                                      "files": {href: {"before": expected, "after": expected}}})
        with patch.object(publisher, "main", return_value=0) as build:
            later = prepare.prepare_candidate(self.root / "stale-binding-metadata-candidate",
                revision="b" * 40, baseline_snapshot=self.output / "candidate.json")
        self.assertEqual(later["rebuilt_reviews"], [])
        self.assertNotIn(review.folder, build.call_args.args[0])

    def test_later_real_revision_records_new_baseline_hashes_and_reason(self):
        review, dist, href = self.review_fixture()

        def publish_checked(arguments):
            (publisher.SITE_DIR / href).write_bytes((dist / "index.html").read_bytes())
            return 0

        with patch.object(publisher, "main", side_effect=publish_checked):
            prepare.prepare_candidate(self.output, revision="a" * 40, reviews=[review.folder],
                                      change_reason="First checked revision")
            previous = hashlib.sha256((dist / "index.html").read_bytes()).hexdigest()
            (dist / "index.html").write_text("second checked scientific revision")
            report = prepare.prepare_candidate(self.root / "second-real-revision", revision="b" * 40,
                reviews=[review.folder], baseline_snapshot=self.output / "candidate.json",
                change_reason="Second checked revision")
        current = hashlib.sha256((dist / "index.html").read_bytes()).hexdigest()
        declaration = json.loads((self.root / "publication_changes" / (review.folder + ".json")).read_text())
        self.assertEqual(report["comparison"]["content_changes"], [href])
        self.assertEqual(declaration, {"version": 1, "reason": "Second checked revision",
                                      "files": {href: {"before": previous, "after": current}}})

    def test_new_review_with_no_existing_after_hashes_can_publish(self):
        review, dist, href = self.review_fixture()
        manifest = (self.source / "manifest.json").read_text()
        (self.source / "manifest.json").write_text("[]")
        (self.source / href).unlink()

        def publish_new(arguments):
            self.assertIn(review.folder, arguments)
            (publisher.SITE_DIR / href).write_bytes((dist / "index.html").read_bytes())
            (publisher.SITE_DIR / "manifest.json").write_text(manifest)
            return 0

        with patch.object(publisher, "main", side_effect=publish_new):
            report = prepare.prepare_candidate(self.output, revision="a" * 40)
        self.assertEqual(report["rebuilt_reviews"], [review.folder])
        self.assertEqual((self.output / "site" / href).read_bytes(), (dist / "index.html").read_bytes())
        self.assertTrue((self.root / "publication/requests" / (review.folder + ".json")).is_file())

    def test_source_change_during_build_does_not_record_a_stale_review_request(self):
        review, dist, href = self.review_fixture()
        def build(arguments):
            (publisher.SITE_DIR / href).write_bytes((dist / "index.html").read_bytes())
            (dist / "index.html").write_text("concurrent unchecked edit")
            return 0
        with patch.object(publisher, "main", side_effect=build):
            with self.assertRaisesRegex(ValueError, "inputs changed while"):
                prepare.prepare_candidate(self.output, revision="a" * 40, reviews=[review.folder])
        self.assertFalse((self.root / "publication/requests" / (review.folder + ".json")).exists())

    def test_metadata_only_edit_refreshes_hub_and_request_without_rebuilding_current_article(self):
        review, dist, href = self.review_fixture()
        def publish_checked(arguments):
            self.assertIn(review.folder, arguments)
            (publisher.SITE_DIR / href).write_bytes((dist / "index.html").read_bytes())
            return 0
        with patch.object(publisher, "main", side_effect=publish_checked):
            prepare.prepare_candidate(self.output, revision="a" * 40, reviews=[review.folder])
        # A locally refreshed site seed already contains the exact published
        # article. A metadata-only edit must not invoke article publication.
        shutil.rmtree(self.source)
        shutil.copytree(self.output / "site", self.source)
        request = self.root / "publication/requests" / (review.folder + ".json")
        before = json.loads(request.read_text())
        registration = self.root / "publication/reviews" / (review.folder + ".json")
        source = json.loads(registration.read_text())
        source["review"].update(summary="목록만 새로 정리한 요약", tags=["Updated topic"])
        registration.write_text(json.dumps(source))
        updated_review = replace(review, summary=source["review"]["summary"], tags=("Updated topic",))
        self.stack.enter_context(patch.object(publisher, "REVIEWS", (updated_review,)))
        later = self.root / "metadata-candidate"
        original_article = (self.source / href).read_bytes()
        def refresh_metadata(arguments):
            self.assertNotIn(review.folder, arguments)
            manifest = json.loads((publisher.SITE_DIR / "manifest.json").read_text())
            refreshed = publisher.refresh_registered_hub_metadata(manifest, set())
            (publisher.SITE_DIR / "manifest.json").write_text(json.dumps(refreshed))
            return 0
        with patch.object(publisher, "main", side_effect=refresh_metadata):
            report = prepare.prepare_candidate(later, revision="b" * 40,
                                                baseline_snapshot=self.output / "candidate.json")
        self.assertEqual(report["rebuilt_reviews"], [])
        self.assertEqual((later / "site" / href).read_bytes(), original_article)
        self.assertEqual(report["comparison"]["content_changes"], [])
        row = json.loads((later / "site/manifest.json").read_text())[0]
        self.assertEqual(row["summary"], updated_review.summary)
        self.assertEqual(row["tags"], list(updated_review.tags))
        after = json.loads(request.read_text())
        self.assertEqual(after["article_registration_sha256"], before["article_registration_sha256"])
        self.assertNotEqual(after["registration_sha256"], before["registration_sha256"])

    def test_concurrent_metadata_edit_is_rejected_before_refreshing_a_review_request(self):
        review, dist, href = self.review_fixture()
        registration = self.root / "publication/reviews" / (review.folder + ".json")
        def build(arguments):
            (publisher.SITE_DIR / href).write_bytes((dist / "index.html").read_bytes())
            source = json.loads(registration.read_text())
            source["review"]["summary"] = "Concurrent unchecked hub edit"
            registration.write_text(json.dumps(source))
            return 0
        with patch.object(publisher, "main", side_effect=build):
            with self.assertRaisesRegex(ValueError, "inputs changed while"):
                prepare.prepare_candidate(self.output, revision="a" * 40, reviews=[review.folder])
        self.assertFalse((self.root / "publication/requests" / (review.folder + ".json")).exists())
        self.assertFalse((self.output / ".publication-candidate.json").exists())


if __name__ == "__main__":
    unittest.main()
