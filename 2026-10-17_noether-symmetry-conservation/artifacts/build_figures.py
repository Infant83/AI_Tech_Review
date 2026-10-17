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

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'artifacts'
PAPER = '#fbf9f3'
INK = '#18313c'
TEAL = '#116f79'
ORANGE = '#ae5b36'
BLUE = '#4869a2'

def setup(font):
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype':'path',
                         'font.size':12, 'axes.spines.top':False,
                         'axes.spines.right':False, 'text.color':INK,
                         'axes.labelcolor':INK, 'xtick.color':INK,
                         'ytick.color':INK, 'axes.edgecolor':'#bbc9c6',
                         'savefig.facecolor':PAPER})
    return FontProperties(fname=str(font))

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
    fig,axes=plt.subplots(2,1,figsize=(10.8,7.2),gridspec_kw={'height_ratios':[1,1.05]},facecolor=PAPER)
    labels=['전진 오일러','심플렉틱 오일러','velocity Verlet'] if ko else ['Forward Euler','Symplectic Euler','Velocity Verlet']
    colors=[ORANGE,BLUE,TEAL]
    for index,(key,values) in enumerate(energies.items()):
        axes[0].plot(time,values/values[0],color=colors[index],label=labels[index],lw=1.7)
    axes[0].set_yscale('log')
    axes[0].set_ylabel('에너지 / 초기 에너지' if ko else 'Energy / initial energy',fontproperties=font if ko else None)
    axes[0].set_ylim(0.7,1e9)
    axes[0].legend(prop=font if ko else None,loc='upper left',frameon=False,ncol=1)
    for index,key in enumerate(['symplectic','verlet'],1):
        values=energies[key]
        axes[1].plot(time,values/values[0],color=colors[index],label=labels[index],lw=1.15)
    axes[1].axhline(1,ls='--',color='#687873',lw=1)
    axes[1].set_ylim(.94,1.065)
    axes[1].set_ylabel('확대: 에너지 / 초기 에너지' if ko else 'Zoom: energy / initial energy',fontproperties=font if ko else None)
    axes[1].set_xlabel('시간 (고유 각진동수의 역수 단위)' if ko else 'Time (inverse natural angular-frequency units)',fontproperties=font if ko else None)
    axes[1].legend(prop=font if ko else None,loc='upper right',frameon=True,
                   facecolor=PAPER,edgecolor='none',framealpha=.95)
    for ax in axes:
        ax.set_facecolor(PAPER);ax.set_xlim(0,200);ax.grid(alpha=.18)
    fig.suptitle('같은 방정식도 이산화에 따라 에너지가 달라진다' if ko else 'Discretization changes the computed energy',fontproperties=font if ko else None,fontsize=19,x=.09,ha='left',y=.97)
    fig.text(.09,.915,'리뷰 자체 계산 · h = 0.1 · 2,000단계 · 질량 = 각진동수 = 1' if ko else 'Original teaching calculation · h = 0.1 · 2,000 steps · mass = angular frequency = 1',fontproperties=font if ko else None,fontsize=11,color='#566b70')
    fig.subplots_adjust(left=.12,right=.97,top=.87,bottom=.1,hspace=.25)
    fig.savefig(ART/f'integrator_{lang}.svg',metadata={'Date':None,'Creator':'AI Tech Review; original teaching calculation'})
    fig.savefig(ART/f'integrator_{lang}.png',dpi=130)
    plt.close(fig)

def symmetry_diagram(lang,font):
    ko=lang=='ko'
    fig,ax=plt.subplots(figsize=(10.8,6.3),facecolor=PAPER)
    ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis('off')
    title='대칭에서 보존량까지, 두 가지 조건이 더 필요하다' if ko else 'From symmetry to conservation: dynamics and boundaries matter'
    ax.text(.025,.95,title,fontproperties=font if ko else None,fontsize=18,va='top')
    rows=[('작용의 연속 대칭','법칙을 정하는 작용이 경계항까지만 변한다'),
          ('운동방정식을 만족하는 운동','제1정리가 국소 연속방정식을 준다'),
          ('선택한 영역의 보존량','경계를 통한 순유출이 0이면 총량이 일정하다')]
    if not ko:
        rows=[('Continuous symmetry of the action','The action is invariant up to a boundary term'),
              ('Motion satisfying the equations','The first theorem gives a local continuity equation'),
              ('Charge in the chosen region','The total stays constant if net boundary flux vanishes')]
    for i,(heading,sub) in enumerate(rows):
        y=.69-i*.245
        box=FancyBboxPatch((.03,y),.69,.17,boxstyle='round,pad=0.015,rounding_size=.015',facecolor='#e8f0eb',edgecolor='#b4cec5',linewidth=1)
        ax.add_patch(box)
        ax.text(.055,y+.112,heading,fontproperties=font if ko else None,fontsize=16,color=TEAL,va='center')
        ax.text(.055,y+.05,sub,fontproperties=font if ko else None,fontsize=11.4,va='center')
        if i<2:ax.add_patch(FancyArrowPatch((.37,y-.025),(.37,y-.065),arrowstyle='-|>',mutation_scale=15,color=TEAL,linewidth=1.4))
    ax.text(.77,.785,'제1정리' if ko else 'First theorem',fontproperties=font if ko else None,fontsize=14,color=TEAL)
    ax.text(.77,.715,'연속 전역 대칭' if ko else 'Continuous global',fontproperties=font if ko else None,fontsize=11)
    ax.text(.77,.67,'→ 보존 전류' if ko else '→ conserved current',fontproperties=font if ko else None,fontsize=11)
    ax.text(.77,.485,'제2정리' if ko else 'Second theorem',fontproperties=font if ko else None,fontsize=14,color=ORANGE)
    ax.text(.77,.415,'임의 함수의 국소 대칭' if ko else 'Local symmetry functions',fontproperties=font if ko else None,fontsize=10.6)
    ax.text(.77,.37,'→ 방정식 사이 항등식' if ko else '→ identities of equations',fontproperties=font if ko else None,fontsize=10.6)
    ax.text(.03,.06,'보존 전류 ≠ 경계가 열린 부분계의 일정한 총량' if ko else 'A conserved current does not require a constant total inside an open region.',fontproperties=font if ko else None,fontsize=12,color='#566b70')
    fig.subplots_adjust(left=.015,right=.99,top=.99,bottom=.015)
    fig.savefig(ART/f'symmetry_{lang}.svg',metadata={'Date':None,'Creator':'AI Tech Review; original explanatory diagram'})
    fig.savefig(ART/f'symmetry_{lang}.png',dpi=130)
    plt.close(fig)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--font',type=Path,required=True)
    args=parser.parse_args()
    ART.mkdir(parents=True,exist_ok=True)
    font=setup(args.font)
    time,energies,results=simulate()
    for lang in ['ko','en']:
        integration_plot(lang,font,time,energies)
        symmetry_diagram(lang,font)
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
