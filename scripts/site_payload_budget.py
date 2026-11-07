"""Portable static payload budgets; network/mobile timings are tested separately."""
from __future__ import annotations

import argparse
import gzip
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

PAGES = ("index.html", "en/index.html", "archive/index.html", "archive/en/index.html",
         "lectures/index.html", "lectures/en/index.html", "briefings/index.html", "briefings/en/index.html")
LAZY_SEARCH = {"minisearch.js", "site-search-core.js", "search-records.json"}


def compressed(path: Path) -> int:
    return len(gzip.compress(path.read_bytes(), mtime=0))


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.has_search = False
        self.images = []
        self.stack = []
        self.card_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "data-site-search" in attrs:
            self.has_search = True
        if tag == "script" and attrs.get("src"):
            self.urls.append(attrs["src"])
        if tag == "link" and attrs.get("rel") in {"stylesheet", "preload", "modulepreload"} and attrs.get("href"):
            self.urls.append(attrs["href"])
        context = dict(self.stack[-1][1]) if self.stack else {}
        classes = set(attrs.get("class", "").split())
        if "review-card" in classes:
            self.card_count += 1
            context.update(card=self.card_count, article_id=attrs.get("data-article-id"))
        if "thumb" in classes and context.get("card"):
            context["image_role"] = "card"
        if "latest-media" in classes:
            context.update(image_role="highlight", article_href=attrs.get("href"))
        if tag == "img" and context.get("image_role"):
            self.images.append({**context, "attrs": attrs})
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append((tag, context))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break


def resource_file(site: Path, page: Path, url: str) -> Path:
    parts = urlsplit(url)
    if parts.scheme or parts.netloc or parts.fragment or not parts.path:
        raise ValueError("Listing and local resources must use public relative paths")
    candidate = page.parent / parts.path
    target = candidate.resolve()
    if not target.is_relative_to(site.resolve()) or not target.is_file():
        raise ValueError("Missing or invalid local page resource")
    for path in (candidate.absolute(), *candidate.absolute().parents):
        if path == site.absolute():
            break
        if path.is_symlink():
            raise ValueError("Symlinked page resource")
    return target


def page_payload(site: Path, relative: str) -> dict:
    root, page = site.resolve(), site / relative
    parser = Resources()
    parser.feed(page.read_text(encoding="utf-8"))
    local, external = {page.resolve()}, []
    for url in parser.urls:
        parts = urlsplit(url)
        if parts.scheme or parts.netloc:
            external.append(url)
            continue
        target = resource_file(site, page, url)
        local.add(target)
    return {"gzip_bytes": sum(compressed(path) for path in local),
            "local_files": sorted(path.relative_to(root).as_posix() for path in local),
            "external_resources": sorted(external), "has_search": parser.has_search}


def listing_payload(site: Path, relative: str) -> dict | None:
    """Validate real listing URLs and estimate a bounded first-six image set.

    This is a static layout model, not browser network measurement. It checks
    every rendered cover, including cards beyond the first visible six, so a
    return to full original images cannot pass as a lightweight first page.
    """
    page = site / relative
    parser = Resources()
    parser.feed(page.read_text(encoding="utf-8"))
    if not parser.images:
        return None
    reviews = json.loads((site / "manifest.json").read_text(encoding="utf-8"))
    by_id = {entry["folder"]: entry for entry in reviews}
    by_href = {(site / variant["href"]).resolve(): entry for entry in reviews
               for variant in [entry, *entry.get("translations", [])]}
    registry_path = site / "assets/listing-images/manifest.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8")) if registry_path.exists() else {"images": {}}
    if not isinstance(registry, dict) or not isinstance(registry.get("images"), dict):
        raise ValueError("Invalid listing-image manifest")
    selected = []
    for image in parser.images:
        role, attrs = image["image_role"], image["attrs"]
        if role == "card":
            record = by_id.get(image.get("article_id"))
        else:
            record = by_href.get(resource_file(site, page, image.get("article_href", "")))
        if not record or not record.get("thumbnail"):
            raise ValueError("Rendered listing image has no registered source: " + relative)
        href = record["thumbnail"]
        source = resource_file(site, site / "index.html", href)
        entry = registry["images"].get(href, {})
        allowed = {}
        if source.stat().st_size <= 60_000:
            allowed[source] = None
        elif source.suffix.lower() == ".svg":
            # Large vectors are still valid vector art, but participate in the
            # same aggregate image budget as any other source.
            allowed[source] = None
        if entry:
            if entry.get("source_sha256") != hashlib.sha256(source.read_bytes()).hexdigest():
                raise ValueError("Listing-image source changed without rebuilding: " + href)
            for variant in entry.get("variants", []):
                variant_href = variant.get("href", "")
                if not re.fullmatch(r"assets/listing-images/[a-f0-9]{64}-w(?:480|960|1200)\.webp", variant_href):
                    raise ValueError("Invalid listing-image derivative path")
                path = resource_file(site, site / "index.html", variant_href)
                if (path.stat().st_size != variant.get("bytes")
                        or hashlib.sha256(path.read_bytes()).hexdigest() != variant.get("sha256")):
                    raise ValueError("Modified listing-image derivative: " + variant_href)
                allowed[path] = variant
        src = resource_file(site, page, attrs.get("src", ""))
        if src not in allowed:
            raise ValueError("Large original or unrelated cover served instead of a registered derivative: " + href)
        candidates = []
        for value in attrs.get("srcset", "").split(","):
            if not value.strip():
                continue
            match = re.fullmatch(r"\s*(\S+)\s+([1-9][0-9]*)w\s*", value)
            if not match:
                raise ValueError("Invalid listing-image srcset: " + href)
            path = resource_file(site, page, match[1])
            variant = allowed.get(path)
            if not variant or variant.get("width") != int(match[2]):
                raise ValueError("Unregistered or incorrect listing-image srcset width: " + href)
            candidates.append((int(match[2]), path))
        if src != source and not candidates:
            raise ValueError("Responsive listing-image srcset is missing: " + href)
        if len({width for width, _ in candidates}) != len(candidates):
            raise ValueError("Duplicate listing-image srcset width: " + href)
        if role == "highlight" or image.get("card", 0) <= 6:
            selected.append({"role": role, "src": src, "candidates": sorted(candidates)})

    def total(paths):
        return sum(path.stat().st_size for path in set(paths))

    def choose(image, width):
        if not image["candidates"]:
            return image["src"]
        return next((path for candidate_width, path in image["candidates"] if candidate_width >= width), image["candidates"][-1][1])

    def display_width(role, viewport):
        if role == "highlight":
            return viewport - 36 if viewport <= 700 else 600
        return viewport - 36 if viewport <= 560 else (viewport - 59) / 2 if viewport <= 960 else 376

    modeled = {f"viewport_{viewport}_{scale}x_bytes": total(choose(image, display_width(image["role"], viewport) * scale) for image in selected)
               for viewport, scale in [(360, 1), (1280, 1), (1280, 2)]}
    return {"validated_listing_images": len(parser.images), "modeled_first_cards": min(parser.card_count, 6),
            "default_bytes": total(image["src"] for image in selected),
            "variants_960_bytes": total(choose(image, 960) for image in selected), **modeled,
            "default_max_bytes": 650_000, "variants_960_soft_max_bytes": 800_000,
            "limits": "Deduplicated local image bytes for the first six cards plus highlight. Viewport estimates use current CSS at device scale1/2; actual browser selection/lazy loading is verified separately."}


def check_budget(site: Path, baseline: Path | None = None, *, baseline_payload: dict | None = None) -> dict:
    pages, failures, warnings = {}, [], []
    if baseline_payload is not None and (not isinstance(baseline_payload, dict)
            or any(name not in PAGES or type(value) is not int or value < 0 for name, value in baseline_payload.items())):
        raise ValueError("Baseline payload must map known page names to nonnegative gzip byte counts")
    has_search = False
    for name in PAGES:
        if not (site / name).exists():
            continue
        report = page_payload(site, name)
        has_search = has_search or report["has_search"]
        if any(Path(path).name in LAZY_SEARCH for path in report["local_files"]):
            failures.append("Search engine/index loaded before interaction: " + name)
        maximum = 100_000
        if baseline_payload is not None and name in baseline_payload:
            maximum = min(baseline_payload[name] + 5_000, 100_000)
        elif baseline and (baseline / name).is_file():
            maximum = min(page_payload(baseline, name)["gzip_bytes"] + 5_000, 100_000)
        report["max_gzip_bytes"] = maximum
        if report["gzip_bytes"] > maximum:
            failures.append("Initial HTML/JS/CSS exceeds budget: " + name)
        listing = listing_payload(site, name)
        if listing:
            report["listing_images"] = listing
            if listing["default_bytes"] > listing["default_max_bytes"]:
                failures.append("First six listing images and highlight exceed 650KB: " + name)
            if listing["variants_960_bytes"] > listing["variants_960_soft_max_bytes"]:
                warnings.append("960px listing image choices exceed 800KB; review quality and dimensions: " + name)
        pages[name] = report
    search_paths = [site / "assets" / name for name in LAZY_SEARCH]
    if has_search:
        for path in search_paths:
            if not path.is_file() or path.is_symlink():
                failures.append("Search widget requires missing/invalid lazy asset: " + path.name)
    search_bytes = sum(compressed(path) for path in search_paths if path.is_file())
    if search_bytes > 100_000:
        failures.append("Lazy metadata search exceeds 100KB gzip")
    icons = [site / "favicon.ico", site / "assets/ai-tech-review-icon.svg"]
    icon_bytes = sum(compressed(path) for path in icons if path.is_file())
    if icon_bytes > 30_000:
        failures.append("Browser favicon payload exceeds 30KB gzip")
    return {"ok": not failures, "failures": failures, "warnings": warnings, "pages": pages,
            "lazy_search_gzip_bytes": search_bytes, "browser_icons_gzip_bytes": icon_bytes,
            "limits": "Local HTML/JS/CSS gzip estimates and separate listing-image byte models exclude external fonts, edge scripts and API traffic. No claim of mobile speed or network transfer."}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--baseline-site", type=Path)
    parser.add_argument("--baseline-payload", type=Path, help="Previously deployed page-name to gzip-byte map")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output and args.output.resolve().is_relative_to(args.site.resolve()):
            raise ValueError("Payload report must stay outside public output")
        previous_payload = json.loads(args.baseline_payload.read_text(encoding="utf-8")) if args.baseline_payload else None
        result = check_budget(args.site, args.baseline_site, baseline_payload=previous_payload)
        payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(payload, encoding="utf-8")
        print(payload, end="")
        return 0 if result["ok"] else 1
    except (ValueError, OSError) as error:
        print(json.dumps({"error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
