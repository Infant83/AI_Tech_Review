"""Add reader controls without rebuilding articles; sync only verified Pages output."""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SCOPE = "/AI_Tech_Review/"
SITE_ROOT = "https://infant83.io" + SCOPE
API_BASE = "https://api.infant83.io"
CATALOG_NAME = "reader-publications.json"
UPDATES_NAME = "reader-updates.json"
FRONTEND_DIR = ROOT / ".automation/reader-engagement/frontend"
ASSET_EXCEPTIONS = ROOT / ".automation/reader-engagement/public-asset-exceptions.json"
ASSETS = {
    "reader-engagement.js": "assets/reader-engagement.js",
    "reader-updates.js": "assets/reader-updates.js",
    "reader-engagement.css": "assets/reader-engagement.css",
    "app.webmanifest": "app.webmanifest",
    "sw.js": "sw.js",
}
BLOCKS = ("Reader Engagement Head", "Reader Engagement Controls")
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
CONTENT_SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9:_-]{0,179}\Z")
PUBLIC_ROOT_FILES = {"index.html", "manifest.json", "archive-manifest.json", "favicon.ico",
                     ".nojekyll", "CNAME", "sw.js", "app.webmanifest", CATALOG_NAME, UPDATES_NAME}
PUBLIC_DIRECTORIES = {"assets", "reviews", "lectures", "archive", "briefings", "methods", "en"}
PUBLIC_EXTENSIONS = {".html", ".css", ".js", ".json", ".webmanifest", ".svg", ".pdf", ".png",
                     ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".woff", ".woff2", ".txt",
                     ".py", ".csv", ".mp4", ".vtt"}
PUBLIC_TEXT_EXTENSIONS = {".html", ".css", ".js", ".json", ".webmanifest", ".svg", ".txt", ".py", ".csv", ".vtt"}
PRIVATE_NAMES = re.compile(r"(?:^\.env(?:\.|$)|^\.dev\.vars(?:\.|$)|^wrangler\.|^id_(?:rsa|ed25519)|"
                           r"(?:^|[._-])(?:credential|credentials|secret|secrets)(?:[._-]|$)|"
                           r"(?:\.pem|\.key|\.p12|\.pfx|\.sqlite|\.sqlite3|\.db|\.sql|\.bak|\.log|~)$)", re.I)
RASTER_DATA_URI = re.compile(r"data:image/(png|jpe?g|gif|webp);base64,([A-Za-z0-9+/=]+)", re.I)


def public_path(href: str) -> str:
    parts = urlsplit(href)
    if (parts.scheme or parts.netloc or parts.query or parts.fragment
            or href.startswith("/") or "\\" in href or "//" in href
            or any(p in {".", ".."} for p in href.split("/"))
            or not re.fullmatch(r"[A-Za-z0-9_./-]+", href)):
        raise ValueError(f"Not a relative public article path: {href!r}")
    return SCOPE + re.sub(r"(?:^|/)index\.html$", lambda m: "/" if m.group().startswith("/") else "", href)


def publication(identifier: str, href: str, title: str, published: str, topic: str) -> dict:
    if not all(isinstance(value, str) for value in (identifier, href, title, published, topic)):
        raise ValueError("Publication fields must be strings")
    if not ID_RE.fullmatch(identifier) or topic not in {"review", "lecture"}:
        raise ValueError("Invalid publication identifier or topic")
    if not title.strip() or len(title) > 240 or date.fromisoformat(published).isoformat() != published:
        raise ValueError("Invalid publication title or original publication date")
    path = public_path(href)
    allowed = path.startswith(SCOPE + "reviews/") if topic == "review" else (
        path.startswith(SCOPE + "lectures/") or (path.startswith(SCOPE + "archive/files/") and path.endswith(".pdf")))
    if not allowed:
        raise ValueError("Publication path does not match its topic")
    if topic == "review" and path != SCOPE + "reviews/" + identifier + "/":
        raise ValueError("Review identifier does not match its canonical path")
    return {"id": identifier, "path": path, "title": title,
            "publishedAt": published, "topic": topic}


def load_publications(site_dir: Path) -> tuple[list[dict], dict[str, dict]]:
    reviews = json.loads((site_dir / "manifest.json").read_text(encoding="utf-8"))
    articles, pages = [], {}
    for review in reviews:
        article = publication(review["folder"], review["href"], review["title"], review["date"], "review")
        articles.append(article)
        for href in [review["href"], *(t["href"] for t in review.get("translations", []))]:
            public_path(href)  # Validate aliases too; translated pages share one article id.
            pages[href] = article
    archive_path = site_dir / "archive-manifest.json"
    archive = json.loads(archive_path.read_text(encoding="utf-8")) if archive_path.exists() else {}
    for document in archive.get("documents", []):
        if document.get("series") != "lecture-notes":
            continue
        href = document.get("study_href") or document["href"]
        article = publication("lecture:" + document["id"], href, document["title"], document["date"], "lecture")
        articles.append(article)
        if document.get("study_href"):
            pages[href.rstrip("/") + "/index.html"] = article
    if len({a["id"] for a in articles}) != len(articles) or len({a["path"] for a in articles}) != len(articles):
        raise ValueError("Duplicate publication ids or canonical paths")
    return sorted(articles, key=lambda a: (a["publishedAt"], a["id"]), reverse=True), pages


def json_script(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("&", "\\u0026")


def strip_engagement(text: str) -> str:
    for marker in BLOCKS:
        text = re.sub(r"<!-- " + marker + r" -->.*?<!-- End " + marker + r" -->\r?\n?", "", text, flags=re.DOTALL)
    return text


def enrich_html(text: str, relative_path: str, article: dict | None,
                *, asset_versions: dict[str, str] | None = None, article_version: str | None = None) -> str:
    text = strip_engagement(text)
    if not re.search(r"</head\s*>", text, re.I) or not re.search(r"</body\s*>", text, re.I):
        return text
    newline = "\r\n" if "\r\n" in text else "\n"
    prefix = os.path.relpath(".", str(Path(relative_path).parent)).replace("\\", "/")
    prefix = "" if prefix == "." else prefix.rstrip("/") + "/"
    config = {"apiBase": API_BASE, "siteRoot": SITE_ROOT, "scope": SCOPE,
              "catalogUrl": SITE_ROOT + CATALOG_NAME, "article": article,
              "updatesUrl": SITE_ROOT + UPDATES_NAME,
              "pageVersion": hashlib.sha256(text.encode("utf-8")).hexdigest(),
              "articleVersion": article_version}
    versions = asset_versions or {}
    def asset_href(name: str) -> str:
        suffix = "?v=" + versions[name] if versions.get(name) else ""
        return html.escape(prefix + "assets/" + name + suffix, quote=True)
    head = (f'<!-- {BLOCKS[0]} -->\n'
            f'<link rel="manifest" href="{html.escape(prefix, quote=True)}app.webmanifest">\n'
            f'<link rel="stylesheet" href="{asset_href("reader-engagement.css")}">\n'
            f'<!-- End {BLOCKS[0]} -->\n')
    controls = (f'<!-- {BLOCKS[1]} -->\n'
                f'<script type="application/json" id="reader-engagement-config">{json_script(config)}</script>\n'
                f'<script defer src="{asset_href("reader-engagement.js")}"></script>\n'
                f'<script defer src="{asset_href("reader-updates.js")}"></script>\n'
                f'<!-- End {BLOCKS[1]} -->\n')
    return re.sub(r"[ \t]*</body\s*>", lambda m: controls.replace("\n", newline) + m.group(),
                  re.sub(r"[ \t]*</head\s*>", lambda m: head.replace("\n", newline) + m.group(), text, count=1, flags=re.I),
                  count=1, flags=re.I)


def write_changed(path: Path, payload: bytes) -> bool:
    if path.exists() and path.read_bytes() == payload:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return True


def content_digest(path: Path) -> str:
    """Hash public content, excluding the injected reader controls and metadata."""
    if path.is_symlink() or not path.is_file():
        raise ValueError("Missing or symlinked update content: " + path.name)
    payload = path.read_bytes()
    if path.suffix == ".html":
        payload = strip_engagement(payload.decode("utf-8")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_updates(site_dir: Path, previous: dict | None = None, *, now: str | None = None) -> dict:
    """Create device-local recency metadata independently of the push catalog.

    Explicit article assets determine editorial revisions. Global reader assets,
    counters and deployment commits never make every old article look updated.
    """
    previous_articles = {item["id"]: item for item in (previous or {}).get("articles", [])
                         if isinstance(item, dict) and isinstance(item.get("id"), str)}
    timestamp = now or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    pages = {public_path(path.relative_to(site_dir).as_posix()): content_digest(path)
             for path in sorted(site_dir.rglob("*.html"))}
    reviews = json.loads((site_dir / "manifest.json").read_text(encoding="utf-8"))
    archive_file = site_dir / "archive-manifest.json"
    documents = json.loads(archive_file.read_text(encoding="utf-8")).get("documents", []) if archive_file.exists() else []
    records, pdf_owners, path_owners = [], {}, {}

    def add(identifier: str, title: str, published: str, hrefs: list[str], assets: list[str], updated: str | None = None) -> dict:
        paths = sorted(set(public_path(href) for href in hrefs))
        if not ID_RE.fullmatch(identifier) or not title.strip() or date.fromisoformat(published).isoformat() != published:
            raise ValueError("Invalid article update metadata")
        hashes = {name: content_digest(site_dir / name) for name in sorted(set(assets))}
        digest = hashlib.sha256(json_script({"title": title, "content": hashes}).encode("utf-8")).hexdigest()
        old = previous_articles.get(identifier)
        initial_day = max(published, updated or published)
        date.fromisoformat(initial_day)
        updated_at = initial_day + "T00:00:00Z"
        change = "updated" if initial_day > published else "new"
        if old:
            unchanged = old.get("revision") == digest
            updated_at = old.get("updatedAt", updated_at) if unchanged else timestamp
            change = old.get("change", change) if unchanged else "updated"
        record = {"id": identifier, "path": public_path(hrefs[0]), "paths": paths, "title": title,
                  "publishedAt": published, "revision": digest, "updatedAt": updated_at, "change": change}
        records.append(record)
        for path in paths:
            path_owners[path] = record
        for name, checksum in hashes.items():
            if name.endswith(".pdf"):
                pdf_owners.setdefault(checksum, record)
        return record

    for review in reviews:
        hrefs, assets = [], []
        for variant in [review, *review.get("translations", [])]:
            href = variant["href"]
            public_path(href)
            hrefs.append(href)
            assets.append(href)
            for name in variant.get("assets", []):
                asset = (Path(href).parent / name).as_posix()
                public_path(asset)
                assets.append(asset)
                if asset.endswith(".pdf"):
                    hrefs.append(asset)
        add(review["folder"], review["title"], review["date"], hrefs, assets, review.get("updated"))

    for document in documents:
        href = document["href"]
        pdf_path = public_path(href)
        checksum = content_digest(site_dir / href)
        owner = path_owners.get(pdf_path) or pdf_owners.get(checksum)
        if owner:
            owner["paths"] = sorted(set([*owner["paths"], pdf_path]))
            path_owners[pdf_path] = owner
            continue
        study = document.get("study_href")
        hrefs, assets = [href], [href]
        if study:
            public_path(study)
            main = study.rstrip("/") + "/index.html"
            hrefs.insert(0, main)
            assets.append(main)
            for name in document.get("study_assets", {}):
                asset = (Path(study) / name).as_posix()
                public_path(asset)
                assets.append(asset)
                if asset.endswith(".html"):
                    hrefs.append(asset)
        identifier = ("lecture:" if document.get("series") == "lecture-notes" else "archive:") + document["id"]
        add(identifier, document["title"], document["date"], hrefs, assets)
    return {"version": 1, "pages": pages,
            "articles": sorted(records, key=lambda item: (item["publishedAt"], item["id"]), reverse=True)}


def validate_updates(updates: dict) -> dict:
    if not isinstance(updates, dict) or set(updates) != {"version", "pages", "articles"} or updates["version"] != 1:
        raise ValueError("Invalid update metadata version")
    if not isinstance(updates["pages"], dict) or not isinstance(updates["articles"], list):
        raise ValueError("Invalid update metadata collection")
    def scoped(path: str) -> bool:
        return isinstance(path, str) and path.startswith(SCOPE) and (path == SCOPE or public_path(path[len(SCOPE):]) == path)
    for path, digest in updates["pages"].items():
        if not scoped(path) or not CONTENT_SHA_RE.fullmatch(str(digest)):
            raise ValueError("Invalid update page digest")
    ids, paths = set(), set()
    for item in updates["articles"]:
        if (not isinstance(item, dict) or set(item) != {"id", "path", "paths", "title", "publishedAt", "revision", "updatedAt", "change"}
                or not isinstance(item["id"], str) or not ID_RE.fullmatch(item["id"]) or item["id"] in ids
                or not isinstance(item["title"], str) or not item["title"].strip()
                or not CONTENT_SHA_RE.fullmatch(str(item["revision"])) or item["change"] not in {"new", "updated"}
                or not isinstance(item["paths"], list) or not item["paths"]
                or item["path"] not in item["paths"] or len(set(item["paths"])) != len(item["paths"])
                or any(not scoped(path) or path in paths for path in item["paths"])):
            raise ValueError("Invalid update article record")
        if date.fromisoformat(item["publishedAt"]).isoformat() != item["publishedAt"]:
            raise ValueError("Invalid update publication date")
        if not isinstance(item["updatedAt"], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", item["updatedAt"]):
            raise ValueError("Invalid update timestamp")
        datetime.fromisoformat(item["updatedAt"].replace("Z", "+00:00"))
        ids.add(item["id"])
        paths.update(item["paths"])
    return updates


def enrich_site(site_dir: Path, *, revision: str | None = None, frontend_dir: Path = FRONTEND_DIR) -> dict:
    """Modify only new marked blocks, new assets and derived lecture checksums."""
    site_dir = Path(site_dir)
    articles, pages = load_publications(site_dir)
    previous_file = site_dir / UPDATES_NAME
    previous = validate_updates(json.loads(previous_file.read_text(encoding="utf-8"))) if previous_file.exists() else None
    updates = build_updates(site_dir, previous)
    validate_updates(updates)
    if revision is None:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if not SHA_RE.fullmatch(revision):
        raise ValueError("Publication revision must be a full source commit SHA")
    # Check the complete asset list before touching a published page.
    payloads = {}
    for source, target in ASSETS.items():
        path = frontend_dir / source
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing reader frontend asset: {source}")
        payloads[target] = path.read_bytes()
    asset_versions = {name: hashlib.sha256(payloads[ASSETS[name]]).hexdigest()[:12]
                      for name in ("reader-engagement.js", "reader-engagement.css", "reader-updates.js")}
    for target, payload in payloads.items():
        write_changed(site_dir / target, payload)
    content_versions = {path: item["revision"] for item in updates["articles"] for path in item["paths"]}
    changed = 0
    for path in sorted(site_dir.rglob("*.html")):
        if path.is_symlink():
            raise ValueError("Reader output cannot contain symlink HTML")
        relative = path.relative_to(site_dir).as_posix()
        original = path.read_bytes().decode("utf-8")
        enriched = enrich_html(original, relative, pages.get(relative), asset_versions=asset_versions,
                               article_version=content_versions.get(public_path(relative)))
        changed += write_changed(path, enriched.encode("utf-8"))
    # Lecture bundles checksum their HTML; keep the derived registry truthful.
    archive_path = site_dir / "archive-manifest.json"
    if archive_path.exists():
        archive = json.loads(archive_path.read_text(encoding="utf-8"))
        updated = False
        for document in archive.get("documents", []):
            for name, checksum in document.get("study_assets", {}).items():
                if name.endswith(".html"):
                    path = site_dir / document["study_href"] / name
                    current = hashlib.sha256(path.read_bytes()).hexdigest()
                    if checksum != current:
                        document["study_assets"][name] = current
                        updated = True
        if updated:
            write_changed(archive_path, (json.dumps(archive, ensure_ascii=False, indent=2) + "\n").encode())
    write_changed(site_dir / UPDATES_NAME, (json.dumps(updates, ensure_ascii=False, indent=2) + "\n").encode())
    catalog = {"revision": revision, "articles": articles}
    write_changed(site_dir / CATALOG_NAME, (json.dumps(catalog, ensure_ascii=False, indent=2) + "\n").encode())
    return {"html_changed": changed, "articles": len(articles), "revision": revision}


def validate_public_artifact(site_dir: Path) -> dict:
    """Fail before artifact upload on private files, links, or unregistered article assets."""
    try:
        from .publish_public_site import public_text_risks
    except ImportError:
        from publish_public_site import public_text_risks
    site_dir = Path(site_dir)
    if site_dir.is_symlink():
        raise ValueError("The public output directory cannot be a symlink")
    catalog = validate_catalog(json.loads((site_dir / CATALOG_NAME).read_text(encoding="utf-8")))
    updates = validate_updates(json.loads((site_dir / UPDATES_NAME).read_text(encoding="utf-8")))
    if build_updates(site_dir, updates) != updates:
        raise ValueError("Update metadata differs from public content")
    generated, _ = load_publications(site_dir)
    if catalog["articles"] != generated:
        raise ValueError("Publication catalog differs from approved public registries")
    reviews = json.loads((site_dir / "manifest.json").read_text(encoding="utf-8"))
    registered = set()
    for review in reviews:
        for variant in [review, *review.get("translations", [])]:
            href = variant["href"]
            public_path(href)
            registered.add(href)
            for asset in variant.get("assets", []):
                path = (Path(href).parent / asset).as_posix()
                public_path(path)
                registered.add(path)
    archive_path = site_dir / "archive-manifest.json"
    archive = json.loads(archive_path.read_text(encoding="utf-8")) if archive_path.exists() else {}
    for document in archive.get("documents", []):
        public_path(document["href"])
        registered.add(document["href"])
        for asset in document.get("study_assets", {}):
            path = (Path(document["study_href"]) / asset).as_posix()
            public_path(path)
            registered.add(path)
    # Four already published alternate cover images predate the registry. Pin their
    # exact bytes rather than deleting covers or silently allowing new unlisted files.
    exceptions = json.loads(ASSET_EXCEPTIONS.read_text(encoding="utf-8"))
    if (not isinstance(exceptions, dict) or any(not isinstance(name, str) or not name.startswith("reviews/")
            or not name.endswith(".webp") or not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value)
            for name, value in exceptions.items())):
        raise ValueError("Invalid reviewed legacy image exceptions")
    protected = [os.environ.get(name, "") for name in
                 ("READER_PUBLISH_TOKEN", "VAPID_PRIVATE_KEY", "RATE_LIMIT_SALT", "CLOUDFLARE_API_TOKEN")]
    protected = [secret for secret in protected if len(secret) >= 16]
    checked = 0
    for path in sorted(site_dir.rglob("*")):
        relative = path.relative_to(site_dir)
        if path.is_symlink():
            raise ValueError(f"Symlink in public output: {relative}")
        if any((part.startswith(".") and relative.as_posix() != ".nojekyll") or PRIVATE_NAMES.search(part)
               for part in relative.parts):
            raise ValueError(f"Private or hidden filename in public output: {relative}")
        if not path.is_file():
            continue
        name = relative.as_posix()
        if len(relative.parts) == 1:
            if name not in PUBLIC_ROOT_FILES:
                raise ValueError(f"Unapproved public root file: {relative}")
        elif relative.parts[0] not in PUBLIC_DIRECTORIES:
            raise ValueError(f"Unapproved public directory: {relative}")
        if relative.parts[0] == "en" and name != "en/index.html":
            raise ValueError(f"Unapproved English hub file: {relative}")
        if name not in {".nojekyll", "CNAME"} and path.suffix.lower() not in PUBLIC_EXTENSIONS:
            raise ValueError(f"Unapproved public file type: {relative}")
        if ((relative.parts[0] == "reviews" or name.startswith("archive/files/")
             or (relative.parts[0] == "lectures" and name not in {"lectures/index.html", "lectures/en/index.html"}))
                and name not in registered):
            if exceptions.get(name) != hashlib.sha256(path.read_bytes()).hexdigest():
                raise ValueError(f"Unregistered public article asset: {relative}")
        if path.suffix.lower() in PUBLIC_TEXT_EXTENSIONS:
            text = path.read_bytes().decode("utf-8")
            # Raster bytes can coincidentally contain /srv/, /tmp/, or credential-like
            # strings in base64. Inspect the surrounding SVG/HTML, not encoded pixels.
            def raster_placeholder(match: re.Match) -> str:
                try:
                    raster = base64.b64decode(match[2], validate=True)
                except ValueError:
                    return match[0]
                kind = match[1].lower()
                correct = ((kind == "png" and raster.startswith(b"\x89PNG\r\n\x1a\n"))
                           or (kind in {"jpeg", "jpg"} and raster.startswith(b"\xff\xd8\xff"))
                           or (kind == "gif" and raster.startswith((b"GIF87a", b"GIF89a")))
                           or (kind == "webp" and raster.startswith(b"RIFF") and raster[8:12] == b"WEBP"))
                return "[embedded raster image]" if correct else match[0]
            inspected = RASTER_DATA_URI.sub(raster_placeholder, text)
            if any(secret in text for secret in protected) or public_text_risks(html.unescape(inspected)):
                # Report the filename only, never the matching secret or its surrounding text.
                raise ValueError(f"Sensitive content detected in public output: {relative}")
        checked += 1
    return {"validated_files": checked, "articles": len(catalog["articles"])}


def request_json(url: str, *, token: str | None = None, body: dict | None = None) -> dict:
    headers = {"Accept": "application/json", "Cache-Control": "no-cache", "User-Agent": "AI-Tech-Review-Publications"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = None if body is None else json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method="GET" if body is None else "POST")
    # Do not forward bearer credentials through redirects to any other origin.
    from urllib.request import HTTPRedirectHandler, build_opener
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, response_headers, newurl):
            return None
    with build_opener(NoRedirect).open(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError("Expected successful JSON response")
        payload = response.read(2_000_001)
        if len(payload) > 2_000_000:
            raise ValueError("Publication response exceeds its size limit")
        return json.loads(payload)


def validate_catalog(catalog: dict) -> dict:
    if not isinstance(catalog, dict) or set(catalog) != {"revision", "articles"} or not SHA_RE.fullmatch(str(catalog.get("revision", ""))):
        raise ValueError("Invalid deployed publication revision")
    if not isinstance(catalog["articles"], list) or not 0 < len(catalog["articles"]) <= 500:
        raise ValueError("Invalid deployed article catalog")
    if len((json.dumps(catalog, ensure_ascii=False, indent=2) + "\n").encode()) > 300_000:
        raise ValueError("Publication catalog exceeds the backend's 300000-byte limit")
    ids, paths = set(), set()
    for article in catalog["articles"]:
        if not isinstance(article, dict) or set(article) != {"id", "path", "title", "publishedAt", "topic"}:
            raise ValueError("Invalid deployed article fields")
        if not isinstance(article["path"], str) or not article["path"].startswith(SCOPE):
            raise ValueError("Publication outside the review site")
        normalized = publication(article["id"], article["path"][len(SCOPE):], article["title"], article["publishedAt"], article["topic"])
        if normalized != article or article["id"] in ids or article["path"] in paths:
            raise ValueError("Duplicate or noncanonical deployed publication")
        ids.add(article["id"])
        paths.add(article["path"])
    return catalog


def assert_live_article(article: dict, revision: str) -> None:
    url = "https://infant83.io" + article["path"] + "?reader_revision=" + revision
    request = Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "AI-Tech-Review-Publications"})
    with urlopen(request, timeout=30) as response:
        final = urlsplit(response.geturl())
        if response.status != 200 or final.scheme != "https" or final.netloc != "infant83.io" or final.path != article["path"]:
            raise ValueError("A publication URL is not live at its canonical HTTPS path")


def sync_publications(expected: dict, revision: str, repository: str, github_token: str, publish_token: str,
                      *, attempts: int = 12, delay: float = 10) -> dict:
    """Run only after deploy-pages succeeds; verify its immutable catalog artifact."""
    expected = validate_catalog(expected)
    if not SHA_RE.fullmatch(revision) or expected["revision"] != revision:
        raise ValueError("Publication catalog does not match the workflow source revision")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Invalid repository")
    base = "https://api.github.com/repos/" + repository
    def branch_sha() -> str:
        return request_json(base + "/git/ref/heads/main", token=github_token)["object"]["sha"]
    if branch_sha() != revision:
        return {"skipped": "superseded source revision"}
    live_url = SITE_ROOT + CATALOG_NAME + "?revision=" + revision + "&check=" + str(time.time_ns())
    for attempt in range(attempts):
        try:
            actual = validate_catalog(request_json(live_url))
            if actual != expected:
                raise ValueError("Public catalog does not match the deployed Git artifact")
            with ThreadPoolExecutor(max_workers=6) as pool:
                list(pool.map(lambda article: assert_live_article(article, expected["revision"]), expected["articles"]))
            break
        except (HTTPError, URLError, ValueError, TimeoutError):
            if attempt + 1 == attempts:
                raise ValueError("Public Pages output was not verified; publication sync withheld") from None
            time.sleep(delay)
    # Recheck immediately before sending; old deployments never register new articles.
    if branch_sha() != revision:
        return {"skipped": "deployment superseded during public verification"}
    if validate_catalog(request_json(live_url)) != expected:
        return {"skipped": "public deployment changed during URL verification"}
    if not publish_token:
        raise ValueError("Set the READER_PUBLISH_TOKEN repository secret before synchronizing")
    for attempt in range(3):
        try:
            result = request_json(API_BASE + "/v1/publications/sync", token=publish_token, body=expected)
            if not result.get("ok"):
                raise ValueError("Backend did not confirm publication synchronization")
            return {"synced": len(expected["articles"]), "revision": expected["revision"], "ok": True}
        except HTTPError as error:
            if error.code != 409 or attempt == 2:
                raise
            time.sleep(5)
            if branch_sha() != revision or request_json(live_url) != expected:
                return {"skipped": "deployment superseded before synchronization retry"}
    raise ValueError("Publication synchronization did not complete")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    enrich = commands.add_parser("enrich", help="Enrich existing output without republishing articles")
    enrich.add_argument("--site-dir", type=Path, default=ROOT / "site")
    enrich.add_argument("--revision")
    validate = commands.add_parser("validate", help="Check the exact public artifact before upload")
    validate.add_argument("--site-dir", type=Path, default=ROOT / "site")
    sync = commands.add_parser("sync", help="After deploy-pages success, verify public output and synchronize")
    sync.add_argument("--catalog", type=Path, required=True, help="Catalog artifact from the Pages build job")
    args = parser.parse_args()
    try:
        if args.command == "enrich":
            result = enrich_site(args.site_dir, revision=args.revision)
        elif args.command == "validate":
            result = validate_public_artifact(args.site_dir)
        else:
            catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
            result = sync_publications(catalog, os.environ["GITHUB_SHA"], os.environ["GITHUB_REPOSITORY"],
                                       os.environ["GITHUB_TOKEN"], os.environ.get("READER_PUBLISH_TOKEN", ""))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (KeyError, ValueError, OSError, HTTPError, URLError) as error:
        # Never print response bodies, headers or bearer credentials in CI.
        print(f"[reader-publication:error] {type(error).__name__}: publication step failed")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
