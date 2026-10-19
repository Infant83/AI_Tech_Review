"""Create readable, original mobile variants without changing desktop figures.

The regions are schematics, not computed zero locations. Power curves compare
only x^(beta-1), not full prime-counting error bounds. RH remains hypothetical.
The workflow describes checks; this review did not execute a Lean proof rebuild.
"""
from pathlib import Path
from fractions import Fraction
import argparse
import textwrap
from matplotlib.text import Text

from build_figures import (
    ART, PREVIEWS, PAPER, INK, MUTED, GRID, TEAL, ORANGE, BLUE,
    configure, save_figure, plt, np, Rectangle, FancyBboxPatch, FancyArrowPatch,
)


def wrap(text, ko, korean_width=22, english_width=40):
    return textwrap.fill(text, width=korean_width if ko else english_width,
                         break_long_words=False, break_on_hyphens=False)


def save_mobile(fig, stem, lang, title, description):
    """Catch labels that extend beyond the actual output canvas."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas = fig.bbox
    for artist in fig.findobj(match=Text):
        if not artist.get_visible() or not artist.get_text().strip():
            continue
        box = artist.get_window_extent(renderer)
        if box.x0 < -1 or box.y0 < -1 or box.x1 > canvas.width + 1 or box.y1 > canvas.height + 1:
            raise AssertionError(f'Mobile label exceeds canvas: {stem}/{lang}: {artist.get_text()}')
    save_figure(fig, stem, lang, title, description)


def zero_regions_mobile(lang, korean_font):
    ko = lang == 'ko'
    font = korean_font if ko else None
    fig, axes = plt.subplots(3, 1, figsize=(5, 10.1), facecolor=PAPER)
    fig.subplots_adjust(left=.14, right=.95, bottom=.22, top=.86, hspace=.73)
    title = '영점 후보 영역과 RH의 선' if ko else 'Candidate zero regions and RH'
    fig.text(.06, .974, title, fontproperties=font, fontsize=17,
             va='top', weight='bold')
    fig.text(.06, .928, '실제 영점을 그리지 않은 개념도' if ko else 'Schematic only; no zeros are plotted',
             fontproperties=font, fontsize=13.5, color=MUTED, va='top')
    panels = [
        ('11/12: 더 약한 주장' if ko else '11/12: weaker claim', 1/12, 11/12,
         ORANGE, '#f2ded0', r'$1/12\leq\sigma\leq11/12$'),
        ('7/8: 더 강한 주장' if ko else '7/8: stronger claim', 1/8, 7/8,
         TEAL, '#cfe6df', r'$1/8\leq\sigma\leq7/8$'),
        ('RH: 아직 가설' if ko else 'RH: still a hypothesis', .5, .5,
         BLUE, '#d9e2f0', r'$\sigma=1/2$'),
    ]
    for ax, (heading, low, high, color, fill, expression) in zip(axes, panels):
        ax.set_facecolor(PAPER)
        ax.set_xlim(-.035, 1.035)
        ax.set_ylim(0, 1)
        ax.add_patch(Rectangle((0, 0), 1, 1, facecolor='#e9eae5', edgecolor='none'))
        for end in [0, 1]:
            ax.axvline(end, color='#84928d', linestyle=(0, (3, 3)), linewidth=1)
        if low < high:
            ax.add_patch(Rectangle((low, 0), high-low, 1, facecolor=fill, edgecolor='none'))
            for edge in [low, high]:
                ax.axvline(edge, color=color, linewidth=2)
            ax.axvline(.5, color=BLUE, linestyle=(0, (3, 3)), linewidth=1.1)
            ax.text(.5, .62, '영점 후보 영역' if ko else 'Candidate region',
                    ha='center', va='center', fontproperties=font, fontsize=14.5, color=color)
            ax.text(.5, .26, expression, ha='center', va='center', fontsize=14, color=color)
            ticks = [0, low, .5, high, 1]
            labels = ['0', r'$\frac{1}{12}$' if low == 1/12 else r'$\frac{1}{8}$',
                      r'$\frac{1}{2}$', r'$\frac{11}{12}$' if high == 11/12 else r'$\frac{7}{8}$', '1']
        else:
            ax.axvline(.5, color=color, linewidth=3)
            ax.text(.57, .50, '가설의 선' if ko else 'Hypothesis',
                    ha='left', va='center', fontproperties=font, fontsize=14, color=color)
            ticks, labels = [0, .5, 1], ['0', r'$\frac{1}{2}$', '1']
        ax.set_title(heading, fontproperties=font, fontsize=15, color=color, pad=10)
        ax.set_xticks(ticks, labels, fontsize=13.5)
        ax.tick_params(axis='x', pad=5, length=3)
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.set_xlabel(r'$\sigma=\mathrm{Re}(s)$', fontsize=13.5, labelpad=4)
    notes = ('회색 바탕은 원래의 임계띠다.\n세로 방향은 임의 높이 t를 뜻한다.\n띠의 실선 경계도 후보 영역에 포함된다.\nRH의 중앙선은 아직 가설이다.' if ko else
             'Gray: the original critical strip.\nVertical extent: arbitrary height t.\nSolid boundaries remain included.\nThe central RH line is hypothetical.')
    fig.text(.06, .155, notes, fontproperties=font, fontsize=13.5,
             color=MUTED, va='top', linespacing=1.6)
    save_mobile(fig, 'zero_regions_mobile', lang, title,
                'Original mobile schematic. No actual zeros are plotted. '
                'Candidate strip boundaries remain included. RH is hypothetical.')


def prime_error_mobile(lang, korean_font):
    ko = lang == 'ko'
    font = korean_font if ko else None
    fig, ax = plt.subplots(figsize=(5, 8.4), facecolor=PAPER)
    fig.subplots_adjust(left=.20, right=.93, bottom=.32, top=.78)
    title = '영점 경계의 지수만 비교하면' if ko else 'Zero-boundary powers'
    fig.text(.06, .973, wrap(title, ko, 22, 34), fontproperties=font,
             fontsize=17, va='top', weight='bold', linespacing=1.4)
    subtitle = ('완전한 소수 오차상계가 아닌\n순수 거듭제곱 인자의 비교' if ko else
                'Pure powers only, not complete\nprime-counting error bounds')
    fig.text(.06, .895, subtitle, fontproperties=font,
             fontsize=13.5, color=MUTED, va='top', linespacing=1.5)
    x = np.logspace(2, 24, 353)
    ax.set_facecolor(PAPER)
    for beta, color, label in [
        (Fraction(11, 12), ORANGE, r'$11/12:\ x^{-1/12}$'),
        (Fraction(7, 8), TEAL, r'$7/8:\ x^{-1/8}$'),
        (Fraction(1, 2), BLUE, r'$1/2:\ x^{-1/2}$'),
    ]:
        ax.plot(x, x**float(beta-1), color=color, linewidth=2.2, label=label,
                linestyle='--' if beta == Fraction(1, 2) else '-')
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlim(1e2, 1e24); ax.set_ylim(7e-13, 1.1)
    ax.set_xticks([1e2, 1e12, 1e24])
    ax.set_yticks([1, 1e-3, 1e-6, 1e-9, 1e-12])
    ax.tick_params(axis='both', labelsize=13.5)
    ax.set_xlabel(r'$x$', fontsize=15, labelpad=4)
    ax.set_ylabel(r'$x^{\beta-1}$', fontsize=15, labelpad=5)
    ax.grid(which='major', color=GRID, linewidth=.7)
    ax.legend(loc='lower left', fontsize=13.5, facecolor=PAPER,
              framealpha=.97, edgecolor='none', labelspacing=.7)
    notes = ('실제 소수 개수 오차를 그리지 않았다.\n상수·로그·$\\epsilon$·영점 높이의 기여는 제외했다.\n1/2 점선은 RH를 가정한 비교다.' if ko else
             'Not actual prime-counting errors.\nConstants, logs, epsilon and zero-height\ncontributions are omitted. The dashed\n1/2 curve assumes RH.')
    fig.text(.06, .205, notes, fontproperties=font, fontsize=13.5,
             color=MUTED, va='top', linespacing=1.65)
    save_mobile(fig, 'prime_error_mobile', lang, title,
                'Original mobile plot of the normalized power x^(beta-1), '
                'not a complete error bound or observed prime-counting error. '
                'Constants, logs, epsilon and zero-height effects are omitted. RH is hypothetical.')


def proof_path_mobile(lang, korean_font):
    ko = lang == 'ko'
    font = korean_font if ko else None
    fig, ax = plt.subplots(figsize=(5, 11.8), facecolor=PAPER)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
    title = '증명 산출물의 검증 단계' if ko else 'Separate checks for a proof artifact'
    ax.text(.06, .972, wrap(title, ko, 23, 33), fontproperties=font,
            fontsize=17, va='top', weight='bold', linespacing=1.4)
    subtitle = '각 단계는 별도의 증거가 필요하다' if ko else 'Each stage needs its own evidence'
    ax.text(.06, .910, subtitle, fontproperties=font, fontsize=13.5, color=MUTED, va='top')
    rows = [
        ('자연어 주장과 원고', '정확한 가정과 결론을 읽는다.'),
        ('형식 진술과 정의의 범위', '기호·정의·예외가 원래 주장과 대응하는지 살핀다.'),
        ('별도 해답과 의존성', '실제 solution의 증명, 의존 정리, 공리와 도구 버전을 확인한다.'),
        ('Comparator와 커널 검사', '진술의 일치와 허용 공리 아래의 논리 검사를 구분한다.'),
        ('사람의 수학적 이해와 응용', '핵심 논증, 새로운 방법과 후속 정리의 가정을 평가한다.'),
    ] if ko else [
        ('Claim and manuscript', 'Read the exact assumptions and conclusion.'),
        ('Formal statement and scope', 'Check that definitions and exceptions express the intended mathematics.'),
        ('Solution and dependencies', 'Inspect the proof, dependencies, axioms and tool versions.'),
        ('Comparator and kernel check', 'Separate statement matching from logical checks under allowed axioms.'),
        ('Human mathematical review', 'Assess the argument, new methods and assumptions of later results.'),
    ]
    centers = [.800, .645, .490, .335, .180]
    for index, ((heading, body), center) in enumerate(zip(rows, centers), 1):
        fill = '#e5ecef' if index == 5 else '#e8f0eb'
        accent = BLUE if index == 5 else TEAL
        ax.add_patch(FancyBboxPatch((.055, center-.064), .89, .128,
                     boxstyle='round,pad=0.009,rounding_size=0.011',
                     facecolor=fill, edgecolor='#b4cec5', linewidth=1))
        heading = f'{index} · ' + heading
        heading = wrap(heading, ko, 24, 40)
        ax.text(.085, center+.043, heading, fontproperties=font, fontsize=14.5,
                color=accent, va='top', linespacing=1.35)
        body_y = center+.010 if '\n' not in heading else center-.010
        ax.text(.085, body_y, wrap(body, ko, 21, 40), fontproperties=font,
                fontsize=13.5, color=INK, va='top', linespacing=1.5)
        if index < 5:
            ax.add_patch(FancyArrowPatch((.5, center-.077), (.5, centers[index]+.077),
                         arrowstyle='-|>', mutation_scale=13, color=TEAL, linewidth=1.2))
    note = ('이 리뷰에서 실행하지 않은 개념 절차다.\nchallenge의 sorry는 문제 진술 템플릿이며,\n실제 solution의 증명과 구별해야 한다.' if ko else
            'Explanatory workflow; not executed here.\nA challenge template is separate from\nthe solution proof and dependencies.')
    ax.text(.06, .074, note, fontproperties=font, fontsize=13.5,
            color=ORANGE, va='top', linespacing=1.55)
    save_mobile(fig, 'proof_path_mobile', lang, title,
                'Original mobile explanatory workflow, not an executed Lean rebuild. '
                'The challenge statement template is distinct from a separate solution proof and dependencies.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path, required=True)
    args = parser.parse_args()
    ART.mkdir(parents=True, exist_ok=True); PREVIEWS.mkdir(parents=True, exist_ok=True)
    korean_font = configure(args.font)
    for lang in ['ko', 'en']:
        zero_regions_mobile(lang, korean_font)
        prime_error_mobile(lang, korean_font)
        proof_path_mobile(lang, korean_font)
    print('Created six mobile SVGs with outlined, readable labels.')


if __name__ == '__main__':
    main()
