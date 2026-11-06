"""Render the complete Markdown manuscript in its preserved article layout."""
from pathlib import Path
import hashlib
import html
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
TOPIC = "2026-08-26_quantum-computing-layers"
sys.path.insert(0, str(ROOT / "scripts"))
from markdown_to_html import strip_frontmatter, build_markdown_html
from html_to_dist import build_flat_refs


def main():
    source = ROOT / TOPIC / "reports" / f"{TOPIC}_final_review.md"
    _, body = strip_frontmatter(source.read_text())
    # The title and hero retain their established positions in the layout.
    body, count = re.subn(r"^# [^\n]+\n", "", body, count=1)
    if count != 1:
        raise ValueError("Expected the manuscript H1")
    hero = re.search(r"!\[([^\]]+)\]\(([^)]+)\)\s*\n\s*\*([^\n]+)\*", body)
    if not hero:
        raise ValueError("Expected the existing hero and caption")
    hero_path = (source.parent / hero.group(2)).resolve()
    body = body[:hero.start()] + body[hero.end():]
    rendered, _ = build_markdown_html(body)
    rendered = rendered.replace("<p>", '<p class="lead">', 1)
    rendered = re.sub(r"<p>(<img\b[^>]+>)</p>", r'<figure class="figure-panel">\1</figure>', rendered)
    rendered = re.sub(r"<p><em>(그림 [23]\..*?)</em></p>", r'<p class="figure-caption">\1</p>', rendered, flags=re.S)
    rendered = rendered.replace("<table>", '<div class="table-wrap" tabindex="0" role="region" aria-label="계산 플랫폼과 해석 조건 비교"><table>').replace("</table>", "</table></div>")
    dist = ROOT / TOPIC / "dist"
    public_body, _, missing, _ = build_flat_refs(rendered, source.parent, dist)
    if missing:
        raise ValueError(f"Missing manuscript assets: {missing}")
    shutil.copyfile(hero_path, dist / hero_path.name)
    def version_svg(match):
        digest = hashlib.sha256((dist / match.group(2)).read_bytes()).hexdigest()[:12]
        return f'{match.group(1)}{match.group(2)}?v={digest}{match.group(3)}'
    public_body = re.sub(r'(\bsrc=")([^"?]+\.svg)(")', version_svg, public_body)
    figure_number = 1
    def add_figure_link(match):
        nonlocal figure_number
        figure_number += 1
        href = html.escape(html.unescape(match.group(2)), quote=True)
        return (match.group(1) + match.group(3)
                + f'<br><a class="figure-open" href="{href}" target="_blank" rel="noopener" aria-label="그림 {figure_number} 크게 보기 (새 탭)">그림 크게 보기 ↗</a>'
                + match.group(4))
    public_body = re.sub(r'(<figure class="figure-panel"><img\b[^>]*src="([^"]+)"[^>]*></figure>\s*<p class="figure-caption">)(.*?)(</p>)', add_figure_link, public_body, flags=re.S)
    public_briefing = ROOT / TOPIC / "artifacts/public-assets/daily_quantum_brief_2026-08-26.pdf"
    if public_briefing.exists():
        shutil.copyfile(public_briefing, dist / public_briefing.name)
    template = Path(__file__).with_name("layout.html").read_text()
    if template.count("<!-- ARTICLE_BODY -->") != 1:
        raise ValueError("Expected exactly one article slot")
    template = re.sub(r'(<figure class="hero-figure"><img\b[^>]*\balt=")[^"]*', lambda m:m.group(1)+html.escape(hero.group(1),quote=True), template)
    # The hero caption is authored alongside the image in the manuscript.
    template = re.sub(r'(<figure class="hero-figure">.*?<figcaption>).*?(</figcaption>)', lambda m:m.group(1)+html.escape(hero.group(3))+m.group(2), template, flags=re.S)
    output = template.replace("<!-- ARTICLE_BODY -->", public_body)
    pdf_name = "daily_quantum_brief_2026-08-26.pdf"
    pdf_version = hashlib.sha256((dist / pdf_name).read_bytes()).hexdigest()[:12]
    output = output.replace(f'href="{pdf_name}"', f'href="{pdf_name}?v={pdf_version}"')
    output = "\n".join(line.rstrip() for line in output.splitlines()) + "\n"
    source.with_suffix(".html").write_text(output)
    (dist / "index.html").write_text(output)
    flat_source = source.read_text()
    for name in ["quantum_layers_hero_imagegen-web.webp", "quantum_evidence_layers.svg", "qrc_baseline_comparison.svg"]:
        flat_source = flat_source.replace("../artifacts/final_review/figures/"+name, name)
    (dist / source.name).write_text(flat_source)
    print(f"Rendered complete manuscript: {TOPIC}")


if __name__ == "__main__":
    main()
