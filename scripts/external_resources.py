"""Validate public book links without exposing or copying privately held PDFs."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote

try:
    from .archive_documents import (
        ArchiveValidationError, ID_PATTERN, DATE_PATTERN, _check_text,
        _reject_symlink_components, _unique_json_object,
    )
except ImportError:
    from archive_documents import (
        ArchiveValidationError, ID_PATTERN, DATE_PATTERN, _check_text,
        _reject_symlink_components, _unique_json_object,
    )


REQUIRED_FIELDS = frozenset({
    "id", "date", "series", "title", "summary", "summary_en", "language",
    "author", "author_url", "book_url", "tags", "public_reviewed",
})
OPTIONAL_FIELDS = frozenset({"title_en"})


def validate_resources(resources: object) -> list[dict]:
    """Accept only reviewed display metadata and clean public landing-page URLs."""
    if not isinstance(resources, list):
        raise ArchiveValidationError("External resources must be a list")
    ids = set()
    for resource in resources:
        if not isinstance(resource, dict):
            raise ArchiveValidationError("Each external resource must be an object")
        if REQUIRED_FIELDS - resource.keys() or resource.keys() - REQUIRED_FIELDS - OPTIONAL_FIELDS:
            raise ArchiveValidationError("External resource has missing or unknown fields")
        if resource["public_reviewed"] is not True:
            raise ArchiveValidationError("External resource public_reviewed must be true")
        resource_id, registered = resource["id"], resource["date"]
        if not isinstance(resource_id, str) or len(resource_id) > 120 or not ID_PATTERN.fullmatch(resource_id):
            raise ArchiveValidationError("Invalid external resource id")
        if not isinstance(registered, str) or not DATE_PATTERN.fullmatch(registered):
            raise ArchiveValidationError("Invalid external registration date")
        try:
            date.fromisoformat(registered)
        except ValueError as exc:
            raise ArchiveValidationError("Invalid external registration date") from exc
        if not resource_id.startswith(registered + "-") or resource_id in ids:
            raise ArchiveValidationError("External id must be unique and start with its registration date")
        ids.add(resource_id)
        if resource["series"] != "external-book" or resource["language"] not in ("ko", "en"):
            raise ArchiveValidationError("Invalid external series or language")
        for field, limit in (("title", 240), ("title_en", 240), ("summary", 1600), ("summary_en", 1600), ("author", 240)):
            if field in resource:
                _check_text(resource[field], field, limit)
        tags = resource["tags"]
        if not isinstance(tags, list) or len(tags) > 12:
            raise ArchiveValidationError("External tags must be a list of at most 12 labels")
        for tag in tags:
            _check_text(tag, "tag", 48)
        if len(set(tags)) != len(tags):
            raise ArchiveValidationError("External tags must not contain duplicates")
        for field in ("author_url", "book_url"):
            value = resource[field]
            if not isinstance(value, str) or len(value) > 1000 or any(char.isspace() or ord(char) < 32 for char in value):
                raise ArchiveValidationError("External URLs must be clean HTTPS landing pages")
            try:
                parsed = urlsplit(value)
            except ValueError as exc:
                raise ArchiveValidationError("Invalid external HTTPS URL") from exc
            # Queries and fragments are deliberately excluded: signed download
            # URLs and email access links do not belong in a public catalog.
            if (parsed.scheme != "https" or not re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", parsed.netloc)
                    or parsed.netloc.rsplit(".", 1)[-1] in {"localhost", "local", "internal", "test", "invalid"}
                    or parsed.query or parsed.fragment or "?" in value or "#" in value
                    or "\\" in value or unquote(parsed.path).lower().endswith(".pdf")):
                raise ArchiveValidationError("External URLs must be clean HTTPS landing pages")
    return sorted(resources, key=lambda item: (item["date"], item["id"]), reverse=True)


def load_external_resources(archive_dir: Path) -> list[dict]:
    """Read only the explicit link registry; never inspect private storage."""
    source = archive_dir / "external-resources.json"
    _reject_symlink_components(source)
    if not source.exists():
        return []
    try:
        manifest = json.loads(source.read_text(encoding="utf-8"), object_pairs_hook=_unique_json_object)
    except json.JSONDecodeError as exc:
        raise ArchiveValidationError("Invalid external resource JSON") from exc
    if (not isinstance(manifest, dict) or set(manifest) != {"version", "resources"}
            or type(manifest["version"]) is not int or manifest["version"] != 1):
        raise ArchiveValidationError("Invalid external resource registry")
    return validate_resources(manifest["resources"])
