"""Independent full-state check of a four-amplitude cubic filter exercise.

This implements state preparation followed by address-to-work XOR, not QSVT.
The oracle is synthesized classically for two explicit educational fixtures.
"""
from fractions import Fraction
from itertools import product
import json
import numpy as np


def preparation(vector):
    """A complete Householder unitary for these fixtures with real first entry."""
    size = len(vector)
    first = np.eye(size, dtype=complex)[:, 0]
    difference = first - vector
    assert abs(vector[0].imag) < 1e-14
    oracle = np.eye(size, dtype=complex) - 2 * np.outer(difference, difference.conj()) / np.vdot(difference, difference)
    assert np.allclose(oracle.conj().T @ oracle, np.eye(size), atol=1e-13)
    assert np.allclose(oracle[:, 0], vector, atol=1e-13)
    return oracle


def apply_to_axis(oracle, state, axis):
    moved = np.tensordot(oracle, state, axes=(1, axis))
    return np.moveaxis(moved, 0, axis)


def xor_address_into_work(state, work_axis):
    result = np.zeros_like(state)
    for incoming in product(range(4), repeat=state.ndim):
        outgoing = list(incoming)
        outgoing[work_axis] ^= incoming[0]
        result[tuple(outgoing)] += state[incoming]
    return result


def run(vector, importance):
    n_filters = 2 if importance else 3
    oracle = preparation(vector)
    state = np.zeros((4,) * (1 + n_filters), dtype=complex)
    state[(0,) * state.ndim] = 1
    if importance:
        state = apply_to_axis(oracle, state, 0)
    else:
        # Two Hadamards on an initially zero two-qubit address register.
        state[:, 0, 0, 0] = 0.5
    for axis in range(1, n_filters + 1):
        state = apply_to_axis(oracle, state, axis)
        state = xor_address_into_work(state, axis)
    assert np.isclose(np.linalg.norm(state), 1, atol=1e-13)
    branch = state[(slice(None),) + (0,) * n_filters]
    expected_branch = vector**3 if importance else vector**3 / 2
    assert np.allclose(branch, expected_branch, atol=1e-13)
    success = float(np.vdot(branch, branch).real)
    normalized = branch / np.sqrt(success)
    target = vector**3 / np.linalg.norm(vector**3)
    fidelity = float(abs(np.vdot(target, normalized))**2)
    assert np.isclose(fidelity, 1, atol=1e-13)
    return {
        "filters": n_filters,
        "qubits": 2 * (1 + n_filters),
        "forward_oracle_calls": n_filters + int(importance),
        "inverse_oracle_calls": 0,
        "cx_calls": 2 * n_filters,
        "success_probability": success,
        "success_probability_fraction": str(Fraction(success).limit_denominator(100000)),
        "expected_trials_per_success": 1 / success,
        "expected_forward_oracle_calls_per_success": 3 / success,
        "target_fidelity": fidelity,
        "branch": [[float(z.real), float(z.imag)] for z in branch],
        "normalized_output": [[float(z.real), float(z.imag)] for z in normalized],
        "address_probabilities": abs(normalized)**2,
    }


def calculations():
    real = np.array([1, 2, -1, 0], dtype=complex) / np.sqrt(6)
    complex_fixture = np.array([1, 1j, -1, 0], dtype=complex) / np.sqrt(3)
    results = {}
    for name, vector, uniform_p, importance_p in [
        ("real", real, Fraction(11, 144), Fraction(11, 36)),
        ("complex", complex_fixture, Fraction(1, 36), Fraction(1, 9)),
    ]:
        results[name] = {"uniform": run(vector, False), "importance": run(vector, True)}
        assert np.isclose(results[name]["uniform"]["success_probability"], float(uniform_p))
        assert np.isclose(results[name]["importance"]["success_probability"], float(importance_p))
    target = complex_fixture**3 / np.linalg.norm(complex_fixture**3)
    wrong = complex_fixture * abs(complex_fixture)**2
    wrong /= np.linalg.norm(wrong)
    y = np.array([[0, -1j], [1j, 0]])
    observable = np.kron(np.eye(2), y)
    assert np.allclose(abs(target)**2, abs(wrong)**2)
    results["phase_diagnostic"] = {
        "wrong_map": "z -> z |z|^2, then normalize",
        "basis_probabilities_equal": bool(np.allclose(abs(target)**2, abs(wrong)**2)),
        "target_vs_wrong_fidelity": float(abs(np.vdot(target, wrong))**2),
        "observable": "I tensor Y, with |00>,|01>,|10>,|11> ordering",
        "target_expectation": float(np.vdot(target, observable @ target).real),
        "wrong_expectation": float(np.vdot(wrong, observable @ wrong).real),
    }
    assert np.isclose(results["phase_diagnostic"]["target_vs_wrong_fidelity"], 1/9)
    assert np.isclose(results["phase_diagnostic"]["target_expectation"], -2/3)
    assert np.isclose(results["phase_diagnostic"]["wrong_expectation"], 2/3)
    return results


if __name__ == "__main__":
    print(json.dumps(calculations(), indent=2, default=lambda item: item.tolist()))
