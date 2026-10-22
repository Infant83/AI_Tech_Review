"""Prompt-brace icon QA: resize, layout and grayscale only; no artwork edits."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
BASELINE = ROOT.parent / "20261022-topic-keywords" / "selected-A-keywords.png"
FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
BG, INK, MUTED = "#e9e2d6", "#382c25", "#6d5d4d"


def font(size):
    return ImageFont.truetype(FONT, size)


def tile(source, size, gray=False):
    result = source.resize((size, size), Image.Resampling.LANCZOS)
    return ImageOps.grayscale(result).convert("RGB") if gray else result


sources = {
    "Previous": Image.open(BASELINE).convert("RGB"),
    "Prompt brace": Image.open(ROOT / "candidate-A.png").convert("RGB"),
}
board = Image.new("RGB", (912, 546), BG)
draw = ImageDraw.Draw(board)
for i, (label, source) in enumerate(sources.items()):
    x = 24 + i * 444
    draw.text((x, 18), label + " / 420 px", font=font(24), fill=INK)
    board.paste(tile(source, 420), (x, 62))
    draw.text((x, 500), "Q · AI · DFT · VQE · LLM · OLED · GPU", font=font(18), fill=MUTED)
board.save(ROOT / "comparison.png")

board = Image.new("RGB", (1120, 610), BG)
draw = ImageDraw.Draw(board)
draw.text((24, 18), "Original artwork at actual display sizes; grayscale uses the same source", font=font(24), fill=INK)
columns = [(60, 180, False), (292, 64, False), (416, 32, False), (504, 16, False), (590, 180, True), (830, 64, True), (954, 32, True), (1042, 16, True)]
for x, size, gray in columns:
    draw.text((x, 64), f"{size}px" + (" gray" if gray else ""), font=font(17), fill=MUTED)
for i, (label, source) in enumerate(sources.items()):
    y = 105 + i * 250
    draw.text((22, y), "Old" if i == 0 else "New", font=font(18), fill=INK)
    for x, size, gray in columns:
        board.paste(tile(source, size, gray), (x, y))
board.save(ROOT / "legibility.png")

print(ROOT / "comparison.png")
print(ROOT / "legibility.png")
