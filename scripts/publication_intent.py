"""Bind persistent review publication intent to the inputs that were checked."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

try:
    from .review_registry import _unique_object
except ImportError:
    from review_registry import _unique_object

SHA = re.compile(r"[a-f0-9]{64}\Z")


def source_digest(directory: Path) -> str | None:
    """Hash relative names and bytes; no source paths/content leave the checkout."""
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError("Reviewed source directory must not be a symlink")
    if not directory.exists():
        return None
    if not directory.is_dir():
        raise ValueError("Reviewed source must be a directory")
    digest = hashlib.sha256()
    for path in sorted(directory.rglob("*")):
        if path.name in {".DS_Store", "Thumbs.db"}:
            continue
        if path.is_symlink():
            raise ValueError("Reviewed source files must not be symlinks")
        if not path.is_file() and not path.is_dir():
            raise ValueError("Reviewed source must contain only regular files and directories")
        if path.is_file():
            digest.update(path.relative_to(directory).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def review_inputs(root: Path, folder: str) -> dict:
    registration = Path(root) / "publication/reviews" / (folder + ".json")
    if registration.is_symlink() or not registration.is_file():
        raise ValueError("Review registration is missing or linked: " + folder)
    return {"source_sha256": source_digest(Path(root) / folder / "dist"),
            "registration_sha256": hashlib.sha256(registration.read_bytes()).hexdigest()}


def pending_review_intents(root: Path, known: set[str], explicit: set[str], existing: set[str]) -> dict:
    root = Path(root)
    directory = root / "publication/requests"
    result = {}
    if directory.exists():
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError("Review publication requests must be a regular directory")
        for path in sorted(directory.glob("*.json")):
            if path.is_symlink() or not path.is_file():
                raise ValueError("Publication request must be a regular file")
            request = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
            if (not isinstance(request, dict)
                    or set(request) != {"version", "review", "source_sha256", "registration_sha256"}
                    or type(request["version"]) is not int or request["version"] != 1
                    or request["review"] not in known or path.name != request["review"] + ".json"
                    or any(not isinstance(request[field], str) or not SHA.fullmatch(request[field])
                           for field in ("source_sha256", "registration_sha256"))):
                raise ValueError("Invalid review publication request: " + path.name)
            folder = request["review"]
            inputs = review_inputs(root, folder)
            if folder not in explicit and any(request[key] != value for key, value in inputs.items()):
                raise ValueError("Review inputs changed after validation; prepare again with --review " + folder)
            result[folder] = inputs
    for folder in existing - set(result) - explicit:
        registration = root / "publication/reviews" / (folder + ".json")
        if not registration.is_file():
            raise ValueError("Published review is missing its registration: " + folder)
        source = json.loads(registration.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        if "source_sha256" not in source:
            raise ValueError("Published review requires its historical source baseline or a reviewed request: " + folder)
        if source_digest(root / folder / "dist") != source["source_sha256"]:
            raise ValueError("Changed review source requires an explicit reviewed update: --review " + folder)
    for folder in explicit:
        if folder not in known:
            raise ValueError("Unknown review selected for publication: " + folder)
        inputs = review_inputs(root, folder)
        if inputs["source_sha256"] is None:
            raise ValueError("Explicit review update requires its reviewed dist source: " + folder)
        result[folder] = inputs
    return result


def write_review_intent(root: Path, folder: str, inputs: dict):
    directory = Path(root) / "publication/requests"
    directory.mkdir(parents=True, exist_ok=True)
    if directory.is_symlink():
        raise ValueError("Review request directory must not be a symlink")
    path = directory / (folder + ".json")
    if path.is_symlink():
        raise ValueError("Review request must not be a symlink")
    descriptor, name = tempfile.mkstemp(prefix=".request-", dir=directory)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump({"version": 1, "review": folder, **inputs}, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)
