"""Build the AI Tech Review Q/node mark from shared vector geometry.

Requires Pillow. Both SVG and raster exports use SHAPES and GRAIN_PATHS;
no font, external image, random effect, or platform drawing service is involved.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"
BACKGROUND = "#3F1D2B"
BEIGE = "#B39B79"
PATINA = "#6F9185"
CANVAS = 512

# Circle: (kind, fill, cx, cy, radius).
# Ring: (kind, stroke, cx, cy, centerline_radius, width).
# Capsule: (kind, fill, x1, y1, x2, y2, width).
# A stroked ring lets the same background grain continue through its counter.
SHAPES = (
    ("ring", BEIGE, 250, 250, 134, 32),
    ("capsule", BEIGE, 300, 300, 374, 374, 32),
    ("capsule", PATINA, 216, 269, 282, 225, 16),
    ("circle", PATINA, 216, 269, 21),
    ("circle", PATINA, 282, 225, 21),
)

# Quiet, irregularly spaced wood-grain curves, shared by both output formats.
# Decorative grain is deliberately much lower contrast than the brand mark.
GRAIN_PATHS = tuple(
    (
        "#462231" if i % 3 else "#381A26",
        1.5 if i % 4 else 2,
        ((x, -24), (x + 18 + (i % 3) * 7, 128), (x - 20 - (i % 4) * 5, 392), (x + 6, 536)),
    )
    for i, x in enumerate((22, 31, 68, 76, 120, 133, 181, 195, 243, 254, 302, 311, 363, 376, 419, 428, 474, 488))
)


def svg_text() -> str:
    elements = [f'  <rect width="512" height="512" fill="{BACKGROUND}"/>']
    for color, width, points in GRAIN_PATHS:
        (x0, y0), (x1, y1), (x2, y2), (x3, y3) = points
        elements.append(
            f'  <path d="M{x0} {y0} C{x1} {y1} {x2} {y2} {x3} {y3}" '
            f'fill="none" stroke="{color}" stroke-width="{width}"/>'
        )
    for kind, color, *values in SHAPES:
        if kind == "circle":
            x, y, radius = values
            elements.append(f'  <circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>')
        elif kind == "ring":
            x, y, radius, width = values
            elements.append(
                f'  <circle cx="{x}" cy="{y}" r="{radius}" fill="none" '
                f'stroke="{color}" stroke-width="{width}"/>'
            )
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

    for color, width, points in GRAIN_PATHS:
        # Sample the same cubic Bezier used in the SVG, in canvas coordinates.
        samples = []
        for i in range(97):
            t = i / 96
            u = 1 - t
            weights = (u**3, 3 * u**2 * t, 3 * u * t**2, t**3)
            samples.append(tuple(round(sum(w * p[axis] for w, p in zip(weights, points)) * scale) for axis in (0, 1)))
        draw.line(samples, fill=color, width=max(1, round(width * scale)), joint="curve")

    for kind, color, *values in SHAPES:
        if kind == "circle":
            circle(*values, color)
        elif kind == "ring":
            x, y, radius, width = values
            outer = radius + width / 2
            draw.ellipse(
                tuple(round(v * scale) for v in (x - outer, y - outer, x + outer, y + outer)),
                outline=color,
                width=round(width * scale),
            )
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
