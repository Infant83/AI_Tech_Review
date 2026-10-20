"""Deterministic teaching plots, calculated from equations in lectures 2, 9 and 18.

These are not measured device data or reproductions of published paper figures.
Requires NumPy and Matplotlib 3.10.7; no network access during figure generation.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
QA = ROOT / 'tmp/pdfs'
QA.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.labelsize': 11,
    'axes.titlesize': 13, 'axes.titleweight': 'bold', 'axes.spines.top': False,
    'axes.spines.right': False, 'svg.fonttype': 'path', 'svg.hashsalt': 'qml-notes-v1',
    'axes.edgecolor': '#aebfc4', 'text.color': '#173440', 'axes.labelcolor': '#173440',
    'xtick.color': '#526b74', 'ytick.color': '#526b74', 'figure.facecolor': 'white',
    'savefig.facecolor': 'white', 'grid.alpha': .25,
})

def save(fig, name):
    fig.savefig(OUT / f'{name}.svg', bbox_inches='tight', metadata={'Date': None, 'Creator': 'AI Tech Review: deterministic teaching calculation'})
    fig.savefig(QA / f'{name}.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

S = np.geomspace(16, 1_000_000, 300)
fig, ax = plt.subplots(figsize=(8.2, 4.5), layout='constrained')
ax.loglog(S, np.sqrt(.75/S), color='#126f79', lw=2.3, label=r'$f=0.5$: $\sqrt{(1-f^2)/S}$')
ax.loglog(S, 1/np.sqrt(S), color='#a65d37', lw=2, ls='--', label=r'Upper bound: $1/\sqrt{S}$')
ax.scatter([1000], [np.sqrt(.75/1000)], color='#126f79', zorder=3)
ax.annotate('1,000 shots: SE = 0.0274', (1000, np.sqrt(.75/1000)), xytext=(1800, .08), arrowprops={'arrowstyle':'-', 'color':'#60747a'}, fontsize=10)
ax.set(xlabel='Independent shots per circuit, S', ylabel='Standard error of the sample mean', title='More shots reduce sampling error as a square root')
ax.grid(True, which='major'); ax.legend(frameon=False, loc='lower left', fontsize=10)
save(fig, 'shot-error')

n = np.arange(1, 41)
global_variance = (1/8)*(3/8)**(n-1)
local_variance = 1/(8*n.astype(float)**2)
fig, ax = plt.subplots(figsize=(8.2, 4.5), layout='constrained')
ax.semilogy(n, global_variance, color='#a65d37', lw=2.3, label=r'Global cost: $(1/8)(3/8)^{n-1}$')
ax.semilogy(n, local_variance, color='#126f79', lw=2.3, ls='--', label=r'Local cost: $1/(8n^2)$')
ax.set(xlabel='Number of independent Ry qubits, n', ylabel='Variance of the first parameter gradient', title='Cost locality changes gradient scaling, without entanglement', xlim=(1,40))
ax.grid(True, which='major'); ax.legend(frameon=False, fontsize=10, loc='lower left')
save(fig, 'gradient-variance')

w = np.arange(0, 101)
p = .01
signal = (1-p)**w
fig, axes = plt.subplots(1, 2, figsize=(9, 4.25), layout='constrained')
axes[0].plot(w, signal, color='#126f79', lw=2.4)
axes[0].set(xlabel='Pauli weight, w', ylabel='Signal factor', title=r'Signal: $(1-p)^w$', ylim=(0,1.05))
axes[0].annotate('w = 100: 0.366', (100,signal[-1]), xytext=(30,.19), arrowprops={'arrowstyle':'-', 'color':'#60747a'}, fontsize=10)
axes[1].plot(w, signal**-2, color='#a65d37', lw=2.4, ls='--')
axes[1].set(xlabel='Pauli weight, w', ylabel='Worst-case variance-bound multiplier', title=r'Inverse correction: $(1-p)^{-2w}$', ylim=(.5,8.3))
axes[1].annotate('w = 100: 7.46', (100,signal[-1]**-2), xytext=(24,6.4), arrowprops={'arrowstyle':'-', 'color':'#60747a'}, fontsize=10)
for ax in axes: ax.grid(True, which='major')
fig.suptitle('One layer of local depolarization, p = 0.01', fontsize=13, fontweight='bold')
save(fig, 'signal-attenuation')

manifest = {
    'version': 1, 'kind': 'deterministic teaching figures', 'date': '2026-10-20',
    'not_device_data': True, 'python_packages': {'numpy': np.__version__, 'matplotlib': matplotlib.__version__},
    'figures': [
        {'file': 'shot-error.svg', 'lecture': 2, 'source': 'Var(mean)=(1-f^2)/S for independent +/-1 outcomes', 'f': .5, 'shots_range': [16,1000000]},
        {'file': 'gradient-variance.svg', 'lecture': 9, 'source': 'Independent uniform Ry angles and global versus local projector costs; derived in lecture 9', 'n_range': [1,40]},
        {'file': 'signal-attenuation.svg', 'lecture': 18, 'source': 'D_p(rho)=(1-p)rho+pI/2 on each qubit; Pauli weight w; inverse correction variance-bound factor', 'p': .01, 'weight_range': [0,100]},
    ],
}
(OUT/'figure-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print('Created three analytic teaching figures and provenance manifest.')
