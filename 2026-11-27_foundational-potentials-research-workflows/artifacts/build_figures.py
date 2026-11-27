"""Deterministic bilingual/responsive science figures; numeric curves use Matplotlib.

Run verify_examples.py first. Dependency: matplotlib, numpy.
All architecture panels are review-authored conceptual designs; Figure 2 is a
harmonic teaching model, not an MLIP/DFT result or Potente reproduction.
"""
from pathlib import Path
import json, math, html, io, re
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/figures'
D=json.loads((ROOT/'artifacts/examples.json').read_text())
P={'bg':'#f7f5ef','ink':'#223c44','muted':'#566c70','line':'#ccd5d1','teal':'#387a7d','teal_dark':'#236366','coral':'#c77756','coral_dark':'#9a4e33','gold':'#b99b5c','light':'#e7eee8','wash':'#e7eeeb','blue':'#597e98','green':'#66845a'}
plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'ATRL-foundation-20261127','font.family':'DejaVu Sans','font.size':18,'axes.labelsize':18,'xtick.labelsize':16,'ytick.labelsize':16,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':P['muted'],'text.color':P['ink'],'axes.labelcolor':P['ink'],'xtick.color':P['muted'],'ytick.color':P['muted'],'figure.facecolor':P['bg'],'axes.facecolor':P['bg']})
def T(ko,en,lang):return en if lang=='en' else ko
class S:
 def __init__(self,w,h,title,desc):
  self.w=w;self.h=h;self.a=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="{P["muted"]}" stroke-width="1.3"/></marker></defs><style>text{{font-family:Arial,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;fill:{P["ink"]}}}.muted{{fill:{P["muted"]}}}.bold{{font-weight:700}}.teal{{fill:{P["teal_dark"]}}}.coral{{fill:{P["coral_dark"]}}}</style>']
  self.rect(0,0,w,h,P['bg'])
 def rect(self,x,y,w,h,fill='none',stroke='none',r=0):self.a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
 def line(self,x1,y1,x2,y2,color=None,width=1.5,dash=None,arrow=False):
  self.a.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or P["line"]}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
 def circle(self,x,y,r,fill=None,stroke='none',sw=1.5):self.a.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill or P["teal"]}" stroke="{stroke}" stroke-width="{sw}"/>')
 def text(self,x,y,text,size=25,cls='',anchor='start',fill=None):self.a.append(f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" text-anchor="{anchor}"'+(f' style="fill:{fill}"' if fill else '')+'>'+html.escape(str(text))+'</text>')
 def lines(self,x,y,ss,size=25,step=34,cls='',anchor='start'):
  for i,t in enumerate(ss):self.text(x,y+i*step,t,size,cls,anchor)
 def path(self,d,color=None,width=2,fill='none',dash=None):self.a.append(f'<path d="{d}" stroke="{color or P["ink"]}" stroke-width="{width}" fill="{fill}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def panel(self,x,y,letter,title,width):
  self.circle(x+14,y-9,14,P['ink']);self.text(x+14,y-3,letter,18,'bold','middle',P['bg']);self.text(x+42,y,title,26,'bold');self.line(x,y+20,x+width,y+20)
 def embed(self,x,y,w,h,svg):
  svg=svg[svg.index('<svg'):];svg=re.sub(r'font-family:[^;]+;', 'font-family:Arial,sans-serif;',svg);rootend=svg.index('>');root=svg[:rootend+1]
  vb=re.search('viewBox="([^"]+)"',root).group(1)
  self.a.append(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}">'+svg[rootend+1:])
 def save(self,path):
  source='\n'.join(self.a+['</svg>'])+'\n';ET.fromstring(source);path.write_text(source)
def header(s,n,title,subs,mobile):
 x=36 if mobile else 44;s.text(x,49,n,21,'bold teal');s.text(x+48,49,title,30 if mobile else 33,'bold')
 s.lines(x,94,subs,24,32,'muted')
def atom_cluster(s,x,y,scale=1,kind='crystal',displaced=False):
 if kind=='molecule':
  pts=[(0,0),(38,-30),(-36,-28),(9,43)]
  for i in range(1,4):s.line(x,y,x+pts[i][0]*scale,y+pts[i][1]*scale,P['gold'],3)
  for i,(dx,dy) in enumerate(pts):s.circle(x+dx*scale,y+dy*scale,(12 if i==0 else 8)*scale,P['coral'] if i==0 else P['blue'])
 elif kind=='surface':
  for row in range(2):
   for col in range(4):s.circle(x+(col-1.5)*28*scale,y+row*28*scale,7*scale,P['blue'])
  s.circle(x,y-38*scale,10*scale,P['coral']);s.line(x,y-26*scale,x-15*scale,y-8*scale,P['gold'],2)
 else:
  pts=[(0,0),(-40,-27),(0,-42),(40,-27),(-40,27),(0,42),(40,27)]
  for i in range(1,len(pts)):s.line(x,y,x+pts[i][0]*scale,y+pts[i][1]*scale,P['line'],2)
  for i,(dx,dy) in enumerate(pts):s.circle(x+dx*scale,y+dy*scale,(12 if i==0 else 8)*scale,P['coral'] if i==0 else P['teal'])
  if displaced:s.line(x,y,x+27*scale,y-4*scale,P['coral_dark'],2.1,arrow=True)
def model_glyph(s,x,y,w=260,h=135):
 # A reusable function, with an explicit hidden representation and output.
 s.path(f'M{x} {y+22} V{y} H{x+w} V{y+h} H{x} V{y+h-22}',P['teal'],2.2)
 for i in range(5):
  for j in range(4):
   if (i+j)%2==0:s.line(x+49,y+30+i*19,x+122,y+38+j*22,P['line'],1)
 for i in range(5):s.circle(x+49,y+30+i*19,4,P['blue'])
 for j in range(4):s.circle(x+122,y+38+j*22,4,P['teal'])
 s.line(x+146,y+68,x+176,y+68,P['muted'],1.5,arrow=True)
 s.text(x+194,y+60,'U',24,'bold');s.text(x+191,y+95,'−∇U',22,'bold')
 return

def fig1(lang,mobile):
 w=720 if mobile else 1200;h=1900 if mobile else 1110
 s=S(w,h,T('재사용되는 것과 다시 확인할 것','What is reused and what is checked again',lang),T('원자 환경에서 표현과 가중치, 새로운 물질의 참조 자료와 검증으로 이어지는 개념 경로.','A conceptual route from atomic environments to representations, weights, new reference data and property validation.',lang))
 title=T('배운 함수를 새 물질에 가져오기','Bringing a learned function to a new material',lang)
 if mobile and lang=='en':title='Reuse a learned function'
 header(s,'01',title,[T('가중치·표현·계산 기준을 구별해 재사용한다','Distinguish weights, representations and reference labels',lang)] if not mobile else [T('무엇을 재사용하고 무엇을 다시 검사할까','What is reused, and what is tested again?',lang)],mobile)
 if mobile:
  s.panel(36,173,'A',T('사전학습이 만든 공통 출발점','A shared starting point',lang),648)
  for x,kind,label in [(130,'molecule',T('분자','Molecule',lang)),(350,'crystal',T('벌크','Bulk',lang)),(570,'surface',T('계면','Interface',lang))]:
   atom_cluster(s,x,270,1.12,kind);s.text(x,353,label,24,'bold',anchor='middle')
  s.text(36,407,T('원자종·배치 R → 표현 hθ(R) → Uθ(R), Fθ(R)','Species and R → hθ(R) → Uθ(R), Fθ(R)',lang),24,'bold')
  s.line(360,438,360,482,P['muted'],2,arrow=True)
  model_glyph(s,228,512);s.text(360,690,T('기존 체크포인트 θ₀','Existing checkpoint θ₀',lang),25,'bold',anchor='middle')
  s.panel(36,778,'B',T('새 물질이 방문할 배치','Configurations of the new material',lang),648)
  atom_cluster(s,145,894,1.3,'crystal',True);s.lines(270,870,[T('이완 구조 + 작은 변위','Relaxed structure + displacements',lang),T('조성·전하·스핀·온도 확인','Charge, spin, temperature',lang)],24,36)
  s.line(360,966,360,1006,P['muted'],2,arrow=True)
  s.lines(36,1050,[T('같은 R에서 예측과 참조를 대조','Compare predictions and references at the same R',lang),T('에너지·힘·응력의 DFT 기준을 맞춘다','Match the DFT energy, force and stress reference',lang)],24,35,'bold')
  # Two evidence routes remain separate: test first, add reference labels when needed.
  s.path('M360 1121 V1160 H170 V1205',P['muted'],2);s.path('M360 1160 H550 V1205',P['muted'],2)
  s.lines(170,1252,[T('독립 검증','Independent test',lang),T('θ₀의 적용 범위','Domain of θ₀',lang)],24,35,'bold','middle')
  s.lines(550,1252,[T('새 참조 표본','New reference data',lang),T('추가 학습 → θ₁','Fine-tune → θ₁',lang)],24,35,'bold','middle')
  s.path('M170 1320 V1380 H550 V1320',P['muted'],2);s.line(360,1380,360,1424,P['muted'],2,arrow=True)
  s.panel(36,1490,'C',T('목표 물성으로 확인한다','Test the requested property',lang),648)
  s.lines(36,1557,[T('보류한 변위의 힘과 곡률','Forces and curvature on held-out displacements',lang),T('진동수·구조 순위·전이 배치','Frequencies, structure ordering, transition states',lang),T('모델 판본 + 참조 기준 + 시험 결과를 보존','Keep model version, reference and test results',lang)],24,39)
  s.lines(36,1776,[T('개념 설계 · 표현의 유사성, 가중치 전이,','Conceptual design · representation alignment,',lang),T('새 물성의 정확도를 각각 검사한다.','weight transfer and property accuracy are tested separately.',lang)],22,31,'muted')
 else:
  s.panel(44,162,'A',T('공통으로 배운 함수','A shared learned function',lang),1112)
  for x,kind,label in [(130,'molecule',T('분자','Molecule',lang)),(315,'crystal',T('벌크','Bulk',lang)),(500,'surface',T('계면','Interface',lang))]:
   atom_cluster(s,x,266,1.1,kind);s.text(x,348,label,24,'bold',anchor='middle')
  s.line(590,266,658,266,P['muted'],2,arrow=True)
  model_glyph(s,697,215,260,135);s.lines(997,264,['θ₀',T('체크포인트','Checkpoint',lang)],25,35,'bold')
  s.text(44,413,T('원자종·배치 R → 표현 hθ(R) → 에너지 Uθ(R), 힘 Fθ(R)=−∇Uθ(R)','Species and R → hθ(R) → energy Uθ(R), forces Fθ(R)=−∇Uθ(R)',lang),25,'bold')
  s.panel(44,502,'B',T('새 계에서 비교할 대상','Comparisons in the new system',lang),1112)
  atom_cluster(s,137,625,1.4,'crystal',True)
  s.lines(263,574,[T('새 물질의 구조·변위 R','New structures and displacements R',lang),T('조성·전하·스핀·온도','Charge, spin, temperature',lang)],24,36,'bold')
  s.line(682,600,733,600,P['muted'],2,arrow=True)
  s.lines(769,570,[T('같은 배치의 예측과 DFT 참조','Predictions and DFT at the same R',lang),T('에너지·힘·응력의 기준 일치','Match energy, force and stress labels',lang)],23,35,'bold')
  s.text(263,696,T('θ₀로 먼저 검사한다','Test θ₀ first',lang),25,'bold teal');s.text(769,696,T('필요한 새 표본으로 θ₁을 학습','New data can refine θ₁',lang),25,'bold coral')
  s.path('M520 727 V768 H960 V727',P['muted'],2);s.line(740,768,740,808,P['muted'],2,arrow=True)
  s.panel(44,865,'C',T('새 예측을 물성으로 검증','Validate the requested property',lang),1112)
  s.lines(44,923,[T('보류한 변위: 힘과 곡률','Held-out displacements: force and curvature',lang),T('목표: 진동수·구조 순위·전이 배치','Targets: frequencies, ordering, transition states',lang)],24,36)
  s.lines(687,923,[T('보존할 기록','Records to keep',lang),T('모델 판본 · 참조 기준 · 시험 결과','Model version · reference · test results',lang)],24,36,'bold')
  s.text(44,1070,T('개념 설계 · 표현 비교, 가중치 전이, 물성 정확도는 각각 확인하는 결과다.','Conceptual design · compare representations, transfer weights and test physical observables.',lang),23,'muted')
 return s

def plot_svg(kind,width,height):
 fig,ax=plt.subplots(figsize=(width/100,height/100),dpi=100)
 fig.subplots_adjust(left=.18,bottom=.2,right=.96,top=.94)
 for i,row in enumerate(D['cases']):
  q=[x['q_A'] for x in row['curve']]
  y=[x['delta_energy_eV'] if kind=='energy' else x['generalized_force_eV_per_A'] for x in row['curve']]
  ax.plot(q,y,color=P['teal'] if i==0 else P['coral'],lw=2.8,label='k = 4.00' if i==0 else 'k = 3.24')
 ax.axvline(0,color=P['line'],lw=1,zorder=0);ax.axhline(0,color=P['line'],lw=1,zorder=0)
 ax.set_xlim(-.16,.16);ax.set_xticks([-.15,0,.15]);ax.set_xlabel('q (Å)')
 if kind=='energy':
  ax.set_ylim(-.001,.056);ax.set_yticks([0,.02,.04]);ax.set_ylabel('ΔU (eV)')
  ax.scatter([.1,.1],[.02,.0162],color=[P['teal'],P['coral']],s=32,zorder=4)
 else:
  ax.set_ylim(-.68,.68);ax.set_yticks([-.6,0,.6]);ax.set_ylabel('Q (eV/Å)')
 ax.grid(axis='y',color=P['line'],lw=.7,ls=(0,(2,4)))
 ax.legend(frameon=False,fontsize=15,loc='upper center' if kind=='energy' else 'upper right',bbox_to_anchor=(.47,1.04) if kind=='energy' else None)
 bio=io.StringIO();fig.savefig(bio,format='svg',metadata={'Date':None});plt.close(fig)
 return bio.getvalue()

def chain_mode(s,x,y,width,lang,mobile=False):
 xs=[x+i*width/3 for i in range(4)]
 # Dashed continuation shows periodicity; all equal atoms and one bond species.
 s.line(x-35,y,xs[-1]+35,y,P['line'],3,dash='5 6')
 for i in range(3):s.line(xs[i]+20*(1 if i%2==0 else -1),y,xs[i+1]+20*(1 if (i+1)%2==0 else -1),y,P['gold'],3)
 for i,xx in enumerate(xs):
  shift=20*(1 if i%2==0 else -1)
  s.circle(xx,y,12,P['bg'],P['muted'],1.4);s.circle(xx+shift,y,12,P['teal'] if i%2==0 else P['coral'])
  s.line(xx,y-29,xx+shift,y-29,P['teal_dark'] if i%2==0 else P['coral_dark'],2,arrow=True)
  s.text(xx,y+53,'+q/2' if i%2==0 else '−q/2',23,anchor='middle')
 s.text(x+width/2,y+102,T('4원자 주기 사슬 · 원자당 28 amu','Periodic four-atom chain · 28 amu per atom',lang),23,'bold',anchor='middle')
 s.text(x+width/2,y+135,T('색: 변위 방향 · 빈 원: 평형 위치','Color: displacement direction · hollow: equilibrium',lang),21,'muted',anchor='middle')

def fig2(lang,mobile):
 w=720 if mobile else 1200;h=1880 if mobile else 1160
 s=S(w,h,T('에너지의 깊이와 휘어짐','Energy depth and curvature',lang),T('같은 최솟값을 가진 두 사슬의 에너지 곡률과 복원력, 진동수를 비교한 독립 검산 교육 계산.','An independently checked harmonic-chain teaching calculation comparing energy curvature, restoring force and vibration frequency at the same energy minimum.',lang))
 header(s,'02',T('같은 최솟값, 다른 진동수','Same minimum, different frequencies',lang),[T('검산한 조화 사슬 · 실제 MLIP 결과와 구별한 교육 계산','Checked harmonic chain · review-authored educational calculation',lang)] if not mobile else [T('같은 모드 좌표 q를 따라 두 함수를 비교한다','Two functions compared along the same mode q',lang)],mobile)
 if mobile:
  s.panel(36,178,'A',T('집단 변위의 좌표를 정한다','Define a collective displacement',lang),648)
  chain_mode(s,100,292,520,lang,True)
  s.lines(36,465,['uᵢ=q eᵢ,  e=(1,−1,1,−1)/2',T('q=0.10 Å → 원자 변위 ±0.05 Å','q=0.10 Å → atomic shifts ±0.05 Å',lang)],25,36,'bold')
  s.panel(36,580,'B',T('곡률이 에너지와 힘을 바꾼다','Curvature changes energy and force',lang),648)
  s.embed(25,616,670,425,plot_svg('energy',670,425))
  s.embed(25,1068,670,385,plot_svg('force',670,385))
  s.panel(36,1530,'C',T('곡률에서 진동수로','From curvature to frequency',lang),648)
  s.lines(36,1601,['μ=28 amu,  k=4K,  f=√(k/μ)/(2π)',T('기준: k=4.00 eV/Å² → f=5.909 THz','Reference: k=4.00 eV/Å² → f=5.909 THz',lang),T('연화: k=3.24 eV/Å² → f=5.318 THz','Softened: k=3.24 eV/Å² → f=5.318 THz',lang)],24,38,'bold')
  s.text(36,1758,T('k × 0.81 → f × 0.90','k × 0.81 → f × 0.90',lang),30,'bold coral')
  s.text(36,1835,T('U(q)=U₀+½kq² · Q=−kq · 같은 U₀','U(q)=U₀+½kq² · Q=−kq · same U₀',lang),23,'muted')
 else:
  s.panel(44,168,'A',T('집단 변위의 좌표를 정한다','Define the collective coordinate',lang),1112)
  chain_mode(s,125,272,450,lang)
  s.lines(715,247,['uᵢ=q eᵢ', 'e=(1,−1,1,−1)/2',T('q=0.10 Å → 원자 변위 ±0.05 Å','q=0.10 Å → atomic shifts ±0.05 Å',lang)],25,39,'bold')
  s.panel(44,477,'B',T('같은 U₀, 다른 곡률과 복원력','Same U₀, different curvature and force',lang),1112)
  s.embed(24,522,650,438,plot_svg('energy',650,438))
  s.embed(682,519,490,351,plot_svg('force',490,351))
  s.lines(727,915,[T('기준: k=4.00 → f=5.909 THz','Reference: k=4.00 → f=5.909 THz',lang),T('연화: k=3.24 → f=5.318 THz','Softened: k=3.24 → f=5.318 THz',lang)],23,37,'bold')
  s.text(44,1024,'μ=28 amu · k=4K · f=√(k/μ)/(2π)',25,'bold')
  s.text(747,1024,'k × 0.81 → f × 0.90',30,'bold coral')
  s.line(44,1060,1156,1060)
  s.text(44,1110,T('U(q)=U₀+½kq² · Q=−dU/dq=−kq · k의 단위 eV/Å² · f=ω/(2π)','U(q)=U₀+½kq² · Q=−dU/dq=−kq · k in eV/Å² · f=ω/(2π)',lang),24,'muted')
 return s

# Sequential numeric artifacts drawn as real, inspectable objects rather than nested keyword boxes.
def mini_matrix(s,x,y,scale=1):
 s.path(f'M{x+8} {y} H{x} V{y+85*scale} H{x+8}',P['muted'],1.7);s.path(f'M{x+133*scale-8} {y} H{x+133*scale} V{y+85*scale} H{x+133*scale-8}',P['muted'],1.7)
 for row,arr in enumerate([[2,-1,0,-1],[-1,2,-1,0],[0,-1,2,-1],[-1,0,-1,2]]):
  for col,v in enumerate(arr):s.text(x+(19+31*col)*scale,y+(18+21*row)*scale,'−1' if v==-1 else str(v),17*scale,anchor='middle')
def small_chain(s,cx,cy):
 for i in range(3):s.line(cx-72+i*48,cy,cx-24+i*48,cy,P['gold'],3)
 s.line(cx-96,cy,cx-72,cy,P['line'],2,dash='3 4');s.line(cx+72,cy,cx+96,cy,P['line'],2,dash='3 4')
 for i in range(4):
  xx=cx-72+48*i;s.circle(xx,cy,10,P['teal'] if i%2==0 else P['coral']);s.line(xx,cy-23,xx+13*(1 if i%2==0 else -1),cy-23,P['muted'],1.7,arrow=True)
def check(s,x,y,color=None):s.path(f'M{x} {y} l8 9 l17 -24',color or P['green'],3)
def fig3(lang,mobile):
 w=720 if mobile else 1200;h=2035 if mobile else 1160
 s=S(w,h,T('연구 의도를 다시 실행할 수 있는 계산으로','From research intent to a reusable calculation',lang),T('사람이 정한 물성과 기준을 에이전트의 그래프 또는 맞춤 코드 기획에 연결하고 검증된 수치 도구, 결과와 실패 기록으로 이어지는 일반화한 설계.','A generalized design connecting human-selected observables and criteria to agent-planned graphs or custom code, verified numeric tools and retained result/failure records.',lang))
 title=T('의도에서 결과, 다시 쓸 절차까지','From intent to results and reusable procedures',lang)
 if mobile and lang=='en':title='From intent to reusable work'
 header(s,'05',title,[T('사람의 물리적 판단 + 에이전트 기획 + 검증한 수치 실행','Human physical judgment + agent planning + checked numeric execution',lang)] if not mobile else [T('한 결정의 진동 계산으로 읽는 일반화한 설계','Generalized design for one vibration calculation',lang)],mobile)
 if mobile:
  s.panel(36,178,'A',T('사람이 질문과 기준을 정한다','People set the target and criteria',lang),648)
  s.lines(36,243,[T('“이 결정의 진동을 검증해 달라”','“Validate this crystal’s vibrations”',lang),T('구조·전자 상태·모델·변위·허용 오차','Structure, electronic state, model, step, tolerance',lang)],25,38,'bold')
  s.line(360,310,360,348,P['muted'],2,arrow=True)
  s.lines(36,401,[T('에이전트의 기획과 분기','Agent planning and routing',lang)],26,36,'bold teal')
  # Two entrances to a common computation, not competing fidelity claims.
  s.path('M360 430 V468 H164 V510',P['muted'],2);s.path('M360 468 H550 V510',P['muted'],2)
  s.lines(164,559,[T('정형 실행 그래프','Typed graph',lang),T('입출력·의존성','Types and dependencies',lang)],24,36,'bold','middle')
  s.lines(550,559,[T('맞춤 코드','Custom code',lang),T('새 절차 + 기존 함수','New logic + existing tools',lang)],24,36,'bold','middle')
  s.path('M164 638 V680 H550 V638',P['muted'],2);s.line(360,680,360,722,P['muted'],2,arrow=True)
  s.panel(36,790,'B',T('검산 가능한 수치 도구를 실행','Run inspectable numeric tools',lang),648)
  ys=[898,1045,1192,1339]
  small_chain(s,121,ys[0]);s.lines(231,ys[0]-16,[T('구조·단위·판본 검사, 이완','Validate structure, units, version; relax',lang),T('후보 구조 R와 계산기 설정','Candidate R and calculator settings',lang)],24,34)
  for i in range(3):s.line(121,ys[i]+53,121,ys[i+1]-53,P['muted'],2,arrow=True)
  s.line(69,ys[1],171,ys[1],P['line'],2)
  for j,(dx,dy) in enumerate([(0,-24),(0,11),(40,-7)]):s.line(91+dx,ys[1]+dy,133+dx,ys[1]+dy,P['coral'],2,arrow=True)
  s.lines(231,ys[1]-16,[T('±변위의 힘 F(R±δ)','Forces at R±δ',lang),T('참조 힘과 독립 검증','Independent check against references',lang)],24,34)
  mini_matrix(s,57,ys[2]-36,1);s.lines(231,ys[2]-16,[T('힘상수 Φ/K → D','Force constants Φ/K → D',lang),T('질량·대칭·수렴을 확인','Check masses, symmetry and convergence',lang)],24,34)
  s.line(60,ys[3]+30,185,ys[3]+30,P['line'],1.2)
  for j,freq in enumerate(D['cases'][0]['all_normal_frequencies_THz']):s.line(73+j*31,ys[3]+30,73+j*31,ys[3]+30-max(freq/D['cases'][0]['frequency_THz']*76,2),P['teal'],8)
  s.text(73,ys[3]+56,'0',18,anchor='middle');s.text(121,ys[3]+88,'f (THz)',20,anchor='middle')
  s.lines(231,ys[3]-16,[T('고유값 → 진동수와 모드','Eigenvalues → frequencies and modes',lang),T('목표 물량의 오차를 판단','Assess errors in the requested observable',lang)],24,34)
  s.text(231,ys[3]+70,'0 · 4.178 · 4.178 · 5.909',23,'bold')
  s.panel(36,1510,'C',T('결과와 실패를 다음 실행에 남긴다','Retain results and failures for reuse',lang),648)
  check(s,48,1585);s.lines(94,1585,[T('성공: 구조·힘·힘상수·진동수','Success: structures, forces, Hessians, frequencies',lang),T('모델·단위·입력·코드·검증 기록','Model, units, inputs, code and validation',lang)],23,35,'bold')
  s.text(43,1721,'×',36,'bold coral');s.lines(94,1718,[T('실패: 오류 단계·입력·재시도 조건','Failure: stage, input and retry condition',lang),T('추가 참조 계산과 절차 수정으로 환류','Feed into new reference data and procedure changes',lang)],23,35)
  s.path('M620 1800 V1850 H105 V1816',P['teal'],2);s.text(360,1900,T('검증한 함수·판본·결과를 다시 사용','Reuse checked tools, versions and results',lang),24,'bold teal','middle')
  s.lines(36,1980,[T('개념 설계 · 수치 계산과 기획·분기 역할을 구별한다.','Conceptual design · planning and numerical execution are distinct.',lang)],21,30,'muted')
 else:
  s.panel(44,165,'A',T('사람이 질문과 물리적 기준을 정한다','People set the question and physical criteria',lang),1112)
  s.lines(44,233,[T('“이 결정의 진동을 검증해 달라”','“Validate this crystal’s vibrations”',lang),T('구조 · 전자 상태 · 모델 · 변위 · 허용 오차','Structure · state · model · tolerances',lang)],25,38,'bold')
  s.line(610,251,668,251,P['muted'],2,arrow=True)
  s.lines(714,231,[T('에이전트: 기획과 분기','Agent: planning and routing',lang),T('정형 그래프 또는 맞춤 코드','Typed graph or custom code',lang)],25,38,'bold teal')
  s.panel(44,369,'B',T('서로 보완하는 두 진입 경로','Two complementary entrances',lang),1112)
  s.lines(44,435,[T('정형 실행 그래프','Typed execution graph',lang),T('입출력 자료형과 의존성','Input/output types and dependencies',lang)],24,35,'bold')
  s.lines(654,435,[T('맞춤 코드','Custom code',lang),T('새 절차를 작성하고 기존 함수를 호출','New logic invokes existing functions',lang)],24,35,'bold')
  s.path('M282 496 V530 H913 V496',P['muted'],2);s.line(597,530,597,564,P['muted'],2,arrow=True)
  # Actual objects form a left-to-right pipeline: structure, forces, Hessian, spectrum.
  ys=663;xs=[150,439,730,1032]
  small_chain(s,xs[0],ys)
  for dx,dy in [(-30,-22),(-4,8),(22,-7)]:s.line(xs[1]+dx-16,ys+dy,xs[1]+dx+25,ys+dy,P['coral'],2.2,arrow=True)
  mini_matrix(s,xs[2]-62,ys-35)
  s.line(xs[3]-63,ys+39,xs[3]+63,ys+39,P['line'],1.2)
  for j,freq in enumerate(D['cases'][0]['all_normal_frequencies_THz']):s.line(xs[3]-49+j*33,ys+39,xs[3]-49+j*33,ys+39-max(freq/D['cases'][0]['frequency_THz']*83,2),P['teal'],9)
  s.text(xs[3]-49,ys+65,'0',18,anchor='middle')
  for i in range(3):s.line(xs[i]+84,ys,xs[i+1]-91,ys,P['muted'],2,arrow=True)
  labs=[[T('구조·판본·단위','Input, units, version',lang),T('이완과 입력 검사','Relax; check inputs',lang)],['F(R±δ)',T('힘의 독립 참조 검증','Reference-force check',lang)],['Φ/K → D',T('질량·대칭·변위 수렴','Mass, symmetry, step',lang)],[T('진동수·모드','Frequencies and modes',lang),'f (THz)']]
  for index,(x,lab) in enumerate(zip(xs,labs)):s.lines(x,756,lab,21 if lang=='en' else 22,34,f'bold stage-{index+1}','middle')
  s.text(xs[3],821,'0 · 4.178 · 4.178 · 5.909',17,'bold',anchor='middle')
  s.panel(44,864,'C',T('산출물과 실패 기록을 함께 보존한다','Retain artifacts and failure records',lang),1112)
  check(s,48,928);s.lines(94,926,[T('구조 · 힘 · 힘상수 · 진동수','Structures · forces · Hessians · frequencies',lang),T('모델·입력·코드·단위·검증 이력','Model, input, code, units, validation history',lang)],23,35,'bold')
  s.text(663,932,'×',35,'bold coral');s.lines(708,926,[T('실패 단계 · 입력 · 재시도 조건','Failure stage · input · retry condition',lang),T('추가 참조 자료와 절차 개선으로 환류','Feed back to data and procedure updates',lang)],23,35)
  s.path('M1110 1007 V1047 H106 V1008',P['teal'],2)
  s.text(598,1096,T('다음 연구에서 재사용: 검증한 함수 + 판본이 묶인 결과 + 개선한 절차','Reuse: checked tools, versioned results and improved procedures',lang),24,'bold teal','middle')
  s.text(44,1140,T('개념 설계 · Potente의 역할 분리를 참고해 진동 계산을 구체화했다.','Conceptual design · vibration workflow informed by Potente’s separation of roles.',lang),21,'muted')
 return s

def main():
 OUT.mkdir(parents=True,exist_ok=True);manifest=[]
 for i,fn in [(1,fig1),(2,fig2),(5,fig3)]:
  for lang in ['ko','en']:
   for mobile in [False,True]:
    s=fn(lang,mobile);name=f'fig{i}_{"mobile" if mobile else "desktop"}{"_en" if lang=="en" else ""}.svg';s.save(OUT/name)
    manifest.append({'file':name,'language':lang,'width':s.w,'height':s.h,'kind':'harmonic educational calculation' if i==2 else 'review-authored conceptual architecture'})
 (ROOT/'artifacts/figure-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'figures':len(manifest),'directory':'artifacts/figures'}))
if __name__=='__main__':main()
