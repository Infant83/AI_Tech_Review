#!/usr/bin/env python3
"""Render an original figure from published results; does not rerun experiments.

Reproduce: python build_evidence_figure.py
Requires matplotlib. Font: macOS Apple SD Gothic Neo.
All axes are linear and start at zero. Each panel has its own metric and scale.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Circle

OUT = Path(__file__).resolve().parent
FONT = Path("/System/Library/Fonts/AppleSDGothicNeo.ttc")
if FONT.exists():
    font_manager.fontManager.addfont(str(FONT))
    plt.rcParams["font.family"] = font_manager.FontProperties(fname=str(FONT)).get_name()
plt.rcParams.update({
    "font.size": 14.5,
    "axes.unicode_minus": False,
    "svg.fonttype": "path",  # stable Korean display without client fonts
    "savefig.facecolor": "white",
    "figure.facecolor": "white",
})

INK = "#253335"
MUTED = "#536367"
GRAY = "#899593"
TEAL = "#347D78"
RED = "#AF514A"
LIGHT = "#F5F8F7"
LINE = "#DDE5E2"

fig = plt.figure(figsize=(10, 11), dpi=100)

def text(x, y, s, size=14.5, color=INK, weight="normal", **kwargs):
    return fig.text(x, y, s, fontsize=size, color=color, weight=weight,
                    ha="left", va="center", **kwargs)

def card(letter, title, top, bottom):
    fig.add_artist(FancyBboxPatch((.04, bottom), .92, top-bottom,
        boxstyle="round,pad=0.008,rounding_size=0.012", linewidth=1,
        edgecolor=LINE, facecolor=LIGHT, transform=fig.transFigure, zorder=-1))
    fig.add_artist(Circle((.081, top-.032), .018,
        facecolor=TEAL, edgecolor="none", transform=fig.transFigure))
    fig.text(.081, top-.032, letter, color="white", fontsize=16,
             weight="bold", ha="center", va="center")
    text(.112, top-.032, title, size=17.5, weight="bold")

def bars(rect, values, labels, colors, xmax, ticks, ticklabels, value_labels):
    ax = fig.add_axes(rect, facecolor="none")
    ypos = [1, 0]
    ax.barh(ypos, values, height=.39, color=colors, zorder=3)
    ax.set_xlim(0, xmax)
    ax.set_ylim(-.6, 1.6)
    ax.set_yticks(ypos, labels)
    ax.set_xticks(ticks, ticklabels)
    ax.tick_params(axis="both", labelsize=14, colors=MUTED,
                   length=0, pad=8)
    ax.grid(axis="x", color=LINE, linewidth=.8, zorder=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.axvline(0, color="#BAC7C3", linewidth=1.0)
    for y, val, lab in zip(ypos, values, value_labels):
        ax.text(val+xmax*.018, y, lab, fontsize=15, color=INK,
                va="center", ha="left", weight="bold", clip_on=False)
    return ax

text(.05, .96, "세 연구가 개선한 것은 서로 다르다", size=23, weight="bold")
text(.05, .922, "설계 자원 · 생성·평가 시간 · 장치 정확도를 각각 읽기", size=15.5, color=MUTED)

card("A", "Anthropic  |  가역 Gaussian 회로의 설계 자원", .884, .615)
text(.075, .815, "Toffoli 수", size=15.5, weight="bold")
text(.656, .815, "최대 동시 논리 큐비트", size=15.5, weight="bold")
bars([.235, .704, .32, .098], [24000, 1583], ["기준선", "LLM 설계"],
     [GRAY, TEAL], 31000, [0, 12000, 24000], ["0", "12,000", "24,000"],
     ["24,000", "1,583"])
bars([.655, .704, .245, .098], [362, 139], ["", ""],
     [GRAY, TEAL], 460, [0, 200, 400], ["0", "200", "400"], ["362", "139"])
text(.075, .645, "39배는 Toffoli × 큐비트의 비용 절감", size=15.5, weight="bold", color=TEAL)
text(.075, .624, "실제 QPU 실행시간을 측정한 배수가 아님", size=14.0, color=MUTED)

card("B", "DQAOA-GPT  |  학습 후 생성·평가에 걸린 시간", .585, .346)
text(.075, .518, "N = 100개 결정변수 · n = 12큐비트 부분문제 · 100회 반복", color=MUTED)
bars([.25, .410, .65, .094], [683.99, 28], ["DQAOA", "DQAOA-GPT"],
     [GRAY, TEAL], 850, [0, 300, 600], ["0", "300", "600초"],
     ["683.99초", "약 28초"])
text(.075, .369, "단일 H200 모사 · 후보 10개 평가 포함 · 사전 학습비 제외", size=14.3, color=MUTED)

card("C", "ADAPT-GQE  |  같은 생성 회로의 에너지 오차", .316, .064)
text(.075, .249, "Gemma 회로 · 12큐비트 · CASCI 기준 오차 · 작을수록 좋음", color=MUTED)
bars([.25, .143, .65, .094], [1.15, 200.4], ["이상적 모사", "Helios-1 실기기"],
     [TEAL, RED], 270, [0, 100, 200], ["0", "100", "200 mHa"],
     ["1.15 mHa", "200.4 mHa"])
text(.075, .094, "빠른 회로 생성과 실제 장치의 정확성은 별도 과제", size=15.5, weight="bold", color=INK)
text(.075, .072, "실기기: 500 shots/회로 · 대칭 검증 적용 · shot noise 18.1 mHa", size=14.0, color=MUTED)

text(.05, .028, "원문 보고값 재도식화 · 실험 재실행 아님 · 각 패널의 단위와 축은 독립", size=13.6, color=MUTED)

png = OUT / "reported_results_boundaries.png"
svg = OUT / "reported_results_boundaries.svg"
fig.savefig(png, dpi=100, metadata={"Title": "세 연구가 개선한 것은 서로 다르다"})
fig.savefig(svg, metadata={"Title": "세 연구가 개선한 것은 서로 다르다",
    "Description": "Independent panels show Toffoli/qubit resources, GPU simulated runtime, and energy error. Replotted from three primary papers; not independently rerun."})
print(png)
print(svg)
