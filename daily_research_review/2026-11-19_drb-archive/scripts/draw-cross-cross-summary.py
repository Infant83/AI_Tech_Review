from pathlib import Path
import argparse,json,hashlib
from PIL import Image,ImageDraw,ImageFont
ap=argparse.ArgumentParser(description='Replot reported gate values and explicitly evaluated decay terms.')
ap.add_argument('--font',type=Path,required=True)
ap.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parents[1]/'artifacts')
args=ap.parse_args()
base=args.output_dir
base.mkdir(parents=True,exist_ok=True)
W,H=1800,880
im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
font=str(args.font)
def ft(n):return ImageFont.truetype(font,n)
navy='#1e3545';blue='#397c95';gold='#bb8841';muted='#52636e';line='#b9c7cf';light='#f1f5f7'
def txt(x,y,s,n=30,c=navy):d.text((x,y),s,font=ft(n),fill=c)
def cent(x,y,s,n=30,c=navy):
 b=d.textbbox((0,0),s,font=ft(n));txt(x-(b[2]-b[0])/2,y,s,n,c)
# Reading path: mechanism and chosen numerical case, then distinct error contributions.
txt(40,24,'Cavity-mediated cross-cross-resonance gate',44)
txt(42,86,'Selected case: two four-level transmons + one cavity | theory and classical numerics',29,muted)
d.line((40,134,1760,134),fill=line,width=2)
txt(42,158,'A  Driven shared-cavity design',34)
# Simple functional diagram; no fabrication/physical scale implied.
for cx,lab in [(205,'Transmon 1'),(665,'Transmon 2')]:
 d.rounded_rectangle((cx-120,264,cx+120,464),20,fill=light,outline=blue,width=3)
 cent(cx,216,lab,29)
 for i in range(4):
  yy=[430,380,338,304][i];d.line((cx-55,yy,cx+55,yy),fill=navy,width=3);txt(cx+65,yy-17,str(i),23)
 cent(cx,485,'4 levels in the model',23,muted)
 # drive at the qubit; separate cavity tone shown below.
 d.line((cx-168,284,cx-126,284),fill=gold,width=4);d.polygon([(cx-121,284),(cx-137,276),(cx-137,292)],fill=gold)
 cent(cx,534,'Ω/(2π) = 100 MHz',28)
# Shared cavity resonator.
d.rounded_rectangle((370,314,500,414),16,outline=blue,width=4,fill='#e9f1f4')
cent(435,347,'Cavity',25)
d.line((325,364,370,364),fill=navy,width=4);d.line((500,364,545,364),fill=navy,width=4)
cent(435,585,'g/(2π) = 40 MHz on both sides',29)
cent(435,635,'P = 4 flowers + cavity cancellation tone',28)
cent(435,683,'T = 469 ns   |   ε/(2π) = 17.52 MHz',30)
d.line((875,157,875,763),fill=line,width=2)
txt(925,158,'B  Reported result and added decay terms',33)
txt(925,218,'Same 469 ns case; contributions shown separately',25,muted)
# Horizontal bars: equal scale, distinct status labels.
X0=1192;X1=1712;scale=(X1-X0)/2.0
for v in [0,.5,1.,1.5,2.]:
 x=X0+v*scale;d.line((x,282,x,624),fill='#e4e9ec',width=2);cent(x,640,f'{v:g}',24,muted)
vals=[1.5,0.816*0.469/400*1000,0.064*0.469/30*1000]
labels=[('Closed-system','numerics'),('Qubit relaxation','model term'),('Cavity loss','model term')]
for j,(value,labs,color) in enumerate(zip(vals,labels,[blue,gold,'#778c66'])):
 y=304+j*114
 txt(925,y,labs[0],25);txt(925,y+34,labs[1],22,muted)
 d.rectangle((X0,y+4,X0+value*scale,y+54),fill=color)
 txt(X0+value*scale+11,y+9,f'{value:.3g}',27)
cent((X0+X1)/2,688,'Infidelity contribution (×10⁻³)',26)
txt(925,740,'T1,q = 400 μs; T1,cavity = 30 μs for model terms',25,muted)
d.line((40,791,1760,791),fill=line,width=2)
txt(42,811,'Own schematic and chart from Gorshkov et al., PRX Quantum 7, 043034 (2026), Sec. IX, p. 27.',24,muted)
txt(42,846,'Decay terms: 0.816 T/T1,q + 0.064 T/T1,cavity. Values evaluated from the authors’ model; no new gate simulation.',23,muted)
out=base/'cross-cross-fourlevel-summary.png';im.save(out,optimize=True)
record={'source_doi':'10.1103/1nt2-f7gl','source':'Version of Record, PRX Quantum 7,043034(2026), Sec.IX p27 final paragraph before Sec.X','input':{'gate_ns':469,'reported_closed_system_infidelity':.0015,'g_MHz':40,'Omega_MHz':100,'epsilon_MHz':17.52,'T1q_us':400,'T1cav_us':30,'qubit_coefficient':.816,'cavity_coefficient':.064},'derived':{'qubit_decay_infidelity':vals[1]/1000,'cavity_decay_infidelity':vals[2]/1000},'method':'Direct arithmetic substitution in authors’ reported linear decay model; no independent quantum simulation and no claim of new full open-system fidelity.','asset':out.name,'dimensions':[W,H],'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}
(base/'cross-cross-summary-validation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False))
