#!/usr/bin/env python3
"""Build original deterministic explanatory SVG figures. No experimental images."""
from pathlib import Path
import csv, html, math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/assets'; OUT.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
NAVY='#183843'; TEAL='#177b80'; GOLD='#bc7937'; MUTED='#526970'; PAPER='#f6f3eb'; LINE='#ccd8d7'
def esc(s): return html.escape(str(s))
class Figure:
 def __init__(self,title,subtitle,h=650):
  self.h=h;self.a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{h}" viewBox="0 0 1200 {h}" role="img" aria-label="{esc(title)}">',f'<rect width="1200" height="{h}" rx="24" fill="{PAPER}"/>','<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="#526970" stroke-width="1.5"/></marker></defs>']
  self.text(48,57,title,32,NAVY,700);self.text(48,96,subtitle,20,MUTED)
 def text(self,x,y,t,size=24,color=NAVY,weight=400,anchor='start'):
  for i,line in enumerate(t.split('\n')):
   self.a.append(f'<text x="{x}" y="{y+i*size*1.3}" font-family="Arial, DejaVu Sans, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{esc(line)}</text>')
 def box(self,x,y,w,h,title,sub='',color=TEAL):
  self.a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="white" stroke="{color}" stroke-width="2"/>')
  self.text(x+w/2,y+39,title,24,color,700,'middle')
  if sub:self.text(x+w/2,y+76,sub,20,MUTED,400,'middle')
 def line(self,x1,y1,x2,y2,color=MUTED,dash=False,arrow=True,width=3):
  self.a.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="9 8"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
 def footer(self,t):self.text(48,self.h-28,t,18,MUTED)
 def save(self,name): (OUT/(name+'.svg')).write_text('\n'.join(self.a)+ '\n</svg>\n')

f=Figure('READING A TINY POLARIZATION CHANGE','Conceptual pump-probe layout | not to scale',640)
f.box(45,248,210,120,'X-ray probe','Linear polarization')
f.box(359,220,305,160,'Overlap in vacuum','Two polarization modes\nacquire a phase difference')
f.box(754,248,178,120,'Analyzer','Crossed channel')
f.box(998,248,157,120,'Detector','Count photons')
f.line(257,308,357,308,TEAL);f.line(666,308,752,308,TEAL);f.line(934,308,996,308,TEAL)
f.text(485,158,'Intense laser pump',24,GOLD,700,'middle');f.line(475,172,509,215,GOLD)
f.box(103,447,454,116,'PUMP OFF','Measure optical leakage',MUTED)
f.box(643,447,454,116,'PUMP ON','Signal + pump-related background',TEAL)
f.footer('Interpret a differential signal only after polarization, scattering and overlap controls.')
f.save('vacuum')

f=Figure('TWO DISTINCT QUANTUM QUESTIONS','Classical records can support quantum inference; re-encoding does not restore the original state.',690)
f.box(338,145,524,105,'Detector event records','Momenta, directions, energies')
f.line(475,252,300,323);f.line(725,252,900,323)
f.box(67,329,466,141,'INFER A SPIN STATE','Decay-angle distributions\nEstimate a density matrix',TEAL)
f.box(667,329,466,141,'ENCODE DATA INTO QUBITS','Choose features and circuit rotations\nTrain a quantum model',GOLD)
f.line(300,473,300,514);f.line(900,473,900,514)
f.box(67,520,466,108,'Correlation / entanglement test','Physics of the produced ensemble',TEAL)
f.box(667,520,466,108,'Anomaly score / classification','Performance of a computation',GOLD)
f.footer('Neither route alone establishes a new particle or a practical quantum advantage.')
f.save('collider')

f=Figure('AUTOENCODER PERFORMANCE IN ONE PAPER','AUC from Table I, 1 Particle 1 Qubit | classical circuit simulation',650)
for i,t in enumerate([0,0.25,0.5,0.75,1]):
 x=280+820*t;f.line(x,178,x,492,LINE,arrow=False,width=1);f.text(x,529,f'{t:g}',20,MUTED,anchor='middle')
data=[('W',.715,.671),('Higgs → bb',.774,.739),('top',.872,.858)]
for i,(name,q,c) in enumerate(data):
 y=194+i*104
 f.text(56,y+40,name,27,NAVY,700)
 for j,(v,col) in enumerate([(q,TEAL),(c,GOLD)]):
  yy=y+j*38;f.a.append(f'<rect x="280" y="{yy}" width="{820*v}" height="27" rx="4" fill="{col}"/>');f.text(291+820*v,yy+23,f'{v:.3f}',22,col,700)
f.text(688,565,'AUC (not classification accuracy)',22,MUTED,anchor='middle')
f.a.append(f'<rect x="55" y="582" width="22" height="14" fill="{TEAL}"/><rect x="386" y="582" width="22" height="14" fill="{GOLD}"/>')
f.text(89,597,'Quantum autoencoder',20,NAVY);f.text(421,597,'Classical autoencoder',20,NAVY)
f.footer('At most 10 retained particles per jet. Source table provides no uncertainty bars.')
f.save('auc')
with (DATA/'auc.csv').open('w') as fp:
 w=csv.writer(fp);w.writerow(['signal','quantum_autoencoder_auc','classical_autoencoder_auc']);w.writerows(data)

f=Figure('A GROWING PEAK NEED NOT MEAN DIVERGING ENERGY','Illustrative 3D scaling only: speed ~ 1/epsilon; volume ~ epsilon^3; local energy ~ epsilon',650)
xs=[1,.5,.25,.125]
for j,(title,values,col,maxv) in enumerate([('Peak speed scale',[1/x for x in xs],TEAL,8),('Local energy scale',xs,GOLD,1)]):
 left=110+j*578;top=210;bottom=482;right=left+410
 f.text(left+205,160,title,27,col,700,'middle')
 for t in [0,.5,1]:
  y=bottom-t*(bottom-top);f.line(left,y,right,y,LINE,arrow=False,width=1);f.text(left-17,y+7,f'{t*maxv:g}',19,MUTED,anchor='end')
 points=[]
 for i,(x,v) in enumerate(zip(xs,values)):
  px=left+i*410/3;py=bottom-v/maxv*(bottom-top);points.append((px,py))
  f.text(px,518,['1','1/2','1/4','1/8'][i],21,MUTED,anchor='middle')
  f.a.append(f'<circle cx="{px}" cy="{py}" r="6" fill="{col}"/>')
 for a,b in zip(points,points[1:]):f.line(*a,*b,col,arrow=False,width=3)
 f.text(left+205,565,'Shrinking length scale ε →',21,MUTED,anchor='middle')
f.footer('Separate normalized vertical scales. This is not a velocity field or a Navier–Stokes solution.')
f.save('concentration')
with (DATA/'concentration.csv').open('w') as fp:
 w=csv.writer(fp);w.writerow(['epsilon','peak_speed_scale','volume_scale','local_energy_scale']);w.writerows([(x,1/x,x**3,x) for x in xs])

f=Figure('WHAT MUST A COMPUTER-ASSISTED PROOF ESTABLISH?','Complementary checks, not interchangeable badges',700)
f.box(348,142,504,104,'Original mathematical problem','Domain, forcing, smoothness, energy',NAVY)
f.line(470,249,302,319);f.line(730,249,891,319)
f.box(65,325,467,137,'AI SEARCH → FORMAL PROOF','Definitions, lemmas, candidate repairs\nChecked within the formal system',TEAL)
f.box(667,325,467,137,'STATEMENT CORRESPONDENCE','Does the encoded theorem match\nthe original mathematical question?',GOLD)
f.line(302,465,471,534);f.line(891,465,732,534)
f.box(265,540,670,100,'INDEPENDENT REVIEW & UNDERSTANDING','Reproduction, assumptions, mathematical mechanism',NAVY)
f.footer('This review inspected released artifacts; it did not run the full Lean build or independent checker.')
f.save('proof')

f=Figure('FROM SENSORY INPUT TO A MEMORY CLAIM','A proposed mechanism requires evidence beyond a behavioral score.',690)
f.box(52,155,340,120,'Peripheral stimulation','Specify the actual nerve',NAVY)
f.box(52,333,340,120,'Sensory input','Brainstem pathways',NAVY)
f.line(222,277,222,330)
f.box(470,190,660,120,'Proposed arousal modulation','LC / noradrenergic network hypothesis',TEAL)
f.line(395,382,510,314,TEAL,dash=True)
f.box(470,377,660,120,'Attention and learning state','Encoding • consolidation • retrieval',TEAL)
f.line(800,313,800,373,TEAL,dash=True)
f.line(800,500,800,536,TEAL,dash=True)
f.box(470,540,660,95,'Task performance','Measure benefits, null effects and harms',GOLD)
f.text(55,525,'Solid: sensory-input concept\nDashed: mechanism not directly\nestablished in the compared\nbehavioral study',20,MUTED)
f.footer('Conceptual pathways, not an anatomical atlas, treatment claim or stimulation protocol.')
f.save('brain')
print('Built 6 SVG figures and 2 source-data tables.')

