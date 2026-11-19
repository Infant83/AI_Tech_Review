"""Synthetic contract tests; no provider, database, build, or live API access."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import inspect
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import admin_inventory as inventory
from scripts.publication_intent import review_inputs


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "source"
        self.root.mkdir()
        self.baseline = Path(self.temp.name) / "baseline"
        self.baseline.mkdir()
        for directory in ("scripts", "publication/reviews", "publication/requests", "publication_changes",
                          "archive/entries", "archive/files"):
            (self.root / directory).mkdir(parents=True)
        models = "from __future__ import annotations\nfrom dataclasses import dataclass\n\n" + "\n\n".join(
            inspect.getsource(model) for model in (inventory.PublicTranslation, inventory.PublicAgent, inventory.PublicReview))
        (self.root / "scripts/publish_public_site.py").write_text(models, encoding="utf-8")
        self.folder = "2026-11-01_example-review"
        self.registration = {"version": 1, "review": {
            "folder": self.folder, "title": "An explicit review", "subtitle": "A public subtitle",
            "date": "2026-11-01", "updated": "2026-11-01", "category": "Quantum science", "tags": ["quantum"],
            "summary": "Public summary", "translations": [{"language": "en", "subdir": "en", "label": "English"}]}}
        self.write_json("publication/reviews/" + self.folder + ".json", self.registration)
        dist = self.root / self.folder / "dist"
        (dist / "en").mkdir(parents=True)
        (dist / "index.html").write_text("<p>Private manuscript body must not be returned.</p>")
        (dist / "en/index.html").write_text("<p>Translated body.</p>")
        self.documents = []
        for identifier, series in (("2026-11-02-brief", "daily-quantum"),
                                   ("2026-11-02-separate-brief", "daily-research")):
            self.add_document(identifier, series=series)
        self.write_json("archive/manifest.json", {"version": 2, "entries": "entries"})
        self.external = {"id": "2026-11-03-official-book", "date": "2026-11-03", "series": "external-book",
                         "title": "Official landing page", "summary": "A public resource", "summary_en": "A public resource",
                         "language": "en", "author": "Public author", "author_url": "https://example.org/author",
                         "book_url": "https://example.org/book", "tags": ["book"], "public_reviewed": True}
        self.write_json("archive/external-resources.json", {"version": 1, "resources": [self.external]})
        self.make_baseline()

    def write_json(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def add_document(self, identifier, *, series="lecture-notes", payload=b"%PDF-1.7\nsynthetic original\n"):
        document = {"id": identifier, "date": identifier[:10], "series": series, "title": "Identical title",
                    "summary": "Public document description", "language": "ko", "file": "files/" + identifier + ".pdf",
                    "tags": ["science"], "public_reviewed": True}
        self.documents.append(document)
        self.write_json("archive/entries/" + identifier + ".json", document)
        (self.root / "archive" / document["file"]).write_bytes(payload)
        return document

    def make_baseline(self, *, orphan=False):
        sha = hashlib.sha256(b"decorated public HTML").hexdigest()
        content = hashlib.sha256(b"public scientific content").hexdigest()
        self.snapshot = {"version": 1, "reviews": {}, "archive": {}, "external": {}, "publications": {},
                         "files": {}, "missing_files": [], "declared_hash_mismatches": []}
        href = "reviews/" + self.folder + "/index.html"
        translated = "reviews/" + self.folder + "/en/index.html"
        for path in (href, translated):
            self.snapshot["files"][path] = {"sha256": sha, "content_sha256": content, "bytes": 31}
        self.snapshot["reviews"][self.folder] = {
            "href": href, "metric_path": "/AI_Tech_Review/reviews/" + self.folder + "/", "date": "2026-11-01",
            "translations": {"en": {"href": translated, "metric_path": None}}, "references": [href, translated]}
        for document in self.documents:
            href = "archive/" + document["file"]
            payload = (self.root / "archive" / document["file"]).read_bytes()
            checksum = hashlib.sha256(payload).hexdigest()
            self.snapshot["archive"][document["id"]] = {"href": href, "study_href": None,
                                                          "date": document["date"], "references": [href]}
            self.snapshot["files"][href] = {"sha256": checksum, "content_sha256": checksum, "bytes": len(payload)}
        self.snapshot["external"][self.external["id"]] = {"book_url": self.external["book_url"]}
        self.catalog = {"revision": "a" * 40, "articles": [{"id": self.folder,
                        "path": "/AI_Tech_Review/reviews/" + self.folder + "/", "title": "An explicit review",
                        "publishedAt": "2026-11-01", "topic": "review"}]}
        if orphan:
            identifier = "2026-11-04_catalog-orphan"
            path = "reviews/" + identifier + "/index.html"
            self.snapshot["files"][path] = {"sha256": sha, "content_sha256": content, "bytes": 31}
            self.catalog["articles"].append({"id": identifier, "path": "/AI_Tech_Review/reviews/" + identifier + "/",
                                             "title": "Catalog reconciliation", "publishedAt": "2026-11-04", "topic": "review"})
        self.snapshot["publications"] = {a["id"]: {k: a[k] for k in ("path", "topic", "publishedAt")}
                                         for a in self.catalog["articles"]}
        self.updates = {"version": 1, "pages": {}, "articles": []}
        self.write_baseline()

    def write_baseline(self):
        raw = lambda value: (json.dumps(value, indent=2) + "\n").encode("utf-8")
        catalog = raw(self.catalog)
        updates = raw(self.updates)
        self.release = {"version": 1, "revision": self.catalog["revision"],
                        "catalog_sha256": hashlib.sha256(catalog).hexdigest(), "snapshot": self.snapshot,
                        "initial_payloads": {}, "artifact_files": {**{
                            name: {"sha256": record["sha256"], "bytes": record["bytes"]}
                            for name, record in self.snapshot["files"].items()}, "reader-publications.json": {
                            "sha256": hashlib.sha256(catalog).hexdigest(), "bytes": len(catalog)}, "reader-updates.json": {
                            "sha256": hashlib.sha256(updates).hexdigest(), "bytes": len(updates)}}}
        for name, payload in (("snapshot.json", raw(self.snapshot)), ("release.json", raw(self.release)),
                              ("reader-publications.json", catalog), ("reader-updates.json", updates)):
            (self.baseline / name).write_bytes(payload)

    def build(self, *, baseline=True):
        return inventory.build_inventory(self.root, self.baseline / "snapshot.json" if baseline else None)

    def rows(self, result):
        return {item["id"]: item for item in result["items"]}

    def error(self, code, call=None):
        with self.assertRaises(inventory.InventoryError) as caught:
            (call or self.build)()
        self.assertEqual(caught.exception.code, code)
        self.assertNotIn(str(self.root), str(caught.exception))
        return caught.exception

    def intent(self, version=2):
        data = {"version": version, "review": self.folder, **review_inputs(self.root, self.folder)}
        if version == 1:
            del data["article_registration_sha256"]
        self.write_json("publication/requests/" + self.folder + ".json", data)
        return data

    def test_explicit_registrations_include_nonnotification_and_do_not_deduplicate(self):
        result = self.build()
        self.assertEqual(result["totals"]["registered"], 4)
        self.assertEqual(result["totals"]["displayed"], 4)
        self.assertEqual(result["totals"]["byKind"], {"archive": 2, "external": 1, "review": 1})
        rows = self.rows(result)
        self.assertTrue(rows["review:" + self.folder]["notificationCatalogMember"])
        for document in self.documents:
            row = rows["archive:" + document["id"]]
            self.assertFalse(row["notificationCatalogMember"])
            self.assertEqual(row["releaseMembership"], "present")
            self.assertEqual(row["contentComparison"]["state"], "matches")
            self.assertEqual(row["versionEvidence"]["basis"], "current_registration_and_pdf_only")
            self.assertEqual(row["checkedInputState"]["article"], "not_recorded")
        self.assertEqual([r["id"] for r in result["items"]][1:3],
                         sorted("archive:" + d["id"] for d in self.documents))

    def test_without_baseline_is_explicit_unknown_not_empty_success_or_pending(self):
        self.intent()
        result = self.build(baseline=False)
        self.assertEqual(result["baseline"]["status"], "not_provided")
        for row in result["items"]:
            self.assertEqual(row["releaseMembership"], "unknown")
            self.assertIsNone(row["notificationCatalogMember"])
            self.assertEqual(row["candidateState"], "not_provided")
            self.assertIsNone(row["previewUrl"])
        review = self.rows(result)["review:" + self.folder]
        self.assertEqual(review["checkedInputState"]["article"], "matched")
        self.assertEqual(review["contentComparison"]["state"], "unknown")

    def test_v2_hub_change_is_separate_from_protected_article_drift(self):
        self.intent()
        self.registration["review"]["subtitle"] = "A different hub subtitle"
        self.write_json("publication/reviews/" + self.folder + ".json", self.registration)
        state = self.rows(self.build())["review:" + self.folder]["checkedInputState"]
        self.assertEqual((state["article"], state["registration"], state["basis"]),
                         ("matched", "changed", "persistent_request_v2"))
        self.registration["review"]["title"] = "Protected changed title"
        self.write_json("publication/reviews/" + self.folder + ".json", self.registration)
        self.assertEqual(self.rows(self.build())["review:" + self.folder]["checkedInputState"]["article"], "changed")

    def test_v1_registration_change_is_uncertain_and_never_upgraded(self):
        request = self.intent(version=1)
        path = self.root / "publication/requests" / (self.folder + ".json")
        before = path.read_bytes()
        self.registration["review"]["summary"] = "Only hub metadata changed"
        self.write_json("publication/reviews/" + self.folder + ".json", self.registration)
        state = self.rows(self.build())["review:" + self.folder]["checkedInputState"]
        self.assertEqual((state["article"], state["registration"]), ("unknown", "changed"))
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(json.loads(before), request)

    def test_source_drift_is_checked_but_does_not_prove_deployment_or_content_match(self):
        self.intent()
        (self.root / self.folder / "dist/index.html").write_text("Changed manuscript")
        row = self.rows(self.build())["review:" + self.folder]
        self.assertEqual(row["checkedInputState"]["article"], "changed")
        self.assertEqual(row["releaseMembership"], "present")
        self.assertEqual(row["contentComparison"]["state"], "unknown")

    def test_current_pdf_drift_differs_without_inventing_historic_review_hash(self):
        document = self.documents[0]
        (self.root / "archive" / document["file"]).write_bytes(b"%PDF-1.7\nnew current bytes\n")
        row = self.rows(self.build())["archive:" + document["id"]]
        self.assertEqual(row["contentComparison"], {"state": "differs",
                         "basis": "current_source_pdf_vs_deployed_artifact", "coveredPaths": ["archive/" + document["file"]]})
        self.assertIn("historical_review_digest_not_recorded", row["warnings"])
        # Link metadata describes sealed deployed bytes, not the changed source.
        self.assertNotEqual(row["publicLinks"][0]["sha256"], row["versionEvidence"]["sourcePdfSha256"])

    def test_declaration_after_covers_only_bound_content_paths_not_raw_html(self):
        self.intent()
        href = "reviews/" + self.folder + "/index.html"
        metadata = self.snapshot["files"][href]
        self.write_json("publication_changes/review.json", {"version": 1, "reason": "Reviewed exact output",
                        "files": {href: {"before": "b" * 64, "after": metadata["content_sha256"]}}})
        row = self.rows(self.build())["review:" + self.folder]
        self.assertEqual(row["contentComparison"], {"state": "matches", "basis": "reviewed_declaration_after", "coveredPaths": [href]})
        self.assertNotEqual(metadata["sha256"], metadata["content_sha256"])
        self.assertEqual(row["publicLinks"][0]["sha256"], metadata["sha256"])

    def test_stale_declaration_is_not_bound_to_changed_or_unrecorded_current_inputs(self):
        href = "reviews/" + self.folder + "/index.html"
        self.write_json("publication_changes/review.json", {"version": 1, "reason": "Past reviewed output",
                        "files": {href: {"before": "b" * 64, "after": self.snapshot["files"][href]["content_sha256"]}}})
        row = self.rows(self.build())["review:" + self.folder]
        self.assertEqual(row["contentComparison"]["state"], "unknown")
        self.assertEqual(row["contentComparison"]["basis"], "reviewed_output_not_bound_to_current_inputs")
        self.intent()
        (self.root / self.folder / "dist/index.html").write_text("New source after the old declaration")
        row = self.rows(self.build())["review:" + self.folder]
        self.assertEqual(row["checkedInputState"]["article"], "changed")
        self.assertEqual(row["contentComparison"]["state"], "unknown")

    def test_catalog_only_and_missing_source_retain_separate_reconciliation_rows(self):
        self.make_baseline(orphan=True)
        removed = self.documents[0]
        (self.root / "archive/entries" / (removed["id"] + ".json")).unlink()
        result = self.build()
        self.assertEqual(result["totals"]["registered"], 3)
        self.assertEqual(result["totals"]["reconciled"], 2)
        rows = self.rows(result)
        self.assertEqual(rows["archive:" + removed["id"]]["registrationState"], "baseline_only_source_missing")
        orphan = rows["catalog_only:2026-11-04_catalog-orphan"]
        self.assertEqual(orphan["releaseMembership"], "present")
        self.assertEqual(orphan["contentComparison"]["state"], "unknown")
        self.assertIsNone(orphan["category"])

    def test_complete_baseline_alone_allows_absent(self):
        document = self.add_document("2026-11-05-new-unnotified", series="article")
        row = self.rows(self.build())["archive:" + document["id"]]
        self.assertEqual(row["releaseMembership"], "absent")
        self.assertEqual(row["contentComparison"]["state"], "unknown")

    def test_course_units_latest_alias_and_supplement_are_not_extra_rows(self):
        anchor = self.add_document("2026-11-04-course-l001", payload=b"%PDF-1.7\nunit one\n")
        latest = self.add_document("2026-11-05-course-l002", payload=b"%PDF-1.7\nunit two\n")
        supplement = self.add_document("2026-11-06-supplement", payload=b"%PDF-1.7\nsupplement\n")
        root = self.root / "2026-11-04_course/dist"
        root.mkdir(parents=True)
        units = []
        for number, document in (("L001", anchor), ("L002", latest)):
            payload = (self.root / "archive" / document["file"]).read_bytes()
            filename = document["id"] + ".pdf"
            (root / filename).write_bytes(payload)
            units.append({"id": number, "archive_id": document["id"], "pdf": filename,
                          "title": "Course unit", "title_en": "Course unit", "public_pages": 1,
                          "sha256": hashlib.sha256(payload).hexdigest()})
        (root / "notes.pdf").write_bytes((self.root / "archive" / latest["file"]).read_bytes())
        self.write_json("2026-11-04_course/dist/unit-registry.json", {
            "format": "ai-tech-review-course-registry", "series_id": "explicit-course", "title": "Explicit course",
            "title_en": "Explicit course", "summary": "Course scope", "summary_en": "Course scope", "latest_unit": "L002", "units": units})
        child = root / "supplements/example/supplement.pdf"
        child.parent.mkdir(parents=True)
        child.write_bytes((self.root / "archive" / supplement["file"]).read_bytes())
        self.write_json("2026-11-04_course/dist/supplement-registry.json", {"version": 1, "parent_id": anchor["id"],
                        "supplements": [{"document_id": supplement["id"], "href": "supplements/example/",
                                         "pdf": "supplements/example/supplement.pdf", "summary": "Separate supplement",
                                         "summary_en": "Separate supplement", "sha256": hashlib.sha256(child.read_bytes()).hexdigest(),
                                         "related_chapters": []}]})
        spec = {anchor["id"]: {"source": "2026-11-04_course/dist", "href": "lectures/example/",
                              "unit_registry": "unit-registry.json", "supplement_registry": "supplement-registry.json",
                              "files": ("supplements/example/supplement.pdf",)}}
        with patch.object(inventory, "LECTURE_BUNDLES", spec):
            result = self.build(baseline=False)
        self.assertEqual(result["totals"]["registered"], 7)
        rows = self.rows(result)
        self.assertEqual(rows["archive:" + anchor["id"]]["series"]["id"], "explicit-course")
        latest_link = next(link for link in rows["archive:" + latest["id"]]["publicLinks"] if link["role"] == "latest_unit_pdf")
        self.assertEqual(latest_link["sha256"], units[1]["sha256"])
        self.assertNotEqual(latest_link["sha256"], units[0]["sha256"])
        self.assertEqual(rows["archive:" + supplement["id"]]["relatedDocumentIds"], [anchor["id"]])
        self.make_baseline()
        alias = "lectures/example/notes.pdf"
        self.snapshot["files"][alias] = {"sha256": units[0]["sha256"], "content_sha256": units[0]["sha256"],
                                         "bytes": len((self.root / "archive" / anchor["file"]).read_bytes())}
        self.snapshot["archive"][anchor["id"]]["references"].append(alias)
        self.write_baseline()
        with patch.object(inventory, "LECTURE_BUNDLES", spec):
            deployed = self.rows(self.build())["archive:" + latest["id"]]
        self.assertIn("public_alias_differs_from_current_unit", deployed["warnings"])
        self.assertFalse(any(link["role"] == "latest_unit_pdf" for link in deployed["publicLinks"]))

    def test_required_manifest_entries_and_external_never_initialize_empty(self):
        for name in ("archive/manifest.json", "archive/external-resources.json"):
            path = self.root / name
            saved = path.read_bytes()
            path.unlink()
            self.error("required_input_missing")
            path.write_bytes(saved)
        directory = self.root / "archive/entries"
        directory.rename(self.root / "entries-away")
        self.error("required_input_missing")

    def test_blank_manifest_duplicate_key_and_duplicate_ids_fail_closed(self):
        path = self.root / "archive/manifest.json"
        before = path.read_bytes()
        path.write_text("")
        self.error("invalid_json")
        path.write_text('{"version":2,"version":2,"entries":"entries"}')
        self.error("duplicate_json_key")
        path.write_bytes(before)
        self.write_json("archive/entries/duplicate.json", self.documents[0])
        self.error("invalid_input")

    def test_invalid_native_registration_and_unregistered_pdf_discovery(self):
        stray = self.root / "archive/files/not-registered.pdf"
        stray.write_bytes(b"%PDF-1.7\nnot a registration")
        self.assertEqual(self.build()["totals"]["registered"], 4)
        malformed = copy.deepcopy(self.documents[0])
        malformed["file"] = "../private.pdf"
        self.write_json("archive/entries/" + malformed["id"] + ".json", malformed)
        self.error("invalid_input")

    def test_source_and_baseline_symlinks_rejected_without_following(self):
        path = self.root / "archive/manifest.json"
        saved = path.read_bytes()
        outside = Path(self.temp.name) / "outside.json"
        outside.write_bytes(saved)
        path.unlink()
        path.symlink_to(outside)
        self.error("input_symlink")
        path.unlink()
        path.write_bytes(saved)
        bundle = self.baseline / "reader-publications.json"
        saved = bundle.read_bytes()
        bundle.unlink()
        outside.write_bytes(saved)
        bundle.symlink_to(outside)
        self.error("input_symlink")

    def test_private_named_manuscript_input_is_rejected_before_hash_read(self):
        path = self.root / self.folder / "dist/.env"
        path.write_text("secret-value-never-print")
        self.error("private_source_input")

    def test_skip_ci_head_difference_is_not_absent_or_pending(self):
        with patch.object(inventory, "_source_revision", return_value=("b" * 40, "match")):
            result = self.build()
        self.assertNotEqual(result["sourceRevision"], result["baseline"]["releaseRevision"])
        self.assertTrue(all(row["releaseMembership"] == "present" for row in result["items"]))
        self.assertTrue(all(row["candidateState"] == "not_provided" for row in result["items"]))

    def test_model_field_drift_is_schema_error_without_importing_publisher(self):
        path = self.root / "scripts/publish_public_site.py"
        path.write_text(path.read_text(encoding="utf-8").replace("    folder: str", "    changed_folder: str"), encoding="utf-8")
        self.error("review_model_schema_changed")

    def test_supplied_incoherent_or_incomplete_baseline_is_not_unknown(self):
        path = self.baseline / "reader-updates.json"
        path.write_text('{"version":1,"pages":{},"articles":[],"extra":true}')
        self.error("invalid_baseline")
        self.write_baseline()
        self.catalog["revision"] = "b" * 40
        (self.baseline / "reader-publications.json").write_text(json.dumps(self.catalog))
        self.error("invalid_baseline")
        self.write_baseline()
        (self.baseline / "release.json").unlink()
        self.error("required_input_missing")

    def test_snapshot_raw_hash_and_size_must_bind_to_sealed_artifact_files(self):
        href = "reviews/" + self.folder + "/index.html"
        for field, value in (("sha256", "f" * 64), ("bytes", 999)):
            with self.subTest(field=field):
                self.write_baseline()
                self.release["artifact_files"][href][field] = value
                (self.baseline / "release.json").write_text(json.dumps(self.release))
                self.error("invalid_baseline")
        self.write_baseline()
        del self.release["artifact_files"][href]
        (self.baseline / "release.json").write_text(json.dumps(self.release))
        self.error("invalid_baseline")

    def test_catalog_snapshot_membership_and_unsafe_sealed_paths_are_rejected(self):
        self.snapshot["publications"] = {}
        self.write_baseline()
        self.error("invalid_baseline")
        self.make_baseline()
        path = "reviews/" + self.folder + "/index.html"
        self.snapshot["reviews"][self.folder]["href"] = "reviews/../private/index.html"
        self.write_baseline()
        self.error("invalid_baseline")

    def test_external_queries_credentials_and_private_downloads_are_rejected(self):
        for url in ("https://user:password@example.org/book", "https://example.org/book?token=secret",
                    "javascript:alert(1)", "https://example.org/book.pdf", "https://localhost/book"):
            with self.subTest(url=url):
                resource = {**self.external, "book_url": url}
                self.write_json("archive/external-resources.json", {"version": 1, "resources": [resource]})
                self.error("invalid_input")

    def test_inputs_changing_during_read_and_new_ledger_entries_fail_closed(self):
        original = inventory.document_version
        path = self.root / "archive/entries" / (self.documents[0]["id"] + ".json")

        def mutate(*args):
            token = original(*args)
            path.write_bytes(path.read_bytes() + b" ")
            return token

        with patch.object(inventory, "document_version", side_effect=mutate):
            self.error("input_changed")
        original = inventory._source_revision

        def new_entry(*args):
            self.write_json("archive/entries/new.json", self.documents[0])
            return original(*args)

        with patch.object(inventory, "_source_revision", side_effect=new_entry):
            self.error("input_changed")

    def test_json_file_total_row_and_response_limits_never_truncate(self):
        with patch.object(inventory, "MAX_JSON_FILE_BYTES", 10):
            self.error("json_file_limit")
        with patch.object(inventory, "MAX_JSON_TOTAL_BYTES", 10):
            self.error("json_total_limit")
        with patch.object(inventory, "MAX_ROWS", 3):
            self.error("row_limit")
        with patch.object(inventory, "MAX_RESPONSE_BYTES", 100):
            self.error("response_limit")

    def test_stable_tokens_ignore_query_time_and_keep_raw_registration_evidence(self):
        with patch.object(inventory, "datetime") as clock:
            clock.now.side_effect = [datetime(2026, 11, 17, tzinfo=timezone.utc),
                                     datetime(2026, 11, 18, tzinfo=timezone.utc)]
            first, second = self.build(), self.build()
        self.assertNotEqual(first["checkedAt"], second["checkedAt"])
        self.assertEqual(first["registrationSnapshotToken"], second["registrationSnapshotToken"])
        self.assertEqual(first["snapshotToken"], second["snapshotToken"])
        path = self.root / "publication/reviews" / (self.folder + ".json")
        path.write_bytes(path.read_bytes() + b" ")
        changed = self.build()
        self.assertNotEqual(first["snapshotToken"], changed["snapshotToken"])

    def test_ignored_baseline_inside_source_is_not_compared_to_the_source_commit(self):
        tracker = inventory._Inputs(self.root)
        source_path = self.root / "archive/manifest.json"
        info = tracker.file(source_path)
        local_bundle = self.root / "output/baseline"
        local_bundle.mkdir(parents=True)
        evidence = local_bundle / "snapshot.json"
        evidence.write_text('{"synthetic":"baseline evidence"}')
        tracker.directory(local_bundle, boundary=local_bundle)
        tracker.json(evidence, boundary=local_bundle)

        def git_read(arguments, **kwargs):
            if arguments[1:] == ["rev-parse", "HEAD"]:
                return SimpleNamespace(stdout=("a" * 40 + "\n").encode())
            if arguments[1:] == ["rev-parse", "--show-toplevel"]:
                return SimpleNamespace(stdout=(str(self.root) + "\n").encode())
            return SimpleNamespace(stdout=("100644 blob " + info["git"] + "\tarchive/manifest.json\0").encode())

        with patch.object(inventory.subprocess, "run", side_effect=git_read):
            self.assertEqual(inventory._source_revision(self.root, tracker), ("a" * 40, "match"))

    def test_tracked_source_deletion_is_not_a_matching_subset_of_commit_inputs(self):
        tracker = inventory._Inputs(self.root)
        path = self.root / self.folder / "dist"
        tracker.tree(path)
        keep = path / "index.html"
        info = tracker.files[keep]

        def git_read(arguments, **kwargs):
            if arguments[1:] == ["rev-parse", "HEAD"]:
                return SimpleNamespace(stdout=("a" * 40 + "\n").encode())
            if arguments[1:] == ["rev-parse", "--show-toplevel"]:
                return SimpleNamespace(stdout=(str(self.root) + "\n").encode())
            blob = "100644 blob " + info["git"] + "\t" + self.folder + "/dist/index.html\0"
            blob += "100644 blob " + "b" * 40 + "\t" + self.folder + "/dist/removed.svg\0"
            return SimpleNamespace(stdout=blob.encode())

        with patch.object(inventory.subprocess, "run", side_effect=git_read):
            self.assertEqual(inventory._source_revision(self.root, tracker), ("a" * 40, "different"))

    def test_allowlisted_projection_no_private_inputs_no_network_no_writes(self):
        (self.root / "private").mkdir()
        secret = self.root / "private/notes.json"
        secret.write_text('{"private":"not public"}')
        before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        with patch("urllib.request.urlopen", side_effect=AssertionError("network is forbidden")), \
                patch("socket.socket", side_effect=AssertionError("network is forbidden")):
            result = self.build()
        encoded = json.dumps(result, ensure_ascii=False)
        for private in (str(self.root), "Private manuscript body", "Translated body", "not public", "responsible_editor"):
            self.assertNotIn(private, encoded)
        self.assertEqual(before, {p.relative_to(self.root).as_posix(): p.read_bytes()
                                 for p in self.root.rglob("*") if p.is_file()})
        self.assertTrue(all(link["httpsVerifiedAt"] is None for row in result["items"] for link in row["publicLinks"]))
        self.assertIsNone(result["sourceRevision"])
        self.assertEqual(result["sourceInputState"], "unknown")

    def test_untrusted_title_remains_plain_text_and_private_path_is_not_projected(self):
        self.registration["review"]["title"] = '<img src=x onerror="alert(1)">'
        self.write_json("publication/reviews/" + self.folder + ".json", self.registration)
        self.assertEqual(self.rows(self.build())["review:" + self.folder]["title"], self.registration["review"]["title"])
        self.registration["review"]["title"] = "/Users/private-person/private-note"
        self.write_json("publication/reviews/" + self.folder + ".json", self.registration)
        self.error("invalid_input")


if __name__ == "__main__":
    unittest.main()
