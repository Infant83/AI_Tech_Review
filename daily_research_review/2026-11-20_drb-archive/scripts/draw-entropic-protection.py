"""Independent explanatory art from reported analytic relations, no science rerun.
Source: Tsao and Luo, arXiv:2602.16777v4, Eqs.(5),(10),(11), Sec.III.
Original source artwork is not reused; no measured/simulated curve is invented.
"""
from pathlib import Path
import json, argparse
from PIL import Image,ImageDraw,ImageFont
ap=argparse.ArgumentParser()
ap.add_argument('--output-dir',type=Path,required=True)
ap.add_argument('--font',required=True)
ap.add_argument('--font-bold',required=True)
a=ap.parse_args()
ROOT=a.output_dir
ROOT.mkdir(parents=True,exist_ok=True)
REG=a.font;BOLD=a.font_bold
INK='#193c50';MUTED='#526774';TEAL='#167c94';GOLD='#bb7424';LINE='#c8d7de'
im=Image.new('RGB',(1800,970),'white');d=ImageDraw.Draw(im)
def text(xy,s,size=34,fill=INK,bold=False,anchor=None):
 d.text(xy,s,font=ImageFont.truetype(BOLD if bold else REG,size),fill=fill,anchor=anchor)
def box(rect,color='#f1f6f8'):
 d.rounded_rectangle(rect,radius=17,fill=color,outline=LINE,width=2)
text((52,27),'Entropic reservoirs suppress creation and motion',49,bold=True)
text((52,99),'Tsao & Luo | public author preprint v4, 3 Nov 2026 | independent explanation of Eqs. (10–11)',28,MUTED)
d.line((52,154,1748,154),fill=LINE,width=3)
text((55,184),'A   Local state-space asymmetry',36,bold=True)
box((55,253,755,450))
text((85,275),'No defect: M accessible reservoir states',33,TEAL)
for x,n in [(100,'0'),(220,'1'),(340,'2'),(570,'M−1')]:
 d.rounded_rectangle((x,345,x+(140 if n=='M−1' else 80),412),radius=11,fill=TEAL)
 text((x+(70 if n=='M−1' else 40),378),n,35,'white',anchor='mm')
text((480,381),'…',43,TEAL,anchor='mm')
box((55,487,755,681),'#fbf4eb')
text((85,513),'Defect: one compatible reservoir state',33,GOLD)
d.rounded_rectangle((100,577,180,644),radius=11,fill=GOLD)
text((140,610),'0',35,'white',anchor='mm')
text((230,595),'phase-space volume 1',33,GOLD)
text((68,719),'M: reservoir dimension, not data-qubit count',29,MUTED)
text((68,770),'Free-energy penalty per defect: kBT ln M',31)

text((845,184),'B   Effective rates in the saturated regime',36,bold=True)
text((872,253),'Process',31,MUTED)
text((1665,253),'Rate / Γ0',31,MUTED,anchor='ra')
for y,label,condition,value,c in [
 (310,'Create a defect pair','two reservoirs must be compatible','≈ M⁻²',TEAL),
 (461,'Move one defect','destination reservoir must be compatible','≈ M⁻¹',GOLD),
 (612,'Annihilate a defect pair','no entropic restriction','≈ 1',INK)]:
 box((845,y,1746,y+128))
 text((872,y+15),label,33,c,True)
 text((872,y+73),condition,28,MUTED)
 text((1687,y+19),value,39,c,anchor='ra')
text((866,778),'Rare-defect torus: τL ≈ M³ ln(L/2) / (c Γ0 L²)',34)
text((866,832),'c ≈ 8 for one Pauli channel; fixed M does not protect L → ∞',27,MUTED)
d.line((52,895,1748,895),fill=LINE,width=2)
text((52,918),'Theory: βεM ≪ 1 ≪ βJ; fast reservoir equilibration and low-frequency error noise are required.',28,MUTED)
im.save(ROOT/'prb-entropic-original-mechanism.png')
data={
 'source':'https://arxiv.org/abs/2602.16777v4',
 'edition_date':'2026-11-03 submission; PDF internal date2026-11-05',
 'equations':[5,10,11],
 'level':'analytic Hamiltonian/Lindblad and random-walk result; no new numerical experiment',
 'relations':{'pair_creation':'Gamma_cr/Gamma0≈M^-2','diffusion':'Gamma_dif/Gamma0≈M^-1','annihilation':'Gamma_ann/Gamma0≈1','lifetime':'tau_L≈M^3 ln(L/2)/(c Gamma0 L^2),c≈8 for one Pauli channel'},
 'conditions':['saturated ladder-reservoir regime beta epsilon M≪1≪beta J','rare defects: L≲sqrt(M), static protection needs M at least of orderL^2','fast reservoir equilibration gamma_bath≫Gamma0lnM','environment cannot supply energy penaltyJ','one channel coefficient; both X/Z doubles logical errorrate'],
 'not_in_figure':'No reproduced source art, fabricated curve, measured lifetime, QPU performance claim or numerical model rerun.'
}
(ROOT/'prb-entropic-original-mechanism-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
