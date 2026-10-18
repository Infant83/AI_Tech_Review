"""Redraw author-reported bulk force-component MAEs as deterministic SVGs."""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

ROOT = Path(__file__).resolve().parents[1]
VALUES = [126.40121, 148.5957, 151.20484, 150.90115]
SOURCE = 'https://github.com/em819/omat24-chemenv-subset/blob/723696de2c26584b8a907ef900690c0caf3c7b68/09_benchmarks/matpes/paper_tables/peratom_force_mae_bulk.csv'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, required=True, help='Openly licensed Korean font file.')
    args = parser.parse_args()
    font = FontProperties(fname=args.font)
    plt.rcParams.update({'svg.fonttype':'path', 'svg.hashsalt':'omat24-force-mae-v1', 'axes.unicode_minus':False})
    for lang in ('ko','en'):
        ko = lang == 'ko'
        fig, ax = plt.subplots(figsize=(11.4, 5.8), facecolor='#fffefa')
        ax.set_facecolor('#fffefa')
        fig.subplots_adjust(left=0.235, right=0.91, top=0.75, bottom=0.21)
        ax.barh(range(4), VALUES, height=.56, color=['#126a72','#a85b31','#78908b','#a2b4ab'], zorder=3)
        ax.invert_yaxis()
        ax.set_xlim(0,185)
        ax.set_xticks([0,40,80,120,160])
        labels = ['전체 데이터','EnvTok','DIRECT','무작위 (시드 평균)'] if ko else ['Full dataset','EnvTok','DIRECT','Random (seed mean)']
        ax.set_yticks(range(4), labels, fontproperties=font, fontsize=13, color='#172f3b')
        for label in ax.get_xticklabels():
            label.set_fontproperties(font)
            label.set_fontsize(11)
            label.set_color('#5b6870')
        ax.tick_params(axis='both', length=0, pad=11)
        ax.xaxis.grid(True, color='#e0e6e1', linewidth=.8, zorder=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xlabel(r'힘 성분 MAE (meV/$\AA$) · 낮을수록 좋음' if ko else r'Force-component MAE (meV/$\AA$) · lower is better', fontproperties=font, fontsize=12, color='#172f3b', labelpad=16)
        for row, value in enumerate(VALUES):
            change = (value/VALUES[0]-1)*100
            suffix = ('기준' if ko else 'baseline') if row == 0 else f'+{change:.1f}%'
            ax.text(value+2.7,row,f'{value:.1f}  ({suffix})',va='center',fontproperties=font,fontsize=12,color='#172f3b')
        fig.text(.06,.91,'벌크 힘 성분 오차 비교' if ko else 'Bulk force-component error',fontproperties=font,fontsize=23,color='#172f3b')
        fig.text(.06,.84,'원자 예산 약 0.5%의 부분집합과 전체 데이터 기준 모델' if ko else 'Subsets with an atom budget of about 0.5%, versus the full-data baseline',fontproperties=font,fontsize=12,color='#5b6870')
        fig.text(.06,.055,'저자 공개 CSV comp 행 재도식화 · 모델 독립 재학습 없음' if ko else 'Redrawn from the authors’ public CSV, comp row · no independent model retraining',fontproperties=font,fontsize=10,color='#5b6870')
        fig.savefig(ROOT/'artifacts'/f'force_mae_{lang}.svg',metadata={'Date':None,'Title':'OMat24 bulk force-component MAE','Description':SOURCE,'Creator':'AI Tech Review deterministic chart'})
        svg_path = ROOT / 'artifacts' / f'force_mae_{lang}.svg'
        svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines()) + '\n')
        plt.close(fig)
    print('Created force_mae_ko.svg and force_mae_en.svg from fixed author-reported values.')

if __name__ == '__main__':
    main()
