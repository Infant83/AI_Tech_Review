"""Redraw selected published TabArena ratings; this does not run the models."""
from pathlib import Path
import argparse
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--png',type=Path,help='Optional raster preview path')
    args=parser.parse_args()
    base=Path(__file__).resolve().parent
    data=json.loads((base/'tabular_foundation_models_20261028.json').read_text())
    rows=data['rows']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'path','svg.hashsalt':'tabular-20261028','axes.labelcolor':'#303b36','text.color':'#26352d'})
    fig,ax=plt.subplots(figsize=(10.8,5.8),facecolor='#fbfaf6')
    ax.set_facecolor('#fbfaf6')
    fig.subplots_adjust(left=.245,right=.955,top=.78,bottom=.25)
    for i,row in enumerate(rows):
        color='#ac7240' if row['model'].startswith('TabPFN') else '#3e6657'
        if row['leakage_warning']:color='#9d5b52'
        ax.errorbar(row['elo'],i,xerr=[[row['ci_lower_error']],[row['ci_upper_error']]],fmt='o',color=color,markersize=7,capsize=4,elinewidth=1.8,markerfacecolor='#fbfaf6' if row['leakage_warning'] else color,markeredgewidth=1.5,zorder=3)
        ax.annotate(str(round(row['elo'])),(row['elo'],i),xytext=(6,7),textcoords='offset points',fontsize=10,color=color)
    labels=[r['model']+(' *' if r['leakage_warning'] else '') for r in rows]
    ax.set_yticks(range(len(rows)),labels)
    ax.invert_yaxis()
    ax.set_ylim(len(rows)-.4,-.7)
    ax.set_xlim(1640,2160)
    ax.set_xticks([1700,1800,1900,2000,2100])
    ax.set_xlabel('Elo rating within this comparison pool',labelpad=9,fontsize=10)
    ax.grid(axis='x',color='#d9ddd4',linewidth=.7,zorder=0)
    ax.tick_params(axis='both',length=0,pad=10,labelsize=11)
    for spine in ax.spines.values():spine.set_visible(False)
    fig.text(.04,.94,'TabArena | selected default configurations',fontsize=19,fontweight='bold')
    fig.text(.04,.885,'51 IID datasets  /  board: 28 October 2026  /  reported 95% confidence intervals',fontsize=10.5,color='#657168')
    fig.text(.04,.08,'* LimiX-2: unresolved contamination warning on two datasets.',fontsize=10,color='#9d5b52')
    fig.text(.04,.035,'GPU evaluations. Mitra-v2 default includes fine-tuning and bagging. AutoML systems are outside this pool.',fontsize=9,color='#657168')
    metadata={'Date':'2026-10-29','Creator':'AI Tech Review; Matplotlib','Title':'Selected TabArena default configurations, 28 October 2026','Description':data['source_url']}
    fig.savefig(base/'tabular_foundation_models_20261028.svg',metadata=metadata,facecolor=fig.get_facecolor())
    svg=base/'tabular_foundation_models_20261028.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    if args.png:fig.savefig(args.png,dpi=160,facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__=='__main__':main()
