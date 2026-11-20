#!/usr/bin/env python3
"""Exact schedule/QUBO enumeration and independent-trial arithmetic, without a QPU."""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from math import ceil, log, log1p
from pathlib import Path
import platform


# Operation: (resource, duration in hours). Adjacent operations are nonpreemptive.
OPERATIONS = {"A1": ("technicians", 2), "A2": ("crane", 3),
              "B1": ("crane", 2), "B2": ("technicians", 3)}
PRECEDENCE = (("A1", "A2"), ("B1", "B2"))


def valid_schedule(starts, deadline):
    if set(starts) != set(OPERATIONS):
        return False
    for operation, start in starts.items():
        if not isinstance(start, int) or start < 0 or start + OPERATIONS[operation][1] > deadline:
            return False
    if any(starts[i] + OPERATIONS[i][1] > starts[j] for i, j in PRECEDENCE):
        return False
    for i, j in combinations(OPERATIONS, 2):
        if OPERATIONS[i][0] == OPERATIONS[j][0]:
            if starts[i] < starts[j] + OPERATIONS[j][1] and starts[j] < starts[i] + OPERATIONS[i][1]:
                return False
    return True


def enumerate_deadline(deadline):
    variables = [(i, t) for i, (_, duration) in OPERATIONS.items()
                 for t in range(deadline - duration + 1)]
    groups = [[k for k, (i, _) in enumerate(variables) if i == operation] for operation in OPERATIONS]
    precedence_pairs = [(k, l) for k, (i, t) in enumerate(variables)
                        for l, (j, u) in enumerate(variables)
                        if (i, j) in PRECEDENCE and t + OPERATIONS[i][1] > u]
    resource_pairs = [(k, l) for k, l in combinations(range(len(variables)), 2)
                      if variables[k][0] != variables[l][0]
                      and OPERATIONS[variables[k][0]][0] == OPERATIONS[variables[l][0]][0]
                      and variables[k][1] < variables[l][1] + OPERATIONS[variables[l][0]][1]
                      and variables[l][1] < variables[k][1] + OPERATIONS[variables[k][0]][1]]

    # Expand the one-hot squares using x^2=x. The constant must be retained.
    linear = [-1] * len(variables)
    quadratic = Counter()
    for group in groups:
        for k, l in combinations(group, 2):
            quadratic[k, l] += 2
    for k, l in precedence_pairs + resource_pairs:
        quadratic[tuple(sorted((k, l)))] += 1
    constant = len(groups)

    distribution = Counter()
    zeros = []
    for bits in product((0, 1), repeat=len(variables)):
        penalties = (sum((sum(bits[k] for k in group) - 1) ** 2 for group in groups)
                     + sum(bits[k] * bits[l] for k, l in precedence_pairs)
                     + sum(bits[k] * bits[l] for k, l in resource_pairs))
        energy = constant + sum(v * x for v, x in zip(linear, bits))
        energy += sum(c * bits[k] * bits[l] for (k, l), c in quadratic.items())
        assert penalties == energy and energy >= 0
        distribution[energy] += 1
        one_hot = all(sum(bits[k] for k in group) == 1 for group in groups)
        starts = {i: t for x, (i, t) in zip(bits, variables) if x} if one_hot else {}
        feasible = one_hot and valid_schedule(starts, deadline)
        assert (energy == 0) == feasible
        if energy == 0:
            zeros.append(starts)

    schedules = []
    domains = [range(deadline - duration + 1) for _, duration in OPERATIONS.values()]
    for times in product(*domains):
        starts = dict(zip(OPERATIONS, times))
        if valid_schedule(starts, deadline):
            schedules.append(starts)
    assert sorted(tuple(s.items()) for s in schedules) == sorted(tuple(s.items()) for s in zeros)
    return {"deadline_hours": deadline, "variables": [f"{i}@{t}" for i, t in variables],
            "logical_variable_count_before_pruning": len(variables),
            "binary_states_exhaustively_evaluated": 2 ** len(variables),
            "start_time_combinations_independently_evaluated": len(list(product(*domains))),
            "precedence_forbidden_pairs": len(precedence_pairs),
            "resource_forbidden_pairs": len(resource_pairs),
            "minimum_QUBO_energy": min(distribution),
            "zero_energy_count": len(zeros), "feasible_schedules": schedules,
            "energy_histogram": dict(sorted(distribution.items())),
            "qubo_zero_iff_feasible_over_all_states": True}


def trial_cost(p):
    n = ceil(log(0.05) / log1p(-float(p)))
    failure_n = (1 - p) ** n
    failure_previous = (1 - p) ** (n - 1)
    assert failure_n <= Fraction(1, 20) < failure_previous
    seconds = Fraction(8) + Fraction(n, 20)
    return {"p": str(p), "minimum_independent_trials_for_95_percent": n,
            "success_probability_at_n": float(1 - failure_n),
            "success_probability_at_n_minus_one": float(1 - failure_previous),
            "fixed_seconds": 8.0, "per_sample_seconds": 0.05,
            "total_seconds": float(seconds), "deadline_seconds": 10.0,
            "meets_ten_second_deadline_under_assumptions": seconds <= 10,
            "expected_trials_until_first_success": float(1 / p),
            "hypothetical_classical_95_percent_seconds": 2.0,
            "total_divided_by_classical_seconds": float(seconds / 2)}


def verify():
    d4, d5 = enumerate_deadline(4), enumerate_deadline(5)
    assert d4["logical_variable_count_before_pruning"] == 10
    assert d5["logical_variable_count_before_pruning"] == 14
    assert d4["zero_energy_count"] == 0 and d5["zero_energy_count"] == 1
    schedule = {"A1": 0, "A2": 2, "B1": 0, "B2": 2}
    assert d5["feasible_schedules"] == [schedule]
    job_loads = [sum(OPERATIONS[i][1] for i in job) for job in PRECEDENCE]
    resource_loads = {r: sum(d for rr, d in OPERATIONS.values() if rr == r)
                      for r in {rr for rr, _ in OPERATIONS.values()}}
    lower_bound = max(job_loads + list(resource_loads.values()))
    makespan = max(schedule[i] + OPERATIONS[i][1] for i in OPERATIONS)
    assert lower_bound == makespan == 5
    trials = [trial_cost(Fraction(1, 10)), trial_cost(Fraction(1, 50))]
    assert [t["minimum_independent_trials_for_95_percent"] for t in trials] == [29, 149]
    assert [t["total_seconds"] for t in trials] == [9.45, 15.45]
    deadline_samples = int((Fraction(10) - 8) / Fraction(1, 20))
    assert deadline_samples == 40
    return {"execution": {"kind": "classical exhaustive enumeration and probability arithmetic",
                          "python": platform.python_version(), "CP_SAT_executed": False,
                          "QPU_executed": False, "annealer_simulation_executed": False},
            "operations": {i: {"resource": r, "duration_hours": d} for i, (r, d) in OPERATIONS.items()},
            "job_chain_lower_bounds_hours": job_loads, "resource_load_lower_bounds_hours": resource_loads,
            "proved_minimum_makespan_hours": makespan,
            "schedule_intervals_hours": {i: [s, s + OPERATIONS[i][1]] for i, s in schedule.items()},
            "deadline_enumerations": [d4, d5], "independent_trial_scenarios": trials,
            "samples_available_in_ten_seconds": deadline_samples,
            "success_with_forty_samples_at_p_002": float(1 - Fraction(49, 50) ** deadline_samples),
            "perfectly_correlated_counterexample": {
                "assumption": "All sample outcomes in a batch equal one Bernoulli outcome of probability p",
                "batch_success_probability_for_any_positive_n": "p",
                "purpose": "Illustrates why marginal success probability alone does not justify the independent-trial formula"},
            "scope": "Exercise inputs and timings are hypothetical, not measurements of Google OR-Tools or D-Wave hardware.",
            "result": "all assertions passed"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("calculations.json"))
    args = parser.parse_args()
    args.output.write_text(json.dumps(verify(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("All exhaustive schedule/QUBO and exact probability-threshold checks passed.")
