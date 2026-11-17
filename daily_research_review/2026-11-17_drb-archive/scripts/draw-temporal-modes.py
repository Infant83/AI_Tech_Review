from pathlib import Path
import argparse,math,json
from PIL import Image,ImageDraw,ImageFont
ap=argparse.ArgumentParser(description='Reconstruct analytic temporal modes and reported receiver populations; optionally excerpt CC BY source panels.')
ap.add_argument('--font',required=True)
ap.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parents[1]/'artifacts')
ap.add_argument('--source-page',type=Path,help='Optional publisher PDF page 3 rendered at 300 dpi for CC BY Fig.1(a,f) excerpt')
a=ap.parse_args();P=a.output_dir;P.mkdir(parents=True,exist_ok=True)
W,H=1800,820
im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
font=a.font
f=lambda n:ImageFont.truetype(font,n)
ink='#16334A';gray='#506270';cols=['#1C5AA6','#C57216','#A44B94']
def txt(x,y,s,n=28,c=ink):d.text((x,y),s,font=f(n),fill=c)
txt(45,25,'A  Orthogonal temporal amplitudes',36)
txt(1030,25,'B  Measured receiver populations',36)
# Panel A: dimensionless functions from source Eqs.(1)–(3).
x0,y0,x1,y1=130,120,930,635
xp=lambda x:x0+(x+12)/24*(x1-x0)
yp=lambda y:y1-(y+.50)/1.10*(y1-y0)
for v in [-.4,-.2,0,.2,.4,.6]:
 yy=yp(v);d.line((x0,yy,x1,yy),fill='#DDE4E8',width=2);txt(55,yy-20,f'{v:.1f}',26,gray)
for v in [-12,-6,0,6,12]:
 xx=xp(v);d.line((xx,y0,xx,y1),fill='#EDF0F2',width=2);txt(xx-20,y1+13,str(v),26,gray)
d.line((x0,y0,x0,y1),fill=ink,width=3);d.line((x0,y1,x1,y1),fill=ink,width=3)
txt(340,700,'Normalized time Γt',30);txt(130,80,'f_n(t) / √Γ',28)
def fn(n,x):
 sech=1/math.cosh(x/2)
 return [.5*sech,math.sqrt(3)/(2*math.pi)*x*sech,math.sqrt(5)/(8*math.pi**2)*(3*x*x-math.pi**2)*sech][n]
for n,col in enumerate(cols):
 pts=[(xp(-12+k*24/1200),yp(fn(n,-12+k*24/1200))) for k in range(1201)]
 d.line(pts,fill=col,width=5)
 lx=620+n*110;d.line((lx,85,lx+35,85),fill=col,width=5);txt(lx+43,63,['f₀','f₁','f₂'][n],29,col)
# Panel B: numbers printed on filled measured bars, not fitted/ideal bars.
M=[[.79,.02,.02],[.02,.78,.04],[.01,.01,.75]]
txt(1160,100,'Absorption mode n_B',29)
for c in range(3):txt(1250+c*160,143,str(c),32)
for r in range(3):
 txt(1040,230+r*150,f'n_A = {r}',27)
 for c in range(3):
  v=M[r][c];q=v/.8;col=tuple(round(245+(z-245)*q) for z in (34,119,130))
  x,y=1190+c*160,195+r*150
  d.rounded_rectangle((x,y,x+150,y+130),radius=7,fill=col,outline='#C9D6DB',width=2)
  d.text((x+33,y+40),f'{v:.2f}',font=f(42),fill='white' if v>.4 else ink)
txt(1080,697,'Emission rows; absorption columns',28)
txt(1070,745,'P_f at the optimum absorption delay',28,gray)
txt(45,777,'A: analytic Eqs. (1)–(3). B: measured bar labels, arXiv:2604.12947v1 Fig. 3(e–g). No raw-data reanalysis.',24,gray)
im.save(P/'prl-temporal-modes-own.png')
# Small numerical validation of analytic basis only, not experimental replication.
N=20000;dx=100/N
vals=[[fn(n,-50+i*dx) for i in range(N+1)] for n in range(3)]
G=[[sum((1 if i in [0,N] else 4 if i%2 else 2)*vals[a][i]*vals[b][i] for i in range(N+1))*dx/3 for b in range(3)] for a in range(3)]
(P/'prl-temporal-modes-own-validation.json').write_text(json.dumps({'domain_Gamma_t':[-50,50],'quadrature':'composite Simpson','intervals':N,'analytic_mode_Gram_matrix':G,'max_identity_error':max(abs(G[a][b]-(a==b)) for a in range(3) for b in range(3)),'scope':'Checks analytic curves only; not original experimental data, transfer simulation or independent reproduction.'},indent=2)+'\n')
# Source figure excerpts; crop only, preserve original panel labels/axes.
if a.source_page:
    src=Image.open(a.source_page)
    for name,box in [('prxq-directional-fig1f.png',(1825,640,2340,1135)),('prxq-directional-fig1a.png',(225,197,1250,633))]:
     crop=src.crop(box)
     if name.endswith('fig1f.png'):
      # Remove only neighboring-panel marks outside the selected panel.
      cd=ImageDraw.Draw(crop);cd.rectangle((65,0,515,33),fill='white');cd.rectangle((0,480,80,495),fill='white')
     crop.save(P/name)
    panel=Image.new('RGB',(1590,530),'white')
    panel.paste(Image.open(P/'prxq-directional-fig1a.png'),(10,45))
    panel.paste(Image.open(P/'prxq-directional-fig1f.png'),(1055,15))
    panel.save(P/'prxq-directional-fig1af-composite.png')
print('Analytic basis max error',max(abs(G[a][b]-(a==b)) for a in range(3) for b in range(3)))
