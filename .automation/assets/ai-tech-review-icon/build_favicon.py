"""Build the AI Tech Review Q/node mark from shared vector geometry.

Requires Pillow. Both SVG and raster exports use SHAPES; no font, external
image, random effect, or platform drawing service is involved.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"
BACKGROUND = "#10242C"
IVORY = "#F4F4EC"
MINT = "#69DECA"
CANVAS = 512

# Circle: (kind, fill, cx, cy, radius).
# Capsule: (kind, fill, x1, y1, x2, y2, width).
# The inset circle uses the background to make the opaque Q counter.
SHAPES = (
    ("circle", IVORY, 250, 250, 150),
    ("circle", BACKGROUND, 250, 250, 118),
    ("capsule", IVORY, 300, 300, 374, 374, 32),
    ("capsule", MINT, 216, 269, 282, 225, 16),
    ("circle", MINT, 216, 269, 21),
    ("circle", MINT, 282, 225, 21),
)


def svg_text() -> str:
    elements = [f'  <rect width="512" height="512" fill="{BACKGROUND}"/>']
    for kind, color, *values in SHAPES:
        if kind == "circle":
            x, y, radius = values
            elements.append(f'  <circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>')
        else:
            x1, y1, x2, y2, width = values
            elements.append(
                f'  <path d="M{x1} {y1} L{x2} {y2}" fill="none" '
                f'stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'
            )
    label = escape("AI Tech Review: quantum Q with connected nodes", quote=True)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" '
        f'role="img" aria-label="{label}">\n'
        + "\n".join(elements)
        + "\n</svg>\n"
    )


def draw_icon(size: int = 2048) -> Image.Image:
    scale = size / CANVAS
    image = Image.new("RGB", (size, size), BACKGROUND)
    draw = ImageDraw.Draw(image)

    def circle(x: float, y: float, radius: float, color: str) -> None:
        draw.ellipse(
            tuple(round(v * scale) for v in (x - radius, y - radius, x + radius, y + radius)),
            fill=color,
        )

    for kind, color, *values in SHAPES:
        if kind == "circle":
            circle(*values, color)
        else:
            x1, y1, x2, y2, width = values
            draw.line(
                [(round(x1 * scale), round(y1 * scale)), (round(x2 * scale), round(y2 * scale))],
                fill=color,
                width=round(width * scale),
            )
            circle(x1, y1, width / 2, color)
            circle(x2, y2, width / 2, color)
    return image


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    (GENERATED / "ai-tech-review-icon.svg").write_text(svg_text(), encoding="utf-8")
    master = draw_icon()
    for name, size in (
        ("ai-tech-review-icon-512.png", 512),
        ("apple-touch-icon.png", 180),
        ("favicon-64x64.png", 64),
        ("favicon-32x32.png", 32),
        ("favicon-16x16.png", 16),
    ):
        master.resize((size, size), Image.Resampling.LANCZOS).save(GENERATED / name)
    master.resize((512, 512), Image.Resampling.LANCZOS).save(
        GENERATED / "favicon.ico",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


if __name__ == "__main__":
    main()
