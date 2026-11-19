#!/usr/bin/env python3
"""Compose licensed final Nature Fig. 4c and 5d without changing their data.

Source: Zhang et al., Nature 659, 634–639 (2026),
doi:10.1038/s41586-026-11268-y. CC BY 4.0, The Author(s) 2026.
Inputs are the publisher's full-resolution Fig4_HTML.png and Fig5_HTML.png.
Only cropping, resizing, repositioning and two explanatory headers are applied.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--figure4', type=Path, required=True)
    ap.add_argument('--figure5', type=Path, required=True)
    ap.add_argument('--font', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    a = Image.open(args.figure4).convert('RGB')
    b = Image.open(args.figure5).convert('RGB')
    assert a.size == (2168, 579) and b.size == (2167, 1010)
    left = a.crop((1490, 0, 2168, 579))
    right = b.crop((990, 420, 2167, 1010))
    left = left.resize((720, round(left.height * 720 / left.width)))
    right = right.resize((1260, round(right.height * 1260 / right.width)))
    out = Image.new('RGB', (2040, max(left.height, right.height) + 85), 'white')
    out.paste(left, (10, 70))
    out.paste(right, (770, 70))
    draw = ImageDraw.Draw(out)
    font = ImageFont.truetype(str(args.font), 28)
    draw.text((25, 10), 'Figure 4(c): tunable dispersion', fill='#17364b', font=font)
    draw.text((785, 10), 'Figure 5(d): fringes and reconstructed phase', fill='#17364b', font=font)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.output)

if __name__ == '__main__':
    main()
