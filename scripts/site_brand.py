"""Shared publication mark for the public catalog headers."""
from html import escape
from html.parser import HTMLParser
import re


ICON_ASSET_VERSION = "20261022-prompt-brace"
SITE_STYLES_VERSION = "20261022-header-brand"
BRAND_TITLE = "Agentic Tech Review"
SITE_NAME = f"{BRAND_TITLE} Letters"
SITE_SHORT_NAME = "ATRL"

_LEGACY_NAME = re.compile(r"AI\s+Tech\s+Review\s+Letters", re.IGNORECASE)
_VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"})


def current_source_title(value: str) -> str:
    """Use the current own-publication name in generated search metadata only."""
    return SITE_NAME if _LEGACY_NAME.fullmatch(value.strip()) else value


class _CurrentBrandParser(HTMLParser):
    """Locate current chrome without reserializing any scientific HTML."""

    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.lines = [0]
        self.lines.extend(match.end() for match in re.finditer("\n", source))
        self.stack: list[tuple[str, frozenset[str]]] = []
        self.edits: list[tuple[int, int, str]] = []

    def position(self) -> int:
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "meta" and values.get("property", "").lower() == "og:site_name":
            if _LEGACY_NAME.fullmatch(values.get("content", "").strip()):
                raw = self.get_starttag_text()
                match = re.search(r"\bcontent\s*=\s*([\"'])(.*?)\1", raw, re.IGNORECASE | re.DOTALL)
                if match:
                    start = self.position() + match.start(2)
                    self.edits.append((start, self.position() + match.end(2), SITE_NAME))
        if tag not in _VOID_TAGS:
            self.stack.append((tag, frozenset((values.get("class") or "").split())))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in _VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if any(tag in {"article", "script", "style", "pre", "code"} for tag, _ in self.stack):
            return
        tags = {tag for tag, _ in self.stack}
        classes = set().union(*(values for _, values in self.stack)) if self.stack else set()
        match = None
        if "title" in tags:
            match = re.search(r"(?<=[|·])\s*(AI\s+Tech\s+Review\s+Letters)\s*$", data, re.IGNORECASE)
            if match:
                start, end = match.span(1)
                self.edits.append((self.position() + start, self.position() + end, SITE_NAME))
            return
        footer = "footer" in tags or "footer" in classes
        chrome = bool(classes & {"brand", "brand-name", "eyebrow"}) or any(
            tag == "nav" and "top" in values for tag, values in self.stack)
        if chrome and _LEGACY_NAME.fullmatch(data.strip()):
            match = _LEGACY_NAME.search(data)
        elif footer:
            match = re.match(r"\s*(AI\s+Tech\s+Review\s+Letters)(?=\s*(?:[·|]|$))", data, re.IGNORECASE)
            if match:
                start, end = match.span(1)
                original = data[start:end]
                replacement = SITE_NAME.upper() if original.isupper() else SITE_NAME
                self.edits.append((self.position() + start, self.position() + end, replacement))
            return
        if match:
            replacement = SITE_NAME.upper() if match.group().isupper() else SITE_NAME
            self.edits.append((self.position() + match.start(), self.position() + match.end(), replacement))


def normalize_brand_html(source: str) -> str:
    """Patch only current journal chrome; retain issue labels, prose and bytes."""
    parser = _CurrentBrandParser(source)
    parser.feed(source)
    parser.close()
    for start, end, value in reversed(parser.edits):
        source = source[:start] + value + source[end:]
    return source


def render_brand_link(asset_prefix: str = "", *, stacked: bool = False) -> str:
    prefix = escape(asset_prefix, quote=True)
    name = f'<b>{BRAND_TITLE}</b> <small>LETTERS</small>' if stacked else SITE_NAME
    return (
        f'<a class="brand" href="{prefix}index.html">'
        f'<img class="brand-icon" src="{prefix}assets/apple-touch-icon.png?v={ICON_ASSET_VERSION}" '
        'width="44" height="44" alt="" aria-hidden="true">'
        f'<span class="brand-name">{name}</span></a>'
    )
