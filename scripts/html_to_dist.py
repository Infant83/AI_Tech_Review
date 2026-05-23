from __future__ import annotations

import argparse
import html
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit


LOCAL_REF_RE = re.compile(
    r"(?P<prefix>\b(?:src|href)=['\"])(?P<url>[^'\"]+)(?P<suffix>['\"])",
    re.IGNORECASE,
)


@dataclass
class DistResult:
    source_html: Path
    dist_dir: Path
    html_output: Path
    index_output: Path | None
    copied_files: list[Path]
    missing_refs: list[str]


def is_external_or_anchor(url: str) -> bool:
    stripped = url.strip()
    if not stripped or stripped.startswith("#"):
        return True
    parts = urlsplit(stripped)
    if parts.scheme or parts.netloc:
        return True
    return stripped.startswith(("data:", "mailto:", "tel:", "javascript:"))


def default_dist_dir(source_html: Path) -> Path:
    if source_html.parent.name == "reports":
        return source_html.parent.parent / "dist"
    return source_html.parent / "dist"


def split_local_url(url: str) -> tuple[str, str, str]:
    parts = urlsplit(html.unescape(url))
    return unquote(parts.path), parts.query, parts.fragment


def rebuild_local_url(filename: str, query: str, fragment: str) -> str:
    rebuilt = filename
    if query:
        rebuilt += f"?{query}"
    if fragment:
        rebuilt += f"#{fragment}"
    return rebuilt


def unique_dest_name(source_path: Path, used_names: set[str]) -> str:
    candidate = source_path.name
    if candidate not in used_names:
        used_names.add(candidate)
        return candidate

    stem = source_path.stem
    suffix = source_path.suffix
    index = 2
    while True:
        candidate = f"{stem}_{index}{suffix}"
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
        index += 1


def build_flat_refs(html_text: str, html_dir: Path, dist_dir: Path) -> tuple[str, list[Path], list[str]]:
    copied: list[Path] = []
    missing: list[str] = []
    source_to_dest: dict[Path, str] = {}
    used_names: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        raw_url = match.group("url")
        if is_external_or_anchor(raw_url):
            return match.group(0)

        local_path, query, fragment = split_local_url(raw_url)
        if not local_path:
            return match.group(0)

        source_path = (html_dir / local_path).resolve()
        if not source_path.exists() or not source_path.is_file():
            missing.append(raw_url)
            return match.group(0)

        if source_path not in source_to_dest:
            dest_name = unique_dest_name(source_path, used_names)
            source_to_dest[source_path] = dest_name
            dest_path = dist_dir / dest_name
            shutil.copy2(source_path, dest_path)
            copied.append(dest_path)

        new_url = rebuild_local_url(source_to_dest[source_path], query, fragment)
        escaped_url = html.escape(new_url, quote=True)
        return f"{match.group('prefix')}{escaped_url}{match.group('suffix')}"

    rewritten = LOCAL_REF_RE.sub(replace, html_text)
    return rewritten, copied, missing


def validate_local_refs(html_text: str, dist_dir: Path) -> list[str]:
    missing: list[str] = []
    for match in LOCAL_REF_RE.finditer(html_text):
        raw_url = match.group("url")
        if is_external_or_anchor(raw_url):
            continue
        local_path, _, _ = split_local_url(raw_url)
        if not local_path:
            continue
        if not (dist_dir / local_path).exists():
            missing.append(raw_url)
    return sorted(set(missing))


def package_html(source_html: Path, dist_dir: Path | None = None, index_name: str = "index.html") -> DistResult:
    source_html = source_html.resolve()
    if not source_html.exists() or not source_html.is_file():
        raise FileNotFoundError(f"HTML file not found: {source_html}")
    if source_html.suffix.lower() not in {".html", ".htm"}:
        raise ValueError(f"Expected an HTML file: {source_html}")

    final_dist_dir = (dist_dir or default_dist_dir(source_html)).resolve()
    final_dist_dir.mkdir(parents=True, exist_ok=True)

    raw_html = source_html.read_text(encoding="utf-8")
    rewritten_html, copied_files, missing_refs = build_flat_refs(raw_html, source_html.parent, final_dist_dir)

    html_output = final_dist_dir / source_html.name
    html_output.write_text(rewritten_html, encoding="utf-8")

    index_output: Path | None = None
    if index_name:
        index_output = final_dist_dir / index_name
        index_output.write_text(rewritten_html, encoding="utf-8")

    missing_after_write = validate_local_refs(rewritten_html, final_dist_dir)
    return DistResult(
        source_html=source_html,
        dist_dir=final_dist_dir,
        html_output=html_output,
        index_output=index_output,
        copied_files=copied_files,
        missing_refs=sorted(set(missing_refs + missing_after_write)),
    )


def make_zip(dist_dir: Path, zip_path: Path | None = None) -> Path:
    final_zip_path = zip_path or dist_dir.with_suffix(".zip")
    final_zip_path.parent.mkdir(parents=True, exist_ok=True)
    if final_zip_path.exists():
        final_zip_path.unlink()
    shutil.make_archive(str(final_zip_path.with_suffix("")), "zip", dist_dir)
    return final_zip_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Package a rendered HTML report into a flat dist folder. Local src/href "
            "files are copied next to the HTML and references are rewritten to filenames."
        )
    )
    parser.add_argument("html", type=Path, help="Rendered HTML file to package.")
    parser.add_argument(
        "--dist",
        type=Path,
        default=None,
        help="Output dist directory. Defaults to <topic>/dist for reports/*.html.",
    )
    parser.add_argument(
        "--index-name",
        default="index.html",
        help="Also write this index HTML filename. Use an empty string to skip.",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Create a zip archive from the dist folder after packaging.",
    )
    parser.add_argument(
        "--zip-path",
        type=Path,
        default=None,
        help="Optional zip output path. Defaults to <dist>.zip.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = package_html(args.html, args.dist, args.index_name)

    print(f"[dist] {result.dist_dir}")
    print(f"[html] {result.html_output}")
    if result.index_output:
        print(f"[index] {result.index_output}")
    for copied_file in sorted(result.copied_files, key=lambda path: path.name.lower()):
        print(f"[copy] {copied_file.name}")

    if args.zip:
        zip_path = make_zip(result.dist_dir, args.zip_path)
        print(f"[zip] {zip_path}")

    if result.missing_refs:
        for ref in result.missing_refs:
            print(f"[missing] {ref}")
        return 2

    print("[local-ref-check] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
