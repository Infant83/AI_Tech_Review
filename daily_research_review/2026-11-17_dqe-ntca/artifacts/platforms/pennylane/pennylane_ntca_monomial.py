"""Cubic amplitude products with PennyLane 0.45.1, locally and without QSVT.

Every filter prepares a fresh work register with forward U, then XORs the
address into that register. All work registers must be zero in the retained
branch. No dense diag(x) oracle, nonlinear unitary, or hardware run is used.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pennylane as qml


TOL = 2e-10
FIXTURES = {
    "real": np.array([1, 2, -1, 0], dtype=complex) / np.sqrt(6),
    "complex": np.array([1, 1j, -1, 0], dtype=complex) / np.sqrt(3),
}


def validate_input(values):
    x = np.asarray(values, dtype=complex)
    if x.ndim != 1 or len(x) < 2 or len(x) & (len(x) - 1):
        raise ValueError("Input length must be 2**n, n >= 1")
    if not np.isfinite(x).all() or not np.isclose(np.linalg.norm(x), 1, atol=1e-12, rtol=0):
        raise ValueError("Expected finite, normalized amplitudes")
    return x


def load(x, wires):
    # Explicit rotation/CNOT decomposition defines a coherent unitary U.
    qml.MottonenStatePreparation(x, wires=wires)


def filter_block(x, address, work):
    load(x, work)
    for control, target in zip(address, work):
        qml.CNOT(wires=[control, target])


def run_case(values, importance):
    x = validate_input(values)
    n = len(x).bit_length() - 1
    k = 2 if importance else 3
    address = list(range(n))
    work = list(range(n, n * (k + 1)))
    dev = qml.device("default.qubit", wires=n * (k + 1), shots=None)

    @qml.qnode(dev)
    def circuit():
        if importance:
            load(x, address)
        else:
            for wire in address:
                qml.Hadamard(wires=wire)
        for j in range(k):
            filter_block(x, address, work[j * n:(j + 1) * n])
        return qml.state(), qml.probs(wires=work)

    state, work_probs = circuit()
    # qml.state uses wire order [0,1,...]: address is the leading MSB register.
    # Select the single all-zero work column, never sum discarded amplitudes.
    branch = np.asarray(state).reshape(len(x), 2**len(work))[:, 0]
    expected = x**3 / (1 if importance else np.sqrt(len(x)))
    success = float(np.vdot(branch, branch).real)
    target = x**3 / np.linalg.norm(x**3)
    retained = branch / np.sqrt(success)
    amplitude_error = float(np.max(np.abs(branch - expected)))
    fidelity = float(abs(np.vdot(target, retained))**2)
    y_lsb = np.kron(np.eye(len(x) // 2), np.array([[0, -1j], [1j, 0]]))
    y_expectation = float(np.vdot(retained, y_lsb @ retained).real)
    assert amplitude_error < TOL
    assert abs(success - np.vdot(expected, expected).real) < TOL
    assert abs(success - work_probs[0]) < TOL
    assert abs(fidelity - 1) < TOL
    return {
        "mode": "importance" if importance else "uniform",
        "success_probability": success,
        "conditional_amplitudes": [[float(v.real), float(v.imag)] for v in retained],
        "conditional_fidelity": fidelity,
        "branch_max_amplitude_error": amplitude_error,
        "conditional_Y_least_significant_bit": y_expectation,
        "logical_qubits": n * (k + 1),
        "filter_U_calls": k,
        "input_U_calls": int(importance),
        "total_forward_U_calls_per_complete_attempt": k + int(importance),
        "XOR_CNOT_count_excluding_U_decomposition": n * k,
        "expected_U_calls_per_acceptance_without_early_abort": (k + int(importance)) / success,
    }


def verify_filter(values):
    x = validate_input(values)
    n = len(x).bit_length() - 1
    # Work first in this isolated matrix check, so the selected block is [:N,:N].
    work, address = list(range(n)), list(range(n, 2 * n))
    mat = qml.matrix(lambda: filter_block(x, address, work), wire_order=range(2 * n))()
    error = float(np.max(np.abs(mat[:len(x), :len(x)] - np.diag(x))))
    assert error < TOL
    assert np.max(np.abs(mat.conj().T @ mat - np.eye(len(mat)))) < TOL
    return error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "execution": "local ideal statevector; no QPU or QSVT execution",
        "versions": {"pennylane": qml.__version__, "numpy": np.__version__},
        "address_order": "logical vector indices 00,01,10,11; PennyLane wire0 is MSB",
        "cases": {},
    }
    for name, vector in FIXTURES.items():
        result["cases"][name] = {
            "filter_block_max_error": verify_filter(vector),
            "runs": [run_case(vector, mode) for mode in (False, True)],
        }
    rng = np.random.default_rng(173)
    for n in [2, 4, 8]:
        vector = rng.normal(size=n) + 1j * rng.normal(size=n)
        vector[-1] = 0
        vector /= np.linalg.norm(vector)
        verify_filter(vector)
        for mode in (False, True):
            run_case(vector, mode)
    result["random_complex_inputs_of_lengths_2_4_8_with_zero_entry"] = "passed"
    result["passed"] = True
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
