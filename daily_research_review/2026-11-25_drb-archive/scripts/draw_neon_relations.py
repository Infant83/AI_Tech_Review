#!/usr/bin/env python3
"""Original relationship diagram using reported facts; run only in an authorized render slot."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--font", type=Path, required=True)
    ap.add_argument("--font-heading", type=Path)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    regular = str(args.font)
    heading = str(args.font_heading or args.font)
    fonts = {
        "title": ImageFont.truetype(heading, 48),
        "head": ImageFont.truetype(heading, 39),
        "value": ImageFont.truetype(heading, 49),
        "body": ImageFont.truetype(regular, 34),
        "small": ImageFont.truetype(regular, 32),
    }
    im = Image.new("RGB", (1800, 1150), "#ffffff")
    d = ImageDraw.Draw(im)
    ink, navy, teal = "#263640", "#17364b", "#247b83"
    muted, line, pale = "#62737c", "#cfdae0", "#e9f2f6"

    def text(x, y, value, style="body", fill=ink, gap=10):
        font = fonts[style]
        for row in value.split("\n"):
            d.text((x, y), row, font=font, fill=fill)
            y += font.size + gap
        return y

    def arrow(x1, y, x2):
        d.line((x1, y, x2, y), fill=teal, width=5)
        d.polygon([(x2, y), (x2-14, y-9), (x2-14, y+9)], fill=teal)

    text(70, 42, "Neon confinement becomes part of the control interface", "title", navy)
    labels = [
        "Neon surface\nconfinement",
        "Different dipole\norientations",
        "Unequal coupling\nto the resonator",
        "Shared drive\nand pulsed readout",
    ]
    for i, label in enumerate(labels):
        x = 70 + i * 440
        d.rounded_rectangle((x, 145, x+340, 285), radius=18, fill=pale, outline=line, width=2)
        text(x+18, 169, label, "small", navy)
        if i < 3:
            arrow(x+350, 215, x+424)
    text(70, 310, "Explanatory relationships, not measured surface topography or a spatial layout.", "small", muted)

    cards = [
        (70, "TWO QUBITS | TiN", "Time-domain CR / bSWAP operations",
         "J / (2 pi)", "3.35(9) MHz", "0.6(1) MHz",
         "Bright qubit mediates drive and readout.\nMeasured resonator signal: normalized I."),
        (950, "THREE QUBITS | Nb", "Separate device and cooldown",
         "J12 / (2 pi)", "62.5(5) MHz", "3.5(7) MHz",
         "Spectroscopy of the three-qubit system.\nThis is not the CR / bSWAP device."),
    ]
    for x, title, subtitle, coupling_label, coupling, linewidth, meaning in cards:
        d.rounded_rectangle((x, 395, x+780, 920), radius=20, outline=line, width=3, fill="#f9fbfc")
        text(x+28, 421, title, "head", navy)
        text(x+28, 478, subtitle, "small", teal)
        text(x+28, 548, "Coupling: " + coupling_label, "body", muted)
        text(x+28, 595, coupling, "value", navy)
        text(x+28, 676, "Hybrid linewidth", "body", muted)
        text(x+28, 722, linewidth, "value", navy)
        text(x+28, 815, meaning, "small", ink)

    text(70, 950, "Quoted coupling is J / (2 pi), not the full spectral peak separation.", "small", ink)
    text(70, 998, "Parentheses retain the final captions' uncertainty notation; no uncertainty type is inferred.", "small", muted)
    text(70, 1046, "Original review diagram | Facts: final Figs.2,4; relationships: arXiv2503.23738v5 Methods.", "small", muted)
    text(70, 1091, "Source research: X. Li et al., Nature Physics (2026), DOI10.1038/s41567-026-03529-4.", "small", muted)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / "neon-relations.png"
    im.save(output)
    facts = {
        "image": output.name,
        "image_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "kind": "original_review_relation_diagram_and_reported_factual_numbers",
        "pixel_size": [1800, 1150],
        "original_source_panels_or_curves_reused": False,
        "reported_values": [
            {"condition": "two-qubit TiN device", "coupling": "J/(2pi)=3.35(9)MHz",
             "hybrid_linewidth": "0.6(1)MHz", "source": "final Fig.2b caption"},
            {"condition": "separate three-qubit Nb device/cooldown", "coupling": "J12/(2pi)=62.5(5)MHz",
             "hybrid_linewidth": "3.5(7)MHz", "source": "final Fig.4b caption"},
        ],
        "source_urls": [
            "https://www.nature.com/articles/s41567-026-03529-4/figures/2",
            "https://www.nature.com/articles/s41567-026-03529-4/figures/4",
            "https://arxiv.org/abs/2503.23738v5",
        ],
        "scope": "No data fitting, simulation, source-panel adaptation or experimental reproduction.",
    }
    (args.output_dir / "neon-relations.json").write_text(json.dumps(facts, indent=2) + "\n")


if __name__ == "__main__":
    main()
