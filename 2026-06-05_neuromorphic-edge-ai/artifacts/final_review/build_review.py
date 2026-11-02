"""Render this canonical article with its existing shared Markdown renderer.

The numbered APS bibliography already contains the source links. The sidebar
points to that bibliography instead of auto-extracting a second source list.
"""
from dataclasses import replace
import hashlib
import html
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[3]
TOPIC = "2026-06-05_neuromorphic-edge-ai"
sys.path.insert(0, str(ROOT / "scripts"))
from markdown_to_html import LinkItem, build_context, render_template, strip_frontmatter
from html_to_dist import build_flat_refs


def main() -> None:
    source = ROOT / TOPIC / "reports" / f"{TOPIC}_final_review.md"
    context = build_context(source, "final-review")
    metadata, _ = strip_frontmatter(source.read_text(encoding="utf-8"))
    context = replace(
        context,
        published_date=metadata.get("published_at", "2026-06-05"),
        links=[LinkItem("References", "#references", False)],
    )
    rendered = "\n".join(line.rstrip() for line in render_template(context).splitlines()) + "\n"
    # The public article links to its bibliography, not internal source files.
    source_anchor = f'<a href="{html.escape(source.name, quote=True)}">{html.escape(source.name)}</a>'
    if rendered.count(source_anchor) != 1:
        raise ValueError("Expected one source-file toolbar link")
    rendered = rendered.replace(source_anchor, "")

    def version_svg(match):
        path = (source.parent / match.group(2)).resolve()
        version = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        return f'{match.group(1)}{match.group(2)}?v={version}{match.group(3)}'

    rendered = re.sub(r'(\bsrc=")([^"?]+\.svg)(")', version_svg, rendered)
    rendered = "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"
    context.output_path.write_text(rendered, encoding="utf-8")
    # Keep the existing local distributable manuscript synchronized as well.
    dist = ROOT / TOPIC / "dist"
    flat_markdown, _, missing, _ = build_flat_refs(source.read_text(encoding="utf-8"), source.parent, dist)
    if missing:
        raise ValueError(f"Missing distributable manuscript assets: {missing}")
    (dist / source.name).write_text(flat_markdown, encoding="utf-8")
    print(f"[rendered:final-review] {context.output_path}")


if __name__ == "__main__":
    main()
