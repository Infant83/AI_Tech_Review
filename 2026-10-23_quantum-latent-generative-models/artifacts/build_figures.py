"""Original deterministic review figures; published data and review CPU data stay separate.

Run: python artifacts/build_figures.py --font /path/to/NanumGothic-Regular.ttf
Requires numpy and matplotlib. SVG text is outlined. PNGs go to ignored tmp/.
QM9 data are author-reported Table 4 means +/- STANDARD ERROR over 20 seeds,
not independent measurements by this review. Protein protocol is taken from
Proteina Appendix F, not a claim that ORCA's PT-3 announcement used that protocol.
"""
from pathlib import Path
import argparse
import csv
import json
import math
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
PREVIEW = ROOT / "tmp" / "figures"
PAPER, INK, MUTED, GRID = "#fbf9f3", "#18313c", "#566b70", "#cbd4d0"
TEAL, BLUE, ORANGE, PURPLE, GRAY = "#116f79", "#4869a2", "#ae5b36", "#80618b", "#778482"
SOURCE = "https://arxiv.org/html/2508.19857v3#S4.SS2.SSS3"
PMLR = "https://proceedings.mlr.press/v306/bacarreza26a.html"
QM9 = [
    {"latent": "quantum_real", "fcd": 1.410, "fcd_se": .07, "valid_unique": 1962, "valid_unique_se": 75, "novel": 1084, "novel_se": 45},
    {"latent": "quantum_simulated", "fcd": 1.414, "fcd_se": .07, "valid_unique": 1903, "valid_unique_se": 66, "novel": 1073, "novel_se": 36},
    {"latent": "photonic_distinguishable", "fcd": 1.560, "fcd_se": .09, "valid_unique": 1638, "valid_unique_se": 102, "novel": 900, "novel_se": 50},
    {"latent": "bernoulli", "fcd": 1.646, "fcd_se": .09, "valid_unique": 1391, "valid_unique_se": 77, "novel": 790, "novel_se": 44},
    {"latent": "gaussian", "fcd": 1.823, "fcd_se": .07, "valid_unique": 1320, "valid_unique_se": 53, "novel": 768, "novel_se": 35},
]
COLORS = [TEAL, BLUE, ORANGE, PURPLE, GRAY]


def configure(font):
    if not font.is_file():
        raise FileNotFoundError(font)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                         "svg.fonttype": "path", "svg.hashsalt": "quantum-latent-2026-10-23",
                         "axes.spines.top": False, "axes.spines.right": False,
                         "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": GRID,
                         "xtick.color": INK, "ytick.color": INK, "savefig.facecolor": PAPER})
    return FontProperties(fname=str(font))


def save(fig, stem, lang, mobile, title, description):
    suffix = "_mobile" if mobile else ""
    path = ART / f"{stem}{suffix}_{lang}.svg"
    fig.savefig(path, metadata={"Date": None, "Creator": "AI Tech Review; original deterministic figure",
                               "Title": title, "Description": description})
    svg = path.read_text()
    assert "<text" not in svg
    path.write_text("\n".join(line.rstrip() for line in svg.splitlines()) + "\n")
    fig.savefig(PREVIEW / f"{stem}{suffix}_{lang}.png", dpi=120)
    plt.close(fig)


def text(ax, x, y, value, font, size=12, **kw):
    return ax.text(x, y, value, fontproperties=font, fontsize=size, **kw)


def wrapped(value, ko, width=None):
    width = width or (32 if ko else 55)
    return "\n".join(textwrap.fill(line, width=width) for line in value.splitlines())


def box(ax, xy, wh, heading, body, font, color=TEAL, size=12):
    x, y = xy
    w, h = wh
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.01,rounding_size=.02",
                               edgecolor=color, facecolor="white", linewidth=1.5))
    text(ax, x+w/2, y+h*.77, heading, font, size+2, ha="center", va="center", color=color, weight="bold")
    text(ax, x+w/2, y+h*.39, body, font, size, ha="center", va="center", linespacing=1.55)


def arrow(ax, start, end, color=MUTED):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=16,
                                linewidth=1.5, color=color))


def pipeline(lang, mobile, font):
    ko = lang == "ko"
    fig, ax = plt.subplots(figsize=(4.8, 10.5) if mobile else (12, 5.1), facecolor=PAPER)
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    fig.subplots_adjust(left=.025, right=.975, bottom=.03, top=.97)
    title = "광자 표본에서 생성 모델의 평가까지" if ko else "From photon samples to evaluated generations"
    if mobile: title = "광자 표본에서\n생성 모델의 평가까지" if ko else "From photon samples\nto evaluated generations"
    text(ax, .02, .96, title, font, 18, weight="bold", va="top")
    subtitle = "광학 회로가 바꾸는 것은 생성기의 입력 분포다." if ko else "The optical circuit changes the generator's input distribution."
    text(ax, .02, .87 if mobile else .86, wrapped(subtitle, ko) if mobile else subtitle, font, 12, va="top", color=MUTED)
    heads = ["1  잠재변수 z", "2  고전 생성기 G", "3  생성 결과 G(z)", "4  별도 품질 평가"] if ko else ["1  Latent vector z", "2  Classical generator G", "3  Output G(z)", "4  Separate evaluation"]
    bodies = (["QPU에서 모은 광자 점유수\n또는 같은 크기의\n고전 잠재분포", "같은 신경망 구조·\n학습 절차를 사용해\n각 분포마다 다시 학습", "QM9 실험에서는\n분자 그래프를 생성\n(원자 · 결합)", "FCD: 분포 유사성\n유효·고유 분자 수\n학습 집합 밖 새 분자 수"] if ko else
              ["Photon occupancies collected\nfrom a QPU, or a classical\nlatent of the same dimension", "Retrain for each latent using\nthe same architecture\nand training recipe", "The QM9 experiment\ngenerates molecular graphs\n(atoms and bonds)", "FCD: distribution similarity\nValid and unique molecules\nNovel molecules vs training set"])
    if mobile:
        ys = [.665, .475, .285, .095]
        for i, y in enumerate(ys):
            box(ax, (.07, y), (.86, .145), heads[i], bodies[i], font, color=TEAL if i == 0 else BLUE, size=12)
            if i < 3: arrow(ax, (.5, y-.009), (.5, ys[i+1]+.157))
        foot = "QPU: 고정 회로 1개에서 50만 표본을 수집.\n20개 학습 seed는 독립 장치 실험 20회를 뜻하지 않는다." if ko else "QPU: 500,000 samples from one fixed circuit.\n20 training seeds do not mean 20 independent device experiments."
        text(ax, .03, .035, wrapped(foot, ko), font, 9, va="center", color=MUTED)
    else:
        xs = [.02, .27, .52, .77]
        for i, x in enumerate(xs):
            box(ax, (x, .32), (.21, .36), heads[i], bodies[i], font, color=TEAL if i == 0 else BLUE, size=11)
            if i < 3: arrow(ax, (x+.222, .50), (xs[i+1]-.012, .50))
        foot = "QPU 표본은 고정 회로 1개에서 50만 개를 수집했다. 20개 학습 seed는 독립 장치 실험 20회가 아니다.\n도식의 화살표는 데이터 흐름이다. 평가 지표는 GAN 학습 critic의 점수와 구분한다." if ko else "The QPU supplied 500,000 samples from one fixed circuit; 20 training seeds are not 20 independent device experiments.\nArrows show data flow. Evaluation metrics are distinct from the critic score used to train the GAN."
        text(ax, .02, .15, foot, font, 11, va="center", color=MUTED, linespacing=1.7)
    save(fig, "sampling_pipeline", lang, mobile, title, "Original schematic based on Bacarreza et al. (2026), sections IV.2.3 and Appendix E; the latent distribution changes and the model is retrained with the same architecture and recipe; not a measured performance chart.")


def qm9_chart(lang, mobile, font):
    ko = lang == "ko"
    labels = (["양자 1-1 · 실제 QPU", "양자 1-1 · 시뮬레이션", "구별 가능한 광자 1-1", "베르누이", "가우시안"] if ko else
              ["Quantum 1-1 · real QPU", "Quantum 1-1 · simulated", "Distinguishable photons 1-1", "Bernoulli", "Gaussian"])
    if mobile:
        labels = ["양자 1-1\n실제 QPU", "양자 1-1\n시뮬레이션", "구별 가능한\n광자 1-1", "베르누이", "가우시안"] if ko else ["Quantum 1-1\nreal QPU", "Quantum 1-1\nsimulated", "Distinguishable\nphotons 1-1", "Bernoulli", "Gaussian"]
    fig, axes = plt.subplots(3, 1, figsize=(4.5, 12.4), facecolor=PAPER) if mobile else plt.subplots(1, 3, figsize=(13.1, 5.6), facecolor=PAPER)
    fig.subplots_adjust(left=.43 if mobile else .205, right=.95, top=.82 if mobile else .76,
                        bottom=.18 if mobile else .25, hspace=.70, wspace=.70)
    title = "QM9: 논문이 보고한 생성 품질" if ko else "QM9: author-reported generation quality"
    if mobile: title = "QM9 생성 품질:\n논문이 보고한 결과" if ko else "QM9: generation quality\nreported by the authors"
    fig.text(.035, .96, title, fontproperties=font, fontsize=17 if mobile else 20, weight="bold", va="top")
    sub = "모든 잠재차원 32 · 20 seed의 평균 ± 표준오차(SE)" if ko else "All latent dimensions = 32 · mean ± standard error (SE), 20 seeds"
    if mobile: sub = "잠재차원 32 · 학습 seed 20개\n평균 ± 표준오차(SE)" if ko else "Latent dimension 32 · 20 training seeds\nMean ± standard error (SE)"
    fig.text(.035, .865 if mobile else .86, sub, fontproperties=font, fontsize=11 if mobile else 13, color=MUTED, linespacing=1.7)
    titles = ["FCD  (작을수록 좋음)", "유효·고유 분자 수", "새 분자 수"] if ko else ["FCD  (lower is better)", "Valid and unique", "Novel molecules"]
    keys = ["fcd", "valid_unique", "novel"]
    for j, (ax, key, heading) in enumerate(zip(axes, keys, titles)):
        ax.set_facecolor(PAPER)
        for i, row in enumerate(QM9):
            value, se = row[key], row[key+"_se"]
            ax.errorbar(value, i, xerr=se, fmt="o" if i == 0 else "s", color=COLORS[i], markersize=7, capsize=4, linewidth=1.7)
        ax.set_yticks(range(5), labels if mobile or j == 0 else [])
        for label in ax.get_yticklabels(): label.set_fontproperties(font); label.set_fontsize(10 if mobile else 11)
        ax.invert_yaxis(); ax.set_ylim(4.5, -.5)
        ax.set_title(heading, fontproperties=font, fontsize=12, loc="left", pad=14)
        ax.grid(axis="x", color=GRID, alpha=.8, zorder=0)
        ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
        if key == "fcd": ax.set_xlim(1.25, 2.00); ax.set_xticks([1.3, 1.5, 1.7, 1.9])
        elif key == "valid_unique": ax.set_xlim(0, 2350); ax.set_xticks([0, 1000, 2000])
        else: ax.set_xlim(0, 1300); ax.set_xticks([0, 500, 1000])
    foot = ("분자 수는 생성 시도 10,000회당. SE는 seed 간 평균의 불확실성이다.\n실제 QPU: 32개 입력 빈을 채우고 검출 광자 16개 이상인 사건을 사후 선택.\n고정 회로 1개의 표본 50만 개를 재사용했다(독립 장치 실험 20회가 아님).\n출처: Bacarreza 외, Table 4. 리뷰의 독립 재현값이 아니다." if ko else
            "Counts are per 10,000 attempts. SE describes uncertainty in the mean across seeds.\nReal QPU: all 32 input bins populated; post-selection retained detections of at least 16 photons.\n500,000 samples from one fixed circuit were reused (not 20 independent device experiments).\nSource: Bacarreza et al., Table 4. These are not independently reproduced review results.")
    if mobile:
        foot = "생성 시도 10,000회당 분자 수.\n실제 QPU: 32개 빈을 모두 채운 뒤\n검출 광자가 16개 이상인 사건을 사후 선택.\n고정 회로 1개에서 모은 50만 표본을 재사용했다.\n장치 실험을 독립적으로 20회 한 것이 아니다.\nTable 4의 논문 보고값 · 리뷰 독립 재현 아님." if ko else "Counts per 10,000 generation attempts.\nQPU: all 32 input bins populated;\nretain detections of at least 16 photons.\nOne fixed circuit; 500,000 samples reused.\nNot 20 independent device experiments.\nTable 4, author-reported; not reproduced here."
    fig.text(.035, .035, foot, fontproperties=font, fontsize=9 if mobile else 11, color=MUTED, linespacing=1.7)
    save(fig, "qm9_results", lang, mobile, title, "Original chart of author-reported Table 4 means and standard errors over 20 model seeds. Fixed physical-device sample pool; no inference about runtime advantage or wet-lab validation.")


def toy(lang, mobile, font):
    data_path = ART / "toy_points.npz"
    results_path = ART / "toy_results.json"
    if not data_path.exists() or not results_path.exists(): return
    results = json.loads(results_path.read_text())
    if len(results["runs"]) != 3: return
    ko = lang == "ko"
    points = np.load(data_path)
    keys = ["target", "gaussian", "distinguishable", "quantum_simulated"]
    labels = ["학습 표적", "가우시안 잠재분포", "구별 가능한 광자", "양자 광자 · CPU 모사"] if ko else ["Training target", "Gaussian latent", "Distinguishable photons", "Quantum photons · CPU simulation"]
    fig, axes = plt.subplots(2, 2, figsize=(4.8, 11.3), facecolor=PAPER) if mobile else plt.subplots(1, 4, figsize=(13.6, 5.6), facecolor=PAPER)
    fig.subplots_adjust(left=.07 if mobile else .055, right=.97, top=.80 if mobile else .74, bottom=.28, hspace=.5, wspace=.35)
    title = "공개 코드의 단일 루프 toy 실험: 한 seed의 관찰" if ko else "Public-code single-loop toy: one-seed observation"
    if mobile:
        title = "공개 코드의 단일 루프 toy:\n한 seed의 관찰" if ko else "Public-code single-loop toy:\none-seed observation"
        labels = ["학습 표적", "가우시안\n잠재분포", "구별 가능한\n광자", "양자 광자\nCPU 모사"] if ko else ["Training target", "Gaussian\nlatent", "Distinguishable\nphotons", "Quantum photons\nCPU simulation"]
    fig.text(.035, .96, title, fontproperties=font, fontsize=16 if mobile else 19, va="top", weight="bold")
    subtitle = f"CPU · 8 photons / 16 bins · {results['steps_per_latent']:,} steps / latent · seed {results['seed']}"
    if mobile: subtitle = f"CPU · 8 photons / 16 bins\n{results['steps_per_latent']:,} steps / latent · seed {results['seed']}"
    fig.text(.035, .85 if mobile else .85, subtitle, fontproperties=font, fontsize=10.5 if mobile else 12, color=MUTED, linespacing=1.7)
    centers = np.column_stack([5*np.cos(np.arange(7)*2*np.pi/7), 5*np.sin(np.arange(7)*2*np.pi/7)])
    for i, (ax, key, label) in enumerate(zip(axes.flat, keys, labels)):
        xy = points[key]
        # Target rows are grouped by mode; evenly spaced rows display all seven.
        shown = xy[np.linspace(0, len(xy)-1, 1500, dtype=int)]
        ax.scatter(shown[:, 0], shown[:, 1], s=2, alpha=.25, color=[INK, GRAY, ORANGE, TEAL][i], linewidths=0)
        for center in centers: ax.add_patch(Circle(center, .75, fill=False, edgecolor=GRID, linewidth=.7, linestyle="--"))
        ax.set(xlim=(-6.3, 6.3), ylim=(-6.3, 6.3), aspect="equal", xlabel="x", ylabel="y")
        ax.set_xticks([-5, 0, 5]); ax.set_yticks([-5, 0, 5]); ax.set_facecolor(PAPER)
        ax.set_title(label, fontproperties=font, fontsize=11, pad=12)
        if i:
            row = results["runs"][i-1]
            note = f"반경 내 {100*row['within_mode_fraction']:.1f}% · 모드 {row['mode_coverage']}/7" if ko else f"Within radius: {100*row['within_mode_fraction']:.1f}% · modes {row['mode_coverage']}/7"
            if mobile: note = f"반경 내 {100*row['within_mode_fraction']:.1f}%\n모드 {row['mode_coverage']}/7" if ko else f"Within radius: {100*row['within_mode_fraction']:.1f}%\nModes {row['mode_coverage']}/7"
            ax.text(.5, -.30 if mobile else -.25, note, transform=ax.transAxes, fontproperties=font, fontsize=9.5, ha="center", va="top")
    foot = ("점선: 각 표적 중심에서 반경 0.75. 이 반경 내 비율은 리뷰가 정한 진단값이다.\n동일 모델 초기화·학습 데이터. 회로는 손실 없는 단일 루프이며 논문 Figure 1의 3루프와 다르다.\n한 seed의 모사로 분포의 우위·QPU 속도 이득·분자 또는 단백질 성능을 판단할 수 없다." if ko else
            "Dashed circles: radius 0.75 around each target center; the within-radius fraction is a review-defined diagnostic.\nSame model initialization and data. This lossless single loop differs from the paper's three-loop Figure 1.\nOne simulated seed does not establish latent superiority, QPU speedup, or molecular/protein performance.")
    if mobile:
        foot = "점선: 표적 중심 반경 0.75(리뷰 진단값).\n동일 초기화·학습 데이터, 손실 없는 단일 루프.\n논문 Figure 1의 3루프나 실제 QPU를 재현하지 않았다.\n한 seed로 우위·속도 이득·분자/단백질 성능을 입증하지 못한다." if ko else "Dashed circles: radius 0.75; review-defined diagnostic.\nSame initialization and data; lossless single loop.\nDifferent from the paper's three-loop Figure 1; no QPU run.\nOne seed establishes no superiority, speedup, or molecular/protein benefit."
    fig.text(.035, .035, wrapped(foot, ko) if mobile else foot, fontproperties=font, fontsize=8.5 if mobile else 10.5, color=MUTED, linespacing=1.75)
    save(fig, "toy_latents", lang, mobile, title, "Review CPU run of pinned official single-loop toy code with a separately checked distinguishable-photon control. One seed; not the paper's three-loop experiment or physical QPU data.")


def hom(lang, mobile, font):
    ko = lang == "ko"
    fig, axes = plt.subplots(2, 1, figsize=(4.8, 10.3), facecolor=PAPER) if mobile else plt.subplots(1, 2, figsize=(11.5, 5.5), facecolor=PAPER)
    fig.subplots_adjust(left=.17 if mobile else .12, right=.95, top=.77 if mobile else .73,
                        bottom=.21 if mobile else .28, hspace=.70, wspace=.28)
    title = "두 광자가 만드는 확률의 차이" if ko else "How two photons change output probabilities"
    if mobile and not ko: title = "How two photons change\noutput probabilities"
    fig.text(.035, .96, title, fontproperties=font, fontsize=18 if mobile else 20, weight="bold", va="top")
    sub = "이상적인 50:50 빔 분할기 · 서로 다른 입력 모드에 광자 1개씩" if ko else "Ideal 50:50 beam splitter · one photon in each of two input modes"
    if mobile: sub = "이상적인 50:50 빔 분할기\n서로 다른 입력 모드에 광자 1개씩" if ko else "Ideal 50:50 beam splitter\nOne photon in each of two input modes"
    fig.text(.035, .85 if mobile else .85, sub, fontproperties=font, fontsize=11.5 if mobile else 13, color=MUTED, linespacing=1.7)
    titles = ["광자를 완전히 구별할 수 있을 때", "광자를 완전히 구별할 수 없을 때"] if ko else ["Fully distinguishable photons", "Fully indistinguishable photons"]
    for ax, probabilities, heading, color in zip(axes, [[.25, .5, .25], [.5, 0, .5]], titles, [ORANGE, TEAL]):
        ax.set_facecolor(PAPER)
        ax.bar(range(3), probabilities, color=color, width=.58, zorder=3)
        for i, value in enumerate(probabilities):
            ax.text(i, value+.025, ["0", "1/4", "1/2"][{0: 0, .25: 1, .5: 2}[value]], ha="center", va="bottom", fontsize=13, color=color)
        ax.set_xticks(range(3), ["(2, 0)", "(1, 1)", "(0, 2)"])
        ax.set_ylim(0, .64); ax.set_yticks([0, .25, .5], ["0", "1/4", "1/2"])
        ax.set_title(heading, fontproperties=font, fontsize=12.5, loc="left", pad=14)
        ax.set_xlabel("출력 모드의 광자 수 $(n_1, n_2)$" if ko else "Photon counts in output modes $(n_1, n_2)$", fontproperties=font, fontsize=11)
        ax.set_ylabel("확률" if ko else "Probability", fontproperties=font, fontsize=11)
        ax.grid(axis="y", color=GRID, zorder=0, alpha=.7)
    foot = ("구별할 수 없는 두 광자는 같은 파형·편광으로 동시에 도착하는 무손실 이상 조건이다.\n한 출력에 2개가 모이고, 양쪽에 1개씩 나오는 사건은 억제된다(Hong–Ou–Mandel 간섭).\n이 예는 다광자 간섭의 원리 설명이며 계산 우위의 증거는 아니다." if ko else
            "Indistinguishable case: ideal lossless conditions, identical wave packets and polarization, simultaneous arrival.\nBoth photons leave together; one photon in each output is suppressed (Hong-Ou-Mandel interference).\nThis illustrates multiphoton interference; it does not establish a computational advantage.")
    fig.text(.035, .035, wrapped(foot, ko) if mobile else foot, fontproperties=font, fontsize=9 if mobile else 11, color=MUTED, linespacing=1.7)
    save(fig, "hom_interference", lang, mobile, title, "Original exact ideal two-photon beam-splitter calculation. Distinguishable probabilities (1/4,1/2,1/4); indistinguishable probabilities (1/2,0,1/2). Lossless balanced splitter, one photon per distinct spatial input; ideal indistinguishable photons have matching wave packets/polarization and arrive simultaneously. Not a computational-advantage benchmark.")


def write_data():
    for row in QM9:
        row["fcd_reported"] = f"{row['fcd']:.3f} ± {row['fcd_se']:.2f}"
        row["valid_unique_reported"] = f"{row['valid_unique']} ± {row['valid_unique_se']}"
        row["novel_reported"] = f"{row['novel']} ± {row['novel_se']}"
    data = {"source": SOURCE, "published_version": PMLR, "table": 4,
            "evidence": "author-reported; not independently reproduced",
            "spread": "standard error of the mean over 20 training seeds",
            "latent_dimension": 32, "generation_attempts_per_evaluation": 10000,
            "qpu": {"nominal_effective_photons": 16, "channels": 32, "collected_samples": 500000, "circuit_realizations": 1,
                    "post_selection": "all 32 input bins populated; detections with fewer than 16 photons discarded",
                    "training_seed_scope": "20 training seeds reuse one hardware sample pool, not 20 independent device experiments"},
            "metrics": {"fcd": "Frechet ChemNet Distance; lower is better",
                        "valid_unique": "number of chemically valid, nonduplicated molecules; higher is better",
                        "novel": "valid and unique molecules absent from training set; higher is better"},
            "rows": QM9}
    (ART / "qm9_table4.json").write_text(json.dumps(data, indent=2) + "\n")
    with (ART / "qm9_table4.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(QM9[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(QM9)
    protein = {"source": "https://arxiv.org/html/2503.00710v1#A6", "scope": "original Proteina computational protocol; not verified PT-3 setup",
               "sequence_designer": "ProteinMPNN", "sequences_per_backbone": 8, "sampling_temperature": .1,
               "structure_predictor": "ESMFold", "scRMSD_atoms": "C-alpha", "alignment": "optimal Kabsch rotation and translation", "evaluation_code_commit": "a44b407daf6a5358e43cd68907f3e3f1cbc65fdc", "designability": "minimum self-consistency RMSD across 8 sequences < 2 angstrom",
               "wet_lab_validation": "not established by this metric"}
    (ART / "protein_metric.json").write_text(json.dumps(protein, indent=2) + "\n")
    hom_data = {"kind": "exact ideal teaching calculation, not measured data", "outcomes": [[2, 0], [1, 1], [0, 2]],
                "distinguishable_probabilities": [.25, .5, .25], "indistinguishable_probabilities": [.5, 0, .5],
                "conditions": "lossless balanced beam splitter; one photon in each spatial input; indistinguishable photons have matching wave packets and polarization and arrive simultaneously",
                "scope": "multiphoton interference illustration, not computational advantage"}
    assert sum(hom_data["distinguishable_probabilities"]) == sum(hom_data["indistinguishable_probabilities"]) == 1
    (ART / "hom_probabilities.json").write_text(json.dumps(hom_data, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, required=True)
    args = parser.parse_args()
    ART.mkdir(exist_ok=True); PREVIEW.mkdir(parents=True, exist_ok=True)
    font = configure(args.font)
    write_data()
    for lang in ["ko", "en"]:
        for mobile in [False, True]:
            pipeline(lang, mobile, font); qm9_chart(lang, mobile, font)
            hom(lang, mobile, font); toy(lang, mobile, font)
    print("Built KO/EN desktop and mobile figure variants.")


if __name__ == "__main__":
    main()
