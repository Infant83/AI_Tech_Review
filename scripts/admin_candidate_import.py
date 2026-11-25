"""B2b1: bounded local source projections, never an editorial request writer.

Only this module writes its private standalone bare store. Git is used solely
through B2a's trusted source reader. Loose objects and immutable import pins are
written directly, so temporary and cumulative logical writes are countable.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import stat
import subprocess
import sys
import time
import uuid
import zlib

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import admin_source_intake as intake
from scripts import admin_requests
from scripts.admin_inventory import InventoryError

FORMAT = "atrl-admin-b2b1-projection"
MAX_SELECTED_FILES = 2_000
MAX_SELECTED_BYTES = 160 * 1024 * 1024
MAX_CONTROL_BYTES = 4 * 1024 * 1024
MAX_READ_BYTES = 1024 * 1024 * 1024
MAX_WRITE_BYTES = 512 * 1024 * 1024
MAX_STORE_BYTES = 512 * 1024 * 1024
MAX_STORE_FILES = 10_000
TOTAL_SECONDS = 180
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
PRINCIPAL = re.compile(r"[A-Za-z0-9_.-]{1,64}\Z")
CONFIG = (b"[core]\n\trepositoryformatversion = 0\n\tbare = true\n\tlogallrefupdates = false\n"
          b"[gc]\n\tauto = 0\n[maintenance]\n\tauto = false\n")
HEAD = b"ref: refs/heads/projection-unset\n"
COMMIT_IDENTITY = b"ATRL local projection <projection@example.invalid> 946684800 +0000"
LIMITS = ["local_projection_only", "not_editorial_request_acceptance", "not_key_replay",
          "not_source_backup", "not_published", "not_live_https", "not_authorization",
          "not_atomic_source_snapshot", "not_production_ref_CAS", "no_power_loss_guarantee"]


class ImportError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__("Local projection refused (" + code + ").")


def _checkpoint(stage):
    """Repository tests inject ordinary I/O failures; no CLI fault mechanism."""


def _raw(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8") + b"\n"


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _json(raw):
    def pairs(values):
        result = {}
        for k, v in values:
            if k in result:
                raise ImportError("store_inconsistent")
            result[k] = v
        return result
    def bad(_):
        raise ImportError("store_inconsistent")
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=bad)
    if _raw(value) != raw:
        raise ImportError("store_inconsistent")
    return value


def _uuid(value):
    if str(uuid.UUID(value)) != value:
        raise ImportError("invalid_local_identity")
    return value


def _operator(repository_id, principal):
    _uuid(repository_id)
    if not PRINCIPAL.fullmatch(principal):
        raise ImportError("invalid_local_identity")
    return {"repositoryId": repository_id, "principal": principal,
            "operation": admin_requests.OPERATION}


def _common(source):
    info = source.common.stat()
    return {"device": info.st_dev, "inode": info.st_ino}


class _Budget:
    def __init__(self):
        self.deadline = time.monotonic() + TOTAL_SECONDS
        self.read_bytes = self.write_bytes = 0

    def check(self, read=0, write=0):
        if read < 0 or write < 0:
            raise ImportError("import_limit")
        self.read_bytes += read; self.write_bytes += write
        if self.read_bytes > MAX_READ_BYTES or self.write_bytes > MAX_WRITE_BYTES:
            raise ImportError("import_limit")
        if time.monotonic() > self.deadline:
            raise ImportError("import_timeout")

    def read_size(self, maximum):
        self.check()
        return min(maximum, MAX_READ_BYTES + 1 - self.read_bytes)


class _SourceBudget(intake._Budget):
    """Keep B2a's narrower limits while charging the outer budget per read."""
    def __init__(self, outer):
        super().__init__()
        self.outer = outer
        self.deadline = min(self.deadline, outer.deadline)

    def check(self, amount=0):
        self.outer.check(read=amount)
        super().check(amount)

    def read_size(self, maximum):
        return self.outer.read_size(super().read_size(maximum))


class _Store:
    """Anchor every directory component and write only through opened dir FDs.

    The parent/operator is trusted. As in B2a, POSIX mkdir does not atomically
    identify its new inode before the first open. No shared-server claim is made.
    """
    def __init__(self, root, budget, *, create=False):
        if not intake._OUTPUT_DIR_FD_SUPPORTED:
            raise ImportError("unsupported_output_platform")
        self.root = intake._safe(root); self.budget = budget
        self.flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        self.anchors = []; self.dirs = {}; self.bytes = self.files = 0
        try:
            fd = os.open(self.root.anchor, self.flags)
            self.anchors.append((fd, self.root.anchor, None))
            self.anchors[-1] = (fd, self.root.anchor, self._identity(os.fstat(fd)))
            for name in self.root.parent.parts[1:]:
                fd = os.open(name, self.flags, dir_fd=self.anchors[-1][0])
                self.anchors.append((fd, name, None))
                self.anchors[-1] = (fd, name, self._identity(os.fstat(fd)))
            if create:
                os.mkdir(self.root.name, 0o700, dir_fd=self.anchors[-1][0])
            fd = os.open(self.root.name, self.flags, dir_fd=self.anchors[-1][0])
            self.dirs[""] = (fd, None)
            self.dirs[""] = (fd, self._identity(os.fstat(fd)))
            self.verify()
            if create and os.listdir(fd):
                raise ImportError("new_store_required")
        except BaseException:
            self.close(); raise

    @staticmethod
    def _identity(info):
        return info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode)

    def verify(self):
        self.budget.check()
        for index, (fd, name, identity) in enumerate(self.anchors):
            info = os.stat(name, dir_fd=self.anchors[index - 1][0] if index else None,
                           follow_symlinks=False)
            if self._identity(info) != identity or self._identity(os.fstat(fd)) != identity:
                raise ImportError("output_changed")
        for path, (fd, identity) in self.dirs.items():
            parent, _, leaf = path.rpartition("/")
            base = self.dirs[parent][0] if path else self.anchors[-1][0]
            info = os.stat(leaf if path else self.root.name, dir_fd=base, follow_symlinks=False)
            opened = os.fstat(fd)
            if (self._identity(info) != identity or self._identity(opened) != identity
                    or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid()
                    or stat.S_IMODE(info.st_mode) != 0o700):
                raise ImportError("output_changed")

    def directory(self, path, *, create=False):
        if path in self.dirs:
            self.verify(); return self.dirs[path][0]
        parts = PurePosixPath(path)
        if parts.is_absolute() or parts.as_posix() != path or any(p in {".", ".."} for p in parts.parts):
            raise ImportError("unsafe_store_path")
        current = ""
        for name in parts.parts:
            child = current + "/" + name if current else name
            if child not in self.dirs:
                if create:
                    self.reserve(0, 1)
                    try:
                        os.mkdir(name, 0o700, dir_fd=self.dirs[current][0])
                        self.files += 1; os.fsync(self.dirs[current][0])
                    except FileExistsError:
                        pass
                fd = os.open(name, self.flags, dir_fd=self.dirs[current][0])
                self.dirs[child] = (fd, None)
                self.dirs[child] = (fd, self._identity(os.fstat(fd)))
                self.verify()
            current = child
        return self.dirs[path][0]

    def reserve(self, amount, files=0):
        self.budget.check()
        if self.bytes + amount > MAX_STORE_BYTES or self.files + files > MAX_STORE_FILES:
            raise ImportError("store_limit")
        if self.budget.write_bytes + amount > MAX_WRITE_BYTES:
            raise ImportError("import_limit")

    @contextmanager
    def new(self, path, maximum):
        parent, _, name = path.rpartition("/")
        directory = self.directory(parent)
        self.reserve(maximum, 1); self.verify()
        fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=directory)
        self.files += 1; written = 0
        def write(raw):
            nonlocal written
            if written + len(raw) > maximum:
                raise ImportError("import_limit")
            self.reserve(len(raw)); self.budget.check(write=len(raw)); self.verify()
            view = memoryview(raw)
            while view:
                count = os.write(fd, view)
                if not count:
                    raise OSError("short output write")
                written += count; self.bytes += count; view = view[count:]
            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
            if self._identity(info) != self._identity(os.fstat(fd)):
                raise ImportError("output_changed")
        try:
            yield write
            os.fsync(fd); self.verify(); os.fsync(directory)
        finally:
            os.close(fd)

    def write(self, path, raw):
        if len(raw) > MAX_CONTROL_BYTES:
            raise ImportError("control_limit")
        with self.new(path, len(raw)) as write:
            write(raw)

    @contextmanager
    def opened(self, path, limit):
        parent, _, name = path.rpartition("/")
        directory = self.directory(parent); self.verify()
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_NONBLOCK", 0), dir_fd=directory)
        try:
            info = os.fstat(fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.geteuid()
                    or stat.S_IMODE(info.st_mode) != 0o600 or info.st_size > limit):
                raise ImportError("store_inconsistent")
            yield fd
            after = os.fstat(fd); current = os.stat(name, dir_fd=directory, follow_symlinks=False)
            if (self._identity(current) != self._identity(info)
                    or (info.st_size, info.st_mtime_ns) != (after.st_size, after.st_mtime_ns)):
                raise ImportError("output_changed")
            self.verify()
        finally:
            os.close(fd)

    def read(self, path, limit=MAX_CONTROL_BYTES):
        with self.opened(path, limit) as fd:
            raw = bytearray()
            while True:
                chunk = os.read(fd, self.budget.read_size(min(65536, limit + 1 - len(raw))))
                if not chunk:
                    break
                self.budget.check(read=len(chunk)); raw.extend(chunk)
                if len(raw) > limit:
                    raise ImportError("control_limit")
            return bytes(raw)

    def exists(self, path):
        parent, _, name = path.rpartition("/")
        directory = self.directory(parent)
        try:
            os.stat(name, dir_fd=directory, follow_symlinks=False); return True
        except FileNotFoundError:
            return False

    def pin(self, path, raw):
        parent, _, name = path.rpartition("/"); directory = self.directory(parent)
        temporary = ".pin-" + uuid.uuid4().hex
        self.write(parent + "/" + temporary, raw)
        self.reserve(len(raw), 1); self.verify()
        os.link(temporary, name, src_dir_fd=directory, dst_dir_fd=directory, follow_symlinks=False)
        self.files += 1; self.bytes += len(raw)
        self.verify(); os.fsync(directory)
        os.unlink(temporary, dir_fd=directory)
        self.files -= 1; self.bytes -= len(raw)
        os.fsync(directory); self.verify()

    def scan(self):
        self.bytes = self.files = 0
        paths = set()
        def walk(path):
            fd = self.directory(path)
            with os.scandir(fd) as entries:
                for entry in entries:
                    self.budget.check()
                    name = path + "/" + entry.name if path else entry.name
                    self.files += 1; self.reserve(0)
                    info = entry.stat(follow_symlinks=False)
                    if stat.S_ISDIR(info.st_mode):
                        walk(name)
                    elif stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
                        self.bytes += info.st_size; self.reserve(0); paths.add(name)
                    else:
                        raise ImportError("store_inconsistent")
        walk(""); self.verify(); return paths

    def close(self):
        for fd, _ in reversed(list(self.dirs.values())):
            try: os.close(fd)
            except OSError: pass
        for fd, _, _ in reversed(self.anchors):
            try: os.close(fd)
            except OSError: pass
        self.dirs = {}; self.anchors = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def _store_identity(store, repository_id, principal):
    try:
        for name in [".keep", "identity.json", "lock", "git/config", "git/HEAD"]:
            if not store.exists(name):
                raise ImportError("store_inconsistent")
        for name in ["git/objects", "git/refs/adopt/imports", "imports"]:
            store.directory(name)
        identity_raw = store.read("identity.json")
    except FileNotFoundError:
        raise ImportError("store_inconsistent") from None
    identity = _json(identity_raw)
    if (not isinstance(identity, dict) or set(identity) != {"format", "version", "namespace", "storeEpoch", "sourceCommon"}
            or identity["format"] != FORMAT or type(identity["version"]) is not int or identity["version"] != 1
            or identity["namespace"] != _operator(repository_id, principal)
            or not isinstance(identity["sourceCommon"], dict) or set(identity["sourceCommon"]) != {"device", "inode"}
            or any(type(v) is not int or v < 0 for v in identity["sourceCommon"].values())):
        raise ImportError("store_inconsistent")
    _uuid(identity["storeEpoch"])
    if store.read(".keep") != b"" or store.read("lock") != b"":
        raise ImportError("store_inconsistent")
    if store.read("git/config") != CONFIG or store.read("git/HEAD") != HEAD:
        raise ImportError("store_inconsistent")
    paths = store.scan()
    for name in paths:
        allowed = name in {".keep", "identity.json", "lock", "git/config", "git/HEAD"}
        allowed |= bool(re.fullmatch(r"git/objects/[a-f0-9]{2}/[a-f0-9]{38}", name))
        allowed |= bool(re.fullmatch(r"git/objects/\.object-[a-f0-9]{32}", name))
        allowed |= bool(re.fullmatch(r"git/refs/adopt/imports/(?:[a-f0-9]{64}|\.pin-[a-f0-9]{32})", name))
        allowed |= bool(re.fullmatch(r"imports/[a-f0-9]{64}/(?:intent|mapping|success)\.json", name))
        if not allowed:
            raise ImportError("store_inconsistent")
    # Empty foreign control directories must not bypass file-only validation.
    for name in store.dirs:
        if (name not in {"", "git", "git/objects", "git/refs", "git/refs/adopt", "git/refs/adopt/imports", "imports"}
                and not re.fullmatch(r"git/objects/[a-f0-9]{2}", name)
                and not re.fullmatch(r"imports/[a-f0-9]{64}", name)):
            raise ImportError("store_inconsistent")
    records = {name.split("/")[1] for name in store.dirs if re.fullmatch(r"imports/[a-f0-9]{64}", name)}
    for name in paths:
        if re.fullmatch(r"git/refs/adopt/imports/[a-f0-9]{64}", name):
            digest = name.rsplit("/", 1)[1]
            if digest not in records or "imports/" + digest + "/intent.json" not in paths:
                raise ImportError("store_inconsistent")
    for digest in records:
        prefix = "imports/" + digest
        if prefix + "/success.json" in paths and (prefix + "/mapping.json" not in paths
                or "git/refs/adopt/imports/" + digest not in paths):
            raise ImportError("store_inconsistent")
        # A valid-looking replacement epoch/identity must not silently fork
        # this store's existing history into a new projection namespace.
        intent_path = prefix + "/intent.json"
        if intent_path not in paths:
            raise ImportError("store_inconsistent")
        intent_raw = store.read(intent_path)
        intent = _json(intent_raw)
        if (not isinstance(intent, dict) or intent.get("identitySha256") != _sha(identity_raw)
                or intent.get("projectionDigest") != digest):
            raise ImportError("store_inconsistent")
        if prefix + "/mapping.json" in paths:
            mapping = _json(store.read(prefix + "/mapping.json"))
            if (not isinstance(mapping, dict) or mapping.get("identitySha256") != _sha(identity_raw)
                    or mapping.get("projectionDigest") != digest
                    or mapping.get("intentSha256") != _sha(intent_raw)):
                raise ImportError("store_inconsistent")
    return identity, _sha(identity_raw)


@contextmanager
def _locked(store):
    try:
        present = store.exists("lock")
    except FileNotFoundError:
        present = False
    if not present:
        raise ImportError("store_inconsistent")
    with store.opened("lock", 0) as fd:
        while True:
            store.budget.check()
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB); break
            except BlockingIOError:
                time.sleep(.025)
        try:
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)


def _tool_hashes():
    return {**intake._tool_hashes(), "scripts/admin_candidate_import.py": _sha(Path(__file__).read_bytes())}


def _read_source_blob(source, entry, budget):
    if intake.GIT is None:
        raise ImportError("trusted_git_unavailable")
    command = [intake.GIT, "--no-replace-objects", "--no-lazy-fetch", "--no-optional-locks",
               "-c", "core.hooksPath=" + os.devnull, "-c", "core.attributesFile=" + os.devnull,
               "-c", "core.fsmonitor=false", "-c", "protocol.allow=never", "-C", str(source.root),
               "cat-file", "blob", entry["blob"]]
    end = min(budget.deadline, time.monotonic() + intake.GIT_SECONDS)
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=intake._env())
    count = 0; error_bytes = 0
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ, True)
            selector.register(process.stderr, selectors.EVENT_READ, False)
            while selector.get_map():
                budget.check(); left = end - time.monotonic()
                if left <= 0:
                    raise ImportError("git_timeout")
                for key, _ in selector.select(min(.2, left)):
                    chunk = os.read(key.fileobj.fileno(), budget.read_size(65536))
                    if not chunk:
                        selector.unregister(key.fileobj); continue
                    budget.check(read=len(chunk))
                    if key.data:
                        count += len(chunk)
                        if count > entry["bytes"]:
                            raise ImportError("input_changed")
                        yield chunk
                    else:
                        error_bytes += len(chunk)
                        if error_bytes > intake.MAX_STDOUT_BYTES:
                            raise ImportError("git_output_limit")
        process.wait(timeout=max(.01, end - time.monotonic()))
        if process.returncode or count != entry["bytes"]:
            raise ImportError("git_read_failed")
    finally:
        if process.poll() is None:
            process.kill(); process.wait()
        process.stdout.close(); process.stderr.close()


def _object_path(oid):
    if not HEX40.fullmatch(oid):
        raise ImportError("store_inconsistent")
    return "git/objects/" + oid[:2] + "/" + oid[2:]


def _read_object(store, oid, *, collect=False):
    path = _object_path(oid); decoder = zlib.decompressobj()
    sha1 = hashlib.sha1(); sha256 = hashlib.sha256(); header = bytearray(); payload = bytearray()
    kind = None; expected = count = 0
    with store.opened(path, MAX_STORE_BYTES) as fd:
        while True:
            compressed = os.read(fd, store.budget.read_size(65536))
            if not compressed:
                break
            store.budget.check(read=len(compressed))
            pending = compressed
            while pending:
                raw = decoder.decompress(pending, 65536)
                pending = decoder.unconsumed_tail
                sha1.update(raw)
                if kind is None:
                    end = raw.find(b"\0")
                    if end < 0:
                        header.extend(raw)
                        if len(header) > 80:
                            raise ImportError("store_inconsistent")
                        continue
                    header.extend(raw[:end]); raw = raw[end + 1:]
                    parts = bytes(header).split(b" ")
                    if len(parts) != 2 or parts[0] not in {b"blob", b"tree", b"commit"} or not re.fullmatch(b"0|[1-9][0-9]*", parts[1]):
                        raise ImportError("store_inconsistent")
                    kind, expected = parts[0].decode(), int(parts[1])
                    if expected > (intake.MAX_BLOB_BYTES if kind == "blob" else MAX_CONTROL_BYTES):
                        raise ImportError("store_inconsistent")
                count += len(raw); sha256.update(raw)
                if count > expected:
                    raise ImportError("store_inconsistent")
                if collect:
                    if expected > MAX_CONTROL_BYTES:
                        raise ImportError("control_limit")
                    payload.extend(raw)
            if decoder.unused_data:
                raise ImportError("store_inconsistent")
    if not decoder.eof or decoder.unused_data or kind is None or count != expected or sha1.hexdigest() != oid:
        raise ImportError("store_inconsistent")
    return {"kind": kind, "bytes": count, "sha256": sha256.hexdigest(), "raw": bytes(payload) if collect else None}


def _write_object(store, kind, chunks, size, *, expected_oid=None, expected_sha=None):
    if size > (intake.MAX_BLOB_BYTES if kind == "blob" else MAX_CONTROL_BYTES):
        raise ImportError("import_limit")
    header = kind.encode() + b" " + str(size).encode() + b"\0"
    # Python's compressor receives only bounded chunks. This conservative bound
    # includes header/zlib overhead; each actual os.write is also budget checked.
    maximum = size + len(header) + (size // 1000 + 1) * 32 + 1024
    temporary = "git/objects/.object-" + uuid.uuid4().hex
    sha1 = hashlib.sha1(header); sha256 = hashlib.sha256(); count = 0
    compressor = zlib.compressobj()
    with store.new(temporary, maximum) as write:
        write(compressor.compress(header))
        for chunk in chunks:
            count += len(chunk)
            if count > size:
                raise ImportError("input_changed")
            sha1.update(chunk); sha256.update(chunk)
            write(compressor.compress(chunk))
        write(compressor.flush())
    oid = sha1.hexdigest()
    if count != size or (expected_oid is not None and oid != expected_oid) or (expected_sha is not None and sha256.hexdigest() != expected_sha):
        raise ImportError("input_changed")
    directory = store.directory("git/objects/" + oid[:2], create=True)
    source_fd = store.directory("git/objects")
    store.verify()
    try:
        info = os.stat(temporary.rsplit("/", 1)[1], dir_fd=source_fd, follow_symlinks=False)
        store.reserve(info.st_size, 1)
        os.link(temporary.rsplit("/", 1)[1], oid[2:], src_dir_fd=source_fd, dst_dir_fd=directory,
                follow_symlinks=False)
        store.files += 1; store.bytes += info.st_size; os.fsync(directory)
    except FileExistsError:
        existing = _read_object(store, oid)
        if existing["kind"] != kind or existing["bytes"] != size or existing["sha256"] != sha256.hexdigest():
            raise ImportError("store_inconsistent")
    os.unlink(temporary.rsplit("/", 1)[1], dir_fd=source_fd)
    store.files -= 1; store.bytes -= info.st_size
    os.fsync(source_fd); store.verify()
    return oid


def _trees(entries):
    root = {}
    for entry in entries:
        name = entry["path"]; path = PurePosixPath(name)
        if (path.is_absolute() or path.as_posix() != name or any(p in {".", "..", ".git"} for p in path.parts)
                or any(ord(c) < 32 for c in name) or entry["mode"] not in {"100644", "100755"}
                or not HEX40.fullmatch(entry["blob"]) or not HEX64.fullmatch(entry["sha256"])
                or type(entry["bytes"]) is not int or entry["bytes"] < 0):
            raise ImportError("invalid_projection_manifest")
        current = root
        for part in path.parts[:-1]:
            current = current.setdefault(part, {})
            if not isinstance(current, dict):
                raise ImportError("invalid_projection_manifest")
        if path.name in current:
            raise ImportError("invalid_projection_manifest")
        current[path.name] = (entry["mode"], entry["blob"])
    records = []
    def build(node):
        rows = []
        for name, value in node.items():
            if isinstance(value, dict):
                mode, oid = "40000", build(value); order = name.encode() + b"/"
            else:
                mode, oid = value; order = name.encode()
            rows.append((order, mode.encode() + b" " + name.encode() + b"\0" + bytes.fromhex(oid)))
        raw = b"".join(row for _, row in sorted(rows))
        oid = hashlib.sha1(b"tree " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        records.append((oid, raw)); return oid
    return build(root), records


def _commit(tree, digest):
    return (b"tree " + tree.encode() + b"\nauthor " + COMMIT_IDENTITY + b"\ncommitter " + COMMIT_IDENTITY
            + b"\n\n" + _raw({"format": FORMAT, "projectionDigest": digest}))


def _validate_intent(intent, identity_sha):
    if (not isinstance(intent, dict) or set(intent) != {"format", "version", "identitySha256", "provenance", "importerCodeSha256", "projectionDigest"}
            or intent["format"] != FORMAT or type(intent["version"]) is not int or intent["version"] != 1
            or intent["identitySha256"] != identity_sha or not isinstance(intent["provenance"], dict)
            or not isinstance(intent["importerCodeSha256"], dict)
            or set(intent["importerCodeSha256"]) != set(_tool_hashes())
            or any(not isinstance(value, str) or not HEX64.fullmatch(value) for value in intent["importerCodeSha256"].values())):
        raise ImportError("store_inconsistent")
    digest = _sha(_raw({"identitySha256": identity_sha, "provenance": intent["provenance"],
                       "importerCodeSha256": intent["importerCodeSha256"]}))
    if intent["projectionDigest"] != digest:
        raise ImportError("store_inconsistent")
    provenance = intent["provenance"]
    expected = {"schemaVersion", "status", "operation", "sourceId", "sourceOriginRevision", "sourceTree",
                "requestFingerprint", "checkedInputs", "releaseRevision", "releaseEvidence", "snapshotSha256",
                "inputs", "directories", "toolCodeSha256", "toolEnvironment", "counts", "limits", "intakeDigest"}
    if set(provenance) != expected or provenance["status"] != "source_intake_plan_only":
        raise ImportError("store_inconsistent")
    basis = {k: v for k, v in provenance.items() if k != "intakeDigest"}
    # B2a's canonical encoder has no final LF.
    if intake._sha(intake._raw(basis)) != provenance["intakeDigest"]:
        raise ImportError("store_inconsistent")
    entries = provenance["inputs"]
    if (not isinstance(entries, list) or not entries or len(entries) > MAX_SELECTED_FILES
            or sum(entry["bytes"] for entry in entries) > MAX_SELECTED_BYTES
            or not HEX40.fullmatch(provenance["sourceOriginRevision"]) or not HEX40.fullmatch(provenance["sourceTree"])):
        raise ImportError("store_inconsistent")
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "mode", "blob", "bytes", "sha256", "role"}:
            raise ImportError("store_inconsistent")
    tree, records = _trees(entries)
    commit = _commit(tree, digest)
    revision = hashlib.sha1(b"commit " + str(len(commit)).encode() + b"\0" + commit).hexdigest()
    return digest, entries, tree, records, revision, commit


def _inspect_locked(store, identity_sha, digest):
    if not HEX64.fullmatch(digest):
        raise ImportError("invalid_projection_digest")
    base = "imports/" + digest
    if not store.exists(base + "/intent.json"):
        raise ImportError("import_incomplete")
    intent = _json(store.read(base + "/intent.json"))
    actual, entries, tree, records, revision, commit = _validate_intent(intent, identity_sha)
    if actual != digest:
        raise ImportError("store_inconsistent")
    ref = "git/refs/adopt/imports/" + digest
    if not store.exists(ref):
        raise ImportError("store_inconsistent" if store.exists(base + "/mapping.json") else "import_incomplete")
    if store.read(ref, 41) != (revision + "\n").encode():
        raise ImportError("store_inconsistent")
    actual_commit = _read_object(store, revision, collect=True)
    if actual_commit["kind"] != "commit" or actual_commit["raw"] != commit:
        raise ImportError("store_inconsistent")
    for oid, raw in records:
        result = _read_object(store, oid, collect=True)
        if result["kind"] != "tree" or result["raw"] != raw:
            raise ImportError("store_inconsistent")
    for entry in entries:
        result = _read_object(store, entry["blob"])
        if result["kind"] != "blob" or result["bytes"] != entry["bytes"] or result["sha256"] != entry["sha256"]:
            raise ImportError("store_inconsistent")
    mapping = {"format": FORMAT, "version": 1, "projectionDigest": digest, "identitySha256": identity_sha,
               "sourceOriginRevision": intent["provenance"]["sourceOriginRevision"],
               "sourceTree": intent["provenance"]["sourceTree"], "candidateBaseRevision": revision,
               "candidateTree": tree, "intentSha256": _sha(_raw(intent))}
    if not store.exists(base + "/mapping.json") or _json(store.read(base + "/mapping.json")) != mapping:
        raise ImportError("import_incomplete")
    attested = store.exists(base + "/success.json")
    if attested:
        success = _json(store.read(base + "/success.json"))
        if (not isinstance(success, dict) or set(success) != {"format", "version", "projectionDigest", "mappingSha256", "checkedAt"}
                or success["format"] != FORMAT or type(success["version"]) is not int or success["version"] != 1 or success["projectionDigest"] != digest
                or success["mappingSha256"] != _sha(_raw(mapping)) or not isinstance(success["checkedAt"], str)):
            raise ImportError("store_inconsistent")
        datetime.fromisoformat(success["checkedAt"].replace("Z", "+00:00"))
    return mapping, attested


def _verify_projection_state(store, repository_id, principal, identity_sha, digest, mapping, *, attested):
    _, current_identity_sha = _store_identity(store, repository_id, principal)
    if current_identity_sha != identity_sha:
        raise ImportError("store_inconsistent")
    current_mapping, current_attested = _inspect_locked(store, identity_sha, digest)
    if current_mapping != mapping or current_attested != attested:
        raise ImportError("store_inconsistent")


def _final_source(source, tracker, code, importer_code, outer):
    outer.check()
    tracker.verify()
    revision, state = source.verify(source.root, tracker)
    if revision != source.revision or state != "match":
        raise ImportError("source_conflict")
    if intake._tool_hashes() != code or _tool_hashes() != importer_code:
        raise ImportError("tool_changed")


def _report(mapping, status, *, attested, source_advanced=None):
    return {"schemaVersion": 1, "ok": True, "status": status,
            "projectionDigest": mapping["projectionDigest"],
            "sourceOriginRevision": mapping["sourceOriginRevision"],
            "candidateBaseRevision": mapping["candidateBaseRevision"], "candidateTree": mapping["candidateTree"],
            "attested": attested, "sourceAdvanced": source_advanced, "limits": LIMITS}


def _initialize(root, source_root, repository_id, principal):
    budget = _Budget(); namespace = _operator(repository_id, principal)
    source_budget = _SourceBudget(budget); source = intake._GitSource(intake._safe(source_root), source_budget)
    root = intake._safe(root)
    if (root == source.root or source.root in root.parents or root in source.root.parents
            or root == source.common or source.common in root.parents or root in source.common.parents):
        raise ImportError("unsafe_store_location")
    with _Store(root, budget, create=True) as store:
        store.write(".keep", b"")
        for path in ["git", "git/objects", "git/refs/adopt/imports", "imports"]:
            store.directory(path, create=True)
        store.write("git/config", CONFIG); store.write("git/HEAD", HEAD)
        identity = {"format": FORMAT, "version": 1, "namespace": namespace,
                    "storeEpoch": str(uuid.uuid4()), "sourceCommon": _common(source)}
        store.write("identity.json", _raw(identity)); store.write("lock", b"")
        source.guard(); budget.check(); _store_identity(store, repository_id, principal)
        return {"schemaVersion": 1, "ok": True, "status": "projection_store_initialized_local",
                "namespaceDigest": _sha(_raw(namespace)), "limits": LIMITS}


def _import_inner(root, source_root, request_path, baseline, repository_id, principal, progress):
    budget = _Budget(); code = _tool_hashes()
    root, baseline = intake._safe(root), intake._safe(baseline)
    if (root == baseline.parent or root in baseline.parent.parents
            or baseline.parent in root.parents):
        raise ImportError("unsafe_store_location")
    with _Store(root, budget) as store, _locked(store):
        identity, identity_sha = _store_identity(store, repository_id, principal)
        # A prior incomplete import is not permission to switch to a new
        # projection/namespace. Inspect remains available for exact evidence.
        for path in sorted(store.dirs):
            if re.fullmatch(r"imports/[a-f0-9]{64}", path):
                if not store.exists(path + "/success.json"):
                    raise ImportError("outcome_unknown")
                # A new digest must not hide damaged historical refs/objects
                # or a success record no longer bound to its exact mapping.
                _, attested = _inspect_locked(store, identity_sha, path.split("/")[1])
                if not attested:
                    raise ImportError("outcome_unknown")
        source_budget = _SourceBudget(budget)
        descriptor, source, tracker, source_code = intake._collect_intake(
            intake._safe(source_root), intake._safe(request_path), intake._safe(baseline), source_budget)
        if _common(source) != identity["sourceCommon"]:
            raise ImportError("source_identity_conflict")
        if (store.root == source.root or store.root in source.root.parents or source.root in store.root.parents
                or store.root == source.common or store.root in source.common.parents or source.common in store.root.parents):
            raise ImportError("unsafe_store_location")
        provenance = {k: v for k, v in descriptor.items() if k not in {"checkedAt", "observedReadBytes"}}
        digest = _sha(_raw({"identitySha256": identity_sha, "provenance": provenance, "importerCodeSha256": code}))
        intent = {"format": FORMAT, "version": 1, "identitySha256": identity_sha,
                  "provenance": provenance, "importerCodeSha256": code, "projectionDigest": digest}
        digest, entries, tree, records, revision, commit = _validate_intent(intent, identity_sha)
        # Bound every object before writing any intent. Directory/ref/control
        # overhead is conservative; actual writes and total store bytes also cap.
        maximum = sum(e["bytes"] + (e["bytes"] // 1000 + 1) * 32 + 1200 for e in entries)
        maximum += sum(len(raw) + 2048 for _, raw in records) + len(commit) + MAX_CONTROL_BYTES * 3
        base = "imports/" + digest
        if base in store.dirs or store.exists("imports/" + digest):
            mapping, attested = _inspect_locked(store, identity_sha, digest)
            if not attested:
                raise ImportError("outcome_unknown")
            _final_source(source, tracker, source_code, code, budget)
            _verify_projection_state(store, repository_id, principal, identity_sha, digest, mapping, attested=True)
            return _report(mapping, "source_projection_already_present_local", attested=True, source_advanced=False)
        store.reserve(maximum, len(entries) * 2 + len(records) * 2 + 20)
        store.directory(base, create=True); store.write(base + "/intent.json", _raw(intent))
        _checkpoint("after_intent")
        for entry in entries:
            if source.objects.get(entry["path"]) != {"mode": entry["mode"], "kind": "blob", "oid": entry["blob"], "bytes": entry["bytes"]}:
                raise ImportError("input_changed")
            _write_object(store, "blob", _read_source_blob(source, entry, budget), entry["bytes"],
                          expected_oid=entry["blob"], expected_sha=entry["sha256"])
        for oid, raw in records:
            _write_object(store, "tree", [raw], len(raw), expected_oid=oid)
        _write_object(store, "commit", [commit], len(commit), expected_oid=revision)
        _checkpoint("after_objects")
        progress["pin_attempted"] = True
        store.pin("git/refs/adopt/imports/" + digest, (revision + "\n").encode())
        _checkpoint("after_pin")
        if store.read("git/refs/adopt/imports/" + digest, 41) != (revision + "\n").encode():
            raise ImportError("store_inconsistent")
        # Validate actual object bytes before writing the authoritative mapping.
        mapping = {"format": FORMAT, "version": 1, "projectionDigest": digest, "identitySha256": identity_sha,
                   "sourceOriginRevision": source.revision, "sourceTree": source.tree,
                   "candidateBaseRevision": revision, "candidateTree": tree, "intentSha256": _sha(_raw(intent))}
        for oid, raw in [(revision, commit), *records]:
            if _read_object(store, oid, collect=True)["raw"] != raw:
                raise ImportError("store_inconsistent")
        for entry in entries:
            result = _read_object(store, entry["blob"])
            if result["kind"] != "blob" or result["bytes"] != entry["bytes"] or result["sha256"] != entry["sha256"]:
                raise ImportError("store_inconsistent")
        store.write(base + "/mapping.json", _raw(mapping)); _checkpoint("after_mapping")
        _final_source(source, tracker, source_code, code, budget)
        _checkpoint("before_attestation")
        _verify_projection_state(store, repository_id, principal, identity_sha, digest, mapping, attested=False)
        store.write(base + "/success.json", _raw({"format": FORMAT, "version": 1, "projectionDigest": digest,
                    "mappingSha256": _sha(_raw(mapping)), "checkedAt": datetime.now(timezone.utc).isoformat()}))
        _checkpoint("after_attestation")
        _verify_projection_state(store, repository_id, principal, identity_sha, digest, mapping, attested=True)
        store.verify(); budget.check()
        return _report(mapping, "source_projection_saved_local", attested=True, source_advanced=False)


def _import(root, source_root, request_path, baseline, repository_id, principal):
    progress = {}
    try:
        return _import_inner(root, source_root, request_path, baseline, repository_id, principal, progress)
    except OSError:
        raise ImportError("outcome_unknown" if progress.get("pin_attempted") else "import_incomplete") from None


def _inspect(root, digest, repository_id, principal, source_root=None):
    budget = _Budget()
    with _Store(root, budget) as store, _locked(store):
        identity, identity_sha = _store_identity(store, repository_id, principal)
        mapping, attested = _inspect_locked(store, identity_sha, digest)
        advanced = None
        if source_root is not None:
            source_budget = _SourceBudget(budget); source = intake._GitSource(intake._safe(source_root), source_budget)
            if _common(source) != identity["sourceCommon"]:
                raise ImportError("source_identity_conflict")
            advanced = source.revision != mapping["sourceOriginRevision"]
        return _report(mapping, "historical_projection_present_local", attested=attested, source_advanced=advanced)


def _call(function, *args):
    try:
        return function(*args)
    except ImportError:
        raise
    except (intake.IntakeError, admin_requests.PreflightError, InventoryError) as error:
        raise ImportError(error.code) from None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError,
            subprocess.SubprocessError, zlib.error):
        raise ImportError("import_incomplete") from None


def initialize_store(store, source_root, repository_id, principal):
    return _call(_initialize, store, source_root, repository_id, principal)


def import_projection(store, source_root, request, baseline, repository_id, principal):
    return _call(_import, store, source_root, request, baseline, repository_id, principal)


def inspect_projection(store, digest, repository_id, principal, source_root=None):
    return _call(_inspect, store, digest, repository_id, principal, source_root)


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ImportError("invalid_arguments")


def main(argv=None):
    try:
        parser = _Parser(description=__doc__)
        commands = parser.add_subparsers(dest="command", required=True)
        for name in ["init-store", "import", "inspect"]:
            command = commands.add_parser(name)
            command.add_argument("--store", type=Path, required=True)
            command.add_argument("--repository-id", required=True)
            command.add_argument("--principal", required=True)
            command.add_argument("--root", type=Path, required=name != "inspect")
            if name == "import":
                command.add_argument("--request", type=Path, required=True)
                command.add_argument("--baseline-snapshot", type=Path, required=True)
            if name == "inspect":
                command.add_argument("--projection-digest", required=True)
        args = parser.parse_args(argv)
        if args.command == "init-store":
            report = initialize_store(args.store, args.root, args.repository_id, args.principal)
        elif args.command == "import":
            report = import_projection(args.store, args.root, args.request, args.baseline_snapshot, args.repository_id, args.principal)
        else:
            report = inspect_projection(args.store, args.projection_digest, args.repository_id, args.principal, args.root)
        raw = _raw(report)
        if len(raw) > intake.MAX_STDOUT_BYTES:
            raise ImportError("stdout_limit")
        sys.stdout.buffer.write(raw); return 0
    except ImportError as error:
        sys.stdout.buffer.write(_raw({"schemaVersion": 1, "ok": False, "reason": error.code})); return 1


if __name__ == "__main__":
    raise SystemExit(main())
