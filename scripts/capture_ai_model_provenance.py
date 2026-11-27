"""Explicit authoring-time Codex model capture; never run automatically in CI.

Save the strict public JSON separately from private session evidence. The latter
must be outside every Git checkout. Existing different records are not replaced;
use new capture paths for later editorial work or revisions.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

try:
    from .ai_model_provenance import ProvenanceError, collect_participants, default_participant
except ImportError:
    from ai_model_provenance import ProvenanceError, collect_participants, default_participant


def _outside_git(path: Path) -> bool:
    return not any((parent / ".git").exists() for parent in (path.parent, *path.parents))


def _target(value: Path, *, private: bool) -> Path:
    value = value.expanduser()
    if value.is_symlink() or value.suffix != ".json":
        raise ProvenanceError("Capture outputs must be regular JSON paths")
    target = value.expanduser().resolve()
    if private and not _outside_git(target):
        raise ProvenanceError("Private model evidence must be outside Git checkouts")
    return target


def _check_existing(path: Path, content: bytes) -> None:
    if path.exists() and (not path.is_file() or path.stat().st_size != len(content) or path.read_bytes() != content):
        raise ProvenanceError("A different capture already exists; use a new capture path")


def _write(path: Path, content: bytes, mode: int) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, pending = tempfile.mkstemp(prefix=".model-provenance-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            os.fchmod(handle.fileno(), mode)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        # Refuse an output that appeared after validation; do not overwrite it.
        if path.exists():
            _check_existing(path, content)
        else:
            os.link(pending, path)
    finally:
        Path(pending).unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--participant", action="append", default=[], metavar="ROLE=UUID",
                        help="Explicit worker identity; repeat for writer/reviewers")
    parser.add_argument("--role", default="authoring", help="Role used only with current CODEX_THREAD_ID")
    parser.add_argument("--since", help="Timezone-bearing lower bound; keeps all settings in the interval")
    parser.add_argument("--until", help="Timezone-bearing upper bound; without --since selects the latest preceding context")
    parser.add_argument("--codex-home", type=Path, help="Optional Codex metadata directory")
    parser.add_argument("--output", required=True, type=Path, help="Saved public model-provenance JSON")
    parser.add_argument("--private-evidence", required=True, type=Path, help="Separate private JSON outside Git")
    args = parser.parse_args(argv)
    try:
        public_path = _target(args.output, private=False)
        private_path = _target(args.private_evidence, private=True)
        if public_path == private_path:
            raise ProvenanceError("Public and private capture paths must differ")
        participants = []
        if args.participant:
            for supplied in args.participant:
                parts = supplied.split("=")
                if len(parts) != 2:
                    raise ProvenanceError("Participants must use ROLE=UUID")
                participants.append(tuple(parts))
        else:
            participants.append(default_participant(args.role))
        public, private = collect_participants(participants, since=args.since, until=args.until,
                                               codex_home=args.codex_home)
        private["public_record"] = public
        public_bytes = (json.dumps(public, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        private_bytes = (json.dumps(private, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        _check_existing(public_path, public_bytes)
        _check_existing(private_path, private_bytes)
        _write(private_path, private_bytes, 0o600)
        _write(public_path, public_bytes, 0o644)
    except (ProvenanceError, OSError) as error:
        # Static provenance errors are safe. OS errors can contain private paths.
        message = str(error) if isinstance(error, ProvenanceError) else "Unable to read or save the selected provenance inputs"
        print("AI model provenance capture failed: " + message, file=sys.stderr)
        return 2
    print(f"Saved public AI model provenance ({len(public['roles'])} role-setting records); private evidence is separate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
