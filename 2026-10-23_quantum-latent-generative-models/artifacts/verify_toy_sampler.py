"""Exact small-case checks for the review's single-loop distinguishable control.

Original check code, no third-party source. The physical convention follows the
inspected upstream beam-splitter amplitude: emitted=c*a-s*b, loop=s*a+c*b.
This control removes interference between distinguishable photons while keeping
the SAME single-particle unitary, including all single-particle amplitudes.
"""
from pathlib import Path
from collections import defaultdict
from itertools import product, permutations, combinations_with_replacement
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def single_loop_unitary(theta):
    """Columns: initial loop vacuum, incoming bins. Rows: outputs, final loop."""
    size = len(theta) + 1
    loop = np.eye(size)[0].copy()
    emitted = []
    for i, angle in enumerate(theta):
        incoming = np.eye(size)[i + 1]
        c, s = math.cos(angle), math.sin(angle)
        emitted.append(c * loop - s * incoming)
        loop = s * loop + c * incoming
    return np.asarray(emitted + [loop])


def labelled_exact(unitary, occupied):
    dist = defaultdict(float)
    for outputs in product(range(len(unitary)), repeat=len(occupied)):
        probability = math.prod(abs(unitary[j, i]) ** 2 for j, i in zip(outputs, occupied))
        occupancy = tuple(outputs.count(j) for j in range(len(unitary)))
        dist[occupancy] += probability
    return dist


def routing_exact(theta, input_state):
    # State is (already emitted occupancy tuple, loop population).
    dist = {((), 0): 1.0}
    for angle, incoming in zip(theta, input_state):
        next_dist = defaultdict(float)
        p, q = math.cos(angle) ** 2, math.sin(angle) ** 2
        for (emitted, loop), weight in dist.items():
            for a in range(loop + 1):
                for b in range(incoming + 1):
                    probability = math.comb(loop, a) * p**a * (1-p)**(loop-a)
                    probability *= math.comb(incoming, b) * q**b * (1-q)**(incoming-b)
                    next_dist[(emitted + (a+b,), loop+incoming-a-b)] += weight * probability
        dist = next_dist
    return {emitted + (loop,): p for (emitted, loop), p in dist.items()}


def boson_exact(unitary, occupied):
    dist = {}
    n = len(occupied)
    for outputs in combinations_with_replacement(range(len(unitary)), n):
        amplitude = sum(math.prod(unitary[outputs[j], occupied[perm[j]]] for j in range(n))
                        for perm in permutations(range(n)))
        occupancy = tuple(outputs.count(j) for j in range(len(unitary)))
        dist[occupancy] = abs(amplitude)**2 / math.prod(math.factorial(k) for k in occupancy)
    return dist


def boson_routing_exact(theta, input_state):
    # Reuse only pinned, inspected transition probabilities, no random draws.
    from run_toy import prepare_sources
    prepare_sources()
    from src.tbi_sampler import _calculate_probs_after_bs
    dist = {((), 0): 1.0}
    for angle, incoming in zip(theta, input_state):
        next_dist = defaultdict(float)
        for (emitted, loop), weight in dist.items():
            choices, probabilities = _calculate_probs_after_bs(loop, incoming, angle)
            for output, probability in zip(choices, probabilities):
                next_dist[(emitted + (int(output),), loop+incoming-int(output))] += weight * probability
        dist = next_dist
    return {emitted + (loop,): p for (emitted, loop), p in dist.items()}


def main():
    checks = []
    for angles in [[math.pi/4]*3, [.17, .63, 1.22], [.0, math.pi/2, .37]]:
        unitary = single_loop_unitary(angles)
        unitarity_error = float(np.max(np.abs(unitary.T @ unitary - np.eye(4))))
        assert unitarity_error < 1e-12
        state = [1, 0, 1]
        independent = labelled_exact(unitary, [1, 3])
        routing = routing_exact(angles, state)
        error = max(abs(independent[k] - routing.get(k, 0)) for k in independent)
        assert error < 1e-12
        assert abs(sum(independent.values()) - 1) < 1e-12
        boson = boson_exact(unitary, [1, 3])
        quantum_routing = boson_routing_exact(angles, state)
        boson_error = max(abs(boson[k] - quantum_routing.get(k, 0)) for k in boson)
        assert boson_error < 1e-12
        assert abs(sum(boson.values()) - 1) < 1e-12
        checks.append({"theta_radians": angles, "max_unitarity_error": unitarity_error,
                       "max_probability_error_categorical_vs_binomial": error,
                       "max_probability_error_permanent_vs_upstream_boson_transition": boson_error,
                       "input": state, "total_probability": sum(independent.values())})
    full_angles = np.random.default_rng(20261024).uniform(0, np.pi/2, 16)
    u = single_loop_unitary(full_angles)
    error = float(np.max(np.abs(u.T @ u - np.eye(17))))
    assert error < 1e-12
    result = {"scope": "same-unitary distinguishable control and upstream quantum transitions; exact 2-photon cases",
              "sampling_definition": "independent labelled-photon categorical draws from |U_ji|^2; equivalent sequential binomial form",
              "same_conditions": "lossless unitary, 16 incoming bins, final loop retained for conservation then discarded from neural-network latent",
              "checks": checks, "full_17x17_unitarity_error": error,
              "passed": True}
    (ROOT / "artifacts" / "sampler_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
