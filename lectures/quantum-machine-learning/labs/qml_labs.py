#!/usr/bin/env python3
"""Independent, offline educational QML labs; all quantum execution is classical.

Run python qml_labs.py --lab all --output results/reference-results.json.
No credential lookup, network access, cloud API, or provider submission exists here.
"""
import argparse
import json
import platform
from pathlib import Path

import numpy as np


Z = np.diag([1.0, -1.0])
I = np.eye(2)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
# Basis order is |q0 q1>: q0 is the most significant bit.
CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0],
                 [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)


def ry(theta):
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def expectation(state, observable):
    return float(np.real(np.vdot(state, observable @ state)))


def sample_z(mean, shots, rng):
    """Sample independent +/-1 measurements, returning the sample mean."""
    return float(2 * rng.binomial(shots, (1 + mean) / 2) / shots - 1)


def lab1():
    rng = np.random.default_rng(101)
    zero = np.array([1, 0, 0, 0], dtype=complex)
    bell = CNOT @ np.kron(H, I) @ zero
    probabilities = np.abs(bell) ** 2
    counts = rng.multinomial(4096, probabilities)
    z0, zz = expectation(bell, np.kron(Z, I)), expectation(bell, np.kron(Z, Z))
    x = np.array([[0, 1], [1, 0]])
    xx = expectation(bell, np.kron(x, x))
    # The incoherent mixture has the same Z counts but <XX>=0, so Z counts
    # alone cannot certify coherence/entanglement.
    mixture = np.diag([0.5, 0, 0, 0.5])
    mixture_xx = float(np.trace(mixture @ np.kron(x, x)))
    theta = 0.73

    def circuit(t):
        state = ry(t) @ np.array([1, 0], dtype=complex)
        return expectation(state, Z)

    shift = (circuit(theta + np.pi / 2) - circuit(theta - np.pi / 2)) / 2
    analytic = -np.sin(theta)
    eps = 1e-6
    finite_difference = (circuit(theta + eps) - circuit(theta - eps)) / (2 * eps)
    shots = 4096
    plus, minus = circuit(theta + np.pi / 2), circuit(theta - np.pi / 2)
    shot_shift = (sample_z(plus, shots, rng) - sample_z(minus, shots, rng)) / 2
    shift_se = np.sqrt(((1 - plus ** 2) + (1 - minus ** 2)) / (4 * shots))
    assert np.allclose(probabilities, [0.5, 0, 0, 0.5])
    assert abs(shift - analytic) < 1e-12
    assert abs(finite_difference - analytic) < 1e-8
    assert np.allclose([z0, zz, xx, mixture_xx], [0, 1, 1, 0])
    return {
        "execution_level": "classical_statevector_and_binomial_sampling",
        "seed": 101, "basis_order": ["00", "01", "10", "11"],
        "bell_probabilities": probabilities.tolist(), "bell_counts_4096": counts.tolist(),
        "bell_Z0": z0, "bell_Z0Z1": zz, "bell_X0X1": xx,
        "incoherent_mixture_X0X1": mixture_xx,
        "theta_radians": theta, "exact_expectation": circuit(theta),
        "analytic_derivative": float(analytic), "parameter_shift": shift,
        "finite_difference": finite_difference, "shot_parameter_shift": shot_shift,
        "shots_per_shift": shots, "shot_shift_standard_error_known_model": float(shift_se),
        "checks": "Bell correlations and derivative checked against analytic identities",
    }


def amplitude(x):
    x = np.asarray(x, dtype=float)
    norm = np.linalg.norm(x)
    if norm == 0:
        raise ValueError("Zero vectors cannot be normalized into an amplitude state")
    return x / norm


def angle_state(x):
    result = np.array([1.0 + 0j])
    for value in x:
        result = np.kron(result, ry(value) @ np.array([1.0, 0.0]))
    return result


def kmeans(points, initial, projective=False, max_steps=100):
    """Lloyd iteration; projective centroids maximize mean pure-state fidelity."""
    centroids = initial.copy()
    history = []
    for _ in range(max_steps):
        if projective:
            distances = 1 - np.abs(points @ centroids.T) ** 2
        else:
            distances = np.sum((points[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
        labels = np.argmin(distances, axis=1)
        history.append(float(np.sum(distances[np.arange(len(points)), labels])))
        updated = centroids.copy()
        for k in range(len(centroids)):
            cluster = points[labels == k]
            if len(cluster) == 0:
                continue
            if projective:
                # Rayleigh quotient: argmax_c c^T(sum_i |x_i><x_i|)c.
                _, eigenvectors = np.linalg.eigh(cluster.T @ cluster)
                updated[k] = eigenvectors[:, -1]
            else:
                updated[k] = np.mean(cluster, axis=0)
        # Compare projectors because v and -v are the same projective centroid.
        if projective:
            change = np.max(np.abs(np.einsum("ki,kj->kij", updated, updated)
                                   - np.einsum("ki,kj->kij", centroids, centroids)))
        else:
            change = np.max(np.abs(updated - centroids))
        centroids = updated
        if change < 1e-12:
            break
    assert all(b <= a + 1e-10 for a, b in zip(history, history[1:]))
    return {"labels": labels.tolist(), "centroids": centroids.tolist(),
            "objective_history": history, "iterations": len(history)}


def lab2():
    vectors = np.array([[1, 0.10], [1, -0.10], [-1, -0.10], [-1, 0.10],
                        [0.10, 1], [-0.10, 1], [-0.10, -1], [0.10, -1]])
    states = np.array([amplitude(x) for x in vectors])
    initial = states[[0, 4]]
    projective = kmeans(states, initial, projective=True)
    euclidean = kmeans(states, initial)
    v = np.array([1.0, 2.0])
    fidelity = float(abs(np.vdot(amplitude(v), amplitude(-v))) ** 2)
    norm_loss = float(abs(np.vdot(amplitude(v), amplitude(10 * v))) ** 2)
    x, y = np.array([0.4, -0.7]), np.array([-0.3, 1.2])
    numerical_kernel = abs(np.vdot(angle_state(x), angle_state(y))) ** 2
    analytic_kernel = np.prod(np.cos((x - y) / 2) ** 2)
    assert np.allclose(np.linalg.norm(states, axis=1), 1)
    assert np.isclose(fidelity, 1) and np.isclose(norm_loss, 1)
    assert np.isclose(numerical_kernel, analytic_kernel)
    assert projective["labels"][:4] == [0, 0, 0, 0]
    assert projective["labels"][4:] == [1, 1, 1, 1]
    return {
        "execution_level": "classical_linear_algebra_on_encoded_states",
        "original_vectors": vectors.tolist(), "normalized_vectors": states.tolist(),
        "projective_fidelity_clustering": projective, "euclidean_kmeans_on_normalized_data": euclidean,
        "opposite_vector_fidelity": fidelity,
        "opposite_normalized_vector_squared_euclidean_distance": float(
            np.sum((amplitude(v) - amplitude(-v)) ** 2)),
        "scaled_vector_fidelity": norm_loss,
        "angle_kernel_statevector": float(numerical_kernel),
        "angle_kernel_product_formula": float(analytic_kernel),
        "checks": "normalization, phase/norm information loss, Rayleigh centroid, objective descent",
    }


def angle_kernel(a, b):
    return np.prod(np.cos((a[:, None, :] - b[None, :, :]) / 2) ** 2, axis=2)


def rbf_kernel(a, b):
    return np.exp(-np.sum((a[:, None, :] - b[None, :, :]) ** 2, axis=2) / 2)


def trig_features(a):
    c, s = np.cos(a), np.sin(a)
    return np.column_stack([np.ones(len(a)), c[:, 0] * c[:, 1],
                            c[:, 0] * s[:, 1], s[:, 0] * c[:, 1], s[:, 0] * s[:, 1]])


def vqc_closed_form(a, theta):
    # Circuit: Ry(x0),Ry(x1); Ry(theta0),Ry(theta1); CNOT(0,1); <Z1>.
    return np.prod(np.cos(a + theta), axis=1)


def vqc_statevector(a, theta):
    state = np.kron(ry(theta[0]), ry(theta[1])) @ angle_state(a)
    return expectation(CNOT @ state, np.kron(I, Z))


def train_vqc(x, y, rng, steps=600):
    theta, gain, bias = rng.uniform(-np.pi, np.pi, 2), 1.0, 0.0
    learning_rate = 0.08
    history = []
    for step in range(steps):
        f = vqc_closed_form(x, theta)
        residual = gain * f + bias - y
        if step % 100 == 0 or step == steps - 1:
            history.append({"step": step, "train_mse": float(np.mean(residual ** 2))})
        grad_theta = np.empty(2)
        for j in range(2):
            delta = np.zeros(2)
            delta[j] = np.pi / 2
            derivative = (vqc_closed_form(x, theta + delta)
                          - vqc_closed_form(x, theta - delta)) / 2
            grad_theta[j] = 2 * np.mean(residual * gain * derivative)
        grad_gain, grad_bias = 2 * np.mean(residual * f), 2 * np.mean(residual)
        theta -= learning_rate * grad_theta
        gain -= learning_rate * grad_gain
        bias -= learning_rate * grad_bias
    return theta, gain, bias, history


def accuracy(y, score):
    return float(np.mean(np.where(score >= 0, 1, -1) == y))


def lab3():
    runs = []
    for seed in [11, 23, 37, 41, 53]:
        rng = np.random.default_rng(seed)
        # Prespecified data-generating distribution; no held-out optimization.
        all_x = rng.uniform(-1.4, 1.4, size=(240, 2))
        all_y = np.where(all_x[:, 0] * all_x[:, 1] >= 0, 1.0, -1.0)
        train_x, test_x, train_y, test_y = all_x[:80], all_x[80:], all_y[:80], all_y[80:]
        ridge = 0.1
        linear_train = np.column_stack([np.ones(80), train_x])
        linear_test = np.column_stack([np.ones(160), test_x])
        features_train, features_test = trig_features(train_x), trig_features(test_x)
        scores = {}
        for name, a, b in [("linear_ridge", linear_train, linear_test),
                           ("classical_matched_trig_ridge", features_train, features_test)]:
            coefficients = np.linalg.solve(a.T @ a + ridge * np.eye(a.shape[1]), a.T @ train_y)
            scores[name] = {"train": a @ coefficients, "test": b @ coefficients}
        gram = angle_kernel(train_x, train_x)
        eigenvalues = np.linalg.eigvalsh(gram)
        assert np.allclose(gram, gram.T)
        assert np.min(eigenvalues) > -1e-10 and np.allclose(np.diag(gram), 1)
        for name, kernel in [("quantum_angle_fidelity_kernel_ridge", angle_kernel),
                              ("classical_rbf_kernel_ridge", rbf_kernel)]:
            k = kernel(train_x, train_x)
            alpha = np.linalg.solve(k + ridge * np.eye(80), train_y)
            scores[name] = {"train": k @ alpha, "test": kernel(test_x, train_x) @ alpha}
        theta, gain, bias, history = train_vqc(train_x, train_y, rng)
        scores["vqc_2_parameter"] = {
            "train": gain * vqc_closed_form(train_x, theta) + bias,
            "test": gain * vqc_closed_form(test_x, theta) + bias}
        # Independent gate-matrix calculation checks the fast closed formula.
        check_error = max(abs(vqc_statevector(x, theta) - vqc_closed_form(x[None, :], theta)[0])
                          for x in test_x[:10])
        assert check_error < 1e-12
        # VQC function is exactly a linear combination of four trig products.
        t0, t1 = theta
        weights = np.array([0, np.cos(t0) * np.cos(t1), -np.cos(t0) * np.sin(t1),
                            -np.sin(t0) * np.cos(t1), np.sin(t0) * np.sin(t1)])
        assert np.allclose(features_test @ weights, vqc_closed_form(test_x, theta))
        metrics = {name: {"train_accuracy": accuracy(train_y, s["train"]),
                          "test_accuracy": accuracy(test_y, s["test"]),
                          "test_mse": float(np.mean((s["test"] - test_y) ** 2))}
                   for name, s in scores.items()}
        runs.append({"seed": seed, "metrics": metrics, "vqc_theta": theta.tolist(),
                     "vqc_gain": float(gain), "vqc_bias": float(bias), "vqc_loss_history": history,
                     "kernel_minimum_eigenvalue": float(np.min(eigenvalues)),
                     "vqc_matrix_vs_formula_max_error": check_error})
    names = list(runs[0]["metrics"])
    summary = {}
    for name in names:
        values = [run["metrics"][name]["test_accuracy"] for run in runs]
        summary[name] = {"test_accuracy_mean": float(np.mean(values)),
                         "test_accuracy_sample_std_across_seeds": float(np.std(values, ddof=1))}
    return {"execution_level": "classical_exact_statevector_formula_and_linear_algebra",
            "dataset": "independent uniform [-1.4,1.4]^2, label=sign(x0*x1)",
            "train_size": 80, "test_size": 160, "ridge_lambda": 0.1,
            "vqc_steps": 600, "vqc_learning_rate": 0.08,
            "shots": None, "hyperparameter_selection": "prespecified; no validation/test selection",
            "runs": runs, "summary": summary,
            "interpretation": "toy nonlinear task; VQC and fidelity kernel are classically tractable; no quantum advantage"}


def lab4():
    # An explicit synthetic workload, not a provider's timing or price quote.
    parameters, batch, steps, groups, shots = 6, 12, 25, 2, 2048
    settings_per_example = 1 + 2 * parameters
    circuit_settings = steps * batch * settings_per_example * groups
    total_shots = circuit_settings * shots
    capacity_per_job = 300
    jobs = (circuit_settings + capacity_per_job - 1) // capacity_per_job
    circuit_duration_seconds = 50e-6
    assumed_queue_seconds_per_job = 30.0
    assumed_fixed_seconds_per_job = 0.2
    shot_time = total_shots * circuit_duration_seconds
    queue_time = jobs * assumed_queue_seconds_per_job
    overhead_time = jobs * assumed_fixed_seconds_per_job
    n_train, n_test = 80, 160
    # Off diagonal symmetric pairs; diagonal K(x,x)=1 is known in ideal pure-state setting.
    kernel_pairs_train = n_train * (n_train - 1) // 2
    kernel_pairs_test = n_train * n_test
    rng = np.random.default_rng(404)
    ideal_mean = np.cos(0.73)
    shot_sweep = []
    for n in [128, 512, 2048, 8192]:
        trials = 1000
        means = 2 * rng.binomial(n, (1 + ideal_mean) / 2, trials) / n - 1
        theoretical_se = np.sqrt((1 - ideal_mean ** 2) / n)
        shot_sweep.append({"shots": n, "repeated_experiments": trials,
                           "empirical_rmse": float(np.sqrt(np.mean((means - ideal_mean) ** 2))),
                           "binomial_standard_error": float(theoretical_se)})
    # Compare algebraic count to enumeration of the actual workload dimensions.
    enumerated = sum(1 for _ in range(steps) for _ in range(batch)
                     for _ in range(settings_per_example) for _ in range(groups))
    assert enumerated == circuit_settings
    assert np.isclose(shot_sweep[0]["binomial_standard_error"] /
                      shot_sweep[-1]["binomial_standard_error"], 8)
    return {
        "execution_level": "offline_cost_bookkeeping_and_classical_binomial_sampling",
        "physical_qpu_executed": False, "seed": 404,
        "assumptions": {"parameters": parameters, "batch_size": batch, "steps": steps,
                        "measurement_groups": groups, "shots_per_setting": shots,
                        "settings_per_example_including_forward": settings_per_example,
                        "max_settings_per_job": capacity_per_job,
                        "circuit_duration_seconds_per_shot": circuit_duration_seconds,
                        "queue_seconds_per_job_serial_assumption": assumed_queue_seconds_per_job,
                        "fixed_overhead_seconds_per_job": assumed_fixed_seconds_per_job},
        "vqc": {"circuit_settings": circuit_settings, "total_shots": total_shots, "jobs": jobs,
                "shot_execution_seconds": shot_time, "serial_queue_seconds": queue_time,
                "fixed_overhead_seconds": overhead_time,
                "assumed_serial_wall_seconds": shot_time + queue_time + overhead_time},
        "kernel": {"train_unique_off_diagonal_pairs": kernel_pairs_train,
                   "test_train_pairs": kernel_pairs_test,
                   "settings_total": kernel_pairs_train + kernel_pairs_test,
                   "shots_at_same_shot_budget": (kernel_pairs_train + kernel_pairs_test) * shots},
        "shot_sweep": shot_sweep,
        "checks": "setting count independently enumerated; standard error scales as shots^(-1/2)",
        "not_included": ["transpilation and routing", "state-preparation decomposition", "calibration",
                         "provider billing", "parallel scheduling", "failed jobs", "data transfer"]}


def lab5():
    rng = np.random.default_rng(505)
    ideal = float(np.cos(0.73))
    # E(s)=E(0)*exp(-lambda*s): intentionally prescribed scalar noise model.
    noise_rate = 0.12
    scales = np.array([1.0, 2.0, 3.0])
    exact_noisy = ideal * np.exp(-noise_rate * scales)
    coefficients = np.array([3.0, -3.0, 1.0])
    # Conditions for quadratic Richardson extrapolation at s=0.
    assert np.allclose([np.sum(coefficients), coefficients @ scales,
                        coefficients @ scales ** 2], [1, 0, 0])
    readout_error = 0.08
    calibration_shots_per_state, data_shots_per_scale = 20000, 4000
    e01 = rng.binomial(calibration_shots_per_state, readout_error) / calibration_shots_per_state
    e10 = rng.binomial(calibration_shots_per_state, readout_error) / calibration_shots_per_state
    estimated_assignment = np.array([[1 - e01, e10], [e01, 1 - e10]])
    attenuation, offset = 1 - e01 - e10, e10 - e01
    repetitions = 1000
    noisy_observed = np.array([
        2 * rng.binomial(data_shots_per_scale, (1 + (1 - 2 * readout_error) * e) / 2,
                         repetitions) / data_shots_per_scale - 1 for e in exact_noisy]).T
    corrected = (noisy_observed - offset) / attenuation
    zne = corrected @ coefficients
    exact_zne = float(coefficients @ exact_noisy)
    # Fixed calibrated matrix: intervals/variance below condition on this single
    # calibration and omit its uncertainty, deliberately stated in the report.
    true_observed = (1 - 2 * readout_error) * exact_noisy
    corrected_variances = (1 - true_observed ** 2) / (data_shots_per_scale * attenuation ** 2)
    zne_variance = float((coefficients ** 2) @ corrected_variances)
    budget = len(scales) * data_shots_per_scale
    # Same science-shot budget, no extrapolation; same calibration cost excluded
    # from both. This is the relevant budget-matched baseline.
    baseline_observed = 2 * rng.binomial(budget, (1 + true_observed[0]) / 2, repetitions) / budget - 1
    baseline_corrected = (baseline_observed - offset) / attenuation

    def summarize(values):
        return {"mean": float(np.mean(values)), "bias_to_ideal": float(np.mean(values) - ideal),
                "sample_std": float(np.std(values, ddof=1)),
                "rmse_to_ideal": float(np.sqrt(np.mean((values - ideal) ** 2)))}

    # Assignment inverse and affine expectation correction must agree.
    probability_observed = np.array([(1 + noisy_observed[0, 0]) / 2,
                                     (1 - noisy_observed[0, 0]) / 2])
    probability_corrected = np.linalg.solve(estimated_assignment, probability_observed)
    assert np.isclose(probability_corrected[0] - probability_corrected[1], corrected[0, 0])
    assert abs(exact_zne - ideal) < abs(exact_noisy[0] - ideal)
    return {
        "execution_level": "classical_scalar_noise_and_binomial_readout_toy",
        "physical_qpu_executed": False, "seed": 505,
        "ideal_expectation": ideal, "noise_model": "E(s)=cos(0.73)*exp(-0.12*s)",
        "noise_scale_factors": scales.tolist(), "exact_noisy_expectations": exact_noisy.tolist(),
        "richardson_coefficients": coefficients.tolist(), "exact_zne_expectation": exact_zne,
        "exact_zne_bias": exact_zne - ideal,
        "true_symmetric_readout_error": readout_error,
        "estimated_assignment_matrix_columns_true_state": estimated_assignment.tolist(),
        "assignment_condition_number": float(np.linalg.cond(estimated_assignment)),
        "calibration_shots_total": 2 * calibration_shots_per_state,
        "science_shots_per_scale": data_shots_per_scale, "repeated_science_experiments": repetitions,
        "first_experiment": {"raw_by_scale": noisy_observed[0].tolist(),
                             "readout_corrected_by_scale": corrected[0].tolist(), "zne": float(zne[0])},
        "raw_scale_1": summarize(noisy_observed[:, 0]),
        "readout_corrected_scale_1": summarize(corrected[:, 0]),
        "readout_corrected_zne": summarize(zne),
        "budget_matched_no_zne": summarize(baseline_corrected),
        "zne_conditional_standard_error_known_model": float(np.sqrt(zne_variance)),
        "coefficient_squared_sum": float(np.sum(coefficients ** 2)),
        "calibration_uncertainty": "not propagated; 1000 repetitions share one fixed calibration",
        "not_demonstrated": ["physical noise scaling", "gate folding", "fault tolerance", "error correction"],
        "checks": "Richardson moment conditions; matrix inverse equals affine correction; bias-variance comparison"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", choices=["1", "2", "3", "4", "5", "all"], default="all")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    labs = {"1": lab1, "2": lab2, "3": lab3, "4": lab4, "5": lab5}
    selected = labs if args.lab == "all" else {args.lab: labs[args.lab]}
    result = {"archive_basis_date": "2026-10-20", "python_version": platform.python_version(),
              "numpy_version": np.__version__, "execution_level": "classical_offline_only",
              "labs": {key: function() for key, function in selected.items()}}
    payload = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
        print("Saved " + args.output.name)
    else:
        print(payload)


if __name__ == "__main__":
    main()
