"""Original bilingual teaching diagrams; not a rerun of the JUPITER simulation.

Usage: python artifacts/build_figures.py --font /path/to/openly-licensed-Korean.ttf
SVG text is outlined. Source fonts are external build inputs; the retained OFL
is shipped with the HTML's locally subset text fonts. Figures do not reproduce
source circuit layouts, noise rates, performance curves or proprietary data.
"""
from pathlib import Path
import argparse, csv, json, math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle, Arc

OUT=Path(__file__).resolve().parent
INK='#172f3b';MUTED='#526870';TEAL='#126a72';GOLD='#b77c28';RED='#ae4a42';BG='#faf9f5';WASH='#eaf1ec';LINE='#cddbd4';BLUE='#42699b'
FONT=None

def tx(ax,x,y,s,size=15,color=INK,ha='left',va='center',weight='normal',**kw):
 s=s.replace('↻','reuse').replace('|0⟩',r'$|0\rangle$').replace('|1⟩',r'$|1\rangle$').replace('|2⟩',r'$|2\rangle$').replace('|T⟩',r'$|T\rangle$').replace('|ψ⟩',r'$|\psi\rangle$').replace('θ',r'$\theta$')
 return ax.text(x,y,s,fontsize=size,color=color,ha=ha,va=va,fontproperties=FONT,weight=weight,**kw)
def box(ax,x,y,w,h,color=WASH,edge=LINE,lw=1.3,rad=.018,**kw):
 p=FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad=0.008,rounding_size={rad}',facecolor=color,edgecolor=edge,linewidth=lw,**kw);ax.add_patch(p);return p
def arrow(ax,x1,y1,x2,y2,color=TEAL,scale=18,style='-|>',lw=1.8,**kw):
 p=FancyArrowPatch((x1,y1),(x2,y2),arrowstyle=style,mutation_scale=scale,color=color,linewidth=lw,**kw);ax.add_patch(p);return p
def canvas(width,height):
 fig=plt.figure(figsize=(width,height),facecolor=BG);ax=fig.add_axes([0,0,1,1]);ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');return fig,ax

def save(fig,name,lang,mobile):
 target=OUT/f'{name}{"_mobile" if mobile else ""}_{lang}.svg'
 fig.canvas.draw()
 renderer=fig.canvas.get_renderer();bounds=fig.bbox
 for item in fig.findobj(matplotlib.text.Text):
  if not item.get_visible() or not item.get_text():continue
  rect=item.get_window_extent(renderer)
  if rect.width and rect.height and (rect.x0 < -1 or rect.y0 < -1 or rect.x1 > bounds.width+1 or rect.y1 > bounds.height+1):
   raise ValueError(f'Figure text exceeds canvas in {target.name}: {item.get_text()}')
 fig.savefig(target,format='svg',facecolor=BG,metadata={'Date':None,'Creator':'Original AI Tech Review teaching diagram; matplotlib'})
 target.write_text('\n'.join(line.rstrip() for line in target.read_text().splitlines())+'\n')
 qa=OUT.parent/'tmp'/'figures';qa.mkdir(parents=True,exist_ok=True)
 fig.savefig(qa/(target.stem+'.png'),dpi=110,facecolor=BG)
 plt.close(fig)

def memory(lang,mobile):
 ko=lang=='ko';fig,ax=canvas(6,14.5) if mobile else canvas(12,7.6)
 title=('104개의 위치와 45비트는 서로 다른 수' if ko else ('104 positions and 45 bits\ncount different things' if mobile else '104 positions and 45 bits count different things'))
 tx(ax,.055,.963,title,size=20 if mobile else 23,va='top',weight='bold')
 tx(ax,.055,.895 if mobile else .90,('메모리는 동시 라이브 상태의 기저 크기로 결정된다.' if ko else 'Memory follows the basis size of the live encoded state.'),size=14 if mobile else 14,va='top',color=MUTED)
 if mobile:
  stages=[(.07,.76,.86,.10),(.07,.61,.86,.10),(.07,.46,.86,.10)]
 else:stages=[(.055,.635,.27,.18),(.365,.635,.27,.18),(.675,.635,.27,.18)]
 labels=[('프로토콜 전체' if ko else 'Across the protocol','104', '데이터 + 보조 물리 위치' if ko else 'data + auxiliary physical positions'),('라이브 상태 관리' if ko else 'Manage the live state','↻','측정 · release · 재사용 · 재배치' if ko else 'measure · release · reuse · reorder'),('인코딩한 라이브 레지스터' if ko else 'Encoded live register','45 bits','큐비트·선택한 큐트리트의 이진 저장' if ko else 'binary storage of qubits + selected qutrits')]
 for i,((x,y,w,h),(a,b,c)) in enumerate(zip(stages,labels)):
  box(ax,x,y,w,h,edge=TEAL if i==2 else LINE)
  tx(ax,x+w/2,y+h*.81,a,size=15 if mobile else 13,ha='center',color=TEAL)
  tx(ax,x+w/2,y+h*.51,b,size=25 if mobile else 28,ha='center',weight='bold')
  tx(ax,x+w/2,y+h*.19,c,size=12.5 if mobile else 11.5,ha='center',color=MUTED)
  if i<2:
   nx,ny,nw,nh=stages[i+1]
   if mobile:arrow(ax,.5,y-.008,.5,ny+nh+.012)
   else:arrow(ax,x+w+.012,y+h/2,nx-.012,ny+nh/2)
 tx(ax,.07 if mobile else .055,.425 if mobile else .59,((('104개를 동시에 저장한\n일반 상태벡터라는 뜻이 아니다.' if ko else 'Not a general state vector of\n104 simultaneous qubits.') if mobile else ('위치 수를 압축한 45개의 물리 큐비트라는 뜻이 아니다.' if ko else 'This is not 104 simultaneous physical qubits compressed into 45.'))),size=12.5,color=MUTED,va='top')
 if mobile:
  plot=fig.add_axes([.14,.165,.77,.19]);qbox=(.07,.012,.86,.06)
 else:
  plot=fig.add_axes([.09,.15,.52,.335]);qbox=(.675,.16,.27,.325)
 ns=np.linspace(39,51,160);ys=2.**(ns-36)
 plot.plot(ns,ys,color=TEAL,lw=2.5)
 plot.set_yscale('log',base=2);plot.set_xlim(39,51);plot.set_ylim(8,32768)
 plot.spines[['top','right']].set_visible(False);plot.spines[['bottom','left']].set_color(LINE)
 plot.set_facecolor(BG);plot.grid(axis='y',color=LINE,lw=.8,zorder=0)
 plot.set_xticks([40,45,50]);plot.set_yticks([16,512,16384],['16 TiB','512 TiB','16 PiB'])
 plot.tick_params(labelsize=13 if mobile else 12,color=LINE)
 plot.set_xlabel('n (encoded binary bits)',fontsize=12 if mobile else 12,labelpad=8)
 plot.set_title(r'$M(n)=16\times2^n\ \mathrm{bytes}$'+'\n'+('complex128 상태벡터만' if ko else 'complex128 state vector only'),fontproperties=FONT,fontsize=14,pad=11,color=INK)
 for n in [40,45,50]:plot.scatter([n],[2**(n-36)],s=45,color=GOLD if n==45 else TEAL,zorder=4)
 plot.annotate('45 → 512 TiB',xy=(45,512),xytext=(40,2000),fontsize=12,color=GOLD,arrowprops={'arrowstyle':'-','color':GOLD})
 x,y,w,h=qbox;box(ax,x,y,w,h)
 if mobile:
  tx(ax,x+.025,y+h*.73,('교육용 인코딩 예시' if ko else 'Illustrative encoding example'),size=14,color=TEAL)
  tx(ax,x+.025,y+h*.39,r'$5\ \mathrm{qutrits}:\quad3^5=243\leq2^8=256$',size=15)
  tx(ax,x+.025,y+h*.09,('실제 45비트의 구성 비율은 비공개.' if ko else 'The actual 45-bit decomposition is undisclosed.'),size=12,color=MUTED)
 else:
  tx(ax,x+w/2,y+h*.88,('큐트리트 인코딩 예시' if ko else 'Qutrit encoding example'),size=14,ha='center',color=TEAL)
  for i,st in enumerate(['|0⟩','|1⟩','|2⟩']):
   yy=y+h*(.72-i*.105);ax.plot([x+.05,x+.105],[yy,yy],color=BLUE,lw=2);tx(ax,x+.12,yy,st,size=13)
  tx(ax,x+w/2,y+h*.31,r'$3^5=243\leq2^8=256$',size=16,ha='center')
  tx(ax,x+w/2,y+h*.16,('5큐트리트 → 8 이진 비트' if ko else '5 qutrits → 8 binary bits'),size=12.5,ha='center')
  tx(ax,x+w/2,y+h*.055,('45비트의 실제 구성은 비공개' if ko else 'Actual 45-bit split undisclosed'),size=11,ha='center',color=MUTED)
 tx(ax,.055,.12 if mobile else .065,((('원문 수치: 104 위치 · 45비트 · 512 TiB.\n곡선은 독립 교육용 계산.' if ko else 'Reported: 104 positions · 45 bits · 512 TiB.\nCurve: independent teaching calculation.') if mobile else ('원문 수치: 104 위치 · 45비트 · 512 TiB. 곡선은 독립 교육용 계산.' if ko else 'Reported: 104 positions · 45 bits · 512 TiB. Curve: independent teaching calculation.'))),size=11.5 if mobile else 12,color=MUTED,va='top')
 save(fig,'memory_register',lang,mobile)

def code_patch(ax,cx,cy,r,large=False):
 # Deliberately generic patch motif; no gate schedule or source geometry is claimed.
 if not large:
  coords=[(0,1),(-.65,.15),(.65,.15),(-1,-.8),(0,-.8),(1,-.8),(0,-.2)]
 else:coords=[(a,b) for a in [-1,-.34,.34,1] for b in [-.8,-.27,.27,.8]]
 for a,b in coords:
  ax.add_patch(Circle((cx+a*r,cy+b*r),r*.12,facecolor=TEAL if b>.05 else BLUE,edgecolor='none'))
 for i in range(len(coords)-1):
  a,b=coords[i];c,d=coords[i+1]
  if math.hypot(a-c,b-d)<1.5:ax.plot([cx+a*r,cx+c*r],[cy+b*r,cy+d*r],color=LINE,lw=1,zorder=0)

def cultivation(lang,mobile):
 ko=lang=='ko';fig,ax=canvas(6,13.5) if mobile else canvas(12,7.5)
 tx(ax,.055,.963,('고품질 매직상태를 얻는 경로' if ko else ('The path toward a\nhigh-quality magic state' if mobile else 'The path toward a high-quality magic state')),size=20 if mobile else 23,weight='bold',va='top')
 tx(ax,.055,.89 if mobile else .90,('검사 결과에 조건을 걸어 채택할 실행을 고른다.' if ko else 'Condition acceptance on the measured check outcomes.'),size=14,color=MUTED,va='top')
 if mobile:stages=[(.08,.74,.84,.105),(.08,.575,.84,.105),(.08,.41,.84,.105),(.08,.245,.84,.105)]
 else:stages=[(.055,.48,.2,.325),(.285,.48,.2,.325),(.515,.48,.2,.325),(.745,.48,.2,.325)]
 headings=[('작은 코드에서 시작' if ko else 'Start in a small code'),('추가 flag 검사' if ko else 'Additional flag checks'),('큰 코드로 확장' if ko else 'Grow the code'),('오류 정정·읽기' if ko else 'Correction and readout')]
 subs=[('d=3 색 코드' if ko else 'd=3 color code'),('검사 이력·조건부 채택' if ko else 'check record and acceptance'),('d=7 혼합 코드' if ko else 'd=7 hybrid code'),('라운드 반복·최종 관측' if ko else ('repeated rounds, final observables' if mobile else 'repeated rounds,\nfinal observables'))]
 for i,(x,y,w,h) in enumerate(stages):
  box(ax,x,y,w,h)
  if mobile:
   tx(ax,x+.025,y+h*.76,headings[i],size=16,color=TEAL,weight='bold')
   tx(ax,x+.025,y+h*.35,subs[i],size=14)
   iconx=x+w*.83;icony=y+h*.49;r=.032
  else:
   tx(ax,x+w/2,y+h*.85,headings[i],size=13,ha='center',color=TEAL,weight='bold')
   tx(ax,x+w/2,y+h*.15,subs[i],size=11.5,ha='center')
   iconx=x+w*.5;icony=y+h*.50;r=.043
  if i in [0,2]:code_patch(ax,iconx,icony,r,large=i==2)
  else:
   ax.add_patch(Arc((iconx,icony),r*2,r*1.6,theta1=0,theta2=180,edgecolor=BLUE,lw=2))
   ax.plot([iconx-r,iconx+r],[icony,icony],color=BLUE,lw=1.5);arrow(ax,iconx,icony,iconx+r*.55,icony+r*.55,color=BLUE,scale=10,lw=1.5)
   if i==1:tx(ax,iconx,icony-r*.5,'flag',size=11,ha='center',color=BLUE)
  if i<3:
   nx,ny,nw,nh=stages[i+1]
   if mobile:arrow(ax,.5,y-.009,.5,ny+nh+.014)
   else:arrow(ax,x+w+.009,y+h*.5,nx-.009,ny+nh*.5)
 if mobile:
  tx(ax,.10,.21,('不채택 검사 결과 → 폐기·재시도'.replace('不','비') if ko else 'Rejected record → discard and retry'),size=13,color=RED)
  liney=.177;foottop=.142
 else:
  arrow(ax,.385,.47,.385,.398,color=RED);arrow(ax,.845,.47,.845,.398,color=RED)
  ax.plot([.385,.845],[.398,.398],color=RED,lw=1.4)
  tx(ax,.615,.352,('비채택 검사 이력 → 폐기·재시도 (배양의 개념)' if ko else 'Rejected check record → discard and retry (cultivation concept)'),size=13,color=RED,ha='center')
  liney=.29;foottop=.18
 ax.plot([.055,.945],[liney,liney],color=LINE,lw=1.4,ls=(0,(4,4)))
 tx(ax,.055,liney-.018,((('아래: 채택 자원의 사용 개념\n이번 모사의 측정 범위 밖' if ko else 'Below: downstream resource use;\noutside this simulation’s reported scope') if mobile else ('아래: 채택한 자원의 사용 개념 · 이번 모사의 측정 범위 밖' if ko else 'Below: downstream resource use · outside this simulation’s reported scope'))),size=12,color=MUTED,va='top')
 if mobile:
  tx(ax,.09,.107,('|T⟩  +  데이터 |ψ⟩' if ko else '|T⟩  +  data |ψ⟩'),size=17,color=TEAL)
  arrow(ax,.1,.077,.21,.077);tx(ax,.25,.077,('Clifford·측정·피드포워드' if ko else 'Clifford, measure, feedforward'),size=13)
  tx(ax,.70,.052,'T|ψ⟩',size=21,color=GOLD)
 else:
  tx(ax,.075,foottop,'|T⟩',size=25,color=GOLD);tx(ax,.075,foottop-.063,'|ψ⟩',size=25,color=TEAL)
  arrow(ax,.165,foottop-.025,.29,foottop-.025)
  box(ax,.32,foottop-.086,.37,.12)
  tx(ax,.505,foottop-.026,('Clifford 게이트 · 측정 · 피드포워드' if ko else 'Clifford gates · measurement · feedforward'),size=13,ha='center')
  arrow(ax,.71,foottop-.025,.82,foottop-.025);tx(ax,.85,foottop-.025,'T|ψ⟩',size=25,color=GOLD)
 tx(ax,.055,.007 if mobile else .035,((('원본 설명도: 패치·경로는 개념 표현이며\n정확한 회로 배치가 아니다.' if ko else 'Original explanatory schematic; patch motifs and paths\nare not the exact circuit layout.') if mobile else ('원본 설명도: 코드 패치·경로는 개념 표현이며 정확한 회로 배치가 아니다.' if ko else 'Original explanatory schematic; patch motifs and paths are not the exact circuit layout.'))),size=10.5 if mobile else 12,color=MUTED,va='bottom')
 save(fig,'cultivation_flow',lang,mobile)

def phase_panel(ax,x,y,w,h,ko,mobile):
 tx(ax,x+.03,y+h*.91,('위상 오차: 진폭을 회전' if ko else 'Phase error: rotate amplitudes'),size=16 if mobile else 14,color=TEAL,weight='bold')
 cx=x+w*.5;cy=y+h*.54;rx=w*.25;ry=h*.22
 # Unit circle in the complex phase plane; not a Bloch sphere measurement.
 th=np.linspace(0,2*np.pi,200);ax.plot(cx+rx*np.cos(th),cy+ry*np.sin(th),color=LINE,lw=1.5)
 ax.plot([cx-rx*1.18,cx+rx*1.18],[cy,cy],color=LINE,lw=1);ax.plot([cx,cx],[cy-ry*1.18,cy+ry*1.18],color=LINE,lw=1)
 arrow(ax,cx,cy,cx+rx*.93,cy,color=BLUE);arrow(ax,cx,cy,cx+rx*np.cos(.9)*.93,cy+ry*np.sin(.9)*.93,color=RED)
 a=np.linspace(0,.9,50);ax.plot(cx+rx*.5*np.cos(a),cy+ry*.5*np.sin(a),color=GOLD,lw=2)
 tx(ax,cx+rx*.7,cy+ry*.38,r'$\theta$',size=18,color=GOLD)
 tx(ax,x+w*.5,y+h*.20,r'$R_z(\theta)=e^{-i\theta Z/2}$',size=17,ha='center')
 tx(ax,x+w*.5,y+h*.065,('진폭의 상대 위상 · 누적과 간섭' if ko else 'relative phase · accumulation and interference'),size=12.5 if mobile else 11.8,ha='center',color=MUTED)

def pauli_panel(ax,x,y,w,h,ko,mobile):
 tx(ax,x+.03,y+h*.91,('확률적 Pauli: 채널의 혼합' if ko else 'Stochastic Pauli: mix channels'),size=16 if mobile else 14,color=TEAL,weight='bold')
 xx=x+w*.23;yy=y+h*.56
 tx(ax,xx,yy,r'$\rho$',size=29,ha='center');arrow(ax,xx+w*.08,yy,x+w*.51,y+h*.70,color=BLUE);arrow(ax,xx+w*.08,yy,x+w*.51,y+h*.42,color=BLUE)
 tx(ax,x+w*.73,y+h*.70,r'$\rho$',size=23,ha='center');tx(ax,x+w*.73,y+h*.42,r'$Z\rho Z$',size=23,ha='center')
 tx(ax,x+w*.46,y+h*.79,r'$1-p$',size=13,color=MUTED);tx(ax,x+w*.46,y+h*.32,r'$p$',size=13,color=MUTED)
 tx(ax,x+w*.5,y+h*.20,r'$\mathcal{E}(\rho)=(1-p)\rho+pZ\rho Z$',size=14 if mobile else 12.4,ha='center')
 tx(ax,x+w*.5,y+h*.065,('단일 회전과 다른 밀도행렬 변환' if ko else 'a different density-matrix transformation'),size=12.5 if mobile else 11.5,ha='center',color=MUTED)

def leakage_panel(ax,x,y,w,h,ko,mobile):
 tx(ax,x+.03,y+h*.91,('누설: 계산 부분공간 밖으로' if ko else 'Leakage: leave the qubit subspace'),size=16 if mobile else 14,color=TEAL,weight='bold')
 left=x+w*.29;right=x+w*.73
 y0=y+h*.30;y1=y+h*.50;y2=y+h*.73
 box(ax,left-.045,y0-h*.08,right-left+.09,y1-y0+h*.16,color='#e3ede8',edge=TEAL)
 for yy,st,col in [(y0,r'$|0\rangle$',TEAL),(y1,r'$|1\rangle$',TEAL),(y2,r'$|2\rangle$',RED)]:
  ax.plot([left,right],[yy,yy],color=col,lw=2);tx(ax,right+.025,yy,st,size=17,color=col)
 arrow(ax,left+w*.10,y1+.013,left+w*.10,y2-.01,color=RED,style='<->',scale=15)
 tx(ax,left-.08,y2,'E',size=12,color=MUTED);arrow(ax,left-.08,y0,left-.08,y2-.02,color=MUTED,scale=10,lw=1)
 tx(ax,x+w*.5,y+h*.13,('회색·초록 영역: |0⟩, |1⟩' if ko else 'shaded region: |0⟩, |1⟩'),size=12.5 if mobile else 11.8,ha='center',color=MUTED)
 tx(ax,x+w*.5,y+h*.045,('세 번째 준위는 비계산 상태' if ko else 'the third level is noncomputational'),size=12.5 if mobile else 11.8,ha='center',color=MUTED)

def noise(lang,mobile):
 ko=lang=='ko';fig,ax=canvas(6,13.7) if mobile else canvas(12,6.7)
 tx(ax,.055,.963,(('결맞는 위상 오차와 확률적 Z 오차,\n그리고 누설' if mobile else '결맞는 위상 오차·확률적 Z 오차·누설') if ko else ('Coherent phase errors,\nstochastic Z errors and leakage' if mobile else 'Coherent phase errors, stochastic Z errors and leakage')),size=20 if mobile else 23,weight='bold',va='top')
 tx(ax,.055,.89 if mobile else .89,('위상 정보와 세 번째 에너지 준위가 중요한 이유' if ko else 'Why relative phases and the third energy level matter'),size=14,color=MUTED,va='top')
 if mobile:panels=[(.055,.632,.89,.23),(.055,.358,.89,.23),(.055,.084,.89,.23)]
 else:panels=[(.045,.20,.29,.59),(.355,.20,.29,.59),(.665,.20,.29,.59)]
 for fn,(x,y,w,h) in zip([phase_panel,pauli_panel,leakage_panel],panels):
  box(ax,x,y,w,h);fn(ax,x,y,w,h,ko,mobile)
 note=('교육용 일반 모형이다. θ·p·누설 전이는 실제 실행의 채널·비율을 뜻하지 않는다.' if ko else 'Generic teaching models. θ, p and the leakage arrow are not the run’s actual channel parameters.')
 tx(ax,.055,.045 if mobile else .11,note if not mobile else (('교육용 일반 모형: θ·p·누설 전이는\n실제 실행의 채널·비율을 뜻하지 않는다.' if ko else 'Generic teaching models: θ, p and leakage arrows\nare not the run’s actual channel parameters.')),size=12 if mobile else 12.5,color=MUTED,va='top')
 save(fig,'noise_channels',lang,mobile)

def main():
 global FONT
 p=argparse.ArgumentParser();p.add_argument('--font',type=Path,required=True);a=p.parse_args()
 if not a.font.is_file():raise FileNotFoundError(a.font)
 FONT=FontProperties(fname=str(a.font))
 plt.rcParams.update({'svg.fonttype':'path','svg.hashsalt':'jupiter-review-2026-10-20','mathtext.fontset':'dejavusans','axes.unicode_minus':False,'font.family':'DejaVu Sans'})
 for lang in ['ko','en']:
  for mobile in [False,True]:
   memory(lang,mobile);cultivation(lang,mobile);noise(lang,mobile)
 values=[{'encoded_bits':n,'complex_amplitudes':2**n,'bytes_per_complex_amplitude':16,'state_bytes':16*2**n,'state_TiB':2**(n-36)} for n in [40,45,50]]
 (OUT/'memory_teaching_values.json').write_text(json.dumps({'basis':'Independent state-vector memory calculation, complex128; excludes workspace, communication buffers and runtime overhead. Not measured allocation.','values':values},indent=2)+'\n')
 with (OUT/'memory_teaching_values.csv').open('w',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=values[0],lineterminator='\n');wr.writeheader();wr.writerows(values)
 print('Created 12 outlined bilingual/responsive SVG diagrams and teaching-memory values.')
if __name__=='__main__':main()
