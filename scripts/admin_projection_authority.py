"""Bounded read-only observation of the existing local no-change writer.

This inspector neither accepts a request nor establishes history continuity.
It reads only the existing writer store and its own installed code. No source,
baseline, live projection store, Git process, repair, or ref writer is used.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import time
import zlib

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import admin_candidate_import as projection
from scripts import admin_projection_jobs as jobs
from scripts import admin_requests

CONTROL_BYTES = 65_536
EVIDENCE_BYTES = 4 * 1024 * 1024
MAX_READ_BYTES = 1024 * 1024 * 1024
MAX_STORE_BYTES = 512 * 1024 * 1024
MAX_STORE_FILES = 10_000
MAX_KEYS = 128
TOTAL_SECONDS = 180
MAX_STDOUT_BYTES = 16 * 1024
LIMITS = ["current_local_self_consistency_only", "history_continuity_not_established",
          "not_authorization", "not_source_freshness", "not_source_snapshot",
          "unreferenced_object_payloads_not_validated", "cooperating_local_flock_only",
          "changed_writer_not_implemented", "native_two_ref_gate_unfulfilled",
          "not_published", "not_live_https", "no_power_loss_guarantee"]
REASONS = frozenset({"invalid_arguments", "invalid_local_identity", "unsupported_output_platform",
                     "store_inconsistent", "outcome_unknown", "observation_changed", "job_limit",
                     "job_timeout", "store_limit", "control_limit", "base_evidence_limit",
                     "key_limit", "stdout_limit"})
_raw, _sha = projection._raw, projection._sha


class AuthorityError(ValueError):
    """A fixed public reason without native exception text or operator input."""

    def __init__(self, code):
        self.code = code if code in REASONS else "outcome_unknown"
        super().__init__("Local writer authority observation refused (" + self.code + ").")


def _checkpoint(stage):
    """Tests may inject faults; no CLI injection or continuation option exists."""


def _json(raw):
    try:
        return projection._json(raw)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise AuthorityError("store_inconsistent") from None


class _Budget:
    def __init__(self):
        self.deadline = time.monotonic() + TOTAL_SECONDS
        self.read_bytes = 0

    def check(self, read=0):
        if type(read) is not int or read < 0:
            raise AuthorityError("job_limit")
        self.read_bytes += read
        if self.read_bytes > MAX_READ_BYTES:
            raise AuthorityError("job_limit")
        if time.monotonic() > self.deadline:
            raise AuthorityError("job_timeout")

    def read_size(self, maximum):
        self.check()
        return min(maximum, MAX_READ_BYTES + 1 - self.read_bytes)


def _metadata(info):
    # atime is deliberately excluded: ordinary reads may update it.
    return (info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode), stat.S_IMODE(info.st_mode),
            info.st_uid, info.st_nlink, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


class _Store(projection._Store):
    """Existing FD-anchored store, with every consumed byte in one read budget.

    Unreferenced loose objects are scanned for allowed type/owner/mode/size and
    membership only. Their payload bytes are not read or certified by a digest.
    """

    def __init__(self, root, budget):
        self.controls = {}
        self.objects = {}
        self.control_limits = {}
        self.read_metadata = {}
        super().__init__(root, budget, create=False)

    def reserve(self, amount, files=0):
        self.budget.check()
        if self.bytes + amount > MAX_STORE_BYTES or self.files + files > MAX_STORE_FILES:
            raise AuthorityError("store_limit")

    def directory(self, path, *, create=False):
        if create:
            raise AuthorityError("store_inconsistent")
        return super().directory(path, create=False)

    def write(self, *args, **kwargs):
        raise AuthorityError("store_inconsistent")

    evidence = new = pin = write

    @contextmanager
    def opened(self, path, limit):
        with super().opened(path, limit) as fd:
            before = _metadata(os.fstat(fd))
            if path == "lock":
                # The existing lock is an empty file. No byte read is omitted.
                self._control_record(path, b"", 0, before)
            yield fd
            parent, _, leaf = path.rpartition("/")
            current = os.stat(leaf, dir_fd=self.directory(parent), follow_symlinks=False)
            if before != _metadata(os.fstat(fd)) or before != _metadata(current):
                raise AuthorityError("observation_changed")

    def _control_record(self, path, raw, limit, metadata):
        record = {"path": path, "bytes": len(raw), "rawSha256": _sha(raw), "mode": metadata[3]}
        if path in self.controls and (self.controls[path] != record or self.read_metadata[path] != metadata):
            raise AuthorityError("observation_changed")
        self.controls[path] = record
        self.control_limits[path] = min(limit, self.control_limits.get(path, limit))
        self.read_metadata[path] = metadata

    def read(self, path, limit=CONTROL_BYTES):
        raw = bytearray()
        with self.opened(path, limit) as fd:
            metadata = _metadata(os.fstat(fd))
            while True:
                chunk = os.read(fd, self.budget.read_size(min(65_536, limit + 1 - len(raw))))
                self.budget.check(read=len(chunk))
                if not chunk:
                    break
                raw.extend(chunk)
                if len(raw) > limit:
                    raise AuthorityError("control_limit")
            if len(raw) != metadata[6]:
                raise AuthorityError("observation_changed")
        value = bytes(raw)
        self._control_record(path, value, limit, metadata)
        return value

    def membership(self):
        paths = self.scan()
        result = {}
        for path in sorted(self.dirs):
            self.budget.check()
            result[("directory", path)] = _metadata(os.fstat(self.directory(path)))
        for path in sorted(paths):
            self.budget.check()
            parent, _, leaf = path.rpartition("/")
            info = os.stat(leaf, dir_fd=self.directory(parent), follow_symlinks=False)
            if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                    or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o600):
                raise AuthorityError("store_inconsistent")
            result[("file", path)] = _metadata(info)
        self.verify()
        return paths, result


def _code(budget):
    """The inspector's own file has the same small per-file/shared read limits."""
    budget.check()
    path = Path(__file__).absolute()
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0)
                 | getattr(os, "O_CLOEXEC", 0))
    try:
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or before.st_uid != os.geteuid() or before.st_size > CONTROL_BYTES):
            raise AuthorityError("control_limit")
        raw = bytearray()
        while True:
            chunk = os.read(fd, budget.read_size(min(65_536, CONTROL_BYTES + 1 - len(raw))))
            budget.check(read=len(chunk))
            if not chunk:
                break
            raw.extend(chunk)
            if len(raw) > CONTROL_BYTES:
                raise AuthorityError("control_limit")
        metadata = _metadata(before)
        if (len(raw) != before.st_size or metadata != _metadata(os.fstat(fd))
                or metadata != _metadata(os.stat(path, follow_symlinks=False))):
            raise AuthorityError("observation_changed")
        return {"path": "inspector", "bytes": len(raw), "rawSha256": _sha(raw),
                "mode": stat.S_IMODE(before.st_mode)}, metadata
    finally:
        os.close(fd)


def _layout(store, paths):
    fixed = {".keep", "lock", "identity.json", "projection-identity.json", "git/config", "git/HEAD"}
    for path in paths:
        if not (path in fixed or re.fullmatch(r"git/objects/[a-f0-9]{2}/[a-f0-9]{38}", path)
                or re.fullmatch(r"git/refs/adopt/bases/[a-f0-9]{64}", path)
                or re.fullmatch(r"bases/[a-f0-9]{64}/(?:identity|intent|mapping|success|base)\.json", path)
                or re.fullmatch(r"(?:inventory|tombstones|states)/[a-f0-9]{64}\.json", path)):
            raise AuthorityError("store_inconsistent")
    directories = {"", "git", "git/objects", "git/refs", "git/refs/adopt", "git/refs/adopt/bases",
                   "git/refs/adopt/operations", "bases", "inventory", "tombstones", "states"}
    for path in store.dirs:
        if (path not in directories and not re.fullmatch(r"git/objects/[a-f0-9]{2}", path)
                and not re.fullmatch(r"bases/[a-f0-9]{64}", path)):
            raise AuthorityError("store_inconsistent")
    if not fixed <= paths or not directories <= store.dirs.keys():
        raise AuthorityError("store_inconsistent")
    bases = {path.split("/")[1] for path in store.dirs if re.fullmatch(r"bases/[a-f0-9]{64}", path)}
    pins = {path.rsplit("/", 1)[1] for path in paths if path.startswith("git/refs/adopt/bases/")}
    if pins - bases:
        raise AuthorityError("store_inconsistent")
    return bases


def _identity(store, repository_id, principal):
    namespace = projection._operator(repository_id, principal)
    raw = store.read("identity.json")
    identity = _json(raw)
    source_raw = store.read("projection-identity.json")
    original = _json(source_raw)
    if (not jobs._version(identity)
            or set(identity) != {"format", "version", "namespace", "writerEpoch", "projectionIdentitySha256"}
            or identity["format"] != jobs.FORMAT or identity["namespace"] != namespace
            or identity["projectionIdentitySha256"] != _sha(source_raw)
            or not jobs._version(original)
            or set(original) != {"format", "version", "namespace", "storeEpoch", "sourceCommon"}
            or original["format"] != projection.FORMAT or original["namespace"] != namespace
            or not isinstance(original["sourceCommon"], dict)
            or set(original["sourceCommon"]) != {"device", "inode"}
            or any(type(v) is not int or v < 0 for v in original["sourceCommon"].values())):
        raise AuthorityError("store_inconsistent")
    try:
        projection._uuid(identity["writerEpoch"])
        projection._uuid(original["storeEpoch"])
    except (ValueError, TypeError, AttributeError):
        raise AuthorityError("store_inconsistent") from None
    for path, expected in [(".keep", b""), ("lock", b""),
                           ("git/config", projection.CONFIG), ("git/HEAD", jobs.HEAD)]:
        if store.read(path) != expected:
            raise AuthorityError("store_inconsistent")
    return identity, _sha(raw)


def _object(store, oid, *, collect=False, tree_modes=()):
    """One bounded compressed stream supplies both raw and Git payload hashes."""
    path = projection._object_path(oid)
    decoder = zlib.decompressobj()
    storage_sha = hashlib.sha256()
    git_sha = hashlib.sha1()
    payload_sha = hashlib.sha256()
    storage_bytes = count = expected = 0
    header, payload = bytearray(), bytearray()
    kind = None
    with store.opened(path, MAX_STORE_BYTES) as fd:
        metadata = _metadata(os.fstat(fd))
        while True:
            compressed = os.read(fd, store.budget.read_size(65_536))
            store.budget.check(read=len(compressed))
            if not compressed:
                break
            storage_bytes += len(compressed)
            if storage_bytes > metadata[6] or storage_bytes > MAX_STORE_BYTES:
                raise AuthorityError("observation_changed")
            storage_sha.update(compressed)
            pending = compressed
            while pending:
                store.budget.check()
                raw = decoder.decompress(pending, 65_536)
                pending = decoder.unconsumed_tail
                git_sha.update(raw)
                if kind is None:
                    end = raw.find(b"\0")
                    if end < 0:
                        header.extend(raw)
                        if len(header) > 80:
                            raise AuthorityError("store_inconsistent")
                        continue
                    header.extend(raw[:end])
                    raw = raw[end + 1:]
                    parts = bytes(header).split(b" ")
                    if (len(header) > 80 or len(parts) != 2 or parts[0] not in {b"blob", b"tree", b"commit"}
                            or not re.fullmatch(b"0|[1-9][0-9]*", parts[1])):
                        raise AuthorityError("store_inconsistent")
                    kind, expected = parts[0].decode("ascii"), int(parts[1])
                    ceiling = projection.intake.MAX_BLOB_BYTES if kind == "blob" else EVIDENCE_BYTES
                    if expected > ceiling or collect and expected > EVIDENCE_BYTES:
                        raise AuthorityError("control_limit")
                count += len(raw)
                if count > expected:
                    raise AuthorityError("store_inconsistent")
                payload_sha.update(raw)
                if collect:
                    payload.extend(raw)
            if decoder.unused_data:
                raise AuthorityError("store_inconsistent")
        if storage_bytes != metadata[6]:
            raise AuthorityError("observation_changed")
    if (not decoder.eof or decoder.unused_data or kind is None or count != expected
            or git_sha.hexdigest() != oid):
        raise AuthorityError("store_inconsistent")
    previous = store.objects.get(path)
    modes = set(tree_modes)
    if previous:
        modes.update(previous["treeEntryModes"])
    record = {"path": path, "storageBytes": storage_bytes, "storageSha256": storage_sha.hexdigest(),
              "mode": metadata[3], "gitKind": kind, "gitOid": oid,
              "payloadBytes": count, "payloadSha256": payload_sha.hexdigest(),
              "treeEntryModes": sorted(modes)}
    if previous and (any(previous[k] != record[k] for k in record if k != "treeEntryModes")
                     or store.read_metadata[path] != metadata):
        raise AuthorityError("observation_changed")
    store.objects[path] = record
    store.read_metadata[path] = metadata
    return {"kind": kind, "bytes": count, "sha256": payload_sha.hexdigest(),
            "raw": bytes(payload) if collect else None}


def _hash_map(value, keys):
    return (isinstance(value, dict) and set(value) == keys
            and all(isinstance(item, str) and projection.HEX64.fullmatch(item) for item in value.values()))


def _relative_path(value, *, root=False):
    if not isinstance(value, str) or not value or any(ord(c) < 32 for c in value):
        return False
    if root and value == ".":
        return True
    path = PurePosixPath(value)
    return (not path.is_absolute() and path.as_posix() == value
            and bool(path.parts) and not any(part in {".", "..", ".git"} for part in path.parts))


def _provenance(value, budget):
    """Check the known v1 schema, not the truth of a past source/environment.

    Rehashing an impossible field type does not make valid local evidence. All
    hashes remain historical values: no installed tool hash or live input is
    substituted. Only counts derivable from preserved inputs are exact here.
    """
    fields = {"schemaVersion", "status", "operation", "sourceId", "sourceOriginRevision", "sourceTree",
              "requestFingerprint", "checkedInputs", "releaseRevision", "releaseEvidence", "snapshotSha256",
              "inputs", "directories", "toolCodeSha256", "toolEnvironment", "counts", "limits", "intakeDigest"}
    if (not jobs._version(value, "schemaVersion") or set(value) != fields
            or value["status"] != "source_intake_plan_only" or value["operation"] != admin_requests.OPERATION
            or not isinstance(value["sourceId"], str) or not admin_requests.SOURCE_ID.fullmatch(value["sourceId"])
            or any(not isinstance(value[name], str) or not projection.HEX40.fullmatch(value[name])
                   for name in ("sourceOriginRevision", "sourceTree", "releaseRevision"))
            or any(not isinstance(value[name], str) or not projection.HEX64.fullmatch(value[name])
                   for name in ("requestFingerprint", "snapshotSha256", "intakeDigest"))
            or not _hash_map(value["checkedInputs"], admin_requests.INPUT_KEYS)
            or not _hash_map(value["releaseEvidence"], admin_requests.RELEASE_KEYS)
            or not _hash_map(value["toolCodeSha256"], projection.intake._tool_paths())):
        raise AuthorityError("store_inconsistent")
    environment = value["toolEnvironment"]
    if (not isinstance(environment, dict) or set(environment) != {"python", "git"}
            or any(not isinstance(item, str) or not item for item in environment.values())):
        raise AuthorityError("store_inconsistent")
    entries = value["inputs"]
    if not isinstance(entries, list) or not entries or len(entries) > projection.MAX_SELECTED_FILES:
        raise AuthorityError("store_inconsistent")
    seen = set()
    total = dist_bytes = dist_files = 0
    prefix = value["sourceId"] + "/dist/"
    for entry in entries:
        budget.check()
        if (not isinstance(entry, dict) or set(entry) != {"path", "mode", "blob", "bytes", "sha256", "role"}
                or not _relative_path(entry["path"]) or entry["path"] in seen
                or not isinstance(entry["mode"], str) or entry["mode"] not in {"100644", "100755"}
                or not isinstance(entry["blob"], str) or not projection.HEX40.fullmatch(entry["blob"])
                or not isinstance(entry["sha256"], str) or not projection.HEX64.fullmatch(entry["sha256"])
                or type(entry["bytes"]) is not int or not 0 <= entry["bytes"] <= projection.intake.MAX_BLOB_BYTES
                or entry["role"] != ("target_dist" if entry["path"].startswith(prefix) else "registration_or_model")):
            raise AuthorityError("store_inconsistent")
        seen.add(entry["path"])
        total += entry["bytes"]
        if entry["role"] == "target_dist":
            dist_files += 1
            dist_bytes += entry["bytes"]
    counts = value["counts"]
    if (not isinstance(counts, dict)
            or set(counts) != {"treeEntries", "selectedFiles", "selectedBytes", "distFiles", "distBytes"}
            or any(type(item) is not int or item < 0 for item in counts.values())
            or counts["selectedFiles"] != len(entries) or counts["selectedBytes"] != total
            or total > projection.MAX_SELECTED_BYTES
            or not len(entries) <= counts["treeEntries"] <= projection.intake.MAX_TREE_ENTRIES
            or not dist_files <= counts["distFiles"] <= projection.intake.MAX_DIST_FILES
            or not dist_bytes <= counts["distBytes"] <= projection.intake.MAX_DIST_BYTES):
        raise AuthorityError("store_inconsistent")
    # dist_files can also contain a request/baseline read below dist with
    # source=False, omitted from inputs. Do not invent exact past dist totals.
    directories = value["directories"]
    if not isinstance(directories, list) or len(directories) > projection.intake.MAX_TREE_ENTRIES:
        raise AuthorityError("store_inconsistent")
    seen = set()
    for directory in directories:
        budget.check()
        if (not isinstance(directory, dict) or set(directory) != {"path", "members"}
                or not _relative_path(directory["path"], root=True) or directory["path"] in seen):
            raise AuthorityError("store_inconsistent")
        seen.add(directory["path"])
        members = directory["members"]
        if members is not None and (not isinstance(members, list)
                or any(not isinstance(name, str) or not name or name in {".", ".."}
                       or "/" in name for name in members)
                or len(set(members)) != len(members)):
            raise AuthorityError("store_inconsistent")
    if (not isinstance(value["limits"], list)
            or any(not isinstance(item, str) or not item for item in value["limits"])):
        raise AuthorityError("store_inconsistent")


def _base(store, identity, identity_sha, digest):
    prefix = "bases/" + digest
    if not store.exists(prefix + "/base.json"):
        raise AuthorityError("outcome_unknown")
    raws, total = {}, 0
    for name in ("identity", "intent", "mapping", "success"):
        path = prefix + "/" + name + ".json"
        # A configured bundle cap is a limit refusal, not corrupt evidence.
        # This FD is metadata-only; the one bounded read below supplies all
        # consumed bytes, semantic values, and raw readset evidence.
        with store.opened(path, projection.MAX_CONTROL_BYTES) as fd:
            if os.fstat(fd).st_size > EVIDENCE_BYTES - total:
                raise AuthorityError("base_evidence_limit")
        raw = store.read(path, EVIDENCE_BYTES - total)
        total += len(raw)
        if total > EVIDENCE_BYTES:
            raise AuthorityError("base_evidence_limit")
        raws[name] = raw
    evidence = _json(store.read(prefix + "/base.json"))
    if (not jobs._version(evidence)
            or evidence != {"format": jobs.FORMAT, "version": 1, "identitySha256": identity_sha,
                            "projectionDigest": digest, "evidenceSha256": {k: _sha(v) for k, v in raws.items()}}
            or _sha(raws["identity"]) != identity["projectionIdentitySha256"]
            or raws["identity"] != store.read("projection-identity.json")):
        raise AuthorityError("store_inconsistent")
    intent, mapping, success = (_json(raws[n]) for n in ("intent", "mapping", "success"))
    if not isinstance(intent, dict):
        raise AuthorityError("store_inconsistent")
    _provenance(intent.get("provenance"), store.budget)
    original_sha = _sha(raws["identity"])
    store.budget.check()
    actual, entries, tree, trees, revision, commit = projection._validate_intent(intent, original_sha)
    store.budget.check()
    if not jobs._version(intent["provenance"], "schemaVersion"):
        raise AuthorityError("store_inconsistent")
    expected_mapping = {"format": projection.FORMAT, "version": 1, "projectionDigest": digest,
        "identitySha256": original_sha, "sourceOriginRevision": intent["provenance"]["sourceOriginRevision"],
        "sourceTree": intent["provenance"]["sourceTree"], "candidateBaseRevision": revision,
        "candidateTree": tree, "intentSha256": _sha(raws["intent"])}
    if (actual != digest or not jobs._version(mapping) or mapping != expected_mapping
            or not jobs._version(success)
            or set(success) != {"format", "version", "projectionDigest", "mappingSha256", "checkedAt"}
            or success["format"] != projection.FORMAT or success["projectionDigest"] != digest
            or success["mappingSha256"] != _sha(raws["mapping"])
            or not isinstance(success["checkedAt"], str)):
        raise AuthorityError("store_inconsistent")
    projection.datetime.fromisoformat(success["checkedAt"].replace("Z", "+00:00"))
    if store.read("git/refs/adopt/bases/" + digest, 41) != (revision + "\n").encode():
        raise AuthorityError("store_inconsistent")
    for oid, raw, kind in [(revision, commit, "commit"), *[(o, r, "tree") for o, r in trees]]:
        value = _object(store, oid, collect=True,
                        tree_modes=("40000",) if kind == "tree" and oid != tree else ())
        if value["kind"] != kind or value["raw"] != raw:
            raise AuthorityError("store_inconsistent")
    for entry in entries:
        value = _object(store, entry["blob"], tree_modes=(entry["mode"],))
        if value["kind"] != "blob" or value["bytes"] != entry["bytes"] or value["sha256"] != entry["sha256"]:
            raise AuthorityError("store_inconsistent")
    return {"intent": intent, "mapping": mapping, "entries": entries, "evidence": evidence}


def _inventory(store, identity, identity_sha, paths, bases):
    names = sorted(path for path in paths if path.startswith("inventory/"))
    if len(names) > MAX_KEYS:
        raise AuthorityError("key_limit")
    namespace_digest = _sha(_raw(identity["namespace"]))
    found, missing = set(), []
    present = 0
    for path in names:
        key = path.split("/")[1][:-5]
        operation = _sha(_raw({"domain": "atrl-admin-b2b2-operation-v1", "keyHash": key}))
        reservation = _json(store.read(path))
        if (not jobs._version(reservation)
                or reservation != {"format": jobs.FORMAT, "version": 1, "identitySha256": identity_sha,
                    "namespaceDigest": namespace_digest, "keyHash": key, "operationId": operation,
                    "tombstoneSha256": reservation.get("tombstoneSha256")}
                or not isinstance(reservation["tombstoneSha256"], str)
                or not projection.HEX64.fullmatch(reservation["tombstoneSha256"])):
            raise AuthorityError("store_inconsistent")
        tombstone_path = "tombstones/" + key + ".json"
        if tombstone_path not in paths:
            raise AuthorityError("outcome_unknown")
        raw = store.read(tombstone_path)
        claim = _json(raw)
        if (not jobs._version(claim) or not jobs._version(claim, "requestFingerprintVersion")
                or _sha(raw) != reservation["tombstoneSha256"]
                or claim.get("keyHash") != key or claim.get("operationId") != operation
                or claim.get("identitySha256") != identity_sha or claim.get("namespaceDigest") != namespace_digest
                or claim.get("noChange") is not True or claim.get("beforeSha256") != claim.get("afterSha256")):
            raise AuthorityError("store_inconsistent")
        base = bases.get(claim.get("projectionDigest"))
        if base is None:
            raise AuthorityError("store_inconsistent")
        saved_tools = claim.get("writerToolCodeSha256")
        tool_paths = projection._tool_paths() | {"scripts/admin_projection_jobs.py"}
        registration = [e for e in base["entries"] if e["path"] == "publication/reviews/"
                        + base["intent"]["provenance"]["sourceId"] + ".json"]
        if (not isinstance(saved_tools, dict) or set(saved_tools) != tool_paths
                or any(not isinstance(v, str) or not projection.HEX64.fullmatch(v) for v in saved_tools.values())
                or len(registration) != 1
                or claim != jobs._claim(identity_sha, namespace_digest, key, operation, base,
                                        registration[0]["sha256"], writer_tools=saved_tools)):
            raise AuthorityError("store_inconsistent")
        state_path = "states/" + key + ".json"
        if state_path in paths:
            expected = {"format": jobs.FORMAT, "version": 1, "identitySha256": identity_sha,
                        "keyHash": key, "tombstoneSha256": _sha(_raw(claim)), "status": "no_change"}
            state = _json(store.read(state_path))
            if not jobs._version(state) or state != expected:
                raise AuthorityError("store_inconsistent")
            present += 1
        else:
            missing.append(state_path)
        found.add(key)
    if any(path.startswith(("tombstones/", "states/")) and path.split("/")[1][:-5] not in found for path in paths):
        raise AuthorityError("store_inconsistent")
    return len(found), present, sorted(missing)


def _final_readset(store, membership, code, code_metadata, budget):
    for path in sorted(store.controls):
        store.read(path, store.control_limits[path])
    for path in sorted(store.objects):
        record = store.objects[path]
        _object(store, record["gitOid"], tree_modes=record["treeEntryModes"])
    _checkpoint("after_final_readset")
    _checkpoint("before_lock_exit")
    final_code, final_metadata = _code(budget)
    if final_code != code or final_metadata != code_metadata:
        raise AuthorityError("observation_changed")
    _, final_membership = store.membership()
    if membership != final_membership:
        raise AuthorityError("observation_changed")
    store.verify()
    budget.check()


def _observe(root, repository_id, principal, budget):
    # Validate operator syntax without reading any operator-supplied source.
    try:
        projection._operator(repository_id, principal)
    except (ValueError, TypeError, AttributeError):
        raise AuthorityError("invalid_local_identity") from None
    code, code_metadata = _code(budget)
    with _Store(root, budget) as store:
        with projection._locked(store):
            paths, membership = store.membership()
            _checkpoint("after_initial_scan")
            base_names = _layout(store, paths)
            identity, identity_sha = _identity(store, repository_id, principal)
            bases = {digest: _base(store, identity, identity_sha, digest) for digest in sorted(base_names)}
            completed, present, missing = _inventory(store, identity, identity_sha, paths, bases)
            _checkpoint("after_authority")
            _checkpoint("before_final_readset")
            _final_readset(store, membership, code, code_metadata, budget)
            digest_basis = {"domain": "atrl-admin-authority-observation-readset-v1", "version": 1,
                "controls": [store.controls[path] for path in sorted(store.controls)],
                "objects": [store.objects[path] for path in sorted(store.objects)],
                "missingStates": missing, "inspector": code}
            evidence_digest = _sha(_raw(digest_basis))
        # In particular, the existing lock's opened-FD exit must succeed first.
        _checkpoint("after_lock_exit")
        budget.check()
    budget.check()
    return {"schemaVersion": 1, "ok": True, "status": "writer_authority_observed_local",
        "storeFormat": jobs.FORMAT, "identitySha256": identity_sha,
        "namespaceDigest": _sha(_raw(identity["namespace"])), "observedEvidenceDigest": evidence_digest,
        "inspectorCodeSha256": code["rawSha256"], "stagedBaseCount": len(bases),
        "completedNoChangeCount": completed, "presentDerivedStateCount": present,
        "missingDerivedStateCount": len(missing), "observedReadBytes": budget.read_bytes,
        "sourceAdvanced": None, "continuityEstablished": False, "limits": list(LIMITS)}


def _call(store, repository_id, principal, budget):
    try:
        return _observe(store, repository_id, principal, budget)
    except AuthorityError:
        raise
    except (projection.ImportError, jobs.JobError) as error:
        code = {"output_changed": "observation_changed"}.get(error.code, error.code)
        raise AuthorityError(code) from None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError, zlib.error):
        raise AuthorityError("outcome_unknown") from None


def observe_writer_authority(store, repository_id, principal):
    """Return a local observation only after the original lock exits normally."""
    return _call(store, repository_id, principal, _Budget())


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise AuthorityError("invalid_arguments")


def _emit(raw, budget=None):
    """Unbuffered output: no pending Python buffer can reflush on shutdown."""
    try:
        fd = sys.stdout.fileno()
        offset = 0
        while offset < len(raw):
            if budget is not None:
                budget.check()
            count = os.write(fd, raw[offset:])
            if type(count) is not int or count <= 0 or count > len(raw) - offset:
                return False
            offset += count
        if budget is not None:
            budget.check()
        return True
    except (OSError, ValueError, AttributeError):
        return False


def main(argv=None):
    budget = _Budget()
    try:
        parser = _Parser(description=__doc__, add_help=False, allow_abbrev=False)
        parser.add_argument("--store", type=Path, required=True)
        parser.add_argument("--repository-id", required=True)
        parser.add_argument("--principal", required=True)
        args = parser.parse_args(argv)
        report = _call(args.store, args.repository_id, args.principal, budget)
        raw = _raw(report)
        if len(raw) > MAX_STDOUT_BYTES:
            raise AuthorityError("stdout_limit")
        budget.check()
    except AuthorityError as error:
        raw = _raw({"schemaVersion": 1, "ok": False, "reason": error.code})
        _emit(raw)
        return 1
    return 0 if _emit(raw, budget) else 1


if __name__ == "__main__":
    raise SystemExit(main())
