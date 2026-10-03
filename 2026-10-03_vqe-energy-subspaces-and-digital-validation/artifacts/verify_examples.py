"""Independent teaching models; NOT a reproduction of DecaQ.

Run: python verify_examples.py
Requires NumPy. Uses dense matrices only for a four-spin check.
"""
import json
import numpy as np

X = np.array([[0., 1.], [1., 0.]])
Z = np.diag([1., -1.])
I = np.eye(2)

def edges(side):
    return [(r * side + c, r * side + c + 1)
            for r in range(side) for c in range(side - 1)] + [
            (r * side + c, (r + 1) * side + c)
            for r in range(side - 1) for c in range(side)]

def product_energy(theta, alpha, links, h=0.05):
    q = np.cos(theta - alpha)
    return -h * q.sum() - sum(q[i] * q[j] for i, j in links)

def embed(op, i, n):
    result = np.array([[1.]])
    for k in range(n):
        result = np.kron(result, op if k == i else I)
    return result

def main():
    alpha4 = np.linspace(0.2, 1.1, 4)
    q4 = [embed(np.cos(a) * Z + np.sin(a) * X, i, 4)
          for i, a in enumerate(alpha4)]
    h4 = -0.05 * sum(q4) - sum(q4[i] @ q4[j] for i, j in edges(2))
    dense4 = float(np.linalg.eigvalsh(h4)[0])
    assert np.isclose(dense4, -4.2, atol=1e-12)
    assert max(np.linalg.norm(q4[i] @ q4[j] - q4[j] @ q4[i])
               for i in range(4) for j in range(4)) < 1e-12
    # Compare arbitrary product-state energies against dense matrices.
    rng = np.random.default_rng(10)
    max_error = 0.
    for _ in range(20):
        theta = rng.uniform(-np.pi, np.pi, 4)
        psi = np.array([1.])
        for t in theta:
            psi = np.kron(psi, [np.cos(t/2), np.sin(t/2)])
        dense_energy = float(psi @ h4 @ psi)
        analytic_energy = product_energy(theta, alpha4, edges(2))
        max_error = max(max_error, abs(dense_energy - analytic_energy))
    assert max_error < 1e-12
    alpha400 = np.linspace(0.2, 1.1, 400)
    links = edges(20)
    assert len(links) == 760
    # Generic angles ensure all 2N+4E Pauli coefficients are nonzero.
    assert np.all(np.sin(alpha400) != 0) and np.all(np.cos(alpha400) != 0)
    term_count = 2 * len(alpha400) + 4 * len(links)
    energy400 = float(product_energy(alpha400, alpha400, links))
    assert term_count == 3840 and np.isclose(energy400, -780.)
    exact_errors = []
    product_errors = []
    # Check exact and globally optimal product energies for the two-spin model.
    for g in np.linspace(0, 2, 41):
        h2 = -np.kron(Z, Z) - g * (np.kron(X, I) + np.kron(I, X))
        exact = -np.sqrt(1 + 4*g*g)
        exact_errors.append(abs(float(np.linalg.eigvalsh(h2)[0]) - exact))
        theta = np.arcsin(g) if g <= 1 else np.pi/2
        psi = np.kron([np.cos(theta/2), np.sin(theta/2)],
                      [np.cos(theta/2), np.sin(theta/2)])
        best_product = -1-g*g if g <= 1 else -2*g
        product_errors.append(abs(float(psi @ h2 @ psi) - best_product))
        assert best_product >= exact - 1e-12
    assert max(exact_errors) < 1e-12 and max(product_errors) < 1e-12
    # Analytic global product minimum: write z1*z2 <= (z1^2+z2^2)/2,
    # choose positive x_i; the resulting bound is saturated by equal spins.
    out = {
        'scope': 'independent teaching examples, not DecaQ reproduction',
        'grid': {'spins': 400, 'edges': len(links), 'pauli_terms': term_count,
                 'analytic_product_ground_energy': energy400},
        'four_spin_dense_ground_energy': dense4,
        'max_arbitrary_product_energy_error': max_error,
        'max_two_spin_dense_error': max(exact_errors),
        'max_two_spin_product_error': max(product_errors),
        'hi_vqe_NH3_table2_error_mHa': round((-56.29215769 + 56.29239989)*1000, 5),
        'hi_vqe_NH3_table2_determinant_percent': 100*199809/9018009,
        'chemical_accuracy_1p6mHa_eV': 0.0016*27.211386245988,
    }
    print(json.dumps(out, indent=2))

if __name__ == '__main__':
    main()
