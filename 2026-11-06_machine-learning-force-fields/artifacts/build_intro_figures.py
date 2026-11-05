from pathlib import Path
import json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

B = Path(__file__).resolve().parent
O = B
O.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.titlesize':17,
                     'axes.labelsize':13,'svg.hashsalt':'mlff-intro-v2-20261106'})

def energy(r): return 4*(r**-12-r**-6)
def radial_force(r): return 24*(2*r**-13-r**-7)
req = 2**(1/6)
assert abs(energy(req)+1)<1e-12 and abs(radial_force(req))<1e-12
checks=[]
for r in [.98,1.0,1.15,1.5,2.2]:
    h=1e-6
    numeric=-(energy(r+h)-energy(r-h))/(2*h)
    assert math.isclose(numeric,radial_force(r),rel_tol=2e-8,abs_tol=1e-8)
    checks.append({'r_over_sigma':r,'U_over_epsilon':energy(r),
                   'F_over_epsilon_per_sigma':radial_force(r),'force_fd_residual':numeric-radial_force(r)})

x=np.linspace(.95,2.8,800)
fig, axs=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
for ax in axs:
    ax.axhline(0,color='#829094',lw=1)
    ax.axvline(req,color='#b08b5b',lw=1.3,ls='--')
    ax.set_xlim(.95,2.8);ax.set_xlabel('Separation r / σ');ax.spines[['top','right']].set_visible(False)
axs[0].plot(x,energy(x),color='#117b7a',lw=2.8)
axs[0].plot([req],[-1],marker='o',color='#b08b5b')
axs[0].set_ylim(-1.3,2.2);axs[0].set_ylabel('Potential energy U / ε')
axs[0].set_title('The energy landscape',loc='left',weight='bold')
axs[0].annotate(r'Minimum: $r=2^{1/6}\sigma$, $U=-\epsilon$',xy=(req,-1),xytext=(1.45,-.82),fontsize=10,
                arrowprops={'arrowstyle':'->','color':'#7b6445'})
axs[0].annotate('U = 0 at r = σ',xy=(1,0),xytext=(1.52,.75),fontsize=10,
                arrowprops={'arrowstyle':'->','color':'#52636b'})
axs[1].plot(x,radial_force(x),color='#117b7a',lw=2.8)
axs[1].set_ylim(-4,60);axs[1].set_ylabel('Radial force Fᵣ / (ε/σ)')
axs[1].set_title('Its negative slope is the force',loc='left',weight='bold')
axs[1].text(1.38,45,'Fᵣ > 0: repulsion',fontsize=11,color='#117b7a')
axs[1].text(1.38,32,'Fᵣ < 0: attraction',fontsize=11,color='#b97441')
zoom=axs[1].inset_axes([.48,.14,.48,.28])
zoom.plot(x,radial_force(x),color='#117b7a',lw=1.8)
zoom.axhline(0,color='#829094',lw=.7)
zoom.axvline(req,color='#b08b5b',lw=.8,ls='--')
zoom.set_xlim(1.05,2.8);zoom.set_ylim(-3,1)
zoom.set_title('Attractive region (zoom)',fontsize=9,pad=4)
zoom.tick_params(labelsize=8);zoom.set_yticks([-2,0]);zoom.spines[['top','right']].set_visible(False)
fig.text(.015,-.06,'Analytic Lennard-Jones pair illustration. Fᵣ = −dU/dr; positive Fᵣ increases separation.\nReduced units; no fitted material, measured data, cutoff or many-body effects.',fontsize=10,color='#52636b')
for ext in ['png','svg']:fig.savefig(O/f'lj_energy_force.{ext}',dpi=180,bbox_inches='tight',metadata={'Creator':'AI Tech Review; analytic pair illustration'})
plt.close(fig)

def propagate(dt,T=4.):
    # Two unit masses in 1D with zero center-of-mass velocity; reduced mass = 1/2.
    steps=round(T/dt);r=1.4;v=0.;mu=.5
    out=np.empty((steps+1,4))
    out[0]=[0,r,energy(r),.5*mu*v*v]
    f=radial_force(r)
    for k in range(1,steps+1):
        vhalf=v+.5*dt*f/mu
        r+=dt*vhalf
        f=radial_force(r)
        v=vhalf+.5*dt*f/mu
        out[k]=[k*dt,r,energy(r),.5*mu*v*v]
    return out

a=propagate(.001);fine=propagate(.0005)
e0=a[0,2]
drift=float(np.max(np.abs(a[:,2]+a[:,3]-e0)))
drift_fine=float(np.max(np.abs(fine[:,2]+fine[:,3]-e0)))
assert drift<1e-4 and drift_fine<drift/3.8
assert np.min(a[:,1])<req<np.max(a[:,1])
fig,axs=plt.subplots(2,1,figsize=(10.5,6),sharex=True,layout='constrained',height_ratios=[1,1.2])
axs[0].plot(a[:,0],a[:,1],color='#117b7a',lw=1.8)
axs[0].axhline(req,color='#b08b5b',ls='--',lw=1.2,label='Energy-minimum separation')
axs[0].set_ylabel('Separation r / σ');axs[0].legend(frameon=False,loc='upper right',fontsize=10)
axs[0].set_title('MD moves through a minimum and exchanges energy',loc='left',weight='bold')
axs[1].plot(a[:,0],a[:,2],label='Potential U',color='#117b7a',lw=1.6)
axs[1].plot(a[:,0],a[:,3],label='Kinetic K',color='#b97441',lw=1.6)
axs[1].plot(a[:,0],a[:,2]+a[:,3],label='Total K + U',color='#526b94',lw=2)
axs[1].set_ylabel('Energy / ε');axs[1].set_xlabel('Reduced time t / (σ√(m/ε))')
axs[1].legend(frameon=False,ncol=3,loc='upper right',fontsize=10)
for ax in axs:ax.spines[['top','right']].set_visible(False);ax.set_xlim(0,4)
fig.text(.015,-.055,'Review calculation: isolated equal-mass LJ pair, r(0)=1.4σ, relative velocity 0, velocity Verlet, Δt=0.001.\nNo thermostat, damping, material fit or many-body environment. Finite-step energy error was checked by halving Δt.',fontsize=10,color='#52636b')
for ext in ['png','svg']:fig.savefig(O/f'lj_md_energy.{ext}',dpi=180,bbox_inches='tight',metadata={'Creator':'AI Tech Review; educational two-particle calculation'})
plt.close(fig)
(O/'intro-calculation-checks.json').write_text(json.dumps({'model':'isolated LJ pair in reduced units',
 'reference':'LAMMPS lj/cut formula without a cutoff','force_gradient_checks':checks,
 'minimum_r':req,'timestep':.001,'max_absolute_total_energy_error':drift,
 'half_timestep_max_error':drift_fine,'error_reduction_factor':drift/drift_fine,
 'r_range':[float(a[:,1].min()),float(a[:,1].max())]},indent=2)+'\n')
np.savetxt(O/'lj_md_trace.csv',a[::10],delimiter=',',header='reduced_time,r_over_sigma,U_over_epsilon,K_over_epsilon',comments='')
print('Created two deterministic introductory figures; finite-difference forces and timestep convergence checked.')
