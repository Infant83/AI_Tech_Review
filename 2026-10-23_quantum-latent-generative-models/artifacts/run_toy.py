"""Limited CPU experiment using pinned, inspected upstream WGAN-GP code.

This is NOT an independent reproduction of the paper's three-loop Figure 1,
QM9 experiment, QPU data collection or protein generation. The public notebook
uses an efficiently classically simulated SINGLE-loop interferometer. We add a
distinguishable-photon control for that same single loop; no third-party source
is bundled. Reviewed Apache-2.0 upstream files are fetched into ignored tmp/ and
checked against SHA-256 before import. The generated results are review data.

Upstream notebook interface/settings: Copyright 2026 ORCA Computing,
Apache License 2.0; see upstream_APACHE_2_0.txt. Review modifications add
CPU/seed controls, diagnostics, checked fetching and a distinguishable control.

Dependencies used: Python 3.12, torch 2.2.2, numpy 1.26.4, numba 0.61.2,
matplotlib 3.10.8. Run: python artifacts/run_toy.py --steps 5000
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math
import platform
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "b950127d3584561fee4aea4af566bcce697d6946"
REPOSITORY = "https://github.com/orcacomputing/quantum-latent-distributions"
HASHES = {
    "src/gan.py": "734e46baf9580b817c9499fe468b98370ad2db34a10dc103178fa9a1d63e33a7",
    "src/gaussians_utils.py": "71b1968cf312674ecc4f40663512e15865bf09610db2d1b4ccdcfc3d23791939",
    "src/tbi_sampler.py": "5dd0893a35229d97a12a7bc50634d7ba581b3e56feb3d1bb5f35b218d6304514",
    "src/utils.py": "29af5c596abe2faa47b3a525481531989f81251248e5e5cbafb986143df47295",
}


def prepare_sources():
    upstream = ROOT / "tmp" / "upstream"
    for name, expected in HASHES.items():
        target = upstream / name
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            url = f"https://raw.githubusercontent.com/orcacomputing/quantum-latent-distributions/{COMMIT}/{name}"
            target.write_bytes(urllib.request.urlopen(url).read())
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Unexpected upstream content: {name}")
    sys.path.insert(0, str(upstream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20261023)
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()
    prepare_sources()
    import numpy as np
    import numba
    import torch
    from torch.utils.data import DataLoader
    from src.gan import WGANGP
    from src.gaussians_utils import SevenGaussians, Generator, Critic
    from src.tbi_sampler import TBISampler, _calculate_probs_after_bs

    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    # Force CPU even when an accelerated backend is available.
    torch.cuda.is_available = lambda: False
    torch.backends.mps.is_available = lambda: False

    @numba.njit
    def seed_numba(seed):
        np.random.seed(seed)

    class GaussianLatent:
        def generate(self, n):
            return torch.randn(n, 16)

    theta = np.random.default_rng(args.seed + 1).uniform(0, np.pi / 2, 16)
    input_state = [1, 0] * 8

    class PhotonicLatent:
        def __init__(self, interference):
            self.interference = interference
            self.tbi = TBISampler()
            self.rng = np.random.default_rng(args.seed + 2)

        def generate(self, n):
            if self.interference:
                counts = self.tbi.sample(input_state, list(theta), n)
                samples = []
                for state, count in counts.items():
                    samples.extend([state] * count)
                samples = np.asarray(samples)
                self.rng.shuffle(samples)
            else:
                # Each labelled photon routes independently at the same beam
                # splitter. No coherent sum of multiphoton amplitudes occurs.
                loop = np.zeros(n, dtype=np.int64)
                samples = np.zeros((n, 17), dtype=np.int64)
                for i, (incoming, angle) in enumerate(zip(input_state, theta)):
                    emitted = self.rng.binomial(loop, np.cos(angle) ** 2)
                    emitted += self.rng.binomial(incoming, np.sin(angle) ** 2, n)
                    samples[:, i] = emitted
                    loop += incoming - emitted
                samples[:, 16] = loop
            if not np.all(samples.sum(axis=1) == 8):
                raise AssertionError("Photon number is not conserved")
            return torch.tensor(samples[:, :16], dtype=torch.float32) - 0.5

    # Unit checks at a balanced beam splitter: Hong-Ou-Mandel suppression of
    # one photon in each output, vs probability 1/2 for labelled photons.
    choices, probs = _calculate_probs_after_bs(1, 1, math.pi / 4)
    middle = probs[np.where(choices == 1)[0][0]]
    assert abs(middle) < 1e-12
    for n in range(9):
        for m in [0, 1]:
            for angle in [0.0, 0.1, math.pi / 4, 1.2, math.pi / 2]:
                _, p = _calculate_probs_after_bs(n, m, angle)
                assert np.min(p) >= 0 and abs(sum(p) - 1) < 1e-10

    dataset = SevenGaussians(n_per_blob=1500, n_blobs=7, radius=5.0,
                            radial_std=0.2, tangential_std=0.05)
    centers = dataset.centers_xy.numpy()
    evaluation_n = 10000
    # Review-defined, fixed geometric diagnostics; not metrics in the paper.
    radius_threshold = 0.75
    result = {
        "kind": "limited CPU run of public single-loop toy code, with review-added distinguishable control",
        "not_reproduced": ["paper Figure 1 three-loop 1-3-9 circuit", "QM9", "physical QPU", "protein generation"],
        "upstream_repository": REPOSITORY, "upstream_commit": COMMIT,
        "upstream_license": "Apache-2.0", "upstream_sha256": HASHES,
        "seed": args.seed, "circuit_seed": args.seed + 1,
        "sampler_seed": args.seed + 2, "device": "cpu", "threads": args.threads,
        "python": platform.python_version(), "torch": torch.__version__,
        "numpy": np.__version__, "numba": numba.__version__,
        "steps_per_latent": args.steps, "critic_steps_per_generator": 5,
        "batch_size": 32, "learning_rate": 0.0005, "gradient_penalty": 10,
        "generator": "16 -> 256 -> 256 -> 2; LeakyReLU(0.2)",
        "critic": "2 -> 256 -> 256 -> 1; LeakyReLU(0.2)",
        "opt": "Adam betas=(0,0.9)", "circuit": "lossless single-loop, 8 input photons / 16 time bins; last loop occupancy discarded",
        "theta_radians": theta.tolist(), "input_state": input_state,
        "latent_preprocessing": "photonic occupancy minus 0.5, exactly as public notebook; Gaussian unchanged",
        "dataset": {"n": len(dataset), "n_blobs": 7, "radius": 5, "radial_std": 0.2, "angular_std_radians": 0.05,
                    "generator": "upstream SevenGaussians internal default torch.Generator()"},
        "evaluation": {"n": evaluation_n, "within_mode_radius": radius_threshold,
                       "within_mode_definition": "distance to closest ideal center <= 0.75",
                       "mode_coverage_definition": "number of centers with at least 1% of all generated points within radius 0.75",
                       "warning": "Review-defined diagnostics on one seed, not paper metrics or significance test"},
        "checks": {"balanced_HOM_coincidence_probability": float(middle), "balanced_distinguishable_coincidence_probability": 0.5,
                   "beam_splitter_probability_normalization": "passed n=0..8,m=0,1,5 angles", "sample_photon_conservation": "checked every sample"},
        "runs": [],
    }
    art = ROOT / "artifacts"
    art.mkdir(exist_ok=True)
    points = {"target": dataset.data.numpy()}
    for label in ["gaussian", "distinguishable", "quantum_simulated"]:
        torch.manual_seed(args.seed)
        np.random.seed(args.seed + 2)
        seed_numba(args.seed + 2)
        loader_generator = torch.Generator().manual_seed(args.seed + 3)
        loader = DataLoader(dataset, batch_size=32, shuffle=True, num_workers=0,
                            pin_memory=False, drop_last=True, generator=loader_generator)
        latent = GaussianLatent() if label == "gaussian" else PhotonicLatent(label == "quantum_simulated")
        generator, critic = Generator(z_dim=16), Critic()
        gan = WGANGP(latent, generator, critic)
        start = time.perf_counter()
        print(f"RUN {label} steps={args.steps} device={gan.device}", flush=True)
        gan.train(loader, n_iter=args.steps, print_frequency=500, verbose=True)
        elapsed = time.perf_counter() - start
        # Separate fixed evaluation random seed, independent of training count.
        torch.manual_seed(args.seed + 4)
        np.random.seed(args.seed + 4)
        seed_numba(args.seed + 4)
        if hasattr(latent, "rng"):
            latent.rng = np.random.default_rng(args.seed + 4)
        with torch.no_grad():
            xy = generator(latent.generate(evaluation_n)).numpy()
        points[label] = xy
        distances = np.sqrt(((xy[:, None] - centers[None]) ** 2).sum(axis=2))
        nearest = distances.argmin(axis=1)
        near = distances.min(axis=1) <= radius_threshold
        counts = np.bincount(nearest[near], minlength=7)
        entry = {"latent": label, "training_seconds": elapsed,
                 "within_mode_fraction": float(near.mean()),
                 "outside_mode_fraction": float(1 - near.mean()),
                 "mode_counts": counts.tolist(),
                 "mode_coverage": int((counts >= evaluation_n * .01).sum()),
                 "mean_nearest_center_distance": float(distances.min(axis=1).mean())}
        result["runs"].append(entry)
        print(json.dumps(entry), flush=True)
        (art / "toy_results.json").write_text(json.dumps(result, indent=2) + "\n")
        np.savez_compressed(art / "toy_points.npz", **points)
    with (art / "toy_results.csv").open("w", newline="") as f:
        fields = ["latent", "training_seconds", "within_mode_fraction", "outside_mode_fraction", "mode_coverage", "mean_nearest_center_distance"]
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for entry in result["runs"]:
            writer.writerow({k: entry[k] for k in fields})
    print("COMPLETE", flush=True)


if __name__ == "__main__":
    main()
