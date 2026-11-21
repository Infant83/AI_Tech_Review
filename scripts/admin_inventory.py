"""Bounded, local, read-only projection of the explicit public registrations.

This adapter does not build an artifact, visit links, update publication intent,
or inspect private reader data. A supplied baseline must already have been
obtained by the normal deployment-verification route; its seals are rechecked
locally here. Hash comparisons describe their stated scope, not human review.
"""
from __future__ import annotations

import ast
from collections import Counter
from dataclasses import MISSING, dataclass, fields
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
from urllib.parse import urlsplit, unquote

from .archive_documents import (load_documents, document_version, _check_text,
                                _reject_symlink_components)
from .external_resources import load_external_resources
from .publication_intent import review_inputs
from .publication_release import (declarations, validate_release, verify_catalog_binding,
                                  verify_baseline_updates)
from .publication_snapshot import ID, SHA, relative_path
from .reader_engagement_publish import (validate_catalog, PUBLIC_DIRECTORIES, PUBLIC_ROOT_FILES,
                                        PUBLIC_EXTENSIONS, PRIVATE_NAMES)
from .review_registry import load_review_registry
from .document_archive_site import LECTURE_BUNDLES, SERIES, lecture_series_metadata
from .lecture_chapters import chapter_files

MAX_JSON_FILE_BYTES = 5_000_000
MAX_JSON_TOTAL_BYTES = 16_000_000
MAX_ROWS = 2_000
MAX_RESPONSE_BYTES = 2_000_000
SITE_ORIGIN = "https://infant83.io"
SITE_SCOPE = "/AI_Tech_Review/"
REVISION = re.compile(r"[a-f0-9]{40}\Z")
LANGUAGE = re.compile(r"[a-z]{2,3}(?:-[A-Za-z0-9]+)*\Z")


class InventoryError(ValueError):
    """A public reason code; never attach the underlying path or source value."""

    def __init__(self, code: str):
        self.code = code
        super().__init__("Local inventory could not be verified (" + code + ").")


# The native reader deliberately accepts dataclass types. Importing the site
# publisher would load its global registry before our bounded-input preflight.
# Keep compatible immutable types and check their AST field schema at runtime.
@dataclass(frozen=True)
class PublicTranslation:
    language: str
    subdir: str
    label: str


@dataclass(frozen=True)
class PublicAgent:
    name: str
    role: str
    role_ko: str


@dataclass(frozen=True)
class PublicReview:
    folder: str
    title: str
    subtitle: str
    date: str
    updated: str
    category: str
    tags: tuple[str, ...]
    summary: str
    translations: tuple[PublicTranslation, ...] = ()
    responsible_editor: str = "김현중"
    responsible_editor_en: str = "Hyun-Jung Kim"
    ai_system: str = "AI-assisted workflow; exact system record not retained"
    ai_system_ko: str = "AI 보조 워크플로; 정확한 시스템 기록은 보존되지 않음"
    ai_model: str = "exact model identifier not retained"
    ai_model_ko: str = "정확한 모델 식별자는 보존되지 않음"
    agents: tuple[PublicAgent, ...] = ()
    agent_roles: tuple[str, ...] = ()
    agent_roles_ko: tuple[str, ...] = ()
    verification_scope: tuple[str, ...] = ()
    verification_scope_ko: tuple[str, ...] = ()
    primary_sources_checked: bool = False
    evidence_cutoff: str = ""
    human_review_level: str = "review level not separately retained"
    human_review_level_ko: str = "세부 검토 수준은 별도 기록되지 않음"
    disclosure_note_ko: str = ""
    disclosure_note_en: str = ""


def _canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _token(value) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InventoryError("duplicate_json_key")
        result[key] = value
    return result


def _plain(path: Path, boundary: Path) -> Path:
    # Check the lexical path first: resolve() alone would conceal a symlink.
    path = Path(os.path.abspath(path))
    if path != boundary and boundary not in path.parents:
        raise InventoryError("input_outside_boundary")
    try:
        _reject_symlink_components(path)
    except ValueError:
        raise InventoryError("input_symlink") from None
    return path


class _Inputs:
    """Remember only inputs actually consumed, including directory membership."""

    def __init__(self, root: Path):
        self.root = root
        self.files = {}
        self.directories = {}
        self.source_directories = set()
        self.json_files = set()
        self.json_total = 0
        self.json_payloads = {}

    def directory(self, path, *, boundary=None, optional=False):
        source_input = boundary is None
        boundary = boundary or self.root
        path = _plain(path, boundary)
        if source_input:
            self.source_directories.add(path)
        if not path.exists():
            if not optional:
                raise InventoryError("required_input_missing")
            self.directories[path] = None
            return []
        if not path.is_dir():
            raise InventoryError("invalid_input_type")
        entries = sorted(path.iterdir())
        self.directories[path] = tuple(p.name for p in entries)
        for entry in entries:
            _plain(entry, boundary)
        return entries

    def file(self, path, *, boundary=None):
        source_input = boundary is None
        boundary = boundary or self.root
        path = _plain(path, boundary)
        if path in self.files:
            return self.files[path]
        try:
            before = path.stat()
            if not stat.S_ISREG(before.st_mode):
                raise InventoryError("invalid_input_type")
            raw, blob = hashlib.sha256(), hashlib.sha1()
            blob.update(("blob " + str(before.st_size)).encode("ascii") + b"\0")
            size = 0
            with path.open("rb") as handle:
                while True:
                    chunk = handle.read(1024 * 1024)
                    if not chunk:
                        break
                    raw.update(chunk)
                    blob.update(chunk)
                    size += len(chunk)
            after = path.stat()
        except OSError:
            raise InventoryError("required_input_missing") from None
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (
                after.st_ino, after.st_size, after.st_mtime_ns) or size != before.st_size:
            raise InventoryError("input_changed")
        info = {"sha256": raw.hexdigest(), "bytes": size, "git": blob.hexdigest(),
                "boundary": boundary, "source": source_input}
        self.files[path] = info
        return info

    def json(self, path, *, boundary=None):
        path = _plain(path, boundary or self.root)
        # Bound the read before any native loader is allowed to parse the file.
        try:
            if path.stat().st_size > MAX_JSON_FILE_BYTES:
                raise InventoryError("json_file_limit")
        except OSError:
            raise InventoryError("required_input_missing") from None
        info = self.file(path, boundary=boundary)
        if path not in self.json_files:
            self.json_total += info["bytes"]
            self.json_files.add(path)
        if self.json_total > MAX_JSON_TOTAL_BYTES:
            raise InventoryError("json_total_limit")
        with path.open("rb") as handle:
            payload = handle.read(MAX_JSON_FILE_BYTES + 1)
        if len(payload) > MAX_JSON_FILE_BYTES:
            raise InventoryError("json_file_limit")
        if hashlib.sha256(payload).hexdigest() != info["sha256"]:
            raise InventoryError("input_changed")
        try:
            value = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique,
                               parse_constant=lambda _: _invalid_json())
        except InventoryError:
            raise
        except (UnicodeError, ValueError, RecursionError):
            raise InventoryError("invalid_json") from None
        # Only bounded JSON bytes are retained, within json_total's existing
        # limit. Native validators must consume the bytes whose hashes we track.
        self.json_payloads[path] = payload
        return value

    def ledger(self, path, *, optional=False):
        entries = self.directory(path, optional=optional)
        result = {}
        for entry in entries:
            if entry.suffix != ".json" or not entry.is_file():
                raise InventoryError("invalid_registry_entry")
            result[entry.stem] = self.json(entry)
        return result

    def tree(self, path):
        # This is the explicitly registered dist source, not arbitrary discovery.
        # Manuscript hash-only reads are separate from decoded JSON input budgets.
        entries = self.directory(path, optional=True)
        for entry in entries:
            if entry.name in {".DS_Store", "Thumbs.db"}:
                continue
            if PRIVATE_NAMES.search(entry.name):
                raise InventoryError("private_source_input")
            if entry.is_dir():
                self.tree(entry)
            else:
                self.file(entry)

    def verify(self):
        for path, names in self.directories.items():
            _plain(path, self.root if path == self.root or self.root in path.parents else path.parent)
            if path.exists() and not path.is_dir():
                raise InventoryError("input_changed")
            current = tuple(p.name for p in sorted(path.iterdir())) if path.is_dir() else None
            if current != names:
                raise InventoryError("input_changed")
        for path, info in self.files.items():
            _plain(path, info["boundary"])
            raw = hashlib.sha256()
            try:
                if not stat.S_ISREG(path.stat().st_mode):
                    raise InventoryError("input_changed")
                with path.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        raw.update(chunk)
            except OSError:
                raise InventoryError("input_changed") from None
            if raw.hexdigest() != info["sha256"]:
                raise InventoryError("input_changed")


def _invalid_json():
    raise InventoryError("invalid_json")


def _check_models(tracker):
    path = tracker.root / "scripts/publish_public_site.py"
    info = tracker.file(path)
    with path.open("rb") as handle:
        payload = handle.read(info["bytes"] + 1)
    if len(payload) != info["bytes"] or hashlib.sha256(payload).hexdigest() != info["sha256"]:
        raise InventoryError("input_changed")
    tree = ast.parse(payload.decode("utf-8"))
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    for model in (PublicTranslation, PublicAgent, PublicReview):
        node = classes.get(model.__name__)
        if node is None:
            raise InventoryError("review_model_schema_changed")
        specs = [item for item in node.body if isinstance(item, ast.AnnAssign)]
        expected = fields(model)
        if len(specs) != len(expected):
            raise InventoryError("review_model_schema_changed")
        for actual, known in zip(specs, expected):
            if (not isinstance(actual.target, ast.Name) or actual.target.id != known.name
                    or ast.unparse(actual.annotation) != model.__annotations__[known.name]):
                raise InventoryError("review_model_schema_changed")
            try:
                value = MISSING if actual.value is None else ast.literal_eval(actual.value)
            except (ValueError, TypeError, SyntaxError):
                raise InventoryError("review_model_schema_changed") from None
            if value != known.default:
                raise InventoryError("review_model_schema_changed")


def _text(value, limit=240):
    _check_text(value, "display text", limit)
    return value


def _public_path(value):
    relative_path(value)
    # URL parser normalization, percent escapes and non-public schemes are not
    # accepted as alternatives to a canonical sealed path.
    pieces = value.rstrip("/").split("/")
    if (len(value) > 2000 or not re.fullmatch(r"[A-Za-z0-9_./-]+", value)
            or any(char.isspace() or ord(char) == 127 for char in value)
            or any((piece.startswith(".") and value != ".nojekyll") or PRIVATE_NAMES.search(piece) for piece in pieces)
            or (len(pieces) == 1 and value not in PUBLIC_ROOT_FILES)
            or (len(pieces) > 1 and pieces[0] not in PUBLIC_DIRECTORIES)
            or (not value.endswith("/") and len(pieces) > 1
                and Path(value).suffix not in PUBLIC_EXTENSIONS and not value.endswith("resources.zip")
                and not (value.startswith("lectures/reader/") and Path(value).suffix in {
                    ".mjs", ".bcmap", ".pfb", ".ttf", ".wasm"}))):
        raise InventoryError("invalid_public_link")
    return value + "index.html" if value.endswith("/") else value


def _external_url(value):
    if not isinstance(value, str) or len(value) > 1000:
        raise InventoryError("invalid_public_link")
    parsed = urlsplit(value)
    if (parsed.scheme != "https" or not re.fullmatch(
            r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", parsed.netloc)
            or parsed.netloc.rsplit(".", 1)[-1] in {"local", "internal", "test", "invalid", "localhost"}
            or parsed.query or parsed.fragment or "?" in value or "#" in value or "\\" in value
            or any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in value)
            or unquote(parsed.path).lower().endswith(".pdf")):
        raise InventoryError("invalid_public_link")
    return value


def _validate_baseline(tracker, path, checked_at):
    boundary = Path(os.path.abspath(path)).parent
    tracker.directory(boundary, boundary=boundary)
    snapshot = tracker.json(path, boundary=boundary)
    release_path = boundary / "release.json"
    catalog_path = boundary / "reader-publications.json"
    updates_path = boundary / "reader-updates.json"
    release = tracker.json(release_path, boundary=boundary)
    catalog = tracker.json(catalog_path, boundary=boundary)
    tracker.json(updates_path, boundary=boundary)
    catalog_bytes = tracker.json_payloads[catalog_path]
    updates_bytes = tracker.json_payloads[updates_path]
    validate_catalog(catalog)
    verify_catalog_binding(release, catalog_bytes)
    updates = verify_baseline_updates(release, snapshot, updates_bytes)
    if not validate_release(snapshot, snapshot)["ok"]:
        raise InventoryError("invalid_baseline")
    if (set(snapshot) != {"version", "reviews", "archive", "publications", "external", "files",
                          "missing_files", "declared_hash_mismatches"}
            or type(snapshot["version"]) is not int or snapshot["version"] != 1
            or snapshot["missing_files"] != [] or snapshot["declared_hash_mismatches"] != []):
        raise InventoryError("invalid_baseline")
    expected_publications = {a["id"]: {key: a[key] for key in ("path", "topic", "publishedAt")}
                             for a in catalog["articles"]}
    if snapshot["publications"] != expected_publications:
        raise InventoryError("invalid_baseline")
    for path_name, record in snapshot["files"].items():
        if (_public_path(path_name) != path_name or not isinstance(record, dict)
                or set(record) - {"sha256", "content_sha256", "bytes", "reader_identity"}
                or not SHA.fullmatch(str(record.get("sha256", "")))
                or not SHA.fullmatch(str(record.get("content_sha256", "")))
                or type(record.get("bytes")) is not int or record["bytes"] < 0):
            raise InventoryError("invalid_baseline")
    for group in ("reviews", "archive"):
        for identifier, record in snapshot[group].items():
            allowed = ({"href", "metric_path", "translations", "date", "references"} if group == "reviews"
                       else {"href", "study_href", "date", "references", "editorial_references"})
            if set(record) - allowed or not {"href", "date", "references"}.issubset(record):
                raise InventoryError("invalid_baseline")
            _date(record["date"])
            refs = record["references"]
            if not isinstance(refs, list) or len(refs) != len(set(refs)):
                raise InventoryError("invalid_baseline")
            for name in refs:
                if _public_path(name) != name or name not in snapshot["files"]:
                    raise InventoryError("invalid_baseline")
            if _public_path(record["href"]) not in refs:
                raise InventoryError("invalid_baseline")
            expected_href = ("reviews/" + identifier + "/index.html" if group == "reviews"
                             else "archive/files/" + identifier + ".pdf")
            if record["href"] != expected_href:
                raise InventoryError("invalid_baseline")
            if group == "archive":
                if record.get("study_href") and _public_path(record["study_href"]) not in refs:
                    raise InventoryError("invalid_baseline")
                if not set(record.get("editorial_references", [])).issubset(refs):
                    raise InventoryError("invalid_baseline")
            else:
                if not isinstance(record.get("translations"), dict):
                    raise InventoryError("invalid_baseline")
                for language, translation in record["translations"].items():
                    if (not LANGUAGE.fullmatch(language) or not isinstance(translation, dict)
                            or set(translation) != {"href", "metric_path"}
                            or _public_path(translation["href"]) not in refs):
                        raise InventoryError("invalid_baseline")
    for identifier, record in snapshot["external"].items():
        if set(record) != {"book_url"}:
            raise InventoryError("invalid_baseline")
        _external_url(record["book_url"])
    for article in catalog["articles"]:
        if _public_path(article["path"][len(SITE_SCOPE):]) not in snapshot["files"]:
            raise InventoryError("invalid_baseline")
        _text(article["title"])
    # The snapshot comparison is the existing continuity validator; these
    # additional checks bind its metadata to one complete local release bundle.
    artifact_files = release.get("artifact_files")
    if not isinstance(artifact_files, dict):
        raise InventoryError("invalid_baseline")
    for name, record in artifact_files.items():
        if (_public_path(name) != name or not isinstance(record, dict)
                or set(record) != {"sha256", "bytes"} or not SHA.fullmatch(str(record["sha256"]))
                or type(record["bytes"]) is not int or record["bytes"] < 0):
            raise InventoryError("invalid_baseline")
    for name, record in snapshot["files"].items():
        if artifact_files.get(name) != {"sha256": record["sha256"], "bytes": record["bytes"]}:
            raise InventoryError("invalid_baseline")
    if artifact_files.get("reader-publications.json") != {
            "sha256": hashlib.sha256(catalog_bytes).hexdigest(), "bytes": len(catalog_bytes)}:
        raise InventoryError("invalid_baseline")
    initial = release.get("initial_payloads")
    if not isinstance(initial, dict) or any(_public_path(name) != name or type(size) is not int or size < 0
                                            for name, size in initial.items()):
        raise InventoryError("invalid_baseline")
    return snapshot, catalog, updates, {
        "status": "verified_deployed_artifact", "releaseRevision": release["revision"],
        "releaseSha256": tracker.files[release_path]["sha256"],
        "catalogSha256": tracker.files[catalog_path]["sha256"],
        "updatesSha256": tracker.files[updates_path]["sha256"],
        "origin": "provided_local_verified_bundle", "checkedAt": checked_at,
    }


def _date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise InventoryError("invalid_registration")
    date.fromisoformat(value)
    return value


def _source_revision(root, tracker):
    """Local Git reads only; HEAD drift is not a deployment-state judgment."""
    try:
        revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True,
                                  check=True, timeout=10).stdout.decode("ascii").strip()
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=root, capture_output=True,
                             check=True, timeout=10).stdout.decode().strip()
        if not REVISION.fullmatch(revision) or Path(top) != root:
            return None, "unknown"
        tree = subprocess.run(["git", "ls-tree", "-rz", revision], cwd=root, capture_output=True,
                              check=True, timeout=10).stdout
        objects = {}
        for row in tree.split(b"\0"):
            if row:
                meta, name = row.split(b"\t", 1)
                mode, kind, sha = meta.split()
                objects[os.fsdecode(name)] = (mode, kind, sha.decode("ascii"))
        consumed = [(p.relative_to(root).as_posix(), info) for p, info in tracker.files.items()
                    if info["source"] and root in p.parents]
        matches = all(objects.get(name) in ((b"100644", b"blob", info["git"]),
                                            (b"100755", b"blob", info["git"]))
                      for name, info in consumed)
        # Removing a selected registration must not look like a matching subset.
        selected = {name for name, _ in consumed}
        selected_directories = tuple(path.relative_to(root).as_posix() + "/" for path in tracker.source_directories
                                     if root in path.parents)
        if any(name.startswith(selected_directories) and name not in selected
               and Path(name).name not in {".DS_Store", "Thumbs.db"} for name in objects):
            matches = False
        return revision, "match" if matches else "different"
    except (OSError, subprocess.SubprocessError, UnicodeError, ValueError):
        return None, "unknown"


def _checked(inputs, request, historical):
    if request:
        full = "matched" if inputs["registration_sha256"] == request["registration_sha256"] else "changed"
        source_matches = inputs["source_sha256"] == request["source_sha256"]
        if inputs["source_sha256"] is None:
            article = "unknown"
        elif request["version"] == 2:
            article = "matched" if (source_matches and inputs["article_registration_sha256"] ==
                                    request["article_registration_sha256"]) else "changed"
        else:
            article = "changed" if not source_matches else ("matched" if full == "matched" else "unknown")
        return {"article": article, "registration": full,
                "basis": "persistent_request_v" + str(request["version"])}
    if historical:
        return {"article": "unknown" if inputs["source_sha256"] is None else (
                    "matched" if inputs["source_sha256"] == historical else "changed"),
                "registration": "not_recorded", "basis": "historical_source_digest_only"}
    return {"article": "not_recorded", "registration": "not_recorded", "basis": "no_checked_input_record"}


def _base_item(kind, identifier, title, published, *, registered=True):
    if not isinstance(identifier, str) or not ID.fullmatch(identifier):
        raise InventoryError("invalid_identifier")
    return {"id": kind + ":" + identifier, "sourceId": identifier, "kind": kind, "series": None,
            "title": _text(title), "languages": [], "category": None, "tags": [],
            "originalPublishedDate": _date(published),
            "registrationState": "registered" if registered else "baseline_only_source_missing",
            "notificationCatalogMember": False,
            "checkedInputState": {"article": "not_recorded", "registration": "not_recorded", "basis": "no_checked_input_record"},
            "releaseMembership": "unknown",
            "contentComparison": {"state": "unknown", "basis": "baseline_not_provided", "coveredPaths": []},
            "candidateState": "not_provided", "publicLinks": [], "relatedDocumentIds": [],
            "versionEvidence": {}, "previewUrl": None, "warnings": []}


def _link(path, role, language, snapshot, *, expected=None, size=None):
    name = _public_path(path)
    evidence = snapshot["files"].get(name) if snapshot else None
    return {"role": role, "language": language, "url": SITE_ORIGIN + SITE_SCOPE + name,
            "sha256": evidence["sha256"] if evidence else expected,
            "sizeBytes": evidence["bytes"] if evidence else size,
            "evidenceState": "sealed_artifact_metadata" if evidence else "registered_source_only",
            "httpsVerifiedAt": None}


def _comparison(snapshot, record, changes, current_pdf=None):
    if snapshot is None:
        return {"state": "unknown", "basis": "baseline_not_provided", "coveredPaths": []}
    if record is None:
        return {"state": "unknown", "basis": "not_in_deployed_artifact", "coveredPaths": []}
    covered = sorted(name for name in record["references"] if name in changes)
    if current_pdf is not None:
        covered = sorted(set(covered) | {record["href"]})
    if not covered:
        return {"state": "unknown", "basis": "no_reviewed_output_hash", "coveredPaths": []}
    matched = all((current_pdf if current_pdf is not None and name == record["href"] else changes[name]["after"])
                  == snapshot["files"][name]["content_sha256"] for name in covered)
    return {"state": "matches" if matched else "differs",
            "basis": "current_pdf_and_declared_content_hashes" if current_pdf is not None and len(covered) > 1 else (
                "current_source_pdf_vs_deployed_artifact" if current_pdf is not None else "reviewed_declaration_after"),
            "coveredPaths": covered}


def _courses(tracker, documents, items, snapshot):
    indexed = {d["id"]: {**d, "href": "archive/" + d["file"],
                          "sha256": tracker.files[tracker.root / "archive" / d["file"]]["sha256"]}
               for d in documents}
    for primary_id, spec in LECTURE_BUNDLES.items():
        if primary_id not in indexed:
            continue
        source = tracker.root / relative_path(spec["source"])
        if spec.get("unit_registry"):
            registry = tracker.json(source / relative_path(spec["unit_registry"]))
            series = lecture_series_metadata(registry, list(indexed.values()), primary_id)
            _text(series["title"])
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", series["series_id"]):
                raise InventoryError("invalid_course_registry")
            units = {u["archive_id"]: u for u in registry["units"]}
            latest = next(u for u in registry["units"] if u["id"] == registry["latest_unit"])
            related = sorted(units)
            for identifier, unit in units.items():
                item = items["archive:" + identifier]
                item["series"] = {"id": series["series_id"], "title": series["title"]}
                item["relatedDocumentIds"] = [x for x in related if x != identifier]
                path = source / relative_path(unit["pdf"])
                info = tracker.file(path)
                if info["sha256"] != unit["sha256"]:
                    raise InventoryError("course_pdf_mismatch")
                item["publicLinks"].append(_link(spec["href"] + unit["pdf"], "course_unit_pdf", item["languages"][0], snapshot,
                                                 expected=unit["sha256"], size=info["bytes"]))
            # notes.pdf follows the explicitly selected latest unit, not anchor.
            alias = tracker.file(source / "notes.pdf")
            if alias["sha256"] != latest["sha256"]:
                raise InventoryError("course_pdf_mismatch")
            owner = items["archive:" + latest["archive_id"]]
            alias_name = _public_path(spec["href"] + "notes.pdf")
            sealed_alias = snapshot["files"].get(alias_name) if snapshot else None
            if sealed_alias and sealed_alias["sha256"] != latest["sha256"]:
                # A newer source unit is legitimate, but the old deployed alias
                # cannot be attached to that new unit as its confirmed PDF.
                owner["warnings"].append("public_alias_differs_from_current_unit")
            else:
                owner["publicLinks"].append(_link(alias_name, "latest_unit_pdf", owner["languages"][0], snapshot,
                                                 expected=latest["sha256"], size=alias["bytes"]))
        elif (source / "notes.pdf").exists():
            info = tracker.file(source / "notes.pdf")
            if info["sha256"] != indexed[primary_id]["sha256"]:
                raise InventoryError("course_pdf_mismatch")
            items["archive:" + primary_id]["publicLinks"].append(_link(
                spec["href"] + "notes.pdf", "study_pdf", indexed[primary_id]["language"], snapshot,
                expected=info["sha256"], size=info["bytes"]))
        if spec.get("supplement_registry"):
            registry = tracker.json(source / relative_path(spec["supplement_registry"]))
            if (not isinstance(registry, dict) or set(registry) != {"version", "parent_id", "supplements"}
                    or type(registry["version"]) is not int or registry["version"] != 1
                    or registry["parent_id"] != primary_id or not isinstance(registry["supplements"], list)):
                raise InventoryError("invalid_course_registry")
            seen = set()
            hrefs = set()
            allowed_chapters = set()
            if spec.get("chapter_pages"):
                tracker.file(source / "index.html")
                allowed_chapters = set(chapter_files((source / "index.html").read_text(encoding="utf-8")))
            for child in registry["supplements"]:
                required = {"document_id", "href", "pdf", "summary", "summary_en", "sha256", "related_chapters"}
                if (not isinstance(child, dict) or set(child) != required
                        or child["document_id"] not in indexed or child["document_id"] == primary_id
                        or indexed[child["document_id"]]["series"] != "lecture-notes"
                        or child["document_id"] in seen or not re.fullmatch(r"supplements/[a-z0-9]+(?:-[a-z0-9]+)*/", child["href"])
                        or child["href"] in hrefs
                        or child["pdf"] != child["href"] + "supplement.pdf"
                        or child["pdf"] not in spec["files"]
                        or child["sha256"] != indexed[child["document_id"]]["sha256"]):
                    raise InventoryError("invalid_course_registry")
                _text(child["summary"], 1600)
                _text(child["summary_en"], 1600)
                chapters = child["related_chapters"]
                if (not isinstance(chapters, list) or len(chapters) != len(set(chapters))
                        or any(not isinstance(name, str) or name not in allowed_chapters for name in chapters)):
                    raise InventoryError("invalid_course_registry")
                info = tracker.file(source / child["pdf"])
                if info["sha256"] != child["sha256"]:
                    raise InventoryError("course_pdf_mismatch")
                identifier = child["document_id"]
                seen.add(identifier)
                hrefs.add(child["href"])
                items["archive:" + primary_id]["relatedDocumentIds"].append(identifier)
                items["archive:" + identifier]["relatedDocumentIds"].append(primary_id)
                items["archive:" + identifier]["publicLinks"].append(_link(
                    spec["href"] + child["pdf"], "supplement_pdf", indexed[identifier]["language"], snapshot,
                    expected=info["sha256"], size=info["bytes"]))


def build_inventory(source_root: Path, baseline_snapshot: Path | None = None) -> dict:
    """Read an explicit source and optional verified bundle without writing either."""
    try:
        return _build_inventory(Path(source_root), baseline_snapshot)
    except InventoryError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError, SyntaxError):
        # Native validators include useful local paths in their errors. The
        # public adapter intentionally exposes only this stable reason code.
        raise InventoryError("invalid_input") from None


def _build_inventory(source_root, baseline_snapshot):
    root = Path(os.path.abspath(source_root))
    _plain(root, root)
    if not root.is_dir():
        raise InventoryError("required_input_missing")
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    tracker = _Inputs(root)
    _check_models(tracker)
    registrations = tracker.ledger(root / "publication/reviews")
    requests = tracker.ledger(root / "publication/requests", optional=True)
    manifest = tracker.json(root / "archive/manifest.json")
    if manifest != {"version": 2, "entries": "entries"} or type(manifest.get("version")) is not int:
        raise InventoryError("invalid_archive_manifest")
    entries = tracker.ledger(root / "archive/entries")
    external_registration = tracker.json(root / "archive/external-resources.json")
    change_documents = tracker.ledger(root / "publication_changes", optional=True)
    reviews = load_review_registry(root / "publication/reviews", PublicReview, PublicTranslation, PublicAgent)
    for row in entries.values():
        if not isinstance(row, dict) or not isinstance(row.get("file"), str):
            raise InventoryError("invalid_registration")
        name = relative_path(row["file"])
        if name != "files/" + str(row.get("id")) + ".pdf":
            raise InventoryError("invalid_registration")
        tracker.file(root / "archive" / name)
    documents = load_documents(root / "archive")
    resources = load_external_resources(root / "archive")
    known = {r.folder for r in reviews}
    for name, request in requests.items():
        version = request.get("version") if isinstance(request, dict) else None
        required = {"version", "review", "source_sha256", "registration_sha256"}
        if version == 2:
            required.add("article_registration_sha256")
        if (not isinstance(request, dict) or set(request) != required or type(version) is not int
                or version not in {1, 2} or request["review"] != name or name not in known
                or any(not isinstance(request[k], str) or not SHA.fullmatch(request[k])
                       for k in required - {"version", "review"})):
            raise InventoryError("invalid_checked_input_record")
    changes = declarations(root / "publication_changes")
    # preflight and native declaration readers must agree, including empty ledgers.
    if len(changes) != sum(len(value["files"]) for value in change_documents.values()):
        raise InventoryError("invalid_change_declaration")
    snapshot, catalog = None, {"articles": []}
    baseline = {"status": "not_provided", "releaseRevision": None, "releaseSha256": None,
                "catalogSha256": None, "updatesSha256": None, "origin": None, "checkedAt": None}
    if baseline_snapshot is not None:
        try:
            snapshot, catalog, _, baseline = _validate_baseline(tracker, Path(baseline_snapshot), checked_at)
        except InventoryError:
            raise
        except (ValueError, KeyError, TypeError, AttributeError):
            raise InventoryError("invalid_baseline") from None
    catalog_index = {r["id"]: r for r in catalog["articles"]}
    items = {}
    for review in reviews:
        folder = review.folder
        tracker.tree(root / folder / "dist")
        inputs = review_inputs(root, folder)
        current = _base_item("review", folder, review.title, review.date)
        current["languages"] = ["ko"] + sorted(t.language for t in review.translations if t.language != "ko")
        current["category"] = _text(review.category)
        current["tags"] = [_text(tag, 48) for tag in review.tags]
        current["checkedInputState"] = _checked(inputs, requests.get(folder), registrations[folder].get("source_sha256"))
        record = snapshot["reviews"].get(folder) if snapshot else None
        current["releaseMembership"] = ("present" if record else "absent") if snapshot else "unknown"
        current["notificationCatalogMember"] = folder in catalog_index if snapshot else None
        current["contentComparison"] = _comparison(snapshot, record, changes)
        checked = current["checkedInputState"]
        if (current["contentComparison"]["state"] in {"matches", "differs"}
                and not (checked["article"] == "matched" and checked["basis"] in {
                    "persistent_request_v1", "persistent_request_v2"})):
            current["contentComparison"] = {"state": "unknown", "basis": "reviewed_output_not_bound_to_current_inputs",
                                              "coveredPaths": current["contentComparison"]["coveredPaths"]}
        current["publicLinks"].append(_link("reviews/" + folder + "/index.html", "article_html", "ko", snapshot))
        for translation in review.translations:
            current["publicLinks"].append(_link("reviews/" + folder + "/" + translation.subdir + "/index.html",
                                                 "article_html", translation.language, snapshot))
        if record:
            for path in record["references"]:
                if path.endswith(".pdf"):
                    language = next((t.language for t in review.translations
                                     if path.startswith("reviews/" + folder + "/" + t.subdir + "/")), "ko")
                    current["publicLinks"].append(_link(path, "article_pdf", language, snapshot))
        current["versionEvidence"] = {"sourceSha256": inputs["source_sha256"],
                                      "registrationSha256": inputs["registration_sha256"],
                                      "articleRegistrationSha256": inputs["article_registration_sha256"],
                                      "requestVersion": requests[folder]["version"] if folder in requests else None,
                                      "basis": current["checkedInputState"]["basis"]}
        if current["contentComparison"]["state"] == "unknown":
            current["warnings"].append(current["contentComparison"]["basis"])
        items[current["id"]] = current
    for document in documents:
        identifier = document["id"]
        current = _base_item("archive", identifier, document["title"], document["date"])
        current["series"] = {"id": document["series"], "title": SERIES[document["series"]][0]}
        current["languages"] = [document["language"]]
        current["tags"] = list(document["tags"])
        record = snapshot["archive"].get(identifier) if snapshot else None
        current["releaseMembership"] = ("present" if record else "absent") if snapshot else "unknown"
        current["notificationCatalogMember"] = "lecture:" + identifier in catalog_index if snapshot else None
        pdf = tracker.files[root / "archive" / document["file"]]
        current["contentComparison"] = _comparison(snapshot, record, changes, pdf["sha256"])
        current["publicLinks"].append(_link("archive/" + document["file"], "registered_pdf", document["language"], snapshot,
                                             expected=pdf["sha256"], size=pdf["bytes"]))
        if record:
            for path in record["references"]:
                if path == record["href"]:
                    continue
                if path.endswith(".html") or path.endswith(".pdf"):
                    role = "pdf_edition" if path.startswith("archive/editions/") else (
                        "editorial_html" if path in record.get("editorial_references", []) else "study_view")
                    language = "en" if "/en/" in path else document["language"]
                    current["publicLinks"].append(_link(path, role, language, snapshot))
        entry_path = root / "archive/entries" / (identifier + ".json")
        current["versionEvidence"] = {"registrationSha256": tracker.files[entry_path]["sha256"],
                                      "sourcePdfSha256": pdf["sha256"],
                                      "documentVersion": document_version(root / "archive", document),
                                      "basis": "current_registration_and_pdf_only"}
        current["warnings"].append("historical_review_digest_not_recorded")
        items[current["id"]] = current
    for resource in resources:
        identifier = resource["id"]
        current = _base_item("external", identifier, resource["title"], resource["date"])
        current["series"] = {"id": resource["series"], "title": SERIES[resource["series"]][0]}
        current["languages"] = [resource["language"]]
        current["tags"] = list(resource["tags"])
        record = snapshot["external"].get(identifier) if snapshot else None
        current["releaseMembership"] = ("present" if record else "absent") if snapshot else "unknown"
        current["notificationCatalogMember"] = identifier in catalog_index if snapshot else None
        current["contentComparison"] = {"state": "not_applicable", "basis": "external_link_only", "coveredPaths": []}
        current["publicLinks"] = [{"role": "external_landing_page", "language": resource["language"],
                                   "url": _external_url(resource["book_url"]), "sha256": None, "sizeBytes": None,
                                   "evidenceState": "external_link_only", "httpsVerifiedAt": None}]
        current["versionEvidence"] = {"registrationSha256": tracker.files[root / "archive/external-resources.json"]["sha256"],
                                      "basis": "external_registry_only"}
        items[current["id"]] = current
    _courses(tracker, documents, items, snapshot)
    if snapshot:
        for group, kind in (("reviews", "review"), ("archive", "archive"), ("external", "external")):
            for identifier, record in snapshot[group].items():
                key = kind + ":" + identifier
                if key in items:
                    continue
                catalog_id = "lecture:" + identifier if kind == "archive" else identifier
                meta = catalog_index.get(catalog_id)
                published = record.get("date") or (meta["publishedAt"] if meta else identifier[:10])
                current = _base_item(kind, identifier, meta["title"] if meta else identifier, published, registered=False)
                current["releaseMembership"] = "present"
                current["notificationCatalogMember"] = meta is not None
                current["contentComparison"] = {"state": "unknown", "basis": "source_registration_missing", "coveredPaths": []}
                current["warnings"] = ["source_registration_missing"]
                if kind == "external":
                    current["publicLinks"] = [{"role": "external_landing_page", "language": None,
                                               "url": _external_url(record["book_url"]), "sha256": None, "sizeBytes": None,
                                               "evidenceState": "external_link_only", "httpsVerifiedAt": None}]
                else:
                    current["publicLinks"] = [_link(record["href"], "deployed_view", None, snapshot)]
                items[key] = current
        mapped = {r.folder for r in reviews} | {"lecture:" + d["id"] for d in documents if d["series"] == "lecture-notes"}
        mapped |= set(snapshot["reviews"]) | {"lecture:" + identifier for identifier in snapshot["archive"]}
        for identifier, meta in catalog_index.items():
            if identifier in mapped:
                continue
            current = _base_item("catalog_only", identifier, meta["title"], meta["publishedAt"], registered=False)
            current["notificationCatalogMember"] = True
            current["releaseMembership"] = "present"
            # Catalog topics describe reader routing (review/lecture), not a
            # scientific category. No registration means no such metadata.
            current["contentComparison"] = {"state": "unknown", "basis": "catalog_only_no_registration", "coveredPaths": []}
            current["warnings"] = ["catalog_only_no_registration"]
            current["publicLinks"] = [_link(meta["path"][len(SITE_SCOPE):], "catalog_view", None, snapshot)]
            items[current["id"]] = current
    if len(items) > MAX_ROWS:
        raise InventoryError("row_limit")
    ordered = sorted(items.values(), key=lambda item: item["id"])
    ordered.sort(key=lambda item: item["originalPublishedDate"], reverse=True)
    for item in ordered:
        item["relatedDocumentIds"] = sorted(set(item["relatedDocumentIds"]))
        # A path may be both a sealed study reference and an explicit unit alias.
        # Keep the more specific role; never merge material rows by file hash.
        links = {}
        for link in item["publicLinks"]:
            links[link["url"]] = link
        item["publicLinks"] = sorted(links.values(), key=lambda link: (link["role"], link["url"]))
    source_revision, source_state = _source_revision(root, tracker)
    registered = len(reviews) + len(documents) + len(resources)
    totals = {"registered": registered, "reconciled": len(ordered) - registered, "displayed": len(ordered),
              "byKind": dict(sorted(Counter(item["kind"] for item in ordered).items())),
              "bySeries": dict(sorted(Counter(item["series"]["id"] for item in ordered if item["series"]).items()))}
    registration_token = _token({"reviews": registrations, "archiveManifest": manifest, "archive": entries,
                                 "external": external_registration})
    result = {"schemaVersion": 1, "checkedAt": checked_at, "sourceRevision": source_revision,
              "sourceInputState": source_state, "registrationSnapshotToken": registration_token,
              "snapshotToken": _token({"registration": registration_token, "baseline": {
                  k: v for k, v in baseline.items() if k != "checkedAt"}, "items": ordered}),
              "baseline": baseline, "totals": totals, "items": ordered, "nextCursor": None}
    if len((json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")) > MAX_RESPONSE_BYTES:
        raise InventoryError("response_limit")
    tracker.verify()
    final_revision, _ = _source_revision(root, tracker)
    if final_revision != source_revision:
        raise InventoryError("input_changed")
    return result
