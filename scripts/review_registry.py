"""Strict per-review source registrations, independent of hosting providers."""
from __future__ import annotations

from dataclasses import MISSING, fields
from datetime import date
import json
from pathlib import Path
import re


class ReviewRegistrationError(ValueError):
    pass


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ReviewRegistrationError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def _text(value, field, *, nonempty=False):
    if (not isinstance(value, str) or (nonempty and not value.strip())
            or any(ord(char) < 32 for char in value)):
        raise ReviewRegistrationError(f"{field} must be single-line text")


def _date(value, field, *, optional=False):
    if optional and value == "":
        return
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ReviewRegistrationError(f"{field} must use YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise ReviewRegistrationError(f"{field} must be a valid calendar date") from error


def load_review_registry(directory: Path, review_type, translation_type, agent_type) -> tuple:
    """Load one JSON source file per review without allocating shared counters.

    legacy_position freezes the pre-migration order only. New registrations omit
    it and use their stable folder names; it is never a publication identifier.
    """
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        raise ReviewRegistrationError("Review registration directory is missing or linked")
    specs = {field.name: field for field in fields(review_type)}
    required = {name for name, field in specs.items()
                if field.default is MISSING and field.default_factory is MISSING}
    list_fields = {name for name, field in specs.items() if field.default == ()} | {"tags"}
    result, folders, positions = [], set(), set()
    for path in sorted(directory.glob("*.json")):
        if path.is_symlink() or not path.is_file():
            raise ReviewRegistrationError(f"Registration must be a regular file: {path.name}")
        try:
            source = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise ReviewRegistrationError(f"Invalid registration JSON: {path.name}") from error
        if (not isinstance(source, dict) or set(source) - {"version", "legacy_position", "source_sha256", "review"}
                or type(source.get("version")) is not int or source["version"] != 1):
            raise ReviewRegistrationError(f"Invalid registration envelope: {path.name}")
        if (source.get("source_sha256") is not None
                and (not isinstance(source["source_sha256"], str)
                     or not re.fullmatch(r"[a-f0-9]{64}", source["source_sha256"]))):
            raise ReviewRegistrationError(f"Invalid historical source hash: {path.name}")
        review = source.get("review")
        if not isinstance(review, dict) or required - review.keys() or review.keys() - specs.keys():
            raise ReviewRegistrationError(f"Missing or unknown review fields: {path.name}")
        review = dict(review)
        folder = review["folder"]
        if (not isinstance(folder, str)
                or not re.fullmatch(r"\d{4}-\d{2}-\d{2}_[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", folder)
                or path.name != folder + ".json"):
            raise ReviewRegistrationError(f"Folder and registration filename must match: {path.name}")
        if folder in folders:
            raise ReviewRegistrationError(f"Duplicate review folder: {folder}")
        folders.add(folder)
        position = source.get("legacy_position")
        if position is not None:
            if type(position) is not int or position < 0 or position in positions:
                raise ReviewRegistrationError(f"Invalid or duplicate legacy position: {path.name}")
            positions.add(position)
        for name, value in review.items():
            if name in list_fields:
                if not isinstance(value, list):
                    raise ReviewRegistrationError(f"{name} must be a list: {path.name}")
                if name in {"translations", "agents"}:
                    cls = translation_type if name == "translations" else agent_type
                    keys = {field.name for field in fields(cls)}
                    if any(not isinstance(row, dict) or set(row) != keys for row in value):
                        raise ReviewRegistrationError(f"Invalid {name}: {path.name}")
                    for row in value:
                        for key, text in row.items():
                            _text(text, key, nonempty=True)
                    if name == "translations":
                        languages, subdirs = set(), set()
                        for row in value:
                            if (not re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z0-9]+)*", row["language"])
                                    or not re.fullmatch(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*", row["subdir"])
                                    or row["language"] in languages or row["subdir"] in subdirs):
                                raise ReviewRegistrationError(f"Invalid or duplicate translation: {path.name}")
                            languages.add(row["language"])
                            subdirs.add(row["subdir"])
                    review[name] = tuple(cls(**row) for row in value)
                else:
                    for text in value:
                        _text(text, name, nonempty=True)
                    review[name] = tuple(value)
            elif name == "primary_sources_checked":
                if type(value) is not bool:
                    raise ReviewRegistrationError(f"{name} must be boolean: {path.name}")
            else:
                _text(value, name, nonempty=name in required)
        _date(review["date"], "date")
        _date(review["updated"], "updated")
        _date(review.get("evidence_cutoff", ""), "evidence_cutoff", optional=True)
        result.append((position, folder, review_type(**review)))
    # New independent records precede the frozen historical group. The hub's
    # normal publication-date sort then places each at its publication date.
    result.sort(key=lambda item: (item[0] is not None, item[0] if item[0] is not None else 0, item[1]))
    return tuple(item[2] for item in result)
