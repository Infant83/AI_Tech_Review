"""Export the selected watercolor logo without altering its artwork.

Requires Pillow. The fixed, reviewed imagegen source is only resized; no
generation call, color correction, crop, or artistic filter runs during builds.
The SVG embeds the exact exported 512px PNG to avoid external image requests.
"""

from __future__ import annotations

import base64
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"
ARTWORK_SOURCE = ROOT / "studies" / "20261022-quantum-ai-editorial" / "selected-D-watercolor.png"


def main() -> None:
    with Image.open(ARTWORK_SOURCE) as source:
        if source.width != source.height:
            raise ValueError("The selected app-icon artwork must be square.")
        if source.mode == "RGBA" and source.getchannel("A").getextrema() != (255, 255):
            raise ValueError("The home-screen icon must have an opaque background.")
        master = source.convert("RGB")
    master.info.clear()
    GENERATED.mkdir(parents=True, exist_ok=True)
    for name, size in (
        ("ai-tech-review-icon-512.png", 512),
        ("apple-touch-icon.png", 180),
        ("favicon-64x64.png", 64),
        ("favicon-32x32.png", 32),
        ("favicon-16x16.png", 16),
    ):
        master.resize((size, size), Image.Resampling.LANCZOS).save(
            GENERATED / name, optimize=True
        )

    png = (GENERATED / "ai-tech-review-icon-512.png").read_bytes()
    encoded = base64.b64encode(png).decode("ascii")
    (GENERATED / "ai-tech-review-icon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" '
        'role="img" aria-label="AI Tech Review Letters Q AI review monogram">\n'
        f'  <image width="512" height="512" href="data:image/png;base64,{encoded}"/>\n'
        '</svg>\n',
        encoding="utf-8",
    )
    master.resize((512, 512), Image.Resampling.LANCZOS).save(
        GENERATED / "favicon.ico",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


if __name__ == "__main__":
    main()
