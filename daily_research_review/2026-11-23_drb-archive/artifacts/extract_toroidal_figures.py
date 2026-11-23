#!/usr/bin/env python3
"""Extract attributed figures from the CC BY 4.0 author preprint.

Requires pypdf and Poppler pdftoppm. Provide the publicly downloadable source PDF
with --source; the source PDF itself is not part of this publication package.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from pypdf import PdfReader, PdfWriter

SOURCE_SHA256 = "606ad775eb43f2cfc6a858f7a8b00c359ae903442c8adb817fae49b232f04a41"
SOURCE_URL = "https://arxiv.org/pdf/2504.08701v2"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
FIGURES = [
    {"asset": "toroidal-v2-fig2.png", "figure": "Fig. 2(a–c)", "page": 3,
     "crop_box_points": [310, 591, 566, 743], "dpi": 300,
     "original_selected_caption": "Selective preparation of a ferrotoroidic state with pulsed microwave radiation. a Schematic of the AlDy6 geometry where the Dy atoms are shown as blue spheres connected by blue pseudo-bonds. h is the height of the molecule and the circumscribed radius of each SMT motif is r. Al is depicted as a grey sphere. In general, the lanthanide ions interact with the central transition metal ion via an exchange coupling J1 and with nearest-neighbours in each SMT motif via J2. The principal magnetic axes of the Dy ions are shown as orange arrows which are canted weakly out of the SMT triangular planes by the angles eta_t and eta_b for the top and bottom triangles, respectively. b Time evolution of the AlDy6 molecular wavefunction obtained from numerical integration of the time-dependent Schrodinger equation. The system is prepared in the AFT state |-tau,+tau> (blue curve) by the application of a static almost longitudinal field B=|B_parallel|(0.1,0,1) (shown as a red translucent arrow in a) with |B_parallel|=1 T. Three pulses of microwave radiation are applied to the system in pulses t_p=hbar*pi/(g_x*mu_B*|B_perp|) separated by the arbitrary wait times t_w=t_p (grey dashed lines delineate the start and end of each pulse). After the completion of the three-pulse protocol, the FT state is prepared with 100% population (red curve). c The time evolution of the molecular toroidal moment projected along the symmetry axis of the molecule <tau_z>=<psi(t)|tau_z|psi(t)>.",
     "reading": "Panel b: time t(ns) versus state populations |c_m|^2. Panel c: time t(ns) versus <tau_z>/(g_z mu_B r), maximum 6. Gray dashed boundaries indicate sequential pulses and arbitrary waits. The 100% result is a modeled target population, not measured gate fidelity.",
     "conditions": "Author-v2 main p3: eta_t-eta_b=1 degree; B=(0.1,0,1) T; sequential frequencies 115, 43, 101 GHz. Geometry panel uses pseudo-bonds; Al is diamagnetic in this low-temperature model."},
    {"asset": "toroidal-v2-fig3cd.png", "figure": "Fig. 3(c,d)", "page": 4,
     "crop_box_points": [177.5, 265, 300, 411], "dpi": 360,
     "original_selected_caption": "Fidelity of the ferrotoroidic preparation protocol. c Final squared amplitudes of the AlDy6 wavefunction on completion of the three pulse protocol as a function of the differential canting angle of Dy3+ principal magnetic axes in the upper and lower SMT moieties. d Final expectation value of the AlDy6 molecular toroidal moment as a function of the differential canting angle of Dy3+ principal magnetic axes in the upper and lower SMT moieties.",
     "reading": "Native shared horizontal axis is eta_t-eta_b (degrees), range -1 to1, not delta_theta. Panel c retains two state-population curves and their spin-configuration pictograms. Panel d retains <tau_z>/(g_z mu_B r), range0 to6. Exact inversion symmetry at zero difference suppresses net toroidal polarization; no precise nonzero threshold is inferred from the plotted curve.",
     "conditions": "Author-v2 p4 discusses final populations and toroidal moment after the same sequential protocol while varying differential canting. It defines the difference eta_t-eta_b; a half-angle delta_theta=0.5 degree is not explicitly defined in this source and is not substituted."},
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--pdftoppm", default=shutil.which("pdftoppm") or "pdftoppm")
    args = parser.parse_args()
    if digest(args.source) != SOURCE_SHA256:
        parser.error("Source differs from the reviewed arXiv v2 PDF; review the edition before extraction.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(args.source)
    manifest = {
        "source_url": SOURCE_URL,
        "source_abs_url": "https://arxiv.org/abs/2504.08701v2",
        "source_sha256": SOURCE_SHA256,
        "source_version": "arXiv:2504.08701v2, submitted 8 Sep 2025; PDF title page dated 9 Sep 2025",
        "source_title": "Preparation and coherent manipulation of toroidal moments in molecules",
        "authors": ["Kieran Hymas", "Alessandro Soncini"],
        "journal_reference": "K. Hymas and A. Soncini, Preparation and coherent control of toroidal moments in molecules, Phys. Rev. B 114, 274426 (2026).",
        "journal_doi": "10.1103/hvgx-whqs",
        "journal_online_date": "2026-11-18",
        "license": "CC BY 4.0",
        "license_url": LICENSE_URL,
        "rights_evidence": "The actual arXiv v2 abstract page Rights to this article link points to CC BY 4.0; its HTML view also labels CC BY 4.0. These are author-preprint figures, not a claimed copy of the differently licensed final APS edition.",
        "operation": "Rectangular excerpts from the specified PDF pages, rasterized with Poppler; no alteration of original scientific labels, axes, colors, curves or pictogram legends. Long source captions are stored below as selected text with formula glyphs linearized.",
        "attribution": "K. Hymas and A. Soncini, arXiv:2504.08701v2 (2025), CC BY 4.0; figures excerpted and rasterized for this research brief.",
        "context": {"citation": "M. Stephens, Controlling single-molecule toroics, Physics 19, s146 (2026).", "date": "2026-11-18", "doi": "10.1103/Physics.19.s146", "url": "https://physics.aps.org/articles/v19/s146"},
        "execution_level": "Effective-Hamiltonian theory and classical numerical integration; state preparation protocol proposal, not a new QPU or measured gate result.",
        "figures": [],
    }
    with tempfile.TemporaryDirectory(prefix="toroidal-figure-") as temp:
        for item in FIGURES:
            page = reader.pages[item["page"] - 1]
            x0, y0, x1, y1 = item["crop_box_points"]
            page.cropbox.lower_left = (x0, y0)
            page.cropbox.upper_right = (x1, y1)
            writer = PdfWriter()
            writer.add_page(page)
            crop = Path(temp) / (item["asset"] + ".pdf")
            with crop.open("wb") as handle:
                writer.write(handle)
            output = args.output_dir / item["asset"]
            subprocess.run([args.pdftoppm, "-cropbox", "-r", str(item["dpi"]), "-png", "-singlefile", str(crop), str(output.with_suffix(""))], check=True)
            manifest["figures"].append({**item, "sha256": digest(output), "bytes": output.stat().st_size})
    (args.output_dir / "toroidal-figure-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
