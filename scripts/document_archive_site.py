"""Build the public PDF library from an explicitly reviewed document registry."""
from __future__ import annotations

import hashlib
import html
import json
import posixpath
import re
import shutil
import tempfile
from pathlib import Path

SERIES = {
    "daily-quantum": ("Daily Quantum Review", "Daily Quantum Review"),
    "weekly-review": ("주간 리뷰", "Weekly reviews"),
    "article": ("수시 아티클", "Articles"),
    "lecture-notes": ("렉처 노트", "Lecture notes"),
}

# Reviewed, self-contained study sites. Never discover or copy a topic folder.
LECTURE_BUNDLES = {
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
}


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def render_archive_teaser(documents: list[dict]) -> str:
    recent = "".join(
        f'<li><time datetime="{escape(doc["date"])}">{escape(doc["date"])}</time>'
        f'<a href="archive/files/{escape(doc["id"])}.pdf" target="_blank" rel="noopener">'
        f'{escape(doc["title"])} <span aria-label="PDF, 새 창">↗</span></a></li>'
        for doc in documents[:3]
    )
    return f'''<section class="archive-preview" aria-labelledby="archive-preview-title">
      <div><p class="section-kicker">The document library</p>
      <h2 id="archive-preview-title">리뷰와 학습 자료를 한곳에.</h2>
      <p>Daily Quantum Review부터 주간 리뷰, 수시 아티클과 렉처 노트까지. 날짜와 주제로 찾고 PDF 원본을 다시 읽습니다.</p>
      <a class="archive-cta" href="archive/">문서 아카이브 <span>{len(documents)}건 →</span></a></div>
      <ul class="archive-recent">{recent}</ul>
    </section>'''


def render_archive(documents: list[dict], base_url: str, language: str = "ko") -> str:
    en = language == "en"
    prefix = "../../" if en else "../"
    pdf_prefix = "../files/" if en else "files/"
    current_url = base_url + "archive/" + ("en/" if en else "")
    title = "Document archive" if en else "리뷰 문서 아카이브"
    description = ("Daily Quantum Review, weekly reviews, articles and lecture notes in one searchable PDF library."
                   if en else "Daily Quantum Review, 주간 리뷰, 수시 아티클과 렉처 노트를 날짜와 주제로 다시 찾는 PDF 라이브러리입니다.")
    counts = {key: sum(doc["series"] == key for doc in documents) for key in SERIES}
    buttons = f'<button type="button" class="collection-button active" data-series="" aria-pressed="true">{"All documents" if en else "전체 문서"}<span>{len(documents)}</span></button>'
    buttons += "".join(
        f'<button type="button" class="collection-button" data-series="{key}" aria-pressed="false">{labels[int(en)]}<span>{counts[key]}</span></button>'
        for key, labels in SERIES.items()
    )
    months = sorted({doc["date"][:7] for doc in documents}, reverse=True)
    month_options = "".join(f'<option value="{month}">{month}</option>' for month in months)
    cards = []
    for doc in documents:
        doc_title = doc.get("title_en") if en else doc["title"]
        doc_summary = doc.get("summary_en") if en else doc["summary"]
        doc_title = doc_title or doc["title"]
        doc_summary = doc_summary or doc["summary"]
        text_language = "en" if en and doc.get("title_en") else doc["language"]
        summary_language = "en" if en and doc.get("summary_en") else doc["language"]
        searchable = " ".join(str(doc.get(key, "")) for key in ("title", "title_en", "summary", "summary_en", "source_title")) + " " + " ".join(doc["tags"])
        pdf = f'{pdf_prefix}{escape(doc["id"])}.pdf'
        study = f'{prefix}{escape(doc["study_href"])}' if doc.get("study_href") else ""
        title_link = f'<a href="{study}">{escape(doc_title)}</a>' if study else f'<a href="{pdf}" target="_blank" rel="noopener">{escape(doc_title)}</a>'
        study_link = f'<a href="{study}">{"Korean study notes" if en else "강의 노트 읽기"} →</a>' if study else ""
        tags = "".join(f'<span>{escape(tag)}</span>' for tag in doc["tags"])
        native_language = ({"ko": "Korean PDF", "en": "English PDF"} if en else {"ko": "한국어 PDF", "en": "영어 PDF"})[doc["language"]]
        cards.append(f'''<article class="document-card" data-series="{escape(doc['series'])}" data-date="{escape(doc['date'])}" data-search="{escape(searchable)}">
          <div class="document-meta"><span>{SERIES[doc['series']][int(en)]}</span><time datetime="{escape(doc['date'])}">{escape(doc['date'])}</time></div>
          <h2 lang="{text_language}">{title_link}</h2>
          <p class="document-summary" lang="{summary_language}">{escape(doc_summary)}</p>
          <div class="tags">{tags}</div>
          <div class="document-footer"><span>{native_language} · {doc['size_bytes'] / 1024:.0f} KB</span>
          <div>{study_link}<a href="{pdf}" target="_blank" rel="noopener">{'Open PDF' if en else 'PDF 열기'} ↗</a><a href="{pdf}" download>{'Download' if en else '다운로드'} ↓</a></div></div>
        </article>''')
    latest = documents[0]["date"] if documents else "—"
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
  <link rel="stylesheet" href="{prefix}assets/site.css"><link rel="stylesheet" href="{prefix}assets/archive.css">
</head><body class="archive-page">
  <header class="site-header">
    <nav class="topbar" aria-label="{'Main navigation' if en else '주요 링크'}">
      <a class="brand" href="{prefix}index.html">AI Tech Review Letters</a>
      <span class="topbar-links"><a href="{prefix}methods/">{'Editorial methods' if en else '작성·검증 원칙'}</a><a href="{'../' if en else 'en/'}" lang="{'ko' if en else 'en'}" hreflang="{'ko' if en else 'en'}">{'한국어' if en else 'English'}</a></span>
    </nav>
    <nav class="hub-nav" aria-label="{'Library navigation' if en else '허브 메뉴'}"><a href="{prefix}index.html">{'Review hub' if en else '리뷰허브'}</a><a href="./" aria-current="page">{'Document archive' if en else '문서 아카이브'} <span>{len(documents)}</span></a><a href="./?series=lecture-notes">{'Lecture notes' if en else '렉처 노트'} <span>{counts['lecture-notes']}</span></a></nav>
    <section class="hero archive-hero"><p class="eyebrow">The document library</p><h1>{title}</h1><p class="lead">{description}</p>
      <p class="archive-caption">{'Latest issue' if en else '최근 발행'} <time>{latest}</time> <span>·</span> {'Original PDF documents' if en else 'PDF 원본 보관'}</p>
    </section>
  </header>
  <main>
    <section class="archive-browser" aria-label="{'Find documents' if en else '문서 찾기'}">
      <div class="collection-filters" aria-label="{'Collections' if en else '문서 분류'}">{buttons}</div>
      <p class="collection-description" id="collection-description">{'Daily Quantum Review collects the Daily Quantum Brief series. Weekly reviews, articles and lecture notes are archived alongside it. For revised lecture notes, only the latest supplied edition is listed.' if en else 'Daily Quantum Review에는 Daily Quantum Brief 시리즈를 모았습니다. 주간 리뷰, 수시 PDF와 렉처 노트를 함께 보관하며, 개정된 렉처 노트는 확인된 최신본만 등록합니다.'}</p>
      <div class="archive-controls">
        <label class="archive-search"><span>{'Search documents' if en else '문서 검색'}</span><input id="archive-search" type="search" placeholder="{'Title, topic, keyword…' if en else '제목, 주제, 키워드로 검색…'}" autocomplete="off"></label>
        <label><span>{'Month' if en else '발행 월'}</span><select id="archive-month"><option value="">{'All months' if en else '전체 기간'}</option>{month_options}</select></label>
        <label><span>{'Sort' if en else '정렬'}</span><select id="archive-sort"><option value="newest">{'Newest first' if en else '최신순'}</option><option value="oldest">{'Oldest first' if en else '오래된순'}</option></select></label>
      </div>
      <div class="archive-results-bar"><p id="archive-result-count" role="status">{len(documents)} {'documents' if en else '건의 문서'}</p><button type="button" id="archive-reset">{'Reset filters' if en else '필터 초기화'}</button></div>
      <div class="document-grid" id="document-grid">{''.join(cards)}</div>
      <div id="archive-empty" class="archive-empty" hidden><h2>{'No matching documents' if en else '조건에 맞는 문서가 없습니다'}</h2><p>{'Try another keyword or clear the filters. Empty collections will appear here when documents are added.' if en else '검색어나 기간을 바꾸거나 필터를 초기화해 보세요. 아직 비어 있는 분류는 문서가 등록되면 이곳에 표시됩니다.'}</p></div>
      <button type="button" class="archive-more" id="archive-more" hidden>{'Show more documents' if en else '문서 더 보기'} ↓</button>
      <noscript><p>{'All documents are shown below. Enable JavaScript to search and filter.' if en else '전체 문서를 표시합니다. 검색과 필터는 JavaScript를 켜면 사용할 수 있습니다.'}</p></noscript>
    </section>
    <footer class="archive-note"><p>{'Archived PDFs are preserved in their original language. The English catalog describes the collection; it does not imply an English PDF translation.' if en else '문서는 발행 당시의 언어와 내용으로 보관합니다. 아카이브 등록은 본문의 연구 결과를 새로 검증하거나 독립 재현했다는 뜻이 아닙니다.'}</p><a href="{prefix}archive-manifest.json">{'Archive data (JSON)' if en else '아카이브 데이터 (JSON)'} ↗</a></footer>
  </main>
  <script src="{prefix}assets/archive.js" defer></script>
</body></html>'''


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
    metadata = (f'<link rel="canonical" href="{escape(canonical)}">'
                f'<meta property="og:type" content="article">'
                f'<meta property="og:title" content="{escape(document["title"])}">'
                f'<meta property="og:description" content="{escape(document["summary"])}">'
                f'<meta property="og:url" content="{escape(canonical)}">')
    prefix = posixpath.relpath(".", href.rstrip("/")) + "/"
    navigation = (f'<nav aria-label="테크리뷰 바로가기"><a href="{prefix}archive/?series=lecture-notes">← 렉처 노트 목록</a>'
                  '<a href="#doc-study-guide">학습 시작 안내</a>'
                  '<a href="#doc-glossary">한영 용어집</a>'
                  '<a href="#doc-labs-readme">실습과 코드</a></nav>')
    text = text.replace("</head>", metadata + "</head>", 1)
    sidebar = re.search(r'<aside\b[^>]*class="sidebar"[^>]*>', text)
    if sidebar:
        text = text[:sidebar.end()] + navigation + text[sidebar.end():]
    else:
        text = text.replace("<body>", "<body>" + navigation, 1)
    publication_note = ('<section class="document publication-note" aria-label="웹 게재 기록">'
                        '<h2>웹 게재 기록</h2><p>2026-10-20 · OpenAI Codex의 root가 웹 게재를 통합하고, '
                        'lecture_publish_audit가 공개 자산과 아카이브 연결을 독립 검토했다. '
                        '강의 집필·수학 검토·실습 실행의 역할과 범위는 본문 작성 공개를 따른다. '
                        '영문 목록은 한국어 학습 자료의 안내이며 영어 번역본이 아니다.</p></section>')
    text = text.replace("</main>", publication_note + "</main>", 1)
    text = decorate(text, prefix)
    index.write_text(text, encoding="utf-8")
    return destination


def publish_archive(archive_dir: Path, site_dir: Path, base_url: str, decorate) -> list[dict]:
    try:
        from .archive_documents import load_documents
    except ImportError:
        from archive_documents import load_documents
    source_documents = load_documents(archive_dir)
    documents = []
    for source in source_documents:
        payload = (archive_dir / source["file"]).read_bytes()
        doc = {key: value for key, value in source.items() if key not in {"file", "public_reviewed"}}
        doc.update(href=f'archive/files/{source["id"]}.pdf', size_bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
        documents.append(doc)
    # Stage the complete allowlist before replacing the generated archive.
    with tempfile.TemporaryDirectory(prefix="document-archive-", dir=site_dir.parent) as temporary:
        temporary_root = Path(temporary)
        lecture_outputs = []
        for source, document in zip(source_documents, documents):
            spec = LECTURE_BUNDLES.get(source["id"])
            if spec:
                if source["series"] != "lecture-notes":
                    raise ValueError("Study bundles must belong to lecture-notes")
                staged = stage_lecture_bundle(archive_dir, temporary_root, source, spec, base_url, decorate)
                # Only derived, public fields leave the source registry.
                document["study_href"] = spec["href"]
                document["study_assets"] = {name: hashlib.sha256((staged / name).read_bytes()).hexdigest() for name in spec["files"]}
                lecture_outputs.append((staged, site_dir / spec["href"]))
        staging = Path(temporary) / "archive"
        (staging / "files").mkdir(parents=True)
        (staging / "en").mkdir()
        for source in source_documents:
            shutil.copyfile(archive_dir / source["file"], staging / "files" / f'{source["id"]}.pdf')
        for lang, prefix in (("ko", "../"), ("en", "../../")):
            target = staging / ("en/index.html" if lang == "en" else "index.html")
            target.write_text(decorate(render_archive(documents, base_url, lang), prefix), encoding="utf-8")
        target = site_dir / "archive"
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(staging), str(target))
        for staged, target in lecture_outputs:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(staged), str(target))
    (site_dir / "archive-manifest.json").write_text(json.dumps({"version": 1, "documents": documents}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assets = site_dir / "assets"
    (assets / "archive.css").write_text(ARCHIVE_CSS.strip() + "\n", encoding="utf-8")
    (assets / "archive.js").write_text(ARCHIVE_JS.strip() + "\n", encoding="utf-8")
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
    return errors


def validate_archive(site_dir: Path) -> list[str]:
    errors = []
    manifest_path = site_dir / "archive-manifest.json"
    if not manifest_path.exists():
        return ["missing public archive manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors.extend(validate_lecture_bundles(site_dir, manifest["documents"]))
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
    return errors


ARCHIVE_CSS = '''
.hub-nav { display:flex; gap:8px; padding:8px 0 20px; flex-wrap:wrap; }
.hub-nav a { text-decoration:none; padding:10px 18px; border-radius:999px; color:var(--muted); font-weight:700; }
.hub-nav a[aria-current="page"] { color:white; background:var(--deep); }
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
.archive-hero { padding:42px 0 30px; }
.archive-hero h1 { font-size:clamp(34px,5vw,56px); }
.archive-caption { color:var(--muted); font-size:13px; margin:24px 0 0; }
.archive-caption time { font-weight:700; margin-left:6px; color:var(--ink); }
.archive-caption > span { margin:0 12px; }
.archive-browser { padding:30px 0 16px; }
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
@media(prefers-reduced-motion:reduce) { html { scroll-behavior:auto; } }
'''

ARCHIVE_JS = '''
(() => {
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
  const en = document.documentElement.lang === 'en';
  const params = new URLSearchParams(location.search);
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
    count.textContent = en ? `${matches} documents · ${Math.min(limit, matches)} shown` : `${matches}건의 문서 · ${Math.min(limit, matches)}건 표시`;
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
