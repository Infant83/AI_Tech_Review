"""Original mathematical illustration; no experimental curve is reconstructed."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch
import numpy as np

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    font_manager.fontManager.addfont(args.font)
    font = FontProperties(fname=args.font)
    plt.rcParams.update({'font.family': font.get_name(), 'font.size': 11,
                         'axes.unicode_minus': False, 'savefig.facecolor': 'white'})
    navy, teal, orange = '#17384c', '#247f8d', '#d49634'
    fig = plt.figure(figsize=(9.2, 4.9), layout='constrained')
    gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.1])
    ax = fig.add_subplot(gs[0, 0])
    phi = np.linspace(0, 2*np.pi, 721)
    ax.plot(np.cos(phi), np.sin(phi), color=teal, lw=2.5)
    for a in [0.25, 1.8, 3.4, 4.95]:
        ax.add_patch(FancyArrowPatch((np.cos(a), np.sin(a)),
                     (np.cos(a+.22), np.sin(a+.22)), arrowstyle='-|>',
                     mutation_scale=15, color=teal, lw=1.8))
    ax.axhline(0, color='#a7b3bb', lw=.8)
    ax.axvline(0, color='#a7b3bb', lw=.8)
    ax.plot([0, np.cos(.72)], [0, np.sin(.72)], color=orange, lw=2)
    ax.scatter([0], [0], s=24, color=navy, zorder=3)
    ax.text(.06, -.14, '전송 영점', color=navy)
    ax.text(.2, .24, r'$|z|/r_C=1$', color=navy)
    ax.set(xlim=(-1.35, 1.35), ylim=(-1.35, 1.35), aspect='equal',
           xlabel=r'Re$(z/r_C)$', ylabel=r'Im$(z/r_C)$')
    ax.set_xticks([-1, 0, 1]); ax.set_yticks([-1, 0, 1])
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.set_title('등진폭 경로에서 위상을 한 바퀴', loc='left', color=navy, pad=18)
    ax.text(.5, -.21, r'$z/r_C=e^{i\varphi},\quad \Delta\varphi=2\pi$',
            transform=ax.transAxes, ha='center', color=navy, fontsize=13)
    bx = fig.add_subplot(gs[0, 1]); bx.axis('off')
    bx.text(.02, .97, '선택한 출력 포트의 광자 예산', va='top', color=navy, fontsize=13)
    bx.text(.02, .80, '최소 affine 3포트 모형의 보고된 상한', color=navy)
    bx.text(.02, .63, r'$\eta_C\leq1/64\ \approx\ 1.56\%$', color=teal, fontsize=23)
    loss = 10*np.log10(64)
    bx.text(.02, .45, rf'$L_{{ins}}\geq {loss:.2f}\ {{\rm dB}}$', color=teal, fontsize=23)
    bx.text(.02, .25, '감쇠기의 위상을 고정한 채 양의 계수\n2개를 조절하는 모형. 추가 경로나 복소\n감쇠 응답을 쓰는 설계는 별도로 평가한다.',
            color=navy, linespacing=1.55, fontsize=10)
    fig.suptitle('등진폭의 위상 제어와 선택 포트의 투과율', color=navy, fontsize=15)
    fig.supxlabel('편집부 개념도 · 왼쪽은 반지름으로 규격화한 수학적 원 · 오른쪽은 SI Eq.(S15)의 보고된 부등식과 산술 대조',
                  fontsize=9, color='#5b707d')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=240)
    plt.close(fig)
    meta = {'kind':'editorial mathematical illustration and reported-inequality arithmetic',
            'measured_data':False,'formula':'z/r_C = exp(i phi), 0 <= phi <= 2 pi',
            'normalization':'Circle is normalized by its arbitrary constant radius; not unit optical transmission.',
            'source_doi':'10.1038/s41467-026-79534-1',
            'source_version':'2026-11-23 Article in Press; Supplementary Note5 Eq.(S15), S12-S13',
            'conditional_model':'Minimal affine three-port architecture with two positive phase-stable attenuation coefficients.',
            'reported_eta_bound':1/64,'arithmetic_loss_dB':float(loss),
            'original_figure_used':False,'experimental_curves_reconstructed':False,
            'output_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
            'output_bytes':args.output.stat().st_size}
    args.output.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')

if __name__ == '__main__':
    main()
