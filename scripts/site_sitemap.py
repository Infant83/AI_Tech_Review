"""Build a canonical-only sitemap from registered public HTML, never PDF/source.

Google's primary guidance: absolute canonical URLs, UTF-8/entity-escaped XML,
and verifiable significant-update dates only. We omit lastmod rather than use
build time or filesystem mtime. Discovery does not establish Google indexing.
https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
"""
from __future__ import annotations

from html.parser import HTMLParser
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import quote, unquote, urlsplit
import xml.etree.ElementTree as ET

try:
    from .site_brand import PUBLIC_ORIGIN
    from .listing_pagination import generated_paths
except ImportError:
    from site_brand import PUBLIC_ORIGIN
    from listing_pagination import generated_paths

BASE_URL = PUBLIC_ORIGIN + "/AI_Tech_Review/"
NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
CORE_PAGES = ("index.html", "en/index.html", "archive/index.html", "archive/en/index.html",
              "lectures/index.html", "lectures/en/index.html", "briefings/index.html",
              "briefings/en/index.html", "methods/index.html", "insights/index.html", "en/insights/index.html")
MAX_URLS, MAX_XML_BYTES = 50_000, 50 * 1024 * 1024
MAX_HTML_BYTES, MAX_REGISTRY_BYTES = 8 * 1024 * 1024, 4 * 1024 * 1024
PRIVATE_PARTS = {"private", "internal", "output", "operations", "node_modules"}
# This is a public Search Console challenge, not a credential or a general
# permission to install root HTML. Preserve the downloaded bytes, without LF.
SEARCH_CONSOLE_NAME = "google60a24e972420ad3d.html"
SEARCH_CONSOLE_SOURCE = (Path(__file__).resolve().parents[1] / "publication" /
                         "search-console" / SEARCH_CONSOLE_NAME)
SEARCH_CONSOLE_BYTES = 53
SEARCH_CONSOLE_SHA256 = "0a1d44f6260fee4b1e85051d9ce588f5e39c71a173792f309ee75077b3694d23"


class SitemapError(ValueError):
    pass


def _verification_identity(info):
    return info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns


def _verification_directory(path):
    try:
        fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError:
        raise SitemapError("Unsafe Search Console verification directory") from None
    return fd


def _verification_payload(directory_fd):
    """Read only the fixed challenge through one bounded, no-follow regular FD."""
    try:
        fd = os.open(SEARCH_CONSOLE_NAME, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                     dir_fd=directory_fd)
        try:
            before = os.fstat(fd)
            if not stat.S_ISREG(before.st_mode) or before.st_size != SEARCH_CONSOLE_BYTES:
                raise SitemapError("Invalid Search Console verification file")
            raw = b""
            while len(raw) <= SEARCH_CONSOLE_BYTES:
                chunk = os.read(fd, SEARCH_CONSOLE_BYTES + 1 - len(raw))
                if not chunk:
                    break
                raw += chunk
            after = os.fstat(fd)
            current = os.stat(SEARCH_CONSOLE_NAME, dir_fd=directory_fd, follow_symlinks=False)
            if (len(raw) != SEARCH_CONSOLE_BYTES
                    or _verification_identity(before) != _verification_identity(after)
                    or _verification_identity(before) != _verification_identity(current)
                    or hashlib.sha256(raw).hexdigest() != SEARCH_CONSOLE_SHA256):
                raise SitemapError("Search Console verification bytes differ from the fixed pin")
            return raw
        finally:
            os.close(fd)
    except OSError:
        raise SitemapError("Cannot read Search Console verification file") from None


def validate_search_console_verification(site_dir):
    """Validate the exact public challenge when present; partial fixtures may omit it."""
    directory_fd = _verification_directory(Path(site_dir))
    try:
        try:
            os.stat(SEARCH_CONSOLE_NAME, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            return False
        _verification_payload(directory_fd)
        return True
    finally:
        os.close(directory_fd)


def install_search_console_verification(site_dir):
    """Install the one pinned public challenge, required by the final publisher."""
    source = SEARCH_CONSOLE_SOURCE
    if source.name != SEARCH_CONSOLE_NAME or source.parent.parent.is_symlink():
        raise SitemapError("Unsafe Search Console verification source")
    source_fd = _verification_directory(source.parent)
    try:
        payload = _verification_payload(source_fd)
    finally:
        os.close(source_fd)
    site = Path(site_dir)
    directory_fd = _verification_directory(site)
    try:
        parent = os.fstat(directory_fd)
        try:
            fd = os.open(SEARCH_CONSOLE_NAME,
                         os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o644, dir_fd=directory_fd)
        except FileExistsError:
            # A damaged immutable challenge is an error, not permission to
            # overwrite it. The next fresh publication candidate can be rebuilt.
            _verification_payload(directory_fd)
            changed = False
        else:
            try:
                written = 0
                while written < len(payload):
                    count = os.write(fd, payload[written:])
                    if count <= 0:
                        raise SitemapError("Cannot install Search Console verification file")
                    written += count
                os.fsync(fd)
            finally:
                os.close(fd)
            _verification_payload(directory_fd)
            changed = True
        current = os.stat(site, follow_symlinks=False)
        if (parent.st_dev, parent.st_ino, parent.st_mode) != (
                current.st_dev, current.st_ino, current.st_mode):
            raise SitemapError("Search Console verification directory changed")
        return {"bytes": SEARCH_CONSOLE_BYTES, "sha256": SEARCH_CONSOLE_SHA256,
                "changed": changed}
    except OSError:
        raise SitemapError("Cannot install Search Console verification file") from None
    finally:
        os.close(directory_fd)


def _relative(value):
    if (not isinstance(value, str) or not value or "\\" in value or "%" in value
            or any(ord(char) < 32 for char in value)):
        raise SitemapError("Invalid registered sitemap path")
    parsed = urlsplit(value)
    parts = value.split("/")
    if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or value.startswith("/")
            or "//" in value or any(part in {".", ".."} or part.startswith(".")
                                     or part.lower() in PRIVATE_PARTS for part in parts)):
        raise SitemapError("Unsafe registered sitemap path")
    return value + "index.html" if value.endswith("/") else value


def _regular(site, name, maximum):
    path = site / name
    if any((site / Path(*Path(name).parts[:end])).is_symlink()
           for end in range(1, len(Path(name).parts) + 1)) or not path.is_file():
        raise SitemapError("Sitemap reference is missing or symlinked")
    with path.open("rb") as handle:
        raw = handle.read(maximum + 1)
    if len(raw) > maximum:
        raise SitemapError("Sitemap input exceeds its limit")
    return raw


def _registry(site, name, fallback):
    if (site / name).is_symlink():
        raise SitemapError("Symlinked sitemap registry")
    if not (site / name).exists():
        return fallback
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise SitemapError("Duplicate sitemap registry key")
            result[key] = value
        return result
    return json.loads(_regular(site, name, MAX_REGISTRY_BYTES), object_pairs_hook=unique)


def registered_html_paths(site):
    """Reuse public registration and list-page generation, without PDF reads."""
    paths = set()
    def add(href):
        name = _relative(href)
        if name.endswith(".html"):
            if name != "index.html" and name.split("/", 1)[0] not in {
                    "reviews", "archive", "lectures", "briefings", "methods", "insights", "en", "page"}:
                raise SitemapError("Sitemap HTML is outside public page directories")
            paths.add(name)
            if len(paths) > MAX_URLS:
                raise SitemapError("Too many sitemap HTML candidates")
    reviews = _registry(site, "manifest.json", [])
    archive = _registry(site, "archive-manifest.json", {})
    if not isinstance(reviews, list) or not isinstance(archive, dict):
        raise SitemapError("Invalid public sitemap registries")
    for review in reviews:
        for variant in [review, *review.get("translations", [])]:
            href = variant["href"]; add(href)
            parent = PurePosixPath(_relative(href)).parent
            for asset in variant.get("assets", []):
                add((parent / _relative(asset)).as_posix())
    for document in archive.get("documents", []):
        for field in ("study_href", "editorial_href", "editorial_en_href"):
            if document.get(field):
                add(document[field])
        if document.get("study_href"):
            parent = PurePosixPath(_relative(document["study_href"])).parent
            for asset in document.get("study_assets", {}):
                add((parent / _relative(asset)).as_posix())
    # Core/list pages are optional in a partial fixture, and generated in the
    # real publisher. Every included URL must still resolve to a regular file.
    for name in set(CORE_PAGES) | generated_paths(site):
        if (site / name).exists():
            add(name)
    return paths


class _Head(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_head = False; self.canonicals = []; self.excluded = False

    def handle_starttag(self, tag, attributes):
        if tag == "head":
            self.in_head = True
        if not self.in_head:
            return
        attrs = dict(attributes)
        if tag == "link" and "canonical" in (attrs.get("rel") or "").lower().split():
            self.canonicals.append(attrs.get("href", ""))
        if tag == "meta":
            if (attrs.get("name") or "").lower() in {"robots", "googlebot"}:
                tokens = re.split(r"[\s,]+", (attrs.get("content") or "").lower())
                self.excluded |= bool({"noindex", "none"} & set(tokens))
            if (attrs.get("http-equiv") or "").lower() == "refresh":
                self.excluded = True

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False

    handle_startendtag = handle_starttag


def _canonical(value):
    parsed = urlsplit(value)
    base = urlsplit(BASE_URL)
    if (parsed.scheme != "https" or parsed.netloc != base.netloc or parsed.query or parsed.fragment
            or not parsed.path.startswith(base.path)):
        raise SitemapError("Canonical sitemap URL is outside the current public site")
    decoded = unquote(parsed.path, errors="strict")
    relative = decoded[len(base.path):]
    name = "index.html" if relative == "" else _relative(relative)
    if not name.endswith(".html"):
        raise SitemapError("Canonical sitemap target is not HTML")
    # Stable URI spelling; UTF-8 percent escaping preserves the actual path.
    url = PUBLIC_ORIGIN + quote(decoded, safe="/-._~!$&'()*+,;=:@")
    return url, name


def sitemap_urls(site_dir):
    site = Path(site_dir)
    if site.is_symlink() or not site.is_dir():
        raise SitemapError("Sitemap site must be a regular public directory")
    metadata = {}
    for name in sorted(registered_html_paths(site)):
        head = _Head(); head.feed(_regular(site, name, MAX_HTML_BYTES).decode("utf-8"))
        if head.excluded or not head.canonicals:
            metadata[name] = None
        elif len(head.canonicals) != 1:
            raise SitemapError("Sitemap HTML must have one canonical URL")
        else:
            metadata[name] = _canonical(head.canonicals[0])
    urls = set()
    for value in metadata.values():
        visited = set()
        while value is not None:
            url, target = value
            if target not in metadata:
                raise SitemapError("Canonical sitemap target is not registered public HTML")
            if target in visited:
                raise SitemapError("Canonical sitemap cycle")
            visited.add(target)
            preferred = metadata[target]
            if preferred is None:
                break
            if preferred[1] == target:
                urls.add(preferred[0]); break
            value = preferred
    return sorted(urls)


def build_sitemap(site_dir):
    site = Path(site_dir)
    urls = sitemap_urls(site)
    ET.register_namespace("", NAMESPACE)
    root = ET.Element("{" + NAMESPACE + "}urlset")
    for url in urls:
        item = ET.SubElement(root, "{" + NAMESPACE + "}url")
        ET.SubElement(item, "{" + NAMESPACE + "}loc").text = url
    payload = ET.tostring(root, encoding="utf-8", xml_declaration=True) + b"\n"
    if len(payload) > MAX_XML_BYTES:
        raise SitemapError("Sitemap exceeds XML byte limit")
    target = site / "sitemap.xml"
    if target.is_symlink() or target.exists() and not target.is_file():
        raise SitemapError("Unsafe sitemap output")
    if target.exists() and _regular(site, "sitemap.xml", MAX_XML_BYTES) == payload:
        return {"urls": len(urls), "bytes": len(payload), "changed": False}
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(payload)
    return {"urls": len(urls), "bytes": len(payload), "changed": True}
