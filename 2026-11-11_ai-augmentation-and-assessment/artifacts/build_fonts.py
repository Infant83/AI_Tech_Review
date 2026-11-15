"""Create openly licensed WOFF2 subsets for the final manuscripts and UI."""
from pathlib import Path
import argparse
import json
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--regular', type=Path, required=True)
    parser.add_argument('--bold', type=Path, required=True)
    parser.add_argument('--license', type=Path, default=ROOT / 'artifacts' / 'font-OFL.txt')
    args = parser.parse_args()
    if not args.license.is_file():
        parser.error('A complete source-font license is required.')
    manuscripts = list((ROOT / 'reports').glob('review*.md'))
    if len(manuscripts) < 2:
        parser.error('Write reports/review.md and reports/review_en.md before building font subsets.')
    text = ''.join(file.read_text(encoding='utf-8') for file in manuscripts)
    text += ''.join(file.read_text(encoding='utf-8') for file in (ROOT / 'artifacts' / 'figures').glob('*.svg'))
    text += (ROOT / 'artifacts' / 'build_review.mjs').read_text(encoding='utf-8')
    text += ''.join(chr(i) for i in range(32, 256))
    license_parts = []
    coverage = {}
    for label, source in [('regular', args.regular), ('bold', args.bold)]:
        font = TTFont(source)
        available = font.getBestCmap()
        missing_hangul = sorted({ord(c) for c in text if 0xAC00 <= ord(c) <= 0xD7A3 and ord(c) not in available})
        if missing_hangul:
            raise ValueError(f'{label}: source font is missing Korean syllables: {missing_hangul}')
        for name_id in [0, 13, 14]:
            license_parts.extend(sorted({n.toUnicode() for n in font['name'].names if n.nameID == name_id}))
        family = 'Review Sans Subset'
        style = 'Bold' if label == 'bold' else 'Regular'
        renamed = {1:family,2:style,3:f'ReviewSansSubset-{style}',4:f'{family} {style}',6:f'ReviewSansSubset-{style}',16:family,17:style}
        for record in font['name'].names:
            if record.nameID in renamed:
                record.string = renamed[record.nameID].encode(record.getEncoding())
        options = subset.Options()
        options.flavor = 'woff2'
        options.desubroutinize = True
        options.recalc_timestamp = False
        options.name_IDs = ['*']
        worker = subset.Subsetter(options=options)
        worker.populate(text=text)
        worker.subset(font)
        font.flavor = 'woff2'
        target = ROOT / 'artifacts' / f'review-{label}.woff2'
        font.save(target)
        result = TTFont(target)
        missing = sorted({ord(c) for c in text if 0xAC00 <= ord(c) <= 0xD7A3 and ord(c) not in result.getBestCmap()})
        if missing:
            raise ValueError(f'{label}: Korean subset coverage failed: {missing}')
        coverage[label] = {'bytes':target.stat().st_size,'missing_korean_syllables':0}
    license_text = '\n\n'.join(dict.fromkeys(license_parts)).strip() + '\n\n' + args.license.read_text(encoding='utf-8')
    (ROOT / 'artifacts' / 'font-license.txt').write_text(license_text.rstrip() + '\n', encoding='utf-8')
    print(json.dumps(coverage, ensure_ascii=False))

if __name__ == '__main__':
    main()
