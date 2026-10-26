"""Localize hub entries from already-published article text.

This module returns plain text, never HTML. Renderers must HTML-escape the
returned fields once. A translation is used only when its public file contains
both a title and a summary; an incomplete translation keeps the Korean entry
together rather than mixing languages or inventing scientific copy.

When a published English intro merely repeats its summary, an approved hub
subtitle may translate the existing Korean subtitle. That fallback applies
only while its recorded Korean source matches the current entry exactly.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote, urlsplit


_VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})
_IGNORED_TAGS = frozenset({"script", "style", "template"})
_INTRO_CLASSES = ("dek", "subtitle", "standfirst")
HUB_SUBTITLES_EN = json.loads(Path(__file__).with_name("hub_subtitles_en.json").read_text(encoding="utf-8"))


def _plain_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _comparison_key(value: str) -> str:
    value = unicodedata.normalize("NFKC", _plain_text(value)).casefold()
    return value.translate(str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})).rstrip(" .:;!?")


class _ArticleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.intros: list[tuple[int, str]] = []
        self._stack: list[str] = []
        self._captures: list[dict] = []
        self._title_started = False
        self._body_started = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        values = {key.lower(): value or "" for key, value in attrs}
        ignored = any(part in _IGNORED_TAGS for part in self._stack)
        if tag == "meta" and not ignored and values.get("name", "").lower() == "description":
            if not self.description:
                self.description = _plain_text(values.get("content", ""))
        if tag in {"br", "img"} and not ignored:
            text = " " if tag == "br" else " " + values.get("alt", "") + " "
            for capture in self._captures:
                capture["chunks"].append(text)
        if tag in _VOID_TAGS:
            return
        self._stack.append(tag)
        if ignored or tag in _IGNORED_TAGS:
            return
        if tag == "h1" and not self._title_started:
            self._title_started = True
            self._captures.append({"kind": "title", "depth": len(self._stack), "chunks": []})
        elif tag == "h2" and self._title_started:
            self._body_started = True
        elif tag == "p" and not self._body_started:
            classes = set(values.get("class", "").split())
            ranks = [rank for rank, name in enumerate(_INTRO_CLASSES) if name in classes]
            if ranks:
                self._captures.append({"kind": "intro", "rank": min(ranks), "depth": len(self._stack), "chunks": []})

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag not in self._stack:
            return
        closing_depth = len(self._stack) - self._stack[::-1].index(tag)
        remaining = []
        for capture in self._captures:
            if capture["depth"] >= closing_depth:
                text = _plain_text("".join(capture["chunks"]))
                if capture["kind"] == "title":
                    self.title = text
                elif text:
                    self.intros.append((capture["rank"], text))
            else:
                remaining.append(capture)
        self._captures = remaining
        del self._stack[closing_depth - 1:]

    def handle_data(self, data: str) -> None:
        if any(part in _IGNORED_TAGS for part in self._stack):
            return
        for capture in self._captures:
            capture["chunks"].append(data)


def extract_english_text(document: str) -> dict[str, str]:
    """Extract the first h1, a distinct published intro, and meta description.

    Only the known introductory paragraph classes before the first body h2 are
    candidates. An intro may supply the summary when metadata is absent. Equal
    intro/description text is emitted once as the summary, not in both slots.
    """
    parser = _ArticleTextParser()
    parser.feed(document)
    parser.close()
    candidates = [text for _rank, text in sorted(parser.intros, key=lambda item: item[0])]
    summary = parser.description or (candidates[0] if candidates else "")
    subtitle = next((text for text in candidates if _comparison_key(text) != _comparison_key(summary)), "")
    return {"title": parser.title, "subtitle": subtitle, "summary": summary}


def _translation_file(site_root: Path, folder: str, href: object) -> tuple[Path, str] | None:
    """Accept only an existing HTML file inside this review's public folder."""
    if not isinstance(href, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", folder):
        return None
    try:
        parts = urlsplit(href)
    except ValueError:
        return None
    decoded = unquote(parts.path)
    if parts.scheme or parts.netloc or parts.query or parts.fragment or decoded.startswith(("/", "\\")) or "\\" in decoded:
        return None
    if any(piece in {"..", "."} for piece in decoded.split("/")):
        return None
    try:
        root = site_root.resolve()
        review_root = (root / "reviews" / folder).resolve()
        path = (root / decoded).resolve()
        if path.is_dir():
            path = (path / "index.html").resolve()
        review_root.relative_to(root)
        path.relative_to(review_root)
        if path.suffix.lower() != ".html" or not path.is_file():
            return None
    except (ValueError, OSError, RuntimeError):
        return None
    return path, href


def _published_english(item: Mapping, site_root: Path) -> tuple[dict[str, str], str] | None:
    translations = item.get("translations") or []
    if not isinstance(translations, list):
        return None
    for translation in translations:
        if not isinstance(translation, Mapping) or str(translation.get("language", "")).lower() != "en":
            continue
        located = _translation_file(site_root, str(item.get("folder", "")), translation.get("href"))
        if located is None:
            continue
        path, href = located
        try:
            text = extract_english_text(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            continue
        if text["title"] and text["summary"]:
            if not text["subtitle"]:
                translated = HUB_SUBTITLES_EN.get(str(item.get("folder", "")), {})
                if (
                    translated.get("source") == item.get("subtitle")
                    and isinstance(translated.get("text"), str)
                    and translated["text"].strip()
                    and _comparison_key(translated["text"]) != _comparison_key(text["summary"])
                ):
                    text["subtitle"] = translated["text"]
            return text, href
    return None


def localize_manifest(
    manifest: Sequence[Mapping], site_root: Path, language: str = "ko",
) -> list[dict]:
    """Copy entries for a ko/en hub while retaining identity and metric aliases.

    ``search_text`` contains both languages so switching the page language can
    keep the current query. ``content_language`` and ``english_available`` let
    the English renderer clearly mark Korean-only articles. The returned href
    remains relative to the public site root; the renderer applies its own
    page-relative prefix. Other original fields, including ``metric_path``,
    dates, thumbnail and translations, are deep-copied without modification.
    """
    if language not in {"ko", "en"}:
        raise ValueError("Hub language must be 'ko' or 'en'")
    root = Path(site_root)
    result = []
    for original in manifest:
        item = deepcopy(dict(original))
        english = _published_english(original, root)
        item["content_language"] = "ko"
        item["english_available"] = english is not None
        item["english_href"] = english[1] if english else ""
        search_fields = [str(original.get(key) or "") for key in ("title", "subtitle", "summary", "category")]
        tags = original.get("tags") or []
        if isinstance(tags, (list, tuple)):
            search_fields.extend(tag for tag in tags if isinstance(tag, str))
        if english:
            text, href = english
            search_fields.extend(text.values())
            if language == "en":
                item.update(text)
                item["href"] = href
                item["content_language"] = "en"
        item["search_text"] = _plain_text(" ".join(search_fields))
        result.append(item)
    return result
