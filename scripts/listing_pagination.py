"""Stable static list pages, with optional on-demand enhancement."""
from __future__ import annotations

import hashlib
import html
import json
from math import ceil
from pathlib import Path

try:
    from .briefing_routes import BRIEFING_SERIES
except ImportError:
    from briefing_routes import BRIEFING_SERIES

SIZES = {"reviews": 6, "archive": 12, "briefings": 12}


def generated_paths(site: Path) -> set[str]:
    """Exact possible list HTML paths derived from the public registrations."""
    reviews = json.loads((site / "manifest.json").read_text()) if (site / "manifest.json").exists() else []
    archive = json.loads((site / "archive-manifest.json").read_text()) if (site / "archive-manifest.json").exists() else {}
    docs = archive.get("documents", [])
    totals = {"reviews": len(reviews), "archive": len(docs) + len(archive.get("external_resources", [])),
              "briefings": sum(row.get("series") in BRIEFING_SERIES for row in docs)}
    return {page_path(area, language, number) for area, total in totals.items()
            for language in ("ko", "en") for number in range(1, page_count(total, area) + 1)}


def is_page_path(name: str) -> bool:
    import re
    match = re.fullmatch(r"(?:(?:archive|briefings)/)?(?:en/)?page/([1-9][0-9]*)/index\.html", name)
    return bool(match and int(match[1]) >= 2)


def page_count(total: int, area: str) -> int:
    return max(1, ceil(total / SIZES[area]))


def page_path(area: str, language: str, number: int = 1) -> str:
    if area not in SIZES or language not in {"ko", "en"} or type(number) is not int or number < 1:
        raise ValueError("Invalid list page")
    start = ("" if area == "reviews" else area + "/") + ("en/" if language == "en" else "")
    return start + (f"page/{number}/" if number > 1 else "") + "index.html"


def page_prefix(area: str, language: str, number: int = 1) -> str:
    return "../" * (len(Path(page_path(area, language, number)).parts) - 1)


def page_directory(area: str, language: str, number: int = 1) -> str:
    return page_path(area, language, number).removesuffix("index.html")


def page_slice(items: list, area: str, number: int = 1) -> list:
    if number > page_count(len(items), area):
        raise ValueError("List page is outside the generated range")
    return items[(number - 1) * SIZES[area]:number * SIZES[area]]


def pagination(area: str, language: str, number: int, total: int) -> str:
    pages = page_count(total, area)
    prefix, en = page_prefix(area, language, number), language == "en"
    numbers = sorted({1, pages, *range(max(1, number - 2), min(pages, number + 2) + 1)})
    parts = []
    def link(target, label, rel=""):
        href = prefix + page_path(area, language, target)
        return f'<a href="{href}"{f" rel={chr(34)}{rel}{chr(34)}" if rel else ""}>{label}</a>'
    if number > 1:
        parts.append(link(number - 1, "Previous" if en else "이전", "prev"))
    previous = 0
    for target in numbers:
        if previous and target - previous > 1:
            parts.append('<span aria-hidden="true">…</span>')
        parts.append(f'<span aria-current="page">{target}</span>' if target == number else link(target, str(target)))
        previous = target
    if number < pages:
        parts.append(link(number + 1, "Next" if en else "다음", "next"))
    label = "List pages" if en else "목록 페이지"
    return (f'<nav class="listing-pagination" data-list-pagination data-area="{area}" data-page="{number}" '
            f'data-pages="{pages}" data-total="{total}" data-size="{SIZES[area]}" data-language="{language}" '
            f'data-root="{prefix}" aria-label="{label}">' + "".join(parts) + '</nav><p class="listing-load-status" data-list-load-status role="status" aria-live="polite"></p>')


def pagination_script(prefix: str) -> str:
    source = Path(__file__).parent / "public_assets/listing-pages.js"
    version = hashlib.sha256(source.read_bytes()).hexdigest()[:12]
    return f'<script src="{html.escape(prefix, quote=True)}assets/listing-pages.js?v={version}" defer></script>'
