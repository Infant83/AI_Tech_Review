"""Portable, explicit public search records and a small progressively enhanced UI.

Only public catalog metadata and headings/glossary terms from registered study
HTML are indexed. PDF bytes and private authoring sources are never discovered.
"""
from __future__ import annotations

try:
    from .site_brand import current_source_title
except ImportError:
    from site_brand import current_source_title

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit

try:
    from .hub_localization import localize_manifest
except ImportError:
    from hub_localization import localize_manifest

SOURCE = Path(__file__).parent / "public_assets"
ASSETS = ("site-search.js", "site-search-core.js", "site-search.css", "minisearch.js", "minisearch-LICENSE.txt", "listing-pages.js")
SCOPES = ("all", "reviews", "lectures", "briefings", "books")


def version(name: str) -> str:
    return hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()[:12]


def search_head(prefix: str = "") -> str:
    return f'<link rel="stylesheet" href="{prefix}assets/site-search.css?v={version("site-search.css")}">'


def search_script(prefix: str = "") -> str:
    return f'<script src="{prefix}assets/site-search.js?v={version("site-search.js")}" defer></script>'


def search_form(prefix: str = "", language: str = "ko", scope: str = "all") -> str:
    en = language == "en"
    if scope not in SCOPES:
        raise ValueError("Unknown search scope")
    labels = ("All", "Reviews", "Lectures", "Briefings", "Books") if en else ("전체", "리뷰", "렉처", "브리핑", "외부 서적")
    options = "".join(f'<option value="{key}"{" selected" if key == scope else ""}>{label}</option>' for key, label in zip(SCOPES, labels))
    return f'''<form class="site-search" role="search" data-site-search data-root="{prefix}" data-default-scope="{scope}" data-engine-version="{version('minisearch.js')}" data-core-version="{version('site-search-core.js')}" action="{prefix}{'en/' if en else ''}" method="get">
      <label class="site-search-scope"><span class="sr-only">{'Search section' if en else '검색 범위'}</span><select name="scope" aria-label="{'Search section' if en else '검색 범위'}">{options}</select></label>
      <div class="site-search-field"><label class="sr-only" for="site-search-input">{'Search titles and topics' if en else '제목·주제 검색'}</label><input id="site-search-input" name="q" type="search" placeholder="{'Search titles or topics' if en else '제목·주제 검색'}" autocomplete="off" maxlength="180" aria-controls="site-search-results"><button type="submit" aria-label="{'Search' if en else '검색'}" title="{'Search' if en else '검색'}"><svg viewBox="0 0 24 24" width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4.5 4.5"/></svg></button></div>
    </form>'''


def search_results(language: str = "ko") -> str:
    en = language == "en"
    return f'''<section class="site-search-results" id="site-search-results" data-site-search-results hidden aria-labelledby="site-search-heading">
      <div class="site-search-heading"><h2 id="site-search-heading">{'Search results' if en else '검색 결과'}</h2><button type="button" data-search-clear>{'Clear search' if en else '검색 지우기'}</button></div>
      <p data-search-status role="status" aria-live="polite"></p><div data-search-list></div><button type="button" data-search-more hidden>{'Show more' if en else '더 보기'}</button>
    </section>'''


def _public_file(root: Path, href: str) -> Path:
    parsed = urlsplit(href)
    path = unquote(parsed.path)
    if parsed.scheme or parsed.netloc or path.startswith("/") or "\\" in path or any(p in {"..", "."} for p in path.split("/")) or "%" in path:
        raise ValueError("Search source must use a relative public path")
    candidate = root / path
    if candidate.is_dir():
        candidate /= "index.html"
    if not candidate.resolve().is_relative_to(root.resolve()) or candidate.is_symlink():
        raise ValueError("Search source must remain inside public output")
    if any(parent.is_symlink() for parent in candidate.parents if parent != root and root in parent.parents):
        raise ValueError("Symlinked search source")
    return candidate


class StudyHeadings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.heading = None
        self.headings = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "style", "svg", "nav", "header", "footer"}:
            self.skip += 1
        if not self.skip and tag in {"h1", "h2", "h3", "h4", "dt"}:
            self.heading = [tag, attrs.get("id", ""), []]

    def handle_endtag(self, tag):
        if tag in {"script", "style", "svg", "nav", "header", "footer"} and self.skip:
            self.skip -= 1
        if self.heading and tag == self.heading[0]:
            title = " ".join("".join(self.heading[2]).split())
            if title:
                self.headings.append((self.heading[1], title[:240]))
            self.heading = None

    def handle_data(self, text):
        if not self.skip and self.heading:
            self.heading[2].append(text)


def _read_json(path: Path, fallback):
    if not path.exists():
        return fallback
    if path.is_symlink():
        raise ValueError("Symlinked search catalog")
    return json.loads(path.read_text(encoding="utf-8"))


def build_records(site_dir: Path) -> list[dict]:
    root = Path(site_dir)
    reviews = _read_json(root / "manifest.json", [])
    archive = _read_json(root / "archive-manifest.json", {"documents": [], "external_resources": []})
    records = []
    review_titles = {re.sub(r"\s+", " ", str(item["title"])).strip().casefold() for item in reviews}
    english_items = {item["folder"]: item for item in localize_manifest(reviews, root, "en")}
    for item in reviews:
        english = english_items[item["folder"]]
        available = english.get("english_available") is True
        titles = item["title"] + (" " + english["title"] if available else "")
        text = " ".join(str(item.get(key, "")) for key in ("subtitle", "summary"))
        if available:
            text += " " + english.get("subtitle", "") + " " + english.get("summary", "")
            review_titles.add(re.sub(r"\s+", " ", english["title"]).strip().casefold())
        records.append({"id": item["folder"], "scope": "reviews", "title": item["title"], "title_en": english["title"] if available else "", "url": item["href"], "url_en": english.get("english_href", "") if available else "", "date": item["date"], "titles": titles, "topics": " ".join([item.get("category", ""), *item.get("tags", [])]), "summary": item.get("summary", ""), "summary_en": english.get("summary", "") if available else "", "text": text, "headings": ""})
    grouped_units = {unit["document_id"]: item["id"] for item in archive.get("documents", []) for unit in item.get("study_series", {}).get("units", []) if unit["document_id"] != item["id"]}
    for item in archive.get("documents", []) + archive.get("external_resources", []):
        series = item["series"]
        if item["id"] in grouped_units:
            continue
        if series == "article" and re.sub(r"\s+", " ", item["title"]).strip().casefold() in review_titles:
            continue
        scope = "lectures" if series == "lecture-notes" else "books" if series == "external-book" else "briefings" if series in {"daily-quantum", "weekly-review"} else "reviews"
        href = item.get("book_url") if scope == "books" else item.get("editorial_href") or item.get("study_href") or item["href"]
        headings = ""
        if scope == "lectures" and item.get("study_href"):
            path = _public_file(root, item["study_href"])
            if path.exists():
                parser = StudyHeadings()
                parser.feed(path.read_text(encoding="utf-8"))
                manifest_path = path.parent / "chapter-manifest.json"
                if manifest_path.exists():
                    manifest = _read_json(manifest_path, {})
                    pages = manifest.get("pages")
                    if manifest.get("version") != 1 or manifest.get("course_href") != item["study_href"] or not isinstance(pages, list) or not 1 <= len(pages) <= 500:
                        raise ValueError("Invalid public lecture chapter manifest")
                    approved = item.get("study_assets", {})
                    if approved.get("chapter-manifest.json") != hashlib.sha256(manifest_path.read_bytes()).hexdigest():
                        raise ValueError("Unregistered lecture chapter manifest")
                    seen_pages = set()
                    for page in pages:
                        leaf_href = page.get("href", "")
                        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\.html", leaf_href) or leaf_href in seen_pages:
                            raise ValueError("Invalid lecture chapter search source")
                        seen_pages.add(leaf_href)
                        leaf = _public_file(root, item["study_href"] + leaf_href)
                        if not leaf.is_file() or approved.get(leaf_href) != hashlib.sha256(leaf.read_bytes()).hexdigest():
                            raise ValueError("Unregistered or changed lecture chapter")
                        parser.feed(leaf.read_text(encoding="utf-8"))
                # Every chapter repeats its course sidebar. Deduplicate before
                # the size cap so repeated navigation cannot displace glossary
                # terms at the end of the original course.
                headings = " ".join(dict.fromkeys(title for _, title in parser.headings))[:20000]
        grouped = item.get("study_series", {})
        if grouped:
            headings += " " + " ".join(" ".join(str(unit.get(key, "")) for key in ("number", "title", "title_en", "summary", "summary_en")) for unit in grouped.get("units", []))
        title, title_en = grouped.get("title", item["title"]), grouped.get("title_en", item.get("title_en", ""))
        summary, summary_en = grouped.get("summary", item["summary"]), grouped.get("summary_en", item.get("summary_en", ""))
        records.append({"id": item["id"], "scope": scope, "title": title, "title_en": title_en, "url": href, "url_en": item.get("editorial_en_href", ""), "date": item["date"], "titles": title + " " + title_en, "topics": " ".join(item.get("tags", [])) + " " + item.get("author", ""), "summary": summary, "summary_en": summary_en, "text": summary + " " + summary_en + " " + current_source_title(item.get("source_title", "")), "headings": headings})
    seen = set()
    for record in records:
        if record["id"] in seen:
            raise ValueError(f'Duplicate search publication ID: {record["id"]}')
        seen.add(record["id"])
        if record["scope"] != "books" and not _public_file(root, record["url"]).is_file():
            raise ValueError(f'Search destination missing: {record["id"]}')
        if record["scope"] == "books" and not record["url"].startswith("https://"):
            raise ValueError("External books must use HTTPS")
    return sorted(records, key=lambda item: (item["date"], item["id"]), reverse=True)


def build_search(site_dir: Path) -> dict:
    root = Path(site_dir)
    records = build_records(root)
    assets = root / "assets"
    if assets.is_symlink():
        raise ValueError("Symlinked search assets directory")
    assets.mkdir(exist_ok=True, parents=True)
    for name in (*ASSETS, "search-records.json", "search-assets.json"):
        destination = assets / name
        if destination.is_symlink() or (destination.exists() and not destination.is_file()):
            raise ValueError("Search assets must be regular files")
    for name in ASSETS:
        shutil.copyfile(SOURCE / name, assets / name)
    raw = json.dumps({"version": 1, "coverage": "Public titles, topics, summaries and study HTML headings/glossary terms; not full PDF text.", "records": records}, ensure_ascii=False, separators=(",", ":")) + "\n"
    (assets / "search-records.json").write_text(raw, encoding="utf-8")
    records_version = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
    # Version the catalog URL in each generated entry point. The same revision
    # always fetches the same catalog, while new posts cannot reuse old JSON.
    entry_points = {"index.html", "en/index.html", "archive/index.html", "archive/en/index.html", "lectures/index.html", "lectures/en/index.html", "briefings/index.html", "briefings/en/index.html"}
    for pattern in ("page/[0-9]*/index.html", "en/page/[0-9]*/index.html", "archive/page/[0-9]*/index.html", "archive/en/page/[0-9]*/index.html", "briefings/page/[0-9]*/index.html", "briefings/en/page/[0-9]*/index.html"):
        entry_points.update(path.relative_to(root).as_posix() for path in root.glob(pattern))
    for relative in sorted(entry_points):
        page = _public_file(root, relative)
        if page.is_file():
            if page.is_symlink():
                raise ValueError("Symlinked search entry point")
            text = page.read_text(encoding="utf-8")
            def stamp(match):
                tag = re.sub(r' data-search-version="[^"]*"', "", match.group(0))
                return tag[:-1] + f' data-search-version="{records_version}">'
            changed = re.sub(r'<form\b[^>]*\bdata-site-search(?=\s|>)[^>]*>', stamp, text)
            if changed != text:
                page.write_text(changed, encoding="utf-8")
    manifest = {"version": 1, "minisearch": "7.2.0", "records": len(records), "files": {name: hashlib.sha256((assets / name).read_bytes()).hexdigest() for name in (*ASSETS, "search-records.json")}}
    (assets / "search-assets.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def validate_search(site_dir: Path) -> list[str]:
    root = Path(site_dir)
    path = root / "assets/search-assets.json"
    if not path.exists():
        return ["missing search asset manifest"]
    errors = []
    try:
        manifest = _read_json(path, {})
        if set(manifest.get("files", {})) != set((*ASSETS, "search-records.json")):
            return ["search asset allowlist differs"]
        for name, checksum in manifest["files"].items():
            target = _public_file(root, "assets/" + name)
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != checksum:
                errors.append(f"search asset missing or changed: {name}")
            elif name in ASSETS and target.read_bytes() != (SOURCE / name).read_bytes():
                errors.append(f"search asset differs from source: {name}")
        expected = build_records(root)
        actual = _read_json(root / "assets/search-records.json", {})
        if actual.get("version") != 1 or actual.get("records") != expected or manifest.get("records") != len(expected):
            errors.append("search records do not match public catalogs")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        errors.append(f"invalid search output: {exc}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path(__file__).resolve().parents[1] / "site")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    result = validate_search(args.site) if args.validate else build_search(args.site)
    print(json.dumps(result, ensure_ascii=False))
    if args.validate and result:
        raise SystemExit(1)
