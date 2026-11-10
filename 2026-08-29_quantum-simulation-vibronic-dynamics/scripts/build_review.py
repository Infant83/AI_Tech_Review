"""Build the two existing web editions from their canonical manuscripts."""
from pathlib import Path
import html
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
TOPIC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from markdown_to_html import build_context, render_final_review_template
from html_to_dist import package_html


def main():
    settings = json.loads(Path(__file__).with_name("rendering-settings.json").read_text())
    for language, suffix, subdir in [("ko", "", ""), ("en", "_en", "en")]:
        source = TOPIC / "reports" / f"{TOPIC.name}_final_review{suffix}.md"
        context = build_context(source, "final-review")
        context.generated_at = settings["original_generated_at"][language]
        context.source_modified_at = context.modified_date
        # Keep the former article fragments even when report-style subheadings
        # have been incorporated into their parent section's prose.
        aliases = settings["legacy_anchors"][language]
        def heading(match):
            level, identifier, content = match.groups()
            title = html.unescape(re.sub("<[^>]+>", "", content))
            anchors = "".join(
                f'<span class="legacy-anchor" id="{old}" aria-hidden="true"></span>'
                for old in aliases.get(title, [])
            )
            return anchors + f'<h{level} id="section-{identifier}">{content}</h{level}>'
        context.body_html = re.sub(r'<h([2-4]) id="([^"]+)">(.*?)</h\1>', heading, context.body_html, flags=re.S)
        context.toc_html = context.toc_html.replace('href="#', 'href="#section-')
        count = 0
        def figure(match):
            nonlocal count
            count += 1
            url = re.search(r'\bsrc="([^"]+)"', match[1]).group(1)
            label = f"그림 {count} 크게 보기 (새 탭)" if language == "ko" else f"Open Figure {count} at full size (new tab)"
            return f'<figure class="figure-panel figure-panel-fit"><a class="figure-zoom" href="{url}" target="_blank" rel="noopener" aria-label="{label}">{match[1]}</a><figcaption>{match[2]}</figcaption></figure>'
        context.body_html = re.sub(r'<p>(<img\b[^>]+>)</p>\s*<p><em>((?:그림|Figure) \d+\..*?)</em></p>', figure, context.body_html, flags=re.S)
        if count != 2:
            raise ValueError(f"Expected two figures in {language}, got {count}")
        label = "표 좌우로 보기" if language == "ko" else "Scroll table horizontally"
        context.body_html = context.body_html.replace("<table>", f'<div class="table-scroll" tabindex="0" role="region" aria-label="{label}"><table>').replace("</table>", "</table></div>")
        output = render_final_review_template(context)
        old_labels = ("생성 시각:", "원본 파일 최종 수정 시각:") if language == "ko" else ("Generated:", "Source last modified:")
        new_labels = ("원 발행본 생성 시각:", "편집 개정:") if language == "ko" else ("Original edition generated:", "Editorial revision:")
        for old, new in zip(old_labels, new_labels):
            output = output.replace(old, new)
        output = output.replace("  </style>", """
    .final-article, .content-grid > *, .hero-inner > * { min-width: 0; }
    .table-scroll { max-width: 100%; overflow-x: auto; }
    .table-scroll:focus-visible, .figure-zoom:focus-visible { outline: 2px solid var(--teal); outline-offset: 4px; }
    .figure-zoom { display: block; cursor: zoom-in; }
    mjx-container[display="true"] { overflow-x: auto; overflow-y: hidden; max-width: 100%; }
    .reference-list { overflow-wrap: anywhere; }
    .reference-list li { margin-bottom: 1rem; }
    .citation { white-space: nowrap; }
    code { overflow-wrap: anywhere; white-space: normal; }
  </style>""")
        source.with_suffix(".html").write_text("\n".join(line.rstrip() for line in output.splitlines()) + "\n")
        result = package_html(source.with_suffix(".html"), TOPIC / "dist" / subdir)
        if result.missing_refs:
            raise ValueError(result.missing_refs)
    print("Built both web editions with two existing figures")


if __name__ == "__main__":
    main()
