"""Deterministic bilingual responsive figures for the quantum-algorithm review.

First run verify_examples.py. Labels are teaching explanations, and the numeric
panels use ideal Born probabilities from examples.json, not hardware data.
"""
from pathlib import Path
import json, math, html
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/figures'
DATA=json.loads((ROOT/'artifacts/examples.json').read_text())
P={'bg':'#f8f7f4','ink':'#26334d','muted':'#56627a','line':'#d8dce3','violet':'#7364a5','violet_dark':'#5d4b8c','orange':'#c7835b','orange_dark':'#955037','blue':'#4f718e','gold':'#b99951','green':'#647d70','wash':'#ececf2','pale_orange':'#f1e2d5'}

def tr(ko,en,lang):return en if lang=='en' else ko
class SVG:
 def __init__(self,w,h,title,desc):
  self.w=w;self.h=h;self.a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="{P["muted"]}" stroke-width="1.3"/></marker></defs><style>text{{font-family:Arial,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;fill:{P["ink"]}}}.muted{{fill:{P["muted"]}}}.bold{{font-weight:700}}.violet{{fill:{P["violet_dark"]}}}.orange{{fill:{P["orange_dark"]}}}</style>']
  self.rect(0,0,w,h,P['bg'])
 def rect(self,x,y,w,h,fill='none',stroke='none',r=0):self.a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
 def line(self,x1,y1,x2,y2,color=None,width=1.5,dash=None,arrow=False,opacity=1):
  self.a.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or P["line"]}" stroke-width="{width}" opacity="{opacity}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
 def circle(self,x,y,r,fill,stroke='none',sw=1.5):self.a.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
 def text(self,x,y,text,size=24,cls='',anchor='start',fill=None):
  self.a.append(f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" text-anchor="{anchor}"'+(f' style="fill:{fill}"' if fill else '')+'>'+html.escape(str(text))+'</text>')
 def lines(self,x,y,strings,size=24,step=33,cls='',anchor='start'):
  for i,t in enumerate(strings):self.text(x,y+i*step,t,size,cls,anchor)
 def path(self,d,color=None,width=2.5,fill='none',dash=None):self.a.append(f'<path d="{d}" stroke="{color or P["ink"]}" stroke-width="{width}" fill="{fill}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def poly(self,pts,color=None,width=2.5):self.path('M'+' L'.join(f'{x:.3f} {y:.3f}' for x,y in pts),color,width)
 def panel(self,x,y,letter,title,width):
  self.circle(x+14,y-9,14,P['ink']);self.text(x+14,y-3,letter,18,'bold','middle',P['bg']);self.text(x+42,y,title,26,'bold');self.line(x,y+20,x+width,y+20)
 def finish(self,path):
  self.a.append('</svg>');path.write_text('\n'.join(self.a)+'\n')

def header(s,number,title,sub,mobile):
 x=36 if mobile else 44
 s.text(x,47,number,21,'bold violet');s.text(x+49,47,title,30 if mobile else 33,'bold')
 for i,t in enumerate(sub):s.text(x,91+i*32,t,24,'muted')

def cycle(s,cx,cy,r=57,labels=True,lang='ko'):
 coords=[(cx-r,cy-r),(cx+r,cy-r),(cx+r,cy+r),(cx-r,cy+r)]
 for a,b in [(0,1),(1,2),(2,3),(3,0)]:s.line(*coords[a],*coords[b],P['gold'],4)
 for i,(x,y) in enumerate(coords):
  s.circle(x,y,18,P['ink'] if i%2==0 else P['orange'])
  if labels:s.text(x,y+7,str(i),21,'bold','middle','#ffffff')
 return coords

def matrix(s,x,y,scale=1):
 s.path(f'M{x+10} {y} H{x} V{y+72*scale} H{x+10}',P['ink'],2)
 s.path(f'M{x+108*scale-10} {y} H{x+108*scale} V{y+72*scale} H{x+108*scale-10}',P['ink'],2)
 for yy,row in enumerate([[2,1],[1,2]]):
  for xx,val in enumerate(row):s.text(x+(28+49*xx)*scale,y+(28+33*yy)*scale,val,25*scale,anchor='middle')

def fig1(lang,mobile):
 w=720 if mobile else 1200;h=1775 if mobile else 1015
 s=SVG(w,h,tr('문제의 표현에서 읽을 결과까지','From problem representation to an observable answer',lang),tr('열 가지 알고리즘을 위상, 진폭, 변분, 행렬·그래프 구조의 네 경로로 연결한 개념도.','Ten named methods connected through phase, amplitude, variational and matrix/graph routes.',lang))
 title=tr('계산할 대상을 바꾸는 네 가지 경로','Four routes from a problem to an answer',lang)
 if mobile and lang=='en':title='Four routes to an answer'
 header(s,'01',title,[tr('문제의 표현 → 작용하는 연산 → 측정·후처리로 얻는 결과','Representation → coherent operation → measurement and post-processing',lang)] if not mobile else [tr('문제의 표현과 읽을 결과를 먼저 잇는다','Connect the input to the answer being read',lang)],mobile)
 rows=[
 ('위상','Phase','QFT · QPE · Shor',['N = 15, a = 2','U = exp(−iHt/ℏ)'],['주기·고유위상을','간섭으로 읽는다'],['Read phases and periods','through interference'],['r = 4 → 15 = 3 × 5','에너지 E'],['r = 4 → 15 = 3 × 5','Energy E']),
 ('진폭','Amplitude','Grover · QAE',['χ(x) = 1','C(x) = 4'],['표식과 반사를 반복해','성공 진폭을 회전시킨다'],['Mark and reflect to','rotate success amplitude'],['후보 x = 0101','확률 a = 1/8'],['Candidate x = 0101','Probability a = 1/8']),
 ('변분','Variational','VQE · QAOA',['H ;  C(x)','θ ; γ, β'],['측정한 값으로','다음 회전 각도를 고른다'],['Use measurements to','choose the next angles'],['E(θ) ; 후보 분포','고전 최적화와 반복'],['E(θ); candidates','Classical feedback']),
 ('행렬·그래프','Matrix / graph','HHL · walks · QSVT',['A|x〉 ∝ |b〉','이웃·블록 접근'],['고유값·특이값·연결을','원하는 변환에 이용한다'],['Use spectra and links','for a target transform'],['해 상태 |x〉 · 관측량','필터·시간 진화'],['State |x〉; observables','Filters; time evolution'])]
 colors=[P['violet'],P['orange'],P['blue'],P['green']]
 for i,r in enumerate(rows):
  ko,en,methods,inputs,opko,open_,outko,outen=r;color=colors[i]
  y=174+i*367 if mobile else 173+i*186
  s.line(36 if mobile else 44,y-36,w-36 if mobile else w-44,y-36)
  s.text(36 if mobile else 44,y,tr(ko,en,lang),26,'bold',fill=color)
  if mobile:
   s.text(36,y+40,methods,28,'bold')
   # Concrete input glyphs at left; a compact operation glyph in the middle.
   gx,gy=100,y+136
   if i==0:
    for j,v in enumerate([1,2,4,8]):s.text(41+j*49,y+116,str(v),27,'bold','middle',color)
    s.path(f'M40 {y+138} Q118 {y+172} 196 {y+138}',color,2)
    s.text(36,y+184,'N=15 · a=2',23,'muted')
   elif i==1:
    for j in range(16):s.circle(48+(j%8)*21,y+106+(j//8)*25,6,color if j in [5,10] else P['line'])
    s.text(36,y+184,'χ(x): C(x)=4',23,'muted')
   elif i==2:
    cycle(s,101,y+130,33,False)
    s.text(36,y+203,'H ; C(x)',23,'muted')
   else:
    matrix(s,44,y+87,.95);s.text(36,y+203,'A ; |b〉',23,'muted')
   s.line(220,y+133,288,y+133,P['muted'],1.8,arrow=True)
   if i==0:
    s.circle(346,y+133,39,'none',color,2)
    for a in [0,1.1,2.2,3.3,4.4]:s.line(346,y+133,346+35*math.cos(a),y+133-35*math.sin(a),color,1.6)
   elif i==1:
    s.path(f'M310 {y+169} A55 55 0 0 1 375 {y+101}',color,3)
    s.line(313,y+167,369,y+115,color,2,arrow=True)
   elif i==2:
    s.poly([(310,y+135),(330,y+154),(350,y+164),(370,y+146),(392,y+105)],color,3)
    s.circle(350,y+164,6,color)
   else:
    for j,bar in enumerate([22,50,75]):s.line(312+j*28,y+171,312+j*28,y+171-bar,color,9)
   s.line(413,y+133,469,y+133,P['muted'],1.8,arrow=True)
   outs=outen if lang=='en' else outko
   if i==2:outs=['E(θ); candidates','Classical feedback'] if lang=='en' else ['기대값·후보 분포','각도를 다시 선택']
   if i==3:outs=['Solution state','Filters / evolution'] if lang=='en' else ['해 상태·관측량','필터·시간 진화']
   s.lines(490,y+120,outs,23,32,'bold')
   ops=open_ if lang=='en' else opko
   s.lines(36,y+260,ops,26,35)
  else:
   s.text(44,y+43,methods,28,'bold')
   s.lines(44,y+92,inputs if lang=='ko' else [inputs[0],tr('이웃·블록 접근','Neighbour / block access',lang) if i==3 else inputs[1]],23,31,'muted')
   # Low-ink input marks and a visible action, with no enclosing keyword boxes.
   x=424;cy=y+63
   if i==0:
    s.circle(x,cy,41,'none',color,2)
    for a in [0,1.1,2.2,3.3,4.4]:s.line(x,cy,x+37*math.cos(a),cy-37*math.sin(a),color,1.6)
   elif i==1:
    for j in range(16):s.circle(x-45+(j%8)*13,cy-13+(j//8)*25,4.5,color if j in [5,10] else P['line'])
    s.path(f'M{x-43} {cy+44} Q{x} {cy+63} {x+43} {cy+44}',color,2.5)
   elif i==2:
    s.poly([(x-47,cy-20),(x-20,cy+18),(x+3,cy+31),(x+28,cy+7),(x+48,cy-26)],color,3);s.circle(x+3,cy+31,7,color)
   else:matrix(s,x-54,cy-39,.95)
   s.line(328,cy,360,cy,P['muted'],1.8,arrow=True)
   s.line(485,cy,529,cy,P['muted'],1.8,arrow=True)
   s.lines(551,y+48,open_ if lang=='en' else opko,23,34)
   s.line(827,cy,868,cy,P['muted'],1.8,arrow=True)
   s.lines(895,y+45,outen if lang=='en' else outko,23,35,'bold')
 note=tr('개념 지도 · 절차(QFT·QPE), 알고리즘, 변환 체계(QSVT)의 재사용을 함께 읽는다.','Conceptual map · procedures, algorithms and the QSVT transformation framework can be reused across routes.',lang)
 if mobile:s.lines(36,h-83,[tr('개념 지도 · 입력과 출력의 관계를 중심으로 분류','Conceptual map · grouped by input and output',lang),tr('QFT·QPE·QSVT는 다른 계산에도 재사용된다','QFT, QPE and QSVT also serve other algorithms',lang)],23,33,'muted')
 else:s.text(44,h-45,note,22,'muted')
 return s

def plot_axes(s,x,y,w,h,xlabel,ylabel,yrange,xticks,yticks,xrange):
 s.line(x,y+h,x+w,y+h,P['ink'],1.5);s.line(x,y,x,y+h,P['ink'],1.5)
 for val,label in xticks:
  xx=x+(val-xrange[0])/(xrange[1]-xrange[0])*w;s.line(xx,y+h,xx,y+h+7,P['ink']);s.text(xx,y+h+34,label,22,anchor='middle')
 for val,label in yticks:
  yy=y+h-(val-yrange[0])/(yrange[1]-yrange[0])*h;s.line(x-5,yy,x+w,yy,P['line'],1,dash='3 5');s.text(x-13,yy+7,label,22,anchor='end')
 s.text(x+w,y+h+70,xlabel,23,anchor='end');s.text(x,y-20,ylabel,23,'bold')

def fig2(lang,mobile):
 t=DATA['two_spin'];q=t['qpe'];w=720 if mobile else 1200;h=1920 if mobile else 1070
 s=SVG(w,h,tr('같은 에너지를 두 경로로 읽기','Two routes to the same energy',lang),tr('두 스핀의 에너지를 VQE의 기대값 최적화와 QPE의 유한 위상 격자로 비교한다.','A two-spin energy compared through variational expectations and a finite phase-estimation register.',lang))
 title=tr('같은 에너지를 두 경로로 읽기','Two routes to the same energy',lang)
 if mobile and lang=='en':title='Two routes to one energy'
 header(s,'02',title,[tr('H/E₀ = Z₀Z₁ + 0.7(X₀ + X₁) · 리뷰의 이상적 상태벡터 계산','H/E₀ = Z₀Z₁ + 0.7(X₀ + X₁) · ideal review-authored calculation',lang)] if not mobile else ['H/E₀ = Z₀Z₁ + 0.7(X₀ + X₁)',tr('이상적 상태벡터 계산 · 에너지 단위 E₀','Ideal statevector calculation · energy unit E₀',lang)],mobile)
 ay=201 if mobile else 160;s.panel(36 if mobile else 44,ay,'A',tr('초기 상태가 정하는 관측 확률','The prepared state sets the probabilities',lang),648 if mobile else 1112)
 if mobile:
  s.text(36,ay+70,'|Ψ+〉 = (|01〉 + |10〉)/√2',28,'bold')
  s.text(36,ay+110,tr('H의 두 고유상태가 겹쳐 있다','Overlap with two eigenstates of H',lang),25,'muted')
  specs=[(-1.720465,0.790619),(1.720465,.209381)]
  for j,(e,p) in enumerate(specs):
   yy=ay+176+j*78;s.line(58,yy,185,yy,P['violet'] if j==0 else P['blue'],4);s.circle(221,yy,9+15*p,P['violet'] if j==0 else P['blue']);s.text(262,yy+8,f'{e:+.4f} E₀',27,'bold');s.text(658,yy+8,f'{p*100:.2f}%',27,anchor='end')
 else:
  s.text(44,ay+77,'|Ψ+〉 = (|01〉 + |10〉)/√2',29,'bold');s.text(44,ay+119,tr('이 상태를 먼저 준비한다','Prepare this initial state',lang),23,'muted')
  s.line(474,ay+84,550,ay+84,P['muted'],2,arrow=True)
  for j,(e,p) in enumerate([(-1.720465,.790619),(1.720465,.209381)]):
   yy=ay+54+j*70;s.line(586,yy,687,yy,P['violet'] if j==0 else P['blue'],4);s.circle(724,yy,9+14*p,P['violet'] if j==0 else P['blue']);s.text(760,yy+8,f'{e:+.4f} E₀',27,'bold');s.text(1146,yy+8,f'{p*100:.2f}%',27,anchor='end')
 by=573 if mobile else 383;s.panel(36 if mobile else 44,by,'B',tr('VQE · 회전 각도와 기대 에너지','VQE · angle and expected energy',lang),648 if mobile else 520)
 x,y,pw,ph=(107,by+105,529,244) if mobile else (107,by+100,415,270)
 plot_axes(s,x,y,pw,ph,tr('θ (rad)','θ (rad)',lang),'E(θ)/E₀',(-2,1.2),[(0,'0'),(math.pi/4,'π/4'),(math.pi/2,'π/2')],[(-2,'−2'),(-1,'−1'),(0,'0'),(1,'1')],(0,math.pi/2))
 coords=[(x+r['theta_rad']/(math.pi/2)*pw,y+ph-(r['energy_over_E0']+2)/3.2*ph) for r in t['curve']];s.poly(coords,P['violet'],3.5)
 yy=y+ph-(-math.sqrt(2.96)+2)/3.2*ph;xx=x+t['theta_star_rad']/(math.pi/2)*pw
 s.line(x,yy,x+pw,yy,P['orange'],1.7,dash='6 5');s.circle(xx,yy,7,P['orange']);s.text(xx+16,yy-19,'−1.7205',25,'bold orange')
 s.text(x+pw,y+ph+113,'θ* = 0.4753 rad',25,'bold',anchor='end')
 if mobile:s.lines(36,by+503,[tr('〈H〉 = −cos2θ − 1.4sin2θ  (단위 E₀)','〈H〉/E₀ = −cos2θ − 1.4sin2θ',lang),tr('각도를 조정해 바닥상태 에너지를 최소화한다','Adjust the angle to minimise the expected energy',lang)],24,35,'muted')
 else:s.lines(44,by+508,['〈H〉/E₀ = −cos2θ − 1.4sin2θ',tr('θ를 바꾸며 같은 H의 기대값을 비교한다','Compare expectations of the same H as θ varies',lang)],23,32,'muted')
 cy=1201 if mobile else 383;s.panel(36 if mobile else 635,cy,'C',tr('QPE · 유한한 위상 격자의 확률','QPE · finite phase grid',lang) if not(mobile and lang=='en') else 'QPE · a finite phase grid',648 if mobile else 521)
 x,y,pw,ph=(101,cy+115,540,240) if mobile else (698,cy+100,420,270)
 plot_axes(s,x,y,pw,ph,tr('φ = y/64','φ = y/64',lang),tr('확률 P(y)','Probability P(y)',lang),(0,.7),[(0,'0'),(.25,'.25'),(.5,'.5'),(.75,'.75'),(1,'1')],[(0,'0'),(.2,'.2'),(.4,'.4'),(.6,'.6')],(0,1))
 for row in q['bins']:
  xx=x+row['phase']*pw;yy=y+ph-row['probability']/.7*ph;s.line(xx,y+ph,xx,yy,P['violet'] if row['y']==38 else P['blue'],3 if row['y'] in [10,38] else 1.5)
  if row['y'] in [10,38]:s.circle(xx,yy,5,P['violet'] if row['y']==38 else P['blue'])
 r=q['top_bins'][0];xx=x+r['phase']*pw;yy=y+ph-r['probability']/.7*ph
 s.text(xx+13,yy+2,'y = 38',24,'bold violet')
 s.text(x+pw,y+ph+113,'E/E₀ = 3 − 8φ',25,'bold',anchor='end')
 notes=[tr('6개 제어 + 2개 표적 큐비트','6 control + 2 target qubits',lang),tr('최빈 y=38 → E/E₀=−1.75 · P=65.57%','Most likely y=38 → E/E₀=−1.75 · P=65.57%',lang)]
 s.lines(36 if mobile else 635,cy+(510 if mobile else 508),notes,23,32,'muted')
 fy=h-97;s.line(36 if mobile else 44,fy-24,w-(36 if mobile else 44),fy-24)
 footer=[tr('U = exp[−i(H/E₀ − 3I)τ], τ=π/4 · t=τℏ/E₀','U = exp[−i(H/E₀ − 3I)τ], τ=π/4 · t=τℏ/E₀',lang),tr('‖H/E₀‖≤2.4 · 위상 한 주기의 에너지 폭 8E₀','‖H/E₀‖≤2.4 · one phase period spans 8E₀',lang)]
 s.lines(36 if mobile else 44,fy,footer,23,34,'muted')
 return s

def hypercube(s,x,y,scale=1):
 pts={}
 for num in range(16):
  bits=[int(v) for v in format(num,'04b')]
  pts[num]=(x+scale*(bits[0]*104+bits[2]*31+bits[3]*211),y+scale*(bits[1]*89-bits[2]*29))
 for num,(xx,yy) in pts.items():
  for bit in range(4):
   nxt=num^(1<<(3-bit))
   if num<nxt:s.line(xx,yy,*pts[nxt],P['blue'],1.3,opacity=.33 if bit==3 else .67)
 for num,(xx,yy) in pts.items():
  s.circle(xx,yy,8*scale if num in [5,10] else 5*scale,P['orange'] if num in [5,10] else P['blue'])
  if num in [5,10]:s.text(xx+11*scale,yy-13*scale,format(num,'04b'),23*scale,'bold orange')
 return pts

def fig3(lang,mobile):
 d=DATA['maxcut'];w=720 if mobile else 1200;h=1850 if mobile else 1260
 s=SVG(w,h,tr('한 cut 문제에서 세 가지 계산 질문','One cut problem, three computational questions',lang),tr('4-cycle MaxCut 입력과16후보의 상태 공간, QAOA와Grover의 이상적 확률, QAE가 읽는 회전각을 나타낸다.','A four-cycle MaxCut input, its sixteen-state candidate space, ideal QAOA/Grover distributions and the angle read by amplitude estimation.',lang))
 title='같은 후보를 어떻게 살펴보는가' if lang=='ko' else 'How to examine the same candidates'
 header(s,'03',title,[tr('4-cycle MaxCut · 16개 후보 중 C=4인 후보는 0101, 1010','Four-cycle MaxCut · 0101 and 1010 are the two C=4 candidates among 16',lang)] if not mobile else [tr('4-cycle MaxCut · 16후보 중 최적 2개','Four-cycle MaxCut · 2 optimal candidates of 16',lang),tr('χ(x)=1 ⇔ C(x)=4','χ(x)=1 ⇔ C(x)=4',lang)],mobile)
 ay=197 if mobile else 160;s.panel(36 if mobile else 44,ay,'A',tr('입력 그래프와 후보 상태 공간','Input graph and candidate-state space',lang),648 if mobile else 1112)
 if mobile:
  cycle(s,150,ay+159,51,True);s.text(150,ay+259,tr('입력: 4개 꼭짓점','Input: 4 vertices',lang),24,'bold',anchor='middle')
  hypercube(s,339,ay+116,.8);s.lines(340,ay+259,[tr('후보: 16개 비트열','Candidates: 16 strings',lang),tr('한 비트 반전으로 연결','Edges flip one bit',lang)],24,34,'bold')
  s.lines(36,ay+355,[tr('입력의 간선은 cut 값을 정한다.','Input edges determine the cut value.',lang),tr('후보 사이의 간선은 mixer의 이동을 나타낸다.','Candidate edges show possible mixer moves.',lang)],24,34,'muted')
 else:
  cycle(s,174,ay+132,54,True);s.text(174,ay+237,tr('입력: 4개 꼭짓점','Input: 4 vertices',lang),24,'bold',anchor='middle')
  s.line(323,ay+131,382,ay+131,P['muted'],2,arrow=True)
  hypercube(s,453,ay+84,1.1);s.lines(909,ay+106,[tr('후보: 16개 비트열','Candidates: 16 strings',lang),tr('한 비트 반전으로 연결','Edges flip one bit',lang)],24,35,'bold')
  s.text(451,ay+252,tr('입력의 간선: cut 비용 · 후보의 간선: mixer 이동','Input edges: cut cost · candidate edges: mixer moves',lang),23,'muted')
 by=690 if mobile else 482;s.panel(36 if mobile else 44,by,'B',tr('연산이 바꾸는 cut 값의 분포','Operations change the cut distribution',lang),648 if mobile else 1112)
 # Identical bins for three preparations; these bars do not equate oracle costs.
 labels=[tr('균등한 초기 상태','Uniform start',lang),'QAOA · p=1','Grover · k=2']
 summaries=[d['uniform'],d['qaoa'],{'cost_probabilities':{'0':.0078125,'2':.046875,'4':.9453125},'success_probability':.9453125,'expected_cut':3.875}]
 bx=68 if mobile else 375;bw=565 if mobile else 596
 for i,row in enumerate(summaries):
  yy=by+90+i*(119 if mobile else 74)
  s.text(36 if mobile else 44,yy,labels[i],25,'bold')
  if mobile:yy+=24
  left=bx
  for cost,color in [('0',P['line']),('2',P['blue']),('4',P['orange'])]:
   bwidth=bw*row['cost_probabilities'][cost];s.rect(left,yy-22,bwidth,30,color);left+=bwidth
  s.text(648 if mobile else 1149,yy+47 if mobile else yy+1,f'{row["success_probability"]*100:.2f}%',24,'bold orange',anchor='end')
 # cost legend
 ly=by+(475 if mobile else 301)
 for j,(label,color) in enumerate([('C=0',P['line']),('C=2',P['blue']),('C=4',P['orange'])]):
  lx=(40+j*180) if mobile else (376+j*166);s.rect(lx,ly-16,15,15,color);s.text(lx+25,ly,label,23,'muted')
 s.text(648 if mobile else 1148,ly,tr('오른쪽 수치: P(C=4)','Right: P(C=4)',lang),23,'muted',anchor='end') if not mobile else None
 if mobile:s.text(36,ly+38,tr('행별 수치: P(C=4)','Each row reports P(C=4)',lang),23,'muted')
 angle_note=tr('QAOA: γ=π/4, β=π/8 · e⁻ⁱᵝΣˣ e⁻ⁱᵞᶜ|+〉⁴','QAOA: γ=π/4, β=π/8 · e⁻ⁱᵝΣˣ e⁻ⁱᵞᶜ|+〉⁴',lang)
 s.text(36 if mobile else 44,ly+(83 if mobile else 49),angle_note,23,'muted')
 cy=1330 if mobile else 918;s.panel(36 if mobile else 44,cy,'C',tr('Grover와 QAE가 공유하는 회전','The rotation shared by Grover and QAE',lang),648 if mobile else 1112)
 cx=181 if mobile else 177;cyc=cy+(248 if mobile else 178);r=132 if mobile else 108
 s.line(cx-34,cyc,cx+r+39,cyc,P['muted'],1.3);s.line(cx,cyc+24,cx,cyc-r-32,P['muted'],1.3)
 # Only the relevant upper arc; coordinates are amplitudes, not physical position.
 points=[(cx+r*math.cos(a),cyc-r*math.sin(a)) for a in [i*math.pi/180 for i in range(0,122)]];s.poly(points,P['line'],2)
 for k in [0,1,2]:
  a=(2*k+1)*d['grover']['theta_rad'];xx=cx+r*math.cos(a);yy=cyc-r*math.sin(a);s.line(cx,cyc,xx,yy,P['orange'] if k==2 else P['blue'],2.2);s.circle(xx,yy,6,P['orange'] if k==2 else P['blue'])
  if k in [0,2]:s.text(xx+(14 if k==0 else -9),yy+(-13 if k==2 else 24),f'k={k}',23,'bold',anchor='end' if k==2 else 'start')
 s.text(cx+r+28,cyc+37,tr('낮은 비용 후보','Bad amplitude',lang) if lang=='en' else '실패 진폭',22,'muted',anchor='end')
 s.text(cx-4,cyc-r-25,tr('성공 진폭','Good amplitude',lang),22,'muted')
 if mobile:
  s.lines(360,cy+104,['a = 2/16 = 1/8','θ = asin√a',f'θ = {d["grover"]["theta_rad"]:.4f} rad'],25,42,'bold')
  s.lines(36,cy+371,[tr('Grover: 상태를 매회 2θ만큼 회전','Grover: rotate the state by 2θ per iteration',lang),tr('QAE: 고유위상 ±2θ를 읽어 a=sin²θ 추정','QAE: read eigenphases ±2θ to estimate a=sin²θ',lang)],24,35,'muted')
 else:
  s.lines(443,cy+82,['a = 2/16 = 1/8',f'θ = asin√a = {d["grover"]["theta_rad"]:.4f} rad'],26,41,'bold')
  s.lines(832,cy+82,[tr('Grover: 상태를 2θ 회전','Grover: state rotation by 2θ',lang),tr('QAE: 고유위상 ±2θ → a','QAE: eigenphases ±2θ → a',lang)],24,41,'muted')
 fy=h-62;s.line(36 if mobile else 44,fy-32,w-(36 if mobile else 44),fy-32)
 if mobile:s.lines(36,fy,[tr('리뷰의 이상적 상태벡터 계산','Ideal statevector calculation',lang),tr('막대: Born 확률 · shot 표본추출 없음','Bars: Born probabilities; no shot sampling',lang)],23,32,'muted')
 else:s.text(44,fy,tr('리뷰의 이상적 상태벡터 계산 · 막대는 Born 확률이며 유한 shot 빈도가 아니다.','Ideal statevector calculation · bars are Born probabilities, not finite-shot frequencies.',lang),23,'muted')
 return s


def main():
 OUT.mkdir(parents=True,exist_ok=True)
 rows=[]
 for n,build in [(1,fig1),(2,fig2),(3,fig3)]:
  for lang in ['ko','en']:
   for mobile in [False,True]:
    stem=f'fig{n}_{"mobile" if mobile else "desktop"}'+('_en' if lang=='en' else '')
    s=build(lang,mobile);p=OUT/(stem+'.svg');s.finish(p);rows.append({'file':p.name,'language':lang,'width':s.w,'height':s.h})
 (ROOT/'artifacts/figure-manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(json.dumps({'figures':len(rows),'directory':'artifacts/figures'}))
if __name__=='__main__':main()
