"""Plan or explicitly remove old verified local publication candidates.

Only direct candidate directories inside this checkout's output/ are eligible.
Published assets, source folders, unknown directories and linked trees are never
removed. Put .keep in an active preview directory before opening its server.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat

try:
    from .publication_lock import publication_lock
except ImportError:
    from publication_lock import publication_lock

ROOT = Path(__file__).resolve().parents[1]
MARKER = ".publication-candidate.json"
REVISION = re.compile(r"[a-f0-9]{40}\Z")
MARKER_KEYS = {"version", "kind", "revision", "created_at", "status", "site"}


def _regular_path(path: Path) -> None:
    for piece in (path, *path.parents):
        if piece.is_symlink():
            raise ValueError("Retention paths must not contain symlinks")


def _scope(root: Path, workspace: Path) -> Path:
    requested = Path(root).absolute()
    _regular_path(requested)
    workspace = Path(workspace).resolve()
    output = workspace / "output"
    resolved = requested.resolve()
    if not resolved.is_relative_to(output) or not resolved.is_dir():
        raise ValueError("Choose an existing local collection inside this checkout's output/ directory")
    if (resolved / MARKER).exists():
        raise ValueError("The retention root must collect candidates, not be a candidate itself")
    return resolved


def _json_file(path: Path):
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 2_000_000:
        raise ValueError("Missing or invalid candidate record")
    def unique_record(pairs):
        record = {}
        for key, value in pairs:
            if key in record:
                raise ValueError("Duplicate candidate record field")
            record[key] = value
        return record
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_record)


def _candidate(path: Path, now: datetime) -> dict:
    if path.is_symlink() or not path.is_dir():
        raise ValueError("Linked or non-directory candidate")
    marker_path = path / MARKER
    marker = _json_file(marker_path)
    if (not isinstance(marker, dict) or set(marker) != MARKER_KEYS
            or type(marker["version"]) is not int or marker["version"] != 1
            or marker["kind"] != "publication-candidate" or marker["status"] != "verified-local"
            or marker["site"] != "site" or not isinstance(marker["revision"], str)
            or not REVISION.fullmatch(marker["revision"]) or not isinstance(marker["created_at"], str)):
        raise ValueError("Unknown candidate marker")
    created = datetime.fromisoformat(marker["created_at"].replace("Z", "+00:00"))
    if created.tzinfo is None or created.utcoffset() != timedelta(0) or created > now:
        raise ValueError("Invalid or future candidate creation time")
    site = path / "site"
    if site.is_symlink() or not site.is_dir():
        raise ValueError("Candidate site is missing or linked")
    report = _json_file(path / "report.json")
    if (not isinstance(report, dict) or report.get("revision") != marker["revision"]
            or report.get("status") != "candidate_only_requires_release_policy_and_browser_review"):
        raise ValueError("Candidate report does not match its successful preparation")
    info = path.stat()
    return {"created": created, "revision": marker["revision"],
            "marker_sha256": hashlib.sha256(marker_path.read_bytes()).hexdigest(),
            "identity": (info.st_dev, info.st_ino)}


def _tree_bytes(path: Path) -> int:
    total = 0
    for parent, directories, files in os.walk(path, followlinks=False):
        for name in directories + files:
            item = Path(parent) / name
            mode = item.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ValueError("contains_symlink")
            if name == ".git":
                raise ValueError("contains_git_checkout")
            if name == ".keep":
                raise ValueError("keep_marker")
            if stat.S_ISREG(mode):
                total += item.stat().st_size
            elif not stat.S_ISDIR(mode):
                raise ValueError("contains_special_file")
    return total


def _protected(path: Path, protected: list[Path], root_keep: bool) -> str | None:
    if root_keep:
        return "root_keep_marker"
    if (path / ".keep").exists() or (path / ".keep").is_symlink():
        return "keep_marker"
    if any(path.is_relative_to(item) or item.is_relative_to(path) for item in protected):
        return "protected_path"
    return None


def _remove_candidate(path: Path, expected: dict, now: datetime, protected: list[Path], root: Path) -> str:
    # Recheck immediately before deletion: a preview may have been protected or
    # a candidate replaced since the plan was assembled.
    try:
        if _protected(path, protected, (root / ".keep").exists() or (root / ".keep").is_symlink()):
            return "protected_after_plan"
        current = _candidate(path, now)
        if current["identity"] != expected["identity"] or current["marker_sha256"] != expected["marker_sha256"]:
            return "changed_after_plan"
        _tree_bytes(path)
        shutil.rmtree(path)
        return "deleted"
    except (ValueError, FileNotFoundError):
        return "changed_or_protected_after_plan"


def retain_candidates(root: Path, *, keep: int = 2, min_age_days: int = 7,
                      protect=(), apply: bool = False, now: datetime | None = None,
                      workspace: Path = ROOT) -> dict:
    if type(keep) is not int or keep < 2 or type(min_age_days) is not int or min_age_days < 7:
        raise ValueError("Keep at least two candidates and only remove candidates at least seven days old")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None or now.utcoffset() != timedelta(0):
        raise ValueError("Use a timezone-aware UTC evaluation time")
    root = _scope(root, workspace)
    protected = []
    for item in protect:
        item = Path(item).absolute()
        _regular_path(item)
        item = item.resolve()
        if not item.exists() or not item.is_relative_to(root):
            raise ValueError("Protected paths must exist inside the chosen output collection")
        protected.append(item)
    rows, known = [], []
    for path in sorted(root.iterdir()):
        if not path.is_dir() and not path.is_symlink():
            continue
        row = {"path": path.name, "action": "keep"}
        rows.append(row)
        try:
            record = _candidate(path, now)
        except (ValueError, OSError, UnicodeError):
            row["reason"] = "unknown_or_linked_directory"
            continue
        known.append((path, record, row))
    known.sort(key=lambda item: (item[1]["created"], item[0].name), reverse=True)
    planned = []
    root_keep = (root / ".keep").exists() or (root / ".keep").is_symlink()
    for position, (path, record, row) in enumerate(known):
        row.update(created_at=record["created"].isoformat().replace("+00:00", "Z"),
                   age_days=round((now - record["created"]).total_seconds() / 86400, 2), revision=record["revision"])
        reason = _protected(path, protected, root_keep)
        if reason:
            row["reason"] = reason
        elif position < keep:
            row["reason"] = "newest_candidates"
        elif now - record["created"] < timedelta(days=min_age_days):
            row["reason"] = "younger_than_minimum_age"
        else:
            try:
                row["bytes"] = _tree_bytes(path)
                row.update(action="would_delete", reason="old_verified_candidate")
                planned.append((path, record, row))
            except (ValueError, OSError) as error:
                row["reason"] = str(error) if isinstance(error, ValueError) else "tree_unavailable"
    errors = []
    if apply and planned:
        with publication_lock(root / ".publication-retention.lock"):
            for path, expected, row in planned:
                try:
                    row["action"] = _remove_candidate(path, expected, now, protected, root)
                except OSError:
                    row["action"] = "delete_failed"
                    errors.append(path.name)
    return {"version": 1, "mode": "apply" if apply else "dry-run", "root": root.relative_to(Path(workspace).resolve()).as_posix(),
            "keep": keep, "min_age_days": min_age_days, "evaluated_at": now.isoformat().replace("+00:00", "Z"),
            "candidates": rows, "planned_bytes": sum(row.get("bytes", 0) for _, _, row in planned),
            "deleted_bytes": sum(row.get("bytes", 0) for _, _, row in planned if row["action"] == "deleted"),
            "errors": errors,
            "byte_accounting": "Logical file sizes; physical space released can differ with filesystem sharing or compression.",
            "limits": "Only marked local candidates are considered. Protect active previews with .keep or --protect before starting them; this command does not archive releases or replace backups."}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Explicit existing candidate collection inside this checkout's output/")
    parser.add_argument("--keep", type=int, default=2, help="Newest verified candidates retained; minimum two")
    parser.add_argument("--min-age-days", type=int, default=7, help="Minimum deletion age; at least seven days")
    parser.add_argument("--protect", type=Path, action="append", default=[], help="Existing path inside a candidate/collection to preserve; repeatable")
    parser.add_argument("--apply", action="store_true", help="Perform the displayed eligible cleanup; omission is read-only")
    args = parser.parse_args(argv)
    try:
        result = retain_candidates(args.root, keep=args.keep, min_age_days=args.min_age_days, protect=args.protect, apply=args.apply)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return int(bool(result["errors"]))
    except (ValueError, OSError, TimeoutError) as error:
        parser.exit(1, f"Candidate retention refused: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
