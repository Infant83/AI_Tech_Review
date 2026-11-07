"""Split the reviewed QML study HTML without rewriting its scientific content.

The reviewed dist/index.html remains the single authoring/print source. Public
HTML contains its original sections once, on independent pages. Only local
fragment links are retargeted; text, equations, figures and IDs are preserved.
"""
from __future__ import annotations

import hashlib
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

COURSE_HREF = "lectures/quantum-machine-learning/"
SOURCE_RELATIVE = "2026-10-20_quantum-machine-learning-lecture-series/dist/index.html"
MANIFEST = "chapter-manifest.json"
NAVIGATION_JS = "course-navigation.js"
NAVIGATION_CSS = "course-navigation.css"
SOURCE_ASSETS = Path(__file__).parent / "public_assets"
SHA = re.compile(r"[a-f0-9]{64}\Z")
PAGE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\.html\Z")
VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"})
READER_BLOCK = re.compile(r"<!-- Reader Engagement (?:Head|Controls) -->.*?<!-- End Reader Engagement (?:Head|Controls) -->\r?\n?", re.S)
HREF = re.compile(r'\bhref=(?P<quote>["\'])(?P<href>.*?)(?P=quote)', re.S | re.I)
ANCHOR_START = re.compile(r'<a\b[^>]*>', re.S | re.I)


def sha256(value: str | bytes) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


class SourceSections(HTMLParser):
    """Record original offsets; HTML serialization would alter MathJax SVG."""
    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.line_offsets = [0]
        for match in re.finditer("\n", source):
            self.line_offsets.append(match.end())
        self.depth = 0
        self.pending = None
        self.sections = []
        self.ids = []
        self.section_ids = []
        self.elements = 0
        self.feed(source)

    def absolute_offset(self):
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        self.elements += 1
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "section":
            if self.depth == 0:
                self.pending = (self.absolute_offset(), values)
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag != "section":
            return
        self.depth -= 1
        if self.depth < 0:
            raise ValueError("Unbalanced source section")
        if self.depth == 0 and self.pending:
            start, attrs = self.pending
            end = self.source.find(">", self.absolute_offset()) + 1
            if not end:
                raise ValueError("Unclosed source section")
            self.sections.append({"start": start, "end": end, "attrs": attrs, "html": self.source[start:end]})
            self.pending = None


class Identifiers(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.elements = 0
        self.title = []
        self.in_title = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        self.elements += 1
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "h1" and not self.title:
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_title = False

    def handle_data(self, value):
        if self.in_title:
            self.title.append(value)


def source_plan(source: str) -> dict:
    parsed = SourceSections(source)
    if parsed.depth or parsed.pending:
        raise ValueError("Incomplete study source")
    documents = [section for section in parsed.sections if "document" in section["attrs"].get("class", "").split() and section["attrs"].get("id")]
    covers = [section for section in parsed.sections if section["attrs"].get("id") == "front-cover"]
    if not documents or len(covers) != 1:
        raise ValueError("Expected one course cover and independently identified study documents")
    routes, records, seen = {}, [], set()
    for section in documents:
        identifier = section["attrs"]["id"]
        filename = identifier.removeprefix("doc-") + ".html"
        if not PAGE.fullmatch(filename) or filename == "index.html":
            raise ValueError("Invalid generated chapter filename")
        body = section["html"]
        content = Identifiers(body)
        if not content.ids or len(content.ids) != len(set(content.ids)):
            raise ValueError("Missing or duplicated source section IDs")
        for anchor in content.ids:
            if anchor in seen:
                raise ValueError("Duplicate source anchor: " + anchor)
            seen.add(anchor)
            routes[anchor] = filename
        records.append({"href": filename, "id": identifier, "title": " ".join("".join(content.title).split()),
                        "source": section["attrs"].get("data-source", ""), "source_section_sha256": sha256(body),
                        "source_elements": content.elements, "anchors": content.ids, "html": body})
    for anchor in parsed.ids:
        routes.setdefault(anchor, "index.html")
    routes["front-cover"] = "index.html"
    return {"records": records, "anchors": routes, "cover": covers[0]["html"], "source_sha256": sha256(source)}


def retarget_fragments(source: str, routes: dict[str, str]) -> str:
    """Change href attributes only; all scientific markup stays byte-identical."""
    def replace(match):
        href = html.unescape(match["href"])
        if not href.startswith("#"):
            return match[0]
        anchor = unquote(href[1:])
        if anchor not in routes:
            # Broken cross-references must be fixed in the reviewed source,
            # never silently hidden during a layout migration.
            raise ValueError("Unresolved source fragment: " + anchor)
        target = routes[anchor] + "#" + href[1:]
        return "href=" + match["quote"] + html.escape(target, quote=True) + match["quote"]
    return ANCHOR_START.sub(lambda match: HREF.sub(replace, match[0]), source)


def chapter_files(source: str) -> tuple[str, ...]:
    return tuple(record["href"] for record in source_plan(source)["records"]) + (MANIFEST, NAVIGATION_JS, NAVIGATION_CSS)


def _asset_href(name: str) -> str:
    return name + "?v=" + sha256((SOURCE_ASSETS / name).read_bytes())[:12]


def _chapter_head(head: str, title: str, canonical: str) -> str:
    head = re.sub(r'<title>.*?</title>', lambda _: '<title>' + html.escape(title) + ' | 퀀텀 머신러닝</title>', head, count=1, flags=re.S)
    head = re.sub(r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*>', '', head, flags=re.I)
    head = re.sub(r'<meta\b(?=[^>]*\bproperty=["\']og:(?:url|title)["\'])[^>]*>', '', head, flags=re.I)
    extra = (f'<link rel="canonical" href="{html.escape(canonical, quote=True)}">'
             f'<meta property="og:url" content="{html.escape(canonical, quote=True)}">'
             f'<meta property="og:title" content="{html.escape(title, quote=True)}">'
             f'<link rel="stylesheet" href="{_asset_href(NAVIGATION_CSS)}">')
    return head.replace("</head>", extra + "</head>", 1)


def _pager(records: list[dict], index: int) -> str:
    links = ['<a href="index.html">코스 목차</a>']
    if index:
        previous = records[index - 1]
        links.append(f'<a rel="prev" href="{previous["href"]}">← 이전 자료</a>')
    if index + 1 < len(records):
        following = records[index + 1]
        links.append(f'<a rel="next" href="{following["href"]}">다음 자료 →</a>')
    return '<nav class="qml-page-navigation" aria-label="학습 자료 이동">' + "".join(links) + '</nav>'


def build_chapters(directory: Path, source: str, published: str, canonical: str) -> dict:
    """Replace only the QML course HTML with a course entry and exact sections.

    source is the reviewed dist HTML, published adds existing site navigation,
    metadata and publication disclosure. Asset paths remain relative because
    chapter files sit beside notes.css, figures, labs and the unchanged PDF.
    """
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError("Chapter output must not be a symlink")
    plan = source_plan(source)
    published_plan = source_plan(published)
    if [r["source_section_sha256"] for r in plan["records"]] != [r["source_section_sha256"] for r in published_plan["records"]]:
        raise ValueError("Site decoration changed scientific source sections")
    head = re.search(r'<!doctype\b.*?</head>', published, re.I | re.S)
    aside = re.search(r'<aside\b[^>]*class="sidebar"[^>]*>.*?</aside>', published, re.S)
    if not head or not aside:
        raise ValueError("Course head or sidebar is missing")
    head = READER_BLOCK.sub("", head[0])
    sidebar = retarget_fragments(aside[0], plan["anchors"])
    trailing = published[published.rfind("</main>") + len("</main>"):]
    trailing = READER_BLOCK.sub("", trailing)
    if not trailing.endswith("</body></html>"):
        raise ValueError("Course document has an unexpected closing structure")
    publication = re.search(r'<section\b[^>]*class="document publication-note".*?</section>', published, re.S)
    disclosure = publication[0] if publication else ""
    record_manifest = []
    for index, record in enumerate(plan["records"]):
        body = retarget_fragments(record["html"], plan["anchors"])
        title = record["title"] or record["id"]
        page = (_chapter_head(head, title, canonical + record["href"]) +
                '<body class="qml-chapter"><a class="skip" href="#' + record["id"] + '">본문 바로가기</a>' + sidebar +
                '<main class="workspace">' + _pager(plan["records"], index) + body + _pager(plan["records"], index) + disclosure + '</main>' + trailing)
        (directory / record["href"]).write_text(page, encoding="utf-8")
        record_manifest.append({key: value for key, value in record.items() if key != "html"} |
                               {"rendered_section_sha256": sha256(body), "raw_page_bytes": len(page.encode("utf-8"))})
    items = []
    for record in plan["records"]:
        items.append(f'<li id="{html.escape(record["id"], quote=True)}"><a href="{record["href"]}#{record["id"]}">{html.escape(record["title"])}</a></li>')
    chapter_ids = {record["id"] for record in plan["records"]}
    fallback = []
    title_by_page = {record["href"]: record["title"] for record in plan["records"]}
    for anchor, target in plan["anchors"].items():
        if target == "index.html" or anchor in chapter_ids:
            continue
        fallback.append(f'<p class="qml-legacy-target" id="{html.escape(anchor, quote=True)}">'
                        f'<a href="{target}#{html.escape(anchor, quote=True)}">{html.escape(title_by_page[target])}에서 해당 위치 열기 →</a></p>')
    contents = ('<section class="document qml-course-contents" aria-labelledby="qml-contents-heading">'
                '<h2 id="qml-contents-heading">강의와 학습 자료</h2>'
                '<p><a href="study-guide.html#doc-study-guide">학습 안내에서 시작하기 →</a> · '
                '<a href="notes.pdf">통합 PDF</a></p><ol>' + ''.join(items) + '</ol></section>')
    entry_head = head.replace('</head>', f'<link rel="stylesheet" href="{_asset_href(NAVIGATION_CSS)}"></head>', 1)
    index_page = (entry_head + '<body class="qml-course-index" data-qml-course-index data-qml-source="' + plan["source_sha256"] + '"><a class="skip" href="#front-cover">본문 바로가기</a>' + sidebar +
                  '<main class="workspace">' + plan["cover"] + contents + ''.join(fallback) + disclosure + '</main>' +
                  f'<script defer src="{_asset_href(NAVIGATION_JS)}"></script>' + trailing)
    (directory / "index.html").write_text(index_page, encoding="utf-8")
    for name in (NAVIGATION_JS, NAVIGATION_CSS):
        (directory / name).write_bytes((SOURCE_ASSETS / name).read_bytes())
    manifest = {"version": 1, "course_href": COURSE_HREF, "source_sha256": plan["source_sha256"],
                "source_bytes": len(source.encode("utf-8")), "pages": record_manifest, "anchors": plan["anchors"],
                "files": [record["href"] for record in record_manifest] + [MANIFEST, NAVIGATION_JS, NAVIGATION_CSS],
                "reader_identity": "lecture:2026-10-20-quantum-machine-learning-lecture-notes-ko",
                "coverage": "Original document sections, equations, figures and IDs; only local fragment hrefs retargeted. Full print source is retained in authoring dist, complete reading copy is the unchanged PDF."}
    (directory / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def validate_chapters(directory: Path, source: str) -> list[str]:
    """Rebuild preservation expectations from the reviewed source, not metadata."""
    directory = Path(directory)
    errors = []
    try:
        path = directory / MANIFEST
        if path.is_symlink():
            raise ValueError("Chapter manifest must not be linked")
        manifest = json.loads(path.read_text(encoding="utf-8"))
        plan = source_plan(source)
        if manifest.get("version") != 1 or manifest.get("source_sha256") != plan["source_sha256"] or manifest.get("anchors") != plan["anchors"]:
            errors.append("chapter source or anchor map differs")
        expected_files = list(chapter_files(source))
        if manifest.get("files") != expected_files:
            errors.append("chapter generated file list differs")
        records = {record["href"]: record for record in manifest.get("pages", [])}
        if set(records) != {record["href"] for record in plan["records"]}:
            errors.append("chapter document set differs")
        for original in plan["records"]:
            path = directory / original["href"]
            if path.is_symlink() or not path.is_file():
                errors.append("missing or linked chapter: " + original["href"])
                continue
            current = SourceSections(path.read_text(encoding="utf-8"))
            body = [s["html"] for s in current.sections if s["attrs"].get("id") == original["id"]]
            expected = retarget_fragments(original["html"], plan["anchors"])
            if body != [expected]:
                errors.append("scientific section changed: " + original["href"])
            record = records.get(original["href"], {})
            if (any(record.get(key) != value for key, value in original.items() if key != "html")
                    or record.get("rendered_section_sha256") != sha256(expected)):
                errors.append("chapter source/content hash differs: " + original["href"])
        for name in (NAVIGATION_JS, NAVIGATION_CSS):
            path = directory / name
            if path.is_symlink() or path.read_bytes() != (SOURCE_ASSETS / name).read_bytes():
                errors.append("chapter navigation source differs: " + name)
        index = directory / "index.html"
        index_text = index.read_text(encoding="utf-8")
        if plan["cover"] not in index_text or any(record["html"] in index_text for record in plan["records"]):
            errors.append("course entry must preserve its cover without duplicating complete study sections")
        index_ids = set(Identifiers(index_text).ids)
        if not set(plan["anchors"]).issubset(index_ids):
            errors.append("legacy fragment fallback is missing")
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append("invalid chapter output: " + str(error))
    return errors
