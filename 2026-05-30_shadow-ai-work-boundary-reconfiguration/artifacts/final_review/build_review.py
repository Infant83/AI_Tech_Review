"""Render this canonical article with its existing shared Markdown renderer.

The numbered APS bibliography already contains the source links. The sidebar
points to that bibliography instead of auto-extracting a second source list.
"""
from dataclasses import replace
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
TOPIC = "2026-05-30_shadow-ai-work-boundary-reconfiguration"
sys.path.insert(0, str(ROOT / "scripts"))
from markdown_to_html import LinkItem, build_context, render_template, strip_frontmatter


def main() -> None:
    source = ROOT / TOPIC / "reports" / f"{TOPIC}_final_review.md"
    context = build_context(source, "final-review")
    metadata, _ = strip_frontmatter(source.read_text(encoding="utf-8"))
    context = replace(
        context,
        published_date=metadata["published_at"],
        links=[LinkItem("References", "#references", False)],
    )
    rendered = "\n".join(line.rstrip() for line in render_template(context).splitlines()) + "\n"
    context.output_path.write_text(rendered, encoding="utf-8")
    print(f"[rendered:final-review] {context.output_path}")


if __name__ == "__main__":
    main()
