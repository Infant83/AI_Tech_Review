"""Independent SO(3) moment check of the exact-channel teaching results."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def rotation(axis, angle):
    v = np.asarray(axis, dtype=float)
    cross = np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    return np.cos(angle)*np.eye(3)+(1-np.cos(angle))*np.outer(v,v)+np.sin(angle)*cross


def main():
    data = json.loads((ROOT/'artifacts/results/dynamics_comparison.json').read_text())
    theta, phi = 1.05, .38
    r0 = np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),np.cos(theta)])
    coefficients = np.array([1,.2,.2])  # Z, X, Y, respectively
    axes = np.array([[0,0,1],[1,0,0],[0,1,0]])
    field = sum(c*a for c,a in zip(coefficients,axes))
    total_time, steps, trajectories = .4, 4, 200
    rexact = rotation(field/np.linalg.norm(field),2*np.linalg.norm(field)*total_time)@r0
    checks = []
    for item in data['qdrift_comparison']:
        q = np.array(item['probabilities'])
        matrices = [rotation(axis,2*c*total_time/(steps*prob)) for axis,c,prob in zip(axes,coefficients,q)]
        first = sum(prob*r for prob,r in zip(q,matrices))
        second = sum(prob*np.kron(r,r) for prob,r in zip(q,matrices))
        mean = np.linalg.matrix_power(first,steps)@r0
        pair = np.linalg.matrix_power(second,steps)@np.kron(r0,r0)
        for name, index in [('Z',2),('X',0)]:
            ref = item['observables'][name]
            variance = pair[index*3+index]-mean[index]**2
            bias = mean[index]-rexact[index]
            metrics = {'exact_expectation':rexact[index],'mean':mean[index],
                       'bias':bias,'trajectory_variance':variance,
                       'MSE_M200':bias*bias+variance/trajectories}
            maximum = max(abs(value-ref[key]) for key,value in metrics.items())
            assert maximum<2e-13,(item['name'],name,metrics,ref)
            checks.append({'distribution':item['name'],'observable':name,'max_absolute_difference':maximum})
    report = {'method':'Independent Bloch-vector Rodrigues rotations and 3x3/9x9 first/second moment matrices',
              'scope':'Exact educational trajectory moments only; no StateDRIFT reproduction, molecular/QPU or shot-noise validation',
              'T':total_time,'N':steps,'M':trajectories,'checks':checks}
    (ROOT/'notes').mkdir(exist_ok=True)
    (ROOT/'notes/independent-dynamics-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Independent SO(3) verification passed; max difference',max(x['max_absolute_difference'] for x in checks))


if __name__=='__main__':
    main()
