#!/usr/bin/env python3
"""Original altermagnetism teaching model and localized scientific figures.

This is an idealized effective Hamiltonian, not a material fit or DFT result.
Run with the repository's scientific Python runtime. Outputs are placed next
 to this script by default; use --output-dir for a disposable verification run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

FONT_PATH = Path.home() / 'Library/Fonts/NanumGothic-Regular.ttf'
if not FONT_PATH.exists():
    raise RuntimeError('The specified NanumGothic font is required for Korean figure output.')
font_manager.fontManager.addfont(str(FONT_PATH))
FONT_NAME = font_manager.FontProperties(fname=str(FONT_PATH)).get_name()
plt.rcParams.update({
    'font.family': FONT_NAME,
    'font.size': 12,
    'axes.unicode_minus': False,
    'mathtext.fontset': 'stix',
    'svg.fonttype': 'path',
    'svg.hashsalt': 'altermagnetism-teaching-2026-11-06',
    'axes.edgecolor': '#A6ADA9',
    'axes.labelcolor': '#263F49',
    'xtick.color': '#52646B',
    'ytick.color': '#52646B',
    'text.color': '#173640',
    'axes.titleweight': 'bold',
    'savefig.facecolor': '#FAF8F2',
})
PAPER = '#FAF8F2'
INK = '#173640'
MUTED = '#52646B'
UP = '#376B98'
DOWN = '#BA674E'
TEAL = '#267C78'
GOLD = '#B5893C'
CMAP = LinearSegmentedColormap.from_list('signed_spin', [DOWN, '#F8FAF7', UP])
T = 1.0
DELTA = 0.35
MU = -1.0
KBT = 0.08
D = 0.45
J = 0.7
T0 = 0.8


def spectrum(kx, ky, delta=DELTA):
    eps = -2 * T * (np.cos(kx) + np.cos(ky))
    field = delta * (np.cos(kx) - np.cos(ky))
    return eps + field, eps - field


def fermi(energy):
    return 1.0 / (np.exp(np.clip((energy - MU) / KBT, -700, 700)) + 1.0)


def two_sublattice(kx, ky, d=D, j=J, t0=T0):
    eps = -2 * T * (np.cos(kx) + np.cos(ky))
    f = np.cos(kx) - np.cos(ky)
    up = np.sqrt(t0**2 + (d * f + j)**2)
    down = np.sqrt(t0**2 + (d * f - j)**2)
    return np.stack((eps - up, eps + up), axis=-1), np.stack((eps - down, eps + down), axis=-1)


def calculate():
    checks = []
    for n in (128, 256, 512):
        k = np.linspace(-np.pi, np.pi, n, endpoint=False)
        x, y = np.meshgrid(k, k, indexing='ij')
        up, down = spectrum(x, y)
        rot_up, rot_down = spectrum(-y, x)
        inv_up, inv_down = spectrum(-x, -y)
        diag_up, diag_down = spectrum(k, k)
        anti_up, anti_down = spectrum(k, -k)
        n_up, n_down = float(fermi(up).mean()), float(fermi(down).mean())
        checks.append({
            'periodic_grid_N_per_axis': n,
            'sample_count': n*n,
            'occupation_per_spin_per_cell': {'up': n_up, 'down': n_down},
            'occupation_difference_up_minus_down': n_up - n_down,
            'max_C4_spin_exchange_residual': float(max(np.max(abs(rot_up-down)), np.max(abs(rot_down-up)))),
            'max_inversion_residual': float(max(np.max(abs(inv_up-up)), np.max(abs(inv_down-down)))),
            'max_diagonal_node_splitting': float(max(np.max(abs(diag_up-diag_down)), np.max(abs(anti_up-anti_down)))),
            'signed_splitting_min': float(np.min(up-down)),
            'signed_splitting_max': float(np.max(up-down)),
        })
    for row in checks:
        for name in ('occupation_difference_up_minus_down', 'max_C4_spin_exchange_residual', 'max_inversion_residual', 'max_diagonal_node_splitting'):
            assert abs(row[name]) < 1e-12, (name, row[name])
    i2 = np.eye(2)
    sx = np.array([[0., 1.], [1., 0.]])
    sz = np.diag([1., -1.])
    exchange_rotation = np.kron(sx, sx)
    rng = np.random.default_rng(20261106)
    points = rng.uniform(-np.pi, np.pi, size=(1024, 2))
    eig_res = symmetry_res = 0.
    for x, y in points:
        eps = -2*T*(np.cos(x)+np.cos(y))
        f = np.cos(x)-np.cos(y)
        h = eps*np.eye(4)+T0*np.kron(sx,i2)+D*f*np.kron(sz,i2)+J*np.kron(sz,sz)
        h_rot = eps*np.eye(4)+T0*np.kron(sx,i2)-D*f*np.kron(sz,i2)+J*np.kron(sz,sz)
        up, down = two_sublattice(x,y)
        exact = np.sort(np.concatenate((up, down)))
        eig_res = max(eig_res, float(np.max(abs(np.linalg.eigvalsh(h)-exact))))
        symmetry_res = max(symmetry_res, float(np.max(abs(exchange_rotation@h@exchange_rotation.T-h_rot))))
    x,y = points.T
    d0_up,d0_down = two_sublattice(x,y,d=0)
    j0_up,j0_down = two_sublattice(x,y,j=0)
    test_up,test_down = two_sublattice(x,y)
    rot_up,rot_down = two_sublattice(-y,x)
    extension = {
        'parameters_in_units_of_t': {'d':D,'J':J,'t0':T0},
        'basis': 'A-up, A-down, B-up, B-down',
        'hamiltonian': 'epsilon I + t0 tau_x + d (cos(kx)-cos(ky)) tau_z + J tau_z sigma_z',
        'analytic_eigenvalues': 'epsilon + eta sqrt(t0^2 + (d f + s J)^2), eta=+/-1, s=+/-1',
        'sample_count':len(points),
        'random_seed':20261106,
        'max_exact_eigenvalue_residual':eig_res,
        'max_C4_matrix_covariance_residual':symmetry_res,
        'max_C4_spin_exchange_residual':float(max(np.max(abs(rot_up-test_down)), np.max(abs(rot_down-test_up)))),
        'max_spin_splitting_when_d_zero':float(np.max(abs(d0_up-d0_down))),
        'max_spin_splitting_when_J_zero':float(np.max(abs(j0_up-j0_down))),
    }
    assert max(extension[key] for key in extension if key.startswith('max_')) < 1e-12
    return {
        'date':'2026-11-06',
        'kind':'Original idealized pedagogical calculation; no material-specific fit.',
        'effective_model': {
            'hamiltonian':'epsilon(k) I + Delta0 (cos(kx)-cos(ky)) sigma_z',
            'epsilon':'-2 t (cos(kx)+cos(ky))',
            't':T,'Delta0':DELTA,'chemical_potential':MU,'kBT':KBT,
            'k_units':'inverse lattice constant; lattice constant=1',
            'energy_units':'t',
            'integration':'Uniform periodic BZ grid [-pi,pi)^2; occupation is mean Fermi occupation per spin and cell.',
            'checks':checks,
            'absolute_occupation_changes_on_refinement':[
                {'from_N':checks[i-1]['periodic_grid_N_per_axis'], 'to_N':checks[i]['periodic_grid_N_per_axis'],
                 'up':abs(checks[i]['occupation_per_spin_per_cell']['up']-checks[i-1]['occupation_per_spin_per_cell']['up'])}
                for i in (1,2)
            ],
            'analytic_Berry_statement': 'A globally fixed spin basis has constant eigenvectors within each spin sector, so this model has no intrinsic charge Hall response. No unique isolated energy-band Berry curvature is asserted at spin-degenerate crossings.',
        },
        'two_sublattice_extension':extension,
        'limits':[
            'No magnetic ground-state selection or self-consistent order parameter.',
            'No material structure, SOC, interactions, defects, lifetime or instrument model.',
            'The finite kBT is an occupation-broadening parameter, not a prediction of finite-temperature magnetic order.',
            'No inference of spin-injection efficiency, switching time or device gain.',
        ],
        'reproduction':{'packages':{'numpy':np.__version__, 'matplotlib':matplotlib.__version__},'text':'SVG text converted to font outlines with NanumGothic and STIX math.'},
    }


LANG = {
    'ko': {
        'title':'방향을 바꾸면 스핀 밴드의 순서가 바뀐다',
        'subtitle':'전체 점유는 보상되어도, 같은 운동량의 에너지는 다를 수 있다',
        'panels':['A   운동량별 에너지 차','B   회전으로 연결되는 등고선','C   경로에 따라 바뀌는 두 밴드'],
        'cbar':r'$E_{\uparrow}-E_{\downarrow}$  [ $t$ ]',
        'up':r'$\uparrow$ 스핀','down':r'$\downarrow$ 스핀',
        'energy':'에너지  [ $t$ ]',
        'contour_note':r'$E_{\uparrow}=\mu$,  $E_{\downarrow}=\mu$',
        'foot':'SOC 없는 2차원 유효 모형 · 격자상수 1 · 에너지 단위 t',
        'param':r'$\Delta_0=0.35t,\quad\mu=-t,\quad k_BT=0.08t$',
        'workflow_title':'계산에서 관측으로: 대칭과 안정성을 함께 검증한다',
        'workflow_sub':'같은 시료 조건에서 여러 관측량을 설명하는 연구 절차',
        'workflow_stages':[
            ('구조와 자기 바닥상태', ['결정상 · 원자 점유 · 자기배열','비자성 · FM · 여러 AFM 비교','경쟁 상태와 구조 안정성']),
            ('SOC 없는 대칭과 밴드', ['스핀 공간군 · 회전 대응','전체 Brillouin 영역 탐색','스핀 분리 · 절점 · 전체 보상']),
            ('실제 조건의 전자구조', ['SOC · 전자 상관 · 쉬운 축','변형률 · 결함 · 표면 · 도메인','수렴과 모형 민감도']),
            ('측정되는 응답', ['분광 · 수송 · 마그논','산란 · 접점 · 도메인 평균','측정 조건과 검출 한계']),
        ],
        'feedback':'실험의 구조 · 결함 · 도메인 정보로 입력을 갱신한다',
        'feedback_mobile':'측정 결과로 입력 갱신',
        'workflow_foot':'리뷰에서 제안한 방법론 · 각 단계는 관측에 맞춰 반복된다',
    },
    'en': {
        'title':'Rotate the direction, exchange the spin bands',
        'subtitle':'Equal total occupation can coexist with unequal energies at the same momentum',
        'panels':['A   Signed spin splitting','B   Rotated equal-energy contours','C   Two spins along a momentum path'],
        'cbar':r'$E_{\uparrow}-E_{\downarrow}$  [ $t$ ]',
        'up':r'$\uparrow$ spin','down':r'$\downarrow$ spin',
        'energy':'Energy  [ $t$ ]',
        'contour_note':r'$E_{\uparrow}=\mu$,  $E_{\downarrow}=\mu$',
        'foot':'2D effective model without SOC · lattice constant 1 · energy unit t',
        'param':r'$\Delta_0=0.35t,\quad\mu=-t,\quad k_BT=0.08t$',
        'workflow_title':'From calculation to observation: test symmetry and stability',
        'workflow_sub':'Explain multiple observables under the same specimen conditions',
        'workflow_stages':[
            ('Structure and ground state', ['Crystal phase · occupancies · order','Compare nonmagnetic, FM, AFM','Competing phases and stability']),
            ('Symmetry without SOC', ['Spin space group · rotation map','Sample the full Brillouin zone','Splitting · nodes · compensation']),
            ('Realistic electronic structure', ['SOC · correlations · easy axis','Strain · defects · surfaces · domains','Convergence and model sensitivity']),
            ('Measured responses', ['Spectra · transport · magnons','Scattering · contacts · domains','Measurement and detection limits']),
        ],
        'feedback':'Update inputs with measured structure, defects and domains',
        'feedback_mobile':'Measurements update inputs',
        'workflow_foot':'Methodology proposed in this review · Iterate against observation',
    },
}


def clean_axes(ax):
    ax.set_facecolor('#FFFFFF')
    ax.spines[['top','right']].set_visible(False)
    ax.tick_params(labelsize=11, length=3)


def k_axes(ax):
    ax.set(xlim=(-np.pi,np.pi), ylim=(-np.pi,np.pi), xlabel=r'$k_x$', ylabel=r'$k_y$')
    ticks=[-np.pi,0,np.pi]
    labels=[r'$-\pi$',r'$0$',r'$\pi$']
    ax.set_xticks(ticks,labels)
    ax.set_yticks(ticks,labels)
    ax.set_aspect('equal')
    ax.tick_params(labelsize=12,length=3)


def model_figure(out,lang,mobile):
    L=LANG[lang]
    if mobile:
        fig=plt.figure(figsize=(6.5,15.4),facecolor=PAPER)
        gs=fig.add_gridspec(3,1,left=.16,right=.9,bottom=.09,top=.885,hspace=.50,height_ratios=[1,1,1.05])
        axes=[fig.add_subplot(gs[i]) for i in range(3)]
        title_size=18 if lang=='ko' else 16
        fig.text(.07,.969,L['title'],fontsize=title_size,fontweight='bold',va='top')
        # A shorter second line avoids turning mobile subtitles into fine print.
        subtitle=L['subtitle'] if lang=='ko' else 'Equal total occupation; direction-dependent energies'
        fig.text(.07,.933,subtitle,fontsize=11.6,color=MUTED,va='top')
        fig.text(.07,.052,L['param'],fontsize=13,color=INK)
        fig.text(.07,.029,L['foot'],fontsize=10.1,color=MUTED)
    else:
        fig=plt.figure(figsize=(15.8,6.0),facecolor=PAPER)
        gs=fig.add_gridspec(1,3,left=.055,right=.98,bottom=.23,top=.73,wspace=.42,width_ratios=[1,1,1.34])
        axes=[fig.add_subplot(gs[i]) for i in range(3)]
        fig.text(.055,.946,L['title'],fontsize=23 if lang=='ko' else 22,fontweight='bold',va='top')
        fig.text(.055,.866,L['subtitle'],fontsize=13,color=MUTED,va='top')
        fig.text(.055,.092,L['param'],fontsize=14,color=INK)
        fig.text(.055,.044,L['foot'],fontsize=11,color=MUTED)
    k=np.linspace(-np.pi,np.pi,513)
    x,y=np.meshgrid(k,k,indexing='xy')
    up,down=spectrum(x,y)
    ax=axes[0]
    image=ax.imshow(up-down,origin='lower',extent=(-np.pi,np.pi,-np.pi,np.pi),cmap=CMAP,vmin=-1.4,vmax=1.4,interpolation='bilinear')
    ax.plot(k,k,color=INK,lw=1.15,ls=(0,(3,3)),alpha=.8)
    ax.plot(k,-k,color=INK,lw=1.15,ls=(0,(3,3)),alpha=.8)
    k_axes(ax)
    if mobile:
        cax=ax.inset_axes([0,-.20,1,.042])
        cbar=fig.colorbar(image,cax=cax,orientation='horizontal')
    else:
        cbar=fig.colorbar(image,ax=ax,orientation='horizontal',fraction=.052,pad=.17,aspect=32)
    cbar.set_ticks([-1.4,0,1.4])
    cbar.ax.tick_params(labelsize=10,length=2)
    if mobile:
        cbar.ax.text(1.04,.5,L['cbar'],ha='left',va='center',fontsize=10,transform=cbar.ax.transAxes)
    else:
        cbar.set_label(L['cbar'],fontsize=11,labelpad=1)
    cbar.outline.set_visible(False)
    ax=axes[1]
    clean_axes(ax)
    ax.contour(x,y,up,levels=[MU],colors=[UP],linewidths=2.4,linestyles='solid')
    ax.contour(x,y,down,levels=[MU],colors=[DOWN],linewidths=2.1,linestyles='dashed')
    ax.axhline(0,lw=.7,color='#D8DEDA',zorder=0)
    ax.axvline(0,lw=.7,color='#D8DEDA',zorder=0)
    k_axes(ax)
    ax.text(.5,1.035,L['contour_note'],ha='center',transform=ax.transAxes,fontsize=12,color=MUTED)
    # Equal-energy contours cross where the analytic spin splitting vanishes.
    theta=np.linspace(0,np.pi/2,80)
    r=2.1
    ax.plot(r*np.cos(theta),r*np.sin(theta),color=TEAL,lw=.9,alpha=.7)
    ax.annotate('',xy=(0,r),xytext=(.22,r-.012),arrowprops={'arrowstyle':'-|>','color':TEAL,'lw':1.0})
    ax.text(.65,.82,r'$C_4$',color=TEAL,transform=ax.transAxes,fontsize=13)
    path=np.array([[0,0],[np.pi,0],[np.pi,np.pi],[0,np.pi],[0,0]])
    nseg=220
    kpath=np.concatenate([np.linspace(path[i],path[i+1],nseg,endpoint=False) for i in range(4)]+[path[-1:]],axis=0)
    abscissa=np.linspace(0,4,len(kpath))
    eu,ed=spectrum(kpath[:,0],kpath[:,1])
    ax=axes[2]
    clean_axes(ax)
    ax.plot(abscissa,eu,color=UP,lw=2.3,label=L['up'])
    ax.plot(abscissa,ed,color=DOWN,lw=1.9,ls=(0,(5,3)),label=L['down'])
    ax.axhline(MU,color=MUTED,lw=.8,ls=(0,(2,3)))
    for pos in (1,2,3):
        ax.axvline(pos,color='#DEE2DF',lw=.8,zorder=0)
    ax.text(3.92,MU+.12,r'$\mu$',ha='right',fontsize=13,color=MUTED)
    ax.set(xlim=(0,4),ylim=(-4.3,4.3),ylabel=L['energy'])
    ax.set_xticks(range(5),[r'$\Gamma$',r'$X$',r'$M$',r'$Y$',r'$\Gamma$'])
    ax.set_yticks([-4,-2,0,2,4])
    if mobile:
        ax.legend(loc='upper left',ncol=1,frameon=False,fontsize=12,handlelength=2.0)
    else:
        ax.legend(loc='lower center',bbox_to_anchor=(.5,-.30),ncol=2,frameon=False,fontsize=12,handlelength=2.0,columnspacing=1.2)
    for i,ax in enumerate(axes):
        if mobile:
            ax.set_title(L['panels'][i],loc='left',fontsize=14.5 if lang=='ko' else 13.5,pad=35 if i==1 else 14)
        else:
            ax.set_title(L['panels'][i],loc='left',fontsize=14 if lang=='ko' else 13,pad=32 if i==1 else 18)
    suffix='_mobile' if mobile else ''
    target=out/f'spin-model{suffix}_{lang}.svg'
    fig.savefig(target,metadata={'Date':'2026-11-06','Creator':'AI Tech Review; original analytical teaching model'})
    plt.close(fig)


def arrow(ax,a,b,color=TEAL,scale=18,lw=1.7,style='-|>'):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle=style,mutation_scale=scale,linewidth=lw,color=color,transform=ax.transAxes))


def workflow_figure(out,lang,mobile):
    L=LANG[lang]
    colors=[GOLD,DOWN,UP,TEAL]
    if mobile:
        fig=plt.figure(figsize=(6.5,12.8),facecolor=PAPER)
        ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
        title=L['workflow_title'] if lang=='ko' else 'From calculation to observation'
        fig.text(.065,.963,title,fontsize=17.7 if lang=='ko' else 19,fontweight='bold',va='top')
        subtitle=L['workflow_sub'] if lang=='ko' else 'Test symmetry, stability and measured responses'
        fig.text(.065,.926,subtitle,fontsize=11.7,color=MUTED,va='top')
        box_x=.07;box_w=.76;box_h=.163
        tops=[.86,.66,.46,.26]
        for i,(title,lines) in enumerate(L['workflow_stages']):
            bottom=tops[i]-box_h
            patch=FancyBboxPatch((box_x,bottom),box_w,box_h,boxstyle='round,pad=0.008,rounding_size=0.014',transform=ax.transAxes,facecolor='#FFFFFF',edgecolor='#D4DCD6',linewidth=1.1)
            ax.add_patch(patch)
            ax.text(box_x+.035,tops[i]-.035,f'{i+1:02d}',transform=ax.transAxes,color=colors[i],fontsize=15,fontweight='bold',va='center')
            ax.text(box_x+.123,tops[i]-.035,title,transform=ax.transAxes,fontsize=14.5 if lang=='ko' else 13.0,fontweight='bold',va='center')
            for j,line in enumerate(lines):
                ax.text(box_x+.045,tops[i]-.078-j*.031,line,transform=ax.transAxes,fontsize=12.7 if lang=='ko' else 11.5,va='center',color=MUTED)
            if i<3:
                arrow(ax,(box_x+box_w/2,bottom-.010),(box_x+box_w/2,tops[i+1]+.012),scale=17)
        # A return bus ties the measured response back to specimen inputs.
        last_mid=tops[3]-box_h/2
        first_mid=tops[0]-box_h/2
        ax.plot([.84,.91,.91,.84],[last_mid,last_mid,first_mid,first_mid],color=TEAL,lw=1.5,transform=ax.transAxes)
        arrow(ax,(.89,first_mid),(.837,first_mid),scale=15)
        ax.text(.925,.49,'피드백' if lang=='ko' else 'FEEDBACK',rotation=90,transform=ax.transAxes,color=TEAL,fontsize=12,ha='center',va='center',bbox={'boxstyle':'round,pad=.35','facecolor':PAPER,'edgecolor':'none'})
        fig.text(.07,.049,L['feedback_mobile'],fontsize=12,color=TEAL)
        foot=L['workflow_foot'] if lang=='ko' else 'Proposed methodology · Iterate against observation'
        fig.text(.07,.023,foot,fontsize=10.4,color=MUTED)
    else:
        fig=plt.figure(figsize=(15.8,5.6),facecolor=PAPER)
        ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
        fig.text(.045,.925,L['workflow_title'],fontsize=23 if lang=='ko' else 21,fontweight='bold',va='top')
        fig.text(.045,.815,L['workflow_sub'],fontsize=13,color=MUTED,va='top')
        xs=[.045,.285,.525,.765];w=.195;bottom=.31;h=.37
        for i,(title,lines) in enumerate(L['workflow_stages']):
            patch=FancyBboxPatch((xs[i],bottom),w,h,boxstyle='round,pad=0.008,rounding_size=0.014',transform=ax.transAxes,facecolor='#FFFFFF',edgecolor='#D4DCD6',linewidth=1.1)
            ax.add_patch(patch)
            ax.text(xs[i]+.015,bottom+h-.052,f'{i+1:02d}',transform=ax.transAxes,color=colors[i],fontsize=16,fontweight='bold',va='center')
            ax.text(xs[i]+.015,bottom+h-.126,title,transform=ax.transAxes,fontsize=14.5 if lang=='ko' else 12.4,fontweight='bold',va='center')
            for j,line in enumerate(lines):
                ax.text(xs[i]+.015,bottom+h-.205-j*.057,line,transform=ax.transAxes,fontsize=12.7 if lang=='ko' else 11.4,va='center',color=MUTED)
            if i<3:
                arrow(ax,(xs[i]+w+.012,bottom+h/2),(xs[i+1]-.012,bottom+h/2))
        left=xs[0]+w/2;right=xs[-1]+w/2
        ax.plot([right,right,left,left],[bottom-.012,.19,.19,bottom-.012],transform=ax.transAxes,color=TEAL,lw=1.5)
        arrow(ax,(left,.23),(left,bottom-.012),scale=16)
        ax.text(.5,.19,L['feedback'],transform=ax.transAxes,ha='center',va='center',fontsize=13,color=TEAL,bbox={'boxstyle':'round,pad=.6','facecolor':PAPER,'edgecolor':'none'})
        fig.text(.045,.06,L['workflow_foot'],fontsize=11,color=MUTED)
    suffix='_mobile' if mobile else ''
    target=out/f'calculation-to-observation{suffix}_{lang}.svg'
    fig.savefig(target,metadata={'Date':'2026-11-06','Creator':'AI Tech Review; original editorial research methodology diagram'})
    plt.close(fig)


def model_print_figure(out,lang):
    """A4 figure: two upper maps and a full-width lower band plot.

    At 170 mm width, a 14 pt label in this 11-inch canvas prints at 8.52 pt.
    The 9-inch canvas then occupies 139 mm, before the article caption.
    """
    L=LANG[lang]
    fig=plt.figure(figsize=(11,9),facecolor=PAPER)
    fig.text(.07,.966,L['title'],fontsize=20,fontweight='bold',va='top')
    subtitle=L['subtitle'] if lang=='ko' else 'Equal total occupation; direction-dependent energies'
    fig.text(.07,.918,subtitle,fontsize=14,color=MUTED,va='top')
    ax_map=fig.add_axes([.10,.51,.32,.34])
    ax_contour=fig.add_axes([.62,.51,.29,.34])
    ax_band=fig.add_axes([.10,.105,.82,.275])
    k=np.linspace(-np.pi,np.pi,513)
    x,y=np.meshgrid(k,k,indexing='xy')
    up,down=spectrum(x,y)
    image=ax_map.imshow(up-down,origin='lower',extent=(-np.pi,np.pi,-np.pi,np.pi),cmap=CMAP,vmin=-1.4,vmax=1.4,interpolation='bilinear')
    ax_map.plot(k,k,color=INK,lw=1.3,ls=(0,(3,3)),alpha=.8)
    ax_map.plot(k,-k,color=INK,lw=1.3,ls=(0,(3,3)),alpha=.8)
    cax=fig.add_axes([.445,.53,.014,.30])
    cbar=fig.colorbar(image,cax=cax,orientation='vertical')
    cbar.set_ticks([-1.4,0,1.4])
    cbar.ax.tick_params(labelsize=14,length=3)
    cbar.set_label(L['cbar'],fontsize=14,labelpad=5)
    cbar.outline.set_visible(False)
    clean_axes(ax_contour)
    ax_contour.contour(x,y,up,levels=[MU],colors=[UP],linewidths=2.6,linestyles='solid')
    ax_contour.contour(x,y,down,levels=[MU],colors=[DOWN],linewidths=2.3,linestyles='dashed')
    ax_contour.axhline(0,lw=.8,color='#D8DEDA',zorder=0)
    ax_contour.axvline(0,lw=.8,color='#D8DEDA',zorder=0)
    theta=np.linspace(0,np.pi/2,80)
    r=2.1
    ax_contour.plot(r*np.cos(theta),r*np.sin(theta),color=TEAL,lw=1.1,alpha=.8)
    ax_contour.annotate('',xy=(0,r),xytext=(.25,r-.015),arrowprops={'arrowstyle':'-|>','color':TEAL,'lw':1.1})
    ax_contour.text(.66,.81,r'$C_4$',color=TEAL,transform=ax_contour.transAxes,fontsize=15)
    ax_contour.text(.5,.035,L['contour_note'],ha='center',va='bottom',transform=ax_contour.transAxes,fontsize=14,color=MUTED,bbox={'facecolor':'white','edgecolor':'none','alpha':.9,'pad':1})
    for i,ax in enumerate((ax_map,ax_contour)):
        k_axes(ax)
        ax.tick_params(labelsize=14,length=3)
        ax.set_xlabel(r'$k_x$',fontsize=14,labelpad=3)
        ax.set_ylabel(r'$k_y$',fontsize=14,labelpad=3)
        ax.set_title(L['panels'][i],loc='left',fontsize=16,pad=14)
    path=np.array([[0,0],[np.pi,0],[np.pi,np.pi],[0,np.pi],[0,0]])
    kpath=np.concatenate([np.linspace(path[i],path[i+1],220,endpoint=False) for i in range(4)]+[path[-1:]],axis=0)
    abscissa=np.linspace(0,4,len(kpath))
    eu,ed=spectrum(kpath[:,0],kpath[:,1])
    clean_axes(ax_band)
    ax_band.plot(abscissa,eu,color=UP,lw=2.4,label=L['up'])
    ax_band.plot(abscissa,ed,color=DOWN,lw=2.1,ls=(0,(5,3)),label=L['down'])
    ax_band.axhline(MU,color=MUTED,lw=.9,ls=(0,(2,3)))
    for pos in (1,2,3):
        ax_band.axvline(pos,color='#DEE2DF',lw=.8,zorder=0)
    ax_band.text(3.94,MU+.16,r'$\mu$',ha='right',fontsize=14,color=MUTED)
    ax_band.set(xlim=(0,4),ylim=(-4.3,4.3))
    ax_band.set_ylabel(L['energy'],fontsize=14,labelpad=5)
    ax_band.set_xticks(range(5),[r'$\Gamma$',r'$X$',r'$M$',r'$Y$',r'$\Gamma$'])
    ax_band.set_yticks([-4,-2,0,2,4])
    ax_band.tick_params(labelsize=14,length=3)
    ax_band.set_title(L['panels'][2],loc='left',fontsize=16,pad=13)
    ax_band.legend(loc='upper left',ncol=2,frameon=False,fontsize=14,handlelength=2.0,columnspacing=1.2)
    fig.text(.07,.045,L['param'],fontsize=14,color=INK)
    fig.text(.07,.012,L['foot'],fontsize=14,color=MUTED)
    fig.savefig(out/f'spin-model_print_{lang}.svg',metadata={'Date':'2026-11-06','Creator':'AI Tech Review; original analytical teaching model; A4 print layout'})
    plt.close(fig)


def workflow_print_figure(out,lang):
    """A4 research workflow with 2x2 boxes and a visible feedback loop."""
    L=LANG[lang]
    fig=plt.figure(figsize=(11,9),facecolor=PAPER)
    ax=fig.add_axes([0,0,1,1]);ax.set_axis_off()
    title=L['workflow_title'] if lang=='ko' else 'From calculation to observation'
    subtitle=L['workflow_sub'] if lang=='ko' else 'Test symmetry, stability and measured responses'
    fig.text(.07,.965,title,fontsize=20,fontweight='bold',va='top')
    fig.text(.07,.914,subtitle,fontsize=14,color=MUTED,va='top')
    positions=[(.10,.53),(.56,.53),(.10,.13),(.56,.13)]
    w=.36;h=.29
    colors=[GOLD,DOWN,UP,TEAL]
    for i,((x,y),(heading,lines)) in enumerate(zip(positions,L['workflow_stages'])):
        patch=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008,rounding_size=0.014',transform=ax.transAxes,facecolor='#FFFFFF',edgecolor='#D4DCD6',linewidth=1.2)
        ax.add_patch(patch)
        ax.text(x+.025,y+h-.046,f'{i+1:02d}',transform=ax.transAxes,color=colors[i],fontsize=17,fontweight='bold',va='center')
        ax.text(x+.025,y+h-.101,heading,transform=ax.transAxes,fontsize=16,fontweight='bold',va='center')
        for j,line in enumerate(lines):
            ax.text(x+.025,y+h-.166-j*.045,line,transform=ax.transAxes,fontsize=14.5,va='center',color=MUTED)
    # Serpentine reading order, 1 -> 2 -> 3 -> 4.
    arrow(ax,(.472,.675),(.548,.675),scale=19,lw=1.8)
    ax.plot([.74,.74,.28,.28],[.518,.475,.475,.432],transform=ax.transAxes,color=TEAL,lw=1.8)
    arrow(ax,(.28,.457),(.28,.432),scale=19,lw=1.8)
    arrow(ax,(.472,.275),(.548,.275),scale=19,lw=1.8)
    # Measured specimen information closes the loop to stage 1.
    ax.plot([.74,.74,.045,.045,.088],[.118,.073,.073,.675,.675],transform=ax.transAxes,color=TEAL,lw=1.6)
    arrow(ax,(.065,.675),(.088,.675),scale=18,lw=1.6)
    feedback=L['feedback'] if lang=='ko' else 'Measured structure, defects and domains update the inputs'
    ax.text(.5,.073,feedback,transform=ax.transAxes,ha='center',va='center',fontsize=14,color=TEAL,bbox={'boxstyle':'round,pad=.4','facecolor':PAPER,'edgecolor':'none'})
    foot=L['workflow_foot'] if lang=='ko' else 'Proposed methodology: iterate against observation'
    fig.text(.07,.021,foot,fontsize=14,color=MUTED)
    fig.savefig(out/f'calculation-to-observation_print_{lang}.svg',metadata={'Date':'2026-11-06','Creator':'AI Tech Review; original research methodology diagram; A4 print layout'})
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output-dir',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--verify-only',action='store_true')
    parser.add_argument('--print-only',action='store_true',help='Generate only print SVGs; preserve web/mobile assets and numerical results.')
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    if args.print_only:
        for lang in ('ko','en'):
            model_print_figure(args.output_dir,lang)
            workflow_print_figure(args.output_dir,lang)
        normalize_svg_output(args.output_dir)
        print('Generated four print SVGs; existing web/mobile assets and model results were preserved.')
        return
    results=calculate()
    (args.output_dir/'model-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    if not args.verify_only:
        for lang in ('ko','en'):
            model_print_figure(args.output_dir,lang)
            workflow_print_figure(args.output_dir,lang)
            for mobile in (False,True):
                model_figure(args.output_dir,lang,mobile)
                workflow_figure(args.output_dir,lang,mobile)
        normalize_svg_output(args.output_dir)
    print(json.dumps({'occupations':results['effective_model']['checks'],'two_sublattice_extension':results['two_sublattice_extension']},ensure_ascii=False,indent=2))


def normalize_svg_output(folder):
    for svg in folder.glob('*.svg'):
        svg.write_text('\n'.join(line.rstrip(' \t') for line in svg.read_text().splitlines())+'\n')


if __name__=='__main__':
    main()
