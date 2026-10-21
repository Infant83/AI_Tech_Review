"""Original teaching diagrams and a reproducible harmonic-oscillator illustration.

This computes an illustrative initial-value problem, not a paper reproduction or
a time/accuracy-matched benchmark. All quantities are nondimensionalized with
mass and angular frequency equal to one.
"""
from pathlib import Path
import argparse
import csv
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
PAPER = '#fbf9f3'
INK = '#18313c'
TEAL = '#116f79'
ORANGE = '#ae5b36'
BLUE = '#4869a2'
METHODS = ['forward', 'symplectic', 'verlet']
COLORS = [ORANGE, BLUE, TEAL]
# Keep method identity in grayscale and in both panels/languages.
LINESTYLES = ['-', (0, (5, 2.5)), (0, (1.2, 2.4))]

def setup(font):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype':'path',
                         'svg.hashsalt':'noether-review-figures-20261022',
                         'font.size':14, 'axes.spines.top':False,
                         'axes.spines.right':False, 'text.color':INK,
                         'axes.labelcolor':INK, 'xtick.color':INK,
                         'ytick.color':INK, 'axes.edgecolor':'#bbc9c6',
                         'savefig.facecolor':PAPER})
    return FontProperties(fname=str(font))

def save_svg(fig, filename, title, description):
    destination = ART / filename
    fig.savefig(destination, metadata={'Date':None,
                'Creator':'AI Tech Review; artifacts/build_figures.py; original teaching material'})
    svg = destination.read_text(encoding='utf-8')
    # Outlined glyphs remain independent of fonts; title/desc retain semantics.
    start = svg.index('>', svg.index('<svg')) + 1
    svg = svg[:start] + f'\n <title>{escape(title)}</title>\n <desc>{escape(description)}</desc>' + svg[start:]
    destination.write_text('\n'.join(line.rstrip() for line in svg.splitlines())+'\n', encoding='utf-8')

def load_existing_calculation():
    """Render existing verified samples without rewriting numerical sources."""
    with (ART / 'oscillator_data.csv').open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    time = np.array([float(row['time']) for row in rows])
    energies = {key:np.array([float(row[f'energy_{key}']) for row in rows])
                for key in METHODS}
    results = json.loads((ART / 'oscillator_results.json').read_text(encoding='utf-8'))
    assert len(time) == results['steps'] + 1 == 2001
    assert time[0] == 0 and time[-1] == 200
    for key, values in energies.items():
        assert math.isclose(values[0], results['methods'][key]['initial_energy'])
        assert math.isclose(float(np.max(np.abs(values/values[0]-1))),
                            results['methods'][key]['max_relative_energy_error'], rel_tol=1e-12)
    return time, energies, results

def simulate():
    h, n = 0.1, 2000
    states = {key:np.empty((n+1,2)) for key in ['forward','symplectic','verlet']}
    for array in states.values():
        array[0] = [1.,0.]
    for i in range(n):
        q,p=states['forward'][i]
        states['forward'][i+1]=[q+h*p,p-h*q]
        q,p=states['symplectic'][i]
        p_new=p-h*q
        states['symplectic'][i+1]=[q+h*p_new,p_new]
        q,p=states['verlet'][i]
        half=p-h*q/2
        q_new=q+h*half
        states['verlet'][i+1]=[q_new,half-h*q_new/2]
    time=np.arange(n+1)*h
    energies={key:np.sum(value**2,axis=1)/2 for key,value in states.items()}
    summaries={key:{'initial_energy':float(value[0]),'final_energy_ratio':float(value[-1]/value[0]),
                    'min_energy_ratio':float(np.min(value/value[0])),
                    'max_energy_ratio':float(np.max(value/value[0])),
                    'max_relative_energy_error':float(np.max(np.abs(value/value[0]-1)))}
               for key,value in energies.items()}
    exact_forward=(1+h*h)**n
    assert math.isclose(summaries['forward']['final_energy_ratio'],exact_forward,rel_tol=5e-13)
    assert summaries['symplectic']['max_relative_energy_error']<0.053
    assert summaries['verlet']['max_relative_energy_error']<0.002501
    data={'purpose':'Independent teaching calculation; not experimental data or a reproduction.',
          'normalization':{'mass':1,'angular_frequency':1,'initial_q':1,'initial_p':0},
          'step_size':h,'steps':n,'final_time':float(time[-1]),
          'forward_euler_analytic_final_ratio':exact_forward,'methods':summaries,
          'updates':{'forward':'q_next=q+h*p; p_next=p-h*q',
                     'symplectic':'p_next=p-h*q; q_next=q+h*p_next',
                     'verlet':'p_half=p-h*q/2; q_next=q+h*p_half; p_next=p_half-h*q_next/2'}}
    (ART/'oscillator_results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    with (ART/'oscillator_data.csv').open('w',newline='') as handle:
        writer=csv.writer(handle, lineterminator="\n")
        writer.writerow(['time','energy_forward','energy_symplectic','energy_verlet'])
        writer.writerows(zip(time,energies['forward'],energies['symplectic'],energies['verlet']))
    return time,energies,data

def integration_plot(lang, font, time, energies):
    ko=lang=='ko'
    fp=font if ko else None
    fig=plt.figure(figsize=(6,8.2),facecolor=PAPER)
    axes=[fig.add_axes([.17,.505,.78,.225]),fig.add_axes([.17,.17,.78,.225])]
    labels=['전진 오일러','심플렉틱 오일러','velocity Verlet'] if ko else ['Forward Euler','Symplectic Euler','Velocity Verlet']
    title='같은 진동자, 다른 수치 에너지' if ko else 'Three methods, one oscillator'
    fig.text(.055,.969,title,fontproperties=fp,fontsize=18,va='top')
    fig.text(.055,.923,r'$\tau=\omega t,\quad h=\omega\Delta t=0.1$' +
             (' · 2,000단계' if ko else ' · 2,000 steps'),fontproperties=fp,fontsize=13)
    fig.text(.055,.891,r'$m=\omega=1,\ q_0=1,\ p_0=0,\ E_0=1/2$',fontsize=13)
    legend_labels=[
        labels[0]+(' · 최종 비율 ' if ko else ' · final ratio ')+r'$4.39\times10^8$',
        labels[1]+(' · 최대 오차 5.26%' if ko else ' · max error 5.26%'),
        labels[2]+(' · 최대 오차 0.25%' if ko else ' · max error 0.25%')]
    handles=[Line2D([],[],color=c,lw=2.2,ls=s) for c,s in zip(COLORS,LINESTYLES)]
    fig.legend(handles,legend_labels,loc='upper left',bbox_to_anchor=(.05,.875),
               prop=FontProperties(fname=font.get_file(),size=13) if ko else {'size':13},
               frameon=False,handlelength=3.2,labelspacing=.65,borderaxespad=0)
    for index,key in enumerate(METHODS):
        values=energies[key]
        axes[0].plot(time,values/values[0],color=COLORS[index],
                     ls=LINESTYLES[index],lw=2.0,zorder=3+index)
    axes[0].set_yscale('log')
    axes[0].set_yticks([1,1e3,1e6,1e9])
    axes[0].set_yticklabels(['1',r'$10^3$',r'$10^6$',r'$10^9$'])
    axes[0].set_ylim(0.7,1e9)
    axes[0].set_title('A  장시간 변화 · 로그 축' if ko else 'A  Long-time growth · log scale',
                      loc='left',fontproperties=fp,fontsize=14,pad=13)
    for index,key in enumerate(['symplectic','verlet'],1):
        values=energies[key]
        axes[1].plot(time,values/values[0],color=COLORS[index],
                     ls=LINESTYLES[index],lw=1.75,zorder=3+index)
    axes[1].set_ylim(.94,1.065)
    axes[1].set_yticks([.95,1,1.05])
    axes[1].set_yticklabels(['0.95','1.00','1.05'])
    axes[1].set_title('B  1 부근 확대 · 선형 축' if ko else 'B  Zoom around 1 · linear scale',
                      loc='left',fontproperties=fp,fontsize=14,pad=13)
    axes[1].set_xlabel(r'$\tau=\omega t$',fontsize=14,labelpad=8)
    for ax in axes:
        ax.set_facecolor(PAPER);ax.set_xlim(0,200)
        ax.set_xticks([0,50,100,150,200])
        ax.tick_params(labelsize=12,pad=5)
        ax.set_ylabel(r'$E/E_0$',fontsize=15,labelpad=7)
        ax.axhline(1,ls=(0,(2,4)),color='#67736f',lw=1.1,zorder=2)
        ax.grid(axis='x',alpha=.18)
        ax.grid(axis='y',alpha=.18)
        ax.set_axisbelow(True)
    fig.text(.055,.073,('연속 운동의 기준: ' if ko else 'Exact-motion reference: ')+r'$E/E_0=1$',
             fontproperties=fp,fontsize=12.5)
    fig.text(.055,.04,('최대 오차: ' if ko else 'Max error: ')+r'$\max|E/E_0-1|$',
             fontproperties=fp,fontsize=12.5)
    fig.text(.055,.012,'같은 h의 교육용 비교 · 계산비용 미보정' if ko else
             'Same h; teaching comparison, not cost matched',fontproperties=fp,fontsize=11,color='#566b70')
    save_svg(fig,f'integrator_{lang}.svg',title,
             ('위 A는 로그 축, 아래 B는 선형 축의 같은 에너지 비율 E/E0이다. 연속 운동의 기준은 1이다. '
              '실선은 전진 오일러, 파선은 심플렉틱 오일러, 점선은 velocity Verlet이다. '
              'τ=ωt, h=ωΔt=0.1, 2000단계의 기존 리뷰 계산을 표시한다.' if ko else
              'Top A uses a logarithmic scale and bottom B a linear scale for the same energy ratio E/E0. '
              'The exact-motion reference is 1. Solid: forward Euler; dashed: symplectic Euler; dotted: velocity Verlet. '
              'Existing review calculation: tau=omega*t, h=omega*delta_t=0.1, 2000 steps.'))
    plt.close(fig)

def symmetry_diagram(lang,font):
    ko=lang=='ko'
    fp=font if ko else None
    fig,ax=plt.subplots(figsize=(6,8.2),facecolor=PAPER)
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
    title='대칭에서 공간 영역의 보존량까지' if ko else 'From symmetry to conserved charge'
    ax.text(.055,.972,title,fontproperties=fp,fontsize=18 if ko else 17,va='top')
    ax.text(.055,.918,'제1정리: 작용의 대칭 → 전류 → 경계 조건' if ko else
            'First theorem: action → current → boundary',fontproperties=fp,fontsize=12.5)
    rows=[('작용의 연속 전역 대칭','법칙을 정하는 작용은\n경계항까지 불변이다'),
          ('운동방정식을 만족하는 운동','제1정리가 보존 전류를 준다\n국소 연속방정식이 성립한다'),
          ('고정한 공간 영역의 총량 Q','경계의 순유출이 0이면\n영역 안의 보존량 Q가 일정하다')]
    if not ko:
        rows=[('Continuous global symmetry','The action is invariant\nup to a boundary term'),
              ('Motion obeying the equations','The first theorem gives a conserved current:\na local continuity equation holds'),
              ('Charge Q in a fixed spatial region','Zero net boundary flux\nmakes the regional total Q constant')]
    for i,(heading,sub) in enumerate(rows):
        y=.72-i*.22
        box=FancyBboxPatch((.06,y),.88,.16,boxstyle='round,pad=0.015,rounding_size=.015',facecolor='#e8f0eb',edgecolor='#b4cec5',linewidth=1.2)
        ax.add_patch(box)
        ax.text(.095,y+.119,f'{i+1}  '+heading,fontproperties=fp,
                fontsize=15 if ko else 13.6,color=TEAL,va='center')
        ax.text(.095,y+.057,sub,fontproperties=fp,fontsize=13.3 if ko else 12.6,
                linespacing=1.5,va='center')
        if i<2:ax.add_patch(FancyArrowPatch((.5,y-.021),(.5,y-.052),
                            arrowstyle='-|>',mutation_scale=18,color=TEAL,linewidth=1.7))
    # A separate box, without an inference arrow from the first-theorem chain.
    ax.add_patch(FancyBboxPatch((.06,.055),.88,.155,
                 boxstyle='round,pad=0.015,rounding_size=.015',facecolor='#f2e8dd',
                 edgecolor='#d8bda9',linewidth=1.2))
    ax.text(.095,.171,'제2정리 · 임의 함수의 국소 대칭' if ko else
            'Second theorem · local symmetry',fontproperties=fp,fontsize=14 if ko else 13.3,
            color=ORANGE,va='center')
    ax.text(.095,.11,'임의의 함수에 의존하는 대칭은\n운동방정식 사이의 항등식을 준다' if ko else
            'Symmetry depending on arbitrary functions\ngives identities among the field equations',
            fontproperties=fp,fontsize=13 if ko else 12.4,linespacing=1.5,va='center')
    fig.subplots_adjust(left=0,right=1,top=1,bottom=0)
    save_svg(fig,f'symmetry_{lang}.svg',title,
             ('제1정리는 작용의 연속 전역 대칭에서 운동방정식을 만족할 때 보존 전류를 준다. '
              '고정한 공간 영역의 총량이 일정하려면 경계 순유출이 0이어야 한다. '
              '별도 제2정리는 임의 함수에 의존하는 국소 대칭에서 방정식 사이 항등식을 준다.' if ko else
              'The first theorem gives a conserved current from a continuous global symmetry of the action '
              'on solutions of the equations of motion. Constant charge in a fixed region additionally needs '
              'zero net boundary flux. The separate second theorem gives identities among equations '
              'from local symmetries depending on arbitrary functions.'))
    plt.close(fig)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--font',type=Path,required=True)
    parser.add_argument('--figures-only',action='store_true',
                        help='Read existing CSV/JSON; do not rewrite the verified calculation.')
    args=parser.parse_args()
    ART.mkdir(parents=True,exist_ok=True)
    font=setup(args.font)
    time,energies,results=load_existing_calculation() if args.figures_only else simulate()
    for lang in ['ko','en']:
        integration_plot(lang,font,time,energies)
        symmetry_diagram(lang,font)
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
