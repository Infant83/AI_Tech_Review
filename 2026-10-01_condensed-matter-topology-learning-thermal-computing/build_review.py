"""Build bilingual pages and original explanatory schematics; no source-data plots."""
from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts"
BASE = "https://infant83.github.io/AI_Tech_Review/reviews/" + ROOT.name + "/"
TITLE = {
    "ko": "적층 위상질서와 AI의 통계물리: 계층 학습과 열잡음 계산",
    "en": "Layered topological order and the statistical physics of AI: hierarchical learning and thermal-noise computing",
}
SUBTITLE = {
    "ko": "JCCM 2026년 9월 선정 논문 6편 — 새로운 위상상, 표본 복잡도와 물리적 계산의 검증 경계",
    "en": "Six papers selected by JCCM in September 2026: new phases, sample complexity and the evidence boundaries of physical computing",
}


def svg_begin(title: str, desc: str, height: int) -> list[str]:
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {height}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc><defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="none" stroke="#32776e" stroke-width="1.7"/></marker></defs><rect width="900" height="{height}" rx="8" fill="#f0f4ee"/><g font-family="Noto Sans KR,Apple SD Gothic Neo,Malgun Gothic,Arial,sans-serif" fill="#193d40">''']


def text(x: int, y: int, value: str, size: int = 17, weight: int = 400) -> str:
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}">{escape(value)}</text>'


def box(x: int, y: int, w: int, h: int, colour: str = "#fff") -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{colour}" stroke="#c5d5ca"/>'


def line(x1: int, y1: int, x2: int, y2: int, arrow: bool = False, colour: str = "#32776e") -> str:
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    return f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{colour}" stroke-width="2"{marker}/>'


def layered(lang: str) -> str:
    ko = lang == "ko"
    parts = svg_begin("적층 위상질서의 구분" if ko else "Distinguishing layered orders", "Three conceptual stack patterns; coupling lines do not depict tunnelling or measured data.", 440)
    parts += [text(30, 38, "층간 결합의 구조를 구분하기" if ko else "DISTINGUISH THE STRUCTURE OF INTERLAYER COUPLING", 19, 700)]
    heads = ("독립적인 층", "점유층 쌍 + 빈 층", "여러 층에 걸친 결합") if ko else ("Independent layers", "Occupied pairs + empty", "Coupling across layers")
    for i, heading in enumerate(heads):
        x = 25 + i * 290
        parts += [box(x, 62, 270, 305), text(x + 16, 92, heading, 17, 700)]
        for j in range(6):
            y = 125 + j * 34
            empty = i == 1 and j % 3 == 2
            fill = "#e9ece6" if empty else "#d8e9df"
            parts.append(f'<rect x="{x+22}" y="{y}" width="225" height="12" rx="3" fill="{fill}" stroke="#7c9d90"/>' )
            if i == 1:
                parts.append(text(x + 192, y + 10, "0" if empty else "1/3", 12))
            if not empty:
                parts.append(f'<circle cx="{x+62}" cy="{y+6}" r="4" fill="#32776e"/>')
        if i == 1:
            for j in (0, 3):
                parts.append(line(x + 125, 131 + j * 34, x + 125, 165 + j * 34, colour="#ae7346"))
        if i == 2:
            parts += [line(x + 75, 131, x + 130, 199), line(x + 130, 165, x + 180, 267), line(x + 75, 233, x + 130, 301)]
        notes = (("출발점: 독립층 질서", "평균 채움 2/9 · 반복 패턴", "non-foliated 질서의 개념도") if ko else ("Baseline: decoupled order", "Mean filling 2/9 · repeated", "Non-foliated: schematic only"))
        parts.append(text(x + 16, 342, notes[i], 14))
    parts += [text(30, 396, "결합 범위 ≠ 준입자의 자유로운 3차원 이동" if ko else "Coupling range does not establish freely mobile 3D quasiparticles.", 16, 700), text(30, 424, "설명 도식 · 특정 K 행렬, 전자 궤적 또는 측정 데이터가 아님" if ko else "Explanatory schematic · not a specific K matrix, particle trajectory or measurement", 13), "</g></svg>"]
    return "".join(parts)


def hierarchy(lang: str) -> str:
    ko = lang == "ko"
    parts = svg_begin("계층 구조와 표본 잡음" if ko else "Hierarchy and sampling noise", "A meaning-preserving hierarchy is shown beside a signal-to-noise criterion. This is not a data chart.", 460)
    parts += [text(30, 38, "표면의 조합 수와 학습할 규칙 수는 다르다" if ko else "COMBINATIONS AND LEARNABLE RULES ARE DIFFERENT COUNTS", 19, 700)]
    parts += [box(25, 65, 470, 345), box(515, 65, 360, 345)]
    parts += [text(45, 96, "의미를 보존하는 치환" if ko else "Meaning-preserving substitutions", 17, 700)]
    parts += [box(190, 116, 140, 45, "#d8e9df"), text(210, 145, "상위 범주" if ko else "Category", 16, 700)]
    for i, x in enumerate((90, 315)):
        parts += [line(260, 161, x + 45, 210, True), box(x, 212, 110, 44, "#d8e9df"), text(x + 15, 240, ("표현 A" if i == 0 else "표현 B") if ko else ("Form A" if i == 0 else "Form B"), 16)]
    for i, x in enumerate((60, 160, 285, 385)):
        parent_x = 145 if i < 2 else 370
        parts += [line(parent_x, 257, x + 35, 300, True), box(x, 305, 75, 40), text(x + 10, 331, ("토큰 " if ko else "Token ") + str(i + 1), 13)]
    parts += [text(45, 385, "동일 색: 동등한 상위 의미" if ko else "Same colour: equivalent higher-level meaning", 14)]
    parts += [text(540, 96, "통계적으로 보이는 조건" if ko else "When structure becomes visible", 17, 700), text(545, 153, "C(r) ∝ r⁻ᵝ", 25), text(545, 199, "noise ∝ P⁻¹ᐟ²", 23), line(545, 225, 837, 225), text(545, 267, "signal > noise", 23, 700), text(545, 317, "r* ∝ P¹ᐟ⁽²ᵝ⁾", 23), text(545, 375, "독립 표본·모형 가정에 의존" if ko else "Depends on sampling/model assumptions", 14)]
    parts += [text(30, 440, "설명 모형 · 실제 생산 규칙이나 학습 곡선을 재현한 그림이 아님" if ko else "Explanatory model · not the paper’s exact production rules or a measured learning curve", 13), "</g></svg>"]
    return "".join(parts)


def thermal(lang: str) -> str:
    ko = lang == "ko"
    parts = svg_begin("디지털 학습과 물리적 실행의 경계" if ko else "Digital training and proposed physical execution", "Two training targets feed a digital parameter-learning stage, followed by proposed coupling programming, thermal evolution and timed readout. Demonstrations were numerical.", 460)
    parts += [text(30, 38, "학습 비용과 실행 비용을 따로 기록하기" if ko else "KEEP TRAINING AND EXECUTION COSTS SEPARATE", 19, 700)]
    parts += [box(25, 65, 850, 165, "#e5eee5"), text(45, 92, "디지털 학습 · 논문의 수치 시연" if ko else "DIGITAL TRAINING · numerical demonstrations", 16, 700)]
    parts += [box(45, 110, 295, 42), text(60, 137, "생성: 역방향 noising 경로" if ko else "Generation: reverse noising paths", 15), box(45, 166, 295, 42), text(60, 193, "분류: 교사 네트워크의 경로" if ko else "Classification: teacher trajectories", 15)]
    parts += [line(340, 131, 505, 157, True), line(340, 187, 505, 157, True), box(510, 126, 325, 67), text(530, 153, "경로 우도에 맞춰 매개변수 학습" if ko else "Learn parameters from path likelihood", 15, 700), text(530, 178, "디지털 최적화 비용 포함" if ko else "Digital optimization has a cost", 14)]
    parts += [line(672, 194, 672, 246, True)]
    parts += [box(25, 250, 850, 160, "#f7eee2"), text(45, 280, "제안된 물리적 실행 · 실물 검증 단계는 별도" if ko else "PROPOSED PHYSICAL EXECUTION · device validation is separate", 16, 700)]
    for x, title, detail in ((45, "결합 설정" if ko else "Program couplings", "입력·초기화" if ko else "Input / initialization"), (325, "열적 동역학" if ko else "Thermal evolution", "힘 + 열잡음" if ko else "Drift + thermal noise"), (605, "유한시간 읽기" if ko else "Timed readout", "측정·리셋" if ko else "Measure / reset")):
        parts += [box(x, 305, 245, 78), text(x + 15, 334, title, 17, 700), text(x + 15, 361, detail, 14)]
    parts += [line(292, 345, 320, 345, True), line(572, 345, 600, 345, True), text(30, 440, "고전 확률 계산 · 소자 전력 실측이나 범용 LLM 구현을 나타내는 도식이 아님" if ko else "Classical stochastic computing · not a device power measurement or a general-purpose LLM", 13), "</g></svg>"]
    return "".join(parts)


def build(lang: str) -> None:
    ko = lang == "ko"
    target = ROOT / "dist" / ("" if ko else "en")
    target.mkdir(parents=True, exist_ok=True)
    for source, name in ((ARTIFACTS / "review.css", "review.css"), (ARTIFACTS / "condmat_hero.webp", "condmat_hero.webp")):
        shutil.copy2(source, target / name)
    for name, fn in (("layered_order.svg", layered), ("hierarchy_signal.svg", hierarchy), ("thermal_workflow.svg", thermal)):
        (target / name).write_text(fn(lang), encoding="utf-8")
    content = (ROOT / "reports" / f"content_{lang}.html").read_text(encoding="utf-8")
    names = ("이번 달의 연결점", "적층 위상질서", "계층 구조의 학습", "열잡음 계산", "후속 검증 제안", "핵심 판단", "참고 자료") if ko else ("Editorial overview", "Layered orders", "Hierarchical learning", "Thermal-noise computing", "Proposed tests", "Bottom line", "References")
    toc = "".join(f'<a href="#{key}">{label}</a>' for key, label in zip(("overview", "topology", "learning", "thermal", "proposals", "outlook", "references"), names))
    alternates = "".join(f'<link rel="alternate" hreflang="{code}" href="{BASE+sub}">' for code, sub in (("ko", ""), ("en", "en/"), ("x-default", "")))
    nav = "".join(f'<a lang="{code}" hreflang="{code}" href="{BASE+sub}"' + (' aria-current="page"' if code == lang else '') + f'>{label}</a>' for code, sub, label in (("ko", "", "한국어"), ("en", "en/", "English")))
    caption = "그림 1. 적층 물질·계층 학습·열잡음 계산을 함께 배치한 AI 생성 개념 표지. 실제 구조·궤적·측정 데이터를 재현하지 않는다." if ko else "Figure 1. AI-generated conceptual cover juxtaposing layered matter, hierarchical learning and thermal-noise computing; not a physical structure, trajectory or measured dataset."
    alt = "반투명 적층 구조와 분기하는 선, 완만한 열적 지형을 함께 그린 개념 일러스트" if ko else "Conceptual illustration of translucent layers, branching paths and a smooth thermal landscape"
    metadata = '<meta property="article:published_time" content="2026-10-01"><meta property="article:modified_time" content="2026-10-01">'
    page = f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(TITLE[lang])}</title><meta name="description" content="{escape(SUBTITLE[lang], quote=True)}"><link rel="canonical" href="{BASE+('' if ko else 'en/')}">{alternates}<meta property="og:type" content="article"><meta property="og:title" content="{escape(TITLE[lang],quote=True)}"><meta property="og:description" content="{escape(SUBTITLE[lang],quote=True)}"><meta property="og:image" content="{BASE}condmat_hero.webp"><meta name="twitter:card" content="summary_large_image">{metadata}<link rel="stylesheet" href="review.css"></head><body>
<div class="masthead"><a href="https://infant83.github.io/AI_Tech_Review/">AI TECH REVIEW</a><span>{nav}</span></div>
<figure class="cover"><img src="condmat_hero.webp" width="1600" height="900" alt="{alt}" fetchpriority="high"><figcaption>{caption}</figcaption></figure>
<header class="title-block"><p class="eyebrow">CONDENSED MATTER / STATISTICAL LEARNING / PHYSICAL COMPUTING</p><h1>{escape(TITLE[lang])}</h1><p class="subtitle">{escape(SUBTITLE[lang])}</p><div class="meta"><span>{'2026년 9월 JCCM 선정' if ko else 'September 2026 JCCM selection'}</span><span>{'검토·게재 2026-10-01' if ko else 'Reviewed and published 2026-10-01'}</span><span>{'원 논문 6편 · 설명 도식 3종' if ko else 'Six papers · three explanatory schematics'}</span></div></header>
<div class="layout"><nav class="toc" aria-label="{'목차' if ko else 'Contents'}"><strong>{'이 리뷰에서' if ko else 'In this review'}</strong>{toc}</nav><main><article>{content}</article></main></div>
<footer class="article-footer">AI Tech Review · {'보고 결과와 리뷰의 해석·후속 제안을 구분합니다.' if ko else 'Reported results are separated from interpretation and proposed tests.'}</footer></body></html>'''
    (target / "index.html").write_text(page, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hero", type=Path, help="Generated source image; create compressed cover derivative")
    args = parser.parse_args()
    if args.hero:
        from PIL import Image, ImageOps
        image = ImageOps.exif_transpose(Image.open(args.hero)).convert("RGB")
        image.thumbnail((1600, 1000), Image.Resampling.LANCZOS)
        image.save(ARTIFACTS / "condmat_hero.webp", "WEBP", quality=88, method=6)
    if not (ARTIFACTS / "condmat_hero.webp").exists():
        parser.error("Cover asset missing: provide --hero once")
    for language in ("ko", "en"):
        build(language)
    print("Built bilingual HTML, cover derivative and three explanatory SVGs per language.")
