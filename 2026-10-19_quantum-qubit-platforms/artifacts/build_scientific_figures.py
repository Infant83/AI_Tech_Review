#!/usr/bin/env python3
"""Original, reproducible scientific figures for the 2026-10-19 qubit review.

Run with Python 3.12, matplotlib 3.11.2 and numpy 2.5.4. Install matplotlib if
needed. SVG text is outlined for portability; title/desc retain accessible prose.
No external images, paper figure tracing, or network access are used by this script.
Set QUBIT_FIGURE_FONT to a Korean-capable font if Noto Sans KR is unavailable.
"""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
NOTES = ROOT / 'notes'
FONT_PATH = Path(os.environ.get('QUBIT_FIGURE_FONT', str(Path.home() / 'Library/Fonts/NotoSansKR-Regular.otf')))
BOLD_PATH = FONT_PATH.with_name('NotoSansKR-Bold.otf')
if not FONT_PATH.exists():
    raise FileNotFoundError('Set QUBIT_FIGURE_FONT to a Korean-capable font file.')
REG = FontProperties(fname=str(FONT_PATH))
BOLD = FontProperties(fname=str(BOLD_PATH if BOLD_PATH.exists() else FONT_PATH))
plt.rcParams.update({'svg.fonttype':'path', 'svg.hashsalt':'quantum-qubit-review-2026-10-19',
                     'axes.unicode_minus':False, 'figure.facecolor':'#F9FAF7',
                     'savefig.facecolor':'#F9FAF7', 'font.size':12})
C = {'bg':'#F9FAF7','white':'#FFFFFF','navy':'#193342','text':'#304B58',
     'muted':'#687B83','teal':'#237F80','teallight':'#E4F1ED',
     'amber':'#AF7A29','amberlight':'#FAF0D9','line':'#D8E2DF',
     'blue':'#4C7792','faint':'#EEF3F0'}


def canvas(w,h):
    fig = plt.figure(figsize=(w/100,h/100),dpi=100)
    ax = fig.add_axes([0,0,1,1])
    ax.set_xlim(0,w); ax.set_ylim(h,0); ax.axis('off')
    return fig,ax


def text(ax,x,y,s,size=14,color=None,bold=False,ha='left',va='top',**kw):
    return ax.text(x,y,s,fontproperties=BOLD if bold else REG,fontsize=size,
                   color=color or C['text'],ha=ha,va=va,linespacing=1.6,**kw)


def box(ax,x,y,w,h,fill=None,edge=None,r=16,lw=1):
    p=patches.FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0,rounding_size={r}',
        facecolor=fill or C['white'],edgecolor=edge or C['line'],linewidth=lw)
    ax.add_patch(p); return p


def line(ax,xy,color=None,lw=2,**kw):
    pts=np.asarray(xy); ax.plot(pts[:,0],pts[:,1],color=color or C['teal'],lw=lw,
                             solid_capstyle='round',**kw)


def arrow(ax,a,b,color=None,lw=2,style='-|>',**kw):
    p=patches.FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=13,
        linewidth=lw,color=color or C['teal'],**kw)
    ax.add_patch(p); return p


def dot(ax,x,y,r=8,color=None,edge=None,lw=1.5):
    p=patches.Circle((x,y),r,facecolor=color or C['teal'],
                     edgecolor=edge or C['teal'],linewidth=lw);ax.add_patch(p)


def wave(ax,x1,x2,y,amp=6,periods=3,color=None,lw=2):
    xs=np.linspace(x1,x2,200)
    line(ax,np.c_[xs,y+amp*np.sin(np.linspace(0,periods*2*np.pi,len(xs)))],color,lw)


def save(fig,stem,title,desc,png=False):
    file=OUT/f'{stem}.svg'
    fig.savefig(file,format='svg',metadata={'Date':None,'Creator':'AI Tech Review / original programmatic scientific illustration'})
    source=file.read_text()
    start=source.index('<svg ')
    end=source.index('>',start)
    source=source[:end]+ ' role="img" aria-labelledby="figure-title figure-desc"'+source[end:]
    pos=source.index('>',start)+1
    source=source[:pos]+'\n <title id="figure-title">'+escape(title)+'</title>\n <desc id="figure-desc">'+escape(desc)+'</desc>'+source[pos:]
    file.write_text('\n'.join(line.rstrip() for line in source.splitlines())+'\n')
    if png:fig.savefig(OUT/f'{stem}.png',dpi=180,metadata={'Software':'AI Tech Review'})
    # Previews stay outside the review package to keep the publication assets clean.
    fig.savefig(Path(tempfile.gettempdir())/f'{stem}_preview.png',dpi=100)
    plt.close(fig)


def mechanisms():
    fig,ax=canvas(1440,1110)
    text(ax,48,34,'양자정보는 어디에 담기고, 어떻게 연결되는가',26,bold=True)
    text(ax,48,88,'대표적인 물리 구현 6종 · 점은 입자 또는 국소화된 자유도, 선은 제어·결합 경로를 나타낸다.',14,color=C['muted'])
    W,H=432,420
    cards=[(48,145),(504,145),(960,145),(48,590),(504,590),(960,590)]
    titles=['트랩트 이온','중성원자','초전도 회로','반도체 스핀','광자','결함 중심']
    ens=['TRAPPED IONS','NEUTRAL ATOMS','SUPERCONDUCTING CIRCUITS','SEMICONDUCTOR SPINS','PHOTONICS','SOLID-STATE DEFECTS']
    carriers=['정보: 원자의 두 내부 상태','정보: 핵스핀·초미세·광학 상태','정보: 비선형 회로의 두 에너지 준위','정보: 전자·정공·도너의 스핀','정보: 경로·시간·편광 또는 광장','정보: 국소 전자 스핀·주변 핵스핀']
    coupling=['얽힘: Coulomb 결합의 공유 운동','얽힘: 일시적인 Rydberg 상호작용','얽힘: 결합기·마이크로파 제어','얽힘: 교환 결합 · 연결: 스핀 이동','연산: 광학 간섭·측정·조건부 제어','연결: 스핀–광자 얽힘과 광학 측정']
    issues=['확장 과제  이동·냉각·모듈 연결률','확장 과제  원자 손실·재공급·판독','확장 과제  상관 오류·배선·열부하','확장 과제  균일성·판독·반복 정정','확장 과제  전체 광손실·상태 공급률','확장 과제  광자 수집·노드 간 균일성']
    for i,((x,y),title,en,carrier,couple,issue) in enumerate(zip(cards,titles,ens,carriers,coupling,issues)):
        box(ax,x,y,W,H)
        text(ax,x+24,y+19,f'{i+1:02d}',11,color=C['teal'],bold=True)
        text(ax,x+62,y+17,title,18,bold=True)
        text(ax,x+24,y+58,en,9.5,color=C['muted'])
        text(ax,x+24,y+103,carrier,13)
        text(ax,x+24,y+135,couple,13,color=C['teal'])
        line(ax,[(x+24,y+337),(x+W-24,y+337)],C['line'],1)
        text(ax,x+24,y+361,issue,12,color=C['muted'])
    # 1. Electrode rails, ions, collective motion and addressing beam.
    x,y=cards[0]
    box(ax,x+37,y+197,355,15,C['faint'],C['line'],r=4)
    box(ax,x+37,y+289,355,15,C['faint'],C['line'],r=4)
    xs=[x+89,x+171,x+253,x+335]
    wave(ax,x+58,x+371,y+251,6,4,C['teal'],1.8)
    for xx in xs:
        dot(ax,xx,y+251,11,C['white'],C['teal'],2)
        text(ax,xx,y+250,'+',11,color=C['teal'],bold=True,ha='center',va='center')
    arrow(ax,(x+151,y+191),(x+169,y+233),C['amber'],2.8)
    text(ax,x+214,y+310,'공유 운동 모드',10.5,ha='center',color=C['muted'])
    # 2. Trapping potentials (not electronic orbital drawings) and Rydberg-mediated link.
    x,y=cards[1]
    for xx in [x+129,x+300]:
        u=np.linspace(-48,48,100); py=y+293-0.035*u*u
        line(ax,np.c_[xx+u,py],C['blue'],2)
        dot(ax,xx,y+282,9,C['teal'])
        arrow(ax,(xx,y+264),(xx,y+207),C['amber'],1.8)
    line(ax,[(x+129,y+198),(x+300,y+198)],C['amber'],1.8,ls=(0,(3,3)))
    text(ax,x+214,y+173,'Rydberg 결합',10.5,color=C['amber'],ha='center')
    text(ax,x+214,y+310,'광학 포획 퍼텐셜',10.5,ha='center',color=C['muted'])
    # 3. Simplified transmon: junction and capacitor in parallel, unequal energy gaps.
    x,y=cards[2]
    line(ax,[(x+65,y+201),(x+239,y+201),(x+239,y+239)],C['blue'],2)
    line(ax,[(x+239,y+257),(x+239,y+296),(x+65,y+296),(x+65,y+201)],C['blue'],2)
    line(ax,[(x+219,y+239),(x+259,y+239)],C['blue'],3)
    line(ax,[(x+219,y+257),(x+259,y+257)],C['blue'],3)
    line(ax,[(x+56,y+239),(x+74,y+257)],C['amber'],3)
    line(ax,[(x+56,y+257),(x+74,y+239)],C['amber'],3)
    box(ax,x+50,y+232,30,32,C['white'],C['amber'],r=0,lw=1.5)
    line(ax,[(x+56,y+239),(x+74,y+257)],C['amber'],2)
    line(ax,[(x+56,y+257),(x+74,y+239)],C['amber'],2)
    for yy,label,col in [(292,'0',C['teal']),(249,'1',C['teal']),(217,'2',C['line'])]:
        line(ax,[(x+310,y+yy),(x+367,y+yy)],col,2)
        text(ax,x+376,y+yy,label,10,va='center',color=C['muted'])
    text(ax,x+65,y+310,'Josephson 접합',10.5,color=C['muted'])
    # 4. Electrostatic dots, spin direction, exchange and alternative shuttling route.
    x,y=cards[3]
    for xx in [x+116,x+296]:
        box(ax,xx-35,y+190,70,13,C['faint'],C['line'],r=3)
        uu=np.linspace(-43,43,100)
        line(ax,np.c_[xx+uu,y+284-0.03*uu*uu],C['blue'],2)
        dot(ax,xx,y+270,14,C['teallight'],C['teal'])
    arrow(ax,(x+116,y+283),(x+116,y+255),C['teal'],2.2)
    arrow(ax,(x+296,y+257),(x+296,y+283),C['teal'],2.2)
    arrow(ax,(x+157,y+252),(x+255,y+252),C['amber'],2,style='<->')
    text(ax,x+206,y+221,'교환 결합 J',10.5,ha='center',color=C['amber'])
    arrow(ax,(x+113,y+307),(x+299,y+307),C['blue'],1.4,linestyle=(0,(4,3)))
    text(ax,x+206,y+312,'별도 연결 방식: 스핀 이동',9.5,ha='center',color=C['muted'])
    # 5. Dual-rail interferometer and measurement; no direct photon-photon force implied.
    x,y=cards[4]
    for yy in [y+228,y+284]:
        line(ax,[(x+61,yy),(x+160,yy),(x+199,y+256),(x+239,yy),(x+346,yy)],C['blue'],2)
        box(ax,x+348,yy-12,18,24,C['faint'],C['blue'],r=3)
    line(ax,[(x+182,y+284),(x+217,y+228)],C['amber'],4)
    wave(ax,x+77,x+111,y+228,5,2,C['teal'],2)
    text(ax,x+198,y+192,'빔분할기',10.5,ha='center',color=C['amber'])
    text(ax,x+80,y+308,'경로 부호화 예시',10.5,color=C['muted'])
    text(ax,x+354,y+308,'검출',10.5,color=C['muted'],ha='center')
    # 6. Localised defects in two separate lattices linked by emitted photons.
    x,y=cards[5]
    for xx in [x+101,x+324]:
        pts=[(xx-36,y+232),(xx,y+211),(xx+36,y+232),(xx+36,y+274),(xx,y+295),(xx-36,y+274),(xx-36,y+232)]
        line(ax,pts,C['line'],2)
        for a,b in zip(pts[:-1],pts[1:]):
            dot(ax,*a,3,C['white'],C['blue'],1)
        for p in pts[:-1]:line(ax,[p,(xx,y+253)],C['line'],1)
        dot(ax,xx,y+253,11,C['teallight'],C['teal'],1.8)
        arrow(ax,(xx,y+263),(xx,y+242),C['teal'],1.5)
    wave(ax,x+145,x+279,y+253,6,3,C['amber'],2)
    text(ax,x+213,y+209,'광학 링크',10.5,ha='center',color=C['amber'])
    text(ax,x+213,y+309,'원격 얽힘의 성공을 광자로 확인',10,ha='center',color=C['muted'])
    text(ax,48,1041,'개념도 · 장치의 실제 크기·배치·스펙트럼과 무관하다. 보소닉 부호와 오류정정부호는 여러 물리계에 걸쳐 구현된다.',13,color=C['muted'])
    save(fig,'qubit_mechanisms','여섯 양자 큐비트 플랫폼의 정보 저장과 결합 원리',
        '트랩트 이온은 내부 상태와 공유 운동, 중성원자는 내부 상태와 Rydberg 상호작용, 초전도 회로는 비선형 에너지 준위와 회로 결합, 반도체 스핀은 스핀과 교환 결합 또는 이동, 광자는 광학 간섭과 측정, 결함 중심은 국소 스핀과 광학 링크를 이용한다. 전자 궤도나 실제 장치 배치를 묘사한 그림은 아니다.')


def evidence():
    fig,ax=canvas(1440,1040)
    text(ax,48,34,'“큰 장치”와 “오류에 강한 계산”은 다른 증거가 필요하다',25,bold=True)
    text(ax,48,88,'네 가지 질문을 함께 읽는다. 상자의 순서·크기·색은 플랫폼의 성숙도나 우열을 뜻하지 않는다.',14,color=C['muted'])
    cards=[(48,149),(736,149),(48,462),(736,462)]
    entries=[
        ('규모와 물리 자원','무엇을 몇 개 셌는가?',
         '원자·양자점·광학 모드의 수를 구분한다.\n데이터와 측정 보조 자원을 따로 적는다.\n큰 배열의 점유율과 얽힘 게이트를 구분한다.'),
        ('반복 오류정정','얼마나 오래, 어떤 오류를 처리했는가?',
         '중간 측정·초기화·디코딩의 결합을 본다.\n주기당 논리 오류와 연속 라운드를 읽는다.\nX·Z 두 오류축과 소실·누설 처리를 확인한다.'),
        ('코드 확대의 효과','더 큰 부호가 오류를 더 억제하는가?',
         '같은 실험 조건에서 코드 거리를 바꾼다.\n오류막대와 비교한 기준선을 확인한다.\n짧은 실행의 억제가 긴 실행에도 남는지 본다.'),
        ('논리 연산과 계산','보호된 정보를 실제로 조작했는가?',
         '메모리 보존과 논리 게이트를 구분한다.\n비Clifford 자원·측정 후 분기를 확인한다.\n연결·재시도·보정을 포함한 시간을 읽는다.')]
    for idx,((x,y),(title,q,body)) in enumerate(zip(cards,entries)):
        box(ax,x,y,656,285)
        box(ax,x+22,y+24,54,54,C['teallight'],C['teallight'],r=10)
        # Separate small glyphs: no arrows between evidence categories.
        if idx==0:
            for i in range(3):
                for j in range(3):dot(ax,x+36+j*13,y+38+i*13,3,C['teal'],C['teal'],0)
        elif idx==1:
            p=patches.Arc((x+49,y+51),31,31,theta1=30,theta2=330,color=C['teal'],lw=2);ax.add_patch(p)
            arrow(ax,(x+62,y+40),(x+65,y+49),C['teal'],1.6)
        elif idx==2:
            for i in range(3):
                box(ax,x+32+i*12,y+35+i*9,7,27-i*8,C['teal'],C['teal'],r=1)
        else:
            for xx in [x+34,x+51,x+66]:line(ax,[(xx,y+38),(xx,y+65)],C['teal'],1.5)
            for xx,yy in [(x+34,y+44),(x+51,y+58),(x+66,y+44)]:dot(ax,xx,yy,3,C['teal'])
        text(ax,x+98,y+23,title,19,bold=True)
        text(ax,x+98,y+66,q,13,color=C['teal'])
        text(ax,x+26,y+125,body,15)
    box(ax,48,783,1344,181,C['amberlight'],C['amberlight'],r=16)
    text(ax,74,806,'모든 결과에 붙여 읽을 조건',17,bold=True,color=C['navy'])
    text(ax,74,851,'후선택을 썼다면  →  조건부 오류 + 채택률 + 재시도 비용',16,color=C['text'])
    text(ax,74,898,'실험인가 시뮬레이션인가  /  평균인가 최고값인가  /  심사 논문인가 사전공개인가',14,color=C['text'])
    text(ax,48,991,'해석 기준을 정리한 편집부 도식. 모든 플랫폼에 동일한 임계 충실도나 하나의 종합 점수를 부여하지 않는다.',13,color=C['muted'])
    save(fig,'evidence_requirements','양자 하드웨어의 성과를 평가하는 네 가지 증거와 결과 조건',
         '규모와 물리 자원, 반복 오류정정, 코드 확대의 오류 억제, 논리 연산과 계산은 서로 구분하여 검증할 질문이다. 모든 결과에서 후선택 여부와 채택률, 실험 또는 시뮬레이션, 평균 또는 최고값, 심사 논문 또는 사전공개 상태를 확인한다. 이 그림은 성숙도 순위가 아니다.')


def toric():
    fig=plt.figure(figsize=(14.4,9.5),dpi=100,facecolor=C['bg'])
    bg=fig.add_axes([0,0,1,1]);bg.set_xlim(0,1440);bg.set_ylim(950,0);bg.axis('off')
    text(bg,48,34,'큰 코드의 이득은 긴 실행에서도 유지되는가',25,bold=True)
    text(bg,48,89,'같은 중성원자 장치의 두 twisted toric code · 긴 실행에서 측정한 Z 논리 관측량',14,color=C['muted'])
    box(bg,48,150,1344,579,C['white'],C['line'],r=17)
    ax=fig.add_axes([0.135,0.395,0.53,0.37],facecolor=C['white'])
    xs=[0,1]; vals=[0.63,0.64]; errs=[0.03,0.04]
    for x,val,err,color in zip(xs,vals,errs,[C['blue'],C['teal']]):
        ax.errorbar(x,val,yerr=err,fmt='o',markersize=10,capsize=9,capthick=2,
                    elinewidth=2.4,color=color,zorder=4)
        ax.text(x,val+err+0.038,f'{val:.2f} ± {err:.2f}%',ha='center',va='bottom',
                fontproperties=BOLD,fontsize=18,color=color)
    ax.set_xlim(-0.62,1.62);ax.set_ylim(0,0.86)
    ax.set_xticks(xs)
    ax.set_xticklabels(['작은 코드 · det 8','큰 코드 · det 16'],fontproperties=BOLD,fontsize=14,color=C['navy'])
    ax.set_yticks([0,.2,.4,.6,.8])
    ax.set_yticklabels(['0.0','0.2','0.4','0.6','0.8'],fontproperties=REG,fontsize=13,color=C['muted'])
    ax.set_ylabel('Z 논리 오류 / 주기 (%)',fontproperties=REG,fontsize=14,color=C['text'],labelpad=13)
    ax.tick_params(axis='both',length=0,pad=12)
    ax.grid(axis='y',color=C['line'],lw=.8,zorder=0)
    for spine in ['top','right','left']:ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color(C['line'])
    for x,labels in zip(xs,[['데이터 16 + 보조 16','총 32개 원자 · 최대 90주기'],['데이터 32 + 보조 32','총 64개 원자 · 최대 70주기']]):
        ax.text(x,-.135,labels[0],ha='center',va='top',transform=ax.get_xaxis_transform(),fontproperties=REG,fontsize=12,color=C['text'])
        ax.text(x,-.212,labels[1],ha='center',va='top',transform=ax.get_xaxis_transform(),fontproperties=REG,fontsize=11,color=C['muted'])
    box(bg,1010,200,338,400,C['teallight'],C['teallight'],r=13)
    text(bg,1034,228,'관측한 것',15,bold=True,color=C['teal'])
    text(bg,1034,272,'중간 측정·초기화\n손실 원자 교체\n10주기마다 저장소 재공급',14)
    line(bg,[(1034,394),(1324,394)],'#C6DCD5',1)
    text(bg,1034,419,'이 지표의 해석',15,bold=True,color=C['teal'])
    text(bg,1034,464,'보고된 오차 범위가 겹친다.\n긴 실행의 Z 지표에서는\n추가 오류 억제가 확인되지 않았다.',13)
    text(bg,74,674,'점: 긴 실행 데이터에 적합한 상수 주기 오류 모형의 추정값. 막대: 논문이 보고한 ± 불확도.',12,color=C['muted'])
    text(bg,48,768,'숫자의 범위',15,bold=True)
    text(bg,48,809,'메모리 실험의 Z 관측량이다. X·Z 평균, 논리 게이트 오류 또는 다른 플랫폼과의 성능 비교를 나타내지 않는다.',13)
    text(bg,48,846,'짧은 실행의 코드 확대 결과와 긴 실행의 적합값은 조건이 다르므로 직접 합치지 않는다.',13)
    text(bg,48,899,'자료: Atom Computing and Collaborators · arXiv:2606.04079v1, Fig. 3b·§V · 2026-06-02 사전공개',11.5,color=C['muted'])
    save(fig,'toric_long_run','중성원자 toric code 긴 실행에서의 Z 논리 오류율',
         '같은 Atom Computing 중성원자 장치에서 작은 코드 det 8은 데이터 16개와 보조 16개, 최대 90주기에서 Z 논리 오류율 주기당 0.63 플러스마이너스 0.03퍼센트를 보고했다. 큰 코드 det 16은 데이터 32개와 보조 32개, 최대 70주기에서 0.64 플러스마이너스 0.04퍼센트를 보고했다. 저장소 원자 재공급을 포함한 긴 실행 데이터의 모형 적합값이며 보고된 오차 범위가 겹친다. X 관측량이나 논리 게이트의 오류율은 아니다.',png=True)


def toric_mobile():
    """Compact 480 x 580 companion with exactly the desktop data and axis baseline."""
    fig,bg=canvas(480,580)
    text(bg,24,24,'긴 실행의 논리 오류',20,bold=True)
    text(bg,24,66,'같은 중성원자 장치 · Z 메모리',13,color=C['muted'])
    text(bg,24,111,'Z 논리 오류 / 주기 (%)',14,color=C['text'])
    ax=fig.add_axes([0.17,0.28,0.78,0.45],facecolor=C['bg'])
    vals=[0.63,0.64];errs=[0.03,0.04]
    for x,val,err,color in zip([0,1],vals,errs,[C['blue'],C['teal']]):
        ax.errorbar(x,val,yerr=err,fmt='o',markersize=8,capsize=7,
                    capthick=1.8,elinewidth=2,color=color,zorder=4)
        ax.text(x,val+err+0.038,f'{val:.2f} ± {err:.2f}%',ha='center',va='bottom',
                fontproperties=BOLD,fontsize=15,color=color)
    ax.set_xlim(-0.5,1.5);ax.set_ylim(0,0.86)
    ax.set_xticks([0,1])
    ax.set_xticklabels(['작은 코드','큰 코드'],fontproperties=BOLD,fontsize=15,color=C['navy'])
    ax.set_yticks([0,.2,.4,.6,.8])
    ax.set_yticklabels(['0.0','0.2','0.4','0.6','0.8'],fontproperties=REG,fontsize=13,color=C['muted'])
    ax.tick_params(axis='both',length=0,pad=9)
    ax.grid(axis='y',color=C['line'],lw=.8,zorder=0)
    for spine in ['top','right','left']:ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color(C['line'])
    for x,labels in zip([0,1],[['데이터 16 + 보조 16','최대 90주기'],['데이터 32 + 보조 32','최대 70주기']]):
        ax.text(x,-.18,labels[0],ha='center',va='top',transform=ax.get_xaxis_transform(),fontproperties=REG,fontsize=12,color=C['text'])
        ax.text(x,-.30,labels[1],ha='center',va='top',transform=ax.get_xaxis_transform(),fontproperties=REG,fontsize=13,color=C['muted'])
    text(bg,24,530,'원문 보고 불확도 · arXiv:2606.04079v1',11,color=C['muted'])
    save(fig,'toric_long_run_mobile','중성원자 toric code 긴 실행의 Z 논리 오류율: 모바일 도표',
         '동일 장치에서 데이터 16개와 보조 16개인 작은 코드는 최대 90주기, Z 논리 오류율 0.63 플러스마이너스 0.03퍼센트/주기다. 데이터 32개와 보조 32개인 큰 코드는 최대 70주기, 0.64 플러스마이너스 0.04퍼센트/주기다. 두 값은 재공급을 포함한 긴 실행의 모형 적합값이며 오차막대는 원문 보고 불확도다. 데스크톱 도표와 동일 자료를 모바일 화면에 맞춰 배치했다.')


def provenance():
    data={
        'as_of':'2026-10-19','created_by':'AI Tech Review',
        'method':'Original code-native diagrams and Matplotlib quantitative plot. No reproduced or traced publisher figures. SVG text outlined; accessible title and description embedded.',
        'script':'artifacts/build_scientific_figures.py',
        'style':{'background':C['bg'],'ink':C['navy'],'teal':C['teal'],'amber':C['amber'],'font':'Noto Sans KR Regular / Bold (outlined in SVG)'},
        'build':{'python':'3.12','matplotlib':matplotlib.__version__,'numpy':np.__version__,'command':'python artifacts/build_scientific_figures.py','deterministic_svg':'fixed svg.hashsalt; omitted Date metadata'},
        'figures':[
            {'file':'artifacts/qubit_mechanisms.svg',
             'caption_ko':'여섯 물리 플랫폼의 정보 저장과 연결 원리. 모든 도형은 편집부가 작성한 개념도이며, 실제 장치의 치수·배치·에너지 간격을 나타내지 않는다. 보소닉 부호화와 오류정정부호는 이 물리계 분류와 별도의 층이다.',
             'alt_ko':'이온의 공유 운동, 중성원자의 Rydberg 상호작용, 초전도 회로의 Josephson 접합, 스핀의 교환과 이동, 광자의 간섭과 측정, 결함 중심의 스핀–광자 링크를 비교한 여섯 개념도.',
             'sources':[
                 {'platform':'trapped ions','url':'https://doi.org/10.1038/s41586-026-10676-4','scope':'Article trapped-ion mechanism section and cited processor paper.'},
                 {'platform':'neutral atoms','url':'https://arxiv.org/html/2606.04079v1','scope':'§II, §III: nuclear-spin qubits, Rydberg gates, rearrangement, loss replenishment.'},
                 {'platform':'superconducting circuits','url':'https://doi.org/10.1103/PRXQuantum.6.010349','scope':'Article Josephson nonlinear circuit description; schematic shows generic simplified transmon circuit rather than fluxonium hardware.'},
                 {'platform':'semiconductor spins','url':'https://doi.org/10.1038/s41586-026-10766-3','scope':'Article exchange and shuttling description; alternatives rather than one particular device layout.'},
                 {'platform':'photons','url':'https://doi.org/10.1038/s41586-025-08820-7','scope':'Dual-rail and optical interference/measurement illustration, not a literal implementation photograph.'},
                 {'platform':'solid-state defects','url':'https://doi.org/10.1038/s41467-026-72818-6','scope':'Article local spin memory and heralded optical entanglement; link is not deterministic entanglement generation.'}],
             'caveats':['Ion circles are localized ions, not electronic orbits.','Neutral-atom curves depict trapping potentials, not orbiting electrons.','The photon card illustrates a dual-rail interferometer; it does not imply deterministic two-photon gates.','Hardware issues are qualitative questions, not maturity scores.']},
            {'file':'artifacts/evidence_requirements.svg',
             'caption_ko':'양자 하드웨어 결과를 읽을 때 필요한 네 종류의 검증. 규모, 반복 오류정정, 코드 확대, 논리 계산은 서로 다른 질문이다. 상자 배열은 플랫폼의 성숙도나 순위를 표현하지 않는다. 후선택 사용 시에는 채택률과 재시도 비용을 함께 확인한다.',
             'alt_ko':'규모와 자원, 반복 오류정정, 코드 확대의 효과, 논리 연산과 계산이라는 네 가지 증거와 모든 결과에 적용할 후선택 및 출판 상태 조건.',
             'sources':[
                 {'url':'https://arxiv.org/html/2606.04079v1','scope':'§I and §V distinguish finite-size suppression from asymptotic threshold and short circuits from long-run cycles.'},
                 {'url':'https://arxiv.org/abs/2602.22211','scope':'Encoded logical qubits and postselection require explicit interpretation; see reviewed manuscript in article.'},
                 {'url':'https://doi.org/10.1038/s41586-025-09848-5','scope':'Universal fault-tolerant ingredients, memory versus operations, readout and feed-forward conditions as discussed in article.'}],
             'caveats':['Editorial synthesis of criteria, not a data plot or a technology readiness ranking.']},
            {'file':'artifacts/toric_long_run.svg','raster':'artifacts/toric_long_run.png',
             'mobile':'artifacts/toric_long_run_mobile.svg','mobile_dimensions_px':[480,580],
             'mobile_note':'Compact layout of the identical two values, uncertainties, data/ancilla counts and maximum cycles; zero-baseline y axis retained. Detailed interpretation and source remain in the article caption.',
             'caption_ko':'같은 장치 안의 비교. Atom Computing의 중성원자 twisted toric code에서 저장소 재공급을 포함한 긴 실행의 Z 논리 오류율. 작은 코드(데이터 16+보조 16, 최대 90주기)는 0.63±0.03%/주기, 큰 코드(32+32, 최대 70주기)는 0.64±0.04%/주기다. 점은 상수 주기 오류 모형의 적합값, 막대는 원문이 보고한 ± 불확도다. 오차 범위가 겹치며, 이 긴 실행 지표에서 큰 코드의 추가 억제는 확인되지 않았다. X·Z 평균이나 논리 게이트 성능으로 일반화하지 않는다.',
             'alt_ko':'원자 32개와 64개의 두 코드에 대한 Z 논리 오류율 0.63±0.03% 및 0.64±0.04%를 같은 0–0.86% 세로축에서 비교한 오차막대 그림.',
             'source':{'title':'Quantum error correction with the toric code','authors':'Atom Computing and Collaborators','url':'https://arxiv.org/html/2606.04079v1','abstract_url':'https://arxiv.org/abs/2606.04079','version':'v1','posted':'2026-06-02','publication_status':'preprint','verified':'2026-10-19','locations':['§III code parameters','Fig. 3b caption','§V long-run reloading experiment']},
             'metric':'Z-type logical error per syndrome-extraction cycle, fit to long-run datasets with storage-zone reloads every tenth cycle; percent units.',
             'data':[{'code':'det 8','data_qubits':16,'ancilla_qubits':16,'total_array_qubits':32,'max_cycles':90,'z_error_per_cycle_percent':0.63,'reported_plusminus_percent':0.03},
                     {'code':'det 16','data_qubits':32,'ancilla_qubits':32,'total_array_qubits':64,'max_cycles':70,'z_error_per_cycle_percent':0.64,'reported_plusminus_percent':0.04}],
             'error_bar_definition':'Reproduces the ± fit-parameter uncertainties reported in Fig.3b and §V. Does not relabel them as a 95% CI or claim a separately verified confidence level.',
             'conditions':['Role swapping, mid-circuit measurement/reset, loss-aware decoding, and replacement of lost atoms are included.','Storage-zone refilling every 10 cycles is part of the plotted long-run fits.','Max cycles differ by code; this graphic does not assert matched circuit durations.','The resource count is data plus syndrome ancillas, not the entire device atom inventory.','No synthetic per-cycle trajectory, extrapolated raw observations, or cross-platform score is drawn.'],
             'interpretation_limits':['Overlap of reported intervals is a descriptive observation, not a formal equivalence or noninferiority test.','The plot does not summarize X-type logical error or a two-axis average.','No assertion about universal logical computation follows from these memory measurements.','Short-run code-size suppression uses different conditions and is intentionally not mixed into this chart.']}
        ]
    }
    NOTES.mkdir(exist_ok=True)
    (NOTES/'scientific_figure_notes.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    mechanisms();evidence();toric();toric_mobile();provenance()
    print('Built qubit_mechanisms.svg, evidence_requirements.svg, toric_long_run.svg/.png, toric_long_run_mobile.svg and scientific_figure_notes.json')
