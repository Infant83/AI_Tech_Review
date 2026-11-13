"""Publish explicitly registered, bilingual editorial readings of briefing PDFs.

Only compiled fragments named by publication/briefings/*.json are read.  Source
paths and fragments remain build inputs; the public document registry receives
only the generated page links and their hashes.
"""
from __future__ import annotations

from datetime import date
import hashlib
import html
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import parse_qsl, unquote, urlsplit

try:
    from .site_brand import SITE_NAME, SITE_STYLES_VERSION, render_brand_link
    from .briefing_routes import BRIEFING_SERIES, editorial_paths
except ImportError:
    from site_brand import SITE_NAME, SITE_STYLES_VERSION, render_brand_link
    from briefing_routes import BRIEFING_SERIES, editorial_paths


REGISTRY_KEYS = {"version", "id", "updated", "evidence_cutoff", "ko", "en"}
ALLOWED_TAGS = {"p", "h2", "h3", "strong", "em", "ol", "ul", "li", "a", "code", "span", "br"}
PUBLIC_ROOTS = {"reviews", "archive", "briefings", "lectures", "methods", "assets"}
TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,95}\Z")
PRIVATE_TEXT = re.compile(
    r"(?:/Users/|/home/|(?<![A-Za-z])[A-Za-z]:[\\/]|file\s*:|\.codex\b|"
    r"mail\.google\.com|gmail\.(?:com|google)|(?:^|[\s/\\])private[/\\]|"
    r"PRIVATE_(?:MAIL|SOURCE|TOKEN|PATH|ID)|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})", re.I
)


def _public_text(value: str) -> None:
    if PRIVATE_TEXT.search(value) or any(ord(char) < 32 and char not in "\n\t\r" for char in value):
        raise ValueError("briefing editorial contains private or non-public text")


def _iso_date(value: object, label: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"invalid editorial {label}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"invalid editorial {label}") from exc


def _regular_file(repo: Path, relative: object, suffix: str) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or "%" in relative:
        raise ValueError("editorial source must be a public repository-relative file")
    path = PurePosixPath(relative)
    if (path.is_absolute() or path.as_posix() != relative or path.suffix != suffix
            or any(part in {".", ".."} or part.startswith(".") for part in path.parts)
            or any("private" in part.lower() for part in path.parts)):
        raise ValueError("editorial source must be a public repository-relative file")
    current = repo
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("editorial source cannot be a symlink")
    if not current.is_file() or not current.resolve().is_relative_to(repo.resolve()):
        raise ValueError("missing editorial source or source outside repository")
    return current


def _href(value: str, prefix: str) -> str:
    _public_text(value)
    if not value or any(char.isspace() or ord(char) < 32 for char in value) or "\\" in value:
        raise ValueError("invalid briefing editorial link")
    decoded = unquote(value)
    if decoded != unquote(decoded) or "\\" in decoded:
        raise ValueError("encoded editorial links are not allowed")
    parsed = urlsplit(value)
    if parsed.scheme:
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("editorial links must use public HTTPS")
        host = parsed.hostname.lower().rstrip(".")
        if host in {"localhost", "localhost.localdomain"} or host.endswith((".localhost", ".local", ".internal", ".lan", ".home", ".test", ".invalid")) or "." not in host:
            raise ValueError("editorial links must use public HTTPS")
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
        if address is None and re.fullmatch(r"[0-9.]+", host):
            raise ValueError("editorial links must use public HTTPS")
        if address is not None and not address.is_global:
            raise ValueError("editorial links must use public HTTPS")
        try:
            if parsed.port not in {None, 443}:
                raise ValueError("editorial links must use public HTTPS")
        except ValueError as exc:
            raise ValueError("invalid public HTTPS port") from exc
        if any(key.lower().startswith("utm_") or key.lower() in {"token", "access_token", "auth", "authorization", "password", "otp", "fbclid", "gclid"}
               for key, _ in parse_qsl(parsed.query)):
            raise ValueError("editorial links cannot contain private or tracking parameters")
        _public_text(decoded)
        return value
    if parsed.netloc or parsed.query:
        raise ValueError("editorial relative link must name a public page")
    if not parsed.path:
        if parsed.fragment and TOKEN.fullmatch(parsed.fragment):
            return value
        raise ValueError("invalid editorial reference anchor")
    path = PurePosixPath(unquote(parsed.path))
    if (path.is_absolute() or any(part in {".", ".."} or part.startswith(".") for part in path.parts)
            or "//" in parsed.path or ":" in parsed.path
            or (path.parts[0] not in PUBLIC_ROOTS and parsed.path != "index.html")):
        raise ValueError("editorial relative link must name a public page")
    if parsed.fragment and not TOKEN.fullmatch(parsed.fragment):
        raise ValueError("invalid editorial reference anchor")
    return prefix + value


class _Fragment(HTMLParser):
    def __init__(self, prefix: str) -> None:
        super().__init__(convert_charrefs=True)
        self.prefix = prefix
        self.parts: list[str] = []
        self.stack: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in ALLOWED_TAGS:
            raise ValueError(f"disallowed editorial HTML tag: {tag}")
        values = {}
        for name, value in attrs:
            if name in values or name not in {"href", "id", "class"} or value is None:
                raise ValueError("disallowed editorial HTML attribute")
            if name == "href":
                if tag != "a":
                    raise ValueError("editorial href belongs on a link")
                value = _href(value, self.prefix)
            elif name == "class":
                if not value.split() or not all(TOKEN.fullmatch(token) for token in value.split()):
                    raise ValueError("invalid editorial class")
            elif not TOKEN.fullmatch(value) or value in self.ids:
                raise ValueError("invalid or duplicate editorial id")
            else:
                self.ids.add(value)
            values[name] = value
        if tag == "a" and "a" in self.stack:
            raise ValueError("nested editorial links are not allowed")
        attributes = "".join(f' {name}="{html.escape(value, quote=True)}"' for name, value in values.items())
        self.parts.append(f"<{tag}{attributes}>")
        if tag != "br":
            self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "br":
            raise ValueError("only br may be a self-closing editorial tag")
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if not self.stack or self.stack[-1] != tag:
            raise ValueError("unbalanced editorial HTML")
        self.stack.pop()
        self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        _public_text(data)
        self.parts.append(html.escape(data, quote=False))

    def handle_comment(self, data: str) -> None:
        raise ValueError("editorial HTML comments are not public content")

    def handle_decl(self, decl: str) -> None:
        raise ValueError("editorial fragment cannot contain a declaration")

    def handle_pi(self, data: str) -> None:
        raise ValueError("editorial fragment cannot contain processing instructions")

    def unknown_decl(self, data: str) -> None:
        raise ValueError("editorial fragment cannot contain a declaration")


def validate_fragment(fragment: str, prefix: str = "") -> str:
    """Validate and serialize a passive fragment, rewriting public relative links."""
    _public_text(fragment)
    parser = _Fragment(prefix)
    parser.feed(fragment)
    parser.close()
    if parser.stack or not fragment.strip() or not any(piece.startswith("<p") for piece in parser.parts):
        raise ValueError("empty or unbalanced editorial HTML")
    return "".join(parser.parts)


def _render(document: dict, spec: dict, fragment: str, base_url: str, language: str) -> str:
    en = language == "en"
    relative = document["editorial_en_href" if en else "editorial_href"]
    other = document["editorial_href" if en else "editorial_en_href"]
    prefix = "../" * (len(PurePosixPath(relative).parts) - 1)
    title = document["title_en" if en else "title"]
    summary = document["summary_en" if en else "summary"]
    escape = lambda value: html.escape(str(value), quote=True)
    body = validate_fragment(fragment, prefix)
    canonical = base_url.rstrip("/") + "/" + relative.removesuffix("index.html")
    links = [("ko", document["editorial_href"]), ("en", document["editorial_en_href"])]
    alternates = "".join(f'<link rel="alternate" hreflang="{lang}" href="{escape(base_url.rstrip("/") + "/" + path.removesuffix("index.html"))}">' for lang, path in links)
    return f'''<!doctype html><html lang="{language}"><head>
      <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{escape(title)} | {SITE_NAME}</title><meta name="description" content="{escape(summary)}">
      <link rel="canonical" href="{escape(canonical)}">{alternates}
      <meta property="og:type" content="article"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(summary)}"><meta property="og:url" content="{escape(canonical)}">
      <link rel="stylesheet" href="{prefix}assets/site.css?v={SITE_STYLES_VERSION}"><link rel="stylesheet" href="{prefix}assets/briefings.css">
      <style>.briefing-editorial{{max-width:70ch;margin:2rem auto;padding:0 1.25rem 3rem;font-size:16px;line-height:1.85}}.briefing-editorial h1{{font-size:2rem;line-height:1.35}}.briefing-editorial h2{{font-size:1.4rem;margin-top:2rem}}.briefing-editorial h3{{font-size:1.15rem}}.briefing-editorial-meta,.briefing-editorial-byline{{font-size:.9rem}}.briefing-editorial-links{{display:flex;gap:1rem;flex-wrap:wrap;margin:1.5rem 0}}.briefing-editorial li{{margin:.5rem 0}}.briefing-editorial a{{overflow-wrap:anywhere}}</style>
      </head><body class="briefings-page">
      <header class="site-header"><nav class="topbar" aria-label="{'Main navigation' if en else '주요 링크'}">{render_brand_link(prefix)}<span class="topbar-links"><a href="{prefix}methods/">{'Editorial methods' if en else '작성·검증 원칙'}</a><a href="{prefix}{other}" lang="{'ko' if en else 'en'}" hreflang="{'ko' if en else 'en'}">{'한국어' if en else 'English'}</a></span></nav></header>
      <main class="briefing-editorial"><article>
      <p class="section-kicker">{'Briefing' if en else '브리핑'}</p><h1>{escape(title)}</h1>
      <p class="briefing-editorial-meta">{'Original issue' if en else '원호 발행'} <time datetime="{document['date']}">{document['date']}</time> · {'Editorial updated' if en else '편집글 개정'} <time datetime="{spec['updated']}">{spec['updated']}</time> · {'Evidence through' if en else '추가 근거 기준'} <time datetime="{spec['evidence_cutoff']}">{spec['evidence_cutoff']}</time></p>
      <p class="briefing-editorial-byline">{'Responsible editor: Hyun-Jung Kim · AI assistance: OpenAI Codex' if en else '책임 편집자 김현중 · AI 보조 OpenAI Codex'}</p>
      <p class="briefing-editorial-summary">{escape(summary)}</p>
      <div class="briefing-editorial-body">{body}</div>
      <nav class="briefing-editorial-links" aria-label="{'Related reading' if en else '관련 자료'}"><a href="{prefix}briefings/{'en/' if en else ''}">{'Briefing list' if en else '브리핑 목록'}</a><a href="{prefix}{escape(document['href'])}" target="_blank" rel="noopener">{'Read archived PDF' if en else '보관 PDF 읽기'} ↗</a><a href="{prefix}{escape(document['href'])}" download>{'Download PDF' if en else 'PDF 다운로드'} ↓</a></nav>
      </article></main></body></html>'''


def stage_editorials(repo: Path, staging_root: Path, documents: list[dict], base_url: str, decorate) -> dict[str, str]:
    """Stage registered pages, enrich documents, and return public paths/hashes.

    An absent registry is valid and preserves the original PDF-only behavior.
    Validation completes before documents are changed or any page is written.
    """
    repo, staging_root = Path(repo), Path(staging_root)
    registry = repo / "publication" / "briefings"
    if not registry.exists():
        if registry.is_symlink():
            raise ValueError("editorial registry cannot be a symlink")
        return {}
    for parent in (repo / "publication", registry):
        if parent.is_symlink() or not parent.is_dir():
            raise ValueError("editorial registry must be a regular repository directory")
    by_id = {document["id"]: document for document in documents}
    if len(by_id) != len(documents):
        raise ValueError("duplicate briefing document id")
    prepared = []
    targets: set[str] = set()
    for registration in sorted(registry.glob("*.json")):
        _regular_file(repo, registration.relative_to(repo).as_posix(), ".json")
        try:
            spec = json.loads(registration.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as exc:
            raise ValueError("invalid briefing editorial registry") from exc
        if not isinstance(spec, dict) or set(spec) != REGISTRY_KEYS or type(spec["version"]) is not int or spec["version"] != 1:
            raise ValueError("invalid briefing editorial registry fields")
        if spec["ko"] == spec["en"]:
            raise ValueError("bilingual editorials require two source manuscripts")
        identity = spec["id"]
        if not isinstance(identity, str) or identity != registration.stem or identity not in by_id:
            raise ValueError("editorial must name an existing registered document")
        document = by_id[identity]
        issue_date = _iso_date(document.get("date"), "issue date")
        if document.get("series") not in BRIEFING_SERIES or not identity.startswith(issue_date.isoformat() + "-") or not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*", identity):
            raise ValueError("editorial must name a briefing with a matching issue date")
        updated = _iso_date(spec["updated"], "updated date")
        cutoff = _iso_date(spec["evidence_cutoff"], "evidence cutoff")
        if updated < issue_date or cutoff > updated:
            raise ValueError("editorial dates do not match the issue and update")
        for key in ("title", "title_en", "summary", "summary_en"):
            if not isinstance(document.get(key), str) or not document[key].strip():
                raise ValueError("bilingual briefing title and summary are required")
            _public_text(document[key])
        href = document.get("href", "")
        if not isinstance(href, str) or not href.startswith("archive/files/") or not href.endswith(".pdf") or _href(href, "") != href:
            raise ValueError("editorial must retain a registered public PDF")
        enriched = dict(document)
        enriched["editorial_href"], enriched["editorial_en_href"] = editorial_paths(issue_date.isoformat(), document["series"])
        enriched["editorial_updated"] = spec["updated"]
        pages = {}
        for language in ("ko", "en"):
            source = _regular_file(repo, spec[language], ".html")
            fragment = source.read_text(encoding="utf-8")
            relative = enriched["editorial_en_href" if language == "en" else "editorial_href"]
            if relative in targets:
                raise ValueError("briefing editorial output collision")
            targets.add(relative)
            prefix = "../" * (len(PurePosixPath(relative).parts) - 1)
            rendered = decorate(_render(enriched, spec, fragment, base_url, language), prefix)
            if not isinstance(rendered, str):
                raise ValueError("editorial decorator must return HTML text")
            pages[relative] = rendered.encode("utf-8")
        prepared.append((document, enriched, pages))
    assets = {}
    for document, enriched, pages in prepared:
        hashes = {}
        for relative, content in pages.items():
            output = staging_root / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
            hashes[relative] = hashlib.sha256(content).hexdigest()
        document.update({"editorial_href": enriched["editorial_href"], "editorial_en_href": enriched["editorial_en_href"], "editorial_updated": enriched["editorial_updated"], "editorial_assets": hashes})
        assets.update(hashes)
    return assets
