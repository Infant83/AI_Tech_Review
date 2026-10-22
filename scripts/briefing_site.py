"""Render a publication calendar and reading list from reviewed public PDFs."""
from __future__ import annotations

import calendar
from datetime import date
import html
import json
from pathlib import Path
import re

try:
    from .site_brand import SITE_STYLES_VERSION, render_brand_link
except ImportError:
    from site_brand import SITE_STYLES_VERSION, render_brand_link

BRIEFING_SERIES = {"daily-quantum", "weekly-review"}
PUBLIC_FIELDS = ("id", "date", "series", "title", "title_en", "summary", "summary_en", "tags", "language", "href")


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def briefing_documents(documents: list[dict], prefix: str = "") -> list[dict]:
    """Do not serialize intake metadata or fields added by another document type."""
    result = []
    for source in documents:
        if source["series"] not in BRIEFING_SERIES:
            continue
        doc = {key: source[key] for key in PUBLIC_FIELDS if key in source}
        doc["href"] = prefix + doc["href"]
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
            topic_label = (f"{len(issues)} briefings: " if en else f"브리핑 {len(issues)}건: ") + "; ".join(doc["title"] for doc in issues)
            label = f"{iso} · " + (topic_label if issues else ("No registered briefing" if en else "등록된 브리핑 없음"))
            links = "".join(f'<a href="{escape(doc["href"])}" lang="{escape(doc["language"])}" target="_blank" rel="noopener" title="{escape(doc["title"])}">{escape(doc["title"])}</a>' for doc in issues)
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
        cards.append(f'<article class="briefing-detail-issue"><h4 lang="{escape(doc["language"])}"><a href="{escape(doc["href"])}" target="_blank" rel="noopener">{escape(doc["title"])}</a></h4><p lang="{summary_language}">{escape(summary)}</p><div class="briefing-tags">{tags}</div><a class="briefing-read" href="{escape(doc["href"])}" target="_blank" rel="noopener">{"Read PDF" if en else "브리핑 읽기"} ↗</a></article>')
    return "".join(cards)


def render_briefings(documents: list[dict], base_url: str, language: str = "ko", navigation: str = "", asset_version: str = "") -> str:
    en = language == "en"
    prefix = "../../" if en else "../"
    issues = briefing_documents(documents, prefix)
    months = calendar_months(issues)
    latest_month = months[0] if months else ""
    latest_date = issues[0]["date"] if issues else ""
    title = "Briefings" if en else "브리핑"
    description = ("Explore quantum briefings by publication date and topic. Choose a day on the calendar or browse the reading list."
                   if en else "날짜별로 양자 연구의 흐름을 살펴봅니다. 달력에서 발행일과 주제를 확인하거나, 목록에서 읽을 브리핑을 찾으세요.")
    canonical = base_url + "briefings/" + ("en/" if en else "")
    options = "".join(f'<option value="{month}">{month_label(month, language)}</option>' for month in months)
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] if en else list("월화수목금토일")
    headers = "".join(f'<th scope="col">{name}</th>' for name in weekdays)
    rows = []
    for doc in issues:
        summary = (doc.get("summary_en") or doc["summary"]) if en else doc["summary"]
        summary_language = "en" if en and doc.get("summary_en") else doc["language"]
        searchable = " ".join(str(doc.get(key, "")) for key in ("title", "title_en", "summary", "summary_en", "date")) + " " + " ".join(doc["tags"])
        tags = "".join(f'<span>{escape(tag)}</span>' for tag in doc["tags"])
        series = ("Weekly review" if en else "주간 브리핑") if doc["series"] == "weekly-review" else "Daily Quantum Brief"
        pdf_language = ({"ko": "Korean PDF", "en": "English PDF"} if en else {"ko": "한국어 PDF", "en": "영어 PDF"})[doc["language"]]
        rows.append(f'''<article class="briefing-row" data-id="{escape(doc['id'])}" data-date="{escape(doc['date'])}" data-search="{escape(searchable)}">
          <div class="briefing-date"><time datetime="{doc['date']}">{doc['date']}</time><span>{series}</span></div>
          <div class="briefing-row-body"><h3 lang="{escape(doc['language'])}"><a href="{escape(doc['href'])}" target="_blank" rel="noopener">{escape(doc['title'])}</a></h3><p lang="{summary_language}">{escape(summary)}</p><div class="briefing-tags">{tags}</div></div>
          <div class="briefing-row-actions"><span>{pdf_language}</span><a href="{escape(doc['href'])}" target="_blank" rel="noopener">{'Read PDF' if en else '읽기'} ↗</a><a href="{escape(doc['href'])}" download>{'Download' if en else '다운로드'} ↓</a></div>
        </article>''')
    payload = json.dumps({"documents": issues, "months": months, "latest_month": latest_month}, ensure_ascii=False, separators=(",", ":"))
    # Raw text script elements do not honor HTML entities. Escape their delimiters.
    payload = payload.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    empty_message = "No briefings have been published yet." if en else "아직 등록된 브리핑이 없습니다."
    calendar_section = f'''<section class="briefing-calendar-wrap" aria-labelledby="briefing-calendar-title">
        <div class="briefing-calendar-heading"><button id="briefing-prev" type="button" aria-label="{'Previous month' if en else '이전 달'}"{' disabled' if len(months) < 2 else ''}>←</button><h2 id="briefing-calendar-title">{month_label(latest_month, language)}</h2><button id="briefing-next" type="button" aria-label="{'Next month' if en else '다음 달'}" disabled>→</button></div>
        <p class="briefing-calendar-help">{'Select a date to see its topics below. Topic links open the PDF.' if en else '날짜를 선택하면 주제가 표시됩니다. 제목을 누르면 PDF를 읽을 수 있습니다.'}</p>
        <table class="briefing-calendar" aria-labelledby="briefing-calendar-title"><thead><tr>{headers}</tr></thead><tbody id="briefing-calendar">{render_calendar(issues, latest_month, language)}</tbody></table>
        <p class="briefing-calendar-legend"><span aria-hidden="true">●</span> {'Published briefing · blank dates have no registered issue' if en else '브리핑 발행일 · 빈 날짜는 등록된 문서가 없습니다'}</p>
      </section>''' if months else f'<p class="briefing-detail-empty">{empty_message}</p>'
    detail = render_detail([doc for doc in issues if doc["date"] == latest_date], language)
    return f'''<!doctype html><html lang="{language}"><head>
      <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{title} | AI Tech Review Letters</title><meta name="description" content="{description}">
      <link rel="canonical" href="{canonical}">
      <link rel="alternate" hreflang="ko" href="{base_url}briefings/"><link rel="alternate" hreflang="en" href="{base_url}briefings/en/"><link rel="alternate" hreflang="x-default" href="{base_url}briefings/">
      <meta property="og:type" content="website"><meta property="og:title" content="{title}"><meta property="og:description" content="{description}"><meta property="og:url" content="{canonical}">
      <link rel="stylesheet" href="{prefix}assets/site.css?v={SITE_STYLES_VERSION}"><link rel="stylesheet" href="{prefix}assets/archive.css?v={asset_version}"><link rel="stylesheet" href="{prefix}assets/briefings.css?v={asset_version}">
      </head><body class="briefings-page">
      <header class="site-header"><nav class="topbar" aria-label="{'Main navigation' if en else '주요 링크'}">{render_brand_link(prefix)}<span class="topbar-links"><a href="{prefix}methods/">{'Editorial methods' if en else '작성·검증 원칙'}</a><a href="{'../' if en else 'en/'}" lang="{'ko' if en else 'en'}" hreflang="{'ko' if en else 'en'}">{'한국어' if en else 'English'}</a></span></nav>
      {navigation}<section class="briefing-hero"><p class="section-kicker">Day by day · Quantum research</p><h1>{title}</h1><p>{description}</p><div class="briefing-hero-meta"><span>{str(len(issues)) + ' published briefings' if en else str(len(issues)) + '건의 브리핑'}</span>{f'<span>{"Latest issue" if en else "최근 발행"} <time datetime="{latest_date}">{latest_date}</time></span>' if latest_date else ''}<a href="#briefing-board">{'Browse list' if en else '목록으로 보기'} ↓</a></div></section></header>
      <main>
      <div class="briefing-tools" role="search">
        <label><span>{'Publication month' if en else '발행 월'}</span><select id="briefing-month"{' disabled' if not months else ''}>{options}</select></label>
        <label class="briefing-search"><span>{'Search topics' if en else '주제 검색'}</span><input id="briefing-search" type="search" placeholder="{'Title, keyword or date…' if en else '제목, 키워드, 날짜로 검색…'}" autocomplete="off"></label>
        <label class="briefing-scope"><input id="briefing-all-months" type="checkbox"><span>{'All months' if en else '전체 기간'}</span></label><button type="button" id="briefing-reset">{'Reset' if en else '초기화'}</button>
      </div>
      <div class="briefing-layout">{calendar_section}<section class="briefing-detail" id="briefing-day-panel" aria-labelledby="briefing-day-heading"><p class="section-kicker">{'Selected day / preview' if en else '날짜별 브리핑'}</p><h3 id="briefing-day-heading">{latest_date or ('No issues yet' if en else '발행 대기')}</h3><div id="briefing-day-content">{detail}</div></section></div>
      <section class="briefing-board" id="briefing-board" aria-labelledby="briefing-board-title"><div class="briefing-board-heading"><div><p class="section-kicker">Reading list</p><h2 id="briefing-board-title">{'Briefing list' if en else '브리핑 목록'}</h2><p id="briefing-filter-label">{'Newest first' if en else '최신 발행순'}</p></div><button type="button" id="briefing-clear-day" hidden>{'Show whole month' if en else '월 전체 보기'}</button></div>
        <p id="briefing-count" role="status">{len(issues)} {'briefings' if en else '건의 브리핑'}</p><div id="briefing-list">{''.join(rows)}</div><div id="briefing-empty" class="briefing-empty"{' hidden' if issues else ''}><p>{'No matching briefings. Try another month or search all months.' if en else '조건에 맞는 브리핑이 없습니다. 다른 달을 선택하거나 전체 기간으로 검색해 보세요.'}</p></div>
        <noscript><p>{'All registered briefings are listed. Calendar selection and search require JavaScript.' if en else '전체 브리핑을 최신순으로 표시합니다. 날짜 선택과 검색은 JavaScript를 켜면 사용할 수 있습니다.'}</p></noscript>
      </section><footer class="archive-note"><p>{'Dates follow each document’s publication date. Topics and PDFs retain their original language. Only publicly registered issues appear here.' if en else '달력은 문서에 표기된 발행일 기준입니다. 공개 등록된 브리핑만 표시하며, 각 PDF는 발행 당시의 내용으로 보관합니다.'}</p><a href="{prefix}archive/{'en/' if en else ''}">{'All-document archive' if en else '전체 자료 아카이브'} →</a></footer>
      </main><script type="application/json" id="briefing-data">{payload}</script><script src="{prefix}assets/briefings.js?v={asset_version}" defer></script>
      </body></html>'''


def validate_briefings(site_dir: Path, documents: list[dict]) -> list[str]:
    errors = []
    root = site_dir / "briefings"
    actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    if actual != {"index.html", "en/index.html"}:
        errors.append("briefing output differs from allowlist")
    for lang, prefix, relative in (("ko", "../", "index.html"), ("en", "../../", "en/index.html")):
        page = root / relative
        if not page.is_file():
            errors.append(f"missing briefing page: {relative}")
            continue
        text = page.read_text(encoding="utf-8")
        match = re.search(r'<script type="application/json" id="briefing-data">(.*?)</script>', text, re.S)
        try:
            payload = json.loads(match.group(1)) if match else None
        except json.JSONDecodeError:
            payload = None
        expected = briefing_documents(documents, prefix)
        if payload != {"documents": expected, "months": calendar_months(expected), "latest_month": calendar_months(expected)[0] if expected else ""}:
            errors.append(f"briefing data differs from public registry: {relative}")
        for doc in expected:
            if f'href="{escape(doc["href"])}"' not in text:
                errors.append(f"briefing PDF absent from {relative}: {doc['id']}")
    for name in ("briefings.css", "briefings.js"):
        source = Path(__file__).parent / "assets" / name
        output = site_dir / "assets" / name
        if not output.is_file() or output.read_bytes() != source.read_bytes():
            errors.append(f"briefing asset missing or changed: {name}")
    return errors
