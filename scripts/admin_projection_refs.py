"""Experimental, internal FD-relative single-ref publisher for local writers.

The expected-value comparison is serialized by the existing persistent flock.
Rename is atomic for ONE ref; this is not native Git two-ref CAS, protection
against noncooperating same-UID writers, or source/publication authorization.
No current writer CLI imports this module. Identity, history and exact objects
must be validated by a future caller under the same lock before using it.
"""
from contextlib import contextmanager
import os
import re
import stat

from scripts import admin_candidate_import as projection

OID = re.compile(r"[a-f0-9]{40}\Z")
DIGEST = re.compile(r"[a-f0-9]{64}\Z")
DIRECTORY = "git/refs/adopt/operations"
REF_BYTES = 41


class RefError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__("Local operation reference refused (" + code + ").")


class _Token:
    def __init__(self, store):
        self.store, self.pid, self.active = store, os.getpid(), True
        # Returned write() counts, not physical disk I/O or fsync durability.
        self.actual_ref_payload_bytes = 0
        self.rename_attempted = False


@contextmanager
def locked_refs(store):
    """Use the original store lock inode; not an authorization capability."""
    token = None
    try:
        with projection._locked(store):
            token = _Token(store)
            try:
                yield token
            finally:
                token.active = False
    except (OSError, ValueError) as error:
        # Unlock and lock-file/anchor revalidation can fail AFTER publish_ref
        # returns, including when a caller handled an inner refusal already.
        if token is not None and token.rename_attempted:
            raise RefError("outcome_unknown") from None
        if isinstance(error, RefError):
            raise
        code = getattr(error, "code", None)
        if isinstance(code, str) and code in {"import_limit", "import_timeout", "store_limit",
                "store_inconsistent", "output_changed", "job_limit", "job_timeout"}:
            raise RefError(code) from None
        raise RefError("ref_io") from None


def _checkpoint(stage):
    """Only own-fixture tests inject faults. There is no CLI injection path."""


def _validate_oid(value):
    return isinstance(value, str) and OID.fullmatch(value) and value != "0" * 40


def _guard(store, base_path, base_raw, operation_path, expected_raw):
    store.verify()
    if store.read(base_path, REF_BYTES) != base_raw:
        raise RefError("store_inconsistent")
    current = store.read(operation_path, REF_BYTES) if store.exists(operation_path) else None
    if current != expected_raw:
        raise RefError("ref_conflict")


def _write_temporary(token, directory, name, raw):
    """Bound each syscall BEFORE it, charge its returned count afterwards."""
    store = token.store
    store.reserve(len(raw), 1)
    store.verify()
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o600, dir_fd=directory)
    store.files += 1
    try:
        original = os.fstat(fd)
        view = memoryview(raw)
        while view:
            store.reserve(len(view))
            store.verify()
            count = os.write(fd, view)
            if count <= 0 or count > len(view):
                raise OSError("invalid local write count")
            token.actual_ref_payload_bytes += count
            store.bytes += count
            store.budget.check(write=count)
            view = view[count:]
            current = os.stat(name, dir_fd=directory, follow_symlinks=False)
            opened = os.fstat(fd)
            if (store._identity(current) != store._identity(original)
                    or store._identity(opened) != store._identity(original)
                    or not stat.S_ISREG(current.st_mode) or current.st_nlink != 1
                    or current.st_uid != os.geteuid() or stat.S_IMODE(current.st_mode) != 0o600):
                raise RefError("store_inconsistent")
        os.fsync(fd)
        store.verify()
        os.fsync(directory)
    finally:
        os.close(fd)


def publish_ref(token, *, base_digest, base_oid, operation, expected_oid, new_oid):
    """Compare under the cooperating writer lock, then replace one loose ref.

    Pre-temp refusal changes nothing. A partial temp is preserved/refused;
    rename-attempt or later failure is unknown. This function does not recover
    a receipt, remove partial files, accept keys, initialize stores or run Git.
    """
    if (not isinstance(token, _Token) or not token.active or token.pid != os.getpid()):
        raise RefError("writer_lock_required")
    if os.name != "posix" or os.rename not in os.supports_dir_fd:
        raise RefError("unsupported_ref_platform")
    if (not isinstance(base_digest, str) or not DIGEST.fullmatch(base_digest)
            or not isinstance(operation, str) or not DIGEST.fullmatch(operation)
            or not _validate_oid(base_oid) or not _validate_oid(new_oid)
            or (expected_oid is not None and not _validate_oid(expected_oid))
            or expected_oid == new_oid):
        raise RefError("invalid_ref_arguments")
    store = token.store
    base_path = "git/refs/adopt/bases/" + base_digest
    operation_path = DIRECTORY + "/" + operation
    temporary = DIRECTORY + "/.pending-" + operation
    base_raw, new_raw = [(value + "\n").encode("ascii") for value in (base_oid, new_oid)]
    expected_raw = None if expected_oid is None else (expected_oid + "\n").encode("ascii")
    temp_attempted = rename_attempted = False
    try:
        files = store.scan()
        if any(path.startswith(DIRECTORY + "/.pending-") for path in files | store.dirs.keys()):
            raise RefError("ref_incomplete")
        directory = store.directory(DIRECTORY)
        _guard(store, base_path, base_raw, operation_path, expected_raw)
        # One extra entry and at most 41 payload bytes coexist with old ref.
        store.reserve(REF_BYTES, 1)
        _checkpoint("before_temp")
        temp_attempted = True
        _write_temporary(token, directory, ".pending-" + operation, new_raw)
        _checkpoint("after_temp")
        _guard(store, base_path, base_raw, operation_path, expected_raw)
        if store.read(temporary, REF_BYTES) != new_raw:
            raise RefError("store_inconsistent")
        _checkpoint("before_rename")
        # No pathname-based child process. Both names use the SAME pinned FD.
        # A noncooperating writer can still race the comparison and rename.
        rename_attempted = True
        token.rename_attempted = True
        os.rename(".pending-" + operation, operation,
                  src_dir_fd=directory, dst_dir_fd=directory)
        if expected_raw is not None:
            store.files -= 1
            store.bytes -= REF_BYTES
        _checkpoint("after_rename")
        os.fsync(directory)
        _guard(store, base_path, base_raw, operation_path, new_raw)
        _checkpoint("before_response")
        store.verify()
        return {"status": "operation_ref_replaced_local", "before": expected_oid,
                "after": new_oid, "refPayloadBytesWritten": REF_BYTES,
                "nativeGitTransaction": False}
    except (OSError, ValueError) as error:
        if rename_attempted:
            raise RefError("outcome_unknown") from None
        if temp_attempted:
            raise RefError("ref_incomplete") from None
        if isinstance(error, RefError):
            raise
        # Both projection.ImportError and writer.JobError are ValueError with
        # safe codes. Do not import the writer or add a circular dependency.
        code = getattr(error, "code", None)
        if isinstance(code, str) and code in {"import_limit", "import_timeout", "store_limit", "store_inconsistent",
                    "output_changed", "job_limit", "job_timeout", "unsupported_output_platform"}:
            raise RefError(code) from None
        raise RefError("ref_io") from None
