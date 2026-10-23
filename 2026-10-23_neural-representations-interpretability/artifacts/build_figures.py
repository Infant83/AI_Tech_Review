#!/usr/bin/env python3
"""Build bilingual, deterministic teaching diagrams for this review.

The vector geometry is illustrative. No trained model or experimental
measurement is reproduced. Python's standard library is sufficient.
"""
from pathlib import Path
from html import escape
import math
import xml.etree.ElementTree as ET

OUT = Path(__file__).resolve().parent / "figures"
BG, INK, MUTED = "#fbfaf6", "#172b3a", "#465965"
BLUE, TEAL, ORANGE, PURPLE = "#28649b", "#16766d", "#a35313", "#7f4c89"
FONT = "'Apple SD Gothic Neo','Noto Sans CJK KR','Noto Sans KR',Arial,sans-serif"


class Diagram:
    def __init__(self, height, title, description):
        self.height = height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}" role="img" aria-labelledby="title desc">',
                      f'<title id="title">{escape(title)}</title>',
                      f'<desc id="desc">{escape(description)}</desc>',
                      '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M1 1 L9 5 L1 9" fill="none" stroke="context-stroke" stroke-width="2"/></marker></defs>',
                      f'<rect width="1000" height="{height}" fill="{BG}"/>']

    def rect(self, x, y, w, h, fill="#ffffff", stroke="#c4d0d6", radius=18, sw=2):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, text, size=28, weight=400, fill=INK, anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(text)}</text>')

    def lines(self, x, y, lines, size=28, gap=39, **kw):
        for i, line in enumerate(lines):
            self.text(x, y + i * gap, line, size=size, **kw)

    def line(self, x1, y1, x2, y2, color=INK, width=3, arrow=False, dash=None):
        extra = ' marker-end="url(#arrow)"' if arrow else ''
        if dash:
            extra += f' stroke-dasharray="{dash}"'
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{extra}/>')

    def circle(self, x, y, r, fill, stroke=INK):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')

    def pill(self, x, y, w, h, text, color=BLUE, size=28):
        self.rect(x, y, w, h, fill="#f2f6f8", stroke=color, radius=14)
        self.text(x+w/2, y+h/2+size*.34, text, size=size, weight=600, fill=color, anchor="middle")

    def save(self, filename):
        content = '\n'.join(self.parts + ['</svg>']) + '\n'
        ET.fromstring(content)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / filename).write_text(content, encoding="utf-8")


def representations(lang):
    ko = lang == "ko"
    title = "관찰·표현·학습 경로를 구분하기" if ko else "Observation, encoding and learning"
    desc = ("리뷰 재구성. 다의적 반응은 관찰, 중첩은 차원보다 많은 특징을 담는 표현 가설, 재귀적 일반화는 유사성의 연쇄를 따라 반응이 넓어진다는 학습 가설이다. 고양이와 자동차 뉴런의 V자 재해석 하나로 일반적인 중첩을 반증할 수 없다. 화살표 기하는 실측값이 아니다."
            if ko else "Review reconstruction. Polysemantic responses are an observation; superposition is an encoding hypothesis involving more features than dimensions; recursive generalization is a proposed learning path through local similarities. A shared V-shape interpretation of one cat-and-car neuron does not refute superposition in general. Feature vectors are schematic, not measured.")
    d = Diagram(1560, title, desc)
    d.text(45, 66, title, 40, 700)
    d.text(45, 111, "서로 다른 질문을 하나의 ‘깨끗함’ 점수로 합치지 않는다." if ko else "These are different claims about neuron representations.", 26, fill=MUTED)

    d.rect(40, 150, 920, 280)
    d.text(70, 197, "1 · 관찰: 다의적 반응(polysemanticity)" if ko else "1 · Observation: polysemantic responses", 32, 700, BLUE)
    d.text(70, 243, "겉으로 다른 입력들이 같은 뉴런을 활성화한다." if ko else "Different-looking inputs activate the same neuron.", 28)
    d.pill(90, 270, 260, 60, "고양이 얼굴" if ko else "Cat face")
    d.pill(90, 345, 260, 60, "자동차 정면" if ko else "Car front")
    d.line(370, 300, 725, 337, BLUE, 3, True)
    d.line(370, 375, 725, 342, BLUE, 3, True)
    d.circle(785, 338, 46, "#e5eef7", BLUE)
    d.text(785, 348, "N", 30, 700, BLUE, "middle")
    d.text(850, 348, "활성" if ko else "ON", 25, 600, BLUE)

    d.text(70, 472, "이 관찰만으로 인코딩 원리는 결정되지 않는다." if ko else "The observation does not determine the encoding mechanism.", 25, fill=MUTED)

    d.rect(40, 505, 920, 390)
    d.text(70, 552, "2 · 표현 가설: 중첩(superposition)" if ko else "2 · Encoding hypothesis: superposition", 32, 700, TEAL)
    d.text(70, 598, "표현 차원보다 많은 특징을 비직교 방향으로 저장한다." if ko else "More features than representation dimensions.", 28)
    # Four feature directions in a two-dimensional drawing, with no orthogonal
    # pair. This is a geometric illustration, not learned feature vectors.
    ox, oy, length = 240, 802, 148
    d.line(75, oy, 405, oy, "#6b7b86", 2, True)
    d.line(ox, 850, ox, 636, "#6b7b86", 2, True)
    for angle, color, label in [(20, TEAL, "a"), (55, BLUE, "b"), (105, PURPLE, "c"), (150, ORANGE, "d")]:
        rad = math.radians(angle)
        ex, ey = ox + length*math.cos(rad), oy-length*math.sin(rad)
        d.line(ox, oy, ex, ey, color, 5, True)
        d.text(ex+10, ey-9, label, 25, 700, color)
    d.text(240, 871, "표현 공간(도식)" if ko else "Representation space", 24, fill=MUTED, anchor="middle")
    d.lines(460, 678, ["하나의 뉴런에 반응이 섞인다는", "설명보다 넓은 기하학적 개념이다."] if ko else ["This geometric meaning is broader", "than arbitrary mixtures per neuron."], 26, 39)
    d.lines(460, 791, ["화살표는 실측한 특징이 아니다.", "비직교성만으로 입증되지 않는다."] if ko else ["Vectors are illustrative, not measured.", "Non-orthogonality alone is not proof."], 24, 37, fill=MUTED)

    d.rect(40, 930, 920, 285)
    d.text(70, 977, "3 · 학습 가설: 재귀적 일반화" if ko else "3 · Learning hypothesis: recursive generalization", 32, 700, PURPLE)
    d.text(70, 1023, "닮은 맥락을 거치며 반응이 연쇄적으로 넓어진다." if ko else "Responses spread through a chain of local similarities.", 28)
    d.pill(80, 1061, 200, 65, "iy", PURPLE, 30)
    d.pill(400, 1061, 200, 65, "diy", PURPLE, 30)
    d.pill(720, 1061, 200, 65, "do it yourself", PURPLE, 25)
    d.line(298, 1093, 381, 1093, PURPLE, 3, True)
    d.line(618, 1093, 701, 1093, PURPLE, 3, True)
    d.text(70, 1180, "제안된 성장 순서는 훈련 체크포인트에서 확인해야 한다." if ko else "Test the proposed growth order in training checkpoints.", 25, fill=MUTED)

    d.rect(40, 1250, 920, 195, fill="#fff5e6", stroke="#bb8d51")
    d.text(70, 1298, "고양이 + 자동차 → 공통 V자 형태?" if ko else "Cat + car → a shared V shape?", 31, 700, ORANGE)
    d.lines(70, 1350, ["한 뉴런에서 공통 패턴을 찾았다고 해서", "다른 뉴런·모델의 중첩이 반증되는 것은 아니다."] if ko else ["Reinterpreting one neuron does not rule out", "superposition elsewhere or in other models."], 28, 42)
    d.text(45, 1492, "리뷰 재구성 · 출처: Goodfire; Toy Models of Superposition" if ko else "Review reconstruction · Sources: Goodfire; Toy Models of Superposition", 24, fill=MUTED)
    d.text(45, 1530, "실측 데이터·훈련 기록을 재현한 그림이 아닙니다." if ko else "Schematic geometry and learning path; not experimental data.", 24, fill=MUTED)
    d.save(f"representation-hypotheses-{lang}.svg")


def testing(lang):
    ko = lang == "ko"
    title = "찾아낸 설명을 어떻게 시험할까" if ko else "How should a neuron explanation be tested?"
    desc = ("리뷰의 후속 실험 제안. 설명 발견, 미리 정한 새 입력에서 활성 예측, 대조군을 포함한 인과 개입, 출력과 회로 평가를 순서대로 연결한다. 원 뉴런과 희소 오토인코더 특징을 같은 조건에서 비교하고 실패 조건을 다음 설명 수정에 쓴다. 아래 순서는 완료된 연구 결과가 아니다."
            if ko else "Proposed tests for this review, not completed experiments. Discover an explanation, predict activation on prespecified held-out inputs, intervene with controls, then evaluate behavior and circuit claims. Compare native neurons with sparse-autoencoder features under matched conditions; use failures to revise the next hypothesis.")
    d = Diagram(1580, title, desc)
    d.text(45, 66, title, 39, 700)
    d.text(45, 111, "읽기 좋은 설명이 새 입력과 모델의 행동까지 예측하는지 묻는다." if ko else "Ask whether a readable explanation predicts activations and behavior.", 26, fill=MUTED)
    steps = [
        ("1 · 설명 발견 → 가설 고정", ["눈에 띄는 예에서 규칙을 제안한다.", "검사용 입력을 보기 전에 예측 기준을 정한다."], BLUE),
        ("2 · 새 입력에서 활성 예측", ["맞는 예·반례, 약한 활성, 분포 밖 입력을 포함한다.", "어디서 켜지는지, 부호와 크기까지 예측한다."], TEAL),
        ("3 · 대조군을 둔 인과 개입", ["제거·패칭·설명으로 예측한 값의 대체를 시험한다.", "개입 강도와 부작용, 대조 개입을 함께 확인한다."], ORANGE),
        ("4 · 출력과 회로에서 확인", ["출력 분포·과제 성능·상류와 하류의 연결을 비교한다.", "맞힌 조건과 실패한 조건을 나누어 설명을 수정한다."], PURPLE),
    ] if ko else [
        ("1 · Discover, then fix the hypothesis", ["Propose a rule from exploratory examples.", "Set predictions before seeing the test inputs."], BLUE),
        ("2 · Predict activations on new inputs", ["Include positives, counterexamples, weak activations and OOD.", "Predict position, sign and magnitude—not just a label."], TEAL),
        ("3 · Intervene with controls", ["Test ablation, patching and replacement with predicted values.", "Check intervention strength, side effects and control edits."], ORANGE),
        ("4 · Evaluate behavior and circuit claims", ["Compare output distributions, task results and circuit links.", "Use successful and failed conditions to revise the explanation."], PURPLE),
    ]
    for i, (heading, lines, color) in enumerate(steps):
        y = 150 + i*230
        d.rect(40, y, 920, 185)
        d.text(70, y+48, heading, 32, 700, color)
        d.lines(70, y+98, lines, 27 if ko else 26, 41)
        if i < 3:
            d.line(500, y+192, 500, y+218, MUTED, 3, True)
    d.line(500, 1035, 500, 1070, MUTED, 3, True)
    d.rect(40, 1080, 920, 285, fill="#f1f4f5", stroke="#9fb4be")
    d.text(70, 1130, "같은 조건에서 두 표현을 비교한다" if ko else "Compare both representations under matched conditions", 31 if ko else 30, 700)
    d.pill(80, 1160, 370, 65, "원 뉴런" if ko else "Native neurons", BLUE, 30)
    d.pill(550, 1160, 370, 65, "SAE 특징" if ko else "SAE features", TEAL, 30)
    d.text(500, 1204, "↔", 34, 700, MUTED, "middle")
    d.lines(70, 1273, ["같은 입력·예산·지표, 대응하는 개입 조건을 맞춘다.", "SAE 재구성 오차와 각 방법의 설명 범위를 함께 보고한다."] if ko else ["Match inputs, budgets, metrics and corresponding interventions.", "Report SAE reconstruction error and each method's scope."], 27 if ko else 26, 42)
    d.text(45, 1422, "실패한 예 → 다음 가설과 검사를 구체화" if ko else "Failed examples → more specific hypotheses and tests", 28, 700, PURPLE)
    d.text(45, 1480, "리뷰의 후속 제안 · 출처: Goodfire; Gao; Bills et al.; Circuit Tracing" if ko else "Proposed tests · Sources: Goodfire; Gao; Bills et al.; Circuit Tracing", 24, fill=MUTED)
    d.lines(45, 1518, ["리뷰 재구성입니다. 완료된 비교 실험이나 모델 성능을 나타내지 않습니다."] if ko else ["Review reconstruction. This does not report completed comparative experiments."], 24, 36, fill=MUTED)
    d.save(f"explanation-tests-{lang}.svg")


if __name__ == "__main__":
    for language in ("ko", "en"):
        representations(language)
        testing(language)
    print("Built four SVG teaching diagrams (1000 px wide; text ≥24 px).")
