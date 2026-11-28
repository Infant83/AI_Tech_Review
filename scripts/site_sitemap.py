"""Build a canonical-only sitemap from registered public HTML, never PDF/source.

Google's primary guidance: absolute canonical URLs, UTF-8/entity-escaped XML,
and verifiable significant-update dates only. We omit lastmod rather than use
build time or filesystem mtime. Discovery does not establish Google indexing.
https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls
"""
from __future__ import annotations

from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import re
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


class SitemapError(ValueError):
    pass


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
