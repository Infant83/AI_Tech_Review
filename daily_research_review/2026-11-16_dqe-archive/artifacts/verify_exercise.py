"""Independently calculate the fictional 16 November 2026 DQE example.

This is educational arithmetic, not a quantum-device run or a reproduction
of the cited catalyst and trapped-ion experiments.  No mail data is read.
"""
from decimal import Decimal
from itertools import product
import json
import math


def calculate():
    number = Decimal
    corrected = {
        "A": number("0.70") + number("-0.06") - number("-0.12"),
        "B": number("0.76") + number("-0.14") - number("-0.05"),
    }
    gap = corrected["A"] - corrected["B"]
    model_bound = number("0.040")
    solver_bound = number("0.020")
    # Independent signed errors for each candidate's already-differenced barrier.
    corners = [
        gap + sign_a_model * model_bound + sign_a_solver * solver_bound
        - sign_b_model * model_bound - sign_b_solver * solver_bound
        for sign_a_model, sign_a_solver, sign_b_model, sign_b_solver
        in product((-1, 1), repeat=4)
    ]
    strict_model_limit = gap / 2 - solver_bound
    structures, evaluations, groups, shots_per_group = 4, 100, 50, 500
    throughput, overhead_seconds, target_seconds = 5000, 25 * 60, 45 * 60
    total_shots = structures * evaluations * groups * shots_per_group
    allowed_shots = (target_seconds - overhead_seconds) * throughput
    assert corrected == {"A": number("0.76"), "B": number("0.67")}
    assert min(corners) == number("-0.030")
    assert max(corners) == number("0.210")
    assert gap - 2 * (strict_model_limit + solver_bound) == 0
    assert gap - 2 * (number("0.0249") + solver_bound) > 0
    assert total_shots == 10000000 and allowed_shots == 6000000
    assert total_shots / throughput + overhead_seconds == 3500
    return {
        "corrected_barriers_eV": {key: str(value) for key, value in corrected.items()},
        "nominal_gap_A_minus_B_eV": str(gap),
        "nominal_rate_B_over_A": math.exp(float(gap / number("0.050"))),
        "rate_assumptions": "Equal prefactors and thermal/entropic corrections; one rate-controlling step; kBT = 0.050 eV.",
        "per_candidate_barrier_error_eV": str(model_bound + solver_bound),
        "gap_error_bound_eV": str(2 * (model_bound + solver_bound)),
        "independent_error_corners_checked": len(corners),
        "worst_case_gap_interval_eV": [str(min(corners)), str(max(corners))],
        "current_ranking_guaranteed": False,
        "model_bound_must_be_strictly_below_eV": str(strict_model_limit),
        "error_unit": "Per-candidate barrier after energy differences; no cancellation assumed.",
        "data_qubits_per_structure": 2 * 8,
        "qubit_assumptions": "One qubit per spin orbital; exclude ancillas and symmetry reductions; structures run sequentially.",
        "total_shots": total_shots,
        "measurement_seconds": total_shots / throughput,
        "overhead_seconds": overhead_seconds,
        "total_seconds": total_shots / throughput + overhead_seconds,
        "target_seconds": target_seconds,
        "allowed_shots": allowed_shots,
        "shot_reduction_fraction": 1 - allowed_shots / total_shots,
        "allowed_mean_shots_per_group": allowed_shots / (structures * evaluations * groups),
        "timing_scope": "Fictional sequential estimates; not measured latency quantiles. Accuracy under fewer shots requires verification.",
    }


if __name__ == "__main__":
    print(json.dumps(calculate(), ensure_ascii=False, indent=2))
