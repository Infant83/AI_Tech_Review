#!/usr/bin/env python3
"""Exact, tiny classical checks of the educational procurement exercise.

Python standard library only. No optimization package, QPU, circuit simulator,
or real procurement data is used. Costs are in units of KRW 10,000.
Run: python3 verify_exercise.py --output calculations.json
"""

import argparse
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path


POLICIES = tuple(product((0, 1), repeat=3))
BASE = (Q(7, 10), Q(2, 10), Q(1, 10))
STRESS = (Q(7, 10), Q(1, 20), Q(1, 4))
SERVICE = Q(9, 10)


def quantities(a, b, c):
    return (6 * a + 4 * b + 4 * c, 4 * b + 4 * c, 6 * a)


def evaluate(policy, probabilities):
    a, b, c = policy
    qty = quantities(a, b, c)
    shortfall = tuple(max(8 - q, 0) for q in qty)
    reservation = 12 * a + 9 * b + 11 * c
    cost = reservation + 10 * sum(p * u for p, u in zip(probabilities, shortfall))
    service = sum((p for p, u in zip(probabilities, shortfall) if u == 0), Q(0))
    filled = sum(p * min(q, 8) for p, q in zip(probabilities, qty)) / 8
    # Existential feasibility of the exercise's binary violation indicators.
    witnesses = [z for z in POLICIES
                 if all(q + 8 * zi >= 8 for q, zi in zip(qty, z))
                 and sum(p * zi for p, zi in zip(probabilities, z)) <= 1 - SERVICE]
    assert bool(witnesses) == (service >= SERVICE)
    minimum_z = tuple(int(u > 0) for u in shortfall)
    assert all(q + 8 * z >= 8 for q, z in zip(qty, minimum_z))
    # Positive shortfall cost makes u=max(8-q,0) optimal for each fixed policy.
    assert all(u >= 0 and u >= 8 - q for u, q in zip(shortfall, qty))
    return {
        "bits_abc": list(policy),
        "policy": "".join(x for x, bit in zip("ABC", policy) if bit) or "none",
        "arrivals_boxes_S0_S1_S2": list(qty),
        "shortfall_boxes_S0_S1_S2": list(shortfall),
        "reservation_cost_10000_KRW": reservation,
        "expected_total_cost_10000_KRW": cost,
        "full_delivery_probability": service,
        "expected_filled_demand_fraction": filled,
        "chance_MILP_feasible": bool(witnesses),
        "minimal_violation_indicator": list(minimum_z),
    }


def multilinear_coefficients(probabilities):
    # Boolean Mobius inversion recovers the unique multilinear polynomial
    # independently from all eight original shortfall-cost evaluations.
    values = {bits: evaluate(bits, probabilities)["expected_total_cost_10000_KRW"]
              for bits in POLICIES}
    coefficients = {}
    for support in POLICIES:
        value = Q(0)
        for sub in POLICIES:
            if all(x <= y for x, y in zip(sub, support)):
                value += (-1) ** (sum(support) - sum(sub)) * values[sub]
        name = "".join(v for v, bit in zip("abc", support) if bit) or "constant"
        coefficients[name] = value
    return coefficients


def penalty(a, b, y):
    return a * b - 2 * a * y - 2 * b * y + 3 * y


def quadratic(a, b, c, y, weight):
    return (80 - 36 * a - 27 * b - 25 * c + 14 * a * b
            + 14 * a * c + 14 * y * c + weight * penalty(a, b, y))


def build():
    assert sum(BASE) == sum(STRESS) == 1
    base = [evaluate(x, BASE) for x in POLICIES]
    stress = [evaluate(x, STRESS) for x in POLICIES]
    coefficients = multilinear_coefficients(BASE)
    assert coefficients == {"constant": 80, "a": -36, "b": -27, "c": -25,
                            "ab": 14, "ac": 14, "bc": 0, "abc": 14}
    feasible = [x for x in base if x["chance_MILP_feasible"]]
    optimum = min(feasible, key=lambda x: x["expected_total_cost_10000_KRW"])
    assert [(x["policy"], x["expected_total_cost_10000_KRW"],
             x["full_delivery_probability"]) for x in feasible] == [
                 ("BC", 28, Q(9, 10)), ("ABC", 34, Q(9, 10))]
    assert optimum["policy"] == "BC"
    assert not any(x["chance_MILP_feasible"] for x in stress)
    assert max(x["full_delivery_probability"] for x in stress) == Q(3, 4)
    ab = next(x for x in base if x["policy"] == "AB")
    bc = next(x for x in base if x["policy"] == "BC")
    abc = next(x for x in base if x["policy"] == "ABC")
    assert ab["expected_filled_demand_fraction"] == Q(7, 8)
    assert abc["expected_total_cost_10000_KRW"] - bc["expected_total_cost_10000_KRW"] == 6
    assert sum(p * q for p, q in zip(BASE, quantities(0, 1, 1))) == Q(36, 5)
    penalty_rows = []
    for a, b, y in product((0, 1), repeat=3):
        value = penalty(a, b, y)
        assert (value == 0) == (y == a * b)
        assert y == a * b or value >= 1
        penalty_rows.append({"a": a, "b": b, "y": y, "penalty_factor": value})
    quad_rows = []
    for a, b, c, y in product((0, 1), repeat=4):
        original = evaluate((a, b, c), BASE)["expected_total_cost_10000_KRW"]
        energy = quadratic(a, b, c, y, 15)
        assert (energy == original) if y == a * b else (energy > original)
        quad_rows.append({"a": a, "b": b, "c": c, "y": y,
                          "consistent": y == a * b,
                          "QUBO_cost_P15_10000_KRW": energy,
                          "original_cost_10000_KRW": original})
    # Boundary illustrates strict per-policy consistency, not a universal or
    # globally minimal penalty claim: ABC can tie with invalid y at P=14.
    assert quadratic(1, 1, 1, 0, 14) == quadratic(1, 1, 1, 1, 14) == 34
    assert quadratic(1, 1, 1, 0, 13) < quadratic(1, 1, 1, 1, 13)
    annealing = 1000 * Q(20, 1_000_000)
    quantum_fixed = 2 + 8 + 15 + 4 + 1
    quantum_total = quantum_fixed + annealing
    classical_total = 2 + Q(30, 100) + 1
    assert annealing == Q(1, 50) and quantum_total == Q(1501, 50)
    assert classical_total == Q(33, 10) and quantum_fixed == 30
    assert classical_total <= 10 < quantum_total
    # Adding two guaranteed boxes makes ABC feasible even in S2. Costs of
    # that extension are unspecified; this is only a feasibility witness.
    assert all(q + 2 >= 8 for q in quantities(1, 1, 1))
    return {
        "issue_date": "2026-11-26",
        "execution": "Exact tiny classical enumeration with Python standard library; no solver or QPU execution.",
        "units": {"cost": "10000 KRW", "quantity": "boxes", "time": "seconds"},
        "base_probabilities_S0_S1_S2": BASE,
        "stress_probabilities_S0_S1_S2": STRESS,
        "base_all_eight_policies": base,
        "stress_all_eight_policies": stress,
        "base_multilinear_cost_coefficients": coefficients,
        "stress_multilinear_cost_coefficients": multilinear_coefficients(STRESS),
        "base_optimal_feasible_policy": "BC",
        "stress_maximum_full_delivery_probability": Q(3, 4),
        "penalty_eight_rows": penalty_rows,
        "quadratic_sixteen_rows_P15": quad_rows,
        "quadratization_scope": "Four bits a,b,c,y for the supplied y=ab representation before service constraints; not a universal minimum or physical-qubit count.",
        "strict_policywise_penalty_sufficient_condition": "P > 14 in cost units; P=15 tested. P=14 permits an inconsistent-y tie for ABC. This does not assert the smallest weight needed solely to preserve global minimizers.",
        "MILP_equivalence": "For each policy, an indicator z exists iff the original full-delivery chance constraint holds; positive shortfall cost attains u=max(8-q,0).",
        "timing": {"reads": 1000, "anneal_per_read_microseconds": 20,
                   "total_anneal_seconds": annealing, "quantum_fixed_seconds": quantum_fixed,
                   "quantum_total_seconds": quantum_total,
                   "classical_total_seconds": classical_total,
                   "operational_limit_seconds": 10},
        "extension_feasibility_witness": "ABC plus two guaranteed boxes satisfies demand in every scenario; extension costs and operational availability require a new model.",
        "decision_scope": "Under the stipulated model/timing: classical base case meets the time limit; quantum operational route fails it; stress requires changing feasible choices. Proposed gap/success/cost thresholds are evaluation criteria, not measured performance.",
    }


def encode(value):
    if isinstance(value, Q):
        return value.numerator if value.denominator == 1 else str(value)
    raise TypeError(type(value).__name__)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("calculations.json"))
    args = parser.parse_args()
    args.output.write_text(json.dumps(build(), default=encode, ensure_ascii=False, indent=2) + "\n")
    print("All eight-policy, polynomial, sixteen-row QUBO, chance-feasibility and timing checks passed.")
