"""Review-authored harmonic-chain example, independently checked in mode/atom coordinates.

NumPy only. No DFT, learned potential, material fit, or source-paper reproduction.
Four equal masses on a periodic 1-D chain. u_i=q e_i, sum(e_i^2)=1.
"""
from pathlib import Path
import json, math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
EV_J=1.602176634e-19
ANGSTROM_M=1e-10
AMU_KG=1.66053906892e-27
N=4
MASS_AMU=28.
U0_EV=-10.
MODE=np.array([1.,-1.,1.,-1.])/2
EDGES=[(0,1),(1,2),(2,3),(3,0)]

def energy(u,K):
    return U0_EV+.5*K*sum((u[b]-u[a])**2 for a,b in EDGES)

def forces(u,K):
    return -K*(2*u-np.roll(u,1)-np.roll(u,-1))

def build():
    assert abs(MODE@MODE-1)<1e-14
    lap=np.zeros((N,N))
    for a,b in EDGES:
        lap[a,a]+=1;lap[b,b]+=1;lap[a,b]-=1;lap[b,a]-=1
    assert np.max(np.abs(np.linalg.eigvalsh(lap)-[0,2,2,4]))<1e-14
    assert np.max(np.abs(lap@MODE-4*MODE))<1e-14
    effective_mass=MASS_AMU*float(MODE@MODE)
    records=[]
    for label,K in [('reference',1.),('softened',.81)]:
        hessian=K*lap
        k=float(MODE@hessian@MODE)
        omega=math.sqrt(k*EV_J/ANGSTROM_M**2/(effective_mass*AMU_KG))
        frequency=omega/(2*math.pi)/1e12
        assert abs(k-4*K)<1e-14
        # Harmonic energy, finite difference force and Hessian, direct mode projection.
        for q in [-.15,-.1,-.03,0,.02,.1,.15]:
            u=q*MODE
            assert abs(energy(u,K)-(U0_EV+.5*k*q*q))<3e-15
            assert abs(float(MODE@forces(u,K))+k*q)<1e-14
            step=1e-5
            fd=-(energy((q+step)*MODE,K)-energy((q-step)*MODE,K))/(2*step)
            assert abs(fd+k*q)<2e-10
        for step in [.01,.005,.002]:
            Hfd=np.column_stack([-(forces(np.eye(N)[j]*step,K)-forces(-np.eye(N)[j]*step,K))/(2*step) for j in range(N)])
            assert np.max(np.abs(Hfd-hessian))<1e-13
        # Independent generalised eigenvalue solve (equal masses) vs mode expression.
        dyn=hessian/(MASS_AMU*AMU_KG)*(EV_J/ANGSTROM_M**2)
        omega_direct=math.sqrt(float(np.linalg.eigvalsh(dyn)[-1]))
        assert abs(omega_direct/omega-1)<1e-14
        q=.1;u=q*MODE
        records.append({'label':label,'spring_eV_per_A2':K,'mode_curvature_eV_per_A2':k,'effective_mass_amu':effective_mass,
          'all_normal_frequencies_THz':[frequency*math.sqrt(v/4) for v in [0,2,2,4]],'omega_rad_per_s':omega,'frequency_THz':frequency,'q_example_A':q,'atomic_displacements_A':u.tolist(),
          'delta_energy_example_eV':float(energy(u,K)-U0_EV),'generalized_restoring_force_example_eV_per_A':float(MODE@forces(u,K)),
          'atomic_forces_example_eV_per_A':forces(u,K).tolist(),
          'hessian_eV_per_A2':hessian.tolist(),
          'curve':[{'q_A':float(q),'delta_energy_eV':.5*k*float(q)**2,'generalized_force_eV_per_A':-k*float(q)} for q in np.linspace(-.16,.16,129)]})
    ratio=records[1]['frequency_THz']/records[0]['frequency_THz']
    assert abs(ratio-.9)<1e-14
    out={'scope':'Ideal harmonic educational example constructed for this review; no learned model or DFT calculation.',
      'model':'U(u)=U0+(K/2) sum_cycle_edges (u_j-u_i)^2; four identical atoms, periodic chain',
      'atom_count':N,'edges':EDGES,'mass_each_amu':MASS_AMU,'minimum_energy_U0_eV':U0_EV,
      'mode_vector':MODE.tolist(),'coordinate_convention':'u_i=q e_i; q in angstrom, sum e_i^2=1; effective mass=sum_i m_i e_i^2',
      'formula':'U(q)=U0+k q^2/2; Q=-dU/dq=-kq; omega=sqrt(k/mu); f=omega/(2pi)',
      'constants':{'eV_J':EV_J,'angstrom_m':ANGSTROM_M,'atomic_mass_unit_kg':AMU_KG,
        'source':'NIST 2022 CODATA; unified atomic mass unit and eV SI conversion',
        'url':'https://physics.nist.gov/cuu/pdf/RevModPhys.97.025002.pdf'},
      'cases':records,'frequency_ratio':ratio,
      'verification':{'analytic_laplacian_spectrum':[0,2,2,4],'checks':'Atomic energy vs mode energy; projected force vs derivative finite difference; force-difference Hessian at three steps; dynamical-matrix spectrum vs mode formula; 0.81 stiffness to 0.9 frequency ratio.',
        'maximum_tolerance':'Energy <3e-15 eV; force finite difference <2e-10 eV/angstrom; other comparisons as asserted in code.'}}
    (ROOT/'artifacts/examples.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks':'passed','f_THz':[r['frequency_THz'] for r in records],'omega_rad_s':[r['omega_rad_per_s'] for r in records],'frequency_ratio':ratio}))
if __name__=='__main__':build()
