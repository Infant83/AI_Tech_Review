"""Prepare a validated static candidate without replacing the published checkout."""
from __future__ import annotations

import argparse
from contextlib import contextmanager, ExitStack
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

try:
    from . import publish_public_site as publisher
    from .publication_lock import publication_lock
    from .publication_snapshot import capture_site, compare_snapshots, read_json
    from .reader_engagement_publish import content_digest, validate_public_artifact
    from .publication_intent import pending_review_intents, review_inputs, write_review_intent
    from .publication_release import declarations, read_baseline_updates, read_metadata_file, validate_updates_payload, MAX_UPDATES_BYTES
    from .archive_documents import load_documents, document_version
except ImportError:
    import publish_public_site as publisher
    from publication_lock import publication_lock
    from publication_snapshot import capture_site, compare_snapshots, read_json
    from reader_engagement_publish import content_digest, validate_public_artifact
    from publication_intent import pending_review_intents, review_inputs, write_review_intent
    from publication_release import declarations, read_baseline_updates, read_metadata_file, validate_updates_payload, MAX_UPDATES_BYTES
    from archive_documents import load_documents, document_version


@contextmanager
def candidate_site(directory):
    previous = publisher.SITE_DIR, publisher.REVIEWS_DIR, publisher.ASSETS_DIR
    publisher.SITE_DIR = Path(directory)
    publisher.REVIEWS_DIR = publisher.SITE_DIR / "reviews"
    publisher.ASSETS_DIR = publisher.SITE_DIR / "assets"
    try:
        yield
    finally:
        publisher.SITE_DIR, publisher.REVIEWS_DIR, publisher.ASSETS_DIR = previous


def write_change_declaration(root: Path, name: str, files: dict, reason: str):
    if not files:
        return
    directory = Path(root) / "publication_changes"
    directory.mkdir(exist_ok=True)
    if directory.is_symlink():
        raise ValueError("Publication changes directory must not be a symlink")
    declaration = directory / (name + ".json")
    if declaration.is_symlink():
        raise ValueError("Publication change declaration must not be a symlink")
    descriptor, pending = tempfile.mkstemp(prefix=".changes-", dir=directory)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump({"version": 1, "reason": reason, "files": files}, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(pending, declaration)
    finally:
        Path(pending).unlink(missing_ok=True)


def reviewed_article_is_current(site: Path, baseline: dict, folder: str, changes: dict | None = None) -> bool:
    """Reuse a seeded article only when every registered content byte agrees.

    A persistent request is still replayed when the old committed site seed
    predates an artifact-only article revision. Hub metadata never makes that
    stale article an acceptable replacement for the checked publication. On
    the first CI run both seed and baseline can still be old, so the checked
    change declaration's after hashes must agree as well.
    """
    record = baseline.get("reviews", {}).get(folder)
    if not record or not record.get("references"):
        return False
    for name in record["references"]:
        path = Path(site) / name
        expected = baseline.get("files", {}).get(name, {}).get("content_sha256")
        if not expected or not path.is_file() or path.is_symlink() or content_digest(path) != expected:
            return False
    prefix = "reviews/" + folder + "/"
    for name, hashes in (changes or {}).items():
        if name.startswith(prefix):
            path = Path(site) / name
            if not path.is_file() or path.is_symlink() or content_digest(path) != hashes["after"]:
                return False
    return True


def prepare_candidate(output: Path, *, revision: str, reviews=(), documents=(), baseline_site: Path | None = None,
                      baseline_snapshot: Path | None = None, change_reason: str = "") -> dict:
    """Seed immutable historical pages, rebuild registrations and validate.

    Existing scientific articles are never regenerated unless explicitly named.
    Newly registered reviews are published from their reviewed dist directories.
    This command creates a candidate only: integration, prior-release policy and
    deployment are handled by CI after independent visual/browser checks.
    """
    if not isinstance(revision, str) or not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("revision must be a complete lowercase Git commit SHA")
    requested_output = Path(output).absolute()
    if requested_output.is_symlink():
        raise ValueError("Output must not be a symlink")
    output = requested_output.resolve()
    source_site = publisher.SITE_DIR.resolve()
    if output.is_symlink() or output.exists():
        raise ValueError("Output must be a new directory; use a fresh candidate name")
    if output.is_relative_to(source_site) or source_site.is_relative_to(output):
        raise ValueError("Candidate output must be outside the published site and its parent directories")
    if baseline_site is not None and baseline_snapshot is not None:
        raise ValueError("Choose either a baseline site or baseline snapshot")
    explicit_local = baseline_site is not None
    baseline_site = Path(baseline_site) if explicit_local else source_site
    output.parent.mkdir(parents=True, exist_ok=True)
    with publication_lock(publisher.ROOT / "archive" / ".publication.lock"):
        # Validate before copying so symlinks/private assets cannot enter staging.
        validate_public_artifact(source_site, verify_search=False, verify_reader_source=False)
        baseline = read_json(baseline_snapshot) if baseline_snapshot is not None else capture_site(baseline_site)
        if baseline_snapshot is not None:
            prior_updates = read_baseline_updates(baseline_snapshot, baseline)
            updates_source = "sealed_release_bundle"
        else:
            prior_updates = read_metadata_file(baseline_site / "reader-updates.json", MAX_UPDATES_BYTES)
            validate_updates_payload(prior_updates)
            updates_source = "explicit_local_site" if explicit_local else "local_seed_only"
        known = {review.folder for review in publisher.REVIEWS}
        selected = set(reviews) | (known - set(publisher.load_existing_manifest()))
        intents = pending_review_intents(publisher.ROOT, known, selected, set(baseline["reviews"]))
        checked_changes = declarations(publisher.ROOT / "publication_changes")
        for folder in set(intents) - selected:
            if folder in baseline["reviews"] and not any(
                    name.startswith("reviews/" + folder + "/") for name in checked_changes):
                raise ValueError("Published review request lacks reviewed after hashes; prepare again with --review " + folder)
        rebuilt_reviews = {folder for folder in intents
                           if folder in selected or not reviewed_article_is_current(source_site, baseline, folder, checked_changes)}
        selected_documents = set(documents)
        source_documents = {row["id"]: row for row in load_documents(publisher.ROOT / "archive")}
        if selected_documents - set(source_documents):
            raise ValueError("Unknown document selected for publication: " + ", ".join(sorted(selected_documents - set(source_documents))))
        document_versions = {identifier: document_version(publisher.ROOT / "archive", source_documents[identifier])
                             for identifier in selected_documents}
        output.mkdir()
        stage = output / "site"
        shutil.copytree(source_site, stage)
        # The copied checkout may predate an artifact-only publication. Feed
        # the verified prior release to the existing revision calculation,
        # before publisher.main enriches pages or computes their after hashes.
        (stage / "reader-updates.json").write_bytes(prior_updates)
        with candidate_site(stage):
            arguments = ["--preserve-existing", "--revision", revision]
            for review in sorted(rebuilt_reviews):
                arguments.extend(("--review", review))
            result = publisher.main(arguments)
        if result:
            raise ValueError("Candidate generation or validation failed; source site was preserved")
        current = capture_site(stage)
        for folder, inputs in intents.items():
            if review_inputs(publisher.ROOT, folder) != inputs:
                raise ValueError("Review inputs changed while the candidate was being built: " + folder)
            if folder not in selected and not reviewed_article_is_current(stage, current, folder, checked_changes):
                raise ValueError("Replayed review does not match its reviewed after hashes: " + folder)
        final_documents = {row["id"]: row for row in load_documents(publisher.ROOT / "archive")}
        for identifier, version in document_versions.items():
            if (identifier not in final_documents
                    or document_version(publisher.ROOT / "archive", final_documents[identifier]) != version):
                raise ValueError("Document inputs changed while the candidate was being built: " + identifier)
        comparison = compare_snapshots(baseline, current)
        report = {
            "version": 1, "revision": revision,
            "reviews": len(current["reviews"]), "archive_documents": len(current["archive"]),
            "selected_reviews": sorted(intents), "selected_documents": sorted(selected_documents), "comparison": comparison,
            "rebuilt_reviews": sorted(rebuilt_reviews),
            "baseline_updates_source": updates_source,
            "status": "candidate_only_requires_release_policy_and_browser_review",
        }
        (output / "baseline.json").write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (output / "candidate.json").write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        # Refresh the complete metadata fingerprint only after the exact inputs
        # were validated before/after the build. Legacy unchanged requests also
        # migrate here, without silently authorizing changed article fields.
        for folder, inputs in intents.items():
            write_review_intent(publisher.ROOT, folder, inputs)
        for folder in selected:
            changed = {name: {"before": baseline["files"][name]["content_sha256"],
                              "after": current["files"][name]["content_sha256"]}
                       for name in comparison["content_changes"]
                       if name.startswith("reviews/" + folder + "/")}
            if not changed and folder in baseline["reviews"]:
                reviewed_changes = {name: hashes for name, hashes in checked_changes.items()
                                    if name.startswith("reviews/" + folder + "/")}
                if reviewed_changes and reviewed_article_is_current(stage, current, folder, reviewed_changes):
                    # Preserve the prior revision's reason and complete HTML/PDF
                    # hashes when they already bind this unchanged checked output.
                    continue
                # A reviewed no-op still needs an output binding so subsequent
                # metadata-only builds can safely reuse the current article.
                for name in current["reviews"][folder]["references"]:
                    if name.endswith("/index.html") and name in baseline["files"]:
                        changed[name] = {"before": baseline["files"][name]["content_sha256"],
                                         "after": current["files"][name]["content_sha256"]}
            write_change_declaration(publisher.ROOT, folder, changed,
                change_reason or "Explicit review update prepared from checked source: " + folder)
        for identifier in selected_documents:
            record = current["archive"][identifier]
            old_record = baseline["archive"].get(identifier)
            if old_record is not None and any(record[key] != old_record[key] for key in ("href", "date")):
                raise ValueError("Document identity and original publication date must remain unchanged: " + identifier)
            # Only this registered PDF and registered PDF copies can be
            # acknowledged here. HTML or unrelated shared changes still fail
            # the separate release guard and need their own explicit review.
            owned_pdfs = {name for name in record["references"] if name.endswith(".pdf")}
            changed = {name: {"before": baseline["files"][name]["content_sha256"],
                              "after": current["files"][name]["content_sha256"]}
                       for name in comparison["content_changes"] if name in owned_pdfs}
            write_change_declaration(publisher.ROOT, "document-" + identifier, changed,
                change_reason or "Explicit registered PDF update prepared from checked source: " + identifier)
        (output / ".publication-candidate.json").write_text(json.dumps({
            "version": 1, "kind": "publication-candidate", "revision": revision,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "status": "verified-local", "site": "site",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New candidate directory, outside site/")
    parser.add_argument("--revision", help="Exact source commit; defaults to current Git HEAD")
    parser.add_argument("--review", action="append", default=[], help="Explicitly republish an existing review; repeatable")
    parser.add_argument("--document", action="append", default=[], help="Acknowledge an explicitly reviewed registered PDF update; repeatable")
    parser.add_argument("--baseline-site", type=Path, help="Previous approved release's site directory")
    parser.add_argument("--baseline-snapshot", type=Path, help="Snapshot of the actual previously approved artifact")
    parser.add_argument("--change-reason", default="", help="Reason recorded for explicit review content changes")
    args = parser.parse_args(argv)
    revision = args.revision or subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=publisher.ROOT, text=True).strip()
    try:
        with ExitStack() as cleanup:
            if args.baseline_site is None and args.baseline_snapshot is None:
                try:
                    from .publication_release import live_baseline
                except ImportError:
                    from publication_release import live_baseline
                temporary = Path(cleanup.enter_context(tempfile.TemporaryDirectory(prefix="publication-baseline-")))
                source = live_baseline(publisher.ROOT, temporary / "release")
                if source["source"] == "verified_pre_snapshot_bootstrap":
                    args.baseline_site = temporary / "release/site"
                else:
                    args.baseline_snapshot = temporary / "release/snapshot.json"
            report = prepare_candidate(args.output, revision=revision, reviews=args.review, documents=args.document, baseline_site=args.baseline_site,
                                       baseline_snapshot=args.baseline_snapshot, change_reason=args.change_reason)
    except (ValueError, OSError, RuntimeError, TimeoutError) as error:
        parser.exit(1, f"Publication preparation failed: {error}\n")
    print(json.dumps({key: report[key] for key in ("revision", "reviews", "archive_documents", "status")}, ensure_ascii=False))
    print(f"Candidate: {args.output / 'site'}")
    print(f"Review report: {args.output / 'report.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
