"""Exact cubic amplitude transformation with reversible Qiskit circuits.

This is a fresh-work-register amplitude-multiplication construction, not a QSVT
implementation. It handles the agreed real and complex four-amplitude examples.
All execution is local, noiseless statevector simulation; no account is needed.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
import platform

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Gate
from qiskit.circuit.library import StatePreparation
from qiskit.quantum_info import Operator, Statevector


ATOL = 2e-10
FIXTURES = {
    "real": np.array([1, 2, -1, 0], dtype=complex) / np.sqrt(6),
    "complex": np.array([1, 1j, -1, 0], dtype=complex) / np.sqrt(3),
}


def normalized_vector(values) -> np.ndarray:
    """Require a normalized power-of-two vector; do not silently renormalize."""
    vector = np.asarray(values, dtype=complex)
    if vector.ndim != 1 or vector.size < 2 or vector.size & (vector.size - 1):
        raise ValueError("Expected a vector of length 2**n, n >= 1")
    if not np.isfinite(vector).all() or not np.isclose(np.linalg.norm(vector), 1, atol=1e-12, rtol=0):
        raise ValueError("Input amplitudes must be finite and normalized")
    return vector


def amplitude_filter(prepare: Gate) -> Gate:
    """Return V = XOR(data -> work) (I_data tensor U_work).

    Qiskit qubits 0..n-1 hold the address, and n..2n-1 hold fresh work. After
    U|0> = sum_k x_k|k>, bitwise XOR maps work |k> to |k XOR j> on address j.
    Therefore <0_work|V|0_work> = diag(x). No x* is introduced: the preparation
    is forward, followed by XOR. The code never supplies a dense diag(x) matrix
    or a dense dilation as a gate.
    """
    n = prepare.num_qubits
    circuit = QuantumCircuit(2 * n, name="amplitude_filter")
    circuit.append(prepare, range(n, 2 * n))
    for bit in range(n):
        circuit.cx(bit, n + bit)
    return circuit.to_gate(label="F(U)")


def cubic_circuit(values, importance: bool) -> tuple[QuantumCircuit, list[int], list[int], dict]:
    """Build D**3|+> or D**2|x>, with every filter using fresh zero work."""
    vector = normalized_vector(values)
    n = vector.size.bit_length() - 1
    prepare = StatePreparation(vector, label="U(x)")
    filters = 2 if importance else 3
    circuit = QuantumCircuit(n * (filters + 1), name="cubic_importance" if importance else "cubic_uniform")
    data = list(range(n))
    ancillas = list(range(n, circuit.num_qubits))
    if importance:
        circuit.append(prepare, data)
    else:
        for bit in data:
            circuit.h(bit)
    block = amplitude_filter(prepare)
    for copy in range(filters):
        work = list(range(n * (copy + 1), n * (copy + 2)))
        circuit.append(block, data + work)
    resources = {
        "data_qubits": n,
        "work_qubits": n * filters,
        "total_qubits": circuit.num_qubits,
        "filter_calls": filters,
        "filter_state_preparation_calls": filters,
        "input_state_preparation_calls": int(importance),
        "total_state_preparation_calls": filters + int(importance),
        "xor_cx_gates": n * filters,
        "all_work_zero_postselection": True,
    }
    return circuit, data, ancillas, resources


def project_zero_work(state: np.ndarray, data: list[int], ancillas: list[int]) -> np.ndarray:
    """Select every work bit = 0, in data basis |q[n-1]...q[0]> order.

    A Qiskit statevector index is sum(bit[q] * 2**q). This explicit map also
    works when the logical data qubits are not the lowest physical positions.
    Each data basis value identifies exactly one full basis state when all
    other qubits are zero. There is no trace, measurement sampling or summing
    amplitudes over discarded work states.
    """
    full_qubits = len(state).bit_length() - 1
    if len(state) != 2**full_qubits or sorted(data + ancillas) != list(range(full_qubits)):
        raise ValueError("Data and work must partition all statevector qubits")
    indices = [sum(((value >> bit) & 1) << qubit for bit, qubit in enumerate(data))
               for value in range(2**len(data))]
    return np.asarray(state)[indices]


def complex_json(vector: np.ndarray) -> list[dict]:
    return [{"real": float(value.real), "imag": float(value.imag)} for value in vector]


def verify_input_block(values) -> dict:
    vector = normalized_vector(values)
    n = vector.size.bit_length() - 1
    prepare = StatePreparation(vector, label="U(x)")
    u = Operator(prepare).data
    v = Operator(amplitude_filter(prepare)).data
    block = v[:2**n, :2**n]
    column_error = float(np.max(np.abs(u[:, 0] - vector)))
    block_error = float(np.max(np.abs(block - np.diag(vector))))
    unitarity_error = float(np.max(np.abs(v.conj().T @ v - np.eye(len(v)))))
    assert column_error < ATOL
    assert block_error < ATOL
    assert unitarity_error < ATOL
    return {"u_first_column_max_error": column_error,
            "amplitude_to_diagonal_block_max_error": block_error,
            "filter_unitarity_max_error": unitarity_error,
            "block_diagonal": complex_json(np.diag(block))}


def run_case(values, importance: bool) -> tuple[dict, QuantumCircuit]:
    vector = normalized_vector(values)
    circuit, data, ancillas, resources = cubic_circuit(vector, importance)
    state = Statevector(circuit)
    branch = project_zero_work(state.data, data, ancillas)
    factor = 1.0 if importance else 1 / np.sqrt(vector.size)
    expected_branch = factor * vector**3
    p = float(np.vdot(branch, branch).real)
    expected_p = float(np.vdot(expected_branch, expected_branch).real)
    target = vector**3 / np.linalg.norm(vector**3)
    conditional = branch / np.sqrt(p)
    fidelity = float(abs(np.vdot(target, conditional))**2)
    amplitude_error = float(np.max(np.abs(branch - expected_branch)))
    conditional_error = float(np.max(np.abs(conditional - target)))
    marginal_p = float(state.probabilities(qargs=ancillas)[0])
    assert amplitude_error < ATOL
    assert conditional_error < ATOL
    assert abs(p - expected_p) < ATOL
    assert abs(p - marginal_p) < ATOL
    assert abs(fidelity - 1) < ATOL
    # This is a toy decomposition count, not a hardware-time or fault-tolerant estimate.
    lowered = transpile(circuit, basis_gates=["u", "cx"], optimization_level=0, seed_transpiler=29)
    resources["decomposed_basis"] = ["u", "cx"]
    resources["decomposed_depth"] = lowered.depth()
    resources["decomposed_gate_counts"] = {str(k): int(v) for k, v in lowered.count_ops().items()}
    return {
        "initialization": "importance" if importance else "uniform",
        "resources": resources,
        "input": complex_json(vector),
        "postselected_unnormalized": complex_json(branch),
        "expected_unnormalized": complex_json(expected_branch),
        "conditional_amplitudes": complex_json(conditional),
        "target_amplitudes": complex_json(target),
        "basis_labels": [format(value, f"0{len(data)}b") for value in range(vector.size)],
        "conditional_probabilities": [float(abs(value)**2) for value in conditional],
        "success_probability": p,
        "analytic_success_probability": expected_p,
        "work_zero_marginal_probability": marginal_p,
        "conditional_fidelity": fidelity,
        "phase_sensitive_amplitude_max_error": amplitude_error,
        "conditional_amplitude_max_error": conditional_error,
    }, circuit


def validation(output: Path) -> dict:
    results = {}
    output.parent.mkdir(parents=True, exist_ok=True)
    for name, vector in FIXTURES.items():
        cases = []
        for importance in (False, True):
            case, circuit = run_case(vector, importance)
            cases.append(case)
            (output.parent / f"{name}-{case['initialization']}-circuit.txt").write_text(str(circuit.draw(output="text")) + "\n")
        assert abs(cases[1]["success_probability"] / cases[0]["success_probability"] - 4) < ATOL
        results[name] = {"input_block_check": verify_input_block(vector), "runs": cases,
                         "success_probability_ratio_importance_over_uniform": 4.0}
    # Independent cases expose a sign/conjugation or physical-order mistake.
    rng = np.random.default_rng(29)
    extra_checks = []
    for size in (2, 4, 8):
        vector = rng.normal(size=size) + 1j * rng.normal(size=size)
        vector[0] = 0
        vector /= np.linalg.norm(vector)
        verify_input_block(vector)
        for importance in (False, True):
            case, _ = run_case(vector, importance)
            extra_checks.append({"dimension": size, "importance": importance,
                                 "amplitude_max_error": case["phase_sensitive_amplitude_max_error"]})
    versions = {name: importlib.metadata.version(name) for name in
                ("qiskit", "numpy", "scipy", "rustworkx", "dill", "stevedore", "typing-extensions")}
    report = {
        "description": "Cubic NTCA exercise using forward U plus XOR and fresh work registers",
        "execution": "local noiseless Qiskit Statevector; no QPU and no cloud account",
        "algorithm": "exact repeated amplitude multiplication; not QSVT",
        "dense_amplitude_diagonal_or_dilation_gate_used": False,
        "python": platform.python_version(), "versions": versions,
        "fixtures": results, "additional_random_complex_checks": extra_checks,
        "limitations": [
            "The state preparation is synthesized from a known classical vector; loading and synthesis cost can grow with input dimension.",
            "Fresh work registers scale as degree times log2(N); this is not the constant-ancilla QSVT construction from the source demo.",
            "The factor-four success comparison uses N=4 and the exact monomial x**3; it is not a general performance or hardware speedup claim.",
            "The complex case computes z**3, not Re(z)**3, |z|**3, or a holomorphic extension of the demo's tanh workflow.",
            "Decomposed u/cx counts are for this local toy circuit and specified transpiler settings only.",
        ],
        "primary_documentation": [
            "https://pennylane.ai/demos/nonlinear_transformation_of_complex_amplitudes",
            "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.circuit.library.StatePreparation",
            "https://quantum.cloud.ibm.com/docs/en/api/qiskit/qiskit.quantum_info.Statevector",
            "https://quantum.cloud.ibm.com/docs/en/qiskit/bit-ordering",
            "https://pypi.org/project/qiskit/2.6.2/",
        ],
    }
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("qiskit-results.json"))
    args = parser.parse_args()
    report = validation(args.output)
    print(json.dumps({"versions": report["versions"], "output": str(args.output),
                      "all_checks_passed": True,
                      "success_probabilities": {key: [run["success_probability"] for run in data["runs"]]
                                                for key, data in report["fixtures"].items()}}, indent=2))


if __name__ == "__main__":
    main()
