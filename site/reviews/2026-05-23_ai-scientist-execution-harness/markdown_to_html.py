from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import markdown


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
HEADING_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
SECTION_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
BARE_URL_RE = re.compile(r"(?<!\()https?://[^\s<>)]+")


@dataclass
class LinkItem:
    label: str
    href: str
    external: bool


@dataclass
class RenderContext:
    title: str
    subtitle: str
    issue_label: str
    source_path: Path
    output_path: Path
    mode: str
    body_html: str
    toc_html: str
    summary_points: list[str]
    links: list[LinkItem]
    section_count: int
    generated_at: str
    source_modified_at: str


def strip_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    metadata: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        metadata[key.strip().lower()] = value.strip()
    return metadata, text[match.end() :]


def split_title(markdown_text: str, default_title: str) -> tuple[str, str]:
    match = HEADING_RE.search(markdown_text)
    if not match:
        return default_title, markdown_text.lstrip()

    title = match.group(1).strip()
    body = markdown_text[: match.start()] + markdown_text[match.end() :]
    return title, body.lstrip()


def extract_summary_points(markdown_text: str) -> list[str]:
    lines = markdown_text.splitlines()
    in_summary = False
    points: list[str] = []
    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()
        if re.match(r"^##\s+summary\s*$", stripped, re.IGNORECASE):
            in_summary = True
            continue
        if in_summary and stripped.startswith("#"):
            break
        if in_summary and line.startswith("- "):
            points.append(line[2:].strip())
        if len(points) == 4:
            break
    return points


def build_issue_label(metadata: dict[str, str]) -> str:
    raw_date = metadata.get("issue date") or metadata.get("date modified") or metadata.get("date") or metadata.get("date created")
    try:
        issue_date = datetime.fromisoformat(raw_date).date() if raw_date else datetime.now().date()
    except ValueError:
        issue_date = datetime.now().date()
    week = issue_date.isocalendar().week
    return f"AI Tech Review Letters: Week {week:02d} ({issue_date.isoformat()})"


def extract_links(markdown_text: str) -> list[LinkItem]:
    seen: set[str] = set()
    items: list[LinkItem] = []

    def add_item(label: str, href: str) -> None:
        normalized = href.strip()
        if not normalized or normalized in seen:
            return
        seen.add(normalized)
        parsed = urlparse(normalized)
        external = parsed.scheme in {"http", "https"}
        final_label = label.strip() or normalized
        if not external and not Path(normalized).suffix:
            final_label = final_label
        items.append(LinkItem(label=final_label, href=normalized, external=external))

    for match in MARKDOWN_LINK_RE.finditer(markdown_text):
        add_item(match.group(1), match.group(2))

    for match in BARE_URL_RE.finditer(markdown_text):
        url = match.group(0)
        parsed = urlparse(url)
        label = parsed.netloc or url
        add_item(label, url)

    return items


CUSTOM_BLOCK_LABELS = {
    "highlight": "Highlight",
    "think": "생각하기",
    "thinking": "생각하기",
    "evidence": "Evidence note",
    "operator": "Operator note",
    "pose": "Pose",
    "bundle": "글묶음",
}


def preprocess_custom_blocks(markdown_text: str) -> str:
    """Convert lightweight article directives into markdown-in-html blocks."""
    lines = markdown_text.splitlines()
    output: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        match = re.match(r"^:::\s*([a-zA-Z_-]+)(?:\s+(.*?))?\s*$", line)
        if not match:
            output.append(line)
            index += 1
            continue

        block_name = match.group(1).strip().lower()
        if block_name not in CUSTOM_BLOCK_LABELS:
            output.append(line)
            index += 1
            continue

        title = (match.group(2) or CUSTOM_BLOCK_LABELS[block_name]).strip()
        block_lines: list[str] = []
        index += 1
        while index < len(lines) and lines[index].strip() != ":::":
            block_lines.append(lines[index])
            index += 1
        if index < len(lines) and lines[index].strip() == ":::":
            index += 1

        safe_title = html.escape(title, quote=True)
        safe_block_name = re.sub(r"[^a-z0-9_-]+", "-", block_name)
        output.extend(
            [
                f'<aside class="callout callout-{safe_block_name}" markdown="1">',
                f'<p class="callout-label">{safe_title}</p>',
                "",
                *block_lines,
                "",
                "</aside>",
            ]
        )

    return "\n".join(output)


def build_markdown_html(markdown_text: str) -> tuple[str, str]:
    renderer = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists", "smarty", "md_in_html"],
        extension_configs={
            "toc": {
                "permalink": False,
                "title": "",
            }
        },
    )
    body_html = renderer.convert(preprocess_custom_blocks(markdown_text))
    toc_html = renderer.toc or ""
    return body_html, toc_html


def format_timestamp(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def source_link_href(source_path: Path, output_path: Path) -> str:
    try:
        return source_path.relative_to(output_path.parent).as_posix()
    except ValueError:
        return source_path.name


def render_link_items(links: list[LinkItem]) -> str:
    if not links:
        return '<li class="empty-state">이 리포트에서 명시적 링크가 감지되지 않았습니다.</li>'

    rendered: list[str] = []
    for item in links:
        target_attr = ' target="_blank" rel="noreferrer"' if item.external else ""
        rendered.append(
            f'<li><a href="{html.escape(item.href, quote=True)}"{target_attr}>'
            f"{html.escape(item.label)}</a></li>"
        )
    return "\n".join(rendered)


def render_template(context: RenderContext) -> str:
    if context.mode == "final-review":
        return render_final_review_template(context)

    summary_html = ""
    if context.summary_points:
        items = "\n".join(
            f"<li>{html.escape(point)}</li>" for point in context.summary_points
        )
        summary_html = f"""
        <section class="summary-band" aria-labelledby="summary-heading">
          <h2 id="summary-heading">주요 신호</h2>
          <ul class="summary-list">
            {items}
          </ul>
        </section>
        """

    toc_panel = ""
    if context.toc_html.strip():
        toc_panel = f"""
        <section class="panel toc-panel" aria-labelledby="toc-heading">
          <h2 id="toc-heading">섹션 맵</h2>
          {context.toc_html}
        </section>
        """

    link_items = render_link_items(context.links)

    source_href = source_link_href(context.source_path, context.output_path)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(context.title)}</title>
  <link rel="icon" href="data:,">
  <meta name="color-scheme" content="light">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%230f766e'/%3E%3Cpath d='M18 22h28v6H18zm0 14h20v6H18z' fill='%23ffffff'/%3E%3C/svg%3E">
  <style>
    :root {{
      --bg: #edf2f0;
      --surface: #ffffff;
      --surface-alt: #f6f8f7;
      --ink: #14201a;
      --muted: #52615a;
      --line: #d9e1dd;
      --accent: #0f766e;
      --accent-alt: #3f6212;
      --accent-warm: #c2410c;
      --shadow: 0 18px 40px rgba(20, 32, 26, 0.08);
      --radius: 8px;
      --wrap: 1220px;
    }}

    * {{
      box-sizing: border-box;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      font-family: "Segoe UI", "Noto Sans KR", Arial, sans-serif;
      color: var(--ink);
      background: linear-gradient(180deg, #f4f7f5 0%, var(--bg) 100%);
    }}

    a {{
      color: var(--accent);
      text-decoration: none;
    }}

    a:hover {{
      text-decoration: underline;
    }}

    .page {{
      width: min(var(--wrap), calc(100% - 32px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }}

    .masthead {{
      display: grid;
      grid-template-columns: minmax(0, 1.3fr) minmax(280px, 0.7fr);
      gap: 24px;
      align-items: start;
      margin-bottom: 24px;
    }}

    .headline {{
      padding: 28px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}

    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      margin: 0 0 18px;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid rgba(15, 118, 110, 0.18);
      background: rgba(15, 118, 110, 0.08);
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--accent);
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      font-size: 2.7rem;
      line-height: 1.02;
      font-weight: 800;
    }}

    .deck {{
      margin: 16px 0 0;
      max-width: 70ch;
      font-size: 1rem;
      line-height: 1.75;
      color: var(--muted);
    }}

    .meta-list {{
      margin: 24px 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}

    .meta-list li {{
      padding: 14px 16px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--surface-alt);
    }}

    .meta-list strong {{
      display: block;
      margin-bottom: 6px;
      font-size: 0.76rem;
      text-transform: uppercase;
      color: var(--accent-alt);
    }}

    .meta-list span {{
      display: block;
      font-size: 0.95rem;
      line-height: 1.5;
      word-break: break-word;
    }}

    .summary-band {{
      padding: 24px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: linear-gradient(180deg, #f8fbfa 0%, #eef4f1 100%);
      box-shadow: var(--shadow);
    }}

    .summary-band h2,
    .panel h2 {{
      margin: 0 0 14px;
      font-size: 1rem;
      line-height: 1.3;
      font-weight: 800;
      text-transform: uppercase;
      color: var(--accent-alt);
    }}

    .summary-list {{
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 10px;
      line-height: 1.65;
    }}

    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 320px;
      gap: 24px;
      align-items: start;
    }}

    .report {{
      padding: 32px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
    }}

    .report > :first-child {{
      margin-top: 0;
    }}

    .report h2 {{
      margin: 38px 0 14px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      font-size: 1.5rem;
      line-height: 1.2;
    }}

    .report h3 {{
      margin: 24px 0 12px;
      font-size: 1.1rem;
      line-height: 1.35;
    }}

    .report p,
    .report li {{
      font-size: 1rem;
      line-height: 1.8;
      color: var(--ink);
    }}

    .report ul,
    .report ol {{
      margin: 0 0 18px;
      padding-left: 22px;
    }}

    .report li + li {{
      margin-top: 8px;
    }}

    .report strong {{
      color: var(--ink);
    }}

    .report blockquote {{
      margin: 20px 0;
      padding: 16px 18px;
      border-left: 4px solid var(--accent);
      background: #f5f9f8;
      color: var(--muted);
    }}

    .report code {{
      padding: 2px 6px;
      border-radius: 6px;
      background: #eef4f1;
      font-family: "Cascadia Code", Consolas, monospace;
      font-size: 0.92rem;
    }}

    .report pre {{
      margin: 18px 0;
      padding: 16px;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #f3f7f5;
    }}

    .report pre code {{
      padding: 0;
      background: transparent;
    }}

    .report table {{
      width: 100%;
      border-collapse: collapse;
      margin: 18px 0;
      display: block;
      overflow-x: auto;
    }}

    .report th,
    .report td {{
      padding: 12px 14px;
      border: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      min-width: 140px;
    }}

    .report th {{
      background: #f4f8f6;
      color: var(--accent-alt);
      font-weight: 700;
    }}

    .sidebar {{
      position: sticky;
      top: 24px;
      display: grid;
      gap: 16px;
    }}

    .panel {{
      padding: 18px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }}

    .toc-panel ul,
    .link-panel ul {{
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 8px;
      line-height: 1.55;
    }}

    .toc-panel li,
    .link-panel li {{
      color: var(--muted);
    }}

    .link-panel a {{
      display: inline-block;
      word-break: break-word;
    }}

    .empty-state {{
      list-style: none;
      margin-left: -18px;
      color: var(--muted);
    }}

    .footer {{
      margin-top: 20px;
      padding: 14px 0 0;
      color: var(--muted);
      font-size: 0.9rem;
      border-top: 1px solid var(--line);
    }}

    @media (max-width: 1080px) {{
      .masthead,
      .layout {{
        grid-template-columns: 1fr;
      }}

      .sidebar {{
        position: static;
      }}
    }}

    @media (max-width: 720px) {{
      .page {{
        width: min(var(--wrap), calc(100% - 20px));
        padding-top: 14px;
      }}

      .headline,
      .summary-band,
      .report,
      .panel {{
        padding: 20px;
      }}

      h1 {{
        font-size: 2rem;
      }}

      .meta-list {{
        grid-template-columns: 1fr;
      }}

      .report h2 {{
        font-size: 1.28rem;
      }}
    }}

    @media print {{
      body {{
        background: #ffffff;
      }}

      .page {{
        width: 100%;
        padding: 0;
      }}

      .headline,
      .summary-band,
      .report,
      .panel {{
        box-shadow: none;
      }}

      .layout {{
        grid-template-columns: 1fr;
      }}

      .sidebar {{
        position: static;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <header class="masthead">
      <section class="headline">
        <p class="eyebrow">데일리 리뷰 시그널 브리프</p>
        <h1>{html.escape(context.title)}</h1>
        <p class="deck">시장 관점의 리뷰 노트, 신호 클러스터링, 그리고 워크스페이스 증거 링크를 빠르게 읽고 후속 리서치로 연결할 수 있도록 정리한 웹 리포트입니다.</p>
        <ul class="meta-list">
          <li>
            <strong>생성 시각</strong>
            <span>{html.escape(context.generated_at)}</span>
          </li>
          <li>
            <strong>섹션 수</strong>
            <span>{context.section_count}</span>
          </li>
          <li>
            <strong>원본 마크다운</strong>
            <span><a href="{html.escape(source_href, quote=True)}">{html.escape(context.source_path.name)}</a></span>
          </li>
        </ul>
      </section>
      {summary_html}
    </header>

    <main class="layout">
      <article class="report">
        {context.body_html}
        <div class="footer">
          원본 파일 최종 수정 시각: {html.escape(context.source_modified_at)}
        </div>
      </article>

      <aside class="sidebar">
        {toc_panel}
        <section class="panel link-panel" aria-labelledby="links-heading">
          <h2 id="links-heading">연결된 근거</h2>
          <ul>
            {link_items}
          </ul>
        </section>
      </aside>
    </main>
  </div>
</body>
</html>
"""


def render_final_review_template(context: RenderContext) -> str:
    summary_html = ""
    if context.summary_points:
        items = "\n".join(
            f"<li>{html.escape(point)}</li>" for point in context.summary_points[:5]
        )
        summary_html = f"""
        <section class="hero-signals" aria-labelledby="signals-heading">
          <h2 id="signals-heading">읽기 전에 볼 신호</h2>
          <ul>
            {items}
          </ul>
        </section>
        """

    toc_panel = ""
    if context.toc_html.strip():
        toc_panel = f"""
        <section class="side-section toc-panel" aria-labelledby="toc-heading">
          <h2 id="toc-heading">섹션 맵</h2>
          {context.toc_html}
        </section>
        """

    link_items = render_link_items(context.links)
    source_href = source_link_href(context.source_path, context.output_path)
    dek_html = ""
    if context.subtitle:
        dek_html = f'<p class="dek">{html.escape(context.subtitle)}</p>'

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(context.title)}</title>
  <link rel="icon" href="data:,">
  <meta name="color-scheme" content="light">
  <style>
    :root {{
      --paper: #fbfaf7;
      --paper-soft: #f2f0ea;
      --ink: #17211d;
      --muted: #5f6b65;
      --line: #d8d5cb;
      --teal: #0f766e;
      --blue: #25456f;
      --amber: #a35a16;
      --rose: #8b3a3a;
      --green-soft: #e9f3ef;
      --blue-soft: #e9eef5;
      --amber-soft: #f6eee2;
      --rose-soft: #f5eaea;
      --wrap: 1180px;
      --article: 780px;
      --radius: 8px;
    }}

    * {{
      box-sizing: border-box;
    }}

    html {{
      scroll-behavior: smooth;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background: var(--paper);
      font-family: "Segoe UI", "Noto Sans KR", Arial, sans-serif;
      text-rendering: optimizeLegibility;
    }}

    a {{
      color: var(--teal);
      text-decoration-thickness: 1px;
      text-underline-offset: 3px;
    }}

    .topline {{
      border-bottom: 1px solid var(--line);
      background: #ffffff;
    }}

    .topline-inner,
    .hero-inner,
    .content-grid {{
      width: min(var(--wrap), calc(100% - 40px));
      margin: 0 auto;
    }}

    .topline-inner {{
      display: flex;
      justify-content: space-between;
      gap: 20px;
      padding: 14px 0;
      color: var(--muted);
      font-size: 0.92rem;
    }}

    .topline a {{
      color: var(--blue);
      font-weight: 650;
      text-decoration: none;
    }}

    .hero {{
      border-bottom: 1px solid var(--line);
      background:
        linear-gradient(90deg, rgba(15, 118, 110, 0.10), transparent 46%),
        linear-gradient(180deg, #ffffff 0%, var(--paper) 100%);
    }}

    .hero-inner {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 360px;
      gap: 40px;
      align-items: end;
      padding: 46px 0 34px;
    }}

    .eyebrow {{
      margin: 0 0 18px;
      color: var(--teal);
      font-weight: 760;
      letter-spacing: 0;
      text-transform: uppercase;
      font-size: 0.82rem;
    }}

    h1 {{
      margin: 0;
      max-width: 900px;
      color: var(--ink);
      font-size: clamp(2.2rem, 5vw, 4.2rem);
      line-height: 1.02;
      letter-spacing: 0;
      font-weight: 820;
      word-break: keep-all;
      overflow-wrap: normal;
    }}

    .dek {{
      margin: 22px 0 0;
      max-width: 760px;
      color: var(--muted);
      font-size: 1.08rem;
      line-height: 1.75;
      word-break: keep-all;
    }}

    .hero-signals {{
      padding: 18px 20px;
      border-top: 4px solid var(--teal);
      background: rgba(255, 255, 255, 0.82);
    }}

    .hero-signals h2,
    .side-section h2 {{
      margin: 0 0 12px;
      color: var(--blue);
      font-size: 0.88rem;
      line-height: 1.3;
      letter-spacing: 0;
      text-transform: uppercase;
    }}

    .hero-signals ul,
    .side-section ul {{
      margin: 0;
      padding-left: 18px;
      display: grid;
      gap: 9px;
      color: var(--muted);
      line-height: 1.62;
    }}

    .content-grid {{
      display: grid;
      grid-template-columns: minmax(0, var(--article)) minmax(260px, 310px);
      gap: 52px;
      align-items: start;
      padding: 38px 0 56px;
    }}

    .final-article {{
      min-width: 0;
      overflow-wrap: break-word;
    }}

    .final-article > :first-child {{
      margin-top: 0;
    }}

    .final-article h2 {{
      margin: 46px 0 16px;
      padding-top: 22px;
      border-top: 1px solid var(--line);
      color: var(--ink);
      font-size: 1.72rem;
      line-height: 1.25;
      letter-spacing: 0;
      word-break: keep-all;
    }}

    .final-article h3 {{
      margin: 30px 0 12px;
      color: var(--blue);
      font-size: 1.18rem;
      line-height: 1.35;
      letter-spacing: 0;
    }}

    .final-article p,
    .final-article li {{
      color: var(--ink);
      font-size: 1.02rem;
      line-height: 1.86;
    }}

    .final-article p {{
      margin: 0 0 18px;
    }}

    .final-article ul,
    .final-article ol {{
      margin: 0 0 22px;
      padding-left: 24px;
    }}

    .final-article li + li {{
      margin-top: 8px;
    }}

    .final-article blockquote {{
      margin: 28px 0;
      padding: 4px 0 4px 22px;
      border-left: 4px solid var(--amber);
      color: var(--ink);
      font-size: 1.12rem;
    }}

    .final-article blockquote p {{
      color: var(--ink);
      font-size: 1.12rem;
      line-height: 1.75;
    }}

    .final-article code {{
      padding: 2px 6px;
      border-radius: 6px;
      background: #ebe7de;
      font-family: "Cascadia Code", Consolas, monospace;
      font-size: 0.92em;
    }}

    .final-article pre {{
      margin: 22px 0;
      padding: 18px;
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #f0ede6;
    }}

    .final-article pre code {{
      padding: 0;
      background: transparent;
    }}

    .final-article img,
    .final-article svg,
    .final-article video,
    .final-article canvas,
    .final-article iframe {{
      display: block;
      max-width: 100%;
      height: auto;
    }}

    .article-hero-figure {{
      margin: 0 0 34px;
    }}

    .article-hero-figure img {{
      width: 100%;
      border: 1px solid var(--line);
      background: #ffffff;
    }}

    .article-hero-figure figcaption {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.55;
      word-break: keep-all;
    }}

    .final-article p:has(> img) {{
      margin: 30px 0;
    }}

    .final-article table {{
      display: block;
      width: 100%;
      margin: 24px 0;
      overflow-x: auto;
      border-collapse: collapse;
      font-size: 0.96rem;
    }}

    .final-article th,
    .final-article td {{
      min-width: 140px;
      padding: 12px 14px;
      border: 1px solid var(--line);
      vertical-align: top;
      text-align: left;
      line-height: 1.58;
    }}

    .final-article th {{
      background: var(--paper-soft);
      color: var(--blue);
      font-weight: 760;
    }}

    .final-article .footnote-ref {{
      font-size: 0.78em;
      line-height: 0;
    }}

    .final-article .footnote,
    .final-article .footnotes {{
      margin: 44px 0 28px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
    }}

    .final-article .footnote::before,
    .final-article .footnotes::before {{
      content: "용어 풀이";
      display: block;
      margin-bottom: 12px;
      color: var(--blue);
      font-size: 0.88rem;
      font-weight: 760;
      letter-spacing: 0;
      text-transform: uppercase;
    }}

    .final-article .footnote ol,
    .final-article .footnotes ol {{
      margin-bottom: 0;
      padding-left: 22px;
    }}

    .final-article .footnote li,
    .final-article .footnote p,
    .final-article .footnotes li,
    .final-article .footnotes p {{
      color: var(--muted);
      font-size: 0.94rem;
      line-height: 1.72;
    }}

    .callout {{
      margin: 26px 0;
      padding: 18px 20px;
      border-left: 4px solid var(--teal);
      background: var(--green-soft);
    }}

    .callout-label {{
      margin: 0 0 8px !important;
      color: var(--teal) !important;
      font-size: 0.84rem !important;
      font-weight: 780;
      line-height: 1.3 !important;
      text-transform: uppercase;
    }}

    .callout-think,
    .callout-thinking {{
      border-left-color: var(--amber);
      background: var(--amber-soft);
    }}

    .callout-think .callout-label,
    .callout-thinking .callout-label {{
      color: var(--amber) !important;
    }}

    .callout-evidence {{
      border-left-color: var(--blue);
      background: var(--blue-soft);
    }}

    .callout-evidence .callout-label {{
      color: var(--blue) !important;
    }}

    .callout-operator {{
      border-left-color: var(--rose);
      background: var(--rose-soft);
    }}

    .callout-operator .callout-label {{
      color: var(--rose) !important;
    }}

    .figure-panel,
    .data-panel {{
      margin: 30px 0;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: #ffffff;
      overflow-x: auto;
    }}

    .figure-panel figcaption,
    .data-panel figcaption {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.55;
    }}

    @media (max-width: 760px) {{
      .figure-panel img[src$=".svg"],
      .data-panel img[src$=".svg"] {{
        width: 680px;
        max-width: none;
      }}
    }}

    .story-flow {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin: 20px 0;
    }}

    .story-flow > * {{
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: var(--radius);
      background: var(--paper-soft);
      color: var(--ink);
      line-height: 1.5;
    }}

    .sidebar {{
      position: sticky;
      top: 24px;
      display: grid;
      gap: 22px;
      min-width: 0;
    }}

    .side-section {{
      padding: 0 0 22px;
      border-bottom: 1px solid var(--line);
    }}

    .toc-panel a,
    .link-panel a {{
      color: var(--muted);
      text-decoration: none;
      word-break: break-word;
    }}

    .toc-panel a:hover,
    .link-panel a:hover {{
      color: var(--teal);
      text-decoration: underline;
    }}

    .footer {{
      margin-top: 42px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.6;
    }}

    @media (max-width: 1120px) {{
      .hero-inner,
      .content-grid {{
        grid-template-columns: 1fr;
      }}

      .sidebar {{
        position: static;
      }}
    }}

    @media (max-width: 680px) {{
      .topline-inner,
      .hero-inner,
      .content-grid {{
        width: min(var(--wrap), calc(100% - 24px));
      }}

      .topline-inner {{
        display: grid;
      }}

      .hero-inner {{
        padding: 34px 0 28px;
      }}

      .final-article h2 {{
        font-size: 1.42rem;
      }}
    }}

    @media print {{
      body {{
        background: #ffffff;
      }}

      .hero {{
        background: #ffffff;
      }}

      .content-grid {{
        grid-template-columns: 1fr;
      }}

      .sidebar {{
        position: static;
      }}
    }}
  </style>
</head>
<body>
  <div class="topline">
    <div class="topline-inner">
      <span>{html.escape(context.issue_label)}</span>
      <span><a href="{html.escape(source_href, quote=True)}">{html.escape(context.source_path.name)}</a></span>
    </div>
  </div>

  <header class="hero">
    <div class="hero-inner">
      <section>
        <p class="eyebrow">AI Tech Review Letters</p>
        <h1>{html.escape(context.title)}</h1>
        {dek_html}
      </section>
      {summary_html}
    </div>
  </header>

  <main class="content-grid">
    <article class="final-article">
      {context.body_html}
      <div class="footer">
        생성 시각: {html.escape(context.generated_at)}<br>
        원본 파일 최종 수정 시각: {html.escape(context.source_modified_at)}
      </div>
    </article>

    <aside class="sidebar">
      {toc_panel}
      <section class="side-section link-panel" aria-labelledby="links-heading">
        <h2 id="links-heading">근거 링크</h2>
        <ul>
          {link_items}
        </ul>
      </section>
    </aside>
  </main>
</body>
</html>
"""


def resolve_mode(source_path: Path, requested_mode: str) -> str:
    if requested_mode != "auto":
        return requested_mode
    if source_path.stem.endswith("_final_review"):
        return "final-review"
    return "default"


def build_context(source_path: Path, mode: str = "auto") -> RenderContext:
    raw_text = source_path.read_text(encoding="utf-8")
    metadata, markdown_text = strip_frontmatter(raw_text)
    title, body_markdown = split_title(markdown_text, metadata.get("title", source_path.stem))
    subtitle = metadata.get("description") or metadata.get("subtitle") or ""
    body_html, toc_html = build_markdown_html(body_markdown)
    source_stat = source_path.stat()
    generated_at = format_timestamp(datetime.now().astimezone())
    source_modified_at = format_timestamp(datetime.fromtimestamp(source_stat.st_mtime).astimezone())
    section_count = len(SECTION_RE.findall(body_markdown))
    resolved_mode = resolve_mode(source_path, mode)
    return RenderContext(
        title=title,
        subtitle=subtitle,
        issue_label=build_issue_label(metadata),
        source_path=source_path,
        output_path=source_path.with_suffix(".html"),
        mode=resolved_mode,
        body_html=body_html,
        toc_html=toc_html,
        summary_points=extract_summary_points(markdown_text),
        links=extract_links(markdown_text),
        section_count=section_count,
        generated_at=generated_at,
        source_modified_at=source_modified_at,
    )


def render_file(source_path: Path, mode: str = "auto") -> Path:
    context = build_context(source_path, mode)
    html_text = render_template(context)
    context.output_path.write_text(html_text, encoding="utf-8")
    return context.output_path


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render one or more markdown reports into polished standalone HTML pages."
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "default", "final-review"],
        default="auto",
        help="Rendering mode. Auto uses final-review mode for *_final_review.md.",
    )
    parser.add_argument("paths", nargs="+", help="Markdown files to render.")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    exit_code = 0
    for raw_path in args.paths:
        path = Path(raw_path).resolve()
        if not path.exists():
            print(f"[missing] {path}")
            exit_code = 1
            continue
        if path.suffix.lower() != ".md":
            print(f"[skip] {path} is not a markdown file")
            exit_code = 1
            continue
        output_path = render_file(path, args.mode)
        print(f"[rendered:{resolve_mode(path, args.mode)}] {path} -> {output_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
