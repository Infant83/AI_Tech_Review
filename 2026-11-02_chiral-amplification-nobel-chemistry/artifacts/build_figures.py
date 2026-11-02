"""Original bilingual educational SVGs and reproducible dimensionless toy data."""
from pathlib import Path
import html, json, math

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts'
DATA=ART/'data'
DATA.mkdir(exist_ok=True)
INK='#173442';GRAY='#5e7078';TEAL='#147382';RUST='#ad542d';PALE='#faf9f4';WASH='#edf3ef';LINE='#d1deda';OFF='#dfe3de'
NS='http://www.w3.org/2000/svg'
def esc(s):return html.escape(str(s),quote=True)

class SVG:
 def __init__(self,w,h,title,desc,meta):
  self.w=w;self.h=h
  self.p=[f'<svg xmlns="{NS}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{esc(title)}</title><desc id="desc">{esc(desc)}</desc><metadata>{esc(json.dumps(meta,ensure_ascii=False))}</metadata><style>text{{font-family:ReviewFigure,NanumGothic,sans-serif;fill:{INK}}}</style>',f'<rect width="{w}" height="{h}" rx="14" fill="{PALE}"/>']
 def text(self,x,y,t,size=20,color=INK,weight=400,anchor='start'):
  if self.w==680:size=max(size,24)
  self.p.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" style="fill:{color}">{esc(t)}</text>')
 def mathtext(self,x,y,markup,size=23):
  if self.w==680:size=max(size,24)
  self.p.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="700">{markup}</text>')
 def lines(self,x,y,items,size=20,step=31,**kw):
  for i,t in enumerate(items):self.text(x,y+i*step,t,size,**kw)
 def rect(self,x,y,w,h,fill=WASH,stroke=LINE,r=7):self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
 def line(self,x1,y1,x2,y2,color=LINE,width=1,dash=None):self.p.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def dot(self,x,y,r=5,color=RUST,fill=None):self.p.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" fill="{fill or color}" stroke="{color}" stroke-width="2"/>')
 def path(self,points,color=TEAL,width=3,dash=None):self.p.append('<path d="'+' '.join(('M' if i==0 else 'L')+f'{x:.3f},{y:.3f}' for i,(x,y) in enumerate(points))+f'" fill="none" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def arrow(self,x1,y1,x2,y2,color=GRAY):
  self.line(x1,y1,x2,y2,color,2)
  a=math.atan2(y2-y1,x2-x1)
  for d in [-.5,.5]:self.line(x2,y2,x2-11*math.cos(a+d),y2-11*math.sin(a+d),color,2)
 def save(self,name):(ART/name).write_text('\n'.join(self.p+['</svg>'])+'\n',encoding='utf-8')

def axes(s,x,y,w,h,xmax,ymax,xticks,yticks):
 fx=lambda v:x+w*v/xmax
 fy=lambda v:y+h-h*v/ymax
 for v,label in yticks:
  yy=fy(v);s.line(x,yy,x+w,yy);s.text(x-13,yy+7,label,17,GRAY,anchor='end')
 for v,label in xticks:
  xx=fx(v);s.line(xx,y+h,xx,y+h+7,INK);s.text(xx,y+h+32,label,17,GRAY,anchor='middle')
 s.line(x,y,x,y+h,INK,1.5);s.line(x,y+h,x+w,y+h,INK,1.5)
 return fx,fy

POOL=[{'ligand_ee':i/200,'active_ee':2*(i/200)/(1+(i/200)**2),'active_fraction':(1+(i/200)**2)/2} for i in range(201)]
assert abs(POOL[100]['active_ee']-.8)<1e-15
assert .75**2==.5625 and 2*.75*.25==.375 and .25**2==.0625

def pool(lang,mobile):
 ko=lang=='ko';w,h=(680,1540) if mobile else (1120,930)
 s=SVG(w,h,'작은 혼합 차이와 활성 집단' if ko else 'A small mixture bias and its active pool','Educational independent two-site pairing: R:S=75:25; RR=56.25%, RS+SR=37.5%, SS=6.25%. With inactive heterochiral pairs and equally active homochiral pairs, the active fraction is62.5%; its RR:SS composition is90:10 and ee80%. The curve is active-pool ee, E(e)=2e/(1+e^2).',{'kind':'review educational pairing model','assumptions':['independent random pairing','heterochiral pairs inactive','homochiral pairs equally active'],'fractions':{'RR':.5625,'RS_plus_SR':.375,'SS':.0625,'active':.625},'active_pool':{'RR':.9,'SS':.1,'ee':.8},'equation':'E(e)=2e/(1+e^2)','background_reference':'https://doi.org/10.1021/ja00269a036','derivation':'independent algebra under the specified educational assumptions'})
 s.text(30,45,'활성 집단에서 커지는 조성 편향' if ko else 'The active pool can carry a larger imbalance',28,weight=700)
 s.text(30,80,'무작위 짝지음의 이상적 교육 모형' if ko else 'An ideal educational model of random pairing',19,GRAY)
 bx,by,bw=(50,130,580) if mobile else (35,145,330)
 s.rect(bx,by,bw*.75,52,RUST,RUST,0);s.rect(bx+bw*.75,by,bw*.25,52,TEAL,TEAL,0)
 s.text(bx+bw*.375,by+34,'R 75%',22,'white',700,'middle');s.text(bx+bw*.875,by+34,'S 25%',22,'white',700,'middle')
 s.text(bx,by+95,'리간드 ee = 50%' if ko else 'Ligand ee = 50%',24,weight=700)
 gx,gy,gw=(140,310,400) if mobile else (445,130,340)
 if mobile:s.text(30,280,'두 자리를 독립적으로 채운 확률' if ko else 'Independent choices for the two sites',23,weight=700)
 else:s.text(gx,108,'두 자리의 독립 조합' if ko else 'Independent two-site pairing',20,weight=700)
 a=gw*.75;b=gw*.25
 for x,y,cw,ch,fill in [(gx,gy,a,a,'#f0d5c6'),(gx+a,gy,b,a,OFF),(gx,gy+a,a,b,OFF),(gx+a,gy+a,b,b,'#cee2e6')]:s.rect(x,y,cw,ch,fill,PALE,0)
 s.text(gx+a/2,gy+a/2-12,'RR',27,RUST,700,'middle');s.text(gx+a/2,gy+a/2+24,'56.25%',25,RUST,700,'middle')
 s.text(gx+a+b/2,gy+a/2,'RS',21,GRAY,700,'middle');s.text(gx+a/2,gy+a+b/2+7,'SR',21,GRAY,700,'middle')
 s.text(gx+a+b/2,gy+a+b/2-6,'SS',20,TEAL,700,'middle');s.text(gx+a+b/2,gy+a+b/2+22,'6.25%',17,TEAL,700,'middle')
 s.text(gx+gw/2,gy+gw+39,'RS + SR = 37.5%  ·  '+('비활성' if ko else 'inactive'),20,GRAY,anchor='middle')
 px,py=(120,805) if mobile else (830,145)
 s.text(px,py-28,'활성 집단 안에서' if ko else 'Within the active pool',23,weight=700)
 chip,gap=(68,22) if mobile else (39,7)
 for i in range(10):
  xx=px+(i%5)*(chip+gap);yy=py+(i//5)*(chip+gap);c=RUST if i<9 else TEAL;s.rect(xx,yy,chip,chip,c,c,5);s.text(xx+chip/2,yy+chip*.67,'RR' if i<9 else 'SS',21 if mobile else 17,'white',700,'middle')
 yy=py+2*(chip+gap)+21
 s.text(px,yy,'RR : SS = 90 : 10',27,weight=700)
 s.text(px,yy+41,'활성 집단 ee = 80%' if ko else 'Active-pool ee = 80%',24,RUST,700)
 if mobile:s.text(30,yy+92,'활성인 양은 전체 복합체의 62.5%' if ko else 'Active pairs are 62.5% of all complexes',23,GRAY)
 else:
  s.lines(35,315,['전체 중 활성인 양','62.5%','활성 집단의 조성 편향','ee 80%'] if ko else ['Active fraction of all pairs','62.5%','Imbalance within that pool','ee 80%'],22,37)
  s.arrow(375,195,425,195);s.arrow(792,225,818,225)
 x,y,cw,ch=(98,1190,535,205) if mobile else (100,565,680,225)
 s.text(x,y-33,'활성 집단의 이상적 ee 곡선' if ko else 'Ideal active-pool ee curve',22,weight=700)
 fx,fy=axes(s,x,y,cw,ch,100,100,[(0,'0'),(50,'50'),(100,'100')],[(0,'0'),(50,'50'),(100,'100')])
 s.path([(fx(0),fy(0)),(fx(100),fy(100))],GRAY,2,'7 6');s.path([(fx(v['ligand_ee']*100),fy(v['active_ee']*100)) for v in POOL],RUST,4)
 s.line(fx(50),fy(0),fx(50),fy(80),RUST,1.5,'4 5');s.dot(fx(50),fy(80),6,RUST)
 s.text(fx(50)-15,fy(80)-20,'50 → 80',20,RUST,700,anchor='end')
 s.text(x+cw/2,y+ch+68,'리간드 ee (%)' if ko else 'Ligand ee (%)',19,anchor='middle')
 s.text(x,y-65,'활성 집단 ee (%)' if ko else 'Active-pool ee (%)',18,GRAY)
 if mobile:
  s.text(30,1500,'곡선: E(e) = 2e/(1 + e²) · 교육 계산' if ko else 'E(e) = 2e/(1 + e²) · educational calculation',21,GRAY)
 else:
  s.lines(825,590,['E(e) = 2e/(1 + e²)','e = 0.5 → E = 0.8'] if ko else ['E(e) = 2e/(1 + e²)','e = 0.5 → E = 0.8'],23,39)
  s.lines(825,710,['실선: 이상적 활성 집단','점선: 선형 기준'] if ko else ['Solid: ideal active pool','Dashed: linear reference'],18,31,color=GRAY)
  s.text(30,910,'무작위 조합 · 이형 비활성 · 동형 동일 활성 · 활성 집단 조성의 교육 계산' if ko else 'Random pairing · inactive heterochiral pairs · equal homochiral activity · active-pool composition',16,GRAY)
 s.save(f'chiral_pool_{"mobile_" if mobile else ""}{lang}.svg')

def rhs(v,kappa):
 a,r,s,d=v;return(-a*(r+s),a*r-kappa*r*s,a*s-kappa*r*s,kappa*r*s)
def integrate(kappa,dt=.005,symmetric=False):
 v=[1,.05,.05,0] if symmetric else [1,.0505,.0495,0];n=round(25/dt);stride=round(.25/dt);out=[]
 for step in range(n+1):
  if step%stride==0:out.append({'tau':step*dt,'a':v[0],'r':v[1],'s':v[2],'d':v[3],'active':v[1]+v[2],'ee':(v[1]-v[2])/(v[1]+v[2])})
  if step==n:break
  k1=rhs(v,kappa);k2=rhs([v[i]+dt*k1[i]/2 for i in range(4)],kappa);k3=rhs([v[i]+dt*k2[i]/2 for i in range(4)],kappa);k4=rhs([v[i]+dt*k3[i] for i in range(4)],kappa)
  v=[v[i]+dt*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6 for i in range(4)]
  assert min(v)>-1e-12 and abs(v[0]+v[1]+v[2]+2*v[3]-1.1)<1e-10
 return out
FRANK={k:integrate(k) for k in [0,4]}
errors={k:max(abs(a[key]-b[key]) for a,b in zip(FRANK[k],integrate(k,.0025)) for key in ['a','r','s','d','ee']) for k in [0,4]}
assert max(errors.values())<1e-7
assert max(abs(v['ee']-.01) for v in FRANK[0])<1e-10
assert max(abs(v['ee']) for v in integrate(4,symmetric=True))<1e-15

def frank(lang,mobile):
 ko=lang=='ko';w,h=(680,1320) if mobile else (1120,970)
 meta={'kind':'review educational Frank-type closed-batch ODE','equations':['a_prime=-a*(r+s)','r_prime=a*r-kappa*r*s','s_prime=a*s-kappa*r*s','d_prime=kappa*r*s'],'time':'tau=k*[A]_0*t','concentrations':'normalized to initial substrate [A]_0','initial':{'a':1,'r':.0505,'s':.0495,'d':0,'ee':.01},'kappa':[0,4],'dt':.005,'step_halving_max_abs_error':errors,'conservation':'a+r+s+2d=1.1','theory_reference':'https://doi.org/10.1016/0006-3002(53)90082-1'}
 s=SVG(w,h,'자가촉매의 증가와 조성 증폭' if ko else 'Autocatalytic growth and compositional amplification','A dimensionless Frank-type closed-batch educational model compares kappa0 and4 from a=1,r=.0505,s=.0495,d=0. Autocatalysis alone preserves initial ee1%; mutual inhibition amplifies the free active-pool imbalance. The lower plot records free r+s. Exactly symmetric deterministic input retains ee0.',meta)
 s.text(30,45,'더 많이 만드는 일과, 비율을 바꾸는 일' if ko else 'Making more and changing the ratio',28,weight=700)
 s.text(30,80,'Frank형 최소 반응망 · 무차원 교육 계산' if ko else 'Minimal Frank-type network · nondimensional calculation',19,GRAY)
 if mobile:
  for i,(t,c) in enumerate([('A + R → 2R',RUST),('A + S → 2S',TEAL),('R + S → D',GRAY)]):s.rect(50,115+i*76,580,61);s.text(340,157+i*76,t,27,c,700,'middle')
  s.lines(30,380,['D: 비활성 생성물 · 두 방향의 같은 수를 소비' if ko else 'D: inactive product consuming one of each hand','a₀ = 1, r₀ = 0.0505, s₀ = 0.0495, d₀ = 0','초기 ee = 1% · κ = h/k' if ko else 'Initial ee = 1% · κ = h/k'],22,35)
  x,y,pw,ph=98,550,535,270
 else:
  for i,(t,c) in enumerate([('A + R → 2R',RUST),('A + S → 2S',TEAL),('R + S → D',GRAY)]):s.rect(30+i*365,120,330,90);s.text(195+i*365,177,t,28,c,700,'middle')
  s.text(30,249,'D: 두 거울상 단위를 하나씩 소비하는 비활성 생성물' if ko else 'D: an inactive product consuming one unit of each enantiomer',20,GRAY)
  x,y,pw,ph=105,340,680,280
 s.text(x,y-31,'자유 R·S의 ee (%)' if ko else 'ee of free R and S (%)',21,weight=700)
 fx,fy=axes(s,x,y,pw,ph,25,100,[(v,str(v)) for v in [0,5,10,15,20,25]],[(v,str(v)) for v in [0,50,100]])
 for k,c,dash in [(0,TEAL,'8 6'),(4,RUST,None)]:s.path([(fx(v['tau']),fy(v['ee']*100)) for v in FRANK[k]],c,4,dash)
 s.text(x+pw/2,y+ph+66,'무차원 시간 τ' if ko else 'Dimensionless time τ',19,anchor='middle')
 if mobile:
  s.text(30,485,'κ = 0: '+('자가촉매' if ko else 'autocatalysis'),22,TEAL,700);s.text(335,485,'κ = 4: '+('상호억제 추가' if ko else '+ inhibition'),22,RUST,700)
  ay,ah=990,140
 else:
  s.lines(835,351,['초기 ee = 1%','a₀ = 1','r₀ = 0.0505','s₀ = 0.0495','d₀ = 0','κ = h/k'] if ko else ['Initial ee = 1%','a₀ = 1','r₀ = 0.0505','s₀ = 0.0495','d₀ = 0','κ = h/k'],21,33)
  s.text(835,591,'κ = 0',23,TEAL,700);s.text(945,591,'κ = 4',23,RUST,700)
  ay,ah=750,120
 s.text(x,ay-30,'자유 활성체 양 r + s' if ko else 'Free active-species amount r + s',21,weight=700)
 ax,af=axes(s,x,ay,pw,ah,25,1.2,[(v,str(v)) for v in [0,10,20,25]],[(v,str(v)) for v in [0,.6,1.2]])
 for k,c,dash in [(0,TEAL,'8 6'),(4,RUST,None)]:s.path([(ax(v['tau']),af(v['active'])) for v in FRANK[k]],c,3,dash)
 if mobile:
  s.lines(30,1210,['농도: 초기 A = 1로 정규화 · τ = k[A]₀t' if ko else 'Concentrations scaled by initial A · τ = k[A]₀t','a + r + s + 2d = 1.1','대칭 초기값 r₀ = s₀이면 ee = 0 유지' if ko else 'Symmetric input r₀ = s₀ retains ee = 0'],21,34,color=GRAY)
 else:
  s.lines(835,741,['농도는 초기 A로 정규화','a + r + s + 2d = 1.1','대칭 초기값은 ee = 0 유지'] if ko else ['Concentrations scaled by initial A','a + r + s + 2d = 1.1','Symmetric input retains ee = 0'],17,32,color=GRAY)
  s.text(30,940,'τ = k[A]₀t · κ = h/k · 계수·초기조건을 정한 교육 반응망의 수치해' if ko else 'τ = k[A]₀t · κ = h/k · numerical solution of the specified educational reaction network',17,GRAY)
 s.save(f'frank_feedback_{"mobile_" if mobile else ""}{lang}.svg')

def optical(lang,mobile):
 ko=lang=='ko';w,h=(680,1480) if mobile else (1120,870)
 s=SVG(w,h,'사슬의 배열에서 원편광 전이로' if ko else 'From chain ordering to circular optical transitions','Conceptual chain arrangement and computational workflow based on PRL128,046401(2022): collective CDW ordering, a glide operation consisting of reflection plus translation, momentum matrix elements Pplus/minus=<psi_nk|px plus/minus i py|psi_mk>, and the normalized difference of their squared magnitudes for a chosen valence-to-conduction transition.',{'kind':'review explanatory chain-arrangement and computation diagram','primary_reference':'https://doi.org/10.1103/PhysRevLett.128.046401','operators':'momentum px plus/minus i py, as in the paper','bands':'m valence to n conduction','channels':'plus/minus; no viewing-direction assignment','eta':'(abs(Pplus)^2-abs(Pminus)^2)/(abs(Pplus)^2+abs(Pminus)^2)','domain':'positive denominator'})
 s.text(30,45,'고체의 배열을, 계산할 전이로 연결한다' if ko else 'Connect the ordered solid to a defined transition',28,weight=700)
 if mobile and not ko:s.lines(30,76,['Conceptual chain array · symmetry','Momentum matrix elements'],19,28,color=GRAY)
 else:s.text(30,80,'설명용 사슬 배열 · 대칭 · 운동량 행렬원소' if ko else 'Conceptual chain array · symmetry · momentum matrix elements',19,GRAY)
 boxes=[(30,120,620,280),(30,450,620,280),(30,780,620,250),(30,1080,620,300)] if mobile else [(30,130,495,305),(565,130,525,305),(30,500,640,275),(710,500,380,275)]
 x,y,bw,bh=boxes[0];s.rect(x,y,bw,bh);s.text(x+20,y+38,'1  사슬 사이의 집단적 배열' if ko else '1  Collective ordering between chains',23,weight=700)
 for row in range(4):
  yy=y+85+row*38;s.line(x+45,yy,x+bw-40,yy,LINE,2)
  for j in range(9):
   xx=x+55+j*(bw-110)/8+(8 if (j+row)%3==0 else -4);s.dot(xx,yy,5,RUST if row%2==0 else TEAL)
 s.text(x+20,y+bh-19,'원자 좌표와 사슬 질서의 순서를 정한다' if ko else 'Specify coordinates and the order between chains',17,GRAY)
 x,y,bw,bh=boxes[1];s.rect(x,y,bw,bh);s.text(x+20,y+38,'2  미끄럼 반사를 시험한다' if ko else '2  Test a glide-mirror operation',23,weight=700)
 axis=y+bh*.51;s.line(x+30,axis,x+bw-30,axis,GRAY,1.5,'6 6')
 ox=x+bw*.24;ty=axis+65;tx=x+bw*.69;s.dot(ox,axis-65,9,RUST);s.dot(ox,ty,9,GRAY,PALE);s.dot(tx,ty,9,RUST)
 s.arrow(ox,axis-49,ox,ty-16);s.arrow(ox+18,ty,tx-18,ty)
 s.text(x+bw*.44,axis-17,'반사' if ko else 'Reflect',18,GRAY,'400','middle');s.text((ox+tx)/2,ty+(24 if mobile else 36),'일정 거리 이동' if ko else 'Translate',18,GRAY,anchor='middle')
 s.text(x+20,y+bh-19,'동작 뒤 전체 배열과 겹치는지 확인' if ko else 'Compare the transformed whole arrangement',17,GRAY)
 x,y,bw,bh=boxes[2];s.rect(x,y,bw,bh);s.text(x+20,y+38,'3  DFT 상태에서 전이를 계산한다' if ko else '3  Evaluate transitions between DFT states',23,weight=700)
 s.text(x+20,y+83,'m: 가전자 상태 → n: 전도 상태' if ko else 'm: valence state → n: conduction state',19,GRAY)
 s.mathtext(x+20,y+129,'P±(k) = ⟨ψ<tspan baseline-shift="sub" font-size="70%">nk</tspan> | p<tspan baseline-shift="sub" font-size="70%">x</tspan> ± i p<tspan baseline-shift="sub" font-size="70%">y</tspan> | ψ<tspan baseline-shift="sub" font-size="70%">mk</tspan>⟩')
 s.text(x+20,y+(168 if mobile else 177),'두 채널의 전이 강도: |P₊|², |P₋|²' if ko else 'Transition strengths: |P₊|² and |P₋|²',21)
 if mobile and not ko:s.lines(x+20,y+bh-48,['+ / − channels: the paper’s','momentum-operator definition'],16,28,color=GRAY)
 else:s.text(x+20,y+bh-20,'+ / − 채널: 원논문의 운동량 연산자 정의' if ko else '+ / − channels: the paper’s momentum-operator definition',16,GRAY)
 x,y,bw,bh=boxes[3];s.rect(x,y,bw,bh);s.text(x+20,y+38,'4  k별 선택성을 비교한다' if ko else '4  Compare selectivity at k',23,weight=700)
 s.text(x+20,y+105,'η(k) =',26,weight=700);fc=x+bw*.68;half=105 if not mobile else 155
 s.text(fc,y+86,'|P₊|² − |P₋|²',23,weight=700,anchor='middle');s.line(fc-half,y+98,fc+half,y+98,INK,1.6);s.text(fc,y+133,'|P₊|² + |P₋|²',23,weight=700,anchor='middle')
 s.lines(x+20,y+190,['η > 0: + 채널이 더 강함','분모가 양수인 전이에서 정의'] if ko else ['η > 0: stronger + channel','Defined for a positive denominator'],19,32,color=GRAY)
 if mobile:
  s.arrow(340,410,340,440);s.arrow(340,740,340,770);s.arrow(340,1040,340,1070)
  s.lines(30,1424,['CDW 집단 배열과 계산 대상의 설명용 개념도' if ko else 'A conceptual map of CDW ordering and the calculation','PRL 128, 046401 (2022) · 단일 m → n 전이' if ko else 'PRL 128, 046401 (2022) · one m → n transition'],21,33,color=GRAY)
 else:
  s.arrow(530,280,558,280);s.line(827,444,827,465,GRAY,2);s.line(827,465,350,465,GRAY,2);s.arrow(350,465,350,490);s.arrow(676,634,702,634)
  s.text(30,833,'설명용 CDW 사슬 배열과 계산 관계 · PRL 128, 046401 (2022)의 단일 전이 정의' if ko else 'Conceptual CDW chain ordering and computational relations · single-transition definition, PRL128,046401(2022)',17,GRAY)
 s.save(f'optical_selectivity_{"mobile_" if mobile else ""}{lang}.svg')

for lang in ['ko','en']:
 for mobile in [False,True]:pool(lang,mobile);frank(lang,mobile);optical(lang,mobile)
(DATA/'pairing-model.json').write_text(json.dumps({'assumptions':['independent pairing','inactive heterochiral pairs','equally active homochiral pairs'],'input_R_fraction':.75,'input_S_fraction':.25,'active_fraction':.625,'active_RR_fraction':.9,'active_SS_fraction':.1,'curve':POOL},indent=2)+'\n')
(DATA/'frank-model.json').write_text(json.dumps({'model':'nondimensional closed-batch educational Frank-type network','initial':{'a':1,'r':.0505,'s':.0495,'d':0},'dt':.005,'halved_dt':.0025,'max_abs_step_halving_error':errors,'conservation':'a+r+s+2d=1.1','curves':FRANK},indent=2)+'\n')
(DATA/'figure-provenance.json').write_text(json.dumps({'date':'2026-11-02','figures':['chiral_pool','frank_feedback','optical_selectivity'],'pairing':'review algebraic model, not experimental product ee','frank':'review nondimensional numerical calculation with stated parameters','optical':'conceptual chain arrangement and PRL2022 momentum-matrix-element definition','original_research_code_execution':False},indent=2)+'\n')
print(json.dumps({'svg_files':12,'pool_50_to_80':POOL[100],'frank_step_halving_max_error':errors,'frank_tau20':{k:FRANK[k][80] for k in FRANK}},ensure_ascii=False))
