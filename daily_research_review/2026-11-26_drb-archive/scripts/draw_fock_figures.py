#!/usr/bin/env python3
"""Draw original explanatory artwork and replot attributed reported data.

No fit, simulation, digitization or raw-run reaggregation is performed.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
DATA = json.loads((OUT / 'fock-measurement-data.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'axes.spines.top':False,
                     'axes.spines.right':False,'axes.labelcolor':'#17364b',
                     'text.color':'#17364b','axes.titleweight':'bold'})
rf = DATA['variance_compression']['rows']
ds = DATA['displacement_sensitivity']['rows']
fig, ax = plt.subplots(1,2,figsize=(11.8,5.7),layout='constrained')
x,y,e = zip(*rf)
ax[0].errorbar(x,y,yerr=e,fmt='o',color='#247b83',capsize=3,ms=7,label='Reported experiment ± s.d.')
ax[0].set(xlabel=r'Mean cavity photon number $\bar{N}$',ylabel=r'Variance compression $R_f$ (dB)',
          ylim=(12,25),xlim=(15,540),title='(a) Photon-number focusing')
ax[0].set_xticks([50,150,250,350,450,500]);ax[0].grid(alpha=.18)
ax[0].legend(loc='upper left',fontsize=11,frameon=False)
ax[0].annotate('500 photons:\n21.5 ± 1.1 dB',xy=(500,y[-1]),xytext=(300,14.2),fontsize=12,
                arrowprops={'arrowstyle':'->','color':'#17364b'})
x,y,e,model=zip(*ds)
ax[1].errorbar(x,y,yerr=e,fmt='o',color='#247b83',capsize=4,ms=5.5,elinewidth=1.4,label='Reported experiment ± s.d.')
ax[1].plot(x,model,'o',mfc='none',mec='#8d6250',ms=6,label='Reported lossless model')
ax[1].axhline(.5,color='#617d43',ls='--',label=r'Theoretical SQL: $\delta\beta=0.5$')
ax[1].set(xlabel=r'Mean cavity photon number $\bar{N}$',ylabel=r'Displacement uncertainty $\delta\beta$',
          xlim=(15,540),ylim=(.033,.66),yscale='log',title='(b) Sensitivity after readout')
ax[1].set_xticks([50,150,250,350,450,500]);ax[1].set_yticks([.04,.05,.1,.2,.5]);ax[1].set_yticklabels(['0.04','0.05','0.1','0.2','0.5'])
ax[1].grid(alpha=.18);ax[1].legend(loc='upper right',bbox_to_anchor=(1,.80),fontsize=10.3,frameon=False)
ax[1].annotate('Best measured gain at 400:\n19.20 ± 0.20 dB',xy=(400,y[7]),xytext=(135,.15),fontsize=11.5,
                arrowprops={'arrowstyle':'->','color':'#17364b'})
fig.supxlabel('Review replot · Fig. 2d and Fig. 4e source tables · DOI 10.6084/m9.figshare.34329033.v1 · CC BY 4.0',fontsize=9)
fig.savefig(OUT/'fock-measurement-replot.png',dpi=190,facecolor='white');plt.close(fig)

fig,ax=plt.subplots(figsize=(12,3.4));ax.set(xlim=(0,12),ylim=(0,3.4));ax.axis('off')
labels=[('Coherent state',r'$D(\alpha)|0\rangle$'),('Fock-space focusing','Kerr phase\n+ weak coherent drive'),
        ('Probe + signal',r'$N$-focused state'+'\n'+r'$D(\beta)$'),('Second lens','+ reverse\ndisplacement'),
        ('Near-vacuum readout','Transmon response\n(averaged voltage)')]
for i,(title,body) in enumerate(labels):
    x=.12+i*2.4
    ax.add_patch(FancyBboxPatch((x,1.15),2.14,1.5,boxstyle='round,pad=.05,rounding_size=.07',fc='#e9f2f6',ec='#247b83',lw=1.5))
    ax.text(x+1.07,2.34,title,ha='center',va='center',fontsize=11.3,weight='bold')
    ax.text(x+1.07,1.73,body,ha='center',va='center',fontsize=10.5,linespacing=1.5)
    if i<4:ax.add_patch(FancyArrowPatch((x+2.17,1.91),(x+2.34,1.91),arrowstyle='-|>',mutation_scale=14,color='#17364b'))
ax.text(.12,3.05,'A microwave storage cavity and an ancilla transmon',fontsize=16,weight='bold')
ax.text(.12,.6,'Preparation demonstrated up to mean photon number 500; peak sensing gain occurs at 400.',fontsize=11.2)
ax.text(.12,.18,'Original editorial schematic from arXiv:2602.23254v1 and final Supplementary Information; no measured distributions drawn.',fontsize=8.5,color='#62737c')
fig.subplots_adjust(left=.025,right=.985,top=.98,bottom=.03)
fig.savefig(OUT/'fock-control-flow.png',dpi=190,facecolor='white');plt.close(fig)
print('Created attributed reported-data replot and original process schematic.')
