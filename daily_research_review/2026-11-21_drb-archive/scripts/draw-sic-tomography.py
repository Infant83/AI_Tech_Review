#!/usr/bin/env python3
"""Plot the published CSV matrix and reported coherence estimates; no new fit."""
from pathlib import Path
import argparse, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();d=json.loads(a.data.read_text())
    m=np.array(d['matrix'],dtype=float)
    assert m.shape==(4,4) and np.allclose(m,m.T) and np.isclose(np.trace(m),1)
    bell=np.array([1,0,0,1])/np.sqrt(2)
    overlap=float(bell@m@bell)
    assert np.isclose(overlap,d['Bell_target_overlap'])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12})
    fig=plt.figure(figsize=(12.4,6.6),facecolor='white')
    navy='#17364b';teal='#247b83';muted='#526a78'
    fig.text(.045,.94,'An electron–nuclear state, and a nuclear memory',fontsize=21,
             color=navy,weight='bold')
    fig.text(.045,.895,'Reported tomography matrix and coherence measurements | room-temperature SiC',
             fontsize=12,color=muted)
    ax=fig.add_axes([.09,.19,.40,.61])
    im=ax.imshow(m,cmap='RdBu_r',vmin=-.5,vmax=.5)
    labels=['0, up','0, down','1, up','1, down']
    ax.set_xticks(range(4),labels,fontsize=13)
    ax.set_yticks(range(4),labels,fontsize=13)
    ax.set_xlabel('Electron, nuclear basis',color=muted,labelpad=7,fontsize=13)
    ax.set_title('Published Fig. 5d: real matrix values',fontsize=13,color=navy,pad=10)
    for i in range(4):
        for j in range(4):
            ax.text(j,i,f'{m[i,j]:.4g}',ha='center',va='center',
                    color='white' if abs(m[i,j])>.28 else navy,fontsize=14)
    cax=fig.add_axes([.505,.20,.014,.58])
    cb=fig.colorbar(im,cax=cax);cb.set_label('Real matrix element (dimensionless)',fontsize=10)
    cb.ax.tick_params(labelsize=9)
    fig.text(.64,.765,'Bell-state overlap',fontsize=14,color=navy,weight='bold')
    fig.text(.64,.697,f'{overlap*100:.2f}%',fontsize=31,color=teal,weight='bold')
    fig.text(.64,.654,'89% reported; 88.95% from the CSV matrix',fontsize=11,color=muted)
    fig.text(.64,.565,'Nuclear Ramsey',fontsize=13,color=navy,weight='bold')
    fig.text(.64,.515,r'$T_2^* = 102.2 \pm 7.2\ \mu s$',fontsize=19,color=teal)
    fig.text(.64,.405,'Nuclear spin echo',fontsize=13,color=navy,weight='bold')
    fig.text(.64,.355,r'$T_2 = 151.0 \pm 6.9\ \mu s$',fontsize=19,color=teal)
    fig.text(.64,.265,'Ramsey and echo use different pulse sequences.',fontsize=10.5,color=muted)
    fig.text(.045,.075,'Review reconstruction: matrix from DaRUS-5965 v1.0, Fig5d.csv; coherence values from published Fig. 4.',
             fontsize=10,color=muted)
    fig.text(.045,.038,'Wörnle et al., npj Quantum Information 12, 191 (2026), doi:10.1038/s41534-026-01415-8. CC BY 4.0.',
             fontsize=10,color=muted)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(a.output,dpi=180,facecolor='white',metadata={'Software':'ATRL deterministic scientific plotting'})
    plt.close(fig)

if __name__=='__main__':main()
