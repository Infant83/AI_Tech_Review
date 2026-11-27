#!/usr/bin/env python3
"""Reproduce KRR, joint-kernel consistency, PSD and measurement-cost arithmetic."""

import argparse
from fractions import Fraction as F
from itertools import combinations
import json
from math import ceil, isclose, sqrt
from pathlib import Path
import platform


def serial(value):
    if isinstance(value, F):
        return value.numerator if value.denominator == 1 else str(value)
    if isinstance(value, dict):
        return {k: serial(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [serial(v) for v in value]
    return value


def determinant(a):
    if len(a) == 1:
        return a[0][0]
    return sum((-1) ** j * a[0][j] * determinant(
        [[a[r][c] for c in range(len(a)) if c != j] for r in range(1, len(a))])
               for j in range(len(a)))


def principal_minors(a):
    return {"indices_" + "_".join(map(str, inds)): determinant([[a[i][j] for j in inds] for i in inds])
            for count in range(1, len(a) + 1) for inds in combinations(range(len(a)), count)}


def solve2(a, b):
    det = determinant(a)
    return ((a[1][1] * b[0] - a[0][1] * b[1]) / det,
            (a[0][0] * b[1] - a[1][0] * b[0]) / det)


def fidelity(a, b):
    return abs(sum(x.conjugate() * y for x, y in zip(a, b))) ** 2


def verify():
    k = [[F(1), F(1, 2)], [F(1, 2), F(1)]]
    regularization, mean = F(1, 2), F(1, 5)
    labels, target = (F(1, 10), F(3, 10)), F(17, 100)
    centered_labels = tuple(r - mean for r in labels)
    system = [[k[i][j] + (regularization if i == j else 0) for j in range(2)] for i in range(2)]
    alpha = solve2(system, centered_labels)
    assert alpha == (F(-1, 10), F(1, 10))
    kq, kc = (F(4, 5), F(1, 5)), (F(3, 5), F(2, 5))
    predictions = [mean + sum(vector[i] * alpha[i] for i in range(2)) for vector in (kq, kc)]
    errors = [abs(prediction - target) for prediction in predictions]
    assert predictions == [F(7, 50), F(9, 50)] and errors == [F(3, 100), F(1, 100)]

    joint_q = [k[0] + [kq[0]], k[1] + [kq[1]], [kq[0], kq[1], F(1)]]
    joint_c = [k[0] + [kc[0]], k[1] + [kc[1]], [kc[0], kc[1], F(1)]]
    assert determinant(joint_q) == F(23, 100) and determinant(joint_c) == F(47, 100)
    assert all(v > 0 for v in principal_minors(joint_q).values())
    assert all(v > 0 for v in principal_minors(joint_c).values())

    # PSD of the squared-overlap matrix alone would not establish quantum
    # fidelity realizability. Give explicit pure states for all three points.
    # cos(theta)=-3/4, sin(theta)=sqrt(7)/4.
    state1 = (complex(1), complex(0))
    state2 = (complex(1 / sqrt(2)), complex(1 / sqrt(2)))
    test = (complex(2 / sqrt(5)), complex(-3, sqrt(7)) / (4 * sqrt(5)))
    states = (state1, state2, test)
    for state in states:
        assert isclose(sum(abs(z) ** 2 for z in state), 1.0, abs_tol=1e-14)
    realized = [[fidelity(a, b) for b in states] for a in states]
    for i in range(3):
        for j in range(3):
            assert isclose(realized[i][j], float(joint_q[i][j]), abs_tol=1e-14)

    audit = [[F(1), F(4, 5), F(4, 5)],
             [F(4, 5), F(1), F(0)], [F(4, 5), F(0), F(1)]]
    audit_det = determinant(audit)
    audit_eigenvalues = (1 - 4 * sqrt(2) / 5, 1.0, 1 + 4 * sqrt(2) / 5)
    assert audit_det == F(-7, 25) and audit_eigenvalues[0] < 0
    ridge_eigenvalues = [value + float(regularization) for value in audit_eigenvalues]
    assert ridge_eigenvalues[0] > 0

    train_count, predict_count, shots_per_pair, throughput = 200, 20, 1000, 5000
    train_pairs = train_count * (train_count - 1) // 2
    predict_pairs = train_count * predict_count
    pairs = train_pairs + predict_pairs
    shots = pairs * shots_per_pair
    measurement_seconds = F(shots, throughput)
    fixed_seconds = 5 * 60 + 10 * 60
    total_seconds = fixed_seconds + measurement_seconds
    classical_seconds = 5 * 60 + 60
    assert (train_pairs, predict_pairs, pairs, shots) == (19900, 4000, 23900, 23900000)
    assert measurement_seconds == 4780 and total_seconds == 5680 and classical_seconds == 360
    measurement_budget = 30 * 60 - fixed_seconds
    assert measurement_budget == 900
    required_rate = F(shots, measurement_budget)
    max_shots_per_pair = measurement_budget * throughput // pairs
    assert ceil(required_rate) == 26556 and max_shots_per_pair == 188
    at_188 = fixed_seconds + F(pairs * 188, throughput)
    at_189 = fixed_seconds + F(pairs * 189, throughput)
    assert at_188 <= 1800 < at_189
    gross_cpu_hours = 20 * 4
    assert gross_cpu_hours == 80

    return serial({
        "execution": {"kind": "classical exact rational arithmetic and numerical pure-state consistency check",
                      "python": platform.python_version(), "sklearn_executed": False,
                      "eight_qubit_circuit_executed": False, "QPU_executed": False,
                      "DFT_executed": False},
        "label_mean_eV": mean, "centered_labels_eV": centered_labels,
        "regularized_training_system": system, "alpha_eV": alpha,
        "prediction_Q_C_eV": predictions, "single_point_absolute_error_Q_C_eV": errors,
        "single_point_error_is_population_MAE": False,
        "joint_quantum_fidelity_Gram": joint_q,
        "joint_quantum_fidelity_Gram_principal_minors": principal_minors(joint_q),
        "joint_classical_Gram_with_one_consistent_test_self_kernel_1": joint_c,
        "joint_classical_Gram_determinant": determinant(joint_c),
        "quantum_realizability_witness": {
            "training_states": ["|0>", "(|0>+|1>)/sqrt(2)"],
            "test_state": "sqrt(4/5)|0> + sqrt(1/5)*exp(i*theta)|1>; cos(theta)=-3/4, sin(theta)=sqrt(7)/4",
            "numerically_recovered_fidelity_Gram": realized,
            "scope": "A classical mathematical existence witness for the three supplied kernel points; not an implementation of the unspecified fixed eight-qubit feature circuit. Unused |0> qubits can embed these states in its Hilbert-space dimension."
        },
        "independent_audit_matrix_B": audit, "B_principal_minors": principal_minors(audit),
        "B_determinant": audit_det, "B_eigenvalues": audit_eigenvalues,
        "B_plus_half_identity_eigenvalues": ridge_eigenvalues,
        "ridge_repairs_the_original_measurement_provenance": False,
        "training_pairs": train_pairs, "prediction_pairs": predict_pairs, "all_pairs": pairs,
        "shots_per_pair": shots_per_pair, "all_shots": shots,
        "measurement_seconds": measurement_seconds, "quantum_total_seconds": total_seconds,
        "quantum_total_minutes_seconds": [94, 40], "classical_total_seconds": classical_seconds,
        "maximum_binomial_element_standard_error_1000_shots": sqrt(0.25 / 1000),
        "remaining_measurement_budget_seconds": measurement_budget,
        "minimum_throughput_exact_shots_per_second": required_rate,
        "minimum_integer_throughput_shots_per_second": ceil(required_rate),
        "maximum_integer_shots_per_pair_at_current_rate": max_shots_per_pair,
        "total_seconds_at_188_shots_per_pair": at_188,
        "total_seconds_at_189_shots_per_pair": at_189,
        "gross_DFT_replacement_upper_bound_CPU_hours": gross_cpu_hours,
        "new_20_label_validation_cost_CPU_hours_if_all_DFT_jobs_are_run": gross_cpu_hours,
        "scope": "Synthetic inputs and timing assumptions. No surrogate deployment, DFT saving, hardware throughput or population accuracy was demonstrated.",
        "result": "all assertions passed"
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("calculations.json"))
    args = parser.parse_args()
    args.output.write_text(json.dumps(verify(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("All KRR, joint-kernel, PSD, sampling, timing and replacement-accounting checks passed.")
