#!/usr/bin/env python3
"""Original basis diagram and chart of reported numerical facts; no source panel."""
from pathlib import Path
import argparse, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--font',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--data',type=Path,default=Path(__file__).resolve().parents[1]/'artifacts/aklt-encoding-results.json')
    a=ap.parse_args(); d=json.loads(a.data.read_text())
    font_manager.fontManager.addfont(str(a.font))
    family=font_manager.FontProperties(fname=str(a.font)).get_name()
    plt.rcParams.update({'font.family':family,'font.size':12,'axes.unicode_minus':False})
    navy='#17364b'; teal='#247b83'; orange='#b46b35'; gray='#687b87'
    fig=plt.figure(figsize=(10.3,4.7),facecolor='white')
    left=fig.add_axes([.025,.16,.42,.73]); left.axis('off');left.set_xlim(0,1);left.set_ylim(0,1)
    left.text(.02,1.06,'A  스핀-1 한 자리에 맞춘 기저',color=navy,weight='bold',fontsize=14)
    left.text(.18,.94,'1 qutrit',ha='center',color=teal,fontsize=13)
    left.text(.76,.94,'2 qubits',ha='center',color=navy,fontsize=13)
    for row,(x,y) in enumerate(d['basis_map'].items()):
        yy=.77-row*.22
        left.text(.18,yy,'|'+x+'〉',ha='center',va='center',fontsize=22,color=teal,
                  bbox=dict(boxstyle='round,pad=.3',fc='#e9f2f6',ec='none'))
        left.annotate('',xy=(.62,yy),xytext=(.36,yy),arrowprops={'arrowstyle':'->','color':gray,'lw':1.5})
        left.text(.76,yy,'|'+y+'〉',ha='center',va='center',fontsize=22,color=navy)
    left.text(.76,.04,'|11〉은 코드 공간 밖',ha='center',fontsize=11,color=gray)
    left.text(.02,-.11,'논문에서 비교한 기저 사상의 개념도',fontsize=10,color=gray)
    ax=fig.add_axes([.59,.20,.38,.63])
    values=d['values']; ys=list(range(len(values)))
    ax.barh(ys,[x['H_percent'] for x in values],color=[teal if x['state'].endswith('a') else orange for x in values],height=.64)
    ax.set_yticks(ys,[x['state']+'  ('+str(x['sites'])+'자리)' for x in values]);ax.invert_yaxis()
    ax.set_xlim(0,100);ax.set_xticks([0,20,40,60,80,100]);ax.set_xlabel('Hellinger 분포 일치도 H (%)',fontsize=11,color=navy)
    ax.set_axisbelow(True);ax.grid(axis='x',alpha=.19)
    for i,v in enumerate(values):ax.text(v['H_percent']-1.8,i,format(v['H_percent'],'.2f'),ha='right',va='center',color='white',fontsize=11,weight='bold')
    for spine in ['top','right','left']:ax.spines[spine].set_visible(False)
    ax.tick_params(axis='y',length=0);ax.spines['bottom'].set_color('#cfdae0')
    fig.text(.56,.94,'B  실제 ibm_hanoi OBC 준비 결과',color=navy,weight='bold',fontsize=14)
    fig.text(.025,.015,'편집부 자체 도해 | 보고 수치: Kumaran et al., DOI 10.1038/s41534-026-01421-w, Fig.3D (AIP, 2026-11-24)',fontsize=8.8,color=gray)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(a.output,dpi=240,facecolor='white');plt.close(fig)

if __name__=='__main__':main()
