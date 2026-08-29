from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import markdown


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
FENCED_CODE_START_RE = re.compile(
    r"(?m)^ {0,3}(?P<fence>`{3,}|~{3,})[^\n]*(?:\n|\Z)"
)
INDENTED_CODE_LINE_RE = re.compile(r"(?m)^(?: {4}|\t)[^\n]*(?:\n|\Z)")
BLOCKQUOTE_PREFIX_RE = re.compile(r"(?: {0,3}>[ \t]?)+")
AUTOLINK_RE = re.compile(r"<[A-Za-z][A-Za-z0-9+.-]*:[^<>\s]+>")
OPAQUE_HTML_TAGS = {"script", "style", "pre", "code", "textarea", "noscript"}
RAW_HTML_TAG_RE = re.compile(
    r"</?[A-Za-z][A-Za-z0-9:-]*"
    r"(?:\s+[A-Za-z_:][A-Za-z0-9:._-]*"
    r"(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s\"'=<>`]+))?)*"
    r"\s*/?>"
)
SECTION_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BARE_URL_RE = re.compile(r"(?<!\()https?://[^\s<>)]+")


@dataclass
class LinkItem:
    label: str
    href: str
    external: bool


@dataclass(frozen=True)
class ProtectedMathExpression:
    source: str
    placeholder: str


@dataclass
class RenderContext:
    title: str
    subtitle: str
    language: str
    canonical_url: str
    alternate_ko_url: str
    alternate_en_url: str
    alternate_default_url: str
    social_image_url: str
    author: str
    published_date: str
    modified_date: str
    issue_label: str
    source_path: Path
    output_path: Path
    mode: str
    body_html: str
    toc_html: str
    summary_points: list[str]
    links: list[LinkItem]
    section_count: int
    generated_at: str
    source_modified_at: str


FINAL_REVIEW_LABELS = {
    "ko": {
        "signals": "읽기 전에 볼 신호",
        "toc": "섹션 맵",
        "links": "근거 링크",
        "empty_links": "이 리포트에서 명시적 링크가 감지되지 않았습니다.",
        "glossary": "용어 풀이",
        "generated": "생성 시각",
        "source_modified": "원본 파일 최종 수정 시각",
        "language_nav": "언어 선택",
        "korean": "한국어",
        "english": "English",
    },
    "en": {
        "signals": "Signals to note before reading",
        "toc": "Section map",
        "links": "Evidence links",
        "empty_links": "No explicit links were detected in this report.",
        "glossary": "Notes and terminology",
        "generated": "Generated",
        "source_modified": "Source last modified",
        "language_nav": "Language",
        "korean": "Korean",
        "english": "English",
    },
}


def strip_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    metadata: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        metadata[key.strip().lower()] = value.strip()
    return metadata, text[match.end() :]


def metadata_value(metadata: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = metadata.get(key.lower(), "").strip()
        if not value:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            return value[1:-1].strip()
        return value
    return ""


def normalize_language(value: str) -> str:
    return "en" if value.strip().lower().startswith("en") else "ko"


def final_review_labels(language: str) -> dict[str, str]:
    return FINAL_REVIEW_LABELS[normalize_language(language)]


def render_document_metadata(context: RenderContext) -> str:
    title = html.escape(context.title, quote=True)
    description = html.escape(context.subtitle, quote=True)
    canonical = html.escape(context.canonical_url, quote=True)
    social_image = html.escape(context.social_image_url, quote=True)
    locale = "en_US" if context.language == "en" else "ko_KR"
    alternate_locale = "ko_KR" if context.language == "en" else "en_US"
    lines: list[str] = []

    if context.subtitle:
        lines.append(f'  <meta name="description" content="{description}">')
    if context.canonical_url:
        lines.append(f'  <link rel="canonical" href="{canonical}">')

    alternates = (
        ("ko", context.alternate_ko_url),
        ("en", context.alternate_en_url),
        ("x-default", context.alternate_default_url),
    )
    for language, href in alternates:
        if href:
            lines.append(
                f'  <link rel="alternate" hreflang="{language}" '
                f'href="{html.escape(href, quote=True)}">'
            )

    lines.extend(
        [
            '  <meta property="og:type" content="article">',
            '  <meta property="og:site_name" content="AI Tech Review Letters">',
            f'  <meta property="og:title" content="{title}">',
        ]
    )
    if context.subtitle:
        lines.append(f'  <meta property="og:description" content="{description}">')
    if context.canonical_url:
        lines.append(f'  <meta property="og:url" content="{canonical}">')
    lines.append(f'  <meta property="og:locale" content="{locale}">')
    has_locale_alternate = (
        context.language == "en" and bool(context.alternate_ko_url)
    ) or (
        context.language == "ko" and bool(context.alternate_en_url)
    )
    if has_locale_alternate:
        lines.append(f'  <meta property="og:locale:alternate" content="{alternate_locale}">')
    if context.social_image_url:
        lines.extend(
            [
                f'  <meta property="og:image" content="{social_image}">',
                f'  <meta property="og:image:alt" content="{title}">',
            ]
        )
    if context.published_date:
        lines.append(
            f'  <meta property="article:published_time" '
            f'content="{html.escape(context.published_date, quote=True)}">'
        )
    if context.modified_date:
        lines.append(
            f'  <meta property="article:modified_time" '
            f'content="{html.escape(context.modified_date, quote=True)}">'
        )
    if context.author:
        lines.append(f'  <meta name="author" content="{html.escape(context.author, quote=True)}">')

    lines.extend(
        [
            '  <meta name="twitter:card" content="summary_large_image">',
            f'  <meta name="twitter:title" content="{title}">',
        ]
    )
    if context.subtitle:
        lines.append(f'  <meta name="twitter:description" content="{description}">')
    if context.social_image_url:
        lines.extend(
            [
                f'  <meta name="twitter:image" content="{social_image}">',
                f'  <meta name="twitter:image:alt" content="{title}">',
            ]
        )
    return "\n".join(lines)


def render_language_switch(context: RenderContext) -> str:
    if not context.alternate_ko_url or not context.alternate_en_url:
        return ""

    labels = final_review_labels(context.language)
    ko_url = html.escape(context.alternate_ko_url, quote=True)
    en_url = html.escape(context.alternate_en_url, quote=True)
    if context.language == "en":
        options = (
            f'<a href="{ko_url}" lang="ko" hreflang="ko">{labels["korean"]}</a>'
            f'<span lang="en" aria-current="page">{labels["english"]}</span>'
        )
    else:
        options = (
            f'<span lang="ko" aria-current="page">{labels["korean"]}</span>'
            f'<a href="{en_url}" lang="en" hreflang="en">{labels["english"]}</a>'
        )
    return (
        f'<nav class="language-switch" aria-label="{html.escape(labels["language_nav"], quote=True)}">'
        f"{options}</nav>"
    )


def split_title(markdown_text: str, default_title: str) -> tuple[str, str]:
    match = HEADING_RE.search(markdown_text)
    if not match:
        return default_title, markdown_text.lstrip()

    title = match.group(1).strip()
    body = markdown_text[: match.start()] + markdown_text[match.end() :]
    return title, body.lstrip()


def extract_summary_points(markdown_text: str) -> list[str]:
    lines = markdown_text.splitlines()
    in_summary = False
    points: list[str] = []
    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if re.match(r"^##\s+summary\s*$", stripped, re.IGNORECASE):
            in_summary = True
            continue
        if in_summary and stripped.startswith("#"):
            break
        if in_summary and line.startswith("- "):
            points.append(line[2:].strip())
        if len(points) == 4:
            break
    return points


def build_issue_label(metadata: dict[str, str]) -> str:
    raw_date = metadata.get("issue date") or metadata.get("date modified") or metadata.get("date") or metadata.get("date created")
    try:
        issue_date = datetime.fromisoformat(raw_date).date() if raw_date else datetime.now().date()
    except ValueError:
        issue_date = datetime.now().date()
    week = issue_date.isocalendar().week
    return f"AI Tech Review Letters: Week {week:02d} ({issue_date.isoformat()})"


def extract_links(markdown_text: str) -> list[LinkItem]:
    seen: set[str] = set()
    items: list[LinkItem] = []

    def add_item(label: str, href: str) -> None:
        normalized = href.strip()
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        parsed = urlparse(normalized)
        external = parsed.scheme in {"http", "https"}
        final_label = label.strip() or normalized
        if not external and not Path(normalized).suffix:
            final_label = final_label
        items.append(LinkItem(label=final_label, href=normalized, external=external))

    for match in MARKDOWN_LINK_RE.finditer(markdown_text):
        add_item(match.group(1), match.group(2))

    for match in BARE_URL_RE.finditer(markdown_text):
        url = match.group(0)
        parsed = urlparse(url)
        label = parsed.netloc or url
        add_item(label, url)

    return items


CUSTOM_BLOCK_LABELS = {
    "highlight": "Highlight",
    "think": "생각하기",
    "thinking": "생각하기",
    "evidence": "Evidence note",
    "operator": "Operator note",
    "pose": "Pose",
    "bundle": "글묶음",
}


def preprocess_custom_blocks(markdown_text: str) -> str:
    """Convert lightweight article directives into markdown-in-html blocks."""
    lines = markdown_text.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^:::\s*([a-zA-Z_-]+)(?:\s+(.*?))?\s*$", line)
        if not match:
            output.append(line)
            index += 1
            continue

        block_name = match.group(1).strip().lower()
        if block_name not in CUSTOM_BLOCK_LABELS:
            output.append(line)
            index += 1
            continue

        title = (match.group(2) or CUSTOM_BLOCK_LABELS[block_name]).strip()
        block_lines: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip() != ":::":
            block_lines.append(lines[index])
            index += 1
        if index < len(lines) and lines[index].strip() == ":::":
            index += 1

        safe_title = html.escape(title, quote=True)
        safe_block_name = re.sub(r"[^a-z0-9_-]+", "-", block_name)
        output.extend(
            [
                f'<aside class="callout callout-{safe_block_name}" markdown="1">',
                f'<p class="callout-label">{safe_title}</p>',
                "",
                *block_lines,
                "",
                "</aside>",
            ]
        )

    return "\n".join(output)


def _is_escaped(text: str, index: int) -> bool:
    backslashes = 0
    cursor = index - 1
    while cursor >= 0 and text[cursor] == "\\":
        backslashes += 1
        cursor -= 1
    return backslashes % 2 == 1


def _fenced_code_end(markdown_text: str, index: int) -> int | None:
    opening = FENCED_CODE_START_RE.match(markdown_text, index)
    if not opening:
        return None

    fence = opening.group("fence")
    closing_re = re.compile(
        rf"(?m)^ {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}"
        r"[ \t]*\r?(?:\n|\Z)"
    )
    closing = closing_re.search(markdown_text, opening.end())
    return closing.end() if closing else len(markdown_text)


def _indented_code_end(markdown_text: str, index: int) -> int | None:
    if index > 0:
        previous_end = index - 1
        previous_start = markdown_text.rfind("\n", 0, previous_end) + 1
        if markdown_text[previous_start:previous_end].strip():
            return None

    opening = INDENTED_CODE_LINE_RE.match(markdown_text, index)
    if not opening:
        return None

    block_end = opening.end()
    cursor = block_end
    while cursor < len(markdown_text):
        line_end = markdown_text.find("\n", cursor)
        line_end = len(markdown_text) if line_end < 0 else line_end + 1
        line = markdown_text[cursor:line_end]
        if line.strip() and not line.startswith(("    ", "\t")):
            break
        block_end = line_end
        cursor = line_end
    return block_end


def _code_span_end(markdown_text: str, index: int) -> tuple[int, int | None]:
    opening_end = index + 1
    while opening_end < len(markdown_text) and markdown_text[opening_end] == "`":
        opening_end += 1
    opening_length = opening_end - index

    cursor = opening_end
    while cursor < len(markdown_text):
        candidate = markdown_text.find("`", cursor)
        if candidate < 0:
            break
        candidate_end = candidate + 1
        while (
            candidate_end < len(markdown_text)
            and markdown_text[candidate_end] == "`"
        ):
            candidate_end += 1
        if candidate_end - candidate == opening_length:
            return opening_end, candidate_end
        cursor = candidate_end
    return opening_end, None


def _markdown_bracket_end(markdown_text: str, index: int) -> int | None:
    depth = 0
    cursor = index
    while cursor < len(markdown_text):
        character = markdown_text[cursor]
        if character == "\\" and not _is_escaped(markdown_text, cursor):
            cursor += 2
            continue
        if character == "[":
            depth += 1
        elif character == "]":
            depth -= 1
            if depth == 0:
                return cursor + 1
        cursor += 1
    return None


def _markdown_destination_end(markdown_text: str, index: int) -> int | None:
    if not markdown_text.startswith("(", index):
        return None

    depth = 0
    quote: str | None = None
    cursor = index
    while cursor < len(markdown_text):
        character = markdown_text[cursor]
        if character == "\\" and not _is_escaped(markdown_text, cursor):
            cursor += 2
            continue
        if quote:
            if character == quote:
                quote = None
        elif (
            character in {'"', "'"}
            and cursor > index
            and markdown_text[cursor - 1].isspace()
        ):
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return cursor + 1
        cursor += 1
    return None


def _markdown_image_end(markdown_text: str, index: int) -> int | None:
    if not markdown_text.startswith("![", index):
        return None
    label_end = _markdown_bracket_end(markdown_text, index + 1)
    if label_end is None:
        return None
    destination_end = _markdown_destination_end(markdown_text, label_end)
    if destination_end is not None:
        return destination_end
    if markdown_text.startswith("[", label_end):
        return _markdown_bracket_end(markdown_text, label_end) or label_end
    return label_end


def _raw_html_end(markdown_text: str, index: int) -> int | None:
    autolink = AUTOLINK_RE.match(markdown_text, index)
    if autolink:
        return autolink.end()
    if markdown_text.startswith("<!--", index):
        closing = markdown_text.find("-->", index + 4)
        return len(markdown_text) if closing < 0 else closing + 3
    if markdown_text.startswith("<![CDATA[", index):
        closing = markdown_text.find("]]>", index + 9)
        return len(markdown_text) if closing < 0 else closing + 3
    if markdown_text.startswith("<?", index):
        closing = markdown_text.find("?>", index + 2)
        return len(markdown_text) if closing < 0 else closing + 2

    remainder = markdown_text[index:]
    opening_tag = re.match(r"<(?P<tag>[A-Za-z][A-Za-z0-9:-]*)(?:\s|/?>)", remainder)
    if not re.match(r"</?[A-Za-z]", remainder) and not re.match(
        r"<![A-Za-z]", remainder
    ):
        return None

    quote: str | None = None
    cursor = index + 1
    while cursor < len(markdown_text):
        character = markdown_text[cursor]
        if quote:
            if character == quote:
                quote = None
        elif character in {'"', "'"}:
            quote = character
        elif character == ">":
            tag_end = cursor + 1
            tag_source = markdown_text[index:tag_end]
            if remainder.startswith(("<", "</")) and not remainder.startswith("<!"):
                if not RAW_HTML_TAG_RE.fullmatch(tag_source):
                    return None
            if (
                opening_tag
                and opening_tag.group("tag").lower() in OPAQUE_HTML_TAGS
                and not markdown_text[index:tag_end].rstrip().endswith("/>")
            ):
                tag = re.escape(opening_tag.group("tag"))
                closing = re.compile(rf"</{tag}\s*>", re.IGNORECASE).search(
                    markdown_text, tag_end
                )
                return closing.end() if closing else len(markdown_text)
            return tag_end
        cursor += 1
    return None


def _find_math_closer(
    markdown_text: str, start: int, delimiter: str
) -> int | None:
    cursor = start
    while True:
        candidate = markdown_text.find(delimiter, cursor)
        if candidate < 0:
            return None
        if not _is_escaped(markdown_text, candidate) and candidate > start:
            return candidate + len(delimiter)
        cursor = candidate + len(delimiter)


def _inline_dollar_end(markdown_text: str, index: int) -> int | None:
    if (
        _is_escaped(markdown_text, index)
        or index + 1 >= len(markdown_text)
        or markdown_text[index + 1] == "$"
        or markdown_text[index + 1].isspace()
    ):
        return None

    cursor = index + 1
    while True:
        candidate = markdown_text.find("$", cursor)
        if candidate < 0 or "\n" in markdown_text[index:candidate]:
            return None
        escaped = _is_escaped(markdown_text, candidate)
        following = markdown_text[candidate + 1 : candidate + 2]
        body = markdown_text[index + 1 : candidate]
        previous = markdown_text[candidate - 1]
        pipe_can_close = (
            previous != "|"
            or body.startswith(("|", r"\|", r"\lvert", r"\left|"))
        )
        if (
            not escaped
            and previous != "$"
            and not previous.isspace()
            and previous not in "([{/+-–—"
            and pipe_can_close
            and following != "$"
            and not following.isdigit()
        ):
            return candidate + 1
        if not escaped:
            return None
        cursor = candidate + 1


def _math_expression_end(
    markdown_text: str, index: int
) -> tuple[int, bool] | None:
    if markdown_text.startswith("$$", index) and not _is_escaped(
        markdown_text, index
    ):
        end = _find_math_closer(markdown_text, index + 2, "$$")
        return (end, True) if end is not None else None
    if markdown_text.startswith(r"\[", index) and not _is_escaped(
        markdown_text, index
    ):
        end = _find_math_closer(markdown_text, index + 2, r"\]")
        return (end, True) if end is not None else None
    if markdown_text.startswith(r"\(", index) and not _is_escaped(
        markdown_text, index
    ):
        end = _find_math_closer(markdown_text, index + 2, r"\)")
        return (end, False) if end is not None else None
    if markdown_text[index] == "$":
        end = _inline_dollar_end(markdown_text, index)
        return (end, False) if end is not None else None
    return None


def _normalize_blockquote_math(
    markdown_text: str, index: int, expression: str, display: bool
) -> str:
    if not display:
        return expression
    line_start = markdown_text.rfind("\n", 0, index) + 1
    prefix = markdown_text[line_start:index]
    if not BLOCKQUOTE_PREFIX_RE.fullmatch(prefix):
        return expression

    quote_depth = prefix.count(">")
    lines = expression.splitlines(keepends=True)
    normalized = [lines[0]]
    for line in lines[1:]:
        line_prefix = BLOCKQUOTE_PREFIX_RE.match(line)
        if not line_prefix or line_prefix.group(0).count(">") != quote_depth:
            return expression
        normalized.append(line[line_prefix.end() :])
    return "".join(normalized)


def _opaque_markdown_ranges(markdown_text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    cursor = 0
    while cursor < len(markdown_text):
        protected_start = cursor
        protected_end: int | None = None
        if cursor == 0 or markdown_text[cursor - 1] == "\n":
            protected_end = _fenced_code_end(markdown_text, cursor)
            if protected_end is None:
                protected_end = _indented_code_end(markdown_text, cursor)

        character = markdown_text[cursor]
        if (
            protected_end is None
            and character == "`"
            and not _is_escaped(markdown_text, cursor)
        ):
            opening_end, code_span_end = _code_span_end(markdown_text, cursor)
            if code_span_end is None:
                cursor = opening_end
                continue
            protected_end = code_span_end
        if protected_end is None and character == "!":
            protected_end = _markdown_image_end(markdown_text, cursor)
        if protected_end is None and character == "<":
            protected_end = _raw_html_end(markdown_text, cursor)
        if (
            protected_end is None
            and character == "]"
            and markdown_text.startswith("(", cursor + 1)
        ):
            protected_start = cursor + 1
            protected_end = _markdown_destination_end(markdown_text, protected_start)
        if (
            protected_end is None
            and character == "]"
            and markdown_text.startswith("[", cursor + 1)
        ):
            protected_start = cursor + 1
            protected_end = _markdown_bracket_end(markdown_text, protected_start)

        if protected_end is not None:
            ranges.append((protected_start, protected_end))
            cursor = protected_end
        else:
            cursor += 1
    return ranges


def _protect_math_in_prose(
    markdown_text: str,
    expressions: list[ProtectedMathExpression],
    placeholder_attribute: str,
) -> str:
    output: list[str] = []
    cursor = 0
    while cursor < len(markdown_text):
        character = markdown_text[cursor]
        if (
            character == "\\"
            and markdown_text.startswith(r"\$", cursor)
            and not _is_escaped(markdown_text, cursor)
        ):
            output.append('<span class="tex2jax_ignore">$</span>')
            cursor += 2
            continue

        math_end = _math_expression_end(markdown_text, cursor)
        if math_end is not None:
            expression_end, display = math_end
            expression = _normalize_blockquote_math(
                markdown_text,
                cursor,
                markdown_text[cursor:expression_end],
                display,
            )
            index = len(expressions)
            tag = "div" if display else "span"
            placeholder = (
                f'<{tag} {placeholder_attribute}="{index}"></{tag}>'
            )
            expressions.append(
                ProtectedMathExpression(source=expression, placeholder=placeholder)
            )
            output.append(placeholder)
            cursor = expression_end
            continue
        if character == "$":
            output.append('<span class="tex2jax_ignore">$</span>')
            cursor += 1
            continue

        output.append(character)
        cursor += 1

    return "".join(output)


def protect_math_expressions(
    markdown_text: str,
) -> tuple[str, list[ProtectedMathExpression]]:
    """Hide TeX from Markdown parsing, except inside code and raw HTML."""
    expressions: list[ProtectedMathExpression] = []
    output: list[str] = []
    cursor = 0
    placeholder_index = 0
    placeholder_attribute = f"data-ai-tech-math-{placeholder_index}"
    while placeholder_attribute in markdown_text:
        placeholder_index += 1
        placeholder_attribute = f"data-ai-tech-math-{placeholder_index}"

    for opaque_start, opaque_end in _opaque_markdown_ranges(markdown_text):
        output.append(
            _protect_math_in_prose(
                markdown_text[cursor:opaque_start],
                expressions,
                placeholder_attribute,
            )
        )
        output.append(markdown_text[opaque_start:opaque_end])
        cursor = opaque_end
    output.append(
        _protect_math_in_prose(
            markdown_text[cursor:], expressions, placeholder_attribute
        )
    )

    return "".join(output), expressions


def restore_math_expressions(
    html_text: str, expressions: list[ProtectedMathExpression]
) -> str:
    for expression in expressions:
        html_text = html_text.replace(
            expression.placeholder, html.escape(expression.source, quote=False)
        )
    return html_text


def build_markdown_html(markdown_text: str) -> tuple[str, str]:
    renderer = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists", "smarty", "md_in_html"],
        extension_configs={
            "toc": {
                "permalink": False,
                "title": "",
            }
        },
    )
    prepared = preprocess_custom_blocks(markdown_text)
    prepared, math_expressions = protect_math_expressions(prepared)
    body_html = renderer.convert(prepared)
    body_html = restore_math_expressions(body_html, math_expressions)
    toc_html = restore_math_expressions(renderer.toc or "", math_expressions)
    return body_html, toc_html


def format_timestamp(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def source_link_href(source_path: Path, output_path: Path) -> str:
    try:
        return source_path.relative_to(output_path.parent).as_posix()
    except ValueError:
        return source_path.name


def render_link_items(links: list[LinkItem], language: str = "ko") -> str:
    if not links:
        empty_label = final_review_labels(language)["empty_links"]
        return f'<li class="empty-state">{html.escape(empty_label)}</li>'

    rendered: list[str] = []
    for item in links:
        target_attr = ' target="_blank" rel="noreferrer"' if item.external else ""
        rendered.append(
            f'<li><a href="{html.escape(item.href, quote=True)}"{target_attr}>'
            f"{html.escape(item.label)}</a></li>"
        )
    return "\n".join(rendered)


def render_template(context: RenderContext) -> str:
    if context.mode == "final-review":
        return render_final_review_template(context)

    summary_html = ""
    if context.summary_points:
        items = "\n".join(
            f"<li>{html.escape(point)}</li>" for point in context.summary_points
        )
        summary_html = f"""
        <section class="summary-band" aria-labelledby="summary-heading">
          <h2 id="summary-heading">주요 신호</h2>
          <ul class="summary-list">
            {items}
          </ul>
        </section>
        """

    toc_panel = ""
    if context.toc_html.strip():
        toc_panel = f"""
        <section class="panel toc-panel" aria-labelledby="toc-heading">
          <h2 id="toc-heading">섹션 맵</h2>
          {context.toc_html}
        </section>
        """

    link_items = render_link_items(context.links, context.language)

    source_href = source_link_href(context.source_path, context.output_path)

    document_metadata = render_document_metadata(context)

    return f"""<!DOCTYPE html>
<html lang="{html.escape(context.language, quote=True)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(context.title)}</title>
{document_metadata}
  <link rel="icon" href="data:,">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%230f766e'/%3E%3Cpath d='M18 22h28v6H18zm0 14h20v6H18z' fill='%23ffffff'/%3E%3C/svg%3E">
  <style>
    :root {{
      --bg: #edf2f0;
      --surface: #ffffff;
      --surface-alt: #f6f8f7;
      --ink: #14201a;
      --muted: #52615a;
      --line: #d9e1dd;
      --accent: #0f766e;
      --accent-alt: #3f6212;
      --accent-warm: #c2410c;
      --shadow: 0 18px 40px rgba(20, 32, 26, 0.08);
      --radius: 8px;
      --wrap: 1220px;
    }}

    * {{
      box-sizing: border-box;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      font-family: "Segoe UI", "Noto Sans KR", Arial, sans-serif;
      color: var(--ink);
      background: linear-gradient(180deg, #f4f7f5 0%, var(--bg) 100%);
    }}

    a {{
      color: var(--accent);
      text-decoration: none;
    }}

    a:hover {{
      text-decoration: underline;
    }}

    .page {{
      width: min(var(--wrap), calc(100% - 32px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }}

    .masthead {{
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.7fr);
      gap: 24px;
      align-items: start;
      margin-bottom: 24px;
    }}

    .headline {{
      padding: 28px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}

    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 18px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid rgba(15, 118, 110, 0.18);
      background: rgba(15, 118, 110, 0.08);
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--accent);
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      font-size: 2.7rem;
      line-height: 1.02;
      font-weight: 800;
    }}

    .deck {{
      margin: 16px 0 0;
      max-width: 70ch;
      font-size: 1rem;
      line-height: 1.75;
      color: var(--muted);
    }}

    .meta-list {{
      margin: 24px 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}

    .meta-list li {{
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface-alt);
    }}

    .meta-list strong {{
      display: block;
      margin-bottom: 6px;
      font-size: 0.76rem;
      text-transform: uppercase;
      color: var(--accent-alt);
    }}

    .meta-list span {{
      display: block;
      font-size: 0.95rem;
      line-height: 1.5;
      word-break: break-word;
    }}

    .summary-band {{
      padding: 24px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: linear-gradient(180deg, #f8fbfa 0%, #eef4f1 100%);
      box-shadow: var(--shadow);
    }}

    .summary-band h2,
    .panel h2 {{
      margin: 0 0 14px;
      font-size: 1rem;
      line-height: 1.3;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--accent-alt);
    }}

    .summary-list {{
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 10px;
      line-height: 1.65;
    }}

    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 320px;
      gap: 24px;
      align-items: start;
    }}

    .report {{
      padding: 32px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}

    .report > :first-child {{
      margin-top: 0;
    }}

    .report h2 {{
      margin: 38px 0 14px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      font-size: 1.5rem;
      line-height: 1.2;
    }}

    .report h3 {{
      margin: 24px 0 12px;
      font-size: 1.1rem;
      line-height: 1.35;
    }}

    .report p,
    .report li {{
      font-size: 1rem;
      line-height: 1.8;
      color: var(--ink);
    }}

    .report ul,
    .report ol {{
      margin: 0 0 18px;
      padding-left: 22px;
    }}

    .report li + li {{
      margin-top: 8px;
    }}

    .report strong {{
      color: var(--ink);
    }}

    .report blockquote {{
      margin: 20px 0;
      padding: 16px 18px;
      border-left: 4px solid var(--accent);
      background: #f5f9f8;
      color: var(--muted);
    }}

    .report code {{
      padding: 2px 6px;
      border-radius: 6px;
      background: #eef4f1;
      font-family: "Cascadia Code", Consolas, monospace;
      font-size: 0.92rem;
    }}

    .report pre {{
      margin: 18px 0;
      padding: 16px;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #f3f7f5;
    }}

    .report pre code {{
      padding: 0;
      background: transparent;
    }}

    .report table {{
      width: 100%;
      border-collapse: collapse;
      margin: 18px 0;
      display: block;
      overflow-x: auto;
    }}

    .report th,
    .report td {{
      padding: 12px 14px;
      border: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      min-width: 140px;
    }}

    .report th {{
      background: #f4f8f6;
      color: var(--accent-alt);
      font-weight: 700;
    }}

    .sidebar {{
      position: sticky;
      top: 24px;
      display: grid;
      gap: 16px;
    }}

    .panel {{
      padding: 18px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}

    .toc-panel ul,
    .link-panel ul {{
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 8px;
      line-height: 1.55;
    }}

    .toc-panel li,
    .link-panel li {{
      color: var(--muted);
    }}

    .link-panel a {{
      display: inline-block;
      word-break: break-word;
    }}

    .empty-state {{
      list-style: none;
      margin-left: -18px;
      color: var(--muted);
    }}

    .footer {{
      margin-top: 20px;
      padding: 14px 0 0;
      color: var(--muted);
      font-size: 0.9rem;
      border-top: 1px solid var(--line);
    }}

    @media (max-width: 1080px) {{
      .masthead,
      .layout {{
        grid-template-columns: 1fr;
      }}

      .sidebar {{
        position: static;
      }}
    }}

    @media (max-width: 720px) {{
      .page {{
        width: min(var(--wrap), calc(100% - 20px));
        padding-top: 14px;
      }}

      .headline,
      .summary-band,
      .report,
      .panel {{
        padding: 20px;
      }}

      h1 {{
        font-size: 2rem;
      }}

      .meta-list {{
        grid-template-columns: 1fr;
      }}

      .report h2 {{
        font-size: 1.28rem;
      }}
    }}

    @media print {{
      body {{
        background: #ffffff;
      }}

      .page {{
        width: 100%;
        padding: 0;
      }}

      .headline,
      .summary-band,
      .report,
      .panel {{
        box-shadow: none;
      }}

      .layout {{
        grid-template-columns: 1fr;
      }}

      .sidebar {{
        position: static;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <header class="masthead">
      <section class="headline">
        <p class="eyebrow">데일리 리뷰 시그널 브리프</p>
        <h1>{html.escape(context.title)}</h1>
        <p class="deck">시장 관점의 리뷰 노트, 신호 클러스터링, 그리고 워크스페이스 증거 링크를 빠르게 읽고 후속 리서치로 연결할 수 있도록 정리한 웹 리포트입니다.</p>
        <ul class="meta-list">
          <li>
            <strong>생성 시각</strong>
            <span>{html.escape(context.generated_at)}</span>
          </li>
          <li>
            <strong>섹션 수</strong>
            <span>{context.section_count}</span>
          </li>
          <li>
            <strong>원본 마크다운</strong>
            <span><a href="{html.escape(source_href, quote=True)}">{html.escape(context.source_path.name)}</a></span>
          </li>
        </ul>
      </section>
      {summary_html}
    </header>

    <main class="layout">
      <article class="report">
        {context.body_html}
        <div class="footer">
          원본 파일 최종 수정 시각: {html.escape(context.source_modified_at)}
        </div>
      </article>

      <aside class="sidebar">
        {toc_panel}
        <section class="panel link-panel" aria-labelledby="links-heading">
          <h2 id="links-heading">연결된 근거</h2>
          <ul>
            {link_items}
          </ul>
        </section>
      </aside>
    </main>
  </div>
</body>
</html>
"""


def render_final_review_template(context: RenderContext) -> str:
    labels = final_review_labels(context.language)
    summary_html = ""
    if context.summary_points:
        items = "\n".join(
            f"<li>{html.escape(point)}</li>" for point in context.summary_points[:5]
        )
        summary_html = f"""
        <section class="hero-signals" aria-labelledby="signals-heading">
          <h2 id="signals-heading">{html.escape(labels["signals"])}</h2>
          <ul>
            {items}
          </ul>
        </section>
        """

    toc_panel = ""
    if context.toc_html.strip():
        toc_panel = f"""
        <section class="side-section toc-panel" aria-labelledby="toc-heading">
          <h2 id="toc-heading">{html.escape(labels["toc"])}</h2>
          {context.toc_html}
        </section>
        """

    link_items = render_link_items(context.links, context.language)
    source_href = source_link_href(context.source_path, context.output_path)
    document_metadata = render_document_metadata(context)
    language_switch = render_language_switch(context)
    dek_html = ""
    if context.subtitle:
        dek_html = f'<p class="dek">{html.escape(context.subtitle)}</p>'

    return f"""<!DOCTYPE html>
<html lang="{html.escape(context.language, quote=True)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(context.title)}</title>
{document_metadata}
  <link rel="icon" href="data:,">
  <meta name="color-scheme" content="light">
  <script>
    window.MathJax = {{
      tex: {{
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
      }},
      options: {{
        skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'],
        ignoreHtmlClass: 'tex2jax_ignore'
      }}
    }};
  </script>
  <script defer
    src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js"
    integrity="sha384-AHAnt9ZhGeHIrydA1Kp1L7FN+2UosbF7RQg6C+9Is/a7kDpQ1684C2iH2VWil6r4"
    crossorigin="anonymous"></script>
  <style>
    :root {{
      --paper: #fbfaf7;
      --paper-soft: #f2f0ea;
      --ink: #17211d;
      --muted: #5f6b65;
      --line: #d8d5cb;
      --teal: #0f766e;
      --blue: #25456f;
      --amber: #a35a16;
      --rose: #8b3a3a;
      --green-soft: #e9f3ef;
      --blue-soft: #e9eef5;
      --amber-soft: #f6eee2;
      --rose-soft: #f5eaea;
      --wrap: 1180px;
      --article: 780px;
      --radius: 8px;
    }}

    * {{
      box-sizing: border-box;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background: var(--paper);
      font-family: "Segoe UI", "Noto Sans KR", Arial, sans-serif;
      text-rendering: optimizeLegibility;
    }}

    a {{
      color: var(--teal);
      text-decoration-thickness: 1px;
      text-underline-offset: 3px;
    }}

    .topline {{
      border-bottom: 1px solid var(--line);
      background: #ffffff;
    }}

    .topline-inner,
    .hero-inner,
    .content-grid {{
      width: min(var(--wrap), calc(100% - 40px));
      margin: 0 auto;
    }}

    .topline-inner {{
      display: flex;
      justify-content: space-between;
      gap: 20px;
      padding: 14px 0;
      color: var(--muted);
      font-size: 0.92rem;
    }}

    .topline a {{
      color: var(--blue);
      font-weight: 650;
      text-decoration: none;
    }}

    .topline-actions,
    .language-switch {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
    }}

    .language-switch {{
      padding-right: 10px;
      border-right: 1px solid var(--line);
      white-space: nowrap;
    }}

    .language-switch span[aria-current="page"] {{
      color: var(--ink);
      font-weight: 760;
    }}

    .hero {{
      border-bottom: 1px solid var(--line);
      background:
        linear-gradient(90deg, rgba(15, 118, 110, 0.10), transparent 46%),
        linear-gradient(180deg, #ffffff 0%, var(--paper) 100%);
    }}

    .hero-inner {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 360px;
      gap: 40px;
      align-items: end;
      padding: 46px 0 34px;
    }}

    .eyebrow {{
      margin: 0 0 18px;
      color: var(--teal);
      font-weight: 760;
      letter-spacing: 0;
      text-transform: uppercase;
      font-size: 0.82rem;
    }}

    h1 {{
      margin: 0;
      max-width: 900px;
      color: var(--ink);
      font-size: clamp(2.2rem, 5vw, 4.2rem);
      line-height: 1.02;
      letter-spacing: 0;
      font-weight: 820;
      word-break: keep-all;
      overflow-wrap: normal;
    }}

    .dek {{
      margin: 22px 0 0;
      max-width: 760px;
      color: var(--muted);
      font-size: 1.08rem;
      line-height: 1.75;
      word-break: keep-all;
    }}

    .hero-signals {{
      padding: 18px 20px;
      border-top: 4px solid var(--teal);
      background: rgba(255, 255, 255, 0.82);
    }}

    .hero-signals h2,
    .side-section h2 {{
      margin: 0 0 12px;
      color: var(--blue);
      font-size: 0.88rem;
      line-height: 1.3;
      letter-spacing: 0;
      text-transform: uppercase;
    }}

    .hero-signals ul,
    .side-section ul {{
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 9px;
      color: var(--muted);
      line-height: 1.62;
    }}

    .content-grid {{
      display: grid;
      grid-template-columns: minmax(0, var(--article)) minmax(260px, 310px);
      gap: 52px;
      align-items: start;
      padding: 38px 0 56px;
    }}

    .final-article {{
      min-width: 0;
      overflow-wrap: break-word;
    }}

    .final-article > :first-child {{
      margin-top: 0;
    }}

    .final-article h2 {{
      margin: 46px 0 16px;
      padding-top: 22px;
      border-top: 1px solid var(--line);
      color: var(--ink);
      font-size: 1.72rem;
      line-height: 1.25;
      letter-spacing: 0;
      word-break: keep-all;
    }}

    .final-article h3 {{
      margin: 30px 0 12px;
      color: var(--blue);
      font-size: 1.18rem;
      line-height: 1.35;
      letter-spacing: 0;
    }}

    .final-article p,
    .final-article li {{
      color: var(--ink);
      font-size: 1.02rem;
      line-height: 1.86;
    }}

    .final-article p {{
      margin: 0 0 18px;
    }}

    .final-article ul,
    .final-article ol {{
      margin: 0 0 22px;
      padding-left: 24px;
    }}

    .final-article li + li {{
      margin-top: 8px;
    }}

    .final-article blockquote {{
      margin: 28px 0;
      padding: 4px 0 4px 22px;
      border-left: 4px solid var(--amber);
      color: var(--ink);
      font-size: 1.12rem;
    }}

    .final-article blockquote p {{
      color: var(--ink);
      font-size: 1.12rem;
      line-height: 1.75;
    }}

    .final-article code {{
      padding: 2px 6px;
      border-radius: 6px;
      background: #ebe7de;
      font-family: "Cascadia Code", Consolas, monospace;
      font-size: 0.92em;
    }}

    .final-article pre {{
      margin: 22px 0;
      padding: 18px;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #f0ede6;
    }}

    .final-article pre code {{
      padding: 0;
      background: transparent;
    }}

    .final-article mjx-container[display="true"] {{
      max-width: 100%;
      overflow-x: auto;
      overflow-y: hidden;
      padding-bottom: 4px;
      -webkit-overflow-scrolling: touch;
    }}

    .math-display {{
      margin: 18px 0 20px;
      padding: 18px 22px;
      overflow-x: auto;
      border: 1px solid #d2cdc1;
      border-radius: 10px;
      background: #fbfaf6;
      color: #101a24;
      font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif;
      font-size: clamp(1.08rem, 2vw, 1.34rem);
      line-height: 1.7;
      text-align: center;
      font-variant-numeric: lining-nums;
      -webkit-overflow-scrolling: touch;
    }}

    .math-display .math-row {{
      min-width: max-content;
      white-space: nowrap;
    }}

    .math-display .math-row + .math-row {{
      margin-top: 2px;
    }}

    .math-display .math-indent {{
      padding-left: 2.4em;
    }}

    .math-display var {{
      font-family: inherit;
      font-style: italic;
    }}

    .math-display .roman {{
      font-style: normal;
    }}

    .math-display sub,
    .math-display sup {{
      font-size: 0.68em;
      line-height: 0;
    }}

    .math-display .sum {{
      display: inline-block;
      margin: 0 0.08em;
      font-size: 1.28em;
      line-height: 0.8;
      vertical-align: -0.06em;
    }}

    .math-display .frac {{
      display: inline-grid;
      grid-template-rows: auto auto;
      margin: 0 0.14em;
      vertical-align: -0.46em;
      text-align: center;
      line-height: 1.08;
    }}

    .math-display .frac > span:first-child {{
      padding: 0 0.22em 0.06em;
      border-bottom: 1px solid currentColor;
    }}

    .math-display .frac > span:last-child {{
      padding: 0.06em 0.22em 0;
    }}

    .math-display .condition {{
      margin-left: 1.2em;
      color: #5e5a52;
      font-size: 0.88em;
      font-style: normal;
    }}

    .math-inline {{
      white-space: nowrap;
      font-family: "Cambria Math", "STIX Two Math", "Times New Roman", serif;
      font-size: 1.02em;
    }}

    .reader-layers {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin: 24px 0 30px;
    }}

    .reader-layer {{
      padding: 16px 17px;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #ffffff;
    }}

    .reader-layer strong {{
      display: block;
      margin-bottom: 7px;
      color: var(--blue);
      font-size: 0.88rem;
    }}

    .reader-layer span {{
      display: block;
      color: var(--muted);
      font-size: 0.94rem;
      line-height: 1.62;
    }}

    details.deep-dive {{
      margin: 24px 0;
      min-width: 0;
      max-width: 100%;
      overflow: hidden;
      border: 1px solid var(--line);
      border-radius: 10px;
      background: #ffffff;
    }}

    details.deep-dive > summary {{
      padding: 15px 18px;
      cursor: pointer;
      color: var(--blue);
      font-weight: 760;
      line-height: 1.5;
    }}

    details.deep-dive[open] > summary {{
      border-bottom: 1px solid var(--line);
      background: var(--blue-soft);
    }}

    details.deep-dive > :not(summary) {{
      margin-left: 18px;
      margin-right: 18px;
    }}

    details.deep-dive > :last-child {{
      margin-bottom: 18px;
    }}

    details.deep-dive > table {{
      display: block;
      width: auto;
      max-width: calc(100% - 36px);
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }}

    .final-article img,
    .final-article svg,
    .final-article video,
    .final-article canvas,
    .final-article iframe {{
      display: block;
      max-width: 100%;
      height: auto;
    }}

    .article-hero-figure {{
      margin: 0 0 34px;
    }}

    .article-hero-figure img {{
      width: 100%;
      border: 1px solid var(--line);
      background: #ffffff;
    }}

    .diagram-mobile {{
      display: none !important;
    }}

    .article-hero-figure figcaption {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.55;
      word-break: keep-all;
    }}

    .final-article p:has(> img) {{
      margin: 30px 0;
    }}

    .final-article table {{
      display: block;
      width: 100%;
      margin: 24px 0;
      overflow-x: auto;
      border-collapse: collapse;
      font-size: 0.96rem;
    }}

    .final-article th,
    .final-article td {{
      min-width: 140px;
      padding: 12px 14px;
      border: 1px solid var(--line);
      vertical-align: top;
      text-align: left;
      line-height: 1.58;
    }}

    .final-article th {{
      background: var(--paper-soft);
      color: var(--blue);
      font-weight: 760;
    }}

    .final-article .footnote-ref {{
      font-size: 0.78em;
      line-height: 0;
    }}

    .final-article .footnote,
    .final-article .footnotes {{
      margin: 44px 0 28px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
    }}

    .final-article .footnote::before,
    .final-article .footnotes::before {{
      content: "{labels["glossary"]}";
      display: block;
      margin-bottom: 12px;
      color: var(--blue);
      font-size: 0.88rem;
      font-weight: 760;
      letter-spacing: 0;
      text-transform: uppercase;
    }}

    .final-article .footnote ol,
    .final-article .footnotes ol {{
      margin-bottom: 0;
      padding-left: 22px;
    }}

    .final-article .footnote li,
    .final-article .footnote p,
    .final-article .footnotes li,
    .final-article .footnotes p {{
      color: var(--muted);
      font-size: 0.94rem;
      line-height: 1.72;
    }}

    .callout {{
      margin: 26px 0;
      padding: 18px 20px;
      border-left: 4px solid var(--teal);
      background: var(--green-soft);
    }}

    .callout-label {{
      margin: 0 0 8px !important;
      color: var(--teal) !important;
      font-size: 0.84rem !important;
      font-weight: 780;
      line-height: 1.3 !important;
      text-transform: uppercase;
    }}

    .callout-think,
    .callout-thinking {{
      border-left-color: var(--amber);
      background: var(--amber-soft);
    }}

    .callout-think .callout-label,
    .callout-thinking .callout-label {{
      color: var(--amber) !important;
    }}

    .callout-evidence {{
      border-left-color: var(--blue);
      background: var(--blue-soft);
    }}

    .callout-evidence .callout-label {{
      color: var(--blue) !important;
    }}

    .callout-operator {{
      border-left-color: var(--rose);
      background: var(--rose-soft);
    }}

    .callout-operator .callout-label {{
      color: var(--rose) !important;
    }}

    .figure-panel,
    .data-panel {{
      margin: 30px 0;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #ffffff;
      overflow-x: auto;
    }}

    .figure-panel figcaption,
    .data-panel figcaption {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.55;
    }}

    @media (max-width: 760px) {{
      .reader-layers {{
        grid-template-columns: 1fr;
      }}

      .math-display {{
        padding: 15px 16px;
        font-size: 1rem;
        line-height: 1.65;
        text-align: left;
      }}

      .math-display .math-indent {{
        padding-left: 1.1em;
      }}

      .diagram-desktop {{
        display: none !important;
      }}

      .diagram-mobile {{
        display: block !important;
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
      }}

      .figure-panel img[src$=".svg"],
      .data-panel img[src$=".svg"] {{
        width: 680px;
        max-width: none;
      }}

      .figure-panel.figure-panel-fit img[src$=".svg"] {{
        width: 100%;
        max-width: 100%;
      }}
    }}

    .story-flow {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin: 20px 0;
    }}

    .story-flow > * {{
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--paper-soft);
      color: var(--ink);
      line-height: 1.5;
    }}

    .sidebar {{
      position: sticky;
      top: 24px;
      display: grid;
      gap: 22px;
      min-width: 0;
    }}

    .side-section {{
      padding: 0 0 22px;
      border-bottom: 1px solid var(--line);
    }}

    .toc-panel a,
    .link-panel a {{
      color: var(--muted);
      text-decoration: none;
      word-break: break-word;
    }}

    .toc-panel a:hover,
    .link-panel a:hover {{
      color: var(--teal);
      text-decoration: underline;
    }}

    .footer {{
      margin-top: 42px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.6;
    }}

    @media (max-width: 1120px) {{
      .hero-inner,
      .content-grid {{
        grid-template-columns: 1fr;
      }}

      .sidebar {{
        position: static;
      }}
    }}

    @media (max-width: 680px) {{
      .topline-inner,
      .hero-inner,
      .content-grid {{
        width: min(var(--wrap), calc(100% - 24px));
      }}

      .topline-inner {{
        display: grid;
      }}

      .hero-inner {{
        padding: 34px 0 28px;
      }}

      .final-article h2 {{
        font-size: 1.42rem;
      }}
    }}

    @media print {{
      body {{
        background: #ffffff;
      }}

      .hero {{
        background: #ffffff;
      }}

      .content-grid {{
        grid-template-columns: 1fr;
      }}

      .sidebar {{
        position: static;
      }}
    }}
  </style>
</head>
<body>
  <div class="topline">
    <div class="topline-inner">
      <span>{html.escape(context.issue_label)}</span>
      <div class="topline-actions">
        <a class="hub-link" href="https://infant83.github.io/AI_Tech_Review/">{("리뷰 허브" if context.language == "ko" else "Review hub")}</a>
        {language_switch}
        <a href="{html.escape(source_href, quote=True)}">{html.escape(context.source_path.name)}</a>
      </div>
    </div>
  </div>

  <header class="hero">
    <div class="hero-inner">
      <section>
        <p class="eyebrow">AI Tech Review Letters</p>
        <h1>{html.escape(context.title)}</h1>
        {dek_html}
      </section>
      {summary_html}
    </div>
  </header>

  <main class="content-grid">
    <article class="final-article">
      {context.body_html}
      <div class="footer">
        {html.escape(labels["generated"])}: {html.escape(context.generated_at)}<br>
        {html.escape(labels["source_modified"])}: {html.escape(context.source_modified_at)}
      </div>
    </article>

    <aside class="sidebar">
      {toc_panel}
      <section class="side-section link-panel" aria-labelledby="links-heading">
        <h2 id="links-heading">{html.escape(labels["links"])}</h2>
        <ul>
          {link_items}
        </ul>
      </section>
    </aside>
  </main>
</body>
</html>
"""


def resolve_mode(source_path: Path, requested_mode: str) -> str:
    if requested_mode != "auto":
        return requested_mode
    if re.search(r"_final_review(?:_(?:ko|en))?$", source_path.stem, re.IGNORECASE):
        return "final-review"
    return "default"


def build_context(source_path: Path, mode: str = "auto") -> RenderContext:
    raw_text = source_path.read_text(encoding="utf-8")
    metadata, markdown_text = strip_frontmatter(raw_text)
    metadata_title = metadata_value(metadata, "title") or source_path.stem
    title, body_markdown = split_title(markdown_text, metadata_title)
    subtitle = metadata_value(metadata, "description", "subtitle")
    language = normalize_language(metadata_value(metadata, "language", "lang"))
    canonical_url = metadata_value(metadata, "canonical url", "canonical_url", "canonical")
    alternate_ko_url = metadata_value(
        metadata, "alternate ko url", "alternate_ko_url", "hreflang ko", "hreflang_ko"
    )
    alternate_en_url = metadata_value(
        metadata, "alternate en url", "alternate_en_url", "hreflang en", "hreflang_en"
    )
    alternate_default_url = metadata_value(
        metadata,
        "alternate x-default url",
        "alternate_x_default_url",
        "hreflang x-default",
        "hreflang_x_default",
    ) or alternate_ko_url
    social_image_url = metadata_value(
        metadata, "social image url", "social_image_url", "og image", "og_image"
    )
    author = metadata_value(metadata, "author")
    published_date = metadata_value(metadata, "date created", "published date", "date")
    modified_date = metadata_value(metadata, "date modified", "modified date") or published_date
    body_html, toc_html = build_markdown_html(body_markdown)
    source_stat = source_path.stat()
    generated_at = format_timestamp(datetime.now().astimezone())
    source_modified_at = format_timestamp(datetime.fromtimestamp(source_stat.st_mtime).astimezone())
    section_count = len(SECTION_RE.findall(body_markdown))
    resolved_mode = resolve_mode(source_path, mode)
    return RenderContext(
        title=title,
        subtitle=subtitle,
        language=language,
        canonical_url=canonical_url,
        alternate_ko_url=alternate_ko_url,
        alternate_en_url=alternate_en_url,
        alternate_default_url=alternate_default_url,
        social_image_url=social_image_url,
        author=author,
        published_date=published_date,
        modified_date=modified_date,
        issue_label=build_issue_label(metadata),
        source_path=source_path,
        output_path=source_path.with_suffix(".html"),
        mode=resolved_mode,
        body_html=body_html,
        toc_html=toc_html,
        summary_points=extract_summary_points(markdown_text),
        links=extract_links(markdown_text),
        section_count=section_count,
        generated_at=generated_at,
        source_modified_at=source_modified_at,
    )


def render_file(source_path: Path, mode: str = "auto") -> Path:
    context = build_context(source_path, mode)
    html_text = "\n".join(
        line.rstrip() for line in render_template(context).splitlines()
    ) + "\n"
    context.output_path.write_text(html_text, encoding="utf-8")
    return context.output_path


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render one or more markdown reports into polished standalone HTML pages."
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "default", "final-review"],
        default="auto",
        help="Rendering mode. Auto uses final-review mode for *_final_review.md and *_final_review_en.md.",
    )
    parser.add_argument("paths", nargs="+", help="Markdown files to render.")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    exit_code = 0
    for raw_path in args.paths:
        path = Path(raw_path).resolve()
        if not path.exists():
            print(f"[missing] {path}")
            exit_code = 1
            continue
        if path.suffix.lower() != ".md":
            print(f"[skip] {path} is not a markdown file")
            exit_code = 1
            continue
        output_path = render_file(path, args.mode)
        print(f"[rendered:{resolve_mode(path, args.mode)}] {path} -> {output_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
