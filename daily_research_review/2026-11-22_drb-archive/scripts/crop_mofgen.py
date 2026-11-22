#!/usr/bin/env python3
"""Crop the original MOFGen Fig. 4 to the AI-MOF-3 and AI-MOF-4 columns."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Original publisher Fig. 4 PNG")
    parser.add_argument("--output", type=Path, default=base / "artifacts/mofgen-fig4-ai3-ai4.png")
    parser.add_argument("--metadata", type=Path, default=base / "artifacts/mofgen-fig4-ai3-ai4-metadata.json")
    parser.add_argument("--box", type=int, nargs=4, metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
    args = parser.parse_args()
    original = Image.open(args.source)
    if args.box is None:
        if original.size != (2163, 1197):
            parser.error("Default crop requires the 2163 x 1197 source; supply --box for another edition")
        box = (1080, 240, 2163, 1197)
    else:
        box = tuple(args.box)
    if not (0 <= box[0] < box[2] <= original.width and 0 <= box[1] < box[3] <= original.height):
        parser.error("Crop box is outside the source image")
    crop = original.crop(box)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    crop.save(args.output)
    metadata = {
        "doi": "10.1038/s43588-026-01058-x",
        "citation": "T. Jaffrelot Inizan et al., System of agentic AI for the discovery of metal–organic frameworks, Nat. Comput. Sci. 6, 1223–1234 (2026).",
        "source_url": "https://www.nature.com/articles/s43588-026-01058-x/figures/4",
        "source_figure": "Final published Figure 4",
        "publication_date": "2026-11-20",
        "source_filename": args.source.name,
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "source_dimensions_px": list(original.size),
        "crop_box_ltrb_px": list(box),
        "output_filename": args.output.name,
        "output_dimensions_px": list(crop.size),
        "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
        "license": "Creative Commons Attribution 4.0 International",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "copyright": "© The Author(s) 2026",
        "changes": "Rectangular crop: first two columns (AI-MOF-1/2) and upper organic-linker drawings/names excluded; AI-MOF-3/4 framework drawings and AI identifiers, experimental/simulated PXRD, axes, units and legends retained. No resampling, redrawing, data transformation or added labels.",
        "scientific_note": "AI-MOF-3 and AI-MOF-4 use the same linker type under different full synthesis conditions; the paper does not isolate solvent as the only changed variable. Red curves are experimental PXRD and grey curves simulated patterns.",
        "source_pixel_identity": crop.tobytes() == original.crop(box).tobytes()
    }
    args.metadata.parent.mkdir(parents=True, exist_ok=True)
    args.metadata.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
