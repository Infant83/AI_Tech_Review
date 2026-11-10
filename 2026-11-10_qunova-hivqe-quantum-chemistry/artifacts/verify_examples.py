"""Independent teaching calculations, not a vendor algorithm reproduction."""
from __future__ import annotations

import json
from math import comb, sqrt
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent


def apply_one(state, orbital, create):
    if state[orbital] == int(create):
        return None
    sign = (-1) ** sum(state[:orbital])
    new = list(state)
    new[orbital] = int(create)
    return tuple(new), sign


def hopping(state, p, q):
    first = apply_one(state, q, False)
    if first is None:
        return None
    second = apply_one(first[0], p, True)
    if second is None:
        return None
    return second[0], first[1] * second[1]


def hamiltonian(u=4.0, t=1.0):
    # Order: site-1 up, site-2 up, site-1 down, site-2 down.
    basis = [(1, 0, 1, 0), (1, 0, 0, 1), (0, 1, 1, 0), (0, 1, 0, 1)]
    h = np.zeros((4, 4))
    for j, state in enumerate(basis):
        h[j, j] += u * (state[0] * state[2] + state[1] * state[3])
        for p, q in [(0, 1), (1, 0), (2, 3), (3, 2)]:
            term = hopping(state, p, q)
            if term is not None:
                h[basis.index(term[0]), j] -= t * term[1]
    assert np.allclose(h, h.T)
    return basis, h


def calculate():
    basis, h = hamiltonian()
    energies, vectors = np.linalg.eigh(h)
    analytic = (4 - sqrt(4**2 + 16)) / 2
    assert abs(energies[0] - analytic) < 1e-12
    subsets = [[1, 2], [0, 1, 2], [0, 1, 2, 3]]
    ritz = [float(np.linalg.eigvalsh(h[np.ix_(s, s)])[0]) for s in subsets]
    assert all(a >= b - 1e-12 for a, b in zip(ritz, ritz[1:]))
    assert abs(ritz[0]) < 1e-12
    assert abs(ritz[-1] - analytic) < 1e-12
    psi = np.array([0, 1 / sqrt(2), 1 / sqrt(2), 0])
    projected_variance = 0.0
    full_variance = float(np.vdot(h @ psi, h @ psi) - np.vdot(psi, h @ psi) ** 2)
    assert abs(full_variance - 4) < 1e-12
    for u in [0.0, 1.0, 4.0, 12.0]:
        _, hu = hamiltonian(u)
        assert abs(np.linalg.eigvalsh(hu)[0] - (u - sqrt(u * u + 16)) / 2) < 1e-12
    determinant_count = comb(20, 7) ** 2
    assert determinant_count == 6_009_350_400
    return {
        "kind": "independent explanatory calculation",
        "physical_qpu_execution": False,
        "vendor_algorithm_reproduction": False,
        "hubbard_dimer": {
            "t": 1.0, "U": 4.0, "energy_unit": "t",
            "orbital_order": ["site1_up", "site2_up", "site1_down", "site2_down"],
            "basis": ["".join(map(str, s)) for s in basis],
            "matrix": h.tolist(), "exact_energy": float(energies[0]),
            "ground_state_probabilities": (vectors[:, 0] ** 2).tolist(),
            "subsets": subsets, "ritz_energies": ritz,
            "projected_variance_for_separated_pair": projected_variance,
            "full_variance_for_separated_pair": full_variance,
            "support_invariance": "Once the same determinant set is retained, rediagonalization does not use input sample frequencies.",
        },
        "ibm_reported_n2_row_arithmetic": {
            "source": "https://quantum.cloud.ibm.com/docs/en/guides/qunova-chemistry",
            "accessed": "2026-11-10", "active_electrons": 14, "active_spatial_orbitals": 20,
            "fixed_ms_determinants": determinant_count,
            "selected_determinants": 9_012_004,
            "selected_fraction": 9_012_004 / determinant_count,
            "total_seconds": 46_547, "total_hours": 46_547 / 3600,
            "qpu_seconds": 258, "qpu_minutes": 258 / 60,
            "qpu_fraction_of_reported_total": 258 / 46_547,
            "reported_reference_error_mHa": 1.20,
        },
        "tracker_energy_difference_arithmetic": {
            "fe2s2_hivqe_minus_hci_mHa": (-116.6046821 + 116.605425) * 1000,
            "n2_hivqe_minus_hci_mHa": (-108.9612287 + 108.9614962) * 1000,
            "timing_comparison": "No speedup derived from different classical compute resources.",
        },
        "checks": ["fermionic anticommutation signs", "matrix Hermiticity", "four analytic Hubbard energies", "nested-space variational ordering", "projected versus full variance", "binomial CAS count"],
        "numpy_version": np.__version__,
    }


def figures(data, *, font_path=None, bold_font_path=None, qa_dir=None):
    """Render the same verified values in bilingual desktop/mobile layouts."""
    import os
    import re
    from html import escape
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    font_path = font_path or os.environ.get("REVIEW_FIGURE_FONT")
    if font_path is None:
        try:
            font_path = font_manager.findfont("Noto Sans KR", fallback_to_default=False)
        except ValueError as error:
            raise ValueError("Provide --font with a licensed Korean-capable source font.") from error
    font_path = Path(font_path)
    if not font_path.is_file():
        raise ValueError("Figure source font is missing.")
    font_manager.fontManager.addfont(font_path)
    family = font_manager.FontProperties(fname=font_path).get_name()
    if bold_font_path:
        font_manager.fontManager.addfont(Path(bold_font_path))
    qa_dir = Path(qa_dir) if qa_dir else None
    if qa_dir:
        qa_dir.mkdir(parents=True, exist_ok=True)
    labels = {
        "en": {
            "title_a": "A  Adding configurations\n    lowers the energy",
            "title_b": "B  Different probabilities,\n    the same four configurations",
            "ticks_a": ["2 separated\nconfigurations", "+ 1 doubly occupied\nconfiguration", "All 4\nconfigurations"],
            "ticks_a_mobile": ["2 separated\nconfigurations", "+ 1 doubly\noccupied\nconfiguration", "All 4\nconfigurations"],
            "ylabel_a": "Projected ground-state energy / t", "ylabel_a_mobile": "Energy / t",
            "model_note": "Hubbard dimer: U = 4t\nOne electron of each spin",
            "exact": "Exact energy", "exact_distribution": "Exact-state probabilities",
            "uniform": "Uniform probabilities", "ylabel_b": "Sampling probability",
            "xlabel_b": "Occupation string: (1 up, 2 up,\n1 down, 2 down)",
            "note_b": "All four retained → the same Ritz energy.\nDiscovery costs depend on the distribution.",
            "note_b_mobile": "All four retained:\nthe same Ritz energy.\nDiscovery costs depend on\nthe sampling distribution.",
            "title": "Selected configurations, sampling probabilities, and Hubbard energy",
            "desc": "Independent two-site Hubbard calculation with t=1, U=4, and one electron of each spin. Ritz energies for two, three and four configurations are 0, -0.449489743 and -0.828427125. The exact-state and uniform distributions both have support on all four occupation strings. The order is site1-up, site2-up, site1-down, site2-down."
        },
        "ko": {
            "title_a": "A  배치를 더 포함하면\n    에너지가 낮아진다",
            "title_b": "B  확률은 달라도\n    가능한 네 배치는 같다",
            "ticks_a": ["분리된\n두 배치", "이중 점유\n한 배치 추가", "네 배치\n모두 포함"],
            "ticks_a_mobile": ["분리된\n두 배치", "이중 점유\n한 배치 추가", "네 배치\n모두 포함"],
            "ylabel_a": "부분공간의 바닥상태 에너지 / t", "ylabel_a_mobile": "에너지 / t",
            "model_note": "두 자리 Hubbard 모형, U = 4t\n스핀별 전자 한 개",
            "exact": "정확한 에너지", "exact_distribution": "정확한 바닥상태 확률",
            "uniform": "균등 분포 확률", "ylabel_b": "표본 추출 확률",
            "xlabel_b": "점유 비트열의 순서:\n(1↑, 2↑, 1↓, 2↓)",
            "note_b": "네 배치를 모두 확보하면 같은 Ritz 에너지\n필요한 표본 수는 분포에 따라 달라진다.",
            "note_b_mobile": "네 배치를 모두 확보하면\n같은 Ritz 에너지\n표본 확보 비용은\n분포에 따라 달라진다.",
            "title": "선택한 전자배치·표본 확률과 Hubbard 에너지",
            "desc": "t=1, U=4, 스핀별 전자가 한 개인 두 자리 Hubbard 독립 계산. 두 배치·세 배치·네 배치의 Ritz 에너지는 0, -0.449489743, -0.828427125이다. 정확한 바닥상태 분포와 균등 분포는 모두 네 점유 비트열을 지지한다. 비트 순서는 1번 자리 위스핀, 2번 자리 위스핀, 1번 자리 아래스핀, 2번 자리 아래스핀이다."
        },
    }
    plt.rcParams.update({"font.family": [family], "font.size": 16,
                         "axes.unicode_minus": False, "svg.fonttype": "none",
                         "svg.hashsalt": "qunova-hubbard-figures-v1",
                         "figure.facecolor": "#fcfaf5", "axes.facecolor": "#fcfaf5",
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.labelcolor": "#243d45", "text.color": "#243d45",
                         "xtick.color": "#243d45", "ytick.color": "#243d45"})
    h = data["hubbard_dimer"]
    for language in ["ko", "en"]:
        l = labels[language]
        for mobile in [False, True]:
            if mobile:
                fig, axes = plt.subplots(2, 1, figsize=(5.2, 12.2), layout="constrained")
                title_size, tick_size, note_size = 18, 14, 14
            else:
                fig, axes = plt.subplots(1, 2, figsize=(13.6, 6.6), layout="constrained")
                title_size, tick_size, note_size = 18, 15, 14
            a, b = axes
            colors = ["#b7c9cd", "#d4ac77", "#649b87"]
            a.bar([0, 1, 2], h["ritz_energies"], color=colors, width=.6)
            a.axhline(h["exact_energy"], color="#44675c", linestyle="--", linewidth=1.2)
            a.set_xticks([0, 1, 2], l['ticks_a_mobile' if mobile else 'ticks_a'], fontsize=tick_size)
            a.set_ylim(-1.16, .18)
            a.set_ylabel(l['ylabel_a_mobile' if mobile else 'ylabel_a'], fontsize=16)
            a.set_title(l['title_a'], loc='left', fontsize=title_size, fontweight='bold', pad=19)
            a.tick_params(axis='y', labelsize=14)
            for i, value in enumerate(h['ritz_energies']):
                a.text(i, value - .06, f'{value:.6f}', ha='center', va='top', fontsize=15)
            a.text(.02, .04, l['model_note'], transform=a.transAxes, fontsize=note_size, va='bottom')
            a.text(.02, h['exact_energy']+.035, l['exact'], fontsize=note_size, va='bottom', color='#44675c')
            x = np.arange(4)
            b.bar(x - .19, h['ground_state_probabilities'], width=.36, color='#649b87', label=l['exact_distribution'])
            b.bar(x + .19, [0.25] * 4, width=.36, color='#d4ac77', label=l['uniform'])
            b.set_xticks(x, h['basis'], fontsize=15)
            b.set_xlabel(l['xlabel_b'], fontsize=14, labelpad=10)
            b.set_ylabel(l['ylabel_b'], fontsize=16)
            b.set_ylim(0, .85)
            b.set_title(l['title_b'], loc='left', fontsize=title_size, fontweight='bold', pad=19)
            b.tick_params(axis='y', labelsize=14)
            b.legend(frameon=False, fontsize=14, loc='upper center')
            b.text(.02, .76, l['note_b_mobile' if mobile else 'note_b'], transform=b.transAxes,
                   fontsize=note_size, va='top', linespacing=1.4)
            filename = f'support_and_energy{"_mobile" if mobile else ""}_{language}'
            svg_path = ROOT / f'{filename}.svg'
            fig.savefig(svg_path, metadata={'Date': None, 'Title': l['title'], 'Description': l['desc']})
            if qa_dir:
                fig.savefig(qa_dir / f'{filename}.png', dpi=160)
            plt.close(fig)
            svg = svg_path.read_text(encoding='utf-8')
            svg = re.sub(r'font-family:[^;\"]+', 'font-family: ReviewFigure,ReviewFigureSymbols,ReviewFigureMath,\'Noto Sans KR\',sans-serif', svg)
            title_id, desc_id = f'{filename}-title', f'{filename}-desc'
            def annotate(match):
                tag = match[0][:-1] + f' role="img" aria-labelledby="{title_id} {desc_id}" xml:lang="{language}">'
                return tag + f'\n <title id="{title_id}">{escape(l["title"])}</title>\n <desc id="{desc_id}">{escape(l["desc"])}</desc>'
            svg = re.sub(r'<svg\b[^>]*>', annotate, svg, count=1)
            svg_path.write_text(svg, encoding='utf-8')
            print(svg_path.name)
    data['matplotlib_version'] = matplotlib.__version__


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--font', type=Path, help='Licensed full Korean-capable font for figure labels')
    parser.add_argument('--bold-font', type=Path, help='Matching licensed bold source font')
    parser.add_argument('--qa-dir', type=Path, help='Optional private PNG render destination')
    args = parser.parse_args()
    data = calculate()
    figures(data, font_path=args.font, bold_font_path=args.bold_font, qa_dir=args.qa_dir)
    (ROOT / "example-results.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"checks": "passed", "energy": data["hubbard_dimer"]["exact_energy"],
                      "ritz_energies": data["hubbard_dimer"]["ritz_energies"]}))
