#!/usr/bin/env python3
"""Excerpt and connect CC BY 4.0 published panels without changing their data.

Requires a separately obtained publisher Article-in-Press PDF. The SHA guard
binds the crops to the edition actually read; it must be re-reviewed for a new PDF.
"""
from pathlib import Path
import argparse, hashlib, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

EXPECTED_SHA256 = "0decdac73c7df69e9930b56c0e24cf4e75fc4eb4fe287672e20311b05f74ff7a"
CROPS = {2: (.399, .769, .948, .947), 5: (.060, .059, .490, .252)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-pdf", type=Path, required=True)
    ap.add_argument("--font", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args()
    if hashlib.sha256(a.source_pdf.read_bytes()).hexdigest() != EXPECTED_SHA256:
        raise ValueError("Source edition changed: review panel bounds and science before composing.")
    a.output_dir.mkdir(parents=True, exist_ok=True)
    panels = {}
    with tempfile.TemporaryDirectory(prefix="cipec-panels-") as tmp:
        for page, rect in CROPS.items():
            prefix = Path(tmp) / ("page-" + str(page))
            subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page),
                            "-singlefile", "-r", "240", "-png",
                            str(a.source_pdf), str(prefix)], check=True,
                           stdout=subprocess.DEVNULL)
            im = Image.open(str(prefix) + ".png").convert("RGB")
            w, h = im.size
            panels[page] = im.crop(tuple(round(x * (w if i % 2 == 0 else h))
                                         for i, x in enumerate(rect)))
    canvas = Image.new("RGB", (2200, 1000), "white")
    d = ImageDraw.Draw(canvas)
    ink, muted, line = "#193c50", "#526774", "#c8d7de"
    def txt(x, y, text, size=34, fill=ink):
        d.text((x, y), text, font=ImageFont.truetype(str(a.font), size), fill=fill)
    txt(65, 28, "CIPEC: compilation information changes the estimator", 55)
    txt(65, 100, "Camilo et al. | published Article in Press, 19 Nov 2026 | selected original panels", 31, muted)
    d.line((65, 160, 2135, 160), fill=line, width=3)
    txt(65, 188, "A   Noisy logical circuits are sampled (Fig. 1, lower)", 34)
    txt(1170, 188, "B   Qibo simulation: 5 logical qubits (Fig. 3)", 34)
    for page, x, y, width in [(2, 65, 250, 1040), (5, 1180, 246, 930)]:
        panel = panels[page]
        height = round(width * panel.height / panel.width)
        panel = panel.resize((width, height), Image.Resampling.LANCZOS)
        canvas.paste(panel, (x, y))
    txt(80, 715, "Controlled extra sampling factor γ²;", 36)
    txt(80, 767, "total shots still grow as ε⁻².", 36)
    txt(80, 825, "Noise characterization must track the target precision.", 31, muted)
    d.line((65, 898, 2135, 898), fill=line, width=2)
    txt(65, 918, "B: trefoil Jones-polynomial estimate | ε = 0.01, δ = 0.1 | local depolarizing noise", 31, muted)
    txt(65, 960, "Excerpted and rearranged; axes and legend preserved. CC BY 4.0 | DOI 10.1038/s41534-026-01407-8", 29, muted)
    output = a.output_dir / "cipec-fig1lower-fig3-composite.png"
    canvas.save(output)
    print(output)

if __name__ == "__main__":
    main()
