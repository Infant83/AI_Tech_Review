"""Generate read-only, bilingual insights pages from the public registries."""
from __future__ import annotations

from html import escape
import hashlib
import json
from pathlib import Path

try:
    from .hub_localization import localize_manifest
except ImportError:
    from hub_localization import localize_manifest

PAGES = frozenset({"insights/index.html", "en/insights/index.html"})
CATEGORY_KO = {"Quantum Computing": "양자 컴퓨팅", "Materials AI": "재료 AI",
               "AI Hardware": "AI 하드웨어", "AI Governance": "AI 거버넌스",
               "Quantum AI": "양자 AI", "Frontier Models": "프런티어 모델",
               "Agent Systems": "에이전트", "AI Research": "AI 연구", "AI Security": "AI 보안"}
SCOPE = "/AI_Tech_Review/"


def catalogs(site_dir: Path, articles: list[dict]) -> dict[str, list[dict]]:
    """Join only published metadata. Tags never supply a scientific category."""
    reviews = json.loads((site_dir / "manifest.json").read_text(encoding="utf-8"))
    archive_file = site_dir / "archive-manifest.json"
    documents = json.loads(archive_file.read_text(encoding="utf-8")).get("documents", []) if archive_file.exists() else []
    lecture = {"lecture:" + row["id"]: row for row in documents if row.get("series") == "lecture-notes"}
    output = {}
    for language in ("ko", "en"):
        localized = {row["folder"]: row for row in localize_manifest(reviews, site_dir, language)}
        rows = []
        for article in articles:
            row = {key: article[key] for key in ("id", "title", "path", "topic", "publishedAt")}
            row.update(category=None, categoryLabel="Unclassified" if language == "en" else "미분류", contentLanguage="ko")
            if article["topic"] == "review":
                metadata = localized[article["id"]]
                category = metadata.get("category")
                if category is not None and (not isinstance(category, str) or not category.strip() or len(category) > 100):
                    raise ValueError("Invalid insights category")
                row.update(title=metadata["title"], path=SCOPE + metadata["href"],
                           contentLanguage=metadata["content_language"], category=category,
                           categoryLabel=(CATEGORY_KO.get(category, category) if language == "ko" else category) or row["categoryLabel"])
                if row["path"].endswith("index.html"):
                    row["path"] = row["path"][:-10]
            elif language == "en":
                metadata = lecture[article["id"]]
                row["title"] = metadata.get("study_series", {}).get("title_en") or metadata.get("title_en") or article["title"]
            rows.append(row)
        output[language] = rows
    return output


def render_page(articles: list[dict], language: str, *, asset_versions: dict[str, str], icon: bool = True) -> str:
    en = language == "en"
    def label(ko, english):
        return english if en else ko
    title = label("읽기 통계", "Reading insights")
    other = "insights/" if en else "en/insights/"
    config = {"version": 1, "language": language, "scope": SCOPE,
              "apiBase": "https://api.infant83.io", "articles": articles}
    data = json.dumps(config, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("&", "\\u0026")
    image = f'<img src="{SCOPE}assets/apple-touch-icon.png" alt="" width="44" height="44">' if icon else ""
    options = "".join(f'<option value="{days}d">{label(f"최근 {days}일", f"Last {days} days")}</option>' for days in (7, 30, 90))
    kinds = "".join(f'<option value="{value}">{text}</option>' for value, text in
                    (("all", label("전체", "All")), ("review", label("리뷰", "Reviews")), ("lecture", label("렉처", "Lectures"))))
    return f'''<!doctype html>
<html lang="{language}" data-theme="light"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · Agentic Tech Review Letters</title>
<meta name="description" content="{label('글별·분야별 읽기와 일별 기록을 확인합니다.', 'Recorded opens by article, category and day.')}">
<meta property="og:site_name" content="Agentic Tech Review Letters">
<link rel="canonical" href="https://infant83.io{SCOPE}{'en/' if en else ''}insights/">
<link rel="alternate" hreflang="ko" href="https://infant83.io{SCOPE}insights/">
<link rel="alternate" hreflang="en" href="https://infant83.io{SCOPE}en/insights/">
<link rel="stylesheet" href="{SCOPE}assets/reader-insights.css?v={asset_versions['reader-insights.css']}">
<script id="reader-insights-config" type="application/json">{data}</script>
<script defer src="{SCOPE}assets/reader-insights.js?v={asset_versions['reader-insights.js']}"></script>
</head><body>
<a class="skip" href="#main">{label('본문으로', 'Skip to content')}</a>
<header class="site-header"><div class="header-inner">
<a class="brand" href="{SCOPE}{'en/' if en else ''}">{image}<span>Agentic Tech Review <small>LETTERS</small></span></a>
<nav aria-label="{label('화면 설정', 'Page settings')}"><a id="insights-language" href="{SCOPE}{other}" hreflang="{'ko' if en else 'en'}">{'한국어' if en else 'English'}</a>
<button id="insights-theme" type="button" role="switch" aria-checked="false" aria-label="{label('어두운 화면', 'Dark theme')}"><span aria-hidden="true">◐</span></button></nav>
</div></header>
<main id="main"><div class="heading"><p class="eyebrow">ATRL</p><h1>{title}</h1>
<p>{label('읽기 횟수는 기록된 글 열람입니다. 고유 독자 수나 과학적 중요도를 뜻하지 않습니다.', 'Opens count recorded article visits. They do not measure unique readers or scientific importance.')}</p></div>
<form id="insights-filters" class="filters"><label for="insights-period">{label('기간', 'Period')}<select id="insights-period" name="period">{options}</select></label>
<label for="insights-kind">{label('글 종류', 'Article type')}<select id="insights-kind" name="kind">{kinds}</select></label>
<button id="insights-refresh" type="button">{label('새로 조회', 'Refresh')}</button></form>
<p id="insights-status" class="status" role="status" aria-live="polite">{label('통계를 불러오는 중입니다.', 'Loading statistics.')}</p>
<p id="insights-range" class="range"></p>
<noscript><p>{label('통계를 보려면 JavaScript가 필요합니다. 글 목록과 집계 기준은 아래 링크에서 읽을 수 있습니다.', 'JavaScript is needed to load statistics. The article list and counting guide remain available below.')}</p></noscript>
<div id="insights-results" hidden>
<section class="panel" aria-labelledby="popular-heading"><div class="panel-heading"><h2 id="popular-heading">{label('많이 읽힌 글', 'Most read articles')}</h2>
<label class="rank-label" for="insights-ranking">{label('순위 기준', 'Rank by')}<select id="insights-ranking"><option value="opens">{label('선택 기간 읽기', 'Opens in selected period')}</option><option value="likes">{label('현재 좋아요', 'Current likes')}</option></select></label></div>
<p id="insights-ranking-note" class="note"></p><div id="insights-popular"></div>
<details><summary>{label('전체 글 수치 표', 'Table of all article counts')}</summary><div class="table-scroll"><table><caption id="insights-article-caption">{label('선택 범위의 글별 수치', 'Article counts for the selected scope')}</caption><thead><tr><th scope="col">{label('글', 'Article')}</th><th scope="col">{label('읽기', 'Opens')}</th><th scope="col">{label('현재 좋아요', 'Current likes')}</th></tr></thead><tbody id="insights-article-table"></tbody></table></div></details></section>
<section class="panel" aria-labelledby="category-heading"><h2 id="category-heading">{label('분야별 읽기', 'Opens by category')}</h2><p class="note">{label('리뷰에 등록된 분야 하나로 집계합니다. 분야가 없는 렉처는 미분류에 포함합니다.', 'Each review uses its one registered category. Lectures without a category are included as unclassified.')}</p><div id="insights-categories"></div><div class="table-scroll"><table><caption>{label('분야별 기록된 읽기 횟수', 'Recorded opens by category')}</caption><thead><tr><th scope="col">{label('분야', 'Category')}</th><th scope="col">{label('글 수', 'Articles')}</th><th scope="col">{label('읽기', 'Opens')}</th></tr></thead><tbody id="insights-category-table"></tbody></table></div></section>
<section class="panel" aria-labelledby="daily-heading"><h2 id="daily-heading">{label('일별 읽기', 'Daily opens')}</h2><p class="note">{label('한국시간(KST) 기준입니다. 오늘과 수집·보존이 시작된 날은 일부 기록일 수 있습니다.', 'Days use Korea Standard Time (KST). Today and the first collection or retained day may be partial.')}</p><div id="insights-daily"></div><details><summary>{label('일별 기록 표', 'Table of daily records')}</summary><div class="table-scroll"><table><caption>{label('일별 읽기와 기록 상태', 'Daily opens and record coverage')}</caption><thead><tr><th scope="col">{label('날짜(KST)', 'Date (KST)')}</th><th scope="col">{label('읽기', 'Opens')}</th><th scope="col">{label('기록 상태', 'Record coverage')}</th></tr></thead><tbody id="insights-daily-table"></tbody></table></div></details></section>
<p class="note coverage-note">{label('수집 전은 미수집, 보존 전은 불완전으로 표시합니다. 기록 0은 저장된 열람이 없다는 뜻이며, 장애가 없었다는 보장은 아닙니다.', 'Before collection: not collected. Before retained records: incomplete. Recorded zero means no stored opens; it does not establish uninterrupted collection.')}</p>
</div></main><footer><a href="{SCOPE}{'en/' if en else ''}">{label('글 목록', 'Articles')}</a><a class="guide" href="{SCOPE}methods/#reader-metrics">{label('집계 기준', 'Counting guide')}</a><span>Agentic Tech Review Letters</span></footer>
</body></html>
'''


def generate(site_dir: Path, articles: list[dict], *, asset_payloads: dict[str, bytes]) -> int:
    site_dir = Path(site_dir)
    versions = {name: hashlib.sha256(asset_payloads["assets/" + name]).hexdigest()[:12]
                for name in ("reader-insights.js", "reader-insights.css")}
    metadata = catalogs(site_dir, articles)
    changed = 0
    for language in ("ko", "en"):
        path = site_dir / ("en/" if language == "en" else "") / "insights/index.html"
        if path.is_symlink() or path.parent.is_symlink():
            raise ValueError("Insights pages cannot be symlinks")
        content = render_page(metadata[language], language, asset_versions=versions,
                              icon=(site_dir / "assets/apple-touch-icon.png").is_file()).encode("utf-8")
        if not path.exists() or path.read_bytes() != content:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            changed += 1
    return changed
