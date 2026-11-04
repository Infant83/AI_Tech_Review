"""Render the recovered canonical manuscript with the shared article renderer."""
from dataclasses import replace
import hashlib
import html
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[3]
TOPIC = "2026-06-11_QC-based-inverse-design"
MANUSCRIPT = "2026-07-11_qc-based-inverse-design_final_review.md"
sys.path.insert(0, str(ROOT / "scripts"))
from markdown_to_html import LinkItem, build_context, render_template
from html_to_dist import build_flat_refs


def main() -> None:
    source = ROOT / TOPIC / "reports" / MANUSCRIPT
    context = replace(
        build_context(source, "final-review"),
        # June 11 is the recovered draft date, not the public publication date.
        published_date="2026-07-11",
        links=[LinkItem("참고문헌", "#references", False)],
    )
    rendered = "\n".join(line.rstrip() for line in render_template(context).splitlines()) + "\n"
    source_anchor = f'<a href="{html.escape(source.name, quote=True)}">{html.escape(source.name)}</a>'
    if rendered.count(source_anchor) != 1:
        raise ValueError("Expected one source-file toolbar link")
    rendered = rendered.replace(source_anchor, "")
    def version_svg(match):
        path = (source.parent / match.group(2)).resolve()
        if path.name not in {"quantum_advantage_ledger.svg", "quantum_advantage_ledger_mobile.svg"}:
            return match.group(0)
        version = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
        return f'{match.group(1)}{match.group(2)}?v={version}{match.group(3)}'
    rendered = re.sub(r'(\bsrc=")([^"?]+\.svg)(")', version_svg, rendered)
    style = """<style id="inverse-design-reference-style">
    .final-article ol.references { list-style:none; padding-left:0; }
    .final-article ol.references li { padding-left:2.6em; text-indent:-2.6em; overflow-wrap:anywhere; scroll-margin-top:28px; }
    .final-article .reference-number { font-variant-numeric:tabular-nums; }
    .final-article .citation { white-space:nowrap; }
    </style>"""
    rendered = rendered.replace("</head>", style + "\n</head>", 1)
    rendered = "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"
    context.output_path.write_text(rendered, encoding="utf-8")
    dist = ROOT / TOPIC / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    flat_markdown, _, missing, _ = build_flat_refs(source.read_text(encoding="utf-8"), source.parent, dist)
    if missing:
        raise ValueError(f"Missing distributable manuscript assets: {missing}")
    (dist / source.name).write_text(flat_markdown, encoding="utf-8")
    print(f"[rendered:final-review] {context.output_path}")


if __name__ == "__main__":
    main()
