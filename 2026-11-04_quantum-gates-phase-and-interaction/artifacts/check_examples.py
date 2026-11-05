"""Check the ideal educational examples used to plan the quantum-gate article.

Basis order is |ab> = (|00>, |01>, |10>, |11>), a controls b.
QAOA convention: maximize C, U = exp(-i beta B) exp(-i gamma C).
Run with Python and NumPy; results are written next to this script.
"""

import json
from pathlib import Path

import numpy as np


I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
CX = np.array([[1, 0, 0, 0], [0, 1, 0, 0],
               [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)


def rz(angle):
    return np.diag(np.exp(-0.5j * angle * np.array([1, -1])))


def rx(angle):
    return np.cos(angle / 2) * I - 1j * np.sin(angle / 2) * X


def cost_scores(n, edges):
    return np.array([
        sum(((s >> (n - 1 - a)) & 1) != ((s >> (n - 1 - b)) & 1)
            for a, b in edges)
        for s in range(2 ** n)
    ])


def qaoa(n, edges, gamma, beta):
    scores = cost_scores(n, edges)
    initial = np.ones(2 ** n, dtype=complex) / np.sqrt(2 ** n)
    phased = np.exp(-1j * gamma * scores) * initial
    mixer = rx(2 * beta)
    for _ in range(n - 1):
        mixer = np.kron(mixer, rx(2 * beta))
    return initial, phased, mixer @ phased, mixer, scores


rng = np.random.default_rng(20261104)
identity_error = 0.0
phase_readout_error = 0.0
probability_formula_error = 0.0

for angle in np.r_[0, np.pi / 2, np.pi, rng.uniform(-4, 4, 32)]:
    rzz = np.diag(np.exp(-0.5j * angle * np.array([1, -1, -1, 1])))
    identity_error = max(identity_error, float(np.max(np.abs(
        CX @ np.kron(I, rz(angle)) @ CX - rzz))))
    output = H @ rz(angle) @ H @ np.array([1, 0], dtype=complex)
    phase_readout_error = max(phase_readout_error, float(abs(
        abs(output[0]) ** 2 - np.cos(angle / 2) ** 2)))

for gamma, beta in rng.uniform(-np.pi, np.pi, (64, 2)):
    initial, phased, final, mixer, scores = qaoa(2, [(0, 1)], gamma, beta)
    expected = (1 + np.sin(4 * beta) * np.sin(gamma)) / 2
    probability_formula_error = max(probability_formula_error, float(abs(
        np.abs(final) ** 2 @ scores - expected)))
    np.testing.assert_allclose(np.abs(phased) ** 2, 0.25, atol=1e-12)

gamma, beta = np.pi / 2, np.pi / 8
initial, phased, final, mixer, scores = qaoa(2, [(0, 1)], gamma, beta)
np.testing.assert_allclose(final, -1j * np.array([0, 1, 1, 0]) / np.sqrt(2),
                           atol=1e-12)
np.testing.assert_allclose(np.abs(mixer @ initial) ** 2, 0.25, atol=1e-12)
reversed_layers = np.exp(-1j * gamma * scores) * (mixer @ initial)
np.testing.assert_allclose(np.abs(reversed_layers) ** 2, 0.25, atol=1e-12)

two_qubit = {
    "gamma": gamma,
    "beta": beta,
    "initial_probabilities": (np.abs(initial) ** 2).tolist(),
    "after_cost_probabilities": (np.abs(phased) ** 2).tolist(),
    "final_probabilities": (np.abs(final) ** 2).tolist(),
    "cut_probability": float(np.abs(final) ** 2 @ scores),
    "reversed_layer_cut_probability": float(np.abs(reversed_layers) ** 2 @ scores),
}
initial, phased, final, _, scores = qaoa(
    3, [(0, 1), (1, 2), (0, 2)], gamma, beta)
triangle = {
    "gamma": gamma,
    "beta": beta,
    "optimal_score": int(max(scores)),
    "initial_expected_score": float(np.abs(initial) ** 2 @ scores),
    "final_expected_score": float(np.abs(final) ** 2 @ scores),
    "initial_optimal_probability": float(sum(np.abs(initial[scores == 2]) ** 2)),
    "final_optimal_probability": float(sum(np.abs(final[scores == 2]) ** 2)),
    "final_probabilities": (np.abs(final) ** 2).tolist(),
}
for error in [identity_error, phase_readout_error, probability_formula_error]:
    assert error < 1e-12
np.testing.assert_allclose(triangle["final_expected_score"], 0.75, atol=1e-12)
np.testing.assert_allclose(triangle["final_optimal_probability"], 0.375, atol=1e-12)

triangle_gamma = np.arctan(1 / np.sqrt(2))
triangle_beta = triangle_gamma / 2
_, _, final, _, scores = qaoa(
    3, [(0, 1), (1, 2), (0, 2)], triangle_gamma, triangle_beta)
triangle_retuned = {
    "gamma": float(triangle_gamma),
    "beta": float(triangle_beta),
    "final_expected_score": float(np.abs(final) ** 2 @ scores),
    "final_optimal_probability": float(sum(np.abs(final[scores == 2]) ** 2)),
    "final_probabilities": (np.abs(final) ** 2).tolist(),
}
np.testing.assert_allclose(triangle_retuned["final_expected_score"], 2, atol=1e-12)
np.testing.assert_allclose(triangle_retuned["final_optimal_probability"], 1,
                           atol=1e-12)

record = {
    "calculation": "Ideal statevector educational calculation",
    "numpy_version": np.__version__,
    "basis_order": "|ab>, a is left tensor factor and CX control",
    "convention": "Maximize C; exp(-i beta sum X) exp(-i gamma C)",
    "rzz_identity_max_abs_error": identity_error,
    "single_qubit_readout_max_abs_error": phase_readout_error,
    "two_qubit_probability_formula_max_abs_error": probability_formula_error,
    "two_qubit": two_qubit,
    "triangle_same_angles": triangle,
    "triangle_retuned_angles": triangle_retuned,
}
output_path = Path(__file__).with_name("example-checks.json")
output_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
print(json.dumps(record, ensure_ascii=False, indent=2))
