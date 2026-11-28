"""Draw reported table facts and an original explanatory workflow; no fitted curves."""
from pathlib import Path
import argparse, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

p=argparse.ArgumentParser();p.add_argument('--font',required=True);a=p.parse_args()
from matplotlib import font_manager
font_manager.fontManager.addfont(a.font)
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=a.font).get_name(),'font.size':13,'axes.spines.top':False,'axes.spines.right':False})
t=Path(__file__).resolve().parents[1];out=t/'artifacts';out.mkdir(exist_ok=True)
navy='#17364b';teal='#247b83';grey='#aab9c1'
facts={'source_doi':'10.1038/s41467-026-79572-9','source':'Article in Press, Table 1, first row','p':.001,'logical_block':12,'ratio_definition':'slope_ratio_squared_in_sqrt_nph_log_pL_fit','RTC_percent':100,'rotated':{'percent':29.2,'minus_pp':4.4,'plus_pp':2.1},'rectangular':{'percent':49.9,'minus_pp':18.3,'plus_pp':5.7},'confidence':'at least 98%','independent_simulation':False}
(out/'figure-data.json').write_text(json.dumps(facts,indent=2))
fig,ax=plt.subplots(figsize=(8.8,3.35));fig.subplots_adjust(left=.26,right=.94,top=.80,bottom=.24)
ax.barh([2,1,0],[100,29.2,49.9],color=[grey,teal,navy],height=.49)
ax.errorbar([29.2,49.9],[1,0],xerr=[[4.4,18.3],[2.1,5.7]],fmt='none',color='#112b3a',capsize=5,lw=1.7)
ax.set_yticks([2,1,0],['RTC reference','Directional: rotated','Directional: rectangular']);ax.set_xlim(0,112);ax.set_xticks([0,25,50,75,100]);ax.set_xlabel('Fitted physical-qubit ratio (% of RTC)')
for y,v in [(2,100),(1,29.2),(0,49.9)]:ax.text(v+3,y+.1,str(v)+'%',fontsize=13,weight='bold')
ax.set_title('p = 0.001 | 12 logical qubits | simulated memory',loc='left',fontsize=14,pad=17,color=navy)
ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0);ax.grid(axis='x',alpha=.16);ax.set_axisbelow(True)
fig.savefig(out/'directional-ratios.png',dpi=220,facecolor='white');plt.close(fig)

fig,ax=plt.subplots(figsize=(8.8,3.45));fig.subplots_adjust(0,0,1,1);ax.set_xlim(0,100);ax.set_ylim(0,100);ax.axis('off')
def box(x,y,w,h,text,color):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.3,rounding_size=2',facecolor=color,edgecolor='none'))
 ax.text(x+w/2,y+h/2,text,ha='center',va='center',color='white',fontsize=12.8,linespacing=1.5)
def arrow(x,y,x2,y2):ax.add_patch(FancyArrowPatch((x,y),(x2,y2),arrowstyle='-|>',mutation_scale=15,lw=1.5,color=navy))
ax.text(4,94,'EGMOF: separate new-property learning from structure pretraining',fontsize=14,color=navy,weight='bold')
box(3,51,21,26,'Target property\n+ labeled data',navy)
box(29,51,23,26,'Prop2Desc\nretrain per property',teal)
box(58,51,39,26,'Desc2MOF\nreuse pretrained structure model',navy)
arrow(24.5,64,28.5,64);arrow(52.5,64,57.5,64)
ax.text(54.5,82,'183 descriptors',ha='center',fontsize=11,color=teal)
ax.text(76,43,'~500,000 hypothetical MOFs for pretraining',ha='center',fontsize=11,color=navy)
arrow(77,50,77,33)
box(29,7,68,24,'Assemble + optimize candidate structures\nH2 benchmark: GCMC | 29 properties: mainly surrogate',teal)
ax.text(3,24,'Classical\nmaterials AI',fontsize=13,color=navy,va='center')
fig.savefig(out/'egmof-modules.png',dpi=220,facecolor='white');plt.close(fig)
print('two original review figures drawn from identified facts')
