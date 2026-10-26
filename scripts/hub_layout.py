"""Bilingual, progressively enhanced entry pages for the existing public catalog."""
from __future__ import annotations

import html
from pathlib import Path
from urllib.parse import unquote, urlsplit

try:
    from .hub_localization import localize_manifest
    from .document_archive_site import render_library_navigation
    from .site_brand import render_brand_link
except ImportError:
    from hub_localization import localize_manifest
    from document_archive_site import render_library_navigation
    from site_brand import render_brand_link


HUB_URL = "https://infant83.io/AI_Tech_Review/"
EDITOR_URL = "https://infant83.io/"
CONTACT_EMAIL = "angpangmokjang@gmail.com"
KOREAN_LANGUAGE_MARK = (Path(__file__).parent / "public_assets/korean-language-mark.svg").read_text(encoding="utf-8").strip()
ICONS = {
    "editor": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="9" r="2.7"/><path d="M6.8 18c.7-3.8 9.7-3.8 10.4 0"/>',
    "methods": '<path d="M12 5.5C8.5 3.5 5.5 3.5 3 4.5v14c3-1 6-1 9 1 3-2 6-2 9-1v-14c-2.5-1-5.5-1-9 1Z"/><path d="M12 5.5v14M6 8h3M6 11h3M15 8h3M15 11h3"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7h.01"/>',
    "sun": '<circle cx="12" cy="12" r="3.5"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "moon": '<path d="M20.2 14.1A8.5 8.5 0 0 1 9.9 3.8 8.5 8.5 0 1 0 20.2 14.1Z"/>',
}
CATEGORY_KO = {
    "Quantum Computing": "양자 컴퓨팅", "Materials AI": "재료 AI", "AI Hardware": "AI 하드웨어",
    "AI Governance": "AI 거버넌스", "Quantum AI": "양자 AI", "AI for Science": "AI for Science",
    "Frontier Models": "프런티어 모델", "Agent Systems": "에이전트", "AI Research": "AI 연구",
    "AI Security": "AI 보안",
}


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def icon(name: str) -> str:
    return ('<svg viewBox="0 0 24 24" width="21" height="21" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">'
            + ICONS[name] + '</svg>')


def icon_link(href: str, label: str, symbol: str) -> str:
    return f'<a class="hub-icon-link" href="{escape(href)}" aria-label="{escape(label)}" title="{escape(label)}">{icon(symbol)}</a>'


def public_href(value: object, prefix: str = "") -> str:
    value = str(value)
    parsed = urlsplit(value)
    decoded = unquote(parsed.path)
    if (parsed.scheme or parsed.netloc or parsed.query or parsed.fragment
            or decoded.startswith(("/", "\\")) or "\\" in decoded or "//" in decoded
            or "%" in decoded or any(ord(char) < 32 for char in value)
            or any(part in {".", ".."} for part in decoded.split("/"))):
        raise ValueError("A hub article or image must use a relative public path")
    return escape(prefix + value)


def category_label(value: object, language: str) -> str:
    category = str(value)
    return CATEGORY_KO.get(category, category) if language == "ko" else category


def language_badge(item: dict, language: str, prefix: str) -> str:
    if language == "en":
        return '<span class="translation-badge" lang="en">Korean</span>' if item.get("content_language", "ko") != "en" else ""
    href = item.get("english_href")
    if href:
        return f'<a class="translation-badge" href="{public_href(href, prefix)}" lang="en" hreflang="en">English</a>'
    return ""


def render_card(item: dict, language: str = "ko", prefix: str = "") -> str:
    en = language == "en"
    title = str(item["title"])
    tags = list(item.get("tags") or [])
    search = str(item.get("search_text") or " ".join(str(item.get(key) or "") for key in ("title", "subtitle", "summary", "category"))) + " " + " ".join(map(str, tags))
    href = public_href(item["href"], prefix)
    thumbnail = item.get("thumbnail")
    image = (f'<img src="{public_href(thumbnail, prefix)}" alt="{escape(title)} {"cover" if en else "대표 이미지"}" loading="lazy" decoding="async" width="960" height="540">'
             if thumbnail else '<div class="thumb-placeholder" aria-hidden="true"></div>')
    subtitle = str(item.get("subtitle") or "").strip()
    summary = str(item.get("summary") or "").strip()
    subtitle_html = f'<p class="subtitle">{escape(subtitle)}</p>' if subtitle else ""
    summary_id = "review-summary-" + str(item["folder"])
    summary_html = (f'<p class="review-summary" id="{escape(summary_id)}">{escape(summary)}</p>'
                    f'<button class="summary-toggle" data-summary-toggle type="button" aria-controls="{escape(summary_id)}" aria-expanded="false" hidden>{"Read full summary" if en else "요약 더 보기"}</button>'
                    if summary else "")
    content_language = "en" if item.get("content_language") == "en" else "ko"
    return f'''<article class="review-card" data-article-id="{escape(item['folder'])}" data-published="{escape(item['date'])}" data-search="{escape(search)}" data-category="{escape(item['category'])}" data-tags="{escape(' '.join(map(str, tags)))}" data-title="{escape(title)}" data-metric-path="{escape(item['metric_path'])}">
  <a class="thumb" href="{href}">{image}</a>
  <div class="review-card-body">
    <p class="meta">{escape(category_label(item['category'], language))} · <time datetime="{escape(item['date'])}">{escape(item['date'])}</time>{language_badge(item, language, prefix)}</p>
    <h3 lang="{content_language}"><a href="{href}">{escape(title)}</a></h3>
    <div class="review-description" lang="{content_language}">{subtitle_html}{summary_html}</div>
    <p class="card-reader-counts" aria-label="{'Cumulative reader activity' if en else '누적 독자 활동'}"><span>{'Views' if en else '조회'} <strong data-discovery-field="opens">—</strong></span><span aria-hidden="true">·</span><span>{'Likes' if en else '좋아요'} <strong data-discovery-field="likes">—</strong></span></p>
  </div>
</article>'''


def render_latest(item: dict, language: str = "ko", prefix: str = "") -> str:
    en = language == "en"
    href = public_href(item["href"], prefix)
    thumbnail = item.get("thumbnail")
    image = (f'<img src="{public_href(thumbnail, prefix)}" alt="{escape(item["title"])} {"cover" if en else "대표 이미지"}" loading="eager" fetchpriority="high" width="1200" height="675">'
             if thumbnail else '<div class="thumb-placeholder" aria-hidden="true"></div>')
    subtitle = str(item.get("subtitle") or "").strip()
    subtitle_html = f'<p class="latest-subtitle">{escape(subtitle)}</p>' if subtitle else ""
    content_language = "en" if item.get("content_language") == "en" else "ko"
    return f'''<section class="latest-update" aria-labelledby="latest-heading">
  <div class="latest-copy">
    <p class="section-kicker">{'Latest review' if en else '최근 리뷰'} · <time datetime="{escape(item['date'])}">{escape(item['date'])}</time></p>
    <h1 id="latest-heading" lang="{content_language}">{escape(item['title'])}</h1>
    <div class="latest-description" lang="{content_language}">{subtitle_html}<p>{escape(item.get('summary') or '')}</p></div>
    <a class="text-link" href="{href}">{'Read review' if en else '리뷰 읽기'} <span aria-hidden="true">↗</span></a>{language_badge(item, language, prefix)}
  </div>
  <a class="latest-media" href="{href}">{image}</a>
</section>'''


def render_hub(manifest: list[dict], preferred_category_order: list[str] | None, documents: list[dict] | None,
               *, site_dir: Path, language: str, css_version: str, js_version: str,
               preferences_version: str, library_version: str) -> str:
    if language not in {"ko", "en"}:
        raise ValueError("Unsupported hub language")
    en = language == "en"
    prefix = "../" if en else ""
    items = localize_manifest(manifest, site_dir, language)
    documents = documents or []
    available = {str(item["category"]) for item in items}
    categories = [value for value in (preferred_category_order or []) if value in available]
    categories.extend(sorted(available - set(categories)))
    category_options = "".join(f'<option value="{escape(value)}">{escape(category_label(value, language))}</option>' for value in categories)
    cards = "\n".join(render_card(item, language, prefix) for item in items)
    latest = render_latest(items[0], language, prefix) if items else ""
    description = "Reviews and lecture notes on AI, quantum computing, and materials science." if en else "AI·양자 컴퓨팅·재료과학 리뷰와 렉처 노트."
    canonical = HUB_URL + ("en/" if en else "")
    image_meta = ""
    if items and items[0].get("thumbnail"):
        image = escape(HUB_URL + str(items[0]["thumbnail"]))
        image_meta = f'<meta property="og:image" content="{image}"><meta name="twitter:image" content="{image}">'
    brand = render_brand_link(prefix).replace('<span class="brand-name">AI Tech Review Letters</span>', '<span class="brand-name"><b>AI Tech Review</b> <small>LETTERS</small></span>')
    if en:
        brand = brand.replace('href="../index.html"', 'href="index.html"', 1)
    navigation = render_library_navigation(documents, "reviews", language, prefix)
    if en:
        navigation = navigation.replace('href="../index.html"', 'href="index.html"', 1)
    methods_label = "Editorial policy" if en else "작성·검증 원칙"
    editor_label = "About the editor" if en else "편집자 소개"
    mail_label = "Email the editor" if en else "편집자에게 메일 보내기"
    data_label = "Reader statistics guide" if en else "독자 통계 안내"
    return f'''<!doctype html>
<html lang="{language}" data-hub-language="{language}" data-theme="light">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Tech Review Letters</title>
  <meta name="description" content="{escape(description)}">
  <link rel="canonical" href="{canonical}">
  <link rel="alternate" hreflang="ko" href="{HUB_URL}">
  <link rel="alternate" hreflang="en" href="{HUB_URL}en/">
  <link rel="alternate" hreflang="x-default" href="{HUB_URL}">
  <link rel="home" href="{prefix}index.html" data-hub-home>
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="AI Tech Review Letters">
  <meta property="og:title" content="AI Tech Review Letters">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:locale" content="{'en_US' if en else 'ko_KR'}">
  {image_meta}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="AI Tech Review Letters">
  <meta name="twitter:description" content="{escape(description)}">
  <script src="{prefix}assets/hub-preferences.js?v={preferences_version}"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;500;600;700&amp;family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&amp;display=swap">
  <link rel="stylesheet" href="{prefix}assets/site.css?v={css_version}">
  <link rel="stylesheet" href="{prefix}assets/archive.css?v={library_version}">
</head>
<body class="hub-page">
  <header class="site-header">
    <nav class="topbar" aria-label="{'Site navigation' if en else '사이트 안내'}">
      <div class="topbar-left">{brand}</div>
      <div class="hub-toolbar">
        <span class="topbar-links">
          {icon_link(EDITOR_URL, editor_label, 'editor')}
          {icon_link(prefix + 'methods/', methods_label, 'methods')}
        </span>
        <button class="hub-toggle hub-language-toggle" type="button" role="switch" data-hub-language-toggle aria-label="{'English' if en else '영어'}" aria-checked="{'true' if en else 'false'}" title="{'Switch to Korean' if en else '영어로 전환'}"><span class="hub-toggle-track" aria-hidden="true"><span class="hub-toggle-choice" lang="ko">{KOREAN_LANGUAGE_MARK}</span><span class="hub-toggle-choice hub-language-en" lang="en">EN</span></span></button>
        <button class="hub-toggle hub-theme-toggle" type="button" role="switch" data-hub-theme-toggle aria-label="{'Dark theme' if en else '어두운 화면'}" aria-checked="false" title="{'Switch to dark theme' if en else '어두운 화면으로 전환'}"><span class="hub-toggle-track" aria-hidden="true"><span class="hub-toggle-choice">{icon('sun')}</span><span class="hub-toggle-choice">{icon('moon')}</span></span></button>
        <span class="sr-only" data-hub-preference-status role="status" aria-live="polite"></span>
        <noscript><style>.hub-toggle{{display:none}}</style><a href="{'../' if en else 'en/'}" hreflang="{'ko' if en else 'en'}">{'한국어' if en else 'English'}</a></noscript>
      </div>
    </nav>
    <div class="hub-browse">{navigation}<label class="top-search"><span class="sr-only">{'Search reviews' if en else '리뷰 검색'}</span><input id="search" type="search" placeholder="{'Search titles or topics' if en else '제목·주제 검색'}" autocomplete="off"></label></div>
  </header>
  <main>
    {latest}
    <section class="topic-filter" id="topic-filter" aria-label="{'Find reviews' if en else '주제별 리뷰 찾기'}">
      <div class="filter-heading"><h2>{'Reviews' if en else '리뷰'}</h2><div class="discovery-controls">
        <label class="category-select"><span>{'Topic' if en else '주제'}</span><select id="category"><option value="">{'All topics' if en else '전체'}</option>{category_options}</select></label>
        <label class="discovery-select"><span>{'Sort' if en else '정렬'}</span><select id="review-sort"><option value="latest">{'Newest' if en else '최신순'}</option><option value="views" disabled>{'Views' if en else '조회순'}</option><option value="likes" disabled>{'Likes' if en else '좋아요순'}</option></select></label>
        <label class="discovery-select"><span>{'Activity period' if en else '관심 집계 기간'}</span><select id="review-period"><option value="all">{'All time' if en else '전체'}</option><option value="7d">{'Last 7 days' if en else '최근 7일'}</option><option value="30d">{'Last 30 days' if en else '최근 30일'}</option><option value="90d">{'Last 90 days' if en else '최근 90일'}</option><option value="custom">{'Custom dates' if en else '기간 지정'}</option></select></label>
      </div></div>
      <div class="discovery-dates" id="discovery-dates" hidden><label><span>{'From' if en else '시작일'}</span><input id="discovery-from" type="date"></label><span aria-hidden="true">–</span><label><span>{'To' if en else '종료일'}</span><input id="discovery-to" type="date"></label></div>
      <p class="discovery-hint" id="discovery-hint">{'The period applies to viewing and liking activity. Card counts are cumulative.' if en else '기간은 글 발행일이 아닌 조회·좋아요 활동 기준이며, 카드 수치는 누적값입니다.'}</p>
      <div class="discovery-feedback"><p id="discovery-status" role="status" aria-live="polite"></p><button class="discovery-retry" id="discovery-retry" type="button" hidden>{'Reload statistics' if en else '통계 다시 불러오기'}</button></div>
    </section>
    <div class="hub-viewbar"><div class="hub-view-switch" role="group" aria-label="{'Review view' if en else '리뷰 보기'}"><button id="hub-view-covers" type="button" data-view="gallery" aria-controls="review-grid" aria-pressed="true">{'Covers' if en else '표지 보기'}</button><button id="hub-view-list" type="button" data-view="list" aria-controls="review-grid" aria-pressed="false">{'All reviews' if en else '전체 목록'}</button></div><p class="discovery-results" id="review-results" role="status" aria-live="polite"></p></div>
    <section class="review-grid" id="review-grid" data-view="gallery" aria-label="{'Review list' if en else '리뷰 목록'}">
{cards}
    </section>
    <p class="discovery-empty" id="review-empty" hidden>{'No reviews match this search.' if en else '검색 조건에 맞는 리뷰가 없습니다.'}</p>
    <div class="discovery-more-wrap"><button class="discovery-more" id="review-more" type="button" hidden>{'Show more' if en else '더 보기'}</button></div>
  </main>
  <footer class="site-footer">
    <div><strong>AI Tech Review Letters</strong><p>{escape(description)}</p></div>
    <nav class="hub-footer-links" aria-label="{'Information' if en else '하단 안내'}">{icon_link(EDITOR_URL, editor_label, 'editor')}{icon_link(prefix + 'methods/', methods_label, 'methods')}{icon_link(prefix + 'methods/#reader-metrics', data_label, 'info')}{icon_link('mailto:' + CONTACT_EMAIL, mail_label, 'mail')}</nav>
    <div data-reader-site-metrics></div>
  </footer>
  <script src="{prefix}assets/site.js?v={js_version}" defer></script>
</body>
</html>
'''
