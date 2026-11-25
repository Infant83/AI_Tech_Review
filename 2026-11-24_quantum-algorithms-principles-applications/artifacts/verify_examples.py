"""Reproduce ideal teaching examples, with independent analytic/statevector checks.

Requires NumPy. No hardware execution, source-paper reproduction or shot sampling.
Basis: |q0 q1 ...>, q0 is the leftmost tensor factor. Energies use E0;
physical evolution time t = tau*hbar/E0. QPE uses 6 controls and 2 targets.
"""
from pathlib import Path
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)

def real(x): return float(np.real(x))
def vals(x): return np.asarray(x).real.tolist()
def normcheck(v):
    assert abs(np.vdot(v, v)-1) < 2e-13

def build():
    h = .7
    H = np.kron(Z,Z) + h*(np.kron(X,I)+np.kron(I,X))
    energies, eigenvectors = np.linalg.eigh(H)
    root = math.sqrt(1+4*h*h)
    assert np.max(np.abs(energies-np.array([-root,-1,1,root]))) < 2e-14
    bell_psi = np.array([0,1,1,0], dtype=complex)/math.sqrt(2)
    bell_phi = np.array([1,0,0,1], dtype=complex)/math.sqrt(2)
    generator = np.kron(Y,Z)
    assert np.linalg.norm(generator@bell_psi+1j*bell_phi) < 1e-14
    theta_star = .5*math.atan2(2*h,1)
    def ansatz(theta): return math.cos(theta)*bell_psi-math.sin(theta)*bell_phi
    def energy(theta):
        p=ansatz(theta)
        return real(np.vdot(p,H@p))
    for theta in np.linspace(0,math.pi/2,17):
        assert abs(energy(theta)-(-math.cos(2*theta)-2*h*math.sin(2*theta))) < 2e-14
        via_rotation=(math.cos(theta)*np.eye(4)-1j*math.sin(theta)*generator)@bell_psi
        assert np.linalg.norm(via_rotation-ansatz(theta)) < 1e-14
    gs=ansatz(theta_star);normcheck(gs)
    assert np.linalg.norm(H@gs+root*gs) < 1e-14
    weights=np.abs(eigenvectors.conj().T@bell_psi)**2
    assert abs(weights[0]-(1+1/root)/2)<1e-14
    tau=math.pi/4; shift=3.; controls=6; size=2**controls
    norm_bound=1+2*h
    assert shift>norm_bound
    phases=np.mod((shift-energies)*tau/(2*math.pi),1)
    # Independent QPE: controlled U^k followed by inverse Fourier transform.
    eig_input=eigenvectors.conj().T@bell_psi
    evolved=[]
    for k in range(size):
        evolved.append(eigenvectors@(np.exp(-1j*(energies-shift)*tau*k)*eig_input)/math.sqrt(size))
    pre_iqft=np.array(evolved)
    final=np.fft.fft(pre_iqft,axis=0)/math.sqrt(size)
    qpe_prob=np.sum(np.abs(final)**2,axis=1)
    bins=np.arange(size); k=np.arange(size)
    kernel=np.abs(np.exp(2j*math.pi*(phases[:,None,None]-bins[None,:,None]/size)*k[None,None,:]).sum(axis=2)/size)**2
    independent=weights@kernel
    assert np.max(np.abs(qpe_prob-independent))<8e-14
    assert abs(qpe_prob.sum()-1)<2e-14
    decoded=shift-8*bins/size
    peaks=sorted(range(size),key=lambda y:qpe_prob[y],reverse=True)[:6]

    n=4; dim=2**n; edges=[(0,1),(1,2),(2,3),(3,0)]
    bit_strings=[format(s,'04b') for s in range(dim)]
    costs=np.array([sum(bits[a]!=bits[b] for a,b in edges) for bits in bit_strings])
    good=costs==4
    assert list(np.flatnonzero(good))==[5,10]
    uniform=np.ones(dim,dtype=complex)/math.sqrt(dim)
    gamma=math.pi/4; beta=math.pi/8
    rx=math.cos(beta)*I-1j*math.sin(beta)*X
    mixer=rx
    for _ in range(n-1):mixer=np.kron(mixer,rx)
    qaoa=mixer@(np.exp(-1j*gamma*costs)*uniform);normcheck(qaoa)
    qaoa_probs=np.abs(qaoa)**2
    # Independent expectation for a 4-cycle at p=1.
    analytic_mean=2+math.sin(4*beta)*math.sin(2*gamma)
    assert abs(np.dot(costs,qaoa_probs)-analytic_mean)<2e-14
    assert abs(qaoa_probs[good].sum()-17/32)<2e-14
    for b,g in [(.13,.29),(.45,-.23),(-.2,1.1)]:
        rx=math.cos(b)*I-1j*math.sin(b)*X
        u=rx
        for _ in range(n-1):u=np.kron(u,rx)
        p=np.abs(u@(np.exp(-1j*g*costs)*uniform))**2
        assert abs(np.dot(costs,p)-(2+math.sin(4*b)*math.sin(2*g)))<2e-14
    oracle=np.diag(np.where(good,-1,1));diffuser=2*np.outer(uniform,uniform)-np.eye(dim)
    G=diffuser@oracle
    a=real(np.sum(np.abs(uniform[good])**2));theta=math.asin(math.sqrt(a))
    grover=uniform.copy();grover_results=[]
    for j in range(5):
        normcheck(grover);p=np.abs(grover)**2
        actual=real(p[good].sum());predicted=math.sin((2*j+1)*theta)**2
        assert abs(actual-predicted)<2e-14
        grover_results.append({'iterations':j,'success_probability':actual,'expected_cut':real(np.dot(costs,p)),'state_probabilities':vals(p)})
        grover=G@grover
    bad_state=np.where(good,0,uniform);bad_state/=np.linalg.norm(bad_state)
    good_state=np.where(good,uniform,0);good_state/=np.linalg.norm(good_state)
    plane=np.column_stack([bad_state,good_state])
    eigenphase_angles=np.sort(np.angle(np.linalg.eigvals(plane.conj().T@G@plane)))
    assert np.max(np.abs(eigenphase_angles-np.array([-2*theta,2*theta])))<1e-14
    assert abs(math.sin(abs(eigenphase_angles[0])/2)**2-a)<1e-14
    def summary(p):return {'probabilities':vals(p),'cost_probabilities':{str(c):real(p[costs==c].sum()) for c in [0,2,4]},'success_probability':real(p[good].sum()),'expected_cut':real(np.dot(costs,p))}
    A=np.array([[2.,1.],[1.,2.]]);b=np.array([1.,0.]);solution=np.linalg.solve(A,b);solution_state=solution/np.linalg.norm(solution)
    assert np.max(np.abs(solution-np.array([2/3,-1/3])))<1e-14
    assert abs(real(solution_state@Z@solution_state)-3/5)<1e-14
    record={
      'scope':'Review-authored ideal educational statevector calculations; no QPU experiment or source-paper reproduction.',
      'basis_convention':'|q0 q1 ...>, q0 is leftmost tensor factor; four-bit strings use this same vertex order.',
      'two_spin':{'hamiltonian':'H/E0 = Z0 Z1 + 0.7 (X0 + X1)','energy_unit':'E0','J_over_E0':1,'h_over_E0':h,'eigenvalues_over_E0':vals(energies),'initial_state':'Psi+ = (|01> + |10>)/sqrt(2)','ground_state_ansatz':'cos(theta) Psi+ - sin(theta) Phi+ = exp[-i theta (Y0 Z1)] Psi+','theta_star_rad':theta_star,'ground_energy_over_E0':-root,'energy_formula':'E(theta)/E0 = -cos(2 theta) - 1.4 sin(2 theta)','initial_energy_over_E0':energy(0),'eigenstate_overlap_probabilities':vals(weights),'curve':[{'theta_rad':float(t),'energy_over_E0':energy(t)} for t in np.linspace(0,math.pi/2,161)],
      'qpe':{'target_qubits':2,'control_qubits':controls,'tau':tau,'physical_time':'t = tau*hbar/E0','shift_over_E0':shift,'known_norm_bound':norm_bound,'unitary':'U = exp[-i (H/E0 - 3 I) tau]','phase_convention':'U|Ej> = exp(2 pi i phi_j)|Ej>, phi_j=(3-Ej/E0)/8','known_phase_interval':[.075,.675],'energy_period_over_E0':8,'eigenphases':vals(phases),'grid_energy_spacing_over_E0':8/size,'bins':[{'y':int(y),'phase':float(y/size),'decoded_energy_over_E0':float(decoded[y]),'probability':float(qpe_prob[y])} for y in bins],'top_bins':[{'y':int(y),'binary':format(y,'06b'),'phase':float(y/size),'decoded_energy_over_E0':float(decoded[y]),'probability':float(qpe_prob[y])} for y in peaks]}},
      'maxcut':{'vertices':4,'edges':edges,'basis_strings':bit_strings,'costs':vals(costs),'marked_strings':['0101','1010'],'cost_formula':'C = sum_edges (1-Zi Zj)/2','uniform':summary(np.abs(uniform)**2),'qaoa':{'p':1,'gamma_rad':gamma,'beta_rad':beta,'order':'exp(-i beta sum X) exp(-i gamma C) |+>^4',**summary(qaoa_probs)},'grover':{'a':a,'theta_rad':theta,'state_plane_axes':['bad amplitude','good amplitude'],'rotation_per_iteration_rad':2*theta,'grover_eigenphase_angles_rad':vals(eigenphase_angles),'qae_phase_fractions':[theta/math.pi,1-theta/math.pi],'qae_readout':'a = sin^2(pi phi) for the two Grover eigenphases phi = theta/pi or 1-theta/pi','results':grover_results}},
      'linear_system':{'scope':'Classical direct solve showing the target state of a quantum linear-system algorithm.','A':vals(A),'b':vals(b),'x':vals(solution),'normalized_solution_state':vals(solution_state),'condition_number_2':float(np.linalg.cond(A)),'Z_expectation':real(solution_state@Z@solution_state)},
      'verification':{'assertions':'Analytic spectrum and energy curve vs direct diagonalization/expectation; Pauli-rotation ansatz; explicit inverse-QFT statevector vs eigenphase kernel; QAOA statevector vs cycle formula; direct Grover iterations vs rotation formula and projected eigenvalues; direct linear solve.','tolerance':1e-12,'shot_sampling':False,'qpe_probabilities':'Exact Born probabilities for a finite ideal register, not shot frequencies.'}}
    out=ROOT/'artifacts/examples.json';out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'saved':out.name,'ground_energy':-root,'ground_overlap':float(weights[0]),'qpe_top':record['two_spin']['qpe']['top_bins'][:2],'qaoa_P_C4':real(qaoa_probs[good].sum()),'grover2_P_C4':grover_results[2]['success_probability'],'checks':'passed'},ensure_ascii=False))
if __name__=='__main__':build()
