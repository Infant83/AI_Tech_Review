"""Independent two-band teaching calculation, not a ReAg2Cl6 reproduction.

Lower-band links use <u(k)|u(k+dk)> with a positively oriented kx,ky
plaquette. C is the sum of principal link-product phases divided by 2pi.
Spectral flattening keeps eigenvectors and generally introduces long-range
hopping; this is an algebraic counterexample, not a local material proposal.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def model(n: int, mass: float = -1.0, flatten: bool = True, scale: float = 1.0):
    k = np.linspace(-np.pi, np.pi, n, endpoint=False)
    kx, ky = np.meshgrid(k, k, indexing="ij")
    d = np.stack((np.sin(kx), np.sin(ky), mass + np.cos(kx) + np.cos(ky)), axis=-1)
    if flatten:
        d /= np.linalg.norm(d, axis=-1, keepdims=True)
    h = np.empty((n, n, 2, 2), dtype=complex)
    h[..., 0, 0], h[..., 1, 1] = d[..., 2], -d[..., 2]
    h[..., 0, 1] = d[..., 0] - 1j * d[..., 1]
    h[..., 1, 0] = d[..., 0] + 1j * d[..., 1]
    return np.linalg.eigh(scale * h)


def chern(u):
    links = []
    minimum = 1.0
    for axis in (0, 1):
        overlap = np.sum(u.conj() * np.roll(u, -1, axis=axis), axis=-1)
        minimum = min(minimum, float(np.abs(overlap).min()))
        if minimum < 1e-8:
            raise ValueError("Singular neighboring-band overlap")
        links.append(overlap / np.abs(overlap))
    ux, uy = links
    flux = np.angle(ux * np.roll(uy, -1, axis=0)
                    * np.conj(np.roll(ux, -1, axis=1)) * np.conj(uy))
    return float(flux.sum() / (2 * np.pi)), flux, minimum


def color(value, maximum):
    t = min(abs(value) / maximum, 1.0)
    a, b = ((247, 246, 239), (14, 111, 113)) if value >= 0 else ((247, 246, 239), (181, 73, 56))
    return "#" + "".join(f"{round(x + t*(y-x)):02x}" for x, y in zip(a, b))


def figure(flux, c):
    n = len(flux)
    # Flux / plaquette area estimates curvature. Colors use a symmetric range.
    omega = flux / (2 * np.pi / n) ** 2
    maximum = float(np.max(np.abs(omega)))
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620">',
           '<rect width="1200" height="620" fill="#f6f4ed"/>',
           '<g font-family="Arial, sans-serif" fill="#173c4c">',
           '<text x="45" y="40" font-size="24" font-weight="700">Identical flat energies do not determine band topology</text>',
           '<text x="45" y="69" font-size="15">Independent two-band teaching models; not ReAg2Cl6 data or a fractional-state calculation</text>',
           '<text x="55" y="116" font-size="18" font-weight="700">A  Energy eigenvalues</text>',
           '<text x="640" y="116" font-size="18" font-weight="700">B  Lower-band Berry curvature</text>']
    for y, label in ((210, "+1"), (420, "-1")):
        out += [f'<line x1="105" y1="{y}" x2="545" y2="{y}" stroke="#007e8c" stroke-width="5"/>',
                f'<text x="67" y="{y+6}" font-size="17">{label}</text>']
    out += ['<path d="M105 155V460H565" fill="none" stroke="#536b75" stroke-width="1.4"/>',
            '<text x="245" y="493" font-size="17">k along any path</text>',
            '<text x="28" y="330" font-size="17" transform="rotate(-90 28 330)">Energy (model units)</text>',
            '<text x="115" y="170" font-size="16">H = sigma_z : C = 0</text>',
            f'<text x="115" y="187" font-size="16">H = d_hat(k) . sigma : C = {c:.0f}</text>']
    x0, y0, side = 675, 150, 310
    for i in range(n):
        for j in range(n):
            out.append(f'<rect x="{x0+i*side/n:.3f}" y="{y0+(n-1-j)*side/n:.3f}" width="{side/n+0.05:.3f}" height="{side/n+0.05:.3f}" fill="{color(omega[i,j],maximum)}"/>')
    out += [f'<rect x="{x0}" y="{y0}" width="{side}" height="{side}" fill="none" stroke="#536b75"/>',
            '<text x="664" y="485" font-size="14">-pi</text><text x="974" y="485" font-size="14">pi</text>',
            '<text x="820" y="506" font-size="17">kx</text><text x="644" y="310" font-size="17">ky</text>',
            '<text x="640" y="159" font-size="14">pi</text><text x="633" y="460" font-size="14">-pi</text>',
            '<text x="1010" y="175" font-size="15">Curvature</text>']
    for j in range(120):
        value = maximum * (1 - 2 * j / 119)
        out.append(f'<rect x="1020" y="{190+j*1.7:.2f}" width="22" height="1.8" fill="{color(value,maximum)}"/>')
    out += [f'<text x="1053" y="204" font-size="14">+{maximum:.2f}</text>',
            '<text x="1053" y="300" font-size="14">0</text>',
            f'<text x="1053" y="394" font-size="14">-{maximum:.2f}</text>',
            '<text x="45" y="551" font-size="16">Both models: lower-band width W = 0, interband gap = 2 (up to floating-point error).</text>',
            '<text x="45" y="578" font-size="15">Rescaling H by 20 leaves W = 0 and C unchanged, while ||H|| increases from 1 to 20.</text>',
            '<text x="45" y="603" font-size="13">Spectral flattening preserves eigenvectors and generally requires long-range hopping. C uses oriented link phases.</text>',
            '</g></svg>']
    return "\n".join(out)


def main():
    results = []
    for n in (31, 61, 121):
        e, v = model(n)
        c, flux, overlap = chern(v[..., :, 0])
        e_raw, v_raw = model(n, flatten=False)
        raw_c = chern(v_raw[..., :, 0])[0]
        trivial = np.zeros_like(v[..., :, 0]); trivial[..., 1] = 1
        trivial_c = chern(trivial)[0]
        rng = np.random.default_rng(20261026)
        gauge = v[..., :, 0] * np.exp(1j*rng.uniform(-np.pi, np.pi, (n, n)))[..., None]
        gauge_c, gauge_flux, _ = chern(gauge)
        reverse_c = chern(v[..., :, 0].conj())[0]
        assert abs(abs(c)-1) < 1e-10 and abs(c-raw_c) < 1e-10
        assert abs(trivial_c) < 1e-10 and abs(c+reverse_c) < 1e-10
        assert np.max(np.abs(gauge_flux-flux)) < 1e-12 and abs(c-gauge_c) < 1e-10
        assert np.ptp(e[..., 0]) < 1e-12 and np.max(np.abs(e[..., 0]+1)) < 1e-12
        results.append({"mesh": n, "mass": -1, "lower_chern": c,
                        "unflattened_lower_chern": raw_c, "conjugated_chern": reverse_c,
                        "trivial_lower_chern": trivial_c,
                        "lower_bandwidth": float(np.ptp(e[..., 0])),
                        "minimum_gap": float(np.min(e[..., 1]-e[..., 0])),
                        "minimum_neighbor_overlap": overlap,
                        "random_gauge_max_flux_change": float(np.max(np.abs(gauge_flux-flux)))})
    (ROOT/"artifacts/results").mkdir(parents=True, exist_ok=True)
    (ROOT/"figures").mkdir(exist_ok=True)
    (ROOT/"artifacts/results/flatband-toy.json").write_text(json.dumps({
        "scope": "Independent exact two-band educational calculation; not material DFT, ED, FCI or QPU reproduction",
        "convention": "C=sum(arg(Ux(k) Uy(k+x) conj(Ux(k+y)) conj(Uy(k))))/(2*pi), lower band",
        "models": "trivial sigma_z and spectrally flattened QWZ d=(sin kx,sin ky,-1+cos kx+cos ky)",
        "meshes": results, "scale_counterexample": {"scales": [1,20], "operator_norms": [1,20], "bandwidths": [0,0]}}, indent=2)+"\n")
    _, v = model(41)
    c, flux, _ = chern(v[..., :, 0])
    (ROOT/"figures/flatness-and-topology.svg").write_text(figure(flux,c))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
