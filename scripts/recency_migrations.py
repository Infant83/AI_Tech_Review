"""Preserve dates for reviewed display-only article revisions during the build.

Raw page and release hashes remain exact. Only the reviewed complete output
assets and publication identity can alias an earlier logical editorial revision.
"""
from __future__ import annotations

from datetime import date, datetime
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


SCOPE = "/AI_Tech_Review/"
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9:_-]{0,179}\Z")
SHA40 = re.compile(r"[a-f0-9]{40}\Z")
SHA64 = re.compile(r"[a-f0-9]{64}\Z")
DAY = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
STAMP = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")
IDENTITY_FIELDS = ("id", "path", "paths", "title", "publishedAt")
ARTICLE_FIELDS = frozenset((*IDENTITY_FIELDS, "before_revision", "after_revision", "updatedAt", "change"))
RECORD_FIELDS = frozenset((*IDENTITY_FIELDS, "revision", "updatedAt", "change"))


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate display revision JSON key: " + key)
        result[key] = value
    return result


def _scoped_path(value: str) -> bool:
    if not isinstance(value, str) or not value.startswith(SCOPE):
        return False
    relative = value[len(SCOPE):]
    if not relative:
        return True
    parts = urlsplit(relative)
    return not (
        parts.scheme or parts.netloc or parts.query or parts.fragment
        or relative.startswith("/") or "\\" in relative or "//" in relative
        or any(part in {".", ".."} for part in relative.split("/"))
        or not re.fullmatch(r"[A-Za-z0-9_./-]+", relative)
        or relative == "index.html" or relative.endswith("/index.html")
    )


def _validate_common(record: dict) -> None:
    if (not isinstance(record.get("id"), str) or not ID.fullmatch(record["id"])
            or not isinstance(record.get("title"), str) or not record["title"].strip()
            or not _scoped_path(record.get("path"))):
        raise ValueError("Invalid display revision identity")
    paths = record.get("paths")
    if (not isinstance(paths, list) or not paths
            or any(not _scoped_path(path) for path in paths)
            or paths != sorted(set(paths)) or record["path"] not in paths):
        raise ValueError("Display revision paths must be sorted, unique and include its main path")
    published = record.get("publishedAt")
    updated = record.get("updatedAt")
    if not isinstance(published, str) or not DAY.fullmatch(published):
        raise ValueError("Invalid display revision publication date")
    try:
        if date.fromisoformat(published).isoformat() != published:
            raise ValueError("Invalid display revision publication date")
    except ValueError as error:
        raise ValueError("Invalid display revision publication date") from error
    if not isinstance(updated, str) or not STAMP.fullmatch(updated):
        raise ValueError("Invalid display revision update timestamp")
    try:
        datetime.fromisoformat(updated.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Invalid display revision update timestamp") from error
    if not isinstance(record.get("change"), str) or record["change"] not in {"new", "updated"}:
        raise ValueError("Invalid display revision change kind")


def _validate_article(record: dict) -> None:
    if not isinstance(record, dict) or set(record) != ARTICLE_FIELDS:
        raise ValueError("Invalid display revision article fields")
    _validate_common(record)
    if any(not isinstance(record[key], str) or not SHA64.fullmatch(record[key])
           for key in ("before_revision", "after_revision")):
        raise ValueError("Display revision requires exact before/after article hashes")


def load_recency_migrations(root: Path) -> dict:
    """Load validated build-only inheritance records, indexed by article ID."""
    root = Path(root)
    publication = root / "publication"
    directory = publication / "display-revisions"
    for path in (root, publication, directory):
        if path.is_symlink():
            raise ValueError("Display revision inputs must not be symlinks")
        if path.exists() and not path.is_dir():
            raise ValueError("Display revision input directory must be a regular directory")
    if not directory.exists():
        return {}
    result, owned_paths = {}, set()
    for path in sorted(directory.iterdir()):
        if path.is_symlink():
            raise ValueError("Display revision inputs must not be symlinks")
        if path.suffix != ".json":
            continue
        if not path.is_file():
            raise ValueError("Display revision JSON must be a regular file")
        try:
            document = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ValueError("Cannot read valid display revision JSON: " + path.name) from error
        if (not isinstance(document, dict)
                or set(document) != {"version", "reason", "baseline", "articles"}
                or type(document["version"]) is not int or document["version"] != 1
                or not isinstance(document["reason"], str) or not document["reason"].strip()
                or not isinstance(document["articles"], list)):
            raise ValueError("Invalid display revision document: " + path.name)
        baseline = document["baseline"]
        if (not isinstance(baseline, dict) or set(baseline) != {"revision", "updates_sha256"}
                or not isinstance(baseline["revision"], str) or not SHA40.fullmatch(baseline["revision"])
                or not isinstance(baseline["updates_sha256"], str)
                or not SHA64.fullmatch(baseline["updates_sha256"])):
            raise ValueError("Invalid display revision baseline: " + path.name)
        for article in document["articles"]:
            _validate_article(article)
            if article["id"] in result:
                raise ValueError("Duplicate display revision article ID: " + article["id"])
            if owned_paths.intersection(article["paths"]):
                raise ValueError("Duplicate article path in display revisions")
            result[article["id"]] = article
            owned_paths.update(article["paths"])
    return result


def preserve_display_recency(record: dict, migrations: dict) -> dict:
    """Keep the editorial revision and dates of an exact display-only edition.

    The incoming revision is the actual complete asset digest. Its reviewed
    after hash can alias the prior editorial revision, preserving read status.
    Equal before/after hashes restore metadata for an unchanged complete edition
    when its seeded date was stale. Page and release hashes remain exact.
    """
    if not isinstance(record, dict) or set(record) != RECORD_FIELDS:
        raise ValueError("Invalid current article update record")
    _validate_common(record)
    if not isinstance(record["revision"], str) or not SHA64.fullmatch(record["revision"]):
        raise ValueError("Current article requires an exact revision hash")
    if not isinstance(migrations, dict):
        raise ValueError("Display revision migrations must be an article map")
    migration = migrations.get(record["id"])
    result = dict(record)
    if migration is None:
        return result
    _validate_article(migration)
    if (record["revision"] == migration["after_revision"]
            and all(record[key] == migration[key] for key in IDENTITY_FIELDS)):
        result.update(revision=migration["before_revision"],
                      updatedAt=migration["updatedAt"], change=migration["change"])
    return result
