"""Shared identities and stable routes for publicly registered briefings."""
from __future__ import annotations

from datetime import date

BRIEFING_SERIES = frozenset({"daily-quantum", "daily-research", "weekly-review"})


def editorial_paths(published: str, series: str) -> tuple[str, str]:
    """Keep existing issue URLs and give research briefs their own date space."""
    if series not in BRIEFING_SERIES:
        raise ValueError("Unknown briefing series")
    if not isinstance(published, str) or date.fromisoformat(published).isoformat() != published:
        raise ValueError("Invalid briefing issue date")
    namespace = "briefings/research" if series == "daily-research" else "briefings"
    stem = f"{namespace}/{published}"
    return f"{stem}/index.html", f"{stem}/en/index.html"
