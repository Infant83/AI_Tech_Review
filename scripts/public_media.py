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

try:
    from .publication_snapshot import capture_site
    from .reader_engagement_publish import validate_public_artifact
except ImportError:
    from publication_snapshot import capture_site
    from reader_engagement_publish import validate_public_artifact


def worker_manifest_bytes(manifest: dict) -> bytes:
    return ("export default " + json.dumps(manifest, ensure_ascii=False, separators=(",", ":")) + ";\n").encode("utf-8")


def export_media(site: Path, output: Path, *, validate=True) -> dict:
    site, output = Path(site), Path(output)
    if output.is_symlink() or output.exists():
        raise ValueError("Media export must use a new directory")
    if output.resolve().is_relative_to(site.resolve()) or site.resolve().is_relative_to(output.resolve()):
        raise ValueError("Media export must be outside the public site")
    if validate:
        validate_public_artifact(site)
    snapshot = capture_site(site)
    manifest = {"version": 1, "scope": "/AI_Tech_Review/", "objects": {}, "aliases": {}}
    output.mkdir(parents=True)
    for name, record in snapshot["files"].items():
        if not name.endswith(".pdf"):
            continue
        digest = record["sha256"]
        key = f"pdf/sha256/{digest[:2]}/{digest}.pdf"
        manifest["aliases"][manifest["scope"] + name] = key
        if key in manifest["objects"]:
            continue
        source = site / name
        if source.is_symlink() or not source.read_bytes().startswith(b"%PDF-"):
            raise ValueError("Invalid public PDF: " + name)
        target = output / "objects" / key
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError("Public PDF changed during export: " + name)
        manifest["objects"][key] = {"sha256": digest, "size_bytes": record["bytes"], "content_type": "application/pdf"}
    (output / "media-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    worker = output / "worker"
    worker.mkdir()
    source = Path(__file__).resolve().parents[1] / ".automation/cloudflare/public-media"
    for name in ("worker.mjs", "serve.mjs", "wrangler.example.jsonc"):
        shutil.copyfile(source / name, worker / name)
    (worker / "manifest.mjs").write_bytes(worker_manifest_bytes(manifest))
    report = {"version": 1, "status": "export_only_no_live_changes", "pdf_aliases": len(manifest["aliases"]),
              "unique_objects": len(manifest["objects"]),
              "local_pdf_bytes": sum(snapshot["files"][name]["bytes"] for name in snapshot["files"] if name.endswith(".pdf")),
              "object_bytes": sum(row["size_bytes"] for row in manifest["objects"].values())}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def verify_export(output: Path) -> dict:
    output = Path(output)
    source = output / "media-manifest.json"
    worker = output / "worker"
    generated = worker / "manifest.mjs"
    if (output.is_symlink() or source.is_symlink() or not source.is_file()
            or worker.is_symlink() or not worker.is_dir()
            or generated.is_symlink() or not generated.is_file()):
        raise ValueError("Media manifests must be regular files in the export")
    manifest = json.loads(source.read_text(encoding="utf-8"))
    if manifest.get("version") != 1:
        raise ValueError("Unknown media manifest")
    if generated.read_bytes() != worker_manifest_bytes(manifest):
        raise ValueError("Worker media manifest differs from the verified export")
    for key, row in manifest["objects"].items():
        digest = row["sha256"]
        if key != f"pdf/sha256/{digest[:2]}/{digest}.pdf" or len(digest) != 64 or any(c not in "abcdef0123456789" for c in digest):
            raise ValueError("Invalid immutable object key")
        path = output / "objects" / key
        if path.is_symlink() or not path.is_file() or path.stat().st_size != row["size_bytes"] or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Missing or corrupt media object: " + key)
    if any(key not in manifest["objects"] for key in manifest["aliases"].values()):
        raise ValueError("Unresolved media alias")
    return {"ok": True, "objects": len(manifest["objects"]), "aliases": len(manifest["aliases"])}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    if args.verify:
        result = verify_export(args.output)
    else:
        if not args.site:
            parser.error("--site is required for export")
        result = export_media(args.site, args.output)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
