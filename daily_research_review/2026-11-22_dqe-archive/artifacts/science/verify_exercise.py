#!/usr/bin/env python3
"""Enumerate the toy unit-commitment decisions and solve dispatch analytically."""

import argparse
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import platform


MINIMUM = (F(40), F(10))
MAXIMUM = (F(80), F(50))
MARGINAL = (F(20), F(35))  # USD/MWh
STARTUP = (F(200), F(20))  # USD per off-to-on transition
DEMAND = (F(30), F(90))  # MW in consecutive one-hour periods
HOURS = F(1)


def number(x):
    if isinstance(x, F):
        return x.numerator if x.denominator == 1 else str(x)
    if isinstance(x, dict):
        return {k: number(v) for k, v in x.items()}
    if isinstance(x, (tuple, list)):
        return [number(v) for v in x]
    return x


def dispatch(commitment, demand, minimum=MINIMUM):
    """Exact continuous LP solution from the feasible interval for output A.

    With p_B=demand-p_A, the linear cost slope is c_A-c_B<0.
    Therefore the upper feasible endpoint minimizes cost; this is not a grid search.
    """
    ua, ub = commitment
    low = max(minimum[0] * ua, demand - MAXIMUM[1] * ub)
    high = min(MAXIMUM[0] * ua, demand - minimum[1] * ub)
    if low > high:
        return None
    assert MARGINAL[0] < MARGINAL[1]
    outputs = (high, demand - high)
    assert sum(outputs) == demand
    assert all(minimum[i] * commitment[i] <= outputs[i] <= MAXIMUM[i] * commitment[i]
               for i in (0, 1))
    cost = sum(MARGINAL[i] * outputs[i] * HOURS for i in (0, 1))
    return {"output_A_interval_MW": (low, high), "optimal_output_MW": outputs,
            "variable_cost_USD": cost}


def transitions(bits):
    # Order is A1,B1,A2,B2, and both generators were initially off.
    return (bits[0], bits[1], max(0, bits[2] - bits[0]), max(0, bits[3] - bits[1]))


def startup_cost(v):
    return sum(STARTUP[k % 2] * v[k] for k in range(4))


def verify_startup_constraints(bits):
    previous = (0, 0, bits[0], bits[1])
    possible = [v for v in product((0, 1), repeat=4)
                if all(v[k] >= bits[k] - previous[k] for k in range(4))]
    best = min(startup_cost(v) for v in possible)
    minimizers = [v for v in possible if startup_cost(v) == best]
    assert minimizers == [transitions(bits)]
    return best


def verify():
    records = []
    feasible_cost = {}
    period_feasible = []
    for demand in DEMAND:
        period_feasible.append([u for u in product((0, 1), repeat=2) if dispatch(u, demand) is not None])
    assert period_feasible == [[(0, 1)], [(1, 1)]]

    for bits in product((0, 1), repeat=4):
        startup = verify_startup_constraints(bits)
        periods = [dispatch(bits[2 * t:2 * t + 2], DEMAND[t]) for t in range(2)]
        feasible = all(p is not None for p in periods)
        record = {"commitment_A1_B1_A2_B2": bits,
                  "startup_indicators_A1_B1_A2_B2": transitions(bits),
                  "minimum_startup_cost_USD": startup, "period_dispatch": periods,
                  "feasible": feasible}
        if feasible:
            variable = sum(p["variable_cost_USD"] for p in periods)
            record.update(variable_cost_USD=variable, total_cost_USD=variable + startup)
            feasible_cost[bits] = variable + startup
        records.append(record)

    assert len(records) == 16 and len(feasible_cost) == 1
    optimum_bits = (0, 1, 1, 1)
    assert feasible_cost[optimum_bits] == 3220
    optimum = next(r for r in records if r["commitment_A1_B1_A2_B2"] == optimum_bits)
    assert optimum["variable_cost_USD"] == 3000
    assert optimum["minimum_startup_cost_USD"] == 220
    assert optimum["period_dispatch"][0]["optimal_output_MW"] == (0, 30)
    assert optimum["period_dispatch"][1]["optimal_output_MW"] == (80, 10)

    # Restore startup charges to the proposed approximate outputs, without
    # silently repairing the omitted minimum-output constraint.
    approximate_bits = (1, 0, 1, 1)
    approximate_outputs = ((F(30), F(0)), (F(80), F(10)))
    approximate_variable = sum(MARGINAL[i] * approximate_outputs[t][i] * HOURS
                               for t in range(2) for i in (0, 1))
    approximate_startup = startup_cost(transitions(approximate_bits))
    approximate_total = approximate_variable + approximate_startup
    assert approximate_variable == 2550 and approximate_startup == 220 and approximate_total == 2770
    assert approximate_outputs[0][0] < MINIMUM[0]
    violation_mw = MINIMUM[0] - approximate_outputs[0][0]
    assert violation_mw == 10 and 3220 - approximate_total == 450
    relaxed = [dispatch(approximate_bits[2*t:2*t+2], DEMAND[t], minimum=(F(0), F(0)))
               for t in range(2)]
    assert [r["optimal_output_MW"] for r in relaxed] == list(approximate_outputs)

    # One legitimate extension of the evaluated feasible cost to all bitstrings
    # uses a fixed penalty M for infeasible commitments. Its unique multilinear
    # polynomial is quartic, demonstrating that this evaluation does not
    # automatically become an exact QUBO on the four original variables.
    penalty = F(10000)
    values = []
    for mask in range(16):
        bits = tuple((mask >> k) & 1 for k in range(4))
        values.append(feasible_cost.get(bits, penalty))
    coefficients = values.copy()
    for k in range(4):
        for mask in range(16):
            if mask & (1 << k):
                coefficients[mask] -= coefficients[mask ^ (1 << k)]
    for mask in range(16):
        recovered = sum(coefficients[sub] for sub in range(16) if sub & mask == sub)
        assert recovered == values[mask]
    degree = max(mask.bit_count() for mask, c in enumerate(coefficients) if c)
    assert degree == 4 and coefficients[15] == 6780

    stages = {"input_and_model": F(8), "classical_evaluations": 40 * F(3, 10),
              "QPU_including_declared_compilation_measurement_mitigation": F(5),
              "queue_and_communication": F(15), "final_validation": F(4)}
    total_seconds = sum(stages.values())
    assert total_seconds == 44 and total_seconds - 30 == 14 and total_seconds > 15
    return number({
        "execution": {"kind": "classical exact arithmetic, binary enumeration and analytical continuous dispatch",
                      "python": platform.python_version(), "MILP_package_executed": False,
                      "QAOA_simulator_executed": False, "QPU_executed": False},
        "commitment_variable_order": ["u_A1", "u_B1", "u_A2", "u_B2"],
        "commitment_patterns_enumerated": 16, "startup_patterns_per_commitment_enumerated": 16,
        "feasible_commitments_by_period": period_feasible,
        "all_commitment_patterns": records,
        "optimum_total_USD": feasible_cost[optimum_bits],
        "approximate_plan": {"commitment": approximate_bits, "output_MW": approximate_outputs,
                             "variable_cost_USD": approximate_variable, "restored_startup_USD": approximate_startup,
                             "restored_total_USD": approximate_total, "first_period_A_minimum_violation_MW": violation_mw,
                             "numeric_difference_USD_not_a_feasible_saving": F(3220) - approximate_total},
        "startup_formulation_check": "For all sixteen commitments, positive startup prices make the unique cost-minimizing v equal the actual off-to-on transitions under v>=u-u_previous.",
        "nonquadratic_evaluated_cost_example": {
            "purpose": "Additional illustrative extension; not an implementation of the cited paper's QAOA",
            "infeasible_commitment_penalty_USD": penalty,
            "polynomial_USD": "10000 - 6780*u_B1*u_A2*u_B2 + 6780*u_A1*u_B1*u_A2*u_B2",
            "exact_multilinear_degree": degree,
            "limitation": "Auxiliary variables or a different justified formulation may change the encoding and resource count."},
        "hypothetical_sequential_stages_seconds": stages,
        "hypothetical_total_seconds": total_seconds, "target_seconds": 30,
        "deadline_excess_seconds": total_seconds - 30, "hypothetical_classical_seconds": 15,
        "logical_commitment_bits_only": 4,
        "scope": "The toy data, timing inputs and operational thresholds are educational assumptions. No hardware or paper benchmark was reproduced.",
        "result": "all assertions passed"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("calculations.json"))
    args = parser.parse_args()
    args.output.write_text(json.dumps(verify(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("All commitment, dispatch, startup, feasibility and timing checks passed.")
