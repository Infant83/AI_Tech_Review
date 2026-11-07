"""Cache small, uncropped list images while keeping published artwork intact.

The publisher builds these derivatives once. HTML rendering only reads their
small manifest; browser users do not need an image service or a new API.
"""
from __future__ import annotations

from functools import lru_cache
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Iterable
from urllib.parse import unquote, urlsplit


ASSET_DIR = "assets/listing-images"
RECIPE_VERSION = 1
# Target width, starting quality, quality floor, soft byte budget. Do not crop
# or blur artwork to force an arbitrary byte target.
RECIPES = {480: (80, 68, 60_000), 960: (76, 62, 120_000), 1200: (82, 68, 200_000)}
DERIVATIVE_NAME = re.compile(r"[a-f0-9]{64}-w(?:480|960|1200)\.webp\Z")
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def _source_path(site_dir: Path, href: str) -> Path:
    parsed = urlsplit(href)
    decoded = unquote(parsed.path)
    if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
            or not decoded or decoded.startswith(("/", "\\"))
            or decoded != href or "\\" in decoded or "%" in decoded
            or any(part in {"", ".", ".."} for part in decoded.split("/"))):
        raise ValueError("A listing source must be an unencoded relative public path")
    root = Path(site_dir).absolute()
    source = root / decoded
    for component in (root, *(root.joinpath(*source.relative_to(root).parts[:i])
                               for i in range(1, len(source.relative_to(root).parts) + 1))):
        if component.is_symlink():
            raise ValueError("Symlinks are not allowed in listing-image paths")
    if not source.resolve().is_relative_to(root.resolve()) or not source.is_file():
        raise ValueError(f"Listing source is unavailable: {href}")
    return source


def _write_atomic(path: Path, data: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=".listing-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def _load_manifest(site_dir: Path) -> dict:
    path = Path(site_dir) / ASSET_DIR / "manifest.json"
    if not path.exists():
        return {"version": RECIPE_VERSION, "images": {}}
    if path.is_symlink():
        raise ValueError("Listing image manifest must not be a symlink")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != RECIPE_VERSION or not isinstance(data.get("images"), dict):
        raise ValueError("Unsupported listing-image manifest")
    return data


def _cached_variant(directory: Path, entry: dict | None) -> bool:
    if not isinstance(entry, dict):
        return False
    href = entry.get("href", "")
    if not isinstance(href, str) or not href.startswith(ASSET_DIR + "/"):
        return False
    name = href.removeprefix(ASSET_DIR + "/")
    if not DERIVATIVE_NAME.fullmatch(name):
        return False
    if (type(entry.get("width")) is not int or type(entry.get("height")) is not int
            or entry["width"] <= 0 or entry["height"] <= 0
            or entry.get("requested_width") not in RECIPES):
        return False
    path = directory / name
    return (path.is_file() and not path.is_symlink()
            and path.stat().st_size == entry.get("bytes")
            and hashlib.sha256(path.read_bytes()).hexdigest() == entry.get("sha256"))


def build_listing_images(site_dir: Path, thumbnails: Iterable[str], *,
                         highlight_hrefs: Iterable[str] = ()) -> dict:
    """Generate/reuse registered raster derivatives and return their manifest.

    Ordinary cards get 480px and 960px variants. Only requested highlights need
    the extra 1200px export. Small sources are never enlarged. SVG artwork
    keeps its original vector URL. Source bytes are never rewritten/deleted.
    """
    try:
        import PIL
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise RuntimeError("Listing-image build requires: python3 -m pip install -r scripts/requirements-listing-images.txt") from exc
    root = Path(site_dir)
    directory = root / ASSET_DIR
    if directory.is_symlink() or (root / "assets").is_symlink():
        raise ValueError("Listing-image output must not be a symlink")
    directory.mkdir(parents=True, exist_ok=True)
    previous = _load_manifest(root)
    highlights = set(highlight_hrefs)
    images = {}
    for href in sorted(set(thumbnails)):
        source = _source_path(root, href)
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if source.suffix.lower() == ".svg":
            images[href] = {"source_sha256": digest, "original_vector": True, "variants": []}
            continue
        if source.suffix.lower() not in RASTER_SUFFIXES:
            raise ValueError(f"Unsupported listing-image type: {href}")
        # Include encoder version, so old recipes are never silently reused by
        # a newly installed Pillow build with different encoded output.
        key = hashlib.sha256(f"{digest}:{RECIPE_VERSION}:{PIL.__version__}:{RECIPES}".encode()).hexdigest()
        prior = previous["images"].get(href, {})
        requested = [480, 960] + ([1200] if href in highlights else [])
        cached = [next((item for item in prior.get("variants", [])
                        if item.get("requested_width") == width
                        and item.get("href") == f"{ASSET_DIR}/{key}-w{width}.webp"), None)
                  for width in requested]
        if (prior.get("source_sha256") == digest and all(_cached_variant(directory, item) for item in cached)):
            images[href] = {**prior, "variants": cached}
            continue
        variants = []
        with Image.open(source) as opened:
            image = ImageOps.exif_transpose(opened)
            image.load()
            # Retain alpha (including indexed PNG transparency) and its color
            # profile. Drop EXIF/XMP rather than changing displayed colors.
            icc_profile = image.info.get("icc_profile", b"")
            has_alpha = "A" in image.getbands() or "transparency" in image.info
            image = image.convert("RGBA" if has_alpha else "RGB")
            image.info.clear()
            original_width, original_height = image.size
            for requested_width in requested:
                old = next((item for item in prior.get("variants", [])
                            if item.get("requested_width") == requested_width
                            and item.get("href") == f"{ASSET_DIR}/{key}-w{requested_width}.webp"), None)
                if _cached_variant(directory, old):
                    variants.append(old)
                    continue
                quality, quality_floor, target = RECIPES[requested_width]
                width = min(requested_width, original_width)
                height = max(1, round(original_height * width / original_width))
                resized = image.resize((width, height), Image.Resampling.LANCZOS)
                while True:
                    output = BytesIO()
                    resized.save(output, "WEBP", quality=quality, method=6, exact=True, icc_profile=icc_profile)
                    data = output.getvalue()
                    if len(data) <= target or quality <= quality_floor:
                        break
                    quality = max(quality_floor, quality - 4)
                name = f"{key}-w{requested_width}.webp"
                _write_atomic(directory / name, data)
                variants.append({"href": f"{ASSET_DIR}/{name}", "requested_width": requested_width,
                                 "width": width, "height": height, "quality": quality,
                                 "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        images[href] = {"source_sha256": digest, "source_bytes": source.stat().st_size,
                        "width": original_width, "height": original_height, "variants": variants}
    result = {"version": RECIPE_VERSION, "encoder": f"Pillow {PIL.__version__}", "images": images}
    encoded = (json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    manifest_path = directory / "manifest.json"
    if not manifest_path.exists() or manifest_path.read_bytes() != encoded:
        _write_atomic(manifest_path, encoded)
    _render_manifest.cache_clear()
    return result


@lru_cache(maxsize=8)
def _render_manifest(site_dir: str, modified_ns: int, size: int) -> dict:
    return _load_manifest(Path(site_dir))


def image_attributes(href: str, *, role: str = "card", prefix: str = "", site_dir: Path | None = None) -> dict[str, str | int]:
    """Return plain img attributes; the caller must HTML-escape their values.

    An absent manifest/vector/small raster yields {} so existing original URL
    fallback remains intact, including no-JavaScript rendering.
    """
    if role not in {"card", "highlight"}:
        raise ValueError("Listing-image role must be card or highlight")
    if site_dir is None:
        return {}
    path = Path(site_dir) / ASSET_DIR / "manifest.json"
    if not path.is_file():
        return {}
    stat = path.stat()
    entry = _render_manifest(str(Path(site_dir).resolve()), stat.st_mtime_ns, stat.st_size)["images"].get(href)
    if not isinstance(entry, dict) or entry.get("original_vector"):
        return {}
    variants = entry.get("variants", [])
    selected = [v for v in variants if isinstance(v, dict) and _cached_variant(path.parent, v)
                and (role == "highlight" or v.get("requested_width") in {480, 960})]
    # Small original images can map several requested sizes to the same width.
    by_width = {v["width"]: v for v in selected}
    selected = [by_width[key] for key in sorted(by_width)]
    if not selected:
        return {}
    default = selected[0] if role == "card" else next((v for v in selected if v["width"] >= 960), selected[-1])
    sizes = ("(max-width: 560px) calc(100vw - 36px), (max-width: 960px) calc((100vw - 59px) / 2), 376px"
             if role == "card" else "(max-width: 700px) calc(100vw - 36px), 600px")
    return {"src": prefix + default["href"], "srcset": ", ".join(f'{prefix}{v["href"]} {v["width"]}w' for v in selected),
            "sizes": sizes, "width": default["width"], "height": default["height"]}
