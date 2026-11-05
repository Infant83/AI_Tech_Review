from pathlib import Path
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

BASE = Path(__file__).resolve().parent
OUT = BASE
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.titlesize':19,
                     'axes.labelsize':14,'svg.hashsalt':'mlff-20261106'})
R = 0.00198720425864083  # kcal mol^-1 K^-1, CODATA R converted with 1 kcal=4184 J
threshold = R * 300 * math.log(2)
assert abs(threshold - 0.4132275) < 1e-6
assert abs(math.exp(1/(R*300)) - 5.3516153) < 1e-6
rows = []
fig, ax = plt.subplots(figsize=(10.6,5.4), layout='constrained')
errors = np.linspace(0,2,301)
for temp, color in [(300,'#117b7a'),(600,'#b97441'),(1000,'#526b94')]:
    factors = np.exp(errors/(R*temp))
    ax.plot(errors, factors, lw=2.6, label=f'{temp} K', color=color)
    rows.append({'temperature_K':temp,'factor_at_1_kcal_mol':math.exp(1/(R*temp)),
                 'barrier_error_for_factor2_kcal_mol':R*temp*math.log(2)})
ax.axhline(2, color='#697b80', lw=1.2, ls='--')
ax.plot([threshold],[2],marker='o',color='#117b7a',ms=7)
ax.annotate('300 K: factor 2 at 0.413 kcal/mol',xy=(threshold,2),xytext=(.63,3.1),
            arrowprops={'arrowstyle':'->','color':'#52636b'},fontsize=11)
ax.set_yscale('log');ax.set_ylim(1,32);ax.set_xlim(0,2)
ax.set_yticks([1,2,5,10,20]);ax.set_yticklabels(['1','2','5','10','20'])
ax.set_xlabel('Absolute free-energy barrier error (kcal/mol)')
ax.set_ylabel('Rate mismatch factor (log scale)')
ax.set_title('A useful accuracy threshold depends on the observable',loc='left',weight='bold',pad=13)
ax.legend(frameon=False);ax.grid(axis='y',alpha=.2)
for s in ['top','right']:ax.spines[s].set_visible(False)
fig.text(.015,-.06,'Analytic illustration: exp(|error|/RT), with the same kinetic prefactor.\nNo MLFF benchmark, barrier measurement or simulated trajectory is shown.',fontsize=10.5,color='#52636b')
for ext in ['png','svg']:fig.savefig(OUT/f'barrier_accuracy.{ext}',dpi=180,bbox_inches='tight',metadata={'Creator':'AI Tech Review; analytic illustration'})
plt.close(fig)
(OUT/'analytic-values.json').write_text(json.dumps({'R_kcal_mol_K':R,'model':'Eyring barrier-only sensitivity with unchanged prefactor','values':rows},indent=2)+'\n')

fig, ax = plt.subplots(figsize=(12,5.5));ax.set_xlim(0,12);ax.set_ylim(0,5.5);ax.axis('off')
boxes=[(.35,3.2,'Electronic reference','functional, basis, charge/spin'),
       (4.25,3.2,'Training structures','chemistry and conditions'),
       (8.15,3.2,'Learned energy','Eθ(R): physics + fitted terms'),
       (8.15,.75,'Conservative forces','Fᵢ = −∇ᵢEθ'),
       (4.25,.75,'Molecular dynamics','integration and sampling'),
       (.35,.75,'Target observable','density, ΔG, diffusion, rates')]
for x,y,title,sub in boxes:
    p=FancyBboxPatch((x,y),3.5,1.15,boxstyle='round,pad=.04,rounding_size=.09',
                    facecolor='#edf5f3',edgecolor='#4c8584',lw=1.2)
    ax.add_patch(p);ax.text(x+1.75,y+.74,title,ha='center',va='center',weight='bold',fontsize=13.5)
    ax.text(x+1.75,y+.31,sub,ha='center',va='center',fontsize=10.5,color='#45626c')
for a,b in [((3.9,3.77),(4.2,3.77)),((7.8,3.77),(8.1,3.77)),((9.9,3.1),(9.9,2.0)),
            ((8.1,1.32),(7.8,1.32)),((4.2,1.32),(3.9,1.32))]:
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=13,lw=1.5,color='#405c66'))
ax.text(.35,5.0,'From an electronic reference to a target observable',fontsize=19,weight='bold',color='#18343e')
ax.text(6.0,4.62,'Reference, coverage, force prediction, integration and sampling each affect the result.',
        ha='center',va='center',fontsize=11.6,color='#6b4936')
ax.text(.35,.12,'Review schematic. Agreement with a reference and agreement with the target experiment are distinct tests.',
        fontsize=10.4,color='#52636b')
for ext in ['png','svg']:fig.savefig(OUT/f'simulation_workflow.{ext}',dpi=180,bbox_inches='tight',metadata={'Creator':'AI Tech Review; conceptual schematic'})
plt.close(fig)
print('Created two original explanatory PNG/SVG figures and checked analytic values.')
