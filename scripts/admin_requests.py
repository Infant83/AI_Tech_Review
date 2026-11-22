"""Local, read-only preflight for one bounded review hub-metadata request.

No authentication, persistent idempotency, Git writes, candidate generation or
publication is implemented here. Source and baseline paths are operator inputs,
never values supplied by the request document. Reports omit source text/paths.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import uuid

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.admin_inventory import (InventoryError, _Inputs, _plain, _check_models,
                                     _source_revision, _validate_baseline,
                                     PublicReview, PublicTranslation, PublicAgent)
from scripts.publication_intent import HUB_METADATA_FIELDS, review_inputs
from scripts.publication_release import declarations
from scripts.publication_snapshot import relative_path
from scripts.review_registry import (ReviewRegistrationError, load_review_registry,
                                     validate_review_registration)

MAX_REQUEST_BYTES = 32_000
OPERATION = "review_hub_metadata_update"
SHA = re.compile(r"[a-f0-9]{64}\Z")
REVISION = re.compile(r"[a-f0-9]{40}\Z")
SOURCE_ID = re.compile(r"\d{4}-\d{2}-\d{2}_[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*\Z")
INPUT_KEYS = {"source_sha256", "registration_sha256", "article_registration_sha256"}
RELEASE_KEYS = {"releaseSha256", "catalogSha256", "updatesSha256"}
REQUEST_KEYS = {"schemaVersion", "operation", "sourceId", "expectedSourceRevision", "expectedInputs",
                "expectedReleaseRevision", "expectedReleaseEvidence", "patch", "idempotencyKey"}
FIELD_LIMITS = {"subtitle": 1_000, "category": 200, "summary": 8_000}


class PreflightError(ValueError):
    """Stable sanitized reason; never include native exception text or inputs."""

    def __init__(self, code):
        self.code = code
        super().__init__("Local request preflight failed (" + code + ").")


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _invalid():
    raise PreflightError("invalid_request")


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            _invalid()
        value[key] = item
    return value


def _hash_object(value, keys):
    return (isinstance(value, dict) and set(value) == keys
            and all(isinstance(v, str) and SHA.fullmatch(v) for v in value.values()))


def parse_request(payload: bytes) -> dict:
    """Validate bounded UTF-8 request bytes; do not normalize editorial text."""
    if not isinstance(payload, bytes) or len(payload) > MAX_REQUEST_BYTES:
        raise PreflightError("request_limit" if isinstance(payload, bytes) else "invalid_request")
    try:
        value = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique,
                           parse_constant=lambda _: _invalid())
        if (not isinstance(value, dict) or set(value) != REQUEST_KEYS
                or type(value["schemaVersion"]) is not int or value["schemaVersion"] != 1
                or value["operation"] != OPERATION
                or not isinstance(value["sourceId"], str) or not SOURCE_ID.fullmatch(value["sourceId"])
                or any(not isinstance(value[k], str) or not REVISION.fullmatch(value[k])
                       for k in ("expectedSourceRevision", "expectedReleaseRevision"))
                or not _hash_object(value["expectedInputs"], INPUT_KEYS)
                or not _hash_object(value["expectedReleaseEvidence"], RELEASE_KEYS)):
            _invalid()
        key = value["idempotencyKey"]
        if not isinstance(key, str) or str(uuid.UUID(key)) != key or uuid.UUID(key).int == 0:
            _invalid()
        patch = value["patch"]
        if not isinstance(patch, dict) or not patch or not set(patch).issubset(HUB_METADATA_FIELDS):
            raise PreflightError("unsupported_scope")
        for field, item in patch.items():
            if field == "tags":
                if (not isinstance(item, list) or len(item) > 40
                        or any(not isinstance(tag, str) or len(tag) > 200 for tag in item)):
                    _invalid()
            elif not isinstance(item, str) or len(item) > FIELD_LIMITS[field]:
                _invalid()
        # Also reject escaped lone surrogates; canonical JSON is UTF-8 bytes.
        _canonical(value)
        return value
    except PreflightError:
        raise
    except (ValueError, UnicodeError, TypeError, RecursionError):
        raise PreflightError("invalid_request") from None


def request_fingerprint(request: dict) -> str:
    """A request identity hash, not a durable idempotency or authorization grant."""
    return hashlib.sha256(_canonical({k: v for k, v in request.items() if k != "idempotencyKey"})).hexdigest()


def _tracked_review_inputs(tracker, folder, registration):
    """Derive the native three hashes from the one already tracked byte set.

    Native review_inputs performs additional reads. Final A bytes alone cannot
    detect an A→B→A edit during those reads, so its result must also agree with
    the registration object/raw hash and source file hashes captured together.
    """
    protected = {**registration, "review": {key: value for key, value in registration["review"].items()
                                              if key not in HUB_METADATA_FIELDS}}
    directory = tracker.root / folder / "dist"
    source = None
    if tracker.directories[directory] is not None:
        digest = hashlib.sha256()
        # Match source_digest's Path-component order, not relative-name string
        # order: en/index.html and en-guide.png must sort exactly as native.
        for path in sorted(path for path in tracker.files if directory in path.parents):
            digest.update(path.relative_to(directory).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(bytes.fromhex(tracker.files[path]["sha256"]))
        source = digest.hexdigest()
    return {"source_sha256": source,
            "registration_sha256": tracker.files[tracker.root / "publication/reviews" / (folder + ".json")]["sha256"],
            "article_registration_sha256": hashlib.sha256(_canonical(protected)).hexdigest()}


def _frozen_registry(documents):
    folders, positions = set(), set()
    result = []
    for name, value in sorted(documents.items()):
        position, folder, review = validate_review_registration(
            value, name + ".json", PublicReview, PublicTranslation, PublicAgent,
            folders=folders, positions=positions)
        folders.add(folder)
        if position is not None:
            positions.add(position)
        result.append(review)
    return result


def _frozen_declarations(documents):
    """Apply the existing declaration schema to the already bounded JSON set."""
    result = {}
    for document in documents.values():
        if (not isinstance(document, dict) or set(document) != {"version", "reason", "files"}
                or document["version"] != 1 or not isinstance(document["reason"], str)
                or not document["reason"].strip() or not isinstance(document["files"], dict)):
            raise PreflightError("invalid_change_declaration")
        for name, hashes in document["files"].items():
            relative_path(name)
            if (not isinstance(hashes, dict) or set(hashes) != {"before", "after"}
                    or not all(isinstance(value, str) and SHA.fullmatch(value) for value in hashes.values())
                    or name in result):
                raise PreflightError("invalid_change_declaration")
            result[name] = hashes
    return result


def _preflight(source_root, request_path, baseline_snapshot, *, tracker=None,
               revision_reader=None, frozen=False, capture=None):
    root = Path(os.path.abspath(source_root))
    _plain(root, root)
    tracker = tracker if tracker is not None else _Inputs(root)
    revision_reader = revision_reader or _source_revision
    incoming = Path(os.path.abspath(request_path))
    boundary = incoming.parent
    _plain(incoming, boundary)
    if incoming.stat().st_size > MAX_REQUEST_BYTES:
        raise PreflightError("request_limit")
    info = tracker.file(incoming, boundary=boundary)
    payload = tracker.read_bytes(incoming, MAX_REQUEST_BYTES, boundary=boundary)
    if hashlib.sha256(payload).hexdigest() != info["sha256"]:
        raise PreflightError("input_changed")
    request = parse_request(payload)
    _check_models(tracker)
    registrations = tracker.ledger(root / "publication/reviews")
    checked = tracker.ledger(root / "publication/requests", optional=True)
    change_documents = tracker.ledger(root / "publication_changes", optional=True)
    reviews = (_frozen_registry(registrations) if frozen else
               load_review_registry(root / "publication/reviews", PublicReview, PublicTranslation, PublicAgent))
    known = {review.folder for review in reviews}
    folder = request["sourceId"]
    if folder not in known:
        raise PreflightError("unsupported_scope")
    # Validate the merged whole record through the same native pure validator.
    merged = {**registrations[folder], "review": {**registrations[folder]["review"], **request["patch"]}}
    try:
        validate_review_registration(merged, folder + ".json", PublicReview, PublicTranslation, PublicAgent)
    except ReviewRegistrationError:
        raise PreflightError("invalid_request") from None
    for identifier, record in checked.items():
        version = record.get("version") if isinstance(record, dict) else None
        keys = {"version", "review", "source_sha256", "registration_sha256"}
        if type(version) is int and version == 2:
            keys.add("article_registration_sha256")
        if (not isinstance(record, dict) or set(record) != keys or type(version) is not int
                or version not in {1, 2} or record["review"] != identifier or identifier not in known
                or any(not isinstance(record[k], str) or not SHA.fullmatch(record[k])
                       for k in keys - {"version", "review"})):
            raise PreflightError("invalid_checked_input_record")
    intent = checked.get(folder)
    if not intent or intent["version"] != 2:
        raise PreflightError("revalidation_required")
    tracker.tree(root / folder / "dist")
    inputs = review_inputs(root, folder, reader=tracker) if frozen else review_inputs(root, folder)
    if inputs != _tracked_review_inputs(tracker, folder, registrations[folder]):
        raise PreflightError("input_changed")
    if (inputs["source_sha256"] is None
            or any(intent[k] != inputs[k] for k in ("source_sha256", "article_registration_sha256"))):
        raise PreflightError("revalidation_required")
    if request["expectedInputs"] != inputs:
        raise PreflightError("input_conflict")
    changes = _frozen_declarations(change_documents) if frozen else declarations(root / "publication_changes")
    tracked_changes = {}
    for document in change_documents.values():
        for name, hashes in document["files"].items():
            if name in tracked_changes:
                raise PreflightError("invalid_change_declaration")
            tracked_changes[name] = hashes
    if changes != tracked_changes:
        raise PreflightError("input_changed")
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    snapshot, _, _, baseline = _validate_baseline(tracker, Path(baseline_snapshot), checked_at)
    evidence = {key: baseline[key] for key in RELEASE_KEYS}
    if (request["expectedReleaseRevision"] != baseline["releaseRevision"]
            or request["expectedReleaseEvidence"] != evidence):
        raise PreflightError("release_changed")
    record = snapshot["reviews"].get(folder)
    # Bind every registered web view. Unchanged images/attachments need not have
    # change declarations; complete artifact continuity belongs to candidate C.
    # Any existing declaration for another referenced file must still agree.
    if not record:
        raise PreflightError("revalidation_required")
    web_views = {record["href"]} | {view["href"] for view in record["translations"].values()}
    covered = web_views | (set(record["references"]) & changes.keys())
    if any(name not in changes or changes[name]["after"] != snapshot["files"][name]["content_sha256"]
           for name in covered):
        raise PreflightError("revalidation_required")
    revision, state = revision_reader(root, tracker)
    if revision is None or state == "unknown":
        raise PreflightError("source_not_verified")
    if revision != request["expectedSourceRevision"]:
        raise PreflightError("source_conflict")
    if state != "match":
        raise PreflightError("source_not_verified")
    tracker.verify()
    final_revision, final_state = revision_reader(root, tracker)
    if final_revision != revision or final_state != "match":
        raise PreflightError("input_changed")
    changed = sorted(k for k, v in request["patch"].items() if registrations[folder]["review"][k] != v)
    if capture is not None:
        capture.update(tracker=tracker, request=request, checked_at=checked_at,
                       baseline=baseline, snapshot=snapshot)
    return {"schemaVersion": 1, "ok": True, "status": "validated_preflight_only" if changed else "no_change",
            "operation": OPERATION, "sourceId": folder, "sourceRevision": revision,
            "checkedInputs": inputs, "releaseRevision": baseline["releaseRevision"],
            "releaseEvidence": evidence, "baselineOrigin": "provided_local_verified_bundle",
            "patchFields": sorted(request["patch"]), "changedFields": changed,
            "requestFingerprint": request_fingerprint(request),
            "limits": ["local_preflight_only", "not_authorization", "not_persisted", "not_published",
                       "not_live_https_verification", "not_atomic_or_durable_idempotency",
                       "attachment_continuity_requires_candidate_checks"]}


def preflight_request(source_root: Path, request_path: Path, baseline_snapshot: Path) -> dict:
    """Read explicit inputs only. Never fetch a baseline, write or run a build."""
    try:
        return _preflight(source_root, request_path, baseline_snapshot)
    except PreflightError:
        raise
    except InventoryError as error:
        raise PreflightError(error.code) from None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError, SyntaxError):
        raise PreflightError("invalid_input") from None


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise PreflightError("invalid_arguments")


def main(argv=None):
    parser = _Parser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--baseline-snapshot", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        report = preflight_request(args.root, args.request, args.baseline_snapshot)
    except PreflightError as error:
        print(json.dumps({"schemaVersion": 1, "ok": False, "reason": error.code}))
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
