"""Export approved public PDFs once per SHA-256 for portable object storage.

This is preparation, not activation: no live routes are changed and no PDFs are
removed from the static artifact. Verify uploaded bytes before switching routes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import re

try:
    from .publication_snapshot import capture_site
    from .reader_engagement_publish import validate_public_artifact
except ImportError:
    from publication_snapshot import capture_site
    from reader_engagement_publish import validate_public_artifact


def worker_manifest_bytes(manifest: dict) -> bytes:
    return ("export default " + json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + ";\n").encode("utf-8")


SCOPE = "/AI_Tech_Review/"
SHA256 = re.compile(r"[a-f0-9]{64}\Z")


def object_key(digest: str) -> str:
    if not isinstance(digest, str) or not SHA256.fullmatch(digest):
        raise ValueError("Invalid immutable object SHA")
    return f"pdf/sha256/{digest[:2]}/{digest}.pdf"


def regular_file(path: Path, root: Path) -> bool:
    """Reject links in the export/site, including object directory components."""
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        return False
    current = root
    if root.is_symlink() or not root.is_dir():
        return False
    for part in parts:
        current = current / part
        if current.is_symlink():
            return False
    return path.is_file()


def valid_alias(path) -> bool:
    return (isinstance(path, str) and path.startswith(SCOPE) and path.endswith(".pdf")
            and not any(c in path for c in "\\?#%\x00")
            and not any(part in ("", ".", "..") for part in path[1:].split("/")))


def manifest_editions(manifest: dict) -> dict:
    """Validate v1/v2 mappings and normalize each alias to its allowed editions.

    V1 is accepted only as a fully verified local input, with its single current
    edition. It is never an instruction to revive a removed public URL.
    """
    if (type(manifest) is not dict or set(manifest) != {"version", "scope", "objects", "aliases"}
            or type(manifest["version"]) is not int or manifest["version"] not in (1, 2)
            or manifest["scope"] != SCOPE or type(manifest["objects"]) is not dict
            or type(manifest["aliases"]) is not dict):
        raise ValueError("Unknown media manifest")
    objects = manifest["objects"]
    for key, row in objects.items():
        if (type(row) is not dict or set(row) != {"sha256", "size_bytes", "content_type"}
                or key != object_key(row["sha256"]) or type(row["size_bytes"]) is not int
                or not 0 < row["size_bytes"] <= 9007199254740991
                or row["content_type"] != "application/pdf"):
            raise ValueError("Invalid immutable object metadata")
    result, referenced = {}, set()
    for path, entry in manifest["aliases"].items():
        if not valid_alias(path):
            raise ValueError("Invalid public PDF alias")
        if manifest["version"] == 1:
            if not isinstance(entry, str) or entry not in objects:
                raise ValueError("Unresolved media alias")
            current = objects[entry]["sha256"]
            editions = {current: entry}
        else:
            if (type(entry) is not dict or set(entry) != {"current", "editions"}
                    or type(entry["editions"]) is not dict or not entry["editions"]
                    or not isinstance(entry["current"], str)
                    or entry["current"] not in entry["editions"]):
                raise ValueError("Invalid media editions")
            current, editions = entry["current"], entry["editions"]
        for digest, key in editions.items():
            if (key != object_key(digest) or key not in objects
                    or objects[key]["sha256"] != digest):
                raise ValueError("Unresolved or inconsistent media edition")
            referenced.add(key)
        result[path] = {"current": current, "editions": dict(editions)}
    if set(objects) != referenced:
        raise ValueError("Unreferenced media object")
    return result


def unique_json(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate media manifest key")
        result[key] = value
    return result


def verified_manifest(output: Path) -> dict:
    output = Path(output)
    source, generated = output / "media-manifest.json", output / "worker/manifest.mjs"
    if not regular_file(source, output) or not regular_file(generated, output):
        raise ValueError("Media manifests must be regular files in the export")
    manifest = json.loads(source.read_text(encoding="utf-8"), object_pairs_hook=unique_json)
    if generated.read_bytes() != worker_manifest_bytes(manifest):
        raise ValueError("Worker media manifest differs from the verified export")
    manifest_editions(manifest)
    for key, row in manifest["objects"].items():
        path = output / "objects" / key
        if not regular_file(path, output) or path.stat().st_size != row["size_bytes"]:
            raise ValueError("Missing or corrupt media object: " + key)
        payload = path.read_bytes()
        if not payload.startswith(b"%PDF-") or hashlib.sha256(payload).hexdigest() != row["sha256"]:
            raise ValueError("Missing or corrupt media object: " + key)
    return manifest


def export_media(site: Path, output: Path, *, validate=True, previous_exports=()) -> dict:
    site, output = Path(site), Path(output)
    if output.is_symlink() or output.exists():
        raise ValueError("Media export must use a new directory")
    if output.resolve().is_relative_to(site.resolve()) or site.resolve().is_relative_to(output.resolve()):
        raise ValueError("Media export must be outside the public site")
    if validate:
        validate_public_artifact(site)
    # Validate all prior exports before creating any output. Never accept an
    # arbitrary JSON mapping in place of its fully checked local object bytes.
    previous = [(Path(path), verified_manifest(Path(path))) for path in previous_exports]
    snapshot = capture_site(site)
    manifest = {"version": 2, "scope": SCOPE, "objects": {}, "aliases": {}}
    output.mkdir(parents=True)
    for name, record in snapshot["files"].items():
        if not name.endswith(".pdf"):
            continue
        if not valid_alias(SCOPE + name):
            raise ValueError("Invalid public PDF alias")
        digest = record["sha256"]
        key = object_key(digest)
        manifest["aliases"][SCOPE + name] = {"current": digest, "editions": {digest: key}}
        if key in manifest["objects"]:
            continue
        source = site / name
        if not regular_file(source, site) or not source.read_bytes().startswith(b"%PDF-"):
            raise ValueError("Invalid public PDF: " + name)
        target = output / "objects" / key
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError("Public PDF changed during export: " + name)
        manifest["objects"][key] = {"sha256": digest, "size_bytes": record["bytes"], "content_type": "application/pdf"}
    for prior_root, prior in previous:
        for path, entry in manifest_editions(prior).items():
            if path not in manifest["aliases"]:
                continue  # Removed/private aliases must not be resurrected.
            allowed = manifest["aliases"][path]["editions"]
            for digest, key in entry["editions"].items():
                allowed[digest] = key
                row = prior["objects"][key]
                if key in manifest["objects"]:
                    if manifest["objects"][key] != row:
                        raise ValueError("Conflicting immutable object metadata")
                    continue
                target = output / "objects" / key
                target.parent.mkdir(parents=True, exist_ok=True)
                if not regular_file(prior_root / "objects" / key, prior_root):
                    raise ValueError("Prior media object changed during export")
                shutil.copyfile(prior_root / "objects" / key, target)
                manifest["objects"][key] = dict(row)
    manifest_editions(manifest)
    (output / "media-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    worker = output / "worker"
    worker.mkdir()
    source = Path(__file__).resolve().parents[1] / ".automation/cloudflare/public-media"
    for name in ("worker.mjs", "serve.mjs", "wrangler.example.jsonc"):
        shutil.copyfile(source / name, worker / name)
    (worker / "manifest.mjs").write_bytes(worker_manifest_bytes(manifest))
    # Also rehash copied prior bytes, catching a source change after validation.
    verify_export(output)
    report = {"version": 2, "status": "export_only_no_live_changes", "pdf_aliases": len(manifest["aliases"]),
              "unique_objects": len(manifest["objects"]),
              "allowed_editions": sum(len(row["editions"]) for row in manifest["aliases"].values()),
              "local_pdf_bytes": sum(snapshot["files"][name]["bytes"] for name in snapshot["files"] if name.endswith(".pdf")),
              "object_bytes": sum(row["size_bytes"] for row in manifest["objects"].values())}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def verify_export(output: Path) -> dict:
    manifest = verified_manifest(Path(output))
    return {"ok": True, "objects": len(manifest["objects"]), "aliases": len(manifest["aliases"])}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--previous-export", type=Path, action="append", default=[],
                        help="Fully verified v1/v2 export; retain editions only for still-public aliases")
    args = parser.parse_args(argv)
    if args.verify:
        result = verify_export(args.output)
    else:
        if not args.site:
            parser.error("--site is required for export")
        result = export_media(args.site, args.output, previous_exports=args.previous_export)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
