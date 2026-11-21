#!/usr/bin/env python3
"""Draw reported discrete checkpoints, not a fitted/digitised data curve."""
from pathlib import Path
import json, argparse
from PIL import Image, ImageDraw, ImageFont

parser=argparse.ArgumentParser()
parser.add_argument('--data',default=str(Path(__file__).with_name('longrange-spin-data.json')))
parser.add_argument('--output',default=str(Path(__file__).with_name('longrange-spin-checkpoints.png')))
parser.add_argument('--font',default='/Library/Fonts/Arial Unicode.ttf')
parser.add_argument('--bold-font',default='/System/Library/Fonts/Supplemental/Arial Bold.ttf')
args=parser.parse_args()
data=json.loads(Path(args.data).read_text())
W,H=1900,1060
im=Image.new('RGB',(W,H),'#f8fafc');d=ImageDraw.Draw(im)
def font(n,bold=False): return ImageFont.truetype(args.bold_font if bold else args.font,n)
def txt(x,y,s,n=30,fill='#173047',bold=False): d.text((x,y),s,font=font(n,bold),fill=fill)
def wrap(x,y,s,width,n=28,fill='#40576a',line=37):
    words=s.split(); current=''; yy=y
    for word in words:
        trial=(current+' '+word).strip()
        if d.textbbox((0,0),trial,font=font(n))[2]>width and current:
            txt(x,yy,current,n,fill);yy+=line;current=word
        else: current=trial
    if current: txt(x,yy,current,n,fill);yy+=line
    return yy
txt(65,38,'Interaction range changes the magnetic ground state',49,bold=True)
txt(67,108,'Selected convergence checkpoints | DFT and classical spin Monte Carlo',28)
panels=[(65,190,865,'CrPS4 monolayer','U = 0 eV',data['materials'][0]),(970,190,865,'NiPS3 monolayer','U = 4 eV',data['materials'][1])]
for x,y,w,title,condition,mat in panels:
    d.rounded_rectangle((x,y,x+w,800),radius=24,fill='white',outline='#cbd5e1',width=2)
    txt(x+27,y+22,title,39,bold=True);txt(x+29,y+78,condition,28)
    top=y+132
    d.rectangle((x+20,top,x+w-20,top+55),fill='#e7eef4')
    txt(x+34,top+9,'Shells kept',26,bold=True)
    txt(x+218,top+9,'Magnetic state',26,bold=True)
    txt(x+649,top+9,'Tc',26,bold=True)
    rh=103
    for k,row in enumerate(mat['checkpoints']):
        yy=top+55+rh*k
        if k%2==1:d.rectangle((x+20,yy,x+w-20,yy+rh),fill='#f4f7fa')
        txt(x+65,yy+25,str(row['shells']),38,bold=True)
        txt(x+218,yy+17,row['state_display'],31,bold=True)
        txt(x+218,yy+57,row['note_display'],23,fill='#536879')
        txt(x+635,yy+26,row['tc_display'],34,bold=True)
    yy=top+55+rh*len(mat['checkpoints'])+24
    wrap(x+29,yy,mat['interpretation_display'],w-58,28,line=38)
txt(75,828,'Spin order and ordering temperature converge at different ranges.',30,bold=True)
wrap(75,878,'Cr: 7 shells marks ground-state convergence; its Tc is omitted here. Temperatures are approximate heat-capacity-peak estimates.',1740,26,line=35)
wrap(75,962,'Source: Nagyfalusi et al., arXiv:2607.20631v2, pp. 4 and 9 (Figs. 3 and 11). Own editorial summary of reported facts.',1740,25,line=34)
Path(args.output).parent.mkdir(parents=True,exist_ok=True)
im.save(args.output)
print(args.output)
