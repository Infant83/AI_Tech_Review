#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
DAILY_DIR = ROOT / "daily_research_review"

HEADING_PATTERNS = [
    "## 오늘 대화 요약",
    "## Executive Summary",
    "## Summary",
    "## Topline",
    "## One-Line View",
    "## One-Line Read",
    "## One-Line Take",
    "## 핵심 요약",
]


@dataclass
class ReviewEntry:
    slug: str
    entry_date: date
    title: str
    kind: str
    source_path: Path
    summary_lines: list[str]
    sort_key: tuple[date, float]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the repository README from recent daily_research_review items."
    )
    parser.add_argument("--limit", type=int, default=5, help="Number of recent review entries to include.")
    parser.add_argument(
        "--output",
        default=str(ROOT / "README.md"),
        help="Output README path. Defaults to the repository root README.md.",
    )
    return parser.parse_args()


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta, body


def first_heading(body: str) -> str | None:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_date_from_name(name: str) -> date | None:
    match = re.match(r"(?P<d>\d{4}-\d{2}-\d{2})", name)
    if not match:
        return None
    return datetime.strptime(match.group("d"), "%Y-%m-%d").date()


def extract_bullets(lines: Iterable[str], limit: int = 3) -> list[str]:
    results: list[str] = []
    base_indent: int | None = None
    for raw_line in lines:
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if not line:
            if results:
                break
            continue
        if line.startswith("## "):
            break
        if line.startswith("- "):
            if base_indent is None:
                base_indent = indent
            elif indent > base_indent:
                continue
            results.append(line[2:].strip())
        elif line.startswith("1. "):
            if base_indent is None:
                base_indent = indent
            elif indent > base_indent:
                continue
            results.append(line[3:].strip())
        elif results:
            break
        if len(results) >= limit:
            break
    return results


def extract_summary(body: str) -> list[str]:
    lines = body.splitlines()
    for pattern in HEADING_PATTERNS:
        for idx, line in enumerate(lines):
            if line.strip() == pattern:
                bullets = extract_bullets(lines[idx + 1 :])
                if bullets:
                    return bullets

    for idx, line in enumerate(lines):
        if line.strip().startswith("## "):
            bullets = extract_bullets(lines[idx + 1 :])
            if bullets:
                return bullets

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        return [line]
    return ["요약을 추출하지 못했다."]


def select_package_source(folder: Path) -> Path | None:
    candidates = [
        folder / "reports",
        folder / "notes",
    ]
    for parent in candidates:
        if not parent.exists():
            continue
        for pattern in ("*_overview.md", "*_obsidian_memo.md", "*_memo.md", "*_pulse_review.md"):
            matches = sorted(parent.glob(pattern))
            if matches:
                return matches[0]
    return None


def collect_entries() -> list[ReviewEntry]:
    entries: list[ReviewEntry] = []
    for child in DAILY_DIR.iterdir():
        if child.name == "README.md":
            continue

        if child.is_file() and child.suffix.lower() == ".md":
            text = read_text(child)
            meta, body = split_frontmatter(text)
            entry_date = parse_date_from_name(child.name) or parse_date_from_name(meta.get("date", "")) or date.min
            title = meta.get("title") or first_heading(body) or child.stem
            entries.append(
                ReviewEntry(
                    slug=child.stem,
                    entry_date=entry_date,
                    title=title,
                    kind="conversation memo",
                    source_path=child,
                    summary_lines=extract_summary(body),
                    sort_key=(entry_date, child.stat().st_mtime),
                )
            )
            continue

        if child.is_dir():
            source = select_package_source(child)
            if not source:
                continue
            text = read_text(source)
            meta, body = split_frontmatter(text)
            entry_date = parse_date_from_name(child.name) or parse_date_from_name(meta.get("date", "")) or date.min
            title = meta.get("title") or first_heading(body) or child.name
            entries.append(
                ReviewEntry(
                    slug=child.name,
                    entry_date=entry_date,
                    title=title,
                    kind="daily package",
                    source_path=source,
                    summary_lines=extract_summary(body),
                    sort_key=(entry_date, source.stat().st_mtime),
                )
            )
    return sorted(entries, key=lambda item: item.sort_key, reverse=True)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def render_readme(entries: list[ReviewEntry], limit: int) -> str:
    selected = entries[:limit]
    lines: list[str] = [
        "# AI_Tech_Review",
        "",
        "기술 리뷰 패키지, 심층 리서치 메모, 슬라이드 산출물을 함께 관리하는 워크스페이스다.",
        "",
        "## 저장소 구성",
        "- 루트 주제 패키지는 `YYYY-MM-DD_<topic-slug>` 형식으로 관리한다.",
        "- 일별 인테이크와 대화 메모는 `daily_research_review/` 아래에 누적한다.",
        "- 리서치 리포트, 슬라이드 입력/산출물, 보조 소스는 주제 폴더 안에 함께 보관한다.",
        "",
        "## 기본 흐름",
        "1. 주제 또는 소스 팩을 받는다.",
        "2. 소스와 노트를 워크스페이스 구조에 맞게 정리한다.",
        "3. 심층 리서치를 수행하거나 보강한다.",
        "4. memo / deepresearch 마크다운을 작성한다.",
        "5. 필요하면 Skywork로 슬라이드를 생성한다.",
        "6. 핵심 메모는 Obsidian에 미러링하고 주요 패키지는 OpenProject에 아카이브한다.",
        "",
        "## 최근 Daily Review 스냅샷",
        f"_`daily_research_review/`의 최신 {min(limit, len(selected))}개 항목에서 자동 생성._",
        "",
    ]

    if not selected:
        lines.extend(
            [
                "- No daily review items were found yet.",
                "",
            ]
        )
    else:
        for entry in selected:
            lines.extend(
                [
                    f"### {entry.entry_date.isoformat()} · {entry.title}",
                    f"- 유형: `{entry.kind}`",
                    f"- 소스: [`{rel(entry.source_path)}`]({rel(entry.source_path)})",
                ]
            )
            for summary in entry.summary_lines[:3]:
                lines.append(f"- {summary}")
            lines.append("")

    lines.extend(
        [
            "## README 갱신",
            "```bash",
            "python scripts/generate_readme.py",
            "```",
            "",
            "최근 항목 수를 늘리고 싶으면:",
            "```bash",
            "python scripts/generate_readme.py --limit 8",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    entries = collect_entries()
    content = render_readme(entries, args.limit)
    output.write_text(content + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
