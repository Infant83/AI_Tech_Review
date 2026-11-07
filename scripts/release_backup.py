"""Create, verify and restore a complete portable public-release recovery copy.

This backs up public static bytes only, not private D1 data or reader notebooks.
It does not deploy, publish notifications or bypass continuity checks.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tarfile
import tempfile

FORMAT = "ai-tech-review-public-release"
LIMIT = 1_500_000_000


def safe_name(name):
    if not isinstance(name, str) or not name or name.startswith("/") or "\\" in name or any(ord(c) < 32 for c in name):
        raise ValueError("Unsafe recovery path")
    if any(part in {"", ".", ".."} for part in name.split("/")):
        raise ValueError("Unsafe recovery path")
    return name


def digest_stream(handle):
    """Streaming SHA-256 compatible with the existing Python 3.9 CLI."""
    digest = hashlib.sha256()
    while chunk := handle.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


def digest_file(path):
    with path.open("rb") as handle:
        return digest_stream(handle)


def create_backup(site: Path, destination: Path):
    site, destination = Path(site), Path(destination)
    if site.is_symlink() or not site.is_dir() or destination.exists() or destination.is_symlink():
        raise ValueError("Recovery copy requires a regular site and a new destination")
    if destination.resolve().is_relative_to(site.resolve()):
        raise ValueError("Recovery copy must be outside the public artifact")
    release_path = site / "publication-release.json"
    release = json.loads(release_path.read_text())
    catalog = site / "reader-publications.json"
    if (release.get("version") != 1 or not re.fullmatch(r"[a-f0-9]{40}", release.get("revision", ""))
            or release.get("catalog_sha256") != digest_file(catalog)
            or json.loads(catalog.read_text()).get("revision") != release["revision"]):
        raise ValueError("Recovery copy requires matching sealed release and catalog")
    files = {}
    for path in sorted(site.rglob("*")):
        if path.is_symlink() or (not path.is_dir() and not path.is_file()):
            raise ValueError("Links and special files are not recovery material")
        if path.is_file():
            name = safe_name(path.relative_to(site).as_posix())
            files[name] = {"sha256": digest_file(path), "bytes": path.stat().st_size}
    if sum(row["bytes"] for row in files.values()) > LIMIT:
        raise ValueError("Recovery copy exceeds static artifact safety limit")
    # A full-file hash map in the seal must still describe these exact bytes.
    for name, row in release.get("snapshot", {}).get("files", {}).items():
        if name not in files or files[name]["sha256"] != row["sha256"]:
            raise ValueError("Sealed artifact changed before backup: " + name)
    if "artifact_files" in release and release["artifact_files"] != {name: row for name, row in files.items() if name != "publication-release.json"}:
        raise ValueError("Complete sealed file inventory differs from the recovery input")
    metadata = {"format": FORMAT, "version": 1, "revision": release["revision"],
                "created_at": datetime.now(timezone.utc).isoformat(), "files": files}
    payload = (json.dumps(metadata, sort_keys=True, separators=(",", ":")) + "\n").encode()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".release-", suffix=".tar.gz", dir=destination.parent)
    os.close(fd)
    try:
        with tarfile.open(temporary, "w:gz", compresslevel=3) as archive:
            info = tarfile.TarInfo("recovery.json"); info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
            for name in files:
                archive.add(site / name, arcname="site/" + name, recursive=False)
        report = verify_backup(Path(temporary))
        # Install exclusively: another agent may have completed this same named
        # recovery copy while compression/verification was running.
        os.link(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return {**report, "archive_sha256": digest_file(destination)}


def verify_backup(path: Path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("Recovery archive must be a regular file")
    with tarfile.open(path, "r|gz") as archive:
        first = archive.next()
        if first is None or first.name != "recovery.json" or not first.isfile() or first.size > 5_000_000:
            raise ValueError("Missing recovery manifest")
        metadata = json.load(archive.extractfile(first))
        if (metadata.get("format") != FORMAT or metadata.get("version") != 1
                or not re.fullmatch(r"[a-f0-9]{40}", metadata.get("revision", ""))
                or not isinstance(metadata.get("files"), dict)):
            raise ValueError("Invalid recovery manifest")
        expected = metadata["files"]
        for name, row in expected.items():
            safe_name(name)
            if (not isinstance(row, dict) or set(row) != {"sha256", "bytes"}
                    or type(row["bytes"]) is not int or row["bytes"] < 0
                    or not re.fullmatch(r"[a-f0-9]{64}", row["sha256"])):
                raise ValueError("Invalid recovery file record")
        if sum(row["bytes"] for row in expected.values()) > LIMIT:
            raise ValueError("Recovery archive exceeds safety limit")
        seen, identities = set(), {}
        # Streaming member iteration starts after the explicitly read first item.
        while (member := archive.next()) is not None:
            safe_name(member.name)
            if not member.isfile() or not member.name.startswith("site/"):
                raise ValueError("Unexpected recovery member")
            name = member.name[5:]
            if name not in expected or name in seen or member.size != expected[name]["bytes"]:
                raise ValueError("Unexpected or duplicate recovery file")
            source = archive.extractfile(member)
            if name in {"reader-publications.json", "publication-release.json"}:
                if member.size > 5_000_000:
                    raise ValueError("Oversized recovery identity metadata")
                identities[name] = source.read()
                actual_hash = hashlib.sha256(identities[name]).hexdigest()
            else:
                actual_hash = digest_stream(source)
            if actual_hash != expected[name]["sha256"]:
                raise ValueError("Corrupt recovery file: " + name)
            seen.add(name)
        if seen != set(expected):
            raise ValueError("Recovery archive is incomplete")
        if set(identities) != {"reader-publications.json", "publication-release.json"}:
            raise ValueError("Recovery archive lacks the sealed publication identities")
        catalog = json.loads(identities["reader-publications.json"])
        release = json.loads(identities["publication-release.json"])
        if (catalog.get("revision") != metadata["revision"] or release.get("revision") != metadata["revision"]
                or release.get("version") != 1
                or release.get("catalog_sha256") != hashlib.sha256(identities["reader-publications.json"]).hexdigest()):
            raise ValueError("Recovery revision, catalog and seal do not agree")
        for name, row in release.get("snapshot", {}).get("files", {}).items():
            if name not in expected or expected[name]["sha256"] != row["sha256"]:
                raise ValueError("Recovery file differs from the publication seal")
        if "artifact_files" in release and release["artifact_files"] != {name: row for name, row in expected.items() if name != "publication-release.json"}:
            raise ValueError("Recovery file inventory differs from the complete publication seal")
    return {"ok": True, "revision": metadata["revision"], "files": len(seen),
            "bytes": sum(row["bytes"] for row in expected.values())}


def restore_backup(path: Path, output: Path):
    report = verify_backup(path)
    if output.exists() or output.is_symlink():
        raise ValueError("Restore destination must be new")
    output.mkdir(parents=True)
    with tarfile.open(path, "r:gz") as archive:
        for member in archive:
            if member.name == "recovery.json":
                continue
            safe_name(member.name)
            if not member.isfile() or not member.name.startswith("site/"):
                raise ValueError("Unexpected recovery member")
            target = output / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, target.open("xb") as handle:
                while chunk := source.read(1024 * 1024): handle.write(chunk)
    return {**report, "status": "restored_only_not_deployed"}


def import_pages(path: Path, output: Path):
    """Read the tar produced by upload-pages-artifact without unsafe extraction."""
    if output.exists() or output.is_symlink():
        raise ValueError("Pages import destination must be new")
    output.mkdir(parents=True)
    seen, total = set(), 0
    with tarfile.open(path, "r:*") as archive:
        for member in archive:
            name = member.name
            while name.startswith("./"): name = name[2:]
            if name in {"", "."} and member.isdir(): continue
            safe_name(name.rstrip("/") if member.isdir() else name)
            if member.isdir(): continue
            total += member.size
            if not member.isfile() or name in seen or total > LIMIT:
                raise ValueError("Unsafe or oversized Pages artifact")
            seen.add(name)
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.extractfile(member) as source, target.open("xb") as handle:
                while chunk := source.read(1024 * 1024): handle.write(chunk)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create"); create.add_argument("--site", required=True, type=Path); create.add_argument("--output", required=True, type=Path)
    verify = sub.add_parser("verify"); verify.add_argument("--archive", required=True, type=Path)
    restore = sub.add_parser("restore"); restore.add_argument("--archive", required=True, type=Path); restore.add_argument("--output", required=True, type=Path)
    pages = sub.add_parser("from-pages"); pages.add_argument("--archive", required=True, type=Path); pages.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    if args.command == "create": result = create_backup(args.site, args.output)
    elif args.command == "verify": result = verify_backup(args.archive)
    elif args.command == "restore": result = restore_backup(args.archive, args.output)
    else:
        with tempfile.TemporaryDirectory(prefix="pages-recovery-") as temporary:
            site = Path(temporary) / "site"
            import_pages(args.archive, site)
            result = create_backup(site, args.output)
    print(json.dumps(result))

if __name__ == "__main__": main()
