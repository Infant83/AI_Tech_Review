"""B2a bounded read-only source intake. Output is a plan, never a candidate."""
from __future__ import annotations

import argparse
import configparser
from datetime import datetime, timezone
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

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import admin_requests, admin_inventory
from scripts.admin_inventory import _Inputs, InventoryError, MAX_JSON_FILE_BYTES

MAX_TREE_ENTRIES = 20_000
MAX_TREE_BYTES = 4 * 1024 * 1024
MAX_DIST_FILES = 1_000
MAX_DIST_BYTES = 128 * 1024 * 1024
MAX_BLOB_BYTES = 64 * 1024 * 1024
MAX_READ_BYTES = 512 * 1024 * 1024
MAX_DESCRIPTOR_BYTES = 2_000_000
MAX_STDOUT_BYTES = 16 * 1024
GIT_SECONDS = 20
TOTAL_SECONDS = 120
HEX40 = re.compile(r"[a-f0-9]{40}\Z")
_OUTPUT_DIR_FD_SUPPORTED = (hasattr(os, "O_NOFOLLOW") and hasattr(os, "O_DIRECTORY")
    and all(call in os.supports_dir_fd for call in [os.open, os.mkdir, os.stat, os.link, os.unlink])
    and os.link in os.supports_follow_symlinks)


class IntakeError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__("Source intake refused (" + code + ").")


def _trusted_git():
    # Fixed operator-installed locations only: inherited PATH must never select
    # an executable. Homebrew's versioned symlink is allowed only in its Git
    # Cellar; arbitrary links to a source/output executable are not trusted.
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


def _raw(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _sha(value):
    return hashlib.sha256(value).hexdigest()


def _safe(path):
    path = Path(os.path.abspath(path))
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise IntakeError("unsafe_path")
    return path


def _control(path, limit=65_536):
    path = _safe(path)
    before = path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
        raise IntakeError("unsafe_source_layout")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    with os.fdopen(descriptor, "rb") as handle:
        opened = os.fstat(handle.fileno())
        if not stat.S_ISREG(opened.st_mode):
            raise IntakeError("unsafe_source_layout")
        raw = handle.read(limit + 1)
        after = os.fstat(handle.fileno())
    if (len(raw) > limit or len(raw) != before.st_size
            or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns)
            or (opened.st_size, opened.st_mtime_ns) != (after.st_size, after.st_mtime_ns)):
        raise IntakeError("source_layout_changed")
    return raw


def _env():
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "PYTHON"))}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_SYSTEM=os.devnull, GIT_CONFIG_GLOBAL=os.devnull,
               GIT_ATTR_NOSYSTEM="1", GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
               GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_ALLOW_PROTOCOL="",
               GIT_LITERAL_PATHSPECS="1", PATH=os.defpath)
    return env


class _Budget:
    def __init__(self):
        self.deadline = time.monotonic() + TOTAL_SECONDS
        self.read_bytes = 0

    def check(self, amount=0):
        self.read_bytes += amount
        if self.read_bytes > MAX_READ_BYTES:
            raise IntakeError("read_budget")
        if time.monotonic() > self.deadline:
            raise IntakeError("intake_timeout")


class _OutputDirectory:
    """Keep output writes relative to the directories opened before reading."""
    def __init__(self, output, budget):
        self.output, self.budget = output, budget
        self.parents, self.directory = [], None
        if not _OUTPUT_DIR_FD_SUPPORTED:
            raise IntakeError("unsupported_output_platform")
        self.flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        try:
            descriptor = os.open(output.anchor, self.flags)
            self.parents.append((descriptor, output.anchor, self.identity(os.fstat(descriptor))))
            for name in output.parent.parts[1:]:
                descriptor = os.open(name, self.flags, dir_fd=self.parents[-1][0])
                self.parents.append((descriptor, name, self.identity(os.fstat(descriptor))))
            self.verify()
            try:
                os.stat(output.name, dir_fd=self.parents[-1][0], follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise IntakeError("new_output_required")
        except BaseException:
            self.close()
            raise

    @staticmethod
    def identity(info):
        return info.st_dev, info.st_ino, stat.S_IFMT(info.st_mode)

    def verify(self):
        self.budget.check()
        try:
            for i, (descriptor, name, expected) in enumerate(self.parents):
                current = os.stat(name, dir_fd=self.parents[i - 1][0] if i else None,
                                  follow_symlinks=False)
                if (self.identity(current) != expected or not stat.S_ISDIR(current.st_mode)
                        or self.identity(os.fstat(descriptor)) != expected):
                    raise IntakeError("output_changed")
            if self.directory is not None:
                self.verify_child(self.output.name, self.parents[-1][0], self.directory)
        except OSError:
            raise IntakeError("output_changed") from None

    def verify_child(self, name, parent, descriptor):
        try:
            current = os.stat(name, dir_fd=parent, follow_symlinks=False)
            opened = os.fstat(descriptor)
        except OSError:
            raise IntakeError("output_changed") from None
        if self.identity(current) != self.identity(opened):
            raise IntakeError("output_changed")

    def publish(self, raw):
        self.verify()
        parent = self.parents[-1][0]
        os.mkdir(self.output.name, mode=0o700, dir_fd=parent)
        self.directory = os.open(self.output.name, self.flags, dir_fd=parent)
        self.verify()
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        keeper = os.open(".keep", flags, 0o600, dir_fd=self.directory)
        try:
            os.fsync(keeper)
            self.verify_child(".keep", self.directory, keeper)
        finally:
            os.close(keeper)
        self.verify()
        descriptor = os.open(".descriptor.partial", flags, 0o600, dir_fd=self.directory)
        try:
            with os.fdopen(descriptor, "wb", closefd=False) as handle:
                self.verify()
                handle.write(raw); handle.flush(); os.fsync(descriptor)
            self.verify()
            self.verify_child(".descriptor.partial", self.directory, descriptor)
            os.link(".descriptor.partial", "descriptor.json", src_dir_fd=self.directory,
                    dst_dir_fd=self.directory, follow_symlinks=False)
            self.verify_child("descriptor.json", self.directory, descriptor)
            self.verify()
            os.unlink(".descriptor.partial", dir_fd=self.directory)
            os.fsync(self.directory)
            self.verify_child("descriptor.json", self.directory, descriptor)
            self.verify()
        finally:
            os.close(descriptor)

    def close(self):
        descriptors = ([self.directory] if self.directory is not None else [])
        descriptors += [item[0] for item in reversed(self.parents)]
        for descriptor in descriptors:
            try:
                os.close(descriptor)
            except OSError:
                pass
        self.directory, self.parents = None, []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class _GitSource:
    """Recognize source Git separately from B1's writable synthetic sandbox."""
    def __init__(self, root, budget):
        self.root, self.budget = _safe(root), budget
        git = self.root / ".git"
        self.pointer_paths = []
        if git.is_dir():
            self.gitdir = _safe(git)
        elif git.is_file():
            raw = self.control(git, 4096).decode("utf-8")
            if not raw.startswith("gitdir: ") or raw.count("\n") != 1:
                raise IntakeError("unsafe_source_layout")
            self.gitdir = _safe(self.root / raw[8:].strip())
            self.pointer_paths.append(git)
        else:
            raise IntakeError("source_git_required")
        common = self.gitdir / "commondir"
        self.common = _safe(self.gitdir / self.control(common, 4096).decode().strip()) if common.exists() else self.gitdir
        self.control_paths = [*self.pointer_paths, self.common / "config"]
        # Bind optional control membership as well as existing file bytes.
        # Creating an initially absent control during intake is a change.
        self.optional_controls = [common, self.gitdir / "config.worktree"]
        self.controls = None
        self.guard()
        self.git_version = self.run("version").decode("ascii").strip()
        if self.run("rev-parse", "--show-object-format").strip() != b"sha1":
            raise IntakeError("unsupported_git_format")
        if self.run("rev-parse", "--show-toplevel").decode().strip() != str(self.root):
            raise IntakeError("unsafe_source_layout")
        if self.run("rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip() != str(self.common):
            raise IntakeError("unsafe_source_layout")
        if self.run("for-each-ref", "--format=%(refname)", "refs/replace").strip():
            raise IntakeError("unsafe_source_objects")
        self.revision = self.head()
        if self.run("cat-file", "-t", self.revision).strip() != b"commit":
            raise IntakeError("source_commit_required")
        self.tree = self.run("rev-parse", self.revision + "^{tree}").decode().strip()
        if not HEX40.fullmatch(self.tree):
            raise IntakeError("invalid_git_metadata")
        self.objects = self.tree_metadata()

    def control(self, path, limit=65_536):
        raw = _control(path, limit)
        self.budget.check(len(raw))
        return raw

    def guard(self):
        self.budget.check()
        _safe(self.gitdir); _safe(self.common)
        _safe(self.common / "objects"); _safe(self.common / "refs")
        for relative in ["objects/info/alternates", "info/grafts", "info/attributes"]:
            if _safe(self.common / relative).exists():
                raise IntakeError("unsafe_source_objects")
        values = {}
        for path in [*self.control_paths, *self.optional_controls]:
            if path in self.optional_controls and not _safe(path).exists():
                values[str(path)] = None
                continue
            raw = self.control(path)
            values[str(path)] = _sha(raw)
            if path.name not in {"config", "config.worktree"}:
                continue
            parser = configparser.RawConfigParser(strict=True)
            try:
                parser.read_string(raw.decode("utf-8"))
                if parser.defaults():
                    raise IntakeError("unsafe_git_config")
                for section in parser.sections():
                    keys = set(parser[section])
                    if section == "core":
                        if keys - {"repositoryformatversion", "bare", "filemode", "logallrefupdates", "ignorecase", "precomposeunicode"}:
                            raise IntakeError("unsafe_git_config")
                        if parser[section].get("repositoryformatversion", "0") != "0" or parser[section].get("bare", "false") != "false":
                            raise IntakeError("unsafe_git_config")
                    elif section == "extensions":
                        if keys != {"worktreeconfig"} or parser[section]["worktreeconfig"].lower() != "true":
                            raise IntakeError("unsafe_git_config")
                    elif re.fullmatch(r'remote "[A-Za-z0-9_.-]+"', section):
                        if keys - {"url", "fetch", "pushurl"}:
                            raise IntakeError("unsafe_git_config")
                    elif re.fullmatch(r'branch "[^"\r\n]+"', section):
                        if keys - {"remote", "merge", "rebase"}:
                            raise IntakeError("unsafe_git_config")
                    elif section == "user":
                        if keys - {"name", "email", "signingkey"}:
                            raise IntakeError("unsafe_git_config")
                    elif section == "codex" and path.name == "config.worktree":
                        # Inert host metadata only. Never open or execute its
                        # value; raw control bytes remain change-bound above.
                        if keys != {"localenvironmentconfigpath"}:
                            raise IntakeError("unsafe_git_config")
                    else:
                        raise IntakeError("unsafe_git_config")
            except (configparser.Error, UnicodeError):
                raise IntakeError("unsafe_git_config") from None
        if self.controls is not None and values != self.controls:
            raise IntakeError("source_layout_changed")
        self.controls = values

    def run(self, *args, limit=None):
        self.budget.check()
        if GIT is None:
            raise IntakeError("trusted_git_unavailable")
        limit = MAX_TREE_BYTES if limit is None else limit
        if args[0] not in {"version", "rev-parse", "cat-file", "ls-tree", "for-each-ref"}:
            raise IntakeError("unsafe_git_command")
        command = [GIT, "--no-replace-objects", "--no-lazy-fetch", "--no-optional-locks",
                   "-c", "core.hooksPath=" + os.devnull, "-c", "core.attributesFile=" + os.devnull,
                   "-c", "core.fsmonitor=false", "-c", "protocol.allow=never", "-C", str(self.root), *args]
        end = min(self.budget.deadline, time.monotonic() + GIT_SECONDS)
        process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, env=_env())
        output, error = bytearray(), bytearray()
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ, output)
                selector.register(process.stderr, selectors.EVENT_READ, error)
                while selector.get_map():
                    left = end - time.monotonic()
                    if left <= 0:
                        raise IntakeError("git_timeout")
                    for key, _ in selector.select(min(left, .2)):
                        destination = key.data
                        ceiling = limit if destination is output else MAX_STDOUT_BYTES
                        chunk = os.read(key.fileobj.fileno(), min(65_536, ceiling + 1 - len(destination)))
                        if not chunk:
                            selector.unregister(key.fileobj)
                        else:
                            destination.extend(chunk)
                            if len(destination) > ceiling:
                                raise IntakeError("git_metadata_limit")
                            if destination is output and args[0] == "ls-tree" and output.count(b"\0") > MAX_TREE_ENTRIES:
                                raise IntakeError("tree_entry_limit")
            process.wait(timeout=max(.01, end - time.monotonic()))
            if process.returncode:
                raise IntakeError("git_read_failed")
            self.budget.check()
            return bytes(output)
        finally:
            if process.poll() is None:
                process.kill(); process.wait()
            process.stdout.close(); process.stderr.close()

    def head(self):
        value = self.run("rev-parse", "HEAD").decode().strip()
        if not HEX40.fullmatch(value):
            raise IntakeError("source_commit_required")
        return value

    def tree_metadata(self):
        result = {}
        raw = self.run("ls-tree", "-r", "-l", "-z", self.revision)
        if raw and not raw.endswith(b"\0"):
            raise IntakeError("invalid_git_metadata")
        for row in raw.split(b"\0"):
            if not row:
                continue
            if len(result) >= MAX_TREE_ENTRIES:
                raise IntakeError("tree_entry_limit")
            meta, name = row.split(b"\t", 1)
            mode, kind, oid, size = meta.split()
            name = name.decode("utf-8")
            path = PurePosixPath(name)
            if (path.is_absolute() or path.as_posix() != name or any(p in {".", ".."} for p in path.parts)
                    or any(ord(c) < 32 for c in name) or name in result):
                raise IntakeError("invalid_git_metadata")
            result[name] = {"mode": mode.decode(), "kind": kind.decode(), "oid": oid.decode(),
                            "bytes": int(size) if size != b"-" else None}
        return result

    def verify(self, root, tracker):
        self.guard()
        if self.head() != self.revision:
            raise IntakeError("source_conflict")
        current = self.tree_metadata()
        if current != self.objects:
            raise IntakeError("input_changed")
        selected = set()
        for path, info in tracker.files.items():
            if not info["source"]:
                continue
            name = path.relative_to(self.root).as_posix(); selected.add(name)
            entry = current.get(name)
            if (entry is None or entry["kind"] != "blob" or entry["mode"] not in {"100644", "100755"}
                    or entry["oid"] != info["git"] or entry["bytes"] != info["bytes"]
                    or entry["mode"] != info["mode"]):
                return self.revision, "different"
        prefixes = tuple(path.relative_to(self.root).as_posix() + "/" for path in tracker.source_directories)
        if any(name.startswith(prefixes) and name not in selected
               and Path(name).name not in {".DS_Store", "Thumbs.db"} for name in current):
            return self.revision, "different"
        return self.revision, "match"


class _BoundedInputs(_Inputs):
    def __init__(self, root, budget):
        super().__init__(root)
        self.budget, self.dist = budget, None
        self.dist_files = {}
        self.byte_limits = {}
        self.enumerated = set()

    def _entries(self, path):
        result = []
        # Path.iterdir on supported Python may eagerly call os.listdir. Bound
        # enumeration itself, including untracked/empty selected directories.
        with os.scandir(path) as entries:
            for entry in entries:
                self.budget.check()
                child = path / entry.name
                if child not in self.enumerated:
                    if len(self.enumerated) >= MAX_TREE_ENTRIES:
                        raise IntakeError("directory_limit")
                    self.enumerated.add(child)
                result.append(child)
        return sorted(result)

    def _chunks(self, path, limit=None):
        self.budget.check()
        ceiling = min(MAX_BLOB_BYTES, self.byte_limits.get(path, MAX_BLOB_BYTES))
        dist_limit = self.dist is not None and self.dist in path.parents and path not in self.files
        if dist_limit:
            ceiling = min(ceiling, MAX_DIST_BYTES - sum(self.dist_files.values()))
        if limit is not None:
            ceiling = min(ceiling, limit)
        if path.stat().st_size > ceiling:
            raise IntakeError("dist_limit" if dist_limit else "blob_limit")
        count = 0
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise IntakeError("invalid_source_type")
            if opened.st_size > ceiling:
                raise IntakeError("dist_limit" if dist_limit else "blob_limit")
            while True:
                chunk = handle.read(min(1024 * 1024, ceiling + 1 - count,
                                        MAX_READ_BYTES + 1 - self.budget.read_bytes))
                if not chunk:
                    break
                self.budget.check(len(chunk)); count += len(chunk)
                if count > ceiling:
                    raise IntakeError("dist_limit" if dist_limit else "blob_limit")
                yield chunk

    def json(self, path, *, boundary=None):
        path = Path(os.path.abspath(path))
        remaining = (admin_inventory.MAX_JSON_TOTAL_BYTES - self.json_total
                     if path not in self.json_files else MAX_JSON_FILE_BYTES)
        if path.stat().st_size > remaining:
            raise InventoryError("json_total_limit")
        self.byte_limits[path] = min(self.byte_limits.get(path, MAX_JSON_FILE_BYTES),
                                     MAX_JSON_FILE_BYTES, remaining)
        return super().json(path, boundary=boundary)

    def file(self, path, *, boundary=None):
        path = Path(os.path.abspath(path))
        if self.dist is not None and self.dist in path.parents and path not in self.dist_files:
            if len(self.dist_files) >= MAX_DIST_FILES:
                raise IntakeError("dist_limit")
        result = super().file(path, boundary=boundary)
        if self.dist is not None and self.dist in path.parents:
            self.dist_files[path] = result["bytes"]
            if sum(self.dist_files.values()) > MAX_DIST_BYTES:
                raise IntakeError("dist_limit")
        result["mode"] = "100755" if path.stat().st_mode & 0o111 else "100644"
        return result

    def tree(self, path):
        for entry in self._entries(path) if path.is_dir() else []:
            if entry.name in {".DS_Store", "Thumbs.db"} and entry.is_dir():
                raise IntakeError("invalid_source_type")
        return super().tree(path)


def _tool_hashes():
    directory = Path(__file__).resolve().parent
    names = ["admin_source_intake.py", "admin_requests.py", "admin_inventory.py", "publication_intent.py",
             "publication_release.py", "publication_snapshot.py", "review_registry.py", "reader_engagement_publish.py"]
    return {"scripts/" + name: _sha((directory / name).read_bytes()) for name in names}


def _intake(source_root, request_path, baseline_snapshot, output):
    budget = _Budget()
    root, incoming, baseline, output = map(_safe, [source_root, request_path, baseline_snapshot, output])
    if output.exists() or not output.parent.is_dir():
        raise IntakeError("new_output_required")
    if (baseline.parent == output or baseline.parent in output.parents
            or (root in output.parents and output.relative_to(root).parts[0] != "output")):
        raise IntakeError("unsafe_output")
    with _OutputDirectory(output, budget) as destination:
        return _read_intake(root, incoming, baseline, output, budget, destination)


def _read_intake(root, incoming, baseline, output, budget, destination):
    code = _tool_hashes()
    source = _GitSource(root, budget)
    if any(p == output or p in output.parents for p in [source.gitdir, source.common]):
        raise IntakeError("unsafe_output")
    tracker = _BoundedInputs(root, budget)
    tracker.byte_limits[incoming] = admin_requests.MAX_REQUEST_BYTES
    payload = tracker.read_bytes(incoming, admin_requests.MAX_REQUEST_BYTES, boundary=incoming.parent)
    request = admin_requests.parse_request(payload)
    if request["expectedSourceRevision"] != source.revision:
        raise IntakeError("source_conflict")
    tracker.dist = root / request["sourceId"] / "dist"
    capture = {}
    report = admin_requests._preflight(root, incoming, baseline, tracker=tracker,
        revision_reader=source.verify, frozen=True, capture=capture)
    files = []
    for path, info in sorted(tracker.files.items()):
        if not info["source"]:
            continue
        name = path.relative_to(root).as_posix()
        files.append({"path": name, "mode": source.objects[name]["mode"], "blob": info["git"],
                      "bytes": info["bytes"], "sha256": info["sha256"],
                      "role": "target_dist" if tracker.dist in path.parents else "registration_or_model"})
    directories = [{"path": path.relative_to(root).as_posix(), "members": list(tracker.directories[path])
                    if tracker.directories[path] is not None else None}
                   for path in sorted(tracker.source_directories)]
    descriptor = {"schemaVersion": 1, "status": "source_intake_plan_only", "operation": report["operation"],
        "sourceId": report["sourceId"], "sourceOriginRevision": source.revision, "sourceTree": source.tree,
        "requestFingerprint": report["requestFingerprint"], "checkedInputs": report["checkedInputs"],
        "releaseRevision": report["releaseRevision"], "releaseEvidence": report["releaseEvidence"],
        "snapshotSha256": tracker.files[baseline]["sha256"], "inputs": files, "directories": directories,
        "toolCodeSha256": code, "toolEnvironment": {"python": sys.version.split()[0], "git": source.git_version},
        "counts": {"treeEntries": len(source.objects), "selectedFiles": len(files),
                   "selectedBytes": sum(f["bytes"] for f in files), "distFiles": len(tracker.dist_files),
                   "distBytes": sum(tracker.dist_files.values())},
        "limits": ["not_authorization", "not_candidate_or_saved_request", "not_published", "not_live_https",
                   "not_atomic_snapshot", "not_source_backup", "attachment_continuity_unverified", "B2b_mapping_required"]}
    descriptor["intakeDigest"] = _sha(_raw(descriptor))
    descriptor["checkedAt"] = capture["checked_at"]
    descriptor["observedReadBytes"] = budget.read_bytes
    raw = _raw(descriptor) + b"\n"
    if len(raw) > MAX_DESCRIPTOR_BYTES:
        raise IntakeError("descriptor_limit")
    budget.check()
    if _tool_hashes() != code:
        raise IntakeError("tool_changed")
    source.guard()
    if source.head() != source.revision:
        raise IntakeError("source_conflict")
    destination.publish(raw)
    budget.check()
    return {"schemaVersion": 1, "ok": True, "status": "source_intake_plan_only",
            "descriptorSha256": _sha(raw), "intakeDigest": descriptor["intakeDigest"]}


def create_intake(source_root: Path, request_path: Path, baseline_snapshot: Path, output: Path):
    try:
        return _intake(source_root, request_path, baseline_snapshot, output)
    except IntakeError:
        raise
    except (InventoryError, admin_requests.PreflightError) as error:
        raise IntakeError(error.code) from None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError,
            SyntaxError, subprocess.SubprocessError):
        raise IntakeError("invalid_intake_input") from None


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise IntakeError("invalid_arguments")


def main(argv=None):
    parser = _Parser(description=__doc__)
    for name in ["root", "request", "baseline-snapshot", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    try:
        args = parser.parse_args(argv)
        result = create_intake(args.root, args.request, args.baseline_snapshot, args.output)
    except IntakeError as error:
        result = {"schemaVersion": 1, "ok": False, "reason": error.code}
    raw = _raw(result)
    if len(raw) > MAX_STDOUT_BYTES:
        raw = b'{"schemaVersion":1,"ok":false,"reason":"stdout_limit"}'
    print(raw.decode("utf-8"))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
