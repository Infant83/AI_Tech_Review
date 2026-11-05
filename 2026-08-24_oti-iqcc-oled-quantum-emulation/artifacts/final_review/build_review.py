"""Render the complete recovered manuscript in its original article layout."""
import hashlib
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
TOPIC = "2026-08-24_oti-iqcc-oled-quantum-emulation"
sys.path.insert(0, str(ROOT / "scripts"))
from markdown_to_html import strip_frontmatter, metadata_value, build_markdown_html
from html_to_dist import build_flat_refs


def main():
    source = ROOT / TOPIC / "reports" / f"{TOPIC}_final_review.md"
    metadata, body = strip_frontmatter(source.read_text())
    rendered, _ = build_markdown_html(body)
    template = Path(__file__).with_name("layout.html").read_text()
    if template.count("<!-- ARTICLE_BODY -->") != 1:
        raise ValueError("Expected one manuscript slot in the preserved layout")
    rendered = template.replace("<!-- ARTICLE_BODY -->", rendered)
    title = metadata_value(metadata, "title")
    if f"<title>{title}</title>" not in rendered:
        raise ValueError("Manuscript and layout titles differ")
    # The revised explanatory SVG keeps its established public filename.
    def version_svg(match):
        path = (source.parent / match.group(2)).resolve()
        version = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        return f'{match.group(1)}{match.group(2)}?v={version}{match.group(3)}'
    rendered = re.sub(r'(\b(?:src|href)=")([^"?]+\.svg)(")', version_svg, rendered)
    rendered = "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"
    source.with_suffix(".html").write_text(rendered)
    dist = ROOT / TOPIC / "dist"
    public, _, missing, _ = build_flat_refs(rendered, source.parent, dist)
    if missing:
        raise ValueError(f"Missing manuscript assets: {missing}")
    (dist / "index.html").write_text(public)
    flat_source, _, missing, _ = build_flat_refs(source.read_text(), source.parent, dist)
    if missing:
        raise ValueError(f"Missing source assets: {missing}")
    (dist / source.name).write_text(flat_source)
    print(f"Rendered complete manuscript: {TOPIC}")


if __name__ == "__main__":
    main()
