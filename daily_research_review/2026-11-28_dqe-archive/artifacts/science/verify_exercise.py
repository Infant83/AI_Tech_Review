#!/usr/bin/env python3
"""Tiny exact classical checks of the synthetic two-channel AP exercise.

Standard library only; no QAOA circuit, wireless controller or QPU is run.
Run: python3 verify_exercise.py --output calculations.json
"""

import argparse
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path


EDGES = ((0, 1, 3), (0, 2, 4), (1, 2, 5), (1, 3, 4), (2, 3, 3))
STATES = tuple(product((0, 1), repeat=4))


def score(bits, middle=5):
    return sum((middle if (i, j) == (1, 2) else w)
               for i, j, w in EDGES if bits[i] == bits[j])


def qubo(bits):
    return sum(w * (1 - bits[i] - bits[j] + 2 * bits[i] * bits[j])
               for i, j, w in EDGES)


def ising(bits):
    z = tuple(1 - 2 * b for b in bits)
    return sum(Q(w, 2) * (1 + z[i] * z[j]) for i, j, w in EDGES)


def cut(bits):
    return sum(w for i, j, w in EDGES if bits[i] != bits[j])


def build():
    total_weight = sum(w for _, _, w in EDGES)
    assert total_weight == 19
    linear = [-sum(w for i, j, w in EDGES if v in (i, j)) for v in range(4)]
    assert linear == [-7, -12, -12, -7]
    rows = []
    for bits in STATES:
        f = score(bits)
        complement = tuple(1 - b for b in bits)
        assert f == qubo(bits) == ising(bits) == score(complement)
        assert cut(bits) == total_weight - f
        expanded = 19 + sum(c * b for c, b in zip(linear, bits))
        expanded += sum(2 * w * bits[i] * bits[j] for i, j, w in EDGES)
        assert expanded == f
        rows.append({"assignment_ABCD": list(bits), "F_points": f,
                     "cut_weight_points": cut(bits),
                     "BC_same": bits[1] == bits[2],
                     "complement_ABCD": list(complement)})
    same = [r for r in rows if r["BC_same"]]
    different = [r for r in rows if not r["BC_same"]]
    assert len(same) == len(different) == 8
    assert min(r["F_points"] for r in same) == 5
    assert min(r["F_points"] for r in different) == 6
    # Conditional lower bounds: same B,C leaves their middle-edge cost;
    # opposite B,C leaves one edge at A and one at D, each at least 3.
    assert score((0, 1, 1, 0)) == 5
    assert score((0, 0, 1, 1)) == 6
    optimum = [r["assignment_ABCD"] for r in rows if r["F_points"] == 5]
    assert optimum == [[0, 1, 1, 0], [1, 0, 0, 1]]
    assert max(r["cut_weight_points"] for r in rows) == 14
    symmetry_representatives = [bits for bits in STATES if bits[0] == 0]
    assert len(symmetry_representatives) == 8
    assert min(map(score, symmetry_representatives)) == 5
    sensitivity = []
    for w in (0, 5, 6, 7, 100):
        fs = [score(bits, w) for bits in STATES if bits[1] == bits[2]]
        fd = [score(bits, w) for bits in STATES if bits[1] != bits[2]]
        assert min(fs) == w and min(fd) == 6
        assert min(score(bits, w) for bits in STATES) == min(w, 6)
        sensitivity.append({"BC_weight_points": w, "BC_same_minimum": min(fs),
                            "BC_different_minimum": min(fd),
                            "global_minimum": min(w, 6)})
    assert sum(score(bits, 6) == 6 for bits in STATES) == 4
    shots = 10 * 500  # The ten evaluations already include final sampling.
    fixed = Q(8, 10) + Q(6, 10) + 2 + Q(4, 10) + Q(2, 10)
    classical = Q(8, 10) + Q(1, 10) + Q(2, 10)
    shot_time = Q(shots, 2000)
    quantum = fixed + shot_time
    available = 5 - fixed
    minimum_rate = Q(shots, 1) / available
    assert (shots, fixed, classical, shot_time, quantum, minimum_rate) == (
        5000, 4, Q(11, 10), Q(5, 2), Q(13, 2), 5000)
    assert fixed + Q(shots, 5000) == 5
    assert fixed + Q(shots, 4999) > 5
    candidates = [
        {"assignment_ABCD": [0, 1, 1, 0], "F_points": 5,
         "supplied_synthetic_P5_Mbit_per_second": 18, "passes_P5_target": False},
        {"assignment_ABCD": [0, 0, 1, 1], "F_points": 6,
         "supplied_synthetic_P5_Mbit_per_second": 22, "passes_P5_target": True},
    ]
    for row in candidates:
        assert score(row["assignment_ABCD"]) == row["F_points"]
        assert (row["supplied_synthetic_P5_Mbit_per_second"] >= 20) == row["passes_P5_target"]
    return {
        "issue_date": "2026-11-28",
        "execution": "Exact sixteen-state classical arithmetic; no circuit, controller, simulator or QPU execution.",
        "vertex_order": ["A", "B", "C", "D"],
        "edges": [{"i": "ABCD"[i], "j": "ABCD"[j], "weight_points": w}
                  for i, j, w in EDGES],
        "absent_pair": "AD",
        "all_sixteen_assignments": rows,
        "conditional_minima_points": {"BC_same": 5, "BC_different": 6},
        "global_minimum_points": 5,
        "global_minimizers_ABCD": optimum,
        "maximum_cut_weight_points": 14,
        "QUBO": {"constant": 19, "linear_ABCD": linear,
                 "quadratic": {"AB": 6, "AC": 8, "BC": 10, "BD": 8, "CD": 6}},
        "Ising": {"convention": "z=1−2x", "constant": "19/2",
                  "ZZ_coefficients": {"AB": "3/2", "AC": 2, "BC": "5/2", "BD": 2, "CD": "3/2"}},
        "complement_symmetry": "F(x)=F(1−x); fixing A=0 gives eight score representatives. This model symmetry supplies no unmeasured throughput data for complemented channel assignments.",
        "middle_weight_sensitivity": sensitivity,
        "QAOA_p1_resources_before_symmetry_reduction": {
            "problem_qubits": 4, "logical_ZZ_terms_per_cost_layer": 5,
            "variational_angles": 2,
            "scope": "Logical cost interactions, not native two-qubit gate count or circuit depth. Routing, gate synthesis and measurement/retry costs depend on the chosen device. No optimal-state probability is determined by the supplied data."},
        "timing_seconds": {"classical": classical, "QAOA_fixed": fixed,
                           "QAOA_shot_evaluation": shot_time, "QAOA_total": quantum,
                           "operation_limit": 5, "available_shot_time": available},
        "shots": {"circuit_evaluations_including_final_sampling": 10,
                  "per_evaluation": 500, "total": shots,
                  "assumed_rate_per_second": 2000,
                  "minimum_rate_for_five_seconds": minimum_rate},
        "P5_target_Mbit_per_second": 20,
        "two_pretested_candidates": candidates,
        "P5_scope": "The two P5 values are given synthetic inputs, not recomputed quantiles: raw throughput observations are absent. Other assignments are untested. Pretesting is explicitly outside the five-second operation clock for both routes.",
        "decision_scope": "At the stipulated inputs, choose the pretested 0011 policy through the 1.1-second classical path. It is qualified among the two pretested candidates, not proved globally best in throughput.",
        "future_criterion": "At least 95% of future repeated runs jointly meet the five-second and P5 targets, with cost or throughput improvement over the matched classical path. This is a proposed criterion, not a measured current success rate or confidence bound."
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
    print("All sixteen assignments, conditional bounds, QUBO/Ising, symmetry, sensitivity and timing checks passed.")
