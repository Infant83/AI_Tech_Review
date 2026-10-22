"""Layout only: original image resizing, masks and grayscale for review boards."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
FONT = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
LABELS = ['A · 열린 저널 Q / AI', 'B · 리뷰의 여백', 'C · 한 권의 저널', 'D · 페이지로 만든 R']

def font(size):
    return ImageFont.truetype(FONT, size)

def tile(source, size, gray=False):
    result = source.resize((size, size), Image.Resampling.LANCZOS)
    if gray:
        result = ImageOps.grayscale(result).convert('RGB')
    return result

def paste_masked(canvas, source, xy, size, gray=False):
    result = tile(source, size, gray)
    mask = Image.new('L', (size, size))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size-1, size-1), radius=size * .23, fill=255)
    canvas.paste(result, xy, mask)

sources = [Image.open(ROOT / f'candidate-{letter}.png').convert('RGB') for letter in 'ABCD']
canvas = Image.new('RGB', (1240, 466), '#E9E2D6')
draw = ImageDraw.Draw(canvas)
for i, source in enumerate(sources):
    x = 32 + i * 302
    draw.text((x, 20), LABELS[i], fill='#382C25', font=font(24))
    paste_masked(canvas, source, (x, 66), 272)
    draw.text((x, 358), '양자 · AI · 리뷰  /  수채화 경계 전환', fill='#6D5D4D', font=font(17))
    for size, dx in [(64, 0), (32, 105), (16, 181)]:
        paste_masked(canvas, source, (x + dx, 390), size)
canvas.save(ROOT / 'comparison.png')

canvas = Image.new('RGB', (1020, 980), '#E9E2D6')
draw = ImageDraw.Draw(canvas)
draw.text((30, 18), '같은 원본의 실제 축소 · 둥근 마스크 · 흑백', fill='#382C25', font=font(27))
for label, x in [('180px', 55), ('64px', 294), ('32px', 410), ('16px', 500), ('흑백 180px', 580), ('어두운 주변 64px', 805)]:
    draw.text((x, 60), label, fill='#6D5D4D', font=font(20))
for i, source in enumerate(sources):
    y = 100 + i * 217
    draw.text((20, y), 'ABCD'[i], fill='#382C25', font=font(20))
    paste_masked(canvas, source, (55, y), 180)
    paste_masked(canvas, source, (294, y + 40), 64)
    paste_masked(canvas, source, (410, y + 40), 32)
    paste_masked(canvas, source, (500, y + 40), 16)
    paste_masked(canvas, source, (580, y), 180, gray=True)
    draw.rounded_rectangle((805, y, 979, y + 179), radius=16, fill='#211D1B')
    paste_masked(canvas, source, (860, y + 40), 64)
canvas.save(ROOT / 'legibility.png')

# Material refinement versus its selected first pass; artwork pixels are unchanged.
canvas = Image.new('RGB', (880, 610), '#E9E2D6')
draw = ImageDraw.Draw(canvas)
refined_path = ROOT / 'selected-D-watercolor.png'
if refined_path.exists():
    refined = Image.open(refined_path).convert('RGB')
    final_board = Image.new('RGB', (1240, 466), '#E9E2D6')
    final_draw = ImageDraw.Draw(final_board)
    for i, source in enumerate(sources[:3] + [refined]):
        x = 32 + i * 302
        label = LABELS[i] if i < 3 else 'D · 페이지 R + Q AI (선택)'
        final_draw.text((x, 20), label, fill='#382C25', font=font(23))
        paste_masked(final_board, source, (x, 66), 272)
        final_draw.text((x, 358), '양자 · AI · 리뷰  /  수채화 경계 전환', fill='#6D5D4D', font=font(17))
        for size, dx in [(64, 0), (32, 105), (16, 181)]:
            paste_masked(final_board, source, (x + dx, 390), size)
    final_board.save(ROOT / 'comparison-final.png')
    for source, x, label in [(sources[3], 30, 'D · 첫 시안'), (refined, 460, 'D · 수채화 재질 보정')]:
        draw.text((x, 20), label, fill='#382C25', font=font(26))
        paste_masked(canvas, source, (x, 65), 385)
        for size, dx in [(64, 0), (32, 112), (16, 195)]:
            paste_masked(canvas, source, (x+dx, 485), size)
            draw.text((x+dx, 560), f'{size}px', fill='#6D5D4D', font=font(18))
    canvas.save(ROOT / 'refinement-comparison.png')

    canvas = Image.new('RGB', (780, 330), '#E9E2D6')
    draw = ImageDraw.Draw(canvas)
    draw.text((25, 20), '선택안 · 같은 원본의 실제 축소와 흑백', fill='#382C25', font=font(25))
    for size, x in [(180, 25), (64, 250), (32, 365), (16, 450)]:
        paste_masked(canvas, refined, (x, 77), size)
        draw.text((x, 275), f'{size}px', fill='#6D5D4D', font=font(18))
    paste_masked(canvas, refined, (565, 77), 180, gray=True)
    draw.text((565, 275), '흑백 180px', fill='#6D5D4D', font=font(18))
    canvas.save(ROOT / 'selected-legibility.png')
