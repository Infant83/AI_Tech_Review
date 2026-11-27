"""Extract author-licensed panels; no data fitting or curve reconstruction."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import subprocess
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject
from PIL import Image


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--dpi", type=int, default=300)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(a.pdf)
    source_hash = hashlib.sha256(a.pdf.read_bytes()).hexdigest()
    specs = [
        ("regional-fig1cde", 3, [60, 259, 550, 550], "Fig.1(c,d,e)"),
        ("regional-fig3c", 6, [56, 338, 542, 474], "Fig.3(c)"),
    ]
    out = []
    for name, page_number, box, panels in specs:
        page = copy.deepcopy(reader.pages[page_number - 1])
        page.mediabox = RectangleObject(box)
        page.cropbox = RectangleObject(box)
        writer = PdfWriter()
        writer.add_page(page)
        cropped_pdf = a.output_dir / (name + "-crop.pdf")
        with cropped_pdf.open("wb") as stream:
            writer.write(stream)
        prefix = a.output_dir / name
        subprocess.run(["pdftoppm", "-singlefile", "-r", str(a.dpi),
                        "-png", str(cropped_pdf), str(prefix)], check=True)
        png = prefix.with_suffix(".png")
        out.append({
            "asset": png.name, "source_page": page_number, "source_panels": panels,
            "crop_points": box, "dpi": a.dpi,
            "sha256": hashlib.sha256(png.read_bytes()).hexdigest(),
            "source_pdf_sha256": source_hash,
            "source_url": "https://www.nature.com/articles/s41534-026-01414-9_reference.pdf",
            "edition": "Article in Press, online 2026-11-24",
            "authors": "D. Du and E. Figueroa",
            "license": "CC BY4.0",
            "license_url": "https://creativecommons.org/licenses/by/4.0/",
            "rights_evidence": "Actual main PDF p13; no separate third-party credit observed in these captions.",
            "changes": "Rectangular panel extraction and rasterization only; source panel labels, axes, legends, curves and uncertainty marks retained.",
            "reproduction": "No new solver/model execution, inference, digitization or curve reconstruction.",
        })
    # Keep the full six-metric excerpt privately. Recompose only the original
    # fidelity and energy plots for the public-sized key excerpt. Axes, points
    # and error bars are pasted at native scale. Shared condition labels are
    # copied from the original first metric; the complete model legend is kept.
    source_image = Image.open(a.output_dir / "regional-fig3c.png").convert("RGB")
    scale = source_image.width / 2025
    box = lambda coords: tuple(round(v * scale) for v in coords)
    fidelity_box = [810, 40, 1110, 455]
    energy_box = [1725, 40, 2025, 455]
    labels_box = [0, 40, 195, 350]
    legend_box = [535, 495, 1540, 567]
    canvas = Image.new("RGB", (round(1000 * scale), round(490 * scale)), "white")
    for coords, xy in [(labels_box, (10, 0)),
                       (fidelity_box, (240, 0)),
                       (energy_box, (665, 0))]:
        canvas.paste(source_image.crop(box(coords)),
                     (round(xy[0] * scale), round(xy[1] * scale)))
    legend = source_image.crop(box(legend_box))
    legend_width = round(960 * scale)
    legend_height = round(legend.height * legend_width / legend.width)
    legend = legend.resize((legend_width, legend_height), Image.Resampling.LANCZOS)
    canvas.paste(legend, (round(20 * scale), round(420 * scale)))
    key_png = a.output_dir / "regional-fig3c-fidelity-energy.png"
    canvas.save(key_png)
    out.append({
        "asset": key_png.name, "source_page": 6, "source_panels": "Fig.3(c), third and sixth metric plots",
        "source_full_excerpt": "regional-fig3c.png",
        "source_full_excerpt_sha256": hashlib.sha256(
            (a.output_dir / "regional-fig3c.png").read_bytes()).hexdigest(),
        "source_pixel_boxes_at_300dpi": {
            "fidelity": fidelity_box, "energy_bias": energy_box,
            "shared_condition_labels": labels_box, "complete_original_model_legend": legend_box},
        "layout_pixels_at_300dpi": {"canvas": [1000, 490],
                                   "labels": [10, 0], "fidelity": [240, 0],
                                   "energy_bias": [665, 0], "legend": [20, 420]},
        "source_pdf_sha256": source_hash,
        "source_url": "https://www.nature.com/articles/s41534-026-01414-9_reference.pdf",
        "edition": "Article in Press, online 2026-11-24",
        "authors": "D. Du and E. Figueroa",
        "license": "CC BY4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "rights_evidence": "Actual main PDF p13; no separate third-party credit observed.",
        "changes": "Third/fidelity and sixth/energy-bias plots excerpted and placed side by side on white canvas. Original ID/OOD1-5 condition labels copied once from first metric as shared row labels. Full original three-model legend retained with uniform resizing. Plot axes, ticks, points and error bars are unchanged native raster pixels.",
        "reproduction": "No data fitting, digitization, model inference or new numerical experiment.",
        "sha256": hashlib.sha256(key_png.read_bytes()).hexdigest(),
    })
    (a.output_dir / "regional-figure-manifest.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
