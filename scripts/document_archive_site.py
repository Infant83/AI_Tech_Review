"""Build a public library from reviewed PDFs and official external book links."""
from __future__ import annotations

import hashlib
import html
import json
import posixpath
import re
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlencode

try:
    from .briefing_site import render_briefings, validate_briefings
    from .site_brand import SITE_STYLES_VERSION, render_brand_link
except ImportError:
    from briefing_site import render_briefings, validate_briefings
    from site_brand import SITE_STYLES_VERSION, render_brand_link

SERIES = {
    "daily-quantum": ("Daily Quantum Review", "Daily Quantum Review"),
    "weekly-review": ("주간 리뷰", "Weekly reviews"),
    "article": ("수시 아티클", "Articles"),
    "lecture-notes": ("렉처 노트", "Lecture notes"),
    "external-book": ("외부 서적", "External books"),
}
LIBRARY_ASSET_VERSION = "20261106-compact-series"

# The shared reader is application code, not a course or an article. Never copy
# a source directory recursively: it may also contain tests or private notes.
LECTURE_READER_SOURCE = Path(__file__).resolve().parents[1] / ".automation/lecture-reader"
LECTURE_READER_HREF = "lectures/reader/"
LECTURE_READER_FILES = (
    "index.html", "reader.css", "reader.mjs", "ink-core.mjs", "storage.mjs",
    "cloud.mjs", "cloud-core.mjs", "cloud.css",
)

# Reviewed, self-contained study sites. Never discover or copy a topic folder.
LECTURE_BUNDLES = {
    "2026-11-05-classiq-qae-l003-notes-ko": {
        "source": "2026-11-05_classiq-qae-onboarding/dist",
        "href": "lectures/classiq-qae-onboarding/",
        "unit_registry": "unit-registry.json",
        "start_anchor": "study-guide",
        "navigation": (("study-guide", "학습 안내"), ("units", "회차별 학습"), ("practice", "별도 재계산"), ("references", "출처")),
        "publication_note": (
            "2026-11-05 · 책임 편집자 김현중 · AI 보조 OpenAI Codex. "
            "public_pdf_qa/auth_audit가 세 회차의 자료 확인·공개판 정제·웹 학습 입구·20개 부분검산을 담당하고 root가 통합·게재한다. "
            "Classiq 공식 강의가 아닌 자체 집필 과정이며, 원판 ZIP과 원판의 검증 전체를 이번에 재실행한 자료가 아니다. "
            "영문 입구는 한국어 PDF 세 회차의 안내다."
        ),
        "files": (
            "index.html", "en/index.html", "notes.css", "notes.pdf", "unit-registry.json",
            "2026-11-01-classiq-qae-l001-notes-ko.pdf",
            "2026-11-03-classiq-qae-l002-notes-ko.pdf",
            "2026-11-05-classiq-qae-l003-notes-ko.pdf",
            "labs/reference_checks.py", "labs/results/reference-checks.json",
        ),
    },
    "2026-11-04-quantum-computing-applications-lecture-notes-ko": {
        "source": "2026-11-04_quantum-computing-applications-lecture/dist",
        "href": "lectures/quantum-computing-applications/",
        "catalog_online": False,
        "start_anchor": "book-toc",
        "navigation": (("book-toc", "목차"), ("answers", "문제 해설"), ("references", "출처")),
        "publication_note": (
            "2026-11-04 · 책임 편집자 김현중 · AI 보조 OpenAI Codex. "
            "root가 공개판 정제·게재를, public_pdf_qa가 별도의 원본 114쪽 출력·출처·대표 식 검토를 담당했다. "
            "내부 대화와 전달 경위를 제외하고 과학 내용·수식·문제·해설을 보존했다. "
            "원판의 소스 ZIP 전체와 188개 검증 조건을 이번 등록에서 독립 재실행한 것은 아니다. "
            "실제 QPU·분자 실험이나 사람의 문장별 심사를 수행한 것으로 표시하지 않는다. "
            "영문 목록은 이 한국어 자료의 안내다."
        ),
        "files": ("index.html", "notes.pdf"),
    },
    "2026-10-20-quantum-machine-learning-lecture-notes-ko": {
        "source": "2026-10-20_quantum-machine-learning-lecture-series/dist",
        "href": "lectures/quantum-machine-learning/",
        "files": (
            "index.html", "notes.css", "notes.pdf",
            "assets/qml-sans-regular.woff2", "assets/qml-sans-bold.woff2",
            "assets/font-OFL.txt", "assets/figure-manifest.json",
            "gradient-variance.svg", "shot-error.svg", "signal-attenuation.svg",
            "labs/qml_labs.py", "labs/pennylane_compare.py", "labs/requirements.txt",
            "labs/requirements-pennylane.txt", "labs/sdk-lock.txt",
            "labs/qpu_submission_template.json", "labs/results/reference-results.json",
            "labs/results/pennylane-results.json",
        ),
    },
    "2026-10-22-classiq-talk-series-notes-ko": {
        "source": "2026-10-22_classiq-talk-series/dist",
        "href": "lectures/classiq-talk-series/",
        "start_anchor": "chapter-0",
        "navigation": (
            ("chapter-0", "학습 시작 안내"),
            ("chapter-6", "한영 용어집"),
            ("chapter-7", "복습 질문과 풀이"),
        ),
        "publication_note": (
            "2026-10-22 · OpenAI Codex의 root가 웹 게재를 통합하고, "
            "publish_audit가 공개 자산과 아카이브 연결을 독립 검토했다. "
            "다시보기 정리·수학 대조·도식과 발표 화면 검토의 역할과 범위는 본문 작성 공개를 따른다. "
            "독립 보충 해설과 손계산은 원발표와 구분해 수록했다. "
            "영문 목록은 한국어 학습 자료의 안내이며 영어 번역본이 아니다."
        ),
        "files": (
            "index.html", "notes.css", "notes.pdf", "font-OFL.txt",
            "assets/qml-sans-regular.woff2", "assets/qml-sans-bold.woff2",
            "figures/manifest.json",
            "figures/concepts/01-platform-workflow.svg",
            "figures/concepts/02-grover-geometry.svg",
            "figures/concepts/03-qaoa-feasible-subspace.svg",
            "figures/concepts/04-payoff-probability-encoding.svg",
            "figures/concepts/05-iqae-adaptive-loop.svg",
            "figures/concepts/06-resource-scope-tradeoffs.svg",
            "figures/screens/platform-skills.png",
            "figures/screens/platform-grover-histogram.png",
            "figures/screens/platform-qaoa-standard.png",
            "figures/screens/platform-qaoa-comparison.png",
            "figures/screens/platform-hardware.png",
            "figures/screens/platform-ft-layout.png",
            "figures/screens/platform-encoding-table.png",
            "figures/screens/finance-pyomo-model.png",
            "figures/screens/finance-qaoa-settings.png",
            "figures/screens/finance-cudaq-cpu.png",
            "figures/screens/finance-qaoa-output.png",
            "figures/screens/finance-option-payoff.png",
            "figures/screens/finance-iqae-output.png",
        ),
    },
}


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def lecture_reader_href(document_id: str | None = None, *, prefix: str = "", language: str = "ko") -> str:
    query = {"id": document_id} if document_id else {"library": "1"}
    if language == "en":
        query["lang"] = "en"
    return prefix + LECTURE_READER_HREF + "?" + urlencode(query)


def lecture_reader_asset_hashes() -> dict[str, str | None]:
    """Return application paths and the exact, checksum-pinned vendor map."""
    manifest_path = LECTURE_READER_SOURCE / "vendor/manifest.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("Missing or symlinked lecture reader vendor manifest")
    try:
        payload = manifest_path.read_bytes()
        manifest = json.loads(payload)
    except (OSError, ValueError) as exc:
        raise ValueError("Invalid lecture reader vendor manifest") from exc
    if (not isinstance(manifest, dict) or set(manifest) != {"pdfjs_dist", "pdf_lib", "simplewebauthn_browser", "source_registry", "integrity", "files"}
            or any(not isinstance(manifest.get(key), str) or not manifest[key].strip()
                   for key in ("pdfjs_dist", "pdf_lib", "simplewebauthn_browser", "source_registry", "integrity"))
            or manifest["source_registry"] != "https://registry.npmjs.org/"
            or not isinstance(manifest["files"], dict) or not 1 <= len(manifest["files"]) <= 400):
        raise ValueError("Invalid lecture reader vendor manifest")
    assets = {name: None for name in LECTURE_READER_FILES}
    assets["vendor/manifest.json"] = hashlib.sha256(payload).hexdigest()
    for name, checksum in manifest["files"].items():
        if (not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+(?:[./-][A-Za-z0-9_-]+)*", name)
                or any(part in {".", ".."} for part in name.split("/"))
                or Path(name).suffix not in {".mjs", ".js", ".txt", ".bcmap", ".bin", ".pfb", ".ttf", ".wasm"}
                or not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum)):
            raise ValueError("Invalid lecture reader vendor path or checksum")
        assets["vendor/" + name] = checksum
    return assets


def stage_lecture_reader(staging: Path) -> Path:
    source = LECTURE_READER_SOURCE
    destination = staging / LECTURE_READER_HREF
    if source.is_symlink() or not source.is_dir():
        raise ValueError("Missing or symlinked lecture reader source")
    for name, checksum in lecture_reader_asset_hashes().items():
        path = source / name
        if (path.is_symlink() or not path.is_file()
                or any(parent.is_symlink() for parent in path.parents if parent != source and source in parent.parents)
                or not path.resolve().is_relative_to(source.resolve())):
            raise ValueError(f"Missing or symlinked lecture reader asset: {name}")
        if checksum and hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
            raise ValueError(f"Lecture reader vendor checksum mismatch: {name}")
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    return destination


def validate_lecture_reader(site_dir: Path, *, required: bool = True) -> list[str]:
    root = site_dir / LECTURE_READER_HREF
    if not root.exists():
        return ["missing shared lecture reader"] if required else []
    if root.is_symlink():
        return ["symlinked shared lecture reader"]
    try:
        assets = lecture_reader_asset_hashes()
    except ValueError as exc:
        return [str(exc)]
    actual = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    errors = []
    if actual != set(assets):
        errors.append("shared lecture reader output differs from allowlist")
    for name in actual & set(assets):
        path, source = root / name, LECTURE_READER_SOURCE / name
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != root and root in parent.parents):
            errors.append(f"symlinked lecture reader asset: {name}")
        elif not source.is_file() or path.read_bytes() != source.read_bytes():
            errors.append(f"lecture reader asset differs from approved source: {name}")
        elif assets[name] and hashlib.sha256(path.read_bytes()).hexdigest() != assets[name]:
            errors.append(f"lecture reader vendor checksum mismatch: {name}")
    return errors


def lecture_series_metadata(registry: dict, documents: list[dict], primary_id: str) -> dict:
    """Derive a series display without changing PDF or publication identities."""
    if registry.get("format") != "ai-tech-review-course-registry":
        raise ValueError("Invalid lecture unit registry")
    fields = ("series_id", "title", "title_en", "summary", "summary_en")
    if not all(isinstance(registry.get(key), str) and registry[key].strip() for key in fields):
        raise ValueError("Missing lecture series display metadata")
    indexed = {doc["id"]: doc for doc in documents if doc["series"] == "lecture-notes"}
    units, seen = [], set()
    for unit in registry.get("units", []):
        identifier = unit.get("archive_id")
        document = indexed.get(identifier)
        if (not document or identifier in seen or unit.get("sha256") != document["sha256"]
                or unit.get("pdf") != Path(document["href"]).name
                or not re.fullmatch(r"L[0-9]+", unit.get("id", ""))
                or not isinstance(unit.get("public_pages"), int) or unit["public_pages"] < 1):
            raise ValueError("Lecture series unit differs from its registered PDF")
        seen.add(identifier)
        units.append({"number": unit["id"], "document_id": identifier, "title": unit["title"],
                      "title_en": unit["title_en"], "date": document["date"],
                      "pages": unit["public_pages"], "href": document["href"]})
    if primary_id not in seen or not units:
        raise ValueError("Lecture series is missing its registered primary PDF")
    return {**{key: registry[key] for key in fields}, "units": units}


def grouped_lectures(documents: list[dict]) -> list[dict]:
    lectures = [doc for doc in documents if doc["series"] == "lecture-notes"]
    members = {unit["document_id"] for doc in lectures for unit in doc.get("study_series", {}).get("units", [])}
    return [doc for doc in lectures if doc.get("study_series") or doc["id"] not in members]


def render_library_navigation(documents: list[dict], area: str, language: str = "ko", prefix: str = "") -> str:
    en = language == "en"
    count = len(grouped_lectures(documents))
    briefing_count = sum(doc["series"] in {"daily-quantum", "weekly-review"} for doc in documents)
    current = lambda key: ' aria-current="page"' if area == key else ""
    return (f'<nav class="hub-nav" aria-label="{"Site sections" if en else "콘텐츠 메뉴"}">'
            '<div class="hub-primary">'
            f'<a href="{prefix}index.html"{current("reviews")}>{"Review hub" if en else "리뷰허브"}</a>'
            f'<a href="{prefix}lectures/{"en/" if en else ""}"{current("lectures")}>{"Lecture notes" if en else "렉처 노트"}<span>{count}</span></a>'
            f'<a href="{prefix}briefings/{"en/" if en else ""}"{current("briefings")}>{"Briefings" if en else "브리핑"}<span>{briefing_count}</span></a>'
            '</div>'
            f'<a class="hub-utility" href="{prefix}archive/{"en/" if en else ""}"{current("archive")}>'
            f'{"All-document archive" if en else "전체 자료 아카이브"}<span>{len(documents)} PDF</span></a></nav>')


def render_learning_teaser(documents: list[dict]) -> str:
    lectures = grouped_lectures(documents)
    recent = "".join(
        f'<li><time datetime="{escape(doc["date"])}">{escape(doc["date"])}</time>'
        f'<a href="{escape(doc.get("study_href") or doc["href"])}">'
        f'{escape(doc.get("study_series", {}).get("title") or doc["title"])}</a></li>'
        for doc in lectures[:2]
    )
    return f'''<section class="archive-preview" aria-labelledby="learning-preview-title">
      <div><p class="section-kicker">Learn &amp; practice</p>
      <h2 id="learning-preview-title">읽은 개념을 직접 계산해 보세요.</h2>
      <p>단계별 설명과 수식, 예제와 실습으로 공부하는 렉처 노트입니다. 주제와 학습 방식에 맞춰 시작하세요.</p>
      <a class="archive-cta" href="lectures/">렉처 노트 <span>{len(lectures)}개 자료 →</span></a></div>
      <ul class="archive-recent">{recent}</ul>
    </section>'''


def render_archive(documents: list[dict], base_url: str, language: str = "ko", external_resources: list[dict] | None = None) -> str:
    en = language == "en"
    catalog = sorted(documents + (external_resources or []), key=lambda doc: (doc["date"], doc["id"]), reverse=True)
    prefix = "../../" if en else "../"
    pdf_prefix = "../files/" if en else "files/"
    current_url = base_url + "archive/" + ("en/" if en else "")
    title = "All-document archive" if en else "전체 자료 아카이브"
    description = ("Find preserved PDFs and official book resources by title, topic and date. Explore the Briefings calendar or study with Lecture notes."
                   if en else "발행한 PDF와 외부 서적의 공식 안내를 제목·주제·날짜로 찾습니다. 날짜별 소식은 브리핑에서, 주제별 학습은 렉처 노트에서 시작하세요.")
    counts = {key: sum(doc["series"] == key for doc in catalog) for key in SERIES}
    buttons = f'<button type="button" class="collection-button active" data-series="" aria-pressed="true">{"All resources" if en else "전체 자료"}<span>{len(catalog)}</span></button>'
    buttons += "".join(
        f'<button type="button" class="collection-button" data-series="{key}" aria-pressed="false">{labels[int(en)]}<span>{counts[key]}</span></button>'
        for key, labels in SERIES.items()
    )
    months = sorted({doc["date"][:7] for doc in catalog}, reverse=True)
    month_options = "".join(f'<option value="{month}">{month}</option>' for month in months)
    cards = []
    for doc in catalog:
        doc_title = doc.get("title_en") if en else doc["title"]
        doc_summary = doc.get("summary_en") if en else doc["summary"]
        doc_title = doc_title or doc["title"]
        doc_summary = doc_summary or doc["summary"]
        text_language = "en" if en and doc.get("title_en") else doc["language"]
        summary_language = "en" if en and doc.get("summary_en") else doc["language"]
        searchable = " ".join(str(doc.get(key, "")) for key in ("title", "title_en", "summary", "summary_en", "source_title")) + " " + " ".join(doc["tags"])
        if doc.get("author"):
            searchable += " " + doc["author"]
        tags = "".join(f'<span>{escape(tag)}</span>' for tag in doc["tags"])
        if doc["series"] == "external-book":
            native = ({"ko": "Korean book", "en": "English book"} if en else {"ko": "한국어 서적", "en": "영어 서적"})[doc["language"]]
            cards.append(f'''<article id="{escape(doc['id'])}" class="document-card" data-series="external-book" data-date="{escape(doc['date'])}" data-search="{escape(searchable)}">
              <div class="document-meta"><span>{SERIES['external-book'][int(en)]}</span><time datetime="{escape(doc['date'])}">{'Added' if en else '등록'} {escape(doc['date'])}</time></div>
              <h2 lang="{text_language}"><a href="{escape(doc['book_url'])}" target="_blank" rel="noopener">{escape(doc_title)}</a></h2>
              <p class="document-author">{escape(doc['author'])} · {native}</p>
              <p class="document-summary" lang="{'en' if en else 'ko'}">{escape(doc_summary)}</p>
              <div class="tags">{tags}</div>
              <p class="external-book-note">{'Get the PDF from the author’s site. This archive does not redistribute it.' if en else 'PDF는 저자 사이트에서 받으세요. 이 아카이브에서는 재배포하지 않습니다.'}</p>
              <div class="document-footer"><div><a href="{escape(doc['author_url'])}" target="_blank" rel="noopener">{'Author page' if en else '저자 페이지'} ↗</a><a href="{escape(doc['book_url'])}" target="_blank" rel="noopener">{'Book & download information' if en else '책·다운로드 안내'} ↗</a></div></div>
            </article>''')
            continue
        pdf = f'{pdf_prefix}{escape(doc["id"])}.pdf'
        study = f'{prefix}{escape(doc["study_href"])}' if doc.get("study_href") else ""
        title_link = f'<a href="{study}">{escape(doc_title)}</a>' if study else f'<a href="{pdf}" target="_blank" rel="noopener">{escape(doc_title)}</a>'
        study_link = f'<a href="{study}">{"Korean study notes" if en else "강의 노트 읽기"} →</a>' if study else ""
        annotate_link = (f'<a href="{escape(lecture_reader_href(doc["id"], prefix=prefix, language=language))}">'
                         f'{"Read &amp; annotate" if en else "필기하며 읽기"} →</a>') if doc["series"] == "lecture-notes" else ""
        native_language = ({"ko": "Korean PDF", "en": "English PDF"} if en else {"ko": "한국어 PDF", "en": "영어 PDF"})[doc["language"]]
        cards.append(f'''<article class="document-card" data-series="{escape(doc['series'])}" data-date="{escape(doc['date'])}" data-search="{escape(searchable)}">
          <div class="document-meta"><span>{SERIES[doc['series']][int(en)]}</span><time datetime="{escape(doc['date'])}">{escape(doc['date'])}</time></div>
          <h2 lang="{text_language}">{title_link}</h2>
          <p class="document-summary" lang="{summary_language}">{escape(doc_summary)}</p>
          <div class="tags">{tags}</div>
          <div class="document-footer"><span>{native_language} · {doc['size_bytes'] / 1024:.0f} KB</span>
          <div>{annotate_link}{study_link}<a href="{pdf}" target="_blank" rel="noopener">{'Open PDF' if en else 'PDF 열기'} ↗</a><a href="{pdf}" download>{'Download' if en else '다운로드'} ↓</a></div></div>
        </article>''')
    latest = catalog[0]["date"] if catalog else "—"
    return f'''<!doctype html>
<html lang="{language}"><head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | AI Tech Review Letters</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{current_url}">
  <link rel="alternate" hreflang="ko" href="{base_url}archive/">
  <link rel="alternate" hreflang="en" href="{base_url}archive/en/">
  <link rel="alternate" hreflang="x-default" href="{base_url}archive/">
  <meta property="og:type" content="website"><meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}"><meta property="og:url" content="{current_url}">
  <link rel="stylesheet" href="{prefix}assets/site.css?v={SITE_STYLES_VERSION}"><link rel="stylesheet" href="{prefix}assets/archive.css?v={LIBRARY_ASSET_VERSION}">
</head><body class="archive-page">
  <header class="site-header">
    <nav class="topbar" aria-label="{'Main navigation' if en else '주요 링크'}">
      {render_brand_link(prefix)}
      <span class="topbar-links"><a href="{prefix}methods/">{'Editorial methods' if en else '작성·검증 원칙'}</a><a href="{'../' if en else 'en/'}" lang="{'ko' if en else 'en'}" hreflang="{'ko' if en else 'en'}">{'한국어' if en else 'English'}</a></span>
    </nav>
    {render_library_navigation(documents, "archive", language, prefix)}
    <section class="hero archive-hero"><p class="eyebrow">Reference library</p><h1>{title}</h1><p class="lead">{description}</p>
      <p class="archive-caption">{'Latest addition' if en else '최근 등록'} <time>{latest}</time> <span>·</span> {'Preserved PDFs & official book links' if en else 'PDF 보관본 · 서적 공식 링크'}</p>
    </section>
  </header>
  <main>
    <section class="archive-browser" aria-label="{'Find documents' if en else '문서 찾기'}">
      <div class="collection-filters" aria-label="{'Collections' if en else '문서 분류'}">{buttons}</div>
      <p class="collection-description" id="collection-description">{'Daily Quantum Review collects the Daily Quantum Brief series alongside weekly reviews, articles and the latest supplied lecture notes. External books link to their authors and official book pages; their dates indicate catalog registration.' if en else 'Daily Quantum Review에는 Daily Quantum Brief 시리즈를 모았습니다. 주간 리뷰, 수시 PDF와 확인된 최신 렉처 노트를 보관합니다. 외부 서적은 저자·책 공식 안내로 연결하며 날짜는 아카이브 등록일입니다.'}</p>
      <div class="archive-controls">
        <label class="archive-search"><span>{'Search documents' if en else '문서 검색'}</span><input id="archive-search" type="search" placeholder="{'Title, topic, keyword…' if en else '제목, 주제, 키워드로 검색…'}" autocomplete="off"></label>
        <label><span>{'Month' if en else '발행·등록 월'}</span><select id="archive-month"><option value="">{'All months' if en else '전체 기간'}</option>{month_options}</select></label>
        <label><span>{'Sort' if en else '정렬'}</span><select id="archive-sort"><option value="newest">{'Newest first' if en else '최신순'}</option><option value="oldest">{'Oldest first' if en else '오래된순'}</option></select></label>
      </div>
      <div class="archive-results-bar"><p id="archive-result-count" role="status">{len(catalog)} {'resources' if en else '건의 자료'}</p><button type="button" id="archive-reset">{'Reset filters' if en else '필터 초기화'}</button></div>
      <div class="document-grid" id="document-grid">{''.join(cards)}</div>
      <div id="archive-empty" class="archive-empty" hidden><h2>{'No matching documents' if en else '조건에 맞는 문서가 없습니다'}</h2><p>{'Try another keyword or clear the filters. Empty collections will appear here when documents are added.' if en else '검색어나 기간을 바꾸거나 필터를 초기화해 보세요. 아직 비어 있는 분류는 문서가 등록되면 이곳에 표시됩니다.'}</p></div>
      <button type="button" class="archive-more" id="archive-more" hidden>{'Show more documents' if en else '문서 더 보기'} ↓</button>
      <noscript><p>{'All documents are shown below. Enable JavaScript to search and filter.' if en else '전체 문서를 표시합니다. 검색과 필터는 JavaScript를 켜면 사용할 수 있습니다.'}</p></noscript>
    </section>
    <footer class="archive-note"><p>{'Archived PDFs are preserved in their original language. The English catalog describes the collection; it does not imply an English PDF translation.' if en else '문서는 발행 당시의 언어와 내용으로 보관합니다. 아카이브 등록은 본문의 연구 결과를 새로 검증하거나 독립 재현했다는 뜻이 아닙니다.'}</p><a href="{prefix}archive-manifest.json">{'Archive data (JSON)' if en else '아카이브 데이터 (JSON)'} ↗</a></footer>
  </main>
  <script src="{prefix}assets/archive.js?v={LIBRARY_ASSET_VERSION}" defer></script>
</body></html>'''


def render_lecture_series(doc: dict, prefix: str, language: str) -> str:
    en = language == "en"
    series = doc["study_series"]
    title = series["title_en" if en else "title"]
    summary = series["summary_en" if en else "summary"]
    course = prefix + doc["study_href"] + ("en/" if en else "")
    units = []
    for unit in series["units"]:
        number = escape(unit["number"])
        reader = escape(lecture_reader_href(unit["document_id"], prefix=prefix, language=language))
        pdf = escape(prefix + unit["href"])
        pages_label = f"{unit['pages']} pages" if en else f"{unit['pages']}쪽"
        units.append(f'''<li data-lecture-unit="{number}">
          <h3><span>{number}</span> {escape(unit['title_en' if en else 'title'])}</h3>
          <p class="lecture-unit-meta"><time datetime="{escape(unit['date'])}">{escape(unit['date'])}</time> · PDF {pages_label}</p>
          <div class="lecture-actions"><a class="lecture-primary" href="{reader}" aria-label="{number} {'Read and annotate' if en else '필기하며 읽기'}">{'Annotate' if en else '필기'} →</a>
          <a class="lecture-secondary" href="{pdf}" target="_blank" rel="noopener" aria-label="{number} {'Open PDF' if en else 'PDF 열기'}">PDF ↗</a>
          <a class="lecture-secondary" href="{pdf}" download aria-label="{number} {'Download PDF' if en else 'PDF 다운로드'}">{'Download' if en else '다운로드'} ↓</a></div>
        </li>''')
    page_count = sum(u['pages'] for u in series['units'])
    facts = f"{len(units)} units · PDF {page_count} pages" if en else f"{len(units)}회차 · PDF {page_count}쪽"
    return f'''<article class="lecture-card lecture-featured lecture-series" data-lecture-series="{escape(series['series_id'])}">
      <details class="lecture-series-disclosure"><summary>
      <div class="lecture-meta"><span class="lecture-format">{'PDF lecture series' if en else 'PDF 강의 시리즈'}</span><span>{'Korean' if en else '한국어'}</span><time datetime="{escape(doc['date'])}">{escape(doc['date'])}</time></div>
      <h2>{escape(title)}</h2>
      <div class="lecture-series-summary"><span class="lecture-facts">{facts}</span><span class="lecture-series-toggle"><span class="series-show">{'View units' if en else '회차 보기'}</span><span class="series-hide">{'Hide units' if en else '회차 접기'}</span><span class="series-chevron" aria-hidden="true"></span></span></div>
      </summary><p class="lecture-summary">{escape(summary)}</p>
      <ol class="lecture-units" aria-label="{'Series units' if en else '시리즈 회차'}">{''.join(units)}</ol>
      <a class="lecture-series-index" href="{escape(course)}">{'Series guide' if en else '자료 안내'} →</a></details>
    </article>'''


def render_lectures(documents: list[dict], base_url: str, language: str = "ko") -> str:
    en = language == "en"
    prefix = "../../" if en else "../"
    lectures = grouped_lectures(documents)
    pdf_count = sum(doc["series"] == "lecture-notes" for doc in documents)
    title = "Lecture notes" if en else "렉처 노트"
    description = ("Study concepts, work through derivations and practice with examples. Choose a series to begin."
                   if en else "개념을 읽고, 수식을 풀고, 예제와 실습으로 이해를 확인합니다. 공부할 주제를 골라 시작하세요.")
    canonical = base_url + "lectures/" + ("en/" if en else "")
    count_label = (f"{len(lectures)} resources · {pdf_count} PDFs" if en
                   else f"{len(lectures)}개 자료 · PDF {pdf_count}편")
    intros = {
        "2026-10-22-classiq-talk-series-notes-ko": (
            "Classiq의 다시보기 네 회를 따라 모델링·회로 합성·실행·결과 해석을 공부합니다. 실제 질의응답과 복습 풀이, 발표 화면과 개념 도식을 함께 수록했습니다.",
            "Study modeling, circuit synthesis, execution and interpretation through four Classiq replays, with the original Q&A, worked review questions, presentation screenshots and explanatory diagrams."),
        "2026-10-20-quantum-machine-learning-lecture-notes-ko": (
            "양자정보의 기초부터 모델 훈련과 최신 연구 읽기까지, 18개의 80분 단원으로 공부합니다. 수학 준비편과 단계별 유도, 예제·풀이·실습을 함께 제공합니다.",
            "Work from quantum-information foundations to model training and current research in 18 units of 80 minutes, with a mathematics primer, derivations, worked examples and labs."),
        "2026-10-16-zi-yang-meng-lecture-4": (
            "스핀 기저와 정확대각화, 벌집 격자 Hubbard 모형과 평균장 임계 현상을 다룹니다. 27쪽 최종 주석판이며, 강의 초반 13분이 누락된 기록을 바탕으로 재구성했습니다.",
            "Study spin bases, exact diagonalization and mean-field criticality in the honeycomb Hubbard model. This 27-page annotated reconstruction omits the first 13 minutes of the lecture."),
    }
    cards = []
    for doc in lectures:
        if doc.get("study_series"):
            cards.append(render_lecture_series(doc, prefix, language))
            continue
        study = prefix + doc["study_href"] if doc.get("study_href") else ""
        online = bool(study) and LECTURE_BUNDLES.get(doc["id"], {}).get("catalog_online", True)
        pdf = prefix + doc["href"]
        reader = escape(lecture_reader_href(doc["id"], prefix=prefix, language=language))
        doc_title = doc.get("title_en") if en else doc["title"]
        doc_title = doc_title or doc["title"]
        summary = intros.get(doc["id"], (doc["summary"], doc.get("summary_en") or doc["summary"]))[int(en)]
        title_language = "en" if en and doc.get("title_en") else doc["language"]
        summary_language = "en" if en and (doc.get("summary_en") or doc["id"] in intros) else doc["language"]
        format_label = ("Online notes + labs" if en else "온라인 노트 · 실습") if online else ("PDF lecture notes" if en else "PDF 강의 노트")
        if doc["id"] == "2026-10-22-classiq-talk-series-notes-ko" and study:
            format_label = "Illustrated online notes" if en else "온라인 노트 · 그림 해설"
        native = ({"ko": "Korean", "en": "English"} if en else {"ko": "한국어", "en": "영어"})[doc["language"]]
        stats = quick_links = ""
        if doc["id"] == "2026-10-20-quantum-machine-learning-lecture-notes-ko":
            metrics = ["18 units", "72 problems", "5 labs", "147-page PDF"] if en else ["18강", "풀이 72문제", "실습 5개", "PDF 147쪽"]
            stats = '<ul class="lecture-facts" aria-label="' + ("Learning materials" if en else "학습 자료 구성") + '">' + ''.join(f'<li>{escape(item)}</li>' for item in metrics) + '</ul>'
            if study:
                quick_links = '<div class="lecture-resources">' + ''.join(
                    f'<a href="{escape(study)}#{anchor}">{label} →</a>'
                    for anchor, label in [("doc-math-primer", "Mathematics primer" if en else "수학 준비편"),
                                          ("doc-glossary", "Bilingual glossary" if en else "한영 용어집"),
                                          ("doc-labs-readme", "Labs and code" if en else "실습과 코드")]) + '</div>'
        elif doc["id"] == "2026-10-22-classiq-talk-series-notes-ko":
            metrics = ["4 replays", "61-page PDF", "19 figures"] if en else ["다시보기 4회", "PDF 61쪽", "그림 19개"]
            stats = '<ul class="lecture-facts" aria-label="' + ("Learning materials" if en else "학습 자료 구성") + '">' + ''.join(f'<li>{escape(item)}</li>' for item in metrics) + '</ul>'
            if study:
                quick_links = '<div class="lecture-resources">' + ''.join(
                    f'<a href="{escape(study)}#{anchor}">{label} →</a>'
                    for anchor, label in [("chapter-1", "New Classiq platform" if en else "새 플랫폼"),
                                          ("chapter-2", "CUDA-Q finance" if en else "CUDA-Q 금융 응용"),
                                          ("chapter-3", "AI agents" if en else "AI 에이전트"),
                                          ("chapter-4", "Finance foundations" if en else "금융 기초"),
                                          ("chapter-7", "Review questions and solutions" if en else "복습 질문과 풀이")]) + '</div>'
        actions = f'<a class="lecture-primary" href="{reader}">{"Read &amp; annotate" if en else "필기하며 읽기"} →</a>'
        if online:
            start_anchor = LECTURE_BUNDLES.get(doc["id"], {}).get("start_anchor", "doc-study-guide")
            actions += f'<a class="lecture-secondary" href="{escape(study)}#{escape(start_anchor)}">{"Online notes" if en else "온라인 노트"} →</a>'
        actions += (f'<a class="lecture-secondary" href="{escape(pdf)}" target="_blank" rel="noopener">{"Read PDF" if en else "PDF 읽기"} ↗</a>'
                    f'<a class="lecture-secondary" href="{escape(pdf)}" download>{"Download" if en else "다운로드"} ↓</a>')
        cards.append(f'''<article class="lecture-card{' lecture-featured' if online else ''}">
          <div class="lecture-meta"><span class="lecture-format">{format_label}</span><span>{native}</span><time datetime="{escape(doc['date'])}">{escape(doc['date'])}</time></div>
          <h2 lang="{title_language}"><a href="{reader}">{escape(doc_title)}</a></h2>
          <p class="lecture-summary" lang="{summary_language}">{escape(summary)}</p>
          {stats}<div class="lecture-actions">{actions}</div>{quick_links}
        </article>''')
    if not cards:
        cards.append('<p class="lecture-empty">' + ("Lecture notes will appear here when a series is published." if en else "새 렉처 시리즈가 발행되면 이곳에서 공부를 시작할 수 있습니다.") + '</p>')
    return f'''<!doctype html><html lang="{language}"><head>
      <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{title} | AI Tech Review Letters</title><meta name="description" content="{description}">
      <link rel="canonical" href="{canonical}">
      <link rel="alternate" hreflang="ko" href="{base_url}lectures/">
      <link rel="alternate" hreflang="en" href="{base_url}lectures/en/">
      <link rel="alternate" hreflang="x-default" href="{base_url}lectures/">
      <meta property="og:type" content="website"><meta property="og:title" content="{title}">
      <meta property="og:description" content="{description}"><meta property="og:url" content="{canonical}">
      <link rel="stylesheet" href="{prefix}assets/site.css?v={SITE_STYLES_VERSION}"><link rel="stylesheet" href="{prefix}assets/archive.css?v={LIBRARY_ASSET_VERSION}">
      </head><body class="lectures-page">
      <header class="site-header">
        <nav class="topbar" aria-label="{'Main navigation' if en else '주요 링크'}">
          {render_brand_link(prefix)}
          <span class="topbar-links"><a href="{escape(lecture_reader_href(prefix=prefix, language=language))}">{'My study notes' if en else '내 학습 노트'}</a><a href="{prefix}methods/">{'Editorial methods' if en else '작성·검증 원칙'}</a><a href="{'../' if en else 'en/'}" lang="{'ko' if en else 'en'}" hreflang="{'ko' if en else 'en'}">{'한국어' if en else 'English'}</a></span>
        </nav>
        {render_library_navigation(documents, 'lectures', language, prefix)}
        <section class="lecture-hero"><p class="section-kicker">Study &amp; practice</p><h1>{title}</h1><p>{description}</p>
          <span class="lecture-count">{count_label}</span>
        </section>
      </header>
      <main><section class="lecture-list" aria-label="{'Choose learning material' if en else '학습 자료 선택'}">{''.join(cards)}</section>
        <footer class="lecture-note"><p>{'Each series retains its original language. The English catalog is a guide to the Korean notes.' if en else '회차별 PDF를 읽거나 필기하며 공부할 수 있습니다. 각 자료의 작성 범위와 출처는 PDF와 자료 안내에 남깁니다.'}</p>
        <a href="{prefix}archive/{'en/' if en else ''}">{'Find all preserved PDFs in the archive' if en else '전체 PDF 보관본 찾기'} →</a></footer>
      </main></body></html>'''


def stage_lecture_bundle(archive_dir: Path, staging: Path, document: dict, spec: dict,
                         base_url: str, decorate) -> Path:
    """Copy only reviewed assets, validating everything before replacing output."""
    try:
        from .archive_documents import _reject_symlink_components
    except ImportError:
        from archive_documents import _reject_symlink_components
    href = spec["href"]
    if not re.fullmatch(r"lectures/[a-z0-9]+(?:-[a-z0-9]+)*/", href):
        raise ValueError("Invalid lecture destination")
    source = archive_dir.parent / spec["source"]
    files = spec["files"]
    if not {"index.html", "notes.pdf"}.issubset(files) or len(set(files)) != len(files):
        raise ValueError("Lecture allowlist must contain index.html and notes.pdf without duplicates")
    destination = staging / href
    for name in files:
        if Path(name).is_absolute() or ".." in Path(name).parts:
            raise ValueError("Invalid lecture asset path")
        asset = source / name
        _reject_symlink_components(asset)
        if not asset.is_file():
            raise ValueError(f"Missing lecture asset: {name}")
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(asset, target)
    if (destination / "notes.pdf").read_bytes() != (archive_dir / document["file"]).read_bytes():
        raise ValueError("Lecture PDF differs from registered archive PDF")
    index = destination / "index.html"
    text = index.read_text(encoding="utf-8")
    canonical = base_url + href
    series = json.loads((destination / spec["unit_registry"]).read_text(encoding="utf-8")) if spec.get("unit_registry") else {}
    display_title = series.get("title") or document["title"]
    display_summary = series.get("summary") or document["summary"]
    metadata = (f'<link rel="canonical" href="{escape(canonical)}">'
                f'<meta property="og:type" content="article">'
                f'<meta property="og:title" content="{escape(display_title)}">'
                f'<meta property="og:description" content="{escape(display_summary)}">'
                f'<meta property="og:url" content="{escape(canonical)}">')
    prefix = posixpath.relpath(".", href.rstrip("/")) + "/"
    navigation_links = spec.get("navigation", (
        ("doc-study-guide", "학습 시작 안내"),
        ("doc-glossary", "한영 용어집"),
        ("doc-labs-readme", "실습과 코드"),
    ))
    if "navigation" in spec:
        anchors = {anchor for anchor, _label in navigation_links} | {spec.get("start_anchor", "doc-study-guide")}
        for anchor in anchors:
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", anchor) or f'id="{anchor}"' not in text:
                raise ValueError(f"Missing lecture navigation anchor: {anchor}")
    navigation = (f'<nav aria-label="테크리뷰 바로가기"><a href="{prefix}lectures/">← 렉처 노트 목록</a>'
                  + ''.join(f'<a href="#{escape(anchor)}">{escape(label)}</a>' for anchor, label in navigation_links)
                  + '</nav>')
    text = text.replace("</head>", metadata + "</head>", 1)
    sidebar = re.search(r'<aside\b[^>]*class="sidebar"[^>]*>', text)
    if sidebar:
        text = text[:sidebar.end()] + navigation + text[sidebar.end():]
    else:
        text = text.replace("<body>", "<body>" + navigation, 1)
    publication_text = spec.get("publication_note", (
        '2026-10-20 · OpenAI Codex의 root가 웹 게재를 통합하고, '
        'lecture_publish_audit가 공개 자산과 아카이브 연결을 독립 검토했다. '
        '강의 집필·수학 검토·실습 실행의 역할과 범위는 본문 작성 공개를 따른다. '
        '영문 목록은 한국어 학습 자료의 안내이며 영어 번역본이 아니다.'
    ))
    publication_note = ('<section class="document publication-note" aria-label="웹 게재 기록">'
                        f'<h2>웹 게재 기록</h2><p>{escape(publication_text)}</p></section>')
    text = text.replace("</main>", publication_note + "</main>", 1)
    text = decorate(text, prefix)
    index.write_text(text, encoding="utf-8")
    return destination


def publish_archive(archive_dir: Path, site_dir: Path, base_url: str, decorate) -> list[dict]:
    try:
        from .archive_documents import load_documents
        from .external_resources import load_external_resources
    except ImportError:
        from archive_documents import load_documents
        from external_resources import load_external_resources
    source_documents = load_documents(archive_dir)
    external_resources = load_external_resources(archive_dir)
    if {doc["id"] for doc in source_documents} & {item["id"] for item in external_resources}:
        raise ValueError("External resource id duplicates a PDF document")
    external_resources = [{key: value for key, value in item.items() if key != "public_reviewed"} for item in external_resources]
    documents = []
    for source in source_documents:
        payload = (archive_dir / source["file"]).read_bytes()
        doc = {key: value for key, value in source.items() if key not in {"file", "public_reviewed"}}
        doc.update(href=f'archive/files/{source["id"]}.pdf', size_bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        documents.append(doc)
    # Stage the complete allowlist before replacing the generated archive.
    with tempfile.TemporaryDirectory(prefix="document-archive-", dir=site_dir.parent) as temporary:
        temporary_root = Path(temporary)
        lecture_outputs = [(stage_lecture_reader(temporary_root), site_dir / LECTURE_READER_HREF)]
        for source, document in zip(source_documents, documents):
            spec = LECTURE_BUNDLES.get(source["id"])
            if spec:
                if source["series"] != "lecture-notes":
                    raise ValueError("Study bundles must belong to lecture-notes")
                staged = stage_lecture_bundle(archive_dir, temporary_root, source, spec, base_url, decorate)
                # Only derived, public fields leave the source registry.
                document["study_href"] = spec["href"]
                document["study_assets"] = {name: hashlib.sha256((staged / name).read_bytes()).hexdigest() for name in spec["files"]}
                if spec.get("unit_registry"):
                    registry = json.loads((staged / spec["unit_registry"]).read_text(encoding="utf-8"))
                    document["study_series"] = lecture_series_metadata(registry, documents, source["id"])
                lecture_outputs.append((staged, site_dir / spec["href"]))
        for lang, prefix in (("ko", "../"), ("en", "../../")):
            page = temporary_root / "lectures" / ("en/index.html" if lang == "en" else "index.html")
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(decorate(render_lectures(documents, base_url, lang), prefix), encoding="utf-8")
            page = temporary_root / "briefings" / ("en/index.html" if lang == "en" else "index.html")
            page.parent.mkdir(parents=True, exist_ok=True)
            navigation = render_library_navigation(documents, "briefings", lang, prefix)
            page.write_text(decorate(render_briefings(documents, base_url, lang, navigation, LIBRARY_ASSET_VERSION), prefix), encoding="utf-8")
        # Read all source assets before replacing any published output.
        briefing_assets = {name: (Path(__file__).parent / "assets" / name).read_text(encoding="utf-8") for name in ("briefings.css", "briefings.js")}
        staging = Path(temporary) / "archive"
        (staging / "files").mkdir(parents=True)
        (staging / "en").mkdir()
        for source in source_documents:
            shutil.copyfile(archive_dir / source["file"], staging / "files" / f'{source["id"]}.pdf')
        for lang, prefix in (("ko", "../"), ("en", "../../")):
            target = staging / ("en/index.html" if lang == "en" else "index.html")
            target.write_text(decorate(render_archive(documents, base_url, lang, external_resources), prefix), encoding="utf-8")
        target = site_dir / "archive"
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(staging), str(target))
        for staged, target in lecture_outputs:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(staged), str(target))
        for relative in ("index.html", "en/index.html"):
            target = site_dir / "lectures" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(temporary_root / "lectures" / relative, target)
        target = site_dir / "briefings"
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(temporary_root / "briefings"), str(target))
    (site_dir / "archive-manifest.json").write_text(json.dumps({"version": 1, "documents": documents, "external_resources": external_resources}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assets = site_dir / "assets"
    (assets / "archive.css").write_text(ARCHIVE_CSS.strip() + "\n", encoding="utf-8")
    (assets / "archive.js").write_text(ARCHIVE_JS.strip() + "\n", encoding="utf-8")
    for name, text in briefing_assets.items():
        (assets / name).write_text(text, encoding="utf-8")
    return documents


def validate_lecture_bundles(site_dir: Path, documents: list[dict]) -> list[str]:
    errors = []
    for document in documents:
        spec = LECTURE_BUNDLES.get(document["id"])
        if not spec:
            if document.get("study_href"):
                errors.append(f"unregistered study site: {document['id']}")
            continue
        if document.get("study_href") != spec["href"]:
            errors.append(f"missing lecture link: {document['id']}")
            continue
        root = site_dir / spec["href"]
        expected = set(spec["files"])
        actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        if actual != expected:
            errors.append(f"lecture output differs from allowlist: {document['id']}")
        hashes = document.get("study_assets", {})
        if set(hashes) != expected:
            errors.append(f"lecture asset hashes differ from allowlist: {document['id']}")
        for name in actual & expected:
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != hashes.get(name):
                errors.append(f"lecture asset checksum mismatch: {name}")
        if (root / "notes.pdf").is_file() and hashlib.sha256((root / "notes.pdf").read_bytes()).hexdigest() != document["sha256"]:
            errors.append(f"lecture PDF differs from archive: {document['id']}")
        if spec.get("unit_registry"):
            try:
                registry = json.loads((root / spec["unit_registry"]).read_text(encoding="utf-8"))
                if document.get("study_series") != lecture_series_metadata(registry, documents, document["id"]):
                    errors.append(f"lecture series metadata differs from registry: {document['id']}")
            except (OSError, ValueError, KeyError, TypeError):
                errors.append(f"invalid lecture series registry: {document['id']}")
    return errors


def validate_archive(site_dir: Path) -> list[str]:
    try:
        from .external_resources import validate_resources
    except ImportError:
        from external_resources import validate_resources
    errors = validate_lecture_reader(site_dir)
    manifest_path = site_dir / "archive-manifest.json"
    if not manifest_path.exists():
        return ["missing public archive manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    external_resources = manifest.get("external_resources", [])
    try:
        external_resources = validate_resources([{**item, "public_reviewed": True} for item in external_resources])
        if {doc["id"] for doc in manifest["documents"]} & {item["id"] for item in external_resources}:
            raise ValueError("External resource id duplicates a PDF document")
    except (ValueError, TypeError) as exc:
        errors.append(f"invalid public external resources: {exc}")
        external_resources = []
    errors.extend(validate_lecture_bundles(site_dir, manifest["documents"]))
    errors.extend(validate_briefings(site_dir, manifest["documents"]))
    for relative in ("index.html", "en/index.html"):
        if not (site_dir / "lectures" / relative).is_file():
            errors.append(f"missing lecture catalog: {relative}")
    expected_files = {"index.html", "en/index.html"}
    for doc in manifest["documents"]:
        path = site_dir / doc["href"]
        if not path.is_file():
            errors.append(f"missing archive PDF: {doc['id']}")
            continue
        payload = path.read_bytes()
        if len(payload) != doc["size_bytes"] or hashlib.sha256(payload).hexdigest() != doc["sha256"]:
            errors.append(f"archive PDF checksum mismatch: {doc['id']}")
        expected_files.add(f"files/{doc['id']}.pdf")
    actual_files = {path.relative_to(site_dir / "archive").as_posix() for path in (site_dir / "archive").rglob("*") if path.is_file()}
    if actual_files != expected_files:
        errors.append(f"archive output differs from allowlist: {sorted(actual_files ^ expected_files)}")
    for relative in ("index.html", "en/index.html"):
        path = site_dir / "archive" / relative
        if not path.exists():
            errors.append(f"missing archive page: {relative}")
        else:
            page = path.read_text(encoding="utf-8")
            for doc in manifest["documents"]:
                if f"files/{doc['id']}.pdf" not in page:
                    errors.append(f"archive PDF absent from {relative}: {doc['id']}")
            for item in external_resources:
                for expected in (f'id="{escape(item["id"])}"', f'href="{escape(item["author_url"])}"', f'href="{escape(item["book_url"])}"'):
                    if expected not in page:
                        errors.append(f"external book link absent from {relative}: {item['id']}")
    return errors


ARCHIVE_CSS = '''
.hub-nav { display:flex; align-items:center; justify-content:space-between; gap:14px; padding:12px 0 20px; flex-wrap:wrap; border-bottom:1px solid var(--line); }
.hub-primary { display:flex; gap:6px; flex-wrap:wrap; }
.hub-primary a { display:inline-flex; align-items:center; min-height:44px; text-decoration:none; padding:10px 18px; border-radius:9px; color:var(--muted); font-weight:700; }
.hub-primary a[aria-current="page"] { color:white; background:var(--deep); }
.hub-nav .hub-utility { display:inline-flex; align-items:center; min-height:44px; margin-left:auto; padding:8px 0 8px 18px; border-left:1px solid var(--line); color:var(--muted); font-size:12px; text-decoration:none; }
.hub-nav .hub-utility:hover { color:var(--green); }
.hub-nav .hub-utility[aria-current="page"] { color:var(--ink); font-weight:700; text-decoration:underline; text-underline-offset:5px; }
.hub-nav span { margin-left:7px; font-size:12px; opacity:.75; }
.archive-preview { display:grid; grid-template-columns:1fr 1.1fr; gap:40px; padding:32px; background:#eaf0e9; border:1px solid var(--line); border-radius:18px; margin:30px 0 40px; }
.archive-preview h2 { font-size:26px; line-height:1.35; margin:0 0 12px; }
.archive-preview p { color:var(--muted); max-width:460px; }
.archive-cta { display:inline-flex; gap:22px; align-items:center; background:var(--green); color:white; padding:11px 18px; border-radius:8px; text-decoration:none; font-weight:700; }
.archive-cta span { font-size:13px; font-weight:500; }
.archive-recent { list-style:none; padding:0; margin:0; }
.archive-recent li { border-bottom:1px solid #ced9ce; padding:12px 0; }
.archive-recent li:last-child { border:0; }
.archive-recent time { display:block; font-size:12px; color:var(--muted); margin-bottom:4px; }
.archive-recent a { display:block; text-decoration:none; line-height:1.5; font-weight:650; }
.archive-recent a:hover { color:var(--green); }
.archive-hero { padding:28px 0 24px; }
.archive-hero h1 { font-size:clamp(34px,5vw,56px); }
.archive-caption { color:var(--muted); font-size:13px; margin:24px 0 0; }
.archive-caption time { font-weight:700; margin-left:6px; color:var(--ink); }
.archive-caption > span { margin:0 12px; }
.archive-browser { padding:18px 0 16px; }
.lecture-hero { padding:28px 0 24px; max-width:760px; }
.lecture-hero h1 { margin:6px 0 12px; font-size:clamp(32px,4.5vw,48px); letter-spacing:-.04em; line-height:1.25; }
.lecture-hero>p:not(.section-kicker) { color:var(--muted); font-size:16px; line-height:1.75; margin:0 0 12px; max-width:660px; }
.lecture-count { color:var(--muted); font-size:12px; }
.lecture-list { display:grid; gap:22px; padding:6px 0 24px; }
.lecture-card { background:white; border:1px solid var(--line); border-radius:14px; padding:30px 34px; }
.lecture-featured { border-top:3px solid var(--green); }
.lecture-meta { display:flex; flex-wrap:wrap; align-items:center; gap:10px; color:var(--muted); font-size:12px; }
.lecture-format { color:var(--green); font-weight:750; }
.lecture-meta time { margin-left:auto; font-variant-numeric:tabular-nums; }
.lecture-card h2 { font-size:25px; line-height:1.45; letter-spacing:-.025em; margin:15px 0 12px; max-width:860px; }
.lecture-card h2 a { text-decoration:none; }
.lecture-card h2 a:hover { color:var(--green); text-decoration:underline; text-underline-offset:4px; }
.lecture-summary { max-width:820px; color:var(--muted); font-size:15px; line-height:1.8; margin:0 0 18px; word-break:keep-all; overflow-wrap:anywhere; }
.lecture-facts { display:flex; flex-wrap:wrap; list-style:none; gap:8px 18px; padding:0; margin:0 0 20px; color:var(--ink); font-size:13px; font-weight:650; }
.lecture-units { list-style:none; padding:0; margin:0; }
.lecture-units>li { border-top:1px solid var(--line); padding:12px 0; }
.lecture-units>li:last-child { padding-bottom:0; }
.lecture-units h3 { margin:0 0 3px; font-size:16px; line-height:1.55; overflow-wrap:anywhere; }
.lecture-units h3 span { color:var(--green); margin-right:7px; font-size:14px; }
.lecture-unit-meta { margin:0 0 3px; color:var(--muted); font-size:11px; }
.lecture-actions { display:flex; flex-wrap:wrap; align-items:center; gap:0 16px; }
.lecture-actions a { display:inline-flex; align-items:center; justify-content:flex-start; min-height:44px; min-width:44px; padding:2px 0; text-decoration:none; font-size:13px; font-weight:650; }
.lecture-primary { background:transparent; color:var(--green); }
.lecture-primary:hover { background:transparent; color:var(--deep); text-decoration:underline; text-underline-offset:4px; }
.lecture-secondary { border:0; color:var(--ink); }
.lecture-secondary:hover { color:var(--green); text-decoration:underline; text-underline-offset:4px; }
.lecture-series-disclosure>summary { cursor:pointer; list-style:none; border-radius:4px; }
.lecture-series-disclosure>summary::-webkit-details-marker { display:none; }
.lecture-series-disclosure>summary::marker { content:""; }
.lecture-series-summary { display:flex; align-items:center; justify-content:space-between; gap:12px; }
.lecture-series-summary .lecture-facts { margin:0; }
.lecture-series-toggle { display:inline-flex; align-items:center; gap:10px; color:var(--green); font-size:12px; white-space:nowrap; }
.series-chevron { width:7px; height:7px; border-right:1.5px solid currentColor; border-bottom:1.5px solid currentColor; transform:rotate(45deg); margin:0 2px 4px; }
.series-hide,.lecture-series-disclosure[open] .series-show { display:none; }
.lecture-series-disclosure[open] .series-hide { display:inline; }
.lecture-series-disclosure[open] .series-chevron { transform:rotate(225deg); margin-top:6px; }
.lecture-series-disclosure[open]>summary { margin-bottom:16px; }
.lecture-series-index { display:inline-flex; align-items:center; min-height:44px; margin-top:5px; font-size:12px; color:var(--muted); text-decoration:none; }
.lecture-resources { display:flex; flex-wrap:wrap; gap:2px 22px; margin-top:15px; padding-top:12px; border-top:1px solid #edf0eb; }
.lecture-resources a { display:inline-flex; align-items:center; min-height:44px; font-size:13px; color:var(--muted); text-decoration:none; }
.lecture-resources a:hover { color:var(--green); text-decoration:underline; }
.lecture-note { border-top:1px solid var(--line); padding:20px 0 36px; color:var(--muted); font-size:12px; line-height:1.8; }
.lecture-note p { max-width:800px; }
.lecture-note a { display:inline-flex; align-items:center; min-height:44px; }
.lectures-page :is(a,button,summary):focus-visible { outline:3px solid #86b6a8; outline-offset:4px; }
.lectures-page .topbar { min-height:76px; }
.collection-filters { display:flex; gap:10px; flex-wrap:wrap; }
.collection-button { display:inline-flex; align-items:center; gap:10px; cursor:pointer; font:inherit; font-size:14px; font-weight:700; color:var(--muted); border:1px solid var(--line); border-radius:10px; background:white; padding:12px 17px; }
.collection-button span { font-size:12px; padding:0 6px; background:#f0f2ef; color:var(--muted); border-radius:4px; }
.collection-button.active { background:var(--green); border-color:var(--green); color:white; }
.collection-button.active span { background:#ffffff25; color:white; }
.collection-description { color:var(--muted); font-size:13px; margin:17px 0 26px; max-width:880px; }
.archive-controls { display:grid; grid-template-columns:minmax(0,1fr) 170px 150px; gap:16px; padding:22px; background:white; border:1px solid var(--line); border-radius:12px; }
.archive-controls label { display:grid; gap:8px; font-size:12px; font-weight:700; color:var(--muted); min-width:0; }
.archive-controls input,.archive-controls select { width:100%; min-width:0; font:inherit; font-size:14px; font-weight:400; padding:11px 12px; color:var(--ink); background:var(--bg); border:1px solid var(--line); border-radius:6px; }
.archive-controls :is(input,select):focus-visible,.archive-page button:focus-visible,.hub-nav a:focus-visible { outline:3px solid #86b6a8; outline-offset:3px; }
.archive-results-bar { display:flex; align-items:center; justify-content:space-between; padding:15px 0; font-size:13px; color:var(--muted); }
#archive-reset { background:none; border:0; cursor:pointer; font:inherit; color:var(--green); text-decoration:underline; text-underline-offset:4px; padding:10px 0 10px 10px; }
.document-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:20px; }
.document-card { display:flex; flex-direction:column; border:1px solid var(--line); border-radius:14px; padding:26px; background:white; min-width:0; }
.document-card[hidden],#archive-empty[hidden],#archive-more[hidden] { display:none; }
.document-meta { display:flex; align-items:center; justify-content:space-between; gap:12px; font-size:12px; color:var(--muted); }
.document-meta > span { color:var(--green); font-weight:750; }
.document-meta time { white-space:nowrap; font-variant-numeric:tabular-nums; }
.document-card h2 { font-size:20px; line-height:1.5; margin:17px 0 10px; letter-spacing:-.02em; word-break:keep-all; overflow-wrap:anywhere; }
.document-card h2 a { text-decoration:none; }
.document-card h2 a:hover { color:var(--green); text-decoration:underline; text-underline-offset:5px; }
.document-author { margin:0 0 12px; color:var(--muted); font-size:13px; }
.external-book-note { color:var(--muted); font-size:12px; line-height:1.7; margin:0 0 16px; }
.document-summary { color:var(--muted); font-size:14px; margin:0 0 18px; word-break:keep-all; overflow-wrap:anywhere; }
.document-card .tags { margin-top:auto; margin-bottom:22px; }
.document-footer { display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; padding-top:17px; border-top:1px solid #edf0eb; font-size:12px; color:var(--muted); }
.document-footer > div { display:flex; gap:18px; flex-wrap:wrap; }
.document-footer a { font-weight:700; color:var(--ink); text-decoration:none; }
.archive-empty { text-align:center; padding:64px 24px; border:1px dashed var(--line); border-radius:12px; background:white; }
.archive-empty h2 { font-size:21px; margin:0 0 12px; }
.archive-empty p { color:var(--muted); font-size:14px; }
.archive-more { display:block; margin:30px auto 0; padding:13px 26px; cursor:pointer; background:white; border:1px solid var(--line); border-radius:8px; font:inherit; font-weight:700; }
.archive-note { padding:24px 0 48px; margin-top:20px; border-top:1px solid var(--line); color:var(--muted); font-size:12px; }
.archive-note p { max-width:800px; }
@media(max-width:760px) { .archive-preview { grid-template-columns:1fr; gap:20px; padding:24px; } .archive-controls { grid-template-columns:1fr 1fr; padding:16px; gap:12px; } .archive-search { grid-column:1 / -1; } .document-grid { grid-template-columns:1fr; } .document-card { padding:22px; } .collection-button { padding:10px 12px; font-size:13px; } .archive-page .topbar { align-items:flex-start; flex-wrap:wrap; gap:10px; } .archive-page .topbar-links { font-size:12px; } }
@media(max-width:600px) { .hub-nav { gap:4px 10px; padding:8px 0 12px; } .hub-primary { gap:4px; width:100%; } .hub-primary a { padding:10px 11px; font-size:14px; } .hub-primary span { font-size:11px; margin-left:5px; } .hub-nav .hub-utility { border-left:0; font-size:11px; padding:6px 0; } .lecture-hero { padding:22px 0 18px; } .lecture-hero h1 { font-size:32px; margin-bottom:10px; } .lecture-hero>p:not(.section-kicker) { font-size:14px; line-height:1.7; } .lecture-list { gap:16px; } .lecture-card { padding:22px; border-radius:11px; } .lecture-card h2 { font-size:21px; line-height:1.45; margin:13px 0 10px; } .lecture-summary { font-size:14px; line-height:1.75; margin-bottom:14px; } .lecture-facts { gap:7px 14px; font-size:12px; margin-bottom:17px; } .lecture-actions a { font-size:13px; padding:2px 0; } .lecture-resources { gap:0 18px; margin-top:12px; padding-top:8px; } .lecture-resources a { font-size:12px; } .lectures-page .topbar { align-items:flex-start; flex-wrap:wrap; gap:10px; padding-top:20px; padding-bottom:15px; min-height:0; } .lectures-page .topbar-links { font-size:12px; } }
@media(prefers-reduced-motion:reduce) { html { scroll-behavior:auto; } }
'''

ARCHIVE_JS = '''
(() => {
  const en = document.documentElement.lang === 'en';
  const params = new URLSearchParams(location.search);
  if (params.get('series') === 'lecture-notes' && !['q', 'month', 'sort'].some(key => params.has(key))) {
    location.replace(en ? '../../lectures/en/' : '../lectures/');
    return;
  }
  if (['daily-quantum', 'weekly-review'].includes(params.get('series')) && !['q', 'month', 'sort'].some(key => params.has(key))) {
    location.replace(en ? '../../briefings/en/' : '../briefings/');
    return;
  }
  const search = document.querySelector('#archive-search');
  if (!search) return;
  const month = document.querySelector('#archive-month');
  const sort = document.querySelector('#archive-sort');
  const grid = document.querySelector('#document-grid');
  const cards = Array.from(grid.querySelectorAll('.document-card'));
  const buttons = Array.from(document.querySelectorAll('[data-series].collection-button'));
  const count = document.querySelector('#archive-result-count');
  const empty = document.querySelector('#archive-empty');
  const more = document.querySelector('#archive-more');
  let series = buttons.some(button => button.dataset.series === params.get('series')) ? params.get('series') : '';
  let limit = 12;
  search.value = params.get('q') || '';
  if (Array.from(month.options).some(option => option.value === params.get('month'))) month.value = params.get('month');
  if (params.get('sort') === 'oldest') sort.value = 'oldest';
  const normalize = value => value.normalize('NFKC').toLocaleLowerCase().replace(/\\s+/g, ' ').trim();
  function apply(updateUrl = true) {
    const words = normalize(search.value).split(' ').filter(Boolean);
    const ordered = [...cards].sort((a, b) => sort.value === 'oldest' ? a.dataset.date.localeCompare(b.dataset.date) : b.dataset.date.localeCompare(a.dataset.date));
    let matches = 0;
    for (const card of ordered) {
      const haystack = normalize(card.dataset.search + ' ' + card.dataset.date);
      const match = (!series || card.dataset.series === series) && (!month.value || card.dataset.date.startsWith(month.value)) && words.every(word => haystack.includes(word));
      card.hidden = !match || matches >= limit;
      if (match) matches++;
      grid.append(card);
    }
    for (const button of buttons) {
      const active = button.dataset.series === series;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
    }
    count.textContent = en ? `${matches} resources · ${Math.min(limit, matches)} shown` : `${matches}건의 자료 · ${Math.min(limit, matches)}건 표시`;
    empty.hidden = matches !== 0;
    more.hidden = matches <= limit;
    more.textContent = en ? `Show more (${matches - limit} remaining) ↓` : `문서 더 보기 (${matches - limit}건 남음) ↓`;
    if (updateUrl) {
      const next = new URLSearchParams();
      if (series) next.set('series', series);
      if (search.value.trim()) next.set('q', search.value.trim());
      if (month.value) next.set('month', month.value);
      if (sort.value !== 'newest') next.set('sort', sort.value);
      history.replaceState(null, '', location.pathname + (next.size ? '?' + next : '') + location.hash);
    }
  }
  for (const control of [search, month, sort]) control.addEventListener(control === search ? 'input' : 'change', () => { limit = 12; apply(); });
  for (const button of buttons) button.addEventListener('click', () => { series = button.dataset.series; limit = 12; apply(); });
  document.querySelector('#archive-reset').addEventListener('click', () => { series = ''; search.value = ''; month.value = ''; sort.value = 'newest'; limit = 12; apply(); search.focus(); });
  more.addEventListener('click', () => { const previous = cards.filter(card => !card.hidden); limit += 12; apply(); const firstNew = Array.from(grid.children).find(card => !card.hidden && !previous.includes(card)); firstNew?.querySelector('a')?.focus(); });
  apply(false);
})();
'''
