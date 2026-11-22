#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministic editorial figures; source values are stated in each SVG.

Run from any directory. This script writes only its ten sibling figure SVGs.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parent / 'figures'
BG = '#f7f4eb'
INK = '#293d42'
TEAL = '#316a67'
CLAY = '#b66c54'
OLIVE = '#76865a'
SAND = '#ddbb7b'
PALE = '#e3e7df'
MUTED = '#657471'
RULE = '#cdd2c7'


class SVG:
    def __init__(self, width, height, title, desc):
        self.w, self.h = width, height
        self.s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
                  f'<title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',
                  f'<defs><marker id="info" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M1 1 L8 4.5 L1 8" fill="none" stroke="{TEAL}" stroke-width="1.5"/></marker><marker id="power" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 1 L8 4.5 L0 8 Z" fill="{CLAY}"/></marker><marker id="muted" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M1 1 L8 4.5 L1 8" fill="none" stroke="{MUTED}" stroke-width="1.5"/></marker></defs>',
                  f'<style>text{{font-family:"Apple SD Gothic Neo","Noto Sans KR",Arial,sans-serif;fill:{INK}}}.serif{{font-family:Georgia,"Times New Roman",serif}}.muted{{fill:{MUTED}}}.teal{{fill:{TEAL}}}.clay{{fill:{CLAY}}}</style>']
        self.rect(0, 0, width, height, BG)

    def rect(self, x, y, w, h, fill='none', stroke=None, sw=1.5, rx=0, dash=None):
        self.s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"' + (f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '') + (f' stroke-dasharray="{dash}"' if dash else '') + '/>')

    def line(self, x1, y1, x2, y2, color=RULE, sw=1.5, dash=None, marker=None):
        self.s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"' + (f' stroke-dasharray="{dash}"' if dash else '') + (f' marker-end="url(#{marker})"' if marker else '') + '/>')

    def path(self, d, color=INK, sw=2, fill='none', dash=None, marker=None):
        self.s.append(f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' + (f' stroke-dasharray="{dash}"' if dash else '') + (f' marker-end="url(#{marker})"' if marker else '') + '/>')

    def circle(self, x, y, r, fill=TEAL, stroke=None, sw=1.5):
        self.s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"' + (f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '') + '/>')

    def text(self, x, y, value, size=26, weight=400, color=INK, anchor='start', cls=''):
        self.s.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" class="{cls}" style="fill:{color}">{escape(str(value))}</text>')

    def lines(self, x, y, values, size=26, lead=36, weight=400, color=INK, anchor='start'):
        for i, value in enumerate(values): self.text(x, y+i*lead, value, size, weight, color, anchor)

    def title(self, n, title, sub, mobile=False):
        x = 40 if mobile else 58
        self.text(x, 52 if mobile else 57, f'{n:02}', 24 if mobile else 21, 700, TEAL)
        self.text(x+50, 53 if mobile else 59, title, 30 if mobile else 34, 700)
        self.text(x, 97 if mobile else 106, sub, 24 if mobile else 25, 400, MUTED)
        self.line(x, 121 if mobile else 132, self.w-x, 121 if mobile else 132)

    def footer(self, text, mobile=False):
        self.text(40 if mobile else 58, self.h-29, text, 24 if mobile else 21, 400, MUTED)

    def document(self, x, y, w=90, h=118, color=TEAL):
        self.path(f'M{x} {y} H{x+w-20} L{x+w} {y+20} V{y+h} H{x} Z M{x+w-20} {y} V{y+20} H{x+w}', color, 2)
        for yy, ww in [(40,w-25),(56,w-30),(72,w-39)]:
            if yy < h-10 and ww > 13: self.line(x+13,y+yy,x+ww,y+yy,color,2)

    def chip(self, x, y, w=100, h=92, color=TEAL):
        self.rect(x,y,w,h,'none',color,2)
        self.rect(x+14,y+14,w-28,h-28,'none',color,1.2)
        for k in range(5):
            xx=x+14+k*(w-28)/4
            self.line(xx,y-9,xx,y,color,2);self.line(xx,y+h,xx,y+h+9,color,2)
            yy=y+14+k*(h-28)/4
            self.line(x-9,yy,x,yy,color,2);self.line(x+w,yy,x+w+9,yy,color,2)

    def save(self, filename):
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT/filename).write_text('\n'.join(self.s)+ '\n</svg>\n', encoding='utf-8')


def fig1(m):
    s = SVG(700 if m else 1400, 1330 if m else 900, '정보 처리와 에너지 전달의 두 흐름', '위쪽은 프롬프트·학습된 모델·검색 증거가 도구와 기억 및 검증을 거쳐 출력에 연결되는 개념도다. 아래쪽은 계산과 냉각에 전력이 들어가고 열이 환경으로 전달되는 별도의 물리 흐름이다.')
    s.title(1,'정보와 에너지를 함께 따라가기','서로 다른 화살표로 읽는 하나의 에이전트 실행',m)
    if m:
        s.text(40,166,'정보 흐름',25,700,TEAL)
        for i,(a,b) in enumerate([('프롬프트','작업의 목적과 입력'),('학습된 모델','매개변수에 담긴 관계'),('검색한 증거','문헌·도구의 새 관찰')]):
            y=213+i*62;s.text(40,y,a,25,700);s.text(254,y,b,24,color=MUTED)
        s.line(345,354,345,395,TEAL,2,marker='info')
        s.rect(40,406,620,242,'none',TEAL,2)
        s.text(66,446,'추론과 행동을 이어 주는 하네스',27,700)
        for x,a,b in [(76,'추론','다음 행동'),(270,'도구','검색·계산'),(470,'기억','관찰 보존')]:
            s.text(x,500,a,28,700);s.text(x,538,b,24,color=MUTED)
        s.path('M106 570 H590 V613 H103',TEAL,2,dash='7 6',marker='info')
        s.text(344,603,'검증 결과에 따라 다시 계획',24,color=TEAL,anchor='middle')
        s.line(345,650,345,700,TEAL,2,marker='info')
        s.document(102,706,64,86);s.text(204,747,'검증한 출력과 보존할 기록',28,700)
        s.text(204,783,'정확성·유용성은 과제 기준으로 평가',24,color=MUTED)
        s.line(40,822,660,822)
        s.text(40,864,'물리적 에너지 흐름',25,700,CLAY)
        s.text(40,910,'전력',28,700,CLAY)
        s.line(113,900,272,900,CLAY,4,marker='power')
        s.chip(290,871,99,80,CLAY)
        s.text(339,992,'계산·메모리·호스트',25,anchor='middle')
        s.path('M410 908 H570 V1047',CLAY,4,marker='power')
        s.text(518,949,'열',26,700,CLAY)
        s.rect(410,1070,238,80,'none',CLAY,2)
        s.text(529,1120,'냉각과 열 전달',26,700,anchor='middle')
        s.path('M80 922 V1108 H388',CLAY,3,marker='power')
        s.lines(91,1046,['냉각에도','전력 투입'],24,34,color=CLAY)
        s.line(529,1150,529,1205,CLAY,4,marker='power')
        s.text(438,1241,'주변 환경',28,700,CLAY)
        s.footer('개념도 · 정보의 가치와 물리 에너지는 별도량',m)
    else:
        s.text(58,180,'정보 흐름',25,700,TEAL)
        for i,(a,b) in enumerate([('프롬프트','작업의 목적과 입력'),('학습된 모델','매개변수에 담긴 관계'),('검색한 증거','문헌·도구의 새 관찰')]):
            y=233+i*70;s.text(58,y,a,28,700);s.text(58,y+31,b,23,color=MUTED);s.line(285,y-9,408,290,TEAL,1.7,marker='info')
        s.rect(435,201,570,225,'none',TEAL,2)
        s.text(463,244,'추론과 행동을 이어 주는 하네스',29,700)
        for x,a,b in [(470,'추론','다음 행동'),(650,'도구','검색·계산'),(830,'기억','관찰 보존')]:
            s.text(x,305,a,29,700);s.text(x,339,b,24,color=MUTED)
        s.path('M482 365 H959 V405 H480',TEAL,2,dash='7 6',marker='info')
        s.text(720,395,'검증 결과에 따라 다시 계획',24,color=TEAL,anchor='middle')
        s.line(1005,294,1092,294,TEAL,2,marker='info')
        s.document(1140,209,92,124)
        s.text(1187,371,'검증한 출력',29,700,anchor='middle')
        s.text(1187,406,'보존할 기록',24,color=MUTED,anchor='middle')
        s.line(58,475,1342,475)
        s.text(58,521,'물리적 에너지 흐름',25,700,CLAY)
        s.text(62,620,'전력',32,700,CLAY)
        s.line(144,610,356,610,CLAY,4,marker='power')
        s.chip(392,564,120,96,CLAY)
        s.text(455,711,'계산·메모리·호스트',27,anchor='middle')
        s.line(535,610,759,610,CLAY,4,marker='power');s.text(646,585,'열',27,700,CLAY,anchor='middle')
        for x in range(782,883,20):s.line(x,563,x,659,CLAY,2)
        s.text(831,711,'냉각과 열 전달',27,anchor='middle')
        s.line(901,610,1183,610,CLAY,4,marker='power');s.text(1092,584,'방출 열',26,color=CLAY,anchor='middle')
        s.text(1235,620,'환경',31,700,CLAY,anchor='middle')
        s.path('M198 610 V774 H730 V635 H759',CLAY,3,marker='power')
        s.rect(365,753,354,42,BG)
        s.text(542,782,'냉각에도 추가 전력이 든다',25,color=CLAY,anchor='middle')
        s.footer('개념도 · 출력의 의미와 품질은 과제 기준으로, 에너지는 물리적 경계 안에서 평가한다',m)
    s.save(f'fig1_{"mobile" if m else "desktop"}.svg')


def well(s,x,y,scale=1):
    s.path(f'M{x} {y} C{x+28*scale} {y+86*scale} {x+70*scale} {y+86*scale} {x+100*scale} {y} C{x+128*scale} {y-74*scale} {x+157*scale} {y-74*scale} {x+185*scale} {y} C{x+214*scale} {y+86*scale} {x+257*scale} {y+86*scale} {x+285*scale} {y}',TEAL,2.5)


def fig2(m):
    s=SVG(700 if m else 1400,1190 if m else 820,'한 비트 초기화의 엔트로피 장부','등확률 두 논리 상태를 한 상태로 초기화하는 표준 등온 모형. 메모리 엔트로피 감소는 환경의 엔트로피 증가와 함께 읽는다. 준정적 이상 한계에서 전체 엔트로피 생성은 영에 접근할 수 있다.')
    s.title(2,'한 비트를 비우는 물리적 과정','대칭인 두 논리 상태 · 단일 온도 T의 환경',m)
    if m:
        s.text(40,169,'초기 분포',27,700);s.text(660,169,'H = 1 bit',27,anchor='end')
        well(s,135,252,1.5);s.circle(210,320,15);s.circle(485,320,15)
        s.text(210,381,'0 · 50%',26,anchor='middle');s.text(485,381,'1 · 50%',26,anchor='middle')
        s.line(345,416,345,469,TEAL,2,marker='info');s.text(379,454,'초기화',25,color=TEAL)
        s.text(40,515,'최종 분포',27,700);s.text(660,515,'H = 0 bit',27,anchor='end')
        well(s,135,590,1.5);s.circle(210,658,21)
        s.text(210,719,'0 · 100%',26,anchor='middle');s.text(485,719,'1 · 0%',26,anchor='middle')
        s.line(40,763,660,763)
        s.text(40,810,'메모리',26,700,TEAL);s.text(660,810,'ΔS = −kB ln 2',31,anchor='end')
        s.text(40,871,'환경',26,700,CLAY);s.text(660,871,'Q환경 ≥ kBT ln 2',30,anchor='end')
        s.text(660,920,'ΔS환경 ≥ kB ln 2',28,color=CLAY,anchor='end')
        s.line(40,949,660,949)
        s.text(40,997,'전체 엔트로피 생성',26,700);s.text(660,997,'Σ ≥ 0',34,anchor='end')
        s.lines(40,1055,['이상적인 준정적 한계: Σ → 0','T는 절대온도, kB는 Boltzmann 상수'],25,39,color=MUTED)
        s.footer('교육 모형 · 대칭 메모리의 등온 초기화',m)
    else:
        s.text(247,190,'초기 분포',29,700,anchor='middle');s.text(1040,190,'최종 분포',29,700,anchor='middle')
        well(s,73,292,1.2);well(s,864,292,1.2)
        for x in [133,356]:s.circle(x,346,15)
        s.circle(924,346,21)
        for x,a in [(133,'0 · 50%'),(356,'1 · 50%'),(924,'0 · 100%'),(1147,'1 · 0%')]:s.text(x,404,a,26,anchor='middle')
        s.text(247,453,'H = 1 bit',29,anchor='middle');s.text(1040,453,'H = 0 bit',29,anchor='middle')
        s.line(492,302,749,302,TEAL,2,marker='info');s.text(620,275,'초기화',27,color=TEAL,anchor='middle')
        s.line(58,500,1342,500)
        for x,a,b,c,col in [(58,'메모리','ΔS = −kB ln 2','논리 상태의 불확실성 감소',TEAL),(530,'환경','Q환경 ≥ kBT ln 2','ΔS환경 ≥ kB ln 2',CLAY),(1044,'전체','Σ ≥ 0','엔트로피 생성',INK)]:
            s.text(x,548,a,26,700,col);s.text(x,604,b,32,500,col);s.text(x,649,c,24,color=MUTED)
        s.line(58,691,1342,691)
        s.text(58,735,'이상적인 준정적 한계에서는 환경의 증가가 메모리의 감소를 상쇄해 Σ → 0',25,color=MUTED)
        s.footer('교육 모형 · T는 절대온도, kB는 Boltzmann 상수 · 대칭 메모리의 등온 초기화',m)
    s.save(f'fig2_{"mobile" if m else "desktop"}.svg')


def bar(s,x,y,w,h,vals,colors):
    pos=x
    for v,col in zip(vals,colors):
        s.rect(pos,y,w*v,h,col);pos+=w*v


def fig3(m):
    s=SVG(700 if m else 1400,1210 if m else 910,'실행 수와 토큰 사용의 다른 분포','저자 보고값을 재도표했다. 1200회 중 78회가 300턴에서 중단되었으며 전체 출력 토큰의 65.6퍼센트를 사용했다. 별도로 성공 실행 출력 토큰의 약80퍼센트는 목표 진행 비율을 바꾸지 않는 호출에서 생성되었다.')
    s.title(3,'성공 뒤에 가려진 토큰의 비용','실행 수와 토큰 수는 서로 다른 분모다',m)
    x=40 if m else 58;w=620 if m else 1284
    if m:
        s.text(x,173,'A  전체 실행 1,200회',28,700)
        bar(s,x,203,w,60,[1110/1200,11/1200,78/1200,1/1200],[TEAL,SAND,CLAY,INK])
        s.text(x,313,'1,110',52,700,TEAL);s.text(226,312,'성공',26,700,TEAL)
        s.text(x,356,'78회 제한 중단  ·  전체 실행의 6.5%',27,700,CLAY)
        s.text(x,399,'11회 목표 미달 종료  ·  1회 판정 불가',24,color=MUTED)
        s.line(x,441,660,441)
        s.text(x,493,'B  전체 출력 토큰의 사용처',28,700)
        bar(s,x,530,w,72,[.656,.344],[CLAY,PALE])
        s.text(x+20,578,'65.6%',33,700,BG);s.text(660-20,578,'34.4%',28,700,INK,'end')
        s.lines(x,654,['78회의 제한 중단 실행이','전체 출력 토큰의 약 3분의 2 사용'],27,39,weight=700,color=CLAY)
        s.text(x,750,'나머지 1,122회의 실행',25,color=MUTED)
        s.line(x,791,660,791)
        s.text(x,842,'C  성공 실행의 출력 토큰 분류',28,700)
        bar(s,x,879,w,72,[.8,.2],[SAND,TEAL])
        s.text(x+20,927,'약 80%',32,700,INK);s.text(660-14,926,'약 20%',25,700,BG,'end')
        s.lines(x,1004,['목표 진행 q가 그대로인 호출: heat','읽기·검색·테스트 등을 포함'],26,38)
        s.lines(x,1104,['q가 변한 호출: work','분류 단위는 호출이며 비용은 출력 토큰'],25,38,color=MUTED)
        s.footer('저자 보고값 재도표 · arXiv:2611.23375v1',m)
    else:
        s.text(x,188,'A  전체 실행 1,200회',28,700)
        bar(s,x,221,w,59,[1110/1200,11/1200,78/1200,1/1200],[TEAL,SAND,CLAY,INK])
        s.text(x,328,'1,110회 성공',30,700,TEAL)
        s.text(527,328,'78회 제한 중단 · 6.5%',30,700,CLAY)
        s.text(x,371,'11회 목표 미달 종료 · 1회 판정 불가',25,color=MUTED)
        s.line(x,406,1342,406)
        s.text(x,453,'B  전체 출력 토큰',28,700)
        bar(s,x,484,w,69,[.656,.344],[CLAY,PALE])
        s.text(x+22,532,'65.6% — 78회의 제한 중단 실행',31,700,BG)
        s.text(1320,532,'34.4% — 나머지 실행',27,700,INK,'end')
        s.text(x,596,'적은 수의 중단 실행이 전체 출력 토큰의 약 3분의 2를 사용했다.',26,color=MUTED)
        s.line(x,630,1342,630)
        s.text(x,678,'C  성공 실행의 출력 토큰',28,700)
        bar(s,x,710,w,62,[.8,.2],[SAND,TEAL])
        s.text(x+22,751,'약 80%  heat — 목표 진행 q가 그대로인 호출',28,700)
        s.text(1320,751,'약 20%  work',26,700,BG,'end')
        s.text(x,819,'heat에는 읽기·검색·테스트가 포함된다. 분류 단위는 호출이며 비용은 출력 토큰이다.',25,color=MUTED)
        s.footer('저자 보고값 재도표 · arXiv:2611.23375v1 · 입력 토큰은 비용 분모에서 제외',m)
    s.save(f'fig3_{"mobile" if m else "desktop"}.svg')


def fig4(m):
    s=SVG(700 if m else 1400,1170 if m else 850,'운영 에너지의 측정 경계','Google이 2025년5월 Gemini Apps 중앙값 텍스트 프롬프트에 대해 보고한 운영 에너지를 재도표했다. 활성 가속기0.14, CPU와DRAM0.06, 대기 용량0.02, 데이터센터 부대설비0.02 Wh를 합해0.24 Wh이다.')
    s.title(4,'전력계의 경계를 넓혀 보기','Gemini Apps · 2025년 5월 중앙값 텍스트 프롬프트',m)
    x=40 if m else 58
    if m:
        s.text(x,211,'0.24',64,700);s.text(223,211,'Wh / prompt',28,color=MUTED)
        s.text(x,257,'서비스를 제공하는 운영 에너지',26,color=MUTED)
        s.rect(x,302,620,317,'none',CLAY,1.8)
        s.text(x+21,343,'데이터센터',25,700,CLAY)
        s.rect(x+21,370,414,218,'none',TEAL,1.6)
        s.text(x+41,409,'가속기와 호스트',25,700,TEAL)
        s.chip(x+46,448,87,84)
        for yy in [450,477,504]:s.rect(x+178,yy,126,16,'none',TEAL,1.8)
        for yy in [418,451,484,517]:s.line(x+474,yy,x+568,yy,CLAY,2)
        s.text(x+520,563,'냉각',25,anchor='middle',color=CLAY)
        s.text(x+520,596,'등',24,anchor='middle',color=CLAY)
        s.text(x,669,'운영 에너지의 구성',27,700)
        bar(s,x,701,620,69,[.14/.24,.06/.24,.02/.24,.02/.24],[TEAL,OLIVE,SAND,CLAY])
        for i,(a,b,c) in enumerate([('활성 가속기','0.14 Wh',TEAL),('CPU · DRAM','0.06 Wh',OLIVE),('대기 용량','0.02 Wh',SAND),('데이터센터 부대설비','0.02 Wh',CLAY)]):
            yy=824+i*57;s.rect(x,yy-20,14,23,c);s.text(x+30,yy,a,25);s.text(660,yy,b,27,700,anchor='end')
        s.lines(x,1068,['이 에너지 값의 범위 밖: 학습·칩 제조','사용자 기기·외부 네트워크'],24,34,color=MUTED)
        s.footer('저자 보고값 재도표 · arXiv:2508.15734v1, Table 1',m)
    else:
        s.text(x,230,'0.24',70,700);s.text(255,229,'Wh / prompt',30,color=MUTED)
        s.lines(x,278,['서비스를 제공하는','운영 에너지'],27,38,color=MUTED)
        s.rect(470,176,870,280,'none',CLAY,1.8)
        s.text(491,217,'데이터센터',26,700,CLAY)
        s.rect(492,243,572,185,'none',TEAL,1.8)
        s.text(516,280,'가속기와 호스트',25,700,TEAL)
        s.chip(525,307,90,83)
        for yy in [309,337,365]:s.rect(675,yy,155,18,'none',TEAL,1.7)
        s.rect(891,307,130,83,'none',OLIVE,1.6,dash='6 5');s.text(956,356,'대기',26,anchor='middle',color=OLIVE)
        for xx in range(1110,1295,25):s.line(xx,256,xx,360,CLAY,2)
        s.text(1201,400,'냉각 등 부대설비',24,color=CLAY,anchor='middle')
        s.text(x,513,'운영 에너지의 구성',28,700)
        bar(s,x,546,1284,70,[.14/.24,.06/.24,.02/.24,.02/.24],[TEAL,OLIVE,SAND,CLAY])
        for xx,a,b,c in [(58,'활성 가속기','0.14 Wh',TEAL),(470,'CPU · DRAM','0.06 Wh',OLIVE),(820,'대기 용량','0.02 Wh',SAND),(1070,'부대설비','0.02 Wh',CLAY)]:
            s.rect(xx,651,13,24,c);s.text(xx+28,675,a,26);s.text(xx+28,716,b,30,700)
        s.text(x,779,'이 에너지 값의 범위 밖: 학습·칩 제조·사용자 기기·외부 네트워크',25,color=MUTED)
        s.footer('저자 보고값 재도표 · arXiv:2508.15734v1, Table 1 · 전체 제공 인프라를 포함한 측정',m)
    s.save(f'fig4_{"mobile" if m else "desktop"}.svg')


def fig5(m):
    s=SVG(700 if m else 1400,1600 if m else 1040,'자원 조건을 실행에 연결하는 거버넌스 제안','근거를 검증하는 리뷰 작성 사례의 설계 제안이다. 사람이 목적과 품질 및 총예산을 정하고, 하네스가 도구와 기억 및 반복을 조절한다. 독립 판정을 거친 결과를 기록한다. 예산이 부족하거나 진전이 없으면 확보한 근거와 미완료 상태를 인계한다. 실패와 검증 비용을 포함한 관찰을 다음 정책 검토에 연결한다.')
    s.title(5,'자원 조건을 실행 규칙에 연결하기','설계 제안 · 근거를 검증하는 리뷰 작성의 경우',m)
    x=40 if m else 58
    if m:
        s.text(x,176,'기획자가 정하는 조건',28,700)
        for i,(a,b) in enumerate([('목적','확인할 주장과 독자의 질문'),('품질','출처 대조·계산·오류 기준'),('예산','작업별 한도와 기간별 총량')]):
            yy=229+i*49;s.text(x,yy,a,25,700,TEAL);s.text(147,yy,b,25)
        s.line(350,350,350,394,TEAL,2,marker='info')
        s.rect(x,411,620,330,'none',TEAL,1.7)
        s.text(x+22,456,'실행을 조절하는 하네스',29,700)
        for i,(a,b) in enumerate([('자료·모델 선택','필요한 증거와 계산 강도'),('기억·도구 사용','검증 기록 검색·수식 계산'),('진전·반복 확인','같은 탐색의 반복을 감지')]):
            yy=509+i*64;s.text(x+22,yy,a,26,700);s.text(x+22,yy+34,b,24,color=MUTED)
        s.line(350,742,350,791,TEAL,2,marker='info')
        s.text(350,834,'독립 판정으로 품질 확인',29,700,anchor='middle')
        s.line(350,852,350,903,TEAL,2,marker='info')
        s.document(72,926,66,88)
        s.text(178,956,'완료한 결과와 검증 기록',28,700,TEAL)
        s.text(178,997,'조건·판본을 남겨 다음 작업에 재사용',24,color=MUTED)
        s.path('M594 829 H650 V386 H584',TEAL,2,dash='7 6',marker='info')
        s.rect(459,747,185,43,BG)
        s.text(551,776,'근거 있으면 수정',24,color=TEAL,anchor='middle')
        s.path('M40 703 H15 V1103 H55',MUTED,1.8,dash='6 5',marker='muted')
        s.text(178,1050,'예산이 부족하거나 진전이 없으면',25,color=MUTED)
        s.document(72,1070,50,67,MUTED)
        s.text(178,1097,'미완료 상태를 인계',28,700)
        s.text(178,1134,'확보 근거·남은 작업·중단 이유',24,color=MUTED)
        s.line(x,1173,660,1173)
        s.text(x,1224,'실패와 검증 비용도 관찰에 포함',27,700)
        s.lines(x,1274,['토큰·에너지·시간·오류와 재시도','측정 범위와 추정 방법을 함께 기록'],25,38,color=MUTED)
        s.path('M350 1340 V1385 H88 V1442',CLAY,2.5,marker='power')
        s.text(189,1410,'주기적 검토',24,color=CLAY)
        s.text(x,1484,'규칙 개정과 기간별 총량 평가',29,700)
        s.text(x,1526,'품질·에너지·탄소·물의 제약을 함께 확인',24,color=MUTED)
        s.footer('평가 결과에 따라 설계를 갱신하는 제안 구조',m)
    else:
        s.text(x,187,'기획자가 정하는 조건',29,700)
        for xx,a,b in [(58,'목적','확인할 주장과 독자의 질문'),(505,'품질','출처·계산·오류 기준'),(950,'예산','작업 한도와 기간별 총량')]:
            s.text(xx,239,a,26,700,TEAL);s.text(xx,276,b,25)
        s.line(58,304,1342,304)
        s.path('M272 311 V367 H438',TEAL,2,marker='info')
        s.rect(466,341,524,315,'none',TEAL,1.7)
        s.text(493,386,'실행을 조절하는 하네스',29,700)
        for i,(a,b) in enumerate([('자료·모델 선택','필요한 증거와 계산 강도'),('기억·도구 사용','검증 기록 검색·수식 계산'),('진전·반복 확인','같은 탐색의 반복을 감지')]):
            yy=438+i*65;s.text(493,yy,a,26,700);s.text(493,yy+33,b,24,color=MUTED)
        s.text(58,430,'입력 자료',27,700,TEAL)
        s.document(68,453,70,98);s.document(167,472,70,98)
        s.text(58,613,'논문·검증 기록',25,color=MUTED)
        s.line(264,505,439,505,TEAL,2,marker='info')
        s.line(990,494,1092,494,TEAL,2,marker='info')
        s.text(1208,458,'독립 판정',29,700,anchor='middle')
        s.text(1208,500,'품질 확인',27,anchor='middle')
        s.line(1208,519,1208,575,TEAL,2,marker='info')
        s.document(1173,589,72,94)
        s.text(1208,720,'완료한 결과',27,700,TEAL,anchor='middle')
        s.text(1208,755,'다음 작업에 재사용',24,color=MUTED,anchor='middle')
        s.path('M1210 407 V354 H1017',TEAL,2,dash='7 6',marker='info')
        s.text(1191,330,'추가 근거가 있으면 수정',24,color=TEAL,anchor='middle')
        s.path('M466 619 H400 V650 H80 V663',MUTED,1.8,dash='6 5',marker='muted')
        s.text(274,639,'예산 부족·진전 없음',22,color=MUTED,anchor='middle')
        s.document(58,676,45,59,MUTED)
        s.text(127,699,'미완료 상태를 인계',26,700)
        s.text(127,738,'확보 근거·남은 작업·중단 이유',23,color=MUTED)
        s.line(58,798,1342,798)
        s.text(58,845,'관찰',27,700,CLAY)
        s.text(171,845,'실패·재시도·검증을 포함한 토큰·에너지·시간·오류',26)
        s.path('M970 667 V707 H1035 V886 H990',CLAY,2.5,marker='power')
        s.text(58,929,'주기적 검토',28,700)
        s.text(276,929,'측정 범위와 추정 방법 · 품질 조건 · 에너지·탄소·물의 기간별 총량',25)
        s.path('M58 889 H29 V185 H39',MUTED,1.8,dash='7 6',marker='muted')
        s.footer('평가 결과를 다음 규칙 개정에 연결하는 설계 제안',m)
    s.save(f'fig5_{"mobile" if m else "desktop"}.svg')


if __name__ == '__main__':
    for fn in [fig1,fig2,fig3,fig4,fig5]:
        for mobile in [False,True]: fn(mobile)
    print(f'Wrote 10 SVGs to {OUT}')
