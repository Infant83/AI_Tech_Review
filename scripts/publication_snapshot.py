"""Read-only publication snapshots and structural regression checks.

Hashes describe bytes, not visual correctness. Content changes require review;
passing this check does not establish mobile layout, rendering or API health.
Snapshots belong outside the public site directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from .reader_engagement_publish import content_digest
except ImportError:
    from reader_engagement_publish import content_digest

SCOPE = "/AI_Tech_Review/"
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9:_-]{0,179}\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
CONFIG = re.compile(r'<script\b[^>]*\bid=[\"\']reader-engagement-config[\"\'][^>]*>(.*?)</script\s*>', re.I | re.S)
GROUPS = ("reviews", "archive", "publications", "external")


class SnapshotError(ValueError):
    pass


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise SnapshotError("Duplicate JSON key: " + key)
        value[key] = item
    return value


def read_json(path: Path):
    if path.is_symlink():
        raise SnapshotError("Symlinked JSON input: " + path.name)
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SnapshotError("Cannot read valid JSON: " + path.name) from error


def relative_path(value: str) -> str:
    if (not isinstance(value, str) or not value or unquote(value) != value
            or any(ord(character) < 32 for character in value)):
        raise SnapshotError("Invalid public relative path")
    parts = urlsplit(value)
    if (parts.scheme or parts.netloc or parts.query or parts.fragment or value.startswith("/")
            or "\\" in value or "//" in value
            or any(part in {".", ".."} for part in value.split("/"))):
        raise SnapshotError("Invalid public relative path: " + value)
    return value


def scoped_path(value: str) -> str:
    if not isinstance(value, str) or not value.startswith(SCOPE):
        raise SnapshotError("Invalid public scoped path")
    relative_path(value[len(SCOPE):])
    return value


def rows(value, label):
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise SnapshotError("Expected a record list: " + label)
    return value


def add_record(group, identifier, record):
    if not isinstance(identifier, str) or not ID.fullmatch(identifier):
        raise SnapshotError("Invalid publication identifier")
    if identifier in group:
        raise SnapshotError("Duplicate publication identifier: " + identifier)
    group[identifier] = record


def capture_site(site: Path) -> dict:
    """Capture registered identities, declared references and public file hashes."""
    site = Path(site)
    if site.is_symlink() or not site.is_dir():
        raise SnapshotError("Site must be a regular directory")
    result = {"version": 1, **{name: {} for name in GROUPS}, "files": {},
              "missing_files": [], "declared_hash_mismatches": []}
    references, expected, review_paths, archive_paths = set(), {}, set(), set()

    def reference(href, checksum=None):
        href = relative_path(href)
        name = href + "index.html" if href.endswith("/") else href
        references.add(name)
        if checksum is not None:
            if not isinstance(checksum, str) or not SHA.fullmatch(checksum):
                raise SnapshotError("Invalid declared hash: " + name)
            if name in expected and expected[name] != checksum:
                raise SnapshotError("Conflicting declared hashes: " + name)
            expected[name] = checksum
        return name

    manifest = read_json(site / "manifest.json")
    for review in rows(manifest, "reviews"):
        href = relative_path(review.get("href"))
        metric = review.get("metric_path")
        if metric is not None:
            scoped_path(metric)
        translations, owned = {}, {reference(href)}
        for variant in [review, *rows(review.get("translations", []), "translations")]:
            variant_href = relative_path(variant.get("href"))
            if variant_href in review_paths:
                raise SnapshotError("Duplicate review or translation path: " + variant_href)
            review_paths.add(variant_href)
            owned.add(reference(variant_href))
            assets = variant.get("assets", [])
            if not isinstance(assets, list):
                raise SnapshotError("Invalid review asset list")
            for asset in assets:
                owned.add(reference((Path(variant_href).parent / relative_path(asset)).as_posix()))
            if variant is not review:
                language = variant.get("language")
                if not isinstance(language, str) or not re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z0-9]+)*", language):
                    raise SnapshotError("Invalid translation language")
                if language in translations:
                    raise SnapshotError("Duplicate translation language")
                variant_metric = variant.get("metric_path")
                if variant_metric is not None:
                    scoped_path(variant_metric)
                translations[language] = {"href": variant_href, "metric_path": variant_metric}
        if review.get("thumbnail"):
            owned.add(reference(review["thumbnail"]))
        add_record(result["reviews"], review.get("folder"),
                   {"href": href, "metric_path": metric, "translations": translations,
                    "date": review.get("date"), "references": sorted(owned)})

    archive_path = site / "archive-manifest.json"
    archive = read_json(archive_path) if archive_path.exists() else {}
    if not isinstance(archive, dict):
        raise SnapshotError("Invalid archive registry")
    for document in rows(archive.get("documents", []), "archive"):
        href = relative_path(document.get("href"))
        if href in archive_paths:
            raise SnapshotError("Duplicate archived document path: " + href)
        archive_paths.add(href)
        study = document.get("study_href")
        owned = {reference(href, document.get("sha256"))}
        for edition in rows(document.get("editions", []), "PDF editions"):
            if edition.get("href") != f'archive/editions/{document["id"]}/{edition.get("sha256")}.pdf':
                raise SnapshotError("Invalid PDF edition path")
            owned.add(reference(edition["href"], edition.get("sha256")))
        if study:
            owned.add(reference(study))
            base = Path(study) if study.endswith("/") else Path(study).parent
            assets = document.get("study_assets", {})
            if not isinstance(assets, dict):
                raise SnapshotError("Invalid study asset map")
            for asset, checksum in assets.items():
                owned.add(reference((base / relative_path(asset)).as_posix(), checksum))
        add_record(result["archive"], document.get("id"),
                   {"href": href, "study_href": study, "date": document.get("date"),
                    "references": sorted(owned)})
    for resource in rows(archive.get("external_resources", []), "external"):
        url = resource.get("book_url")
        if not isinstance(url, str) or urlsplit(url).scheme not in {"https", "http"}:
            raise SnapshotError("Invalid external resource URL")
        add_record(result["external"], resource.get("id"), {"book_url": url})

    catalog_path = site / "reader-publications.json"
    if catalog_path.exists():
        catalog = read_json(catalog_path)
        if not isinstance(catalog, dict):
            raise SnapshotError("Invalid publication catalog")
        paths = set()
        for article in rows(catalog.get("articles"), "publications"):
            path = scoped_path(article.get("path"))
            if path in paths:
                raise SnapshotError("Duplicate canonical publication path: " + path)
            paths.add(path)
            reference(path[len(SCOPE):])
            add_record(result["publications"], article.get("id"),
                       {"path": path, "topic": article.get("topic"), "publishedAt": article.get("publishedAt")})
    for name in ("index.html", "en/index.html", "archive/index.html", "lectures/index.html",
                 "briefings/index.html", "assets/site.css", "assets/site.js",
                 "assets/archive.css", "assets/archive.js", "assets/briefings.css", "assets/briefings.js"):
        if (site / name).exists():
            reference(name)
    try:
        from .listing_pagination import generated_paths
    except ImportError:
        from listing_pagination import generated_paths
    for name in generated_paths(site):
        if (site / name).exists():
            reference(name)
    for directory in (site / "assets", site / "lectures/reader"):
        if directory.is_symlink():
            raise SnapshotError("Symlink in shared public assets")
        if directory.exists():
            for path in directory.rglob("*"):
                if path.is_symlink():
                    raise SnapshotError("Symlink in shared public assets")
                if path.is_file():
                    reference(path.relative_to(site).as_posix())
    for name in sorted(references):
        path = site / name
        pieces = Path(name).parts
        if any((site / Path(*pieces[:end])).is_symlink() for end in range(1, len(pieces) + 1)):
            raise SnapshotError("Symlink in public reference: " + name)
        if not path.is_file():
            result["missing_files"].append(name)
            continue
        payload = path.read_bytes()
        raw_hash = hashlib.sha256(payload).hexdigest()
        info = {"sha256": raw_hash, "content_sha256": content_digest(path), "bytes": len(payload)}
        if path.suffix == ".html":
            match = CONFIG.search(payload.decode("utf-8"))
            if match:
                try:
                    article = json.loads(match[1]).get("article")
                    info["reader_identity"] = None if article is None else {
                        "id": article["id"], "path": scoped_path(article["path"]), "topic": article.get("topic")}
                except (ValueError, KeyError, TypeError, AttributeError) as error:
                    raise SnapshotError("Invalid reader identity: " + name) from error
        result["files"][name] = info
        if name in expected and expected[name] != raw_hash:
            result["declared_hash_mismatches"].append(name)
    return result


def compare_snapshots(baseline: dict, current: dict) -> dict:
    if not isinstance(baseline, dict) or baseline.get("version") != 1:
        raise SnapshotError("Unsupported baseline snapshot")
    blockers, additions = [], []
    for group in GROUPS:
        old, new = baseline.get(group), current[group]
        if not isinstance(old, dict):
            raise SnapshotError("Invalid baseline record group: " + group)
        for identifier, record in old.items():
            if not ID.fullmatch(identifier) or not isinstance(record, dict):
                raise SnapshotError("Invalid baseline record")
            if identifier not in new:
                blockers.append({"kind": "record_removed", "group": group, "id": identifier})
            elif record != new[identifier]:
                blockers.append({"kind": "identity_or_references_changed", "group": group, "id": identifier})
        additions.extend({"group": group, "id": identifier} for identifier in sorted(new.keys() - old.keys()))
    old_files = baseline.get("files")
    if not isinstance(old_files, dict):
        raise SnapshotError("Invalid baseline files")
    content_changes, instrumentation_changes = [], []
    for name, old in old_files.items():
        relative_path(name)
        if (not isinstance(old, dict) or not SHA.fullmatch(str(old.get("sha256", "")))
                or not SHA.fullmatch(str(old.get("content_sha256", "")))):
            raise SnapshotError("Invalid baseline file hashes")
        new = current["files"].get(name)
        if new is None:
            blockers.append({"kind": "reference_missing", "path": name})
        else:
            if old.get("reader_identity") != new.get("reader_identity"):
                blockers.append({"kind": "reader_identity_changed", "path": name})
            if old.get("content_sha256") != new["content_sha256"]:
                content_changes.append(name)
            elif old.get("sha256") != new["sha256"]:
                instrumentation_changes.append(name)
    for kind, key in (("missing_file", "missing_files"), ("declared_hash_mismatch", "declared_hash_mismatches")):
        blockers.extend({"kind": kind, "path": name} for name in current[key])
    return {"structural_ok": not blockers, "blockers": blockers, "additions": additions,
            "content_review_required": bool(content_changes), "content_changes": content_changes,
            "instrumentation_only_changes": instrumentation_changes,
            "limits": "Byte and identity checks do not verify rendering, mobile layout or live API health."}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("capture", "compare"))
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output and args.output.resolve().is_relative_to(args.site.resolve()):
            raise SnapshotError("Snapshot output must be outside the public site")
        current = capture_site(args.site)
        if args.action == "capture":
            if args.baseline or not args.output:
                parser.error("capture requires --output and does not accept --baseline")
            result, failed = current, bool(current["missing_files"] or current["declared_hash_mismatches"])
        else:
            if not args.baseline:
                parser.error("compare requires --baseline")
            result = compare_snapshots(read_json(args.baseline), current)
            failed = not result["structural_ok"]
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
        else:
            print(text, end="")
        return int(failed)
    except (SnapshotError, UnicodeError):
        print(json.dumps({"error": "Invalid publication input; capture or comparison was not completed."}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
