#!/usr/bin/env python3
"""Deterministic explanatory figures for the Classiq replay notes.

Dependencies: Python 3, numpy, matplotlib. Uses a locally installed Noto Sans KR
font, embeds glyph paths in SVG, and exports matching 180-dpi PNGs.
All numeric examples are pedagogical calculations, not replay measurements.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, patches
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "concepts"
OUT.mkdir(parents=True, exist_ok=True)
REG = Path(os.environ.get("CLASSIQ_FIGURE_FONT_REGULAR", str(Path.home() / "Library/Fonts/NotoSansKR-Regular.otf")))
BOLD = Path(os.environ.get("CLASSIQ_FIGURE_FONT_BOLD", str(Path.home() / "Library/Fonts/NotoSansKR-Bold.otf")))
for fp in [REG, BOLD]:
    if fp.exists():
        font_manager.fontManager.addfont(str(fp))
plt.rcParams.update({
    "font.family": ["Noto Sans KR", "DejaVu Sans"], "font.size": 16, "axes.unicode_minus": False,
    "svg.fonttype": "path", "svg.hashsalt": "classiq-concepts-20261022",
    "mathtext.fontset": "dejavusans", "figure.facecolor": "white",
    "savefig.facecolor": "white", "axes.edgecolor": "#9eafb3",
    "axes.labelcolor": "#213c45", "text.color": "#213c45",
    "xtick.color": "#49616a", "ytick.color": "#49616a",
})
INK = "#213c45"
MUTED = "#5a7079"
TEAL = "#147d86"
CORAL = "#cf6659"
PALE = "#e9f4f4"
WARM = "#fff0eb"
GRAY = "#e7ecee"
LINE = "#becbd0"
manifest = []


def canvas(title, subtitle, height=7.0):
    fig = plt.figure(figsize=(12, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 12)
    ax.set_ylim(0, height)
    ax.axis("off")
    ax.text(.42, height-.36, title, fontsize=23, fontweight="bold", va="top")
    ax.text(.43, height-.94, subtitle, fontsize=14.5, color=MUTED, va="top")
    return fig, ax


def box(ax, x, y, w, h, title, body="", fc=PALE, ec=TEAL, title_size=17, body_size=14.5):
    ax.add_patch(patches.FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.018,rounding_size=.12", fc=fc, ec=ec, lw=1.25))
    if body:
        ax.text(x+w/2, y+h-.23, title, fontsize=title_size, fontweight="bold", ha="center", va="top")
        ax.text(x+w/2, y+h-.75, body, fontsize=body_size, ha="center", va="top", linespacing=1.6)
    else:
        ax.text(x+w/2, y+h/2, title, fontsize=title_size, fontweight="bold", ha="center", va="center")


def arrow(ax, x1, y1, x2, y2, color=TEAL, style="-|>", lw=1.8, rad=0):
    ax.add_patch(patches.FancyArrowPatch((x1,y1),(x2,y2),arrowstyle=style,
        mutation_scale=13, lw=lw,color=color,connectionstyle=f"arc3,rad={rad}"))


def rule(ax, x1, y1, x2, y2, color=LINE, lw=1.1, **kwargs):
    ax.plot([x1,x2],[y1,y2], color=color, lw=lw, **kwargs)


def finish(fig, ident, title, kind, description, source_urls, parameters=None):
    stem = OUT / ident
    for ext in ["svg", "png"]:
        metadata = {"Date": "2026-10-22", "Creator": "AI Tech Review / deterministic Python"} if ext=="svg" else {"Software": "AI Tech Review / deterministic Python"}
        fig.savefig(stem.with_suffix("."+ext), dpi=180, metadata=metadata)
    plt.close(fig)
    manifest.append({
        "id": ident, "file": str(stem.with_suffix(".svg").relative_to(ROOT)),
        "png": str(stem.with_suffix(".png").relative_to(ROOT)),
        "title": title, "kind": kind, "description": description,
        "source_urls": source_urls, "parameters": parameters or {},
        "sha256": hashlib.sha256(stem.with_suffix(".svg").read_bytes()).hexdigest(),
    })


def platform_workflow():
    fig, ax = canvas("모델에서 결과까지: 도구와 실행 장치의 역할", "이 노트의 Classiq → CUDA-Q 연결 경로를 재구성한 개념도", 7.0)
    xs = [.42, 3.30, 6.18, 9.06]
    titles = ["① 모델 작성", "② 회로 합성", "③ 실행 인터페이스", "④ 결과 해석"]
    bodies = ["Qmod\n변수·연산·제약", "Classiq 합성기\n폭·깊이·게이트·연결성", "CUDA-Q 커널\nsample / observe", "비트열 디코딩\n목적값·확률·신뢰구간"]
    for x,t,b in zip(xs,titles,bodies):
        box(ax,x,3.82,2.52,1.82,t,b,fc=PALE if x<6 else "#f4f7f8")
    for x in xs[:-1]: arrow(ax,x+2.57,4.73,x+2.80,4.73)
    rule(ax,7.44,3.80,7.44,3.28)
    rule(ax,4.50,3.28,10.26,3.28)
    backends = [
        (3.28,"CPU 시뮬레이터","예: qpp-cpu\n고전 메모리에서 회로 모사",PALE,TEAL),
        (6.16,"GPU 시뮬레이터","예: nvidia\n고전 GPU에서 회로 모사",PALE,TEAL),
        (9.04,"실제 QPU","장치의 양자 연산·측정\n지원·접근 조건 확인",WARM,CORAL),
    ]
    for x,t,b,fc,ec in backends:
        arrow(ax,x+1.24,3.28,x+1.24,2.98,color=ec)
        box(ax,x,1.13,2.52,1.82,t,b,fc=fc,ec=ec,title_size=16,body_size=14)
    ax.text(.48,2.54,"고전 코드가\n반복을 제어",fontsize=16,fontweight="bold",color=MUTED,va="top",linespacing=1.65)
    ax.text(.48,1.58,"QAOA: 각도 갱신\nIQAE: 반복 깊이 선택",fontsize=13.5,color=MUTED,va="top",linespacing=1.7)
    rule(ax,.45,.70,11.55,.70)
    ax.text(.47,.48,"CPU/GPU 모사 속도 비교와 실제 QPU의 업무 성능 비교는 평가 대상이 다르다.",fontsize=14.5,color=INK,va="center")
    finish(fig,"01-platform-workflow","Classiq·CUDA-Q·CPU·GPU·QPU 역할 지도","concept",
        "모델 작성, 합성, 실행 인터페이스, 결과 해석을 연결하고 CPU/GPU 시뮬레이션과 실제 QPU를 구별한다. 이 도식은 강연 경로의 설명용 재구성이며 실제 제품 UI가 아니다.",
        ["https://www.youtube.com/watch?v=E4Uko49fBaU&t=2567s","https://nvidia.github.io/cuda-quantum/latest/using/basics/run_kernel.html"])


def grover_geometry():
    n,m=64,4
    theta=math.asin(math.sqrt(m/n))
    r=np.arange(9)
    probs=np.sin((2*r+1)*theta)**2
    assert abs(probs[3]-0.9613189697265625)<1e-12
    fig, ax = canvas("Grover 반복: 위상 표시가 측정확률을 바꾸는 기하", "교육용 정확 계산 · 균등 초기 상태, N = 64개 중 M = 4개가 정답 · 잡음 없음", 6.9)
    geo=fig.add_axes([.045,.275,.425,.48])
    geo.set_xlim(-.46,1.20); geo.set_ylim(-.08,1.24);geo.set_aspect("equal");geo.axis("off")
    t=np.linspace(0,math.pi*.62,250)
    geo.plot(np.cos(t),np.sin(t),c=LINE,lw=1.1)
    geo.annotate("",xy=(1.10,0),xytext=(-.41,0),arrowprops={"arrowstyle":"->","color":MUTED,"lw":1.2})
    geo.annotate("",xy=(0,1.14),xytext=(0,-.05),arrowprops={"arrowstyle":"->","color":MUTED,"lw":1.2})
    geo.text(1.10,-.08,r"$|B\rangle$",fontsize=18,ha="center")
    geo.text(-.10,1.18,r"$|G\rangle$",fontsize=18,ha="center")
    vectors=[(0,TEAL,"시작: θ",(1.00,.22)),(1,"#6a9099","1회: 3θ",(.87,.71)),(3,CORAL,"3회: 7θ",(-.43,1.07))]
    for k,col,lab,txt in vectors:
        a=(2*k+1)*theta
        geo.annotate("",xy=(math.cos(a),math.sin(a)),xytext=(0,0),arrowprops={"arrowstyle":"-|>","color":col,"lw":2.7})
        geo.text(*txt,lab,color=col,fontsize=16,ha="left" if k<3 else "center",va="center")
    geo.add_patch(patches.Arc((0,0),.65,.65,theta1=0,theta2=math.degrees(theta),color=TEAL,lw=2))
    geo.text(.36,.055,r"$\theta$",color=TEAL,fontsize=18)
    ax.text(2.75,1.55,"각 화살표는 2차원 진폭 벡터\n세로 성분의 제곱이 정답 측정확률",fontsize=14,ha="center",linespacing=1.6)
    plot=fig.add_axes([.565,.30,.38,.46])
    plot.plot(r,probs,c=TEAL,lw=2,marker="o",ms=6)
    plot.scatter([3],[probs[3]],s=100,color=CORAL,zorder=3)
    plot.set_xlim(-.25,8.25);plot.set_ylim(0,1.10)
    plot.set_xticks(r);plot.set_yticks([0,.25,.5,.75,1],["0","25","50","75","100"])
    plot.set_xlabel("Grover 반복 횟수 k",fontsize=15)
    plot.set_ylabel("정답 측정확률 (%)",fontsize=15)
    plot.tick_params(labelsize=13)
    plot.spines[["top","right"]].set_visible(False)
    plot.grid(axis="y",color=GRAY,lw=1)
    plot.annotate("k = 3: 96.13%",xy=(3,probs[3]),xytext=(4.05,1.03),fontsize=15,color=CORAL,
        arrowprops={"arrowstyle":"-","color":CORAL})
    ax.text(8.9,1.18,"반복을 더 해도 확률이 계속 커지지 않는다.",fontsize=14.5,ha="center")
    ax.add_patch(patches.FancyBboxPatch((.45,.37),11.08,.65,boxstyle="round,pad=.02,rounding_size=.1",fc=PALE,ec="none"))
    ax.text(6,.69,r"$a=M/N=1/16,\quad \sin^2\theta=a,\quad P_k=\sin^2((2k+1)\theta)$",fontsize=19,ha="center",va="center")
    finish(fig,"02-grover-geometry","Grover의 2차원 회전과 이상적 성공확률","calculation",
        "정답·비정답 중첩의 평면에서 Grover 회전을 표시하고 k=0…8의 이상적 정답 확률을 직접 계산했다. 원영상의 측정 히스토그램을 재현한 그림이 아니다.",
        ["https://arxiv.org/abs/quant-ph/0005055","https://www.youtube.com/watch?v=QtKbkvWgncQ&t=1113s"],
        {"N":n,"M":m,"theta_rad":theta,"iterations":r.tolist(),"success_probabilities":probs.tolist(),"k3_success":float(probs[3])})


def qaoa_subspace():
    states=list(itertools.product([0,1],repeat=5))
    feasible=[sum(s)==3 for s in states]
    assert len(states)==32 and sum(feasible)==10
    fig,ax=canvas("QAOA: 전체 공간을 쓸까, 제약 보존 공간을 쓸까?", "자산 5개 중 정확히 3개 선택 · 타일 하나는 하나의 5비트 상태 · 성능 측정 그래프가 아닌 구조 비교", 7.0)
    centers=[3.0,9.0]
    for idx,cx in enumerate(centers):
        ax.text(cx,5.52,"전체 비트열에서 시작" if idx==0 else "유효 상태에서 시작",fontsize=20,fontweight="bold",ha="center")
        ax.text(cx,5.03,r"$|+\rangle^{\otimes 5}$" if idx==0 else "Dicke 상태: 1이 세 개인 중첩",fontsize=17,color=TEAL,ha="center")
        x0=cx-2.00; y0=4.30; sz=.39; gap=.13
        for j,good in enumerate(feasible):
            x=x0+(j%8)*(sz+gap);y=y0-(j//8)*(sz+gap)
            fc=TEAL if good else GRAY
            if idx==1 and not good: fc="white"
            ax.add_patch(patches.FancyBboxPatch((x,y),sz,sz,boxstyle="round,pad=.01,rounding_size=.055",fc=fc,ec=TEAL if good else (LINE if idx==0 else "#edf1f2"),lw=1))
        ax.text(cx,2.22,"32개 상태 중 유효 상태 10개" if idx==0 else "10개 유효 상태만 탐색",fontsize=18,fontweight="bold",ha="center")
        ax.text(cx,1.65,"선택 개수가 다른 22개 상태도 포함\n제약을 비용층에서 처리" if idx==0 else "상태 준비와 mixer가 제약 보존\n1의 개수 = 3인 부분공간 안에서 이동",fontsize=15,ha="center",va="top",linespacing=1.6)
    rule(ax,6,1.35,6,5.62)
    ax.add_patch(patches.Rectangle((.5,.74),.18,.18,fc=TEAL,ec="none"))
    ax.text(.8,.84,"유효 상태",fontsize=14.5,va="center")
    ax.add_patch(patches.Rectangle((2.4,.74),.18,.18,fc=GRAY,ec=LINE,lw=.7))
    ax.text(2.7,.84,"제약 위반 상태",fontsize=14.5,va="center")
    ax.text(8.1,.84,r"$2^5=32\qquad \binom{5}{3}=10$",fontsize=21,ha="center",va="center")
    ax.text(.48,.34,"공간을 줄이는 설계가 준비·mixer 비용까지 없애는 것은 아니다. 실제 해 품질은 별도 검증한다.",fontsize=14,color=MUTED,va="center")
    finish(fig,"03-qaoa-feasible-subspace","QAOA의 전체 공간과 카디널리티 제약 부분공간","calculation",
        "5비트 상태 32개를 전수 열거하고 정확히 3개의 자산을 선택하는 10개를 강조했다. 2%와 25%는 재현하거나 가상의 분포로 그리지 않았으며 초기 상태·탐색 공간의 차이만 설명한다.",
        ["https://www.youtube.com/watch?v=QtKbkvWgncQ&t=1319s","https://www.youtube.com/watch?v=QtKbkvWgncQ&t=1538s","https://arxiv.org/abs/1411.4028"],
        {"n_assets":5,"cardinality":3,"total_states":32,"feasible_states":10,"bitstring_order":"lexicographic 00000 to 11111"})


def payoff_encoding():
    prices=np.array([80,100,120,140]);prob=np.array([.1,.2,.4,.3]);strike=110
    payoff=np.maximum(prices-strike,0);c=30
    expected=float(prob@payoff);a=expected/c;exercise=float(prob[prices>strike].sum())
    assert expected==13 and abs(a-13/30)<1e-14 and abs(exercise-.7)<1e-14
    fig,ax=canvas("옵션 보수의 기대값을 표시 큐비트의 확률로 바꾸기", "교육용 이산 가격 분포 · 행사가 K = 110 · 보수 g(S) = max(S − K, 0) · 할인 전", 8.1)
    for i,(vals,col,ylab,title) in enumerate([(prob,TEAL,"확률 pᵢ","① 가격이 나올 확률"),(payoff,CORAL,"보수 gᵢ (가격과 같은 단위)","② 가격별로 받을 보수")]):
        p=fig.add_axes([.09+i*.49,.50,.37,.27])
        p.bar(prices,vals,width=11,color=col,zorder=3)
        p.set_xlim(68,151);p.set_xticks(prices);p.set_xlabel("만기 가격 Sᵢ",fontsize=15)
        p.set_ylabel(ylab,fontsize=14);p.set_title(title,fontsize=17,pad=13,fontweight="bold")
        p.set_ylim(0,.5 if i==0 else 36);p.tick_params(labelsize=13)
        p.grid(axis="y",c=GRAY,zorder=0);p.spines[["top","right"]].set_visible(False)
        for x,v in zip(prices,vals): p.text(x,v+(.015 if i==0 else .9),str(v) if i==0 else str(int(v)),ha="center",fontsize=15,color=col,fontweight="bold")
    ax.text(6,3.03,r"$\mathbb{E}[g]=\sum_i p_i g_i=0.1(0)+0.2(0)+0.4(10)+0.3(30)=13$",fontsize=18,ha="center")
    box(ax,.48,1.52,3.35,1.10,"③ 보수를 0–1로 정규화","fᵢ = gᵢ / 30 = (0, 0, 1/3, 1)",title_size=16,body_size=14.5)
    arrow(ax,3.89,2.07,4.17,2.07)
    box(ax,4.24,1.52,3.35,1.10,"④ 가격의 확률로 가중","a = Σᵢ pᵢfᵢ = 13/30 ≈ 0.4333",title_size=16,body_size=14)
    arrow(ax,7.65,2.07,7.93,2.07)
    box(ax,8.00,1.52,3.52,1.10,"⑤ 측정 후 단위 복원","기대 보수 = 30 × a = 13",title_size=16,body_size=14.5)
    # Korean wording is drawn separately to keep the expression readable.
    ax.text(1.95,.91,"표시 비트가 1일 확률은 a,\n그 부분공간의 진폭은 √a",fontsize=14.5,ha="center",va="center",linespacing=1.5)
    ax.text(7.95,.91,"S > K만 표시하면 행사 확률 0.7을 얻는다.\n보수 크기까지 넣어야 기대 보수 13을 얻는다.",fontsize=14.5,ha="center",va="center",linespacing=1.5)
    finish(fig,"04-payoff-probability-encoding","가격 분포·보수·기대값의 확률 인코딩","calculation",
        "가격의 확률과 보수를 별도 축에 표시하고 정규화·가중·역변환으로 기대 보수 13과 표시 비트 확률 13/30을 연결했다. 원영상의 로그정규분포나 실제 시장 입력이 아닌 손계산 예제다.",
        ["https://arxiv.org/abs/quant-ph/0005055","https://www.youtube.com/watch?v=E4Uko49fBaU&t=2358s","https://www.youtube.com/watch?v=diJa_JRJ2F8&t=2181s"],
        {"prices":prices.tolist(),"probabilities":prob.tolist(),"strike":strike,"payoffs":payoff.tolist(),"payoff_normalization":c,"expected_undiscounted_payoff":expected,"indicator_probability":a,"exercise_probability":exercise})


def iqae_loop():
    fig,ax=canvas("IQAE: 측정 통계로 다음 증폭 깊이를 고른다", "동일한 확률 인코딩 A에서 단순 측정과 IQAE를 비교한 절차도 · 수치 실험 결과가 아님", 7.5)
    ax.text(.45,5.79,"단순 측정",fontsize=18,fontweight="bold",color=MUTED)
    box(ax,.49,4.28,2.75,1.23,"상태 준비 A",r"$A|0\rangle$",fc="#f4f7f8",ec=LINE,title_size=17,body_size=18)
    arrow(ax,3.31,4.90,3.70,4.90,color=MUTED)
    box(ax,3.78,4.28,2.75,1.23,"표시 큐비트 측정","k = 0으로 고정",fc="#f4f7f8",ec=LINE,title_size=17,body_size=15)
    arrow(ax,6.60,4.90,6.99,4.90,color=MUTED)
    box(ax,7.07,4.28,4.45,1.23,"1의 비율로 a 추정","같은 깊이의 회로를 반복해 표본 누적",fc="#f4f7f8",ec=LINE,title_size=17,body_size=14.5)
    ax.text(.45,3.75,"IQAE의 적응 반복",fontsize=18,fontweight="bold",color=TEAL)
    items=[("상태 준비 A",r"$A|0\rangle$"),("증폭 연산",r"$Q^k$"),("표시 비트 측정","nₖ번 측정 통계"),("고전 구간 갱신","θ와 a의 신뢰구간")]
    for i,(title,body) in enumerate(items):
        x=.49+i*2.88
        box(ax,x,2.05,2.45,1.23,title,body,title_size=17,body_size=16)
        if i<3: arrow(ax,x+2.51,2.66,x+2.80,2.66)
    # Classical feedback: choose the next k using the current interval.
    rule(ax,10.35,2.02,10.35,1.55,color=CORAL,lw=1.7)
    rule(ax,1.70,1.55,10.35,1.55,color=CORAL,lw=1.7)
    arrow(ax,1.70,1.55,1.70,2.00,color=CORAL)
    ax.text(6.10,1.23,"목표 정밀도까지 반복: 매번 A로 새로 준비해 다음 k 실행",fontsize=14.5,color=CORAL,ha="center")
    ax.text(6,.67,r"$P_k(1)=\sin^2((2k+1)\theta),\quad a=\sin^2\theta$",fontsize=18,ha="center")
    ax.text(6,.26,"샷 수 Σ nₖ와 상태 준비·역준비의 호출량 Σ nₖ(2k+1)은 서로 다른 비용 지표다.",fontsize=14.5,color=MUTED,ha="center")
    finish(fig,"05-iqae-adaptive-loop","단순 측정과 IQAE의 적응적 증폭·추정 루프","concept",
        "같은 인코딩 확률을 반복 측정하는 k=0 방식과, 서로 다른 Grover power·측정 통계·고전적 구간 갱신을 사용하는 IQAE를 비교한다. 고전 Monte Carlo의 모든 기법을 이 상단 경로로 대표하지 않는다.",
        ["https://arxiv.org/abs/1912.05559","https://www.youtube.com/watch?v=E4Uko49fBaU&t=2567s","https://www.youtube.com/watch?v=diJa_JRJ2F8&t=2315s"],
        {"cost_definition":"Q^k A circuit uses 2k+1 calls of A or A† under the standard Grover decomposition; shot count is Σ n_k","no_numerical_benchmark":True})


def resource_scope():
    fig,ax=canvas("큐비트 수를 줄일 때: 회로 비용과 문제 범위를 함께 읽기", "윗부분은 일반적 자원 교환의 개념도 · 아랫부분은 발표 화면의 10주식·10일 설계안 재구성", 9.2)
    ax.text(.47,7.71,"같은 수학적 모델 안에서의 합성 선택",fontsize=18,fontweight="bold")
    box(ax,.49,6.03,5.10,1.27,"임시 큐비트 재사용","폭을 줄이는 대신 깊이가 늘 수 있다.",title_size=18,body_size=15)
    box(ax,6.41,6.03,5.10,1.27,"더 많은 임시 큐비트 활용","폭을 늘려 깊이를 줄일 수 있다.",title_size=18,body_size=15)
    arrow(ax,5.67,6.66,6.33,6.66,style="<->",color=MUTED)
    ax.text(6,5.60,"가능한 교환 관계이며, 모든 모델에서 보장되는 법칙이나 실제 깊이 측정값은 아니다.",fontsize=14.5,color=MUTED,ha="center")
    rule(ax,.48,5.26,11.53,5.26)
    ax.text(.47,4.95,"문제를 나누거나 선택지를 고정하면 비교 범위도 달라진다",fontsize=18,fontweight="bold")
    rows=[
        ("400","큐비트 · 10일 전체","Exact counts · whole horizon","10주식 × 10일 × 4큐비트","롱·숏 보유 수를 각각 표현\n전체 기간을 함께 모델링",PALE,TEAL),
        ("40","큐비트 / 하루","Exact counts · one day at a time","10주식 × 1일 × 4큐비트","날짜 연결은 고전 동적 계획법(DP)\nDP 상태·전이 비용을 별도 계산",PALE,TEAL),
        ("20","큐비트 / 하루","Direction-fixed · one day at a time","10주식 × 1일 × 2큐비트","롱·숏 방향을 미리 고정\n방향 선택·헤지 자유도 축소",WARM,CORAL),
    ]
    for i,(value,unit,title,calc,meaning,fc,ec) in enumerate(rows):
        y=3.45-i*1.14
        ax.add_patch(patches.FancyBboxPatch((.49,y),11.03,1.02,boxstyle="round,pad=.015,rounding_size=.10",fc=fc,ec=ec,lw=1.05))
        ax.text(1.24,y+.67,value,fontsize=29,fontweight="bold",color=ec,ha="center",va="center")
        ax.text(1.24,y+.22,unit,fontsize=11.7,color=ec,ha="center",va="center")
        ax.text(2.48,y+.73,title,fontsize=15.5,fontweight="bold",va="center")
        ax.text(2.48,y+.29,calc,fontsize=14.5,va="center")
        ax.text(8.89,y+.52,meaning,fontsize=14.5,ha="center",va="center",linespacing=1.65)
    ax.text(6,.55,"400 → 40 → 20을 동일한 범위와 표현력을 유지한 단순 압축률로 읽으면 안 된다.",fontsize=15.5,color=INK,ha="center",fontweight="bold")
    finish(fig,"06-resource-scope-tradeoffs","폭·깊이 교환과 다기간 포트폴리오 축소의 범위","concept",
        "일반적인 폭·깊이 교환과 발표 화면의 400큐비트 전체 10일, 하루 40큐비트, 방향 고정 하루 20큐비트를 분리해 설명한다. 일별 처리의 고전 DP 비용과 방향 고정의 헤지 자유도 손실을 보존했다. 원 실험을 재현한 벤치마크가 아니다.",
        ["https://www.youtube.com/watch?v=gaLZNQkcsp8&t=917s","https://www.youtube.com/watch?v=QtKbkvWgncQ&t=2934s","https://docs.classiq.io/qmod-reference/language-reference/uncomputation"],
        {"stocks":10,"whole_horizon_days":10,"exact_counts_qubits_per_stock_day":4,"direction_fixed_qubits_per_stock_day":2,"whole_horizon_qubits":400,"daily_exact_qubits":40,"daily_direction_fixed_qubits":20,"scope_warning":"400 is all 10 days; 40 and 20 are per day; 20 removes direction choice"})


if __name__ == "__main__":
    platform_workflow()
    grover_geometry()
    qaoa_subspace()
    payoff_encoding()
    iqae_loop()
    resource_scope()
    (OUT/"manifest.json").write_text(json.dumps({"figures":manifest},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"count":len(manifest),"output":"figures/concepts","files":[f["file"] for f in manifest]},ensure_ascii=False))
