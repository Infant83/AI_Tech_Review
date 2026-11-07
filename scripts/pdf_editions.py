"""Keep exact prior public PDF bytes when a registered document is replaced.

The current legacy URL remains unchanged. Historical editions use content hashes;
notes are never copied between distinct PDF fingerprints.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil

SHA = re.compile(r"[a-f0-9]{64}\Z")
ID = re.compile(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def regular(path: Path):
    # Use the archive module's macOS system-alias-aware path check.
    try:
        from .archive_documents import _reject_symlink_components
    except ImportError:
        from archive_documents import _reject_symlink_components
    _reject_symlink_components(path)


def preserve_previous(archive: Path, identifier: str, pdf: Path) -> Path:
    if not ID.fullmatch(identifier):
        raise ValueError("Invalid edition document ID")
    regular(pdf)
    payload = pdf.read_bytes()
    if not payload.startswith(b"%PDF-"):
        raise ValueError("Invalid edition PDF")
    digest = hashlib.sha256(payload).hexdigest()
    target = archive / "editions" / identifier / (digest + ".pdf")
    regular(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents accidental mutation of an immutable edition.
    try:
        with target.open("xb") as handle:
            handle.write(payload)
    except FileExistsError:
        if target.read_bytes() != payload:
            raise ValueError("Existing immutable PDF edition is corrupt")
    return target


def historical_editions(archive: Path, identifier: str, current_sha: str) -> list[dict]:
    if not ID.fullmatch(identifier) or not SHA.fullmatch(current_sha):
        raise ValueError("Invalid edition identity")
    directory = archive / "editions" / identifier
    regular(directory)
    if not directory.exists():
        return []
    if not directory.is_dir():
        raise ValueError("PDF editions must be a directory")
    editions = []
    for path in sorted(directory.iterdir()):
        regular(path)
        if not path.is_file() or path.suffix != ".pdf" or not SHA.fullmatch(path.stem):
            raise ValueError("Unexpected PDF edition file")
        payload = path.read_bytes()
        if not payload.startswith(b"%PDF-") or hashlib.sha256(payload).hexdigest() != path.stem:
            raise ValueError("PDF edition checksum mismatch")
        if path.stem != current_sha:
            editions.append({"sha256": path.stem, "size_bytes": len(payload),
                             "href": f"archive/editions/{identifier}/{path.name}"})
    return editions


def stage_editions(archive: Path, staging: Path, documents: list[dict]):
    for document in documents:
        editions = historical_editions(archive, document["id"], document["sha256"])
        if editions:
            document["editions"] = editions
        for edition in editions:
            source = archive / edition["href"].removeprefix("archive/")
            target = staging / edition["href"].removeprefix("archive/")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)


def validate_editions(site: Path, document: dict) -> list[str]:
    if "editions" not in document:
        return []
    errors, seen = [], {document["sha256"]}
    editions = document.get("editions", [])
    if not isinstance(editions, list):
        return ["Invalid PDF editions list"]
    for row in editions:
        if (not isinstance(row, dict) or set(row) != {"sha256", "size_bytes", "href"}
                or not isinstance(row.get("sha256"), str) or not SHA.fullmatch(row["sha256"])
                or row["sha256"] in seen or type(row.get("size_bytes")) is not int
                or row["size_bytes"] < 5
                or row.get("href") != f'archive/editions/{document["id"]}/{row["sha256"]}.pdf'):
            errors.append("Invalid PDF edition identity")
            continue
        seen.add(row["sha256"])
        path = site / row["href"]
        regular(path)
        if (not path.is_file() or path.stat().st_size != row["size_bytes"]
                or hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]):
            errors.append("Missing or corrupt PDF edition: " + row["href"])
    return errors
