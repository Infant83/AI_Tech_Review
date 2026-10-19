#!/usr/bin/env python3
"""Original physical-principle figures, with explicit models and basis conventions.

Requires numpy and matplotlib; imports the review's local drawing helpers.
SVG text is outlined. Previews are temporary. No experimental data are generated.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import numpy as np
from matplotlib import patches
from build_scientific_figures import canvas,text,box,line,arrow,dot,save as original_save,C,OUT,NOTES


def save(fig,stem,title,desc):
    original_save(fig,stem,title,desc)
    path=OUT/f'{stem}.svg'
    source=path.read_text()
    w,h=np.round(fig.get_size_inches()*fig.dpi).astype(int)
    source=re.sub(r'width="[^"]+" height="[^"]+"',f'width="{w}" height="{h}"',source,count=1)
    path.write_text(source)


def axes(ax,x,y,w,h,xlabel='',ylabel=''):
    arrow(ax,(x,y+h),(x+w+6,y+h),C['muted'],1.2)
    arrow(ax,(x,y+h),(x,y-5),C['muted'],1.2)
    if xlabel:text(ax,x+w+10,y+h,xlabel,12,va='center')
    if ylabel:text(ax,x-10,y-18,ylabel,12)


def level(ax,x,y,w,label,col=None):
    line(ax,[(x,y),(x+w,y)],col or C['teal'],2)
    text(ax,x+w+8,y,label,13,va='center')


def atomic_panel(ax,x,y,w,h,index,mobile):
    box(ax,x,y,w,h)
    p=24;fs=14 if mobile else 16
    text(ax,x+p,y+20,(['이온: 내부 상태와 공유 운동','중성원자와 Rydberg 결합'] if mobile else ['이온: 내부 상태와 공유 운동','중성원자: 저장 상태와 Rydberg 결합'])[index],17 if mobile else 20,bold=True)
    if index==0:
        text(ax,x+p,y+64,'포획은 질량중심 운동, 큐비트는 선택한 내부 상태',11.7 if mobile else 14,color=C['muted'])
        # Two distinct coordinates; no electron-orbit picture.
        px=x+42;py=y+125;pw=145 if mobile else 205;ph=115
        axes(ax,px,py,pw,ph,'x','U(x)')
        u=np.linspace(-1,1,100)
        line(ax,np.c_[px+pw*(u+1)/2,py+ph-16-85*u*u],C['blue'],2)
        dot(ax,px+pw/2,py+ph-25,7,C['white'],C['teal'])
        text(ax,px+pw/2,py+ph+26,'한 이온의 위치',12,ha='center',color=C['muted'])
        lx=x+w-160;ly=y+150
        level(ax,lx,ly,62,r'$|1\rangle$')
        level(ax,lx,ly+80,62,r'$|0\rangle$')
        arrow(ax,(lx+30,ly+72),(lx+30,ly+8),C['amber'],2,style='<->')
        text(ax,lx+33,ly+112,'내부 준위',12,ha='center',color=C['muted'])
        text(ax,x+p,y+325,'얽힘은 운동을 매개로 만든다',16,bold=True)
        # Collective ion displacements, then a closed trajectory of an oscillator.
        cy=y+391
        for k in range(3):
            xx=x+67+78*k
            dot(ax,xx,cy,10,C['white'],C['teal'])
            text(ax,xx,cy,'+',12,ha='center',va='center',color=C['teal'])
            arrow(ax,(xx-12,cy+30),(xx+12,cy+30),C['blue'],1.5)
        text(ax,x+p,cy+57,'Coulomb 결합 → 공유 운동',12.8,color=C['teal'])
        text(ax,x+p,cy+87,'화살표: 질량중심 모드의 예',10.5,color=C['muted'])
        ex=x+w-92;ey=cy
        ts=np.linspace(0,2*np.pi,200)
        line(ax,[(ex-46,ey),(ex+46,ey)],C['line'],1)
        line(ax,[(ex,ey-37),(ex,ey+37)],C['line'],1)
        text(ax,ex+48,ey,'q',9.5,va='center')
        text(ax,ex,ey-49,'p',9.5,ha='center')
        line(ax,np.c_[ex+36*np.cos(ts),ey+26*np.sin(ts)],C['amber'],2)
        dot(ax,ex+36,ey,3,C['amber'])
        arrow(ax,(ex+35,ey-5),(ex+33,ey+9),C['amber'],1.5)
        text(ax,ex,cy+57,'운동 위상공간',11,ha='center',color=C['amber'])
        text(ax,x+p,y+500,'스핀 의존 힘으로 운동 위상공간을 한 바퀴 돌린다.\n마지막에 운동을 분리하며 스핀 사이에 위상을 남긴다.',fs-1)
        text(ax,x+p,y+h-99,'MS 게이트의 예. 충분한 냉각·Lamb–Dicke 조건과\n최종 운동 분리가 필요하며, 항상 n = 0만 요구하지 않는다.',11.8 if mobile else 13,color=C['muted'])
    else:
        text(ax,x+p,y+64,'빛의 포획과 얽힘용 레이저는 역할이 다르다',11.8 if mobile else 14,color=C['muted'])
        # Internal levels and the doubly excited pair shift; B>0 example.
        lx=x+48;ly=y+147
        level(ax,lx,ly,65,r'$|r\rangle$',C['amber'])
        level(ax,lx,ly+97,65,r'$|1\rangle$')
        level(ax,lx,ly+145,65,r'$|0\rangle$')
        arrow(ax,(lx+30,ly+89),(lx+30,ly+8),C['amber'],2,style='<->')
        text(ax,lx+32,ly+47,r'$\Omega$',12,color=C['amber'])
        text(ax,lx+28,ly+180,'한 원자',12,ha='center',color=C['muted'])
        rx=x+w-170
        level(ax,rx,ly+150,69,r'$|11\rangle$')
        level(ax,rx,ly+77,69,'',C['line'])
        text(ax,rx+34,ly+93,r'$|r1\rangle,|1r\rangle$',11.8,ha='center')
        line(ax,[(rx,ly+3),(rx+69,ly+3)],C['line'],1.5,ls='--')
        text(ax,rx+34,ly+22,'Vrr = 0 기준',10.2,ha='center',color=C['muted'])
        level(ax,rx,ly-38,69,r'$|rr\rangle$',C['amber'])
        arrow(ax,(rx+22,ly-1),(rx+22,ly-34),C['amber'],1.8)
        text(ax,rx+32,ly-19,r'$V_{rr}$',12,va='center',color=C['amber'])
        text(ax,rx+34,ly+180,'두 원자',12,ha='center',color=C['muted'])
        text(ax,x+p,y+380,r'$|V_{rr}|/\hbar\ \gg\ \Omega$',23,color=C['navy'],bold=True)
        text(ax,x+p,y+438,'상호작용으로 두 번째 여기의 공명이 어긋난다.',fs-1)
        text(ax,x+p,y+490,'얽힘은 결맞는 펄스와 조건부 위상으로 구현한다.\nBlockade는 원자가 부딪히거나 겹친다는 뜻이 아니다.',fs-1)
        text(ax,x+p,y+h-99,'양의 에너지 이동 Vrr > 0의 예. 부호·세기는 상태·거리 의존.\n$|0\\rangle$, $|1\\rangle$은 저장 상태이고 $|r\\rangle$은 일시적 보조 상태다.',11.8 if mobile else 13,color=C['muted'])


def atomic(mobile=False):
    w,h=(480,1650) if mobile else (1320,1000)
    fig,ax=canvas(w,h)
    text(ax,24 if mobile else 40,25,'원자 큐비트의 포획과 얽힘' if mobile else '포획과 큐비트 상태와 얽힘을 구분한다',19 if mobile else 28,bold=True)
    text(ax,24 if mobile else 40,75,'대표 원리의 개념도 · 에너지와 길이는 축척이 아니다',11 if mobile else 15,color=C['muted'])
    if mobile:
        atomic_panel(ax,20,123,440,718,0,True)
        atomic_panel(ax,20,862,440,718,1,True)
    else:
        atomic_panel(ax,40,140,600,760,0,False)
        atomic_panel(ax,680,140,600,760,1,False)
    text(ax,24 if mobile else 40,h-34,'편집부 원본 도식 · 수식의 조건과 포획·구동·판독 방식은 본문 참조.',10.5,color=C['muted'])
    stem='atomic_physics'+('_mobile' if mobile else '')
    save(fig,stem,'원자계 큐비트의 포획, 내부 상태와 얽힘','이온의 포획 위치와 내부 상태를 분리한다. Coulomb 결합의 공유 운동에 스핀 의존 힘을 가해 최종 운동을 분리하면서 얽힘 위상을 만든다. 중성원자는 저장 상태에서 Rydberg 보조 상태를 일시적으로 구동하며 이중 여기의 상호작용 이동을 이용한다. 양의 에너지 이동의 예시이며 에너지 축척과 실제 장치 도면이 아니다.')


def model_energies():
    # Transmon: charge basis, ng=0, units EC. Fluxonium: finite difference in phi.
    n=np.arange(-35,36);EJ=50.
    ht=np.diag(4*n*n)+np.diag(np.full(len(n)-1,-EJ/2),1)+np.diag(np.full(len(n)-1,-EJ/2),-1)
    et=np.linalg.eigvalsh(ht)[:3]+EJ
    def flux(N):
        ph=np.linspace(-2*np.pi,4*np.pi,N);d=ph[1]-ph[0]
        pot=-4*np.cos(ph)+.5/2*(ph-np.pi)**2
        hf=np.diag(pot+8/d**2)+np.diag(np.full(N-1,-4/d**2),1)+np.diag(np.full(N-1,-4/d**2),-1)
        return ph,pot,np.linalg.eigvalsh(hf)[:3]
    pf,uf,ef=flux(601);_,_,echeck=flux(901)
    err=float(np.max(np.abs(ef-echeck)))
    if err>.005:raise ValueError(f'Fluxonium model grid difference exceeds tolerance: {err}')
    return et,pf,uf,ef,err


def circuit_panel(ax,x,y,w,h,index,data,mobile):
    et,pf,uf,ef,err=data
    box(ax,x,y,w,h)
    text(ax,x+24,y+20,['Transmon','Fluxonium'][index],21,bold=True)
    text(ax,x+24,y+65,['큰 EJ/EC로 전하 분산을 억제한다','큰 인덕턴스와 외부 자속이 퍼텐셜을 바꾼다'][index],12 if mobile else 15,color=C['muted'])
    # Plot in explicit EC units. These are model eigenvalues, not device data.
    gx=x+55;gy=y+140;gw=w-115;gh=260
    if index==0:
        ph=np.linspace(-np.pi,np.pi,400);pot=50*(1-np.cos(ph));en=et;vmin=0.;vmax=52.;xmin=-np.pi;xmax=np.pi
        lab=r'$E_J/E_C=50,\quad n_g=0$'
    else:
        ph=pf;vmin=float(uf.min());pot=uf-vmin;en=ef-vmin;vmax=8.;xmin=-2*np.pi;xmax=4*np.pi
        lab=r'$E_J/E_C=4,\quad E_L/E_C=0.5,\quad\varphi_{ext}=\pi$'
    xx=gx+(ph-xmin)/(xmax-xmin)*gw
    yy=gy+gh-pot/vmax*gh
    visible=(pot<=vmax)&(pot>=0)
    # Separate contiguous pieces to avoid drawing across omitted high-potential regions.
    inds=np.flatnonzero(visible);groups=np.split(inds,np.where(np.diff(inds)>1)[0]+1)
    for ids in groups:
        if len(ids)>1:line(ax,np.c_[xx[ids],yy[ids]],C['blue'],2)
    axes(ax,gx,gy,gw,gh,r'$\varphi$',r'$(E-U_{min})/E_C$')
    for i,ev in enumerate(en):
        good=np.where(pot<=ev)[0]
        a,b=(xx[good[0]],xx[good[-1]]) if len(good) else (gx, gx+gw)
        ey=gy+gh-float(ev)/vmax*gh
        line(ax,[(a,ey),(b,ey)],[C['teal'],C['teal'],C['amber']][i],1.8)
        if not(index==1 and i<2):text(ax,gx+gw+8,ey,str(i),12,va='center')
    if index==1:
        text(ax,gx+gw+8,gy+gh-float(np.mean(en[:2]))/vmax*gh,'0,1',12,va='center')
    text(ax,x+24,y+444,lab,11.3 if mobile else 16)
    gaps=np.diff(en)
    text(ax,x+24,y+493,f'본 모형의 간격: 01 = {gaps[0]:.2f} EC, 12 = {gaps[1]:.2f} EC',11.5 if mobile else 14,color=C['teal'])
    if index==0:
        body='조화진동자와 달리 인접 준위 간격이 다르다.\n$|0\\rangle$↔$|1\\rangle$을 골라 구동하되 $|2\\rangle$ 누설을 제어한다.'
        foot='Transmon의 계산 상태는 Cooper 쌍의 고전적\n이동 방향 두 가지가 아니라 회로의 양자 고유상태다.'
    else:
        body='자속에 따라 우물 구조와 전이 성질이 달라진다.\n반 자속 양자 근처의 퍼텐셜을 한 예로 그렸다.'
        foot='외부 자속이 정하는 위상은 본문에 정의했다.\n모든 fluxonium 소자가 이 비율을 쓰는 것은 아니다.'
    text(ax,x+24,y+546,body,12.5 if mobile else 15)
    text(ax,x+24,y+h-88,foot,11.5 if mobile else 13,color=C['muted'])


def circuits(data,mobile=False):
    w,h=(480,1750) if mobile else (1320,1080)
    fig,ax=canvas(w,h)
    text(ax,24 if mobile else 40,25,'회로의 비선형성과 준위' if mobile else '회로의 비선형성이 선택 가능한 준위를 만든다',18 if mobile else 28,bold=True)
    text(ax,24 if mobile else 40,75,'해밀토니안의 설명용 수치 모형 · 실제 장치의 측정 결과가 아니다',10.5 if mobile else 15,color=C['muted'])
    if mobile:
        circuit_panel(ax,20,123,440,775,0,data,True)
        circuit_panel(ax,20,921,440,775,1,data,True)
    else:
        circuit_panel(ax,40,140,600,835,0,data,False)
        circuit_panel(ax,680,140,600,835,1,data,False)
    text(ax,24 if mobile else 40,h-52 if mobile else h-34,'곡선은 퍼텐셜, 수평선은 낮은 세 고유에너지다.\n서로 다른 모형의 충실도 비교가 아니다.' if mobile else '곡선은 퍼텐셜, 수평선은 낮은 세 고유에너지다. 서로 다른 모형의 충실도 비교가 아니다.',10 if mobile else 13,color=C['muted'])
    stem='circuit_energy_models'+('_mobile' if mobile else '')
    save(fig,stem,'Transmon과 fluxonium의 퍼텐셜과 에너지 준위','각 해밀토니안의 설명용 고유에너지 계산이다. Transmon은 EJ/EC=50, ng=0의 전하 기저 대각화이며 fluxonium은 EJ/EC=4, EL/EC=0.5, 외부 위상 π의 유한차분 모형이다. 곡선은 퍼텐셜, 수평선은 낮은 세 고유에너지이며 모든 세로축은 각 퍼텐셜 최솟값을 뺀 EC 단위이다. 실제 장치의 측정, 준위 간격 또는 성능 비교가 아니다.')


def encoding_panel(ax,x,y,w,h,index,mobile):
    box(ax,x,y,w,h)
    titles=['두 모드에 한 여기: dual-rail','한 모드의 결맞음 상태: cat','한 모드의 격자 부호화: GKP','네 Majorana 모드: tetron']
    text(ax,x+24,y+20,titles[index],16.5 if mobile else 20,bold=True)
    if index==0:
        text(ax,x+24,y+72,r'$|0_L\rangle=|1,0\rangle,\quad |1_L\rangle=|0,1\rangle$',18 if mobile else 22)
        for bit in range(2):
            left=x+44+bit*(w-60)/2
            railw=(w-110)/2
            for mode in range(2):
                yy=y+163+66*mode
                line(ax,[(left,yy),(left+railw,yy)],C['blue'],2)
                if mode==bit:dot(ax,left+railw/2,yy,12,C['teallight'],C['teal'])
            text(ax,left+railw/2,y+264,rf'$|{1-bit},{bit}\rangle$',16,ha='center')
        text(ax,x+24,y+308,'각 기저 그림의 두 선은 두 모드, 점은 한 여기다.',11.4 if mobile else 14)
        text(ax,x+24,y+350,r'$|1,0\rangle,|0,1\rangle\ \longrightarrow\ |0,0\rangle$',17 if mobile else 21,color=C['amber'])
        text(ax,x+24,y+405,'손실을 검출하면 소거로 다룰 수 있다.\n검출 누락·잘못된 경보·위상 오류는 별도 문제다.',12 if mobile else 14,color=C['muted'])
    elif index==1:
        text(ax,x+24,y+72,r'$|C_{\pm}\rangle\propto|\alpha\rangle\pm|-\alpha\rangle$',21 if mobile else 25)
        cx=x+w/2;cy=y+198
        line(ax,[(cx-140,cy),(cx+140,cy)],C['line'],1.3)
        line(ax,[(cx,cy-65),(cx,cy+65)],C['line'],1.3)
        for sign in [-1,1]:
            ax.add_patch(patches.Ellipse((cx+sign*82,cy),49,62,facecolor=C['teallight'],edgecolor=C['teal'],lw=2))
            text(ax,cx+sign*82,cy+49,r'$|\alpha\rangle$' if sign>0 else r'$|-\alpha\rangle$',15,ha='center')
        text(ax,x+24,y+295,'±alpha는 위상공간의 두 성분을 가리킨다.\nC+와 C-는 각각 짝수·홀수 광자수 중첩이다.',12.4 if mobile else 15)
        text(ax,x+24,y+383,'±alpha와 홀짝 cat은 같은 기저가 아니다.\n어떤 오류를 X·Z로 부를지는 선택한 기저에 달린다.',12 if mobile else 14,color=C['muted'])
    elif index==2:
        text(ax,x+24,y+72,r'$[q,p]=i,\quad q_0=2k\sqrt{\pi},\quad q_1=(2k+1)\sqrt{\pi}$',13 if mobile else 19)
        gx=x+50;gw=w-100;gy=y+247
        line(ax,[(gx,gy),(gx+gw,gy)],C['line'],1)
        qs=np.linspace(-5,5,1000)
        for bit,col,off in [(0,C['teal'],0),(1,C['amber'],38)]:
            amp=np.zeros_like(qs)
            for k in range(-4,5):
                center=(2*k+bit)*np.sqrt(np.pi)
                amp+=np.exp(-center**2/18)*np.exp(-(qs-center)**2/.06)
            line(ax,np.c_[gx+(qs+5)/10*gw,gy-90*amp+off],col,2)
        text(ax,x+24,y+308,'q 표현의 유한 폭 피크와 유한 포락선',12.5 if mobile else 15)
        text(ax,x+24,y+350,'청록: 0L · 황색: 1L (곡선은 구별을 위해 세로 이동)',10.5 if mobile else 12.7,color=C['muted'])
        text(ax,x+24,y+389,'설명용 파형이며 Wigner 함수·실험 데이터가 아니다.\n이상적 델타 격자는 무한 에너지여서 그대로 만들 수 없다.',11.7 if mobile else 14,color=C['muted'])
    else:
        text(ax,x+24,y+72,r'$f_1=(\gamma_1+i\gamma_2)/2,\quad f_2=(\gamma_3+i\gamma_4)/2$',13.5 if mobile else 19)
        yy=y+169
        xx=np.linspace(x+70,x+w-70,4)
        for j,xc in enumerate(xx):
            dot(ax,xc,yy,13,C['white'],C['teal'])
            text(ax,xc,yy-37,rf'$\gamma_{j+1}$',16,ha='center')
        line(ax,[(xx[0],yy+30),(xx[1],yy+30)],C['blue'],2)
        line(ax,[(xx[2],yy+30),(xx[3],yy+30)],C['blue'],2)
        text(ax,x+24,y+240,'총 짝수 패리티를 고정한 예',14,color=C['teal'])
        text(ax,x+24,y+282,r'$|0_L\rangle=|0,0\rangle,\quad |1_L\rangle=|1,1\rangle$',19 if mobile else 23)
        text(ax,x+24,y+354,'고정 패리티에서 두 상태의 중첩을 쓴다.\n한 쌍만 있고 그 패리티도 고정하면 한 상태만 남는다.',12 if mobile else 14.5)
        text(ax,x+24,y+420,'Majorana 기호는 준입자 연산자다.\n전자를 네 조각으로 자른 그림이 아니다.' if mobile else 'Majorana 기호는 준입자 연산자다. 전자를 네 조각으로 자른 그림이 아니다.',10.7 if mobile else 12.5,color=C['muted'])


def encodings(mobile=False):
    w,h=(480,2290) if mobile else (1320,1280)
    fig,ax=canvas(w,h)
    text(ax,24 if mobile else 40,25,'모드·입자·큐비트 수의 구분' if mobile else '모드 수와 입자 수와 큐비트 수는 다르다',19 if mobile else 28,bold=True)
    text(ax,24 if mobile else 40,76,'서로 다른 부호화 공간 · 파형과 모드 그림은 원리 설명용이다',11 if mobile else 15,color=C['muted'])
    if mobile:
        for i in range(4):encoding_panel(ax,20,125+531*i,440,510,i,True)
    else:
        for i in range(4):encoding_panel(ax,40+640*(i%2),140+525*(i//2),600,500,i,False)
    text(ax,24 if mobile else 40,h-52 if mobile else h-34,'각 기저와 잡음의 관계는 본문 참조. 모드·여기·소자 수를\n논리 큐비트 수로 바로 환산하지 않는다.' if mobile else '각 기저와 잡음의 관계는 본문 참조. 모드·여기·소자 수를 논리 큐비트 수로 바로 환산하지 않는다.',10 if mobile else 13,color=C['muted'])
    stem='qubit_encoding_spaces'+('_mobile' if mobile else '')
    save(fig,stem,'Dual-rail, cat, GKP와 tetron의 서로 다른 부호화 공간','Dual-rail은 두 모드의 한 여기, cat은 결맞음 상태의 중첩, GKP는 한 모드의 격자 부호화다. GKP 곡선은 q표현의 유한 폭 봉우리와 포락선을 그린 설명용 진폭 모양이며 Wigner 함수나 실험 자료가 아니다. Tetron은 네 Majorana 모드로 두 복소 페르미온 모드를 만들고 고정 총 패리티에서 두 차원 부호 공간을 쓴다. 모드 수, 여기 수와 계산 큐비트 수를 구별한다.')


def main():
    OUT.mkdir(exist_ok=True);NOTES.mkdir(exist_ok=True)
    data=model_energies()
    for mobile in [False,True]:atomic(mobile);circuits(data,mobile);encodings(mobile)
    notes={'as_of':'2026-10-19','creator':'AI Tech Review; original deterministic scientific schematics','generator':'artifacts/build_physics_figures.py','figure_type':'Conceptual diagrams and explicit toy-model energy calculations; no reported experimental observations redrawn.',
      'files':{'atomic_physics':{'desktop':[1320,1000],'mobile':[480,1650]},'circuit_energy_models':{'desktop':[1320,1080],'mobile':[480,1750]},'qubit_encoding_spaces':{'desktop':[1320,1280],'mobile':[480,2290]}},
      'model':{'transmon':{'EJ_over_EC':50,'ng':0,'charge_basis_n':[-35,35],'energies_minus_potential_min_in_EC':data[0].tolist()},'fluxonium':{'EJ_over_EC':4,'EL_over_EC':0.5,'external_phase':'pi','phase_domain':['-2pi','4pi'],'grid_points':601,'boundary':'finite-difference Dirichlet; extended phase domain','energy_check_901_grid_max_difference_EC':data[4],'energies_minus_potential_min_in_EC':(data[3]-data[2].min()).tolist()}},
      'limits':['Atomic energy and position motifs are schematic and have no common scale.','The Rydberg ladder illustrates a positive pair energy shift; blockade relies on the magnitude and coherent pulse protocol, not collision.','Circuit spectra are parameter-specific model calculations and do not rank platforms or imply device fidelity.','Cat phase-space ellipses mark coherent-state components, not a positive probability substitute for the full cat Wigner function.','GKP waveforms are schematic finite-width approximate q-space amplitudes, vertically offset for clarity; not a Wigner plot, measured distribution or a specified experimentally prepared state.','Tetron basis uses even total parity as a convention and does not claim protected experimental operations.'],
      'sources':[
      {'figure':'atomic_physics','urls':['https://doi.org/10.1103/PhysRevA.62.022311','https://doi.org/10.1103/PhysRevLett.85.2208','https://doi.org/10.1103/PhysRevLett.57.314']},
      {'figure':'circuit_energy_models','urls':['https://doi.org/10.1103/PhysRevA.76.042319','https://arxiv.org/abs/0906.0831']},
      {'figure':'qubit_encoding_spaces','urls':['https://doi.org/10.1073/pnas.2221736120','https://arxiv.org/abs/1312.2017','https://arxiv.org/abs/quant-ph/0008040','https://arxiv.org/abs/1609.01697']}],
      'independent_model_audit':{'fluxonium_expanded_domain_energy_change_EC':4.18e-7,'review':'Second-agent finite-difference boundary check; Hamiltonian coefficients, charge conventions and low-energy gaps checked.'},
      'visual_qa':'Desktop and mobile previews inspected; state labels, phase-space axes and parity conventions audited. Mobile tetron and footer wrapping corrected before final render.'}
    (NOTES/'physics_figure_notes.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'flux_grid_max_difference_EC':data[4],'files_built':6}))

if __name__=='__main__':main()
