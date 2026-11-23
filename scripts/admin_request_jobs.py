"""B1 synthetic standalone Git candidates. No production writer or server API.

Only init-fixture creates a sandbox. apply never initializes missing state.
Immutable key claims reserve identity; Git receipts prove candidate contents;
mutable state files are derived views. No journal contains editorial values.
"""
from __future__ import annotations

import argparse
import configparser
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import uuid

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.admin_requests import (parse_request, request_fingerprint, PreflightError,
                                    MAX_REQUEST_BYTES, OPERATION)
from scripts.admin_inventory import PublicReview, PublicTranslation, PublicAgent
from scripts.publication_intent import review_inputs
from scripts.publication_lock import publication_lock
from scripts.review_registry import validate_review_registration

FORMAT = "atrl-admin-b1-synthetic"
FOLDER = "2026-11-21_b1-synthetic-review"
PREFIX = "refs/atrl-admin-b1/"
ZERO = "0" * 40
HEX = re.compile(r"[a-f0-9]{64}\Z")
SHA1 = re.compile(r"[a-f0-9]{40}\Z")
MAX_JOBS = 128
MAX_FILES = 3_000
MAX_BYTES = 16_000_000
CONTROL_BYTES = 65_536


def _trusted_git():
    for name, cellar in [("/usr/local/bin/git", "/usr/local/Cellar/git"),
                         ("/opt/homebrew/bin/git", "/opt/homebrew/Cellar/git"),
                         ("/usr/bin/git", None)]:
        try:
            candidate = Path(name).resolve(strict=True)
            if cellar is not None and Path(cellar) not in candidate.parents:
                continue
            if cellar is None and candidate != Path(name):
                continue
            info = candidate.stat()
            if (stat.S_ISREG(info.st_mode) and info.st_mode & 0o111
                    and not info.st_mode & 0o022 and os.access(candidate, os.X_OK)):
                return str(candidate)
        except OSError:
            continue
    return None


GIT = _trusted_git()


class JobError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__("Local synthetic job failed (" + code + ").")


def _checkpoint(stage):
    """Tests inject process termination/I/O failures here; no CLI fault option."""


def _raw(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8") + b"\n"


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _path(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise JobError("unsafe_path")
    return path


def _read(path, limit=CONTROL_BYTES):
    path = _path(path)
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > limit:
        raise JobError("invalid_local_input")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as handle:
        opened = os.fstat(handle.fileno())
        raw = handle.read(limit + 1)
        after = os.fstat(handle.fileno())
    if (len(raw) > limit or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
            or (opened.st_ino, opened.st_size, opened.st_mtime_ns)
            != (after.st_ino, after.st_size, after.st_mtime_ns) or len(raw) != opened.st_size):
        raise JobError("input_changed")
    return raw


def _pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise JobError("invalid_local_input")
        value[key] = item
    return value


def _json(raw):
    def invalid(_):
        raise JobError("invalid_local_input")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=invalid)


def _sync_directory(path):
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _new(path, raw):
    _path(path)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    _sync_directory(path.parent)


def _replace(path, raw):
    _path(path)
    if path.exists():
        _read(path)
    pending = path.parent / (".pending-" + uuid.uuid4().hex)
    try:
        _new(pending, raw)
        os.replace(pending, path)
        _sync_directory(path.parent)
    finally:
        pending.unlink(missing_ok=True)


def _env():
    # Both our plumbing and the A child lose inherited Git/config/replace hooks.
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "PYTHON"))}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_SYSTEM=os.devnull, GIT_CONFIG_GLOBAL=os.devnull,
               GIT_ATTR_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0", GIT_NO_REPLACE_OBJECTS="1",
               GIT_OPTIONAL_LOCKS="0", GIT_ALLOW_PROTOCOL="", PATH=os.defpath,
               GIT_AUTHOR_NAME="B1 synthetic fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="B1 synthetic fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
               GIT_AUTHOR_DATE="2000-01-01T00:00:00+0000", GIT_COMMITTER_DATE="2000-01-01T00:00:00+0000")
    settings = [("core.hooksPath", os.devnull), ("core.attributesFile", os.devnull),
                ("commit.gpgSign", "false"), ("core.fsmonitor", "false"),
                ("core.logAllRefUpdates", "false"), ("protocol.allow", "never")]
    env["GIT_CONFIG_COUNT"] = str(len(settings))
    for i, (key, value) in enumerate(settings):
        env["GIT_CONFIG_KEY_" + str(i)] = key
        env["GIT_CONFIG_VALUE_" + str(i)] = value
    return env


def _git(repo, *args, raw=None, missing=False):
    if GIT is None:
        raise JobError("trusted_git_unavailable")
    result = subprocess.run([GIT, "--no-replace-objects", "-C", str(repo), *args], input=raw,
                            capture_output=True, env=_env(), timeout=20)
    if len(result.stdout) > MAX_BYTES or len(result.stderr) > CONTROL_BYTES:
        raise JobError("git_output_limit")
    if result.returncode:
        if missing:
            return None
        raise JobError("git_operation_failed")
    return result.stdout


def _scan(root):
    count = total = 0
    for path in root.rglob("*"):
        _path(path)
        info = path.stat()
        if not stat.S_ISDIR(info.st_mode) and not stat.S_ISREG(info.st_mode):
            raise JobError("unsafe_sandbox")
        if path.is_file():
            count += 1; total += info.st_size
            if info.st_nlink != 1 or count > MAX_FILES or total > MAX_BYTES:
                raise JobError("sandbox_limit")
        if path.name in {".gitattributes", ".gitmodules"}:
            raise JobError("unsafe_sandbox")


def _sandbox(root):
    root = _path(root)
    if not root.is_dir() or not (root / ".keep").is_file():
        raise JobError("sandbox_not_initialized")
    marker_raw = _read(root / "sandbox.json")
    marker = _json(marker_raw)
    if (not isinstance(marker, dict) or set(marker) != {"format", "version", "sandboxId", "principal", "sourceId", "rootSha256"}
            or marker["format"] != FORMAT or type(marker["version"]) is not int or marker["version"] != 1
            or str(uuid.UUID(marker["sandboxId"])) != marker["sandboxId"]
            or marker["principal"] != "trusted-local-synthetic" or marker["sourceId"] != FOLDER
            or marker["rootSha256"] != _sha(str(root).encode())):
        raise JobError("unsafe_sandbox")
    repo, store = root / "repo", root / "store"
    if not (repo / ".git").is_dir():
        raise JobError("shared_git_rejected")
    gitdir = repo / ".git"
    for name in ["HEAD", "objects", "refs", "refs/heads", "refs/heads/main", "packed-refs"]:
        _path(gitdir / name)
    if _read(gitdir / "HEAD") != b"ref: refs/heads/main\n":
        raise JobError("shared_git_rejected")
    # Reject local include/command settings before the first Git process can
    # parse them. This first fixture supports only Git init's simple core INI.
    config = configparser.RawConfigParser(strict=True)
    try:
        config.read_string(_read(gitdir / "config").decode("utf-8"))
        allowed_core = {"repositoryformatversion", "filemode", "bare", "logallrefupdates", "ignorecase", "precomposeunicode"}
        if (config.sections() != ["core"] or config.defaults()
                or set(config["core"]) - allowed_core or config["core"].get("repositoryformatversion") != "0"
                or config["core"].get("bare") != "false"
                or any(value not in {"0", "true", "false"} for value in config["core"].values())):
            raise JobError("unsafe_git_config")
    except (configparser.Error, UnicodeError):
        raise JobError("unsafe_git_config") from None
    if (_git(repo, "rev-parse", "--show-toplevel").decode().strip() != str(repo)
            or _git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip() != str(gitdir)
            or _git(repo, "symbolic-ref", "HEAD").decode().strip() != "refs/heads/main"
            or _read(gitdir / "b1-sandbox-id") != (marker["sandboxId"] + "\n").encode()):
        raise JobError("shared_git_rejected")
    forbidden = ["commondir", "config.worktree", "objects/info/alternates", "info/grafts", "info/attributes", "shallow", "worktrees", "modules"]
    if any(_path(gitdir / name).exists() for name in forbidden):
        raise JobError("unsafe_sandbox")
    if (gitdir / "hooks").exists() and any((gitdir / "hooks").iterdir()):
        raise JobError("unsafe_sandbox")
    if (gitdir / "refs/replace").exists() and any((gitdir / "refs/replace").rglob("*")):
        raise JobError("unsafe_sandbox")
    allowed = {"core.repositoryformatversion", "core.filemode", "core.bare", "core.logallrefupdates", "core.ignorecase", "core.precomposeunicode"}
    for row in _git(repo, "config", "--local", "--no-includes", "--null", "--list").split(b"\0"):
        if row and row.split(b"\n", 1)[0].decode().lower() not in allowed:
            raise JobError("unsafe_git_config")
    identity = _json(_read(store / "identity.json"))
    if identity != {"version": 1, "sandboxId": marker["sandboxId"], "markerSha256": _sha(marker_raw)}:
        raise JobError("store_inconsistent")
    if not (store / "claims").is_dir() or not (store / "states").is_dir():
        raise JobError("store_inconsistent")
    _read(store / "lock")
    return root, repo, store, marker


def _source_tree(repo):
    main = _ref(repo, "refs/heads/main")
    if main is None:
        raise JobError("store_inconsistent")
    rows = _git(repo, "ls-tree", "-r", "-z", main).split(b"\0")
    if len(rows) > MAX_FILES + 1:
        raise JobError("sandbox_limit")
    for row in rows:
        if row:
            meta, name = row.split(b"\t", 1)
            if meta.split()[0] not in {b"100644", b"100755"} or name.split(b"/")[-1] in {b".gitattributes", b".gitmodules"}:
                raise JobError("unsafe_sandbox")


def _ref(repo, name):
    raw = _git(repo, "show-ref", "--verify", "--hash", name, missing=True)
    if raw is None:
        return None
    value = raw.decode().strip()
    if not SHA1.fullmatch(value):
        raise JobError("store_inconsistent")
    return value


def _blob(repo, revision, name):
    oid = _git(repo, "rev-parse", revision + ":" + name).decode().strip()
    if not SHA1.fullmatch(oid) or int(_git(repo, "cat-file", "-s", oid)) > 5_000_000:
        raise JobError("invalid_git_object")
    return _git(repo, "cat-file", "blob", oid)


def _tree(repo, files):
    grouped = {}
    for path, raw in files.items():
        first, sep, rest = path.partition("/")
        grouped.setdefault(first, {})[rest if sep else ""] = raw
    rows = []
    for name, values in grouped.items():
        if "" in values:
            oid = _git(repo, "hash-object", "--no-filters", "-w", "--stdin", raw=values[""]).strip()
            mode = b"100644 blob "
        else:
            oid = _tree(repo, values).encode(); mode = b"040000 tree "
        rows.append(mode + oid + b"\t" + name.encode() + b"\0")
    return _git(repo, "mktree", "-z", raw=b"".join(rows)).decode().strip()


def _changed_tree(repo, tree, parts, blob):
    rows = _git(repo, "ls-tree", "-z", tree).split(b"\0")
    replaced = []
    found = False
    for row in rows:
        if not row:
            continue
        meta, name = row.split(b"\t", 1)
        if name == parts[0].encode():
            mode, kind, oid = meta.split()
            if len(parts) == 1:
                if mode != b"100644" or kind != b"blob":
                    raise JobError("unsupported_scope")
                meta = b"100644 blob " + blob.encode()
            else:
                if kind != b"tree":
                    raise JobError("unsupported_scope")
                child = _changed_tree(repo, oid.decode(), parts[1:], blob)
                meta = b"040000 tree " + child.encode()
            found = True
        replaced.append(meta + b"\t" + name + b"\0")
    if not found:
        raise JobError("unsupported_scope")
    return _git(repo, "mktree", "-z", raw=b"".join(replaced)).decode().strip()


def _commit(repo, tree, metadata, parent=None):
    args = ["commit-tree", tree]
    if parent:
        args.extend(["-p", parent])
    value = _git(repo, *args, raw=_raw(metadata)).decode().strip()
    if not SHA1.fullmatch(value):
        raise JobError("invalid_git_object")
    return value


def _expected_tree_oid(repo, tree, parts, blob):
    """Compute the exact replacement tree in memory; replay writes no objects."""
    raw = _git(repo, "cat-file", "tree", tree)
    rows, position, found = [], 0, False
    while position < len(raw):
        space = raw.index(b" ", position)
        end = raw.index(b"\0", space + 1)
        mode, name = raw[position:space], raw[space + 1:end]
        oid = raw[end + 1:end + 21]
        if len(oid) != 20:
            raise JobError("store_inconsistent")
        if name == parts[0].encode():
            if len(parts) == 1:
                if mode != b"100644":
                    raise JobError("store_inconsistent")
                oid = bytes.fromhex(blob)
            else:
                if mode != b"40000":
                    raise JobError("store_inconsistent")
                oid = bytes.fromhex(_expected_tree_oid(repo, oid.hex(), parts[1:], blob))
            found = True
        rows.append(mode + b" " + name + b"\0" + oid)
        position = end + 21
    if not found:
        raise JobError("store_inconsistent")
    replaced = b"".join(rows)
    return hashlib.sha1(b"tree " + str(len(replaced)).encode() + b"\0" + replaced).hexdigest()


def _cas(repo, ref, new, old, base):
    script = f"start\nverify refs/heads/main {base}\nupdate {ref} {new} {old}\nprepare\ncommit\n".encode()
    try:
        _git(repo, "update-ref", "--stdin", raw=script)
    except (OSError, subprocess.SubprocessError):
        # A lost response cannot establish whether the transaction committed.
        raise JobError("outcome_unknown") from None
    except JobError:
        try:
            current = _ref(repo, "refs/heads/main")
        except (JobError, OSError, subprocess.SubprocessError):
            raise JobError("outcome_unknown") from None
        if current != base:
            raise JobError("source_conflict") from None
        raise JobError("outcome_unknown") from None


def _inventory(repo, store, marker):
    value = _json(_read(store / "inventory.json"))
    if (not isinstance(value, dict) or set(value) != {"version", "sandboxId", "keys"}
            or type(value["version"]) is not int or value["version"] != 1
            or value["sandboxId"] != marker["sandboxId"] or not isinstance(value["keys"], dict)
            or len(value["keys"]) > MAX_JOBS
            or any(not HEX.fullmatch(k) or not isinstance(v, str) or not HEX.fullmatch(v) for k, v in value["keys"].items())):
        raise JobError("store_inconsistent")
    claims = {}
    for key, checksum in value["keys"].items():
        path = store / "claims" / (key + ".json")
        if not path.exists():
            raise JobError("outcome_unknown")
        raw = _read(path)
        if _sha(raw) != checksum:
            raise JobError("store_inconsistent")
        claim = _json(raw)
        fields = {"version", "sandboxId", "principalScope", "keyHash", "operationId", "requestFingerprint",
                  "baseRevision", "sourceId", "target", "beforeSha256", "afterSha256", "noChange"}
        if (not isinstance(claim, dict) or set(claim) != fields or type(claim["version"]) is not int or claim["version"] != 1
                or claim["sandboxId"] != marker["sandboxId"] or claim["principalScope"] != _sha(marker["principal"].encode())
                or claim["keyHash"] != key or claim["operationId"] != _sha(b"operation\0" + key.encode())
                or any(not isinstance(claim[k], str) or not HEX.fullmatch(claim[k])
                       for k in ["requestFingerprint", "beforeSha256", "afterSha256"])
                or not isinstance(claim["baseRevision"], str) or not SHA1.fullmatch(claim["baseRevision"])
                or claim["sourceId"] != FOLDER or claim["target"] != "publication/reviews/" + FOLDER + ".json"
                or type(claim["noChange"]) is not bool
                or (claim["noChange"] and claim["beforeSha256"] != claim["afterSha256"])):
            raise JobError("store_inconsistent")
        claims[key] = claim
    if {p.name for p in (store / "claims").iterdir()} != {key + ".json" for key in claims}:
        raise JobError("store_inconsistent")
    if any(p.name not in {key + ".json" for key in claims} for p in (store / "states").iterdir()):
        raise JobError("store_inconsistent")
    refs = _git(repo, "for-each-ref", "--format=%(refname)", PREFIX).decode().splitlines()
    if any(name[len(PREFIX):] not in claims for name in refs):
        raise JobError("outcome_unknown")
    return value, claims


def _metadata(claim, phase):
    return {**claim, "format": FORMAT, "phase": phase}


def _receipt(repo, ref, claim):
    revision = _ref(repo, ref)
    if revision is None:
        raise JobError("outcome_unknown")
    # cat-file's explicit type and rev-parse peel tags; bind the ref itself.
    if _git(repo, "cat-file", "-t", revision).strip() != b"commit":
        raise JobError("store_inconsistent")
    raw = _git(repo, "cat-file", "commit", revision)
    if len(raw) > CONTROL_BYTES:
        raise JobError("store_inconsistent")
    header, sep, message = raw.partition(b"\n\n")
    metadata = _json(message)
    phase = metadata.get("phase") if isinstance(metadata, dict) else None
    if not sep or phase not in {"claimed", "candidate_saved_local"} or metadata != _metadata(claim, phase):
        raise JobError("store_inconsistent")
    parents = [row[7:].decode() for row in header.splitlines() if row.startswith(b"parent ")]
    if parents != [claim["baseRevision"]]:
        raise JobError("store_inconsistent")
    if phase == "claimed":
        if _git(repo, "rev-parse", revision + "^{tree}") != _git(repo, "rev-parse", claim["baseRevision"] + "^{tree}"):
            raise JobError("store_inconsistent")
    else:
        after = _blob(repo, revision, claim["target"])
        blob = hashlib.sha1(b"blob " + str(len(after)).encode() + b"\0" + after).hexdigest()
        base_tree = _git(repo, "rev-parse", claim["baseRevision"] + "^{tree}").decode().strip()
        expected = _expected_tree_oid(repo, base_tree, claim["target"].split("/"), blob)
        actual = _git(repo, "rev-parse", revision + "^{tree}").decode().strip()
        if expected != actual:
            raise JobError("store_inconsistent")
        paths = _git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", claim["baseRevision"], revision).split(b"\0")
        if paths != [claim["target"].encode(), b""] or _sha(after) != claim["afterSha256"]:
            raise JobError("store_inconsistent")
        if _sha(_blob(repo, claim["baseRevision"], claim["target"])) != claim["beforeSha256"]:
            raise JobError("store_inconsistent")
        for point in [revision, claim["baseRevision"]]:
            entry = _git(repo, "ls-tree", "-z", point, "--", claim["target"])
            if not entry.startswith(b"100644 blob "):
                raise JobError("store_inconsistent")
    return phase, revision


def _report(repo, claim, revision, replay):
    return {"schemaVersion": 1, "ok": True, "status": "no_change" if claim["noChange"] else "candidate_saved_local",
            "operationId": claim["operationId"], "requestFingerprint": claim["requestFingerprint"],
            "candidateRevision": revision, "replay": replay,
            "sourceAdvanced": _ref(repo, "refs/heads/main") != claim["baseRevision"],
            "limits": ["synthetic_standalone_only", "trusted_local_not_server_authorization", "not_published",
                       "not_production_ref_cas", "no_build_or_attachment_continuity", "no_power_loss_guarantee"]}


def _state(store, key, report):
    try:
        _checkpoint("before_state")
        _replace(store / "states" / (key + ".json"), _raw(report))
    except OSError:
        raise JobError("outcome_unknown") from None


def _preflight(root, request_path, baseline, request):
    result = subprocess.run([sys.executable, "-I", "-B", str(Path(__file__).with_name("admin_requests.py")),
                             "--root", str(root), "--request", str(request_path), "--baseline-snapshot", str(baseline)],
                            capture_output=True, env=_env(), timeout=30)
    if len(result.stdout) > CONTROL_BYTES or result.stderr:
        raise JobError("preflight_failed")
    report = _json(result.stdout)
    if result.returncode or report.get("ok") is not True:
        raise JobError(report.get("reason", "preflight_failed"))
    if (report.get("requestFingerprint") != request_fingerprint(request)
            or report.get("sourceRevision") != request["expectedSourceRevision"]
            or report.get("checkedInputs") != request["expectedInputs"]
            or report.get("releaseRevision") != request["expectedReleaseRevision"]
            or report.get("releaseEvidence") != request["expectedReleaseEvidence"]):
        raise JobError("input_changed")
    return report


def _run_job(sandbox, request_path, baseline):
    root, repo, store, marker = _sandbox(sandbox)
    request_path, baseline = _path(request_path), _path(baseline)
    request = parse_request(_read(request_path, MAX_REQUEST_BYTES))
    fingerprint = request_fingerprint(request)
    principal = _sha(marker["principal"].encode())
    key = _sha(_raw([marker["sandboxId"], principal, OPERATION, request["idempotencyKey"]]))
    operation = _sha(b"operation\0" + key.encode())
    lock_inode = (store / "lock").stat().st_ino
    with publication_lock(store / "lock"):
        if (store / "lock").stat().st_ino != lock_inode:
            raise JobError("store_inconsistent")
        # Other cooperating jobs create/rename Git objects and state files.
        # Scan mutable directories only after acquiring this shared store lock.
        _scan(root)
        _source_tree(repo)
        inventory, claims = _inventory(repo, store, marker)
        claim = claims.get(key)
        fresh = claim is None
        ref = PREFIX + key
        if claim is not None:
            if (not isinstance(claim, dict) or claim.get("operationId") != operation
                    or claim.get("sandboxId") != marker["sandboxId"] or claim.get("principalScope") != principal
                    or claim.get("keyHash") != key):
                raise JobError("store_inconsistent")
            if claim.get("requestFingerprint") != fingerprint:
                raise JobError("idempotency_conflict")
            if claim["noChange"]:
                if _ref(repo, ref) is not None:
                    raise JobError("store_inconsistent")
                original = _blob(repo, claim["baseRevision"], claim["target"])
                if (_sha(original) != claim["beforeSha256"]
                        or any(_json(original)["review"].get(k) != v for k, v in request["patch"].items())):
                    raise JobError("store_inconsistent")
                report = _report(repo, claim, None, True)
                _state(store, key, report)
                return report
            phase, revision = _receipt(repo, ref, claim)
            if phase == "candidate_saved_local":
                report = _report(repo, claim, revision, True)
                _state(store, key, report)
                return report
        if request["sourceId"] != marker["sourceId"]:
            raise JobError("unsupported_scope")
        report_a = _preflight(repo, request_path, baseline, request)
        base = request["expectedSourceRevision"]
        target = "publication/reviews/" + request["sourceId"] + ".json"
        before = _blob(repo, base, target)
        if _sha(before) != report_a["checkedInputs"]["registration_sha256"]:
            raise JobError("input_changed")
        registration = _json(before)
        merged = {**registration, "review": {**registration["review"], **request["patch"]}}
        validate_review_registration(merged, request["sourceId"] + ".json", PublicReview, PublicTranslation, PublicAgent)
        no_change = report_a["status"] == "no_change"
        after = before if no_change else _raw(merged)
        proposed = {"version": 1, "sandboxId": marker["sandboxId"], "principalScope": principal, "keyHash": key,
                    "operationId": operation, "requestFingerprint": fingerprint, "baseRevision": base,
                    "sourceId": request["sourceId"], "target": target, "beforeSha256": _sha(before),
                    "afterSha256": _sha(after), "noChange": no_change}
        if fresh:
            if len(inventory["keys"]) >= MAX_JOBS:
                raise JobError("job_limit")
            inventory["keys"][key] = _sha(_raw(proposed))
            _replace(store / "inventory.json", _raw(inventory))
            _checkpoint("after_inventory")
            _new(store / "claims" / (key + ".json"), _raw(proposed))
            _checkpoint("after_claim")
            claim = proposed
        elif claim != proposed:
            raise JobError("store_inconsistent")
        if no_change:
            report = _report(repo, claim, None, not fresh)
            _state(store, key, report)
            return report
        tree = _git(repo, "rev-parse", base + "^{tree}").decode().strip()
        if fresh:
            revision = _commit(repo, tree, _metadata(claim, "claimed"), base)
            _cas(repo, ref, revision, ZERO, base)
            _checkpoint("after_receipt")
        else:
            phase, revision = _receipt(repo, ref, claim)
            if phase != "claimed":
                raise JobError("store_inconsistent")
        blob = _git(repo, "hash-object", "--no-filters", "-w", "--stdin", raw=after).decode().strip()
        candidate_tree = _changed_tree(repo, tree, target.split("/"), blob)
        candidate = _commit(repo, candidate_tree, _metadata(claim, "candidate_saved_local"), base)
        _checkpoint("after_candidate_object")
        _checkpoint("before_result_cas")
        _cas(repo, ref, candidate, revision, base)
        _checkpoint("after_result_ref")
        _receipt(repo, ref, claim)
        report = _report(repo, claim, candidate, not fresh)
        _state(store, key, report)
        return report


def run_job(sandbox: Path, request_path: Path, baseline_snapshot: Path) -> dict:
    try:
        return _run_job(sandbox, request_path, baseline_snapshot)
    except JobError:
        raise
    except PreflightError as error:
        raise JobError(error.code) from None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError,
            subprocess.SubprocessError):
        raise JobError("local_job_failed") from None


def _initialize(sandbox):
    root = _path(sandbox)
    if root.exists() or not root.parent.is_dir() or not (root.parent / ".keep").is_file():
        raise JobError("new_protected_sandbox_required")
    _read(root.parent / ".keep")
    root.mkdir(mode=0o700)
    _new(root / ".keep", b"")
    repo, baseline, store = root / "repo", root / "baseline", root / "store"
    for path in [repo, baseline, store, store / "claims", store / "states"]:
        path.mkdir(mode=0o700)
    marker = {"format": FORMAT, "version": 1, "sandboxId": str(uuid.uuid4()), "principal": "trusted-local-synthetic",
              "sourceId": FOLDER, "rootSha256": _sha(str(root).encode())}
    _new(root / "sandbox.json", _raw(marker))
    _new(store / "identity.json", _raw({"version": 1, "sandboxId": marker["sandboxId"], "markerSha256": _sha(_raw(marker))}))
    _new(store / "inventory.json", _raw({"version": 1, "sandboxId": marker["sandboxId"], "keys": {}}))
    _new(store / "lock", b"")
    _git(repo, "init", "-q", "--template=", "--initial-branch=main", "--object-format=sha1")
    _new(repo / ".git/b1-sandbox-id", (marker["sandboxId"] + "\n").encode())
    models = "from __future__ import annotations\nfrom dataclasses import dataclass\n\n" + "\n\n".join(
        inspect.getsource(model) for model in (PublicTranslation, PublicAgent, PublicReview))
    registration = {"version": 1, "review": {"folder": FOLDER, "title": "Synthetic B1 fixture review",
                    "subtitle": "Synthetic subtitle", "date": "2026-11-21", "updated": "2026-11-21",
                    "category": "Synthetic", "tags": ["fixture"], "summary": "Synthetic original summary",
                    "translations": [{"language": "en", "subdir": "en", "label": "English"}]}}
    files = {"scripts/publish_public_site.py": models.encode(), "publication/reviews/" + FOLDER + ".json": _raw(registration),
             FOLDER + "/dist/index.html": b"<p>Synthetic B1 Korean fixture</p>",
             FOLDER + "/dist/en/index.html": b"<p>Synthetic B1 English fixture</p>"}
    for name, raw in files.items():
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        _new(repo / name, raw)
    inputs = review_inputs(repo, FOLDER)
    files["publication/requests/" + FOLDER + ".json"] = _raw({"version": 2, "review": FOLDER, **inputs})
    published = {"reviews/" + FOLDER + "/index.html": files[FOLDER + "/dist/index.html"],
                 "reviews/" + FOLDER + "/en/index.html": files[FOLDER + "/dist/en/index.html"]}
    files["publication_changes/fixture.json"] = _raw({"version": 1, "reason": "Synthetic reviewed fixture outputs",
            "files": {name: {"before": _sha(raw), "after": _sha(raw)} for name, raw in published.items()}})
    for name in ["publication/requests/" + FOLDER + ".json", "publication_changes/fixture.json"]:
        (repo / name).parent.mkdir(parents=True, exist_ok=True); _new(repo / name, files[name])
    tree = _tree(repo, files)
    base = _commit(repo, tree, {"format": FORMAT, "phase": "synthetic_source"})
    _git(repo, "update-ref", "refs/heads/main", base, ZERO)
    _git(repo, "read-tree", base)
    refs = list(published)
    article = {"id": FOLDER, "path": "/AI_Tech_Review/reviews/" + FOLDER + "/", "title": registration["review"]["title"],
               "publishedAt": "2026-11-21", "topic": "review"}
    catalog = {"revision": "a" * 40, "articles": [article]}
    snapshot = {"version": 1, "reviews": {FOLDER: {"href": refs[0], "metric_path": article["path"],
                "date": article["publishedAt"], "translations": {"en": {"href": refs[1], "metric_path": None}}, "references": refs}},
                "archive": {}, "external": {}, "publications": {FOLDER: {k: article[k] for k in ["path", "topic", "publishedAt"]}},
                "files": {name: {"sha256": _sha(raw), "content_sha256": _sha(raw), "bytes": len(raw)} for name, raw in published.items()},
                "missing_files": [], "declared_hash_mismatches": []}
    data = {"snapshot.json": _raw(snapshot), "reader-publications.json": _raw(catalog),
            "reader-updates.json": _raw({"version": 1, "pages": {}, "articles": []})}
    release = {"version": 1, "revision": catalog["revision"], "snapshot": snapshot,
               "catalog_sha256": _sha(data["reader-publications.json"]), "initial_payloads": {},
               "artifact_files": {**{name: {"sha256": _sha(raw), "bytes": len(raw)} for name, raw in published.items()},
                                   **{name: {"sha256": _sha(raw), "bytes": len(raw)} for name, raw in data.items() if name != "snapshot.json"}}}
    data["release.json"] = _raw(release)
    for name, raw in data.items():
        _new(baseline / name, raw)
    request = {"schemaVersion": 1, "operation": OPERATION, "sourceId": FOLDER, "expectedSourceRevision": base,
               "expectedInputs": inputs, "expectedReleaseRevision": catalog["revision"],
               "expectedReleaseEvidence": {key: _sha(data[name]) for key, name in [("releaseSha256", "release.json"),
                     ("catalogSha256", "reader-publications.json"), ("updatesSha256", "reader-updates.json")]},
               "patch": {"summary": "Synthetic B1 candidate summary"}, "idempotencyKey": str(uuid.uuid4())}
    _new(root / "example-request.json", _raw(request))
    _scan(root)
    _sandbox(root)
    _source_tree(repo)
    return {"schemaVersion": 1, "ok": True, "status": "synthetic_sandbox_initialized", "sourceRevision": base,
            "limits": ["not_authorization", "not_production_source", "not_published"]}


def initialize_sandbox(sandbox: Path) -> dict:
    try:
        return _initialize(sandbox)
    except JobError:
        raise
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, subprocess.SubprocessError):
        raise JobError("sandbox_initialization_failed") from None


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise JobError("invalid_arguments")


def main(argv=None):
    parser = _Parser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    init = actions.add_parser("init-fixture"); init.add_argument("--sandbox", type=Path, required=True)
    apply = actions.add_parser("apply"); apply.add_argument("--sandbox", type=Path, required=True)
    apply.add_argument("--request", type=Path, required=True); apply.add_argument("--baseline-snapshot", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        result = initialize_sandbox(args.sandbox) if args.action == "init-fixture" else run_job(args.sandbox, args.request, args.baseline_snapshot)
    except JobError as error:
        print(json.dumps({"schemaVersion": 1, "ok": False, "reason": error.code})); return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
