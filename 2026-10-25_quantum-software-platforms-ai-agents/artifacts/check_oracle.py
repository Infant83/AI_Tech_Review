"""Exact educational three-qubit example; not a vendor or QPU benchmark.

Basis ordering is |q2 q1 q0>, integer 0..7. The intended marked state is 101.
Both the correct and deliberately wrong phase oracle are unitary. Measurement
immediately after either oracle is uniform; a single ideal Grover iteration
amplifies the marked state to probability 25/32, whether the marking matched
our intended specification or not. No quantum SDK, LLM or device is executed.
"""
from pathlib import Path
import json
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def calculate():
    n=8;s=np.ones(n,dtype=complex)/np.sqrt(n)
    diffusion=2*np.outer(s,s.conj())-np.eye(n)
    rows=[]
    for label,target in [('correct_specification',5),('wrong_specification',7)]:
        oracle=np.eye(n,dtype=complex);oracle[target,target]=-1
        after_oracle=oracle@s;after_grover=diffusion@after_oracle
        p_oracle=np.abs(after_oracle)**2;p=np.abs(after_grover)**2
        assert np.allclose(oracle.conj().T@oracle,np.eye(n),atol=1e-14)
        assert np.allclose(p_oracle,np.ones(n)/8,atol=1e-14)
        assert np.isclose(p.sum(),1,atol=1e-14)
        assert np.isclose(p[target],25/32,atol=1e-14)
        assert all(np.isclose(p[i],1/32,atol=1e-14) for i in range(n) if i!=target)
        rows.append({'case':label,'marked_basis':format(target,'03b'),'basis':[format(i,'03b') for i in range(n)],'oracle_phases':[int(oracle[i,i].real) for i in range(n)],'after_oracle_probabilities':p_oracle.tolist(),'after_one_iteration_probabilities':p.tolist(),'intended_answer_probability':float(p[5]),'oracle_unitarity_error':float(np.max(np.abs(oracle.conj().T@oracle-np.eye(n))))})
    result={'kind':'review-created exact state-vector teaching calculation','physical_execution':False,'vendor_benchmark':False,'intended_answer':'101','qubits':3,'basis_order':'q2 q1 q0; integer 0..7','iterations':1,'noise':'none; ideal unitary evolution','checks':'unitarity, normalization, uniform post-oracle measurement, exact 25/32 and 1/32 probabilities','cases':rows}
    (ROOT/'artifacts/oracle_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'checks':'passed','intended_answer_probability':{x['case']:x['intended_answer_probability'] for x in rows}}))

if __name__=='__main__':calculate()
