"""Validate the explicit public PDF registry and import reviewed PDF documents.

Only files named in manifest.json are eligible for publication. This module has
no dependency on the site publisher, so the publisher can safely import it.
"""

from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARCHIVE_DIR = ROOT / "archive"
SERIES = frozenset({"daily-quantum", "weekly-review", "article", "lecture-notes"})
LANGUAGES = frozenset({"ko", "en"})
REQUIRED_FIELDS = frozenset(
    {"id", "date", "series", "title", "summary", "language", "file", "tags", "public_reviewed"}
)
OPTIONAL_FIELDS = frozenset({"title_en", "summary_en", "source_title"})
ID_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\Z")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}\Z")
EMAIL_PATTERN = re.compile(r"[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
URL_PATTERN = re.compile(r"(?:[a-z][a-z0-9+.-]*://|mailto:|www\.)", re.I)
LOCAL_PATH_PATTERN = re.compile(
    r"(?:/(?:Users|home|private|tmp|var|Volumes)/|[A-Z]:[\\/]|\\\\[^\\\s]+\\|(?<!\w)~/)", re.I
)


class ArchiveValidationError(ValueError):
    """The registry or input is not safe to publish."""


def _fail(message: str) -> None:
    raise ArchiveValidationError(message)


def _reject_symlink_components(path: Path) -> None:
    """Reject linked files and directories, retaining macOS system aliases.

    macOS exposes its normal temporary directory through /var -> /private/var.
    Those three OS-owned aliases are accepted; user-created links below them
    are checked just as they are under /Users.
    """
    absolute = path.absolute()
    system_aliases = {"/var": "/private/var", "/tmp": "/private/tmp", "/etc": "/private/etc"}
    for component in reversed((absolute, *absolute.parents)):
        if component.is_symlink():
            if (
                sys.platform == "darwin"
                and str(component) in system_aliases
                and str(component.resolve()) == system_aliases[str(component)]
            ):
                continue
            _fail(f"Symlinks are not allowed in archive/input paths: {component}")


def _check_directory(path: Path, *, allow_missing: bool = False) -> None:
    _reject_symlink_components(path)
    if not path.exists():
        if allow_missing:
            return
        _fail(f"Directory does not exist: {path}")
    if not path.is_dir():
        _fail(f"Expected a directory: {path}")


def _check_pdf(path: Path) -> None:
    _reject_symlink_components(path)
    try:
        mode = path.stat().st_mode
    except OSError as exc:
        _fail(f"PDF is unavailable: {path}: {exc.strerror}")
    if not stat.S_ISREG(mode):
        _fail(f"PDF must be a regular file: {path}")
    try:
        with path.open("rb") as handle:
            if handle.read(5) != b"%PDF-":
                _fail(f"File does not have a PDF header: {path}")
    except OSError as exc:
        _fail(f"Could not read PDF: {path}: {exc.strerror}")


def _check_text(value: Any, field: str, limit: int) -> None:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        _fail(f"{field} must be nonempty text of at most {limit} characters")
    if value != value.strip() or any(ord(char) < 32 for char in value):
        _fail(f"{field} must be a single line without surrounding whitespace")
    if EMAIL_PATTERN.search(value):
        _fail(f"{field} contains an email address; use public display text only")
    if URL_PATTERN.search(value):
        _fail(f"{field} contains a URL; use public display text only")
    if LOCAL_PATH_PATTERN.search(value):
        _fail(f"{field} contains a local path; use public display text only")


def _validate_metadata(document: Any) -> None:
    if not isinstance(document, dict):
        _fail("Each document must be an object")
    missing = REQUIRED_FIELDS - document.keys()
    unknown = document.keys() - REQUIRED_FIELDS - OPTIONAL_FIELDS
    if missing:
        _fail(f"Document is missing required fields: {', '.join(sorted(missing))}")
    if unknown:
        _fail(f"Unknown document fields: {', '.join(sorted(unknown))}")
    if document["public_reviewed"] is not True:
        _fail("public_reviewed must be true after the PDF and display text are reviewed for public release")
    document_id = document["id"]
    if not isinstance(document_id, str) or len(document_id) > 120 or not ID_PATTERN.fullmatch(document_id):
        _fail("id must be a lowercase YYYY-MM-DD-slug using letters, digits, and single hyphens (at most 120 characters)")
    issue_date = document["date"]
    if not isinstance(issue_date, str) or not DATE_PATTERN.fullmatch(issue_date):
        _fail("date must use YYYY-MM-DD")
    try:
        date.fromisoformat(issue_date)
    except ValueError:
        _fail("date must be a valid calendar date")
    if not document_id.startswith(issue_date + "-"):
        _fail("id must start with the document date followed by a hyphen")
    if not isinstance(document["series"], str) or document["series"] not in SERIES:
        _fail(f"series must be one of: {', '.join(sorted(SERIES))}")
    if not isinstance(document["language"], str) or document["language"] not in LANGUAGES:
        _fail("language must be ko or en")
    if document["file"] != f"files/{document_id}.pdf":
        _fail("file must be exactly files/<id>.pdf")
    for field, limit in (("title", 240), ("summary", 1600), ("title_en", 240), ("summary_en", 1600), ("source_title", 240)):
        if field in document:
            _check_text(document[field], field, limit)
    tags = document["tags"]
    if not isinstance(tags, list) or len(tags) > 12:
        _fail("tags must be a list of at most 12 text labels")
    for tag in tags:
        _check_text(tag, "tag", 48)
    if len(set(tags)) != len(tags):
        _fail("tags must not contain duplicates")


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def load_documents(archive_dir: Path) -> list[dict[str, Any]]:
    """Return validated, explicitly registered public PDFs, newest first.

    A missing or zero-byte manifest initializes an empty registry. Extra files
    in archive/files are never discovered or returned automatically.
    """
    archive_dir = Path(archive_dir)
    _check_directory(archive_dir, allow_missing=True)
    _check_directory(archive_dir / "files", allow_missing=True)
    manifest_path = archive_dir / "manifest.json"
    _reject_symlink_components(manifest_path)
    if not manifest_path.exists():
        return []
    if not manifest_path.is_file():
        _fail("manifest.json must be a regular file")
    try:
        raw = manifest_path.read_text(encoding="utf-8")
        if not raw.strip():
            return []
        manifest = json.loads(raw, object_pairs_hook=_unique_json_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail(f"Could not read archive manifest: {exc}")
    if not isinstance(manifest, dict) or set(manifest) != {"version", "documents"}:
        _fail("Manifest must contain exactly version and documents")
    if type(manifest["version"]) is not int or manifest["version"] != 1:
        _fail("Manifest version must be 1")
    documents = manifest["documents"]
    if not isinstance(documents, list):
        _fail("Manifest documents must be a list")
    seen: set[str] = set()
    for document in documents:
        _validate_metadata(document)
        if document["id"] in seen:
            _fail(f"Duplicate document id: {document['id']}")
        seen.add(document["id"])
        pdf_path = archive_dir / document["file"]
        if not pdf_path.resolve().is_relative_to(archive_dir.resolve()):
            _fail("PDF path must remain inside the archive directory")
        _check_pdf(pdf_path)
    return sorted(documents, key=lambda document: (document["date"], document["id"]), reverse=True)


def _write_manifest_atomic(archive_dir: Path, documents: list[dict[str, Any]]) -> None:
    manifest = {"version": 1, "documents": sorted(documents, key=lambda item: (item["date"], item["id"]), reverse=True)}
    fd, temporary_name = tempfile.mkstemp(prefix=".manifest-", suffix=".json", dir=archive_dir)
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, archive_dir / "manifest.json")
    finally:
        temporary_path.unlink(missing_ok=True)


def import_document(
    input_pdf: Path,
    document: dict[str, Any],
    archive_dir: Path = DEFAULT_ARCHIVE_DIR,
    *,
    replace: bool = False,
) -> Path:
    """Copy an explicitly reviewed PDF and atomically update the registry.

    --replace can replace the PDF of an existing registry entry only. An
    unregistered file is never overwritten, even when replace is requested.
    """
    archive_dir = Path(archive_dir)
    input_pdf = Path(input_pdf)
    _validate_metadata(document)
    _check_pdf(input_pdf)
    documents = load_documents(archive_dir)
    existing = next((item for item in documents if item["id"] == document["id"]), None)
    if existing is not None and not replace:
        _fail(f"Document id already exists: {document['id']}; use --replace to update it")
    files_dir = archive_dir / "files"
    _check_directory(files_dir, allow_missing=True)
    destination = archive_dir / document["file"]
    _reject_symlink_components(destination)
    if destination.exists() and existing is None:
        _fail(f"Refusing to overwrite an unregistered file: {destination}")
    archive_dir.mkdir(parents=True, exist_ok=True)
    files_dir.mkdir(exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=".incoming-", suffix=".pdf", dir=files_dir)
    os.close(fd)
    temporary_path = Path(temporary_name)
    backup_path: Path | None = None
    installed = False
    try:
        shutil.copyfile(input_pdf, temporary_path)
        _check_pdf(temporary_path)
        updated = [item for item in documents if item["id"] != document["id"]] + [document]
        if existing is not None:
            backup_fd, backup_name = tempfile.mkstemp(prefix=".previous-", suffix=".pdf", dir=files_dir)
            os.close(backup_fd)
            backup_path = Path(backup_name)
            shutil.copyfile(destination, backup_path)
        os.replace(temporary_path, destination)
        installed = True
        _write_manifest_atomic(archive_dir, updated)
    except BaseException:
        if installed:
            if backup_path is not None:
                os.replace(backup_path, destination)
            else:
                destination.unlink(missing_ok=True)
        raise
    finally:
        temporary_path.unlink(missing_ok=True)
        if backup_path is not None:
            backup_path.unlink(missing_ok=True)
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import a PDF reviewed for publication into the review archive")
    parser.add_argument("input_pdf", type=Path, help="PDF file supplied by the user")
    parser.add_argument("--archive-dir", type=Path, default=DEFAULT_ARCHIVE_DIR)
    parser.add_argument("--date", required=True, help="Publication date, YYYY-MM-DD")
    parser.add_argument("--series", required=True, choices=sorted(SERIES))
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--language", required=True, choices=sorted(LANGUAGES))
    parser.add_argument("--id", required=True, help="YYYY-MM-DD-lowercase-slug")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--title-en")
    parser.add_argument("--summary-en")
    parser.add_argument("--source-title", help="Public series or publication title, without email metadata")
    parser.add_argument("--public-reviewed", action="store_true", required=True, help="Confirm the entire PDF and display metadata have been reviewed for public release")
    parser.add_argument("--replace", action="store_true", help="Replace an existing registered document with the same id")
    args = parser.parse_args(argv)
    document = {
        "id": args.id,
        "date": args.date,
        "series": args.series,
        "title": args.title,
        "summary": args.summary,
        "language": args.language,
        "file": f"files/{args.id}.pdf",
        "tags": args.tag,
        "public_reviewed": args.public_reviewed,
    }
    for field in OPTIONAL_FIELDS:
        value = getattr(args, field)
        if value is not None:
            document[field] = value
    try:
        destination = import_document(args.input_pdf, document, args.archive_dir, replace=args.replace)
    except (ArchiveValidationError, OSError) as exc:
        parser.exit(1, f"Archive import failed: {exc}\n")
    print(f"Imported {document['id']}: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
