#!/usr/bin/env python3
"""Reproduce the exercise's two-asset arithmetic; no quantum device is used."""

import argparse
from fractions import Fraction as F
import json
from math import sqrt
from pathlib import Path
import platform


def solve2(a, b):
    det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    return ((a[1][1] * b[0] - a[0][1] * b[1]) / det,
            (a[0][0] * b[1] - a[1][0] * b[0]) / det)


def mv(a, x):
    return tuple(sum(a[i][j] * x[j] for j in range(2)) for i in range(2))


def risk(a, w):
    return sum(w[i] * mv(a, w)[i] for i in range(2))


def exact(values):
    if isinstance(values, (tuple, list)):
        return [exact(v) for v in values]
    return str(values)


def verify():
    a = ((F(4), F(1)), (F(1), F(2)))
    a_ridge = ((F(5), F(1)), (F(1), F(3)))
    b = (F(1), F(1))
    x = solve2(a, b)
    w = tuple(v / sum(x) for v in x)
    v = risk(a, w)
    equal_v = risk(a, (F(1, 2), F(1, 2)))
    norm_squared = sum(vv * vv for vv in x)
    probabilities = tuple(vv * vv / norm_squared for vv in x)
    wrong_v = risk(a, probabilities)
    x_ridge = solve2(a_ridge, b)
    w_ridge = tuple(vv / sum(x_ridge) for vv in x_ridge)
    ridge_v_in_original_model = risk(a, w_ridge)
    excess = ridge_v_in_original_model - v
    relative_excess = excess / v
    eigenvalues_a = (3 - sqrt(2), 3 + sqrt(2))
    eigenvalues_ridge = (4 - sqrt(2), 4 + sqrt(2))
    kappa_a = eigenvalues_a[1] / eigenvalues_a[0]
    kappa_ridge = eigenvalues_ridge[1] / eigenvalues_ridge[0]
    components_seconds = (20, 10, 5, 30, 10)
    total_seconds = sum(components_seconds)
    # A second real vector shows the sign ambiguity of computational probabilities.
    sign_ambiguous_x = (F(1, 7), F(-3, 7))
    alternative_probabilities = tuple(vv * vv / norm_squared for vv in sign_ambiguous_x)
    alternative_weights = tuple(vv / sum(sign_ambiguous_x) for vv in sign_ambiguous_x)

    assert mv(a, x) == b
    assert x == (F(1, 7), F(3, 7))
    assert w == (F(1, 4), F(3, 4))
    assert sum(w) == 1 and mv(a, w) == (F(7, 4), F(7, 4))
    assert v == F(7, 4) and equal_v == 2
    assert (equal_v - v) / equal_v == F(1, 8)
    assert v / 10000 == F(7, 40000)
    assert norm_squared == F(10, 49)
    assert probabilities == (F(1, 10), F(9, 10))
    assert wrong_v == F(46, 25)
    assert mv(a_ridge, x_ridge) == b
    assert x_ridge == (F(1, 7), F(2, 7))
    assert w_ridge == (F(1, 3), F(2, 3))
    assert ridge_v_in_original_model == F(16, 9)
    assert excess == F(1, 36) and relative_excess == F(1, 63)
    assert risk(a_ridge, w_ridge) == risk(a, w_ridge) + sum(vv * vv for vv in w_ridge)
    assert kappa_ridge < kappa_a
    assert total_seconds == 75 and total_seconds - 60 == 15
    assert alternative_probabilities == probabilities and alternative_weights != w

    return {
        "execution": {"kind": "classical exact rational arithmetic and floating-point square roots",
                      "python": platform.python_version(), "quantum_circuit_run": False,
                      "qpu_run": False},
        "matrix": exact(a), "rhs": exact(b), "solution": exact(x),
        "weights": exact(w), "kkt_A_times_w": exact(mv(a, w)),
        "variance_in_percentage_points_squared": str(v),
        "variance_in_fractional_returns_squared": str(v / 10000),
        "equal_weight_variance_in_percentage_points_squared": str(equal_v),
        "relative_variance_reduction": str((equal_v - v) / equal_v),
        "normalized_solution_state": "(1, 3) / sqrt(10)",
        "computational_basis_probabilities": exact(probabilities),
        "variance_if_probabilities_are_used_as_weights": str(wrong_v),
        "regularized_matrix": exact(a_ridge), "regularized_solution": exact(x_ridge),
        "regularized_weights": exact(w_ridge),
        "regularized_weights_variance_under_original_covariance": str(ridge_v_in_original_model),
        "absolute_variance_increase": str(excess), "relative_variance_increase": str(relative_excess),
        "condition_numbers": {"A": kappa_a, "A_plus_I": kappa_ridge},
        "hypothetical_sequential_seconds": list(components_seconds),
        "hypothetical_total_seconds": total_seconds, "deadline_seconds": 60,
        "deadline_excess_seconds": total_seconds - 60,
        "old_p95_divided_by_hypothetical_total": 90 / total_seconds,
        "timing_comparison_is_measured_speedup": False,
        "sign_ambiguity_example": {"other_vector": exact(sign_ambiguous_x),
                                   "same_probabilities": exact(alternative_probabilities),
                                   "other_budget_normalized_weights": exact(alternative_weights)},
        "result": "all assertions passed",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("independent-calculations.json"))
    args = parser.parse_args()
    args.output.write_text(json.dumps(verify(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("All exact arithmetic, unit, state/probability, regularization and timing checks passed.")
