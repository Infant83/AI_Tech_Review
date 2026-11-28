"""Recalculate the educational H-phase-H example using complex amplitudes."""
from pathlib import Path
import cmath
import json
import math


def hadamard(state):
    a, b = state
    return ((a + b) / math.sqrt(2), (a - b) / math.sqrt(2))


results = []
for degrees in [0, 45, 90, 180, 270, 360]:
    a, b = hadamard((1 + 0j, 0j))
    before = (a, cmath.exp(1j * math.radians(degrees)) * b)
    after = hadamard(before)
    probabilities = [abs(value) ** 2 for value in after]
    expected_zero = (1 + math.cos(math.radians(degrees))) / 2
    assert all(abs(abs(value) ** 2 - 0.5) < 1e-12 for value in before)
    assert abs(probabilities[0] - expected_zero) < 1e-12
    assert abs(sum(probabilities) - 1) < 1e-12
    results.append({'phase_degrees': degrees,
                    'before_final_H': [abs(value) ** 2 for value in before],
                    'after_final_H': probabilities})

expected = json.loads((Path(__file__).parent / 'interference-values.json').read_text())
for actual, stored in zip(results, expected):
    assert actual['phase_degrees'] == stored['phase_degrees']
    for key in ['before_final_H', 'after_final_H']:
        assert all(abs(a - b) < 1e-12 for a, b in zip(actual[key], stored[key]))
print('Six phase settings agree with the analytic probability and stored data within 1e-12.')
