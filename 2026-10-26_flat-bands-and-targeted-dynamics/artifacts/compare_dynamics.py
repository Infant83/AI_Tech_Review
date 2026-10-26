#!/usr/bin/env python3
"""Small, exact classical teaching calculations; not a paper reproduction.

Run with Python 3 and numpy. No QPU, molecular integrals, finite-shot data,
StateDRIFT fourth-order allocator, or native-gate compilation is used.
"""
from __future__ import annotations

import itertools
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FIGURES = HERE / "figures"
I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.diag([1, -1]).astype(complex)
PAULIS = [Z, X, Y]
METHODS = ["lie", "partial_strang", "full_strang", "lambda_second"]
COLORS = ["#64748b", "#c65d2e", "#207e78", "#6d55a2"]
LABELS = {
    "en": ["Lie (order 1)", "Partial-Strang (order 1)", "Full Strang (order 2)", "Lambda formula (order 2)"],
    "ko": ["Lie 1차", "Partial–Strang 1차", "완전 Strang 2차", "최적 λ 공식 2차"],
}


def exp_h(h: np.ndarray, time: float) -> np.ndarray:
    """Hermitian exponential by spectral decomposition, with no scipy."""
    values, vectors = np.linalg.eigh(h)
    return (vectors * np.exp(-1j * time * values)) @ vectors.conj().T


def ordered_product(factors: list[tuple[np.ndarray, float]]) -> np.ndarray:
    """Literal left-to-right matrix product; rightmost factor acts first."""
    result = I.copy()
    for h, time in factors:
        result = result @ exp_h(h, time)
    return result


def formula_step(alpha: float, dt: float, method: str) -> np.ndarray:
    if method == "lie":
        factors = [(Z, dt), (X, alpha * dt), (Y, alpha * dt)]
    elif method == "partial_strang":
        # Dominant half steps enclose an UNSYMMETRIZED small-term product.
        factors = [(Z, dt / 2), (X, alpha * dt), (Y, alpha * dt), (Z, dt / 2)]
    elif method == "full_strang":
        factors = [(Z, dt / 2), (X, alpha * dt / 2), (Y, alpha * dt),
                   (X, alpha * dt / 2), (Z, dt / 2)]
    elif method == "lambda_second":
        lam = 0.5 - math.sqrt(3) / 6
        block = [(X, alpha * dt / 4), (Y, alpha * dt / 2), (X, alpha * dt / 4)]
        factors = [(Z, lam * dt)] + block + [(Z, (1 - 2 * lam) * dt)] + block + [(Z, lam * dt)]
    else:
        raise ValueError(method)
    return ordered_product(factors)


def initial_state() -> np.ndarray:
    theta, phi = 1.05, 0.38
    return np.array([math.cos(theta / 2), np.exp(1j * phi) * math.sin(theta / 2)])


def product_metrics(alpha: float, total_time: float, steps: int) -> dict:
    psi = initial_state()
    exact = exp_h(Z + alpha * X + alpha * Y, total_time)
    exact_psi = exact @ psi
    record = {}
    for method in METHODS:
        approx = np.linalg.matrix_power(formula_step(alpha, total_time / steps, method), steps)
        out = approx @ psi
        record[method] = {
            "operator_spectral_norm_error": float(np.linalg.norm(approx - exact, 2)),
            "state_l2_error": float(np.linalg.norm(out - exact_psi)),
            "observable_bias": {name: float(np.vdot(out, obs @ out).real - np.vdot(exact_psi, obs @ exact_psi).real)
                                for name, obs in [("Z", Z), ("X", X)]},
            "merged_exponential_count": {"lie": 3 * steps, "partial_strang": 3 * steps + 1,
                                         "full_strang": 4 * steps + 1, "lambda_second": 8 * steps + 1}[method],
        }
    return record


def qdrift_unitaries(coefficients: np.ndarray, probabilities: np.ndarray, dt: float) -> list[np.ndarray]:
    if min(probabilities) <= 0 or abs(sum(probabilities) - 1) > 1e-10:
        raise ValueError("Probabilities must be positive and sum to one.")
    return [exp_h(p, c * dt / q) for c, q, p in zip(coefficients, probabilities, PAULIS)]


def averaged_channel(unitaries: list[np.ndarray], probabilities: np.ndarray) -> np.ndarray:
    # Column-major vec(U rho U†) = (U* tensor U) vec(rho).
    return sum(q * np.kron(u.conj(), u) for q, u in zip(probabilities, unitaries))


def exact_qdrift_moments(coefficients: np.ndarray, probabilities: np.ndarray,
                        total_time: float, steps: int, observables: list[np.ndarray]) -> list[dict]:
    """Average over ALL independent term choices, without Monte Carlo.

    The two-copy channel uses the SAME term in both replicas. It computes
    E[<O>_trajectory**2], hence trajectory variance, not measurement shot noise.
    """
    psi = initial_state()
    rho = np.outer(psi, psi.conj())
    us = qdrift_unitaries(coefficients, probabilities, total_time / steps)
    channel = averaged_channel(us, probabilities)
    rho_mean = (np.linalg.matrix_power(channel, steps) @ rho.reshape(-1, order="F")).reshape(2, 2, order="F")
    doubles = [np.kron(u, u) for u in us]
    channel2 = averaged_channel(doubles, probabilities)
    rho2 = np.kron(rho, rho)
    rho2_mean = (np.linalg.matrix_power(channel2, steps) @ rho2.reshape(-1, order="F")).reshape(4, 4, order="F")
    h = sum(c * p for c, p in zip(coefficients, PAULIS))
    psi_exact = exp_h(h, total_time) @ psi
    answers = []
    for obs in observables:
        mean = float(np.trace(obs @ rho_mean).real)
        second = float(np.trace(np.kron(obs, obs) @ rho2_mean).real)
        target = float(np.vdot(psi_exact, obs @ psi_exact).real)
        variance = max(0.0, second - mean**2)
        answers.append({"exact_expectation": target, "mean": mean, "bias": mean - target,
                        "trajectory_variance": variance})
    return answers


def optimize_toy_distribution(coefficients: np.ndarray, total_time: float, steps: int,
                              target: int, trajectories: int = 200, mixing_floor: float = 0.2) -> np.ndarray:
    """Deterministic exact-oracle toy search, NOT the StateDRIFT allocator.

    Minimize exact bias² + trajectory_variance/M, using the true full dynamics.
    The floor q >= 0.2*q_van avoids vanishing probabilities. StateDRIFT instead
    estimates local densities and uses truncated objectives; this does neither.
    """
    base = np.abs(coefficients) / np.abs(coefficients).sum()
    def score(q):
        m = exact_qdrift_moments(coefficients, q, total_time, steps, [Z, X])[target]
        return m["bias"]**2 + m["trajectory_variance"] / trajectories
    best, best_score = base.copy(), score(base)
    for a in range(17):
        for b in range(17 - a):
            r = np.array([a, b, 16 - a - b]) / 16
            q = mixing_floor * base + (1 - mixing_floor) * r
            loss = score(q)
            if loss < best_score:
                best, best_score = q, loss
    for delta in [0.02, 0.005, 0.001, 0.0002, 0.00004]:
        for _ in range(100):
            improved = False
            for a, b in itertools.permutations(range(3), 2):
                trial = best.copy()
                trial[a] += delta
                trial[b] -= delta
                if np.any(trial < mixing_floor * base - 1e-14):
                    continue
                loss = score(trial)
                if loss < best_score - 1e-18:
                    best, best_score, improved = trial, loss, True
            if not improved:
                break
    return best


def independently_check_enumeration(coefficients, probabilities, total_time, steps):
    """Brute-force all 3**N pure trajectories as an independent check."""
    psi = initial_state()
    us = qdrift_unitaries(coefficients, probabilities, total_time / steps)
    means, second = np.zeros(2), np.zeros(2)
    for choices in itertools.product(range(3), repeat=steps):
        weight, state = 1.0, psi.copy()
        for j in choices:
            weight *= probabilities[j]
            state = us[j] @ state
        values = np.array([np.vdot(state, o @ state).real for o in [Z, X]])
        means += weight * values
        second += weight * values**2
    moments = exact_qdrift_moments(coefficients, probabilities, total_time, steps, [Z, X])
    assert np.allclose(means, [m["mean"] for m in moments], atol=2e-13)
    assert np.allclose(second - means**2, [m["trajectory_variance"] for m in moments], atol=2e-13)
    return float(max(np.max(np.abs(means - [m["mean"] for m in moments])),
                     np.max(np.abs(second - means**2 - [m["trajectory_variance"] for m in moments]))))


def svg_start(title: str, description: str, width=1180, height=690):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
            '<rect width="100%" height="100%" fill="#fffdf8"/>',
            '<style>text{font-family:Arial,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;fill:#23333d} .title{font-size:25px;font-weight:700} .small{font-size:14px} .label{font-size:17px} .tick{font-size:13px}</style>',
            f'<text x="46" y="40" class="title">{escape(title)}</text>']


def line_plot(svg, bounds, xs, series, xlim, ylim, xlabel, ylabel, logx=True, logy=True):
    x, y, w, h = bounds
    def scale(v, lim, logarithmic):
        if logarithmic:
            v, lo, hi = math.log10(max(v, 1e-30)), math.log10(lim[0]), math.log10(lim[1])
        else:
            lo, hi = lim
        return (v - lo) / (hi - lo)
    def px(v): return x + w * scale(v, xlim, logx)
    def py(v): return y + h * (1 - scale(v, ylim, logy))
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="#aebbc0"/>')
    xticks = [2**i for i in range(0, 11) if xlim[0] <= 2**i <= xlim[1]] if logx else [xlim[0], (xlim[0]+xlim[1])/2, xlim[1]]
    if logx and xlim[0] < 1:
        xticks = [10**i for i in range(-6, 2) if xlim[0] <= 10**i <= xlim[1]]
    yticks = [10**i for i in range(-15, 2) if ylim[0] <= 10**i <= ylim[1]] if logy else list(np.linspace(*ylim, 5))
    for v in xticks:
        vx = px(v)
        svg.append(f'<line x1="{vx:.2f}" y1="{y}" x2="{vx:.2f}" y2="{y+h}" stroke="#e4e9e7"/>')
        svg.append(f'<text x="{vx:.2f}" y="{y+h+21}" text-anchor="middle" class="tick">{v:g}</text>')
    for v in yticks:
        vy = py(v)
        label = f'10^{int(round(math.log10(v)))}' if logy else f'{v:.2g}'
        svg.append(f'<line x1="{x}" y1="{vy:.2f}" x2="{x+w}" y2="{vy:.2f}" stroke="#e4e9e7"/>')
        svg.append(f'<text x="{x-8}" y="{vy+4:.2f}" text-anchor="end" class="tick">{label}</text>')
    for values, color, _ in series:
        points = ' '.join(f'{px(a):.3f},{py(max(b, ylim[0])):.3f}' for a, b in zip(xs, values))
        svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
    svg.append(f'<text x="{x+w/2}" y="{y+h+48}" text-anchor="middle" class="label">{escape(xlabel)}</text>')
    svg.append(f'<text x="{x-57}" y="{y+h/2}" transform="rotate(-90 {x-57} {y+h/2})" text-anchor="middle" class="label">{escape(ylabel)}</text>')


def make_figures(data):
    for lang in ["ko", "en"]:
        ko = lang == "ko"
        labels = LABELS[lang]
        title = "앞뒤 절반 단계는 전체 2차 대칭화와 다르다" if ko else "Dominant half steps do not make a full second-order formula"
        desc = "Exact one-qubit educational calculation H=Z+0.2X+0.2Y, T=1; not a molecular or QPU reproduction. Left: state-l2 error versus N. Right: propagator spectral-norm error versus alpha at fixed N=64."
        svg = svg_start(title, desc)
        svg.append('<text x="46" y="70" class="small">H = Z + αX + αY; T = 1; ħ = 1. Exact classical 2 × 2 calculation.</text>')
        ns = [r["N"] for r in data["product_N_sweep"]]
        series = [([r["methods"][m]["state_l2_error"] for r in data["product_N_sweep"]], color, label)
                  for m, color, label in zip(METHODS, COLORS, labels)]
        line_plot(svg, (110, 135, 420, 330), ns, series, (2, 256), (1e-10, 1),
                  "단계 수 N (α = 0.2)" if ko else "Steps N (alpha = 0.2)",
                  "상태 ℓ2 오차" if ko else "State l2 error")
        alphas = [r["alpha"] for r in data["product_alpha_sweep"]]
        series = [([r["methods"][m]["operator_spectral_norm_error"] for r in data["product_alpha_sweep"]], color, label)
                  for m, color, label in zip(METHODS, COLORS, labels)]
        line_plot(svg, (685, 135, 420, 330), alphas, series, (1e-4, 0.5), (1e-13, 1e-1),
                  "작은 항의 계수 α (N = 64)" if ko else "Small-term coefficient alpha (N = 64)",
                  "전파 연산자 2-노름 오차" if ko else "Propagator spectral-norm error")
        for j, (label, color) in enumerate(zip(labels, COLORS)):
            lx, ly = 75 + (j % 2) * 550, 555 + (j // 2) * 32
            svg.append(f'<line x1="{lx}" y1="{ly}" x2="{lx+32}" y2="{ly}" stroke="{color}" stroke-width="4"/><text x="{lx+42}" y="{ly+5}" class="label">{escape(label)}</text>')
        text1 = "교육 계산. 논문 분자 결과·실기기 데이터가 아님. 모든 곡선의 총 시간 T는 같다." if ko else "Teaching calculation; not paper reproduction or hardware data. Same total time T for every curve."
        text2 = "N=16의 병합 지수함수 수: Lie 48, PS 49, Strang 65, λ 129. 네이티브 게이트 수가 아니다." if ko else "At N=16: merged exponentials 48 / 49 / 65 / 129. These are not native-gate counts."
        svg.extend([f'<text x="46" y="638" class="small">{text1}</text>', f'<text x="46" y="663" class="small">{text2}</text>', '</svg>'])
        (FIGURES / f"product_formula_comparison_{lang}.svg").write_text('\n'.join(svg), encoding="utf-8")

        title = "어느 관측량을 고르느냐가 확률 배분을 바꾼다" if ko else "The target observable changes the sampling distribution"
        desc = "Exact averaged qDRIFT channels for H=Z+0.2X+0.2Y, same initial state, T=0.4,N=4. Exact-oracle toy distributions minimize MSE for 200 trajectories. Not the StateDRIFT allocation algorithm. No measurement shot noise."
        svg = svg_start(title, desc)
        svg.append('<text x="46" y="73" class="small">H = Z + 0.2X + 0.2Y; T = 0.4; N = 4; M = 200 trajectories.</text>')
        names = ["계수 기반 qDRIFT", "Z 목표의 교육 최적화", "X 목표의 교육 최적화"] if ko else ["Coefficient-based qDRIFT", "Toy optimization for Z", "Toy optimization for X"]
        records = data["qdrift_comparison"]
        max_mse = 0.0055  # Common linear scale in both panels.
        for panel, obs in enumerate(["Z", "X"]):
            x0 = 82 + panel * 565
            svg.append(f'<text x="{x0}" y="119" class="label">{obs}: '+("평균제곱오차 = 편향² + trajectory 분산/M" if ko else "MSE = bias squared + trajectory variance/M")+'</text>')
            for i, (r, name) in enumerate(zip(records, names)):
                yy = 157 + i * 87
                m = r["observables"][obs]
                bias_width = 400 * m["bias"]**2 / max_mse
                var_width = 400 * m["trajectory_variance"] / 200 / max_mse
                svg.append(f'<text x="{x0}" y="{yy}" class="small">{escape(name)}</text>')
                svg.append(f'<rect x="{x0}" y="{yy+10}" width="{bias_width:.3f}" height="25" fill="#bd5939"/>')
                svg.append(f'<rect x="{x0+bias_width:.3f}" y="{yy+10}" width="{var_width:.3f}" height="25" fill="#247f79"/>')
                svg.append(f'<text x="{x0}" y="{yy+57}" class="small">bias={m["bias"]:.5f}; MSE={m["MSE_M200"]:.6f}</text>')
            svg.append(f'<line x1="{x0}" y1="413" x2="{x0+400}" y2="413" stroke="#9aa8ad"/>')
            for value in [0, 0.001, 0.002, 0.003, 0.004, 0.005]:
                xx = x0 + 400 * value / max_mse
                svg.append(f'<text x="{xx:.2f}" y="433" text-anchor="middle" class="tick">{value:g}</text>')
        svg.append('<rect x="80" y="455" width="19" height="19" fill="#bd5939"/><text x="110" y="471" class="small">'+("편향²" if ko else "Bias squared")+'</text>')
        svg.append('<rect x="290" y="455" width="19" height="19" fill="#247f79"/><text x="320" y="471" class="small">'+("trajectory 분산 / M" if ko else "Trajectory variance / M")+'</text>')
        for i, (r, name) in enumerate(zip(records, names)):
            svg.append(f'<text x="80" y="{517+i*28}" class="small">{escape(name)}: q(Z,X,Y) = '+', '.join(f'{v:.4f}' for v in r["probabilities"])+'.</text>')
        text1 = "정확한 평균·분산으로 최적화한 교육 예제이며 StateDRIFT 구현·분자 결과 재현이 아니다." if ko else "Exact-oracle teaching optimization; NOT a StateDRIFT implementation or molecular reproduction."
        text2 = "표시한 분산은 회로 선택 trajectory의 변동이다. 최종 양자 측정 샷 잡음은 포함하지 않았다." if ko else "Variance is over random circuit trajectories; final quantum measurement shot noise is excluded."
        svg.extend([f'<text x="46" y="638" class="small">{text1}</text>', f'<text x="46" y="663" class="small">{text2}</text>', '</svg>'])
        (FIGURES / f"observable_sampling_comparison_{lang}.svg").write_text('\n'.join(svg), encoding="utf-8")

        title = "평평한 밴드가 작은 연산자 노름을 뜻하지는 않는다" if ko else "A flat band does not imply a small Hamiltonian norm"
        desc = "Algebraic two-band counterexample H(k)=A[cos(k) Z+sin(k) X], eigenvalues +A and -A, hence zero bandwidth. Spectral norm A; component commutator norm A squared at k=pi/4. Not a material simulation."
        svg = svg_start(title, desc)
        svg.append('<text x="46" y="73" class="small">H(k) = A[cos(k) Z + sin(k) X]; A = 1; k in [−π, π].</text>')
        ks = list(np.linspace(-math.pi, math.pi, 129))
        line_plot(svg, (110, 145, 420, 300), ks,
                  [([1.0]*129, COLORS[1], "+A"), ([-1.0]*129, COLORS[2], "−A")],
                  (-math.pi, math.pi), (-1.5, 1.5), "k", "고유에너지" if ko else "Eigenenergy", False, False)
        line_plot(svg, (685, 145, 420, 300), ks,
                  [(list(np.cos(ks)), COLORS[1], "cos k"), (list(np.sin(ks)), COLORS[2], "sin k")],
                  (-math.pi, math.pi), (-1.5, 1.5), "k", "Pauli 성분 계수" if ko else "Pauli coefficients", False, False)
        messages = ["두 밴드의 폭 W는 모두 0이다. 그런데 ||H(k)||₂=A이며, A는 원하는 만큼 크게 고를 수 있다.",
                    "k=π/4에서 Z·X 성분은 같은 크기다. 성분 간 교환자 노름은 A²이다.",
                    "이는 대수적 교육 반례다. 특정 평탄밴드 재료나 전자구조·큐비트 매핑의 계산 결과가 아니다."] if ko else [
                    "Both bandwidths W are zero, while ||H(k)||2=A, and A can be arbitrarily large.",
                    "At k=pi/4 the Z and X components are equal; their commutator norm is A squared.",
                    "An algebraic counterexample, not a material calculation or electronic-to-qubit mapping."]
        for j, msg in enumerate(messages):
            svg.append(f'<text x="46" y="{548+j*38}" class="label">{escape(msg)}</text>')
        svg.append('</svg>')
        (FIGURES / f"flat_band_norm_counterexample_{lang}.svg").write_text('\n'.join(svg), encoding="utf-8")


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    state = initial_state()
    coefficients = np.array([1.0, 0.2, 0.2])
    base = abs(coefficients) / sum(abs(coefficients))
    distributions = [base] + [optimize_toy_distribution(coefficients, 0.4, 4, target) for target in [0, 1]]
    records = []
    for name, probabilities in zip(["vanilla", "toy_Z_optimized", "toy_X_optimized"], distributions):
        moments = exact_qdrift_moments(coefficients, probabilities, 0.4, 4, [Z, X])
        for m in moments:
            m["MSE_M200"] = m["bias"]**2 + m["trajectory_variance"] / 200
        records.append({"name": name, "probabilities": probabilities.tolist(),
                        "observables": dict(zip(["Z", "X"], moments))})
    ns = [2**i for i in range(1, 9)]
    n_sweep = [{"N": n, "methods": product_metrics(0.2, 1.0, n)} for n in ns]
    a_sweep = [{"alpha": float(a), "methods": product_metrics(float(a), 1.0, 64)} for a in np.geomspace(1e-4, 0.5, 60)]
    # Independent exact validations: analytic Pauli exponential and exhaustive trajectories.
    exponential_check = max(float(np.linalg.norm(exp_h(p, 0.317) - (math.cos(0.317)*I - 1j*math.sin(0.317)*p))) for p in PAULIS)
    assert exponential_check < 1e-13
    enumeration_error = max(independently_check_enumeration(coefficients, q, 0.4, 3) for q in distributions)
    flat_errors = []
    for k in np.linspace(-math.pi, math.pi, 37):
        h = math.cos(k)*Z + math.sin(k)*X
        flat_errors.append(max(abs(np.linalg.eigvalsh(h) - [-1, 1])))
    assert max(flat_errors) < 1e-13
    # Verify expected N-orders in the asymptotic portion of the teaching model.
    slopes = {}
    for method in METHODS:
        errors = [r["methods"][method]["operator_spectral_norm_error"] for r in n_sweep[-4:]]
        slope = float(np.polyfit(np.log(ns[-4:]), np.log(errors), 1)[0])
        expected = -1 if method in ["lie", "partial_strang"] else -2
        assert abs(slope - expected) < 0.06, (method, slope)
        slopes[method] = slope
    qtest = distributions[1]
    assert np.linalg.norm(qtest - base) > 0.01
    assert records[1]["observables"]["Z"]["MSE_M200"] < records[0]["observables"]["Z"]["MSE_M200"]
    output = {
        "provenance": {
            "kind": "new exact classical educational calculations; not a research-paper reproduction",
            "units": "dimensionless Hamiltonian and time, hbar=1",
            "Hamiltonian": "H=Z+alpha*X+alpha*Y; three mutually noncommuting Pauli components",
            "initial_state": {"theta": 1.05, "phi": 0.38, "amplitudes_real_imag": [[float(z.real), float(z.imag)] for z in state]},
            "qdrift": "exact average channel and same-choice two-copy channel; independent choices at each step",
            "toy_allocator": "exact-oracle MSE search on simplex with q>=0.2*q_vanilla; not the StateDRIFT fourth-order allocator",
            "exclusions": ["molecular integrals", "QPU data", "measurement shot noise", "state preparation cost", "native-gate compilation", "StateDRIFT implementation"],
        },
        "product_N_sweep": n_sweep,
        "product_alpha_sweep": a_sweep,
        "qdrift_comparison": records,
        "flat_band_counterexample": {"Hamiltonian": "H(k)=A*(cos(k)*Z+sin(k)*X)", "eigenvalues": "[-A,+A] for every k", "bandwidth_each": 0,
                                     "operator_spectral_norm": "abs(A)", "at_k_pi_over_4_component_norms": "abs(A)/sqrt(2) each", "at_k_pi_over_4_commutator_norm": "A**2"},
        "validation": {"analytic_pauli_exponential_max_error": exponential_check,
                       "brute_force_27_trajectories_max_moment_error": enumeration_error,
                       "flat_eigenvalue_max_error": float(max(flat_errors)),
                       "log_error_vs_log_N_slopes": slopes,
                       "checks": "All assertions passed. No independent third-party review is claimed."},
    }
    (RESULTS / "dynamics_comparison.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n', encoding="utf-8")
    make_figures(output)
    print(json.dumps({"validation": output["validation"], "qdrift_comparison": records,
                      "product_N16": n_sweep[3]}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
