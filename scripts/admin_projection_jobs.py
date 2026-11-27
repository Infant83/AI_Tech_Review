"""B2b2 first local slice: explicit bases and durable no-change receipts.

Changed requests fail closed before key reservation. This is not the complete
B2b2 candidate writer: changed Git receipts/CAS and publication remain absent.
The original B1 sandbox and B2b1 projection store formats are not extended.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid
import zlib

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import admin_candidate_import as projection
from scripts import admin_requests, admin_source_intake as intake
from scripts.admin_inventory import InventoryError, PublicReview, PublicTranslation, PublicAgent
from scripts.review_registry import validate_review_registration

FORMAT = "atrl-admin-b2b2-no-change-slice"
HEAD = b"ref: refs/heads/writer-unset\n"
CONTROL_BYTES = 65_536
EVIDENCE_BYTES = 4 * 1024 * 1024
MAX_KEYS = 128
MAX_STORE_BYTES = 512 * 1024 * 1024
MAX_STORE_FILES = 10_000
MAX_READ_BYTES = 1024 * 1024 * 1024
MAX_WRITE_BYTES = 512 * 1024 * 1024
TOTAL_SECONDS = 180
FINGERPRINT_VERSION = 1
LIMITS = ["local_no_change_slice_only", "changed_candidate_CAS_not_implemented",
          "not_source_writer", "not_published", "not_authorization", "not_live_https",
          "not_atomic_source_snapshot", "no_power_loss_guarantee"]
_raw, _sha, _json = projection._raw, projection._sha, projection._json
HEX64 = projection.HEX64


class JobError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__("Local projection job refused (" + code + ").")


def _checkpoint(stage):
    """Tests may inject faults; there is no CLI fault-injection option."""


def _version(value, field="version", expected=1):
    # Canonical JSON and dict equality do not distinguish True/1.0 from 1.
    return isinstance(value, dict) and type(value.get(field)) is int and value[field] == expected


class _Budget:
    def __init__(self):
        self.deadline = time.monotonic() + TOTAL_SECONDS
        self.read_bytes = self.write_bytes = 0

    def check(self, read=0, write=0):
        if read < 0 or write < 0:
            raise JobError("job_limit")
        self.read_bytes += read
        self.write_bytes += write
        if self.read_bytes > MAX_READ_BYTES or self.write_bytes > MAX_WRITE_BYTES:
            raise JobError("job_limit")
        if time.monotonic() > self.deadline:
            raise JobError("job_timeout")

    def read_size(self, maximum):
        self.check()
        return min(maximum, MAX_READ_BYTES + 1 - self.read_bytes)


class _Store(projection._Store):
    def reserve(self, amount, files=0):
        self.budget.check()
        if self.bytes + amount > MAX_STORE_BYTES or self.files + files > MAX_STORE_FILES:
            raise JobError("store_limit")
        if self.budget.write_bytes + amount > MAX_WRITE_BYTES:
            raise JobError("job_limit")

    def read(self, path, limit=CONTROL_BYTES):
        return super().read(path, limit)

    def write(self, path, raw):
        if len(raw) > CONTROL_BYTES:
            raise JobError("control_limit")
        with self.new(path, len(raw)) as write:
            write(raw)

    def evidence(self, path, raw):
        if len(raw) > EVIDENCE_BYTES:
            raise JobError("base_evidence_limit")
        with self.new(path, len(raw)) as write:
            write(raw)


def _separate(root, *others):
    for other in others:
        if root == other or root in other.parents or other in root.parents:
            raise JobError("unsafe_store_location")


def _key(namespace, request):
    namespace_digest = _sha(_raw(namespace))
    key = _sha(_raw({"namespaceDigest": namespace_digest, "idempotencyKey": request["idempotencyKey"]}))
    operation = _sha(_raw({"domain": "atrl-admin-b2b2-operation-v1", "keyHash": key}))
    return namespace_digest, key, operation


def _identity(store, repository_id, principal):
    expected_namespace = projection._operator(repository_id, principal)
    identity_raw = store.read("identity.json")
    identity = _json(identity_raw)
    source_raw = store.read("projection-identity.json")
    source_identity = _json(source_raw)
    if (not isinstance(identity, dict)
            or set(identity) != {"format", "version", "namespace", "writerEpoch", "projectionIdentitySha256"}
            or identity["format"] != FORMAT or type(identity["version"]) is not int
            or identity["version"] != 1 or identity["namespace"] != expected_namespace
            or identity["projectionIdentitySha256"] != _sha(source_raw)
            or not isinstance(source_identity, dict)
            or set(source_identity) != {"format", "version", "namespace", "storeEpoch", "sourceCommon"}
            or source_identity["format"] != projection.FORMAT
            or type(source_identity["version"]) is not int or source_identity["version"] != 1
            or source_identity["namespace"] != expected_namespace
            or not isinstance(source_identity["sourceCommon"], dict)
            or set(source_identity["sourceCommon"]) != {"device", "inode"}
            or any(type(v) is not int or v < 0 for v in source_identity["sourceCommon"].values())):
        raise JobError("store_inconsistent")
    projection._uuid(identity["writerEpoch"])
    projection._uuid(source_identity["storeEpoch"])
    for name, raw in [(".keep", b""), ("lock", b""), ("git/config", projection.CONFIG), ("git/HEAD", HEAD)]:
        if store.read(name) != raw:
            raise JobError("store_inconsistent")
    for name in ["git/objects", "git/refs/adopt/bases", "git/refs/adopt/operations", "bases", "inventory", "tombstones", "states"]:
        store.directory(name)
    files = store.scan()
    fixed = {".keep", "lock", "identity.json", "projection-identity.json", "git/config", "git/HEAD"}
    for name in files:
        allowed = (name in fixed
            or re.fullmatch(r"git/objects/[a-f0-9]{2}/[a-f0-9]{38}", name)
            or re.fullmatch(r"git/refs/adopt/bases/[a-f0-9]{64}", name)
            or re.fullmatch(r"bases/[a-f0-9]{64}/(?:identity|intent|mapping|success|base)\.json", name)
            or re.fullmatch(r"(?:inventory|tombstones|states)/[a-f0-9]{64}\.json", name))
        if not allowed:
            raise JobError("store_inconsistent")
    fixed_dirs = {"", "git", "git/objects", "git/refs", "git/refs/adopt", "git/refs/adopt/bases",
                  "git/refs/adopt/operations", "bases", "inventory", "tombstones", "states"}
    for name in store.dirs:
        if (name not in fixed_dirs and not re.fullmatch(r"git/objects/[a-f0-9]{2}", name)
                and not re.fullmatch(r"bases/[a-f0-9]{64}", name)):
            raise JobError("store_inconsistent")
    pins = {name.rsplit("/", 1)[1] for name in files if name.startswith("git/refs/adopt/bases/")}
    bases = {name.split("/")[1] for name in store.dirs if re.fullmatch(r"bases/[a-f0-9]{64}", name)}
    if pins - bases:
        raise JobError("store_inconsistent")
    # Even valid-looking epoch replacement cannot reopen an existing key space.
    identity_sha = _sha(identity_raw)
    for name in files:
        if name.startswith(("inventory/", "tombstones/", "states/")) or name.endswith("/base.json"):
            value = _json(store.read(name))
            if not _version(value) or value.get("identitySha256") != identity_sha:
                raise JobError("store_inconsistent")
    return identity, identity_sha, source_identity, files


def _evidence(reader, paths):
    """Bound the whole preserved bundle while reading, not after allocation."""
    result = {}; total = 0
    for name, path in paths.items():
        with reader.opened(path, projection.MAX_CONTROL_BYTES) as fd:
            if os.fstat(fd).st_size > EVIDENCE_BYTES - total:
                raise JobError("base_evidence_limit")
        raw = reader.read(path, EVIDENCE_BYTES - total)
        total += len(raw); result[name] = raw
    return result


def _base(store, identity, identity_sha, digest):
    if not isinstance(digest, str) or not HEX64.fullmatch(digest):
        raise JobError("invalid_projection_digest")
    prefix = "bases/" + digest
    if not store.exists(prefix):
        raise JobError("projection_not_staged")
    if not store.exists(prefix + "/base.json"):
        raise JobError("outcome_unknown")
    raws = _evidence(store, {name: prefix + "/" + name + ".json" for name in ["identity", "intent", "mapping", "success"]})
    evidence = _json(store.read(prefix + "/base.json"))
    if (not _version(evidence) or set(evidence) != {"format", "version", "identitySha256", "projectionDigest", "evidenceSha256"}
            or evidence != {"format": FORMAT, "version": 1, "identitySha256": identity_sha,
                            "projectionDigest": digest, "evidenceSha256": {k: _sha(v) for k, v in raws.items()}}
            or _sha(raws["identity"]) != identity["projectionIdentitySha256"]
            or raws["identity"] != store.read("projection-identity.json")):
        raise JobError("store_inconsistent")
    intent, mapping, success = (_json(raws[n]) for n in ["intent", "mapping", "success"])
    original_identity_sha = _sha(raws["identity"])
    actual, entries, tree, trees, revision, commit = projection._validate_intent(intent, original_identity_sha)
    if not _version(intent["provenance"], "schemaVersion"):
        raise JobError("store_inconsistent")
    expected_mapping = {"format": projection.FORMAT, "version": 1, "projectionDigest": digest,
        "identitySha256": original_identity_sha, "sourceOriginRevision": intent["provenance"]["sourceOriginRevision"],
        "sourceTree": intent["provenance"]["sourceTree"], "candidateBaseRevision": revision,
        "candidateTree": tree, "intentSha256": _sha(raws["intent"])}
    if (actual != digest or not _version(mapping) or mapping != expected_mapping
            or not isinstance(success, dict) or set(success) != {"format", "version", "projectionDigest", "mappingSha256", "checkedAt"}
            or success.get("format") != projection.FORMAT or type(success.get("version")) is not int or success["version"] != 1
            or success.get("projectionDigest") != digest or success.get("mappingSha256") != _sha(raws["mapping"])
            or not isinstance(success.get("checkedAt"), str)):
        raise JobError("store_inconsistent")
    projection.datetime.fromisoformat(success["checkedAt"].replace("Z", "+00:00"))
    if store.read("git/refs/adopt/bases/" + digest, 41) != (revision + "\n").encode():
        raise JobError("store_inconsistent")
    for oid, raw, kind in [(revision, commit, "commit"), *[(o, r, "tree") for o, r in trees]]:
        actual_object = projection._read_object(store, oid, collect=True)
        if actual_object["kind"] != kind or actual_object["raw"] != raw:
            raise JobError("store_inconsistent")
    for entry in entries:
        value = projection._read_object(store, entry["blob"])
        if value["kind"] != "blob" or value["bytes"] != entry["bytes"] or value["sha256"] != entry["sha256"]:
            raise JobError("store_inconsistent")
    return {"intent": intent, "mapping": mapping, "entries": entries, "evidence": evidence}


def _all_bases(store, identity, identity_sha):
    for name in sorted(store.dirs):
        if re.fullmatch(r"bases/[a-f0-9]{64}", name):
            _base(store, identity, identity_sha, name.split("/")[1])


def _registration(store, base, request, *, validate=True):
    target = "publication/reviews/" + request["sourceId"] + ".json"
    entries = [entry for entry in base["entries"] if entry["path"] == target]
    if len(entries) != 1:
        raise JobError("store_inconsistent")
    entry = entries[0]
    raw = projection._read_object(store, entry["blob"], collect=True)["raw"]
    if _sha(raw) != request["expectedInputs"]["registration_sha256"]:
        raise JobError("input_conflict")
    # Registrations need not use the control file canonical encoder.
    registration = json.loads(raw.decode("utf-8"), object_pairs_hook=admin_requests._unique,
                              parse_constant=lambda _: admin_requests._invalid())
    merged = {**registration, "review": {**registration["review"], **request["patch"]}}
    if validate:
        validate_review_registration(merged, request["sourceId"] + ".json", PublicReview, PublicTranslation, PublicAgent)
    unchanged = all(registration["review"][k] == v for k, v in request["patch"].items())
    return target, entry["sha256"], unchanged


def _claim(identity_sha, namespace_digest, key, operation, base, before, *, writer_tools):
    provenance, mapping = base["intent"]["provenance"], base["mapping"]
    return {"format": FORMAT, "version": 1, "identitySha256": identity_sha,
        "namespaceDigest": namespace_digest, "keyHash": key, "operationId": operation,
        "requestFingerprintVersion": FINGERPRINT_VERSION, "requestFingerprint": provenance["requestFingerprint"],
        "sourceId": provenance["sourceId"], "target": "publication/reviews/" + provenance["sourceId"] + ".json",
        "sourceOriginRevision": mapping["sourceOriginRevision"], "sourceTree": mapping["sourceTree"],
        "checkedInputs": provenance["checkedInputs"], "releaseRevision": provenance["releaseRevision"],
        "releaseEvidence": provenance["releaseEvidence"], "projectionDigest": mapping["projectionDigest"],
        "intentSha256": mapping["intentSha256"], "mappingSha256": _sha(_raw(mapping)),
        "candidateBaseRevision": mapping["candidateBaseRevision"], "candidateTree": mapping["candidateTree"],
        "baseEvidenceSha256": _sha(_raw(base["evidence"])), "beforeSha256": before,
        "afterSha256": before, "noChange": True,
        "projectionToolCodeSha256": base["intent"]["importerCodeSha256"],
        "writerToolCodeSha256": writer_tools}


def _tool_hashes(budget=None):
    return {**projection._tool_hashes(budget=budget),
            "scripts/admin_projection_jobs.py": _sha(intake._tool_bytes(Path(__file__).resolve(), budget))}


def _inventory(store, identity, identity_sha, files):
    names = sorted(name for name in files if name.startswith("inventory/"))
    if len(names) > MAX_KEYS:
        raise JobError("key_limit")
    found = {}
    namespace_digest = _sha(_raw(identity["namespace"]))
    for name in names:
        value = _json(store.read(name)); key = name.split("/")[1][:-5]
        operation = _sha(_raw({"domain": "atrl-admin-b2b2-operation-v1", "keyHash": key}))
        if (not _version(value) or set(value) != {"format", "version", "identitySha256", "namespaceDigest", "keyHash", "operationId", "tombstoneSha256"}
                or value != {"format": FORMAT, "version": 1, "identitySha256": identity_sha,
                    "namespaceDigest": namespace_digest, "keyHash": key, "operationId": operation,
                    "tombstoneSha256": value.get("tombstoneSha256")}
                or not isinstance(value["tombstoneSha256"], str) or not HEX64.fullmatch(value["tombstoneSha256"])):
            raise JobError("store_inconsistent")
        tombstone_path = "tombstones/" + key + ".json"
        if not store.exists(tombstone_path):
            raise JobError("outcome_unknown")
        raw = store.read(tombstone_path)
        tombstone = _json(raw)
        if (_sha(raw) != value["tombstoneSha256"] or not _version(tombstone)
                or not _version(tombstone, "requestFingerprintVersion", FINGERPRINT_VERSION)
                or tombstone.get("keyHash") != key or tombstone.get("operationId") != operation
                or tombstone.get("identitySha256") != identity_sha or tombstone.get("namespaceDigest") != namespace_digest
                or tombstone.get("noChange") is not True
                or tombstone.get("beforeSha256") != tombstone.get("afterSha256")):
            raise JobError("store_inconsistent")
        base = _base(store, identity, identity_sha, tombstone["projectionDigest"])
        expected_tools = projection._tool_paths() | {"scripts/admin_projection_jobs.py"}
        saved_tools = tombstone.get("writerToolCodeSha256")
        registration = [e for e in base["entries"] if e["path"] == "publication/reviews/" + base["intent"]["provenance"]["sourceId"] + ".json"]
        if (not isinstance(saved_tools, dict) or set(saved_tools) != expected_tools
                or any(not isinstance(v, str) or not HEX64.fullmatch(v) for v in saved_tools.values())
                or len(registration) != 1
                or tombstone != _claim(identity_sha, namespace_digest, key, operation, base,
                                      registration[0]["sha256"], writer_tools=saved_tools)):
            raise JobError("store_inconsistent")
        # No operation ref is allowed in this slice, including for no_change.
        if store.exists("git/refs/adopt/operations/" + operation):
            raise JobError("store_inconsistent")
        found[key] = tombstone
    if any(name.startswith(("tombstones/", "states/")) and name.split("/")[1][:-5] not in found for name in files):
        raise JobError("store_inconsistent")
    return found


def _advanced(source_root, source_identity, original, budget):
    if source_root is None:
        return None
    try:
        source = intake._GitSource(intake._safe(source_root), projection._SourceBudget(budget))
        if projection._common(source) != source_identity["sourceCommon"]:
            return None
        return source.revision != original
    except (OSError, ValueError, subprocess.SubprocessError):
        # A historical result survives an unavailable or unrelated source.
        budget.check()
        return None


def _report(claim, *, replay, advanced):
    return {"schemaVersion": 1, "ok": True, "status": "no_change", "replay": replay,
        "operationId": claim["operationId"], "keyHash": claim["keyHash"],
        "requestFingerprint": claim["requestFingerprint"], "projectionDigest": claim["projectionDigest"],
        "sourceOriginRevision": claim["sourceOriginRevision"], "candidateBaseRevision": claim["candidateBaseRevision"],
        "candidateTree": claim["candidateTree"], "beforeSha256": claim["beforeSha256"], "afterSha256": claim["afterSha256"],
        "candidateRevision": None, "sourceAdvanced": advanced, "attested": True, "limits": LIMITS}


def _state(store, key, claim):
    state = {"format": FORMAT, "version": 1, "identitySha256": claim["identitySha256"],
             "keyHash": key, "tombstoneSha256": _sha(_raw(claim)), "status": "no_change"}
    path = "states/" + key + ".json"
    if store.exists(path):
        actual = _json(store.read(path))
        if not _version(actual) or actual != state:
            raise JobError("store_inconsistent")
    else:
        store.write(path, _raw(state))


def _initialize(root, projection_root, source_root, baseline, repository_id, principal):
    budget = _Budget(); namespace = projection._operator(repository_id, principal)
    root, projection_root, baseline = map(intake._safe, [root, projection_root, baseline])
    source = intake._GitSource(intake._safe(source_root), projection._SourceBudget(budget))
    _separate(root, source.root, source.common, baseline.parent, projection_root)
    with _Store(root, budget, create=True) as store:
        store.write(".keep", b""); store.write("lock", b"")
        with projection._locked(store):
            with projection._Store(projection_root, budget) as original, projection._locked(original):
                original_identity, original_sha = projection._store_identity(original, repository_id, principal)
                if original_identity["sourceCommon"] != projection._common(source):
                    raise JobError("source_identity_conflict")
                original_raw = original.read("identity.json")
                if _sha(original_raw) != original_sha:
                    raise JobError("store_inconsistent")
                for name in ["git/objects", "git/refs/adopt/bases", "git/refs/adopt/operations", "bases", "inventory", "tombstones", "states"]:
                    store.directory(name, create=True)
                store.write("git/config", projection.CONFIG); store.write("git/HEAD", HEAD)
                store.write("projection-identity.json", original_raw)
                store.write("identity.json", _raw({"format": FORMAT, "version": 1, "namespace": namespace,
                    "writerEpoch": str(uuid.uuid4()), "projectionIdentitySha256": original_sha}))
                source.guard(); _identity(store, repository_id, principal)
    return {"schemaVersion": 1, "ok": True, "status": "projection_writer_initialized_local",
            "namespaceDigest": _sha(_raw(namespace)), "limits": LIMITS}


def _copy_object(original, store, oid):
    name = projection._object_path(oid)
    store.directory("git/objects/" + oid[:2], create=True)
    if store.exists(name):
        projection._read_object(store, oid)
        return
    with original.opened(name, projection.MAX_STORE_BYTES) as fd:
        size = os.fstat(fd).st_size
        with store.new(name, size) as write:
            count = 0
            while True:
                chunk = os.read(fd, store.budget.read_size(min(65536, size + 1 - count)))
                if not chunk:
                    break
                count += len(chunk); store.budget.check(read=len(chunk))
                if count > size:
                    raise JobError("store_inconsistent")
                write(chunk)
            if count != size:
                raise JobError("store_inconsistent")
    projection._read_object(store, oid)


def _stage(root, projection_root, digest, repository_id, principal):
    budget = _Budget()
    with _Store(root, budget) as store, projection._locked(store):
        identity, identity_sha, _, files = _identity(store, repository_id, principal)
        _inventory(store, identity, identity_sha, files); _all_bases(store, identity, identity_sha)
        if not isinstance(digest, str) or not HEX64.fullmatch(digest):
            raise JobError("invalid_projection_digest")
        if store.exists("bases/" + digest):
            base = _base(store, identity, identity_sha, digest)
            return {"schemaVersion": 1, "ok": True, "status": "projection_base_staged_local", "replay": True,
                    **base["mapping"], "attested": True, "limits": LIMITS}
        projection_root = intake._safe(projection_root); _separate(store.root, projection_root)
        with projection._Store(projection_root, budget) as original, projection._locked(original):
            _, original_sha = projection._store_identity(original, repository_id, principal)
            if original_sha != identity["projectionIdentitySha256"]:
                raise JobError("projection_identity_conflict")
            mapping, attested = projection._inspect_locked(original, original_sha, digest)
            if not attested:
                raise JobError("projection_not_attested")
            raws = _evidence(original, {"identity": "identity.json", **{name: "imports/" + digest + "/" + name + ".json"
                                 for name in ["intent", "mapping", "success"]}})
            intent = _json(raws["intent"])
            _, entries, _, trees, revision, _ = projection._validate_intent(intent, original_sha)
            # The B2b1 v1 mapping reader historically compared a dict, which
            # accepts bool/float as int. Refuse malformed source evidence before
            # creating any writer base/control/object/pin, preserving B2b1.
            if not _version(_json(raws["mapping"])) or not _version(intent["provenance"], "schemaVersion"):
                raise JobError("store_inconsistent")
            oids = {revision, *[oid for oid, _ in trees], *[entry["blob"] for entry in entries]}
            sizes = {}
            for oid in oids:
                with original.opened(projection._object_path(oid), projection.MAX_STORE_BYTES) as fd:
                    sizes[oid] = os.fstat(fd).st_size
            maximum = sum(sizes.values()) + sum(map(len, raws.values())) + CONTROL_BYTES + 82
            store.reserve(maximum, len(oids) * 2 + 20)
            base_prefix = "bases/" + digest; store.directory(base_prefix, create=True)
            for name, raw in raws.items():
                store.evidence(base_prefix + "/" + name + ".json", raw)
            _checkpoint("after_base_evidence")
            for oid in sorted(oids):
                _copy_object(original, store, oid)
            _checkpoint("after_base_objects")
            # Exact 41-byte immutable pin: bounded .pin temporary plus final
            # link entry, no external Git writing or unspecified temp files.
            store.pin("git/refs/adopt/bases/" + digest, (revision + "\n").encode())
            _checkpoint("after_base_pin")
            projection._verify_projection_state(original, repository_id, principal, original_sha, digest, mapping, attested=True)
            final_raws = _evidence(original, {"identity": "identity.json", **{name: "imports/" + digest + "/" + name + ".json"
                                 for name in ["intent", "mapping", "success"]}})
            if final_raws != raws:
                raise JobError("input_changed")
            if store.read("identity.json") != _raw(identity):
                raise JobError("store_inconsistent")
            store.write(base_prefix + "/base.json", _raw({"format": FORMAT, "version": 1, "identitySha256": identity_sha,
                "projectionDigest": digest, "evidenceSha256": {name: _sha(raw) for name, raw in raws.items()}}))
            _checkpoint("after_base_complete")
            final_identity, final_sha, _, _ = _identity(store, repository_id, principal)
            if final_sha != identity_sha:
                raise JobError("store_inconsistent")
            final = _base(store, final_identity, final_sha, digest)
            return {"schemaVersion": 1, "ok": True, "status": "projection_base_staged_local", "replay": False,
                    **final["mapping"], "attested": True, "limits": LIMITS}


def _apply(root, request_path, digest, source_root, baseline, repository_id, principal):
    budget = _Budget()
    incoming = intake._safe(request_path)
    payload = intake._control(incoming, admin_requests.MAX_REQUEST_BYTES, budget=projection._SourceBudget(budget))
    frozen_request = admin_requests._FrozenRequest(payload)
    request = frozen_request.value()
    with _Store(root, budget) as store, projection._locked(store):
        identity, identity_sha, source_identity, files = _identity(store, repository_id, principal)
        namespace_digest, key, operation = _key(identity["namespace"], request)
        inventory = _inventory(store, identity, identity_sha, files)
        if key in inventory:
            claim = inventory[key]
            if claim["requestFingerprint"] != admin_requests.request_fingerprint(request):
                raise JobError("idempotency_conflict")
            base = _base(store, identity, identity_sha, claim["projectionDigest"])
            _, before, unchanged = _registration(store, base, request, validate=False)
            # Stored writer tool hashes are historical evidence, not silently
            # replaced by the current installed tool version during replay.
            expected = _claim(identity_sha, namespace_digest, key, operation, base, before,
                              writer_tools=claim["writerToolCodeSha256"])
            if claim != expected or not unchanged:
                raise JobError("store_inconsistent")
            _state(store, key, claim); _checkpoint("after_state")
            final_identity, final_sha, _, final_files = _identity(store, repository_id, principal)
            if final_sha != identity_sha or _inventory(store, final_identity, final_sha, final_files).get(key) != claim:
                raise JobError("store_inconsistent")
            advanced = _advanced(source_root, source_identity, claim["sourceOriginRevision"], budget)
            final_identity, final_sha, _, final_files = _identity(store, repository_id, principal)
            if final_sha != identity_sha or _inventory(store, final_identity, final_sha, final_files).get(key) != claim:
                raise JobError("store_inconsistent")
            return _report(claim, replay=True, advanced=advanced)
        _all_bases(store, identity, identity_sha)
        base = _base(store, identity, identity_sha, digest)
        _, before, unchanged = _registration(store, base, request)
        if not unchanged:
            raise JobError("changed_candidate_not_implemented")
        if len(inventory) >= MAX_KEYS:
            raise JobError("key_limit")
        source_root, baseline = map(intake._safe, [source_root, baseline])
        _separate(store.root, source_root, baseline.parent)
        code = _tool_hashes(budget=projection._SourceBudget(budget))
        source_budget = projection._SourceBudget(budget)
        descriptor, source, tracker, source_code = intake._collect_intake(source_root, incoming, baseline, source_budget,
                                                                          frozen_request=frozen_request)
        if projection._common(source) != source_identity["sourceCommon"]:
            raise JobError("source_identity_conflict")
        _separate(store.root, source.common)
        provenance = {k: v for k, v in descriptor.items() if k not in {"checkedAt", "observedReadBytes"}}
        if (provenance != base["intent"]["provenance"] or projection._tool_hashes(budget=source_budget) != base["intent"]["importerCodeSha256"]
                or provenance["requestFingerprint"] != admin_requests.request_fingerprint(request)
                or intake._control(incoming, admin_requests.MAX_REQUEST_BYTES, budget=source_budget) != payload):
            raise JobError("projection_input_conflict")
        claim = _claim(identity_sha, namespace_digest, key, operation, base, before, writer_tools=code)
        reservation = {"format": FORMAT, "version": 1, "identitySha256": identity_sha,
            "namespaceDigest": namespace_digest, "keyHash": key, "operationId": operation,
            "tombstoneSha256": _sha(_raw(claim))}
        claim_raw, reservation_raw = _raw(claim), _raw(reservation)
        if max(len(claim_raw), len(reservation_raw)) > CONTROL_BYTES:
            raise JobError("control_limit")
        store.reserve(len(claim_raw) + len(reservation_raw) + CONTROL_BYTES, 3)
        _checkpoint("before_final_check")
        projection._final_source(source, tracker, source_code, base["intent"]["importerCodeSha256"], budget)
        if _tool_hashes(budget=source_budget) != code or intake._control(incoming, admin_requests.MAX_REQUEST_BYTES, budget=source_budget) != payload:
            raise JobError("input_changed")
        final_identity, final_sha, _, final_files = _identity(store, repository_id, principal)
        if final_identity != identity or final_sha != identity_sha:
            raise JobError("store_inconsistent")
        _inventory(store, identity, identity_sha, final_files)
        _base(store, identity, identity_sha, digest)
        try:
            # An attempted reservation may already have durable or partial
            # bytes. Later semantic failures must not look like an unaccepted
            # request that can safely be replaced with a new key.
            store.write("inventory/" + key + ".json", reservation_raw); _checkpoint("after_inventory")
            projection._final_source(source, tracker, source_code, base["intent"]["importerCodeSha256"], budget)
            if _tool_hashes(budget=source_budget) != code:
                raise JobError("tool_changed")
            if store.read("identity.json") != _raw(identity):
                raise JobError("store_inconsistent")
            _base(store, identity, identity_sha, digest)
            if store.read("inventory/" + key + ".json") != reservation_raw:
                raise JobError("store_inconsistent")
            store.write("tombstones/" + key + ".json", claim_raw); _checkpoint("after_tombstone")
            _state(store, key, claim); _checkpoint("after_state")
            final_identity, final_sha, _, final_files = _identity(store, repository_id, principal)
            if final_sha != identity_sha or _inventory(store, final_identity, final_sha, final_files).get(key) != claim:
                raise JobError("store_inconsistent")
            advanced = _advanced(source_root, source_identity, claim["sourceOriginRevision"], budget)
            final_identity, final_sha, _, final_files = _identity(store, repository_id, principal)
            if final_sha != identity_sha or _inventory(store, final_identity, final_sha, final_files).get(key) != claim:
                raise JobError("store_inconsistent")
            return _report(claim, replay=False, advanced=advanced)
        except (JobError, projection.ImportError, intake.IntakeError,
                admin_requests.PreflightError, InventoryError) as error:
            reason = "store_inconsistent" if error.code == "store_inconsistent" else "outcome_unknown"
            raise JobError(reason) from None


def _call(function, *args):
    try:
        return function(*args)
    except JobError:
        raise
    except (projection.ImportError, intake.IntakeError, admin_requests.PreflightError, InventoryError) as error:
        raise JobError(error.code) from None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError,
            subprocess.SubprocessError, zlib.error):
        raise JobError("outcome_unknown") from None


def initialize_writer(store, projection_store, source_root, baseline_snapshot, repository_id, principal):
    return _call(_initialize, store, projection_store, source_root, baseline_snapshot, repository_id, principal)


def stage_base(store, projection_store, digest, repository_id, principal):
    return _call(_stage, store, projection_store, digest, repository_id, principal)


def apply_no_change(store, request, digest, source_root, baseline_snapshot, repository_id, principal):
    return _call(_apply, store, request, digest, source_root, baseline_snapshot, repository_id, principal)


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise JobError("invalid_arguments")


def main(argv=None):
    try:
        parser = _Parser(description=__doc__)
        commands = parser.add_subparsers(dest="command", required=True)
        for name in ["init-writer", "stage-base", "apply-no-change"]:
            command = commands.add_parser(name)
            command.add_argument("--store", type=Path, required=True)
            command.add_argument("--repository-id", required=True)
            command.add_argument("--principal", required=True)
            if name in {"init-writer", "stage-base"}:
                command.add_argument("--projection-store", type=Path, required=True)
            if name != "stage-base":
                command.add_argument("--root", type=Path, required=name == "init-writer")
                command.add_argument("--baseline-snapshot", type=Path, required=name == "init-writer")
            if name != "init-writer":
                command.add_argument("--projection-digest", required=True)
            if name == "apply-no-change":
                command.add_argument("--request", type=Path, required=True)
        args = parser.parse_args(argv)
        if args.command == "init-writer":
            report = initialize_writer(args.store, args.projection_store, args.root, args.baseline_snapshot, args.repository_id, args.principal)
        elif args.command == "stage-base":
            report = stage_base(args.store, args.projection_store, args.projection_digest, args.repository_id, args.principal)
        else:
            report = apply_no_change(args.store, args.request, args.projection_digest, args.root, args.baseline_snapshot, args.repository_id, args.principal)
        raw = _raw(report)
        if len(raw) > intake.MAX_STDOUT_BYTES:
            raise JobError("stdout_limit")
        sys.stdout.buffer.write(raw); return 0
    except JobError as error:
        sys.stdout.buffer.write(_raw({"schemaVersion": 1, "ok": False, "reason": error.code})); return 1


if __name__ == "__main__":
    raise SystemExit(main())
