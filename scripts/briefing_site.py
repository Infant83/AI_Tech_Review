"""Render a publication calendar and reading list from reviewed public PDFs."""
from __future__ import annotations

import calendar
import hashlib
from datetime import date
import html
import json
from pathlib import Path
import re

try:
    from .site_search import search_head, search_form, search_results, search_script
    from .listing_pagination import page_count, page_path, page_prefix, page_directory, page_slice, pagination, pagination_script
    from .site_brand import SITE_NAME, SITE_STYLES_VERSION, render_brand_link
    from .briefing_routes import BRIEFING_SERIES, editorial_paths
except ImportError:
    from site_search import search_head, search_form, search_results, search_script
    from listing_pagination import page_count, page_path, page_prefix, page_directory, page_slice, pagination, pagination_script
    from site_brand import SITE_NAME, SITE_STYLES_VERSION, render_brand_link
    from briefing_routes import BRIEFING_SERIES, editorial_paths

PUBLIC_FIELDS = ("id", "date", "series", "title", "title_en", "summary", "summary_en", "tags", "language", "href", "editorial_href", "editorial_en_href")


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def briefing_documents(documents: list[dict], prefix: str = "") -> list[dict]:
    """Do not serialize intake metadata or fields added by another document type."""
    result = []
    for source in documents:
        if source["series"] not in BRIEFING_SERIES:
            continue
        doc = {key: source[key] for key in PUBLIC_FIELDS if key in source}
        for key in ("href", "editorial_href", "editorial_en_href"):
            if key in doc:
                doc[key] = prefix + doc[key]
        result.append(doc)
    return sorted(result, key=lambda doc: (doc["date"], doc["id"]), reverse=True)


def calendar_months(documents: list[dict]) -> list[str]:
    """Include intervening empty months, without inventing publication records."""
    dates = [date.fromisoformat(doc["date"]) for doc in documents if doc["series"] in BRIEFING_SERIES]
    if not dates:
        return []
    first, last = min(dates), max(dates)
    start, end = first.year * 12 + first.month - 1, last.year * 12 + last.month - 1
    return [f"{number // 12:04d}-{number % 12 + 1:02d}" for number in range(end, start - 1, -1)]


def month_label(month: str, language: str = "ko") -> str:
    year, number = map(int, month.split("-"))
    return f"{calendar.month_name[number]} {year}" if language == "en" else f"{year}년 {number}월"


def briefing_title(document: dict, language: str = "ko") -> str:
    return (document.get("title_en") or document["title"]) if language == "en" else document["title"]


def briefing_title_language(document: dict, language: str = "ko") -> str:
    return "en" if language == "en" and document.get("title_en") else document["language"]


def briefing_reading_href(document: dict, language: str = "ko") -> str:
    return document.get("editorial_en_href" if language == "en" else "editorial_href") or document["href"]


def briefing_has_editorial(document: dict, language: str = "ko") -> bool:
    return bool(document.get("editorial_en_href" if language == "en" else "editorial_href"))


def briefing_reading_target(document: dict, language: str = "ko") -> str:
    return "" if briefing_has_editorial(document, language) else ' target="_blank" rel="noopener"'


def render_calendar(documents: list[dict], month: str, language: str = "ko") -> str:
    """A Monday-first native table, also readable with scripting disabled."""
    en = language == "en"
    year, number = map(int, month.split("-"))
    days = {}
    for doc in briefing_documents(documents):
        days.setdefault(doc["date"], []).append(doc)
    rows = []
    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(year, number):
        cells = []
        for day in week:
            if not day:
                cells.append('<td class="calendar-pad" aria-hidden="true"></td>')
                continue
            iso = f"{month}-{day:02d}"
            issues = days.get(iso, [])
            topic_label = (f"{len(issues)} briefings: " if en else f"브리핑 {len(issues)}건: ") + "; ".join(briefing_title(doc, language) for doc in issues)
            label = f"{iso} · " + (topic_label if issues else ("No registered briefing" if en else "등록된 브리핑 없음"))
            links = "".join(f'<a href="{escape(briefing_reading_href(doc, language))}" lang="{escape(briefing_title_language(doc, language))}"{briefing_reading_target(doc, language)} title="{escape(briefing_title(doc, language))}">{escape(briefing_title(doc, language))}</a>' for doc in issues)
            badge = f'<span class="day-count" aria-hidden="true">{len(issues)}</span>' if issues else ""
            cells.append(f'<td class="calendar-day{" has-briefing" if issues else ""}"><button class="day-select" type="button" data-date="{iso}" aria-label="{escape(label)}" aria-pressed="false"{" disabled" if not issues else ""}><span class="day-number">{day}</span>{badge}</button><div class="day-topics">{links}</div></td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "".join(rows)


def render_detail(documents: list[dict], language: str = "ko") -> str:
    en = language == "en"
    if not documents:
        return '<p class="briefing-detail-empty">' + ("No registered briefing for this selection." if en else "선택한 조건에 등록된 브리핑이 없습니다.") + '</p>'
    cards = []
    for doc in documents:
        summary = (doc.get("summary_en") or doc["summary"]) if en else doc["summary"]
        summary_language = "en" if en and doc.get("summary_en") else doc["language"]
        tags = "".join(f'<span>{escape(tag)}</span>' for tag in doc["tags"])
        editorial = briefing_has_editorial(doc, language)
        reading = briefing_reading_href(doc, language)
        pdf_actions = (f'<a class="briefing-read" href="{escape(doc["href"])}" target="_blank" rel="noopener">{"Read PDF" if en else "PDF 읽기"} ↗</a> <a href="{escape(doc["href"])}" download>{"Download PDF" if en else "PDF 다운로드"} ↓</a>' if editorial else "")
        read_label = ("Read briefing" if editorial else "Read PDF") if en else "브리핑 읽기"
        target = briefing_reading_target(doc, language)
        cards.append(f'<article class="briefing-detail-issue"><h4 lang="{escape(briefing_title_language(doc, language))}"><a href="{escape(reading)}"{target}>{escape(briefing_title(doc, language))}</a></h4><p lang="{summary_language}">{escape(summary)}</p><div class="briefing-tags">{tags}</div><a class="briefing-read" href="{escape(reading)}"{target}>{read_label} ↗</a> {pdf_actions}</article>')
    return "".join(cards)


def render_briefings(documents: list[dict], base_url: str, language: str = "ko", navigation: str = "", asset_version: str = "", page_number: int = 1) -> str:
    en = language == "en"
    script_version = hashlib.sha256((Path(__file__).parent / "assets" / "briefings.js").read_bytes()).hexdigest()[:12]
    prefix = page_prefix("briefings", language, page_number)
    issues = briefing_documents(documents, prefix)
    months = calendar_months(issues)
    latest_month = months[0] if months else ""
    latest_date = issues[0]["date"] if issues else ""
    title = "Briefings" if en else "브리핑"
    description = ("Explore research briefings by publication date and topic. Choose a day on the calendar or browse the reading list."
                   if en else "날짜별로 연구의 흐름을 살펴봅니다. 달력에서 발행일과 주제를 확인하거나, 목록에서 읽을 브리핑을 찾으세요.")
    canonical = base_url + page_directory("briefings", language, page_number)
    alternate = prefix + page_path("briefings", "ko" if en else "en", page_number)
    options = "".join(f'<option value="{month}">{month_label(month, language)}</option>' for month in months)
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] if en else list("월화수목금토일")
    headers = "".join(f'<th scope="col">{name}</th>' for name in weekdays)
    rows = []
    for doc in page_slice(issues, "briefings", page_number):
        summary = (doc.get("summary_en") or doc["summary"]) if en else doc["summary"]
        summary_language = "en" if en and doc.get("summary_en") else doc["language"]
        searchable = " ".join(str(doc.get(key, "")) for key in ("title", "title_en", "summary", "summary_en", "date")) + " " + " ".join(doc["tags"])
        tags = "".join(f'<span>{escape(tag)}</span>' for tag in doc["tags"])
        series = {"weekly-review": "Weekly review" if en else "주간 브리핑",
                  "daily-research": "Daily Research Brief", "daily-quantum": "Daily Quantum Brief",
                  "daily-quantum-exercise": "Daily Quantum Exercise"}[doc["series"]]
        pdf_language = ({"ko": "Korean PDF", "en": "English PDF"} if en else {"ko": "한국어 PDF", "en": "영어 PDF"})[doc["language"]]
        reading = briefing_reading_href(doc, language)
        editorial_action = (f'<a href="{escape(reading)}">{"Read briefing" if en else "브리핑 읽기"} →</a>' if briefing_has_editorial(doc, language) else "")
        rows.append(f'''<article class="briefing-row" data-id="{escape(doc['id'])}" data-date="{escape(doc['date'])}">
          <div class="briefing-date"><time datetime="{doc['date']}">{doc['date']}</time><span>{series}</span></div>
          <div class="briefing-row-body"><h3 lang="{escape(briefing_title_language(doc, language))}"><a href="{escape(reading)}"{briefing_reading_target(doc, language)}>{escape(briefing_title(doc, language))}</a></h3><p lang="{summary_language}">{escape(summary)}</p><div class="briefing-tags">{tags}</div></div>
          <div class="briefing-row-actions"><span>{pdf_language}</span>{editorial_action}<a href="{escape(doc['href'])}" target="_blank" rel="noopener">{'Read PDF' if en else ('PDF 읽기' if editorial_action else '읽기')} ↗</a><a href="{escape(doc['href'])}" download>{'Download' if en else '다운로드'} ↓</a></div>
        </article>''')
    payload = json.dumps({"documents": issues, "months": months, "latest_month": latest_month}, ensure_ascii=False, separators=(",", ":"))
    # Raw text script elements do not honor HTML entities. Escape their delimiters.
    payload = payload.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    empty_message = "No briefings have been published yet." if en else "아직 등록된 브리핑이 없습니다."
    calendar_section = f'''<section class="briefing-calendar-wrap" aria-labelledby="briefing-calendar-title">
        <div class="briefing-calendar-heading"><button id="briefing-prev" type="button" aria-label="{'Previous month' if en else '이전 달'}"{' disabled' if len(months) < 2 else ''}>←</button><h2 id="briefing-calendar-title">{month_label(latest_month, language)}</h2><button id="briefing-next" type="button" aria-label="{'Next month' if en else '다음 달'}" disabled>→</button></div>
        <p class="briefing-calendar-help">{'Select a date to see its topics below. Topic links open the briefing; PDF links remain available.' if en else '날짜를 선택하면 주제가 표시됩니다. 제목을 누르면 브리핑을 읽을 수 있고 PDF도 따로 열 수 있습니다.'}</p>
        <table class="briefing-calendar" aria-labelledby="briefing-calendar-title"><thead><tr>{headers}</tr></thead><tbody id="briefing-calendar">{render_calendar(issues, latest_month, language)}</tbody></table>
        <p class="briefing-calendar-legend"><span aria-hidden="true">●</span> {'Published briefing · blank dates have no registered issue' if en else '브리핑 발행일 · 빈 날짜는 등록된 문서가 없습니다'}</p>
      </section>''' if months else f'<p class="briefing-detail-empty">{empty_message}</p>'
    detail = render_detail([doc for doc in issues if doc["date"] == latest_date], language)
    return f'''<!doctype html><html lang="{language}"><head>
      <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{title} | {SITE_NAME}</title><meta name="description" content="{description}">
      <link rel="canonical" href="{canonical}">
      <link rel="alternate" hreflang="ko" href="{base_url}{page_directory('briefings', 'ko', page_number)}"><link rel="alternate" hreflang="en" href="{base_url}{page_directory('briefings', 'en', page_number)}"><link rel="alternate" hreflang="x-default" href="{base_url}{page_directory('briefings', 'ko', page_number)}">
      <meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{description}"><meta property="og:url" content="{canonical}">
      <link rel="stylesheet" href="{prefix}assets/site.css?v={SITE_STYLES_VERSION}"><link rel="stylesheet" href="{prefix}assets/archive.css?v={asset_version}"><link rel="stylesheet" href="{prefix}assets/briefings.css?v={asset_version}">
      {search_head(prefix)}
      </head><body class="briefings-page">
      <header class="site-header"><nav class="topbar" aria-label="{'Main navigation' if en else '주요 링크'}">{render_brand_link(prefix)}<span class="topbar-links"><a href="{prefix}methods/">{'Editorial methods' if en else '작성·검증 원칙'}</a><a href="{alternate}" lang="{'ko' if en else 'en'}" hreflang="{'ko' if en else 'en'}">{'한국어' if en else 'English'}</a></span></nav>
      {navigation}{search_form(prefix, language, "briefings")}<section class="briefing-hero"><p class="section-kicker">Day by day · Research briefings</p><h1>{title}</h1><p>{description}</p><div class="briefing-hero-meta"><span>{str(len(issues)) + ' published briefings' if en else str(len(issues)) + '건의 브리핑'}</span>{f'<span>{"Latest issue" if en else "최근 발행"} <time datetime="{latest_date}">{latest_date}</time></span>' if latest_date else ''}<a href="#briefing-board">{'Browse list' if en else '목록으로 보기'} ↓</a></div></section></header>
      <main>{search_results(language)}
      <div class="briefing-tools" role="search">
        <label><span>{'Publication month' if en else '발행 월'}</span><select id="briefing-month"{' disabled' if not months else ''}>{options}</select></label>
        <label class="briefing-search legacy-search-hidden"><span>{'Search topics' if en else '주제 검색'}</span><input id="briefing-search" type="search" placeholder="{'Title, keyword or date…' if en else '제목, 키워드, 날짜로 검색…'}" autocomplete="off"></label>
        <label class="briefing-scope"><input id="briefing-all-months" type="checkbox"><span>{'All months' if en else '전체 기간'}</span></label><button type="button" id="briefing-reset">{'Reset' if en else '초기화'}</button>
      </div>
      <div class="briefing-layout">{calendar_section}<section class="briefing-detail" id="briefing-day-panel" aria-labelledby="briefing-day-heading"><p class="section-kicker">{'Selected day / preview' if en else '날짜별 브리핑'}</p><h3 id="briefing-day-heading">{latest_date or ('No issues yet' if en else '발행 대기')}</h3><div id="briefing-day-content">{detail}</div></section></div>
      <section class="briefing-board" id="briefing-board" aria-labelledby="briefing-board-title"><div class="briefing-board-heading"><div><p class="section-kicker">Reading list</p><h2 id="briefing-board-title">{'Briefing list' if en else '브리핑 목록'}</h2><p id="briefing-filter-label">{'Newest first' if en else '최신 발행순'}</p></div><button type="button" id="briefing-clear-day" hidden>{'Show whole month' if en else '월 전체 보기'}</button></div>
        <p id="briefing-count" role="status">{len(issues)} {'briefings' if en else '건의 브리핑'}</p><div id="briefing-list">{''.join(rows)}</div><div id="briefing-empty" class="briefing-empty"{' hidden' if issues else ''}><p>{'No matching briefings. Try another month or search all months.' if en else '조건에 맞는 브리핑이 없습니다. 다른 달을 선택하거나 전체 기간으로 검색해 보세요.'}</p></div>
        {pagination("briefings", language, page_number, len(issues))}
        <button type="button" id="briefing-more" class="archive-more" hidden>{'Show more briefings' if en else '브리핑 더 보기'}</button>
        <noscript><p>{'Use the page links to browse all briefings. Calendar selection and search require JavaScript.' if en else '페이지 링크로 전체 브리핑을 읽을 수 있습니다. 날짜 선택과 검색은 JavaScript를 켜면 사용할 수 있습니다.'}</p></noscript>
      </section><footer class="archive-note"><p>{'Dates follow each document’s publication date. PDFs retain their original language and content. Only publicly registered issues appear here.' if en else '달력은 문서에 표기된 발행일 기준입니다. 공개 등록된 브리핑만 표시하며, 각 PDF는 발행 당시의 내용으로 보관합니다.'}</p><a href="{prefix}archive/{'en/' if en else ''}">{'All-document archive' if en else '전체 자료 아카이브'} →</a></footer>
      </main>{pagination_script(prefix)}<script type="application/json" id="briefing-data">{payload}</script><script src="{prefix}assets/briefings.js?v={script_version}" defer></script>
      {search_script(prefix)}
      </body></html>'''


def validate_briefings(site_dir: Path, documents: list[dict]) -> list[str]:
    errors = []
    root = site_dir / "briefings"
    first_page = root / "index.html"
    paginated = first_page.is_file() and 'data-list-pagination' in first_page.read_text(encoding="utf-8")
    total = len(briefing_documents(documents))
    pages = page_count(total, "briefings") if paginated else 1
    expected_files = {page_path("briefings", lang, number).removeprefix("briefings/") for lang in ("ko", "en") for number in range(1, pages + 1)}
    editorial_files = {}
    for doc in documents:
        if doc.get("series") not in BRIEFING_SERIES:
            continue
        ko_path, en_path = editorial_paths(doc["date"], doc["series"])
        expected_paths = {ko_path, en_path}
        declared = doc.get("editorial_assets", {})
        if doc.get("editorial_href") or doc.get("editorial_en_href") or declared:
            if (doc.get("editorial_href") != ko_path
                    or doc.get("editorial_en_href") != en_path
                    or not isinstance(declared, dict) or set(declared) != expected_paths
                    or any(not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value) for value in declared.values())
                    or editorial_files.keys() & declared.keys()):
                errors.append(f"invalid briefing editorial registration: {doc['id']}")
                continue
            editorial_files.update(declared)
            expected_files.update(path.removeprefix("briefings/") for path in declared)
    actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    if actual != expected_files:
        errors.append("briefing output differs from allowlist")
    for relative, digest in editorial_files.items():
        page = site_dir / relative
        if not page.is_file() or page.is_symlink() or hashlib.sha256(page.read_bytes()).hexdigest() != digest:
            errors.append(f"briefing editorial missing or changed: {relative}")
    for lang in ("ko", "en"):
        for number in range(1, pages + 1):
            relative = page_path("briefings", lang, number).removeprefix("briefings/")
            page = root / relative
            if not page.is_file():
                errors.append(f"missing briefing page: {relative}"); continue
            text = page.read_text(encoding="utf-8")
            match = re.search(r'<script type="application/json" id="briefing-data">(.*?)</script>', text, re.S)
            try:
                payload = json.loads(match.group(1)) if match else None
            except json.JSONDecodeError:
                payload = None
            prefix = page_prefix("briefings", lang, number)
            expected = briefing_documents(documents, prefix)
            if payload != {"documents": expected, "months": calendar_months(expected), "latest_month": calendar_months(expected)[0] if expected else ""}:
                errors.append(f"briefing data differs from public registry: {relative}")
            cards = page_slice(expected, "briefings", number) if paginated else expected
            if paginated and re.findall(r'class="briefing-row" data-id="([^"]+)"', text) != [row["id"] for row in cards]:
                errors.append(f"briefing page cards differ from registered slice: {relative}")
            for doc in cards:
                if f'href="{escape(doc["href"])}"' not in text:
                    errors.append(f"briefing PDF absent from {relative}: {doc['id']}")
                if f'href="{escape(briefing_reading_href(doc, lang))}"' not in text:
                    errors.append(f"briefing reading link absent from {relative}: {doc['id']}")
    for name in ("briefings.css", "briefings.js"):
        source = Path(__file__).parent / "assets" / name
        output = site_dir / "assets" / name
        if not output.is_file() or output.read_bytes() != source.read_bytes():
            errors.append(f"briefing asset missing or changed: {name}")
    return errors
