"""Render the complete manuscript in the article's preserved layout.

Original image files are kept as source assets; public HTML and the flat
Markdown copy are generated from reports/, rather than edited independently.
"""
from pathlib import Path
import hashlib
import html
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[3]
TOPIC = "2026-08-27_classiq-ashn-circuit-compression"
ASSETS = Path(__file__).with_name("figures")
sys.path.insert(0, str(ROOT / "scripts"))
from markdown_to_html import strip_frontmatter, build_markdown_html, metadata_value
from html_to_dist import build_flat_refs

# Pandoc's former section identifiers omitted numeric heading prefixes.
# Retain these existing links while allowing Markdown's ordinary identifiers.
LEGACY_IDS = {
    "먼저 큰 그림: 양자 회로 최적화는 여러 층에서 일어난다": "먼저-큰-그림-양자-회로-최적화는-여러-층에서-일어난다",
    "1. 연구 배경: 왜 양자 회로 최적화가 필요한가": "연구-배경-왜-양자-회로-최적화가-필요한가",
    "‘회로 깊이’도 세 종류로 나눠야 한다": "회로-깊이도-세-종류로-나눠야-한다",
    "2. Classiq은 위쪽에서 구현을 고른다": "classiq은-위쪽에서-구현을-고른다",
    "Qmod와 EDA식 합성: 먼저 기능을 쓰고 나중에 회로를 정한다": "qmod와-eda식-합성-먼저-기능을-쓰고-나중에-회로를-정한다",
    "Automatic control skips: 제어하지 않아도 되는 부분을 찾는다": "automatic-control-skips-제어하지-않아도-되는-부분을-찾는다",
    "3. AshN은 아래쪽에서 ‘이동과 계산’을 합친다": "ashn은-아래쪽에서-이동과-계산을-합친다",
    "실제 QPU에서 확인된 숫자": "실제-qpu에서-확인된-숫자",
    "어디에서 잘 안 듣는가": "어디에서-잘-안-듣는가",
    "흡수 기회를 정하는 회로 구조": "어디에서-잘-안-듣는가",
    "4. 두 대표 사례는 왜 닮았고, 어디가 다른가": "두-대표-사례는-왜-닮았고-어디가-다른가",
    "5. 발전 방향: 개별 최적화에서 교차 계층 공동 최적화로": "발전-방향-개별-최적화에서-교차-계층-공동-최적화로",
    "6. QAOA·양자화학·재료 계산에서 어떻게 시험할까": "qaoa양자화학재료-계산에서-어떻게-시험할까",
    "7. 무엇이 입증됐고 무엇이 남았나": "무엇이-입증됐고-무엇이-남았나",
    "7. 최적화의 효과는 다음 층에서 다시 평가된다": "무엇이-입증됐고-무엇이-남았나",
    "결론: 최적화는 연결된 설계 문제다": "결론",
    "참고문헌": "references",
}


def normalized_text(value):
    return " ".join(html.unescape(re.sub(r"<[^>]*>", "", value)).split()).replace("’", "'").replace("‘", "'")


def preserve_heading_links(rendered):
    lookup = {normalized_text(key): value for key, value in LEGACY_IDS.items()}
    present = set(re.findall(r'\bid="([^"]+)"', rendered))

    def alias(match):
        legacy = lookup.get(normalized_text(match.group(3)))
        if not legacy or legacy in present:
            return match.group(0)
        present.add(legacy)
        return f'<span class="legacy-anchor" id="{legacy}" aria-hidden="true"></span>' + match.group(0)

    return re.sub(r'<h([23]) id="([^"]+)">(.*?)</h\1>', alias, rendered, flags=re.S)


def main():
    source = ROOT / TOPIC / "reports" / f"{TOPIC}_final_review.md"
    manuscript = source.read_text()
    metadata, body = strip_frontmatter(manuscript)
    revision = metadata_value(metadata, "date modified")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", revision):
        raise ValueError("Expected an ISO date modified in the source manuscript")
    body, count = re.subn(r"^# [^\n]+\n", "", body, count=1)
    if count != 1:
        raise ValueError("Expected the manuscript H1")
    # Preserve old flat image references as well as future source-relative refs.
    for asset in ASSETS.iterdir():
        body = body.replace(f"]({asset.name})", f"](../artifacts/final_review/figures/{asset.name})")
    hero = re.search(r"!\[([^\]]+)\]\(([^)]+)\)\s*\n\s*\*([^\n]+)\*", body)
    if not hero:
        raise ValueError("Expected the existing hero and caption")
    hero_path = (source.parent / hero.group(2)).resolve()
    body = body[:hero.start()] + body[hero.end():]
    rendered, _ = build_markdown_html(body)
    rendered = preserve_heading_links(rendered)
    rendered = re.sub(r"(?s)(\$\$.*?\$\$)", r'<div class="equation-scroll" tabindex="0" role="region" aria-label="수식 좌우로 보기">\1</div>', rendered)
    rendered = rendered.replace("<p>", '<p class="lead">', 1)
    rendered = re.sub(r"<p>(<img\b[^>]+>)</p>", r'<figure class="figure-panel">\1</figure>', rendered)
    rendered = re.sub(r"<p><em>(그림 [23]\..*?)</em></p>", r'<p class="figure-caption">\1</p>', rendered, flags=re.S)
    rendered = rendered.replace("<table>", '<div class="table-wrap" tabindex="0" role="region" aria-label="회로 최적화와 평가 조건 비교"><table>').replace("</table>", "</table></div>")
    dist = ROOT / TOPIC / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    public_body, _, missing, _ = build_flat_refs(rendered, source.parent, dist)
    if missing:
        raise ValueError(f"Missing manuscript assets: {missing}")
    for asset in ASSETS.iterdir():
        if asset.is_file():
            shutil.copy2(asset, dist / asset.name)
    shutil.copy2(hero_path, dist / hero_path.name)

    def version_svg(match):
        digest = hashlib.sha256((dist / match.group(2)).read_bytes()).hexdigest()[:12]
        return f'{match.group(1)}{match.group(2)}?v={digest}{match.group(3)}'

    public_body = re.sub(r'(\bsrc=")([^"?]+\.svg)(")', version_svg, public_body)
    figure_number = 1

    def add_figure_link(match):
        nonlocal figure_number
        figure_number += 1
        path = Path(html.unescape(match.group(2)).split("?", 1)[0])
        svg = dist / path.with_suffix(".svg")
        if path.suffix == ".png" and svg.exists():
            digest = hashlib.sha256(svg.read_bytes()).hexdigest()[:12]
            url = f"{svg.name}?v={digest}"
        else:
            url = html.unescape(match.group(2))
        href = html.escape(url, quote=True)
        return (match.group(1) + match.group(3)
                + f'<br><a class="figure-open" href="{href}" target="_blank" rel="noopener" aria-label="그림 {figure_number} 크게 보기 (새 탭)">그림 크게 보기 ↗</a>'
                + match.group(4))

    public_body = re.sub(r'(<figure class="figure-panel"><img\b[^>]*src="([^"]+)"[^>]*></figure>\s*<p class="figure-caption">)(.*?)(</p>)', add_figure_link, public_body, flags=re.S)
    template = Path(__file__).with_name("layout.html").read_text()
    if template.count("<!-- ARTICLE_BODY -->") != 1:
        raise ValueError("Expected exactly one article slot")
    template = template.replace("<!-- REVISION_DATE -->", revision)
    template = re.sub(r'(<figure class="hero-figure"><img\b[^>]*\balt=")[^"]*', lambda m:m.group(1)+html.escape(hero.group(1),quote=True), template)
    template = re.sub(r'(<figure class="hero-figure">.*?<figcaption>).*?(</figcaption>)', lambda m:m.group(1)+html.escape(hero.group(3))+m.group(2), template, flags=re.S)
    output = template.replace("<!-- ARTICLE_BODY -->", public_body)
    output = "\n".join(line.rstrip() for line in output.splitlines()) + "\n"
    source.with_suffix(".html").write_text(output)
    (dist / "index.html").write_text(output)
    flat_source = manuscript
    for asset in ASSETS.iterdir():
        flat_source = flat_source.replace("../artifacts/final_review/figures/"+asset.name, asset.name)
    (dist / source.name).write_text(flat_source)
    print(f"Rendered complete manuscript: {TOPIC}")


if __name__ == "__main__":
    main()
