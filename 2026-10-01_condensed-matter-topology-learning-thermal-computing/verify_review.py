"""Non-network checks for the bilingual review's publication boundary."""
from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, unquote
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SITE = ROOT.parent / "site"


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[str] = []
        self.images: list[dict[str, str]] = []
        self.lang = ""
        self.h1_count = 0
        self.canonicals: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {k: v or "" for k, v in attrs}
        if "id" in data:
            self.ids.append(data["id"])
        if tag == "html":
            self.lang = data.get("lang", "")
        if tag == "a":
            self.links.append(data.get("href", ""))
        if tag == "img":
            self.images.append(data)
        if tag == "h1":
            self.h1_count += 1
        if tag == "link" and data.get("rel") == "canonical":
            self.canonicals.append(data["href"])


def verify(lang: str) -> dict[str, object]:
    path = SITE / "reviews" / ROOT.name / ("" if lang == "ko" else "en") / "index.html"
    content = path.read_text(encoding="utf-8")
    page = Page()
    page.feed(content)
    assert page.lang == lang and page.h1_count == 1
    assert len(page.canonicals) == 1
    assert page.canonicals[0].endswith("/" if lang == "ko" else "/en/")
    assert len(page.ids) == len(set(page.ids)), "Duplicate IDs"
    assert len(page.images) == 4, "One cover plus three mechanism figures"
    for href in page.links:
        link = urlsplit(href)
        if link.fragment and not link.path and not link.scheme:
            assert unquote(link.fragment) in page.ids, href
        if link.path and not link.scheme:
            resolved = (path.parent / unquote(link.path)).resolve()
            if resolved.is_dir():
                resolved /= "index.html"
            assert resolved.exists(), href
    for image in page.images:
        assert image.get("alt"), "Missing accessible description"
        asset = path.parent / image["src"]
        assert asset.exists()
        if asset.suffix == ".svg":
            tree = ET.parse(asset)
            assert tree.getroot().attrib.get("viewBox")
            assert tree.find("{http://www.w3.org/2000/svg}title") is not None
    for value in ("97.3%", "91.7%", "92.0%", "2606.19426", "2607.13127", "2307.02129v5", "2406.00048v3", "2506.15121v3", "2509.15324v1", "2026-10-01", "OpenAI Codex Work Mode", "2026.08"):
        assert value in content, f"Protected value absent: {value}"
    assert not re.search(r"(?:/workspace/|/root/|mail\.google\.com|gmail\.com|Fwd:|messageId|[\w.+-]+@[\w.-]+\.[a-z]{2,})", content, re.I)
    assert "authoring-disclosure" in content and "byline-disclosure" in content
    assert "commentary PDFs" in content if lang == "en" else "해설 PDF" in content
    return {"language": lang, "images": len(page.images), "unique_ids": len(page.ids), "links": len(page.links), "status": "pass"}


if __name__ == "__main__":
    manifest = json.loads((SITE / "manifest.json").read_text(encoding="utf-8"))
    matching = [entry for entry in manifest if entry["folder"] == ROOT.name]
    assert len(matching) == 1
    assert matching[0]["date"] == "2026-10-01"
    assert matching[0]["thumbnail"].endswith("condmat_hero.webp")
    assert len(matching[0]["translations"]) == 1
    for language in ("ko", "en"):
        print(json.dumps(verify(language), ensure_ascii=False))
    print("Protected values, privacy boundary, references, language variants and image assets: PASS")
