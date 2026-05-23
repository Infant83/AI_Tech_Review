from __future__ import annotations

import html
import json
import re
import shutil
import stat
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
REVIEWS_DIR = SITE_DIR / "reviews"
ASSETS_DIR = SITE_DIR / "assets"


@dataclass(frozen=True)
class PublicReview:
    folder: str
    title: str
    subtitle: str
    date: str
    updated: str
    category: str
    tags: tuple[str, ...]
    summary: str

    @property
    def dist_index(self) -> Path:
        return ROOT / self.folder / "dist" / "index.html"

    @property
    def public_dir(self) -> Path:
        return REVIEWS_DIR / self.folder

    @property
    def href(self) -> str:
        return f"reviews/{self.folder}/index.html"


REVIEWS: tuple[PublicReview, ...] = (
    PublicReview(
        folder="2026-05-23_ai-scientist-execution-harness",
        title="AI 과학자는 어떻게 우리 곁에 오는가",
        subtitle="에르되시 문제 #1196에서 AI Co-Scientist까지, 발견의 속도와 실행 환경을 함께 읽는 리뷰",
        date="2026-05-23",
        updated="2026-05-23",
        category="AI for Science",
        tags=("AI for Science", "AI Scientist", "AI Co-Scientist", "AlphaEvolve"),
        summary=(
            "수학 문제 풀이 소식에서 출발해 AI 과학자가 연구 동료, 조수, 검증 대상이 되는 조건을 "
            "과학 활동과 기업 실행 환경의 관점에서 정리합니다."
        ),
    ),
    PublicReview(
        folder="2026-05-07_tabpfn-oled-manufacturing-foundation-model",
        title="TabPFN: Foundation model for Tabular inference",
        subtitle="OLED 분자 계산, 공정, SCM, 검사 데이터에서 표 기반 Foundation 모델을 어떻게 읽을 것인가",
        date="2026-05-17",
        updated="2026-05-21",
        category="Materials AI",
        tags=("TabPFN", "OLED", "Materials Informatics", "Data Provenance"),
        summary=(
            "작은 표 데이터에서 빠른 기준 모델을 세우는 TabPFN의 장점과, OLED 연구·제조 데이터에 "
            "적용할 때 함께 보아야 할 계산 조건과 실험 provenance를 살펴봅니다."
        ),
    ),
    PublicReview(
        folder="2026-05-09_ai-updates-weekly",
        title="AI 에이전트를 일하게 하는 기술: 하네스 엔지니어링",
        subtitle="도구 호출, 권한, 기억, 검증, 병합이 에이전트 운영의 기본 조건이 되는 이유",
        date="2026-05-09",
        updated="2026-05-13",
        category="Agent Systems",
        tags=("AI Agents", "Harness Engineering", "Developer Tools", "Governance"),
        summary=(
            "모델 성능만으로는 설명하기 어려운 에이전트 운영 문제를 권한, 메모리, 검증, 승인, "
            "병합의 관점에서 따라갑니다."
        ),
    ),
    PublicReview(
        folder="2026-05-06_gpt-5-5-family-post-release-evaluation",
        title="GPT-5.5 기술동향 리포트",
        subtitle="긴 작업 수행 능력, Hallucination 평가, Claude Opus 4.7 비교, 안전한 활용 조건",
        date="2026-05-10",
        updated="2026-05-10",
        category="Frontier Models",
        tags=("GPT-5.5", "Claude Opus", "Agentic AI", "Trust and Safety"),
        summary=(
            "GPT-5.5 계열 모델의 장시간 작업 수행 능력과 외부 평가를 함께 보며, 실제 업무에 "
            "맡길 수 있는 일의 조건을 점검합니다."
        ),
    ),
)


LOCAL_REF_RE = re.compile(
    r"(?P<prefix>\b(?:src|href)=['\"])(?P<url>[^'\"]+)(?P<suffix>['\"])",
    re.IGNORECASE,
)
LOCAL_HREF_RE = re.compile(r"\s+href=(?P<quote>['\"])(?P<url>[^'\"]+)(?P=quote)", re.IGNORECASE)
INTERNAL_PATH_RE = re.compile(r"(?:file:///[A-Za-z]:[\\/][^<>'\"\s]+|(?<![A-Za-z0-9])[A-Za-z]:[\\/][^<>'\"\s]+)")


class FirstImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.first_image: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.first_image or tag.lower() != "img":
            return
        attr_map = {name.lower(): value for name, value in attrs}
        src = attr_map.get("src")
        if src:
            self.first_image = src


def is_external_or_anchor(url: str) -> bool:
    stripped = url.strip()
    if not stripped or stripped.startswith("#"):
        return True
    parts = urlsplit(stripped)
    return bool(parts.scheme or parts.netloc) or stripped.startswith(("data:", "mailto:", "tel:", "javascript:"))


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
    index = 2
    while True:
        candidate = f"{source_path.stem}_{index}{source_path.suffix}"
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
        index += 1


def remove_tree(path: Path) -> None:
    if not path.exists():
        return
    for item in path.rglob("*"):
        try:
            item.chmod(stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            pass
    path.chmod(stat.S_IWRITE | stat.S_IREAD)
    shutil.rmtree(path)


def sanitize_for_public(html_text: str, dist_dir: Path, public_dir: Path) -> tuple[str, list[str]]:
    copied: list[str] = []
    source_to_dest: dict[Path, str] = {}
    used_names: set[str] = {"index.html"}
    allowed_asset_suffixes = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".css", ".js", ".ico"}

    def replace_ref(match: re.Match[str]) -> str:
        raw_url = match.group("url")
        if is_external_or_anchor(raw_url):
            return match.group(0)

        local_path, query, fragment = split_local_url(raw_url)
        if not local_path:
            return match.group(0)

        source_path = (dist_dir / local_path).resolve()
        suffix = source_path.suffix.lower()

        if match.group("prefix").lower().startswith("href") and suffix not in {".css", ".js", ".ico"}:
            safe_url = html.escape(raw_url, quote=True)
            return f"data-local-ref=\"{safe_url}\""

        if suffix not in allowed_asset_suffixes:
            safe_url = html.escape(raw_url, quote=True)
            return f"data-local-ref=\"{safe_url}\""

        if not source_path.exists() or not source_path.is_file():
            safe_url = html.escape(raw_url, quote=True)
            return f"data-missing-ref=\"{safe_url}\""

        if source_path not in source_to_dest:
            dest_name = unique_dest_name(source_path, used_names)
            source_to_dest[source_path] = dest_name
            shutil.copy2(source_path, public_dir / dest_name)
            copied.append(dest_name)

        new_url = rebuild_local_url(source_to_dest[source_path], query, fragment)
        return f"{match.group('prefix')}{html.escape(new_url, quote=True)}{match.group('suffix')}"

    sanitized = LOCAL_REF_RE.sub(replace_ref, html_text)
    sanitized = INTERNAL_PATH_RE.sub("[local path removed]", sanitized)
    sanitized = sanitized.replace("<body>", '<body class="public-review">')
    if "</body>" in sanitized:
        public_note = (
            "\n<section id=\"public-local-references\" class=\"public-note\">"
            "<p>공개 HTML에는 본문과 시각 자료, 외부 참고 링크만 포함했습니다. "
            "로컬 작업 메모와 자동화 파일 링크는 공개본에서 비활성화했습니다.</p>"
            "</section>\n"
        )
        sanitized = sanitized.replace("</body>", public_note + "</body>")
    return sanitized, copied


def publish_review(review: PublicReview) -> dict[str, object]:
    if not review.dist_index.exists():
        raise FileNotFoundError(f"Missing dist index for {review.folder}: {review.dist_index}")

    public_dir = review.public_dir
    if public_dir.exists():
        remove_tree(public_dir)
    public_dir.mkdir(parents=True, exist_ok=True)

    raw_html = review.dist_index.read_text(encoding="utf-8")
    public_html, copied_assets = sanitize_for_public(raw_html, review.dist_index.parent, public_dir)
    (public_dir / "index.html").write_text(public_html, encoding="utf-8")

    parser = FirstImageParser()
    parser.feed(public_html)
    thumbnail = f"reviews/{review.folder}/{parser.first_image}" if parser.first_image else ""

    return {
        "folder": review.folder,
        "title": review.title,
        "subtitle": review.subtitle,
        "date": review.date,
        "updated": review.updated,
        "category": review.category,
        "tags": list(review.tags),
        "summary": review.summary,
        "href": review.href,
        "thumbnail": thumbnail,
        "assets": copied_assets,
    }


def render_review_card(item: dict[str, object]) -> str:
    tags = "".join(f"<span>{html.escape(tag)}</span>" for tag in item["tags"])
    thumbnail = item.get("thumbnail") or ""
    image_html = (
        f'<img src="{html.escape(str(thumbnail), quote=True)}" alt="{html.escape(str(item["title"]), quote=True)} 대표 이미지" loading="lazy">'
        if thumbnail
        else '<div class="thumb-placeholder" aria-hidden="true"></div>'
    )
    return f"""
        <article class="review-card" data-category="{html.escape(str(item["category"]), quote=True)}" data-tags="{html.escape(" ".join(item["tags"]), quote=True)}" data-title="{html.escape(str(item["title"]), quote=True)}">
          <a class="thumb" href="{html.escape(str(item["href"]), quote=True)}">{image_html}</a>
          <div class="review-card-body">
            <p class="meta">{html.escape(str(item["category"]))} · {html.escape(str(item["updated"]))}</p>
            <h3><a href="{html.escape(str(item["href"]), quote=True)}">{html.escape(str(item["title"]))}</a></h3>
            <p class="subtitle">{html.escape(str(item["subtitle"]))}</p>
            <p>{html.escape(str(item["summary"]))}</p>
            <div class="tags">{tags}</div>
          </div>
        </article>
    """


def render_latest_update(item: dict[str, object]) -> str:
    tags = "".join(f"<span>{html.escape(tag)}</span>" for tag in item["tags"][:4])
    thumbnail = item.get("thumbnail") or ""
    image_html = (
        f'<img src="{html.escape(str(thumbnail), quote=True)}" alt="{html.escape(str(item["title"]), quote=True)} 대표 이미지" loading="eager">'
        if thumbnail
        else '<div class="thumb-placeholder" aria-hidden="true"></div>'
    )
    return f"""
      <section class="latest-update" aria-labelledby="latest-heading">
        <div class="latest-copy">
          <p class="section-kicker">Latest update</p>
          <h2 id="latest-heading">{html.escape(str(item["title"]))}</h2>
          <p class="latest-subtitle">{html.escape(str(item["subtitle"]))}</p>
          <p>{html.escape(str(item["summary"]))}</p>
          <div class="tags">{tags}</div>
          <a class="text-link" href="{html.escape(str(item["href"]), quote=True)}">최신 리뷰 읽기</a>
        </div>
        <a class="latest-media" href="{html.escape(str(item["href"]), quote=True)}">{image_html}</a>
      </section>
    """


def render_index(manifest: list[dict[str, object]]) -> str:
    updated = date.today().isoformat()
    categories = sorted({str(item["category"]) for item in manifest})
    category_options = "\n".join(f'<option value="{html.escape(category)}">{html.escape(category)}</option>' for category in categories)
    cards = "\n".join(render_review_card(item) for item in manifest)
    latest = render_latest_update(manifest[0]) if manifest else ""

    return f"""<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AI Tech Review Letters</title>
    <meta name="description" content="AI, 과학, 에이전트, 제조 데이터, 거버넌스 주제를 다루는 공개 기술 리뷰 허브">
    <link rel="stylesheet" href="assets/site.css">
  </head>
  <body>
    <header class="site-header">
      <nav class="topbar" aria-label="주요 링크">
        <a class="brand" href="index.html">AI Tech Review Letters</a>
        <span class="topbar-links">
          <a href="https://infant83.github.io/">Operator</a>
          <a href="manifest.json">Manifest</a>
        </span>
      </nav>
      <section class="hero">
        <p class="eyebrow">Public report hub · {updated}</p>
        <h1>Enlighten your AI Technology Insight.</h1>
        <p class="lead">AI for Science, frontier models, agent systems, materials AI를 원문 링크와 함께 다시 읽는 공개 리뷰 허브입니다.</p>
        <div class="stats" aria-label="허브 요약">
          <span><strong>{len(manifest)}</strong> 공개 리뷰</span>
          <span><strong>{len(categories)}</strong> 주제 묶음</span>
          <span><strong>김현중</strong> 운영</span>
          <span><strong>HTML</strong> 정적 배포</span>
        </div>
      </section>
    </header>

    <main>
      {latest}

      <section class="toolbar" aria-label="리뷰 찾기">
        <label>
          <span>검색</span>
          <input id="search" type="search" placeholder="AI scientist, TabPFN, agent..." autocomplete="off">
        </label>
        <label>
          <span>주제</span>
          <select id="category">
            <option value="">전체</option>
            {category_options}
          </select>
        </label>
      </section>

      <section class="review-grid" id="review-grid" aria-live="polite">
        {cards}
      </section>

      <section class="transparency-notice" aria-labelledby="transparency-heading">
        <div>
          <p class="section-kicker">AI Transparency and Source Notice</p>
          <h2 id="transparency-heading">투명성 및 출처 고지</h2>
          <p class="operator">사이트 운영자: <a href="https://infant83.github.io/">김현중</a></p>
        </div>
        <ul>
          <li>이 허브의 게시물은 Federlicht 기반 AI 보조 생성물이며, 최종 책임은 사용자/조직에 있습니다.</li>
          <li>외부 출처의 저작권/라이선스는 원 저작권자에게 있으며, 재배포 전 원문 정책 확인이 필요합니다.</li>
          <li>고위험 의사결정(법률·의료·재무·규제)에는 원문 대조와 추가 검증 절차를 수행하세요.</li>
          <li>EU AI Act 투명성 취지에 따라 AI 생성/보조 작성 콘텐츠임을 명시합니다.</li>
        </ul>
      </section>
    </main>

    <script src="assets/site.js"></script>
  </body>
</html>
"""


SITE_CSS = """
:root {
  --bg: #f6f7f4;
  --paper: #ffffff;
  --ink: #171b1f;
  --muted: #5c6670;
  --line: #d9ded8;
  --green: #0d7c66;
  --blue: #2357a5;
  --red: #a23645;
  --deep: #0d141b;
  --shadow: 0 18px 48px rgba(27, 36, 45, 0.10);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif;
  line-height: 1.6;
}
h1, h2, h3, .lead, .subtitle, .review-card p, .latest-update p, .transparency-notice li {
  word-break: keep-all;
  overflow-wrap: break-word;
}
a { color: inherit; }
.site-header, main {
  width: min(1180px, calc(100% - 36px));
  margin: 0 auto;
}
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 0 18px;
  font-size: 14px;
  color: var(--muted);
}
.topbar-links {
  display: inline-flex;
  align-items: center;
  gap: 16px;
}
.brand {
  color: var(--ink);
  font-weight: 800;
  text-decoration: none;
}
.hero {
  border-top: 5px solid var(--green);
  border-bottom: 1px solid var(--line);
  padding: 52px 0 34px;
}
.eyebrow {
  margin: 0 0 14px;
  color: var(--green);
  font-size: 13px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
h1 {
  max-width: 860px;
  margin: 0;
  font-size: clamp(34px, 6vw, 64px);
  line-height: 1.08;
  letter-spacing: 0;
}
.lead {
  max-width: 780px;
  margin: 22px 0 0;
  color: var(--muted);
  font-size: 18px;
}
.section-kicker {
  margin: 0 0 8px;
  color: var(--green);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 28px;
}
.stats span {
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.65);
  padding: 10px 13px;
  font-size: 14px;
}
.latest-update {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(360px, 1.05fr);
  gap: 24px;
  align-items: stretch;
  margin: 30px 0 26px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  box-shadow: var(--shadow);
  overflow: hidden;
}
.latest-copy {
  padding: clamp(24px, 4vw, 38px);
}
.latest-copy h2 {
  margin: 0 0 12px;
  font-size: clamp(28px, 4vw, 46px);
  line-height: 1.08;
}
.latest-copy p {
  color: var(--muted);
}
.latest-subtitle {
  color: var(--ink) !important;
  font-weight: 800;
}
.latest-media {
  display: grid;
  min-height: 100%;
  background: #eef1ed;
}
.latest-media img {
  display: block;
  width: 100%;
  height: 100%;
  min-height: 320px;
  object-fit: contain;
}
.text-link {
  display: inline-flex;
  margin-top: 22px;
  color: var(--green);
  font-weight: 900;
  text-decoration: none;
}
.text-link:hover {
  color: var(--blue);
}
.toolbar {
  display: grid;
  grid-template-columns: 1fr minmax(180px, 260px);
  gap: 12px;
  margin: 30px 0 18px;
}
.toolbar label {
  display: grid;
  gap: 6px;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
}
input, select {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
  color: var(--ink);
  padding: 12px 13px;
  font: inherit;
}
input:focus, select:focus {
  outline: 3px solid rgba(13, 124, 102, 0.18);
  border-color: var(--green);
}
.review-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}
.review-card {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 0;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: var(--shadow);
}
.thumb {
  display: block;
  aspect-ratio: 16 / 10;
  background: #e8ece8;
}
.thumb img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.thumb-placeholder {
  width: 100%;
  aspect-ratio: 16 / 10;
  background: linear-gradient(135deg, rgba(13,124,102,0.24), rgba(35,87,165,0.18));
}
.review-card-body {
  padding: 22px;
}
.meta {
  margin: 0 0 10px;
  color: var(--green);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
h3 {
  margin: 0 0 10px;
  font-size: 21px;
  line-height: 1.25;
}
h3 a {
  text-decoration: none;
}
h3 a:hover {
  color: var(--blue);
}
.subtitle {
  color: var(--muted);
  font-weight: 700;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 18px;
}
.tags span {
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--muted);
  padding: 4px 9px;
  font-size: 12px;
}
.transparency-notice {
  display: grid;
  grid-template-columns: minmax(220px, 0.85fr) minmax(0, 1.4fr);
  gap: 24px;
  margin: 46px 0 76px;
  padding: clamp(22px, 4vw, 34px);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  background: var(--deep);
  color: #eaf0f3;
}
.transparency-notice h2 {
  margin: 0 0 14px;
  font-size: 24px;
}
.transparency-notice .operator {
  margin: 0;
  color: rgba(234, 240, 243, 0.72);
}
.transparency-notice a {
  color: #8bd8c6;
  font-weight: 800;
}
.transparency-notice ul {
  margin: 0;
  padding-left: 20px;
  color: rgba(234, 240, 243, 0.82);
}
.transparency-notice li + li {
  margin-top: 8px;
}
.public-note {
  max-width: 980px;
  margin: 52px auto 0;
  padding: 18px 24px;
  border-top: 1px solid rgba(0,0,0,0.12);
  color: #5c6670;
  font-size: 14px;
}
a:not([href]) {
  color: inherit;
  text-decoration: none;
  cursor: default;
}
.hidden { display: none !important; }
@media (max-width: 900px) {
  .latest-update,
  .transparency-notice {
    grid-template-columns: 1fr;
  }
  .review-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 680px) {
  .site-header, main { width: min(100% - 24px, 1180px); }
  .toolbar { grid-template-columns: 1fr; }
  .review-grid { grid-template-columns: 1fr; }
  .thumb { aspect-ratio: 16 / 9; }
  .latest-media img { min-height: 220px; }
  .hero { padding-top: 36px; }
}
"""


SITE_JS = """
const search = document.querySelector("#search");
const category = document.querySelector("#category");
const cards = Array.from(document.querySelectorAll(".review-card"));

function normalize(value) {
  return (value || "").toLocaleLowerCase("ko-KR");
}

function applyFilters() {
  const q = normalize(search.value);
  const c = category.value;
  for (const card of cards) {
    const haystack = normalize(`${card.dataset.title} ${card.dataset.tags} ${card.textContent}`);
    const categoryMatch = !c || card.dataset.category === c;
    const searchMatch = !q || haystack.includes(q);
    card.classList.toggle("hidden", !(categoryMatch && searchMatch));
  }
}

search.addEventListener("input", applyFilters);
category.addEventListener("change", applyFilters);
"""


def validate_public_site(manifest: list[dict[str, object]]) -> list[str]:
    errors: list[str] = []
    for item in manifest:
        review_index = SITE_DIR / str(item["href"])
        if not review_index.exists():
            errors.append(f"missing review index: {review_index}")
            continue
        text = review_index.read_text(encoding="utf-8")
        for match in LOCAL_HREF_RE.finditer(text):
            raw_url = match.group("url")
            if not is_external_or_anchor(raw_url):
                errors.append(f"local href left in {review_index}: {raw_url}")
        if INTERNAL_PATH_RE.search(text):
            errors.append(f"internal path left in {review_index}")
        parser = FirstImageParser()
        parser.feed(text)
        if parser.first_image and not (review_index.parent / split_local_url(parser.first_image)[0]).exists():
            errors.append(f"missing thumbnail asset in {review_index}: {parser.first_image}")
    return errors


def main() -> int:
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    REVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    manifest = [publish_review(review) for review in REVIEWS]
    manifest.sort(key=lambda item: str(item["date"]), reverse=True)

    (SITE_DIR / "index.html").write_text(render_index(manifest), encoding="utf-8")
    (SITE_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")
    (ASSETS_DIR / "site.css").write_text(SITE_CSS.strip() + "\n", encoding="utf-8")
    (ASSETS_DIR / "site.js").write_text(SITE_JS.strip() + "\n", encoding="utf-8")

    errors = validate_public_site(manifest)
    if errors:
        for error in errors:
            print(f"[public-site:error] {error}")
        return 2

    print(f"[public-site] {SITE_DIR}")
    print(f"[public-site] reviews={len(manifest)}")
    for item in manifest:
        print(f"[review] {item['href']}")
    print("[public-site-check] ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
