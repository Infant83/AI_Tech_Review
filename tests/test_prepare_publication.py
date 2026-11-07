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
