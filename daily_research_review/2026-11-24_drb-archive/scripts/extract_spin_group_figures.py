#!/usr/bin/env python3
"""Extract two attributed CC BY 4.0 PRX panels from verified source PDFs.

Source PDFs must be supplied explicitly. This script performs only cropping
and rasterization; it does not run any scientific computation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from pypdf import PdfReader, PdfWriter


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--li-source', type=Path, required=True)
    parser.add_argument('--nomoto-source', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--pdftoppm', default='pdftoppm')
    args = parser.parse_args()
    poppler = shutil.which(args.pdftoppm)
    if poppler is None:
        raise SystemExit('pdftoppm not found; supply --pdftoppm.')
    args.output_dir.mkdir(parents=True, exist_ok=True)
    specs = [
        (args.li_source, '742ce3c5db891c2d1cc54b21ebe7389868ac8c84328979d086f021858200849a',
         12, (78, 391, 313, 548.5), 'li-fig5c'),
        (args.nomoto_source, '9421103f5ef40a046a27bc7a0b72c09e1d64a1b18a899d9d4046449b72a3842f',
         3, (50, 486, 298, 635), 'nomoto-fig1c'),
    ]
    receipts = []
    for source, expected, page_no, box, name in specs:
        if digest(source) != expected:
            raise SystemExit('Source version hash mismatch: ' + source.name)
        page = PdfReader(source).pages[page_no - 1]
        page.cropbox.lower_left = box[:2]
        page.cropbox.upper_right = box[2:]
        with tempfile.TemporaryDirectory() as temp:
            cropped = Path(temp) / 'panel.pdf'
            writer = PdfWriter()
            writer.add_page(page)
            with cropped.open('wb') as output:
                writer.write(output)
            subprocess.run([poppler, '-cropbox', '-r', '300', '-singlefile', '-png',
                            str(cropped), str(args.output_dir / name)], check=True)
        png = args.output_dir / (name + '.png')
        receipts.append({'asset': png.name, 'sha256': digest(png), 'bytes': png.stat().st_size,
                         'source_sha256': expected, 'source_page_1based': page_no,
                         'crop_box_points_bottom_origin': box, 'render_dpi': 300})
    print(json.dumps(receipts, indent=2))


if __name__ == '__main__':
    main()
