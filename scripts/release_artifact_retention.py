"""Bound recovery-artifact count after a successful production deployment."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import re
import subprocess
import time

NAME = "publication-recovery"
MAX_METADATA_BYTES = 4_000_000
VISIBILITY_ATTEMPTS = 3
VISIBILITY_DELAY_SECONDS = 2


class RetentionError(ValueError):
    """Safe CLI reason; never expose provider output or credentials."""
    def __init__(self, code, *, metadata_counts=None):
        self.code = code
        self.deleted = []
        self.delete_attempted = []
        self.unconfirmed_delete = []
        self.metadata_counts = None
        if code == "incomplete_metadata" and metadata_counts is not None:
            self.metadata_counts = {}
            for name in ("page_count", "advertised_total_count", "collected_row_count"):
                value = metadata_counts.get(name)
                self.metadata_counts[name] = (value if type(value) is int
                    and 0 <= value <= (1 << 53) - 1 else None)
        super().__init__("Recovery retention refused (" + code + ").")


def deletion_plan(artifacts: list, keep=3):
    if type(keep) is not int or keep < 1:
        raise ValueError("Keep at least one complete recovery artifact")
    matching = [row for row in artifacts if row.get("name") == NAME and not row.get("expired")]
    if any(type(row.get("id")) is not int or row["id"] <= 0 or not isinstance(row.get("created_at"), str) for row in matching):
        raise ValueError("Invalid recovery artifact record")
    matching.sort(key=lambda row: (row["created_at"], row["id"]), reverse=True)
    return {"keep": [row["id"] for row in matching[:keep]], "delete": [row["id"] for row in matching[keep:]]}


def _positive(value):
    return type(value) is int and value > 0


def _utcnow():
    return datetime.now(timezone.utc)


def _timestamp(value):
    if (not isinstance(value, str) or not re.fullmatch(
            r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|\+00:00)", value)):
        raise RetentionError("invalid_metadata")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise RetentionError("invalid_metadata") from None


def _api(*arguments):
    try:
        result = subprocess.run(["gh", "api", *arguments], check=True, capture_output=True,
                                text=True, timeout=30)
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise RetentionError("api_error") from None
    try:
        valid_output = isinstance(result.stdout, str) and len(result.stdout.encode("utf-8")) <= MAX_METADATA_BYTES
    except UnicodeError:
        valid_output = False
    if not valid_output:
        raise RetentionError("metadata_limit")
    return result.stdout


def _pairs(items):
    value = {}
    for key, item in items:
        if key in value:
            raise RetentionError("invalid_metadata")
        value[key] = item
    return value


def _invalid_constant(_):
    raise RetentionError("invalid_metadata")


def _read_artifacts(repository):
    raw = _api("--paginate", "--slurp",
               f"repos/{repository}/actions/artifacts?per_page=100&name={NAME}")
    try:
        pages = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_invalid_constant)
    except (ValueError, RecursionError):
        raise RetentionError("invalid_metadata") from None
    if not isinstance(pages, list) or not 1 <= len(pages) <= 100:
        raise RetentionError("incomplete_metadata", metadata_counts={
            "page_count": len(pages) if isinstance(pages, list) else None})
    rows, total = [], None
    for page in pages:
        if (not isinstance(page, dict) or type(page.get("total_count")) is not int
                or page["total_count"] < 0 or not isinstance(page.get("artifacts"), list)
                or len(page["artifacts"]) > 100):
            raise RetentionError("invalid_metadata")
        if total is not None and total != page["total_count"]:
            raise RetentionError("metadata_changed")
        total = page["total_count"]
        rows.extend(page["artifacts"])
    if total != len(rows):
        raise RetentionError("incomplete_metadata", metadata_counts={
            "page_count": len(pages), "advertised_total_count": total,
            "collected_row_count": len(rows)})
    ids = set()
    for row in rows:
        if (not isinstance(row, dict) or not _positive(row.get("id"))
                or not isinstance(row.get("name"), str) or not row["name"]
                or type(row.get("expired")) is not bool or row["id"] in ids):
            raise RetentionError("invalid_metadata")
        ids.add(row["id"])
    return rows


def _snapshot(rows, current_id, run_id, revision):
    current = next((row for row in rows if row["id"] == current_id), None)
    if current is not None and (current["name"] != NAME or current["expired"]):
        raise RetentionError("current_artifact_mismatch")
    result = {}
    for row in rows:
        # Expired artifacts are not cleanup targets or proof of a complete copy.
        if row["name"] != NAME or row["expired"]:
            continue
        created, expires = _timestamp(row.get("created_at")), _timestamp(row.get("expires_at"))
        workflow = row.get("workflow_run")
        digest = row.get("digest")
        if (not _positive(row.get("size_in_bytes")) or expires <= created or expires <= _utcnow()
                or not isinstance(workflow, dict) or not _positive(workflow.get("id"))
                or not isinstance(workflow.get("head_sha"), str)
                or not re.fullmatch(r"[0-9a-f]{40}", workflow["head_sha"])
                or (digest is not None and (not isinstance(digest, str)
                    or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest)))):
            raise RetentionError("invalid_metadata")
        result[row["id"]] = {"id": row["id"], "name": NAME, "expired": False,
            "created_at": created.isoformat(timespec="microseconds"),
            "expires_at": expires.isoformat(timespec="microseconds"),
            "size_in_bytes": row["size_in_bytes"], "digest": digest,
            "workflow_run": {"id": workflow["id"], "head_sha": workflow["head_sha"]}}
    if current_id is not None:
        if current is None:
            raise RetentionError("current_artifact_not_visible")
        if current_id not in result or result[current_id]["workflow_run"] != {"id": run_id, "head_sha": revision}:
            raise RetentionError("current_artifact_mismatch")
    return result


def _current_snapshot(repository, current_id, run_id, revision):
    for attempt in range(VISIBILITY_ATTEMPTS):
        try:
            return _snapshot(_read_artifacts(repository), current_id, run_id, revision), attempt + 1
        except RetentionError as error:
            if error.code != "current_artifact_not_visible" or attempt == VISIBILITY_ATTEMPTS - 1:
                raise
            time.sleep(VISIBILITY_DELAY_SECONDS)


def run_retention(repository, keep=3, *, apply=False, expected_artifact_id=None,
                  expected_run_id=None, expected_source_revision=None):
    """Bind cleanup to this upload and recheck metadata before each DELETE.

    The provider listing is not an atomic transaction. On disappearance, drift,
    partial failure or uncertain DELETE, stop; never claim an untouched store.
    """
    if type(apply) is not bool:
        raise RetentionError("invalid_arguments")
    if (not isinstance(repository, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
            or any(part in {".", ".."} for part in repository.split("/"))):
        raise RetentionError("invalid_repository")
    if type(keep) is not int or keep < (3 if apply else 1):
        raise RetentionError("invalid_keep")
    supplied = [expected_artifact_id is not None, expected_run_id is not None, expected_source_revision is not None]
    if apply and not all(supplied):
        raise RetentionError("current_upload_required")
    if any(supplied) and (not all(supplied) or not _positive(expected_artifact_id)
            or not _positive(expected_run_id) or not isinstance(expected_source_revision, str)
            or not re.fullmatch(r"[0-9a-f]{40}", expected_source_revision)):
        raise RetentionError("invalid_current_upload")
    deleted, attempted, uncertain = [], [], []
    try:
        snapshot, tries = _current_snapshot(repository, expected_artifact_id, expected_run_id, expected_source_revision)
        plan = deletion_plan(list(snapshot.values()), keep)
        if expected_artifact_id is not None and expected_artifact_id not in plan["keep"]:
            raise RetentionError("current_artifact_not_retained")
        if apply:
            expected = dict(snapshot)
            for identifier in plan["delete"]:
                fresh, extra = _current_snapshot(repository, expected_artifact_id, expected_run_id, expected_source_revision)
                tries += extra
                fresh_plan = deletion_plan(list(fresh.values()), keep)
                if (fresh != expected or fresh_plan["keep"] != plan["keep"]
                        or fresh_plan["delete"] != [i for i in plan["delete"] if i not in deleted]):
                    raise RetentionError("metadata_changed")
                attempted.append(identifier)
                try:
                    _api("--method", "DELETE", f"repos/{repository}/actions/artifacts/{identifier}")
                except RetentionError:
                    uncertain.append(identifier)
                    raise RetentionError("delete_outcome_unknown") from None
                deleted.append(identifier)
                del expected[identifier]
        return {"ok": True, "status": "applied" if apply else "dry_run", **plan,
                "applied": apply, "deleted": deleted, "listingAttempts": tries,
                "currentArtifactVerified": expected_artifact_id is not None}
    except RetentionError as error:
        error.deleted = deleted.copy()
        error.delete_attempted = attempted.copy()
        error.unconfirmed_delete = uncertain.copy()
        raise


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise RetentionError("invalid_arguments")


def main(argv=None):
    parser = _Parser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--keep", type=int, default=3)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--expected-artifact-id", type=int)
    parser.add_argument("--expected-run-id", type=int)
    parser.add_argument("--expected-source-revision")
    args = None
    try:
        args = parser.parse_args(argv)
        report = run_retention(args.repository, args.keep, apply=args.apply,
            expected_artifact_id=args.expected_artifact_id, expected_run_id=args.expected_run_id,
            expected_source_revision=args.expected_source_revision)
    except RetentionError as error:
        report = {"ok": False, "status": "refused" if not error.delete_attempted else "partial_or_uncertain",
            "reason": error.code, "apply_requested": bool(args and args.apply),
            "deleted": error.deleted, "delete_attempted": error.delete_attempted,
            "unconfirmed_delete": error.unconfirmed_delete}
        if error.metadata_counts is not None:
            report["metadata_counts"] = error.metadata_counts
        print(json.dumps(report))
        return 1
    print(json.dumps(report))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
