"""Redraw cited public values and a stated two-level teaching model; no research code runs."""
from pathlib import Path
import csv, hashlib, html, json, shutil

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts'
INK='#18323c'; TEAL='#116a73'; RUST='#a8512b'; GRAY='#566971'; LINE='#d4dfda'; WASH='#f0f5f2'; PAPER='#fffefa'
DATA_URL='https://borealisdata.ca/api/access/datafile/1022680?format=original'
BOREALIS='https://doi.org/10.5683/SP3/UAKARI'
JCCM='https://github.com/akhmerov/papers-to-end-all-papers/blob/0b55e3424559c12f98718185cca87ba42424ddbd/review/data/aggregates.json'

def esc(x): return html.escape(str(x),quote=True)
class SVG:
 def __init__(self,w,h,title,desc,source):
  self.w=w;self.h=h
  self.p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{esc(title)}</title><desc id="desc">{esc(desc)}</desc><metadata>{esc(json.dumps(source,ensure_ascii=False))}</metadata><style>text{{font-family:ReviewFigure,NanumGothic,sans-serif;fill:{INK}}}.muted{{fill:{GRAY}}}.teal{{fill:{TEAL}}}.rust{{fill:{RUST}}}</style>',f'<rect width="{w}" height="{h}" rx="16" fill="{PAPER}"/>']
 def text(self,x,y,s,size=20,color=INK,weight=400,anchor='start'):
  if self.w==680:size=max(size,24)
  self.p.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" style="fill:{color}">{esc(s)}</text>')
 def lines(self,x,y,lines,size=20,step=30,**kw):
  for i,s in enumerate(lines): self.text(x,y+i*step,s,size,**kw)
 def line(self,x1,y1,x2,y2,color=LINE,width=1,dash=None):
  self.p.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def rect(self,x,y,w,h,fill=WASH,stroke=LINE,r=8): self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')
 def dot(self,x,y,r=5,color=RUST,fill=None): self.p.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" fill="{fill or color}" stroke="{color}" stroke-width="2"/>')
 def path(self,pts,color=TEAL,width=3,dash=None):
  self.p.append('<path d="'+' '.join(('M' if i==0 else 'L')+f'{x:.3f},{y:.3f}' for i,(x,y) in enumerate(pts))+f'" fill="none" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def save(self,name):
  p=ART/name;p.write_text('\n'.join(self.p+['</svg>'])+'\n',encoding='utf-8');return p

def axes(s,x,y,w,h,xmin,xmax,ymin,ymax,xticks,yticks):
 def fx(v):return x+(v-xmin)/(xmax-xmin)*w
 def fy(v):return y+h-(v-ymin)/(ymax-ymin)*h
 for v,label in yticks:
  yy=fy(v);s.line(x,yy,x+w,yy);s.text(x-14,yy+5,label,16,GRAY,anchor='end')
 for v,label in xticks:
  xx=fx(v);s.line(xx,y+h,xx,y+h+6,INK);s.text(xx,y+h+28,label,16,GRAY,anchor='middle')
 s.line(x,y,x,y+h,INK,1.4);s.line(x,y+h,x+w,y+h,INK,1.4)
 return fx,fy

data_dir=ART/'data';data_dir.mkdir(exist_ok=True)
source=ROOT/'notes/borealis-h2-dissociation-data-original.csv'
target=data_dir/'borealis-h2-dissociation-data.csv';shutil.copyfile(source,target)
assert hashlib.sha256(target.read_bytes()).hexdigest()=='6882ed85b802fb1c4e593470b09be5e6afced215375038cf385ace96629628c2'
rows=[{k:float(v) for k,v in row.items()} for row in csv.DictReader(target.open())]
assert len(rows)==19
for r in rows:r['reported_error_microHa']=r['VQE_Error_mHa']*1000
assert abs(max(r['reported_error_microHa'] for r in rows)-1.19)<1e-12
(data_dir/'h2-redraw-values.json').write_text(json.dumps({'source_url':DATA_URL,'licence':'CC0-1.0','transformation':'reported VQE_Error_mHa multiplied by 1000 to microhartree; not subtracted from rounded energies','values':rows},indent=2)+'\n')

def h2(lang,mobile):
 ko=lang=='ko';w,h=(680,950) if mobile else (1120,820)
 s=SVG(w,h,'H₂: 에너지와 오차를 함께 읽기' if ko else 'H₂: read the energy and the error', '19 public H2 dissociation data points; VQE and exact energy reference in hartree, reported absolute error converted from millihartree to microhartree.',{'data':DATA_URL,'dataset':BOREALIS,'licence':'CC0-1.0','type':'redraw of reported public data, no independent VQE execution'})
 s.text(30,45,('H₂: 겹치는 에너지와 작은 오차' if ko else 'H₂: energies and small errors') if mobile else ('H₂: 겹치는 에너지 곡선, 따로 읽어야 할 오차' if ko else 'H₂: overlapping energies, a separate error scale'),26,weight=700)
 s.text(30,77,('공개 19점 재도표 · VQE 재실행 없음' if ko else '19 reported points · no new VQE run') if mobile else ('공개 데이터 19점 · 계산 재실행 없이 재도표' if ko else '19 public data points · redrawn without rerunning the calculation'),18,GRAY)
 x,y,pw,ph=(98,182,540,280) if mobile else (105,145,660,270)
 s.text(x,y-28,'총에너지 (Ha)' if ko else 'Total energy (Ha)',19,weight=700)
 fx,fy=axes(s,x,y,pw,ph,.4,2.2,-1.16,-.9,[(v,str(v)) for v in [.4,.8,1.2,1.6,2.2]],[(v,f'{v:.2f}') for v in [-1.15,-1.10,-1.05,-1.00,-.95,-.90]])
 s.path([(fx(r['Bond_Distance_A']),fy(r['Exact_Energy_Ha'])) for r in rows],TEAL,4)
 for r in rows:s.dot(fx(r['Bond_Distance_A']),fy(r['VQE_Energy_Ha']),3.6,RUST,PAPER)
 s.text(x+pw/2,y+ph+60,'핵 사이 거리 R (Å)' if ko else 'Internuclear distance R (Å)',18,anchor='middle')
 ey=y+ph+135;eh=155 if mobile else 140
 s.text(x,ey-25,'보고된 절대 오차 (µHa)' if ko else 'Reported absolute error (µHa)',19,weight=700)
 ex,ef=axes(s,x,ey,pw,eh,.4,2.2,0,1.3,[(v,str(v)) for v in [.4,.8,1.2,1.6,2.2]],[(v,f'{v:.1f}') for v in [0,.4,.8,1.2]])
 for r in rows:
  xx=ex(r['Bond_Distance_A']);yy=ef(r['reported_error_microHa']);s.line(xx,ef(0),xx,yy,RUST,1.5);s.dot(xx,yy,4,RUST)
 s.text(x+pw/2,ey+eh+59,'핵 사이 거리 R (Å)' if ko else 'Internuclear distance R (Å)',18,anchor='middle')
 lx,ly=(105,112) if mobile else (815,172)
 s.line(lx,ly-6,lx+35,ly-6,TEAL,4);s.text(lx+47,ly,'정확 참조값' if ko else 'Exact reference',18)
 s.dot(lx+290 if mobile else lx+17,ly-6 if mobile else ly+32,4,RUST,PAPER);s.text(lx+308 if mobile else lx+47,ly if mobile else ly+38,'보고 VQE' if ko else 'Reported VQE',18)
 if mobile:
  s.text(30,h-78,'최대 오차: 1.19 µHa, R = 0.4 Å' if ko else 'Maximum error: 1.19 µHa at R = 0.4 Å',19,weight=700)
  s.text(30,h-48,'1 µHa = 10⁻⁶ Ha · 보고 오차의 단위 변환' if ko else '1 µHa = 10⁻⁶ Ha · reported errors converted',17,GRAY)
  s.text(30,h-20,'Borealis V6 · CC0 1.0 · QPU 측정 아님' if ko else 'Borealis V6 · CC0 1.0 · not a QPU run',16,GRAY)
 else:
  s.lines(810,300,['최대 보고 오차','1.19 µHa','R = 0.4 Å'] if ko else ['Maximum reported error','1.19 µHa','R = 0.4 Å'],20,32,weight=700)
  s.lines(810,433,['같은 에너지 축에서는','오차가 거의 보이지 않는다.','아래 축은 오차만 확대한다.'] if ko else ['The energy plot nearly','hides the discrepancy.','The lower plot isolates it.'],18,29,color=GRAY)
  s.text(30,h-22,'Borealis V6 · CC0 1.0 · 1 µHa = 10⁻⁶ Ha · 공개 보고값 재도표, 실제 QPU 측정 아님' if ko else 'Borealis V6 · CC0 1.0 · 1 µHa = 10⁻⁶ Ha · reported values redrawn, not QPU measurements',16,GRAY)
 s.save(f'h2_energy_{"mobile_" if mobile else ""}{lang}.svg')

def density(lang,mobile):
 ko=lang=='ko';w,h=(680,1040) if mobile else (1120,740)
 s=SVG(w,h,'같은 점유 상태, 다른 빈 준위' if ko else 'Same occupied state, different empty level','A fixed orthonormal two-orbital basis with two noninteracting electrons. H0 diag(-1,+1) eV, H1 diag(-1,+2) eV. The occupied orbital and density remain identical while the one-particle level gap changes from 2 to 3 eV. Not independent self-consistent DFT solutions or a Hohenberg-Kohn counterexample.',{'type':'review teaching model','basis':'fixed orthonormal phi0, phi1','electrons':2,'H0_eV':[[-1,0],[0,1]],'H1_eV':[[-1,0],[0,2]],'warning':'not independent self-consistent DFT solutions or a Hohenberg-Kohn counterexample'})
 s.text(30,45,'같은 점유 상태, 다른 빈 준위' if ko else 'Same occupied state, different empty level',28,weight=700)
 s.text(30,79,('직교 기저 φ₀, φ₁ 고정 · 비상호작용 전자 2개' if ko else 'Fixed basis φ₀, φ₁ · 2 noninteracting electrons') if mobile else ('고정된 직교 기저 φ₀, φ₁ · 상호작용 없는 전자 2개' if ko else 'Fixed orthonormal basis φ₀, φ₁ · two noninteracting electrons'),19,GRAY)
 cards=[(30,115,620,280),(30,420,620,280)] if mobile else [(30,120,510,340),(580,120,510,340)]
 for i,(x,y,cw,ch) in enumerate(cards):
  upper=1+i;s.rect(x,y,cw,ch)
  s.text(x+25,y+38,f'H{i} = diag(−1, +{upper}) eV',25,weight=700)
  levelx=x+85;levelw=cw-180;yy0=y+ch-65;scale=43 if mobile else 52;yy1=yy0-(upper+1)*scale
  s.line(levelx,yy0,levelx+levelw,yy0,TEAL,4);s.line(levelx,yy1,levelx+levelw,yy1,RUST,3)
  s.text(x+20,yy0+6,'−1',18,TEAL);s.text(x+20,yy1+6,f'+{upper}',18,RUST)
  s.text(levelx+levelw+15,yy0+6,'φ₀',22,TEAL);s.text(levelx+levelw+15,yy1+6,'φ₁',22,RUST)
  for dx in [-12,12]:s.dot(levelx+levelw/2+dx,yy0,7,TEAL)
  s.text(levelx+levelw/2,yy0+34,'점유 전자 2개' if ko else '2 occupied electrons',17,TEAL,anchor='middle')
  s.text(levelx+levelw/2,yy1-14,'비점유' if ko else 'unoccupied',17,RUST,anchor='middle')
  bx=levelx+levelw-24;s.line(bx,yy1+9,bx,yy0-9,GRAY,2);s.line(bx-6,yy1+9,bx+6,yy1+9,GRAY,2);s.line(bx-6,yy0-9,bx+6,yy0-9,GRAY,2)
  s.text(bx-14,(yy1+yy0)/2+6,f'Δ = {upper+1} eV',18,GRAY,anchor='end')
 by=735 if mobile else 495
 s.rect(30,by,w-60,118,'#e6f0ed',TEAL)
 s.text(w/2,by+36,'점유 궤도는 그대로 → 밀도도 그대로' if ko else 'Same occupied orbital → same density',23,TEAL,700,'middle')
 s.text(w/2,by+81,'n₀(r) = n₁(r) = 2 |φ₀(r)|²',28,TEAL,700,'middle')
 if mobile:s.lines(30,h-115,['고정 기저의 단일입자 교육 모형.','독립 SCF 해나 Hohenberg–Kohn 정리의','반례를 제시하는 그림이 아니다.'] if ko else ['An idealized one-particle teaching model.', 'Not independent self-consistent DFT solutions;', 'not a Hohenberg–Kohn counterexample.'],17,35,color=GRAY)
 else:s.lines(30,h-80,['이상화된 단일입자 모형: 독립적인 자기일관 DFT 해나','Hohenberg–Kohn 정리의 반례를 제시하는 그림이 아니다.'] if ko else ['An idealized one-particle model: not independent self-consistent DFT solutions', 'and not a counterexample to the Hohenberg–Kohn theorem.'],17,29,color=GRAY)
 s.save(f'density_gap_{"mobile_" if mobile else ""}{lang}.svg')

def referee(lang,mobile):
 ko=lang=='ko';w,h=(680,800) if mobile else (1120,700)
 s=SVG(w,h,'AI 심사자가 지적한 주요 문제' if ko else 'Major issues flagged by an AI referee','Matched-field comparison: 130 AI papers, rounded 84 percent with 95 percent bootstrap CI 78-90; 50 control papers, 76 percent, CI 64-88. AI referee judgments, not independent human verdicts. Selected sample, not all scientific work.',{'source':JCCM,'type':'reported data redraw','AI_n':130,'AI_percent':83.8,'AI_95CI':[77.7,90.0],'control_n':50,'control_percent':76,'control_95CI':[64,88],'display':'whole-percent rounding','difference_control_minus_AI_percentage_points':-7.8,'difference_95CI':[-21.5,4.9]})
 s.text(30,45,'AI 심사자가 지적한 주요 문제' if ko else 'Major issues flagged by an AI referee',28,weight=700)
 s.lines(30,80,(['같은 주분야: cond-mat/quant-ph','적어도 하나의 major issue를 지적한 비율'] if ko else ['Matched primary fields: cond-mat/quant-ph', 'Share with at least one major issue']) if mobile else (['같은 주분야(cond-mat/quant-ph)의 논문을 비교','적어도 하나의 major issue를 지적한 비율'] if ko else ['Papers matched on primary field (cond-mat/quant-ph)', 'Share flagged with at least one major issue']),19,30,color=GRAY)
 x=90 if mobile else 315;y=220 if mobile else 200;pw=w-x-55
 fx=lambda v:x+v/100*pw
 for v in [0,20,40,60,80,100]:
  xx=fx(v);s.line(xx,y-35,xx,y+215,LINE);s.text(xx,y+245,f'{v}%',18,GRAY,anchor='middle')
 entries=[(84,78,90,130,TEAL),(76,64,88,50,RUST)]
 for i,(value,lo,hi,n,color) in enumerate(entries):
  yy=y+i*145
  if mobile:
   s.text(30,yy-45,('AI 논문' if ko else 'AI papers')+f' (n = {n})' if i==0 else ('일반 논문' if ko else 'Control papers')+f' (n = {n})',21,color,700)
  else:
   s.text(30,yy+7,('AI 논문' if ko else 'AI papers')+f' (n = {n})' if i==0 else ('일반 논문' if ko else 'Control papers')+f' (n = {n})',21,color,700)
  s.line(fx(lo),yy,fx(hi),yy,color,4)
  for edge in [lo,hi]:s.line(fx(edge),yy-10,fx(edge),yy+10,color,3)
  s.dot(fx(value),yy,7,color)
  s.text(fx(value),yy+40,f'{value}% [{lo}, {hi}]',21,color,700,'middle')
 fy=560 if mobile else 500
 s.rect(30,fy,w-60,112)
 if mobile:
  s.lines(50,fy+34,['점: 보고 비율 · 선: 95% bootstrap 구간','AI 심사자의 판단이며','사람이 확정한 오류율은 아니다.'] if ko else ['Dot: reported share · line: 95% bootstrap CI', 'AI-referee judgments,', 'not human-confirmed error rates.'],18,32,color=GRAY)
  s.lines(30,h-70,['출처: JCCM 동결 공개 집계','표시값은 정수로 반올림'] if ko else ['Source: frozen JCCM public aggregates', 'Values rounded to whole percent'],16,32,color=GRAY)
 else:
  s.lines(50,fy+34,['점: 보고 비율 · 선: 95% bootstrap 신뢰구간','이 비율은 AI 심사자의 판단이며 사람의 확정 오류율이 아니다.'] if ko else ['Dot: reported share · line: 95% bootstrap confidence interval', 'These are AI-referee judgments, not human-confirmed error rates.'],18,31,color=GRAY)
  s.text(30,h-24,'출처: JCCM 동결 공개 집계 · 표시값은 정수로 반올림' if ko else 'Source: frozen JCCM public aggregates · plotted values rounded to integers',16,GRAY)
 s.save(f'referee_controls_{"mobile_" if mobile else ""}{lang}.svg')

for lang in ['ko','en']:
 for mobile in [False,True]:h2(lang,mobile);density(lang,mobile);referee(lang,mobile)
(data_dir/'figure-provenance.json').write_text(json.dumps({'cutoff':'2026-11-01','h2':{'source':DATA_URL,'doi':BOREALIS,'licence':'CC0-1.0','original_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'data_points':len(rows),'maximum_reported_error_microHa':1.19},'density_model':{'basis':'fixed orthonormal two orbitals','electrons':2,'H0_eV':[-1,1],'H1_eV':[-1,2],'occupied_orbital':'phi0','density_both':'2|phi0(r)|^2','gaps_eV':[2,3],'not':'independent self-consistent DFT solutions or Hohenberg-Kohn counterexample'},'referee':{'source':JCCM,'AI':{'n':130,'percent':83.8,'CI95':[77.7,90.0]},'control':{'n':50,'percent':76,'CI95':[64,88]},'display_rounding':'nearest integer percent','judgment':'AI referee, not human ground truth'}},ensure_ascii=False,indent=2)+'\n')
print('Created 12 bilingual desktop/mobile SVGs and traceable figure data; no original research code executed.')
