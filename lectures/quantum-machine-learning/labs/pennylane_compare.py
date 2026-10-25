#!/usr/bin/env python3
"""Optional SDK cross-check; default.qubit is a classical simulator, not a QPU."""
import argparse
import json
import platform
from pathlib import Path

import numpy as np
import pennylane as qml
from pennylane import numpy as pnp

from qml_labs import amplitude, angle_kernel, vqc_statevector


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    two = qml.device("default.qubit", wires=2, shots=None)
    one = qml.device("default.qubit", wires=1, shots=None)

    @qml.qnode(two)
    def bell():
        qml.Hadamard(wires=0)
        qml.CNOT(wires=[0, 1])
        return qml.state()

    @qml.qnode(one, diff_method="parameter-shift")
    def single(theta):
        qml.RY(theta, wires=0)
        return qml.expval(qml.PauliZ(0))

    @qml.qnode(one)
    def embed(values):
        qml.AmplitudeEmbedding(values, wires=[0], normalize=True)
        return qml.state()

    @qml.qnode(two)
    def overlap(x, y):
        qml.AngleEmbedding(x, wires=[0, 1], rotation="Y")
        qml.adjoint(qml.AngleEmbedding)(y, wires=[0, 1], rotation="Y")
        return qml.probs(wires=[0, 1])

    @qml.qnode(two)
    def vqc(x, theta):
        qml.AngleEmbedding(x, wires=[0, 1], rotation="Y")
        qml.RY(theta[0], wires=0)
        qml.RY(theta[1], wires=1)
        qml.CNOT(wires=[0, 1])
        return qml.expval(qml.PauliZ(1))

    theta = pnp.array(0.73, requires_grad=True)
    derivative = float(qml.grad(single)(theta))
    x, y = np.array([0.4, -0.7]), np.array([-0.3, 1.2])
    parameters = np.array([0.8, -0.2])
    kernel_value = float(overlap(x, y)[0])
    vqc_value = float(vqc(x, parameters))
    amplitude_error = float(np.max(np.abs(embed([1.0, 2.0]) - amplitude([1.0, 2.0]))))
    derivative_error = float(abs(derivative + np.sin(0.73)))
    kernel_error = float(abs(kernel_value - angle_kernel(x[None, :], y[None, :])[0, 0]))
    vqc_error = float(abs(vqc_value - vqc_statevector(x, parameters)))
    assert np.allclose(np.abs(bell()) ** 2, [0.5, 0, 0, 0.5])
    assert max(amplitude_error, derivative_error, kernel_error, vqc_error) < 1e-12
    result = {
        "execution_level": "classical_PennyLane_default.qubit_exact_simulator",
        "physical_qpu_executed": False, "python_version": platform.python_version(),
        "numpy_version": np.__version__, "pennylane_version": qml.__version__,
        "bell_probabilities": (np.abs(bell()) ** 2).tolist(),
        "parameter_shift_derivative": derivative, "derivative_absolute_error": derivative_error,
        "amplitude_embedding_max_error": amplitude_error,
        "overlap_fidelity": kernel_value, "fidelity_absolute_error": kernel_error,
        "vqc_expectation": vqc_value, "vqc_absolute_error": vqc_error,
        "checks": "NumPy gate matrices, analytic derivative, normalized vector, and kernel formula agree",
    }
    payload = json.dumps(result, indent=2, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print("Saved " + args.output.name)
    else:
        print(payload)


if __name__ == "__main__":
    main()
