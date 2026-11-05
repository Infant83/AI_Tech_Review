"""Independent, small classical checks for the published QAE study guide.

Uses only Python's standard library. It does not reconstruct the unavailable
original source ZIP, invoke Classiq, or submit a quantum-computer job.
"""
import cmath
import json
import math
from pathlib import Path
import platform

I = [[1, 0], [0, 1]]
X = [[0, 1], [1, 0]]
Y = [[0, -1j], [1j, 0]]
Z = [[1, 0], [0, -1]]
A = [[-1, .2], [.2, 1]]
rho = math.sqrt(1.04)


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def adj(a):
    return [[complex(a[j][i]).conjugate() for j in range(2)] for i in range(2)]


def combine(a, ca, b, cb):
    return [[ca*a[i][j] + cb*b[i][j] for j in range(2)] for i in range(2)]


def distance(a, b):
    return math.sqrt(sum(abs(a[i][j]-b[i][j])**2 for i in range(2) for j in range(2)))


def rotation(p, angle):
    return combine(I, math.cos(angle/2), p, -1j*math.sin(angle/2))


def exact(tau):
    return combine(I, math.cos(rho*tau), A, -1j*math.sin(rho*tau)/rho)


def trotter(tau, steps):
    one = mul(rotation(Z, -2*tau/steps), rotation(X, .4*tau/steps))
    result = I
    for _ in range(steps):
        result = mul(one, result)
    return result


def main():
    checks = []

    def check(name, residual, tolerance=2e-12):
        assert residual <= tolerance, (name, residual, tolerance)
        checks.append(dict(name=name, residual=residual, tolerance=tolerance))

    check('A squared equals 1.04 identity', distance(mul(A, A), combine(I, 1.04, I, 0)))
    check('A is Hermitian', distance(A, adj(A)))
    theta = -.5*math.atan(.2)
    energy = -math.cos(2*theta)+.2*math.sin(2*theta)
    check('variational minimum equals exact lower eigenvalue', abs(energy+rho))
    check('complex inner product norm squared', abs(sum(abs(v)**2 for v in [1+1j, 2j])-6))
    plus, minus = [1/math.sqrt(2), 1/math.sqrt(2)], [1/math.sqrt(2), -1/math.sqrt(2)]
    check('orthonormal plus and minus states', abs(sum(complex(u).conjugate()*v for u, v in zip(plus, minus))))
    bell = [[1/math.sqrt(2), 0], [0, 1/math.sqrt(2)]]
    check('Bell determinant is one half in magnitude', abs(abs(bell[0][0]*bell[1][1]-bell[0][1]*bell[1][0])-.5))
    check('energy projector probability sums to one', abs((1+1/rho)/2+(1-1/rho)/2-1))
    check('energy variance in zero state', abs(rho*rho-1-.04))
    alpha = math.atan(.2)
    for tau in [0, .3, 1, 2.4]:
        u = exact(tau)
        check('unitarity tau='+str(tau), distance(mul(adj(u), u), I))
        gates = mul(mul(rotation(Y, -alpha), rotation(Z, -2*rho*tau)), rotation(Y, alpha))
        check('three rotation identity tau='+str(tau), distance(gates, u))
    euler = combine(I, 1, A, -1j*.1)
    check('Euler norm drift identity', distance(mul(adj(euler), euler), combine(I, 1.0104, I, 0)))
    check('Trotter remains unitary', distance(mul(adj(trotter(1, 16)), trotter(1, 16)), I))
    errors = {str(n): distance(trotter(1, n), exact(1)) for n in [8, 16, 32]}
    assert errors['32'] < errors['16'] < errors['8']
    checks.append(dict(name='Trotter error decreases for the three tested step counts', values=errors))
    p1 = abs(exact(1)[1][0])**2
    check('published transition probability at tau one', abs(p1-.0279197369), 5e-11)
    result = dict(format='classiq-qae-public-reference-checks-v1', date='2026-11-05',
                  execution='classical Python standard-library finite matrices', python=platform.python_version(),
                  original_source_zip_available=False, original_check_counts_independently_rerun=False,
                  quantum_hardware_or_Classiq_executed=False, checks=checks, check_count=len(checks),
                  values=dict(lower_energy_hartree=-rho, transition_probability_tau_1=p1, trotter_frobenius_errors=errors))
    target = Path(__file__).parent/'results/reference-checks.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2)+'\n')
    print('Passed', len(checks), 'small classical checks')


if __name__ == '__main__':
    main()
