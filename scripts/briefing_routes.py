"""Shared identities and stable routes for publicly registered briefings."""
from __future__ import annotations

from datetime import date
import re

BRIEFING_SERIES = frozenset({"daily-quantum", "daily-research", "daily-quantum-exercise", "weekly-review"})


def editorial_paths(published: str, series: str, identifier: str | None = None) -> tuple[str, str]:
    """Keep dated issue URLs, with explicit DQE supplements below their date."""
    if series not in BRIEFING_SERIES:
        raise ValueError("Unknown briefing series")
    if not isinstance(published, str) or date.fromisoformat(published).isoformat() != published:
        raise ValueError("Invalid briefing issue date")
    namespace = {"daily-research": "briefings/research",
                 "daily-quantum-exercise": "briefings/exercises"}.get(series, "briefings")
    stem = f"{namespace}/{published}"
    if series == "daily-quantum-exercise" and identifier is not None:
        if not isinstance(identifier, str):
            raise ValueError("Invalid exercise identifier")
        supplement_prefix = f"{published}-daily-quantum-exercise-"
        if identifier.startswith(supplement_prefix):
            slug = identifier[len(supplement_prefix):]
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug == "en":
                raise ValueError("Invalid exercise supplement slug")
            stem += "/" + slug
    return f"{stem}/index.html", f"{stem}/en/index.html"
