"""Build original, deterministic explanatory figures for the quasi-RH review.

The region diagrams contain no computed or measured zeros. The log-log chart
compares pure powers, not complete error bounds for pi or psi. The numerical
table reports rounded decimal approximations, with exact integer inputs and
rational exponents retained separately. The proof workflow illustrates checks;
it does not report that any particular proof was independently rebuilt here.

Example invocation from the package directory:
python artifacts/build_figures.py --font /path/to/NanumGothic-Regular.ttf
"""

from pathlib import Path
from decimal import Decimal, localcontext
from fractions import Fraction
import argparse
import csv
import json
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
PREVIEWS = ROOT / "tmp" / "figures"
PAPER = "#fbf9f3"
INK = "#18313c"
MUTED = "#566b70"
GRID = "#cbd4d0"
TEAL = "#116f79"
ORANGE = "#ae5b36"
BLUE = "#4869a2"


def configure(font_path):
    if not font_path.is_file():
        raise FileNotFoundError(f"Korean font not found: {font_path}")
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "svg.fonttype": "path",
        "svg.hashsalt": "quasi-riemann-ai-proof-2026-10-20",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "savefig.facecolor": PAPER,
        "mathtext.fontset": "dejavusans",
    })
    return FontProperties(fname=str(font_path))


def save_figure(fig, stem, lang, title, description):
    """Save outlined SVG to artifacts and a preview outside publication assets."""
    svg_path = ART / f"{stem}_{lang}.svg"
    fig.savefig(svg_path, metadata={
        "Date": None,
        "Creator": "AI Tech Review; original explanatory figure",
        "Title": title,
        "Description": description,
    })
    svg = svg_path.read_text(encoding="utf-8")
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
        encoding="utf-8",
    )
    if "<text" in svg:
        raise AssertionError(f"SVG text was not outlined: {svg_path.name}")
    fig.savefig(PREVIEWS / f"{stem}_{lang}.png", dpi=150)
    plt.close(fig)


def zero_regions(lang, korean_font):
    ko = lang == "ko"
    font = korean_font if ko else None
    fig, axes = plt.subplots(1, 3, figsize=(11.8, 6.2), facecolor=PAPER)
    fig.subplots_adjust(left=0.075, right=0.98, bottom=0.23,
                        top=0.73, wspace=0.25)
    title = ("영점이 놓일 수 있는 띠와 RH의 선" if ko
             else "Candidate zero regions: two strips and the RH line")
    fig.text(0.065, 0.94, title, fontproperties=font, fontsize=20,
             va="top", weight="bold")
    subtitle = ("비자명 영점만 표시하는 개념도 · 영점 자체는 그리지 않았다" if ko
                else "Schematic for nontrivial zeros only · no zeros are plotted")
    fig.text(0.065, 0.866, subtitle, fontproperties=font,
             fontsize=12, color=MUTED)
    panels = [
        {
            "heading": "11/12: 더 약한 주장" if ko else "11/12: weaker claim",
            "low": 1 / 12, "high": 11 / 12,
            "color": ORANGE, "fill": "#f2ded0",
            "fraction": r"$1/12\leq\sigma\leq11/12$",
            "ticks": [0, 1 / 12, 0.5, 11 / 12, 1],
            "ticklabels": ["0", r"$\frac{1}{12}$", r"$\frac{1}{2}$",
                           r"$\frac{11}{12}$", "1"],
        },
        {
            "heading": "7/8: 더 강한 주장" if ko else "7/8: stronger claim",
            "low": 1 / 8, "high": 7 / 8,
            "color": TEAL, "fill": "#cfe6df",
            "fraction": r"$1/8\leq\sigma\leq7/8$",
            "ticks": [0, 1 / 8, 0.5, 7 / 8, 1],
            "ticklabels": ["0", r"$\frac{1}{8}$", r"$\frac{1}{2}$",
                           r"$\frac{7}{8}$", "1"],
        },
        {
            "heading": "RH: 아직 가정" if ko else "RH: still a hypothesis",
            "low": 0.5, "high": 0.5,
            "color": BLUE, "fill": "#d9e2f0",
            "fraction": r"$\sigma=1/2$",
            "ticks": [0, 0.5, 1],
            "ticklabels": ["0", r"$\frac{1}{2}$", "1"],
        },
    ]
    for ax, panel in zip(axes, panels):
        ax.set_facecolor(PAPER)
        ax.set_xlim(-0.055, 1.055)
        ax.set_ylim(0, 1)
        # Gray is the original open critical strip 0 < sigma < 1.
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor="#e9eae5",
                               edgecolor="none", zorder=0))
        for endpoint in [0, 1]:
            ax.axvline(endpoint, color="#84928d", linestyle=(0, (2.5, 3)),
                       linewidth=1.0, zorder=1)
        if panel["low"] < panel["high"]:
            ax.add_patch(Rectangle((panel["low"], 0),
                                   panel["high"] - panel["low"], 1,
                                   facecolor=panel["fill"], edgecolor="none"))
            for edge in [panel["low"], panel["high"]]:
                ax.axvline(edge, color=panel["color"], linewidth=1.8)
            ax.axvline(0.5, color=BLUE, linestyle=(0, (3, 3)),
                       linewidth=1.1, alpha=0.8)
            ax.text(0.5, 0.55, "후보 영역" if ko else "Candidate\nregion",
                    fontproperties=font, fontsize=15, color=panel["color"],
                    ha="center", va="center", linespacing=1.5)
        else:
            ax.axvline(0.5, color=BLUE, linewidth=3.3)
            ax.text(0.57, 0.55, "가설의 선" if ko else "Hypothesized\nline",
                    fontproperties=font, fontsize=13.5, color=BLUE,
                    ha="left", va="center", linespacing=1.5)
        ax.set_title(panel["heading"], fontproperties=font,
                     fontsize=13.5, color=panel["color"], pad=28)
        ax.text(0.5, 1.055, panel["fraction"], fontsize=13,
                color=panel["color"], ha="center", transform=ax.transAxes)
        ax.set_xticks(panel["ticks"], panel["ticklabels"], fontsize=11)
        ax.tick_params(axis="x", length=4, pad=8)
        ax.set_yticks([])
        ax.set_xlabel(r"$\sigma=\mathrm{Re}(s)$", labelpad=11, fontsize=12)
        ax.spines["left"].set_visible(False)
        ax.spines["bottom"].set_position(("outward", 0))
    axes[0].text(-0.10, 1.02, r"$t=\mathrm{Im}(s)$", fontsize=12,
                 color=MUTED, ha="left", transform=axes[0].transAxes)
    note1 = (r"회색 바탕: 원래의 임계띠 $0 < \sigma < 1$. 세로 방향은 임의 높이 $t$를 나타낸다." if ko
             else r"Gray background: the original critical strip $0 < \sigma < 1$. Vertical extent represents arbitrary height $t$.")
    note2 = (r"실선 경계는 후보 영역에 포함된다. $\mathrm{Re}(s) > \beta$의 비영점 주장은 경계 $\sigma = \beta$를 제외하지 않는다." if ko
             else r"Solid strip boundaries remain included: a zero-free claim for $\mathrm{Re}(s) > \beta$ does not exclude $\sigma = \beta$.")
    fig.text(0.065, 0.095, note1, fontproperties=font, fontsize=11,
             color=MUTED)
    fig.text(0.065, 0.047, note2, fontproperties=font, fontsize=11,
             color=MUTED)
    save_figure(fig, "zero_regions", lang, title,
                "Original schematic of candidate nontrivial-zeta-zero regions. "
                "No zero data are plotted. Claimed open zero-free half-planes "
                "do not exclude their boundaries. RH is shown as a hypothesis.")


def prime_error(lang, korean_font):
    ko = lang == "ko"
    font = korean_font if ko else None
    fig, ax = plt.subplots(figsize=(11.8, 6.9), facecolor=PAPER)
    fig.subplots_adjust(left=0.105, right=0.965, bottom=0.25, top=0.76)
    title = ("영점 경계의 지수만 비교하면" if ko
             else "Comparing only the power associated with a zero boundary")
    fig.text(0.07, 0.945, title, fontproperties=font, fontsize=20,
             va="top", weight="bold")
    fig.text(0.07, 0.867,
             "완전한 소수 오차상계가 아닌, 순수 거듭제곱 인자의 교육용 비교" if ko
             else "A teaching comparison of pure powers, not complete prime-counting error bounds",
             fontproperties=font, fontsize=12, color=MUTED)
    x = np.logspace(2, 24, 353)
    factors = [
        (Fraction(11, 12), ORANGE, r"$\beta=11/12:\quad x^{-1/12}$"),
        (Fraction(7, 8), TEAL, r"$\beta=7/8:\quad x^{-1/8}$"),
        (Fraction(1, 2), BLUE, r"$\beta=1/2:\quad x^{-1/2}$"),
    ]
    ax.set_facecolor(PAPER)
    for beta, color, label in factors:
        y = x ** float(beta - 1)
        ax.plot(x, y, color=color, linewidth=2.5, label=label,
                linestyle="--" if beta == Fraction(1, 2) else "-")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1e2, 1e24)
    ax.set_ylim(7e-13, 1.1)
    ax.set_xticks([1e2, 1e6, 1e12, 1e18, 1e24])
    ax.set_yticks([1, 1e-3, 1e-6, 1e-9, 1e-12])
    ax.set_xlabel(r"$x$", fontsize=13, labelpad=8)
    ax.set_ylabel(r"$x^{\beta-1}$", fontsize=15, labelpad=10)
    ax.grid(which="major", color=GRID, linewidth=0.7, alpha=0.8)
    ax.legend(loc="lower left", frameon=True, facecolor=PAPER,
              framealpha=0.97, edgecolor="none", fontsize=11.5,
              labelspacing=0.85)
    note1 = (r"정규화한 거듭제곱 $x^{\beta-1}$만 계산했다. $\pi(x)$ 또는 $\psi(x)$의 실제 오차값을 그린 것이 아니다." if ko
             else r"Only the normalized power $x^{\beta-1}$ is computed. These curves are not actual errors of $\pi(x)$ or $\psi(x)$.")
    note2 = (r"상수, 로그 인자, $\epsilon$과 영점 높이의 기여는 제외했다. $\beta = 1/2$ 곡선은 RH를 가정한 비교다." if ko
             else r"Constants, logarithmic factors, $\epsilon$, and zero-height contributions are omitted. $\beta = 1/2$ is an RH comparison.")
    fig.text(0.07, 0.11, note1, fontproperties=font, fontsize=11,
             color=MUTED)
    fig.text(0.07, 0.06, note2, fontproperties=font, fontsize=11,
             color=MUTED)
    save_figure(fig, "prime_error", lang, title,
                "Original log-log teaching plot of x^(beta-1) for beta=11/12, "
                "7/8 and 1/2 over x from 10^2 to 10^24. Not a complete error "
                "bound for pi or psi; constants, logs, epsilon and zero-height "
                "contributions are omitted. The 1/2 line is hypothetical.")


def proof_path(lang, korean_font):
    ko = lang == "ko"
    font = korean_font if ko else None
    fig, ax = plt.subplots(figsize=(11.8, 8.8), facecolor=PAPER)
    fig.subplots_adjust(left=0.025, right=0.985, top=0.99, bottom=0.01)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    title = ("증명 산출물은 여러 검증 단계를 거친다" if ko
             else "A proof artifact passes through separate checks")
    ax.text(0.035, 0.965, title, fontproperties=font, fontsize=21,
            va="top", weight="bold")
    ax.text(0.035, 0.903,
            "설명용 검증 절차 · 각 단계는 별도의 증거가 필요하다" if ko
            else "Explanatory verification workflow · each stage needs its own evidence",
            fontproperties=font, fontsize=12, color=MUTED, va="top")
    rows_ko = [
        ("자연어 주장과 원고", "정확히 무엇을 주장하는지, 가정과 결론을 읽는다."),
        ("형식 진술 + 정의의 범위 검토", "기호·정의·예외 조건이 원래 수학적 주장과 대응하는가?"),
        ("별도 해답 + 의존성", "실제 solution의 증명, 의존 정리, 공리와 도구 버전을 확인한다."),
        ("Comparator 대응 + 커널 검사", "대상 진술의 일치와 허용 공리 아래의 논리 검사를 구분한다."),
        ("인간의 수학적 이해와 응용", "증명의 핵심, 새로운 방법과 후속 정리의 가정을 평가한다."),
    ]
    rows_en = [
        ("Natural-language claim and manuscript",
         "Read the precise hypotheses and conclusion of the claim."),
        ("Formal statement + audit of definition scope",
         "Do the symbols, definitions and exceptions express the intended mathematics?"),
        ("Separate solution + dependencies",
         "Inspect the actual solution, dependencies, axioms and tool versions."),
        ("Comparator match + kernel check",
         "Distinguish statement matching from logical checking under allowed axioms."),
        ("Human mathematical understanding and applications",
         "Evaluate the core argument, new methods and assumptions of later results."),
    ]
    rows = rows_ko if ko else rows_en
    centers = [0.785, 0.63, 0.475, 0.32, 0.165]
    for index, ((heading, body), center) in enumerate(zip(rows, centers), 1):
        fill = "#e5ecef" if index == 5 else "#e8f0eb"
        edge = "#b5c6d7" if index == 5 else "#b4cec5"
        accent = BLUE if index == 5 else TEAL
        ax.add_patch(FancyBboxPatch(
            (0.12, center - 0.058), 0.83, 0.116,
            boxstyle="round,pad=0.012,rounding_size=0.015",
            facecolor=fill, edgecolor=edge, linewidth=1.0,
        ))
        ax.text(0.065, center, str(index), ha="center", va="center",
                fontsize=18, color=accent, weight="bold")
        ax.text(0.145, center + 0.02, heading, fontproperties=font,
                fontsize=14.2, color=accent, va="center")
        ax.text(0.145, center - 0.024, body, fontproperties=font,
                fontsize=11.1, color=INK, va="center")
        if index < len(rows):
            ax.add_patch(FancyArrowPatch(
                (0.535, center - 0.073), (0.535, centers[index] + 0.073),
                arrowstyle="-|>", mutation_scale=14, linewidth=1.35,
                color=TEAL,
            ))
    ax.text(0.035, 0.035,
            "challenge의 sorry는 문제 진술 템플릿이다. 실제 solution의 증명과 구별해야 한다." if ko
            else "A sorry in the challenge is a statement template; inspect the proof in the separate solution.",
            fontproperties=font, fontsize=11.1, color=ORANGE,
            va="center")
    save_figure(fig, "proof_path", lang, title,
                "Original explanatory verification workflow, not a report of "
                "an independent Lean rebuild. The challenge template is distinct "
                "from the solution proof and its dependencies.")


def teaching_values():
    """Calculate rounded values using Decimal and independently check identities."""
    samples = ["21", "1000000", "1000000000000", "1000000000000000000000000"]
    denominators = [12, 8, 2]
    checks = []
    rows = []
    with localcontext() as ctx:
        ctx.prec = 80
        for x_string in samples:
            x = Decimal(x_string)
            powers = [x ** (-Decimal(1) / Decimal(d)) for d in denominators]
            for d, power in zip(denominators, powers):
                relative = abs(power ** d * x - 1)
                assert relative < Decimal("1e-65"), (x_string, d, relative)
                reference = math.pow(float(x), -1.0 / d)
                assert math.isclose(float(power), reference, rel_tol=3e-14)
            norm = (Decimal("0.04934") * x ** (-Decimal(1) / 4) * x.ln() ** 2
                    + Decimal("0.02636425") * x ** (-Decimal(1) / 8))
            # Independently evaluate the unnormalized expression, then divide by x.
            raw = (Decimal("0.04934") * x ** (Decimal(3) / 4) * x.ln() ** 2
                   + Decimal("0.02636425") * x ** (Decimal(7) / 8))
            assert abs(norm / (raw / x) - 1) < Decimal("1e-65")
            float_reference = (
                0.04934 * math.pow(float(x), -0.25) * math.log(float(x)) ** 2
                + 0.02636425 * math.pow(float(x), -0.125)
            )
            assert math.isclose(float(norm), float_reference, rel_tol=3e-14)
            rows.append({
                "x_exact_integer": x_string,
                "factor_beta_11_12_approx": format(powers[0], ".18E"),
                "factor_beta_7_8_approx": format(powers[1], ".18E"),
                "factor_beta_1_2_approx": format(powers[2], ".18E"),
                "fiori_normalized_bound_approx": format(norm, ".18E"),
            })
        assert abs(Decimal(rows[2]["factor_beta_11_12_approx"]) - Decimal("0.1")) < Decimal("1e-19")
        assert abs(Decimal(rows[3]["factor_beta_7_8_approx"]) - Decimal("0.001")) < Decimal("1e-21")
        assert abs(Decimal(rows[3]["factor_beta_1_2_approx"]) - Decimal("1e-12")) < Decimal("1e-30")
        checks.extend([
            "For d = 12, 8, 2, (x^(-1/d))^d * x = 1 to relative tolerance 1e-65.",
            "Decimal powers and normalized Fiori values agree with separate float calculations to relative tolerance 3e-14.",
            "The normalized Fiori expression equals the unnormalized expression divided by x to relative tolerance 1e-65.",
            "At x=10^12, x^(-1/12)=0.1; at x=10^24, x^(-1/8)=0.001 and x^(-1/2)=10^-12.",
        ])
    data = {
        "purpose": "Original teaching calculations; not zero observations, measured errors, a benchmark or an independent proof verification.",
        "numeric_policy": "Exact integer inputs are stored as strings; rational exponents and decimal coefficients are specified exactly. Numerical outputs are rounded approximations computed with Decimal precision 80, not a claim of exact integer arithmetic or certified interval arithmetic.",
        "plot": {
            "x_min": "100", "x_max": "1000000000000000000000000",
            "sample_count": 353,
            "factors_exact": {
                "beta_11_12": "x^(-1/12)",
                "beta_7_8": "x^(-1/8)",
                "beta_1_2": "x^(-1/2)",
            },
            "excluded": "Constants, logarithmic factors, epsilon and zero-height contributions; curves are not full pi/psi error bounds. beta=1/2 is hypothetical RH comparison.",
        },
        "fiori_normalized_bound": {
            "source": "Andrew Fiori and Mikko Jaskari, Explicit bounds for the prime number theorem, arXiv:2609.23222v2 (2026-10-08), Theorem 1.4 and abstract.",
            "url": "https://arxiv.org/html/2609.23222v2",
            "assumption": "Every nontrivial zeta zero has real part at most 7/8; this calculation does not independently establish that assumption.",
            "formula": "0.04934*x^(-1/4)*(ln(x))^2 + 0.02636425*x^(-1/8)",
            "bounds": "abs(psi(x)-x)/x",
            "domain": "x >= 21 (the theorem gives x > exp(3))",
            "logarithm": "natural",
            "precision": "80-digit Decimal working precision; output rounded to 19 significant decimal digits",
        },
        "samples": rows,
        "independent_checks": checks,
    }
    (ART / "teaching_values.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (ART / "teaching_values.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    # Preserve exact expressions next to all sampled plotted values as well.
    with (ART / "power_factors.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["log10_x", "x_approx", "x^(-1/12)_approx",
                         "x^(-1/8)_approx", "x^(-1/2)_approx"])
        for log_x in np.linspace(2, 24, 353):
            x = 10.0 ** log_x
            writer.writerow([format(log_x, ".16g"), format(x, ".16g"),
                             *[format(x ** (-1.0 / d), ".16g") for d in denominators]])
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, required=True)
    args = parser.parse_args()
    ART.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    korean_font = configure(args.font)
    values = teaching_values()
    for lang in ["ko", "en"]:
        zero_regions(lang, korean_font)
        prime_error(lang, korean_font)
        proof_path(lang, korean_font)
    print(json.dumps({
        "figures": [f"{name}_{lang}.svg"
                    for name in ["zero_regions", "prime_error", "proof_path"]
                    for lang in ["ko", "en"]],
        "preview_directory": str(PREVIEWS),
        "checks": values["independent_checks"],
        "samples": values["samples"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
