"""Original editorial figures from explicitly attributed reported facts.

No original paper artwork, digitized curves, scientific solver or new fit is used.
All plotted values are supplied in condensed-figure-data.json.
"""
from pathlib import Path
import argparse,json
from PIL import Image, ImageDraw, ImageFont

ap=argparse.ArgumentParser()
ap.add_argument('--font',required=True)
ap.add_argument('--font-bold',required=True)
ap.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parents[1]/'artifacts')
ap.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'artifacts/condensed-figure-data.json')
a=ap.parse_args();ROOT=a.output_dir;ROOT.mkdir(parents=True,exist_ok=True)
DATA=json.loads(a.data.read_text())
REG=a.font
BOLD=a.font_bold
INK, MUTED, TEAL, GOLD, LINE = '#193c50', '#526774', '#167c94', '#bb7424', '#c8d7de'

def canvas(title, subtitle):
    im = Image.new('RGB', (1800, 960), 'white')
    d = ImageDraw.Draw(im)
    txt(d, (55, 35), title, 51, bold=True)
    txt(d, (55, 105), subtitle, 29, MUTED)
    d.line((55, 160, 1745, 160), fill=LINE, width=3)
    return im, d

def txt(d, xy, s, size=34, fill=INK, bold=False, anchor=None):
    d.text(xy, s, font=ImageFont.truetype(BOLD if bold else REG, size), fill=fill, anchor=anchor)

def box(d, rect, fill='#f1f6f8'):
    d.rounded_rectangle(rect, radius=18, fill=fill, outline=LINE, width=2)

def arrow(d, start, end, fill=TEAL):
    d.line((*start, *end), fill=fill, width=5)
    x, y = end
    d.polygon([(x,y), (x-15,y-9), (x-15,y+9)], fill=fill)

def hole():
    im, d = canvas('Hole number and magnetic-field response', 'Jin et al. | public author preprint v1, 9 Nov 2024 | original editorial reconstruction')
    txt(d, (60, 193), 'A   Three occupation settings in one double dot', 36, bold=True)
    txt(d, (60, 253), 'QD2 occupation N held fixed', 32, MUTED)
    for y, label in zip([345, 485, 625], ['(M, N)', '(M + 2, N)', '(M + 16, N)']):
        box(d, (65, y-10, 810, y+100))
        d.ellipse((100,y+12,166,y+78), fill=TEAL)
        d.ellipse((218,y+12,284,y+78), fill=GOLD)
        d.line((166,y+45,218,y+45), fill=MUTED, width=4)
        txt(d, (330, y+22), label, 39, bold=True)
    txt(d, (65, 755), 'M and N: absolute hole numbers not identified', 29, MUTED)
    txt(d, (65, 805), 'Angular patterns changed little across these settings.', 30)
    txt(d, (930, 193), 'B   Approximate g1 summary in v1', 36, bold=True)
    x0, x1, top, bottom = 1050, 1690, 300, 710
    d.line((x0,top,x0,bottom,x1,bottom), fill=INK, width=3)
    for v in [0, 1, 2, 3]:
        y = bottom-v/3*410
        d.line((x0-10,y,x0,y), fill=INK, width=2)
        txt(d,(x0-22,y),str(v),27,MUTED,anchor='rm')
        if v: d.line((x0+1,y,x1,y),fill='#e7edf0',width=1)
    for x, v, label, color in [(1140, DATA['hole']['g1_in_plane'], 'In plane', TEAL), (1450, DATA['hole']['g1_out_of_plane'], 'Out of plane', GOLD)]:
        y=bottom-v/3*410
        d.rectangle((x,y,x+170,bottom),fill=color)
        txt(d,(x+85,y-20),'≈ '+str(v),42,color,bold=True,anchor='mb')
        txt(d,(x+85,bottom+24),label,31,anchor='mt')
    txt(d,(1050,252),'g1 (dimensionless)',29,MUTED)
    txt(d,(945,805),'Approximate reported values; no curve or error bar inferred.',27,MUTED)
    d.line((55,880,1745,880),fill=LINE,width=2)
    txt(d,(55,901),'Measured quantities: DC leakage current and continuous-wave electric-dipole spin resonance.',27,MUTED)
    im.save(ROOT/'prb-hole-reported-summary.png')

def cpdft():
    im, d = canvas('Conditional electron density in periodic solids', 'You et al. | accepted author preprint v2, 30 Sep 2026 | editorial reconstruction')
    txt(d,(60,192),'A   A reference electron changes the question',36,bold=True)
    box(d,(65,265,800,370))
    txt(d,(100,295),'KS-DFT: ground-state n(r) and potential',32)
    d.line((430,371,430,410),fill=TEAL,width=4)
    box(d,(65,412,800,540))
    txt(d,(100,435),'Choose reference position r and coupling λ',31)
    txt(d,(100,482),'Solve an (N − 1)-electron CP-KS problem',31)
    d.line((430,541,430,582),fill=TEAL,width=4)
    box(d,(65,584,800,735))
    txt(d,(100,607),'Conditional density: n_r(r′)',35,bold=True)
    txt(d,(100,663),'Pair density: P(r, r′) = n(r) n_r(r′)',33)
    txt(d,(65,780),'Practical approximation: PBE + local blue-electron potential',27,MUTED)
    txt(d,(65,821),'Independent SCF calculations for selected r and each λ.',28,MUTED)
    txt(d,(920,192),'B   Weak-correlation consistency check',36,bold=True)
    txt(d,(920,254),'Reported integrated XC energy (eV)',30,MUTED)
    txt(d,(1180,318),'CP-DFT',30,TEAL,bold=True)
    txt(d,(1485,318),'KS-PBE',30,GOLD,bold=True)
    for y, row in zip([400,525,650],DATA['cpdft']['xc_energies_eV']):
        d.line((930,y+88,1720,y+88),fill=LINE,width=2)
        txt(d,(950,y+14),row['system'],39,bold=True)
        txt(d,(1240,y+14),str(row['cpdft']).replace('-','−'),40,TEAL,anchor='mt')
        txt(d,(1550,y+14),str(row['ks_pbe']).replace('-','−'),40,GOLD,anchor='mt')
    txt(d,(920,780),'Within-row comparison of the reported numbers.',28,MUTED)
    txt(d,(920,821),'Per-atom normalization / Na, Si atom counts: not stated.',27,MUTED)
    d.line((55,880,1745,880),fill=LINE,width=2)
    txt(d,(55,901),'New target: pointwise pair correlations. Computational evidence: classical PBE/SIESTA-based CP-DFT.',27,MUTED)
    im.save(ROOT/'prl-cpdft-method-and-reported-values.png')

hole()
cpdft()
