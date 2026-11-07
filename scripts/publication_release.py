"""Check a staged release against the actually published source revision.

Generated navigation may change. Published identities and original article/PDF
bytes require continuity or an exact, reviewable per-file change declaration.
This guard complements the public artifact validator and browser verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

try:
    from .publication_snapshot import capture_site, compare_snapshots, read_json, relative_path, SHA, GROUPS
except ImportError:
    from publication_snapshot import capture_site, compare_snapshots, read_json, relative_path, SHA, GROUPS

ROOT = Path(__file__).resolve().parents[1]
LIVE_CATALOG = "https://infant83.io/AI_Tech_Review/reader-publications.json"
LIVE_RELEASE = "https://infant83.io/AI_Tech_Review/publication-release.json"
# Only the verified last release before the artifact snapshot existed may use
# a Git archive bootstrap. Every later deployment must supply its own snapshot.
BOOTSTRAP_REVISION = "faa0bffb2a9bdb3e6d4b539bfe01ba1746a1fdf4"
REVISION = re.compile(r"[a-f0-9]{40}\Z")
DERIVED_LISTING = re.compile(r"assets/listing-images/[a-f0-9]{64}-w(?:480|960|1200)\.webp\Z")
GENERATED = frozenset({
    "index.html", "en/index.html", "archive/index.html", "archive/en/index.html",
    "lectures/index.html", "lectures/en/index.html", "briefings/index.html", "briefings/en/index.html",
    "assets/site.css", "assets/site.js", "assets/archive.css", "assets/archive.js",
    "assets/briefings.css", "assets/briefings.js", "assets/hub-preferences.js",
    "assets/ai-tech-review-icon.svg", "assets/favicon-16x16.png", "assets/favicon-32x32.png",
    "assets/favicon-64x64.png", "assets/apple-touch-icon.png", "favicon.ico",
    "assets/site-search.js", "assets/site-search-core.js", "assets/site-search.css",
    "assets/minisearch.js", "assets/minisearch-LICENSE.txt", "assets/search-records.json",
    "assets/search-assets.json", "assets/listing-images/manifest.json",
    "assets/listing-pages.js",
})


def compatible_record(group: str, before: dict, after: dict) -> bool:
    """Allow adding references/translations while retaining every old identity."""
    old, new = dict(before), dict(after)
    if group in {"reviews", "archive"}:
        if not set(old.pop("references", [])).issubset(new.pop("references", [])):
            return False
    if group == "reviews":
        old_translations, new_translations = old.pop("translations", {}), new.pop("translations", {})
        if any(new_translations.get(language) != record for language, record in old_translations.items()):
            return False
    return old == new


def declarations(directory: Path | None) -> dict:
    result = {}
    if directory is None or not directory.exists():
        return result
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Change declarations must be a regular directory")
    for path in sorted(directory.glob("*.json")):
        document = read_json(path)
        if (not isinstance(document, dict) or set(document) != {"version", "reason", "files"}
                or document["version"] != 1 or not isinstance(document["reason"], str)
                or not document["reason"].strip() or not isinstance(document["files"], dict)):
            raise ValueError("Invalid change declaration: " + path.name)
        for name, hashes in document["files"].items():
            relative_path(name)
            if (not isinstance(hashes, dict) or set(hashes) != {"before", "after"}
                    or not all(isinstance(hashes[key], str) and SHA.fullmatch(hashes[key]) for key in hashes)):
                raise ValueError("Change declaration requires exact before/after content hashes")
            if name in result:
                raise ValueError("Duplicate file in change declarations: " + name)
            result[name] = hashes
    return result


def validate_release(baseline: dict, candidate: dict, changes: dict | None = None) -> dict:
    comparison = compare_snapshots(baseline, candidate)
    blockers = []
    for issue in comparison["blockers"]:
        # These are replaceable build caches, never original covers or article
        # assets. The payload guard separately validates every rendered cover
        # against the current source hash and derivative manifest. Old unused
        # cache variants need not be retained after a cover/encoder update.
        if issue["kind"] == "reference_missing" and DERIVED_LISTING.fullmatch(issue["path"]):
            continue
        if issue["kind"] == "identity_or_references_changed":
            group, identifier = issue["group"], issue["id"]
            if compatible_record(group, baseline[group][identifier], candidate[group][identifier]):
                continue
        blockers.append(issue)
    permitted, undeclared = [], []
    for name in comparison["content_changes"]:
        try:
            from .listing_pagination import is_page_path
        except ImportError:
            from listing_pagination import is_page_path
        if name in GENERATED or DERIVED_LISTING.fullmatch(name) or is_page_path(name):
            permitted.append(name)
            continue
        actual = {"before": baseline["files"][name]["content_sha256"],
                  "after": candidate["files"][name]["content_sha256"]}
        if (changes or {}).get(name) == actual:
            permitted.append(name)
        else:
            undeclared.append(name)
    blockers.extend({"kind": "undeclared_content_change", "path": name} for name in undeclared)
    return {"ok": not blockers, "blockers": blockers, "additions": comparison["additions"],
            "reviewed_changes": permitted, "instrumentation_only_changes": comparison["instrumentation_only_changes"],
            "counts": {name: len(candidate[name]) for name in GROUPS},
            "limits": "Continuity does not prove visual rendering, query quality or API health; run their separate checks."}


def extract_baseline(repo: Path, output: Path, revision: str) -> dict:
    if not REVISION.fullmatch(revision):
        raise ValueError("The deployed revision must be a full Git SHA")
    if output.exists():
        raise ValueError("Baseline output already exists; use a new empty destination")
    probe = subprocess.run(["git", "cat-file", "-e", revision + "^{commit}"], cwd=repo, capture_output=True)
    if probe.returncode:
        subprocess.run(["git", "fetch", "--no-tags", "origin", revision], cwd=repo, check=True, capture_output=True)
    output.mkdir(parents=True)
    process = subprocess.Popen(["git", "archive", revision, "site"], cwd=repo, stdout=subprocess.PIPE)
    try:
        with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
            for member in archive:
                name = relative_path(member.name.rstrip("/"))
                if name != "site" and not name.startswith("site/"):
                    raise ValueError("Unexpected baseline archive path")
                target = output / name
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = archive.extractfile(member)
                    with target.open("wb") as destination:
                        while chunk := source.read(1024 * 1024):
                            destination.write(chunk)
                else:
                    raise ValueError("Linked or special baseline archive member")
        if process.wait() != 0:
            raise ValueError("Could not extract deployed source revision")
    finally:
        if process.stdout:
            process.stdout.close()
        if process.poll() is None:
            process.kill()
            process.wait()
    (output / "revision.txt").write_text(revision + "\n", encoding="utf-8")
    return {"revision": revision, "site": "site"}


def deployed_revision() -> str:
    request = Request(LIVE_CATALOG + "?release_check=" + str(time.time_ns()), headers={"User-Agent": "AI-Tech-Review-release-validation", "Cache-Control": "no-cache"})
    with urlopen(request, timeout=30) as response:
        payload = response.read(2_000_001)
    if len(payload) > 2_000_000:
        raise ValueError("Live publication catalog is too large")
    revision = json.loads(payload)["revision"]
    if not isinstance(revision, str) or not REVISION.fullmatch(revision):
        raise ValueError("Live publication catalog has no valid source revision")
    return revision


def live_baseline(repo: Path, output: Path) -> dict:
    """Read the snapshot packaged in the actual deployment, not committed site/."""
    if output.exists():
        raise ValueError("Baseline output already exists")
    request = Request(LIVE_CATALOG + "?release_check=" + str(time.time_ns()), headers={"User-Agent": "AI-Tech-Review-release-validation", "Cache-Control": "no-cache"})
    with urlopen(request, timeout=30) as response:
        catalog_bytes = response.read(2_000_001)
    if len(catalog_bytes) > 2_000_000:
        raise ValueError("Live catalog exceeds limit")
    catalog = json.loads(catalog_bytes)
    revision = catalog.get("revision", "")
    if not isinstance(revision, str) or not REVISION.fullmatch(revision):
        raise ValueError("Live catalog has invalid revision")
    try:
        request = Request(LIVE_RELEASE + "?release_check=" + str(time.time_ns()), headers={"User-Agent": "AI-Tech-Review-release-validation", "Cache-Control": "no-cache"})
        with urlopen(request, timeout=30) as response:
            payload = response.read(5_000_001)
        if len(payload) > 5_000_000:
            raise ValueError("Live release snapshot exceeds limit")
        release = json.loads(payload)
        if (release.get("version") != 1 or release.get("revision") != revision
                or release.get("catalog_sha256") != hashlib.sha256(catalog_bytes).hexdigest()):
            raise ValueError("Deployed catalog and release snapshot do not describe the same artifact; retry after deployment settles")
        snapshot, page_sizes = release["snapshot"], release["initial_payloads"]
        if not validate_release(snapshot, snapshot)["ok"]:
            raise ValueError("Deployed release snapshot is not internally valid")
        output.mkdir(parents=True)
        source = "deployed_artifact_snapshot"
    except HTTPError as error:
        if error.code != 404 or revision != BOOTSTRAP_REVISION:
            raise ValueError("Deployed artifact snapshot is unavailable; do not substitute a source checkout") from error
        extract_baseline(repo, output, revision)
        snapshot = capture_site(output / "site")
        # Bootstrap has a known, manually verified immutable predecessor. Its
        # published catalog still must agree with the registered identities.
        actual = {a["id"]: {key: a.get(key) for key in ("path", "topic", "publishedAt")} for a in catalog["articles"]}
        if snapshot["publications"] != actual:
            raise ValueError("Bootstrap source identities differ from the live deployment")
        try:
            from .site_payload_budget import page_payload, PAGES
        except ImportError:
            from site_payload_budget import page_payload, PAGES
        page_sizes = {name: page_payload(output / "site", name)["gzip_bytes"] for name in PAGES if (output / "site" / name).is_file()}
        source = "verified_pre_snapshot_bootstrap"
    (output / "snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "payload.json").write_text(json.dumps(page_sizes, indent=2) + "\n", encoding="utf-8")
    (output / "revision.txt").write_text(revision + "\n", encoding="utf-8")
    return {"revision": revision, "source": source}


def seal_release(site: Path, revision: str, payload_report: Path) -> dict:
    if not REVISION.fullmatch(revision):
        raise ValueError("Release requires exact source revision")
    catalog_bytes = (site / "reader-publications.json").read_bytes()
    if json.loads(catalog_bytes).get("revision") != revision:
        raise ValueError("Release revision differs from its catalog")
    payload = read_json(payload_report)
    if payload.get("ok") is not True:
        raise ValueError("A release must pass payload checks before sealing")
    snapshot = capture_site(site)
    if not validate_release(snapshot, snapshot)["ok"]:
        raise ValueError("A release must pass structural checks before sealing")
    complete_files = {}
    for path in sorted(site.rglob("*")):
        if path.is_symlink():
            raise ValueError("Cannot seal linked artifact files")
        if path.is_file() and path != site / "publication-release.json":
            complete_files[path.relative_to(site).as_posix()] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size}
    result = {"version": 1, "revision": revision, "catalog_sha256": hashlib.sha256(catalog_bytes).hexdigest(),
              "snapshot": snapshot, "artifact_files": complete_files,
              "initial_payloads": {name: record["gzip_bytes"] for name, record in payload["pages"].items()}}
    # This root-level file is deliberately outside capture_site's referenced
    # assets, avoiding a self-referential checksum. It is fetched by CI only.
    (site / "publication-release.json").write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    return {"revision": revision, "snapshot_files": len(snapshot["files"])}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    baseline = actions.add_parser("baseline")
    baseline.add_argument("--repo", type=Path, default=ROOT)
    baseline.add_argument("--output", type=Path, required=True)
    baseline.add_argument("--revision", help="Explicit previously approved revision; omission reads live HTTPS catalog")
    check = actions.add_parser("check")
    baseline_input = check.add_mutually_exclusive_group(required=True)
    baseline_input.add_argument("--baseline-site", type=Path)
    baseline_input.add_argument("--baseline-snapshot", type=Path)
    check.add_argument("--site", type=Path, required=True)
    check.add_argument("--changes", type=Path, default=ROOT / "publication_changes")
    check.add_argument("--output", type=Path)
    seal = actions.add_parser("seal")
    seal.add_argument("--site", type=Path, required=True)
    seal.add_argument("--revision", required=True)
    seal.add_argument("--payload-report", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == "baseline":
            result = extract_baseline(args.repo, args.output, args.revision) if args.revision else live_baseline(args.repo, args.output)
        elif args.action == "seal":
            result = seal_release(args.site, args.revision, args.payload_report)
        else:
            prior = read_json(args.baseline_snapshot) if args.baseline_snapshot else capture_site(args.baseline_site)
            result = validate_release(prior, capture_site(args.site), declarations(args.changes))
        payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if getattr(args, "output", None) is not None and args.action == "check":
            if args.output.resolve().is_relative_to(args.site.resolve()):
                raise ValueError("Validation report must remain outside the public site")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding="utf-8")
        print(payload, end="")
        return 0 if result.get("ok", True) else 1
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(json.dumps({"error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
