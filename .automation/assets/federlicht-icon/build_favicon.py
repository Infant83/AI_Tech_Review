from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parent
GENERATED = ROOT / "generated"


def lerp(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def color_lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int, int]:
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t), 255)


def bezier(points: tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]], t: float) -> tuple[float, float]:
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = points
    u = 1 - t
    x = u**3 * x0 + 3 * u**2 * t * x1 + 3 * u * t**2 * x2 + t**3 * x3
    y = u**3 * y0 + 3 * u**2 * t * y1 + 3 * u * t**2 * y2 + t**3 * y3
    return x, y


def scaled(points: list[tuple[float, float]], scale: int) -> list[tuple[int, int]]:
    return [(round(x * scale), round(y * scale)) for x, y in points]


def draw_round_rect(draw: ImageDraw.ImageDraw, size: int, scale: int) -> None:
    margin = 18 * scale
    radius = 92 * scale
    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=radius,
        fill=(8, 14, 20, 255),
        outline=(31, 48, 58, 255),
        width=2 * scale,
    )
    draw.ellipse((70 * scale, 62 * scale, 460 * scale, 430 * scale), fill=(15, 43, 58, 90))
    draw.ellipse((92 * scale, 108 * scale, 452 * scale, 464 * scale), fill=(78, 64, 24, 58))


def draw_icon(size: int = 1024) -> Image.Image:
    scale = size // 512
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow, "RGBA")
    draw_round_rect(g, size, scale)
    im = Image.alpha_composite(im, glow.filter(ImageFilter.GaussianBlur(0.5 * scale)))
    d = ImageDraw.Draw(im, "RGBA")

    spine = ((154, 395), (203, 285), (296, 176), (399, 111))
    left_outer = ((148, 400), (118, 320), (208, 188), (386, 119))
    right_outer = ((156, 392), (246, 378), (370, 250), (407, 110))
    n = 34
    spine_pts = [bezier(spine, i / (n - 1)) for i in range(n)]
    left_pts = [bezier(left_outer, i / (n - 1)) for i in range(n)]
    right_pts = [bezier(right_outer, i / (n - 1)) for i in range(n)]

    left_a, left_b = (64, 167, 224), (207, 241, 255)
    right_a, right_b = (244, 192, 54), (255, 243, 169)
    for i in range(n - 1):
        t = i / (n - 2)
        d.polygon(scaled([left_pts[i], left_pts[i + 1], spine_pts[i + 1], spine_pts[i]], scale), fill=color_lerp(left_a, left_b, t))
        d.polygon(scaled([spine_pts[i], spine_pts[i + 1], right_pts[i + 1], right_pts[i]], scale), fill=color_lerp(right_a, right_b, t))

    outline = scaled(left_pts + list(reversed(right_pts)), scale)
    d.line(outline + [outline[0]], fill=(248, 253, 255, 185), width=max(2, 2 * scale), joint="curve")

    for t in (0.16, 0.25, 0.34, 0.44, 0.55, 0.67, 0.80):
        s = bezier(spine, t)
        l = bezier(left_outer, t * 0.96)
        r = bezier(right_outer, min(0.98, t * 1.02))
        d.line(scaled([s, ((s[0] * 0.42 + l[0] * 0.58), (s[1] * 0.42 + l[1] * 0.58))], scale), fill=(232, 248, 255, 180), width=max(2, 2 * scale))
        d.line(scaled([s, ((s[0] * 0.42 + r[0] * 0.58), (s[1] * 0.42 + r[1] * 0.58))], scale), fill=(124, 88, 28, 130), width=max(2, 2 * scale))

    # Base light: reduced to a small, crisp anchor so the favicon does not smear.
    base = (149 * scale, 398 * scale)
    for radius, alpha in ((48, 52), (30, 80), (15, 220)):
        d.ellipse(
            (
                base[0] - radius * scale,
                base[1] - radius * scale,
                base[0] + radius * scale,
                base[1] + radius * scale,
            ),
            fill=(255, 197, 55, alpha),
        )

    spine_scaled = scaled([bezier(spine, i / 38) for i in range(39)], scale)
    d.line(spine_scaled, fill=(18, 29, 38, 165), width=max(4, 7 * scale), joint="curve")
    d.line(spine_scaled, fill=(250, 252, 255, 245), width=max(3, 4 * scale), joint="curve")
    d.line(spine_scaled, fill=(255, 205, 66, 155), width=max(1, 1 * scale), joint="curve")

    # Minimal book/light cue from the source logo, kept below the feather.
    d.arc((110 * scale, 382 * scale, 260 * scale, 455 * scale), 202, 345, fill=(255, 228, 134, 230), width=3 * scale)
    d.arc((142 * scale, 382 * scale, 392 * scale, 455 * scale), 190, 338, fill=(235, 245, 255, 215), width=3 * scale)
    d.line(scaled([(130, 424), (382, 424)], scale), fill=(255, 197, 55, 175), width=2 * scale)

    return im


def write_svg(path: Path) -> None:
    path.write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Federlicht feather icon">
  <defs>
    <linearGradient id="blueVane" x1="120" y1="400" x2="390" y2="115" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#40a7e0"/>
      <stop offset="1" stop-color="#d8f5ff"/>
    </linearGradient>
    <linearGradient id="goldVane" x1="155" y1="395" x2="408" y2="110" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#f4c036"/>
      <stop offset="1" stop-color="#fff3a9"/>
    </linearGradient>
    <radialGradient id="glow" cx="31%" cy="77%" r="25%">
      <stop offset="0" stop-color="#ffd75a"/>
      <stop offset="1" stop-color="#ffd75a" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="18" y="18" width="476" height="476" rx="92" fill="#080e14"/>
  <ellipse cx="265" cy="251" rx="205" ry="183" fill="#0f2b3a" opacity=".34"/>
  <ellipse cx="277" cy="286" rx="192" ry="176" fill="#4e4018" opacity=".23"/>
  <circle cx="149" cy="398" r="58" fill="url(#glow)"/>
  <path d="M148 400 C118 320 208 188 386 119 C308 179 220 290 154 395 Z" fill="url(#blueVane)" stroke="#f8fdff" stroke-opacity=".62" stroke-width="2"/>
  <path d="M154 395 C246 378 370 250 407 110 C374 241 268 351 154 395 Z" fill="url(#goldVane)" stroke="#f8fdff" stroke-opacity=".62" stroke-width="2"/>
  <path d="M184 351 C158 338 137 327 121 315 M209 313 C177 297 153 282 135 266 M238 273 C204 254 176 235 156 215 M269 236 C235 214 206 191 184 168" stroke="#e8f8ff" stroke-opacity=".72" stroke-width="4" stroke-linecap="round"/>
  <path d="M211 337 C259 327 310 293 359 240 M235 298 C282 282 329 248 375 191 M265 255 C309 236 354 201 394 139" stroke="#7c581c" stroke-opacity=".58" stroke-width="4" stroke-linecap="round"/>
  <path d="M154 395 C203 285 296 176 399 111" fill="none" stroke="#121d26" stroke-opacity=".72" stroke-width="9" stroke-linecap="round"/>
  <path d="M154 395 C203 285 296 176 399 111" fill="none" stroke="#fbfcff" stroke-width="5" stroke-linecap="round"/>
  <path d="M154 395 C203 285 296 176 399 111" fill="none" stroke="#ffcd42" stroke-opacity=".6" stroke-width="1.4" stroke-linecap="round"/>
  <path d="M110 424 C162 395 209 389 260 424 M142 424 C225 389 305 389 392 424" fill="none" stroke="#f7fbff" stroke-opacity=".82" stroke-width="4" stroke-linecap="round"/>
  <path d="M130 424 H382" stroke="#ffc537" stroke-opacity=".7" stroke-width="2" stroke-linecap="round"/>
</svg>
""",
        encoding="utf-8",
    )


def main() -> None:
    GENERATED.mkdir(parents=True, exist_ok=True)
    icon_1024 = draw_icon(1024)
    icon_512 = icon_1024.resize((512, 512), Image.Resampling.LANCZOS)
    icon_512.save(GENERATED / "federlicht-favicon-512.png")
    icon_512.resize((180, 180), Image.Resampling.LANCZOS).save(GENERATED / "apple-touch-icon.png")
    icon_512.resize((64, 64), Image.Resampling.LANCZOS).save(GENERATED / "favicon-64x64.png")
    icon_512.resize((32, 32), Image.Resampling.LANCZOS).save(GENERATED / "favicon-32x32.png")
    icon_512.resize((16, 16), Image.Resampling.LANCZOS).save(GENERATED / "favicon-16x16.png")
    icon_512.save(
        GENERATED / "favicon.ico",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    write_svg(GENERATED / "federlicht-favicon.svg")


if __name__ == "__main__":
    main()
