"""Independent editorial schematic from Roy et al., arXiv:2603.12256v1.
No paper artwork, sampled curve, fit, or new physics calculation is used.
"""
from pathlib import Path
import argparse,json
from PIL import Image, ImageDraw, ImageFont

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--font',type=Path,required=True)
ap.add_argument('--font-bold',type=Path,required=True)
ap.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parents[1]/'artifacts')
args=ap.parse_args()
ROOT=args.output_dir
ROOT.mkdir(parents=True,exist_ok=True)
REG=str(args.font)
BOLD=str(args.font_bold)
INK, MUTED, TEAL, GOLD, LINE = '#193c50', '#526774', '#167c94', '#bb7424', '#c8d7de'
im = Image.new('RGB', (1800, 980), 'white')
d = ImageDraw.Draw(im)
def txt(xy, s, size=32, color=INK, bold=False, anchor=None):
    d.text(xy, s, font=ImageFont.truetype(BOLD if bold else REG,size), fill=color,anchor=anchor)
def box(r, fill='#f1f6f8'):
    d.rounded_rectangle(r,radius=18,fill=fill,outline=LINE,width=2)
def arrow(a,b,color=TEAL):
    import math
    d.line((*a,*b),fill=color,width=5)
    q=math.atan2(b[1]-a[1],b[0]-a[0]);x,y=b
    d.polygon([(x,y),(x-17*math.cos(q-.4),y-17*math.sin(q-.4)),(x-17*math.cos(q+.4),y-17*math.sin(q+.4))],fill=color)

txt((50,30),'Two controls, two complementary responses',50,bold=True)
txt((50,100),'Roy, Sau & Tewari | arXiv:2603.12256v1, 12 Mar 2026 | original editorial schematic',28,MUTED)
d.line((50,153,1750,153),fill=LINE,width=3)
txt((55,180),'A   Nanowire–dot interferometer',35,bold=True)
txt((58,230),'Not to scale',26,MUTED)
d.rounded_rectangle((95,300,750,354),radius=17,fill=TEAL)
txt((420,280),'semiconductor–superconductor wire',28,anchor='mm')
d.line((120,354,120,545,359,545),fill=MUTED,width=7)
d.line((725,354,725,545,482,545),fill=MUTED,width=7)
d.ellipse((359,484,482,606),fill='#f8e8d5',outline=GOLD,width=5)
txt((420,545),'QD',33,GOLD,True,anchor='mm')
txt((420,420),'Flux Φ through loop',31,anchor='mm')
arrow((420,695),(420,615),GOLD)
txt((420,730),'gate potential V_QD',30,GOLD,anchor='mm')
txt((55,798),'φ = πΦ/Φ0;  Φ0 = h/(2e)',32)

txt((880,180),'B   H(V_QD, φ): distinct response operators',35,bold=True)
box((880,249,1745,382))
txt((910,275),'Gate variation → charge response C_Q',34,TEAL,True)
txt((910,330),'∂H/∂V_QD  |  capacitance in fF',31)
box((880,410,1745,543))
txt((910,436),'Flux variation → inverse inductance L_Q⁻¹',34,GOLD)
txt((910,490),'∂H/∂φ and ∂²H/∂φ²  |  response in nH⁻¹',30)
txt((887,565),'Lehmann response, Eqs. (22–23); ω = 0, η = 0.002 meV',27,MUTED)

txt((884,623),'C   Reported weak-disorder examples (Fig. 8)',33,bold=True)
txt((890,678),'Γ (meV)    V_QD (meV)    Calculated inductive response',28,MUTED)
txt((890,726),'0.60           0.525                parity-branch crossings',29,TEAL)
txt((890,773),'0.30           0.545                extrema at apparent C_Q crossings',29,GOLD)
txt((890,827),'L = 3 µm; V0 = 0.3 meV; µ = 0.5 meV in both cases',28,MUTED)
d.line((50,890,1750,890),fill=LINE,width=2)
txt((50,914),'Classical model calculations (200 BdG eigenstates), not a measured device or a universal topology test.',29,MUTED)
im.save(ROOT/'prb-inductance-original-summary.png')
data={
 'source':'https://arxiv.org/abs/2603.12256v1',
 'source_equations':[22,23], 'reported_figure':8,
 'method':'static-limit Lehmann response of tight-binding BdG model',
 'common_conditions':{'length_um':3,'disorder_std_meV':0.3,'chemical_potential_meV':0.5,'omega_meV':0,'eta_meV':0.002,'retained_BdG_eigenstates':200},
 'cases':[{'Zeeman_Gamma_meV':0.60,'QD_gate_potential_meV':0.525,'reported_regime':'topological','reported_inductance':'parity-branch crossings at flux h/(4e), 3h/(4e)'},{'Zeeman_Gamma_meV':0.30,'QD_gate_potential_meV':0.545,'reported_regime':'trivial','reported_inductance':'extrema at narrow double crossings in capacitance'}],
 'new_calculation':False,'original_artwork_reused':False,'curves_reconstructed':False,
 'scope':'Quantitative settings from public v1; final publication abstract read, final full text inaccessible. Conditions do not establish a universal diagnostic across other Hamiltonian classes.'
}
(ROOT/'prb-inductance-original-summary-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
